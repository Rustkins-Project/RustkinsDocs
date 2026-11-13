---
id: DOC-0005
title: "RabbitMQ Architecture (Rustkins V1)"
type: architecture
status: draft
summary: "Architecture RabbitMQ V1 : échanges, files, transport des ordres de jobs, annulations, logs et publication par outbox."
topics: [rabbitmq, messaging, outbox, worker]
applies_to: [V1]
related_adrs: [ADR-0001]
---

# ARCH-02 --- RabbitMQ Architecture (Rustkins V1)

**Status:** Draft (Implementation Reference)

------------------------------------------------------------------------

# 1. Purpose

This document specifies how RabbitMQ is used inside Rustkins V1.

RabbitMQ is **not** the source of truth.

Responsibilities:

-   transport execution orders from the Scheduler to a given Worker
-   transport Worker events (job progress, completion, heartbeat) to
    the Scheduler
-   transport cancellation requests
-   transport log chunks
-   decouple API, Scheduler and Workers

PostgreSQL remains the authoritative state. Only the Scheduler (and the
API for user-facing data) writes it; Workers never access PostgreSQL
([ADR-0001](../../../../decisions/ADR-0001-worker-scheduler-communication.md)).

RabbitMQ publication is driven by a PostgreSQL transactional outbox.

The Scheduler writes durable OutboxMessages inside runtime transactions.

The Outbox Publisher publishes pending messages to RabbitMQ.

The Outbox Publisher is a Scheduler subcomponent.

------------------------------------------------------------------------

# 2. Architecture

``` mermaid
flowchart LR

API --> Scheduler
Scheduler --> PostgreSQL
PostgreSQL --> OutboxPublisher
OutboxPublisher --> RabbitMQ

RabbitMQ -->|job.assigned / cancel| Worker
Worker --> RustFS

Worker -->|events / log chunks| RabbitMQ
RabbitMQ -->|events| Scheduler
Scheduler --> PostgreSQL
RabbitMQ -->|log chunks| API
API --> Browser
```

------------------------------------------------------------------------

# 3. Exchanges

Four exchanges are defined.

  Exchange           Type     Purpose
  ------------------ -------- ----------------------------------
  rustkins.jobs      direct   Job execution orders per Worker
  rustkins.control   fanout   Runtime control
  rustkins.events    topic    Worker events to the Scheduler
  rustkins.logs      topic    Real-time logs

------------------------------------------------------------------------

# 4. Queues

  Queue                                Consumer     Description
  ------------------------------------ ------------ -----------------------------
  rustkins.jobs.worker.{worker_id}.q   One Worker   Jobs assigned to this Worker
  rustkins.jobs.retry.q                Scheduler    Delayed retry
  rustkins.jobs.dlq                    Operators    Dead Letter Queue
  rustkins.control.cancel.q            Workers      Cancellation broadcast
  rustkins.events.scheduler.q          Scheduler    Worker events
  rustkins.logs.sse.q                  API          Real-time log streaming

Each Worker declares its own job queue at startup. The Scheduler routes
a job only to the Worker on which it reserved resources.

------------------------------------------------------------------------

# 5. Routing Keys

## rustkins.jobs

``` text
worker.{worker_id}
job.retry
```

## rustkins.control

``` text
cancel.job
cancel.run
```

## rustkins.events

``` text
worker.registered
worker.heartbeat
job.started
step.finished
job.finished
```

## rustkins.logs

``` text
logs.{job_run_id}
```

------------------------------------------------------------------------

# 6. Job message (`job.assigned`)

``` json
{
  "message_id":"uuid",
  "type":"job.assigned",
  "worker_id":"uuid",
  "pipeline_run_id":"uuid",
  "job_run_id":"uuid",
  "pipeline_version_job_id":"uuid",
  "project_id":"uuid",
  "attempt":1,
  "idempotency_key":"run:job:attempt",
  "repository":{"url":"https://git.example.com/org/repo.git","commit_sha":"sha"},
  "job":{
    "name":"build",
    "image":"node:22",
    "optional":false,
    "timeout_seconds":3600,
    "resources":{"cpu_milli":1000,"memory_mb":1024},
    "env":{"NODE_ENV":"test"},
    "steps":[
      {"index":0,"name":"install","run":"npm ci","continue_on_error":false}
    ],
    "artifacts":{"paths":["dist/"]}
  },
  "restore_artifacts":[
    {"artifact_id":"uuid","object_key":"runs/.../artifacts/uuid.tar.gz","sha256":"..."}
  ],
  "created_at":"2026-01-01T12:00:00Z"
}
```

