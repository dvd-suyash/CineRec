# ADR-003 — pgvector for Vector Search and Embeddings

**Status:** Accepted
**Date:** 2026-09-28
**Decision Owners:** CineRec Engineering
**Scope:** Vector storage and vector similarity retrieval

---

# 1. Decision Summary

CineRec will use **pgvector as its initial vector storage and similarity-search layer inside PostgreSQL**.

Embeddings will be stored alongside the application's authoritative relational data where appropriate.

The initial architecture is:

```text
                 PostgreSQL
 ┌─────────────────────────────────────────┐
 │                                         │
 │  Relational Data                        │
 │  ├── Users                              │
 │  ├── Movies                             │
 │  ├── Interactions                       │
 │  ├── Ratings                            │
 │  └── Preferences                         │
 │                                         │
 │  Vector Data                             │
 │  ├── Movie Embeddings                    │
 │  └── User Embeddings                     │
 │                                         │
 │  pgvector                                │
 │  ├── Similarity Search                   │
 │  └── Approximate NN Indexes              │
 │                                         │
 └─────────────────────────────────────────┘
```

The initial approximate nearest-neighbor strategy will use **HNSW** where the workload benefits from it.

**IVFFlat remains an available alternative** when its build, memory, or operational characteristics are more appropriate for a particular workload.

pgvector currently supports vector, half-precision, binary, and sparse vector types, along with HNSW and IVFFlat indexing and multiple distance functions.

A dedicated vector database will **not** be introduced during the initial architecture phase.

---

# 2. Context

CineRec uses embeddings for semantic personalization.

Potential embeddings include:

```text
Movie Embedding
User Taste Embedding
Conversation / Query Embedding
Future Semantic Memory Embedding
```

These embeddings enable capabilities such as:

```text
movie-to-movie similarity
user-to-movie similarity
semantic candidate retrieval
taste-space exploration
semantic memory retrieval
hybrid recommendation
```

The vector data is tightly coupled to the application's existing relational data.

For example:

```text
User
 ├── ratings
 ├── viewing history
 ├── preferences
 ├── interactions
 └── embedding

Movie
 ├── genres
 ├── keywords
 ├── credits
 ├── metadata
 └── embedding
```

Introducing a separate vector database would therefore create an additional synchronization boundary for data that is already naturally related.

CineRec's current requirements do not justify that additional distributed-system complexity.

---

# 3. Problem Statement

The recommendation system needs to answer queries such as:

```text
"Find movies semantically similar to this movie."

"Find movies close to this user's current taste representation."

"Find movies matching this natural-language request."

"Find memories semantically relevant to the current conversation."
```

A vector search layer must provide:

1. efficient similarity search
2. predictable latency
3. filtering alongside vector retrieval
4. integration with relational metadata
5. manageable operational complexity
6. reproducible behavior
7. low infrastructure cost
8. a path to scale

PostgreSQL + pgvector provides these capabilities without requiring another primary data system.

pgvector supports vector similarity operators and approximate indexes directly in PostgreSQL.

---

# 4. Considered Alternatives

## Option A — pgvector inside PostgreSQL

```text
Application
      ↓
PostgreSQL
      ├── relational data
      └── pgvector
```

Advantages:

* one authoritative persistence layer
* SQL joins between vector results and relational metadata
* transactional consistency with application data
* fewer infrastructure components
* simpler local development
* lower operational cost
* straightforward backups
* integrates naturally with SQLAlchemy/PostgreSQL
* supports exact and approximate nearest-neighbor search
* supports filtering during retrieval
* enables hybrid SQL + vector queries

**Decision:** Selected.

---

## Option B — Dedicated Vector Database

Examples include specialized vector-search systems designed primarily for approximate nearest-neighbor retrieval.

Potential advantages:

* specialized vector infrastructure
* independent scaling
* potentially better behavior at very large vector volumes
* specialized operational features

Disadvantages for the initial CineRec architecture:

* additional infrastructure
* separate availability boundary
* additional synchronization
* additional authentication and networking
* more complicated local development
* additional backup and recovery concerns
* duplicated identifiers and metadata
* increased operational cost

**Decision:** Rejected initially.

---

## Option C — Elasticsearch/OpenSearch as Vector Store

A search engine could provide:

```text
lexical search
+
vector search
+
filtering
```

This becomes attractive when full-text and semantic search workloads become large enough to justify specialized search infrastructure.

However, CineRec does not initially need a second search/data platform.

PostgreSQL already provides relational search capabilities and pgvector provides vector similarity.

**Decision:** Rejected initially.

