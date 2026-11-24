---
id: DOC-0024
title: "Rustkins — Récapitulatif détaillé V1"
type: version
status: draft
summary: "Périmètre de Rustkins V1 : usage en équipe, authentification, webhooks, scheduling, logs temps réel et artéfacts."
topics: [V1, teams, webhooks, scheduling]
applies_to: [V1]
related_adrs: [ADR-0001, ADR-0002, ADR-0003, ADR-0004]
---

# Rustkins — Récapitulatif détaillé V1

## 1. Objectif de la V1

La V1 de Rustkins correspond au **moteur CI utilisable en équipe**.

L'objectif est de transformer le socle V0 en une plateforme réellement exploitable par une petite équipe :

```txt
Push Git / déclenchement manuel / déclenchement API
  → authentification et autorisations projet
  → réception webhook sécurisée par HMAC
  → récupération du YAML Rustkins version 2
  → création d'une PipelineVersion immuable
  → création d'un PipelineRun
  → scheduling avec ressources CPU/RAM
  → dispatch durable via outbox PostgreSQL + RabbitMQ
  → exécution sur plusieurs workers Docker
  → logs persistés et diffusés en temps réel via SSE
  → artifacts stockés dans RustFS
  → affichage des statuts, logs et artifacts dans l'interface
```

À la fin de la V1, Rustkins doit être capable d'exécuter un pipeline comme celui-ci :

```yaml
version: 2

name: Backend CI

on:
  push:
    branches:
      - main
      - develop
  manual: {}
  api: {}

vars:
  NODE_ENV: test

image: node:22

jobs:
  build:
    resources:
      cpu: 1000
      memory: 2048
    steps:
      - name: Install dependencies
        run: npm ci
      - name: Build application
        run: npm run build
    artifacts:
      paths:
        - dist/**

  test:
    needs:
      - build
    steps:
      - name: Run tests
        run: npm test
      - name: Generate coverage
        run: npm run coverage
        continue_on_error: true

  cleanup:
    needs:
      - build
      - test
    run_if: always
    image: alpine:latest
    steps:
      - run: echo "cleanup"
```

La V1 ne cherche pas encore à couvrir les usages CI/CD complexes de production. Elle doit surtout rendre Rustkins fiable pour plusieurs utilisateurs, plusieurs projets, plusieurs workers et des pipelines déclenchés automatiquement.

---

## 2. Périmètre fonctionnel V1

### 2.1 Inclus

#### Gestion des utilisateurs et des projets

- Authentification JWT.
- Refresh tokens révocables.
- Gestion des utilisateurs.
- Gestion des membres d'un projet.
- Rôles projet : `owner`, `maintainer`, `developer`, `viewer`.
- Tokens d'API par projet.
- Scopes de tokens d'API.
- Autorisation des actions sensibles : run, cancel, logs, artifacts, webhooks.

#### Déclenchement

- Déclenchement manuel.
- Déclenchement API authentifié.
- Webhooks Git.
- Providers supportés : GitHub, GitLab, Gitea.
- Vérification HMAC.
- Déduplication des livraisons webhook.
- Déclenchement automatique sur événement `push`.
- Filtrage par branche.
- Support de plusieurs pipelines par projet.

#### Moteur de pipeline

- Support de la spécification YAML `version: 2`.
- Variables globales `vars`.
- Variables par job.
- Image Docker globale surchargeable par job.
- Ressources CPU/RAM par job.
- Jobs optionnels avec `optional`.
- Steps non bloquantes avec `continue_on_error`.
- Politique d'exécution `run_if`.
- Politique de relance par job `retry.worker_loss` (`never` par défaut, `unsafe` sur choix explicite).
- Valeurs `run_if` : `all_success`, `always`, `on_failure`.
- Normalisation du YAML vers un modèle interne complet.
- Création de `PipelineVersion` immuables.
- Séparation stricte entre configuration et runtime.

#### Exécution

- Support de plusieurs workers.
- Workers sans état d'exécution durable local : PostgreSQL et RabbitMQ portent la reprise.
- Scheduling centralisé.
- Réservation CPU/RAM avant dispatch.
- Limites Docker CPU/RAM appliquées aux conteneurs.
- État `waiting_resources`.
- Annulation d'un run.
- Annulation d'un job.
- Retry automatique avant autorisation d'exécuter ; après perte d'un Worker autorisé, uniquement sur option explicite `retry.worker_loss: unsafe` du YAML v2.
- Dead Letter Queue.
- Autorisation unique de chaque tentative par le Scheduler.
- Gestion explicite des statuts `warning`.
- Heartbeat workers.
- Détection des workers offline.

#### RabbitMQ et robustesse runtime

- RabbitMQ utilisé comme transport uniquement.
- PostgreSQL reste la source de vérité.
- Transactional outbox pour les ordres et contrôles émis par le Scheduler ; événements des workers publiés avec confirmation RabbitMQ.
- Outbox Publisher côté Scheduler.
- Ordres d'exécution autonomes envoyés par le Scheduler dans la file propre à chaque worker.
- Événements des workers (`job.start.requested`, `step.finished`, `job.finished`, heartbeat) envoyés au Scheduler, seul à écrire l'état en base.
- Workers sans accès à PostgreSQL ([ADR-0001](../../../decisions/ADR-0001-worker-scheduler-communication.md)).
- ACK manuel côté worker.
- Aucun retry automatique par défaut d'un job autorisé dont l'issue est inconnue ; l'option `unsafe` accepte explicitement le risque de répétition des effets externes.
- Autorisation unique d'une tentative par le Scheduler avant l'exécution Docker.

#### Logs

- Logs temps réel via Server-Sent Events.
- Endpoint SSE par job.
- Reconnexion automatique.
- Reprise via `Last-Event-ID`.
- Chunks de logs transportés par RabbitMQ.
- Logs complets persistés dans RustFS.
- PostgreSQL stocke seulement les métadonnées de flux.
- Buffer mémoire court côté API.

#### Artifacts

- Déclaration d'artifacts dans le YAML.
- Upload d'artifacts en fin de job.
- Archive `tar.gz`.
- Checksum SHA-256.
- Stockage binaire dans RustFS.
- Métadonnées en PostgreSQL.
- Téléchargement via API et URL signée.
- Restauration automatique des artifacts des jobs listés dans `needs`.
- Politique de rétention par projet.
- Nettoyage des artifacts expirés.

#### Interface utilisateur

- Login/logout.
- Liste des projets accessibles.
- Liste des pipelines.
- Détail d'un pipeline.
- Liste des runs.
- Détail d'un run.
- Statuts en temps réel ou quasi temps réel.
- Logs temps réel.
- Téléchargement d'artifacts.
- Annulation de run/job selon permissions.
- Gestion minimale des membres projet.
- Gestion minimale des tokens d'API et webhooks.

---

### 2.2 Hors périmètre V1

- Kubernetes.
- Cache avancé.
- Secrets complets.
- Injection sécurisée de secrets dans les jobs.
- Redaction complète des secrets dans les logs.
- Services / sidecars.
- Matrix builds.
- Pull request triggers.
- Tag triggers.
- Conditions avancées `when`.
- Conditions par fichiers modifiés.
- Artifacts nommés.
- Téléchargement sélectif d'artifacts.
- Partage d'artifacts entre pipelines.
- Version comparison UI.
- Rollback de pipeline.
- Organisations et teams avancées.
- Permissions fines au-delà des rôles projet V1.
- Scheduling intelligent avec priorités, labels ou affinités.
- Haute disponibilité complète.

---

## 3. Décisions structurantes V1

