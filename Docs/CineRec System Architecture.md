# CineRec — System Architecture

**Status:** Architecture / source of truth
**Working title:** CineRec
**Version:** 1.0
**Depends on:**

* `01-product-vision.md`
* `02-functional-requirements.md`

**Primary objective:** Define a production-quality, scalable, maintainable architecture for CineRec while preserving a low-cost deployment strategy and avoiding premature distributed-system complexity.

---

# 1. Architecture Overview

CineRec is a personalized movie-discovery platform centered around a conversational AI orb.

The system combines:

* conversational AI
* structured intent extraction
* persistent user memory
* collaborative filtering
* contextual recommendation
* semantic retrieval
* movie metadata
* behavioral feedback
* recommendation explainability

The architecture must keep these concerns separate.

The fundamental responsibility split is:

```text
LLM
→ understands the human

Recommendation Engine
→ determines suitable movies

TMDB
→ provides movie knowledge

PostgreSQL
→ stores application truth

Redis
→ provides ephemeral/high-speed infrastructure

Frontend
→ delivers the cinematic experience
```

No individual component should become responsible for all of these concerns.

---

# 2. Architectural Philosophy

The system follows these principles.

## 2.1 Modular Monolith First

CineRec MUST begin as a modular monolith.

The initial deployment SHOULD consist of:

* one frontend application
* one backend application
* one PostgreSQL instance
* one Redis instance
* background workers
* offline ML processes

The system MUST NOT introduce microservices merely for architectural appearance.

Service extraction requires a concrete justification such as:

* independent scaling requirements
* independent deployment lifecycle
* organizational ownership
* resource isolation
* failure isolation
* materially different runtime requirements

---

## 2.2 Complexity Must Be Earned

Every infrastructure component must have a clear reason to exist.

The initial system MUST prefer:

```text
PostgreSQL
+
pgvector
+
Redis
+
background workers
```

over immediately introducing:

```text
Kafka
Kubernetes
Elasticsearch
dedicated vector database
service mesh
distributed feature store
```

unless requirements later justify them.

---

## 2.3 Domain Boundaries Over Deployment Boundaries

Logical modules should be designed as though they could eventually become independent services, but should initially run inside one deployable backend.

For example:

```text
auth
movies
interactions
memory
recommendations
```

remain separate application modules even though they are deployed together.

This permits future extraction without forcing distributed infrastructure prematurely.

---

# 3. High-Level Architecture

```text
                                      ┌──────────────────────┐
                                      │       Browser        │
                                      │                      │
                                      │ Next.js              │
                                      │ React                │
                                      │ TypeScript           │
                                      └──────────┬───────────┘
                                                 │
                                           HTTPS / API
                                                 │
                                                 ▼
                                      ┌──────────────────────┐
                                      │       FastAPI        │
                                      │                      │
                                      │ API / Application    │
                                      │ Services             │
                                      └──────────┬───────────┘
                                                 │
                 ┌───────────────────────────────┼──────────────────────────────┐
                 │                               │                              │
                 ▼                               ▼                              ▼
        ┌─────────────────┐             ┌─────────────────┐             ┌─────────────────┐
        │   PostgreSQL    │             │      Redis      │             │ External APIs   │
        │                 │             │                 │             │                 │
        │ Users           │             │ Cache           │             │ Gemini          │
        │ Movies          │             │ Rate limiting   │             │ TMDB            │
        │ Ratings         │             │ Background jobs │             │                 │
        │ Interactions    │             │ Ephemeral data  │             └─────────────────┘
        │ Memories        │             └────────┬────────┘
        │ Recommendations │                      │
        │ Vectors         │                      ▼
        └────────┬────────┘             ┌─────────────────┐
                 │                      │ Background      │
                 │                      │ Workers         │
                 │                      │                 │
                 │                      │ ingestion       │
                 │                      │ embeddings      │
                 │                      │ memory jobs     │
                 │                      │ recommendations │
                 │                      └────────┬────────┘
                 │                               │
                 ▼                               ▼
        ┌────────────────────────────────────────────────────┐
        │                 Recommendation System               │
        │                                                    │
        │ Candidate generation                               │
        │ Collaborative filtering                            │
        │ Semantic retrieval                                 │
        │ Contextual filtering                               │
        │ Ranking                                            │
        │ Diversity                                          │
        │ Explanations                                       │
        └──────────────────────────┬─────────────────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │     ML Pipeline      │
                         │                      │
                         │ preprocessing        │
                         │ training             │
                         │ evaluation           │
                         │ model artifacts      │
                         └──────────────────────┘
```

---

# 4. Major System Components

## 4.1 Web Application

Technology:

* Next.js
* React
* TypeScript

Responsibilities:

* landing page
* authentication initiation
* orb interface
* conversation rendering
* recommendation presentation
* movie details
* movie search
* watchlist
* ratings
* personal dashboard
* taste visualizations
* memory controls

The web application MUST NOT:

* access PostgreSQL directly
* access Redis directly
* store server-side API secrets
* implement recommendation algorithms
* make privileged TMDB requests directly
* make privileged Gemini requests directly

All sensitive application operations go through the backend.

---

# 5. Backend Application

Technology:

* Python
* FastAPI
* Pydantic
* SQLAlchemy 2
* Alembic

The backend is the primary application boundary.

Responsibilities:

* authentication/session integration
* authorization
* API handling
* input validation
* orchestration
* movie-domain operations
* interaction recording
* memory management
* recommendation orchestration
* external API adapters
* caching
* job submission
* observability

The backend MUST remain independent from presentation-specific concerns.

---

# 6. Backend Layering

Backend code SHOULD follow this logical structure:

```text
HTTP / API
    ↓
Application Services
    ↓
Domain
    ↓
Repository / Infrastructure
    ↓
Database / External Providers
```

