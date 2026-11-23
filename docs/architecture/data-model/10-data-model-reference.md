---
id: DOC-0012
title: "Data Model Reference (Rustkins V1)"
type: architecture
status: draft
summary: "Sémantique et relations des entités Rustkins V1 : identité, configuration des pipelines et exécution des runs."
topics: [data-model, postgresql, pipeline, runtime]
applies_to: [V1]
---

# ARCH-10 --- Data Model Reference (Rustkins V1)

**Status:** Draft (Implementation Reference)

------------------------------------------------------------------------

# 1. Purpose

This document explains the role of every entity composing the Rustkins
V1 data model.

The Entity Relationship Diagram (ERD) defines the structure. This
document explains the semantics, ownership rules, lifecycle and
relationships.

------------------------------------------------------------------------

# 2. Model Overview

``` mermaid
flowchart TD

PROJECT --> PIPELINE
PIPELINE --> PIPELINE_VERSION
PIPELINE_VERSION --> PIPELINE_RUN

PIPELINE_VERSION --> PIPELINE_VERSION_JOB
PIPELINE_VERSION_JOB --> PIPELINE_VERSION_STEP

PIPELINE_RUN --> JOB_RUN
JOB_RUN --> JOB_RUN_ATTEMPT
JOB_RUN_ATTEMPT --> STEP_RUN

JOB_RUN --> ARTIFACT
JOB_RUN --> JOB_LOG_STREAM
PIPELINE_RUN --> OUTBOX_MESSAGE
```

The model is intentionally divided into three domains:

-   Identity & Security
-   Pipeline Configuration
-   Runtime Execution

------------------------------------------------------------------------

# 3. Identity Domain

## USER

Represents one authenticated Rustkins user.

Responsibilities

-   Login
-   Project membership
-   Manual pipeline execution
-   Pipeline cancellation

Lifecycle

Created once. Never deleted physically.

------------------------------------------------------------------------

## USER_REFRESH_TOKEN

Represents one refresh token bound to a device/session.

Characteristics

-   hashed
-   revocable
-   expires
-   one record per session

------------------------------------------------------------------------

## PROJECT_MEMBER

Associates a User with a Project.

Stores

-   role
-   creation date

Valid roles

``` text
owner
maintainer
developer
viewer
```

------------------------------------------------------------------------

# 4. Project Domain

## PROJECT

Root entity.

Represents one Git repository managed by Rustkins.

Owns

-   members
-   pipelines
-   API tokens
-   webhook configuration
-   retention policy
-   pipeline runs

------------------------------------------------------------------------

## API_TOKEN

Authentication for automation.

Characteristics

-   project scoped
-   hashed
-   structured scopes stored in `scopes_json`
-   optional expiration

V1 scopes are stored as a JSON array of scope strings, rather than in
separate permission rows.

------------------------------------------------------------------------

## WEBHOOK_CONFIG

Stores webhook provider configuration.

Contains

-   provider
-   encrypted HMAC secret
-   enabled flag

One project may expose several webhook configurations.

------------------------------------------------------------------------

## WEBHOOK_DELIVERY

Historical record of received webhook deliveries.

Purpose

-   deduplication
-   audit
-   diagnostics

Only `push` deliveries trigger runs in V1. `before_sha` and `after_sha`
preserve the pushed range; the run executes `after_sha`.

Never deleted automatically.

------------------------------------------------------------------------

# 5. Pipeline Definition Domain

## PIPELINE

Logical CI pipeline.

Represents

``` text
.rustkins/ci.yml
```

Stores

-   name
-   yaml path
-   activation state

Does not store execution data.

------------------------------------------------------------------------

## PIPELINE_VERSION

Immutable snapshot of a pipeline.

Created for one Git SHA.

Stores

-   YAML
-   YAML specification version (v1 or v2 in product V1)
-   validation result
-   hash

One Pipeline owns many versions.

Versions never change.

------------------------------------------------------------------------

