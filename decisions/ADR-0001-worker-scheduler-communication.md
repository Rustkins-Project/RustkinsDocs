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
| Worker → Scheduler | `worker.registered`, `worker.heartbeat` | Déclaration de la capacité, signe de vie |
| Worker → Scheduler | `job.started`, `step.finished`, `job.finished` | Avancement et résultat du job (statut, logs, artifacts, consommation) |

À la réception de `job.finished`, le Scheduler vérifie que l'événement est cohérent (bon worker, bonne tentative), écrit le résultat, libère les ressources et envoie les jobs suivants.

Les workers continuent d'écrire les logs et les artifacts dans RustFS.

## Alternatives

- **Workers connectés à PostgreSQL** : rejeté, surface d'attaque trop large.
- **API interne dédiée aux workers** : même isolation, mais un service de plus alors que RabbitMQ est déjà là.

## Conséquences

- Un worker compromis ne peut qu'envoyer des événements, que le Scheduler valide.
- Un seul composant écrit l'état : plus simple à comprendre et à tester.
- Le job arrive sur le worker où les ressources ont été réservées.
- Si RabbitMQ est indisponible, les états remontent en retard. Le worker garde `job.finished` en local jusqu'à confirmation pour ne pas le perdre.
- À arbitrer : un compte RabbitMQ par worker, pour qu'un worker ne puisse pas se faire passer pour un autre.

Détails techniques : [ARCH-02](../docs/architecture/components/messaging/02-rabbitmq-architecture.md), [ARCH-09](../docs/architecture/components/worker/09-worker-architecture.md), [ARCH-11](../docs/architecture/components/scheduler/11-scheduler-architecture.md).
