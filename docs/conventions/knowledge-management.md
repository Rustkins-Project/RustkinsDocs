---
id: DOC-0013
title: "Gestion de la documentation et de la mémoire collective"
type: convention
status: approved
summary: "Sources de vérité, classement, niveaux d'autorité, règles de revue et contribution à la mémoire collective de Rustkins."
topics: [documentation, knowledge, governance, agents]
applies_to: [all]
---

# Gestion de la documentation et de la mémoire collective

## 1. Sources de vérité

| Sujet | Référentiel |
| --- | --- |
| Backlog, sprints, work items, états | Azure Boards |
| Code, commits et Pull Requests | Repositories du code sur GitHub |
| Interventions et suivis individuels | RustkinsActivity |
| Spécifications, architecture et conventions | RustkinsDocs |
| ADR acceptées et connaissance durable | RustkinsDocs |
| Questions et réponses validées sur Discord | RustkinsDiscordBot, avant publication éventuelle dans RustkinsDocs |

Les agents ne doivent pas répliquer le backlog dans les fichiers ni transformer un journal d'activité en connaissance durable.

## 2. Règles de classement

Les domaines documentaires sont regroupés dans `docs/`. L'index `INDEX.md`, les décisions (`decisions/`), les connaissances (`knowledge/`), les recherches (`research/`), les modèles (`templates/`) et les schémas (`schemas/`) restent à la racine. Le `README.md` racine est le point d'entrée général.

- `docs/versions/` : roadmap et synthèse des lots du produit.
- `docs/specifications/` : comportement attendu, contrats et règles.
- `docs/architecture/` : organisation technique, composants et modèles de données.
- `decisions/` : décisions et arbitrages (ADR).
- `knowledge/` : observations vérifiables, solutions et pratiques réutilisables.
- `docs/operations/` : procédures exécutables par étapes (runbooks).
- `docs/conventions/` : conventions de contribution et règles d'équipe.
- `docs/cross-cutting/` : sujets d'entreprise et de projet (RGPD, business model, direction artistique, veille, éco-conception, communication). Les analyses transversales se réfèrent aux sources techniques sans les recopier ; les pistes ne valent pas décisions de mise en œuvre.
- `docs/project-management/` : gouvernance Agile, DoD, gestion des sprints et Azure Boards.
  Point d'entrée : [index de gestion de projet](../project-management/README.md) ; les règles sont réparties par thème dans ce dossier.
- `research/` : études exploratoires et POC sans caractère officiel.

**Ne pas dédoubler les documents par version par défaut.** Utiliser `applies_to` dans les documents de connaissance et les ADR ; conserver des spécifications versionnées lorsque le contrat diffère. La **version YAML d'un pipeline** est distincte de la **version du produit**.

## 3. Niveaux d'autorité

1. Les conventions et spécifications publiées décrivent les règles en vigueur dans leur périmètre.
2. Les ADR `accepted` et fusionnées justifient les décisions d'architecture, en respectant `applies_to` ; une ADR `superseded` ne prescrit plus le comportement actuel.
3. Les connaissances `verified` apportent des preuves et des solutions pratiques, sans modifier implicitement un contrat produit.
4. Les connaissances `candidate`, les ADR `proposed` et les recherches sont informatives ; elles ne valent pas décision officielle.

**En cas de contradiction entre documents officiels**, ne pas choisir silencieusement. Signaler le conflit et proposer une correction ou un arbitrage. Les sources peuvent être historiquement divergentes : leur simple déplacement n'en résout pas le contenu.

## 4. Publication et validation

### Connaissance : sans revue obligatoire

Une note dans `knowledge/` peut être ajoutée ou mise à jour **sans approbation humaine préalable**, y compris par un agent autorisé. Une PR est recommandée pour l'historique et les vérifications, mais **aucune revue de pair n'est exigée**. Un agent ne doit pas prétendre avoir testé une solution s'il ne l'a pas réellement vérifiée ; en cas de doute utiliser `candidate`.

### ADR : une revue humaine minimum

Toute ADR créée, modifiée substantiellement ou remplacée passe par une **PR approuvée par au moins un autre membre humain de l'équipe** (Timothy, Alexis ou Loick ; approbateur différent de l'auteur). Les agents IA ne peuvent pas valider seuls une ADR. Le statut `accepted` n'est opposable qu'une fois publié sur `main`, après approbation de la PR. Une réponse validée sur Discord est une source, pas une publication automatique.

