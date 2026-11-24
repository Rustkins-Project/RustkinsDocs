---
id: ADR-0001
title: "Les workers communiquent uniquement avec le Scheduler, sans accès à PostgreSQL"
status: accepted
topics: [architecture, worker, scheduler, rabbitmq, security]
applies_to: [all]
decided_at: 2026-11-20
approved_by: [T-Rogier]
supersedes: []
related_work_items: []
references:
  - "https://github.com/Rustkins-Project/RustkinsDocs/pull/18"
  - "https://github.com/Rustkins-Project/RustkinsDocs/pull/18#pullrequestreview-5992533435"
---

# Les workers communiquent uniquement avec le Scheduler, sans accès à PostgreSQL

## Contexte

Le worker exécute du code venant des dépôts. S'il accède à PostgreSQL, un job malveillant peut récupérer ses identifiants et atteindre toute la base : utilisateurs, tokens, état de tous les projets.

Vision produit : **le worker écoute le Scheduler, lui signale quand il a fini un job, et le Scheduler lui envoie les jobs suivants.**

## Décision

- Les workers **n'ont aucun accès à PostgreSQL**.
- Le **Scheduler est le seul à écrire les transitions et résultats d'exécution** remontés par les workers (jobs, steps, métadonnées de logs et d'artifacts). L'API peut créer les enregistrements initiaux d'un run selon la version.
- Scheduler et workers communiquent **uniquement via RabbitMQ** :

| Sens | Message | Rôle | Périmètre |
| --- | --- | --- | --- |
| Scheduler → Worker | `job.assigned` | Ordre autonome contenant le dépôt et le SHA, l'image et les steps | V0 et V1 |
| Scheduler → Worker | `job.start.accepted`, `job.start.rejected` | Autorisation ou refus d'exécuter une tentative | V0 et V1 |
| Worker → Scheduler | `job.start.requested` | Demande d'autorisation pour la livraison et la tentative en cours | V0 et V1 |
| Worker → Scheduler | `job.finished` | Résultat du job | V0 et V1 |
| Scheduler → Worker | `cancel.job` | Annulation | V1 |
| Worker → Scheduler | `worker.registered`, `worker.heartbeat`, `step.finished` | Capacité, signe de vie et avancement des steps | V1 |

À la réception de `job.finished`, le Scheduler vérifie que l'événement est cohérent (bon worker, bonne tentative), écrit le résultat, libère les ressources réservées le cas échéant et envoie les jobs suivants.

Avant de lancer le conteneur, le worker envoie `job.start.requested` avec un `start_request_id` propre à la livraison de `job.assigned`, puis attend la réponse correspondante. Le Scheduler valide la demande et enregistre durablement l'autorisation de cette tentative avec le `start_request_id` avant de répondre `job.start.accepted`. Cet enregistrement marque la frontière de retry, même si le worker n'a pas encore reçu la réponse. Une retransmission avec le même ID sur la tentative encore active reçoit à nouveau `job.start.accepted` sans nouvelle autorisation ; une autre demande ou une tentative périmée reçoit `job.start.rejected`. Le worker n'exécute le job que si l'acceptation correspond à sa demande en attente. Aucun registre durable des jobs n'est conservé sur le worker.

Les workers continuent d'écrire les logs dans RustFS et, dès la V1, les artifacts.

## Alternatives

- **Workers connectés à PostgreSQL** : rejeté, surface d'attaque trop large.
- **API interne dédiée aux workers** : même isolation, mais un service de plus alors que RabbitMQ est déjà là.

## Conséquences

- Les droits RabbitMQ de chaque worker sont limités à ses propres files et à la publication de ses événements. Le Scheduler authentifie le compte RabbitMQ émetteur et vérifie qu'il correspond au `worker_id` annoncé.
- Un seul composant décide et écrit les transitions d'exécution : plus simple à comprendre et à tester.
- En V1, le job arrive sur le worker où les ressources ont été réservées.
- Une panne du transport peut retarder les échanges ; les documents propres à chaque version détaillent la livraison et la reprise.
- Si le worker disparaît **avant l'autorisation de démarrer**, le Scheduler peut réassigner le job : aucun code du dépôt n'a été exécuté. S'il disparaît **après l'autorisation** sans résultat confirmé, l'issue du job est `indeterminate` par défaut et aucun retry automatique n'est lancé. Un résultat tardif de la même tentative peut encore résoudre cet état. Les jobs dépendants attendent une vérification ; un opérateur doit contrôler les éventuels effets externes avant toute nouvelle exécution.
- En V1, `retry.worker_loss: unsafe` dans le YAML v2 autorise explicitement une nouvelle tentative après perte d'un worker déjà autorisé, dans la limite globale de trois tentatives. L'ancienne tentative reste `indeterminate` dans l'historique et son résultat tardif ne remplace pas celui de la nouvelle. Les effets externes peuvent être répétés ; la valeur par défaut `never` évite cette relance automatique.
- Un compte RabbitMQ distinct par worker est requis dès la V1. La perte d'un worker ne doit pas permettre de lire les ordres d'un autre worker ni d'usurper ses événements.
- Le socket Docker donne au worker le contrôle du démon de son hôte. La séparation réseau du conteneur ne suffit pas à isoler PostgreSQL sur un hôte partagé ; une installation de production place les workers et le plan de contrôle sur des hôtes distincts.

Détails techniques : [V0](../docs/versions/v0/overview.md#9-contrat-de-communication-entre-services), [V1](../docs/versions/v1/overview.md#9-contrat-de-communication-entre-services), [ARCH-02](../docs/architecture/components/messaging/02-rabbitmq-architecture.md), [ARCH-09](../docs/architecture/components/worker/09-worker-architecture.md), [ARCH-11](../docs/architecture/components/scheduler/11-scheduler-architecture.md).

## Références de validation

La [PR #18](https://github.com/Rustkins-Project/RustkinsDocs/pull/18), proposée par `SNEAXIII`, a reçu la [review `APPROVED` de `T-Rogier`](https://github.com/Rustkins-Project/RustkinsDocs/pull/18#pullrequestreview-5992533435) le **20 novembre 2026 à 13:18:39, heure de Paris** (`2026-11-20T12:18:39Z`). La review porte sur le dernier commit de la PR (`35f8ed7`) ; celle-ci a été fusionnée le **22 novembre 2026 à 23:02:01, heure de Paris** (`2026-11-22T22:02:01Z`). Le champ `decided_at` conserve la date de la review, conformément au schéma ADR qui accepte une date sans heure.
