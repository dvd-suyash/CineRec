# ADR-001 — Modular Monolith

**Status:** Accepted
**Date:** 2026-09-28
**Decision owners:** CineRec Engineering
**Scope:** Overall backend architecture
**Related documents:**
`03-system-architecture.md`
`04-database-design.md`
`05-api-contract.md`
`06-recommendation-system.md`
`07-orb-conversation-design.md`
`08-memory-system.md`
`09-tmdb-integration.md`
`10-gemini-integration.md`
`11-security.md`
`12-testing-strategy.md`
`13-observability.md`
`14-deployment.md`

---

# 1. Decision

CineRec will initially be implemented as a **modular monolith**.

The application will have:

```text
one primary backend codebase
+
explicit domain/application/infrastructure boundaries
+
multiple logical modules
+
separately deployable runtime processes where useful
```

The initial runtime may contain:

```text
FastAPI API
Celery worker
```

but these processes will share the same repository and core application modules.

The architecture is intentionally designed so that components can later be extracted into separate services when measurable requirements justify doing so.

---

# 2. Context

CineRec contains several technically distinct responsibilities:

```text
authentication
movie catalog
TMDB integration
conversation orchestration
Gemini integration
memory
recommendation generation
collaborative filtering
semantic retrieval
ML inference
watchlists
ratings
viewing history
background jobs
observability
```

A natural reaction is to turn each responsibility into a microservice.

That is not the correct initial architecture.

At the beginning of the project:

```text
team size
≈ very small

traffic
≈ unknown / low

data volume
≈ manageable

deployment complexity
≈ significant relative cost

service-to-service traffic
≈ unnecessary

operational maturity
≈ developing
```

The project therefore needs strong architectural boundaries without paying the operational cost of distributed systems before they are necessary.

---

# 3. Problem

A microservice-first implementation would introduce:

```text
network calls between internal services
service discovery
distributed tracing requirements
multiple deployment pipelines
multiple runtime failures
distributed transactions
service authentication
API versioning between internal services
more infrastructure
more operational configuration
more debugging complexity
```

before CineRec has evidence that these are necessary.

At the opposite extreme, a poorly structured monolith could create:

```text
one giant application module
cross-module database access
business logic in API routes
provider-specific code everywhere
LLM code inside domain logic
recommendation logic mixed with controllers
```

That would create a monolith that is difficult to evolve.

The chosen architecture must therefore achieve both:

```text
low operational complexity
+
strong internal separation
```

---

# 4. Decision Drivers

The decision is driven by:

```text
1. Low initial infrastructure cost
2. Small engineering team
3. Fast development
4. Strong testability
5. Clear domain boundaries
6. Low operational burden
7. Simple local development
8. Simple deployment
9. Strong database consistency
10. Independent background processing
11. Future horizontal scaling
12. Future service extraction
13. Minimal premature infrastructure
14. Good developer experience
```

---

# 5. Chosen Architecture

The backend will use layered modular architecture:

```text id="5rj2s8"
                    API
                     │
                     ▼
            Application Services
                     │
                     ▼
                 Domain
                     │
                     ▼
             Interfaces / Ports
                     │
                     ▼
              Infrastructure
```

With domain modules:

```text id="a8m2pw"
auth
user
movie
conversation
memory
recommendation
rating
watchlist
history
personalization
```

and infrastructure modules:

```text id="nz7x4q"
postgres
redis
tmdb
gemini
celery
observability
```

---

# 6. Repository Structure

The canonical backend structure is:

```text
apps/api/app/
├── api/
├── application/
│   ├── auth/
│   ├── movie/
│   ├── conversation/
│   ├── recommendation/
│   ├── memory/
│   ├── watchlist/
│   ├── rating/
│   ├── history/
│   └── personalization/
│
├── domain/
│   ├── auth/
│   ├── movie/
│   ├── conversation/
│   ├── recommendation/
│   ├── memory/
│   ├── watchlist/
│   ├── rating/
│   └── history/
│
├── infrastructure/
│   ├── db/
│   ├── cache/
│   ├── llm/
│   │   └── gemini/
│   ├── providers/
│   │   └── tmdb/
│   ├── workers/
│   └── observability/
│
└── main.py
```

The exact directory names may evolve, but the conceptual boundaries are mandatory.

---

# 7. Module Ownership

Each domain module owns its business rules.

Example:

```text id="v7m1p3"
Recommendation
→ candidate generation
→ ranking
→ diversity

Memory
→ memory lifecycle
→ authority
→ conflict resolution

Watchlist
→ add/remove semantics

Conversation
→ session state
→ message orchestration
```

A module must not casually implement another module's business logic.

---

# 8. Dependency Rule

Dependencies should flow inward:

```text id="q4k8x6"
API
↓
Application
↓
Domain
```

Infrastructure implements interfaces required by application/domain layers.

Domain code must not directly import:

```text id="m0w5vb"
FastAPI
SQLAlchemy session
Redis client
Gemini SDK
TMDB SDK/client
Celery
```

---

# 9. Provider Abstraction

External providers are isolated behind interfaces.

Examples:

```python id="x6e2m4"
MovieDataProvider
LLMProvider
```

Concrete implementations:

```text id="k4c7m8"
TMDBMovieDataProvider
GeminiProvider
```

This allows provider replacement without changing domain logic.

---

# 10. Database Boundary

PostgreSQL is the durable application database.

