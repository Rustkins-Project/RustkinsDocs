# Décisions d'architecture (ADR)

Une ADR formalise **une décision et ses conséquences**, pas une simple découverte ou étude.

- Template : [adr.md](../templates/adr.md)
- Contrat des métadonnées : [adr.schema.json](../schemas/adr.schema.json)
- Règles complètes : [knowledge-management.md](../docs/conventions/knowledge-management.md)

## Décisions

| ADR | Titre |
| --- | --- |
| [ADR-0001](ADR-0001-worker-scheduler-communication.md) | Les workers communiquent uniquement avec le Scheduler, sans accès à PostgreSQL |
| [ADR-0002](ADR-0002-postgresql-authoritative-state-rabbitmq-transport.md) | PostgreSQL conserve l'état de référence, RabbitMQ transporte les messages |
| [ADR-0003](ADR-0003-scheduler-transactional-outbox.md) | Le Scheduler publie ses ordres V1 par outbox transactionnelle |
| [ADR-0004](ADR-0004-immutable-pipeline-versions.md) | Chaque run référence une version immuable du pipeline |

Le statut à jour est celui du frontmatter de chaque ADR.

## Gouvernance obligatoire

- Toute **nouvelle ADR ou modification de décision** passe par une Pull Request.
- **Au moins une approbation humaine d'un autre membre de l'équipe** est requise avant fusion (Timothy, Alexis ou Loick, distinct de l'auteur). L'agent IA ne peut pas approuver.
- Une ADR n'est applicable qu'après **fusion sur main, approbation et inscription de `accepted` par le workflow de finalisation**. L'approbation d'une réponse Discord seule ne publie pas une ADR.
- Statuts : `proposed`, `accepted`, `rejected`, `superseded`.
- Une décision remplacée reste consultable : nouvelle ADR + liens `supersedes`, sans effacement du passé.
- Le champ `applies_to` permet de distinguer les versions de Rustkins. Pour une décision valable dès V0 et conservée en V1, utiliser `[all]` : son principe reste applicable aux versions futures jusqu'à décision contraire. Une décision introduite plus tard, comme l'outbox V1, garde un périmètre explicite qui n'inclut pas V0.

## Finalisation automatique après fusion

1. L'agent prépare l'ADR avec `status: proposed`, `approved_by: []` et `decided_at: null`. La discussion et les corrections ont lieu sur la PR.
2. Un autre membre humain de l'équipe approuve le dernier commit de la PR, puis la PR est fusionnée sur `main`. Aucun commit de métadonnées d'approbation n'est demandé au reviewer.
3. Le workflow [Finalize approved ADRs](../.github/workflows/adr-finalization.yml) retrouve la PR fusionnée et ses reviews GitHub, retient les approbations humaines valides du dernier commit, puis écrit `status: accepted`, les comptes dans `approved_by`, le jour de la dernière approbation (heure de Paris) dans `decided_at` et les liens de preuve dans `references`. Il valide le dépôt et pousse un commit distinct sur `main` avec l'identité du bot.

Si la finalisation échoue, l'ADR reste `proposed` et la décision n'est pas encore publiée. Corriger la cause et relancer le workflow avec le SHA du commit de fusion de la PR. Les champs `approved_by` et `decided_at` facilitent la lecture ; la review GitHub reste la preuve à vérifier. Un agent ne remplit pas lui-même ces champs pour prétendre qu'une décision a été approuvée. Une ADR remplacée reste traçable ; son passage à `superseded` et le lien depuis l'ADR de remplacement restent dans la PR soumise à review.

Le workflow exige une GitHub App dédiée installée uniquement sur ce dépôt, avec la permission **Contents: Read and write**. Configurer la variable Actions `ADR_FINALIZER_CLIENT_ID`, le secret Actions `ADR_FINALIZER_PRIVATE_KEY` et ajouter **cette App uniquement** en bypass `Always allow` du ruleset de `main` pour permettre son commit direct. Le token temporaire est limité à `contents: write` et créé après la validation. Le ruleset exige une review humaine des chemins `.github/workflows/**`, `scripts/**` et `requirements.txt`, qui contrôlent cette automatisation. Ne pas accorder de bypass à tous les workflows Actions ni à tous les collaborateurs.

Au 24 novembre 2026, le ruleset GitHub actif de `main` exige une approbation de l'équipe Rustkins pour `decisions/**`, `.github/workflows/**`, `scripts/**` et `requirements.txt`, ainsi que le contrôle `Validate documentation`. Il n'impose pas cette approbation à `knowledge/**`. Vérifier la configuration effective sur GitHub si elle change. Les rubriques « ADR-001 » dans les anciens documents d'architecture ne sont pas des ADR approuvées dans `decisions/`.