| Sujet | Décision V1 |
|---|---|
| Objectif produit | Utilisation en petite équipe |
| Spécification pipeline | YAML `version: 2` |
| Authentification | JWT + refresh tokens |
| Autorisation | Rôles projet + scopes API tokens |
| Webhooks | GitHub, GitLab, Gitea |
| Sécurité webhooks | HMAC obligatoire |
| Git events | `push` uniquement |
| Source de vérité runtime | PostgreSQL |
| Transport async | RabbitMQ |
| Communication Scheduler ↔ Workers | RabbitMQ uniquement ; les workers n'accèdent pas à PostgreSQL ([ADR-0001](../../../decisions/ADR-0001-worker-scheduler-communication.md)) |
| Publication RabbitMQ | Transactional outbox |
| Outbox Publisher | Sous-composant du Scheduler |
| Logs temps réel | SSE |
| Stockage logs | RustFS |
| Stockage artifacts | RustFS |
| Téléchargement artifacts | API + URL signée |
| Exécution jobs | Docker Engine |
| Workers | Plusieurs workers possibles |
| Scheduling | Centralisé dans le Scheduler |
| Ressources | CPU milliCPU + mémoire MB |
| Sélection worker | Premier worker compatible |
| Retry | Erreurs d'infrastructure avant autorisation de démarrer ; après perte d'un Worker autorisé : `indeterminate` par défaut, relance seulement avec `retry.worker_loss: unsafe` dans le YAML v2 |
| Tentatives max | 3 |
| Déploiement dev | Docker Compose |
| Déploiement cible | Docker Swarm distribué simple |
| Kubernetes | Hors V1 |
| Secrets | Hors V1, sauf secrets webhook chiffrés |

---

## 4. Architecture logique

```mermaid
flowchart TD
  Browser[Utilisateur / Navigateur] --> Traefik[Traefik HTTP]
  GitProvider[GitHub / GitLab / Gitea] --> Traefik
  ExternalSystem[Système externe] --> Traefik

  Traefik --> UI[UI Rustkins]
  Traefik --> API[API Rustkins]

  UI -->|XHR /api/*| API
  UI -->|SSE logs| API

  API --> PG[(PostgreSQL)]
  API --> FS[(RustFS)]
  API --> Scheduler[Scheduler]

  API -->|webhook push| Scheduler
  Scheduler --> PG
  Scheduler --> Outbox[Outbox Publisher]
  Outbox --> MQ[(RabbitMQ)]

  MQ --> Worker1[Worker 1]
  MQ --> Worker2[Worker 2]
  MQ --> WorkerN[Worker N]

  Worker1 --> FS
  Worker1 --> Git[Git externe]
  Worker1 --> Docker1[Docker Engine worker 1]

  Worker2 --> FS
  Worker2 --> Git
  Worker2 --> Docker2[Docker Engine worker 2]

  WorkerN --> FS
  WorkerN --> Git
  WorkerN --> DockerN[Docker Engine worker N]

  Docker1 --> JobContainer1[Conteneur job]
  Docker2 --> JobContainer2[Conteneur job]
  DockerN --> JobContainerN[Conteneur job]

  Worker1 -->|événements + log chunks| MQ
  Worker2 -->|événements + log chunks| MQ
  WorkerN -->|événements + log chunks| MQ
  MQ -->|rustkins.events| Scheduler
  MQ -->|rustkins.logs| API

  PG --> PGVolume[(Volume postgres_data)]
  FS --> FSVolume[(Volume rustfs_data)]
```

---

## 5. Architecture infra V1 distribuée simple

La V1 peut encore fonctionner sur une seule machine en dev, mais la cible est un déploiement distribué simple avec plusieurs workers.

```txt
Cluster Rustkins V1
├── Manager / core node
│   ├── Traefik
│   ├── UI Rustkins
│   ├── API Rustkins
│   ├── Scheduler
│   ├── Outbox Publisher
│   ├── PostgreSQL
│   ├── RabbitMQ
│   └── RustFS
│
├── Worker node 1
│   ├── Worker Rustkins
│   └── Docker Engine
│
├── Worker node 2
│   ├── Worker Rustkins
│   └── Docker Engine
│
└── Worker node N
    ├── Worker Rustkins
    └── Docker Engine
```

```mermaid
flowchart TD
  User[Utilisateur / Git provider] --> Manager[Node manager Rustkins]

  subgraph Manager[Core node]
    Traefik[Traefik]
    UI[UI]
    API[API]
    Scheduler[Scheduler + Outbox Publisher]
    PG[(PostgreSQL)]
    MQ[(RabbitMQ)]
    FS[(RustFS)]
  end

  subgraph W1[Worker node 1]
    Worker1[Worker]
    Docker1[Docker Engine]
  end

  subgraph W2[Worker node 2]
    Worker2[Worker]
    Docker2[Docker Engine]
  end

  Traefik --> UI
  Traefik --> API
  API --> PG
  API --> Scheduler
  API --> FS
  Scheduler --> PG
  Scheduler --> MQ
  MQ --> Worker1
  MQ --> Worker2
  Worker1 -->|événements| MQ
  Worker2 -->|événements| MQ
  MQ -->|événements| Scheduler
  Worker1 --> FS
  Worker1 --> Docker1
  Worker2 --> FS
  Worker2 --> Docker2
```

Les conteneurs workers n'ont **aucune route directe vers PostgreSQL** : ils joignent RabbitMQ, RustFS, Git et leur Docker Engine local. Le socket Docker peut contourner cette séparation sur un hôte partagé ; en production, les workers résident sur des hôtes distincts du plan de contrôle (§19.1).

---

## 6. Dimensionnement recommandé V1

### Minimum raisonnable pour une petite équipe

```txt
Core node
CPU    : 4 vCPU
RAM    : 8 à 16 Go
Disque : 150 Go+
OS     : Debian ou Ubuntu Server

Worker node
CPU    : 4 vCPU
RAM    : 8 Go
Disque : 100 Go+
OS     : Debian ou Ubuntu Server
```

### Confortable

```txt
Core node
CPU    : 6 à 8 vCPU
RAM    : 16 à 32 Go
Disque : 300 Go+

Workers
CPU    : 8 vCPU par worker
RAM    : 16 Go par worker
Disque : 150 Go+ par worker
```

Le dimensionnement dépend surtout :

- du nombre de jobs parallèles ;
- des images Docker utilisées ;
- du poids des artifacts ;
- du volume de logs ;
- des builds nécessitant beaucoup de RAM, comme `npm`, `rustc`, `dotnet` ou les tests E2E.

---

## 7. Réseaux Docker / Swarm

### 7.1 Réseau public

Le réseau public expose uniquement le point d'entrée HTTP.

```txt
rustkins-public
└── traefik
```

### 7.2 Réseau privé applicatif

Le réseau privé permet aux services Rustkins de communiquer entre eux.

```txt
rustkins-private
├── traefik
├── ui
├── api
├── scheduler
├── worker
├── postgres
├── rabbitmq
└── rustfs
```

### 7.3 Réseau worker

En V1, les workers peuvent être distribués sur plusieurs nodes.

Ils doivent pouvoir accéder à :

```txt
- RabbitMQ
- RustFS
- Git externe
- Docker Engine local
- Internet sortant pour les containers de job
```

Ils ne doivent **pas** accéder à PostgreSQL ([ADR-0001](../../../decisions/ADR-0001-worker-scheduler-communication.md)). Un réseau dédié aux workers, ne contenant que RabbitMQ et RustFS, matérialise cette séparation.

Traefik reste connecté aux réseaux public et privé :

```txt
public  → reçoit navigateur, API tokens et webhooks
private → route vers UI/API
```

---

## 8. Ports et exposition

