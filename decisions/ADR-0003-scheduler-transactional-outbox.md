---
id: ADR-0003
title: "Le Scheduler publie ses ordres V1 par outbox transactionnelle"
status: proposed
topics: [architecture, scheduler, rabbitmq, outbox, reliability]
applies_to: [V1]
decided_at: null
approved_by: []
supersedes: []
related_work_items: []
references: []
---

# Le Scheduler publie ses ordres V1 par outbox transactionnelle

## Contexte

En V1, le Scheduler doit faire évoluer l'état d'un job dans PostgreSQL et envoyer à un Worker l'ordre correspondant. Une écriture en base suivie d'une publication directe dans RabbitMQ laisse une fenêtre où la base est mise à jour mais où aucun ordre n'est livré. Une publication avant le commit crée le risque inverse. La V0 décrit une publication directe avec mécanismes de réconciliation ; elle ne possède pas de table d'outbox. Cette ADR propose la garantie supplémentaire prévue par l'architecture V1.

## Décision

- Le Scheduler écrit chaque ordre ou contrôle qui modifie l'exécution, notamment `job.assigned`, `job.start.accepted` et `cancel.job`, dans un `OutboxMessage` au cours de la même transaction PostgreSQL que la transition concernée.
- Un Outbox Publisher, sous-composant du Scheduler, publie les messages en attente dans RabbitMQ et marque leur publication après confirmation du broker.
- Une publication peut être répétée après panne ; l'identifiant de message et l'état durable permettent au destinataire de traiter la répétition sans exécuter deux fois une décision.
- Les événements émis par les Workers et les fragments de logs ne passent pas par cette outbox PostgreSQL. Leur confirmation, leur consommation et leur persistance suivent les contrats de messagerie V1.

Cette décision complète [ADR-0002](ADR-0002-postgresql-authoritative-state-rabbitmq-transport.md) et le protocole de démarrage de [ADR-0001](ADR-0001-worker-scheduler-communication.md). Elle ne modifie pas rétroactivement le transport V0.

## Alternatives

- **Publication directe après commit, comme en V0** : nécessite une réconciliation pour détecter et réparer la fenêtre entre commit et publication ; la garantie V1 serait moins explicite.
- **Publication avant commit** : un Worker pourrait recevoir un ordre pour un état qui n'a finalement pas été validé.
- **Transaction distribuée entre PostgreSQL et RabbitMQ** : complexité opérationnelle supérieure pour un besoin couvert par outbox et idempotence.

Ces options décrivent le compromis proposé, sans leur attribuer une validation ou un rejet historique non documenté.

## Conséquences

- Une panne de RabbitMQ n'annule pas une transition déjà committée ; l'ordre reste à publier.
- L'outbox garantit la persistance de l'intention d'envoi, pas une livraison exactement une fois. Les Workers et le Scheduler doivent traiter les redélivraisons.
- La table d'outbox, son publisher, ses retries et sa supervision ajoutent du travail et du stockage en V1.
- Les formats de messages, files, délais et règles d'ACK restent dans l'[architecture RabbitMQ V1](../docs/architecture/components/messaging/02-rabbitmq-architecture.md).

## Références

- [Contrat de communication V0](../docs/versions/v0/overview.md#9-contrat-de-communication-entre-services) et [contrat V1](../docs/versions/v1/overview.md#9-contrat-de-communication-entre-services).
- [Architecture RabbitMQ V1](../docs/architecture/components/messaging/02-rabbitmq-architecture.md#10-transactional-outbox).
- [Architecture du Scheduler](../docs/architecture/components/scheduler/11-scheduler-architecture.md) et [modèle de données V1](../docs/architecture/data-model/10-data-model-reference.md#outbox_message).