## PIPELINE_VERSION_JOB

Represents one parsed job.

Contains immutable execution definition:

-   stable YAML key and human-readable name
-   image
-   resources
-   timeout
-   run_if
-   optional
-   retry_worker_loss (`never` or `unsafe`, default `never`)

`optional = true` means that business failures on this job produce a
JobRun `warning` instead of a PipelineRun-blocking `failed`.

------------------------------------------------------------------------

## PIPELINE_VERSION_STEP

Represents one immutable command.

Contains

-   command
-   order
-   continue_on_error

`continue_on_error = true` means that a non-zero command exit produces a
StepRun `warning` and does not stop the remaining steps of the same job.

------------------------------------------------------------------------

## PIPELINE_VERSION_JOB_DEPENDENCY

Represents the immutable DAG.

Purpose

Describe execution order exactly as defined in YAML.

------------------------------------------------------------------------

# 6. Runtime Domain

## PIPELINE_RUN

Represents one execution.

References

-   project
-   pipeline
-   pipeline version

Stores

-   trigger
-   status
-   branch
-   commit
-   author

`trigger_type` records the business origin: `manual`, `api` or
`webhook`. Exactly the corresponding nullable reference is populated:

``` text
manual  -> triggered_by_user_id
api     -> triggered_by_api_token_id
webhook -> webhook_delivery_id
```

The Git context is captured directly on PipelineRun for V1.

------------------------------------------------------------------------

## JOB_RUN

Runtime execution of one PipelineVersionJob.

Stores only runtime state.

Examples

-   worker
-   status
-   retry count
-   exit code
-   timestamps

Written only by the Scheduler, including from Worker events
(`job.start.requested`, `step.finished`, `job.finished`).

`warning` is a final non-blocking status used when a job completed with
non-blocking issues.

`worker_node_id` on JobRun is the current assignment. Each
JobRunAttempt keeps its own WorkerNode so reassignment does not erase
the worker that ran a previous attempt. JobRun `exit_code` summarizes
the final outcome.

------------------------------------------------------------------------

## JOB_RUN_DEPENDENCY

Runtime DAG.

Allows scheduler to reason on execution state without modifying
immutable definitions.

------------------------------------------------------------------------

## JOB_RUN_ATTEMPT

One precise attempt of a JobRun on one WorkerNode.

Purpose

Keep retry history independently from JobRun.

Each attempt retains its own status, nullable exit code, error message,
creation time and execution times. Infrastructure failure before start
authorization may be retried; after an authorized Worker is lost, the
existing `retry.worker_loss` policy determines whether another attempt
is allowed.

`start_request_id` is null before authorization and then stores the
start request accepted by the Scheduler. Retransmitting that same
request can replay the acceptance without granting a second
authorization.

When an authorized Worker is lost without a confirmed result, the
attempt is `indeterminate`. With YAML v2 `retry.worker_loss: unsafe`,
a new attempt may start while this record remains available for audit.
A late result from the older attempt cannot change the current one.

The Scheduler records `cpu_seconds` and `memory_peak_mb` from the
validated `job.finished` event on this attempt. `cpu_seconds` is the
container CPU time, not wall-clock duration; `memory_peak_mb` is the
highest observed container memory use. Wall-clock duration is derived
from `started_at` and `finished_at`. A missing measurement remains
`null`, for example after Worker loss, rather than being recorded as
zero. These fields do not estimate energy or CO2e.

Per-Worker utilization, image download time and size, and storage
volumes are not part of this V1 contract. Their collection and export
still require a separate specification.

------------------------------------------------------------------------

## STEP_RUN

Execution state of one PipelineVersionStep within one JobRunAttempt.

Contains

-   status
-   exit code
-   timestamps

`warning` is used when the step command failed but the corresponding
PipelineVersionStep has `continue_on_error = true`.

This association preserves step results from earlier attempts when a
job is retried. The Scheduler accepts a `step.finished` event only for
the matching Worker and attempt.

