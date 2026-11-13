---
id: DOC-0008
title: "Scheduler Architecture (Rustkins V1)"
type: architecture
status: draft
summary: "Responsabilités du scheduler V1 : DAG, ressources, outbox, dispatch des jobs, retries, annulations et pannes de workers."
topics: [scheduler, dag, outbox, retry, worker]
applies_to: [V1]
related_adrs: [ADR-0001]
---

# ARCH-11 --- Scheduler Architecture (Rustkins V1)

**Status:** Draft (Implementation Reference)

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

The event is acknowledged after commit. Duplicate or stale events are
ignored.

`job.started` and `step.finished` events are handled the same way and
update JobRun `running` and StepRun states.

------------------------------------------------------------------------

# 10. Retry Management

Infrastructure failures only.

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

When exhausted

``` text
JobRun = dead_lettered
PipelineRun = failed
```

------------------------------------------------------------------------

# 11. Cancellation

Queued JobRun

``` text
cancelled
```

Running JobRun

1.  cancel_requested
2.  create cancel OutboxMessage
3.  wait for the Worker `job.finished` event with status `cancelled`
4.  release resources
5.  mark JobRun cancelled

Timeout

``` text
failed
```

------------------------------------------------------------------------

# 12. Worker Failure

Heartbeat timeout

Scheduler

-   marks Worker offline
-   releases reservations
-   evaluates running JobRuns

If attempts remain

``` text
retrying
```

Otherwise

``` text
dead_lettered
```

------------------------------------------------------------------------

# 13. Pipeline Completion

PipelineRun reaches

``` text
success
warning
failed
cancelled
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
-   `job.started`
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

Worker events are delayed. Workers keep `job.finished` in a local
spool and republish it. Heartbeat timeouts must tolerate a short
broker outage before marking Workers offline.

Worker unavailable

Retry or dead_lettered.

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
