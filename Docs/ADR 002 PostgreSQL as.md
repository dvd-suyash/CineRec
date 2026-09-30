# ADR-002 — PostgreSQL as the Primary Database

**Status:** Accepted
**Date:** 2026-09-28
**Decision Owners:** CineRec Engineering
**Scope:** Primary persistent data store for CineRec

---

## 1. Decision Summary

CineRec will use **PostgreSQL as its primary and authoritative database** for all durable application data.

PostgreSQL will serve as the system of record for:

* users and identities
* user profiles
* movies and provider metadata
* genres, keywords, credits, and relationships
* ratings and preferences
* watchlists
* viewing history
* user interactions
* conversations and messages
* conversation intents
* memories and memory evidence
* taste profiles
* embeddings
* recommendation requests and results
* model metadata
* experiments and experiment assignments
* other application data requiring durable persistence

PostgreSQL will also provide capabilities needed by CineRec's personalization workload, including:

* relational transactions
* foreign keys and constraints
* indexing
* JSONB where justified
* full-text search
* trigram-based search
* vector storage through **pgvector**
* aggregation and analytical queries over application data

Redis will remain a **cache and ephemeral infrastructure component**, not the authoritative data store.

---

# 2. Context

CineRec has several fundamentally different classes of data.

Some data represents durable application state:

```text
User
Movie
Rating
Watchlist
Memory
Conversation
Recommendation
Taste Profile
```

Some data is generated from events or interactions:

```text
click
search
view
skip
rate
like
dislike
watchlist_add
recommendation_impression
recommendation_selection
```

Some data is derived:

```text
taste profile
embeddings
recommendation candidates
similarity features
aggregated statistics
```

The system therefore needs a database that can simultaneously support:

1. **Strong relational integrity**
2. **Transactional updates**
3. **Flexible application metadata**
4. **Efficient querying**
5. **Personalization workloads**
6. **Search**
7. **Vector similarity**
8. **Future analytical workloads**
9. **A low operational burden**
10. **A clear migration path as CineRec scales**

The project is intentionally being built with a low infrastructure budget and a modular-monolith architecture.

Introducing multiple databases at the beginning would create operational and consistency complexity before the workload justifies it.

---

# 3. Considered Alternatives

The following architectures were considered.

### Option A — PostgreSQL

```text
Application
    ↓
PostgreSQL
```

Advantages:

* mature relational database
* ACID transactions
* strong constraints
* excellent ecosystem
* sophisticated indexing
* support for structured and semi-structured data
* supports full-text search
* supports trigram search
* pgvector enables vector similarity inside PostgreSQL
* excellent integration with Python and SQLAlchemy
* straightforward local development
* managed hosting widely available
* can scale vertically and horizontally through established patterns
* allows many CineRec workloads to remain in one consistency boundary

Disadvantages:

* not optimized for every specialized workload
* very large-scale search may eventually require a dedicated search engine
* very large recommendation workloads may eventually justify specialized infrastructure
* analytical workloads may eventually require a warehouse/lakehouse

**Decision:** Selected.

---

### Option B — MongoDB

Potentially useful for highly flexible documents and rapidly changing schemas.

However, CineRec contains substantial relational structure:

```text
users
    ↓
ratings
    ↓
movies

movies
    ↓
genres
    ↓
keywords
    ↓
credits

users
    ↓
memories
    ↓
memory_evidence

users
    ↓
recommendation_requests
    ↓
recommendation_items
```

These relationships benefit from relational constraints, joins, transactions, and explicit schema ownership.

MongoDB would also introduce a separate solution for capabilities already available within PostgreSQL.

**Decision:** Rejected as the primary database.

---

### Option C — MySQL

MySQL is capable of handling CineRec's relational workload.

However, PostgreSQL provides a broader feature set that aligns particularly well with CineRec's combination of:

* relational application state
* JSONB
* full-text search
* trigram search
* vector storage through pgvector
* complex analytical queries

Using PostgreSQL also avoids having to introduce another technology when vector capabilities become part of the core recommendation architecture.

**Decision:** Rejected in favor of PostgreSQL.

---

### Option D — Multiple Specialized Databases

Example:

```text
PostgreSQL
+ Redis
+ Elasticsearch
+ Vector DB
+ Data Warehouse
```

This can become an appropriate architecture at significant scale.

