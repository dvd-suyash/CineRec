# CineRec — Master Implementation Plan

**Status:** Active Engineering Plan  
**Date:** 2026-09-28  
**Scope:** End-to-end implementation of CineRec  
**Primary Consumer:** AI coding agents (Google Antigravity) and human engineers  
**Related Documents:** `AGENTS.md`, `docs/01-product-vision.md` through `docs/14-deployment.md`, `docs/decisions/ADR-001-modular-monolith.md` through `ADR-003-pgvector.md`

---

# 1. Purpose

This document is the **master execution plan** for building CineRec from an empty or partially initialized repository into a production-oriented personalized movie recommendation platform.

It converts the product, architecture, database, API, recommendation, conversation, memory, AI, security, testing, observability, and deployment documents into a **dependency-ordered implementation sequence**.

The implementation must optimize for:

- correctness
- security
- maintainability
- testability
- observability
- performance
- reproducibility
- cost efficiency
- architectural clarity
- safe evolution

The implementation must **not** optimize for:

- maximum number of technologies
- premature microservices
- unnecessary abstraction
- artificial complexity
- visually impressive architecture diagrams without operational justification
- speed at the expense of verification

> **Primary engineering principle: every phase must produce a working, testable, verifiable increment, and no phase is complete until its completion gate passes.**

---

# 2. Implementation Philosophy

CineRec is being built as a **modular monolith with explicitly separated infrastructure boundaries**.

The expected initial architecture is:

```text
Browser
   ↓
Next.js Web
   ↓
FastAPI
   ↓
Application Services
   ↓
Domain Modules
   ↓
Ports / Interfaces
   ↓
Infrastructure
   ├── PostgreSQL + pgvector
   ├── Redis
   ├── Celery
   ├── TMDB Adapter
   ├── Gemini Adapter
   └── Observability
```

The recommendation pipeline is:

```text
User Request
    ↓
Conversation / Intent Understanding
    ↓
Context Assembly
    ↓
Candidate Generation
    ├── Collaborative Filtering
    ├── Semantic Retrieval
    ├── Metadata Retrieval
    ├── Popularity
    └── Exploration
    ↓
Candidate Union
    ↓
Hard Filtering
    ↓
Feature Construction
    ↓
Ranking
    ↓
Diversity / Exploration
    ↓
3–5 Recommendations
    ↓
Explanation
    ↓
User Feedback
    ↓
Updated Personalization
```

---

# 3. Non-Negotiable Engineering Rules

These rules apply to every phase.

## 3.1 Source-of-truth order

The agent must follow:

```text
1. Explicit user requirements
2. AGENTS.md
3. Architecture / requirements documentation
4. Accepted ADRs
5. Existing tested behavior
6. Existing local conventions
7. Agent assumptions
```

Conflicts must not be silently resolved by inventing architecture.

## 3.2 No architecture drift

Do not introduce, without a corresponding accepted ADR:

- microservices
- Kafka
- Elasticsearch/OpenSearch
- a dedicated vector database
- a graph database
- Kubernetes
- service mesh
- database-per-service
- database-per-feature
- another LLM provider as a core dependency
- another movie-data provider as a core dependency

## 3.3 Hard boundaries

The following boundaries must remain intact:

```text
Frontend → API only
API → Application Services
Application Services → Domain / Ports
Infrastructure → Provider / Database implementations
Gemini → interpretation/orchestration, not authority
TMDB → external movie data, not domain authority
PostgreSQL → durable source of truth
Redis → cache / ephemeral infrastructure
pgvector → vector retrieval, not recommendation ranking
Recommendation Engine → recommendation logic
```

## 3.4 No fake success

Never report success when:

- a durable write failed
- authorization failed
- required provider data was unavailable
- required processing was skipped
- the implementation is only mocked
- tests fail

## 3.5 No unverified completion

A feature is not complete because:

- the page renders
- a curl request works once
- a model returns a plausible answer
- the code compiles locally

Completion requires the phase's verification gates.

---

# 4. Universal Agent Workflow

For every task inside every phase:

```text
READ
  ↓
UNDERSTAND
  ↓
INSPECT
  ↓
PLAN
  ↓
IMPLEMENT
  ↓
TEST
  ↓
VERIFY
  ↓
REVIEW
  ↓
DOCUMENT
  ↓
COMMIT
```

When verification fails:

```text
FAIL
  ↓
REPRODUCE
  ↓
ISOLATE
  ↓
ROOT CAUSE
  ↓
FIX
  ↓
REGRESSION TEST
  ↓
RE-RUN
```

Never skip directly from `IMPLEMENT` to `DONE`.

---

# 5. Standard Definition of Done

Unless a phase or task explicitly defines stronger requirements, a work item is complete only when all applicable conditions are satisfied:

```text
[ ] Requirements satisfied
[ ] Correct architectural boundary
[ ] Types / schemas valid
[ ] Validation implemented
[ ] Authorization implemented
[ ] Failure paths handled
[ ] Tests added or updated
[ ] Relevant existing tests pass
[ ] Lint passes
[ ] Type checks pass
[ ] Formatting passes
[ ] Database migration exists when required
[ ] Observability added when operationally relevant
[ ] Documentation updated
[ ] No secrets committed
[ ] No known architecture violations
[ ] Diff reviewed
```

---

# 6. Phase Dependency Map

The required implementation order is:

```text
PHASE 0  → Repository Audit & Planning
    ↓
PHASE 1  → Repository / Tooling Foundation
    ↓
PHASE 2  → Local Infrastructure Foundation
    ↓
PHASE 3  → Database Schema & Persistence
    ↓
PHASE 4  → Authentication & User Identity
    ↓
PHASE 5  → Movie Domain + TMDB Integration
    ↓
PHASE 6  → Core API Contract + Application Services
    ↓
PHASE 7  → Web Shell + Design System + Orb UI
    ↓
PHASE 8  → Gemini / Conversation Engine
    ↓
PHASE 9  → Memory System
    ↓
PHASE 10 → Interaction / Feedback Infrastructure
    ↓
PHASE 11 → Recommendation Baselines
    ↓
PHASE 12 → pgvector + Semantic Retrieval
    ↓
PHASE 13 → Collaborative Filtering
    ↓
PHASE 14 → Hybrid Recommendation Engine
    ↓
PHASE 15 → My Cinema / Dashboard
    ↓
PHASE 16 → Async Processing / Redis / Celery
    ↓
PHASE 17 → Observability + Reliability
    ↓
PHASE 18 → Security Hardening
    ↓
PHASE 19 → Performance / Load / Scale Validation
    ↓
PHASE 20 → End-to-End Hardening
    ↓
PHASE 21 → Production Deployment
    ↓
PHASE 22 → Release Validation / Operational Readiness
```

