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

> **Date de relevé : 10 novembre 2026, grille mise à jour le 13 novembre 2026.** Les informations marquées *(non vérifié)* proviennent de sources secondaires (blogs, agrégateurs) et doivent être confirmées sur le site officiel avant d'être réutilisées dans un support externe.

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

### 3.8 CircleCI

- **Forces** : `resource_class` par job, cache des couches Docker, retry automatique (`max_auto_reruns`, workflow ou step), découpage des tests selon leur durée, détection des tests instables (Insights), orbs réutilisables.
- **Faiblesses** : SaaS avant tout (le serveur auto-hébergé relève de l'offre entreprise), facturation au crédit, dépend d'une forge externe.
- **Enseignement** : référence sur l'analyse des tests et l'optimisation, ce que vise la V3 de Rustkins. Ses comparatifs marketing sont à vérifier ligne par ligne.

### 3.9 Projets CI en Rust

| Projet | État | Différence avec Rustkins |
| --- | --- | --- |
| FluentCI | Le plus avancé ; exécution **sans conteneurs**, sur Wasm et Nix | Modèle d'exécution différent (pas Docker) |
| Helipad | Preuve de concept très précoce | Pas de plateforme complète |
| Oxide CI | Alpha 0.1 ; Tokio, API HTTP, scheduler et agents via NATS, plugins natifs et Wasm, vise la compatibilité avec GitHub Actions, se construit lui-même | Pas de roadmap produit ni d'offre de support ; Rustkins utilise RabbitMQ plutôt que NATS |

Aucun projet Rust ne propose aujourd'hui une **plateforme CI/CD complète auto-hébergée** (UI, historique, scheduling, artifacts) avec une offre de service. Le créneau est ouvert, mais « écrit en Rust » ne suffit pas comme argument commercial.

## 4. Grille comparative

**Colonne Rustkins** : version de la [roadmap](../../versions/roadmap.md) où la fonctionnalité arrive (V0 → V3). « — » = non prévu à ce jour ; « à fixer » = voulu mais sans version.
**Concurrents** : ✅ natif · 🟡 partiel, via plugin/action officielle, configuration manuelle ou plan payant · ❌ absent · ? inconnu (Oxide CI est en alpha 0.1 et seul son README est disponible).

### 4.1 Modèle et hébergement

| Critère | Rustkins | CircleCI | Jenkins | GitLab CI | GitHub Actions | Woodpecker | Gitea/Forgejo Actions | Oxide CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Open source et gratuit | V0 | ❌ (SaaS, offre gratuite limitée) | ✅ | 🟡 (CE ; fonctions avancées payantes) | ❌ | ✅ | ✅ | ✅ |
| Auto-hébergement complet | V0 | 🟡 (runners ; serveur en offre entreprise) | ✅ | ✅ | 🟡 (runners ; GHES payant) | ✅ | ✅ | ✅ |
| Indépendant d'une forge | V0 | 🟡 (connexion GitHub/GitLab/Bitbucket) | ✅ | ❌ | ❌ | 🟡 (OAuth d'une forge) | ❌ | ? |
| Support commercial | V0 (premium) | ✅ | ✅ (CloudBees) | ✅ | ✅ | ❌ | 🟡 (Gitea Ltd ; rien pour Forgejo) | ❌ |

### 4.2 Écriture des pipelines

| Critère | Rustkins | CircleCI | Jenkins | GitLab CI | GitHub Actions | Woodpecker | Gitea/Forgejo Actions | Oxide CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pipeline en YAML | V0 | ✅ | 🟡 (Jenkinsfile Groovy) | ✅ | ✅ | ✅ | ✅ | ? |
| Dépendances entre jobs (DAG) | V0 | ✅ | 🟡 (stages) | ✅ | ✅ | ✅ | ✅ | ? |
| Fail-fast et jobs `skipped` | V0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ? |
| Conditions `always` / `on_failure` | V1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ? |
| Jobs optionnels / steps non bloquants | V1 | 🟡 | 🟡 | ✅ | ✅ | ✅ | ✅ | ? |
| Condition par branche | V1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ? |
| `when: changed` (chemins modifiés) par job | V2 | 🟡 (orb, config dynamique) | 🟡 | ✅ | 🟡 (au niveau du workflow) | ✅ | 🟡 | ? |
| Matrix | V2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ? |
| Jobs réutilisables / templates | V3 | ✅ (orbs) | ✅ (shared libraries) | ✅ | ✅ | 🟡 | ✅ | 🟡 (plugins) |
| Actions officielles pour uv, ruff, cargo, clippy… | à fixer | 🟡 (orbs) | 🟡 (plugins) | 🟡 (templates) | 🟡 (souvent tierces) | 🟡 (plugins) | 🟡 (actions GitHub) | ? |
| Écosystème communautaire | — | ✅ | ✅ | 🟡 | ✅ | 🟡 | ✅ | 🟡 (vise la compatibilité GitHub Actions) |

### 4.3 Exécution et fiabilité

