---
id: DOC-0102
title: "Veille concurrentielle — plateformes CI/CD"
type: cross-cutting
status: draft
summary: "Panorama des plateformes CI/CD concurrentes (SaaS, auto-hébergées, moteurs programmables, projets Rust) au 10 novembre 2026 et éléments différenciants de Rustkins."
topics: [technology-watch, competition, ci-cd, positioning]
applies_to: [all]
related_docs: [DOC-0101, DOC-0022, DOC-0021]
---

# Veille concurrentielle — plateformes CI/CD

> **Date de relevé : 10 novembre 2026.** Les informations marquées *(non vérifié)* proviennent de sources secondaires (blogs, agrégateurs) et doivent être confirmées sur le site officiel avant d'être réutilisées dans un support externe.

## 1. Objectif

Identifier les solutions avec lesquelles Rustkins sera comparé, comprendre leurs forces et faiblesses, et formuler ce qui différencie réellement Rustkins. Ce document est une veille : il **ne vaut pas décision produit** (voir les [règles transversales](../README.md)).

Rappel du positionnement retenu ([modèle économique](../business-model/business-model.md)) : moteur CI/CD **open source, gratuit, auto-hébergé uniquement**, sans SaaS, financé par du support premium, du déploiement sur infrastructure cliente et du développement sur devis.

## 2. Cartographie de la concurrence

| Catégorie | Solutions | Ce qu'un prospect y cherche |
| --- | --- | --- |
| CI intégrée à une forge (SaaS ou self-managed) | GitHub Actions, GitLab CI, Azure Pipelines, Bitbucket Pipelines | Tout-en-un : code + CI + registry |
| Serveur CI historique auto-hébergé | Jenkins | Extensibilité totale via plugins |
| CI légère auto-hébergée | Woodpecker CI, Drone, Forgejo/Gitea Actions, OneDev, Concourse | Simplicité, YAML, conteneurs |
| CI SaaS dédiée | CircleCI, Buildkite (agents auto-hébergés), TeamCity Cloud | Performance, runners managés |
| Moteurs « pipeline as code » | Dagger, Earthly, Tekton, Argo Workflows | Portabilité local ↔ CI, Kubernetes natif |
| Projets CI écrits en Rust | FluentCI, Helipad, Oxide CI | Concurrence directe sur le « moteur Rust » |

## 3. Fiches concurrents

### 3.1 GitHub Actions

- **Forces** : écosystème de milliers d'actions réutilisables, intégration native au dépôt, runners hébergés.
- **Faiblesses** : dépendance à GitHub, coût des minutes sur dépôts privés, actions tierces = surface d'attaque supply chain.
- **Actualité** : en décembre 2025, GitHub a annoncé une redevance de 0,002 $/min sur les runners **auto-hébergés** à partir du 1er mars 2026, puis l'a **reportée** après la réaction de la communauté. Les sources consultées indiquent qu'aucune redevance ne s'applique à ce jour. Les prix des runners hébergés ont baissé jusqu'à 39 % au 1er janvier 2026.
- **Enseignement pour Rustkins** : l'épisode montre que les équipes **craignent la dépendance tarifaire** envers une plateforme qui contrôle aussi l'orchestration de leurs runners. C'est un argument direct pour un moteur entièrement auto-hébergé.

### 3.2 GitLab CI (self-managed)

- **Forces** : forge complète auto-hébergeable, runners self-managed disponibles dès le tier Free sans coût par minute, DAG (`needs`), services, cache, environnements.
- **Faiblesses** : installation lourde (forge entière à opérer), fonctionnalités avancées réservées aux tiers Premium/Ultimate, YAML devenu complexe (`rules`, `extends`, `include`).
- **Enseignement** : c'est la référence fonctionnelle la plus proche de la roadmap V2 de Rustkins (services, cache, matrix, environnements).

### 3.3 Jenkins