Repositories isolate persistence details:

```text id="z9w3q2"
Application Service
→ Repository Interface
→ SQLAlchemy Repository
→ PostgreSQL
```

The API layer must not contain arbitrary SQL.

---

# 11. Redis Boundary

Redis is infrastructure.

It provides:

```text id="h5p7v1"
cache
locks
rate limiting
Celery broker
ephemeral coordination
```

It does not become an application domain boundary.

---

# 12. LLM Boundary

Gemini is accessed only through:

```text id="u3n9q5"
LLMProvider
```

The domain must not depend on:

```text id="c7k2x8"
google.genai
Gemini model IDs
Gemini-specific response objects
Gemini SDK exceptions
```

---

# 13. TMDB Boundary

TMDB is accessed only through:

```text id="r4m6x7"
MovieDataProvider
```

The core movie domain uses CineRec entities and provider mappings rather than raw TMDB responses.

---

# 14. Recommendation Boundary

The recommendation engine is an internal domain/application component.

Gemini does not become the recommender.

Recommendation generation remains:

```text id="y5t8q1"
RecommendationService
→ RecommendationEngine
```

The conversation layer may invoke the recommendation service.

---

# 15. Conversation Boundary

Conversation orchestration owns:

```text id="n6b2m9"
session lifecycle
context assembly
LLM orchestration
tool execution
response validation
message persistence
```

It does not own:

```text id="s9k4q3"
recommendation algorithms
movie persistence
watchlist business rules
memory lifecycle
```

It invokes those capabilities through application services.

---

# 16. Memory Boundary

Memory owns:

```text id="p8y7r6"
candidate validation
authority
scope
conflicts
deduplication
lifecycle
retrieval policy
deletion
```

Gemini may propose memory candidates.

MemoryService decides whether they become durable state.

---

# 17. API Boundary

FastAPI routes are thin.

A route should primarily perform:

```text id="t3v9x2"
request parsing
authentication context
application-service invocation
response serialization
```

It should not contain:

```text id="q6m8w1"
SQL
TMDB calls
Gemini orchestration
ranking logic
memory rules
```

---

# 18. Worker Boundary

Celery provides asynchronous execution.

Workers invoke application services rather than duplicating business logic.

Example:

```text id="m7x4c2"
Celery task
→ MovieEnrichmentService
→ MovieDataProvider
```

not:

```text id="b2q9v8"
Celery task
→ custom TMDB logic
```

separate from the API implementation.

---

# 19. Why Not Microservices Initially?

Microservices would introduce distributed complexity without an established need.

At the beginning, CineRec does not require independent:

```text id="w3c8n1"
deployment
scaling
ownership
database
failure domain
```

for each domain module.

The recommendation engine may be computationally heavier than standard CRUD operations, but that does not automatically justify a network service.

A separate worker process provides sufficient isolation initially.

---

# 20. Why Not a Simple Monolith?

A traditional unstructured monolith would create architectural coupling.

The problem is not:

```text id="r8m2v7"
"one application"
```

The problem is:

```text id="q5n1x3"
"one application with no boundaries"
```

CineRec therefore deliberately chooses:

```text id="f6w9k2"
modular monolith
```

rather than:

```text id="p3r5x8"
big ball of mud
```

---

# 21. Modular Means Explicit Contracts

Modules communicate through:

```text id="n7m3q1"
application services
domain objects
interfaces
events where appropriate
```

They should not communicate through:

```text id="c5x8p2"
arbitrary database queries
internal table assumptions
global mutable state
private implementation details
```

---

# 22. Database Access Rule

Modules should access data through their repository/application interfaces.

Avoid:

```text id="q4f7n9"
RecommendationModule
→ directly queries arbitrary Memory tables
```

Instead:

```text id="m6z2w5"
RecommendationService
→ PersonalizationContextProvider
```

when cross-domain information is required.

---

# 23. Shared Database Does Not Mean Shared Ownership

All modules initially use the same PostgreSQL database.

However, logical ownership remains explicit.

Example:

```text id="g8p4k1"
Memory module
→ owns memory tables

Recommendation module
→ owns recommendation tables

Movie module
→ owns movie catalog tables
```

Shared infrastructure is not permission to modify another module's state arbitrarily.

---

# 24. Cross-Module Reads

Cross-module reads are allowed when necessary.

Preferred:

```text id="h2j7n3"
RecommendationService
→ UserTasteProvider
```

rather than:

```text id="v4q6m8"
RecommendationService
→ direct SQL against every personalization table
```

---

# 25. Cross-Module Writes

Cross-module writes require explicit application-level coordination.

Example:

```text id="w3k5r9"
User feedback
→ InteractionService
→ Recommendation update trigger
```

rather than arbitrary writes into multiple modules from an API route.

---

# 26. Transactions

The modular monolith can use local PostgreSQL transactions for operations requiring atomicity.

Example:

```text id="n6x4p8"
rating creation
+
interaction event
```

may be committed together when the domain requires it.

This is significantly simpler than a distributed transaction across services.

---

# 27. Eventual Consistency

Not everything must be synchronous.

Examples:

```text id="t7p3m2"
rating
→ taste profile update
→ eventual

movie metadata update
→ embedding regeneration
→ eventual
```

The monolith supports this using:

```text id="q4n8w5"
Celery
```

rather than introducing Kafka immediately.

---

# 28. Domain Events

