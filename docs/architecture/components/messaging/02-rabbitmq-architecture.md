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

Scheduler orders and control messages are published through a
PostgreSQL transactional outbox. Worker events and log chunks are
published directly with publisher confirms; durable event queues and
Scheduler ACK-after-commit provide their delivery guarantee.

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
  rustkins.control   direct   Runtime control per Worker
  rustkins.events    topic    Worker events to the Scheduler
  rustkins.logs      topic    Real-time logs

------------------------------------------------------------------------

# 4. Queues

  Queue                                Consumer     Description
  ------------------------------------ ------------ -----------------------------
  rustkins.jobs.worker.{worker_id}.q   One Worker   Jobs assigned to this Worker
  rustkins.jobs.retry.q                Scheduler    Delayed retry
  rustkins.jobs.dlq                    Operators    Dead Letter Queue
  rustkins.control.worker.{worker_id}.q One Worker   Controls for this Worker
  rustkins.events.scheduler.q          Scheduler    Worker events
  rustkins.logs.sse.q                  API          Real-time log streaming

The Scheduler provisions one durable job queue and one durable control
queue per registered Worker. Each control queue is bound to the direct
exchange with `worker.{worker_id}`; one shared queue would deliver each
cancellation to only one consumer. The Scheduler routes a job only to
the Worker on which it reserved resources.

------------------------------------------------------------------------

# 5. Routing Keys

## rustkins.jobs

``` text
worker.{worker_id}
job.retry
```

## rustkins.control

``` text
worker.{worker_id}
```

The message type distinguishes `cancel.job`, `cancel.run`,
`job.start.accepted` and `job.start.rejected`. The Scheduler publishes
each control message with the routing key of its target Worker. For a
run spanning multiple Workers, it sends one `cancel.run` message to
each Worker executing a job in that run.

## rustkins.events

``` text
worker.registered
worker.heartbeat
job.start.requested
step.finished
job.finished
```

`job.start.accepted` and `job.start.rejected` are control messages on
`rustkins.control`; each carries `job_run_id`, `attempt`, `worker_id`
and the `start_request_id` from the corresponding `job.start.requested`. The
target Worker acts only when all four fields match its pending start
request. The Worker must receive
`job.start.accepted` before starting Docker.

## rustkins.logs

``` text
logs.{worker_id}.{job_run_id}
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
  "worker_id":"uuid",
  "attempt":1,
  "requested_by":"uuid"
}
```

The Scheduler publishes this control to `worker.{worker_id}` on
`rustkins.control`, using the assigned Worker and attempt from its
durable state. The Worker checks those fields before acting. It
confirms with a `job.finished` event whose status is `cancelled`.

Cancel messages are also published through the transactional outbox.

------------------------------------------------------------------------

# 8. Log message

``` json
{
  "worker_id":"uuid",
  "job_run_id":"uuid",
  "sequence":42,
  "stream":"stdout",
  "content":"Running tests...",
  "timestamp":"2026-01-01T12:00:00Z"
}
```

The Worker publishes on `logs.{worker_id}.{job_run_id}` with its
RabbitMQ-validated AMQP `user_id`. Per-Worker topic permissions prevent
publishing under another Worker's routing-key prefix. The API also
checks that the account and `worker_id` match the assigned JobRun before
forwarding a chunk to SSE.

Maximum chunk size:

``` text
16 KB
```

------------------------------------------------------------------------

# 9. Worker events

Workers publish persistent events on `rustkins.events`. The Scheduler
consumes them from the durable `rustkins.events.scheduler.q`. The broker
validates the AMQP `user_id` property against the publishing account.
The Scheduler rejects an event without `user_id` or when the account
does not match the registered `worker_id` and the assigned Worker.
Worker accounts must not have RabbitMQ's `impersonator` tag.

Provision each Worker identity before starting it. The `worker_id` is
stable across restarts and maps to the RabbitMQ user `worker-{worker_id}`.
For example, with an administrator shell on the broker (`WORKER_ID` and
`WORKER_PASSWORD` are supplied securely by the administrator):

