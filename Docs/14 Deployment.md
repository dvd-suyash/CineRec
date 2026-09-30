# 14 — Deployment

**Project:** CineRec
**Document:** Deployment
**Status:** Normative
**Version:** 1.0
**Primary objective:** Reliable, reproducible, low-cost deployment with a clean scalability path

---

# 1. Purpose

This document defines how CineRec moves from:

```text id="4a2b8e"
source code
```

to:

```text id="j23x8f"
running product
```

while preserving:

```text id="yy1v4p"
security
reproducibility
observability
availability
data integrity
scalability
cost control
```

The deployment architecture must support the project's central constraint:

> **Spend infrastructure complexity only where the product has demonstrated a need for it.**

The first deployment should therefore be simple enough for one developer to operate while preserving boundaries that allow the system to scale later.

---

# 2. Deployment Philosophy

CineRec follows these deployment principles:

```text id="x9z8hs"
1. Build once, run the same artifact everywhere.
2. Keep application services stateless.
3. Keep PostgreSQL as durable source of truth.
4. Keep Redis ephemeral.
5. Keep workers separate from HTTP request handling.
6. Keep secrets outside source code and images.
7. Automate deployment through CI/CD.
8. Test migrations before production.
9. Make rollback explicit.
10. Do not introduce Kubernetes prematurely.
```

Docker's production guidance explicitly describes running Compose applications on a single server as a practical deployment model and supports separate production Compose overrides for production-specific configuration.

---

# 3. Deployment Targets

CineRec has four deployment environments:

```text id="e1w7v4"
development
test / CI
staging
production
```

Each environment must be isolated.

---

# 4. Environment Definitions

## Development

Purpose:

```text id="x6rj3c"
local feature development
```

Characteristics:

```text id="jv8g0e"
Docker Compose
local PostgreSQL
local Redis
local Celery
mock/sandbox providers where practical
debug logging
```

---

## Test / CI

Purpose:

```text id="2cl4qv"
automated testing
```

Characteristics:

```text id="1o5j1v"
ephemeral database
ephemeral Redis
fake/mock Gemini
fake/mock TMDB
automated migrations
automated tests
```

---

## Staging

Purpose:

```text id="08c8qh"
production-like validation
```

Characteristics:

```text id="gqlz17"
production build artifacts
production-like configuration
separate data
real provider integration where useful
security testing
E2E testing
migration verification
```

---

## Production

Purpose:

```text id="5q7s6j"
real users
```

Characteristics:

```text id="2mw0d6"
HTTPS
managed secrets
managed or hardened PostgreSQL
Redis
API
worker
monitoring
backups
automated deployment
```

---

# 5. Recommended Initial Production Topology

The recommended initial architecture is:

```text id="x4lkq7"
                     Internet
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
        Next.js Web              FastAPI API
        deployment               deployment
             │                       │
             │               ┌───────┼────────┐
             │               │       │        │
             │               ▼       ▼        ▼
             │          PostgreSQL  Redis    Celery
             │               │                │
             │               │                ▼
             │               │             Workers
             │               │                │
             │               └───────┬────────┘
             │                       │
             │               ┌───────┴────────┐
             │               ▼                ▼
             │            Gemini             TMDB
             │
             └───────────────►
```

Recommended initial managed-service split:

```text id="9ayz0n"
Frontend
→ Vercel or equivalent Next.js hosting

API
→ Dockerized FastAPI service

Worker
→ Dockerized Celery service

PostgreSQL
→ Supabase or equivalent managed PostgreSQL

Redis
→ managed Redis or private Redis deployment
```

Next.js officially supports both Node.js-server and Docker deployments, while Vercel provides zero-configuration deployment for Next.js.

Render currently documents Docker-based deployments and FastAPI deployment directly, making it a valid initial host for both the API and worker containers.

---

# 6. Why This Split

The system is deliberately divided by workload.

```text id="x6yy6t"
Next.js
→ user-facing web traffic

FastAPI
→ synchronous API traffic

Celery worker
→ asynchronous jobs

PostgreSQL
→ durable state

Redis
→ caching + queue/coordination
```

This prevents:

```text id="b6ad6i"
LLM jobs
TMDB imports
embedding generation
```

from competing directly with user-facing HTTP traffic.

---

# 7. Alternative Single-Server Deployment

For the absolute lowest operational complexity/cost:

```text id="qj5gh7"
One VM
│
├── reverse proxy
├── Next.js
├── FastAPI
├── Celery worker
├── PostgreSQL
└── Redis
```

can be used.

Docker explicitly documents single-server Compose deployment as a production option.

However, this creates a larger blast radius:

```text id="u6dlq9"
VM failure
→ web
→ API
→ worker
→ database
→ Redis
```

all become unavailable simultaneously.

Therefore managed database infrastructure is preferred once the product matters beyond a demo.

---

# 8. Deployment Strategy Decision

Default:

```text id="h7xvku"
managed services + containerized application
```

Not:

```text id="3b5x4y"
Kubernetes
```

Not:

```text id="9yo61o"
microservices
```

Not:

```text id="0ukm7c"
full self-hosting of every dependency
```

---

# 9. Frontend Deployment

The Next.js application:

```text id="se7tn5"
apps/web
```

should be deployed independently from the FastAPI application.

Next.js currently supports:

```text id="j2a3hs"
Node.js server
Docker
static export
```

with different feature support. CineRec should use a full Node.js/Docker-compatible deployment rather than static export because the product may require server-side functionality, streaming, authenticated behavior, and future Next.js server features.

---

# 10. Recommended Frontend Platform

Initial preference:

```text id="z5f47n"
Vercel
```

because Next.js is directly supported and deployment is intentionally optimized for the framework.

Alternative:

```text id="v4cc7n"
Dockerized Next.js
→ Render / VM / equivalent
```

The application code must not depend on Vercel-specific APIs unless explicitly required.

---

# 11. Frontend Build

Production build:

```bash id="3xwd1l"
npm ci
npm run build
npm run start
```

or the equivalent package-manager workflow.

The exact package manager must be fixed in the repository.

---

# 12. Frontend Production Requirements

Production frontend must have:

```text id="r1l4v5"
production environment variables
HTTPS
secure authentication flow
API URL configured
error monitoring
source control revision
```

---

# 13. Frontend Environment Variables

Only public configuration belongs in frontend-exposed variables.

Example:

```env id="k0b7hm"
NEXT_PUBLIC_API_BASE_URL=https://api.cinerec.example.com
NEXT_PUBLIC_APP_URL=https://cinerec.example.com
```

Never put:

```text id="n4c6j6"
GEMINI_API_KEY
TMDB_ACCESS_TOKEN
DATABASE_URL
REDIS_URL
```

into the frontend environment.

---

# 14. Backend Deployment

The FastAPI backend:

```text id="p8h5ev"
apps/api
```

should be packaged as a production Docker image.

Recommended runtime:

```text id="m0n8ns"
Uvicorn
```

behind the hosting provider's HTTP/reverse-proxy layer.

Render's current FastAPI deployment documentation uses Uvicorn bound to `0.0.0.0` and the provider-provided `PORT`.

---

# 15. API Container

Conceptual startup:

```bash id="9t0j0e"
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The application must not hardcode:

```text id="61c7c9"
port 8000
```

for production hosting.

Use:

```text id="i0us1v"
PORT
```

or deployment-specific configuration.

---

# 16. API Container Responsibilities

The API container handles:

```text id="6ajpn8"
authentication context
API requests
conversation orchestration
recommendation requests
movie catalog access
user state
read/write business logic
```

It must not handle:

```text id="l7q8ut"
long-running training
large-scale catalog imports
heavy embedding batches
long asynchronous maintenance jobs
```

---

# 17. Worker Deployment

Celery workers run separately from the API.

Conceptually:

```text id="h6qg8n"
celery -A app.worker worker
```

The exact command depends on project structure.

---

# 18. Worker Responsibilities

Workers handle:

```text id="v4d3hu"
TMDB enrichment
model preprocessing
embedding generation
recommendation precomputation
background memory processing
evaluation jobs
scheduled refreshes
maintenance
```

---

# 19. Worker Scaling

Initially:

```text id="hl9jnu"
1 worker process/container
```

Later:

```text id="g6yvrv"
N worker replicas
```

when queue backlog or throughput requires it.

---

# 20. API vs Worker Scaling

These should scale independently.

Example:

```text id="4xq8d2"
API:
5 replicas

Worker:
2 replicas
```

because they solve different bottlenecks.

---

# 21. PostgreSQL Deployment

PostgreSQL is the durable source of truth.

Preferred:

```text id="p8rcbp"
managed PostgreSQL
```

initially.

Supabase currently provides managed PostgreSQL with multiple connection methods. Its documentation recommends direct connections for persistent backends such as long-running containers/VMs and pooled connections for serverless/edge workloads.

---

# 22. Database Connection Strategy

For a persistent FastAPI container:

```text id="hkmj3k"
SQLAlchemy
→ connection pool
→ PostgreSQL
```

is the default.

For horizontally scaled/serverless environments, a managed pooler may become useful.

Supabase documents that application-side pools work well for persistent backends and server-side poolers help when many short-lived connections are created by horizontally/serverlessly scaled workloads.

---

# 23. Database Connection Limits

Database connection limits must be explicitly planned.

The rough relationship is:

```text id="wyo3as"
total_connections
≈
API_replicas × API_pool_size
+
worker_replicas × worker_pool_size
+
other clients
```

Do not set:

```text id="80mx2l"
pool_size = 100
```

for every container by default.

---

# 24. Connection Pool Sizing

Start conservatively.

Example:

```text id="1dco5p"
API pool:
5–10 connections/process

