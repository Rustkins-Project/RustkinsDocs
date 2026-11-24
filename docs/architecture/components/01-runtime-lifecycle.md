---
id: DOC-0002
title: "Runtime & Execution Lifecycle (Rustkins V1)"
type: architecture
status: draft
summary: "Cycle de vie des exécutions Rustkins V1, de la création des runs à leur ordonnancement et exécution par les workers."
topics: [runtime, scheduler, worker, pipeline]
applies_to: [V1]
---

# ARCH-01 --- Runtime & Execution Lifecycle (Rustkins V1)

**Status:** Draft (Implementation Reference)\
**Scope:** Rustkins V1

------------------------------------------------------------------------

# 1. Purpose

This document specifies the runtime execution model of Rustkins V1.

It is the reference for implementing:

-   API
-   Scheduler
-   Worker
-   RabbitMQ integration
-   Pipeline execution
-   Retry mechanism
-   Cancellation
-   Resource scheduling

It intentionally does **not** cover:

-   UI
-   Observability
-   Metrics
-   Kubernetes
-   Matrix builds

------------------------------------------------------------------------

# 2. Vocabulary

  -----------------------------------------------------------------------
  Term                    Definition
  ----------------------- -----------------------------------------------
  Project                 Repository managed by Rustkins

  Pipeline                Logical pipeline configured in Rustkins

  Pipeline Version        Immutable snapshot of a YAML definition for one
                          Git SHA

  Pipeline Run            One execution of one Pipeline Version

  Job Run                 Runtime execution of one job

  Step Run                Runtime execution of one step

  Worker                  Machine executing Docker containers

  Scheduler               Component deciding which job can start

  Artifact                File produced by a JobRun
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 3. High level architecture

``` mermaid
flowchart LR

Git --> API
API --> PipelineVersion
PipelineVersion --> Scheduler
Scheduler --> PostgreSQL
PostgreSQL --> OutboxPublisher
OutboxPublisher --> RabbitMQ
RabbitMQ -->|job.assigned| Worker
Worker --> Docker
Docker --> RustFS
Worker -->|events| RabbitMQ
RabbitMQ -->|events| Scheduler
```

Workers never access PostgreSQL. They receive self-contained execution
orders and report events to the Scheduler, which is the only writer of
runtime state ([ADR-0001](../../../decisions/ADR-0001-worker-scheduler-communication.md)).

Responsibilities:

  Component    Responsibility
  ------------ -----------------------------------------
  API          Receive requests and webhooks
  Scheduler    Build execution graph, dispatch jobs, persist Worker events
  OutboxPublisher Publish durable outbox messages to RabbitMQ
  Worker       Execute Docker containers and report events
  PostgreSQL   Source of truth
  RabbitMQ     Transport layer
  RustFS       Persistent storage

------------------------------------------------------------------------

# 4. Runtime model

Execution hierarchy

``` text
Project
 └── Pipeline
      └── Pipeline Version
           └── Pipeline Run
                ├── Job Run
                │      ├── Step Run
                │      ├── Logs
                │      └── Artifacts
                └── Job Run
```

Each PipelineVersion is immutable.

Each PipelineRun references exactly one PipelineVersion.

A PipelineVersion may be executed many times.

------------------------------------------------------------------------

# 5. Pipeline Run lifecycle

## States

  State       Meaning
  ----------- ------------------------------------------------------------
  queued      Created but not started
  running     At least one job running
  success     All mandatory jobs succeeded
  warning     No mandatory failure occurred, but at least one job ended in warning
  failed      Mandatory execution failed
  cancelled   Execution cancelled
  indeterminate  An authorized job lost its result; execution is suspended for review

State machine

``` mermaid
stateDiagram-v2
[*] --> queued
queued --> running
queued --> cancelled
running --> success
running --> warning
running --> failed
running --> cancelled
running --> indeterminate
running --> retrying
indeterminate --> running
```

Transition rules

### queued → running

Conditions

-   pipeline version validated
-   DAG created
-   first runnable job queued

### running → success

Conditions

-   no JobRun = warning
-   no failed mandatory jobs
-   no dead_lettered jobs
-   no indeterminate jobs
-   skipped jobs are only skipped because their `run_if` condition was not satisfied

### running → warning

Conditions

-   no mandatory JobRun = failed
-   no JobRun = dead_lettered
-   one or more JobRuns = warning

### running → failed

Conditions

-   mandatory job failed
-   dead_lettered reached

### running → cancelled

User explicitly cancelled execution.

### running → indeterminate

A Worker disappeared or cancellation timed out after start
authorization without a confirmed final event. The Scheduler does not retry that job or unlock its
dependents. A late authenticated result from the same attempt, or
operator reconciliation, can resume the PipelineRun.

------------------------------------------------------------------------

# 6. Job lifecycle

States