The architecture may use internal domain/application events for decoupling.

Examples:

```text id="y6m9c1"
MovieRated
MovieWatched
MemoryCreated
RecommendationAccepted
```

Events should remain lightweight.

---

# 29. Internal Events Are Not Microservices

Publishing an internal event does not require:

```text id="s3q7x5"
Kafka
RabbitMQ
service bus
```

Initially, an in-process or database-backed/event-driven mechanism may be sufficient.

---

# 30. Background Jobs as Async Boundary

If an operation is:

```text id="p8x5k1"
long-running
retriable
batch-oriented
provider-heavy
```

it should become a background job.

This provides much of the workload isolation needed without distributed services.

---

# 31. Scaling the Monolith

The FastAPI layer is stateless.

Therefore:

```text id="a7q3m5"
API instance × N
```

is supported.

The shared infrastructure remains:

```text id="z4p8c2"
PostgreSQL
Redis
```

---

# 32. Independent Worker Scaling

Workers can scale separately:

```text id="h5m7x3"
API = 3 replicas
Worker = 5 replicas
```

if workload requires it.

---

# 33. Why This Is Enough Initially

The system already separates:

```text id="r8c1y6"
HTTP traffic
background work
durable state
cache
external providers
```

The most important sources of scaling pressure are therefore isolated without introducing service-to-service networking.

---

# 34. Future Extraction Strategy

The modular boundaries are designed so a component can eventually become:

```text id="n2x7m4"
Recommendation Service
```

for example.

Initial:

```text id="e4p9q6"
RecommendationService
```

runs inside the monolith.

Future:

```text id="k8w3z1"
RecommendationService
→ HTTP/gRPC API
→ separate deployment
```

The domain contract should remain conceptually the same.

---

# 35. Extraction Trigger

A module should become a separate service only when one or more measurable conditions occur:

```text id="h6q1v5"
independent scaling requirement
independent deployment requirement
resource isolation requirement
failure isolation requirement
clear ownership boundary
technology/runtime mismatch
```

---

# 36. Non-Triggers

The following are not sufficient reasons to create a microservice:

```text id="p3m7x9"
"microservices are industry standard"
"the codebase is getting bigger"
"containers are being used"
"the architecture diagram looks cooler"
"the module has many files"
```

---

# 37. Extraction Candidates

Likely future extraction candidates:

```text id="q8w4n2"
recommendation inference
ML training/inference
catalog ingestion
AI orchestration
```

But this remains conditional.

---

# 38. Poor Extraction Candidates

Do not split tiny CRUD domains such as:

```text id="b5x7m1"
ratings
watchlist
profile
```

into independent services without strong operational reasons.

---

# 39. Shared Database During Extraction

A future service extraction should avoid accidentally creating permanent cross-service database coupling.

Ideal progression:

```text id="j4n8p3"
module owns logical data
→ service boundary created
→ data ownership clarified
→ API/event contract created
→ database extraction later if necessary
```

---

# 40. Service Extraction Sequence

When extraction is justified:

```text id="q7m5x2"
1. identify module boundary
2. identify public contract
3. identify data ownership
4. isolate dependencies
5. add contract tests
6. create service
7. migrate calls
8. monitor
9. remove old in-process path
```

---

# 41. Strangler Approach

Do not rewrite the module completely.

Prefer:

```text id="x3p6v8"
existing module
→ introduce service interface
→ route selected calls externally
→ compare behavior
→ migrate completely
```

---

# 42. Internal Interfaces as Future Service Contracts

Application interfaces should be designed cleanly enough that they can later become:

```text id="f2q9w5"
REST
gRPC
message/event
```

contracts if required.

---

# 43. Avoid Premature RPC

Do not introduce HTTP calls between modules merely to simulate microservices.

Inside the monolith:

```text id="c7m1x9"
direct application method call
```

is preferable to:

```text id="v4p8q2"
HTTP localhost call
```

---

# 44. Avoid Network Simulation

The following is prohibited:

```text id="n6q3y7"
RecommendationService
→ localhost HTTP
→ same process/application
```

without a real service-boundary requirement.

It increases latency and complexity without providing meaningful isolation.

---

# 45. Deployment Units

The architecture distinguishes:

```text id="r5c8x2"
logical modules
```

from:

```text id="m7p4k9"
runtime deployment units
```

Initial deployment units:

```text id="a2y6q1"
web
api
worker
```

Logical modules remain inside the API/worker codebase.

---

# 46. Runtime Separation

The same codebase can produce:

```text id="w8x3m5"
API runtime
Worker runtime
```

using different startup commands.

This gives independent resource behavior without duplicated application logic.

---

# 47. Testing Benefit

The modular monolith provides:

```text id="k3m9p7"
unit tests
integration tests
contract tests
```

without requiring every test to cross a network boundary.

This makes the test suite:

```text id="t6y1q4"
faster
more deterministic
cheaper
```

---

# 48. Local Development Benefit

Developers can start the whole system with:

```bash id="x8p2w6"
docker compose up
```

rather than starting:

```text id="f7m4n9"
10+ independent services
```

with separate networking and credentials.

---

# 49. Deployment Benefit

Production initially needs only:

```text id="a4q9x1"
frontend
API
worker
database
Redis
```

instead of a service fleet.

---

# 50. Cost Benefit

Fewer deployment units mean:

```text id="s3k7m8"
fewer idle instances
fewer load balancers
fewer service domains
fewer monitoring targets
fewer network hops
```

which aligns with the near-zero-budget constraint.

---

# 51. Reliability Benefit

A modular monolith avoids a large class of distributed-system failures:

```text id="h9w3c5"
service discovery failure
RPC timeout chains
partial service deployment
network partition
distributed transaction failure
service authentication errors
```

These are not automatically eliminated, but they are avoided where they are unnecessary.

---

# 52. Reliability Trade-Off

The monolith has a larger deployment blast radius.

A fatal API-level bug could affect several modules simultaneously.

This is accepted initially because:

```text id="q6m8p4"
operational simplicity
```

has greater value at current scale.

This trade-off must be reconsidered as traffic and team size grow.

---

# 53. Failure Isolation

Even within the monolith, some workloads should remain isolated through:

```text id="x2n7m9"
separate worker process
timeouts
circuit breakers
rate limits
resource limits
```

This is particularly important for:

```text id="m8p4q1"
Gemini
TMDB
ML jobs
```

---

# 54. Heavy ML Work

Training and expensive batch processing must not run inside API requests.

Use:

```text id="j5x7c3"
Celery / offline jobs
```

or dedicated compute later.

---

# 55. Memory Usage Isolation

Workers with large ML/data workloads should have independently tunable memory limits from API processes.

---

# 56. Provider Failure Isolation

A TMDB outage should not cause the entire application process to crash.

Provider calls use:

```text id="q8m2w6"
timeouts
retries
circuit breakers
fallbacks
```

as specified in the provider documents.

---

# 57. LLM Failure Isolation

Gemini failures should produce:

```text id="r3x7m5"
fallback
graceful degradation
controlled error
```

rather than an application-wide outage.

---

# 58. Module Interface Rule

Every module must expose a deliberate public interface.

Example:

```text id="c9w4y1"
recommendation/
    public.py
```

or an equivalent application-service structure.

Other modules should depend on that interface rather than private internals.

---

# 59. Private Module Internals

A module may contain:

```text id="u7x3m8"
repositories
helpers
algorithm internals
mappers
database queries
```

that are private to the module.

---

# 60. No Circular Dependencies

The module graph must not contain:

```text id="g5n8q2"
A → B → A
```

through imports or service dependencies.

Circular dependencies should be resolved by:

```text id="f2m6x9"
shared abstraction
dependency inversion
domain event
```

rather than shortcuts.

---

# 61. Dependency Graph Review

Major module dependencies should remain documented.

Example:

```text id="v9q3k7"
Conversation
 ├── Recommendation
 ├── Movie
 ├── Memory
 └── Watchlist

Recommendation
 ├── Movie
 └── Personalization

Memory
 └── User
```

---

# 62. Dependency Direction Example

Good:

```text id="c6m2x8"
Conversation
→ Recommendation interface
```

Bad:

```text id="p7q4n5"
Recommendation
→ Conversation internals
```

unless an explicit domain dependency requires it.

---

# 63. Shared Kernel

Only genuinely shared domain concepts should become shared primitives.

Examples may include:

```text id="x5m8q1"
MovieId
UserId
Timestamp
Pagination
```

Avoid a giant:

```text id="n4q7p3"
shared/utils/
```

containing unrelated business logic.

---

# 64. Shared Utility Rule

A utility belongs in shared code only when:

```text id="s6x2m9"
multiple modules genuinely need it
+
its semantics are stable
```

---

# 65. No Global Service Locator

Do not introduce a global registry through which every module can retrieve every service.

Prefer dependency injection.

---

# 66. Dependency Injection

Use constructor/function injection for:

```text id="k8p4q6"
repositories
providers
LLM
cache
clock
recommendation engine
```

This improves testing and preserves boundaries.

---

# 67. Configuration Boundary

Configuration should be centralized.

Modules should receive only the configuration they need.

Do not pass the entire application settings object everywhere.

---

# 68. Secrets Boundary

No domain module should directly inspect:

```text id="r5x8m3"
GEMINI_API_KEY
TMDB_ACCESS_TOKEN
DATABASE_PASSWORD
```

Infrastructure owns secret consumption.

---

# 69. Logging Boundary

Modules should produce structured domain/operational logs through shared observability infrastructure.

---

# 70. Metrics Boundary

Custom metrics should be registered centrally or through well-defined module instrumentation.

---

# 71. API Boundary Stability

Internal restructuring must not unnecessarily change:

```text id="u2m6q9"
/api/v1
```

contracts.

---

# 72. Database Boundary Stability

Module refactoring should not require schema changes unless data ownership actually changes.

---

# 73. Provider Boundary Stability

Switching:

```text id="p8x5n4"
TMDB
```

or:

```text id="k7m3q1"
Gemini
```

must not require changes to domain entities.

---

# 74. Recommendation Boundary Stability

The recommendation API should remain stable while algorithms evolve.

Example:

```text id="q3y8m6"
RecommendationEngine.recommend(context)
```

can internally change from:

```text id="h4n7x2"
popularity
```

to:

```text id="j6m9q5"
hybrid CF + semantic + ranker
```

without changing callers.

---

# 75. Model Boundary

ML models are implementation details behind the recommendation interface.

---

# 76. Prompt Boundary

Gemini prompts are implementation details behind the conversation/AI interfaces.

---

# 77. Database Boundary

ORM models are persistence implementation details.