Phases may be internally split into smaller tickets, but the dependency order must not be casually rearranged.

---

# 7. PHASE 0 — Repository Audit & Implementation Preparation

## Objective

Establish a shared understanding of the repository before modifying it.

## Inputs

Read:

```text
AGENTS.md
01-product-vision.md
02-functional-requirements.md
03-system-architecture.md
04-database-design.md
05-api-contract.md
06-recommendation-system.md
07-orb-conversation-design.md
08-memory-system.md
09-tmdb-integration.md
10-gemini-integration.md
11-security.md
12-testing-strategy.md
13-observability.md
14-deployment.md
ADR-001
ADR-002
ADR-003
```

## Tasks

1. Inspect repository tree.
2. Identify implemented vs missing components.
3. Identify existing package managers and lockfiles.
4. Identify existing environment configuration.
5. Identify existing tests.
6. Identify existing migrations.
7. Identify existing CI/CD.
8. Identify conflicting or stale implementation.
9. Confirm Node and Python versions.
10. Produce an implementation gap map.

## Required output

Create/update:

```text
IMPLEMENTATION_STATUS.md
```

with:

```text
Implemented
Partially Implemented
Missing
Broken
Needs Refactor
Needs Verification
```

## Checks

```text
[ ] Repository builds or current failures are recorded
[ ] Existing tests are identified
[ ] Existing architecture is mapped
[ ] Required docs are present
[ ] No duplicate architecture has been invented
```

## Completion Gate

Do not begin Phase 1 until the agent can explain:

- where the frontend lives
- where the backend lives
- where ML code lives
- where migrations live
- how tests run
- how configuration works
- which portions are already implemented
- which architecture documents govern them

---

# 8. PHASE 1 — Repository & Tooling Foundation

## Objective

Create a deterministic, reproducible development environment.

## Tasks

### Repository structure

Establish:

```text
apps/
  web/
  api/
packages/
  shared-types/
  config/
ml/
  data/
  features/
  models/
  training/
  evaluation/
  inference/
infrastructure/
  docker/
  deployment/
tests/
docs/
scripts/
```

### Frontend tooling

Configure:

- Next.js App Router
- TypeScript strict mode
- Tailwind CSS
- shadcn/ui
- Motion
- TanStack Query
- ESLint
- Prettier
- Vitest
- Playwright

### Backend tooling

Configure:

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy 2
- Alembic
- Pytest
- Ruff
- Pyright

### Repository quality

Add:

```text
.pre-commit-config.yaml
.editorconfig
.gitignore
.env.example
README.md
```

Add standard scripts for:

```text
install
format
lint
typecheck
test
build
dev
```

## Tests / Checks

```text
[ ] Frontend starts
[ ] Frontend production build succeeds
[ ] Backend imports successfully
[ ] Backend test runner starts
[ ] Ruff passes
[ ] Pyright passes
[ ] ESLint passes
[ ] TypeScript passes
[ ] Prettier check passes
[ ] Git hooks execute
```

## Completion Gate

A fresh clone must be able to reach a known-good baseline using documented commands.

No feature work begins if basic repository tooling remains broken.

---

# 9. PHASE 2 — Local Infrastructure Foundation

## Objective

Create reproducible local infrastructure without introducing unnecessary services.

## Required services

```text
PostgreSQL
Redis
API
Web
Celery Worker
```

Use Docker Compose.

## Tasks

1. PostgreSQL container.
2. Enable required PostgreSQL extensions, including pgvector and pg_trgm where appropriate.
3. Redis container.
4. API container/dev service.
5. Worker container/dev service.
6. Health checks.
7. Dependency startup behavior.
8. Environment variable loading.
9. Local networking.
10. Persistent development volume for PostgreSQL.

## Failure requirements

Startup must clearly distinguish:

```text
database unavailable
redis unavailable
provider configuration missing
migration missing
application startup failure
```

## Tests

```text
[ ] docker compose config validates
[ ] PostgreSQL accepts connections
[ ] Redis accepts connections
[ ] API can reach PostgreSQL
[ ] API can reach Redis
[ ] Worker can reach broker
[ ] Health endpoint works
[ ] Readiness endpoint correctly reflects dependency health
```

## Completion Gate

A fresh development machine with Docker must be able to start the local stack reproducibly from documented instructions.

---

# 10. PHASE 3 — Database Schema & Persistence

## Objective

Implement the relational model defined in `04-database-design.md`.

## Initial schema groups

### Core

```text
users
user_identities
user_profiles
```

### Movie catalog

```text
movies
movie_provider_ids
genres
movie_genres
people
movie_credits
movie_keywords
movie_keyword_links
movie_relations
movie_watch_providers
```

### User activity

```text
ratings
movie_preferences
watchlists
viewing_history
interactions
```

### Conversation

```text
conversation_sessions
conversation_messages
conversation_intents
```

### Personalization

```text
memories
memory_evidence
taste_profiles
user_embeddings
movie_embeddings
```

### Recommendations

```text
recommendation_requests
recommendation_items
```

### ML

```text
model_versions
training_datasets
experiments
experiment_variants
experiment_assignments
```

## Tasks

1. Define SQLAlchemy models.
2. Define relationships.
3. Define constraints.
4. Define foreign keys.
5. Define unique indexes.
6. Define query-driven indexes.
7. Enable required extensions.
8. Create initial Alembic migration.
9. Verify migration from empty database.
10. Verify downgrade strategy where feasible.

## Required database principles

```text
PostgreSQL = source of truth
UTC timestamps
UUID-based application identifiers
explicit ownership
JSONB only when justified
no unbounded unindexed access
```

## Critical tests

Test:

- foreign keys
- uniqueness
- not-null constraints
- ownership fields
- duplicate interaction handling
- rating uniqueness semantics
- cascade behavior
- delete behavior
- transaction rollback
- migration correctness

## Completion Gate

```text
[ ] Empty DB → migration → working schema
[ ] All critical constraints tested
[ ] No model uses SQLite-specific assumptions
[ ] Integration tests use real PostgreSQL
[ ] Repository layer can create/read/update/delete core entities
[ ] Migration is committed
```

---

# 11. PHASE 4 — Authentication & User Identity

## Objective

Implement secure Google OAuth-based authentication with managed auth, initially expected to use Supabase Auth or an equivalent managed provider.

## Tasks