Worker:
small bounded pool
```

Actual values should be established from:

```text id="j1k8nz"
database capacity
query latency
replica count
concurrency
```

---

# 25. Database SSL

Production database connections should use TLS/SSL where supported and appropriate.

Never disable certificate verification casually.

---

# 26. Database Backups

Production PostgreSQL requires:

```text id="h6h7t8"
automatic backups
point-in-time recovery where available
restore testing
access controls
```

---

# 27. Restore Testing

A backup is not considered valid until restoration has been tested.

Process:

```text id="zv8g23"
backup
 ↓
restore to isolated environment
 ↓
run migrations if needed
 ↓
run smoke tests
```

---

# 28. Migration Strategy

All schema changes use:

```text id="65p3a2"
Alembic
```

No manual production SQL changes should become part of ordinary deployment.

---

# 29. Migration Pipeline

```text id="34e8ff"
Developer
 ↓
create migration
 ↓
unit/integration tests
 ↓
CI migration test
 ↓
staging migration
 ↓
staging smoke tests
 ↓
production migration
```

---

# 30. Migration Safety

Before applying a migration:

```text id="vi4g8o"
check production compatibility
estimate execution time
check locking behavior
check index creation impact
check data-volume implications
```

---

# 31. Backward-Compatible Migrations

Prefer expand/contract migrations.

Example:

```text id="z3b8r1"
Phase 1:
add new nullable column

Phase 2:
deploy code using both

Phase 3:
backfill

Phase 4:
switch reads

Phase 5:
enforce constraint

Phase 6:
remove old column
```

Avoid changes that require an old and new application version to disagree about the schema.

---

# 32. Zero-Downtime Schema Changes

For common production changes:

```text id="p2o03j"
add columns
add indexes carefully
backfill asynchronously
switch application
remove old fields later
```

---

# 33. Large Index Creation

For very large tables, index-building strategy must account for production locking and workload.

Use PostgreSQL's appropriate online/concurrent mechanisms where supported and validated.

---

# 34. Database Seed Policy

Production does not run:

```text id="2nq4lx"
development seed data
```

automatically.

Production data is managed through:

```text id="ux5jx4"
migrations
controlled ingestion
background jobs
admin operations
```

---

# 35. Redis Deployment

Redis is:

```text id="2jz1i4"
cache
rate limiter
distributed lock
Celery broker
ephemeral coordination
```

It is not durable application truth.

---

# 36. Redis Persistence

Do not depend on Redis persistence for critical application data.

If Redis disappears:

```text id="5yp3x4"
PostgreSQL
```

must remain the source of truth.

---

# 37. Redis Scaling

Initial:

```text id="x9wq8g"
one managed/private Redis instance
```

Later:

```text id="r5n8y6"
larger instance
replication
high availability
```

only when necessary.

---

# 38. Redis Namespaces

Use explicit prefixes:

```text id="m0n55a"
cache:
lock:
rate:
celery:
session:
```

Example:

```text id="n0u9w3"
cache:movie:tmdb:27205:en-US
rate:user:<id>
lock:tmdb:movie:27205
```

---

# 39. Worker Queue

Use Redis initially as the Celery broker.

The architecture must keep the queue abstraction isolated so the broker can later be replaced if workload justifies it.

---

# 40. Celery Result Backend

CineRec should not persist large job results in Redis by default.

Prefer:

```text id="j8g2h0"
database
object storage
explicit application state
```

for durable results.

Redis remains ephemeral.

---

# 41. Containerization

Every deployable application component should have a Dockerfile:

```text id="v7a6om"
apps/web/Dockerfile
apps/api/Dockerfile
```

The worker can reuse:

```text id="fpl1eo"
API Docker image
```

with a different command.

---

# 42. Multi-Stage Docker Builds

Use multi-stage builds where appropriate:

```text id="7p95ae"
build stage
→ production runtime stage
```

to reduce image size.

---

# 43. Backend Image

Production image should contain:

```text id="crn6j6"
Python runtime
application dependencies
application code
```

and not:

```text id="f2dw9i"
Git
development tools
credentials
test data
```

unless explicitly required.

---

# 44. Frontend Image

Production image should contain only what the runtime needs.

---

# 45. Non-Root Containers

Production containers should run as a non-root user where the platform permits it.

---

# 46. Immutable Images

Deployments should use immutable image artifacts identified by:

```text id="8jvc9k"
commit SHA
image digest
release version
```

rather than mutable:

```text id="ghvy8u"
latest
```

for production deployments.

---

# 47. Image Tagging

Recommended:

```text id="n0m3lk"
cinerec-api:<git-sha>
cinerec-web:<git-sha>
```

Optionally:

```text id="g5l8ks"
cinerec-api:v1.4.0
```

where releases are versioned.

---

# 48. Image Registry

Use a private container registry where appropriate.

Examples include:

```text id="c6gpy3"
GitHub Container Registry
Docker Hub private repository
cloud provider registry
```

The application must not depend on a specific registry.

---

# 49. Image Scanning

CI should scan built images for:

```text id="v34q3h"
OS vulnerabilities
dependency vulnerabilities
secrets
```

before production deployment.

---

# 50. Docker Compose

Development:

```text id="4j8o7m"
docker-compose.yml
```

Production:

```text id="2h3f6q"
compose.production.yaml
```

Docker explicitly recommends using an additional Compose file for production-specific changes.

---

# 51. Development Compose

Conceptually:

```yaml id="d4k8vb"
services:
  web:
  api:
  worker:
  postgres:
  redis:
```

---

# 52. Production Compose

Production configuration should modify:

```text id="w5z43q"
restart policy
ports
environment variables
volumes
logging
resource limits
health checks
```

without duplicating the entire base configuration.

---

# 53. Health Checks

Every container should expose a useful health check where appropriate.

API:

```text id="5v7c3k"
/health
/ready
```

Worker:

```text id="kq4e5j"
worker liveness/heartbeat
```

Database:

```text id="z6in2w"
provider-native health
```

---

# 54. `/health`

Should answer:

```text id="f5cvj7"
Is the application process alive?
```

It should not require every external provider to be available.

---

# 55. `/ready`

Should answer:

```text id="yn4t1a"
Can this instance serve traffic?
```

Potential checks:

```text id="qj8c74"
PostgreSQL
critical configuration
essential local dependencies
```

Provider availability should normally be separate.

---

# 56. Startup Validation

At startup validate:

```text id="hf1xan"
required environment variables
database configuration
Redis configuration
Gemini configuration
TMDB configuration
application version
```

---

# 57. Startup Failure Policy

If a required secret is missing:

```text id="m0s4k8"
fail startup
```

Do not silently run with:

```text id="3v8f49"
missing production security configuration
```

---

# 58. Configuration Validation

Use Pydantic settings to validate:

```text id="elmb9x"
URLs
timeouts
integers
enums
required secrets
```

---

# 59. Secret Injection

Secrets must enter the process at runtime.

Sources may include:

```text id="p7n8wz"
hosting provider secret store
environment variables
secret manager
```

---

# 60. Never Bake Secrets Into Images

Prohibited:

```dockerfile id="gq75x3"
ENV GEMINI_API_KEY=...
```

or:

```dockerfile id="u0s4pa"
COPY .env .
```

---

# 61. Production Environment Files

Do not upload:

```text id="lc2x8d"
.env.production
```

to the repository.

Use deployment-provider secrets.

---

# 62. Environment Variable Separation

Use distinct credentials for:

```text id="b5x5k2"
development
staging
production
```

---

# 63. Google OAuth Deployment Configuration

Production OAuth configuration must contain:

```text id="y9x8w7"
production client identity
production callback URI
production allowed origin
```

and staging must use its own configuration where practical.

---

# 64. API Domain

Recommended:

```text id="t0k1f1"
https://api.cinerec.example.com
```

Frontend:

```text id="j1r0k8"
https://cinerec.example.com
```

---

# 65. Domain Strategy

Keep application domains stable.

Provider/deployment-specific URLs should not leak into application logic.

---

# 66. HTTPS

Production must use:

```text id="3q1y3p"
HTTPS only
```

including API endpoints.

---

# 67. HSTS

Once production domain configuration is stable:

```text id="h8n4yp"
Strict-Transport-Security
```

should be enabled.

---

# 68. TLS Termination

TLS may terminate at:

```text id="1d4z6t"
Vercel
reverse proxy
managed hosting layer
load balancer
```

The application should then receive trusted forwarded headers only from its configured proxy infrastructure.

---

# 69. Reverse Proxy

If self-hosting, use:

```text id="j89q47"
Caddy
Nginx
Traefik
```

or equivalent for:

```text id="3ck6ad"
TLS
routing
compression
request size limits
```

Do not introduce a reverse proxy when the chosen managed platform already provides it unless required.

---

# 70. API Routing

Recommended:

```text id="6isfd0"
api.cinerec.example.com
→ FastAPI
```

rather than:

```text id="1f8e3v"
browser
→ directly to individual services
```

---

# 71. Worker Accessibility

Celery workers should never be publicly reachable.

---

# 72. Redis Accessibility

Redis should never be publicly reachable.

---

# 73. PostgreSQL Accessibility

PostgreSQL should never be publicly reachable unless explicitly required by the managed provider's connection architecture.

---

# 74. Network Architecture

Preferred:

```text id="20z3b8"
Public
  │
  ├── Web
  └── API
       │
       ├── PostgreSQL
       ├── Redis
       └── Worker