------------------------------------------------------------------------

## RUN_EVENT

Business events produced during execution.

Examples

``` text
job_started
job_finished
artifact_uploaded
retry
cancelled
```

Used for audit and diagnostics.

`message` is human-readable; `payload_json` holds structured event
details, and `severity` is `info`, `warning` or `error`.

`job_started` records actual execution after authorization; the AMQP
request sent beforehand is named `job.start.requested`.

------------------------------------------------------------------------

## OUTBOX_MESSAGE

Durable message waiting to be published to RabbitMQ.

Purpose

-   bridge PostgreSQL transactions and RabbitMQ publication
-   avoid losing dispatch messages after a database commit
-   make RabbitMQ publication retryable

Stores

-   optional pipeline run reference
-   optional job run reference
-   exchange
-   routing key
-   event type
-   payload
-   status
-   attempts
-   next retry date
-   last error

Status values

``` text
pending
publishing
published
failed
```

The Scheduler creates OutboxMessages inside the same transaction as the
runtime state change.

The Outbox Publisher is the only component allowed to mark an
OutboxMessage as `published`.

------------------------------------------------------------------------

# 7. Infrastructure Domain

## WORKER_NODE

Represents one execution node.

Stores

-   capacity
-   reservations
-   heartbeat
-   status

Scheduler is the only component allowed to reserve and release capacity.

Created and updated by the Scheduler from `worker.registered` and
`worker.heartbeat` events. Workers never access PostgreSQL
([ADR-0001](../../../decisions/ADR-0001-worker-scheduler-communication.md)).

------------------------------------------------------------------------

## JOB_LOG_STREAM

Metadata describing one persistent log stream.

Binary log content is stored in RustFS.

------------------------------------------------------------------------

## LOG_EVENT

Transient log chunk.

Transported through RabbitMQ and SSE.

Not persisted in PostgreSQL.

------------------------------------------------------------------------

## ARTIFACT

Metadata describing one uploaded archive.

Stores

-   storage key
-   checksum
-   size
-   expiration

Archive bytes remain in RustFS.

------------------------------------------------------------------------

## ARTIFACT_RETENTION_POLICY

Project retention configuration.

Defines

-   default retention
-   maximum retention
-   size limits

A Project has zero or one retention policy; `project_id` is unique.

------------------------------------------------------------------------

# 8. Field Reference

All `id` fields are UUID primary keys. Foreign keys are required unless
marked nullable below. Lifecycle timestamps remain null until the
corresponding transition occurs. The MCD describes PostgreSQL entities;
LogEvent is a transient RabbitMQ/SSE message and has no database key.

## Identity and Project

### USER

-   `email`, `username`: login identity and display identifier.
-   `password_hash`, `role_global`, `is_active`: credentials, platform
    role and account availability.
-   `created_at`, `updated_at`, `last_login_at`: creation, modification
    and nullable last successful login.

### USER_REFRESH_TOKEN

-   `user_id`, `token_hash`: owning User and hashed token.
-   `created_at`, `expires_at`, `revoked_at`: issue, expiry and nullable
    revocation.
-   `user_agent`, `ip_address`: session audit context.

### PROJECT

-   `name`, `slug`: display name and stable URL identifier.
-   `repository_url`, `default_branch`: Git origin and default branch.
-   `is_active`, `created_at`, `updated_at`: activation and lifecycle.

### PROJECT_MEMBER

-   `project_id`, `user_id`: associated Project and User.
-   `role`: `owner`, `maintainer`, `developer` or `viewer`.
-   `created_at`: membership creation.

### API_TOKEN

-   `project_id`, `name`: owning Project and token label.
-   `token_prefix`, `token_hash`: lookup prefix and hashed secret.
-   `scopes_json`: JSON array of V1 scope strings.
-   `revoked`, `created_at`, `expires_at`, `last_used_at`: revocation,
    creation, nullable expiry and nullable last use.

