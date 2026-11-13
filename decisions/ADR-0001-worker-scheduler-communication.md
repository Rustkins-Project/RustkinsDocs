---
id: ADR-0001
title: "Les workers communiquent uniquement avec le Scheduler, sans accès à PostgreSQL"
status: proposed
topics: [architecture, worker, scheduler, rabbitmq, security]
applies_to: [all]
decided_at: null
approved_by: []
supersedes: []
related_work_items: []
references: []
---

# Les workers communiquent uniquement avec le Scheduler, sans accès à PostgreSQL

## Contexte

Avant cette décision, la documentation d'architecture faisait accéder les workers **directement à PostgreSQL** :

- à la réception d'un message `job.ready`, le worker rechargeait le `JobRun` en base, le message ne contenant que des identifiants ;
- le worker écrivait lui-même les états d'exécution (`running`, `success`, `warning`, `failed`, `cancelled`), les `StepRun`, les métadonnées de logs et d'artifacts, et son heartbeat ;
- le Scheduler « réagissait » ensuite à ces écritures pour libérer les ressources et débloquer les jobs suivants.

Ce modèle pose trois problèmes :

1. **Sécurité.** Le worker exécute du code arbitraire venant des dépôts (via Docker et le socket Docker). Un worker compromis détiendrait des identifiants PostgreSQL donnant accès aux utilisateurs, aux tokens hachés, aux secrets webhook chiffrés et à l'état de tous les projets.
2. **Responsabilités floues.** Deux composants écrivaient l'état d'un même `JobRun`, et le Scheduler devait détecter les changements faits par un autre.
3. **Placement incohérent.** Le Scheduler choisit un worker et y réserve des ressources, mais le message était publié dans une file partagée (`rustkins.jobs.ready.q`) que n'importe quel worker pouvait consommer.

Vision produit retenue : **le worker écoute le Scheduler, lui signale quand il a fini un job, et le Scheduler lui envoie les jobs suivants.**

## Décision

### Principe

- Les workers **n'ont aucun accès à PostgreSQL** : ni identifiants, ni route réseau.
- Le **Scheduler est le seul composant qui écrit l'état d'exécution** : `JobRun`, `StepRun`, `WorkerNode`, métadonnées de logs et d'artifacts.
- Toute communication entre Scheduler et workers passe par **RabbitMQ**, dans les deux sens.
- PostgreSQL reste la source de vérité ; RabbitMQ reste un transport.

### Scheduler → Worker

- Chaque worker possède **sa propre file** : `rustkins.jobs.worker.{worker_id}.q`, liée à l'échange `rustkins.jobs` avec la clé de routage `worker.{worker_id}`. Seul le worker choisi par le Scheduler reçoit le job.
- Le message `job.assigned` est un **ordre d'exécution autonome** : il contient tout ce dont le worker a besoin (dépôt et SHA, image, steps, `continue_on_error`, caractère optionnel du job, variables non secrètes, limites CPU/RAM, timeout, chemins d'artifacts à produire, artifacts amont à restaurer avec leurs clés RustFS et checksums, tentative, clé d'idempotence).
- Les messages Scheduler → Worker continuent de passer par l'**outbox transactionnelle**.
- L'annulation reste diffusée sur `rustkins.control` (fanout).

### Worker → Scheduler

Un nouvel échange `rustkins.events` (topic) reçoit les événements des workers. Le Scheduler les consomme dans la file `rustkins.events.scheduler.q`.