```

---

# 75. Private Services

These should stay private:

```text id="u8f2oh"
PostgreSQL
Redis
Celery worker
internal admin services
telemetry collector where applicable
```

---

# 76. External Provider Access

API/worker services may initiate outbound connections to:

```text id="5p7j1j"
Gemini
TMDB
```

through restricted egress where infrastructure supports it.

---

# 77. No Inbound Provider Access

TMDB/Gemini should not need direct inbound access to CineRec infrastructure.

---

# 78. CI/CD Overview

CineRec should use:

```text id="3p7rgl"
GitHub
→ GitHub Actions
→ test
→ build
→ deploy staging
→ verify
→ production
```

---

# 79. CI Stages

```text id="85r6qk"
1. checkout
2. dependency install
3. lint
4. typecheck
5. unit tests
6. integration tests
7. security tests
8. build
9. container scan
10. artifact publish
```

---

# 80. Staging Deployment

After CI:

```text id="p13yv3"
deploy staging
→ migrate
→ smoke tests
→ E2E
→ security checks
```

---

# 81. Production Deployment

Production should occur only after required staging checks pass.

---

# 82. Git Branch Strategy

Initial:

```text id="w3qim1"
feature branches
        ↓
pull request
        ↓
main
        ↓
staging
        ↓
production
```

---

# 83. Main Branch

`main` must always remain deployable.

---

# 84. Pull Request Requirements

Require:

```text id="z6b66c"
CI passing
review
security checks
```

for meaningful changes.

---

# 85. Deployment Trigger

Recommended:

```text id="e2n3j6"
merge to main
→ staging deployment
```

and a deliberate production promotion.

---

# 86. Production Promotion

Options:

```text id="c1x5z9"
manual approval
tag release
protected environment
```

The exact mechanism depends on the hosting provider.

---

# 87. Continuous Deployment

The deployment pipeline should be automated but not blindly autonomous.

Production changes should have:

```text id="z3v2p8"
validated artifact
migration check
health check
rollback path
```

---

# 88. Build Once, Promote

Prefer:

```text id="ng0w9q"
build image
→ test image
→ deploy same image to staging
→ promote same image to production
```

rather than rebuilding production independently.

---

# 89. Artifact Immutability

A production release should be associated with:

```text id="2zv4d8"
Git SHA
image digest
environment
deployment timestamp
```

---

# 90. Deployment Metadata

Record:

```text id="1mj8h1"
version
commit SHA
deployment actor
deployment time
environment
```

---

# 91. Deployment Event

Emit:

```text id="s7n8d3"
deployment_started
deployment_completed
deployment_failed
```

for observability.

---

# 92. Database Migration Deployment

Deployment sequence:

```text id="x1c9r3"
new image available
 ↓
migration compatibility verified
 ↓
migration
 ↓
application rollout
 ↓
health checks
```

For complex expand/contract migrations:

```text id="t7n9v5"
schema expand
→ compatible deployment
→ data backfill
→ application switch
→ schema cleanup
```

---

# 93. Rolling Deployment

Where the platform supports multiple instances:

```text id="w6x81y"
old replica
old replica
old replica

↓ rollout

new replica
old replica
old replica

↓

new replica
new replica
old replica

↓

new replica
new replica
new replica
```

---

# 94. Stateless API Requirement

The FastAPI layer must remain stateless.

No required user session state should exist only in process memory.

---

# 95. In-Memory State

Allowed:

```text id="7y3zdm"
short-lived caches
metrics buffers
connection pools
```

Not allowed:

```text id="4f4rj0"
authoritative user session
watchlist
memory
conversation state
```

---

# 96. Horizontal Scaling

Because the API is stateless:

```text id="s35x1h"
one API instance
```

can become:

```text id="cz8y8x"
multiple API instances
```

without changing product logic.

---

# 97. Session Scaling

If authentication uses centralized/session-backed infrastructure, any API instance should be able to authenticate the same request.

---

# 98. Redis in Horizontal Scaling

Redis may support:

```text id="7m9f8u"
shared cache
locks
rate limits
queue coordination
```

across API instances.

---

# 99. Database Pool Scaling

When increasing API replicas:

```text id="4n3u1t"
recalculate total DB connections
```

Do not blindly multiply the pool size.

---

# 100. Worker Horizontal Scaling

Workers should be horizontally scalable.

Example:

```text id="6o1h9g"
queue
 ↓
worker 1
worker 2
worker 3
```

---

# 101. Worker Idempotency

Every background job must remain safe to retry.

---

# 102. Worker Shutdown

Deployments should allow workers to finish safe tasks where supported rather than immediately terminating active jobs.

---

# 103. Queue Draining

Before destructive worker shutdown:

```text id="o4qf3h"
stop accepting new work
→ complete safe current jobs
→ terminate
```

where supported.

---

# 104. Cron/Scheduled Jobs

Scheduled jobs should be centralized.

Examples:

```text id="a7c4pl"
refresh movie metadata
refresh availability
recompute profiles
cleanup expired data
evaluate models
```

---

# 105. Scheduler Ownership

Only one logical scheduler should create recurring jobs unless duplicate-safe scheduling is explicitly designed.

---

# 106. Scheduled Job Idempotency

A scheduled task running twice should not corrupt data.

---

# 107. Deployment of Scheduled Jobs

The scheduler may run:

```text id="1o7go2"
inside worker infrastructure
```

or through the hosting platform's scheduler.

Do not create multiple independent schedulers accidentally.

---

# 108. Long-Running Jobs

Long jobs must be asynchronous.

Examples:

```text id="ow33h0"
catalog ingestion
embedding generation
model training
```

---

# 109. Job Timeouts

Every background job should have:

```text id="x9t0wm"
execution timeout
retry policy
max attempts
failure state
```

---

# 110. Dead-Letter / Failed Job Handling

Repeated failures:

```text id="s3d4x4"
PENDING
→ RUNNING
→ RETRY
→ FAILED
```

must become inspectable.

---

# 111. Deployment Failure Strategy

If deployment fails:

```text id="j7ny13"
do not silently continue
```

The system should:

```text id="q1y6j9"
mark deployment failed
retain logs
retain previous artifact
retain migration state
```

---

# 112. Health Gate

A deployment should not be considered successful until:

```text id="1q8x4f"
container starts
health passes
readiness passes
database connection works
critical smoke tests pass
```

---

# 113. Automatic Rollback

Where supported, automatically roll back application artifacts when:

```text id="m8o9ib"
health checks fail
startup repeatedly fails
deployment never becomes ready
```

---

# 114. Database Rollback Caveat

Application rollback does not automatically mean database rollback.

For example:

```text id="8k6z2w"
application v2
migration v2
```

may not be compatible with:

```text id="x6d3o5"
application v1
```

after an irreversible migration.

Therefore schema changes must use expand/contract patterns.

---

# 115. Deployment Rollback Strategy

Preferred:

```text id="x7j2k3"
application rollback
+
forward-compatible schema
```

rather than:

```text id="6q9t0m"
blind database downgrade
```

---

# 116. Blue/Green Future

At larger scale:

```text id="6p79go"
Blue = current
Green = new
```

can be introduced.

Initially unnecessary.

---

# 117. Canary Future

At larger scale:

```text id="q7z0be"
1–5% traffic
→ new release
→ verify
→ increase
```

can reduce deployment risk.

---

# 118. Preview Environments

Pull requests may optionally receive:

```text id="3x1m7v"
preview frontend
preview API
```

but this should not automatically create a complete PostgreSQL/TMDB/Gemini stack for every PR.

Cost matters.

---

# 119. Preview Data

Use:

```text id="4iqz4q"
synthetic data
```

for preview environments.

Never use production user data.

---

# 120. Database for Preview

Potential options:

```text id="c4y1x6"
shared isolated development DB
ephemeral database
managed preview database
```

Choose according to cost and isolation.

---

# 121. Provider Credentials for Preview

Prefer:

```text id="8x1sv8"
mock Gemini
mock TMDB
or tightly restricted staging credentials
```

rather than production provider keys.

---

# 122. Deployment Security

CI/CD must enforce:

```text id="f7n4l2"
secret isolation
least privilege
protected production environment
artifact integrity
dependency scanning
```

---

# 123. GitHub Actions Permissions

Use least privilege:

```yaml id="oy1j9a"
permissions:
  contents: read