### WEBHOOK_CONFIG

-   `project_id`, `provider`: owning Project and Git provider.
-   `encrypted_secret`, `enabled`: HMAC secret and activation.
-   `created_at`, `updated_at`: lifecycle.

### WEBHOOK_DELIVERY

-   `project_id`, `webhook_config_id`: target Project and receiving
    configuration.
-   `external_delivery_id`: provider identifier used for deduplication
    within that configuration.
-   `event_type`, `branch`: provider event (`push` in V1) and branch.
-   `before_sha`, `after_sha`: pushed range; `after_sha` is the executed
    commit when a run is created.
-   `status`, `error_message`: processing state and nullable failure.
-   `received_at`, `processed_at`: receipt and nullable completion.

## Pipeline Definition

### PIPELINE

-   `project_id`, `name`, `yaml_path`: owner, display name and
    repository-relative YAML path.
-   `is_active`, `created_at`, `updated_at`: activation and lifecycle.

### PIPELINE_VERSION

-   `pipeline_id`, `git_sha`: owning Pipeline and Git revision.
-   `yaml_hash`, `yaml_content`: content hash and original source.
-   `specification_version`: top-level YAML `version`, independently of
    the product version; product V1 accepts YAML v1 and v2.
-   `validation_status`, `validation_errors_json`: validation outcome
    and structured errors.
-   `created_at`: immutable snapshot creation.

The normalized `PIPELINE_VERSION_*` rows are the engine representation;
there is no duplicate global parsed-definition JSON column.

### PIPELINE_VERSION_JOB

-   `pipeline_version_id`, `job_key`, `name`: owning snapshot, stable
    YAML key and human-readable name.
-   `image`, `run_if`, `optional`, `retry_worker_loss`: execution image,
    dependency rule, non-blocking behavior and Worker-loss policy.
-   `cpu_limit_milli`, `memory_limit_mb`, `timeout_seconds`: resource
    and duration limits.
-   `order_index`: deterministic definition order.

### PIPELINE_VERSION_STEP

-   `pipeline_version_job_id`, `step_key`, `name`: owning job, stable
    step key and human-readable name.
-   `command`, `order_index`, `continue_on_error`: command, order and
    non-blocking failure setting.

### PIPELINE_VERSION_JOB_DEPENDENCY

-   `pipeline_version_job_id`: dependent definition.
-   `depends_on_pipeline_version_job_id`: prerequisite definition.

## Runtime

### PIPELINE_RUN

-   `project_id`, `pipeline_id`, `pipeline_version_id`: owner, logical
    Pipeline and immutable snapshot.
-   `triggered_by_user_id`, `triggered_by_api_token_id`,
    `webhook_delivery_id`: nullable and mutually exclusive origins.
-   `cancelled_by_user_id`: nullable cancelling User.
-   `trigger_type`: `manual`, `api` or `webhook`.
-   `status`: aggregate execution state.
-   `branch`, `commit_sha`, `commit_message`, `author_name`,
    `author_email`: captured V1 Git context.
-   `created_at`, `started_at`, `finished_at`, `cancelled_at`,
    `cancel_reason`: creation and nullable execution/cancellation audit.

### JOB_RUN

-   `pipeline_run_id`, `pipeline_version_job_id`: run and immutable job
    definition.
-   `worker_node_id`: nullable current assignment; historical assignment
    belongs to each attempt.
-   `status`, `idempotency_key`: logical state and dispatch key.
-   `attempt_count`, `max_attempts`: attempts created and retry ceiling.
-   `queued_at`, `started_at`, `finished_at`, `cancelled_at`,
    `cancel_reason`: execution and cancellation audit.
-   `exit_code`: nullable summarized final process exit.

### JOB_RUN_DEPENDENCY

-   `job_run_id`: dependent runtime job.
-   `depends_on_job_run_id`: prerequisite runtime job.