Pour une ADR nouvelle ou à accepter, l'agent laisse `status: proposed`, `approved_by: []` et `decided_at: null` dans la PR. Un humain différent de l'auteur approuve le dernier commit ; après fusion, le workflow `.github/workflows/adr-finalization.yml` lit la PR et les reviews GitHub, puis pousse un commit sur `main` avec `status: accepted`, les comptes des approbateurs dans `approved_by`, la date de la dernière approbation dans `decided_at` (`AAAA-MM-JJ`, heure de Paris) et les liens de preuve dans `references`. Le reviewer n'a aucun commit de métadonnées à faire. Si le workflow échoue, l'ADR demeure `proposed` jusqu'à correction et relance. Le passage d'une ancienne ADR à `superseded` et le lien depuis l'ADR de remplacement sont examinés dans la même PR.

Au 24 novembre 2026, le ruleset GitHub actif de `main` exige une PR, le contrôle `Validate documentation` à jour et une approbation de l'équipe Rustkins pour `decisions/**`, `.github/workflows/**`, `scripts/**` et `requirements.txt` ; il ne demande aucune approbation générale pour `knowledge/**`. Les approbations obsolètes après un nouveau commit sont invalidées. Pour activer le commit automatique, un compte machine à accès limité au dépôt doit être autorisé à contourner ce ruleset. La configuration détaillée figure dans `decisions/README.md`. Les métadonnées `approved_by` et `decided_at` ne remplacent pas la preuve de review GitHub. Vérifier la configuration effective si le ruleset évolue ; ne pas imposer une revue à toutes les notes `knowledge/`.

### Autres documents

Les modifications structurantes des spécifications, de l'architecture et des conventions passent par PR, avec revue adaptée à leur impact. Les procédures opérationnelles ne doivent pas exécuter d'actions dangereuses sans vérification des prérequis.

## 5. Formats Markdown

- Les ADR, connaissances et runbooks utilisent leurs schémas respectifs dans `schemas/`. Les runbooks sous `docs/operations/` portent un ID `RUN-xxxx`, `type: operation`, et suivent `templates/runbook.md`.
- Les autres documents Markdown de référence sous `docs/` utilisent le frontmatter YAML de `schemas/document.schema.json` et le modèle `templates/document.md`, à l'exception de **tous les fichiers `README.md`**, réservés à la navigation et sans métadonnées. `README.md` et `INDEX.md` à la racine sont également exemptés. Un document métier ou normatif (comme la gestion de projet) utilise un nom dédié (`project-management.md`) plutôt que `README.md`.
- Les métadonnées documentaires incluent `id`, `title`, `type`, `status`, `summary`, `topics` et `applies_to`. Les champs de références et `specification_version` sont facultatifs.
- `applies_to` décrit la version **du produit Rustkins** : `V0`, `V1`, `V2`, `V3` ou `all` seul. `specification_version` peut décrire la version d'un contrat YAML distinct.
- Pour les ADR, un principe applicable dès V0 et conservé en V1 reçoit `applies_to: [all]` : il vaut aussi pour les versions futures tant qu'une décision approuvée ne le remplace pas. Ne pas utiliser `[all]` pour un mécanisme introduit seulement en V1 ou après, car cela l'appliquerait à tort à V0.
- `draft` est le statut par défaut d'un document historique sans validation explicite ; `approved` exige une validation effective selon les règles d'équipe. Le fait d'être déjà dans `main` ne prouve pas à lui seul cette validation.
- Les identifiants `DOC-xxxx`, `RUN-xxxx`, `ADR-xxxx` et `KNOW-xxxx` sont uniques et stables. Les valeurs `0000` sont réservées aux templates. Ne pas réattribuer un identifiant déjà publié, y compris après retrait du frontmatter d'un ancien README. Le validateur vérifie le frontmatter, l'unicité, les références et les liens ; les autorisations de revue restent du ressort de GitHub.
- `related_docs` accepte uniquement les IDs `DOC-xxxx` et `RUN-xxxx` existants ; `related_adrs` accepte les IDs d'ADR. Les chemins de fichiers s'écrivent dans les liens Markdown. Les dates YAML sans guillemets sont normalisées en ISO-8601 par le validateur.
- Les schémas JSON s'appliquent **aux objets résultant du parsing YAML**, pas au fichier Markdown brut.
- Le corps doit présenter des faits précis, des limites et des références vérifiables.
- Identifiants stables : `ADR-0001`, `KNOW-0001` (exemples) ; s'assurer qu'ils n'existent pas déjà.
- Renseigner `applies_to` avec les versions du produit concernées ; utiliser `all` si réellement transversal.
- Ne pas inventer de preuve, d'approbation, de résultat CI, ni de statut GitHub/Azure.

## 6. Travail des agents Codex et Claude Code

