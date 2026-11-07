---
id: DOC-0032
title: "Intégration opérationnelle de RustkinsActivity"
type: project-management
status: draft
summary: "Utilisation actuelle de RustkinsActivity et RustkinsSkills avec GitHub, Azure Boards et les rapports Discord ; responsabilités, granularité et limites."
topics: [activity, agents, github, azure-boards, automation]
applies_to: [all]
references:
  - "https://github.com/Rustkins-Project/RustkinsActivity"
  - "https://github.com/Rustkins-Project/RustkinsSkills"
  - "https://github.com/Rustkins-Project/RustkinsDiscordBot"
---

# Intégration opérationnelle de RustkinsActivity

> **La solution est implémentée** dans RustkinsActivity et RustkinsSkills. Le statut documentaire `draft` ci-dessus concerne la revue formelle du présent guide et ne signifie pas que les outils sont encore à développer. Ce document décrit uniquement les responsabilités **transverses** ; les contrats techniques restent dans leurs dépôts respectifs.

## 1. Sources de vérité

| Sujet | Source canonique |
| --- | --- |
| Backlog, work items, états, itérations, DoD et Sprint Review | Azure Boards |
| Code, branches, PR, reviews et CI | GitHub |
| Interventions et résultats individuels | [RustkinsActivity](https://github.com/Rustkins-Project/RustkinsActivity) |
| Spécifications, ADR, connaissance et conventions | RustkinsDocs |
| Installation et usage des agents Codex/Claude Code | [RustkinsSkills](https://github.com/Rustkins-Project/RustkinsSkills) |
| Questions à l'équipe et rapports quotidiens d'activité | [RustkinsDiscordBot](https://github.com/Rustkins-Project/RustkinsDiscordBot) |

RustkinsDiscordBot **lit** les fiches d'Activity publiées sur `main` : il n'en crée ni n'en clôture. RustkinsSkills **oriente** Codex et Claude Code ; la CLI Rust de RustkinsActivity réalise la validation, la préparation et la publication Git.

## 2. Interventions et liens Azure Boards

Une activité est une **intervention cohérente par responsable humain**, pas une session IA, une Task Azure ou une PR. Elle peut regrouper plusieurs sessions, plusieurs dépôts (`repositories`) et plusieurs PR. Plusieurs développeurs peuvent référencer le même work item avec leurs activités respectives ; le champ `work_item_id` vise le work item principal, ou vaut `null` lorsqu'aucun ticket n'est nécessaire.

Le périmètre et la condition de fin sont définis au démarrage, puis peuvent évoluer **sur une activité ouverte**, avec une trace dans le Journal. Une intervention brève peut être publiée directement `completed`. Par défaut, `completed` signifie travail vérifié et livrable publié ; review et merge ne sont attendus que s'ils font partie du périmètre. Une nouvelle correction de review après clôture implique une **nouvelle activité**, l'ancienne restant intégralement immuable. `abandoned` est également terminal et immuable.

Les statuts d'activité (`in_progress`, `paused`, `blocked`, `completed`, `abandoned`) ne synchronisent **jamais** automatiquement `System.State` dans Azure Boards. Une Task respecte sa DoD et une US n'est `Closed` qu'après validation humaine en Sprint Review, selon les [règles d'équipe](definition-of-done-and-tests.md). Les PR utilisent `AB#123` dans leur description pour la liaison Azure Boards–GitHub ; une simple référence dans une activité ne remplace pas ce lien.

## 3. Workflow opérationnel des agents

Les trois développeurs installent [RustkinsSkills](https://github.com/Rustkins-Project/RustkinsSkills#installation-windows-et-linux) sur leur poste avec leur profil humain et leur login GitHub, **un clone RustkinsActivity partagé par Codex et Claude Code sur ce poste**, et un dossier de brouillons local hors clone.

À chaque intervention, le skill exécute `recover` puis `discover`, consulte les brouillons et activités ouvertes du profil, reprend une correspondance claire sans demander, crée si aucune activité correspond, et demande confirmation **uniquement en cas d'ambiguïté**. Une activité terminale ne sert qu'au contexte.

Les opérations `prepare-create` / `prepare-patch` enregistrent un brouillon durable. `publish` prend un verrou **interprocessus local court**, synchronise la dernière version de `origin/main`, applique les changements ciblés compatibles, vérifie le schéma et le hook pré-commit, committe et pousse. La publication n'est confirmée qu'après lecture de `origin/main` ; `recover` gère les interruptions connues et les erreurs sont signalées sans écrasement destructeur.

**Pas de seconde recherche sémantique sous verrou**, pas de synchronisation périodique en arrière-plan, pas de modification directe des fichiers du journal par l'agent, pas de push forcé ni de contournement de hook. Les fiches sont poussées directement sur `main` ; les **changements structurels** (Rust, schéma, conventions, templates) passent par PR et revue humaine. Aucun CI obligatoire n'a été ajouté pour ces fiches.

## 4. Scénarios de référence

| Cas | Comportement |
| --- | --- |
| Correction rapide hors Azure | Recherche puis fiche directement `completed`, avec vérifications réelles |
| Fonctionnalité répartie sur plusieurs sessions | Une activité ouverte et enrichie jusqu'au livrable convenu |
| Codex puis Claude Code | Même activité et même dossier de brouillons du développeur |
| Plusieurs responsables sur la même Task | Activité distincte pour chaque personne |
| Intervention sur plusieurs dépôts | Une fiche avec plusieurs éléments dans `repositories` |
| Question bloquante sur Discord | `blocked` et lien/action attendue, reprise une fois le blocage réellement levé |
| Retour de review après clôture | Nouvelle fiche reliée à l'intervention initiale |
| Échec Git ou crash | Brouillon conservé ; reprise avec `recover` et sans faux succès distant |

## 5. Périmètre et références

Ce workflow journalise les interventions **sans dupliquer le backlog Azure**, ne prétend pas détecter toutes les correspondances sémantiques de façon déterministe, et ne remplace pas l'approbation humaine d'une ADR ou d'une US. La synchronisation vers Discord est **une lecture des publications sur `main`**, pas une écriture du bot dans le journal.

Le format, les invariants et les détails techniques sont documentés dans :

- [RustkinsActivity — cycle de vie](https://github.com/Rustkins-Project/RustkinsActivity/blob/main/docs/activity-workflow.md)
- [RustkinsActivity — contrat de publication](https://github.com/Rustkins-Project/RustkinsActivity/blob/main/docs/publication-contract.md)
- [RustkinsActivity — CLI des agents](https://github.com/Rustkins-Project/RustkinsActivity/blob/main/docs/agent-cli.md)
- [RustkinsSkills — installation et skill](https://github.com/Rustkins-Project/RustkinsSkills)
- [Règles de gestion Azure et agents](agent-workflow.md) · [DoD et revue](definition-of-done-and-tests.md)

Le document reste en `draft` tant que sa validation documentaire selon les conventions RustkinsDocs n'est pas formalisée ; son passage à `approved` requiert la revue appropriée.