### JOB_RUN_ATTEMPT

-   `job_run_id`, `worker_node_id`, `attempt_number`: logical job,
    assigned Worker and one-based sequence.
-   `start_request_id`: nullable until start authorization; identifies
    the accepted request for this attempt.
-   `status`, `exit_code`, `error_message`: attempt result and nullable
    process exit or diagnostic detail.
-   `cpu_seconds`, `memory_peak_mb`: nullable observed container usage,
    recorded from a validated `job.finished` event.
-   `created_at`, `started_at`, `finished_at`: creation and nullable
    execution boundaries.

### STEP_RUN

-   `job_run_attempt_id`, `pipeline_version_step_id`: precise attempt
    and immutable step definition.
-   `status`, `exit_code`: step outcome and nullable command exit.
-   `started_at`, `finished_at`: nullable execution boundaries.

### RUN_EVENT

-   `pipeline_run_id`, `job_run_id`: owning run and nullable concerned
    job.
-   `event_type`, `severity`, `message`, `payload_json`: event name,
    level, readable message and structured detail.
-   `created_at`: event creation.

### OUTBOX_MESSAGE

-   `pipeline_run_id`, `job_run_id`: nullable runtime references. The
    message contract defines which one is required for each event type.
-   `exchange`, `routing_key`, `event_type`, `payload_json`: RabbitMQ
    destination and message body.
-   `status`, `attempts`, `next_attempt_at`, `last_error`: publication
    state and retry audit.
-   `created_at`, `published_at`: creation and nullable publication.

## Infrastructure

### WORKER_NODE

-   `name`, `hostname`, `status`: identity and availability.
-   `total_cpu_milli`, `total_memory_mb`: advertised capacity.
-   `reserved_cpu_milli`, `reserved_memory_mb`: Scheduler reservations.
-   `last_heartbeat_at`, `created_at`: liveness and registration.

### JOB_LOG_STREAM

-   `job_run_id`, `storage_key`, `last_sequence`: owning job, RustFS
    object key and last persisted chunk number.
-   `created_at`, `updated_at`: lifecycle.

### LOG_EVENT

-   `sequence`, `stream`, `content`, `emitted_at`: transient chunk order,
    output channel, text and emission time.

### ARTIFACT

-   `pipeline_run_id`, `job_run_id`: producing run and job.
-   `name`, `archive_name`, `storage_key`: label, uploaded archive name
    and RustFS object key.
-   `size_bytes`, `content_type`, `checksum_sha256`: size, media type
    and integrity checksum.
-   `created_at`, `expires_at`, `deleted_at`, `deleted`: upload,
    retention expiry and deletion audit.

### ARTIFACT_RETENTION_POLICY

-   `project_id`: uniquely configured Project.
-   `default_retention_days`, `max_retention_days`: retention limits.
-   `max_artifact_size_mb`, `max_run_artifacts_size_mb`: upload limits.
-   `created_at`, `updated_at`: lifecycle.

------------------------------------------------------------------------

# 9. Entity Lifecycles

## Immutable

``` text
PIPELINE_VERSION
PIPELINE_VERSION_JOB
PIPELINE_VERSION_STEP
PIPELINE_VERSION_JOB_DEPENDENCY
```

## Mutable

``` text
PIPELINE_RUN
JOB_RUN
JOB_RUN_ATTEMPT
STEP_RUN
WORKER_NODE
OUTBOX_MESSAGE
```

## Ephemeral

``` text
LOG_EVENT
```

------------------------------------------------------------------------

# 10. Relations and Constraints

-   Every ProjectMember belongs to one User and Project. Each API token,
    webhook configuration, Pipeline and PipelineRun belongs to one Project.
    Every WebhookDelivery also belongs to one Project and one
    WebhookConfig.
-   A Project has zero or one ArtifactRetentionPolicy; other Project
    collections have zero or many records.
-   Every PipelineVersion belongs to one Pipeline. Its job, step and
    definition-dependency rows form an immutable DAG.