``` sh
rabbitmqctl add_user "worker-${WORKER_ID}" "${WORKER_PASSWORD}"
rabbitmqctl set_permissions -p / "worker-${WORKER_ID}" '^$' \
  '^(rustkins\.events|rustkins\.logs)$' \
  "^(rustkins\.jobs\.worker\.${WORKER_ID}\.q|rustkins\.control\.worker\.${WORKER_ID}\.q)$"
rabbitmqctl set_topic_permissions -p / "worker-${WORKER_ID}" rustkins.logs \
  "^logs\.${WORKER_ID}\.[^.]+$" '^$'
```

The Scheduler uses an account with permission to provision queues and
publish orders. The API uses its own account. The Worker connection
sets AMQP `user_id` to its account name on every event. Queue and
exchange names are provisioned by the Scheduler, not by Workers.

Each Worker account can read only `rustkins.jobs.worker.{worker_id}.q` and
`rustkins.control.worker.{worker_id}.q`, and publish only to
`rustkins.events` and `rustkins.logs`. The Scheduler alone configures
queues and bindings. No Worker uses the Scheduler or API account.
See the [RabbitMQ access-control documentation](https://www.rabbitmq.com/docs/access-control)
and [validated user ID](https://www.rabbitmq.com/docs/validated-user-id).

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

`resource_usage` contains the V1 measurements when available. The
Scheduler stores them on `JOB_RUN_ATTEMPT`; absent readings remain
`null`. Wall-clock duration comes from timestamps. This payload does
not yet specify image download metrics or Worker-wide utilization.

Rules:

-   `job.start.requested` carries a fresh `start_request_id` for each
    `job.assigned` delivery; retransmission of that request reuses the
    same ID. The Scheduler stores the accepted ID on the attempt and
    copies the requested ID into `job.start.accepted` or
    `job.start.rejected`. A same-ID request on the current running attempt
    replays acceptance; a different or stale request is rejected.
-   Workers publish with publisher confirms.
-   A live Worker retains an unconfirmed `job.finished` in memory and
    retries publication. Once confirmed, RabbitMQ holds the persistent
    event until the Scheduler ACKs it after commit.
-   If a Worker disappears before broker confirmation, the Scheduler
    checks whether start authorization was committed. Before
    authorization, the job can be reassigned. After authorization, its
    outcome becomes `indeterminate` and it is not automatically retried
    by default. YAML v2 `retry.worker_loss: unsafe` allows a new attempt
    within the global limit.
-   The Scheduler validates the sender, the attempt and the state
    transition, writes the state, then ACKs the event after commit.
-   Duplicate or stale result events are ignored and acknowledged.
    Start requests receive `job.start.accepted` or `job.start.rejected`
    according to the attempt state and request ID, then are acknowledged
    after the response is persisted.

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

This is acceptable because a Worker requests start authorization for
each delivery. The Scheduler grants it only once for the assigned
`job_run_id:attempt`. Retransmitting the same `start_request_id` replays
the response; a different or stale request is rejected (§15).

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
Worker->>Worker: Preflight Docker availability (no repository code)
Worker->>MQ: Publish job.start.requested
MQ->>Scheduler: job.start.requested
Scheduler->>DB: JobRun = running
Scheduler->>MQ: job.start.accepted (outbox)
MQ->>Worker: job.start.accepted
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

The Worker never ACKs a delivery while waiting for start authorization.
On `job.start.rejected` it ACKs without executing. If it crashes after
publication but before ACK, the event remains in RabbitMQ for the
Scheduler; a redelivered execution order cannot receive a second
authorization for the same attempt.

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

Before start authorization, a known infrastructure failure or lost
Worker can be retried. After authorization, even a confirmed
infrastructure failure is not automatically retried in V1: the job
code may already have produced external effects.

Example after authorization:

``` text
job.finished(status = failed, infrastructure error)
ACK current message
Scheduler records failed without automatic retry
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

Automatically retryable failures by default, only before start authorization

-   Docker daemon unavailable during preflight
-   PostgreSQL or RabbitMQ temporary outage before authorization
-   Network timeout before authorization
-   Worker loss before start authorization

Non retryable

-   Build failed
-   Tests failed
-   YAML invalid
-   Exit code != 0
-   Worker loss after start authorization with no confirmed result:
    `indeterminate` by default, even if attempts remain
-   Known failure reported after authorization: `failed`, without an
    automatic worker-loss retry

YAML v2 jobs may explicitly set `retry.worker_loss: unsafe`. After an
authorized Worker is lost, the Scheduler then records the old attempt as
`indeterminate` and schedules another within the three-attempt limit.
Late events for the old attempt are retained for audit and cannot change
the current attempt. External effects may be repeated. The default is
`retry.worker_loss: never`; V0 and YAML v1 always use that default.

------------------------------------------------------------------------

# 14. Dead Letter Queue

After maximum pre-authorization retries:

``` text
JobRun.status = dead_lettered
```

PipelineRun becomes:

``` text
failed
```

Dead-lettered jobs require manual retry.
An authorized Worker loss with no confirmed result remains
`indeterminate` when the attempt limit is exhausted, even with
`retry.worker_loss: unsafe`.

------------------------------------------------------------------------

# 15. Idempotency

RabbitMQ guarantees at-least-once delivery.

Workers must always:

1.  Publish `job.start.requested` and wait for `job.start.accepted` before
    launching the container.
2.  ACK a rejected duplicate delivery without execution.

The Scheduler must always:

1.  Validate the sender Worker, the attempt and the state transition
    of every event.
2.  Ignore and ACK duplicate or stale result events.
3.  Atomically move an assigned `queued` attempt to `running`, persist
    its `start_request_id` and put `job.start.accepted` in the outbox.
    For the same request ID on the still-current running attempt,
    replay acceptance without a second authorization. Reject a
    different or stale request.

The same attempt must never be authorized twice. By default, automatic
retries are limited to cases where no start authorization was committed.
Once a start was authorized, a lost outcome becomes `indeterminate` and
no new attempt is dispatched. The Scheduler can accept a late
`job.finished` from that original Worker and attempt to resolve the
state. Dependent jobs do not run while the outcome remains unknown.
With YAML v2 `retry.worker_loss: unsafe`, the old attempt stays in the
audit history while a new attempt may be dispatched.

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
-   if start was never authorized: retry if attempts remain, otherwise
    `dead_lettered`
-   if start was authorized and no result was confirmed: `indeterminate`
    with no automatic retry by default; a late result may resolve it
-   with YAML v2 `retry.worker_loss: unsafe`: record the old attempt as
    `indeterminate` and retry if attempts remain; ignore its late result
    for the current attempt

## RabbitMQ restart

Outbox Publisher republishes `pending` or `publishing` messages using
OutboxMessage state.

Duplicate publication is safe thanks to the idempotency rules (§15).
Live Workers retry unconfirmed events held in memory. On Worker loss
before broker confirmation, the Scheduler applies the start-authorization
boundary above; it never assumes the job had no external effects.

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

Workers retain only in-memory state while executing; durable execution
state is held by PostgreSQL and RabbitMQ. Workers never access PostgreSQL.

Consequence:

Execution orders are self-contained and Workers report through
`rustkins.events`. See [ADR-0001](../../../../decisions/ADR-0001-worker-scheduler-communication.md).

------------------------------------------------------------------------

## ADR-003

Transactional outbox is used for Scheduler orders and control messages.

Consequence:

RabbitMQ outages delay publication without corrupting scheduling state.

------------------------------------------------------------------------

## ADR-004

Cancellation uses targeted controls on each Worker's own queue.

Reason:

The Scheduler knows the assigned Worker. Direct routing avoids sending
job-specific controls to unrelated Workers. A run-wide cancellation
is sent separately to every Worker executing a job in that run.

------------------------------------------------------------------------

# 19. Future evolution

V2 candidates

-   Priority queues
-   Delayed exchanges
-   Multi-tenant isolation
-   Queue metrics