A request handler MUST NOT become the place where:

* SQL is written
* recommendation algorithms are implemented
* LLM prompts are constructed ad hoc
* business rules are duplicated

---

# 7. Backend Module Boundaries

The backend SHOULD be organized into logical modules:

```text
auth/
users/
movies/
ratings/
interactions/
watchlists/
memory/
recommendations/
search/
analytics/
```

Each module SHOULD expose a small application-facing interface.

Example:

```text
recommendations
├── API
├── application
├── domain
├── infrastructure
└── tests
```

---

# 8. Authentication Boundary

Authentication is a dedicated concern.

The authentication layer handles:

* Google OAuth
* session identity
* user identification
* logout
* authenticated request context

Authorization MUST be handled by the application and MUST NOT be delegated entirely to the frontend.

A frontend-provided `user_id` MUST NOT be treated as proof of identity.

The backend MUST derive the effective authenticated user from the validated authentication context.

---

# 9. Authorization Model

The default security model is:

```text
authenticated user
    ↓
owns resource?
    ↓
allow / deny
```

Examples:

A user may:

```text
read own ratings
read own watchlist
modify own memories
read own recommendation history
```

A user MUST NOT:

```text
read another user's memories
modify another user's ratings
read another user's viewing history
```

Administrative capabilities require a separate privileged role.

---

# 10. Movie Domain

The movie domain is responsible for CineRec's internal representation of a movie.

It MUST NOT expose raw TMDB objects throughout the rest of the application.

Instead:

```text
TMDB response
    ↓
TMDB adapter
    ↓
mapping / normalization
    ↓
internal Movie domain representation
```

The internal movie model SHOULD contain only fields required by the application.

---

# 11. External Provider Abstraction

External providers MUST be hidden behind adapters.

For movie data:

```text
MovieDataProvider
       │
       └── TMDBProvider
```

For LLMs:

```text
LLMProvider
       │
       └── GeminiProvider
```

This prevents the rest of the application from becoming tightly coupled to provider-specific SDK objects.

---

# 12. TMDB Integration Architecture

The frontend MUST NOT directly rely on TMDB as its application backend.

The flow should be:

```text
Frontend
   ↓
FastAPI
   ↓
MovieDataProvider
   ↓
TMDBProvider
   ↓
TMDB
```

The backend SHOULD cache or persist useful metadata where appropriate.

The application SHOULD use an internal movie representation so that provider changes do not require rewriting the product.

---

# 13. TMDB Caching Strategy

Movie data is generally much less volatile than user interaction data.

The system MAY maintain:

### Redis cache

For frequently requested movie information.

### PostgreSQL

For useful persisted movie metadata.

### TMDB

As the upstream metadata source.

The system MUST avoid unnecessary repeated calls to TMDB.

The application SHOULD use appropriate freshness policies for different categories of data.

For example:

```text
movie identity
→ highly reusable

cast/crew
→ relatively stable

popularity
→ more frequently refreshed

availability
→ comparatively volatile
```

Exact TTL values belong in configuration rather than being scattered throughout code.

---

# 14. Gemini Integration

Gemini is the initial LLM implementation.

The application MUST interact with Gemini through an internal abstraction:

```text
LLMProvider
```

The provider SHOULD support capabilities such as:

```text
conversation
intent extraction
tool calling
memory candidate extraction
recommendation explanation
```

The LLM provider MUST NOT gain unrestricted access to application internals.

---

# 15. LLM Request Architecture

The preferred flow is:

```text
User message
    ↓
FastAPI
    ↓
Conversation orchestration
    ↓
LLMProvider
    ↓
Gemini
    ↓
structured response
    ↓
Pydantic validation
    ↓
application logic
```

LLM-generated output MUST be treated as untrusted input.

---

# 16. LLM Responsibilities

Gemini SHOULD be responsible for:

* interpreting natural language
* identifying cinematic intent
* generating concise conversational responses
* deciding whether clarification is useful
* requesting application tools
* generating grounded explanations
* identifying potential memory candidates

Gemini MUST NOT be responsible for:

* direct SQL
* authorization
* final movie eligibility
* unrestricted external API access
* inventing movie identifiers
* changing application data without application validation
* implementing collaborative filtering

---

# 17. Tool Calling Boundary

The LLM may request tools.

Example:

```text
search_movies
get_movie
get_user_taste
get_recommendations
save_memory
record_interaction
```

The architecture MUST treat tool calls as requests, not commands with unrestricted authority.

Flow:

```text
Gemini
   ↓
tool request
   ↓
application validates
   ↓
authorization
   ↓
application executes
   ↓
tool result
   ↓
Gemini
```

The tool layer MUST enforce permitted argument schemas and user ownership.

---

# 18. Orb Conversation Architecture

The orb experience is composed of:

```text
Conversation State
        +
Session Intent
        +
Long-Term User Context
        +
LLM Provider
        +
Application Tools
```

The conversational system SHOULD preserve:

* current session context
* recent conversational history
* relevant user taste context
* recommendation history where useful

It SHOULD NOT blindly send the entire user's lifetime dataset to the LLM.

---

# 19. Session Context

Session-level cinematic intent SHOULD be represented explicitly.

Example:

```text
{
  mood: ["tired"],
  emotional_goal: ["comfort"],
  energy: "low",
  max_runtime: 120,
  avoid: ["depressing"]
}
```

Session state is temporary unless promoted to persistent memory.

---

# 20. Long-Term Taste Context

Long-term personalization is stored separately from session context.

Conceptually:

```text
User Taste Profile
├── genre preferences
├── themes
├── styles
├── runtime tendencies
├── director/actor preferences
├── negative preferences
└── confidence/evidence
```

The recommendation engine consumes this profile without exposing the complete underlying database to the LLM.

