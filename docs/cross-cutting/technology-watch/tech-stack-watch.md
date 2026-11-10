---
id: DOC-0103
title: "Veille technologique — stack Rustkins"
type: cross-cutting
status: draft
summary: "Processus de veille sur les outils de Rustkins (Rust, Tokio, Axum, lapin, SQLx, S3/RustFS, bollard, RabbitMQ, PostgreSQL, Next.js, Traefik) et état de chaque outil au 10 novembre 2026."
topics: [technology-watch, rust, dependencies, security, stack]
applies_to: [all]
related_docs: [DOC-0102, DOC-0023]
---

# Veille technologique — stack Rustkins

> **Date de relevé : 10 novembre 2026.** Les versions viennent des registres (crates.io, docs.rs, lib.rs, npm) et des sites officiels ; les miroirs ont parfois un jour ou deux de retard. Vérifier avant toute montée de version.

## 1. Objectif

1. Savoir à tout moment si une dépendance de Rustkins a publié une version majeure, une faille ou un changement de licence.
2. Évaluer l'**effet sur Rustkins** de chaque évolution, puis décider : *ignorer*, *planifier* (work item Azure Boards) ou *agir tout de suite* (sécurité).
3. Garder une trace datée de cette veille, exigée pour le dossier et utile pour les ADR.

Une entrée de veille n'est pas une décision : un changement de dépendance structurant passe par une ADR ([règles](../../conventions/knowledge-management.md)).

## 2. Processus de veille

### 2.1 Principe : les lockfiles définissent le périmètre

La liste des technologies suivies n'est pas tenue à la main : elle découle de `Cargo.toml` / `Cargo.lock`, `package.json` / `pnpm-lock.yaml` et des images de `compose.yaml`. Une technologie qui n'y figure pas n'est pas suivie (sauf veille concurrentielle et réglementaire).

### 2.2 Sources, par niveau

| Niveau | Source | Ce qu'elle couvre | Filtrage |
| --- | --- | --- | --- |
| **1 — Automatique** | **Renovate** ou **Dependabot** sur les dépôts de code | Nouvelles versions des crates, paquets npm et images Docker (RabbitMQ, PostgreSQL, RustFS, Traefik), changelog inclus dans la PR | Natif : seules nos dépendances |
| | **`cargo audit`** (RustSec) et **`pnpm audit`** en CI | Failles connues, dépendances transitives comprises | Natif : notre arbre de dépendances |
| | **`cargo deny`** en CI | Licences, sources et doublons de crates | Natif |
| | **`cargo outdated`** une fois par sprint | Écarts de version restants | Natif |
| **2 — Annonces des dépendances directes** | Flux Atom des releases GitHub (`https://github.com/<owner>/<repo>/releases.atom`) : tokio-rs/tokio, tokio-rs/axum, amqp-rs/lapin, launchbadge/sqlx, rustfs/rustfs, fussybeaver/bollard, vercel/next.js, traefik/traefik, rabbitmq/rabbitmq-server | Versions majeures, feuilles de route | Un flux par dépendance **directe** uniquement |
| | Blogs officiels : blog.rust-lang.org, tokio.rs/blog, nextjs.org/blog, rabbitmq.com/blog, postgresql.org/about/news, rustfs.com/blog | Annonces majeures | — |
| **3 — Écosystème** | *This Week in Rust* (hebdomadaire) : rubriques « Crate of the week » et « Updates from Rust Community » | Tendances Rust, nouvelles crates | Lecture ciblée par mots-clés |
| | Hacker News via hnrss.org (ex. `https://hnrss.org/newest?q=tokio+OR+axum+OR+rabbitmq`) | Débats, retours d'expérience | Mots-clés (§2.3) |
| | F5Bot : alerte mail sur Reddit et Hacker News | Mentions de « rustkins », des concurrents et des outils | Mots-clés (§2.3) |
| | r/rust, users.rust-lang.org | Questions et pièges | Lecture occasionnelle |
| **4 — Concurrence et réglementation** | Releases de Woodpecker, Forgejo, GitLab Runner, Jenkins ; ENISA, Commission européenne, OpenSSF (Cyber Resilience Act) | Voir [veille concurrentielle](competitive-landscape.md) | — |