| Critère | Rustkins | CircleCI | Jenkins | GitLab CI | GitHub Actions | Woodpecker | Gitea/Forgejo Actions | Oxide CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Un conteneur par job | V0 | ✅ | 🟡 (plugin Docker) | ✅ | ✅ | ✅ | ✅ | ? |
| Déclenchement manuel | V0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Webhooks Git + tokens d'API | V1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (API HTTP) |
| Plusieurs workers | V1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (agents via NATS) |
| Limites CPU/RAM par job | V1 | ✅ (`resource_class`) | 🟡 | 🟡 (config du runner) | 🟡 (larger runners, plans payants) | 🟡 | ? | ? |
| Placement selon CPU/RAM libres du nœud | V1 | n/a (SaaS) | ❌ | 🟡 (via Kubernetes) | ❌ | 🟡 (via Kubernetes) | ❌ | ? |
| Annulation d'un run / d'un job | V1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ? |
| Retry automatique des jobs en échec | V1 | ✅ (`max_auto_reruns`) | 🟡 (step `retry`) | ✅ (`retry:`) | ❌ (relance manuelle) | ? | ? | ? |
| File durable, DLQ, idempotence | V1 | n/a | ❌ | n/a | n/a | ❌ | ❌ | 🟡 (NATS) |
| Services / sidecars (BDD de test) | V2 | ✅ | 🟡 | ✅ | ✅ | ✅ | ✅ | ? |
| Build Docker rootless | V2 | 🟡 | 🟡 | 🟡 (Kaniko/Buildah) | 🟡 | 🟡 | 🟡 | ? |
| Kubernetes | V2 | ✅ | ✅ | ✅ | ✅ (ARC) | ✅ | 🟡 | ? |
| Reprise après crash du serveur | V2 | n/a | 🟡 | ✅ | n/a | ? | ? | ? |

### 4.4 Logs, artifacts, cache

| Critère | Rustkins | CircleCI | Jenkins | GitLab CI | GitHub Actions | Woodpecker | Gitea/Forgejo Actions | Oxide CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Logs consultables après exécution | V0 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ? |
| Logs en temps réel | V1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ? |
| Artifacts + rétention | V1 | ✅ | ✅ | ✅ | ✅ | 🟡 (plugins) | ✅ | ? |
| Cache de dépendances | V2 | ✅ | 🟡 | ✅ | ✅ | 🟡 (plugins) | 🟡 | ? |
| Cache des couches Docker | à fixer | ✅ | 🟡 | 🟡 | 🟡 (`cache-to: type=gha`) | 🟡 | 🟡 | ? |

### 4.5 Sécurité et organisation

| Critère | Rustkins | CircleCI | Jenkins | GitLab CI | GitHub Actions | Woodpecker | Gitea/Forgejo Actions | Oxide CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Authentification et membres d'un projet | V1 | ✅ | ✅ | ✅ | ✅ | 🟡 (via la forge) | ✅ | ? |
| Secrets chiffrés + masquage dans les logs | V2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ? |
| Permissions fines / rôles | V2 | ✅ | 🟡 (plugin) | ✅ | ✅ | 🟡 | 🟡 | ? |
| Environnements de déploiement | V2 | ✅ | 🟡 | ✅ | ✅ | 🟡 | 🟡 | ? |
| Registry d'images interne | V3 | ❌ | ❌ | ✅ | ✅ (GHCR) | ❌ | ✅ (packages) | ❌ |

### 4.6 Analyse des tests et optimisation

| Critère | Rustkins | CircleCI | Jenkins | GitLab CI | GitHub Actions | Woodpecker | Gitea/Forgejo Actions | Oxide CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Statistiques et suggestions d'optimisation | V3 | ✅ (Insights) | 🟡 (plugins) | 🟡 | 🟡 | ❌ | ❌ | ? |
| Détection des tests instables (flaky) | — | ✅ | 🟡 (plugin) | 🟡 | ❌ | ❌ | ❌ | ? |
| Découpage des tests selon leur durée | — | ✅ | 🟡 (plugin) | 🟡 (`parallel:` + script) | 🟡 (matrix + script) | 🟡 | 🟡 | ? |

### 4.7 Lecture de la grille

- **Avantages de Rustkins dès la V1** : placement selon les ressources libres du nœud et file durable avec retry, DLQ et idempotence (presque aucun concurrent ne les fait nativement), retry automatique (absent de GitHub Actions), le tout open source, auto-hébergé et sans forge imposée.
- **Rattrapage en V2** : services, cache, secrets, matrix, `when: changed`, Kubernetes. Ces fonctions sont standard chez tous les concurrents : elles ne différencient pas, mais leur absence bloque l'adoption.
- **Cache des couches Docker** : voulu par l'équipe mais absent de la roadmap et de la spécification YAML v3 (dont le cache ne couvre que des fichiers déclarés) ; version à fixer.
- **Non prévus** : détection des tests instables, découpage des tests selon leur durée. Ce sont les arguments de vente de CircleCI ; à évaluer pour la V3 (proposition, pas une décision).
- **Oxide CI** est le seul projet Rust comparable (Tokio, agents via NATS, plugins natifs et Wasm), mais il reste une alpha sans offre de service.

> Les cases concurrentes résument la documentation publique et des sources secondaires au 13/11/2026. Vérifier une case avant de la citer à l'extérieur, et se méfier des comparatifs publiés par les éditeurs eux-mêmes (ex. le tableau CircleCI vs GitHub Actions, qui marque ❌ des fonctions disponibles via une action officielle ou un plan payant).

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
- CircleCI, Automatic reruns — https://circleci.com/docs/guides/orchestrate/automatic-reruns/
- GitHub, re-run workflows and jobs — https://docs.github.com/en/enterprise-server@3.15/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs
- GitHub, larger runners — https://docs.github.com/de/enterprise-cloud@latest/actions/concepts/runners/about-larger-runners · https://github.blog/changelog/2025-04-09-github-actions-hosted-runner-fleet-now-incudes-96-vcpu-larger-runner/
- Docker, GitHub Actions cache backend — https://docs.docker.com/build/cache/backends/gha/
- Woodpecker, workflow syntax — https://woodpecker-ci.org/docs/usage/workflow-syntax
- Oxide CI — https://github.com/copyleftdev/oxide-ci