---

# 21. Memory Architecture

Memory consists of at least:

```text
Explicit Memory
Inferred Memory
Session Context
```

These MUST remain distinguishable.

A memory object SHOULD include concepts such as:

```text
memory_id
user_id
type
subject
value
polarity
confidence
source
created_at
updated_at
```

Possible sources:

```text
user_explicit
behavior_inferred
conversation_inferred
system_derived
```

---

# 22. Memory Precedence

When conflicting preferences exist:

```text
explicit user preference
        ↓
high-confidence inferred preference
        ↓
weak inference
```

Higher-authority preferences should override weaker ones.

Session-specific constraints may override long-term preferences for the current recommendation request.

---

# 23. Recommendation Architecture

The recommendation system MUST be a dedicated subsystem.

It SHOULD be structured as:

```text
Recommendation Request
        ↓
Context Builder
        ↓
Candidate Generation
        ↓
Candidate Union
        ↓
Hard Filtering
        ↓
Ranking
        ↓
Diversity / Exploration
        ↓
Explanation Metadata
        ↓
Recommendation Response
```

---

# 24. Recommendation Request

A recommendation request SHOULD include:

```text
user
session context
long-term taste context
explicit constraints
availability constraints
recommendation surface
exploration preference
previously shown items
```

The request SHOULD have a unique request identifier.

Example:

```text
recommendation_request_id
```

---

# 25. Candidate Generation

Candidate generation SHOULD be modular.

Initial sources:

```text
Collaborative Filtering
Popularity fallback
```

Future sources:

```text
Item similarity
Semantic retrieval
Trending
Exploration
Contextual retrieval
```

Each source SHOULD return candidates with source metadata.

Example:

```text
movie_id
source
candidate_score
metadata
```

---

# 26. Collaborative Filtering Architecture

The initial collaborative-filtering system SHOULD remain decoupled from API and UI code.

Conceptually:

```text
Raw interactions
       ↓
Preprocessing
       ↓
Interaction matrix
       ↓
CF training
       ↓
Model artifact
       ↓
Recommendation model loader
       ↓
Candidate generation
```

Possible models may include:

* user-user collaborative filtering
* item-item collaborative filtering
* matrix factorization

The architecture SHOULD permit replacing the initial method without changing API contracts.

---

# 27. ML Model Interface

The application SHOULD interact with a stable model interface.

Conceptually:

```text
RecommendationModel
├── load()
├── score()
├── recommend()
└── metadata()
```

The application should not know model-specific implementation details.

Possible future implementations:

```text
ItemCFModel
ALSModel
BPRModel
HybridModel
```

---

# 28. Offline ML Pipeline

Training MUST occur outside ordinary synchronous HTTP requests.

The ML pipeline SHOULD contain:

```text
ingestion
preprocessing
feature generation
training
validation
evaluation
artifact creation
model registration
```

Training should produce a versioned artifact.

---

# 29. Model Versioning

Every production recommendation model MUST have a version.

Example:

```text
cf-als-v12
```

The system SHOULD associate recommendation requests with the model version used.

Model metadata SHOULD include:

```text
model_version
algorithm
training_dataset_version
parameters
evaluation_metrics
created_at
status
```

---

# 30. Recommendation Ranking

After candidates are generated:

```text
candidate set
     ↓
hard filters
     ↓
ranking
```

Ranking SHOULD consider:

* collaborative relevance
* current session context
* user taste
* quality signals
* exploration
* diversity
* availability
* prior user interactions

Ranking logic MUST live in the recommendation subsystem.

---

# 31. Hard Filtering

Hard constraints MUST happen before final presentation.

Examples:

```text
already watched
explicitly blocked
outside requested runtime
wrong requested language
provider unavailable when explicitly required
invalid movie
```

Hard constraints MUST NOT be overridden simply because a model assigns a high score.

---

# 32. Soft Ranking Signals

Soft signals MAY include:

```text
historical user preference
collaborative score
semantic similarity
current mood alignment
popularity
novelty
quality
exploration
```

These are ranked rather than treated as absolute exclusions.

---

# 33. Diversity

The ranking layer SHOULD support diversity constraints.

The system should avoid returning ten nearly identical recommendations unless the user explicitly requests highly narrow similarity.

Diversity may consider:

* genre
* theme
* language
* release period
* creator
* recommendation source

---

# 34. Exploration

The recommendation system SHOULD support controlled exploration.

A recommendation may intentionally be less familiar if it shares important contextual or semantic properties with the user request.

Exploration should be configurable rather than hardcoded.

---

# 35. Semantic Retrieval

The architecture should support semantic recommendation as a later or parallel candidate source.

Potential flow:

```text
movie metadata
    ↓
embedding generation
    ↓
pgvector
```

User intent may also be represented semantically:

```text
natural language
    ↓
embedding
    ↓
nearest movie candidates
```

These candidates can then be combined with collaborative-filtering candidates.

---

# 36. PostgreSQL + pgvector

PostgreSQL is the primary source of truth.

pgvector SHOULD initially provide vector storage and retrieval for:

* movie embeddings
* semantic search
* semantic recommendation
* potentially user/taste representations

A separate vector database SHOULD NOT be introduced during initial development.

---

# 37. Search Architecture

Initial search should use PostgreSQL capabilities.

Conceptually:

```text
Search request
   ↓
Search application service
   ↓
Text search
+
fuzzy matching
+
optional vector search
   ↓
ranked results
```

The architecture should support adding a dedicated search engine later if query volume or feature requirements justify it.

---

# 38. Redis Architecture

Redis SHOULD be used only for data that benefits from fast, ephemeral access.

Primary uses:

```text
recommendation cache
movie-detail cache
popular/trending cache
rate limiting
background-job broker
short-lived session data
```

