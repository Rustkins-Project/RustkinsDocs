---
id: DOC-0031
title: "Configuration Azure DevOps et références techniques"
type: project-management
status: approved
summary: "Configuration Azure Boards pour les skills disponibles, liens GitHub et références Microsoft Learn."
topics: [azure-devops, configuration, github, integration]
applies_to: [all]
---

# Configuration Azure DevOps et références techniques

[Retour au sommaire de gestion de projet](README.md)

## 1. Configuration Azure DevOps pour les skills

1. Confirmer le projet Azure Boards, son processus Agile et la disponibilité des work item types `Epic`, `Feature`, `User Story`, `Task`, `Bug` et `Issue` ; configurer les Bugs au niveau des US dans le Product Backlog (**Bugs as requirements**), conformément à la politique de suivi validée.
2. Dans le **processus Agile hérité**, créer les états **`Blocked` et `On Hold` sur les US et les Tasks**, tous deux en catégorie système **In Progress**. Les deux états doivent être visibles dans le champ Azure `System.State` et requêtables par les skills.
3. Configurer les **colonnes homonymes `Blocked` et `On Hold`** sur le Board des US et vérifier leur correspondance avec les nouveaux états ; examiner séparément les colonnes créées ou affichées sur le **Taskboard des sprints**.
4. Vérifier les états des US : `New`, `Active`, `Blocked`, `On Hold`, `Resolved`, `Closed` ; si `Resolved` n'est pas présent, l'ajouter en catégorie **Resolved**. Vérifier ceux des Tasks : `New`, `Active`, `Blocked`, `On Hold`, `Closed`. Confirmer le comportement des changements d'état sur des work items de test avant l'automatisation.
5. Disposer de **Story Points** et de **Business Value (1–10)** pour les US. **Aucun champ d'estimation horaire spécifique n'est nécessaire** pour les US ni les Tasks.
6. Installer/configurer **Azure Boards pour GitHub** sur tous les dépôts concernés ; valider la liaison par `AB#<id>` et les transitions `Closed AB#<task>` / `Resolved AB#<us>` **au merge vers la branche par défaut**, sur de vrais work items de **test**.
7. Prévoir éventuellement à terme une **CI supplémentaire** de contrôle des liens PR ↔ work items. **Pas de GitHub Actions personnalisé pour la clôture** au premier lot : les transitions natives sont utilisées et la review/les checks existants contrôlent la qualité. En aucun cas la PR ne doit passer une US directement à `Closed`.
8. Définir les **preuves de DoD** lisibles par les skills : trois types de tests verts, Tasks `Closed`, version déployée sur plateforme de test, AC vérifiés, liens PR et documentation.
9. Prévoir la traçabilité de la **validation collective durant la Sprint Review** dans le compte rendu et, selon les possibilités Azure, dans un commentaire ou un champ de référence.
10. Créer les vues/requêtes de suivi nécessaires : US `Resolved`, US non terminées en fin de sprint, PR non liées, Bugs, dépendances et éléments dont **`System.State` vaut `Blocked` ou `On Hold`**. Contrôler aussi l'affichage de ces états dans les colonnes du Board et du Taskboard.
11. Tester chaque opération de lecture/modification sur des work items de test, et vérifier les permissions avant de l'autoriser à un agent.

> **Règle d'exploitation :** les PR intermédiaires ne résolvent pas leur US ; seule la dernière PR **mergée**, avec preuves DoD complètes et toutes les autres PR intégrées, peut demander `Resolved AB#<us-id>`. Si déploiement et E2E ne sont vérifiables qu'après merge, conserver `AB#<us-id>` et résoudre plus tard par `az`. Voir [le modèle opérationnel des skills](agent-skills-operating-model.md).

> **Note technique :** Rustkins choisit volontairement **de vrais états `System.State` ET leurs colonnes homonymes** pour `Blocked` et `On Hold`. Une colonne personnalisée n'est pas en elle-même un état ; il faut donc créer les états dans le processus hérité, les associer au Board, et vérifier leur représentation sur le Taskboard.

---

## 2. Références techniques Azure DevOps

- [Configurer les colonnes d'un Board Azure](https://learn.microsoft.com/en-us/azure/devops/boards/boards/add-columns?view=azure-devops) — colonnes, états et mapping.
- [Personnaliser un Taskboard de sprint](https://learn.microsoft.com/en-us/azure/devops/boards/sprints/customize-taskboard?view=azure-devops) — colonnes spécifiques aux Tasks.
- [Catégories d'états et work items](https://learn.microsoft.com/en-us/azure/devops/boards/work-items/workflow-and-state-categories?view=azure-devops) — état technique et avancement.
- [Personnaliser le workflow d'un processus hérité](https://learn.microsoft.com/en-us/azure/devops/organizations/settings/work/customize-process-workflow?view=azure-devops) — création des états personnalisés et choix de leur catégorie.
- [Lier Azure Boards à GitHub](https://learn.microsoft.com/en-us/azure/devops/boards/github/install-github-app?view=azure-devops) — association entre PR et work items.
- [Intégration Azure Boards / GitHub](https://learn.microsoft.com/en-us/azure/devops/boards/github/?view=azure-devops) — comportement des références `AB#...`.
- [Relations entre work items](https://learn.microsoft.com/en-us/azure/devops/boards/queries/link-type-reference?view=azure-devops) — hiérarchie et dépendances.
