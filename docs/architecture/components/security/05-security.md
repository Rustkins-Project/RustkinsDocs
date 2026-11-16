---
id: DOC-0009
title: "Security (Rustkins V1)"
type: architecture
status: draft
summary: "Modèle de sécurité V1 : authentification JWT, refresh tokens, autorisations de projet, jetons API et signatures de webhooks."
topics: [security, authentication, authorization, jwt, webhooks]
applies_to: [V1]
related_adrs: [ADR-0001]
---

# ARCH-05 --- Security (Rustkins V1)

**Status:** Draft (Implementation Reference)

------------------------------------------------------------------------

# 1. Purpose

This document defines the security model of Rustkins V1.

It specifies:

-   Authentication
-   Authorization
-   JWT
-   Refresh Tokens
-   Project Roles
-   API Tokens
-   Webhook HMAC
-   Signed URLs
-   Password storage

Out of scope:

-   SSO
-   LDAP
-   OAuth login providers
-   Secret management

------------------------------------------------------------------------

# 2. Security Architecture

``` mermaid
flowchart LR

Browser --> API
API --> PostgreSQL

GitHub --> Webhook
Webhook --> API

API --> RustFS
API --> RabbitMQ
```

PostgreSQL is the authoritative source for identities and permissions.

Worker isolation

Workers execute arbitrary code from repositories. They therefore have
**no configured access to PostgreSQL**: no credentials and no direct network route
([ADR-0001](../../../../decisions/ADR-0001-worker-scheduler-communication.md)).

-   Workers receive self-contained execution orders from the Scheduler
    through RabbitMQ and report events back on `rustkins.events`.
-   The Scheduler validates every event (sender Worker, attempt, state
    transition) before writing it.
-   Each Worker has a distinct RabbitMQ account. Its permissions allow
    reading only its own job and control queues and publishing only to
    `rustkins.events` and `rustkins.logs`. Queue and binding creation
    belongs to the Scheduler. The Scheduler requires RabbitMQ's
    validated AMQP `user_id` on every Worker event and maps that account
    to the expected Worker; a payload `worker_id` alone is not proof of
    identity. Worker accounts have no `impersonator` tag. Topic
    permissions restrict each Worker's log routing keys to its own
    prefix; the API checks the sender against the assigned JobRun
    before streaming logs.
-   Worker RustFS credentials should be restricted to the `runs/`
    prefix.

The Docker socket grants broad control of its host. A separate Docker
network is insufficient when a Worker shares a host with PostgreSQL.
Production Workers run on dedicated hosts, separate from the API,
Scheduler, PostgreSQL and their Docker daemon. Single-host Compose is
for local development and does not provide this host-level isolation.

------------------------------------------------------------------------

# 3. Authentication

Authentication is JWT based.

Two tokens exist.

  Token           Lifetime
  --------------- ------------
  Access Token    30 minutes
  Refresh Token   7 days

Access Tokens authenticate API requests.

Refresh Tokens issue new Access Tokens.

------------------------------------------------------------------------

# 4. JWT

Contains at least:

``` text
sub
email
roles
exp
iat
iss
aud
```

JWTs are stateless.

Expiration is validated on every request.

------------------------------------------------------------------------

# 5. Refresh Tokens

Refresh Tokens are:

-   random
-   stored hashed
-   revocable
-   device specific

Database stores only:

``` text
token_hash
expires_at
revoked_at
user_agent
ip_address
```

Logout revokes the current Refresh Token.

------------------------------------------------------------------------

# 6. Passwords

Passwords are never stored.

Only password hashes are persisted.

Passwords are verified server-side.

------------------------------------------------------------------------

# 7. Project Roles

Roles

``` text
owner
maintainer
developer
viewer
```

Typical permissions

  Action                Owner   Maintainer   Developer   Viewer
  -------------------- ------- ------------ ----------- --------
  View project            ✓         ✓            ✓         ✓
  Trigger pipeline        ✓         ✓            ✓         ✗
  Cancel pipeline         ✓         ✓            ✓         ✗
  Manage members          ✓         ✓            ✗         ✗
  Configure webhooks      ✓         ✓            ✗         ✗
  Download artifacts      ✓         ✓            ✓         ✓
  View logs               ✓         ✓            ✓         ✓

------------------------------------------------------------------------

# 8. API Tokens

API Tokens allow automation.

Properties

-   project scoped
-   hashed
-   displayed once
-   revocable
-   optional expiration

Database stores

``` text
token_prefix
token_hash
scopes
expires_at
last_used_at
```

------------------------------------------------------------------------

# 9. API Token scopes

Examples

``` text
pipeline:read
pipeline:run
pipeline:cancel

artifact:read

logs:read

project:read

webhook:trigger
```

Each request validates required scope.

------------------------------------------------------------------------

# 10. Webhook Security

Every webhook uses HMAC verification.

Flow

``` mermaid
sequenceDiagram

GitHub->>API: Payload + Signature
API->>API: Load encrypted secret
API->>API: Compute HMAC
API->>API: Compare signatures
API-->>GitHub: 200 or 401
```

Missing signature

Result

``` text
401 Unauthorized
```

Invalid signature

Result

``` text
401 Unauthorized
```

------------------------------------------------------------------------

# 11. Secret Storage

Webhook secrets must remain readable.

Therefore

API Tokens

``` text
hashed
```

Refresh Tokens

``` text
hashed
```

Webhook Secret

``` text
encrypted
```

Reason

HMAC requires the original secret.

------------------------------------------------------------------------

# 12. Artifact Downloads

Artifacts are never publicly exposed.

Download flow

``` mermaid
sequenceDiagram

Browser->>API: Request download
API->>API: Check permissions
API->>RustFS: Generate signed URL
RustFS-->>Browser: Temporary download
```

Signed URLs expire automatically.

------------------------------------------------------------------------

# 13. Authorization

Every authenticated request verifies

-   identity
-   project membership
-   role
-   scope (API Tokens)

Authorization is evaluated server-side.

------------------------------------------------------------------------

# 14. Token Revocation

Refresh Token

-   logout
-   manual revocation
-   expiration

API Token

-   manual revocation
-   expiration

Access Token

Naturally expires after 30 minutes.

------------------------------------------------------------------------

# 15. Security Events

Typical events

-   login
-   logout
-   refresh
-   api_token_created
-   api_token_revoked
-   webhook_rejected
-   unauthorized_access
-   artifact_download

------------------------------------------------------------------------

# 16. Failure Scenarios

Expired JWT

``` text
401 Unauthorized
```

Expired Refresh Token

``` text
401 Unauthorized
```

Revoked API Token

``` text
403 Forbidden
```

Missing scope

``` text
403 Forbidden
```

Invalid HMAC

``` text
401 Unauthorized
```

------------------------------------------------------------------------

# 17. ADR

## ADR-001

Access Tokens remain short-lived.

Consequence

Reduced exposure if leaked.

------------------------------------------------------------------------

## ADR-002

Refresh Tokens are stored hashed.

Consequence

Database leak does not reveal valid tokens.

------------------------------------------------------------------------

## ADR-003

Webhook secrets are encrypted.

Consequence

API can recompute HMAC.

------------------------------------------------------------------------

## ADR-004

Artifacts use signed URLs.

Consequence

RustFS remains private.

------------------------------------------------------------------------

# 18. Future Evolution

Candidates

-   OAuth providers
-   MFA
-   Fine-grained permissions
-   Organization roles
-   Secret vault
-   Audit log