1. Synchroniser le clone de **lecture** du dépôt avec `git pull --ff-only` en début de session et régulièrement si nécessaire ; ne pas perturber un worktree d'écriture avec des changements locaux.
2. Avant chaque intervention importante, rechercher par **sujet + version**, en priorité dans les spécifications, les ADR acceptées et l'architecture.
3. Lire **seulement les fichiers pertinents**, plutôt que charger toute la base de connaissances.
4. Lorsqu'une découverte mérite une conservation durable, rechercher d'abord la note existante. Proposer son enrichissement ou une création sous `knowledge/`.
5. Pour un changement de conception, proposer une ADR et demander la validation appropriée ; ne pas publier une décision acceptée sans revue humaine.
6. Pour une décision Discord, le skill récupère la réponse via l'API du bot, prépare l'ADR et sa PR ; il ne considère pas une réponse en base comme une ADR déjà officielle.
7. Préserver les références vers Azure Boards et GitHub ; éviter les journaux détaillés ou transcriptions.
8. Ne jamais committer des secrets, credentials, données personnelles inutiles ou contenu sensible.

## 7. Maintenance documentaire

Lors d'un déplacement ou d'une réorganisation, vérifier les liens Markdown relatifs, les images et les références croisées. Mettre à jour les liens utilisés par les scripts et autres repositories. Les anciennes URLs vers les fichiers ne sont pas nécessairement redirigées par GitHub.

Ne pas créer de décisions rétrospectives sur la seule base d'un document technique, ni déclarer un ancien brouillon comme validé sans approbation.

## 8. Validation locale et CI

Depuis la racine de RustkinsDocs, avec Python 3.13 :

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/validate_docs.py
python scripts/validate_docs.py --base-ref origin/main
```

La dernière commande requiert une référence `origin/main` disponible localement (`git fetch origin main`). Sans `--base-ref`, aucun accès à `main` n'est nécessaire. Le validateur inspecte tous les documents publiés, les templates et les pages de navigation ; `research/` est exclu. Il contrôle les fichiers locaux et les ancres, mais ne contacte jamais les URL externes. Les références vers des documents obsolètes sont signalées comme avertissements ; les erreurs donnent un code de sortie non nul. Le contrôle historique compare les IDs de la base et de la branche : un déplacement avec ID conservé passe. La continuité du sujet d'un document déplacé reste à apprécier en revue humaine.

Le workflow `.github/workflows/docs-validation.yml` exécute les tests et la validation sur le commit de fusion temporaire de chaque PR vers `main`, avec comparaison des identités publiées au SHA de la base de la PR. Un push sur `main` relance la validation courante. Le ruleset de `main` exige actuellement le job **Validate documentation** et une branche à jour avant fusion. La protection de `main`, l'interdiction des force-pushs et les reviewers humains ciblés pour `decisions/**` sont des réglages GitHub, distincts du validateur. Ne pas imposer une revue aux connaissances.

### Hook pre-commit local

Le dépôt fournit une configuration `.pre-commit-config.yaml` pour exécuter **avant chaque commit** la validation documentaire complète :

```bash
python scripts/validate_docs.py
```

Les tests Python (`python -m pytest -q`) restent exécutés par **GitHub Actions** et peuvent être lancés manuellement lors d'une modification du validateur ; ils ne ralentissent pas les commits documentaires ordinaires.

Installer [pre-commit](https://pre-commit.com/) sur le poste de développement, avec Python (idéalement 3.13 comme dans la CI), puis activer le hook dans **chaque clone** :

```bash
python -m pip install pre-commit
pre-commit install --hook-type pre-commit
pre-commit run --all-files
```

La première exécution installe les dépendances du validateur dans un environnement Python isolé. Elles reprennent les dépendances nécessaires dans `requirements.txt` (sans `pytest`) ; un test automatisé en vérifie la cohérence. Le hook parcourt **tout le dépôt**, même pour un commit portant sur un seul fichier : il ne passe pas de liste de fichiers modifiés au script. Si la validation échoue, `git commit` est interrompu ; corriger les erreurs avant de recommencer.

Le contrôle historique (`--base-ref origin/main`) reste assuré de manière fiable par la **CI des Pull Requests**, qui connaît le SHA exact de la branche de base. Pour le reproduire localement après un `git fetch origin main`, lancer explicitement `python scripts/validate_docs.py --base-ref origin/main`.

Le hook reste une protection **locale et facultative à installer par clone** : la CI GitHub Actions et les protections de `main` demeurent les contrôles bloquants pour la fusion. Pour désinstaller le hook local : `pre-commit uninstall`.