Tous les flux (niveaux 2 à 4) sont regroupés dans un même lecteur RSS (FreshRSS auto-hébergé, Inoreader ou Feedly).

### 2.3 Règles de filtrage

1. **Dépendances directes** (`Cargo.toml`, `package.json`, `compose.yaml`) : flux de releases (niveau 2) et alertes sécurité.
2. **Dépendances transitives** : sécurité uniquement, via `cargo audit` / `pnpm audit` ; pas de suivi de leurs nouveautés.
3. **Un mot-clé par outil**, identique dans le lecteur RSS, hnrss et F5Bot : `tokio`, `axum`, `lapin`, `sqlx`, `rustfs`, `bollard`, `rabbitmq`, `postgresql`, `next.js`, `traefik`, plus `rustkins` et les noms des concurrents.
4. **Trier par urgence** avec la grille du §2.6 : faille → action immédiate ; version majeure ou changement de licence → work item ; le reste → lu puis ignoré s'il ne concerne pas Rustkins.
5. **Ne consigner au journal (§4) que ce qui a un effet sur Rustkins.**
6. **Mettre à jour la liste de mots-clés et de flux** dès qu'une dépendance directe est ajoutée ou retirée.

### 2.4 Diffusion

*Proposition, à valider en équipe :* un salon Discord `#veille` comme boîte de réception unique. Le RustkinsDiscordBot lirait les flux RSS et ne publierait que les entrées contenant un mot-clé du §2.3. Les PR Renovate/Dependabot et les échecs `cargo audit` restent signalés dans les dépôts de code.

### 2.5 Rituel

| Fréquence | Action | Responsable |
| --- | --- | --- |
| Continu | Traiter les alertes sécurité dans la semaine (critique : sous 48 h) | Développeur de permanence |
| Hebdomadaire | Lire *This Week in Rust* et les releases reçues ; noter les points marquants dans le journal (§4) | Tournant |
| Fin de sprint | 10 min en rétrospective : qu'est-ce qui affecte Rustkins ? créer les work items | Équipe |
| Trimestriel | Mettre à jour le tableau §3 et la veille concurrentielle | Tournant |

### 2.6 Grille d'évaluation d'une évolution

| Question | Si oui |
| --- | --- |
| Faille de sécurité exploitable dans notre usage ? | Agir tout de suite |
| Changement de licence ou projet abandonné ? | Ouvrir une ADR de remplacement |
| Version majeure avec changements cassants ? | Planifier une montée de version avec budget de temps |
| Nouvelle fonctionnalité qui simplifie un composant ? | Noter dans `research/`, éventuellement POC |
| MSRV (version Rust minimale) relevée ? | Vérifier la toolchain épinglée (`rust-toolchain.toml`) |

## 3. État des outils au 10 novembre 2026

### 3.1 Backend Rust