- **Forces** : maturité, très grand nombre de plugins, gratuit et auto-hébergé, base installée énorme. Rythme LTS trimestriel (ligne 2.568.x LTS depuis juillet 2026 *(non vérifié)*).
- **Faiblesses** : JVM gourmande, configuration et plugins fragiles à maintenir, Groovy/Jenkinsfile difficile, sécurité dépendante de la qualité des plugins, UX datée.
- **Enseignement** : Rustkins vise explicitement l'usage « Jenkins-like » auto-hébergé, sans la dette de plugins. Le nom même du projet invite à la comparaison : il faut être prêt à y répondre.

### 3.4 Woodpecker CI (fork de Drone)

- **Forces** : léger (Go), Apache 2.0, server + agents, pipelines YAML dans des conteneurs, branche 3.x active.
- **Faiblesses** : dépend d'une forge externe pour l'authentification (OAuth Gitea/Forgejo/GitHub…), pas de scheduling selon les ressources, artifacts et cache via plugins.
- **Enseignement** : **concurrent le plus direct** sur le segment « CI légère auto-hébergée open source ». C'est la comparaison à préparer en priorité.

### 3.5 Forgejo / Gitea Actions

- **Forces** : syntaxe compatible GitHub Actions, réutilisation d'actions existantes, forge légère.
- **Faiblesses** : couplé à la forge, cache non fourni par défaut, résolution des actions via `data.forgejo.org` par défaut ; Codeberg n'héberge pas de runners Actions pour raisons de sécurité *(non vérifié)*.
- **Enseignement** : la compatibilité avec la syntaxe GitHub est un argument d'adoption fort ; Rustkins a fait le choix inverse d'un YAML propre (voir §5).

### 3.6 Dagger

- **Forces** : pipelines écrits dans un vrai langage (Go, Python, TypeScript), exécution identique en local et en CI, v0.20 (février 2026) avec un langage de script dédié *(non vérifié)*.
- **Faiblesses** : ce n'est pas une plateforme CI (pas d'UI de runs, de déclenchement, d'historique) : il s'exécute *dans* une CI ; cache distant lié à Dagger Cloud.
- **Enseignement** : complémentaire plutôt que concurrent. Un job Rustkins pourrait exécuter Dagger.

### 3.7 Tekton / Argo Workflows

- **Forces** : natifs Kubernetes, adaptés aux grandes organisations.
- **Faiblesses** : nécessitent un cluster Kubernetes et une forte expertise.
- **Enseignement** : hors cible V0–V1 (Docker Compose / Swarm) ; à surveiller pour la cible Kubernetes de la V2.

### 3.8 Projets CI en Rust

| Projet | État | Différence avec Rustkins |
| --- | --- | --- |
| FluentCI | Le plus avancé ; exécution **sans conteneurs**, sur Wasm et Nix | Modèle d'exécution différent (pas Docker) |
| Helipad | Preuve de concept très précoce | Pas de plateforme complète |
| Oxide CI | Alpha 0.1, projet personnel basé sur Tokio | Pas de roadmap produit ni d'offre de support |

Aucun projet Rust ne propose aujourd'hui une **plateforme CI/CD complète auto-hébergée** (UI, historique, scheduling, artifacts) avec une offre de service. Le créneau est ouvert, mais « écrit en Rust » ne suffit pas comme argument commercial.

## 4. Grille comparative

Légende : ✅ natif · 🟡 partiel / via plugin / tier payant · ❌ absent · 🗓️ prévu dans la roadmap Rustkins (version indiquée).