Do not expose SQLAlchemy models directly through the public API.

---

# 78. API DTO Boundary

Public response objects should be API DTOs.

Example:

```text id="w5q8m3"
MovieSummaryResponse
```

not:

```text id="x2m6k9"
SQLAlchemy Movie
```

---

# 79. Provider DTO Boundary

TMDB response models should not become public API schemas.

---

# 80. Domain Entity Boundary

Domain entities should not depend on provider-specific DTOs.

Map:

```text id="n4q7c8"
Provider DTO
→ Domain representation
```

---

# 81. Error Boundary

Infrastructure errors map to application-level errors.

Example:

```text id="g6m2x5"
TMDB 429
→ ProviderRateLimitError
```

rather than leaking HTTP-provider behavior throughout the domain.

---

# 82. Observability Boundary

Provider-specific telemetry can exist inside infrastructure, but application-level metrics should use stable CineRec concepts.

---

# 83. Security Boundary

Authorization belongs in the application/service layer and must not rely on frontend module boundaries.

---

# 84. Background Job Boundary

Celery tasks invoke application services.

They should not independently recreate business rules.

---

# 85. Job Payloads

Worker payloads should use stable IDs and typed arguments.

Example:

```text id="n9q5w2"
refresh_movie(movie_id)
```

not complete ORM objects serialized into Redis.

---

# 86. Worker-to-Database Access

Workers may access PostgreSQL through the same repositories/application services as the API.

---

# 87. Worker-to-Provider Access

Workers use the same provider abstractions as synchronous application code.

---

# 88. Worker-to-LLM Access

Background AI work uses:

```text id="w7m4x9"
LLMProvider
```

not direct Gemini SDK code.

---

# 89. Atomicity

Within the monolith, prefer local atomic database operations where possible.

This is one of the significant advantages of delaying service decomposition.

---

# 90. Transaction Example

A rating operation can potentially perform:

```text id="p2x6m8"
create/update rating
+
record interaction
+
invalidate relevant cache
```

with clearly defined transaction boundaries.

---

# 91. Async Side Effects

Expensive side effects should happen after the core transaction.

Example:

```text id="j4q8w3"
rating committed
↓
enqueue profile update
```

---

# 92. Transactional Outbox

If reliable event publishing becomes necessary, introduce a transactional outbox before introducing a distributed messaging system.

Initial architecture does not require Kafka.

---

# 93. Outbox Future

Potential:

```text id="x8m5q2"
database transaction
├── domain state
└── outbox event

worker
→ publish/process
```

---

# 94. Service Extraction and Events

When modules become services, events may become the preferred cross-service integration mechanism for suitable workflows.

---

# 95. API-to-Service Migration

A future extracted service should preserve the application-level contract:

```text id="q6w3n8"
RecommendationService
```

whether implemented:

```text id="p9m4x7"
in-process
```

or:

```text id="f3k8c2"
remote service
```

---

# 96. Remote Call Resilience Future

When service extraction happens, introduce:

```text id="j5q7m2"
timeouts
retries
circuit breakers
bulkheads
service authentication
```

for internal RPC.

These are unnecessary for in-process calls.

---

# 97. Service Authentication Future

Extracted services must not trust each other merely because they are on the same network.

Use explicit service identity/authentication.

---

# 98. Database Ownership Future

A service extraction should eventually clarify:

```text id="v8n3q5"
which service owns which tables
```

and minimize cross-service database access.

---

# 99. No Distributed Database Requirement Now

The current design intentionally uses:

```text id="w6x2m9"
one PostgreSQL instance
```

because:

```text id="r4p7k1"
transactions
joins
consistency
operations
```

are simpler and sufficient at the initial scale.

---

# 100. One Database Does Not Mean One Schema Forever

If later extraction requires stronger isolation, data ownership can evolve.

But this is deferred.

---

# 101. Deployment Mapping

The current logical architecture maps to deployment like:

```text id="k3m8q7"
Logical modules
        │
        ▼
 ┌───────────────┐
 │ FastAPI API   │
 └───────────────┘

Background modules
        │
        ▼
 ┌───────────────┐
 │ Celery Worker  │
 └───────────────┘
```

---

# 102. Separate Worker Image

The worker may use the same application image as the API while executing a different command.

---

# 103. Independent Resources

API and worker may have different:

```text id="p7x4m2"
CPU
memory
replica count
timeouts
```

---

# 104. Horizontal API Scaling

Because the API is stateless:

```text id="g5m8q3"
API replicas
```

may increase without code decomposition.

---

# 105. Horizontal Worker Scaling

Likewise:

```text id="z2q7x6"
worker replicas
```

may increase independently.

---

# 106. Database as Shared Consistency Layer

The shared PostgreSQL instance supports strong local consistency across modules where necessary.

---

# 107. Caching Strategy

Redis is shared infrastructure but cache namespaces remain module-specific.

Example:

```text id="u8x3n5"
recommendation:...
tmdb:...
session:...
rate:...
```

---

# 108. Cache Ownership

A module may own its cache keys.

Another module must not mutate them casually.

---

# 109. Observability Across Modules

The monolith should still emit:

```text id="q4n7m2"
module
operation
trace
```

metadata so internal boundaries remain visible.

---

# 110. Trace Example

