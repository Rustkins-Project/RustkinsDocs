# Décisions d'architecture (ADR)

Une ADR formalise **une décision et ses conséquences**, pas une simple découverte ou étude.

- Template : [adr.md](../templates/adr.md)
- Contrat des métadonnées : [adr.schema.json](../schemas/adr.schema.json)
- Règles complètes : [knowledge-management.md](../docs/conventions/knowledge-management.md)

## Décisions

| ADR | Titre | Statut |
| --- | --- | --- |
| [ADR-0001](ADR-0001-worker-scheduler-communication.md) | Les workers communiquent uniquement avec le Scheduler, sans accès à PostgreSQL | `proposed` |
| [ADR-0002](ADR-0002-postgresql-authoritative-state-rabbitmq-transport.md) | PostgreSQL conserve l'état de référence, RabbitMQ transporte les messages | `proposed` |
| [ADR-0003](ADR-0003-scheduler-transactional-outbox.md) | Le Scheduler publie ses ordres V1 par outbox transactionnelle | `proposed` |
| [ADR-0004](ADR-0004-immutable-pipeline-versions.md) | Chaque run référence une version immuable du pipeline | `proposed` |

## Gouvernance obligatoire

- Toute **nouvelle ADR ou modification de décision** passe par une Pull Request.
- **Au moins une approbation humaine d'un autre membre de l'équipe** est requise avant fusion (Timothy, Alexis ou Loick, distinct de l'auteur). L'agent IA ne peut pas approuver.
- Une ADR n'est applicable qu'après **fusion sur main et approbation**. L'approbation d'une réponse Discord seule ne publie pas une ADR.
- Statuts : `proposed`, `accepted`, `rejected`, `superseded`.
- Une décision remplacée reste consultable : nouvelle ADR + liens `supersedes`, sans effacement du passé.
- Le champ `applies_to` permet de distinguer les versions de Rustkins.

## Passage manuel à `accepted`

1. L'agent prépare l'ADR avec `status: proposed`, `approved_by: []` et `decided_at: null`. La discussion et les corrections ont lieu sur la PR.
2. Quand la décision est prête à être approuvée, **un humain** pousse un commit sur la branche de la PR : `status: accepted`, `approved_by` avec le compte GitHub de l'approbateur humain et `decided_at` avec la date de son approbation prévue (`AAAA-MM-JJ`). Il peut aussi ajouter l'URL de la PR dans `references`. Ce commit peut être fait par le reviewer avant sa review finale ; l'auteur de l'ADR ne peut pas être son seul approbateur.
3. Après ce commit, attendre le nouveau résultat de `Validate documentation`. Un autre membre humain que l'auteur approuve **le dernier état de la PR**, puis un humain fusionne la PR sur `main`. Si la review finale a lieu un autre jour ou par une autre personne, corriger les métadonnées par un nouveau commit et demander une nouvelle approbation.

Le champ `accepted` dans une branche de PR n'est **pas encore applicable** : il le devient seulement après l'approbation humaine et la fusion sur `main`. Ne pas pousser le commit de métadonnées après la review finale : le ruleset actuel invalide les approbations devenues obsolètes après un nouveau commit. Les champs `approved_by` et `decided_at` facilitent la lecture ; la review GitHub et la fusion restent les preuves à vérifier. Un agent ne remplit pas lui-même ces champs pour prétendre qu'une décision a été approuvée.

Au 24 novembre 2026, le ruleset GitHub actif de `main` exige une approbation de l'équipe Rustkins pour `decisions/**`, ainsi que le contrôle `Validate documentation`. Il n'impose pas cette approbation à `knowledge/**`. Vérifier la configuration effective sur GitHub si elle change. Les rubriques « ADR-001 » dans les anciens documents d'architecture ne sont pas des ADR approuvées dans `decisions/`.