| Outil | Rôle dans Rustkins | Dernière version relevée | Points marquants | Effet sur Rustkins |
| --- | --- | --- | --- | --- |
| **Rust** | Langage de l'API, du scheduler et du worker | Sortie toutes les 6 semaines ; 1.92 en décembre 2025, donc ~1.99 aujourd'hui *(à confirmer avec `rustup check`)* | Édition 2024 stable depuis Rust 1.85 | Épingler la toolchain ; suivre la MSRV des crates (SQLx 0.9 cible Rust 1.94) |
| **Tokio** | Runtime async | **1.54.1** (21/10/2026) | 1.54 relève la MSRV à 1.85 ; aucune version 2.0 annoncée (ignorer les articles qui en parlent) | Stable, aucun chantier ; version 1.x maintenue sur le long terme |
| **Axum** | Framework HTTP de l'API | **0.8.9** (dernière stable) | **0.9 en développement** sur `main` avec changements cassants, sans date annoncée | Rester en 0.8 ; prévoir une montée en 0.9 (extracteurs, routing) quand elle sort |
| **lapin** | Client AMQP 0.9.1 vers RabbitMQ | **4.12.3** (18/10/2026) | Branche 4.x active toute l'année 2026 (4.4 → 4.12) ; 3.x arrêtée à 3.7.2 (11/2025) | Si le code est encore en 3.x : migration à planifier. Vérifier la compatibilité de `deadpool-lapin` |
| **SQLx** | Accès PostgreSQL, migrations | **0.9.0** (21/05/2026) | Changements cassants (`RawSql`, migrator, `sqlx.toml`, hash des migrations possiblement modifié) ; MSRV 1.94 ; dépôt déplacé dans une nouvelle organisation GitHub | Tester les migrations existantes avant la montée ; régénérer le cache des requêtes hors ligne (`cargo sqlx prepare`) |
| **Client S3** | Logs et artifacts vers RustFS | `aws-sdk-s3` (officiel, complet, lourd) · `object_store` **0.13.1** (Apache Arrow, multi-backend, release tous les ~2 mois) · `rust-s3` **0.37.2** (léger) | Tous compatibles S3 v4, donc RustFS | Si `object_store` : backend `LocalFileSystem` gratuit pour les tests. Garder l'appel S3 derrière un trait pour rester portable |
| **bollard** | Pilotage de Docker par le worker | **0.21.0** | Schéma de l'API Docker 1.52 ; détection automatique du socket **Podman** | Piste pour l'exécution rootless (feature V2 « build rootless ») sans changer de crate |

### 3.2 Infrastructure

| Outil | Rôle | Dernière version relevée | Points marquants | Effet sur Rustkins |
| --- | --- | --- | --- | --- |
| **RabbitMQ** | File des jobs | **4.3** (23/04/2026) ; 4.4 annoncée le 20/10/2026 *(non vérifié)* | Khepri seul store de métadonnées (Mnesia supprimé) ; quorum queues : **retry différé avec backoff**, priorités strictes (32 niveaux), consumer timeout | Le retry et la DLQ prévus en V1 peuvent s'appuyer sur les fonctions natives des quorum queues plutôt que sur du code maison. Utiliser des quorum queues, pas des classic mirrored |
| **PostgreSQL** | Base relationnelle | **18** (09/2025) ; **19 GA prévue le 19/11/2026** (RC2 le 12/11) | PG 18 : I/O asynchrone, `uuidv7()`, colonnes générées virtuelles, auth OAuth. PG 14 en fin de vie le 12/11/2026 | Partir sur PG 18 ; `uuidv7()` donne des identifiants triables pour les runs. Évaluer PG 19 après la première version corrective |
| **RustFS** | Stockage objet S3 | **1.0.0 GA** (16/09/2026) | API S3, multipart, versioning, réplication déclarés prêts pour la production ; Apache 2.0 | Le choix est conforté. Retirer toute mention « alpha » des docs ; tester la politique de rétention (logs 2 mois) via les règles de cycle de vie S3 |
| **MinIO** (pour comparaison) | Alternative écartée | CE archivée (avril 2026) | Plus d'images communautaires, failles non corrigées | Ne pas utiliser MinIO CE. Alternatives de repli si RustFS déçoit : Garage, SeaweedFS |
| **Traefik** | Reverse proxy UI/API | **3.7.x** (3.7.14 au 05/10/2026 *(non vérifié)*) | Plusieurs CVE corrigées en 2026 ; version ≥ 3.7.11 requise pour les correctifs d'août | Épingler une version patchée, pas `latest` |
| **Docker Engine / Swarm** | Exécution des jobs, orchestration V1 | API 1.52 | — | Suivre la compatibilité bollard ↔ version du démon |

### 3.3 Frontend

| Outil | Rôle | Dernière version relevée | Points marquants | Effet sur Rustkins |
| --- | --- | --- | --- | --- |
| **Next.js** | Interface web | **16.4.x** (16.4 le 06/10/2026 ; patch 16.4.5/16.4.6) | Turbopack stable ; Cache Components ; React 19.3 ; **publications de sécurité mensuelles** (ex. 16.2.6) | Rester sur le dernier patch 16.x ; une UI surtout dynamique (runs, logs) a peu besoin du cache serveur : éviter de complexifier |
| **React** | Bibliothèque UI | 19.3 (embarquée par Next 16.4) | — | Suivre avec Next |
| **SSE (logs temps réel V1)** | Diffusion des logs | Standard web | `axum::response::sse` natif côté API | Aucune dépendance supplémentaire nécessaire |