| Critère | Rustkins | GitHub Actions | GitLab CI | Jenkins | Woodpecker | Forgejo Actions |
| --- | --- | --- | --- | --- | --- | --- |
| Open source et gratuit | ✅ | ❌ (runner seul) | 🟡 (CE) | ✅ | ✅ | ✅ |
| Auto-hébergement complet | ✅ | 🟡 (GHES payant) | ✅ | ✅ | ✅ | ✅ |
| Indépendant d'une forge | ✅ | ❌ | ❌ | ✅ | 🟡 (OAuth forge) | ❌ |
| DAG `needs` + fail-fast | ✅ V0 | ✅ | ✅ | 🟡 | ✅ | ✅ |
| Scheduling CPU/RAM (admission) | 🗓️ V1 | ❌ | ❌ | ❌ | ❌ | ❌ |
| File durable, retry, DLQ | 🗓️ V1 | n/a | n/a | ❌ | ❌ | ❌ |
| Logs temps réel | 🗓️ V1 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Artifacts sur stockage S3 auto-hébergé | 🗓️ V1 | ❌ | ✅ | 🟡 | 🟡 | 🟡 |
| Services / sidecars | 🗓️ V2 | ✅ | ✅ | 🟡 | ✅ | ✅ |
| Cache | 🗓️ V2 | ✅ | ✅ | 🟡 | 🟡 | 🟡 |
| `when: changed` déclaratif | 🗓️ V2 | 🟡 (`paths`) | ✅ (`rules:changes`) | 🟡 | ✅ | 🟡 |
| Registry et images prébuildées | 🗓️ V3 | ✅ | ✅ | ❌ | ❌ | ✅ |
| Actions officielles pour les outils de base (uv, ruff, cargo, clippy…) | 🗓️ | 🟡 (souvent tierces) | 🟡 (templates) | 🟡 (plugins) | 🟡 (plugins) | 🟡 (actions GitHub) |
| Écosystème communautaire d'actions/plugins | ❌ | ✅ | 🟡 | ✅ | 🟡 | ✅ |
| Support commercial | 🗓️ (premium) | ✅ | ✅ | ✅ (CloudBees) | ❌ | ❌ |

> Les cases des concurrents résument la documentation publique et l'usage courant ; les vérifier avant toute publication.

## 5. Ce qui différencie Rustkins

Arguments à **défendre** (alignés sur la roadmap et le modèle économique) :

1. **Moteur autonome, sans forge imposée.** Rustkins ne demande ni GitLab, ni Gitea, ni compte GitHub : il se branche sur n'importe quel dépôt Git (clone au SHA, puis webhooks HMAC en V1). Woodpecker et Forgejo Actions dépendent d'une forge.
2. **Exécution fiable par construction.** RabbitMQ durable avec ack manuel, retry, DLQ et clé d'idempotence côté worker (V1) : un job n'est ni perdu ni exécuté deux fois lors d'un crash. Les CI légères reposent en général sur un polling des agents, sans ces garanties.
3. **Scheduling selon les ressources.** Admission CPU/RAM par nœud avec réservation et libération (V1, [ARCH-06](../../architecture/components/scheduler/06-resource-scheduling.md)) : pas de sur-souscription d'un nœud. Les concurrents limitent seulement un nombre de jobs concurrents.
4. **Empreinte réduite.** API, scheduler et worker en Rust (Tokio/Axum) : binaires natifs sans JVM ni runtime, ce qui compte pour l'auto-hébergement sur une petite VM et pour l'[éco-conception](../eco-design/README.md). *À prouver par une mesure comparative (RAM au repos, temps de démarrage) face à Jenkins et Woodpecker avant d'en faire un argument public.*
5. **Stack 100 % auto-hébergeable et souveraine.** PostgreSQL, RabbitMQ, RustFS (S3, Apache 2.0) : aucun service cloud requis, données et logs chez le client, argument RGPD (sans promettre de conformité automatique).
6. **YAML lisible et déclaratif.** `run_if`, `optional`, `continue_on_error` (V1), puis `when: branch` et `when: changed` (V2) remplacent les expressions `if` et les jobs de détection de changements.
7. **Accompagnement humain.** Support premium, déploiement sur l'infrastructure du client, développement sur devis : ni Woodpecker ni Forgejo Actions ne proposent d'offre de service.
8. **Actions officielles pour les outils courants.** Des actions prêtes à l'emploi pour les outils de base (uv, ruff, cargo, clippy, etc.), maintenues par l'équipe Rustkins : un job lint ou test s'écrit en quelques lignes. Comme elles sont officielles, il n'y a pas d'action tierce non auditée dans le pipeline, contrairement au risque supply chain de GitHub Actions (§3.1).
9. **Différenciation V3.** Registry interne, images prébuildées, statistiques et suggestions d'optimisation des pipelines.