The message is a **self-contained execution order**: the Worker never
reads PostgreSQL. The Scheduler resolves everything, including the
upstream artifacts to restore, before publishing.

Secrets are out of scope for V1. When secrets are introduced, they must
not be stored in the outbox in clear text.

------------------------------------------------------------------------

# 7. Cancel message

``` json
{
  "type":"cancel_job",
  "pipeline_run_id":"uuid",
  "job_run_id":"uuid",
  "requested_by":"uuid"
}
```

Cancellation is broadcast to all workers.

Only the worker executing the job reacts. It confirms with a
`job.finished` event whose status is `cancelled`.

Cancel messages are also published through the transactional outbox.

------------------------------------------------------------------------

# 8. Log message

``` json
{
  "job_run_id":"uuid",
  "sequence":42,
  "stream":"stdout",
  "content":"Running tests...",
  "timestamp":"2026-01-01T12:00:00Z"
}
```

Maximum chunk size:

``` text
16 KB
```

------------------------------------------------------------------------

# 9. Worker events

Workers publish events on `rustkins.events`. The Scheduler consumes
them from `rustkins.events.scheduler.q`.

Example `job.finished`:

``` json
{
  "event_id":"uuid",
  "type":"job.finished",
  "worker_id":"uuid",
  "job_run_id":"uuid",
  "attempt":1,
  "status":"success",
  "exit_code":0,
  "started_at":"2026-01-01T12:00:00Z",
  "finished_at":"2026-01-01T12:03:10Z",
  "error":null,
  "log":{"object_key":"runs/.../logs.txt","size_bytes":48213},
  "artifacts":[
    {"name":"dist","object_key":"runs/.../artifacts/uuid.tar.gz","size_bytes":1048576,"sha256":"..."}
  ],
  "resource_usage":{"cpu_seconds":95.2,"memory_peak_mb":612}
}
```

Rules:

-   Workers publish with publisher confirms.
-   `job.finished` is kept in a local spool on the Worker until
    confirmed, and republished after a restart.
-   The Scheduler validates the sender, the attempt and the state
    transition, writes the state, then ACKs the event after commit.
-   Duplicate or stale events are ignored and acknowledged.

------------------------------------------------------------------------

# 10. Transactional outbox

RabbitMQ messages that affect execution state are never published
directly inside the scheduling transaction.

Instead, the Scheduler persists an OutboxMessage in PostgreSQL.

OutboxMessage fields:

``` text
exchange
routing_key
event_type
payload_json
status
attempts
next_attempt_at
last_error
created_at
published_at
```

Status values:

``` text
pending
publishing
published
failed
```

Publication loop:

1.  Load pending OutboxMessages.
2.  Publish the payload to RabbitMQ.
3.  Mark the OutboxMessage as `published`.
4.  If publication fails, increment attempts and schedule a retry.

RabbitMQ downtime never rolls back committed runtime state.

It only delays outbox publication.

If the Outbox Publisher crashes after publishing to RabbitMQ but before
marking the OutboxMessage as `published`, the message may be published
again.

This is acceptable because Workers keep a local registry of accepted
`job_run_id:attempt` pairs and ACK duplicate deliveries without
executing them twice. The Scheduler also rejects unexpected
`job.started` events (see §15).

------------------------------------------------------------------------

# 11. Message lifecycle