```text id="m8x2p5"
HTTP
└── conversation.turn
    ├── memory.retrieve
    ├── gemini.interaction
    ├── recommendation.generate
    │   ├── candidate.cf
    │   ├── candidate.semantic
    │   └── ranking
    └── persist
```

---

# 111. Test Architecture

The modular monolith supports:

```text id="f6q9x4"
unit
component
integration
contract
E2E
```

tests at clear boundaries.

---

# 112. Module Contract Tests

Each module should have tests for its public application interfaces.

---

# 113. Architecture Tests

The project should eventually enforce dependency rules automatically.

For Python, architecture tests may inspect imports and reject prohibited dependencies.

Example rule:

```text id="p8m4x7"
domain
X
→ infrastructure

domain
✓
→ domain
```

---

# 114. Architecture Regression

If a developer writes:

```python id="q2x7m5"
from infrastructure.tmdb.client import TMDBClient
```

inside domain logic, CI should ideally detect this.

---

# 115. Architecture Documentation

The following diagrams are normative:

```text id="y7m3q8"
module dependency graph
data ownership map
provider boundaries
deployment topology
```

---

# 116. Architecture Change Process

Any change that alters module boundaries requires:

```text id="j9x4p6"
ADR
```

---

# 117. ADR Triggers

Create an ADR when:

```text id="c5m8q2"
creating a microservice
splitting a major module
changing database ownership
introducing Kafka/message bus
introducing Kubernetes
introducing service mesh
changing authentication architecture
changing primary LLM architecture
```

---

# 118. Non-ADR Changes

Ordinary implementation changes do not require ADRs.

Examples:

```text id="q7x2m9"
refactor helper
add unit test
optimize query
change component layout
fix bug
```

provided architectural boundaries remain unchanged.

---

# 119. Reassessment Triggers

This ADR must be reconsidered when:

```text id="r4m8x6"
API scaling becomes a bottleneck
worker scaling becomes a bottleneck
ML inference requires dedicated hardware
one module requires independent deployment
one module causes unacceptable failure coupling
team ownership becomes distributed
database contention becomes a system bottleneck
```

---

# 120. Metrics for Reassessment

The decision should be revisited using evidence such as:

```text id="v3q7m1"
API CPU saturation
worker queue age
database saturation
recommendation latency
deployment frequency
deployment blast radius
incident frequency
module release independence
```

---

# 121. No Arbitrary Threshold

There is no universal number of:

```text id="k8x5m3"
users
requests
files
lines of code
```

that automatically requires microservices.

The decision is evidence-driven.

---

# 122. Team Size Consideration

As engineering teams grow, independent ownership may justify service extraction.

But team size alone does not require it.

---

# 123. Technology Mismatch

A future component may justify extraction if it needs an incompatible runtime.

Example:

```text id="n7m4x8"
Python ML service
```

while another component may use:

```text id="q6x2p9"
different runtime
```

The decision should be based on actual need.

---

# 124. Resource Isolation

A component may be extracted if its workload cannot safely share resources.

Example:

```text id="w5m9k3"
massive inference
→ dedicated compute
```

---

# 125. Failure Isolation

A component may become a service if its failure must not threaten the availability of the rest of the application.

---

# 126. Independent Scaling

The strongest common extraction signal is:

```text id="a3q8m5"
one workload scales radically differently from the rest
```

---

# 127. Independent Deployment

If one component needs to deploy:

```text id="f7m2x9"
several times/day
```

while the rest deploy:

```text id="r8q4n6"
weekly
```

service extraction may eventually reduce operational friction.

---

# 128. Independent Ownership

A stable service boundary may become useful when:

```text id="m6x9p3"
distinct engineering teams
```

own different capabilities.

---

# 129. Data Ownership

Extraction should not proceed without clear data ownership.

---

# 130. Service Extraction Anti-Pattern

Do not create:

```text id="q9m4x6"
movie-service
user-service
rating-service
watchlist-service
memory-service
```

simply because each domain has a table.

---

# 131. CRUD-Service Warning

A service should have a meaningful independent operational boundary.

A database table is not a service boundary.

---

# 132. Distributed Transactions Warning

Splitting tightly coupled modules too early often creates distributed transaction problems.

The monolith avoids these where local ACID transactions provide better correctness.

---

# 133. Latency Warning

Internal network calls add latency.

For hot paths like:

```text id="x5m8q2"
recommendation
conversation
```

keeping computation local is valuable initially.

---

# 134. Debugging Warning

A request crossing six services is harder to debug than:

```text id="n7q3m9"
one process trace
```

when the same result can be achieved locally.

---

# 135. Operational Warning

Every additional service adds:

```text id="p4m8x7"
deployment
logs
metrics
alerts
credentials
health checks
configuration
failure modes
```

---

# 136. Cost Warning

Every additional continuously running service may add fixed cost.

This conflicts with the project's near-zero-budget target.

---

# 137. Developer Experience

The modular monolith enables a developer to reason about:

```text id="j8m3q5"
one repository
one database
one API
one worker system
```

while retaining clear code boundaries.

---

# 138. Local Environment

Target local setup:

```text id="q6w9m4"
Docker Compose
├── web
├── api
├── worker
├── postgres
└── redis
```

Optional:

```text id="r3x7p8"
observability stack
```

---

# 139. Production Environment

Target:

```text id="n5m8q2"
web
api × N
worker × N
postgres
redis
```

---

# 140. Deployment Independence

Although modules are not independently deployable initially, API and worker processes are independently deployable runtime units.