At CineRec's initial scale, however, this would introduce:

* more infrastructure
* more operational work
* more failure modes
* synchronization problems
* additional backup requirements
* more complicated local development
* more complex observability
* higher hosting costs

The architecture should therefore begin with fewer systems and introduce specialized infrastructure only when measurable requirements justify it.

**Decision:** Rejected initially.

---

# 4. Decision

CineRec will use PostgreSQL as the **single authoritative persistent database**.

The application will interact with PostgreSQL primarily through:

```text
FastAPI
    ↓
Application Services
    ↓
Repositories / Data Access Layer
    ↓
SQLAlchemy 2
    ↓
PostgreSQL
```

Database schema changes will be managed through:

```text
Alembic migrations
```

PostgreSQL is the **source of truth**.

Derived data may be regenerated from authoritative state where practical.

---

# 5. Database Responsibilities

PostgreSQL owns durable application state.

## 5.1 Identity and User Data

PostgreSQL stores:

```text
users
user_identities
user_profiles
```

The authentication provider may manage authentication credentials and OAuth mechanics.

CineRec's application database remains responsible for application-level user state.

The application must not rely on authentication-provider database APIs as its primary application data-access abstraction.

---

## 5.2 Movie Catalog

PostgreSQL stores normalized movie information obtained from the movie-data provider.

Example entities:

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

External provider identifiers must be stored explicitly.

Example:

```text
movie_id                → CineRec internal ID
provider                → TMDB
provider_movie_id       → external TMDB ID
```

Internal references should use CineRec identifiers rather than making the external provider ID the primary application identity.

---

## 5.3 User Activity

Durable user interactions belong in PostgreSQL.

Examples:

```text
ratings
movie_preferences
watchlists
viewing_history
interactions
```

Raw interaction history should remain available for:

* recommendation algorithms
* behavioral analysis
* model training
* debugging
* experimentation
* personalization
* recommendation attribution

Interaction events should not be overwritten merely because derived user state changes.

---

## 5.4 Conversation Data

Persistent conversation state belongs in PostgreSQL.

Examples:

```text
conversation_sessions
conversation_messages
conversation_intents
```

The system should distinguish:

```text
Raw conversation history
        ↓
Extracted intent
        ↓
Memory candidate
        ↓
Persisted memory
```

Conversation storage must not automatically imply that every conversational statement becomes permanent memory.

---

## 5.5 Memory

Long-term user memory belongs in PostgreSQL.

Example structure:

```text
memories
memory_evidence
```

The database must preserve sufficient provenance to distinguish:

```text
USER_EXPLICIT
BEHAVIOR_INFERRED
CONVERSATION_INFERRED
SYSTEM_DERIVED
```

Memory state must remain independently queryable, editable, disableable, and deletable.

---

## 5.6 Recommendation Data

Recommendation requests and their outputs should be persisted when required for:

* recommendation history
* analytics
* evaluation
* debugging
* attribution
* model comparison
* reproducibility

Example:

```text
recommendation_requests
    ↓
recommendation_items
```

A recommendation item should retain sufficient context to understand why it was produced.

Relevant metadata may include:

```text
model_version
ranker_version
profile_version
request_context
candidate_source
ranking_score
explanation_metadata
created_at
```

This allows recommendation behavior to be investigated after the fact.

---

# 6. Transactions and Consistency

PostgreSQL transactions will protect operations where multiple writes must remain consistent.

Example:

```text
Add movie to watchlist
        ↓
Create watchlist row
        ↓
Create interaction event
        ↓
Update relevant derived state
```

Where atomicity is required, these operations should occur within an appropriate database transaction.

The system must avoid distributed transactions across external systems whenever possible.

For example:

```text
PostgreSQL transaction
        ↓
commit
        ↓
publish asynchronous event
```

is preferable to attempting to create a transaction spanning:

```text
PostgreSQL
+
Redis
+
Gemini
+
TMDB
```

External API calls should not be treated as part of a PostgreSQL transaction unless there is a specific and justified design requiring that behavior.

---

# 7. Schema Design Principles

## 7.1 Relational Modeling First

Core entities should be represented using explicit relational tables.

Avoid storing the entire application model inside one large JSON document.

Prefer:

```text
movies
genres
movie_genres
```

over:

```text
movies {
    genres: [...]
}
```

