---
id: ADR-0002
title: "PostgreSQL conserve l'état de référence, RabbitMQ transporte les messages"
status: proposed
topics: [architecture, postgresql, rabbitmq, runtime]
applies_to: [all]
decided_at: null
approved_by: []
supersedes: []
related_work_items: []
references: []
---

# PostgreSQL conserve l'état de référence, RabbitMQ transporte les messages

## Contexte

Les demandes de run, l'état du DAG et les résultats doivent rester consultables après une panne ou un redémarrage de RabbitMQ. Le broker livre des ordres et des événements de manière asynchrone ; sa file ne constitue pas un historique fiable des transitions métier. Les vues V0 et V1 ainsi que la spécification YAML v3 décrivent PostgreSQL comme source de vérité de l'exécution, mais ce choix n'a pas encore été approuvé dans une ADR.

Cette proposition concerne la responsabilité des deux systèmes. La frontière de confiance des Workers et la propriété des écritures d'exécution sont traitées dans [ADR-0001](ADR-0001-worker-scheduler-communication.md).

## Décision

- PostgreSQL conserve l'état durable de référence : définitions et versions de pipeline, runs, tentatives, transitions et métadonnées nécessaires à la reprise. Le contenu binaire des logs et des artéfacts reste hors de cette décision.
- RabbitMQ transporte les commandes d'exécution et les événements. La présence, l'absence ou l'ordre d'un message dans une file ne fait pas autorité sur l'état d'un run.
- Après un redémarrage, le Scheduler reconstruit son travail depuis l'état PostgreSQL et réconcilie les messages selon le contrat de la version du produit.
- Les consommateurs valident l'identité, la tentative et la transition avant d'écrire l'état. Une livraison répétée ne doit pas créer une seconde transition métier.

Les garanties de publication des ordres du Scheduler en V1 font l'objet d'[ADR-0003](ADR-0003-scheduler-transactional-outbox.md). La V0 conserve son contrat de publication et de réconciliation propre.

## Alternatives

- **RabbitMQ comme état de référence** : nécessiterait une reconstruction de l'état métier depuis les messages et ferait dépendre l'historique des politiques de rétention et de livraison du broker.
- **PostgreSQL seul avec scrutation, sans broker** : simplifierait l'infrastructure mais reporterait le transport et la réactivité des échanges sur la base.
- **État durable propre à chaque Worker** : compliquerait la reprise et la coordination et élargirait la frontière de confiance décrite dans ADR-0001.

Ces alternatives explicitent l'arbitrage proposé ; les documents historiques ne prouvent pas qu'elles ont déjà été formellement rejetées par l'équipe.

## Conséquences

- Une panne RabbitMQ retarde la circulation des messages sans effacer l'état d'exécution déjà validé dans PostgreSQL.
- La livraison au moins une fois demande des traitements idempotents et une réconciliation après panne.
- PostgreSQL devient une dépendance de disponibilité du plan de contrôle ; ses sauvegardes et migrations exigent une attention particulière.
- Les rôles de l'API, du Scheduler et des Workers ainsi que les contrats de messages restent détaillés dans les spécifications par version, sans être dupliqués ici.

## Références

- [Vue V0](../docs/versions/v0/overview.md#9-contrat-de-communication-entre-services) et [vue V1](../docs/versions/v1/overview.md#9-contrat-de-communication-entre-services).
- [Architecture du runtime](../docs/architecture/components/01-runtime-lifecycle.md) et [architecture RabbitMQ](../docs/architecture/components/messaging/02-rabbitmq-architecture.md).
- [Modèle de données V1](../docs/architecture/data-model/10-data-model-reference.md) et [spécification YAML v3](../docs/specifications/pipeline/yaml-v3.md).