``` text
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

``` mermaid
stateDiagram-v2
[*] --> waiting_dependencies
waiting_dependencies --> waiting_resources
waiting_dependencies --> queued
waiting_resources --> queued
queued --> running
queued --> retrying
queued --> cancelled
running --> success
running --> warning
running --> failed
running --> indeterminate
running --> cancel_requested
cancel_requested --> cancelled
cancel_requested --> indeterminate
retrying --> queued
retrying --> dead_lettered
indeterminate --> success
indeterminate --> warning
indeterminate --> failed
indeterminate --> cancelled
```

Detailed description

### waiting_dependencies

The DAG still blocks execution.

### waiting_resources

Dependencies satisfied but scheduler found no compatible worker.

### queued

Resources reserved.

A durable OutboxMessage exists for RabbitMQ dispatch.

The RabbitMQ message may already be published or still pending in the
outbox.

### running

The Scheduler committed start authorization for the assigned attempt:
`running`, its `start_request_id` and the `job.start.accepted` outbox
message. The Worker may still be waiting for that response.

### success

Container finished with exit code 0.

### warning

Execution completed with a non blocking issue.

Examples:

-   a `continue_on_error` step failed
-   an optional job encountered a business failure
-   an artifact operation on an optional job failed

### failed

Business execution failure.

Examples

-   tests failed
-   build failed
-   script exit code != 0

If the JobRun is optional, a business failure produces `warning`
instead of `failed`.

Infrastructure failures follow the default automatic retry policy only
when no start authorization was committed. An authorized Worker loss
may be retried only with YAML v2 `retry.worker_loss: unsafe`.

### retrying

Infrastructure failure.

### dead_lettered

Maximum retries before start authorization exceeded. An authorized
Worker loss without a confirmed result remains `indeterminate` if the
attempt limit is exhausted, even with `retry.worker_loss: unsafe`.

### indeterminate

Start was authorized, but the result is unknown after Worker loss or
cancellation timeout. By default no retry is dispatched. A late result
from the original attempt can settle the state; otherwise an operator
must check external effects before any new execution is considered.
With YAML v2 `retry.worker_loss: unsafe`, only Worker loss permits
another attempt; the original attempt remains `indeterminate` in the
audit history.

------------------------------------------------------------------------

# 7. Warning semantics

`warning` is a final non-blocking runtime state.

It preserves diagnostic information without failing the entire
PipelineRun.

## Step warning

A StepRun becomes `warning` when:

-   the command exits with a non-zero code
-   the PipelineVersionStep has `continue_on_error = true`

The Worker continues with the next step.

If no later blocking failure occurs, the parent JobRun finishes as
`warning`.

## Job warning

A JobRun becomes `warning` when:

-   at least one StepRun is `warning` and no blocking step failed
-   the PipelineVersionJob is `optional = true` and a business failure occurs
-   an artifact operation on an optional job fails

JobRun `warning` is treated as completed and non-blocking by the DAG.

## Pipeline warning

A PipelineRun becomes `warning` when:

-   at least one JobRun is `warning`
-   no mandatory JobRun is `failed`
-   no JobRun is `dead_lettered`
-   no JobRun is `indeterminate`

## Dependency evaluation

For `run_if`:

-   `all_success` accepts dependencies in `success` or `warning`
-   `always` accepts dependencies in any known final state;
    `indeterminate` blocks it
-   `on_failure` only matches dependencies in `failed` or `dead_lettered`

------------------------------------------------------------------------

# 8. Scheduler responsibilities

The Scheduler is responsible for:

-   validating dependencies
-   evaluating resource availability
-   reserving worker capacity
-   releasing worker capacity
-   creating durable RabbitMQ outbox messages
-   updating runtime state

The Scheduler NEVER executes containers.

The Outbox Publisher is responsible for publishing pending outbox
messages to RabbitMQ.

------------------------------------------------------------------------

# 9. Retry strategy

Maximum attempts

``` text
3
```

Delays

``` text
Attempt 1 -> 30 s
Attempt 2 -> 2 min
Attempt 3 -> 5 min
```

Retry infrastructure failures automatically by default only when start
was never authorized. A lost result after authorization becomes
`indeterminate` even when attempts remain. YAML v2
`retry.worker_loss: unsafe` explicitly permits a new attempt after
authorized Worker loss, up to the global three-attempt limit. The old
attempt stays `indeterminate` in the audit history; a late result
cannot overwrite the new attempt. External effects may repeat.

Retryable examples

-   Docker daemon unavailable during preflight
-   RabbitMQ connection lost before authorization
-   PostgreSQL timeout before authorization
-   Worker crash before start authorization

Non retryable

-   Tests failed
-   Exit code != 0
-   YAML validation
-   Build failed
-   Worker loss after start authorization with no confirmed result,
    unless the job explicitly sets `retry.worker_loss: unsafe`

State transition

``` mermaid
flowchart LR
FailedInfra --> Retrying
Retrying --> Queue
Retrying --> DLQ
```

------------------------------------------------------------------------

# 10. Cancellation

Queued jobs

-   status = cancelled
-   no RabbitMQ publication

Running jobs

1.  status = cancel_requested
2.  create cancel OutboxMessage routed to the assigned Worker's control
    queue; for a run-wide cancellation, target each Worker with an
    active job in that run
3.  worker stops container
4.  worker confirms with `job.finished` (status `cancelled`)
5.  scheduler releases resources
6.  status = cancelled

If worker disappears

If start was authorized and no final result was confirmed, the JobRun
and PipelineRun become `indeterminate`. No automatic retry follows a
cancellation timeout. A late authenticated result can resolve it.

------------------------------------------------------------------------

# 11. Idempotency

RabbitMQ provides at-least-once delivery.

Workers publish `job.start.requested` and wait for `job.start.accepted` before
launching Docker. The Scheduler atomically authorizes only the first
valid request for the assigned `job_run_id:attempt` and stores its
`start_request_id`. Retransmissions of that same request while the
attempt is current and running receive the same acceptance. A distinct
or stale request receives `job.start.rejected` and is ACKed without
execution. Workers keep no durable deduplication registry.

The Scheduler validates every Worker event against the JobRun state.

Rules

-   duplicate or stale result event -\> ignore and ACK
-   current running attempt with the same `start_request_id` -\> replay
    `job.start.accepted` without authorizing a second execution
-   current running attempt with a different `start_request_id`, or a
    stale attempt -\> send `job.start.rejected`
-   terminal attempt -\> send `job.start.rejected` for any start request

------------------------------------------------------------------------

# 12. Runtime events

Pipeline events

-   pipeline_created
-   pipeline_started
-   pipeline_finished
-   pipeline_cancelled

Job events

-   job_waiting_dependencies
-   job_waiting_resources
-   job_queued
-   job_started
-   job_warning
-   job_retry
-   job_finished
-   job_cancel_requested
-   job_cancelled
-   job_dead_lettered

`job_started` is a persisted audit event for the actual execution
start, after `job.start.accepted`. It is distinct from the RabbitMQ
`job.start.requested` authorization request.

Storage events

-   artifact_uploaded
-   logs_completed

------------------------------------------------------------------------

# 13. Typical execution sequence

``` mermaid
sequenceDiagram
participant API
participant Scheduler
participant OutboxPublisher
participant RabbitMQ
participant Worker
participant Docker