| Service | Port interne | Exposé V1 | Remarque |
|---|---:|---|---|
| Traefik | 80 / 443 | Oui | Point d'entrée HTTP/HTTPS |
| UI | 80 | Non direct | Accessible via Traefik |
| API | 8080 | Non direct | Accessible via Traefik `/api` |
| PostgreSQL | 5432 | Non public | Accessible par l'API et le Scheduler uniquement |
| RabbitMQ AMQP | 5672 | Non public | Accessible par Scheduler/API/Workers |
| RabbitMQ Management | 15672 | Admin uniquement | À protéger fortement |
| RustFS API | 9000 | Non public | Accessible par API/Workers |
| RustFS Console | 9001 | Admin uniquement | Optionnelle |
| Docker Engine | socket local | Non | Monté uniquement dans chaque Worker |

En V1, l'exposition directe de RabbitMQ Management et RustFS Console doit être évitée en production réelle. L'accès doit passer par un réseau admin, un bastion ou une règle d'accès restreinte.

---

## 9. Contrat de communication entre services

### 9.1 UI → API

L'UI appelle l'API via Traefik.

Exemples :

```txt
POST /api/auth/login
POST /api/auth/refresh
GET /api/projects
GET /api/projects/{projectId}/pipelines
POST /api/pipelines/{pipelineId}/runs
POST /api/runs/{runId}/cancel
GET /api/runs/{runId}
GET /api/jobs/{jobRunId}/logs/stream
GET /api/artifacts/{artifactId}
```

Les appels sont authentifiés par JWT, sauf routes explicitement publiques comme les webhooks.

---

### 9.2 Git provider → API

Endpoints publics :

```txt
POST /api/webhooks/github
POST /api/webhooks/gitlab
POST /api/webhooks/gitea
```

Règles :

- signature obligatoire ;
- validation HMAC ;
- comparaison en temps constant ;
- déduplication par identifiant de livraison ;
- normalisation vers un modèle Git interne ;
- création de run uniquement si le projet et le pipeline existent.

---

### 9.3 API → PostgreSQL

L'API lit et écrit :

- utilisateurs ;
- refresh tokens ;
- projets ;
- membres ;
- tokens d'API ;
- webhooks ;
- pipelines ;
- versions de pipeline ;
- runs ;
- logs metadata ;
- artifacts metadata.

PostgreSQL est la source de vérité.

---

### 9.4 API → Scheduler

L'API demande au Scheduler de créer ou traiter un run pour :

- déclenchement manuel ;
- déclenchement API ;
- webhook push validé.

Le Scheduler construit le DAG runtime et prend les décisions d'ordonnancement.

---

### 9.5 Scheduler → PostgreSQL

Le Scheduler :

- crée les `JobRun`, puis les `JobRunAttempt` et leurs `StepRun` à chaque
  tentative ;