1. Configure provider-side OAuth.
2. Configure exact redirect URLs.
3. Implement callback/session handling.
4. Establish trusted authenticated principal.
5. Create/synchronize CineRec application user record.
6. Create user identity record.
7. Implement `/users/me`.
8. Enforce application-level ownership.
9. Handle logout and session expiry.

## Security checks

Verify:

```text
[ ] No auth secrets in frontend bundle
[ ] No tokens in localStorage unless explicitly justified by provider architecture
[ ] Secure cookie behavior where cookies are used
[ ] Exact redirect URI allowlist
[ ] No open redirect
[ ] CORS allowlist
[ ] User ID is derived from authenticated principal
[ ] Arbitrary client user_id is ignored/rejected
[ ] Cross-user resource access returns 403/404 as designed
```

## Tests

- first login
- returning user login
- callback failure
- expired session
- logout
- unauthenticated endpoint access
- cross-user access
- malformed auth context

## Completion Gate

An authenticated user can safely access their own application profile, and authorization tests prove they cannot access another user's private state.

---

# 12. PHASE 5 — Movie Domain & TMDB Integration

## Objective

Build a reliable canonical movie catalog and provider adapter.

## Tasks

### Domain

Implement:

```text
Movie
Genre
Keyword
Person
Credit
MovieRelation
Availability
```

### Provider boundary

Create:

```text
MovieDataProvider
TMDBProvider
```

### Ingestion

Implement:

```text
fetch movie
search movie
fetch details
fetch credits
fetch genres
fetch keywords
fetch watch providers where supported
```

### Normalization

Map provider responses to CineRec domain models.

Do not leak raw TMDB response objects through the public API.

## Reliability

Define:

```text
timeout
retry policy
rate-limit handling
cache policy
error mapping
partial response behavior
```

## Tests

Use recorded fixtures/fakes for deterministic CI.

Test:

- successful fetch
- malformed response
- missing fields
- changed provider data
- timeout
- rate limiting
- provider unavailable
- duplicate provider ID
- normalization
- idempotent ingestion

## Completion Gate

A movie can be reliably searched, ingested, normalized, stored, and retrieved through CineRec's own API without frontend knowledge of TMDB internals.

---

# 13. PHASE 6 — Core API & Application Services

## Objective

Implement the `/api/v1` application contract.

## Priority endpoints

```text
GET  /health
GET  /ready
GET  /api/v1/users/me
GET  /api/v1/movies/search
GET  /api/v1/movies/{id}
GET  /api/v1/movies/{id}/similar
GET  /api/v1/movies/{id}/availability
POST /api/v1/conversations
POST /api/v1/conversations/{session_id}/messages
POST /api/v1/recommendations
POST /api/v1/recommendations/{id}/feedback
POST /api/v1/ratings
GET  /api/v1/watchlist
POST /api/v1/watchlist
GET  /api/v1/viewing-history
GET  /api/v1/memories
GET  /api/v1/taste-profile
GET  /api/v1/dashboard
```

Implement only contracts defined in the API specification.

## Layering

Every endpoint should follow:

```text
Route
 ↓
Application Service
 ↓
Domain / Repository
 ↓
Infrastructure
```

## Required API behavior

- typed request validation
- typed responses
- consistent error envelope
- pagination
- request IDs
- authentication
- authorization
- rate limiting where specified
- idempotency where specified

## Tests

For each endpoint:

```text
happy path
validation failure
authentication failure
authorization failure
not found
conflict
dependency failure
pagination
```

## Completion Gate

OpenAPI is coherent with implementation, integration tests pass, and no API route contains substantial raw SQL/business orchestration.

---

# 14. PHASE 7 — Web Shell, Design System & Orb UI

## Objective

Build the application shell and the orb interaction surface before wiring complex AI behavior.

## UI areas

```text
Landing
Auth
Onboarding
Orb
Recommendation Results
Movie Detail
My Cinema
Taste Profile
Watchlist
History
Memory Controls
Settings
Error States
Loading States
```

## Orb implementation

Implement visual state machine:

```text
IDLE
INPUT
PROCESSING
FOLLOW-UP
SEARCHING
SYNTHESIZING
RECOMMENDING
WAITING_FOR_FEEDBACK
REFINING
ERROR
```

The orb's animation state must remain separate from business state.

## Accessibility

Implement from the beginning:

- keyboard input
- focus handling
- semantic controls
- screen-reader labels
- reduced motion
- sufficient contrast
- mobile responsiveness

## Frontend tests

```text
[ ] components render
[ ] state transitions work
[ ] input works with keyboard
[ ] reduced motion works
[ ] mobile layout works
[ ] error states render
[ ] loading states render
```

## Browser verification

Use Playwright for:

```text
landing → auth → authenticated shell → orb
```

## Completion Gate

The product has a functional UI shell with an operational orb state machine, but AI calls may still be mocked behind interfaces.

---

# 15. PHASE 8 — Gemini & Conversation Engine

## Objective

Connect the orb to Gemini through the defined LLM abstraction.

## Architecture

```text
Conversation Service
    ↓
LLMProvider
    ↓
GeminiProvider
    ↓
Gemini Interactions API
```

## Gemini responsibilities

Use Gemini for:

- intent extraction
- conversation
- clarification
- reference resolution
- tool selection
- memory candidate extraction
- explanation generation
- final response synthesis

Do not use Gemini for:

- authorization
- direct SQL
- raw TMDB access
- deterministic filtering
- thousands-item ranking
- persistence decisions

## Structured output

Define schemas for:

```text
Intent
Clarification
RecommendationContext
MemoryCandidate
ToolRequest
ResponseMetadata
```

Validate all model output.

## Prompt design

Version:

```text
system prompt
conversation prompt templates
structured-output schemas
```

Do not hardcode unversioned prompt text throughout the codebase.

## Tool architecture

Tools must be:

```text
typed
allowlisted
authorized
bounded
observable
```

## Failure handling

Handle:

- timeout
- model error
- malformed structured output
- tool denial
- provider rate limit
- stream interruption
- incomplete response

## Tests

Mock/fake LLM provider for deterministic tests.

Test:

```text
normal conversation
clarification
intent extraction
malformed model output
prompt injection
forbidden tool request
provider outage
retry
streaming interruption
```

## Completion Gate

The orb can conduct a real conversation, produce validated structured intent, and request recommendation work through the application rather than inventing recommendations itself.

---

# 16. PHASE 9 — Memory System

## Objective

Implement controlled long-term personalization memory.

## Memory hierarchy