API->>Scheduler: Create PipelineRun
Scheduler->>Scheduler: Build DAG
Scheduler->>Scheduler: Reserve resources
Scheduler->>Scheduler: Insert OutboxMessage(job.assigned)
OutboxPublisher->>RabbitMQ: Publish outbox message
RabbitMQ->>Worker: job.assigned
Worker->>RabbitMQ: job.start.requested
RabbitMQ->>Scheduler: job.start.requested
Scheduler->>Scheduler: Persist running + outbox(job.start.accepted)
RabbitMQ->>Worker: job.start.accepted
Worker->>Docker: Start container
Docker-->>Worker: Exit code
Worker->>RabbitMQ: job.finished
RabbitMQ->>Scheduler: job.finished
Scheduler->>Scheduler: Persist state, release resources
Scheduler->>Scheduler: Unlock dependent jobs, assign next jobs
```

------------------------------------------------------------------------

# 14. Runtime invariants

The following rules MUST always remain true.

-   One PipelineRun references exactly one PipelineVersion.
-   PipelineVersion objects are immutable.
-   One JobRun belongs to exactly one PipelineRun.
-   One StepRun belongs to exactly one JobRunAttempt and one immutable
    PipelineVersionStep. Separate attempts retain separate step results.
-   Scheduler is the only component allowed to enqueue jobs.
-   Scheduler is the only component allowed to reserve or release worker capacity.
-   Scheduler orders and control messages are persisted as
    OutboxMessages before publication; Worker events and live log
    chunks are published with broker confirmations.
-   Workers never modify DAG topology.
-   Workers never access PostgreSQL; the Scheduler is the only writer
    of runtime execution state.
-   A completed JobRun never returns to running.
-   Dead-lettered jobs require manual retry.
-   PostgreSQL is the single source of truth.

------------------------------------------------------------------------

# 15. ADR

## ADR-001

Decision

Pipeline definitions are immutable through PipelineVersion.

Consequence

Historical executions remain reproducible.

------------------------------------------------------------------------

## ADR-002

Decision

Scheduler owns execution ordering.

Consequence

Workers keep only in-memory state for active jobs; PostgreSQL and
RabbitMQ hold the durable execution state.

------------------------------------------------------------------------

## ADR-003

Decision

Retry only infrastructure failures.

Consequence

Business failures remain deterministic.

------------------------------------------------------------------------

## ADR-004

Decision

Dedicated waiting_resources state.

Consequence

Scheduler can distinguish dependency blocking from capacity blocking.

------------------------------------------------------------------------

# 16. Future evolution

Planned V2

-   Worker labels
-   Affinity
-   Priority scheduling
-   Matrix execution
-   Dynamic DAG generation
-   Multi-queue scheduling
