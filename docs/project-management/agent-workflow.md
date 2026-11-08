---
id: DOC-0029
title: "Règles des agents IA et automatisations"
type: project-management
status: approved
summary: "Création et mise à jour des work items par les agents, vérification des états et automatisation graduelle de la DoD."
topics: [agents, automation, azure-boards, dod]
applies_to: [all]
---

# Règles des agents IA et automatisations

## 1. Règles opérationnelles des agents et skills

### 1.1. Détection et création

1. Identifier si la demande relève d'une **petite activité**, d'une **Task**, d'une **US**, d'un **Bug** ou d'une **Issue**.
2. Consulter `RustkinsDocs` de façon ciblée et synchroniser le clone de lecture si nécessaire.
3. Rechercher les work items Azure existants, y compris ceux liés à une US, et éviter les doublons.
4. **Petite intervention** : créer/compléter une activité `RustkinsActivity`, sans ticket Azure obligatoire.
5. **Travail suivi** : se rattacher au work item existant ; créer une Task si la valeur d'un suivi le justifie et si sa parenté est appropriée.
6. **Nouveau besoin fonctionnel absent du backlog** : formuler l'US, ses AC, sa Feature/Epic et **demander l'autorisation humaine** avant toute création.
7. **Anomalie** : créer un Bug si le défaut justifie un suivi ; rattacher le Bug à la fonctionnalité impactée.
8. **Recherche / POC** : utiliser une Issue si le sujet demande un livrable et une priorisation ; sinon journaliser l'activité.

### 1.2. Mise à jour des états et colonnes

| Action proposée par l'agent | Règle de sécurité |
|---|---|
| Créer une activité | Autorisé selon la convention Git du journal |
| Ouvrir / renseigner une Task | Autorisé si elle justifie un suivi et n'existe pas déjà ; les tests sont intégrés aux Tasks de développement |
| Créer une US | **Validation préalable explicite d'un des trois humains** après recherche du backlog existant |
| Passer une Task à `Closed` | Vérifier la DoD de la Task et les preuves pertinentes |
| Passer une Task/US à l'état `Blocked` | Dépendance vérifiée, lien/motif renseigné, effet sur le sprint visible ; vérifier la colonne du Board |
| Passer une Task/US à l'état `On Hold` | Pause justifiée, sans dépendance bloquante, avec condition de reprise ; vérifier la colonne du Board |
| Passer une US à `Resolved` | **Contrôler tous les AC, les trois niveaux de tests, toutes les Tasks `Closed` et le déploiement test** |
| Passer une US à `Closed` | **Uniquement après validation humaine à la Sprint Review**, décision présente au compte rendu |
| Ajouter/retirer/replanifier une US pendant le sprint | **Arbitrage par Timothy** et justification écrite |
| Clore un Epic / livrer une version | Critères du lot remplis et validation humaine de l'équipe |

Pour `Blocked` et `On Hold`, les skills doivent modifier **`System.State`** vers l'état personnalisé correspondant (après vérification qu'il existe sur le type US/Task), puis s'assurer que la carte apparaît dans **la colonne homonyme** du Board ou du Taskboard. Ils ne doivent pas confondre état du work item et simple préférence d'affichage du Board.

**Idempotence :** relire l'état courant, la colonne et les relations avant chaque mutation ; éviter tout doublon après reprise de session ou nouvel essai. Un conflit entraîne une nouvelle lecture puis un arbitrage, pas un écrasement silencieux.

**Aucune annonce de réussite** sans confirmation par Azure, GitHub ou Git.

### 1.3. Automatisation DoD graduelle

**Contrôles automatisables :** statut des Tasks enfants, présence des AC, résultats CI sur la révision cible, déploiement test, liens E2E, dépendances, état/liaison des PR `AB#...`, documentation et référence au compte rendu de review.

**Contrôles nécessitant un jugement humain de Timothy, Alexis ou Loick :** qualité réelle des AC, dérogations, validation produit en review, arbitrage de périmètre et validation de livraison d'une version. Le Sprint Backlog est piloté par Timothy.

Les skills peuvent calculer `eligible_for_resolved` et `eligible_for_closed` comme **recommandations**, jamais comme preuves à eux seuls. En particulier, `eligible_for_closed` ne déclenche pas la clôture hors Sprint Review, même si tous les tests sont verts.

### 1.4. Workflow de développement et transitions par PR

Le [modèle opérationnel des skills](agent-skills-operating-model.md) formalise les décisions d'équipe : `gh`/`git` et `az` en priorité, appels API ciblés possibles (notamment Discord), **aucun usage opérationnel de RustkinsMCP**, pas de versionnement individuel des skills et encodage UTF-8 pour le français.

Le backlog Epic/Feature/US est préparé avant développement. Au Sprint Planning, l'équipe valide les US ; les Tasks principales sont alors créées **sans responsable**. À la prise en charge, l'agent attribue une Task libre au développeur courant ; il ne réattribue pas le travail d'un tiers. Des Tasks techniques supplémentaires peuvent être créées pendant le sprint si leur périmètre reste celui de l'US.

L'agent crée les branches, code, teste, committe, pousse et ouvre la PR sans confirmation supplémentaire, **mais ne review, n'approuve ni ne merge**. Une PR couvre une US par défaut ; plusieurs PR ou dépôts sont possibles pour une même US. Une Task/Bug autonome peut avoir sa PR dédiée.

Pour chaque **Task réellement terminée par une PR**, inscrire `Closed AB#<id>` dans le **corps de la PR**. Les PR intermédiaires d'une US utilisent `AB#<us-id>` sans transition. Une seule PR finale peut porter `Resolved AB#<us-id>`, à condition que les autres PR soient mergées d'abord **et** que toute la DoD de l'US, y compris déploiement/test E2E sur plateforme de test, soit vérifiée. Sinon, garder une simple référence `AB#` et passer à `Resolved` ensuite via Azure après validation. `Closed` pour l'US reste réservé à la Sprint Review.

L'application Azure Boards for GitHub exécute les transitions au merge vers la branche par défaut ; elle **ne vérifie pas elle-même la DoD**. Aucun workflow GitHub Actions personnalisé de clôture n'est prévu à ce stade. Après merge, relire les états réellement persistés.

### 1.5. Journal des interventions (RustkinsActivity)

Les agents suivent le [guide opérationnel transversal](activity-journal-integration.md) et les [règles canoniques](https://github.com/Rustkins-Project/RustkinsActivity/blob/main/docs/activity-workflow.md). Le skill partagé est publié dans [RustkinsSkills](https://github.com/Rustkins-Project/RustkinsSkills). Ils recherchent les brouillons et activités ouvertes avant de créer ; reprennent automatiquement une correspondance claire, mais ne modifient jamais `completed` ou `abandoned`. Le nouveau `repositories` contient un ou plusieurs dépôts, et une intervention rapide peut être enregistrée directement `completed`.

La CLI RustkinsActivity implémente aujourd'hui la validation, les brouillons, le verrou local court, la publication Git et la récupération ; Codex et Claude Code partagent sa configuration. Une publication d'activité ne crée ni ne clôture un work item Azure et la fin d'une session IA ne clôture pas l'activité.

---