```text
Conversation History
 ↓
Session Context
 ↓
Explicit Memory
 ↓
Inferred Memory
 ↓
Taste Profile
 ↓
User Embedding
```

## Tasks

1. Implement memory schema.
2. Implement evidence records.
3. Implement candidate extraction.
4. Implement validation.
5. Implement confidence.
6. Implement source/provenance.
7. Implement status lifecycle.
8. Implement conflict resolution.
9. Implement deduplication.
10. Implement user correction.
11. Implement deletion.
12. Implement retrieval scoping.

## Required memory states

```text
CANDIDATE
VALIDATED
ACTIVE
UPDATED
SUPERSEDED
DISABLED
DELETED
```

## Authority order

```text
Explicit user correction
    >
Explicit preference
    >
High-confidence inference
    >
Weak inference
    >
Weak behavioral signal
```

## Tests

Test:

- explicit preference
- inferred preference
- contradiction
- correction
- duplicate memory
- memory expiration
- deletion
- unauthorized retrieval
- prompt-injection content inside memory
- no conversion of search/click into liking without evidence

## Completion Gate

The orb can use controlled long-term memory without misrepresenting inferred preferences as facts the user explicitly stated.

---

# 17. PHASE 10 — Interaction & Feedback Infrastructure

## Objective

Capture the behavioral signals required for personalization and evaluation.

## Interaction types

At minimum support:

```text
search
movie_view
movie_click
recommendation_impression
recommendation_selection
skip
like
dislike
watchlist_add
watchlist_remove
rating
watch_complete
```

The exact event taxonomy must remain consistent across frontend, API, database, and ML.

## Rules

Raw interactions should be append-oriented.

Do not overwrite historical events merely to maintain current state.

Separate:

```text
raw events
```

from:

```text
current derived state
```

## Required metadata

Where appropriate capture:

```text
user_id
movie_id
session_id
request_id
event_type
position / rank
surface
model version
timestamp
metadata
```

## Tests

- event persistence
- duplicate delivery
- idempotency
- malformed event
- ownership
- ordering
- concurrent writes
- deletion

## Completion Gate

Core behavioral signals are reliably captured in a way that can later support recommendation training and attribution.

---

# 18. PHASE 11 — Recommendation Baselines

## Objective

Create a working recommender before implementing sophisticated ML.

This establishes measurable baselines and prevents the project from becoming an untestable AI demo.

## Baselines

Implement:

### Popularity

Time-windowed and globally scoped popularity as appropriate.

### Metadata similarity

Use:

```text
genre
keywords
tags
selected metadata
```

### Seen-item exclusion

Do not recommend explicitly excluded or already-consumed items where policy requires exclusion.

### Rule-based personalization

Combine:

```text
explicit preferences
current request context
simple historical signals
```

## Evaluation harness

Implement offline evaluation infrastructure before advanced ranking.

Metrics:

```text
Precision@K
Recall@K
NDCG@K
MAP@K
Hit Rate
Coverage
Diversity
Novelty
```

## Temporal split

Evaluation must avoid future-to-past leakage.

## Completion Gate

A deterministic baseline produces measurable recommendations and the project has a reproducible offline evaluation pipeline.

This baseline becomes the benchmark for every later recommender change.

---

# 19. PHASE 12 — pgvector & Semantic Retrieval

## Objective

Implement the vector infrastructure defined by ADR-003.

## Tasks

1. Enable pgvector.
2. Implement embedding provider abstraction.
3. Define canonical movie embedding input.
4. Define user embedding input.
5. Persist model/version metadata.
6. Validate embedding dimension.
7. Persist source hash/version.
8. Implement vector repository.
9. Implement exact search.
10. Implement HNSW approximate search.
11. Implement filtered vector retrieval.
12. Implement stale detection.
13. Implement re-embedding pipeline.

## Initial defaults

```text
Vector Store: PostgreSQL + pgvector
Primary type: vector
Initial metric: cosine distance
Initial ANN: HNSW
```

These remain benchmark-driven defaults.

## Required vector boundaries

```text
Recommendation Engine
 ↓
Vector Retrieval Interface
 ↓
pgvector Adapter
```

## Exact search requirement

Keep exact search available for:

- ground-truth comparison
- debugging
- small datasets
- ANN recall measurement

## Benchmark

Measure:

```text
exact recall
p50 latency
p95 latency
p99 latency
throughput
memory
index size
build time
```

Test filtered vector queries because CineRec uses structured filtering.

## Completion Gate

Vector search is measurable, versioned, authorized, testable, and integrated as one candidate-generation source rather than replacing the recommendation engine.

---

# 20. PHASE 13 — Collaborative Filtering

## Objective

Introduce behavioral recommendation signals.

## Implementation order

Start with:

```text
item-item CF
```

Then evaluate:

```text
user-user CF
matrix factorization
implicit-feedback models
```

Do not implement every algorithm simultaneously.

## Signal policy

Distinguish:

```text
explicit ratings
likes
likes inferred from behavior
clicks
views
watch completion
watchlist
skips
```

Do not automatically interpret every non-interaction as negative feedback.

## Training data

Implement:

```text
raw events
 ↓
feature extraction
 ↓
training dataset
 ↓
model
 ↓
evaluation
```

## Leakage prevention

Use temporal evaluation.

Do not train on data that occurs after the evaluation target.

## Completion Gate

Collaborative candidate generation measurably improves over the recommendation baseline on at least some relevant offline metrics without violating temporal evaluation rules.

If it does not improve quality, keep the baseline and investigate rather than adding more complexity.

---

# 21. PHASE 14 — Hybrid Recommendation Engine

## Objective

Combine candidate sources into CineRec's production recommendation pipeline.

## Architecture

```text
Context Builder
      ↓
Candidate Generators
 ├── Popularity
 ├── Metadata
 ├── Semantic / pgvector
 ├── Item-item CF
 └── Other validated sources
      ↓
Candidate Union
      ↓
Hard Filters
      ↓
Feature Builder
      ↓
Ranker
      ↓
Diversity / Exploration
      ↓
Recommendation Set
```

## Candidate provenance

Every candidate should retain internal provenance such as:

```text
COLLABORATIVE
SEMANTIC
POPULAR
METADATA
DISCOVERY
HYBRID
```

## Hard filters

Explicit user constraints must be enforced before soft scoring.

Examples:

```text
runtime
language
genre exclusions
availability constraints
already watched
explicit dislikes
```

## Ranking

Initial ranking may combine:

```text
CF score
semantic score
popularity
context relevance
novelty
exploration
```

The exact formula is evaluation-driven.

## Diversity