**Faiblesses à assumer** : un catalogue d'actions limité aux outils de base, sans écosystème communautaire comparable à GitHub Actions, produit jeune sans base installée, pas de Kubernetes avant la V2, pas de compatibilité avec la syntaxe GitHub Actions (frein à la migration).

## 6. Signaux de marché à suivre

| Signal | Effet possible sur Rustkins |
| --- | --- |
| Redevance GitHub sur les runners auto-hébergés (reportée) | Si elle revient : argument fort pour une CI indépendante |
| Archivage de MinIO Community Edition (2025–2026) | Valide le choix de RustFS ; montre le risque d'un open source « freemium » qui se ferme (point à garder en tête pour la licence de Rustkins) |
| Cyber Resilience Act (signalement des vulnérabilités par les fabricants depuis le 11 septembre 2026, obligations des *stewards* open source au 11 décembre 2027) | Une CI peut produire SBOM et rapports de vulnérabilités : fonctionnalité candidate, et obligations possibles pour Rustkins s'il est commercialisé |
| Montée des agents IA qui lancent des pipelines | API et tokens scopés (V1) à concevoir pour un usage machine |

## 7. Limites

- Pas de test pratique des concurrents : la grille repose sur la documentation et des sources secondaires.
- Aucun chiffre de part de marché fiable n'a été retenu.
- À réviser chaque trimestre (voir [veille sur la stack](tech-stack-watch.md), §2).

## Références

- GitHub Changelog, « Update to GitHub Actions pricing », 16/12/2025 — https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions/
- DevClass, « GitHub to charge for self-hosted runners from March 2026 » — https://www.devclass.com/development/2025/12/17/github-to-charge-for-self-hosted-runners-from-march-2026/1734518
- Northflank, « GitHub self-hosted runners cost increase and alternatives (2026) » — https://northflank.com/blog/github-pricing-change-self-hosted-alternatives-github-actions
- GitLab Docs, Runners — https://docs.gitlab.com/ci/runners
- Jenkins dev list, « 2.553 as the next LTS baseline » — https://groups.google.com/g/jenkinsci-dev/c/W5jf2vgLhNY
- versionlog.com, Jenkins — https://versionlog.com/jenkins/
- Woodpecker CI (auto-hébergement) — https://www.nzian.xyz/blog/self-hosting-woodpecker-ci-a-complete-guide-to-running-an-open-source-ci-cd-platform
- Codeberg Docs, Forgejo Actions — https://docs.codeberg.org/ci/actions/
- Dagger v0.20 — https://dev.to/x4nent/complete-guide-to-dagger-v020-beyond-yaml-pipelines-with-cicd-as-code-dang-scripting-and-4g45
- FluentCI Engine — https://github.com/fluentci-io/fluentci-engine
- Helipad — https://github.com/joseluisq/helipad
- Oxide CI — https://dev.to/copyleftdev/building-a-blazing-fast-ci-engine-in-rust-that-dogfoods-itself-458l
- MinIO CE en 2026 — https://glukhov.org/data-infrastructure/object-storage/minio-dead/
- OpenSSF, CRA Stewards One Pager — https://policy.openssf.org/CRA/stewards-one-pager.html
- Obligations de signalement CRA au 11 septembre — https://pasqualepillitteri.it/en/news/15586/cyber-resilience-act-reporting-obligations-september-11