---

## Option D — Application-Memory Vector Search

The system could load vectors into application memory and perform similarity calculations directly.

This is useful for:

* prototypes
* very small datasets
* offline experimentation

It is not appropriate as CineRec's authoritative production retrieval layer because:

* vectors must be loaded into each process
* memory usage scales with dataset size
* multiple API instances duplicate data
* restarts require reloads
* filtering becomes more complicated
* synchronization becomes harder
* horizontal scaling becomes inefficient

**Decision:** Rejected for production.

---

# 5. Decision

CineRec will store production embeddings in PostgreSQL using pgvector.

The vector layer is treated as a **capability of PostgreSQL**, not as a separate application service.

The conceptual architecture is:

```text
Recommendation Engine
        ↓
Vector Repository
        ↓
PostgreSQL + pgvector
```

The recommendation engine does not depend directly on pgvector-specific SQL throughout the codebase.

Instead:

```text
Recommendation Engine
        ↓
Vector Retrieval Interface
        ↓
PostgreSQL Vector Adapter
        ↓
pgvector
```

This preserves the ability to replace the implementation later.

---

# 6. Responsibilities

pgvector is responsible for:

```text
vector storage
distance calculations
nearest-neighbor retrieval
approximate nearest-neighbor indexing
vector-oriented SQL operators
```

The recommendation engine remains responsible for:

```text
candidate generation
candidate union
hard filtering
ranking
diversity
exploration
recommendation policy
```

The LLM remains responsible for:

```text
natural-language understanding
intent extraction
reference resolution
conversation
explanations
```

Therefore:

```text
LLM
 ≠
Vector Search
 ≠
Recommendation Ranking
```

---

# 7. Embedding Model Boundary

Embeddings are generated by a dedicated embedding component.

Conceptually:

```text
Movie / User / Query
        ↓
Embedding Provider
        ↓
Vector
        ↓
PostgreSQL + pgvector
```

The embedding provider must be abstracted.

Example:

```python
class EmbeddingProvider(Protocol):
    async def embed_text(self, text: str) -> list[float]:
        ...
```

This prevents the database layer from becoming coupled to one particular embedding model.

---

# 8. Embedding Versioning

Embedding vectors are **model-dependent artifacts**.

The system must therefore retain metadata describing how an embedding was created.

At minimum, the embedding record should be associated with:

```text
entity_id
embedding_type
model_name
model_version
dimension
created_at
content_hash
```

Conceptually:

```text
movie_embedding
├── movie_id
├── embedding
├── model_name
├── model_version
├── dimension
├── source_hash
└── created_at
```

The model version must not be inferred from the current application configuration.

It should be persisted explicitly.

---

# 9. Why Versioning Matters

Suppose CineRec moves from:

```text
Embedding Model A
```

to:

```text
Embedding Model B
```

The vectors generated by the two models may occupy different semantic spaces.

Therefore this is unsafe:

```text
Model A vectors
+
Model B query
```

unless compatibility has been explicitly established.

A versioned embedding architecture allows:

```text
Model A
 └── embedding set A

Model B
 └── embedding set B
```

to coexist during migration.

---

# 10. Embedding Identity

An embedding should be tied to the exact content from which it was generated.

For example:

```text
movie_id
+
canonicalized embedding input
+
embedding model/version
```

should produce a deterministic identity or source fingerprint.

The system should maintain a content hash such as:

```text
source_hash
```

so that unchanged content does not require unnecessary re-embedding.

Conceptually:

```text
Movie metadata
      ↓
Canonical embedding input
      ↓
SHA-256 / equivalent content hash
      ↓
Compare with stored source_hash
      ↓
Embed only when changed
```

---

# 11. What Should Be Embedded

CineRec should not blindly concatenate every movie field.

Movie embeddings should be generated from a carefully defined canonical semantic representation.

Potential inputs:

```text
title
overview
genres
keywords
selected credits
themes
tone-related metadata
release context
```

The exact embedding input should be versioned.

For example:

```text
embedding_input_version = "movie-v1"
```

This prevents silent changes to embedding semantics.

---

# 12. Movie Embeddings

Each eligible movie may have one or more embedding representations.

The initial production design should favor a **single primary movie embedding** unless evaluation demonstrates that multiple specialized embeddings are useful.

Example:

```text
movies
    └── primary_embedding
```

Potential future embeddings:

```text
semantic_content_embedding
cast_embedding
visual_embedding
plot_embedding
style_embedding
```

These should not be introduced without evidence that they improve recommendation quality.

---

# 13. User Embeddings