``` mermaid
sequenceDiagram
participant Scheduler
participant DB
participant Publisher as Outbox Publisher
participant MQ
participant Worker

Scheduler->>DB: Reserve resources
Scheduler->>DB: Insert OutboxMessage(job.assigned)
Publisher->>DB: Load pending OutboxMessage
Publisher->>MQ: Publish job.assigned (worker.{id})
Publisher->>DB: Mark OutboxMessage published
MQ->>Worker: Deliver message
Worker->>MQ: Publish job.started
MQ->>Scheduler: job.started
Scheduler->>DB: JobRun = running
Worker->>Worker: Execute container
Worker->>MQ: Publish job.finished
Worker->>MQ: ACK job.assigned
MQ->>Scheduler: job.finished
Scheduler->>DB: Final state, release resources, assign next jobs
Scheduler->>MQ: ACK event
```

------------------------------------------------------------------------

# 12. ACK / NACK policy

## ACK

The Worker ACKs `job.assigned` only after:

-   logs finalized
-   artifacts uploaded
-   `job.finished` confirmed by RabbitMQ

Resource release is performed by the Scheduler when it processes
`job.finished`.

## Business failure

Examples:

-   tests failed
-   exit code != 0

Action:

``` text
job.finished(status = failed)
ACK
```

## Infrastructure failure

Examples:

-   Docker unavailable
-   RustFS unavailable
-   Worker crash

Action:

``` text
job.finished(status = failed, infrastructure error)
ACK current message
Scheduler schedules retry
```

------------------------------------------------------------------------

# 13. Retry policy

Maximum attempts

``` text
3
```

Retry delays

``` text
30 seconds
2 minutes
5 minutes
```

Retryable failures

-   Docker daemon unavailable
-   RustFS unavailable
-   PostgreSQL temporary outage
-   RabbitMQ temporary outage
-   Network timeout
-   Worker crash

Non retryable

-   Build failed
-   Tests failed
-   YAML invalid
-   Exit code != 0

------------------------------------------------------------------------

# 14. Dead Letter Queue

After maximum retries:

``` text
JobRun.status = dead_lettered
```

PipelineRun becomes:

``` text
failed
```

Dead-lettered jobs require manual retry.

------------------------------------------------------------------------

# 15. Idempotency

RabbitMQ guarantees at-least-once delivery.

Workers must always:

1.  Check the local registry of accepted `job_run_id:attempt` pairs.
2.  ACK duplicate deliveries without execution.

The Scheduler must always:

1.  Validate the sender Worker, the attempt and the state transition
    of every event.
2.  Ignore and ACK duplicate or stale events.
3.  Publish `cancel.job` when a `job.started` targets a JobRun that is
    no longer `queued` for this attempt and this Worker.

Duplicate execution must never occur.

------------------------------------------------------------------------

# 16. Ordering

RabbitMQ ordering is never trusted.

Execution ordering is entirely controlled by:

-   DAG
-   Scheduler
-   Resource manager

Workers execute only received jobs.

------------------------------------------------------------------------

# 17. Failure scenarios

## Worker crashes

-   heartbeat lost
-   resources released by the Scheduler
-   retry if attempts remain
-   otherwise dead_lettered

## RabbitMQ restart

Outbox Publisher republishes `pending` or `publishing` messages using
OutboxMessage state.

Duplicate publication is safe thanks to the idempotency rules (§15).
Workers republish unconfirmed `job.finished` events from their local
spool.

## API unavailable

Workers continue executing.

Real-time logs are temporarily unavailable.

------------------------------------------------------------------------

# 18. ADR

## ADR-001

RabbitMQ is transport only.

Consequence:

Database remains the single source of truth.

------------------------------------------------------------------------

## ADR-002

Workers are stateless and never access PostgreSQL.

Consequence:

Execution orders are self-contained and Workers report through
`rustkins.events`. See [ADR-0001](../../../../decisions/ADR-0001-worker-scheduler-communication.md).

------------------------------------------------------------------------

## ADR-003

Transactional outbox is used for runtime messages.

Consequence:

RabbitMQ outages delay publication without corrupting scheduling state.

------------------------------------------------------------------------

## ADR-004

Cancellation uses broadcast.

Reason:

Simpler multi-worker implementation for V1.

------------------------------------------------------------------------

# 19. Future evolution

V2 candidates

-   Priority queues
-   One RabbitMQ account per Worker
-   Delayed exchanges
-   Multi-tenant isolation
-   Queue metrics