| Événement | Envoyé quand | Contenu principal |
| --- | --- | --- |
| `worker.registered` | Au démarrage du worker | `worker_id`, capacité CPU/RAM, version |
| `worker.heartbeat` | Périodiquement | `worker_id`, jobs en cours |
| `job.started` | Avant le premier step | `job_run_id`, `attempt`, `worker_id`, `started_at` |
| `step.finished` | À la fin de chaque step | index du step, statut, code de retour, horodatages |
| `job.finished` | À la fin du job (y compris annulation et erreur d'infrastructure) | statut final, code de retour, horodatages, détail d'erreur, clé et taille du log dans RustFS, métadonnées des artifacts, consommation de ressources mesurée |

Chaque événement porte un `event_id` unique, le `worker_id`, le `job_run_id` et l'`attempt` lorsqu'il concerne un job.

### Traitement par le Scheduler

À la réception d'un événement, le Scheduler, **dans une seule transaction** :

1. vérifie que l'événement est attendu : bon worker, bonne tentative, transition d'état autorisée ;
2. écrit l'état en base ;
3. pour `job.finished` : libère les ressources réservées, débloque les jobs dépendants, choisit leurs workers, réserve les ressources et crée les `OutboxMessage` `job.assigned` correspondants ;
4. ACK l'événement **après** le commit.

Un événement en double ou périmé (tentative ancienne, job déjà terminé) est ignoré puis acquitté. Un `job.started` inattendu (job déjà terminé, réassigné ou annulé) déclenche un `cancel.job` vers ce worker.

### Fiabilité côté worker

- Le worker publie ses événements avec les **confirmations de publication** RabbitMQ.
- Le worker ne dispose pas d'outbox en base : `job.finished` est conservé dans un **spool local** (disque) jusqu'à confirmation, et republié après un redémarrage.
- Le message `job.assigned` est acquitté **après** la confirmation de `job.finished`.
- Une livraison en double de `job.assigned` est détectée par un registre local des `job_run_id:attempt` déjà acceptés, puis acquittée sans exécution. Le Scheduler reste l'arbitre final (règle ci-dessus).

### Hors périmètre

- Les workers continuent d'écrire **logs et archives d'artifacts dans RustFS** et de publier les chunks de logs temps réel sur `rustkins.logs`. Restreindre leurs identifiants RustFS au préfixe `runs/` est recommandé.
- L'API ne communique jamais directement avec les workers.

## Alternatives

| Option | Raison du rejet |
| --- | --- |
| Statu quo : workers connectés à PostgreSQL | Surface d'attaque inacceptable pour un composant qui exécute du code arbitraire ; double écriture de l'état |
| Comptes PostgreSQL restreints par worker (droits par table ou sécurité au niveau des lignes) | Réduit l'exposition sans la supprimer, complexe à maintenir, et le Scheduler doit toujours détecter les écritures d'un autre composant |
| API interne HTTP/gRPC dédiée aux workers | Isolation équivalente, mais ajoute un service ou un serveur à sécuriser alors que RabbitMQ est déjà présent et transporte déjà les jobs |
| File partagée unique avec auto-sélection des workers | Incompatible avec la réservation de ressources par le Scheduler sur un worker précis |

## Conséquences

**Avantages**

- Un worker compromis n'a accès ni à la base ni aux données des autres projets ; il peut seulement émettre des événements, que le Scheduler valide.
- Un seul écrivain de l'état d'exécution : machine à états centralisée et plus simple à tester.
- Le job arrive sur le worker où les ressources ont été réservées.
- Les workers n'ont plus besoin du réseau de la base : déploiement plus simple sur des nodes distants.
- Le Scheduler reçoit les mesures de consommation dans `job.finished`, ce qui alimente les métriques prévues par l'[éco-conception](../docs/cross-cutting/eco-design/eco-design-approach.md).

**Limites et risques**

- **Message de job plus volumineux** : il transporte la définition du job. À surveiller, sans enjeu pour des pipelines de taille courante.
- **Charge sur le Scheduler** : il traite tous les événements. Les `step.finished` et heartbeats restent légers ; le volume de logs ne passe pas par lui.
- **Disponibilité de RabbitMQ** : si le broker est indisponible, les états ne remontent plus. Le spool local évite la perte de `job.finished`, mais l'interface affiche un état en retard.
- **Confiance dans le `worker_id`** : en V1, les workers peuvent partager un même compte RabbitMQ aux permissions restreintes (lecture de leur file et de `rustkins.control`, écriture sur `rustkins.events` et `rustkins.logs`). Un worker compromis pourrait se faire passer pour un autre. Un compte RabbitMQ par worker supprime ce risque ; à arbitrer selon la complexité de déploiement.
- **Impact documentaire** : les documents d'architecture (ARCH-01, 02, 04, 06, 09, 11), le modèle de données et les récapitulatifs V0 et V1 sont mis à jour dans la même PR que cette ADR.

## Références

- [ARCH-02 — RabbitMQ Architecture](../docs/architecture/components/messaging/02-rabbitmq-architecture.md)
- [ARCH-09 — Worker Architecture](../docs/architecture/components/worker/09-worker-architecture.md)
- [ARCH-11 — Scheduler Architecture](../docs/architecture/components/scheduler/11-scheduler-architecture.md)
- [Éco-conception — Démarche, leviers et limites](../docs/cross-cutting/eco-design/eco-design-approach.md)
