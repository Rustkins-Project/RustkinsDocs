---
id: DOC-0011
title: "Worker Architecture (Rustkins V1)"
type: architecture
status: approved
summary: "Architecture et responsabilités du Worker V1 : récupération Git, exécution Docker, logs, artéfacts et états des jobs."
topics: [worker, docker, git, execution]
applies_to: [V1]
related_adrs: [ADR-0001]
---

# ARCH-09 --- Worker Architecture (Rustkins V1)

**Status:** Approved (Implementation Reference)

------------------------------------------------------------------------

# 1. Purpose

This document specifies the internal architecture and responsibilities
of a Rustkins Worker.

The Worker is responsible for executing JobRuns assigned by the
Scheduler.

It is **not** responsible for scheduling, dependency resolution or
resource allocation.

Out of scope:

-   Scheduler
-   Kubernetes
-   Auto-scaling
-   Multi-runtime execution

------------------------------------------------------------------------

# 2. Responsibilities

The Worker is responsible for:

-   Consuming JobRun execution orders from its own RabbitMQ queue
-   Detecting duplicate deliveries
-   Cloning the repository
-   Checking out the requested Git SHA
-   Preparing the execution environment
-   Restoring upstream artifacts
-   Executing the Docker container
-   Streaming logs
-   Uploading artifacts
-   Reporting job and step events to the Scheduler
-   Publishing its heartbeat

The Worker MUST NEVER:

-   Schedule jobs
-   Modify the execution DAG
-   Allocate resources
-   Release reserved resources
-   Create PipelineRuns
-   Access PostgreSQL (see [ADR-0001](../../../../decisions/ADR-0001-worker-scheduler-communication.md))

------------------------------------------------------------------------

# 3. High-Level Architecture

``` mermaid
flowchart LR

RabbitMQ -->|job.assigned / cancel| Worker
Worker -->|events / log chunks| RabbitMQ
Worker --> Git
Worker --> Docker
Docker --> Worker
Worker --> RustFS
```

The Worker has no access to PostgreSQL. It receives self-contained
execution orders from the Scheduler and reports back through
`rustkins.events`. The Scheduler is the only writer of runtime state.

------------------------------------------------------------------------

# 4. Execution Lifecycle

``` mermaid
stateDiagram-v2
[*] --> Idle
Idle --> JobReceived
JobReceived --> Preparing
Preparing --> Running
Running --> UploadingArtifacts
UploadingArtifacts --> Finalizing
Finalizing --> Idle
Running --> Failed
Failed --> Idle
```

------------------------------------------------------------------------

# 5. Job Processing Sequence

``` mermaid
sequenceDiagram

participant MQ as RabbitMQ
participant W as Worker
participant Git
participant Docker
participant RustFS

MQ->>W: job.assigned (self-contained order)
W->>W: Preflight Docker availability (no repository code)
W->>MQ: Publish job.start.requested
MQ->>W: job.start.accepted (after Scheduler commit)
W->>Git: Clone repository
W->>Git: Checkout commit SHA
W->>RustFS: Restore upstream artifacts
W->>Docker: Start container
Docker-->>W: stdout / stderr
W->>RustFS: Persist logs
W->>MQ: Publish step.finished (per step)
W->>RustFS: Upload artifacts
W->>MQ: Publish job.finished (confirmed)
W->>MQ: ACK job.assigned
```

The Scheduler consumes these events, writes the state into PostgreSQL
and sends the next jobs.

------------------------------------------------------------------------

# 6. Repository Preparation

Before execution the Worker:

1.  Clones the repository.
2.  Checks out the Git SHA given in the execution order.
3.  Loads the workspace.
4.  Restores the upstream artifacts listed in the execution order
    (RustFS keys and checksums resolved by the Scheduler).
5.  Starts the execution container.

The Worker must always execute the exact Git revision associated with
the PipelineVersion.

------------------------------------------------------------------------

# 7. Docker Execution

Each JobRun executes inside its own container.

The Worker applies:

-   CPU limits
-   Memory limits
-   Working directory
-   Environment variables
-   Mounted workspace

Container lifetime equals JobRun lifetime.

------------------------------------------------------------------------

# 8. Step Warning Handling

The Worker executes steps sequentially.

If a step exits with code `0`:

``` text
StepRun = success
```

Step definitions, including `continue_on_error`, and the optional flag
of the job are part of the execution order.

If a step exits with a non-zero code and
`PipelineVersionStep.continue_on_error = true`:

``` text
StepRun = warning
```

The Worker continues with the next step.

If no later blocking failure occurs, the JobRun finishes as `warning`.

If a step exits with a non-zero code and
`PipelineVersionStep.continue_on_error = false`:

``` text
StepRun = failed
```

The Worker stops the remaining steps.

If the parent PipelineVersionJob is optional, the JobRun finishes as
`warning`.

Otherwise, the JobRun finishes as `failed`.

------------------------------------------------------------------------

# 9. Log Management

Container output is continuously captured.

For each chunk:

1.  Append to RustFS.
2.  Publish to RabbitMQ.
3.  Preserve ordering using sequence numbers.

Persistent storage always occurs before live transport.

------------------------------------------------------------------------

# 10. Artifact Upload

When execution finishes:

1.  Discover configured artifact paths.
2.  Validate paths.
3.  Create tar.gz archive(s).
4.  Compute SHA-256 checksum.
5.  Upload to RustFS.
6.  Include Artifact metadata (name, RustFS key, size, checksum) in
    the `job.finished` event. The Scheduler persists it.

