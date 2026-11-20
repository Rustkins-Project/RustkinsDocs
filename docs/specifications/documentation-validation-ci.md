---
id: DOC-0041
title: "Cahier des charges — validation documentaire et CI de RustkinsDocs"
type: specification
status: draft
summary: "Spécification d'implémentation du validateur Python, des schémas, des contrôles Markdown et de la CI GitHub Actions pour RustkinsDocs."
topics: [documentation, validation, ci, github-actions, python, governance]
applies_to: [all]
---

# Cahier des charges — validation documentaire et CI de RustkinsDocs

> **Statut :** spécification à implémenter, pas compte rendu de fonctionnalités déjà livrées.
> **Périmètre :** uniquement le dépôt `Rustkins-Project/RustkinsDocs`.
> **Livraison attendue :** une PR technique sur la branche portant cette spécification, sans merge automatique.
> **Priorité :** fidélité aux décisions ci-dessous, simplicité, diagnostics utiles et tests réels.

## 1. Objectif et principes

Développer une validation documentaire fiable, rapide, déterministe et exécutable de manière identique sur Windows et dans GitHub Actions.

- Valider **tout le dépôt documentaire concerné**, pas seulement les fichiers modifiés.
- Séparer les contrôles **locaux** (schémas, structure, références, liens) des contrôles **historiques** (conservation des IDs par comparaison à `main`).
- Lancer la même commande Python en local et en CI, avec des options explicites.
- Bloquer les erreurs structurelles ; émettre des avertissements non bloquants pour les références vers des documents obsolètes.
- Ne jamais supposer qu'un statut YAML prouve une validation humaine ou un résultat technique.
- Corriger les éventuelles anomalies documentaires existantes nécessaires à une CI verte, sans réécrire les contenus métier pour les « améliorer ».
- Ne pas créer un framework de validation générique, un service réseau, ni un package publiable.

**Hors périmètre absolu :** `RustkinsActivity`. Ne pas ajouter de CI ni de règles de PR à ce dépôt ; ses pushes directs vers `main` restent possibles avec sa validation locale Rust actuelle.

**Hors périmètre de cette PR :** activation effective des protections/rulesets GitHub, création d'une équipe de reviewers, approbation humaine d'ADR, merge de la PR. Préparer les vérifications CI nécessaires mais laisser la configuration des règles de protection aux administrateurs après recette.

## 2. Cartographie des fichiers

| Chemin | Rôle | Validation |
| --- | --- | --- |
| `docs/**/*.md` hors `README.md` et hors `docs/operations/**` | Documents de référence `DOC-xxxx` | Frontmatter `document.schema.json`, cohérence du `type`, corps libre, liens, références |
| `docs/operations/**/*.md` hors `README.md` | Runbooks `RUN-xxxx` | Frontmatter `runbook.schema.json`, sections imposées, liens, références |
| `decisions/**/*.md` hors `README.md` | ADR `ADR-xxxx` | Frontmatter `adr.schema.json`, sections imposées, graphe de remplacement, liens |
| `knowledge/**/*.md` hors `README.md` | Connaissances `KNOW-xxxx` | Frontmatter `knowledge.schema.json`, corps libre, liens |
| `README.md`, `INDEX.md` et `**/README.md` hors `research/` | Navigation | Pas de frontmatter obligatoire ; liens/fichiers/ancres à contrôler |
| `templates/document.md`, `templates/adr.md`, `templates/knowledge.md`, `templates/runbook.md` | Modèles non publiés | Frontmatter obligatoire, schéma correspondant, structure ADR/RUN, liens réels ; aucune unicité/résolution des références documentaires |
| `research/**` | Recherche exploratoire | **Exclusion totale** : ni frontmatter, ni liens sortants, ni métadonnées, ni structure |
| `schemas/*.schema.json` | Contraintes de frontmatter | JSON valide et schéma vérifiable, test des quatre schémas |
| Fichiers locaux non Markdown (PNG, MMD, DOC, DOCX, etc.) | Cibles de liens | Leur existence est contrôlée quand un fichier Markdown validé les référence ; ne pas interpréter leur contenu |