PostgreSQL remains the source of truth.

Redis loss MUST NOT corrupt the application's authoritative data.

---

# 39. Cache Design

Cache entries should have explicit ownership and invalidation policies.

Examples:

```text
movie:{id}
user:{id}:recommendations:{surface}
popular:{region}
```

Cached data SHOULD be reconstructable from authoritative sources.

The system MUST NOT treat Redis as the only persistent copy of important user data.

---

# 40. Background Jobs

Background workers SHOULD process operations that are:

* slow
* resource-intensive
* retryable
* asynchronous
* unnecessary for immediate HTTP response

Examples:

```text
TMDB synchronization
embedding generation
model training
recommendation precomputation
memory summarization
analytics processing
cleanup jobs
```

The API should enqueue jobs and return where appropriate.

---

# 41. Job Idempotency

Background jobs SHOULD be idempotent where practical.

Repeated execution must not cause:

* duplicate permanent records
* inconsistent preference states
* duplicate model registration
* corrupted recommendation data

Jobs SHOULD use stable identifiers or deduplication mechanisms where necessary.

---

# 42. Interaction/Event Architecture

User behavior is represented as interactions.

Conceptually:

```text
interaction
├── impression
├── click
├── view
├── watch
├── complete
├── rating
├── like
├── dislike
├── watchlist_add
├── watchlist_remove
├── skip
└── temporary_rejection
```

All interactions SHOULD contain enough metadata to determine:

* who
* what
* when
* in what context
* from which recommendation request
* from which product surface

---

# 43. Recommendation Attribution

Recommendation items SHOULD retain attribution metadata.

For example:

```text
request_id
model_version
candidate_sources
position
surface
score
```

This allows the system to understand:

* what was shown
* why it entered the result
* which model generated it
* where it appeared

---

# 44. Feedback Loop

The long-term recommendation loop is:

```text
User
 ↓
Recommendation
 ↓
Interaction
 ↓
Stored event
 ↓
Preference update
 ↓
Future recommendation
```

Near-term personalization MAY update cached user state without retraining the entire model.

Full model retraining remains an offline/batch process.

---

# 45. Database Architecture

PostgreSQL should contain logical groups of data:

```text
Identity
├── users
└── profiles

Movie
├── movies
├── genres
├── movie_genres
└── provider identifiers

User activity
├── ratings
├── interactions
├── watchlists
└── viewing history

Personalization
├── memories
├── taste profiles
└── preference signals

Recommendations
├── recommendation requests
├── recommendation items
└── recommendation feedback

ML
├── model versions
├── experiments
└── evaluation metadata
```

Exact schema belongs in `04-database-design.md`.

---

# 46. Data Ownership

Each logical module should have clear ownership of its tables/data.

For example:

```text
auth/users
→ identity module

movies
→ movie module

ratings/watchlist/interactions
→ user activity module

memories
→ memory module

recommendation requests/items
→ recommendation module
```

Other modules SHOULD access data through defined application/repository interfaces rather than arbitrary SQL against unrelated tables.

---

# 47. Transaction Boundaries

Operations requiring atomicity MUST use database transactions.

Examples:

```text
rating creation/update
watchlist update
memory update
critical user-profile changes
```

Distributed transactions across external APIs MUST be avoided.

External side effects should generally occur after the local transaction is safely committed.

---

# 48. External API Failure Strategy

External providers can fail independently.

The system should degrade gracefully.

## Gemini unavailable

Fallback MAY include:

* cached recommendations
* standard search
* non-conversational recommendation flow
* existing taste-based recommendations

## TMDB unavailable

Fallback MAY include:

* internally stored metadata
* cache
* previously retrieved movie records

The entire application MUST NOT become unavailable simply because one external provider is down.

---

# 49. Retry Strategy

Retries MUST be selective.

Retryable examples:

* transient network failures
* temporary upstream service errors
* temporary worker failures

Non-retryable examples:

* invalid user input
* authorization failures
* malformed requests
* deterministic validation errors

Retries MUST use bounded attempts and backoff.

---

# 50. Timeout Strategy

External requests MUST have explicit timeouts.

The system MUST NOT wait indefinitely for:

* Gemini
* TMDB
* database operations
* Redis
* background task completion

Timeouts should be configured centrally.

---

# 51. API Versioning

The public API SHOULD begin under:

```text
/api/v1
```

Breaking API changes should result in a new version rather than silently changing behavior.

---

# 52. API Response Boundary

Internal database models MUST NOT be exposed directly as public API responses.

Use explicit response schemas.

Example:

```text
Database model
     ↓
application mapping
     ↓
API response schema
```

This protects the internal data model from accidental public coupling.

---

# 53. Pagination

Potentially large collections MUST be paginated.

Examples:

* movie search
* watched movies
* watchlist
* recommendation history
* interactions

Cursor-based pagination SHOULD be preferred where appropriate for large or frequently changing datasets.

---

# 54. N+1 Prevention

The backend MUST avoid N+1 query patterns.

For example:

Bad:

```text
query 20 recommendation IDs
→ query movie 1
→ query movie 2
→ query movie 3
...
```

Preferred:

```text
query recommendation IDs
→ batch query movie metadata
→ map results
```

The same principle applies to all relationship loading.

---

# 55. Secrets

The following MUST remain server-side:

```text
GEMINI_API_KEY
TMDB_API_KEY
Google OAuth client secret
DATABASE_URL
Redis credentials
```

Secrets MUST NOT:

* appear in client bundles
* be committed to source control
* be written into logs
* appear in error responses

---

# 56. Configuration

Configuration SHOULD be centralized.

Categories include:

```text
application
database
redis
authentication
external APIs
LLM
recommendation
model
logging
rate limits
feature flags
```

Hardcoded environment-specific values should be avoided.

---