---

# 141. Configuration Independence

Modules may read only their relevant configuration.

---

# 142. Security Independence

Each module must preserve authorization and data-ownership boundaries even though they share a process.

---

# 143. No Trust-by-Module

The fact that:

```text id="k4m7x9"
RecommendationService
```

runs in the same process as:

```text id="q8x2m5"
MemoryService
```

does not justify bypassing their interfaces.

---

# 144. Code Review Rule

A reviewer should reject code that:

```text id="f3m9q7"
bypasses module interfaces
imports infrastructure into domain
duplicates provider logic
adds arbitrary SQL
mixes orchestration into routes
```

without strong justification.

---

# 145. Architecture Linting

Introduce automated dependency checks when the repository structure stabilizes.

---

# 146. Boundary Tests

At minimum test:

```text id="u6m3x8"
domain does not import infrastructure
API does not contain SQL
Gemini code exists only behind provider boundary
TMDB code exists only behind provider boundary
```

---

# 147. Refactoring Rule

Internal module refactors should preserve public application contracts unless the change intentionally modifies behavior.

---

# 148. Code Ownership

Ownership can be assigned at module level even before services are extracted.

Example:

```text id="p7x5m3"
recommendation/
conversation/
memory/
movie/
```

each can have responsible maintainers.

---

# 149. Future Microservice Contract

If a module becomes a service, its existing public interface becomes the starting point for the service API.

---

# 150. API Technology for Future Services

Do not decide REST vs gRPC vs events now.

Choose based on the actual extracted workload.

---

# 151. Message Bus Deferral

Kafka or another distributed message bus is explicitly deferred.

Celery + Redis is sufficient initially for background processing.

---

# 152. Service Mesh Deferral

Service mesh is explicitly deferred.

No current requirement justifies it.

---

# 153. Kubernetes Deferral

Kubernetes is explicitly deferred.

Containerization is retained so a future migration remains possible.

---

# 154. Multi-Region Deferral

Multi-region deployment is explicitly deferred.

---

# 155. Multi-Database Deferral

Multiple databases are explicitly deferred.

---

# 156. Architecture Evolution

The intended evolution is:

```text id="x8m4q7"
Modular Monolith
        ↓
Horizontally Scaled Modular Monolith
        ↓
Isolate heavy workloads
        ↓
Extract only justified services
        ↓
Distributed architecture if required
```

---

# 157. Stage 1 — Modular Monolith

```text id="m4q8x2"
one backend repo
one PostgreSQL
one Redis
one API deployment
one worker deployment
```

---

# 158. Stage 2 — Scale Processes

```text id="p7x3m9"
API × N
Worker × N
```

with shared infrastructure.

---

# 159. Stage 3 — Isolate Workloads

Possible:

```text id="j8m5q4"
ML inference worker
recommendation compute worker
catalog ingestion worker
```

---

# 160. Stage 4 — Extract Service

Only after measurable need:

```text id="q6x9m2"
Recommendation Service
```

for example.

---

# 161. Stage 5 — Distributed System

Only where required:

```text id="w4m7x8"
multiple services
message bus
service discovery
advanced orchestration
```

---

# 162. Consequences — Positive

This decision provides:

```text id="a9x3m6"
simpler deployment
lower cost
simpler local development
strong database transactions
fewer network failures
faster development
easier debugging
simpler testing
clear domain organization
easy initial scaling
```

---

# 163. Consequences — Negative

It also means:

```text id="q7m4x2"
larger deployment blast radius
shared runtime resources
less independent deployment
less independent scaling at module level
strong discipline required to maintain boundaries
```

These trade-offs are accepted initially.

---

# 164. Mitigation — Deployment Blast Radius

Use:

```text id="m5x8q3"
health checks
staging
E2E tests
rollback
feature flags
```

---

# 165. Mitigation — Resource Competition

Use:

```text id="j2q7m4"
separate worker process
resource limits
queue isolation
```

---

# 166. Mitigation — Boundary Erosion

Use:

```text id="x6m9p1"
architecture documentation
code review
dependency tests
ADR process
```

---

# 167. Mitigation — Lack of Independent Scaling

Use:

```text id="w8q3m5"
API/worker separation
horizontal process scaling
```

before service extraction.

---

# 168. Mitigation — Deployment Coupling

Use:

```text id="p4x7m9"
feature flags
backward-compatible migrations
independent runtime commands
```

---

# 169. Decision Scope

This ADR covers the initial architecture only.

It does not prohibit future:

```text id="r8m3q6"
microservices
service extraction
multi-region deployment
different message systems
different databases
```

It simply requires evidence before adopting them.

---

# 170. Reassessment Process

When extraction becomes a possibility:

```text id="n5q8m2"
1. Identify bottleneck.
2. Measure it.
3. Confirm simpler scaling options are insufficient.
4. Identify module boundary.
5. Define data ownership.
6. Define service contract.
7. Create new ADR.
8. Prototype extraction.
9. Compare operational cost.
10. Decide.
```

---

# 171. Evidence Required

A service-extraction ADR should contain:

```text id="x7m2q9"
current workload
bottleneck measurements
current failure mode
required scaling behavior
data ownership
expected benefits
operational cost
migration strategy
rollback strategy
```

---

# 172. No Architecture by Resume Keywords

The architecture must not be designed to maximize the number of technologies listed on a résumé.