A user embedding represents the user's learned taste space.

It is derived from signals such as:

```text
ratings
likes
dislikes
viewing history
watchlist behavior
interaction history
recommendation feedback
```

A user embedding is therefore **derived state**, not the authoritative representation of what the user likes.

The authoritative signals remain:

```text
ratings
preferences
interactions
history
explicit memory
```

This follows ADR-002's principle that derived data should remain rebuildable.

---

# 14. User Embedding Updates

User embeddings may be updated asynchronously.

Preferred path:

```text
User Interaction
      ↓
PostgreSQL
      ↓
Interaction Event
      ↓
Background Job
      ↓
Recompute User Representation
      ↓
Store New Embedding
```

A normal user request should not be blocked unnecessarily waiting for an expensive embedding recomputation.

For immediate UX responsiveness, the recommendation engine may use current session features in addition to the latest persisted embedding.

---

# 15. Current Session vs Long-Term Embedding

The long-term user embedding must not completely dominate the current conversation.

Example:

```text
Long-term taste:
    Crime
    Sci-fi
    Thrillers

Current request:
    "Tonight I want something light and funny."
```

The recommendation engine should combine:

```text
long-term representation
+
current session context
+
explicit constraints
```

rather than blindly querying with only the long-term user vector.

The LLM extracts the user's current intent.

The recommendation engine constructs the retrieval representation.

---

# 16. Query Embeddings

Natural-language requests may also be embedded.

Example:

```text
"I want a rainy-night mystery with a slow burn."
```

becomes:

```text
query_embedding
```

This can be used for candidate retrieval.

However, vector similarity should not replace explicit structured filtering.

For example:

```text
"nothing over 2 hours"
```

must be represented as an explicit constraint rather than relying on semantic similarity.

---

# 17. Hard Filters vs Vector Similarity

Vector similarity is a **soft retrieval signal**.

Hard business constraints remain explicit.

Example:

```text
User request:
"Give me something under two hours, not horror,
and preferably in English."
```

The system should conceptually perform:

```text
Vector Retrieval
      ↓
Hard Constraints
      ├── runtime < 120 min
      ├── exclude horror
      └── language preference
      ↓
Ranking
```

A high vector similarity score must never override an explicit user constraint.

---

# 18. Distance Metric

The distance metric must be selected based on the embedding model and recommendation objective.

pgvector supports multiple distance operators, including:

```text
L2 distance
inner product
cosine distance
```

and supports corresponding operator classes for HNSW and IVFFlat.

For normalized semantic embeddings, **cosine similarity/distance is the default candidate metric**, subject to validation against the selected embedding model.

The metric must be configurable rather than hardcoded throughout the application.

---

# 19. HNSW Decision

CineRec will initially prefer **HNSW** for production approximate nearest-neighbor retrieval where vector-scale and latency justify indexing.

HNSW builds a multilayer graph and generally provides a better speed/recall tradeoff than IVFFlat, at the cost of slower index construction and higher memory usage. HNSW also does not require a training step before index creation.

Conceptual configuration:

```text
HNSW
├── m
├── ef_construction
└── ef_search
```

These parameters must be tuned empirically.

The project must not treat defaults as production-optimal.

---

# 20. IVFFlat Decision

IVFFlat remains a supported alternative.

IVFFlat partitions vectors into lists and searches a selected subset of those lists.

Its main tradeoff is:

```text
faster build
+
lower memory
-
lower query speed/recall tradeoff than HNSW
```

compared with HNSW.

IVFFlat may become preferable when:

```text
index build time
memory consumption
bulk ingestion characteristics
```

matter more than HNSW's query characteristics.

The choice must be benchmark-driven.

---

# 21. Initial Index Policy

The first production implementation should use:

```text
pgvector
+
HNSW
+
cosine distance
```

for the primary semantic embedding workload, assuming the chosen embedding model and evaluation validate that choice.

The exact index configuration must be treated as an operational parameter.

Example parameters include:

```text
m
ef_construction
hnsw.ef_search
```

pgvector supports configuring HNSW construction and search parameters.

---

# 22. Filtered Vector Queries

Recommendation retrieval will frequently combine vector similarity with relational filters.

Example:

```sql
SELECT ...
FROM movies
WHERE ...
ORDER BY embedding <=> :query_embedding
LIMIT :candidate_count;
```

PostgreSQL indexes on filtering columns may be important because approximate vector indexes do not automatically solve every filtered-query workload.

pgvector documents that filtering with approximate indexes occurs after the index scan in common cases, which can reduce the number of matching results. It also supports iterative index scans to compensate for this behavior.