Apply diversification after candidate ranking where required.

Possible methods include:

```text
MMR
category quotas
franchise deduplication
creator concentration limits
```

Do not blindly apply all methods.

## Explanations

Explanation metadata must correspond to actual recommendation provenance.

The LLM may verbalize the explanation but may not invent a reason that was not supported by the system.

## Completion Gate

The engine produces 3–5 personalized candidates with:

```text
valid provenance
hard constraints respected
stable ordering
measurable ranking behavior
repeat suppression
reasonable diversity
```

and the complete pipeline is covered by automated tests.

---

# 22. PHASE 15 — My Cinema / Dashboard

## Objective

Turn personalization into a visible, useful product surface.

## Features

Implement:

```text
watched movies
watchlist
ratings
recommendation history
recent activity
taste profile
movie DNA / taste visualization
memory controls
personalization controls
```

## Rules

Derived visualizations must not become the only representation of user data.

For example:

```text
Taste Profile
```

must be reconstructible from authoritative data where appropriate.

## Tests

- empty state
- large history
- pagination
- filters
- mobile
- accessibility
- user isolation
- stale/derived data states

## Completion Gate

An authenticated user can meaningfully inspect and control their cinematic profile beyond the chat interface.

---

# 23. PHASE 16 — Async Processing, Redis & Celery

## Objective

Move expensive or non-critical work out of synchronous HTTP requests.

## Initial background workloads

```text
embedding generation
movie ingestion refresh
user embedding refresh
taste profile recomputation
recommendation feature aggregation
analytics aggregation
maintenance jobs
```

## Celery rules

Tasks must be:

```text
idempotent
retry-aware
observable
bounded
safe under duplicate delivery
```

## Redis rules

Redis may be used for:

```text
cache
Celery broker
rate limiting
ephemeral coordination
```

Never make Redis the only durable copy of user state.

## Required failure testing

Kill Redis.

Kill a worker.

Restart a worker during a task.

Duplicate a task.

Verify:

```text
no corrupted durable state
no silent data loss
no unbounded retry loop
```

## Completion Gate

Expensive work no longer blocks normal HTTP execution unnecessarily, and task failure/retry behavior is deterministic enough for production operation.

---

# 24. PHASE 17 — Observability & Reliability

## Objective

Make the system measurable before production scaling.

## Implement

```text
OpenTelemetry
structured JSON logs
Prometheus metrics
Grafana dashboards where deployed
```

## Traces

Propagate correlation through:

```text
web
 ↓
API
 ↓
PostgreSQL
Redis
Gemini
TMDB
Celery
Recommendation Engine
```

## Required metrics

### Application

```text
request rate
error rate
latency
status code distribution
```

### Database

```text
query latency
pool utilization
connections
lock contention
slow queries
```

### Redis

```text
hit rate
latency
memory
errors
```

### Celery

```text
queue depth
job latency
failures
retries
```

### Gemini

```text
request count
latency
input/output usage
failures
retry count
```

### TMDB

```text
request count
latency
rate limits
errors
cache effectiveness
```

### Recommendation

```text
candidate counts
empty-result rate
ranking latency
feedback
coverage
diversity
```

## Privacy

Redact secrets and unnecessary private content.

## Completion Gate

The team can diagnose at least these classes of failure from telemetry:

```text
API failure
DB bottleneck
provider outage
queue backlog
LLM latency
recommendation degradation
```

---

# 25. PHASE 18 — Security Hardening

## Objective

Complete security review against the dedicated security architecture.

## Areas

### Authentication

- OAuth flow
- session lifecycle
- cookie security
- redirect security

### Authorization

Test:

```text
BOLA
BFLA
property-level authorization
cross-user data access
```

### API

Test:

```text
rate limiting
CSRF where applicable
CORS
input validation
mass assignment
request size limits
```

### Database

Test:

```text
SQL injection
privilege boundaries
connection security
migration safety
```

### LLM

Test:

```text
prompt injection
tool abuse
untrusted content
memory injection
indirect injection
```

### SSRF

Ensure provider tools cannot be turned into arbitrary URL fetchers.

### Secrets

Scan repository and build artifacts for credentials.

## Required tooling

Use appropriate automated and manual security checks compatible with the project.

## Completion Gate

No critical or high-severity unresolved security issue remains for the production scope.

---

# 26. PHASE 19 — Performance, Load & Scale Validation

## Objective

Measure whether the initial architecture meets expected workloads.

Do not introduce new infrastructure before this phase produces evidence.

## Workloads

Test:

```text
movie search
movie detail
recommendation request
conversation turn
watchlist mutation
rating mutation
memory retrieval
vector retrieval
```

## Load dimensions

Test varying:

```text
concurrency
movie-catalog size
user count
interaction volume
candidate count
embedding count
```

## Metrics

Record:

```text
p50
p95
p99
requests/sec
CPU
memory
database connections
database CPU
Redis utilization
queue latency
LLM latency
TMDB latency
vector latency
```

## N+1 detection

Use query logging or instrumentation to detect pathological query counts.

## Performance gates

Define explicit target thresholds before interpreting results.

Do not call the system "optimized" without measurements.

## Completion Gate

Observed bottlenecks are documented, and any optimization introduced can be tied to a measured problem.

If additional infrastructure is needed, create an ADR before adding it.

---

# 27. PHASE 20 — End-to-End Hardening

## Objective

Exercise the system as a complete product rather than independent modules.

## Critical golden paths

### Golden Path 1 — First-time user

```text
landing
 → OAuth
 → onboarding
 → seed preferences
 → orb
 → first recommendation
```

### Golden Path 2 — Conversational refinement

```text
recommend
 → "too serious"
 → refined request
 → new candidates
```

### Golden Path 3 — Feedback loop

```text
recommendation
 → like/dislike/rating
 → interaction persisted
 → profile update
 → future recommendation changes
```

### Golden Path 4 — Watchlist

```text
movie
 → add watchlist
 → dashboard
 → remove watchlist
```

### Golden Path 5 — Memory

```text
conversation
 → memory candidate
 → validation
 → future retrieval
 → user correction
 → corrected behavior
```

### Golden Path 6 — Provider degradation

Simulate:

```text
Gemini failure
TMDB failure
Redis failure
Celery failure
vector retrieval failure
```

Verify safe degradation.

## Browser testing

Playwright must cover the primary user flows.

## Completion Gate

The full product loop works under both normal and degraded conditions.

---

# 28. PHASE 21 — Production Deployment

## Objective

Deploy the system using the infrastructure architecture defined in `14-deployment.md`.