```

then explicitly add only required permissions.

---

# 124. Deployment Secrets

Store production secrets in:

```text id="y6z4es"
GitHub environment secrets
hosting provider secret manager
```

not:

```text id="0awf6b"
repository files
```

---

# 125. OIDC

When supported by the deployment provider, prefer short-lived OIDC-based deployment credentials over long-lived static cloud credentials.

---

# 126. Build Security

CI must not expose:

```text id="x9bnx3"
production database
Gemini production key
TMDB production token
```

to untrusted pull-request code.

---

# 127. Branch Protection

Production branch/release controls should prevent:

```text id="uj8v2s"
unreviewed deployment
```

---

# 128. Dependency Locking

Builds must use locked dependency resolution.

Python:

```text id="7v5g6g"
locked requirements/environment
```

Node:

```text id="uw3e1p"
package-lock.json
```

or the chosen package manager's equivalent.

---

# 129. Reproducible Builds

The same Git SHA should generate the same application artifact to the practical extent supported by the toolchain.

---

# 130. Build Metadata

Include:

```text id="54pco3"
commit SHA
build timestamp
version
```

but never secrets.

---

# 131. Production Configuration

Required:

```text id="7d8m4j"
DEBUG=false
secure cookies
restricted CORS
HTTPS
rate limits
structured logging
provider secrets
database URL
Redis URL
```

---

# 132. Configuration Drift

Production configuration should be versioned where safe.

Secrets themselves remain outside Git.

---

# 133. Infrastructure as Code

Infrastructure may initially be configured manually through a managed provider.

Once infrastructure becomes significant, move toward:

```text id="2k3r5b"
Terraform / OpenTofu
```

or the provider's equivalent.

Do not adopt IaC merely to satisfy aesthetics.

---

# 134. Infrastructure State

If IaC is used:

```text id="v5g0p7"
state must be backed up
access-controlled
versioned
```

---

# 135. Deployment Documentation

Maintain:

```text id="0f8m0k"
docs/deployment/
├── local.md
├── staging.md
├── production.md
├── migrations.md
├── rollback.md
└── secrets.md
```

---

# 136. Local Development Deployment

Primary flow:

```bash id="c7c6n0"
docker compose up -d
```

Then:

```text id="kxyy44"
database
redis
api
worker
web
```

become available.

---

# 137. Local Migrations

Run:

```bash id="j0s1i8"
alembic upgrade head
```

inside the API environment.

---

# 138. Local Seed

Optional:

```text id="i8s3yp"
development seed
```

for deterministic demo data.

---

# 139. Staging Deployment Sequence

```text id="e0k0to"
1. build artifact
2. deploy artifact
3. run migration
4. verify health
5. smoke test
6. run E2E
7. inspect telemetry
8. approve production
```

---

# 140. Production Deployment Sequence

```text id="7i5k0j"
1. validate release
2. verify backups
3. deploy schema-compatible version
4. run migrations
5. start new API instances
6. start worker
7. health checks
8. smoke tests
9. enable traffic
10. monitor
```

---

# 141. Deployment Window

Deploy during periods when:

```text id="kfn7f0"
operator attention is available
```

especially for:

```text id="w2gq3m"
database migrations
model changes
authentication changes
```

---

# 142. Migration Backups

For risky schema changes:

```text id="e9gqvj"
verify recent backup
```

before proceeding.

---

# 143. Data Migration Jobs

Large migrations should not run inside:

```text id="4j9y4v"
request path
```

Use background/offline jobs where appropriate.

---

# 144. Database Backfill

For large datasets:

```text id="y4w7m5"
add field
→ deploy
→ backfill gradually
→ monitor
→ enforce
```

---

# 145. Deployment Observability

Every release should automatically provide:

```text id="8a7n3v"
version
deployment event
release timestamp
```

to the observability system.

---

# 146. Release Dashboard

The main dashboard should display deployment markers so operators can correlate:

```text id="t0x5f7"
release
→ latency
→ error
→ recommendation quality
```

---

# 147. Post-Deployment Monitoring

Immediately after release inspect:

```text id="s9v2zo"
API 5xx
latency
database connections
Redis
worker queue
Gemini errors
TMDB errors
recommendation failures
```

---

# 148. Deployment Verification

A deployment is not successful merely because:

```text id="1zq8c0"
container = running
```

It must be:

```text id="2r0i1c"
healthy
ready
serving correct data
```

---

# 149. Smoke Tests

Minimum production smoke suite:

```text id="ik8m8t"
homepage
authentication
movie search
movie detail
recommendation
conversation
watchlist
```

Use a dedicated test identity/data set where authentication is required.

---

# 150. Synthetic Monitoring

Run periodic safe checks for:

```text id="6i7g5f"
API health
movie search
recommendation
conversation
```

where appropriate.

---

# 151. Production Data Protection

Synthetic checks must never modify:

```text id="6qs5qh"
real user accounts
real user watchlists
real user ratings
real user memories
```

---

# 152. Deployment Cost Controls

Near-zero-budget deployment should optimize:

```text id="m4ex0o"
idle services
provider requests
database usage
worker concurrency
LLM calls
observability retention
```

---

# 153. Scale-to-Zero Consideration

Services that support scale-to-zero can reduce idle cost.

However, scale-to-zero may introduce:

```text id="r0g9l0"
cold start
first-request latency
worker delay
```

The product should choose based on actual traffic patterns.

---

# 154. API Cold Start

The user-facing conversation path is latency-sensitive.

Avoid a deployment strategy that causes frequent API cold starts unless measured latency remains acceptable.

---

# 155. Worker Scale-to-Zero

Workers can potentially scale down more aggressively because they process asynchronous work.

---

# 156. Database Cost Strategy

Database is usually the most important persistent dependency.

Avoid unnecessary storage from:

```text id="6n7z8j"
raw provider payloads
duplicate embeddings
unbounded logs
duplicate events
unused indexes
```

---

# 157. Redis Cost Strategy

Keep only required data in Redis.

Every key should have:

```text id="3r0m4l"
purpose
TTL where appropriate
```

---

# 158. LLM Cost Strategy

Deployment must not create uncontrolled LLM usage.

Enforce:

```text id="l75i7y"
per-user limits
global limits
tool-call limits
output limits
```

---

# 159. TMDB Cost Strategy

Keep most movie retrieval local:

```text id="8fk53k"
PostgreSQL
+
Redis
```

and use TMDB primarily for:

```text id="02v67p"
enrichment
freshness
new entity resolution
availability
```

---

# 160. Worker Cost Strategy

Worker concurrency should be bounded.

Do not deploy:

```text id="z7k24m"
20 worker replicas
```

for a product with:

```text id="fb6g2t"
10 users
```

---

# 161. Autoscaling

Initial:

```text id="0k1v2a"
manual scaling
```

Later:

```text id="o8c99j"
CPU-based
request-based
queue-based
```

autoscaling can be added.

---

# 162. API Autoscaling

Scale API based on:

```text id="q3l2t4"
request concurrency
CPU
memory
latency
```

rather than CPU alone.

---

# 163. Worker Autoscaling

Scale workers primarily from:

```text id="x4y8j7"
queue depth
job age
job throughput
```

---

# 164. Database Scaling

First optimize:

```text id="t7v0f1"
queries
indexes
pooling
caching
```

before increasing database hardware.

---

# 165. Read Scaling Future

When read load materially exceeds a single database's capability:

```text id="t3c6h5"
read replicas
```

may be introduced.

Do not add them prematurely.

---

# 166. Database Write Scaling Future

Write scaling is much more complicated.

Before considering sharding:

```text id="q4i0tm"
optimize schema
optimize transactions
batch writes
remove unnecessary writes
```

---

# 167. Redis Scaling Future

At higher usage:

```text id="u9x7we"
replication
managed HA
cluster
```

may become appropriate.

---

# 168. Worker Scaling Future

If Celery/Redis becomes a bottleneck:

```text id="m8xkq9"
alternative broker
```

may be considered.

The application should remain broker-agnostic.

---

# 169. Kubernetes Rule

Kubernetes is not part of the initial deployment.

Introduce it only when concrete requirements justify:

```text id="9j4k5f"
many independently scaled services
complex orchestration
multi-region deployment
advanced scheduling
organizational operations requirements
```

---

# 170. Microservices Rule

Do not convert the modular monolith into microservices merely because deployment uses containers.

Containers do not require microservices.

---

# 171. Modular Monolith Deployment

The default is:

```text id="g5x2b8"
one backend codebase
multiple runtime processes
```

Specifically:

```text id="f6h7j4"
FastAPI process
Celery process
```

from the same application codebase.

---

# 172. Future Service Extraction

A component may become a separate service when:

```text id="9n0s5x"
independent scaling is required
independent deployment is required
resource profile differs substantially
failure isolation matters
team ownership requires it
```

---

# 173. Candidate Future Services

Potential future extraction candidates:

```text id="z1u8n7"
recommendation service
ML inference service
ingestion service
AI orchestration service
```

But not initially.

---

# 174. Deployment Architecture Evolution

### Stage 1

```text id="u8g4o3"
Next.js
FastAPI
Celery
PostgreSQL
Redis
```

### Stage 2

```text id="k2j8x9"
multiple API replicas
multiple workers
managed database
managed Redis
```

### Stage 3

```text id="m6x9r5"
dedicated ML inference
read replicas
advanced queue
```

### Stage 4

```text id="fy2v5s"
service extraction where justified
```

---

# 175. Domain Name Evolution

Keep public domains stable even as backend topology changes.

```text id="5a5y4b"
api.cinerec.example.com
```

may eventually route to:

```text id="k8d1v7"
API gateway
→ multiple services
```

without frontend redesign.

---

# 176. Database URL Abstraction

Application code should receive:

```text id="v0m7fn"
DATABASE_URL
```

rather than hardcoded host/port assumptions.

---

# 177. Redis URL Abstraction

Likewise:

```text id="s5k1jx"
REDIS_URL
```

---

# 178. Provider URL Abstraction

Gemini:

```text id="n5o0i9"
provider configuration
```

TMDB:

```text id="q1x0e5"
TMDB_BASE_URL
```

No hardcoded deployment topology.

---

# 179. Environment-Specific Domain

Use:

```text id="7l0g8j"
app.staging.cinerec.example.com
api.staging.cinerec.example.com
```

for staging where a custom domain is available.

---

# 180. CORS per Environment

Development:

```text id="9lxn5i"
localhost origins
```

Staging:

```text id="4d7jql"
staging origin
```

Production:

```text id="t7j8y0"
production origin
```

---

# 181. OAuth Callback per Environment

Each environment must have its own valid callback configuration.

---

# 182. Environment Data Isolation

Never allow:

```text id="2w1q8i"
staging
→ production database
```

through accidental environment-variable reuse.

---

# 183. Production Database Naming

Use a clearly separate production resource.

Do not rely on:

```text id="9v6o4t"
database name
```

alone for protection.

---

# 184. Staging Production-Likeness

Staging should reproduce important:

```text id="5k6w4j"
container
database
Redis
authentication
provider
```

behavior without containing production user data.

---

# 185. Secrets Testing

CI should verify that:

```text id="gr4y5z"
production secrets are not present in source tree
```

---

# 186. Deployment Secret Rotation

Maintain a documented process:

```text id="3e8f6a"
create replacement
→ deploy
→ verify
→ revoke old
```

---

# 187. Incident Deployment Freeze

During a major production incident:

```text id="7x0l4n"
pause nonessential deployments
```

until the root problem is understood.

---

# 188. Emergency Deployment

Security fixes may bypass ordinary release timing, but should still retain:

```text id="0o4y8d"
testing
audit trail
rollback plan
```

---

# 189. Emergency Configuration Change

Operational flags may be changed without redeploying when supported, but every such change must be auditable.

---

# 190. Feature Flags

Use feature flags for risky launches:

```text id="e4t6x8"
new recommender
new Gemini orchestration
new memory behavior
new UI flow
```

---

# 191. Feature Flag Defaults

Risky feature flags must default to:

```text id="p0y7w9"
disabled
```

in new environments unless explicitly enabled.

---

# 192. Gradual Rollout

Feature rollout may progress:

```text id="z5k9m8"
internal
→ staging
→ 1%
→ 10%
→ 50%
→ 100%
```

where infrastructure supports it.

---

# 193. Deployment and Models

Model deployments are application deployments.

A recommender model cannot be updated without:

```text id="3k7j2a"
model version
artifact
configuration
rollback path
```

---

# 194. ML Model Artifact Deployment

Store models separately from application code when they become large.

Example:

```text id="7q9v1o"
model registry/object storage
```

with:

```text id="4m8o2c"
version
checksum
training dataset
feature version
```

---

# 195. Model Rollback

Rollback should mean:

```text id="q3n5z8"
select previous known-good model
```

rather than rebuilding it from scratch.

---

# 196. Embedding Model Changes

Embedding-model changes require:

```text id="l2v9q7"
new embedding version
backfill strategy
compatibility strategy
rollback plan
```

---

# 197. Prompt Deployment

Prompt changes should be versioned separately from application release metadata.

---

# 198. Gemini Model Deployment

Production Gemini configuration should record:

```text id="5r7w9p"
provider
model
prompt version
thinking configuration
```

---

# 199. Provider Failure Deployment

A deployment changing TMDB/Gemini integration must include:

```text id="0p6a3z"
provider contract tests
failure tests
rate-limit tests
```

---

# 200. Deployment Observability Requirements

Every production deployment must allow operators to identify:

```text id="x8j0t4"
which version is running
which model is running
which prompt version is active
whether migrations completed
whether workers are healthy
```

---

# 201. Application Version Endpoint

A safe internal/public metadata endpoint may expose:

```json id="k6f73a"
{
  "version": "1.2.0",
  "commit": "abc123"
}
```

Do not expose:

```text id="nh5x8d"
environment variables
secrets
database URLs
internal credentials
```

---

# 202. Deployment Logs

Each deployment should create:

```text id="g4y5m1"
deployment_started
deployment_completed
deployment_failed
```

---

# 203. Deployment Event Metadata

Example:

```json id="cmcb1t"
{
  "event": "deployment_completed",
  "service": "cinerec-api",
  "version": "1.2.0",
  "commit": "abc123",
  "environment": "production"
}
```

---

# 204. Deployment Health Metrics

Track:

```text id="j2o6d0"
deployment success rate
startup failures
rollback rate
time to healthy
```

---

# 205. Change Failure Rate

Track:

```text id="c4o5e7"
deployments causing rollback
/
total deployments
```

---

# 206. Mean Time to Recovery

Track:

```text id="d9s1f2"
incident start
→ restored service
```

---

# 207. Deployment Frequency

Once stable, track:

```text id="m7r9x3"
successful production deployments/week
```

Do not optimize this metric at the expense of reliability.

---

# 208. Lead Time

Track:

```text id="n8v4w7"
code merged
→ production
```

where useful.

---

# 209. DORA-Style Metrics

Eventually track:

```text id="0y6f9n"
deployment frequency
lead time for changes
change failure rate
time to restore
```

These are useful operational indicators but not goals by themselves.

---

# 210. Backup Deployment Interaction

A deployment must not silently disable:

```text id="f8w5z6"
backups
retention
restore capability
```

---

# 211. Monitoring Deployment

Production deployment must include:

```text id="d6q1n9"
logs
metrics
traces
alerts
```

from day one.

---

# 212. Cost Monitoring

Track deployment-related costs for:

```text id="8c4e2m"
frontend hosting
API compute
worker compute
database
Redis
LLM
TMDB-related infrastructure
observability
storage
```

---

# 213. Cost Budget Alerts

Where the provider supports billing alerts:

```text id="h5s6k7"
configure budget notifications
```

This is particularly important for Gemini and other usage-metered infrastructure.

---

# 214. Usage-Based Failure

High usage should trigger:

```text id="q9x4h3"
rate limiting
degradation
```

before an uncontrolled bill becomes a production incident.

---

# 215. Deployment Resource Limits

Containers should have explicit or platform-managed limits for:

```text id="u4e3w2"
CPU
memory
disk
concurrency
```

where supported.

---

# 216. Memory Limits

Memory-heavy components:

```text id="7t5n9p"
ML jobs
embedding generation
data processing
```

must not share unconstrained resources with the API.

---

# 217. Worker Resource Isolation

Workers may require more CPU/memory than the API.

Deploy independently.

---

# 218. ML Job Isolation

Large training jobs should not run inside the production API container.

Use:

```text id="i7q3o2"
offline worker
CI job
dedicated compute
```

as scale requires.

---

# 219. Training Deployment Boundary

Training:

```text id="f0l3m5"
offline
```

Inference:

```text id="8x2h7s"
production
```

---

# 220. Model Build Pipeline

```text id="7p8l1s"
data
→ training
→ evaluation
→ artifact
→ registry
→ deployment
```

---

# 221. Model Promotion

A model may be promoted only when:

```text id="1c7s0x"
evaluation passes
```

defined in `12-testing-strategy.md`.

---

# 222. Data Migration Deployment

For large data migrations:

```text id="u9s8d7"
migration
→ background backfill
→ monitor
→ validation
→ switch
```

---

# 223. Deployment and Search Indexes

If PostgreSQL search structures change:

```text id="2h9v4m"
migration
→ index creation
→ query validation
```

must precede switching traffic.

---

# 224. Deployment and pgvector

If vector dimensionality changes:

```text id="m7j6k2"
new vector column/index
→ migration
→ backfill
→ switch
```

rather than incompatible in-place mutation without planning.

---

# 225. Deployment and Redis Cache

After schema/API changes, cache keys may need versioning.

Example:

```text id="v8p4x6"
cache:v2:movie:...
```

---

# 226. Cache Versioning

When response structure changes incompatibly:

```text id="y1q5m9"
increment cache namespace version
```

to avoid old entries being interpreted incorrectly.

---

# 227. Deployment and Celery Jobs

When job payload schemas change:

```text id="q5y7n3"
version task payload
```

or maintain backward compatibility during rolling deployments.

---

# 228. Worker/API Compatibility

During rolling deploys:

```text id="b7c9m0"
old worker
+
new API
```

may temporarily coexist.

Job contracts must remain compatible.

---

# 229. Deployment Compatibility Rule

Any asynchronously persisted message or job must be considered a versioned interface.

---

# 230. Deployment and Conversations

Conversation sessions should survive API deployments.

Their durable state belongs in PostgreSQL/provider state, not process memory.

---

# 231. Gemini Interaction IDs

If stateful Gemini Interactions are used:

```text id="h3m7k1"
persist interaction ID
```

must survive API restarts.

---

# 232. Deployment and Streaming

SSE connections may be interrupted during deployments.

The client should:

```text id="x9q7m4"
reconnect
resume/refetch
```

where supported.

---

# 233. Partial Stream Handling

A deployment must never convert an interrupted stream into an incorrectly persisted complete response.

---

# 234. Graceful Shutdown

API:

```text id="c3n4x9"
stop accepting new work
→ finish safe active requests
→ shutdown
```

Worker:

```text id="q2p8y6"
stop taking new jobs
→ finish safe jobs
→ shutdown
```

---

# 235. Deployment Timeouts

Set bounded:

```text id="1k5d4j"
startup timeout
health-check timeout
shutdown timeout
migration timeout
```

---

# 236. Hung Deployment Detection

A deployment stuck in:

```text id="9s6h2m"
starting
```

must fail rather than remain indefinitely pending.

---

# 237. Deployment Notifications

Production deployment status may notify operators through:

```text id="j4l5n7"
GitHub
Slack
email
```

where configured.

---

# 238. Release Notes

Every production release should have:

```text id="p7r0s2"
version
changes
migration notes
model changes
known issues
rollback notes
```

---

# 239. Semantic Versioning

Where releases are versioned:

```text id="d5n6q8"
MAJOR
MINOR
PATCH
```

should follow consistent semantics.

---

# 240. Database Change Documentation

Release notes must identify:

```text id="k3x8v4"
schema changes
new indexes
data migrations
```

---

# 241. AI Change Documentation

Release notes should identify:

```text id="r9m7t1"
Gemini model
prompt version
recommendation model
feature changes
```

---

# 242. Provider Change Documentation

TMDB/Gemini client changes should be included in release notes when externally significant.

---

# 243. Deployment Runbook

Maintain:

```text id="k5y6w2"
pre-deploy
deploy
verify
rollback
```

procedures.

---

# 244. Pre-Deploy Checklist

```text id="3f7h0p"
[ ] CI green
[ ] security checks green
[ ] migration tested
[ ] backup verified
[ ] release artifact identified
[ ] environment variables verified
[ ] provider configuration verified
[ ] rollback artifact available
[ ] monitoring ready
```

---

# 245. Deploy Checklist

```text id="5v9z1c"
[ ] deploy artifact
[ ] run migration
[ ] start/roll API
[ ] start/roll workers
[ ] health check
[ ] readiness check
[ ] smoke test
```

---

# 246. Post-Deploy Checklist

```text id="y0x4n3"
[ ] 5xx normal
[ ] latency normal
[ ] DB healthy
[ ] Redis healthy
[ ] workers healthy
[ ] Gemini healthy
[ ] TMDB healthy
[ ] recommendation quality normal
```

---

# 247. Rollback Checklist

```text id="j7p3c5"
[ ] identify previous version
[ ] confirm schema compatibility
[ ] rollback application
[ ] verify health
[ ] verify critical flow
[ ] monitor
[ ] document incident
```

---

# 248. Rollback Must Not Be Guesswork

The team must know before deployment:

```text id="3h5k8d"
what version to return to
how to return to it
whether the database permits it
```

---

# 249. Disaster Recovery

Define:

```text id="7c9f2p"
RPO
RTO
backup frequency
restore procedure
```

---

# 250. RPO

Initial target:

```text id="m2f8x1"
acceptable amount of data loss
```

must be defined based on the deployed database's backup capabilities.

---

# 251. RTO

Initial target:

```text id="v1n4q7"
acceptable time to restore service
```

should reflect the project's actual operational needs.

---

# 252. Disaster Scenarios

Test:

```text id="n3k5b8"
API failure
worker failure
Redis failure
database failure
deployment failure
credential compromise
hosting outage
```

---

# 253. Database Recovery

Database recovery is the highest-priority persistence recovery path.

---

# 254. Application Recovery

Application containers should be rebuildable from:

```text id="r8y2m6"
Git
+
locked dependencies
+
configuration
```

without manual code modification.

---

# 255. Infrastructure Recovery

Infrastructure should be rebuildable from:

```text id="q7x3n9"
managed configuration
or
IaC
```

as the deployment matures.

---

# 256. Disaster Recovery Test

At least periodically:

```text id="z5m1k8"
restore database
→ deploy application
→ migrate
→ smoke test
```

---

# 257. Domain Recovery

After database restoration, verify:

```text id="b5c7m9"
users
movies
ratings
watchlists
memories
recommendation data
```

remain consistent.

---

# 258. Cache Recovery

Redis can be rebuilt.

The system must not treat cache restoration as a disaster-recovery blocker.

---

# 259. Worker Recovery

Queued background work should either:

```text id="o1c4k7"
survive broker persistence
```

or:

```text id="q9z5m0"
be safely re-enqueued
```

without corrupting data.

---

# 260. Provider Outage During Deployment

Do not block deployment merely because:

```text id="m6b8s1"
TMDB
```

or:

```text id="n3x7q4"
Gemini
```

is temporarily degraded, unless the release directly depends on that provider.

---

# 261. Deployment During Provider Outage

Use:

```text id="4p8c0y"
cached/stale data
fallback
```

for verification where appropriate.

---

# 262. Zero-Downtime Goal

For ordinary API deployments, target:

```text id="y7n3k6"
no meaningful user-visible downtime
```

where hosting infrastructure supports rolling/zero-downtime deployment.

Render currently documents zero-downtime deploy support for Docker-based services.

---

# 263. Worker Downtime

Brief worker downtime should not directly affect normal API operation.

Queue backlog may temporarily increase.

---

# 264. Database Maintenance

Database maintenance should be scheduled with consideration for:

```text id="t9c2w1"
traffic
locks
backup
provider maintenance windows
```

---

# 265. Database Capacity Monitoring

Before increasing user load, monitor:

```text id="m7q5p3"
CPU
memory
connections
storage
query latency
locks
```

---

# 266. Redis Capacity Monitoring

Monitor:

```text id="c6v8h4"
memory
connections
commands
latency
evictions
```

---

# 267. Worker Capacity Monitoring

Monitor:

```text id="u5x1z6"
CPU
memory
queue depth
job duration
```

---

# 268. API Capacity Monitoring

Monitor:

```text id="o8n4s5"
requests
concurrency
CPU
memory
p95 latency
```

---

# 269. Frontend Capacity Monitoring

Monitor:

```text id="x0y8z3"
build duration
runtime errors
Web Vitals
API latency
```

---

# 270. Deployment Capacity Thresholds

Scale only when:

```text id="q6j7m2"
SLO
resource utilization
queue age
cost
```

show a sustained need.

---

# 271. No Premature Autoscaling

One stable API replica and one worker may be sufficient early in the project's life.

---

# 272. Deployment Architecture at Moderate Scale

```text id="s9m6w2"
                CDN / Frontend
                      │
                      ▼
              ┌──────────────┐
              │ Load Balancer│
              └──────┬───────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
             API           API
              │             │
              └──────┬──────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
      PostgreSQL   Redis      Workers
                                │
                           ┌────┴────┐
                           ▼         ▼
                        Worker    Worker
