---
id: DOC-0040
title: "Modèle opérationnel des skills Codex et Claude Code"
type: project-management
status: approved
summary: "Responsabilités des skills locaux, autonomie de développement, gestion des Tasks, références Azure Boards dans les PR et futurs workflows de sprint."
topics: [agents, skills, azure-boards, github, sprint, governance]
applies_to: [all]
references:
  - "https://github.com/Rustkins-Project/RustkinsSkills"
  - "https://github.com/Rustkins-Project/RustkinsDiscordBot"
  - "https://learn.microsoft.com/en-us/azure/devops/boards/github/link-to-from-github?view=azure-devops"
---

# Modèle opérationnel des skills Codex et Claude Code

> Ce document précise les décisions d'équipe pour le **futur workflow des agents**. Il ne signifie pas que tous les skills et scripts sont déjà livrés. Le détail technique et le plan d'implémentation vivent dans [RustkinsSkills](https://github.com/Rustkins-Project/RustkinsSkills/blob/main/docs/implementation-plan.md).

## 1. Sources de vérité, outils et périmètre

- **Azure Boards** : Epic, Feature, US, Task, Bug, Issue, sprint, relations, états, DoR et DoD. Accès principal : CLI `az` avec extension `azure-devops`.
- **GitHub** : code, branches, commits, PR, review, CI. Accès principal : `git` et `gh`.
- **RustkinsActivity** : journal d'intervention **Git**, via sa CLI Rust et le skill existant `rustkins-activity` ; aucune clôture Azure implicite.
- **RustkinsDocs** : documents, architecture, ADR et connaissance durable ; contributions avec PR.
- **RustkinsDiscordBot** : questions de l'agent à l'équipe et réponses humaines validées, via **API privée** du bot.
- **RustkinsMCP** : historique du travail réalisé, **hors architecture opérationnelle cible** ; ni dépendance ni journal d'Activity partagé.

Les appels API directs sont autorisés lorsque la CLI ne couvre pas correctement le besoin ; ils doivent être ciblés et justifiés. Aucun nouveau serveur MCP n'est requis. Les cinq skills du premier lot sont `rustkins-activity`, `rustkins-boards`, `rustkins-work`, `rustkins-ask-team` et `rustkins-knowledge`. Les trois skills dédiés aux sprints (`planning`, `status`, `close`) viendront après leur socle commun.

Les skills partagent une configuration locale et des scripts lorsque c'est utile, **sans versionnement individuel des skills**. Prendre en charge le français et les accents de bout en bout (UTF-8, en particulier Windows/PowerShell).

## 2. Backlog préexistant et création contrôlée

L'équipe construit principalement les Epics, Features et US **avant de développer** ; l'agent travaille à partir de ces éléments. Après recherche des doublons, il peut **proposer** un nouvel Epic, une Feature ou une US hors périmètre, mais ne l'écrit qu'après validation humaine explicite. Les modifications du Sprint Backlog (ajout/retrait/report/repriorisation d'US) sont arbitrées par le responsable défini dans [les règles des agents](agent-workflow.md).

**Tasks : stratégie hybride.** Au Sprint Planning, les US choisies sont décomposées en Tasks techniques utiles **après validation du planning**, non assignées initialement. Pendant le développement, un agent peut créer ou modifier une Task dans le périmètre de l'US, s'il évite les doublons et renseigne le livrable, le parent et les dépendances. Les tests sont inclus dans les Tasks de développement, pas automatiquement une Task de test distincte.

**Attribution à la prise en charge.** Une Task non attribuée est assignée au développeur qui la prend effectivement. Ne pas assigner les Tasks par défaut lors du planning ; ne pas réattribuer silencieusement une Task déjà détenue par quelqu'un d'autre.

## 3. Autonomie GitHub et review

L'agent peut sans confirmation supplémentaire : analyser le travail autorisé, choisir une branche, modifier le code et les tests, committer, pousser et ouvrir **une PR normale** lorsque les vérifications exigées sont satisfaisantes. Il corrige les retours de review sur la même PR.

**La review, l'approbation et le merge restent exclusivement humains.** Une PR mergée est censée avoir satisfait les vérifications de qualité prévues par les protections de branche et la revue ; l'agent ne doit ni contourner les protections ni déclarer des tests fictivement réussis.

**Granularité :** une PR par US par défaut, mais plusieurs PR pour la même US sont permises dans le même repo ou sur plusieurs repos si le travail le nécessite. Une Task ou un Bug **sans US** possède une PR propre. Chaque Task de développement doit être couverte par une PR qui termine son livrable. Les PR d'une même US sont indépendamment vérifiées et peuvent être mergées successivement.

## 4. Transitions natives GitHub ↔ Azure Boards

L'application **Azure Boards for GitHub** assure les liens et transitions au **merge dans la branche par défaut**. Dans la **description** de la PR, utiliser les instructions explicites ci-dessous ; la simple référence est sans transition.

| Situation | Exemple de texte dans le corps de PR | Effet demandé |
| --- | --- | --- |
| PR intermédiaire de l'US 142 | `AB#142` | Lier l'US sans la résoudre |
| Task 151 réellement terminée par cette PR | `Closed AB#151` | Clôturer cette Task lors du merge |
| PR finale de l'US 142, DoD vérifiée | `Resolved AB#142` | Passer l'US à Resolved au merge |
| Bug autonome 218 terminé par sa PR | `Closed AB#218` | Clôturer le Bug au merge selon workflow |
| PR finale mais DoD de l'US incomplète | `AB#142` | Aucun passage anticipé à Resolved |

Une PR intermédiaire peut comporter plusieurs lignes `Closed AB#<task>`, **une par Task terminée**. Une Task mentionnée uniquement pour contexte n'est pas fermée. Les références d'US et de Tasks doivent apparaître dans la description de PR ; éviter tout `Fixes AB#...` accidentel dans les commits/PR.

**Une seule PR d'une US demande `Resolved`, celle qui est mergée en dernier**, même si elle a été ouverte plus tôt. L'application ne déduit pas automatiquement les dépendances entre PR : avant le merge final, les autres PR doivent déjà être intégrées. Réviser la description de la PR si les conditions changent ; vérifier ensuite l'état réel dans Azure Boards, car une transition inconnue peut être ignorée.

## 5. Garde-fou DoD : la plateforme de test n'est pas facultative

Les règles approuvées de [DoD](definition-of-done-and-tests.md) incluent **les AC, toutes les Tasks Closed, les tests unitaires, intégration, E2E et un déploiement sur la plateforme de test avec des preuves de la version testée**.

- `Resolved AB#<US>` est permis sur la PR finale **seulement si les conditions sont effectivement réunies avant son merge**. Les dernières Tasks fermées par ce merge doivent être entièrement validées ; les états résultants seront contrôlés.
- **Si une validation n'est possible qu'après merge**, mettre uniquement `AB#<US>` dans la dernière PR. Après preuve de déploiement/test, `rustkins-boards` peut passer l'US à `Resolved` via `az`, avec relecture et traces.
- Une US n'est jamais `Closed` au merge : elle passe à `Closed` **après validation humaine lors de la Sprint Review**, décision consignée dans le compte rendu.
- Les Tasks hors PR (analyse/documentation qui ne nécessite pas de publication) peuvent passer à `Closed` dès que leur livrable est réellement vérifié.

Si l'équipe veut changer cette DoD, il faut modifier explicitement la politique de validation, **pas masquer le manque de preuves dans les instructions de PR**.

## 6. Gestion des sprints

- `rustkins-sprint-planning` prépare et propose Sprint Goal, sélection des US selon DoR, SP, dépendances et disponibilité ; après arbitrage, renseigne le sprint et crée les Tasks **non attribuées**.
- `rustkins-sprint-status` lit l'état réel Azure et GitHub ; distingue `Resolved` de `Closed`, `Blocked` de `On Hold`, et ne comptabilise comme livrés que les SP des US `Closed`.
- `rustkins-sprint-close` prépare review/rétro, recueille les décisions humaines, produit les deux comptes rendus dans RustkinsDocs, clôt uniquement les US acceptées et prépare le report des autres US après arbitrage.

Aucun skill n'attend un Daily obligatoire ni une présence constante. Les questions à l'équipe transitent par `rustkins-ask-team`, et une réponse Discord validée n'est pas automatiquement une ADR acceptée.

## 7. Validation de cette stratégie

Avant déploiement des nouveaux skills : tester sur des work items de **test**, pas sur les données métier, un lien seul `AB#`, une transition `Closed`, une transition `Resolved`, une PR mergée hors branche par défaut, un ordre de merge défavorable et un échec de mise à jour d'état. Contrôler les statuts effectivement persistés.

Le plan de développement et les tests par skill sont documentés dans [RustkinsSkills](https://github.com/Rustkins-Project/RustkinsSkills/blob/main/docs/implementation-plan.md).
