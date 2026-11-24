---
id: DOC-0008
title: "Scheduler Architecture (Rustkins V1)"
type: architecture
status: approved
summary: "Responsabilités du scheduler V1 : DAG, ressources, outbox, dispatch des jobs, retries, annulations et pannes de workers."
topics: [scheduler, dag, outbox, retry, worker]
applies_to: [V1]
related_adrs: [ADR-0001]
---

# ARCH-11 --- Scheduler Architecture (Rustkins V1)

**Status:** Approved (Implementation Reference)

------------------------------------------------------------------------

# 1. Purpose

This document specifies the Scheduler architecture of Rustkins V1.

The Scheduler is the orchestration engine of Rustkins.

Responsibilities:

-   Build and evaluate execution DAGs
-   Detect runnable jobs
-   Allocate workers
-   Reserve CPU and memory
-   Release CPU and memory
-   Create durable outbox messages
-   Publish outbox messages to RabbitMQ
-   Manage retries
-   Handle cancellations
-   Consume Worker events and write runtime state
-   React to worker failures

The Scheduler never executes containers.

The Scheduler is the only writer of runtime execution state (JobRun,
StepRun, WorkerNode). Workers never access PostgreSQL
([ADR-0001](../../../../decisions/ADR-0001-worker-scheduler-communication.md)).

------------------------------------------------------------------------

# 2. High-Level Architecture

``` mermaid
flowchart LR

API --> Scheduler
Webhook --> Scheduler
Scheduler --> PostgreSQL
PostgreSQL --> OutboxPublisher
OutboxPublisher --> RabbitMQ
RabbitMQ -->|job.assigned / cancel| Worker
Worker -->|events| RabbitMQ
RabbitMQ -->|events| Scheduler
```

PostgreSQL is the source of truth.

RabbitMQ is only the transport layer.

OutboxPublisher is a Scheduler subcomponent.

------------------------------------------------------------------------

# 3. Responsibilities

The Scheduler MUST:

-   create execution DAGs
-   monitor PipelineRuns
-   evaluate dependencies
-   evaluate resource availability
-   reserve resources
-   release resources
-   create outbox messages for runnable jobs
-   run the outbox publisher loop
-   unlock dependent jobs
-   schedule retries
-   consume Worker events (`rustkins.events`) and persist the
    resulting states
-   register Workers and record their heartbeats
-   react to worker heartbeat loss

The Scheduler MUST NOT:

-   execute Docker containers
-   upload artifacts
-   stream logs

------------------------------------------------------------------------

# 4. Runtime Loop

``` mermaid
flowchart TD

Start --> FindRuns
FindRuns --> FindRunnableJobs
FindRunnableJobs --> Dependencies
Dependencies --> Resources
Resources --> SelectWorker
SelectWorker --> Reserve
Reserve --> Outbox
Outbox --> WaitEvents
WaitEvents --> FindRuns

Outbox --> Publish
Publish --> WaitEvents
```

The Scheduler continuously reacts to runtime events.

------------------------------------------------------------------------

# 5. DAG Evaluation

Each PipelineVersion contains an immutable DAG.

Scheduler evaluates JobRuns.

Job becomes runnable when:

-   all dependencies are completed
-   dependency status satisfies run_if
-   resources are available

For dependency evaluation:

-   `success` and `warning` satisfy `run_if = all_success`
-   any final dependency state satisfies `run_if = always`
-   only `failed` and `dead_lettered` satisfy `run_if = on_failure`

`warning` is non-blocking and does not count as failure for `on_failure`.

Otherwise

``` text
waiting_dependencies
```

or

``` text
waiting_resources
```

------------------------------------------------------------------------

# 6. Worker Selection

Worker eligibility

-   online
-   enough available CPU
-   enough available memory

V1 strategy

``` text
First compatible worker
```

Future versions may introduce priorities and affinity.

------------------------------------------------------------------------

# 7. Resource Reservation

Reservation sequence

``` mermaid
sequenceDiagram

participant Scheduler
participant PostgreSQL

Scheduler->>PostgreSQL: Lock Worker
Scheduler->>PostgreSQL: Validate capacity
Scheduler->>PostgreSQL: Reserve CPU/RAM
Scheduler->>PostgreSQL: JobRun = queued
Scheduler->>PostgreSQL: Insert OutboxMessage(job.assigned)
```