```

---

# 273. Deployment Architecture at Larger Scale

Potential future:

```text id="m4n8x9"
                API Gateway
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
 Conversation   Recommendation   Catalog
 Service           Service       Service
        │            │            │
        └────────────┼────────────┘
                     │
                Shared data
```

Only extract services when justified.

---

# 274. Kubernetes Future Boundary

If Kubernetes becomes necessary:

```text id="x3k7m2"
Docker images
→ Kubernetes deployments
```

without requiring a rewrite of application architecture.

This is one reason the current services should already be stateless and containerized.

---

# 275. Container Contract

Each service should know only:

```text id="j6b4v8"
its environment
its ports
its dependencies
its startup command
```

not the deployment platform.

---

# 276. Twelve-Factor Principles

CineRec should broadly follow:

```text id="w5c0s3"
configuration from environment
stateless processes
logs as streams
disposable processes
build/release/run separation
```

while adapting these principles to the actual infrastructure.

---

# 277. Build/Release/Run

Deployment should be:

```text id="d7x8m4"
Build
→ create immutable artifact

Release
→ combine artifact + configuration

Run
→ execute
```

Secrets belong to the release/runtime environment, not source.

---

# 278. Logs as Streams

Application containers should write logs to:

```text id="r0w6y2"
stdout
stderr
```

rather than requiring local log files for ordinary operational logging.

---

# 279. Persistent File Storage

Do not assume container-local disk is durable.

Containers should treat local filesystem state as ephemeral unless an explicit persistent volume/object storage system is used.

---

# 280. Uploaded Files Future

If the application introduces user uploads:

```text id="k8x1m9"
object storage
```

should be used rather than container disk.

---

# 281. Static Assets

Next.js/static assets should use the platform/CDN where appropriate.

---

# 282. Movie Images

TMDB image paths should remain provider-backed as defined in `09-tmdb-integration.md`.

Do not automatically copy the entire image catalog into the application filesystem.

---

# 283. Model Files

Large ML artifacts should not be copied into every API image unless they are small enough to justify it.

---

# 284. Worker Artifact Access

Workers may download/load model artifacts from controlled object storage or registry.

---

# 285. Database Migration Image

Migration execution should use the same backend code version/artifact compatibility assumptions as the API.

---

# 286. Migration Command

Conceptually:

```bash id="v7y2k4"
alembic upgrade head
```

must run before the application version assumes the new schema.

---

# 287. Migration Ownership

Only one controlled deployment path should own production migrations.

Avoid:

```text id="z0m9k6"
every API replica
→ independently runs migrations
```

unless the migration mechanism explicitly handles concurrency safely.

---

# 288. Migration Locking

Where necessary, use application/deployment-level coordination to ensure only one migration operation runs at a time.

---

# 289. Deployment Concurrency

Do not allow:

```text id="m4x9c7"
deployment A
+
deployment B
```

to independently mutate the same production database schema.

Use deployment serialization.

---

# 290. Release Lock

Production promotion should support a release lock or equivalent mechanism.

---

# 291. Environment Promotion

Recommended:

```text id="q4p6c1"
commit
→ staging
→ verification
→ production
```

not:

```text id="n8w1j0"
different code built separately
```

---

# 292. Production Smoke Tests

Smoke tests should exercise:

```text id="b3m7v2"
GET /
auth
search
movie details
recommendations
conversation
```

with controlled test data.

---

# 293. Smoke-Test Failure

If smoke test fails:

```text id="o7q9k4"
deployment is not considered successful
```

and rollback/mitigation begins.

---

# 294. Post-Deploy Observation Window

After a release, inspect telemetry before declaring the release stable.

Pay particular attention to:

```text id="j4m1x8"
5xx
latency
provider errors
worker backlog
recommendation empty rate
```

---

# 295. Release Stability

A release should remain under observation through its first meaningful traffic window.

---

# 296. Deployment SLO

Track:

```text id="e6r3n7"
percentage of deployments completing successfully
```

---

# 297. Rollback SLO

Track:

```text id="f5m8y2"
time from rollback decision
→ restored healthy version
```

---

# 298. Deployment Testing Matrix

| Layer             |      Dev |   CI |    Staging | Production |
| ----------------- | -------: | ---: | ---------: | ---------: |
| Unit tests        |        ✓ |    ✓ |            |            |
| Integration tests |        ✓ |    ✓ |          ✓ |            |
| Security tests    |        ✓ |    ✓ |          ✓ |            |
| E2E               | optional |    ✓ |          ✓ |      smoke |
| Provider tests    |     mock | mock | real smoke |       real |
| Migrations        |        ✓ |    ✓ |          ✓ |          ✓ |
| Load tests        |          |      |          ✓ |    limited |
| Backup restore    |          |      |          ✓ |   periodic |
| Observability     |        ✓ |    ✓ |          ✓ |          ✓ |

---

# 299. Deployment Definition of Done

```text id="k6p0v9"
[ ] Production Docker images build successfully
[ ] Images are immutable/versioned
[ ] Images pass security scanning
[ ] Frontend deploys independently
[ ] API deploys independently
[ ] Worker deploys independently
[ ] PostgreSQL configured
[ ] Redis configured
[ ] Secrets configured
[ ] HTTPS enabled
[ ] CORS configured
[ ] OAuth production callbacks configured
[ ] Health checks configured
[ ] Readiness checks configured
[ ] Migrations automated
[ ] Migration compatibility verified
[ ] CI/CD configured
[ ] Staging environment exists
[ ] Production smoke tests exist
[ ] Rollback procedure documented
[ ] Backups enabled
[ ] Restore tested
[ ] OpenTelemetry configured
[ ] Prometheus/Grafana configured
[ ] Deployment events recorded
[ ] Alerts configured
[ ] Cost monitoring configured
```

---

# 300. First Production Architecture

The first serious production deployment should look approximately like:

```text id="f0w6o4"
                         USERS
                           │
                           ▼
                    ┌──────────────┐
                    │    Vercel    │
                    │   Next.js    │
                    └──────┬───────┘
                           │
                           ▼
                 api.cinerec.example
                           │
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    │   Container  │
                    └──────┬───────┘
                           │
              ┌────────────┼─────────────┐
              │            │             │
              ▼            ▼             ▼
         PostgreSQL      Redis        Gemini/TMDB
        (managed)       (managed)       APIs
              │
              │
              ▼
        Durable CineRec state

              ▲
              │
         Celery broker
              │
              ▼
        ┌───────────────┐
        │ Celery Worker │
        │   Container   │
        └───────────────┘