-   Every PipelineRun references exactly one PipelineVersion. Exactly
    one origin reference matches its `trigger_type`; the cancelling User
    remains optional.
-   Every JobRun references exactly one PipelineVersionJob. A JobRun has
    zero or many attempts, each retaining its assigned WorkerNode.
-   Every StepRun references exactly one JobRunAttempt and one
    PipelineVersionStep. This keeps step outcomes separate across retries.
-   Every Artifact belongs to one PipelineRun and one JobRun. Every
    RunEvent belongs to one PipelineRun and may concern one JobRun.
-   An OutboxMessage may reference a PipelineRun, a JobRun, both or
    neither, subject to its message contract.
-   Scheduler orders and control messages are persisted as
    OutboxMessages before publication. Worker events and log chunks
    are published with RabbitMQ confirmations instead.
-   Pipeline definitions never depend on runtime entities.

Relational uniqueness constraints:

``` text
PROJECT_MEMBER: UNIQUE(project_id, user_id)
WEBHOOK_DELIVERY: UNIQUE(webhook_config_id, external_delivery_id)
PIPELINE_VERSION_JOB: UNIQUE(pipeline_version_id, job_key)
PIPELINE_VERSION_STEP: UNIQUE(pipeline_version_job_id, step_key)
PIPELINE_VERSION_STEP: UNIQUE(pipeline_version_job_id, order_index)
PIPELINE_VERSION_JOB_DEPENDENCY:
    UNIQUE(pipeline_version_job_id, depends_on_pipeline_version_job_id)
JOB_RUN: UNIQUE(pipeline_run_id, pipeline_version_job_id)
JOB_RUN_ATTEMPT: UNIQUE(job_run_id, attempt_number)
JOB_RUN_DEPENDENCY: UNIQUE(job_run_id, depends_on_job_run_id)
STEP_RUN: UNIQUE(job_run_attempt_id, pipeline_version_step_id)
ARTIFACT_RETENTION_POLICY: UNIQUE(project_id)
```

`JOB_RUN` uniqueness holds in V1 because matrix expansion is out of
scope. It must be revisited when one definition can create several
runtime jobs in the same PipelineRun.

Functional consistency constraints:

-   `manual` requires `triggered_by_user_id`; `api` requires
    `triggered_by_api_token_id`; `webhook` requires
    `webhook_delivery_id`. The other two origin fields must be null.
-   The trigger reference belongs to the PipelineRun's Project.
    WebhookDelivery and its WebhookConfig refer to that same Project.
-   A PipelineRun's PipelineVersion belongs to its Pipeline; each
    JobRun's PipelineVersionJob belongs to that run's PipelineVersion.
    Runtime dependencies connect jobs within the same PipelineRun.
-   An Artifact's JobRun and a RunEvent's optional JobRun belong to
    their recorded PipelineRun.
-   The JobRun `worker_node_id` is the current assignment; the attempt
    row is the historical source for the Worker that ran that attempt.
-   A `STEP_RUN` must refer to a PipelineVersionStep belonging to the
    PipelineVersionJob used by its parent attempt's JobRun.

------------------------------------------------------------------------

# 11. Historical Design Notes

## Configuration and runtime

Configuration and runtime are separated.

Consequence

Pipeline history remains immutable.

------------------------------------------------------------------------

## Binary storage

Binary data is never stored in PostgreSQL.

Consequence

Database remains lightweight.

------------------------------------------------------------------------

## Runtime state

Runtime tables store only execution state.

Consequence

Configuration duplication is minimized.

------------------------------------------------------------------------

## Historical pipeline definitions

PipelineVersion is the historical source of truth.

Consequence

Every execution remains reproducible.

------------------------------------------------------------------------

# 12. Future Evolution

Candidates

-   Organizations
-   Teams
-   Secret entities
-   Cache entities
-   Matrix execution
-   Kubernetes resources