# 57. Rate Limiting

Rate limiting SHOULD exist at the backend boundary.

Higher-risk/high-cost operations should receive stricter limits.

Examples:

```text
LLM requests
movie search
authentication
interaction ingestion
recommendation generation
```

Rate limits MAY be implemented with Redis.

Limits should be configurable.

---

# 58. Observability Architecture

The application SHOULD provide:

```text
structured logs
metrics
traces
health checks
```

A request should have a correlation/request ID.

Example:

```text
request_id
```

should be propagated where practical through:

```text
API
→ application service
→ external API call
→ background job
```

---

# 59. Logging Rules

Logs SHOULD contain useful operational information such as:

```text
request ID
endpoint
latency
status
error category
user-safe identifiers
```

Logs MUST NOT contain:

* passwords
* OAuth secrets
* API keys
* raw access tokens
* session cookies
* unnecessary sensitive user content

---

# 60. Recommendation Observability

Recommendation requests SHOULD expose metrics such as:

```text
request latency
cache hit/miss
candidate count
filtered candidate count
final count
model version
candidate-source distribution
```

This allows debugging of recommendation quality and performance separately.

---

# 61. Health Endpoints

The backend SHOULD expose:

```text
/health
/liveness
/readiness
```

Liveness indicates the process is functioning.

Readiness indicates that required dependencies are sufficiently available to serve traffic.

---

# 62. Error Model

Application errors SHOULD be represented using structured categories.

Examples:

```text
VALIDATION_ERROR
AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
RESOURCE_NOT_FOUND
RATE_LIMITED
UPSTREAM_ERROR
DEPENDENCY_UNAVAILABLE
INTERNAL_ERROR
```

The frontend should receive user-safe messages.

Internal diagnostic information belongs in logs, not API responses.

---

# 63. Frontend ↔ Backend Contract

The backend's OpenAPI definition should be treated as the API contract.

Types SHOULD be generated or synchronized from the backend contract rather than manually duplicated.

This reduces drift between:

```text
FastAPI
```

and:

```text
Next.js
```

---

# 64. Frontend Data Flow

The frontend should separate:

### Server state

Examples:

* movie data
* recommendations
* watchlist
* ratings
* profile
* memory

### Local UI state

Examples:

* orb animation state
* modal open/closed
* temporary input
* selected movie
* transient UI preferences

Server state SHOULD be managed through an appropriate query/data-fetching layer.

---

# 65. Frontend Recommendation Flow

```text
User submits orb message
       ↓
API request
       ↓
conversation response
       ↓
recommendation request if needed
       ↓
recommendation response
       ↓
orb transitions
       ↓
recommendation cards appear
       ↓
user interaction
       ↓
interaction API
```

The frontend should not independently recreate recommendation logic.

---

# 66. Orb State Machine

The orb SHOULD behave as an explicit state machine rather than a collection of unrelated booleans.

Conceptual states:

```text
IDLE
 ↓
INPUT
 ↓
PROCESSING
 ↓
SEARCHING
 ↓
SYNTHESIZING
 ↓
RECOMMENDING
 ↓
WAITING_FOR_FEEDBACK
 ↓
REFINING
```

Failure state:

```text
ERROR
```

The implementation should prevent contradictory states such as:

```text
isListening = true
isError = true
isRecommending = true
```

all simultaneously unless intentionally supported.

---

# 67. Conversation Session Architecture

A conversation session SHOULD have an identifiable session ID.

Conceptually:

```text
conversation_session
├── session_id
├── user_id
├── started_at
├── current_intent
├── status
└── metadata
```

Messages may be stored according to product/privacy requirements.

Persistent taste memory should not simply become a copy of the entire message history.

---

# 68. Recommendation Session

Recommendation generation may be associated with the conversation session.

Conceptually:

```text
Conversation Session
       │
       ├── Intent state
       │
       ├── Recommendation request #1
       │
       ├── User feedback
       │
       └── Recommendation request #2
```

This allows refinement to remain contextually coherent.

---

# 69. Search vs Recommendation

Search and recommendation are separate concerns.

Search answers:

> "What matches what I asked for?"

Recommendation answers:

> "What should this user probably choose?"

They may share:

* movie data
* search indexes
* semantic retrieval
* metadata

but should remain distinct application capabilities.

---

# 70. Personalization Context Builder

A dedicated context-building component SHOULD combine:

```text
long-term taste
+
explicit memory
+
recent behavioral signals
+
current session intent
+
hard constraints
+
availability
```

into a normalized recommendation context.

This prevents every downstream component from reconstructing user context independently.

---

# 71. Context Precedence

Context should follow a conceptual hierarchy:

```text
Hard explicit current constraints
        ↓
Explicit persistent preferences
        ↓
Session preferences
        ↓
High-confidence learned preferences
        ↓
Weak learned preferences
        ↓
Generic popularity/discovery
```

The exact mathematical implementation belongs in the recommendation design document.

---

# 72. Model and Application Separation

The application should not embed training code into request-handling modules.

Separate:

```text
ML training
ML evaluation
ML artifacts
ML inference
```

Training code may depend on scientific computing libraries.

The API should consume model artifacts through a stable inference interface.

---

# 73. Model Loading

The production recommendation service SHOULD load the active model into memory rather than retrain on demand.

Conceptually:

```text
application startup
        ↓
load active model
        ↓
model available for inference
```

Model-loading failures MUST be detectable.

The application should either:

* fail readiness
* fall back to another valid model
* use a simpler fallback recommendation mechanism

according to configured policy.

---

# 74. Model Promotion

A future production workflow SHOULD support:

```text
trained
  ↓
evaluated
  ↓
registered
  ↓
approved
  ↓
active
```

The product should not automatically replace a production model merely because a new model exists.

---

# 75. Feature Flags