La vérification d'un lien émis depuis une source validée vers `research/` peut se limiter à l'existence de sa cible : **ne pas valider le contenu du dossier `research/`**.

Le répertoire `docs/operations/` ne doit plus être traité comme un `DOC` : tout nouveau runbook publié reçoit un identifiant `RUN`. Garder les README de navigation exempts de frontmatter, y compris `docs/operations/README.md`.

Ne pas parcourir `.git/`, les environnements virtuels Python, les caches, les fixtures de tests ni d'autres fichiers techniques comme des documents publiés.

## 3. Frontmatter et JSON Schema

### 3.1 Quatre schémas distincts

Utiliser et adapter :

- `schemas/document.schema.json` : exclusivement `DOC-[0-9]{4,}`.
- `schemas/adr.schema.json` : exclusivement `ADR-[0-9]{4,}`.
- `schemas/knowledge.schema.json` : exclusivement `KNOW-[0-9]{4,}`.
- **Créer `schemas/runbook.schema.json`** : exclusivement `RUN-[0-9]{4,}`, schéma **indépendant** de `document.schema.json`.

Le schéma runbook reprend initialement les métadonnées pertinentes d'un document : `id`, `title`, `type`, `status`, `summary`, `topics`, `applies_to` et les champs de référence facultatifs appropriés. Imposer `type: operation`. Les statuts sont `draft`, `approved` et `deprecated`. Conserver la validation métier des sections dans le parseur Markdown, **pas** dans JSON Schema.

Dans `document.schema.json`, éviter d'autoriser `type: operation` pour les documents classiques si cela contredit l'exclusivité des runbooks. Vérifier également la cohérence du `type` avec les emplacements fonctionnels existants : `docs/architecture` → `architecture` ; `docs/specifications` → `specification` ; `docs/conventions` → `convention` ; `docs/project-management` → `project-management` ; `docs/versions` → `version` ; `docs/cross-cutting` → `cross-cutting`. Les README restent à part.

Préserver les exigences existantes utiles : champs requis, énumérations de statut/type, `additionalProperties: false`, tableaux uniques, valeurs non vides, `summary` limité à 500 caractères, `related_work_items` positifs, dates et URI au bon format. Utiliser JSON Schema **draft 2020-12** et un `FormatChecker` effectif pour ne pas ignorer les formats `date` et `uri`.

Le YAML est d'abord parsé comme un objet, puis passé au schéma. Signaler proprement les erreurs YAML, un frontmatter manquant, plusieurs métadonnées identiques ou les clés YAML dupliquées. Prendre en charge UTF-8, LF/CRLF et les dates YAML automatiquement transformées en objets `date` : soit normalisation contrôlée en ISO-8601, soit consigne documentée et testée d'écriture entre guillemets.

### 3.2 Versions du produit

`applies_to` accepte **uniquement** `V0`, `V1`, `V2`, `V3` et `all`. Toute autre valeur, comme `V4` ou `V99`, est bloquante jusqu'à évolution explicite de cette liste.