## Initial production topology

```text
Next.js
   ↓
FastAPI API
   ↓
Managed PostgreSQL
   +
Managed/private Redis
   +
Celery Worker
   +
Gemini
   +
TMDB
```

## Tasks

### Containers

- reproducible images
- non-root runtime where practical
- health checks
- minimal runtime dependencies

### Configuration

- production environment variables
- secret management
- no secret baked into image

### Database

- production migrations
- backup policy
- restore procedure
- connection pool configuration

### CI/CD

Pipeline:

```text
push
 ↓
format/lint/typecheck
 ↓
unit tests
 ↓
integration tests
 ↓
build
 ↓
container build
 ↓
staging
 ↓
smoke tests
 ↓
production
```

## Deployment strategy

Prefer:

```text
build once
promote same artifact
```

## Rollback

Document:

```text
application rollback
database rollback / forward-fix strategy
migration recovery
provider configuration rollback
```

## Completion Gate

A new version can be deployed and rolled back through documented, repeatable procedures.

---

# 29. PHASE 22 — Release Validation & Operational Readiness

## Objective

Perform the final release gate before treating CineRec as production-ready.

## Application checks

```text
[ ] Authentication works
[ ] OAuth callbacks work
[ ] Authorization isolation tested
[ ] Movie search works
[ ] Movie detail works
[ ] Orb works
[ ] Conversation works
[ ] Recommendations work
[ ] Refinement works
[ ] Feedback persists
[ ] Watchlist works
[ ] History works
[ ] Dashboard works
[ ] Memory controls work
```

## Infrastructure checks

```text
[ ] PostgreSQL healthy
[ ] pgvector healthy
[ ] Redis healthy
[ ] Celery healthy
[ ] API readiness works
[ ] Web build works
[ ] Health monitoring works
```

## Observability checks

```text
[ ] logs structured
[ ] traces correlated
[ ] metrics emitted
[ ] dashboards available
[ ] alerts configured
```

## Security checks

```text
[ ] secrets scan passes
[ ] dependency audit reviewed
[ ] authorization regression suite passes
[ ] injection tests pass
[ ] provider tool restrictions verified
```

## Recovery checks

```text
[ ] backup exists
[ ] backup restore tested
[ ] rollback documented
[ ] incident runbook exists
```

## Completion Gate

Release is allowed only when no production-blocking gate remains unresolved.

---

# 30. Phase-Gate Rule

Every phase must produce a written completion record.

Use:

```text
PHASE-N-COMPLETION.md
```

or the project's preferred release/engineering record.

Each record should contain:

```text
Phase
Date
Implemented
Tests Run
Tests Passed
Known Issues
Deferred Work
Architecture Changes
Migration Changes
Security Findings
Performance Findings
Final Decision
```

The decision must be one of:

```text
PASS
PASS WITH EXPLICIT DEFERRED ITEMS
BLOCKED
```

Never use vague status such as:

```text
mostly done
looks good
basically complete
```

---

# 31. Phase Exit Standard

A phase may advance only when:

```text
1. Functional work is complete for the phase scope.
2. Required tests pass.
3. Required static checks pass.
4. Required integration checks pass.
5. Security requirements for the phase pass.
6. Documentation is synchronized.
7. No critical known defect remains hidden.
8. The next phase has a stable dependency boundary.
```

A phase must be blocked when its output is too unstable to safely become the next phase's input.

---

# 32. Required Testing Matrix

The project should maintain testing coverage across these dimensions.

| Layer | Required Testing |
|---|---|
| TypeScript | typecheck, unit tests |
| React/UI | component tests, accessibility checks |
| Browser | Playwright E2E |
| FastAPI | route/API tests |
| Domain | unit tests |
| Repositories | PostgreSQL integration tests |
| DB schema | migration tests |
| Redis | integration tests where behavior matters |
| Celery | task tests, retry/idempotency tests |
| TMDB | fixture/contract tests |
| Gemini | fake provider + structured-output tests |
| Memory | lifecycle/conflict/security tests |
| Recommendation | offline metrics + deterministic tests |
| CF | leakage-safe evaluation |
| Vector | exact-vs-ANN recall tests |
| Security | authz/injection/SSRF/prompt-injection tests |
| Performance | load/stress/spike tests |
| Deployment | smoke tests |

---

# 33. Regression Test Policy

Whenever a production bug is fixed:

```text
Bug
 ↓
Regression test
 ↓
Fix
 ↓
Full relevant test suite
```

The regression test should fail against the old implementation and pass against the fixed implementation whenever practical.

---

# 34. Test Data Policy

Tests must use deterministic fixtures or factories where reproducibility matters.

Do not rely on:

- live TMDB responses
- live Gemini behavior
- current external availability
- production data
- developer-specific local database state

unless the test is explicitly classified as an external/integration smoke test.

---

# 35. Data Migration Verification

Every production migration must be evaluated for:

```text
compatibility
locking
runtime
rollback/forward-fix
backfill cost
index creation impact
application-version compatibility
```

Large migrations should prefer:

```text
expand
 ↓
backfill
 ↓
validate
 ↓
switch
 ↓
contract
```

---

# 36. Recommendation Release Policy

Recommendation changes must not be judged solely through code review.

Before release, capture:

```text
baseline metrics
candidate metrics
ranking metrics
diversity
coverage
novelty
latency
failure rate
```

For meaningful model changes, retain:

```text
model version
training data version
feature version
embedding version
ranker version
experiment configuration
```

Rollback must be possible by model/ranker version rather than requiring a code redeploy where practical.

---

# 37. LLM Release Policy

Every meaningful LLM behavior change should identify:

```text
model
prompt version
schema version
tool schema
retrieval context rules
```

Use a controlled evaluation set covering:

- natural requests
- ambiguity
- corrections
- references such as "the second one"
- seen movies
- explicit constraints
- prompt injection
- unsupported claims
- tool misuse

Do not ship an LLM behavior change merely because one manual conversation looked good.

---

# 38. Embedding Release Policy

Every embedding model change requires:

```text
offline similarity evaluation
recommendation evaluation
dimension validation
version metadata
migration plan
backfill plan
rollback / coexistence strategy
```

Do not silently overwrite the existing production embedding space.

---

# 39. Cache Release Policy

Every cache change must document:

```text
key
value
TTL
invalidation
freshness
failure behavior
privacy scope
```

Before enabling a personalized cache, verify that one user's data cannot collide with another user's cache key.

---

# 40. API Change Policy

For every API change:

```text
contract
 ↓
tests
 ↓
implementation
 ↓
frontend integration
 ↓
documentation
```