Therefore vector retrieval must be evaluated using **real CineRec filter patterns**, not only unfiltered benchmarks.

---

# 23. Iterative Index Scans

Where filtered nearest-neighbor searches produce insufficient candidates, CineRec may use pgvector's iterative index-scan capabilities.

For HNSW, pgvector supports:

```text
strict_order
relaxed_order
```

iterative scanning modes.

These allow the system to continue scanning the approximate index when initial results do not satisfy enough filtering conditions.

The initial implementation should prefer correctness and predictable candidate availability over prematurely aggressive tuning.

---

# 24. Candidate Generation Architecture

Vector search is one candidate-generation strategy rather than the complete recommendation system.

Canonical architecture:

```text
                    Candidate Generation
                           │
       ┌───────────────────┼───────────────────┐
       ↓                   ↓                   ↓
  Collaborative      Vector Similarity     Popularity
   Filtering             Retrieval           / Trends
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ↓
                    Candidate Union
                           ↓
                    Hard Filtering
                           ↓
                        Ranking
                           ↓
                       Diversity
```

This preserves the hybrid recommendation architecture defined in `06-recommendation-system.md`.

---

# 25. Vector Search Must Not Become the Recommender

This is a critical architectural boundary.

The following is prohibited:

```text
User
 ↓
Embedding
 ↓
Nearest Movies
 ↓
Return Top 5
```

as CineRec's complete recommendation algorithm.

Pure nearest-neighbor retrieval can produce:

* overly similar results
* poor diversity
* popularity bias
* insufficient exploration
* weak personalization for sparse users
* repeated recommendations
* poor handling of explicit exclusions

Vector retrieval should instead produce a strong candidate set.

---

# 26. Hybrid Recommendation

The recommendation engine may combine multiple scores.

Conceptually:

```text
final_score =
    w_cf      * cf_score
  + w_vector  * semantic_score
  + w_pop     * popularity_score
  + w_context * context_score
  + w_novelty * novelty_score
  + w_explore * exploration_score
```

The exact formula is not fixed by this ADR.

The important boundary is:

```text
pgvector
→ semantic candidate generation

Recommendation Engine
→ final recommendation decision
```

---

# 27. Vector Search and Collaborative Filtering

Collaborative filtering and vector similarity capture different signals.

Collaborative filtering answers questions such as:

```text
"What do users with similar behavior tend to like?"
```

Semantic retrieval answers questions such as:

```text
"What movies are semantically close to this representation?"
```

Therefore CineRec should not assume that one eliminates the need for the other.

The recommendation engine should preserve both candidate sources.

---

# 28. Cold Start

Embeddings can help with cold-start recommendation, but they do not solve cold start completely.

For a new user:

```text
No interaction history
        ↓
Onboarding preferences / seed movies
        ↓
Query or user representation
        ↓
Semantic retrieval
        +
Popularity baseline
        +
Explicit constraints
```

Once sufficient interactions exist:

```text
behavioral signals
        ↓
collaborative filtering
        +
user embedding
```

The recommendation system should transition naturally from content-heavy retrieval toward increasingly behavioral personalization.

---

# 29. New Movie Cold Start

A newly ingested movie may have no interaction history.

However, its metadata may already permit embedding generation.

Therefore:

```text
TMDB metadata
      ↓
Canonical movie representation
      ↓
Embedding
      ↓
pgvector
```

allows a new movie to participate in semantic retrieval before collaborative filtering has sufficient behavioral evidence.

This is an important advantage of hybrid recommendation.

---

# 30. Embedding Generation Pipeline

Embedding generation should be asynchronous.

Preferred architecture:

```text
Movie Created / Updated
        ↓
Detect content hash change
        ↓
Queue embedding job
        ↓
Embedding Provider
        ↓
Validate dimension
        ↓
Store embedding + metadata
        ↓
Update embedding status
```

Potential statuses:

```text
PENDING
PROCESSING
READY
FAILED
STALE
```

The application should never assume that an embedding exists simply because the movie exists.

---

# 31. Embedding Failure Handling

Embedding generation failures must not make core movie functionality unavailable.

For example:

```text
TMDB movie ingestion
        ↓
embedding generation fails
        ↓
movie remains usable
        ↓
semantic features temporarily unavailable
```

The recommendation engine should degrade to alternative candidate sources:

```text
collaborative filtering
+
metadata filtering
+
popularity
```

where appropriate.

---

# 32. Dimension Validation

Every stored embedding must conform to its declared dimension.

For example:

```text
expected dimension = D
actual vector dimension = D
```

The application must reject incompatible vectors.

This should be checked during:

```text
embedding generation
embedding ingestion
model migration
database writes
```

A vector generated by an incompatible model must never silently enter an existing vector index.

---

# 33. Multiple Embedding Versions

During model migration, the database may temporarily contain:

```text
embedding_model_A
embedding_model_B
```

The active version should be controlled explicitly.

Possible strategy:

```text
embedding_registry
        ↓
active model/version
        ↓
retrieval configuration
```

The application must not implicitly use "whatever vector exists."

---

# 34. Re-Embedding Strategy

A re-embedding job may be triggered by:

```text
embedding model change
embedding input change
movie metadata change
corrupted embedding
dimension change
```

The process should support bulk recomputation without taking the application offline.

Preferred migration pattern:

```text
Current Embeddings
        ↓
Generate New Embeddings
        ↓
Validate
        ↓
Build/prepare new index
        ↓
Switch active version
        ↓
Retire old vectors
```

The exact operational implementation should depend on table size and deployment characteristics.

---

# 35. Storage Strategy

The initial schema should use pgvector's supported vector representation appropriate to the chosen embedding model.

pgvector currently supports:

```text
vector
halfvec
bit
sparsevec
```

with documented dimensionality limits for the respective types.

CineRec should initially use the standard **`vector` type** unless benchmarks demonstrate a meaningful benefit from alternatives such as `halfvec`.

Premature quantization should not be used merely to reduce storage.

---

# 36. Half-Precision Vectors

pgvector supports `halfvec`, which can reduce vector-storage and index footprint for appropriate workloads.

CineRec may evaluate half-precision storage when:

```text
vector count becomes large
index memory becomes material
retrieval quality remains acceptable
```

This is an optimization decision, not the initial default.

Any migration to lower precision must be evaluated against recommendation quality.

---

# 37. Exact vs Approximate Search

CineRec should retain the ability to perform exact nearest-neighbor queries where appropriate.

Exact search is useful for:

```text
small datasets
offline evaluation
benchmarking approximate recall
debugging
ground-truth comparisons
```

Approximate search becomes useful when vector volume and query latency make exact search too expensive.

The system therefore uses:

```text
Exact Search
→ evaluation / small workloads

Approximate Search
→ production retrieval at scale
```

where appropriate.

---

# 38. Recall Evaluation

Approximate vector retrieval must be evaluated against exact nearest-neighbor results.

A representative benchmark should measure:

```text
Recall@K
Latency
Throughput
Candidate availability
Memory usage
Index build time
```

A configuration that is faster but substantially reduces useful candidate recall must not automatically be considered better.

---

# 39. Recommendation-Level Evaluation

Vector retrieval quality cannot be evaluated solely through ANN recall.

Ultimately the relevant question is:

```text
Do retrieved candidates improve recommendations?
```

Therefore vector-search evaluation should also connect to:

```text
Precision@K
Recall@K
NDCG@K
MAP@K
coverage
diversity
novelty
user feedback
```

defined in the recommendation-system architecture.

A better vector benchmark does not automatically imply a better recommender.

---

# 40. Filtering and Diversity

Vector similarity naturally favors nearby points in embedding space.

That can create:

```text
five versions of the same movie
five movies from the same franchise
five movies with near-identical themes
```

The recommendation engine must therefore apply diversity after retrieval.

Example:

```text
Vector Retrieval
       ↓
Candidate Set
       ↓
Diversity / MMR / Policy
       ↓
Final Recommendations
```

Vector similarity must not be treated as a diversity mechanism.

---

# 41. Semantic Memory Retrieval

The memory subsystem may eventually use vector search to retrieve relevant long-term memories.

Example:

```text
Conversation:
"I want something tense but not depressing tonight."

        ↓

Current semantic representation
        ↓
Retrieve relevant memories
        ↓
"User generally likes slow-burn thrillers."
        ↓
Recommendation context
```

However, semantic memory retrieval is subject to the memory architecture and authorization rules.

Vector similarity must not expose unrelated or weakly relevant memories merely because they are mathematically close.

---

# 42. Memory Safety Boundary

The vector store does not decide whether a memory is:

```text
active
relevant
authoritative
private
expired
deleted
```

Those decisions belong to the memory subsystem.

The retrieval layer should receive an explicit retrieval scope.

Conceptually:

```text
Memory Service
      ↓
Authorized Candidate Scope
      ↓
Vector Retrieval
      ↓
Ranked Relevant Memories
```