for data that requires relational integrity and efficient querying.

---

## 7.2 JSONB for Flexible Data

JSONB is allowed where schema flexibility provides genuine value.

Appropriate examples include:

```text
recommendation context
provider-specific metadata
LLM structured metadata
experiment configuration
model configuration
extensible event payloads
```

JSONB must not become a substitute for relational modeling.

A field that is:

* frequently queried
* indexed
* constrained
* joined
* required for application logic

should generally be modeled explicitly.

---

## 7.3 Foreign Keys

Foreign keys should be used to protect important relationships.

Example:

```text
ratings.user_id
    → users.id

ratings.movie_id
    → movies.id
```

Referential integrity should be enforced by the database rather than relying solely on application code.

---

## 7.4 Constraints

Where practical, business invariants should be represented through:

* primary keys
* foreign keys
* unique constraints
* check constraints
* not-null constraints

Example:

A user should not accidentally have multiple active ratings for the same movie when the product model specifies one current rating.

The exact constraint should match the domain semantics rather than being inferred from implementation convenience.

---

# 8. Identifier Strategy

CineRec will use application-level UUID identifiers for major entities.

Preferred identifier strategy:

```text
UUIDv7 where supported
```

otherwise an appropriate UUID implementation.

External provider IDs must not be assumed to be globally unique across providers.

Example:

```text
provider = "tmdb"
provider_id = "12345"
```

and:

```text
provider = "future_provider"
provider_id = "12345"
```

must be capable of representing two distinct external identities.

---

# 9. Time and Timestamps

All server-side timestamps will be stored using timezone-aware database timestamps and interpreted in **UTC**.

Examples:

```text
created_at
updated_at
watched_at
rated_at
expires_at
superseded_at
```

The frontend may convert timestamps to the user's local timezone for display.

Business logic should not depend on client-provided timestamps when server-side timestamps are authoritative.

---

# 10. Indexing Strategy

Indexes will be driven by measured query patterns.

The project must not blindly index every column.

Likely index categories include:

```text
foreign-key lookups
unique identifiers
user + movie combinations
user activity timelines
movie provider IDs
recommendation history
memory retrieval
conversation history
search fields
timestamp-based queries
```

Specialized indexes may be introduced for:

* full-text search
* trigram search
* vector similarity
* partial queries
* composite filtering

Index decisions should be based on:

```text
query frequency
query latency
table size
write overhead
execution plans
```

rather than assumptions.

---

# 11. Search Strategy

PostgreSQL will initially provide CineRec's search functionality.

The initial search architecture is:

```text
Movie Search Request
        ↓
PostgreSQL
        ├── Full-Text Search
        ├── pg_trgm
        └── Structured Filters
```

This is sufficient for the initial movie-search workload.

A dedicated search engine such as Elasticsearch/OpenSearch should not be introduced merely because it is commonly used in large systems.

Migration to a dedicated search system becomes justified when measured requirements demonstrate that PostgreSQL search is no longer sufficient.

---

# 12. Vector Storage

Movie and user embeddings may be stored using **pgvector**.

Conceptually:

```text
movies
    └── embedding

users
    └── embedding
```

This allows the recommendation system to combine:

```text
relational filtering
+
metadata
+
behavioral signals
+
vector similarity
```

without requiring an immediately separate vector database.

The pgvector decision is formally documented separately in:

```text
ADR-003-pgvector.md
```

PostgreSQL remains the authoritative persistence layer even when vector retrieval is used.

---

# 13. Redis Boundary

Redis is explicitly **not** the source of truth.

Redis may store:

```text
API cache
TMDB responses
recommendation cache
session-related ephemeral state
rate-limit counters
Celery broker data
short-lived distributed coordination data
```

Durable application state must remain recoverable from PostgreSQL.

Therefore:

```text
PostgreSQL failure
→ application cannot safely operate on durable state

Redis failure
→ application should degrade or rebuild cache/queue state where possible
```

The exact durability characteristics of individual Redis workloads must be documented rather than assumed.

---

# 14. Derived Data

Some PostgreSQL data is authoritative.

Some PostgreSQL data is derived.

Examples of derived data:

```text
taste_profiles
user_embeddings
movie_embeddings
aggregated recommendation statistics
certain recommendation features
```

Derived data should be designed to be:

```text
rebuildable
versioned
recomputable
replaceable
```

The system should avoid making irreversible decisions based solely on a derived artifact when the underlying source interactions are still available.

Example:

```text
ratings + interactions
        ↓
recompute taste profile
```

rather than treating the taste profile as the only record of user behavior.

---

# 15. Data Lifecycle

Different classes of data may have different retention policies.

Examples:

```text
Current user state
    → durable

Interaction history
    → durable according to product retention policy

Conversation history
    → durable according to privacy/retention policy

Caches
    → ephemeral

Embeddings
    → rebuildable

Recommendation caches
    → rebuildable
```

Deletion operations must account for:

* foreign-key dependencies
* privacy requirements
* derived data
* caches
* asynchronous jobs
* embeddings
* recommendation history

Deleting a user must not leave unauthorized orphaned user data elsewhere in the system.

---

# 16. Backup and Recovery

PostgreSQL is the system of record and therefore requires explicit backup and recovery procedures.

Production configuration must provide:

```text
automated backups
point-in-time recovery where supported
restore procedures
backup verification
retention policy
recovery documentation
```

Backups are not considered valid merely because they were successfully created.

At least periodically, restoration must be tested.

Relevant operational targets should eventually be defined as:

```text
RPO — Recovery Point Objective
RTO — Recovery Time Objective
```

These values may initially be modest and should evolve with product requirements.

---

# 17. Connection Management

The application must avoid uncontrolled database connections.

The deployment architecture should use:

```text
connection pooling
bounded worker concurrency
appropriate pool sizing
timeouts
health checks
```

Database capacity must be considered across:

```text
API processes
Celery workers
background jobs
administrative processes
migration processes
```

The total possible connection count must remain within the database's operational limits.

---

# 18. Database Access Boundary

Application routes must not contain arbitrary SQL and business logic mixed together.

Preferred structure:

```text
API Route
    ↓
Application Service
    ↓
Repository / Domain Service
    ↓
SQLAlchemy
    ↓
PostgreSQL
```

This maintains the architectural boundary defined in ADR-001.

The following is prohibited:

```text
HTTP route
    ↓
raw SQL
    ↓
business decision
    ↓
response
```

unless there is a clearly documented exception for a specialized query.

---

# 19. SQLAlchemy

The Python backend will use **SQLAlchemy 2** as the application's database abstraction.

Responsibilities include:

* database connectivity
* ORM mapping where appropriate
* query construction
* transaction management
* relationship handling
* connection pooling integration
* database-level operations

SQLAlchemy should not hide important database behavior unnecessarily.

For performance-sensitive queries, explicit SQL or carefully constructed SQLAlchemy queries may be used.

The abstraction must serve the database design rather than obscure it.

---

# 20. Alembic Migrations

All schema changes must be tracked through **Alembic migrations**.

Examples:

```text
create table
add column
remove column
add index
change constraint
create extension
alter type
```

Developers must not treat manual production schema modifications as the normal migration mechanism.

Migration requirements:

1. Every schema change has a migration.
2. Migrations are committed to version control.
3. CI validates migrations.
4. Production migrations are executed through the deployment process.
5. Destructive changes require additional review.
6. Expand/contract techniques should be used when a migration could break running application versions.

---

# 21. Zero-Downtime Schema Evolution

When deployment involves multiple application versions, database changes must be compatible with both the previous and new application versions whenever practical.

Preferred pattern:

```text
Phase 1
Add compatible schema

        ↓

Phase 2
Deploy application that understands new schema

        ↓

Phase 3
Migrate/backfill data

        ↓

Phase 4
Remove obsolete behavior/schema
```

Avoid deployments that require:

```text
database schema change
+
application replacement
```

to occur as one irreversible operation.

---

# 22. Concurrency

The system must account for concurrent requests.

Examples include:

```text
two simultaneous rating updates
two watchlist requests
duplicate interaction events
concurrent recommendation requests
multiple workers processing the same job
```

Concurrency protection may use:

* database constraints
* transactions
* row-level locking where necessary
* idempotency keys
* unique indexes
* optimistic concurrency mechanisms
* application-level coordination

Application code must not assume that a prior read guarantees that a subsequent write is still valid.

---

# 23. Recommendation-System Integration

PostgreSQL is the primary persistence layer for recommendation-related state, but PostgreSQL is **not itself the recommendation engine**.