Feature flags SHOULD be available for major behavioral changes such as:

```text
semantic_recommendations
hybrid_ranker
new_orb_flow
new_memory_system
new_recommendation_model
```

This permits gradual rollout and safer experimentation.

---

# 76. Experimentation

The architecture SHOULD support future A/B experiments.

A recommendation request MAY carry:

```text
experiment_id
variant
```

Experiments MUST be designed so that user assignment is stable where necessary.

---

# 77. Data Lifecycle

Data should have explicit lifecycle rules.

Example:

```text
raw external data
→ normalized data
→ application data
→ interaction data
→ derived signals
→ model training data
```

Derived artifacts should be reproducible where possible.

---

# 78. Data Reproducibility

ML results SHOULD be reproducible from:

```text
dataset version
+
feature configuration
+
model algorithm
+
hyperparameters
```

The system should maintain enough metadata to understand how a production model was produced.

---

# 79. Deployment Architecture

Initial deployment may use:

```text
Next.js
FastAPI
PostgreSQL
Redis
worker
```

with Docker containers.

The deployment should be capable of running locally through Docker Compose.

---

# 80. Local Development Architecture

The developer environment SHOULD provide:

```text
docker compose up
```

to start infrastructure such as:

```text
PostgreSQL
Redis
```

Application services may run locally or within containers.

The setup should be reproducible across machines.

---

# 81. Production Scaling Strategy

The initial application is designed for vertical and modest horizontal scaling.

### API

Keep backend instances stateless wherever possible.

### Redis

Used as shared ephemeral infrastructure.

### PostgreSQL

Primary persistent store.

### Workers

Scale independently if background workload increases.

### ML inference

Initially local/in-process.

If inference demand grows significantly, it can later be extracted.

---

# 82. Stateless API Principle

FastAPI instances SHOULD remain stateless with respect to durable user state.

Important state belongs in:

```text PostgreSQL
Redis
external auth/session system
```

not local process memory.

Local memory may contain:

* loaded model artifacts
* temporary caches
* immutable configuration

but not authoritative user state.

---

# 83. Horizontal Scaling Path

A likely future progression:

```text
1 API instance
      ↓
multiple API instances
      ↓
shared Redis
      ↓
shared PostgreSQL
      ↓
independent workers
      ↓
dedicated recommendation service
```

The architecture should support this without requiring a rewrite of the product.

---

# 84. Database Scaling Path

Potential evolution:

```text
single PostgreSQL
      ↓
indexes + query optimization
      ↓
connection pooling
      ↓
read replicas if justified
      ↓
partitioning if justified
      ↓
sharding only if genuinely necessary
```

No database sharding should be implemented in the initial product.

---

# 85. Cache Scaling Path

Potential evolution:

```text
single Redis
      ↓
larger Redis instance
      ↓
Redis replication / managed high availability
      ↓
partitioning if required
```

Again, only when actual workload justifies it.

---

# 86. Search Scaling Path

Initial:

```text
PostgreSQL FTS
+
pg_trgm
+
pgvector
```

Potential future:

```text
dedicated search service
```

only if PostgreSQL search becomes a measurable bottleneck or required feature set cannot be efficiently supported.

---

# 87. Recommendation Scaling Path

Initial:

```text
offline CF model
+
small candidate pool
+
in-process ranking
```

Future:

```text
multiple candidate generators
+
precomputed recommendations
+
vector retrieval
+
dedicated inference
+
distributed ranking
```

The API contract should remain stable.

---

# 88. Event Volume Scaling Path

Initial:

```text
PostgreSQL interaction table
```

Future:

```text
PostgreSQL
+
queue
+
analytics store
```

At much larger scale:

```text
event streaming platform
```

should only be introduced when event throughput actually demands it.

---

# 89. Analytics Separation

Operational application data and analytical workloads SHOULD eventually be separable.

Initially they may share PostgreSQL.

If analytical queries begin harming transactional performance:

```text
PostgreSQL
    ↓
analytics pipeline
    ↓
analytical storage
```

This is a future scaling path, not an MVP requirement.

---

# 90. Reliability Principles

The architecture should isolate failures.

Examples:

### Redis unavailable

Core authoritative writes should still be possible where practical.

### Gemini unavailable

Non-LLM product functions should continue.

### TMDB unavailable

Cached/internal movie data should continue working.

### Worker unavailable

The synchronous application should continue operating for functions that do not require that background task.

### Recommendation model unavailable

Fallback recommendation strategy should remain available.

---

# 91. Graceful Degradation Hierarchy

For recommendation generation, the system SHOULD conceptually degrade through:

```text
Hybrid personalized recommendation
        ↓
Collaborative-filtered recommendation
        ↓
Content/semantic recommendation
        ↓
Popularity/trending
        ↓
Basic catalog discovery
```

The exact fallback graph is implementation-specific but should prevent a total failure state wherever reasonable.

---

# 92. Idempotent User Operations

Operations such as:

```text
set rating
add/remove watchlist
save explicit memory
```

SHOULD be designed so retries do not produce contradictory state.

---

# 93. Concurrency

The system MUST account for concurrent user operations.

Examples:

```text
two rating updates
watchlist add + remove
multiple recommendation requests
multiple memory updates
```

Database constraints and transaction boundaries should preserve consistent state.

---

# 94. Database Constraints

Important invariants SHOULD be enforced at the database level where practical.

Examples:

```text
one active rating per user/movie
one active watchlist relationship per user/movie
valid foreign-key relationships
unique provider identifiers
```

Business logic alone should not be trusted to enforce every invariant.

---

# 95. Domain Events

The application MAY use internal domain events to decouple follow-up work.

Example:

```text
RatingChanged
      ↓
update preference signal
      ↓
invalidate recommendation cache
      ↓
analytics processing
```