Telemetry:
FastAPI / Worker
      │
      ▼
OpenTelemetry
      │
      ├── traces
      ├── metrics
      └── logs
```

---

# 301. Moderate-Scale Architecture

When traffic grows:

```text id="s3m7q2"
                         CDN
                          │
                          ▼
                     Next.js
                          │
                          ▼
                   Load Balancer
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
            API          API          API
             │            │            │
             └────────────┼────────────┘
                          │
                ┌─────────┼─────────┐
                ▼         ▼         ▼
             Redis     PostgreSQL   Workers
                                    │
                             ┌──────┼──────┐
                             ▼      ▼      ▼
                          Worker Worker Worker
```

---

# 302. Scaling Path

The architecture scales in this order:

```text id="c5j7m1"
1. optimize code
2. improve caching
3. improve queries
4. add API replicas
5. add worker replicas
6. increase DB capacity
7. improve DB pooling
8. add read replicas if necessary
9. isolate heavy ML workloads
10. extract services only when justified
```

---

# 303. Things We Explicitly Do Not Deploy Initially

```text id="a0x7r4"
Kubernetes
Kafka
Elasticsearch/OpenSearch
separate vector database
service mesh
multi-region database
microservice fleet
GPU inference cluster
dedicated feature store
dedicated service registry
```

None is necessary for the first serious CineRec deployment.

---

# 304. Deployment Complexity Rule

Every infrastructure component must answer:

```text id="f7m5q9"
What problem does this solve?
What measurable bottleneck requires it?
What operational burden does it add?
```

If no strong answer exists:

```text id="k8t6x0"
do not add it.
```

---

# 305. Platform Abstraction

Application code must not assume:

```text id="q6x9m4"
Vercel
Render
Supabase
AWS
GCP
Azure
```

unless provider-specific behavior is explicitly encapsulated.

---

# 306. Provider Configuration

Infrastructure-specific settings belong in:

```text id="0s7jv8"
deployment/
infrastructure/
environment
```

not domain logic.

---

# 307. Deployment Repository Structure

Recommended additions:

```text id="t6q4v0"
infrastructure/
├── docker/
│   ├── api.Dockerfile
│   ├── web.Dockerfile
│   └── compose.production.yaml
│
├── deployment/
│   ├── staging/
│   ├── production/
│   └── scripts/
│
└── monitoring/
```

---

# 308. Dockerfile Structure

```text id="u7s8m2"
apps/
├── api/
│   └── Dockerfile
└── web/
    └── Dockerfile