This prevents vector similarity from becoming an access-control mechanism.

---

# 43. Tenant and User Isolation

CineRec is primarily a multi-user application.

User-owned embeddings must always carry an explicit ownership boundary.

A vector query must never implicitly assume:

```text
"The caller probably owns these vectors."
```

Authorization must occur through application-level ownership and query constraints.

For shared movie embeddings, the dataset may be globally accessible.

For private user embeddings or private memory embeddings:

```text
user_id
```

must be part of the retrieval boundary.

pgvector's documentation also notes that approximate indexes combined with tenant filtering can affect recall and may require partitioning or separate tables at larger multi-tenant scales.

---

# 44. Deletion

Deleting an entity must account for its embeddings.

Examples:

```text
Delete Movie
    ↓
Delete / invalidate movie embedding

Delete User
    ↓
Delete / invalidate user embedding
    ↓
Delete private memory embeddings
```

Embeddings must not remain as orphaned user-derived data after the underlying entity has been deleted, unless retention is explicitly required and documented.

---

# 45. Privacy

Embeddings are derived from user or movie data.

User embeddings may encode information about a person's preferences.

Therefore they should be treated as application data subject to the same ownership and privacy principles as the underlying user information.

The system must not assume that:

> "It is only a vector, therefore it is harmless."

Embedding storage, retrieval, export, and deletion must follow the application's privacy model.

---

# 46. Caching

Vector retrieval results may be cached when beneficial.

However:

```text
PostgreSQL + pgvector
```

remains authoritative.

Cached vector results must be invalidated or allowed to expire when:

```text
embedding changes
filter context changes materially
user profile changes
recommendation model changes
privacy state changes
```

Redis must not become a second vector database merely because cached vectors exist.

---

# 47. Query Caching

Potentially cacheable workloads include:

```text
movie similarity
popular semantic queries
stable public recommendations
repeated system-level candidate retrieval
```

Personalized user queries are less cacheable because the relevant context can change frequently.

Caching decisions should be driven by:

```text
latency benefit
cache hit rate
freshness requirements
memory cost
invalidation complexity
```

---

# 48. Database Access Boundary

Application code should not scatter pgvector SQL throughout the codebase.

Preferred structure:

```text
Recommendation Service
        ↓
Vector Retrieval Interface
        ↓
Repository
        ↓
SQLAlchemy / SQL
        ↓
PostgreSQL + pgvector
```

This ensures that a future migration to another vector backend would primarily affect the infrastructure implementation rather than the recommendation domain.

---

# 49. Migration Portability

The recommendation engine must not depend directly on:

```text
<=> operator
HNSW configuration
pgvector-specific SQL
```

outside the vector-storage adapter.

The repository boundary may use PostgreSQL-specific functionality because PostgreSQL is explicitly the selected implementation.

Domain logic must remain backend-agnostic.

---

# 50. Operational Monitoring

The vector subsystem should expose metrics such as:

```text
vector query latency
p50/p95/p99 retrieval latency
queries per second
candidate count
empty-result rate
index build duration
embedding generation rate
embedding failure rate
stale embedding count
embedding coverage
memory usage
index size
exact-vs-approximate recall
```

Recommendation quality metrics must remain separate from infrastructure latency metrics.

---

# 51. Embedding Freshness

The system should track whether an embedding corresponds to the current canonical input.

For example:

```text
Movie metadata version: 17
Embedding source version: 16
```

means the embedding is stale.

The application should be able to detect this.

A useful conceptual field is:

```text
source_hash
```

or:

```text
source_version
```

rather than simply assuming that `embedding IS NOT NULL` means "current."

---

# 52. Async Processing

Embedding generation should normally run through Celery/background processing.

Example:

```text
API
 ↓
PostgreSQL transaction
 ↓
enqueue embedding job
 ↓
Celery
 ↓
Embedding Provider
 ↓
PostgreSQL
```

The HTTP request should not perform expensive bulk re-embedding operations.

---

# 53. Bulk Ingestion

When importing a large movie catalog:

```text
TMDB
 ↓
Raw / normalized movie data
 ↓
PostgreSQL
 ↓
Bulk embedding generation
 ↓
pgvector storage
 ↓
Index maintenance
```

Index creation and maintenance must be planned around dataset size.

pgvector documents that HNSW can be built before data is present because it has no training phase, while IVFFlat benefits from having data available before index creation because it performs clustering during index construction.

---

# 54. Initial Movie Catalog Strategy

For initial development:

```text
Small Dataset
        ↓
Exact / simple vector queries
```

As the catalog grows:

```text
Larger Dataset
        ↓
HNSW
```

The system should not assume that approximate indexing is useful on a tiny dataset merely because it is available.

---

# 55. Failure Modes

### Embedding Provider Failure

```text
Embedding API unavailable
        ↓
mark job failed/retry
        ↓
movie remains usable
```

### pgvector Unavailable

Because pgvector is part of PostgreSQL:

```text
PostgreSQL unavailable
        ↓
vector retrieval unavailable
```

The recommendation engine should fall back to non-vector candidates where possible.

### Stale Embedding

```text
Embedding stale
        ↓
do not silently treat it as current
        ↓
schedule regeneration
```

---

# 56. Retry Strategy

Embedding jobs must be safe to retry.

A retry must not create uncontrolled duplicate logical embeddings.

Idempotency should be based on something like:

```text
entity_id
+
embedding_type
+
model_version
+
source_hash
```

This allows the worker to determine whether the exact artifact already exists.

---

# 57. Reproducibility

Every vector used in recommendation experiments should be traceable to:

```text
embedding model
embedding model version
embedding input version
source hash
generation timestamp
```

This is important for:

```text
recommendation debugging
offline evaluation
A/B experiments
regression analysis
model migration
incident investigation
```

---

# 58. Experimentation

Vector configuration itself may become experimental.

Examples:

```text
HNSW ef_search = 40
vs
HNSW ef_search = 100
```

or:

```text
Embedding Model A
vs
Embedding Model B
```

or:

```text
Cosine
vs
Alternative metric
```

Experimental configurations must be versioned.

The recommendation experiment system must be able to associate a recommendation outcome with the embedding configuration used to produce it.

---

# 59. Security

The vector layer must follow the same security requirements as PostgreSQL generally.

Specifically:

* no public database credentials
* parameterized queries
* explicit authorization boundaries
* user-owned vector isolation
* no arbitrary vector queries from untrusted clients
* no direct database access from the browser
* no unrestricted vector-query API
* no treating similarity as authorization
* audit sensitive administrative operations

A client must never be allowed to specify an arbitrary internal `user_id` and retrieve that user's embedding.

---

# 60. Testing Requirements

Tests must cover:

```text
vector insertion
vector retrieval
distance ordering
dimension validation
embedding versioning
stale detection
filtered vector queries
authorization
user isolation
deletion
retry idempotency
index behavior
fallback behavior
exact-vs-approximate recall
```

Recommendation tests should validate that vector retrieval improves candidate quality rather than merely proving that SQL execution succeeds.

---

# 61. Benchmarking Requirements

Before production optimization, benchmark representative workloads.

The benchmark dataset should approximate:

```text
movie catalog size
embedding dimension
filter selectivity
query concurrency
candidate K
user population
```

Measure:

```text
p50 latency
p95 latency
p99 latency
throughput
recall
memory usage
index size
build time
```

Benchmarks must include filtered queries because real CineRec recommendation queries will rarely be pure nearest-neighbor lookups.

---

# 62. Scaling Strategy

The intended progression is:

```text
Exact PostgreSQL Vector Search
        ↓
pgvector HNSW
        ↓
Query / index optimization
        ↓
Larger PostgreSQL instance
        ↓
Read scaling / workload isolation where justified
        ↓
Evaluate specialized vector infrastructure
```

The system should exhaust reasonable PostgreSQL optimizations before introducing another distributed system.

---

# 63. Conditions for Reconsideration

A dedicated vector database or specialized vector infrastructure should be considered only when measured evidence demonstrates a meaningful limitation.

Possible triggers include:

### Scale

Vector volume becomes too large for the current PostgreSQL architecture.

### Latency

Required p95/p99 latency cannot be achieved despite appropriate:

```text
indexing
hardware
query design
filtering
caching
```

### Throughput

Concurrent vector-query demand materially interferes with transactional database workloads.

### Memory

Vector indexes consume a disproportionate amount of PostgreSQL memory.

### Independent Scaling

Vector workloads need to scale independently from relational workloads.

### Operational Isolation

Vector retrieval needs independent deployment or failure isolation.

### Feature Requirements

A specialized system provides a capability required by CineRec that cannot reasonably be implemented with PostgreSQL + pgvector.

These conditions must be demonstrated through metrics and benchmarks.

---

# 64. Explicit Non-Triggers

The following are **not** valid reasons to introduce a dedicated vector database:

```text
"Vector databases are industry standard."

"Everyone uses one."

"Our architecture diagram should look more advanced."

"We might need it someday."

"We have embeddings, so we need a vector DB."

"A blog post used one."

"It looks better on the resume."
```