Technology should follow requirements.

---

# 173. No Architecture by Diagram Aesthetics

A more complex architecture diagram is not automatically a better architecture.

---

# 174. No Architecture by Trend

Do not introduce:

```text id="q4m8x7"
Kafka
Kubernetes
service mesh
microservices
```

because they are commonly associated with "industry-grade" systems.

---

# 175. Industry-Grade Definition

For CineRec, industry-grade means:

```text id="j7x3p9"
correct boundaries
security
testing
observability
reliability
reproducibility
scalability
maintainability
```

not maximum infrastructure complexity.

---

# 176. Architecture Quality Gate

A proposed architecture change must improve at least one of:

```text id="m8q4x2"
scalability
reliability
security
developer velocity
operability
cost efficiency
```

without creating disproportionate complexity.

---

# 177. Complexity Budget

Every major architectural component incurs a complexity cost.

Examples:

```text id="q3m7x9"
service
database
queue
load balancer
cluster
provider
```

must have an explicit purpose.

---

# 178. Final Decision Matrix

| Requirement                   | Modular Monolith | Microservices Initially |
| ----------------------------- | ---------------: | ----------------------: |
| Low cost                      |                ✓ |                         |
| Fast development              |                ✓ |                         |
| Simple local setup            |                ✓ |                         |
| Strong DB transactions        |                ✓ |                         |
| Horizontal API scaling        |                ✓ |                       ✓ |
| Worker scaling                |                ✓ |                       ✓ |
| Independent module deployment |                  |                       ✓ |
| Independent module scaling    |                  |                       ✓ |
| Operational simplicity        |                ✓ |                         |
| Future extraction             |                ✓ |                       ✓ |
| Current CineRec needs         |                ✓ |                         |

This table describes architectural characteristics; it is not a ranking of alternatives.

---

# 179. Canonical Architecture

```text id="v6q3m8"
                         CineRec
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
         FastAPI API                 Celery Worker
              │                           │
              └─────────────┬─────────────┘
                            │
                     Modular Application
                            │
      ┌─────────┬───────────┼────────────┬─────────┐
      ▼         ▼           ▼            ▼         ▼
    Movie   Conversation  Memory    Recommendation  User
      │         │           │            │
      └─────────┴───────────┴────────────┘
                            │
                      Application Ports
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
      PostgreSQL          Redis            Providers
                                              │
                                        ┌─────┴─────┐
                                        ▼           ▼
                                      TMDB       Gemini
```

---

# 180. Architectural Invariants

The following must remain true:

```text id="h4m8q1"
1. CineRec is a modular monolith initially.
2. API routes remain thin.
3. Domain logic remains independent of infrastructure.
4. External providers remain behind interfaces.
5. PostgreSQL remains the durable source of truth.
6. Redis remains infrastructure, not domain truth.
7. Workers remain separate from synchronous API execution.
8. Modules communicate through explicit contracts.
9. Arbitrary cross-module database access is prohibited.
10. No module may bypass authorization.
11. No module may bypass provider abstractions.
12. Architecture changes require ADRs.
13. Microservices require evidence.
14. Containers are deployment units, not proof that microservices are needed.
15. The application remains horizontally scalable at the API/worker level.
```

---

# 181. Antigravity Implementation Rules

Antigravity must preserve this architecture.

It must not:

```text id="m7q3x9"
split every module into a microservice
introduce Kubernetes
introduce Kafka
introduce service discovery
introduce service mesh
create direct module-to-module SQL
put SQL in routes
put Gemini calls inside domain entities
put TMDB calls inside recommendation algorithms
```

unless a later ADR explicitly authorizes such a change.

---

# 182. Antigravity Refactoring Rule

When implementing a feature, Antigravity should first ask:

```text id="q5m8x2"
Which existing module owns this behavior?
```

It should extend that module rather than create a new architectural layer unnecessarily.

---

# 183. Antigravity Dependency Rule

When a module needs another capability:

```text id="x7p4m9"
depend on its public application interface
```

not its:

```text id="n3q6w8"
private repository
database tables
provider implementation
```

---

# 184. Antigravity Provider Rule

External integrations must enter through:

```text id="m6x2q8"
provider abstraction
```

not directly from:

```text id="r9p4n7"
route
domain object
recommendation algorithm
```

---

# 185. Antigravity Database Rule

Database access must remain:

```text id="j8m5x2"
repository/infrastructure
```

and application services.

---

# 186. Antigravity Testing Rule

Every architectural boundary introduced by code must have corresponding tests.

---

# 187. Antigravity Documentation Rule

If implementation reveals that this architecture is insufficient:

```text id="q4m7x8"
do not silently redesign it
```

Create an ADR describing:

```text id="p8x3m6"
problem
evidence
alternatives
decision
migration
```

---

# 188. Status

**Accepted.**

This decision governs the initial CineRec architecture and remains active until superseded by a new ADR.

---

# 189. Summary

CineRec will start as:

```text id="y7m4q2"
a modular monolith
```

with:

```text id="x3p8m5"
strong internal boundaries
+
separate API and worker runtimes
+
shared PostgreSQL
+
shared Redis
+
provider abstractions
```

The system is intentionally designed to evolve:

```text id="q6m2x9"
without
```

premature distributed-system complexity.

The architecture's central principle is:

> **Keep the code modular from day one, but keep the system distributed only when the workload proves that distribution is necessary.**