```

---

# 309. Worker Image Strategy

The worker should reuse the API image where reasonable:

```text id="o6n3b7"
cinerec-api:<sha>
```

with:

```text id="j1r7k5"
API command
```

or:

```text id="x3v9p0"
Celery command
```

---

# 310. Build Cache

Use Docker layer caching in CI to reduce:

```text id="q8k4m6"
build time
CI resource usage
```

---

# 311. Build Context

Keep Docker build contexts small.

Do not copy:

```text id="y4r8k1"
.git
local datasets
node_modules
Python virtualenv
test artifacts
```

into production images.

Use `.dockerignore`.

---

# 312. Dockerfile Security

Do not include:

```text id="w7x0r2"
credentials
private keys
production env files
```

---

# 313. Runtime User

Create a non-root runtime user.

---

# 314. Filesystem

Run the application with minimal write permissions.

If write access is required:

```text id="f4m9q7"
temporary directory
```

only.

---

# 315. Container Restart Policy

Production services should automatically restart after transient crashes where supported.

Docker's production Compose guidance explicitly recommends an appropriate restart policy.

---

# 316. Restart Storm Prevention

Restart policy must not create an infinite crash loop consuming resources.

Monitor repeated restarts.

---

# 317. Startup Dependency Handling

Do not assume:

```text id="x7p4h1"
PostgreSQL starts
→ API starts
```

at exactly the same moment.

Use retries/readiness rather than brittle startup ordering.

---

# 318. Database Startup

API should retry initial database connection for a bounded period.

---

# 319. Redis Startup

Likewise Redis connection startup should be resilient.

---

# 320. Provider Startup

Gemini/TMDB should not necessarily block application startup if the API can operate in degraded mode.

---

# 321. Dependency Health

Critical dependencies:

```text id="u9n5x7"
PostgreSQL
```

may be startup-critical.

Optional dependencies:

```text id="i3h2c9"
TMDB
Gemini
```

may be runtime-degraded depending on feature.

---

# 322. Readiness Policy

If the application cannot serve any protected functionality without PostgreSQL:

```text id="h7k4p2"
PostgreSQL unavailable
→ not ready
```

If Gemini fails:

```text id="r4x6m8"
Gemini unavailable
→ API can remain ready
```

because fallback behavior exists.

---

# 323. Production Logs

Container logs should go to standard output and be collected by the hosting platform/observability system.

---

# 324. Log Retention

Keep operational logs long enough to:

```text id="z9f4y1"
debug recent incidents
```

without collecting unlimited historical data.

---

# 325. Release Artifact Retention

Keep previous production images long enough to support rollback.

---

# 326. Artifact Garbage Collection

Delete obsolete images/artifacts according to a retention policy.

---

# 327. Dependency Update Workflow

Dependency updates should go through:

```text id="m4z7x2"
PR
→ CI
→ security scan
→ staging
→ production
```

not manual production changes.

---

# 328. OS/Base Image Updates

Rebuild images when base images receive important security fixes.

---

# 329. Security Patch Priority

Critical security patches should bypass normal release cadence when risk justifies it.

---

# 330. Deployment Ownership

At least one explicit project role must own:

```text id="v3j6w8"
deployment
credentials
backups
incident response
```

---

# 331. Deployment Runbook Ownership

Runbooks must have a responsible maintainer.

---

# 332. Production Access

Production access should be:

```text id="q5m1n7"
individual
least-privileged
audited
```

---

# 333. No Shared Production Credentials

Avoid shared administrator accounts.

---

# 334. Deployment Account

The CI/CD deployment identity should have only the permissions required to deploy.

It should not automatically receive unrestricted database administration rights.

---

# 335. Migration Permission Separation

Where practical:

```text id="h8n3q6"
deployment migration identity
≠
normal API database identity
```

---

# 336. Production Shell Access

Use only when required.

Prefer:

```text id="s2j7v9"
managed logs
managed database console
deployment tools
```

---

# 337. Infrastructure Audit

Review periodically:

```text id="u0w5c3"
public ports
public resources
secrets
service accounts
OAuth settings
CORS
domains
```

---

# 338. DNS

Production DNS should be managed through a controlled provider.

Record:

```text id="x6q1p4"
A
AAAA
CNAME
TXT
```

records appropriately.

---

# 339. Domain Verification

OAuth providers, frontend hosting, and API hosting may require domain verification.

Keep DNS ownership under controlled project accounts.

---

# 340. TLS Certificate

Use managed certificates where possible.

Do not manually rotate certificates unless required.

---

# 341. CDN

Frontend/static content should use CDN capabilities provided by the hosting layer where appropriate.

---

# 342. API CDN

Do not put authenticated dynamic API responses behind a public CDN cache unless explicitly designed and secured.

---

# 343. Cache-Control

Public/static:

```text id="6r4n9v"
long-lived cache
```

Private:

```text id="b8x7c2"
private/no-store
```

as appropriate.

---

# 344. Deployment and Browser Caching

Frontend deployment must invalidate stale application assets correctly.

Next.js handles asset versioning through its build system; do not implement an ad hoc cache-busting system.

---

# 345. API Client Compatibility

Frontend and backend changes should remain compatible during rolling deployments.

---

# 346. API Versioning

Use:

```text id="j7v4m2"
/api/v1
```

for the API.

Breaking changes should become:

```text id="a2q8v5"
/api/v2
```

or another explicit compatibility strategy.

---

# 347. Deployment of API Versions

Old and new API versions may coexist temporarily during migration.

---

# 348. Deprecation

Old versions should have:

```text id="e3s6w1"
deprecation timeline
usage monitoring
removal plan
```

---

# 349. Deployment Health Dashboard

The dashboard should show:

```text id="h1v5q7"
release version
API replicas
worker replicas
DB health
Redis health
queue depth
Gemini health
TMDB health
```

---

# 350. Final Deployment Decision

The canonical initial deployment should be:

```text id="k7x4p0"
Frontend:
Next.js
→ Vercel or equivalent