------------------------------------------------------------------------

# 11. Status Updates

The Worker never writes states. It publishes events on
`rustkins.events`; the Scheduler validates each transition and writes
it into PostgreSQL.

  Event             Resulting JobRun / StepRun state
  ----------------- ------------------------------------------------
  `job.start.requested`     JobRun `running`
  `step.finished`   StepRun `success`, `warning` or `failed`
  `job.finished`    JobRun `success`, `warning`, `failed` or `cancelled`

`job.finished` also carries exit code, timestamps, infrastructure error
details, log object key and size, artifact metadata and measured
resource usage.

Events are published as persistent messages with RabbitMQ publisher
confirms. A live Worker keeps an unconfirmed `job.finished` in memory
and retries publication. After confirmation, the durable Scheduler
queue retains it until the Scheduler commits and ACKs. If the Worker
dies before confirmation, the Scheduler checks whether start
authorization was committed. An unauthorized attempt can be
reassigned; an authorized attempt becomes `indeterminate` without
automatic retry by default. With YAML v2 `retry.worker_loss: unsafe`,
the Scheduler may create a new attempt after Worker loss. No local
spool survives a restart.

The Scheduler retries by default only failures known to precede start
authorization. An authorized attempt without a confirmed outcome
becomes `indeterminate`. An explicit YAML v2
`retry.worker_loss: unsafe` permits a new attempt after Worker loss;
the previous attempt remains in the audit history and may have
produced external effects.

------------------------------------------------------------------------

# 12. Cancellation

When a cancel request is received:

1.  Mark execution as cancelling.
2.  Stop the Docker container.
3.  Flush remaining logs.
4.  Upload completed artifacts (if applicable).
5.  Publish `job.finished` with status `cancelled`.
6.  Let the Scheduler persist the state and release reserved resources.

If the container cannot be stopped within the timeout, the JobRun
transitions to `failed`.

------------------------------------------------------------------------

# 13. Idempotency

RabbitMQ guarantees at-least-once delivery.

The Worker publishes `job.start.requested` with a fresh `start_request_id` per
delivery and reuses that ID when retransmitting the same request. It
waits for a `job.start.accepted` control message with that same ID,
Worker, JobRun and attempt before launching Docker. The
Scheduler atomically moves the assigned attempt from `queued` to
`running`, stores the request ID and puts the acceptance in its outbox.
A retransmission with the same ID receives the same acceptance without
another authorization. A different or stale request receives
`job.start.rejected` and is ACKed without execution.
The Worker ignores repeated acceptances for an already active delivery
and retains only the in-memory state of its active jobs.

An attempt is authorized at most once. By default, the Scheduler does
not create another attempt when an authorized outcome is unknown. A
late `job.finished` from the same attempt can resolve `indeterminate`.
YAML v2 `retry.worker_loss: unsafe` is the explicit exception.

------------------------------------------------------------------------

# 14. Heartbeat

At startup the Worker publishes `worker.registered` (worker id, CPU
and memory capacity, version).

Then it periodically publishes `worker.heartbeat` (worker id, running
jobs) on `rustkins.events`.

The Scheduler updates `last_heartbeat_at` and `status`, and uses this
information to detect offline Workers.

------------------------------------------------------------------------

# 15. Failure Handling

Typical infrastructure failures:

-   Docker unavailable
-   Git clone failure
-   RustFS unavailable
-   Network timeout

Only failures known to precede start authorization follow the default
automatic retry policy. After authorization, a lost result cannot be
assumed safe to replay. YAML v2 `retry.worker_loss: unsafe` explicitly
opts into that risk for Worker loss.

Business failures (tests, compilation, commands) do not trigger retries.

------------------------------------------------------------------------

# 16. Runtime Invariants

-   One Worker executes one JobRun at a time per reserved slot.
-   Each attempt is assigned to one Worker. Heartbeat loss after start
    authorization creates no new attempt by default; YAML v2
    `retry.worker_loss: unsafe` explicitly allows one. An isolated
    Worker may still be executing the original attempt.
-   Each attempt owns at most one Docker job container.
-   Workers never modify scheduling decisions.
-   Workers never reserve or release worker capacity.
-   Workers never access PostgreSQL.
-   PostgreSQL remains the source of truth, written by the Scheduler.

------------------------------------------------------------------------

# 17. ADR

## ADR-001

Decision

Workers keep no durable execution registry or event spool. They
communicate only with the Scheduler, through RabbitMQ.

Consequence

All execution state is stored externally, by the Scheduler. See
[ADR-0001](../../../../decisions/ADR-0001-worker-scheduler-communication.md).

------------------------------------------------------------------------

## ADR-002

Decision

Repository is checked out at the exact Git SHA.

Consequence

Execution remains reproducible.

------------------------------------------------------------------------

## ADR-003

Decision

Logs are persisted before live streaming.

Consequence

History survives API failures.

------------------------------------------------------------------------

## ADR-004

Decision

Artifact upload is performed by the Worker.

Consequence

Execution output remains local until completion.

------------------------------------------------------------------------

# 18. Future Evolution

Candidates

-   Workspace cache
-   Parallel Git clone optimization
-   Container reuse
-   Sandboxed execution
-   Multiple execution backends
-   Remote execution
-   Per-job resource usage collection (CPU time, peak memory, image
    pull time, OOM kills), see the
    [eco-design approach](../../../cross-cutting/eco-design/eco-design-approach.md)