- Plusieurs versions connues sont acceptées, sans doublons.
- `all` doit être **la seule valeur** du tableau.
- La liste autorisée doit avoir **une source de vérité explicite dans la configuration Python** ; garder les contraintes structurelles et le motif de format dans les schémas.
- Appliquer la règle aux quatre catégories `DOC`, `ADR`, `KNOW`, `RUN`.
- Ne pas confondre `applies_to` (versions **du produit Rustkins**) avec `specification_version` (version éventuelle d'un contrat YAML).

### 3.3 Identifiants et templates

Les IDs publiés doivent être uniques dans leur espace global et être stables :
`DOC-xxxx`, `RUN-xxxx`, `ADR-xxxx`, `KNOW-xxxx`, avec au moins quatre chiffres décimaux.

Les valeurs réservées `DOC-0000`, `RUN-0000`, `ADR-0000` et `KNOW-0000` sont **autorisées seulement dans les templates**. Un identifiant numérique égal à zéro est interdit pour tout document publié.

- Un `DOC` hors `docs/operations` ne peut pas avoir `RUN-xxxx` et inversement.
- Une ADR / connaissance ne peut pas utiliser un ID d'une autre catégorie.
- Détecter et afficher les deux chemins en cas de doublon.
- Les placeholders des templates ne comptent jamais dans le registre des documents publiés.

Créer le frontmatter manquant de `templates/runbook.md` avec `id: RUN-0000`, `type: operation`, `status: draft`, `applies_to: [all]` et les autres champs requis du nouveau schéma. Conserver le corps utile du template.

## 4. Contenu Markdown

Utiliser un parseur Markdown réel (par exemple `markdown-it-py`), et non une simple regex appliquée à tout le texte. En particulier, ignorer les titres et liens qui figurent dans des blocs de code ou du code inline.

### 4.1 ADR : sections `H2` obligatoires

Les ADR publiées et leur template doivent contenir, avec contenu non vide :

- `## Contexte`
- `## Décision`
- `## Alternatives`
- `## Conséquences`

Les autres sections, dont `Références`, sont facultatives. Autoriser des sous-sections ; ne pas imposer un ordre strict. Vérifier le niveau `H2`, pas simplement la présence textuelle du titre.

### 4.2 Runbooks : sections `H2` obligatoires

Les runbooks publiés et `templates/runbook.md` doivent contenir, avec contenu non vide :

- `## Objectif`
- `## Préparation`
- `## Étapes`
- `## Vérifications`

`## Retour arrière` et `## Références` sont facultatives mais, **si présentes**, ne doivent pas être vides. Autoriser des sections supplémentaires sans ordre strict.

Une section est non vide si elle contient du contenu Markdown réel (prose, liste, commande/code utile, etc.), pas uniquement des espaces ou des commentaires HTML. Ne pas essayer de juger automatiquement la pertinence ou la sécurité réelle de la procédure.

### 4.3 DOC et KNOW

**Aucune structure de sections obligatoire** pour les documents classiques et les connaissances. Valider leur frontmatter, liens, références et identifiants.

## 5. Références croisées, existence et statuts

### 5.1 Références structurées

`related_docs` n'accepte que des IDs existants, **jamais des chemins** :

```yaml
related_docs:
  - DOC-0021
  - RUN-0001
```

- Format des éléments : `^(DOC|RUN)-[0-9]{4,}$`.
- Vérifier que chaque ID visé existe dans les documents publiés de la PR.
- Refuser les doublons et les auto-références.
- Ne pas créer de champ `related_runbooks`.
- Conserver `related_adrs` pour les références aux ADR, avec contrôle d'existence.
- Vérifier `supersedes` pour les ADR selon le graphe décrit au chapitre 6.
- Les références vers des work items Azure ou des URL externes ne nécessitent **pas** de requête distante.

Ne pas ajouter automatiquement de champs arbitraires dans des schémas qui ne les possèdent pas ; documenter les champs réellement disponibles.

### 5.2 Liens vers des documents obsolètes

Ne pas bloquer un lien documentaire valide dont la cible est obsolète. Émettre un **warning** si une référence résolue pointe vers :

| Catégorie | Statut obsolète |
| --- | --- |
| DOC | `deprecated` |
| RUN | `deprecated` |
| ADR | `superseded` |
| KNOW | `outdated` |

Un identifiant cible **inexistant** reste une **erreur bloquante**.

**Exception :** le champ `supersedes` est destiné à référencer une ADR remplacée ; ne jamais émettre ce warning pour cette relation. Un lien Markdown vers un document obsolète peut aussi être signalé si la cible est reconnue comme document publié.

## 6. Graphe de remplacement des ADR

Les quatre statuts existants sont `proposed`, `accepted`, `rejected` et `superseded`.

- Toute référence `supersedes` doit viser une ADR existante.
- Aucune ADR ne peut se remplacer elle-même.
- Aucun cycle de remplacement n'est autorisé, même via plusieurs ADR.
- Lorsqu'une ADR `accepted` référence une ADR dans `supersedes`, **chaque cible** doit être `superseded` ; sinon erreur.
- Toute ADR `superseded` doit être référencée par **au moins une ADR `accepted`** qui la remplace ; sinon erreur.
- Une ADR `proposed` peut déclarer les remplacements envisagés sans modifier le statut des anciennes ADR tant qu'elle n'est pas acceptée.
- Une ADR acceptée peut remplacer **plusieurs** ADR ; une ancienne ADR peut être remplacée par **plusieurs** ADR acceptées (relation plusieurs-à-plusieurs).
- Vérifier les règles sur l'**état final de l'ensemble des fichiers** de la PR, afin d'autoriser un remplacement et le changement de statut associé dans la même PR.

Le `approved_by` et `decided_at` d'une ADR acceptée restent soumis au schéma actuel : approbateur non vide et date valide. **Ces champs ne valent pas preuve de review GitHub**.

## 7. Liens Markdown, fichiers et ancres

### 7.1 Liens locaux : vérification bloquante

- Vérifier l'existence des chemins relatifs pointés par les liens Markdown, les images et les références vers des fichiers annexes (`.mmd`, `.png`, `.doc`, `.docx`, etc.).
- Vérifier les liens avec définition de référence, les liens et images inline ainsi que les ancres sans nom de fichier (`#section`).
- Résoudre un chemin relatif depuis le répertoire du document **source**, et non depuis la racine du processus Python.
- Décoder correctement les caractères percent-encoded ; prendre en charge les chemins UTF-8, espaces, accents et la syntaxe Markdown habituelle.
- Contrôler que les chemins de cibles locales ne sortent pas du dépôt de manière imprévue ; signaler clairement les chemins invalides.
- Lorsqu'une cible est du Markdown, vérifier également que l'ancre `#fragment` existe.
- Ne pas essayer d'interpréter le contenu des fichiers binaires ou Mermaid.

### 7.2 Ancres compatibles GitHub

Reproduire les conventions de slug GitHub pour les titres Markdown : espaces, ponctuation, accents/Unicode, casse, titres dupliqués avec suffixes numériques, encodage d'URL. Tester des exemples représentatifs, y compris `#installation`, les titres répétés, les caractères accentués et les liens vers une section du même document.

Éviter les fausses erreurs issues de titres dans des blocs de code et de faux liens dans du code inline. Traiter les liens de navigation des README/INDEX comme les autres liens locaux.

### 7.3 Liens externes : syntaxe uniquement

Pour `https://...`, `http://...` et les URL externes autorisées par les schémas :

- Contrôler une **syntaxe valide** selon le type de champ/lien.
- **Aucun appel HTTP**, aucune requête HEAD, aucun retry réseau.
- Aucune erreur due à une page privée, un rate-limit ou une indisponibilité externe.
- Pas de tentative de vérifier à distance l'existence des ancres.

## 8. Conservation des identifiants : contrôle historique

Après la migration initiale des doublons (PR #19 déjà fusionnée), les documents identifiés sont **inaltérables en tant qu'identités** :

| Modification | Attendu |
| --- | --- |
| Mettre à jour le texte ou un statut autorisé | Autorisé |
| Déplacer/renommer un fichier en conservant exactement son ID | Autorisé |
| Changer un ID déjà publié | Erreur bloquante |
| Supprimer un `DOC`, `RUN`, `ADR` ou `KNOW` déjà publié | Erreur bloquante |
| Réutiliser un ID publié pour un autre document | Interdit |
| Déprécier un document en conservant le fichier | Autorisé |
| Supprimer un README, un template, un fichier `research/` | Autorisé |

En CI PR, comparer le registre d'identifiants **de la branche de base `main`** au registre de la version courante :

1. Extraire les IDs publiés de la base, sans attribuer d'ID à des README/templates/research.
2. Extraire les IDs de la branche à valider.
3. Toute identité de la base doit être présente **exactement une fois** dans l'état cible.
4. Les nouveaux IDs sont possibles et doivent respecter toutes les validations.
5. Ne pas se fonder uniquement sur les noms de fichiers : un déplacement avec même ID doit passer.
6. Afficher les diagnostics avec ancien et nouveau chemin ou ID quand ils sont disponibles.
7. Si la base historique comporte déjà des anomalies, les signaler sans inventer de migrations automatiques ; la PR #19 corrige les doublons connus.

Le mode local `python scripts/validate_docs.py` exécute toutes les validations **sans nécessiter `main` distant**. Une option explicite, par exemple `--base-ref origin/main`, ajoute le contrôle historique. Le comportement sur `push` à `main` peut faire la validation complète de l'état courant sans exiger une base distante.

**Attention :** utiliser une référence Git stable et accessible à la CI (fetch suffisant ou SHA de la base PR), et comparer l'état effectivement testé. Ne pas bloquer un simple déplacement légitime. Ne pas tenter de consulter tout l'historique Git à chaque exécution pour reconstituer les IDs historiques déjà retirés : la règle de non-suppression commence dès le référentiel conforme.

## 9. Architecture d'implémentation proposée

Solution minimale suggérée (l'agent peut adapter les noms si l'architecture finale reste simple) :

```text
scripts/
  validate_docs.py
  doccheck/
    __init__.py
    frontmatter.py
    rules.py
    links.py
tests/
  test_validation.py
  fixtures/
schemas/
  document.schema.json
  adr.schema.json
  knowledge.schema.json
  runbook.schema.json
templates/
  document.md
  adr.md
  knowledge.md
  runbook.md
.github/
  workflows/
    docs-validation.yml
requirements-dev.txt
```

Dépendances recommandées : `PyYAML`, `jsonschema`, `markdown-it-py`, `pytest`. Limiter strictement les dépendances ; utiliser la bibliothèque standard pour les fichiers, chemins, diffs locaux et diagnostics quand c'est suffisant.

Une logique de validation compréhensible par étapes :

1. Découverte et classification des fichiers (avec exclusions explicites).
2. Extraction/parsing du frontmatter.
3. Validation par schéma et contrôles de version/chemin/ID.
4. Construction du registre des IDs publiés.
5. Résolution des références croisées et contrôle des statuts.
6. Validation des sections du corps Markdown.
7. Contrôle des liens locaux et ancres, syntaxe des liens externes.
8. Contrôle historique optionnel avec la base Git.
9. Émission des erreurs/warnings et code de sortie final.

Ne pas ajouter de serveur, de base de données, de cache distribué, de framework de plugins, de service web, ni de CLI complexe.

## 10. Interface et diagnostics du validateur

Commandes minimales attendues :

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_docs.py
python scripts/validate_docs.py --base-ref origin/main
python -m pytest -q
```

- `0` : aucune erreur (warnings tolérés).
- `1` ou autre code non nul : au moins une erreur bloquante, problème de configuration ou erreur de lecture.
- Pour chaque erreur/warning, indiquer au minimum fichier, ligne si connue, catégorie et message actionnable.
- Afficher un résumé final : nombre de documents vérifiés, erreurs, warnings.
- Sur GitHub Actions, utiliser les annotations `::error` / `::warning` si possible, sans exposer de données sensibles dans les logs.
- Permettre à Codex/Claude Code et à un développeur d'utiliser la commande locale comme vérification avant PR.
- Pas de pre-commit obligatoire en V1 de cette CI ; éventuellement ajouté plus tard.

## 11. Tests automatisés attendus

Prévoir de **vrais tests automatisés** avec fixtures isolées. Cas minimum :

- Quatre frontmatters valides, quatre schémas valides, champs requis/valeurs interdites et YAML mal formé.
- Clé YAML dupliquée, dates `date` et URI, Unicode/CRLF.
- IDs uniques, IDs en doublon, mauvais préfixe/emplacement, ID `0000` refusé dans un document publié et accepté dans un template.
- `applies_to` : `[V0]`, `[V0,V1,V2]`, `[all]` acceptés ; `[V4]`, `[V1,all]`, doublons refusés.
- `related_docs` : référence DOC/RUN valide, chemin relatif invalide, ID inexistant, doublon et auto-référence.
- `related_adrs` : ID ADR valide/inexistant.
- Référence obsolète : warning non bloquant ; référence inexistante : erreur.
- Sections ADR/RUN présentes, manquantes, vides, supplémentaires ; fausses sections en bloc de code.
- Liens fichiers, images, MMD, README/INDEX, Markdown références, ancres locales/distantes, titres GitHub dupliqués et Unicode ; faux liens dans code.
- URL externe bien/mal formée **sans aucun accès réseau**.
- Graphe ADR : proposé, remplacement accepté cohérent, remplacement manquant dans les deux sens, self-loop, cycle, remplacements multiples d'une même ancienne ADR.
- Contrôle `--base-ref` : suppression interdite, changement d'ID interdit, déplacement accepté, nouveau document accepté.
- Exclusion totale `research/` et absence de frontmatter obligatoire pour README/INDEX.
- Exécution du CLI sur une fixture valide et sur une fixture invalide, avec vérification du code de sortie.

Ne pas réduire la suite de tests à des mocks vérifiant simplement que des fonctions sont appelées : elle doit constater les diagnostics et les codes de sortie.

## 12. Workflow GitHub Actions

Créer `.github/workflows/docs-validation.yml` :

- Déclenchement sur les événements PR vers `main` (notamment ouverture, mise à jour et réouverture) et éventuellement `push` sur `main` pour vérification post-merge.
- Pas de filtre `paths` qui pourrait sauter un contrôle requis ou manquer une suppression/renommage.
- Runner Linux, version Python explicitement fixée et documentée.
- Checkout avec profondeur d'historique suffisante pour le contrôle historique et fetch de la base PR quand nécessaire.
- Installer les dépendances, lancer `pytest`, puis le validateur complet avec `--base-ref` en PR.
- Permissions GitHub minimales, principalement `contents: read`. **Aucun token d'écriture**, aucun secret de production, aucune requête externe pour les liens.
- Le contrôle doit être utilisable comme **required status check** une fois testé.
- Ne pas tenter d'approuver des PR, de configurer des approbations depuis Python, de créer des règles serveur ou de merger automatiquement.

## 13. Protections natives GitHub : procédure distincte

Ces règles sont **des décisions de gouvernance**, pas du code à intégrer au validateur :

- Les contributions à RustkinsDocs passent par PR vers `main`.
- Le check documentaire doit être vert avant merge.
- Les créations/modifications substantielles d'ADR sous `decisions/**` exigent l'approbation d'au moins **un autre membre humain** de Rustkins ; auteur et approbateur doivent être distincts.
- Les connaissances sous `knowledge/**` ne doivent **pas** imposer de review humaine obligatoire.
- Ne pas configurer une règle globale « 1 approval required » si elle rend obligatoires les revues de connaissances.
- Utiliser les protections natives GitHub (rulesets/required reviewers ciblés) **si le plan et les permissions de l'organisation le permettent** ; sinon, signaler le blocage au propriétaire sans inventer une protection.
- Empêcher les pushes directs et les force-pushs sur `main` du dépôt **RustkinsDocs**, une fois les protections en place.
- Ne rien modifier à `RustkinsActivity`.

L'agent peut **documenter** les étapes manuelles de configuration dans la PR, mais ne doit pas prétendre avoir appliqué ces protections.

## 14. Migration initiale et compatibilité du dépôt

Le dépôt disposait de doublons `DOC-0102`, `DOC-0103` et `DOC-0105`. Ils ont été corrigés dans la PR **#19, déjà mergée**, avec attribution notamment de `DOC-0107` à `DOC-0110`. **Ne pas refaire cette migration, ne pas re-numéroter les documents existants.**

L'agent doit néanmoins :

- Scanner l'état réel de la branche avant de modifier le contenu.
- Corriger si nécessaire les `related_docs` restants contenant des chemins (le principe est « IDs exclusivement »).
- Corriger les liens locaux/ancres cassés **réellement identifiés**, sans dégrader les pages de navigation.
- Ajouter le nouveau frontmatter du runbook et mettre à jour les schémas/conventions/templates nécessaires.
- Vérifier la cohérence avec `docs/conventions/knowledge-management.md`, notamment la distinction DOC/RUN et le fait que les connaissances ne demandent pas de review.
- Ajouter les liens de navigation vers cette spécification lorsqu'approprié.
- Ne pas modifier les IDs des documents existants et ne pas remplacer silencieusement `draft` par `approved`.
- Signaler explicitement toute ambiguïté métier qu'une modification automatique ne peut pas trancher.

Si la validation complète révèle des anomalies préexistantes, les corriger dans la même PR lorsqu'elles sont factuelles et sûres ; sinon les décrire clairement. **Ne pas affaiblir une règle convenue pour obtenir artificiellement une CI verte.**

## 15. Définition de terminé et livrables

L'implémentation est terminée si :

- [ ] Les quatre JSON Schema sont opérationnels et le runbook utilise `RUN`.
- [ ] Les règles décrites ici sont réellement implémentées, avec diagnostics bloquants/warnings appropriés.
- [ ] Les quatre templates sont validables et les règles de sections respectées.
- [ ] `research/` est entièrement exclu des contrôles de contenu.
- [ ] Les tests automatisés passent en local.
- [ ] Le validateur exécuté sur tout le dépôt passe sans erreur bloquante.
- [ ] Le contrôle historique est testé avec un cas de renommage, de modification d'ID et de suppression.
- [ ] Le workflow GitHub Actions est présent et sa configuration permet son exécution sur les PR.
- [ ] La documentation d'utilisation locale et de fonctionnement CI est mise à jour.
- [ ] La PR contient le détail des changements, les commandes exécutées et leurs résultats réellement observés.
- [ ] Aucune approbation, merge ou protection GitHub n'est déclarée comme réalisée si elle ne l'a pas été.

**Ne pas ouvrir de PR tant que les vérifications locales exigées sont connues comme échouées**, sauf blocage externe précisément expliqué au propriétaire. La PR sera **laissée ouverte**, sans auto-merge, pour validation humaine.

## 16. Ordre de travail suggéré à l'agent

1. Se placer sur la branche qui contient cette spécification et inspecter le dépôt et ses schémas existants.
2. Implémenter les quatre schémas et les quatre templates, avec les tests de frontmatter.
3. Développer le validateur Python par étapes, avec tests ciblés.
4. Ajouter liens/ancres et contrôles historiques avec fixtures.
5. Corriger les anomalies réelles du dépôt et les conventions de documentation.
6. Ajouter le workflow GitHub Actions et les instructions d'utilisation.
7. Exécuter toute la suite de tests et le CLI, vérifier le diff et l'absence de modifications hors périmètre.
8. Committer/pousser sur la branche existante puis ouvrir une PR vers `main`, **sans merge**.

En cas de conflit apparent entre cette spécification et un contenu métier du dépôt, préserver le contenu métier, expliquer le conflit et privilégier une correction ciblée. Le présent document décrit des **décisions d'implémentation**, pas une autorisation de changer le produit Rustkins lui-même.