Backend:
FastAPI
→ Docker
→ Render/equivalent

Workers:
Celery
→ Docker
→ same backend artifact

Database:
PostgreSQL
→ managed provider

Redis:
managed/private Redis

CI/CD:
GitHub Actions

Telemetry:
OpenTelemetry
→ Prometheus/Grafana
```

This topology keeps the codebase portable while using managed infrastructure where operational toil is not valuable.

---

# 351. Final Scaling Decision

When the application grows:

```text id="w6n2k5"
First:
more API replicas

Then:
more workers

Then:
database optimization/scaling

Then:
Redis scaling

Then:
ML isolation

Only later:
service extraction / orchestration platform
```

---

# 352. Final Deployment Principle

> **CineRec should be deployable by one developer today and scalable by an engineering team tomorrow without replacing the application architecture.**

The initial deployment therefore optimizes for:

```text id="x9m4k6"
simplicity
security
reproducibility
observability
low fixed cost
```

while preserving:

```text id="q7v1c3"
stateless services
provider abstraction
database ownership
background processing
immutable artifacts
automated migrations
horizontal scaling
```

---

# 353. Final Deployment Contract

The deployment contract is:

```text id="a6f8q2"
Git commit
   ↓
CI validation
   ↓
Immutable artifact
   ↓
Staging
   ↓
Migration verification
   ↓
Smoke/E2E
   ↓
Production promotion
   ↓
Health checks
   ↓
Telemetry
   ↓
Rollback if necessary
```

The production system must never depend on:

```text id="m9j5r4"
manual source edits
manual secret insertion
manual database schema changes
developer laptops
untracked production state
```

---

# 354. Antigravity Deployment Rules

Antigravity must preserve these deployment invariants:

```text id="n2w8q7"
1. Never hardcode production secrets.
2. Never put API secrets into frontend variables.
3. Never expose PostgreSQL or Redis publicly by default.
4. Never run migrations implicitly from every API replica.
5. Never deploy mutable `latest` artifacts as the canonical production version.
6. Never couple application logic to one hosting provider.
7. Never run long ML jobs inside HTTP request handlers.
8. Never make API correctness depend on local filesystem state.
9. Never bypass CI for ordinary production changes.
10. Never remove health checks to "make deployment work."
11. Never skip rollback planning for database changes.
12. Never treat Redis as durable truth.
13. Never use production data in preview environments.
14. Never deploy a model without a version.
15. Never deploy a prompt change without versioning/evaluation.
```

---

# 355. Definition of Done — Production

```text id="4m8p2x"
[ ] Code is reproducibly buildable
[ ] Production Docker images exist
[ ] Image versions are immutable
[ ] Frontend deployment is configured
[ ] API deployment is configured
[ ] Worker deployment is configured
[ ] PostgreSQL is provisioned
[ ] Redis is provisioned
[ ] Secrets are configured securely
[ ] Production domain exists
[ ] TLS works
[ ] OAuth works
[ ] CORS is restricted
[ ] Health endpoint works
[ ] Readiness endpoint works
[ ] Migrations are automated
[ ] Database backups exist
[ ] Database restore has been tested
[ ] CI/CD works
[ ] Staging deployment works
[ ] Production smoke test works
[ ] Rollback path is documented
[ ] OpenTelemetry is connected
[ ] Metrics are visible
[ ] Logs are visible
[ ] Alerts are configured
[ ] Cost monitoring exists
[ ] Release metadata is recorded
```

---

# 356. Final Architecture

```text id="6q8f3r"
                         ┌─────────────────┐
                         │     USERS       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Next.js / CDN  │
                         └────────┬────────┘
                                  │
                           HTTPS / JSON / SSE
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    FastAPI      │
                         │  Stateless API  │
                         └────────┬────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
      ┌─────────────┐      ┌─────────────┐      ┌──────────────┐
      │ PostgreSQL  │      │    Redis    │      │   Providers  │
      │   Durable   │      │ Cache/Queue │      │ Gemini/TMDB  │
      └──────┬──────┘      └──────┬──────┘      └──────────────┘
             │                    │
             │                    ▼
             │             ┌─────────────┐
             │             │   Celery    │
             │             │   Workers   │
             │             └─────────────┘
             │
             ▼
       CineRec State

All services
     │
     ▼
OpenTelemetry
     │
 ┌───┼──────┐
 ▼   ▼      ▼
Trace Metric Log
```

---

# 357. Ultimate Engineering Rule

> **Deploy the simplest architecture that preserves the boundaries required by the product, then scale the boundaries rather than rewriting them.**

For CineRec that means:

```text id="2x7m9f"
modular monolith
→ containerized runtime
→ managed persistence
→ stateless API
→ separate workers
→ automated deployment
→ strong observability
→ measured scaling
```

not:

```text id="6n4q0z"
premature microservices
+
Kubernetes
+
Kafka
+
service mesh
+
multiple databases
```

before the workload justifies them.

The deployment architecture is therefore designed to start small, remain inexpensive, and grow into a serious production system without throwing away the engineering decisions made in the rest of the CineRec specification.