Reservation, JobRun update and OutboxMessage creation occur in one
PostgreSQL transaction.

------------------------------------------------------------------------

# 8. Job Dispatch

RabbitMQ dispatch is performed from the transactional outbox.

Outbox Publisher flow:

1.  Load pending OutboxMessages.
2.  Publish the message to RabbitMQ.
3.  Mark the OutboxMessage as `published`.
4.  If publication fails, increment attempts and schedule a retry.

The `job.assigned` message is routed with the key `worker.{worker_id}`
to the queue of the Worker on which resources were reserved.

It is a self-contained execution order: repository and SHA, image,
steps, limits, timeout, artifacts to produce and upstream artifacts to
restore. The Scheduler resolves all of it from PostgreSQL before
writing the OutboxMessage.

Advantages

-   Workers need no database access
-   the job reaches the Worker that holds the reservation
-   single source of truth, single writer

------------------------------------------------------------------------

# 9. Completion Handling

The Worker publishes `job.finished` on `rustkins.events`.

The Scheduler, in one transaction:

1.  validates the sender Worker, the attempt and the state transition;
2.  writes the final JobRun state, log and artifact metadata and
    measured resource usage;
3.  releases reserved resources;
4.  unlocks dependent jobs, selects their Workers, reserves resources
    and inserts their `job.assigned` OutboxMessages;
5.  completes the PipelineRun, schedules a retry or marks the JobRun
    `dead_lettered` when applicable.

The event is acknowledged after commit. Duplicate or stale result events
are ignored; start requests receive a correlated response instead.

`step.finished` updates StepRun state. `job.start.requested` follows the
authorization protocol below.

For `job.start.requested`, the Scheduler first verifies the RabbitMQ-validated
`user_id`, the assigned Worker and the attempt. In one transaction it
moves a `queued` attempt to `running`, stores its `start_request_id` and
inserts an OutboxMessage for `job.start.accepted`. A retransmission
with the same request ID on the still-current running attempt receives
another acceptance through the outbox, without authorizing execution
twice. A different or stale request receives `job.start.rejected` through
the outbox. Both responses copy
the request's `start_request_id` so the Worker can match the response
to its pending delivery. The Scheduler ACKs the request only after the
response is persisted.
The Worker starts Docker only after receiving acceptance. This durable
authorization replaces a local Worker deduplication registry; each
attempt can be authorized once. If the Worker disappears after
authorization without a confirmed final event, the Scheduler cannot
know whether external effects occurred. It marks the JobRun
`indeterminate` and does not automatically dispatch another attempt by
default.
A late valid `job.finished` from the original Worker and attempt may
resolve this state.

------------------------------------------------------------------------

# 10. Retry Management

Automatic retries apply by default only to failures before start
authorization. Once `job.start.accepted` is committed, a lost outcome
becomes `indeterminate` without retry. YAML v2 permits an explicit
`retry.worker_loss: unsafe` per job: on Worker loss, record the old
attempt as `indeterminate` and schedule a new attempt if the global
three-attempt limit permits. The JobRun becomes `retrying`; a late
result from the old attempt remains audit data and cannot overwrite
the current attempt. This option can repeat external effects. V0 and
YAML v1 use the safe default `never`.

Policy

``` text
Attempt 1 : 30 s
Attempt 2 : 2 min
Attempt 3 : 5 min
```

Maximum attempts

``` text
3
```

When pre-authorization retries are exhausted

``` text
JobRun = dead_lettered
PipelineRun = failed
```

If an authorized Worker is lost without a confirmed result and the
attempt limit is exhausted, the JobRun and PipelineRun are
`indeterminate`, including with `retry.worker_loss: unsafe`.

------------------------------------------------------------------------

# 11. Cancellation

Queued JobRun

``` text
cancelled
```

Running JobRun

1.  cancel_requested
2.  create cancel OutboxMessage routed to the assigned Worker's control
    queue; a run-wide cancellation targets each Worker with active jobs