Architecture is driven by workload requirements, not technology fashion.

---

# 65. Migration to a Dedicated Vector Service

If a future migration becomes justified, the intended architecture is:

```text
Current

Recommendation Engine
        ↓
Vector Retrieval Interface
        ↓
PostgreSQL + pgvector
```

then:

```text
Future

Recommendation Engine
        ↓
Vector Retrieval Interface
        ↓
Dedicated Vector Service
```

The application-facing interface should remain stable.

Migration should therefore primarily replace:

```text
infrastructure implementation
```

rather than:

```text
recommendation domain logic
```

---

# 66. Data Migration Strategy

A future migration should follow:

```text
PostgreSQL / pgvector
        ↓
Export versioned embeddings
        ↓
Load into new vector system
        ↓
Validate counts
        ↓
Validate dimensions
        ↓
Validate nearest-neighbor recall
        ↓
Shadow queries
        ↓
Compare latency
        ↓
Gradual traffic migration
        ↓
Retire old path
```

The PostgreSQL source remains authoritative until the migration is proven.

---

# 67. Relationship to ADR-002

ADR-002 established:

> PostgreSQL is CineRec's authoritative persistent database.

This ADR extends that decision to vector data.

Therefore:

```text
PostgreSQL
    ↓
Relational State
+
Vector State
```

remains one persistence boundary.

pgvector does not change PostgreSQL's role as the source of truth.

---

# 68. Relationship to ADR-001

ADR-001 established the modular-monolith architecture.

The vector subsystem follows that boundary:

```text
Recommendation Module
        ↓
Vector Retrieval Port
        ↓
PostgreSQL Vector Adapter
```

Vector infrastructure therefore remains an implementation detail of the modular monolith.

It does not justify creating a separate vector microservice.

---

# 69. Consequences

## Positive Consequences

CineRec gains:

* one primary database
* no separate vector infrastructure initially
* straightforward joins between metadata and vectors
* transactional persistence
* simpler backups
* simpler local development
* lower operating cost
* easy integration with the recommendation engine
* strong filtering capabilities
* a clear future migration boundary
* access to HNSW and IVFFlat without introducing another service

---

## Negative Consequences

CineRec accepts:

* PostgreSQL memory must accommodate vector indexes
* vector workloads compete for database resources
* ANN performance must be tuned
* approximate search introduces recall/latency tradeoffs
* heavily filtered ANN queries require careful evaluation
* very large vector workloads may eventually exceed the comfortable operating range
* future migration to a dedicated vector system remains possible and must be designed for deliberately

---

# 70. Initial Technical Policy

The initial implementation should follow these defaults:

```text
Vector Store:
    PostgreSQL + pgvector

Primary Type:
    vector

Primary Similarity:
    cosine distance

Primary ANN Index:
    HNSW

Embedding Metadata:
    versioned and persisted

Embedding Generation:
    asynchronous

Source of Truth:
    PostgreSQL

Recommendation Role:
    candidate generation

Final Ranking:
    recommendation engine

Caching:
    Redis where justified

Access:
    backend only

Deletion:
    synchronized with owning entity

Evaluation:
    exact-search ground truth + recommendation metrics
```

These are initial engineering defaults, not immutable requirements.

---

# 71. Definition of Done

The pgvector implementation is considered complete when:

* pgvector is enabled through a reproducible migration/setup process
* embedding schema is versioned
* vector dimensions are validated
* model metadata is persisted
* movie embeddings can be generated and stored
* user embeddings can be generated and stored
* asynchronous generation works
* vector retrieval is exposed through an application interface
* filtered vector queries are tested
* authorization boundaries are tested
* deletion is handled
* stale embeddings are detectable
* retries are idempotent
* ANN configuration is benchmarked
* exact-vs-approximate recall is measured
* recommendation metrics incorporate vector candidate quality
* observability covers vector-generation and retrieval behavior
* fallback behavior exists when vector retrieval is unavailable
* no frontend code directly accesses pgvector/PostgreSQL
* no domain code is coupled directly to pgvector-specific SQL

---

# 72. Final Principle

> **Use pgvector because CineRec's vectors belong naturally beside its relational data. Keep the vector layer behind an abstraction, measure its real limits, and introduce a dedicated vector system only when workload evidence proves that PostgreSQL is no longer the appropriate boundary.**

---

# References

* pgvector official documentation and implementation repository: PostgreSQL vector similarity, HNSW, IVFFlat, filtering, iterative scans, vector types, and indexing behavior.