The architecture remains:

```text
PostgreSQL
   ↓
User / Movie / Interaction Data
   ↓
Recommendation Engine
   ↓
Candidates
   ↓
Ranking
   ↓
Recommendation Results
   ↓
PostgreSQL
```

The database stores the data required by the recommendation system.

The recommendation engine owns recommendation logic.

This separation prevents database queries from becoming a hidden implementation of recommendation algorithms.

---

# 24. ML Training Boundary

Model training must not occur inside normal HTTP requests.

Preferred architecture:

```text
PostgreSQL
    ↓
Training Dataset Builder
    ↓
ML Training Job
    ↓
Model Artifact
    ↓
Model Registry / Version Metadata
    ↓
Inference
```

Production inference may read required features from PostgreSQL or other explicitly defined stores.

Training workloads may eventually require:

* object storage
* feature storage
* data warehouses
* distributed compute

but these should be introduced only when justified by dataset size and training requirements.

---

# 25. Scaling Strategy

PostgreSQL is expected to scale through stages.

### Stage 1 — Local Development

```text
Docker Compose
    ↓
PostgreSQL
```

### Stage 2 — Initial Production

```text
Managed PostgreSQL
```

### Stage 3 — Increased Workload

Potential improvements:

```text
larger database instance
better indexes
query optimization
connection pooling
caching
read replicas where justified
partitioning where justified
```

### Stage 4 — Specialized Workloads

Only after measurable pressure:

```text
PostgreSQL
+
dedicated search infrastructure
+
analytical warehouse
+
specialized recommendation infrastructure
```

PostgreSQL is therefore not considered permanently sufficient for every possible future workload.

It is the correct **initial system of record** and the default database until measurements demonstrate otherwise.

---

# 26. Partitioning

Partitioning must not be introduced preemptively.

Potential future candidates include very large append-oriented tables such as:

```text
interactions
viewing_history
conversation_messages
```

Partitioning becomes appropriate only after observing:

* table growth
* query patterns
* maintenance costs
* index size
* retention requirements
* vacuum behavior
* actual performance limitations

A large table by itself is not sufficient justification for partitioning.

---

# 27. Read and Write Patterns

The architecture should distinguish between:

```text
transactional writes
```

and:

```text
read-heavy workloads
```

Caching may reduce repeated reads.

Materialized or precomputed data may be introduced for expensive recurring queries.

However, the initial design should prefer simple indexed PostgreSQL queries before introducing additional read models.

---

# 28. Failure and Degradation

The application must define behavior for database failures.

When PostgreSQL is unavailable:

```text
writes → fail safely
durable state mutations → fail closed
```

Some read-only experiences may be served from cache when appropriate, but cached data must not be represented as current authoritative state without an explicit freshness model.

The system must never silently acknowledge a write that was not durably persisted.

---

# 29. Security Requirements

PostgreSQL security must include:

* credentials stored as secrets
* TLS for remote database connections where applicable
* least-privilege database roles
* no database exposure to the public internet unless explicitly secured
* parameterized queries
* protection against SQL injection
* appropriate network controls
* encrypted backups
* restricted administrative access
* auditability of sensitive administrative actions

The application must never expose database credentials to the frontend.

---

# 30. Observability

Database behavior must be observable through application and infrastructure telemetry.

Important measurements include:

```text
query latency
query error rate
connection pool utilization
active connections
transaction duration
lock contention
slow queries
cache hit ratio where relevant
database CPU
memory utilization
storage utilization
IO pressure
```

Slow or inefficient queries must be investigated using actual query plans and production-like workloads.

The system should avoid collecting excessive high-cardinality database metrics that create an observability problem of their own.

---

# 31. Testing Requirements

Database behavior must be tested against **real PostgreSQL** for integration tests.

SQLite should not be treated as a drop-in substitute for PostgreSQL when PostgreSQL-specific semantics matter.

Tests must cover:

```text
schema creation
migrations
constraints
transactions
foreign keys
unique constraints
concurrent operations
repository behavior
authorization boundaries
pagination
search
vector queries
deletion behavior
rollback behavior
```

Representative production-like indexes and schema should be present in integration environments.

---

# 32. Local Development

Developers should be able to start PostgreSQL locally using Docker Compose.

Expected developer experience:

```text
docker compose up -d postgres
```