These events may initially be implemented through internal/background mechanisms rather than distributed event infrastructure.

---

# 96. Recommendation Cache Invalidation

Recommendation caches SHOULD be invalidated or refreshed after meaningful events such as:

* explicit rating
* explicit dislike
* watchlist changes where relevant
* user preference changes
* explicit memory changes
* major recommendation-model changes

The system SHOULD avoid unnecessary full-cache invalidation.

---

# 97. Cache Stampede Protection

Frequently requested cache keys SHOULD be protected against many simultaneous cache misses.

Possible strategies include:

* request coalescing
* short lock
* stale-while-revalidate
* background refresh

The chosen implementation should depend on actual workload.

---

# 98. API Security Boundary

Every externally reachable endpoint MUST:

1. validate input
2. authenticate when required
3. authorize resource access
4. enforce rate limits when applicable
5. avoid exposing internal implementation details

---

# 99. CORS and Browser Security

The backend MUST explicitly configure acceptable frontend origins.

Wildcard production CORS should not be used casually.

Security headers should be configured according to deployment architecture.

---

# 100. Dependency Boundary Rules

The following dependency rules are mandatory:

```text
Frontend
  → API contract
  → backend

API
  → application services

Application
  → domain

Infrastructure
  → domain/application interfaces

Domain
  → MUST NOT depend on infrastructure implementations
```

External provider SDKs should remain in infrastructure/provider modules.

---

# 101. No Circular Dependencies

Modules MUST NOT form cyclic dependency chains.

If two modules seem to require each other directly, introduce:

* a shared abstraction
* an application-level orchestration layer
* a domain event
* a carefully defined interface

rather than creating a circular import.

---

# 102. No Business Logic in UI

The frontend may:

* render state
* collect input
* perform client-side validation for UX
* request API operations

The frontend MUST NOT become the authority for:

* recommendation scoring
* authorization
* persistent memory policy
* data ownership
* hard recommendation filtering

---

# 103. No Business Logic in ORM Models

ORM models should represent persistence structure.

Core domain behavior SHOULD remain in domain/application components rather than becoming an uncontrolled collection of ORM methods.

---

# 104. No Raw Provider Leakage

TMDB and Gemini-specific response objects SHOULD NOT leak into:

* domain layer
* frontend
* persistence schema
* recommendation engine interfaces

Normalize them at the integration boundary.

---

# 105. No Direct LLM-to-Database Path

There MUST NOT be an architectural path equivalent to:

```text
Gemini
 ↓
database
```

The correct path is:

```text
Gemini
 ↓
application tool request
 ↓
application validation
 ↓
repository/service
 ↓
database
```

---

# 106. No Direct Frontend-to-Database Path

The frontend MUST NOT directly access PostgreSQL.

---

# 107. No Training During Recommendation Requests

The recommendation API MUST NOT train a full collaborative-filtering model synchronously as part of ordinary recommendation generation.

Training is an offline/background concern.

---

# 108. No Provider-Dependent Domain Models

A domain entity such as `Movie` should remain meaningful even if TMDB is replaced.

A recommendation should remain meaningful even if Gemini is replaced.

This is essential for long-term maintainability.

---

# 109. Documentation Requirements

Architecture-relevant changes SHOULD update:

* architecture documentation
* API contracts
* database documentation
* relevant ADRs
* operational documentation

The repository should never contain a fundamentally different architecture from the documented architecture without explanation.

---

# 110. Architectural Decision Records

Significant architectural changes MUST use ADRs.

Examples:

```text
ADR-001: Modular Monolith
ADR-002: PostgreSQL as Source of Truth
ADR-003: Redis for Caching and Jobs
ADR-004: Gemini Provider Abstraction
ADR-005: TMDB Provider Abstraction
ADR-006: PostgreSQL + pgvector
ADR-007: Offline Recommendation Training
```

An ADR should state:

```text
context
decision
alternatives considered
consequences
```

---

# 111. Testing Architecture

Testing should exist at multiple layers:

```text
unit
integration
contract
end-to-end
ML evaluation
```

The architecture should make components testable independently.

External providers SHOULD have mock/fake implementations.

Example:

```text
MovieDataProvider
├── TMDBProvider
└── FakeMovieDataProvider
```

Similarly:

```text
LLMProvider
├── GeminiProvider
└── FakeLLMProvider
```

---

# 112. Contract Testing

The frontend/backend contract SHOULD be tested sufficiently to detect:

* schema drift
* missing fields
* incompatible response changes
* invalid enum/value assumptions

---

# 113. ML Evaluation as a First-Class Layer

Recommendation model quality MUST be evaluated independently of UI functionality.

A model can be:

```text
technically functional
```

while:

```text
recommendation quality is poor
```

Therefore ML evaluation is an independent engineering concern.

---

# 114. Production Data vs Training Data

Application data and training datasets should be conceptually separate.

```text
PostgreSQL production interactions
        ↓
training data extraction
        ↓
validated dataset
        ↓
model training
```

The training pipeline should not arbitrarily mutate production transactional data.

---

# 115. Data Privacy in ML

Only data necessary for model training should be incorporated.

The system SHOULD avoid retaining unnecessary raw conversation content in training datasets.

User deletion requirements should be considered when maintaining derived personalization artifacts.

---

# 116. Model Artifact Storage

Model artifacts should be stored separately from transactional database records.

Conceptually:

```text
model artifact
+
metadata
```

The exact object storage mechanism can initially be local/filesystem or another low-cost storage solution.

The application should retain model metadata separately.

---

# 117. Startup Behavior

On startup, the backend SHOULD:

1. load configuration
2. initialize database connections
3. initialize Redis connection
4. initialize required provider clients
5. load active recommendation model if configured
6. verify critical readiness conditions
7. expose readiness