- évalue le DAG ;
- réserve CPU/RAM ;
- passe les jobs en `queued` ;
- crée les `OutboxMessage` ;
- libère les ressources ;
- gère les retries ;
- marque les jobs en `dead_lettered` si nécessaire ;
- calcule le statut final du run ;
- enregistre les états remontés par les workers (`JobRun`, `StepRun`, métadonnées de logs et d'artifacts, heartbeats).

Le Scheduler est le **seul composant qui décide et écrit les transitions
d'exécution**.

---

### 9.6 Scheduler / Outbox Publisher → RabbitMQ

Le Scheduler ne publie pas directement les messages critiques.

Il écrit d'abord un `OutboxMessage` dans PostgreSQL dans la même transaction que le changement d'état.

L'Outbox Publisher publie ensuite vers RabbitMQ.

Le message `job.assigned` est routé avec la clé `worker.{worker_id}` vers la file du worker sur lequel les ressources ont été réservées.

C'est un **ordre d'exécution autonome** : dépôt et SHA, image, steps, `continue_on_error`, caractère optionnel du job, limites CPU/RAM, timeout, artifacts à produire et artifacts amont à restaurer. Extrait :

```json
{
  "message_id": "uuid",
  "type": "job.assigned",
  "worker_id": "uuid",
  "pipeline_run_id": "uuid",
  "job_run_id": "uuid",
  "attempt": 1,
  "idempotency_key": "run:job:attempt",
  "repository": { "url": "https://git.example.com/org/repo.git", "commit_sha": "sha" },
  "job": { "image": "node:22", "steps": [ { "index": 0, "run": "npm ci", "continue_on_error": false } ] },
  "restore_artifacts": [ { "artifact_id": "uuid", "object_key": "runs/...", "sha256": "..." } ],
  "created_at": "2026-01-01T12:00:00Z"
}
```

Format complet : [ARCH-02 §6](../../architecture/components/messaging/02-rabbitmq-architecture.md#6-job-message-jobassigned).

---

### 9.7 Worker → RabbitMQ

Le Worker consomme les jobs qui lui sont assignés et publie ses événements.

Files et échanges utilisés par le Worker :

```txt
rustkins.jobs.worker.{worker_id}.q   (lecture : jobs assignés)
rustkins.control.worker.{worker_id}.q (lecture : annulations et autorisations)
rustkins.events                      (écriture : événements vers le Scheduler)
rustkins.logs                        (écriture : chunks de logs)
```

Règles :

- ACK manuel du `job.assigned`, après confirmation de `job.finished` ;
- attente de `job.start.accepted` avant toute exécution Docker ; un `job.start.rejected` est ACK sans exécution ;
- publication des événements avec confirmations RabbitMQ ;
- événement non confirmé gardé en mémoire tant que le Worker vit ; la file durable RabbitMQ le conserve après confirmation, et le Scheduler acquitte après commit ;
- publication de chunks de logs vers `rustkins.logs`.

---

### 9.8 Worker → Scheduler (événements)

Le Worker **n'accède pas à PostgreSQL**. Il publie sur `rustkins.events` :

| Événement | Contenu |
|---|---|
| `worker.registered` | identifiant, capacité CPU/RAM, version |
| `worker.heartbeat` | identifiant, jobs en cours |
| `job.start.requested` | job, worker, tentative, `start_request_id`, horodatage |
| `step.finished` | statut du step, code de retour, horodatages |
| `job.finished` | statut final, code de retour, horodatages, détail d'erreur infrastructure, clé du log, métadonnées des artifacts, consommation de ressources |

Le Scheduler exige le `user_id` AMQP validé par RabbitMQ et le compare au compte du worker assigné. Pour `job.start.requested`, il inscrit `running`, conserve le `start_request_id` dans la tentative et crée l'`OutboxMessage` de `job.start.accepted` dans la même transaction. Une retransmission de la même demande sur la tentative encore active reçoit à nouveau l'acceptation via l'outbox ; une autre demande ou une tentative périmée reçoit `job.start.rejected` par le même mécanisme. La réponse reprend le `start_request_id` de la demande ; le Worker ne lance Docker qu'après avoir reçu l'acceptation correspondant à sa livraison en cours. Le Scheduler acquitte la demande après avoir enregistré sa réponse. Les autres événements sont validés, écrits en base puis acquittés après commit.

Le Worker ne réserve pas et ne libère pas de ressources. Cette responsabilité reste au Scheduler.

---

### 9.9 Worker → RustFS

Le Worker écrit :

- logs persistants ;
- archives d'artifacts.

Convention possible :

```txt
runs/{pipeline_run_id}/jobs/{job_run_id}/logs.txt
runs/{pipeline_run_id}/jobs/{job_run_id}/artifacts/{artifact_id}.tar.gz
```

---

### 9.10 API → RustFS

L'API lit les logs historiques et génère les URLs signées pour les artifacts.

RustFS n'est pas exposé directement aux utilisateurs finaux.

---

### 9.11 Worker → Docker Engine

Chaque Worker contrôle le Docker Engine local de son node.

Actions nécessaires :

```txt
pull image
create container avec limites CPU/RAM
mount workspace
start container
stream stdout/stderr
wait container
stop container si annulation
remove container
```

Le socket Docker donne au Worker le contrôle du démon de son hôte. En production, les workers sont sur des hôtes dédiés, séparés de PostgreSQL, de l'API et du Scheduler. Les exemples Compose sur un seul hôte sont réservés au développement local et n'offrent pas cette isolation forte.

---

## 10. Modèle de données V1

### 10.1 Principe

Le modèle V1 sépare quatre grands domaines :

```txt
Identité / sécurité
  → user
  → user_refresh_token
  → project_member
  → api_token

Configuration
  → project
  → webhook_config
  → pipeline
  → pipeline_version
  → pipeline_version_job
  → pipeline_version_step
  → pipeline_version_job_dependency

Exécution
  → pipeline_run
  → job_run
  → job_run_dependency
  → job_run_attempt
  → step_run
  → run_event
  → outbox_message
  → worker_node

Stockage lourd
  → job_log_stream metadata
  → artifact metadata
  → contenu binaire dans RustFS
```

La définition d'un pipeline est immuable. Le runtime référence cette définition au lieu de dupliquer les commandes dans chaque run.

---

### 10.2 MCD Mermaid simplifié

```mermaid
erDiagram
  USER ||--o{ USER_REFRESH_TOKEN : has
  USER ||--o{ PROJECT_MEMBER : belongs_to
  PROJECT ||--o{ PROJECT_MEMBER : has
  PROJECT ||--o{ API_TOKEN : owns
  PROJECT ||--o{ WEBHOOK_CONFIG : owns
  PROJECT ||--o{ WEBHOOK_DELIVERY : receives
  WEBHOOK_CONFIG ||--o{ WEBHOOK_DELIVERY : receives

  PROJECT ||--o{ PIPELINE : owns
  PIPELINE ||--o{ PIPELINE_VERSION : has
  PIPELINE_VERSION ||--o{ PIPELINE_VERSION_JOB : defines
  PIPELINE_VERSION_JOB ||--o{ PIPELINE_VERSION_STEP : contains
  PIPELINE_VERSION_JOB ||--o{ PIPELINE_VERSION_JOB_DEPENDENCY : has

  PIPELINE_VERSION ||--o{ PIPELINE_RUN : used_by
  USER o|--o{ PIPELINE_RUN : triggers
  API_TOKEN o|--o{ PIPELINE_RUN : triggers
  WEBHOOK_DELIVERY o|--o{ PIPELINE_RUN : triggers
  PIPELINE_RUN ||--o{ JOB_RUN : contains
  JOB_RUN ||--o{ JOB_RUN_ATTEMPT : has
  JOB_RUN_ATTEMPT ||--o{ STEP_RUN : contains
  JOB_RUN ||--o| JOB_LOG_STREAM : writes
  JOB_RUN ||--o{ ARTIFACT : produces
  WORKER_NODE ||--o{ JOB_RUN : executes
  PIPELINE_RUN ||--o{ RUN_EVENT : has
  PIPELINE_RUN ||--o{ OUTBOX_MESSAGE : emits
```

---

### 10.3 Tables principales

#### `users`

Représente un utilisateur authentifié Rustkins.

| Colonne | Description |
|---|---|
| `id` | Identifiant utilisateur |
| `email` | Email de connexion |
| `username` | Nom affiché |
| `password_hash` | Hash du mot de passe |
| `role_global` | Rôle global éventuel |
| `is_active` | Compte actif ou non |
| `last_login_at` | Dernière connexion |

---

#### `user_refresh_tokens`

Représente une session révocable.

| Colonne | Description |
|---|---|
| `user_id` | Utilisateur lié |
| `token_hash` | Refresh token hashé |
| `expires_at` | Expiration |
| `revoked_at` | Révocation |
| `user_agent` | Contexte client |
| `ip_address` | Adresse IP observée |

---

#### `project_members`

Associe un utilisateur à un projet.

| Colonne | Description |
|---|---|
| `project_id` | Projet |
| `user_id` | Utilisateur |
| `role` | `owner`, `maintainer`, `developer`, `viewer` |

---

#### `api_tokens`

Permet l'automatisation par projet.

| Colonne | Description |
|---|---|
| `project_id` | Projet lié |
| `name` | Nom du token |
| `token_prefix` | Préfixe affichable |
| `token_hash` | Token hashé |
| `scopes_json` | Tableau JSON des scopes autorisés |
| `revoked` | Révocation |
| `expires_at` | Expiration optionnelle |
| `last_used_at` | Dernière utilisation |

---

#### `webhook_configs`

Stocke la configuration webhook d'un projet.

| Colonne | Description |
|---|---|
| `project_id` | Projet lié |
| `provider` | GitHub, GitLab ou Gitea |
| `encrypted_secret` | Secret HMAC chiffré |
| `enabled` | Webhook actif |

---

#### `webhook_deliveries`

Historique des webhooks reçus.

| Colonne | Description |
|---|---|
| `external_delivery_id` | Identifiant provider |
| `event_type` | Type d'événement |
| `before_sha` | Commit précédent de la référence poussée |
| `after_sha` | Nouveau commit, utilisé pour le run |
| `branch` | Branche reçue |
| `status` | `received`, `validated`, `processed`, `completed`, `rejected` |
| `error_message` | Erreur éventuelle |

---

#### `pipeline_versions`

Snapshot immuable d'un YAML.

| Colonne | Description |
|---|---|
| `pipeline_id` | Pipeline logique |
| `git_sha` | SHA Git |
| `yaml_hash` | Hash du YAML |
| `yaml_content` | YAML brut |
| `specification_version` | Version du contrat YAML, distincte de la version du produit |
| `validation_status` | `valid` ou `invalid` |
| `validation_errors_json` | Erreurs de validation |

Unicité recommandée :

```txt
pipeline_id + git_sha
```

---

#### `pipeline_version_jobs`

Définition immuable d'un job parsé.

| Colonne | Description |
|---|---|
| `job_key` | Identifiant YAML |
| `image` | Image résolue |
| `run_if` | Politique d'exécution |
| `optional` | Job non bloquant |
| `retry_worker_loss` | `never` par défaut, ou `unsafe` si déclaré dans le YAML v2 |
| `cpu_limit_milli` | CPU demandé |
| `memory_limit_mb` | Mémoire demandée |
| `timeout_seconds` | Timeout job |

---

#### `pipeline_version_steps`

Définition immuable d'une commande.

| Colonne | Description |
|---|---|
| `pipeline_version_job_id` | Job parent |
| `step_key` | Identifiant interne |
| `name` | Nom lisible |
| `command` | Commande |
| `order_index` | Ordre d'exécution |
| `continue_on_error` | Step non bloquante |

---

#### `pipeline_runs`

Exécution complète d'une version.

| Colonne | Description |
|---|---|
| `pipeline_version_id` | Version utilisée |
| `triggered_by_user_id` | Utilisateur déclencheur, si `manual` |
| `triggered_by_api_token_id` | Token déclencheur, si `api` |
| `webhook_delivery_id` | Livraison déclencheuse, si `webhook` |
| `cancelled_by_user_id` | Utilisateur ayant annulé |
| `trigger_type` | `manual`, `api`, `webhook` |
| `status` | Statut runtime |
| `branch` | Branche |
| `commit_sha` | Commit exécuté |
| `commit_message` | Message du commit |
| `author_name` | Auteur |
| `author_email` | Email auteur |

Une seule des trois références de déclenchement est renseignée, selon
`trigger_type`.

---

#### `job_runs`

Exécution runtime d'un job.

| Colonne | Description |
|---|---|
| `pipeline_run_id` | Run parent |
| `pipeline_version_job_id` | Définition exécutée |
| `worker_node_id` | Worker assigné |
| `status` | Statut runtime |
| `idempotency_key` | Clé d'idempotence |
| `attempt_count` | Nombre de tentatives |
| `max_attempts` | Tentatives max |
| `exit_code` | Code de retour |

`worker_node_id` indique l'affectation courante ; chaque tentative conserve
son propre worker pour l'historique.

---

#### `job_run_attempts` et `step_runs`

Une tentative conserve son `worker_node_id`, son `attempt_number`, son
`start_request_id` éventuel, son `status`, son `exit_code`, ses dates et
ses métriques CPU/mémoire. Chaque `step_run` référence cette tentative
via `job_run_attempt_id` et la définition via
`pipeline_version_step_id`. Les résultats des steps restent ainsi
distincts entre deux tentatives du même job.

---

#### `worker_nodes`

Représente un worker d'exécution.

| Colonne | Description |
|---|---|
| `name` | Nom logique |
| `hostname` | Hôte |
| `status` | `online`, `offline`, etc. |
| `total_cpu_milli` | Capacité CPU |
| `total_memory_mb` | Capacité mémoire |
| `reserved_cpu_milli` | CPU réservé |
| `reserved_memory_mb` | Mémoire réservée |
| `last_heartbeat_at` | Dernier heartbeat |

---

#### `outbox_messages`

Message durable à publier vers RabbitMQ.

| Colonne | Description |
|---|---|
| `exchange` | Exchange RabbitMQ |
| `routing_key` | Routing key |
| `event_type` | Type d'événement |
| `payload_json` | Payload |
| `status` | `pending`, `publishing`, `published`, `failed` |
| `attempts` | Tentatives de publication |
| `next_attempt_at` | Prochaine tentative |
| `last_error` | Dernière erreur |
| `published_at` | Date de publication |

---

#### `artifacts`

Métadonnées d'un artifact.

| Colonne | Description |
|---|---|
| `pipeline_run_id` | Run parent |
| `job_run_id` | Job producteur |
| `archive_name` | Nom de l'archive |
| `storage_key` | Clé RustFS |
| `size_bytes` | Taille |
| `checksum_sha256` | Checksum |
| `expires_at` | Expiration |
| `deleted` | Archive supprimée |

---

## 11. Statuts V1

### 11.1 `pipeline_runs`

```txt
queued
running
success
warning
failed
cancelled
indeterminate
```

### 11.2 `job_runs`

```txt
waiting_dependencies
waiting_resources
queued
running
success
warning
failed
skipped
cancel_requested
cancelled
retrying
dead_lettered
indeterminate
```

### 11.3 `step_runs`

```txt
running
success
warning
failed
skipped
indeterminate
```

### 11.4 `outbox_messages`

```txt
pending
publishing
published
failed
```

### 11.5 `webhook_deliveries`

```txt
received
validated
processed
completed
rejected
```

Le statut `warning` est structurant en V1. Il signifie : problème réel, mais non bloquant pour le pipeline.

---

## 12. Flux complet d'exécution

```mermaid
sequenceDiagram
  actor Dev as Développeur
  participant Git as Git provider
  participant API as API Rustkins
  participant PG as PostgreSQL
  participant Scheduler as Scheduler
  participant Outbox as Outbox Publisher
  participant MQ as RabbitMQ
  participant Worker as Worker
  participant Docker as Docker Engine
  participant FS as RustFS
  participant UI as UI

  Dev->>Git: git push
  Git->>API: POST webhook
  API->>API: Vérifie HMAC
  API->>PG: Enregistre WebhookDelivery
  API->>Git: Lit YAML au commit SHA
  API->>API: Parse + valide YAML v2
  API->>PG: Crée ou réutilise PipelineVersion
  API->>Scheduler: Demande création PipelineRun

  Scheduler->>PG: Crée PipelineRun et JobRuns
  Scheduler->>PG: Évalue DAG
  Scheduler->>PG: Sélectionne worker compatible
  Scheduler->>PG: Réserve CPU/RAM
  Scheduler->>PG: JobRun = queued, crée tentative et StepRuns + OutboxMessage(job.assigned)

  Outbox->>PG: Lit OutboxMessage pending
  Outbox->>MQ: Publie job.assigned (clé worker.{id})
  Outbox->>PG: Marque OutboxMessage published

  MQ->>Worker: Livre job.assigned (ordre autonome)
  Worker->>Worker: Vérifie la disponibilité de Docker sans exécuter le dépôt
  Worker->>MQ: Publie job.start.requested
  MQ->>Scheduler: Livre job.start.requested
  Scheduler->>PG: JobRun = running + OutboxMessage(job.start.accepted)
  MQ->>Worker: Livre job.start.accepted
  Worker->>Git: Clone repo au SHA
  Worker->>FS: Restaure artifacts des dépendances
  Worker->>Docker: Lance conteneur avec limites CPU/RAM
  Docker-->>Worker: stdout/stderr + exit code
  Worker->>FS: Persiste logs
  Worker->>MQ: Publie chunks de logs
  MQ->>API: Transmet chunks de logs
  API->>UI: SSE logs temps réel
  Worker->>MQ: Publie step.finished (à chaque step)
  MQ->>Scheduler: Livre step.finished pour la tentative courante
  Scheduler->>PG: Met à jour son StepRun
  Worker->>FS: Upload artifacts
  Worker->>MQ: Publie job.finished (statut, métadonnées logs/artifacts, consommation)
  Worker->>MQ: ACK du message job.assigned

  MQ->>Scheduler: Livre job.finished
  Scheduler->>PG: Valide et écrit JobRun/JobRunAttempt/Artifacts
  Scheduler->>PG: Libère ressources
  Scheduler->>PG: Débloque jobs dépendants + OutboxMessage(job.assigned)
  Scheduler->>PG: Calcule statut final du PipelineRun
  Scheduler->>MQ: ACK de l'événement
```

Le worker **écoute le Scheduler, lui signale la fin de chaque job, et le Scheduler lui envoie les jobs suivants** ([ADR-0001](../../../decisions/ADR-0001-worker-scheduler-communication.md)).

`job.finished` porte l'état final. Le Scheduler ne le prend pas pour argent comptant : il vérifie le worker émetteur, la tentative et la transition d'état avant d'écrire, dans la même transaction que la libération des ressources et l'assignation des jobs suivants. Un événement en double ou périmé est ignoré.

L'ACK RabbitMQ du message `job.assigned` garde son rôle transport : confirmer que l'ordre d'exécution reçu par le Worker a été traité et ne doit pas être redistribué.

---

## 13. Gestion du DAG, du warning et des ressources

### 13.1 Exemple de DAG

```mermaid
flowchart TD
  build[build]
  test[test]
  cleanup[cleanup]
  failure[failure-report]

  build --> test
  build --> cleanup
  test --> cleanup
  test --> failure
```

### 13.2 Règles `run_if`

| Valeur | Règle |
|---|---|
| `all_success` | Le job s'exécute si toutes ses dépendances sont `success` ou `warning` |
| `always` | Le job s'exécute dès que toutes ses dépendances ont une issue finale connue ; `indeterminate` le bloque |
| `on_failure` | Le job s'exécute si au moins une dépendance est `failed` ou `dead_lettered` |

`indeterminate` indique qu'un worker a disparu après l'autorisation de démarrer sans résultat confirmé. Par défaut, le Scheduler ne relance pas le job et ne débloque aucun descendant, même avec `run_if: always`. Le PipelineRun prend aussi le statut `indeterminate`. Un `job.finished` tardif de la même tentative peut résoudre l'état ; sinon une vérification humaine des effets externes est nécessaire avant toute nouvelle exécution. Le YAML v2 permet `retry.worker_loss: unsafe` par job : le Scheduler garde l'ancienne tentative comme `indeterminate` dans l'historique et en lance une nouvelle si la limite de trois tentatives le permet. Un résultat tardif de l'ancienne tentative ne remplace pas celui de la nouvelle. Les effets externes peuvent être répétés.

Par défaut :

```yaml
run_if: all_success
```

### 13.3 Règles `warning`

- Une step avec `continue_on_error: true` qui échoue devient `warning`.
- Un job contenant seulement des erreurs non bloquantes devient `warning`.
- Un job `optional: true` avec une erreur métier devient `warning`.
- Un pipeline avec au moins un job `warning`, sans échec obligatoire, devient `warning`.
- Un `warning` ne déclenche pas `run_if: on_failure`.

### 13.4 Règles ressources

- Un job ne devient `queued` que si un worker compatible existe.
- Le Scheduler réserve CPU/RAM avant le dispatch RabbitMQ.
- Si aucun worker n'a assez de ressources temporairement, le job passe `waiting_resources`.
- Si le job demande plus que la capacité de tous les workers, il passe `failed`.
- Les ressources sont libérées uniquement par le Scheduler, après résultat final ou perte confirmée du worker ; un worker offline ne reçoit aucun nouveau job avant réconciliation de ses conteneurs.

### 13.5 Fail-fast V1

Le fail-fast V0 devient une évaluation plus fine :

- un job obligatoire `failed` bloque les descendants en `all_success` ;
- les descendants incompatibles passent `skipped` ;
- les jobs `always` peuvent encore tourner ;
- les jobs `on_failure` peuvent gérer les erreurs ;
- les jobs `warning` restent non bloquants.
- un job `indeterminate` suspend l'évaluation de tous ses descendants jusqu'à résolution.

---

## 14. Exemple Docker Compose dev V1

Ce compose représente un environnement de développement V1 avec deux workers locaux.

```yaml
services:
  traefik:
    image: traefik:v3.0
    command:
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - rustkins-public
      - rustkins-private

  ui:
    image: rustkins/ui:dev
    labels:
      - traefik.enable=true
      - traefik.http.routers.rustkins-ui.rule=PathPrefix(`/`)
      - traefik.http.services.rustkins-ui.loadbalancer.server.port=80
    networks:
      - rustkins-private

  api:
    image: rustkins/api:dev
    environment:
      DATABASE_URL: postgres://rustkins:rustkins@postgres:5432/rustkins
      RABBITMQ_URL: ${RABBITMQ_API_URL}
      RUSTFS_ENDPOINT: http://rustfs:9000
      JWT_ISSUER: rustkins
      JWT_AUDIENCE: rustkins-ui
      RUSTKINS_PUBLIC_URL: http://localhost
    labels:
      - traefik.enable=true
      - traefik.http.routers.rustkins-api.rule=PathPrefix(`/api`)
      - traefik.http.services.rustkins-api.loadbalancer.server.port=8080
    depends_on:
      - postgres
      - rabbitmq
      - rustfs
    networks:
      - rustkins-private

  scheduler:
    image: rustkins/scheduler:dev
    environment:
      DATABASE_URL: postgres://rustkins:rustkins@postgres:5432/rustkins
      RABBITMQ_URL: ${RABBITMQ_SCHEDULER_URL}
      SCHEDULER_POLL_INTERVAL_SECONDS: 2
    depends_on:
      - postgres
      - rabbitmq
    networks:
      - rustkins-private

  worker-1:
    image: rustkins/worker:dev
    environment:
      WORKER_ID: ${WORKER_1_ID}
      WORKER_NAME: worker-1
      WORKER_TOTAL_CPU_MILLI: 4000
      WORKER_TOTAL_MEMORY_MB: 8192
      # Pas de DATABASE_URL : les workers n'accèdent pas à PostgreSQL (ADR-0001).
      RABBITMQ_URL: ${RABBITMQ_WORKER_1_URL}
      RUSTFS_ENDPOINT: http://rustfs:9000
      WORKER_WORKDIR: /workdir
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - worker_1_workdir:/workdir
    networks:
      - rustkins-worker

  worker-2:
    image: rustkins/worker:dev
    environment:
      WORKER_ID: ${WORKER_2_ID}
      WORKER_NAME: worker-2
      WORKER_TOTAL_CPU_MILLI: 4000
      WORKER_TOTAL_MEMORY_MB: 8192
      RABBITMQ_URL: ${RABBITMQ_WORKER_2_URL}
      RUSTFS_ENDPOINT: http://rustfs:9000
      WORKER_WORKDIR: /workdir
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - worker_2_workdir:/workdir
    networks:
      - rustkins-worker

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: rustkins
      POSTGRES_USER: rustkins
      POSTGRES_PASSWORD: rustkins
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - rustkins-private

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_ADMIN_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_ADMIN_PASSWORD}
    ports:
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - rustkins-private
      - rustkins-worker

  rustfs:
    image: rustfs/rustfs:latest
    environment:
      RUSTFS_ACCESS_KEY: rustkins
      RUSTFS_SECRET_KEY: rustkins-password
      RUSTFS_CONSOLE_ENABLE: "true"
    ports:
      - "9001:9001"
    volumes:
      - rustfs_data:/data
    networks:
      - rustkins-private
      - rustkins-worker

volumes:
  postgres_data:
  rabbitmq_data:
  rustfs_data:
  worker_1_workdir:
  worker_2_workdir:

networks:
  rustkins-public:
  rustkins-private:
  rustkins-worker:
```

Le réseau `rustkins-worker` ne contient que les workers, RabbitMQ et RustFS : PostgreSQL n'y est pas directement joignable. Le socket Docker sur le même hôte peut contourner cette séparation ; cet exemple est destiné au développement local.

`WORKER_1_ID` et `WORKER_2_ID` sont distincts et stables. Les URL RabbitMQ de l'API, du Scheduler et de chaque worker utilisent des comptes distincts, provisionnés avec les droits d'[ARCH-02 §9](../../architecture/components/messaging/02-rabbitmq-architecture.md#9-worker-events) avant le démarrage. Le compte administrateur du broker sert uniquement au provisionnement ; aucun composant applicatif ne le reçoit.

---

## 15. Exemple Swarm distribué pour V1

La V1 vise un Swarm simple avec plusieurs workers.

```bash
docker swarm init
docker node update --label-add rustkins.role=core <core-node>
docker node update --label-add rustkins.role=worker <worker-node-1>
docker node update --label-add rustkins.role=worker <worker-node-2>
docker node update --label-add rustkins.worker_id=worker-1 <worker-node-1>
docker node update --label-add rustkins.worker_id=worker-2 <worker-node-2>
```

Principes :

- services core placés sur le node `core` ;
- workers placés sur les nodes `worker` ;
- volumes PostgreSQL/RabbitMQ/RustFS sur le core node ;
- Docker socket monté uniquement dans les workers ;
- Traefik expose l'UI et l'API ;
- RabbitMQ/RustFS/PostgreSQL restent privés.

### 15.1 Stack Swarm V1 exemple

```yaml
version: "3.9"

services:
  traefik:
    image: traefik:v3.0
    command:
      - --providers.swarm=true
      - --providers.swarm.exposedbydefault=false
      - --entrypoints.web.address=:80
    ports:
      - target: 80
        published: 80
        protocol: tcp
        mode: host
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - public
      - private
    deploy:
      placement:
        constraints:
          - node.labels.rustkins.role == core

  ui:
    image: rustkins/ui:v1
    networks:
      - private
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.rustkins.role == core
      labels:
        - traefik.enable=true
        - traefik.http.routers.rustkins-ui.rule=PathPrefix(`/`)
        - traefik.http.services.rustkins-ui.loadbalancer.server.port=80

  api:
    image: rustkins/api:v1
    environment:
      DATABASE_URL: postgres://rustkins:rustkins@postgres:5432/rustkins
      RABBITMQ_URL: ${RABBITMQ_API_URL}
      RUSTFS_ENDPOINT: http://rustfs:9000
      RUSTKINS_PUBLIC_URL: http://rustkins.example.local
    networks:
      - private
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.rustkins.role == core
      labels:
        - traefik.enable=true
        - traefik.http.routers.rustkins-api.rule=PathPrefix(`/api`)
        - traefik.http.services.rustkins-api.loadbalancer.server.port=8080

  scheduler:
    image: rustkins/scheduler:v1
    environment:
      DATABASE_URL: postgres://rustkins:rustkins@postgres:5432/rustkins
      RABBITMQ_URL: ${RABBITMQ_SCHEDULER_URL}
      SCHEDULER_POLL_INTERVAL_SECONDS: 2
    networks:
      - private
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.rustkins.role == core

  worker-1:
    image: rustkins/worker:v1
    environment:
      WORKER_ID: ${WORKER_1_ID}
      RABBITMQ_URL: ${RABBITMQ_WORKER_1_URL}
      RUSTFS_ENDPOINT: http://rustfs:9000
      WORKER_TOTAL_CPU_MILLI: 4000
      WORKER_TOTAL_MEMORY_MB: 8192
      WORKER_WORKDIR: /workdir
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - worker_workdir:/workdir
    networks:
      - workers
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.rustkins.role == worker
          - node.labels.rustkins.worker_id == worker-1

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: rustkins
      POSTGRES_USER: rustkins
      POSTGRES_PASSWORD: rustkins
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - private
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.rustkins.role == core

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_ADMIN_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_ADMIN_PASSWORD}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - private
      - workers
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.rustkins.role == core

  rustfs:
    image: rustfs/rustfs:latest
    environment:
      RUSTFS_ACCESS_KEY: rustkins
      RUSTFS_SECRET_KEY: rustkins-password
      RUSTFS_CONSOLE_ENABLE: "false"
    volumes:
      - rustfs_data:/data
    networks:
      - private
      - workers
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.rustkins.role == core

volumes:
  postgres_data:
  rabbitmq_data:
  rustfs_data:
  worker_workdir:

networks:
  public:
    driver: overlay
  private:
    driver: overlay
  workers:
    driver: overlay
```

Déploiement :

```bash
docker stack deploy -c stack.v1.yml rustkins
```

Chaque autre worker nécessite un service distinct, un `WORKER_ID`
stable, un compte RabbitMQ propre et une contrainte de placement vers
son hôte dédié. Le mode `global` avec une URL RabbitMQ partagée ne
respecterait pas l'identité par worker. Les variables d'environnement
du fichier stack doivent être renseignées lors du rendu de la
configuration avant `docker stack deploy`.

---

## 16. Différence Compose dev / Swarm V1

| Sujet | Compose dev V1 | Swarm V1 |
|---|---|---|
| Commande | `docker compose up -d` | `docker stack deploy` |
| Cible | Machine dev | Plusieurs nodes |
| Réseau | Bridge Compose | Overlay Swarm |
| Workers | Plusieurs conteneurs locaux | Un service par worker, placé sur son hôte dédié |
| Placement | Non significatif | Labels `core` / `worker` |
| Volumes | Volumes locaux | Volumes locaux du node ciblé |
| PostgreSQL | Local compose | Core node |
| RabbitMQ | Local compose | Core node |
| RustFS | Local compose | Core node |
| Docker socket | Même host dev | Chaque worker node |
| Ressources | Simulées par workers locaux | Capacité par worker node |
| Logs SSE | Local | Via API centrale |
| Artifacts | RustFS local | RustFS core |
| HA | Non | Limitée, pas complète en V1 |
| Kubernetes | Non | Non |

---

## 17. Variables d'environnement à prévoir

### API

```txt
DATABASE_URL
RABBITMQ_URL
RUSTFS_ENDPOINT
RUSTFS_ACCESS_KEY
RUSTFS_SECRET_KEY
RUSTFS_BUCKET_LOGS
RUSTFS_BUCKET_ARTIFACTS
RUSTKINS_PUBLIC_URL
JWT_SECRET
JWT_ISSUER
JWT_AUDIENCE
JWT_ACCESS_TOKEN_TTL_MINUTES
JWT_REFRESH_TOKEN_TTL_DAYS
WEBHOOK_SECRET_ENCRYPTION_KEY
SIGNED_URL_TTL_SECONDS
```

### Scheduler

```txt
DATABASE_URL
RABBITMQ_URL
SCHEDULER_POLL_INTERVAL_SECONDS
SCHEDULER_WORKER_HEARTBEAT_TIMEOUT_SECONDS
OUTBOX_PUBLISH_INTERVAL_SECONDS
JOB_MAX_ATTEMPTS
JOB_RETRY_DELAY_1_SECONDS
JOB_RETRY_DELAY_2_SECONDS
JOB_RETRY_DELAY_3_SECONDS
CANCEL_TIMEOUT_SECONDS
```

### Worker

```txt
WORKER_NAME
WORKER_HOSTNAME
WORKER_TOTAL_CPU_MILLI
WORKER_TOTAL_MEMORY_MB
WORKER_WORKDIR
WORKER_HEARTBEAT_INTERVAL_SECONDS
RABBITMQ_URL
RUSTFS_ENDPOINT
RUSTFS_ACCESS_KEY
RUSTFS_SECRET_KEY
RUSTFS_BUCKET_LOGS
RUSTFS_BUCKET_ARTIFACTS
DOCKER_HOST
DEFAULT_JOB_CPU_MILLI
DEFAULT_JOB_MEMORY_MB
DEFAULT_JOB_TIMEOUT_SECONDS
```

### PostgreSQL

```txt
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

### RabbitMQ

```txt
RABBITMQ_DEFAULT_USER
RABBITMQ_DEFAULT_PASS
```

### RustFS

```txt
RUSTFS_ACCESS_KEY
RUSTFS_SECRET_KEY
RUSTFS_CONSOLE_ENABLE
```

---

## 18. Rétention des logs et artifacts

### 18.1 Logs

Les logs restent persistés dans RustFS.

Décision recommandée V1 :

```txt
Rétention logs par défaut : 60 jours
```

Principe :

```txt
À la création d'un PipelineRun :
  logs_expires_at = created_at + 60 jours

Une tâche quotidienne :
  - sélectionne les JobLogStreams expirés
  - supprime les objets RustFS
  - conserve les métadonnées en base
```

### 18.2 Artifacts

Décision V1 :

```txt
Rétention artifacts par défaut : 30 jours
Taille max artifact : 100 MB
Taille max artifacts par run : 500 MB
```

Chaque projet peut définir :

- rétention par défaut ;
- rétention maximale ;
- taille maximale d'un artifact ;
- taille maximale des artifacts d'un run.

Quand un artifact expire :

```txt
artifact.deleted = true
artifact.deleted_at = now()
objet RustFS supprimé
métadonnées conservées
```

Le run reste consultable, mais l'archive n'est plus téléchargeable.

---

## 19. Points de vigilance infra/dev

### 19.1 Docker socket

Chaque Worker ayant accès au Docker socket contrôle fortement son host Docker. La séparation des réseaux de conteneurs ne protège pas PostgreSQL si le démon Docker est partagé. En production, le plan de contrôle et les workers utilisent des hôtes distincts ; aucun Worker ne dispose du socket Docker d'un hôte du plan de contrôle.

Pistes de durcissement supplémentaires :

```txt
- sandbox plus stricte
- exécution rootless
- isolation par runtime dédié
- backend Kubernetes
```

---

### 19.2 Outbox obligatoire

RabbitMQ ne doit pas être traité comme source de vérité.

Toute décision runtime critique doit être persistée dans PostgreSQL avant publication RabbitMQ.

Sans outbox, une panne RabbitMQ au mauvais moment peut créer un run bloqué ou un job perdu.

---

### 19.3 Idempotence worker

RabbitMQ fonctionne en livraison at-least-once.

Le Worker doit toujours :

```txt
1. publier job.start.requested et attendre job.start.accepted avant de lancer Docker
2. ACK sans exécution un job.start.rejected
```

Le Scheduler doit toujours :

```txt
1. valider le user_id AMQP, le worker assigné, la tentative et la transition d'état de chaque événement
2. ignorer et ACK les résultats en double ou périmés
3. inscrire running, start_request_id et job.start.accepted dans une même transaction ; rejouer l'acceptation pour la même demande encore active, refuser les autres
```

Une tentative de `JobRun` n'est autorisée qu'une fois. Si son issue est perdue après cette autorisation, le Scheduler passe le job et le run à `indeterminate` sans nouvelle tentative automatique par défaut. Les pannes antérieures à l'autorisation utilisent les délais de retry V1. Pour un job YAML v2 avec `retry.worker_loss: unsafe`, une perte du Worker autorisé déclenche une nouvelle tentative avec ces mêmes délais si la limite de trois tentatives le permet. La tentative précédente reste `indeterminate` dans l'historique ; ses événements tardifs ne modifient pas la tentative courante. Si la limite est atteinte sans résultat confirmé, le job et le run restent `indeterminate`, pas `dead_lettered`. Cette option peut répéter des effets externes et ne s'applique pas à une erreur métier ni à un échec connu. Les pipelines YAML v1 gardent le comportement par défaut.

---

### 19.4 Logs temps réel

RabbitMQ transporte les chunks live, mais RustFS reste la source persistante.

Ordre recommandé côté Worker :

```txt
1. écrire le chunk dans RustFS
2. publier le chunk dans RabbitMQ
```

Si l'API ou RabbitMQ tombe, les logs doivent rester récupérables depuis RustFS.

---

### 19.5 Artifacts

Les artifacts doivent être validés strictement :

```txt
- pas de path traversal
- pas de chemins absolus
- pas de symlinks cassés
- checksum SHA-256
- extraction relative au workspace
```

La restauration automatique des artifacts de `needs` doit éviter les collisions de chemins.

---

### 19.6 Ressources workers

La réservation CPU/RAM doit être atomique.

Séquence obligatoire :

```txt
lock worker row
calcul capacité disponible
réservation CPU/RAM
JobRun = queued
création OutboxMessage
commit
```

Sinon deux jobs concurrents peuvent être assignés au même worker au-delà de sa capacité.

---

### 19.7 Webhooks

Un webhook ne doit jamais créer automatiquement un projet ou un pipeline.

La configuration Rustkins reste explicite :

```txt
projet existant
pipeline existant
yaml_path configuré
webhook actif
signature valide
branche compatible
```

---

### 19.8 Secrets

Les secrets complets sont hors V1.

Il faut donc éviter de présenter `vars` comme un mécanisme sûr pour :

```txt
- mots de passe
- tokens
- clés API
- clés privées
- credentials Docker
```

Seuls les secrets webhook sont stockés chiffrés, car le HMAC nécessite de relire la valeur originale.

---

## 20. Critères de validation V1

La V1 est considérée comme validée si :

1. Un utilisateur peut se connecter avec JWT.
2. Un refresh token permet de renouveler un access token.
3. Un utilisateur peut être membre d'un projet avec un rôle.
4. Les rôles bloquent correctement les actions non autorisées.
5. Un token d'API projet peut déclencher un pipeline avec le bon scope.
6. Un webhook GitHub, GitLab ou Gitea signé déclenche un run.
7. Un webhook avec signature absente ou invalide est rejeté en `401`.
8. Une livraison webhook dupliquée est ignorée.
9. Un push sur une branche non autorisée ne crée pas de run.
10. Un projet peut contenir plusieurs pipelines.
11. Le YAML `version: 2` est parsé et validé.
12. Les variables globales et de job sont fusionnées correctement.
13. L'image globale est utilisée quand le job n'a pas d'image.
14. Les ressources CPU/RAM par job sont normalisées.
15. Une `PipelineVersion` immuable est créée ou réutilisée par SHA.
16. Le modèle sépare configuration et runtime.
17. Le Scheduler réserve les ressources avant dispatch.
18. Un job sans worker compatible temporaire passe `waiting_resources`.
19. Un job trop gros pour tous les workers passe `failed`.
20. Un message `job.assigned` est créé via `OutboxMessage` et routé vers la file du worker choisi.
21. L'Outbox Publisher publie vers RabbitMQ après commit.
22. Un Worker exécute un job sans accès à PostgreSQL ; ses événements sont validés puis écrits par le Scheduler.
23. Un doublon RabbitMQ n'exécute pas deux fois le même job.
24. Une erreur d'infrastructure survenue avant l'autorisation de démarrer est retry avec les délais V1.
25. Après 3 tentatives préalables au démarrage, un job passe `dead_lettered`.
26. Si un worker disparaît après autorisation sans résultat confirmé, le job et le run passent `indeterminate` par défaut ; aucun descendant ni nouvelle tentative ne démarre. Un résultat tardif authentifié peut résoudre cet état.
27. Avec `retry.worker_loss: unsafe`, une perte du Worker autorisé crée une nouvelle tentative si la limite le permet ; l'ancienne reste dans l'historique et son résultat tardif ne remplace pas le résultat courant. Si la limite est atteinte sans résultat confirmé, l'issue reste `indeterminate`.
28. Une erreur métier ne déclenche pas de retry.
29. Une step `continue_on_error` en échec devient `warning`.
30. Un job `optional` en échec métier devient `warning`.
31. Un pipeline avec warning mais sans échec obligatoire devient `warning`.
32. `run_if: always` s'exécute après une dépendance échouée.
33. `run_if: on_failure` s'exécute seulement après `failed` ou `dead_lettered`.
34. Un run peut être annulé.
35. Un job en cours peut recevoir une demande d'annulation.
36. Les ressources sont libérées après état final.
37. Un Worker offline est détecté par heartbeat.
38. Les logs sont visibles en temps réel via SSE.
39. Une reconnexion SSE reprend les logs manquants.
40. Les logs complets restent consultables depuis RustFS.
41. Un job peut uploader un artifact.
42. Un artifact est archivé en `tar.gz`.
43. Le checksum SHA-256 est stocké.
44. Un artifact est téléchargeable via API et URL signée.
45. Un job dépendant restaure les artifacts directs de ses `needs`.
46. Les artifacts expirés sont supprimés de RustFS.
47. La stack peut tourner en Docker Compose dev.
48. La stack peut être déployée en Swarm simple avec plusieurs workers.

---

## 21. Résumé final

La V1 doit faire passer Rustkins d'un moteur local viable à un outil CI crédible pour une petite équipe.

Elle doit prouver les fondations suivantes :

```txt
- authentification JWT
- rôles projet
- tokens d'API scopés
- webhooks Git sécurisés
- YAML version 2
- PipelineVersion immuable
- modèle configuration/runtime séparé
- transactional outbox
- RabbitMQ comme transport uniquement
- scheduler centralisé
- workers multiples
- réservation CPU/RAM
- retry infrastructure
- idempotence worker
- annulation
- logs temps réel SSE
- logs persistés RustFS
- artifacts RustFS
- URL signées
- déploiement Docker Compose dev
- déploiement Swarm distribué simple
```

Ce qui reste volontairement repoussé :

```txt
- Kubernetes
- secrets complets
- cache
- services/sidecars
- matrix builds
- pull request triggers
- tag triggers
- conditions avancées when
- permissions très fines
- scheduling intelligent
- haute disponibilité complète
```

La priorité de la V1 est la fiabilité d'équipe : déclenchements automatiques, sécurité minimale solide, exécution distribuée simple, logs temps réel, artifacts et robustesse face aux doublons ou aux pannes temporaires.