3.  wait for the Worker `job.finished` event with status `cancelled`
4.  release resources
5.  mark JobRun cancelled

Timeout

``` text
indeterminate if the Worker may have executed code and no final result is confirmed
```

------------------------------------------------------------------------

# 12. Worker Failure

Heartbeat timeout

Scheduler

-   marks Worker offline
-   releases reservations
-   checks whether each assigned attempt was authorized to start

If start was never authorized and attempts remain

``` text
retrying
```

If start was never authorized and attempts are exhausted

``` text
dead_lettered
```

If start was authorized and no final event was confirmed:

``` text
indeterminate
```

The Scheduler does not dispatch another attempt or unlock dependent
jobs. A late event from the same Worker and attempt can still resolve
the outcome. Reconnecting Workers must report existing containers
before accepting new assignments.

------------------------------------------------------------------------

# 13. Pipeline Completion

PipelineRun reaches

``` text
success
warning
failed
cancelled
indeterminate
```

only after every JobRun reaches a final state.

------------------------------------------------------------------------

# 14. Transactions

Every scheduling decision requiring reservations must execute
atomically.

Transaction

1.  Lock worker row
2.  Validate capacity
3.  Reserve resources
4.  Update JobRun
5.  Insert OutboxMessage
6.  Commit

This prevents concurrent over-allocation.

RabbitMQ publication happens after commit through the Outbox Publisher.

------------------------------------------------------------------------

# 15. Runtime Events

Scheduler reacts to

-   PipelineRun created
-   `worker.registered`
-   `worker.heartbeat`
-   `job.start.requested`
-   `step.finished`
-   `job.finished`
-   Retry timeout
-   Cancel request
-   Worker offline (heartbeat timeout)

------------------------------------------------------------------------

# 16. Failure Scenarios

Database unavailable

No scheduling occurs.

RabbitMQ unavailable

OutboxMessages remain `pending`.

No reservation is rolled back because RabbitMQ is transport only.

Publication resumes when RabbitMQ is available.

Worker events are delayed. Live Workers retry unconfirmed events in
memory; confirmed events stay in RabbitMQ until the Scheduler commits
and ACKs them. Heartbeat timeouts must tolerate a short broker outage
before marking Workers offline.

Worker unavailable

Before authorization: retry or `dead_lettered`. After authorization:
`indeterminate` by default; retry only with explicit YAML v2
`retry.worker_loss: unsafe` and remaining attempts.

Oversized Job

Immediate failed.

------------------------------------------------------------------------

# 17. Invariants

-   Scheduler is the only orchestrator.
-   Scheduler is the only resource allocator and releaser.
-   Worker selection is deterministic.
-   One JobRun is queued only once.
-   Job dispatch is always persisted as an OutboxMessage before RabbitMQ publication.
-   Runtime control messages are also persisted as OutboxMessages before RabbitMQ publication.
-   Runtime state is persisted before messaging.
-   The Scheduler is the only writer of JobRun, StepRun and WorkerNode
    runtime state.
-   Every Worker event is validated before being persisted.

------------------------------------------------------------------------

# 18. ADR

## ADR-001

Decision

Centralized scheduling. Workers communicate only with the Scheduler,
through RabbitMQ, and never access PostgreSQL.

Consequence

Workers remain simple executors. See [ADR-0001](../../../../decisions/ADR-0001-worker-scheduler-communication.md).

------------------------------------------------------------------------

## ADR-002

Decision

Database is authoritative.

Consequence

RabbitMQ restart never loses runtime state.

------------------------------------------------------------------------

## ADR-003

Decision

Transactional outbox for RabbitMQ publication.

Consequence

RabbitMQ outages cannot leave committed runtime state without a durable
message to publish.

------------------------------------------------------------------------

## ADR-004

Decision

Scheduler evaluates immutable DAG.

Consequence

Historical consistency across retries.

------------------------------------------------------------------------

# 19. Future Evolution

Candidates

-   Priority scheduler
-   Fair scheduling
-   Worker labels
-   Affinity/anti-affinity
-   Multiple queues
-   Kubernetes backend
-   Pluggable scheduling strategies
