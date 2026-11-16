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

Le worker exécute du code venant des dépôts. S'il accède à PostgreSQL, un job malveillant peut récupérer ses identifiants et atteindre toute la base : utilisateurs, tokens, état de tous les projets.

Vision produit : **le worker écoute le Scheduler, lui signale quand il a fini un job, et le Scheduler lui envoie les jobs suivants.**

## Décision

- Les workers **n'ont aucun accès à PostgreSQL**.
- Le **Scheduler est le seul à écrire l'état d'exécution** (jobs, steps, workers, métadonnées de logs et d'artifacts).
- Scheduler et workers communiquent **uniquement via RabbitMQ** :

| Sens | Message | Rôle |
| --- | --- | --- |
| Scheduler → Worker | `job.assigned` | Ordre d'exécution complet (dépôt et SHA, image, steps, limites, artifacts à restaurer), envoyé dans la file propre au worker choisi |
| Scheduler → Worker | `cancel.job` | Annulation |
| Scheduler → Worker | `job.start.accepted`, `job.start.rejected` | Autorisation ou refus d'exécuter une tentative |
| Worker → Scheduler | `worker.registered`, `worker.heartbeat` | Déclaration de la capacité, signe de vie |
| Worker → Scheduler | `job.start.requested`, `step.finished`, `job.finished` | Avancement et résultat du job (statut, logs, artifacts, consommation) |

À la réception de `job.finished`, le Scheduler vérifie que l'événement est cohérent (bon worker, bonne tentative), écrit le résultat, libère les ressources et envoie les jobs suivants.

Avant de lancer le conteneur, le worker attend `job.start.accepted` : le Scheduler n'émet cette réponse qu'après avoir validé `job.start.requested` et écrit le passage à `running`. Il mémorise le `start_request_id` dans la tentative ; une retransmission de cette même demande reçoit à nouveau `job.start.accepted` sans nouvelle autorisation. Une demande différente pour une tentative déjà autorisée ou périmée reçoit `job.start.rejected`. Aucun registre durable des jobs n'est conservé sur le worker.

Les workers continuent d'écrire les logs et les artifacts dans RustFS.

## Alternatives

- **Workers connectés à PostgreSQL** : rejeté, surface d'attaque trop large.
- **API interne dédiée aux workers** : même isolation, mais un service de plus alors que RabbitMQ est déjà là.

## Conséquences

- Les droits RabbitMQ de chaque worker sont limités à ses propres files et à la publication de ses événements. Le Scheduler authentifie le compte RabbitMQ émetteur et vérifie qu'il correspond au `worker_id` annoncé.
- Un seul composant écrit l'état : plus simple à comprendre et à tester.
- Le job arrive sur le worker où les ressources ont été réservées.
- Si RabbitMQ est indisponible, le worker vivant garde `job.finished` en mémoire et réessaie. Après confirmation de publication, la file durable et l'ACK du Scheduler après commit assurent sa livraison.
- Si le worker disparaît **avant l'autorisation de démarrer**, le Scheduler peut réassigner le job : aucun code du dépôt n'a été exécuté. S'il disparaît **après l'autorisation** sans résultat confirmé, l'issue du job est `indeterminate` par défaut et aucun retry automatique n'est lancé. Un résultat tardif de la même tentative peut encore résoudre cet état. Les jobs dépendants attendent une vérification ; un opérateur doit contrôler les éventuels effets externes avant toute nouvelle exécution.
- En V1, `retry.worker_loss: unsafe` dans le YAML v2 autorise explicitement une nouvelle tentative après perte d'un worker déjà autorisé, dans la limite globale de trois tentatives. L'ancienne tentative reste `indeterminate` dans l'historique et son résultat tardif ne remplace pas celui de la nouvelle. Les effets externes peuvent être répétés ; la valeur par défaut `never` évite cette relance automatique.
- Un compte RabbitMQ distinct par worker est requis dès la V1. La perte d'un worker ne doit pas permettre de lire les ordres d'un autre worker ni d'usurper ses événements.
- Le socket Docker donne au worker le contrôle du démon de son hôte. La séparation réseau du conteneur ne suffit pas à isoler PostgreSQL sur un hôte partagé ; une installation de production place les workers et le plan de contrôle sur des hôtes distincts.

Détails techniques : [ARCH-02](../docs/architecture/components/messaging/02-rabbitmq-architecture.md), [ARCH-09](../docs/architecture/components/worker/09-worker-architecture.md), [ARCH-11](../docs/architecture/components/scheduler/11-scheduler-architecture.md).