Breaking changes require:

- explicit migration strategy
- compatibility period where needed
- versioning or contract transition
- ADR when architectural

---

# 41. Database Query Review Checklist

Before merging a significant query, ask:

```text
[ ] Is the query bounded?
[ ] Is pagination needed?
[ ] Is an index available?
[ ] Does the query produce N+1 behavior?
[ ] Is filtering pushed into SQL?
[ ] Does it return only needed columns?
[ ] Is a join cheaper than repeated requests?
[ ] Is the query correct under concurrency?
[ ] Has it been tested against realistic data?
```

For important queries, capture and inspect execution plans.

---

# 42. Security Review Checklist

Before each production release:

```text
[ ] no secrets committed
[ ] no debug endpoints exposed
[ ] authorization tests pass
[ ] CORS is restricted
[ ] CSRF assumptions verified
[ ] SQL uses parameterization
[ ] SSRF controls verified
[ ] LLM tools are allowlisted
[ ] model cannot access arbitrary SQL/shell
[ ] user-owned resources are isolated
[ ] logs do not leak secrets
[ ] private memory is appropriately protected
[ ] deletion semantics are verified
```

---

# 43. Performance Review Checklist

Before major releases:

```text
[ ] p95 API latency measured
[ ] p99 latency measured for critical endpoints
[ ] DB connections remain bounded
[ ] no major N+1 regressions
[ ] recommendation latency measured
[ ] vector search latency measured
[ ] LLM latency measured
[ ] queue backlog behavior understood
[ ] cache hit rate measured where relevant
[ ] frontend bundle checked
```

---

# 44. Failure-Injection Checklist

The system should eventually simulate:

```text
PostgreSQL unavailable
Redis unavailable
Celery unavailable
TMDB unavailable
Gemini unavailable
Gemini malformed output
vector retrieval unavailable
network timeout
slow database
worker crash
duplicate task delivery
expired auth
```

Expected behavior must be:

```text
safe
observable
bounded
recoverable
```

---

# 45. Data Integrity Invariants

The following invariants must always hold.

## Identity

```text
Every authenticated application user maps to one valid CineRec user identity.
```

## Ownership

```text
A user cannot access another user's private resources.
```

## Ratings

```text
Current rating state and rating history semantics remain internally consistent.
```

## Watchlist

```text
Duplicate logical watchlist membership is prevented according to domain rules.
```

## Embeddings

```text
Embedding dimension matches declared model metadata.
```

## Memory

```text
Disabled/deleted memories are not returned as active memory context.
```

## Recommendations

```text
Hard user constraints are never violated by soft ranking signals.
```

## External data

```text
Provider failures are never converted into fabricated successful data.
```

## Persistence

```text
Successful user mutations are durably represented in PostgreSQL.
```

---

# 46. Recommendation Invariants

The recommendation engine must preserve these rules:

```text
1. Explicit user constraints override soft similarity.
2. Explicit correction overrides weak inference.
3. Seen/excluded items are handled according to product policy.
4. Candidate generation and final ranking remain distinct.
5. Vector retrieval does not equal final recommendation ordering.
6. LLM explanations must correspond to actual system behavior.
7. Historical interactions are not silently rewritten as current state.
8. Recommendation outputs remain attributable to versions/configuration.
```

---

# 47. Conversation Invariants

The orb must preserve:

```text
1. Current session context is distinct from long-term memory.
2. Temporary requests do not automatically become permanent memories.
3. User corrections take precedence.
4. The system asks only useful clarifying questions.
5. LLM output is validated before entering business logic.
6. Authoritative movie facts come from application/provider data.
7. The LLM does not become an authorization layer.
8. The orb remains usable under reduced motion/accessibility settings.
```

---

# 48. Memory Invariants

```text
1. Memory has provenance.
2. Memory has an authority level.
3. Memory can be corrected.
4. Memory can be disabled/deleted.
5. Memory retrieval is scoped.
6. Weak inference is not presented as explicit user instruction.
7. Memory content is treated as untrusted data when inserted into prompts.
```

---

# 49. Operational Runbooks Required Before Production

Create runbooks for:

```text
service restart
API outage
PostgreSQL outage
Redis outage
Celery backlog
TMDB outage
Gemini outage
migration failure
bad deployment
rollback
backup restore
stale embeddings
embedding model migration
recommendation regression
security incident
user data deletion incident
```

Each runbook should include:

```text
symptoms
checks
commands / actions
expected signals
recovery
verification
rollback / escalation
```

---

# 50. Production Readiness Checklist

The production release must satisfy all applicable checks.

## Code

```text
[ ] clean build
[ ] clean lint
[ ] clean typecheck
[ ] relevant tests pass
[ ] no known blocker bugs
```

## Database

```text
[ ] schema migration tested
[ ] backups enabled
[ ] restore tested
[ ] pooling configured
[ ] indexes reviewed
```

## Security

```text
[ ] authz tests pass
[ ] secrets protected
[ ] headers configured
[ ] CORS restricted
[ ] injection tests pass
[ ] LLM tool boundary tested
```

## AI

```text
[ ] model/version tracked
[ ] prompts versioned
[ ] structured output validated
[ ] provider failures handled
[ ] cost controls present
```

## Recommendation

```text
[ ] baseline exists
[ ] hybrid pipeline tested
[ ] offline metrics tracked
[ ] candidate provenance exists
[ ] fallback path works
```

## Operations

```text
[ ] logging
[ ] metrics
[ ] tracing
[ ] alerts
[ ] runbooks
```

## UX

```text
[ ] mobile
[ ] keyboard
[ ] screen-reader semantics
[ ] reduced motion
[ ] loading states
[ ] error states
```

---

# 51. Definition of Production-Grade

CineRec should not be called **production-grade** merely because it is deployed.

The system qualifies as production-grade when it demonstrates:

```text
Correctness
+ Security
+ Testability
+ Observability
+ Recoverability
+ Reproducibility
+ Performance awareness
+ Explicit architecture
+ Safe failure behavior
```

A deployed but unobservable or unrecoverable system is not production-grade.

---

# 52. Definition of Industry-Grade Engineering

For CineRec, "industry-grade" means:

```text
clear architecture
strong interfaces
explicit contracts
real database integration tests
security-first authorization
versioned AI behavior
versioned ML artifacts
measurable recommendation quality
reproducible experiments
structured observability
safe migrations
bounded retries
idempotent background jobs
load-tested critical paths
documented rollback
```

It does **not** mean:

```text
Kubernetes
Kafka
microservices
multiple databases
custom infrastructure everywhere
```

Those are implementation options, not definitions of engineering quality.

---

# 53. When to Add New Infrastructure

Before introducing a new infrastructure component, answer all of these:

```text
1. What specific problem exists?
2. What metric demonstrates the problem?
3. Why can the existing architecture not solve it?
4. What operational cost will the new component introduce?
5. What new failure mode will it introduce?
6. How will it be monitored?
7. How will it be backed up/recovered if necessary?
8. How will local development work?
9. How will it be tested?
10. What is the removal/migration path?
```

If these answers are not clear, do not introduce the component.

Create an ADR first when the decision is architectural.

---

# 54. When to Refactor

Refactor when:

- a boundary has become unclear
- duplication produces correctness risk
- performance data identifies a bottleneck
- a module has too many responsibilities
- tests are becoming difficult because of hidden coupling
- provider-specific behavior leaks into the domain

Do not refactor solely because another pattern looks cleaner.

---

# 55. When to Stop a Phase

Stop and repair the current phase when:

```text
critical tests fail
architecture is violated
a migration is unsafe
a security boundary is unclear
persistent data integrity is uncertain
observability is insufficient for the risk level
```

Do not continue building dependent functionality on top of unstable foundations merely to maintain project momentum.

---

# 56. Change Control

Any significant architecture change requires:

```text
problem statement
alternatives
tradeoffs
ADR
implementation
migration plan
verification
```

Any significant schema change requires:

```text
SQLAlchemy change
Alembic migration
integration tests
compatibility assessment
```

Any significant recommendation change requires:

```text
algorithm/config change
evaluation
versioning
attribution
```

Any significant LLM change requires:

```text
model/prompt/schema change
evaluation
failure testing
```

---

# 57. Agent Behavior During Implementation

Antigravity should operate as an engineering agent rather than a code generator.

For each meaningful change it should:

1. inspect relevant code
2. identify the owning module
3. read governing documentation
4. determine dependencies
5. make a small implementation plan
6. implement
7. run focused tests
8. run broader tests
9. inspect failures
10. fix root causes
11. update documentation
12. review the resulting diff

The agent should avoid large speculative rewrites.

---

# 58. Agent Self-Review Questions

Before declaring a task complete, the agent must answer:

```text
What changed?
Why does it belong in this layer?
What contract does it implement?
What can fail?
How is failure handled?
What tests prove correctness?
What security boundary applies?
What data does this own?
What external dependencies exist?
What happens if they fail?
Did the implementation change architecture?
Did the implementation change the DB schema?
Did documentation remain accurate?
```

If any answer is unclear for a significant change, the task is not ready to be declared complete.

---

# 59. Suggested Commit Strategy

Prefer coherent commits such as:

```text
chore: establish repository tooling
feat: add postgres persistence foundation
feat: implement google oauth user identity
feat: add tmdb movie provider
feat: implement movie search api
feat: add orb conversation state machine
feat: integrate gemini provider
feat: add persistent memory lifecycle
feat: add interaction event pipeline
feat: add popularity recommender baseline
feat: add pgvector semantic retrieval
feat: add item-item collaborative filtering
feat: add hybrid recommendation ranking
feat: add my cinema dashboard
chore: add celery background processing
chore: add observability instrumentation
security: harden authorization boundaries
perf: optimize recommendation retrieval
ops: add production deployment pipeline
```

Avoid mixed commits that combine unrelated architectural changes.

---

# 60. Final End-to-End Verification Flow

Before the first serious production release, run the following complete sequence:

```text
1. Fresh clone
2. Configure environment
3. Start Docker infrastructure
4. Run migrations
5. Seed controlled development data
6. Start web + API + worker
7. Run static checks
8. Run unit tests
9. Run integration tests
10. Run API tests
11. Run security tests
12. Run recommendation evaluation
13. Run vector benchmark
14. Run E2E browser tests
15. Run failure-injection tests
16. Run load tests
17. Verify telemetry
18. Verify backup/restore
19. Deploy to staging
20. Run staging smoke tests
21. Verify rollback
22. Promote same artifact to production
23. Run production smoke tests
24. Verify alerts
```

No manual happy-path check should substitute for this sequence.

---

# 61. Final Architecture Guardrails

The finished initial CineRec implementation should preserve these boundaries:

```text
                 ┌────────────────────┐
                 │       Next.js      │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │      FastAPI       │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ Application Layer  │
                 └─────────┬──────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
       Conversation     Memory      Recommendation
            │              │              │
            │              │      ┌───────┼────────┐
            │              │      ▼       ▼        ▼
            │              │     CF    pgvector  Popularity
            │              │      └───────┼────────┘
            │              │              ▼
            │              │          Rank / Diversify
            │              │
            └──────────────┼──────────────┘
                           ▼
                  PostgreSQL Source
                       of Truth
                    ┌──────┴──────┐
                    ▼             ▼
                 pgvector       Redis
                                /Celery
```

Provider boundaries remain:

```text
TMDB  ← MovieDataProvider
Gemini ← LLMProvider
```

---

# 62. Final Completion Standard

CineRec is considered fully implemented only when the system can reliably execute this end-to-end loop:

```text
User signs in
      ↓
User establishes initial taste
      ↓
User speaks/types to the orb
      ↓
Gemini understands the request
      ↓
Structured intent is validated
      ↓
Current session + long-term personalization are assembled
      ↓
Recommendation engine generates candidates
      ↓
Collaborative + semantic + metadata + popularity signals combine
      ↓
Hard constraints are enforced
      ↓
Ranking + diversity are applied
      ↓
3–5 useful recommendations are returned
      ↓
LLM explains them honestly
      ↓
User clicks / watches / likes / dislikes / rates
      ↓
Interaction is persisted
      ↓
Derived personalization updates asynchronously
      ↓
Future recommendations improve
      ↓
User can inspect and control their cinematic profile
```

And the same system must continue to behave safely when:

```text
Gemini fails
TMDB fails
Redis fails
Celery fails
vector retrieval fails
requests are duplicated
users act concurrently
data is deleted
a deployment fails
```

---

# 63. Final Principle

> **Build in dependency order. Make every layer testable. Make every important decision explicit. Keep PostgreSQL authoritative, AI bounded, recommendation logic deterministic where possible, derived state rebuildable, and infrastructure simple until measurements prove that more complexity is necessary. Never advance on unverified assumptions.**

The implementation is successful when CineRec is not merely a functioning application, but a system that another engineer—or another AI agent—can safely inspect, test, debug, operate, and evolve.