The local database must support the same important PostgreSQL features relied upon in development and testing.

Database initialization and migrations must be reproducible.

Developers should not need manually configured local database state to run the application.

---

# 33. Why PostgreSQL Fits CineRec

CineRec has an unusual combination of workloads for a relatively small application:

```text
Transactional Application
        +
Search
        +
Personalization
        +
Vector Similarity
        +
Behavioral Data
        +
Recommendation Metadata
        +
Analytics
```

PostgreSQL allows these workloads to coexist within a single consistency boundary.

This is especially important during early product development because the engineering team can focus on product and recommendation quality rather than maintaining a collection of infrastructure systems.

---

# 34. What This Decision Does Not Mean

Choosing PostgreSQL does **not** mean:

> "PostgreSQL must solve everything forever."

The decision means:

> "PostgreSQL is the authoritative persistence layer until a measured requirement justifies introducing another system."

CineRec may eventually introduce:

```text
Dedicated Search Engine
Data Warehouse
Object Storage
Feature Store
Specialized Recommendation Service
Distributed Compute
```

Each addition should be justified by workload characteristics rather than architectural fashion.

---

# 35. Conditions for Reconsideration

This ADR should be reconsidered when one or more of the following become true:

### Search

PostgreSQL search can no longer meet required:

```text
latency
relevance
throughput
ranking
```

requirements.

### Recommendation

Recommendation workloads require infrastructure that cannot efficiently operate within the application/database architecture.

### Analytics

Analytical workloads materially interfere with transactional application workloads.

### Data Volume

Dataset size or growth creates measurable problems involving:

```text
storage
index size
vacuuming
query latency
maintenance
backup duration
```

### Availability

The required availability architecture exceeds the capabilities or operational model of the current PostgreSQL deployment.

### Organizational Scale

Independent teams require independent data ownership and deployment boundaries.

At that point, the architecture should evolve deliberately rather than through ad hoc infrastructure additions.

---

# 36. Rejected Patterns

The following patterns are explicitly rejected during the initial architecture phase:

```text
PostgreSQL + MongoDB "just in case"
PostgreSQL + Elasticsearch "from day one"
PostgreSQL + dedicated vector DB "because embeddings exist"
Redis as primary persistent storage
Database-per-feature
Database-per-table
Raw SQL embedded throughout API routes
Manual production schema changes
Unbounded JSONB application models
Unindexed high-volume access patterns
Premature database sharding
Premature partitioning
Premature read replicas
```

These may become valid later, but only under documented requirements.

---

# 37. Consequences

## Positive Consequences

CineRec gains:

* one authoritative source of truth
* strong transactional consistency
* relational integrity
* a mature SQL ecosystem
* efficient application querying
* simpler local development
* lower infrastructure cost
* fewer distributed-system failure modes
* straightforward SQLAlchemy integration
* straightforward Alembic migration workflow
* compatibility with pgvector
* search capabilities without another service
* simpler backup and recovery
* easier debugging
* simpler observability

---

## Negative Consequences

CineRec accepts that:

* PostgreSQL will not be optimal for every future workload
* very large search workloads may eventually require a dedicated search system
* very large-scale analytics may need a separate analytical store
* recommendation infrastructure may eventually require independent scaling
* database performance becomes an important architectural consideration
* careful schema and index design will be necessary as data grows

These are accepted tradeoffs.

---

# 38. Relationship to Other ADRs

This ADR depends on and reinforces:

```text
ADR-001-modular-monolith.md
```

Related decisions include:

```text
ADR-003-pgvector.md
```

Future ADRs may address:

```text
Redis
Celery
authentication provider
TMDB integration
Gemini integration
model registry
search architecture
analytics architecture
object storage
```

---

# 39. Migration / Evolution Path

The intended evolution is:

```text
PostgreSQL
     ↓
Optimize schema and indexes
     ↓
Introduce caching
     ↓
Introduce read replicas if justified
     ↓
Isolate heavy workloads
     ↓
Add specialized stores where required
     ↓
Extract independent services where justified
```

The database architecture should evolve in response to measured workload characteristics.

---

# 40. Final Principle

> **PostgreSQL is CineRec's source of truth and default persistence layer. Keep the data model relational, keep derived data rebuildable, and introduce specialized databases only when measurable workload requirements justify them.**