## 4. Journal de veille

À compléter à chaque relevé (le plus récent en haut).

| Date | Outil | Évolution | Effet / action | Work item |
| --- | --- | --- | --- | --- |
| 2026-11-10 | SQLx | 0.9.0 disponible depuis mai | Vérifier la version utilisée ; planifier la migration si encore en 0.8 | à créer |
| 2026-11-10 | lapin | 4.12.x ; 3.x plus maintenue | Vérifier la version utilisée | à créer |
| 2026-11-10 | RabbitMQ | 4.3 : retry différé natif des quorum queues | À étudier pour le retry/DLQ de la V1 (`research/`) | à créer |
| 2026-11-10 | RustFS | 1.0 GA | Confirme le choix du stockage | — |
| 2026-11-10 | PostgreSQL | 19 GA le 19/11 | Rester en 18 pour la V0 | — |
| 2026-11-10 | Axum | 0.9 non publiée | Surveiller | — |

## 5. Limites

- Les versions effectivement utilisées dans les dépôts de code ne sont pas reprises ici : comparer avec `Cargo.lock` et `pnpm-lock.yaml`.
- Les lignes marquées *(non vérifié)* reposent sur une seule source secondaire.
- Le choix du client S3 n'est pas tranché dans la documentation : ce document décrit les options, il ne décide pas.

## Références

- Tokio releases — https://github.com/tokio-rs/tokio/releases
- Tokio sur docs.rs — https://docs.rs/crate/tokio/latest
- Axum README et releases — https://github.com/tokio-rs/axum · https://github.com/tokio-rs/axum/releases
- Axum, discussion « Timeline for 0.9.x » — https://github.com/tokio-rs/axum/discussions/3488
- lapin sur lib.rs — https://lib.rs/crates/lapin · CHANGELOG — https://github.com/amqp-rs/lapin/blob/main/CHANGELOG.md
- SQLx 0.9.0 — https://docs.rs/crate/sqlx/latest · https://lib.rs/crates/sqlx-cli
- PR Renovate SQLx 0.9 (notes de version citées) — https://github.com/factorial-io/scotty/pull/942
- object_store — https://docs.rs/object_store · https://crates.io/crates/object-store
- rust-s3 — https://lib.rs/crates/rust-s3
- Comparatif clients S3 avec Axum — https://encore.dev/articles/add-object-storage-to-axum
- bollard 0.21.0 — https://docs.rs/crate/bollard/latest
- RabbitMQ 4.3 Highlights — https://www.rabbitmq.com/blog/2026/04/23/rabbitmq-4.3-release
- RabbitMQ 4.3 (cycle de vie) — https://versionlog.com/rabbitmq/4.3/
- PostgreSQL 19 RC 1 — https://www.postgresql.org/about/news/postgresql-19-rc-1-released-3409/
- PostgreSQL 18 release notes — https://www.postgresql.org/docs/release/18/
- RustFS 1.0 GA — https://www.linuxtoday.com/blog/rustfs-1-0-s3-compatible-object-storage-reaches-ga/
- RustFS, production — https://dev.to/ethan-carter/rustfs-10-is-ga-after-25-years-whats-actually-production-ready-and-what-isnt-15go
- MinIO CE en 2026 — https://glukhov.org/data-infrastructure/object-storage/minio-dead/
- Traefik, avis de sécurité FreeBSD — https://vuxml.freebsd.org/freebsd/9645fcd7-82a1-11f1-8c96-5404a68ad561.html
- Next.js blog — https://nextjs.org/blog · Next.js 16.3 — https://nextjs.org/blog/next-16-3
- Next.js sur npm — https://www.npmjs.com/package/next?activeTab=versions
- Next.js 16.2 (InfoQ) — https://www.infoq.com/news/2026/06/nextjs-6-2/
- Rust 1.92.0 — https://lwn.net/Articles/1050125/
- RustSec Advisory Database — https://rustsec.org/