Startup should fail clearly if an essential dependency cannot be initialized.

---

# 118. Graceful Shutdown

The application SHOULD:

* finish or cancel in-flight work safely
* release resources
* close database connections
* close Redis connections
* stop accepting new work before termination

Workers should similarly handle shutdown signals gracefully.

---

# 119. Deployment Environments

At minimum:

```text
development
test
production
```

A staging environment MAY be added later.

Configuration SHOULD differ by environment through environment variables/configuration management rather than source-code conditionals.

---

# 120. Production Architecture Target

The initial production deployment may remain relatively simple:

```text
                    Internet
                       │
                       ▼
                 Reverse Proxy
                       │
          ┌────────────┴─────────────┐
          ▼                          ▼
      Next.js                    FastAPI
                                     │
                       ┌─────────────┼──────────────┐
                       ▼             ▼              ▼
                  PostgreSQL       Redis       Workers
                       │             │
                       │             │
                       └──────┬──────┘
                              ▼
                     Recommendation Engine
```

The exact hosting provider is intentionally left to the deployment document.

---

# 121. Future Service Extraction

The following modules are the most plausible candidates for future extraction if scale justifies it:

### Recommendation Service

Because recommendation compute can have very different resource characteristics.

### ML Training Service

Because training may require different dependencies and compute.

### Search Service

If search requirements outgrow PostgreSQL.

### Analytics Pipeline

If analytical workloads become large enough to impact transactional performance.

The system should not extract these prematurely.

---

# 122. Future Distributed Architecture

Only after actual scaling pressure may the architecture evolve toward:

```text
                         API Gateway
                              │
          ┌───────────────────┼──────────────────┐
          ▼                   ▼                  ▼
       User API         Recommendation API    Movie API
                              │
                    ┌─────────┼──────────┐
                    ▼         ▼          ▼
                  CF      Semantic     Ranking
                Retrieval Retrieval     Model
                    │         │          │
                    └─────────┼──────────┘
                              ▼
                         Redis / Cache

                 Event / Analytics Pipeline
                              │
                              ▼
                        Data Warehouse
```

This is explicitly a future architecture, not an MVP requirement.

---

# 123. Architectural North Star

The architecture must preserve this separation:

```text
             ┌──────────────────────┐
             │       HUMAN          │
             │    says what they    │
             │       want           │
             └──────────┬───────────┘
                        │
                        ▼
                   Gemini / LLM
                        │
                 Understand intent
                        │
                        ▼
               Structured Context
                        │
                        ▼
            ┌───────────────────────┐
            │ Recommendation Engine │
            │                       │
            │ CF                    │
            │ Semantic Retrieval    │
            │ Context               │
            │ Filtering             │
            │ Ranking               │
            │ Diversity             │
            └───────────┬───────────┘
                        │
                        ▼
                      Movies
                        │
                        ▼
                       TMDB
                  metadata / facts
```

The LLM interprets.

The recommendation system ranks.

The movie provider supplies facts.

The database remembers.

The frontend presents.

---

# 124. Final Architectural Contract

The following architectural rules are mandatory for CineRec.

1. CineRec begins as a modular monolith.
2. PostgreSQL is the authoritative persistent datastore.
3. Redis is ephemeral/cache infrastructure, not the source of truth.
4. The frontend communicates with the backend through explicit APIs.
5. FastAPI owns application orchestration.
6. SQLAlchemy owns database persistence access.
7. Alembic owns database schema migrations.
8. External providers are accessed through adapters.
9. Gemini is accessed through an LLM abstraction.
10. TMDB is accessed through a movie-data abstraction.
11. LLM output is untrusted and must be validated.
12. The LLM cannot directly access the database.
13. The frontend cannot directly access the database.
14. Recommendation generation is separated from conversation.
15. Collaborative filtering remains independently replaceable.
16. Training never occurs synchronously inside ordinary recommendation requests.
17. Hard constraints are enforced by application logic, not merely by the LLM.
18. Explicit user preferences override weaker inferred preferences.
19. Session context is distinct from persistent memory.
20. Recommendation requests are identifiable and attributable.
21. Important user operations are idempotent.
22. Large collections are paginated.
23. N+1 query patterns are prohibited.
24. Provider failures should degrade gracefully.
25. Secrets remain server-side.
26. API contracts are explicit and versioned.
27. Major architectural changes require ADRs.
28. New infrastructure must have a demonstrated reason.
29. The initial design must remain viable under a low/zero-budget strategy.
30. Every architectural decision must preserve the ability to evolve the recommendation system without rewriting the product.

---

# 125. Canonical Data / Control Flow

The canonical end-to-end interaction is:

```text
USER
  ↓
Next.js Orb
  ↓
FastAPI
  ↓
Conversation Orchestrator
  ↓
Gemini
  ↓
Structured Cinematic Intent
  ↓
Context Builder
  ├── Session intent
  ├── Explicit memory
  ├── Long-term taste
  ├── Behavioral signals
  ├── Constraints
  └── Availability
  ↓
Recommendation Engine
  ├── Collaborative Filtering
  ├── Semantic Retrieval
  ├── Popularity
  └── Exploration
  ↓
Candidate Union
  ↓
Hard Filtering
  ↓
Ranking
  ↓
Diversity / Exploration
  ↓
Recommendation Set
  ↓
TMDB Metadata Enrichment
  ↓
FastAPI Response
  ↓
Next.js
  ↓
Orb + Recommendation Cards
  ↓
User Interaction
  ↓
Interaction API
  ↓
PostgreSQL
  ↓
Preference / Cache Updates
  ↓
Future Recommendations
```

This is the canonical architectural flow against which implementation decisions should be evaluated.

If an implementation substantially deviates from this flow, the deviation should be documented and justified through an architectural decision record.

