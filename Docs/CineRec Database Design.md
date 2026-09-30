# CineRec — Database Design

**Status:** Database design / source of truth
**Working title:** CineRec
**Version:** 1.0
**Depends on:**

* `01-product-vision.md`
* `02-functional-requirements.md`
* `03-system-architecture.md`

**Database:** PostgreSQL
**Extensions:** `pgvector`, `pg_trgm`
**Primary objective:** Provide a normalized, durable, query-efficient data model for identity, movies, user behavior, personalization, memory, recommendations, and ML metadata while preserving clear ownership boundaries and future scalability.

---

# 1. Database Philosophy

PostgreSQL is the authoritative persistent datastore for CineRec.

The database must prioritize:

* data integrity
* explicit relationships
* appropriate normalization
* efficient read patterns
* safe concurrent updates
* clear ownership
* auditability
* extensibility
* reproducibility of recommendation behavior
* low operational complexity

Redis is **not** an authoritative datastore.

The application must be able to reconstruct Redis state from PostgreSQL and other authoritative sources.

---

# 2. Database Responsibilities

PostgreSQL owns:

```text
Identity / application users
Movie metadata required by the application
Movie-provider mappings
Genres and normalized movie metadata
Ratings
Likes/dislikes
Viewing history
Watchlists
General user interactions
Conversation sessions
Session intent
Persistent memories
Taste profiles
Recommendation requests
Recommendation items
Recommendation feedback
Model versions
Experiment metadata
Vector embeddings
```

PostgreSQL does not own:

* temporary cache state
* ephemeral job locks
* transient worker state
* secrets
* raw external provider sessions

---

# 3. High-Level Data Model

```text id="upj5vu"
                         ┌─────────────────┐
                         │     USERS       │
                         └────────┬────────┘
                                  │
              ┌───────────────────┼─────────────────────┐
              │                   │                     │
              ▼                   ▼                     ▼
        ┌───────────┐       ┌────────────┐       ┌──────────────┐
        │ IDENTITIES│       │  MEMORIES  │       │ TASTE_PROFILE│
        └───────────┘       └────────────┘       └──────────────┘
              │
              │
              ▼
        ┌──────────────┐
        │ CONVERSATION │
        │   SESSIONS   │
        └──────┬───────┘
               │
               ▼
        ┌────────────────┐
        │ SESSION INTENT │
        └────────────────┘


                         ┌───────────────┐
                         │    MOVIES     │
                         └───────┬───────┘
                                 │
         ┌───────────────────────┼──────────────────────────┐
         │                       │                          │
         ▼                       ▼                          ▼
   ┌───────────┐          ┌────────────┐            ┌──────────────┐
   │  GENRES   │          │ PROVIDERS  │            │  EMBEDDINGS  │
   └───────────┘          └────────────┘            └──────────────┘
         │
         │
         ▼
   ┌─────────────────┐
   │ MOVIE_RELATIONS │
   └─────────────────┘


                 USER × MOVIE ACTIVITY
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌──────────┐     ┌────────────┐   ┌──────────────┐
   │ RATINGS  │     │ WATCHLISTS │   │ INTERACTIONS │
   └──────────┘     └────────────┘   └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                 Recommendation system
                         │
                         ▼
              ┌────────────────────┐
              │ RECOMMENDATION     │
              │ REQUESTS           │
              └─────────┬──────────┘
                        │
                        ▼
              ┌────────────────────┐
              │ RECOMMENDATION     │
              │ ITEMS              │
              └─────────┬──────────┘
                        │
                        ▼
              ┌────────────────────┐
              │ MODEL / EXPERIMENT │
              │ METADATA           │
              └────────────────────┘
```

---

# 4. General Database Conventions

## 4.1 Primary Keys

Application entities SHOULD use UUID primary keys.

Recommended:

```text
UUIDv4 or UUIDv7
```

UUIDv7 is preferred for new entities where supported because its time-ordered nature can provide better index locality than completely random UUIDs.

Provider identifiers such as TMDB IDs remain separate from internal primary keys.

---

# 5. Timestamps

All persisted timestamps MUST use PostgreSQL:

```text
TIMESTAMPTZ
```

not plain `TIMESTAMP`.

Store timestamps in UTC.

Application presentation may convert them into user-local time.

Standard fields:

```text
created_at
updated_at
```

where appropriate.

---

# 6. Soft Deletes

Soft deletion SHOULD NOT be applied universally.

Use it only where historical/audit requirements justify it.

Examples where deletion state may matter:

* memories
* user-created preferences
* watchlist relationships where history matters

For simple immutable/reference entities such as genres, ordinary deletion or controlled archival is preferable.

---

# 7. JSONB Usage

JSONB SHOULD be used for:

* provider-specific metadata that does not justify first-class columns
* flexible interaction metadata
* model configuration snapshots
* experiment configuration
* structured but evolving contextual information

JSONB MUST NOT become an excuse to avoid proper relational modeling.

Important fields that are frequently queried or constrained SHOULD have dedicated columns.

---

# 8. Enum Strategy

Application-level enums SHOULD be represented consistently.

For rapidly evolving values, a text column with an application-level validated enum MAY be preferable to PostgreSQL native enums to simplify migrations.

Core values should nevertheless have database-level validation where practical.

Examples:

```text interaction_type
memory_type
memory_source
recommendation_surface
candidate_source
```

---

# 9. User / Identity Model

CineRec should separate:

```text
Application User
```

from:

```text
Authentication Identity
```

This avoids tightly coupling the database to Google or any particular authentication provider.

---

# 10. `users`

Stores CineRec's canonical application user.

### Columns

```text
id                  UUID PRIMARY KEY
display_name        TEXT
avatar_url          TEXT
locale              TEXT
timezone            TEXT
region_code         TEXT
onboarding_status   TEXT
created_at          TIMESTAMPTZ NOT NULL
updated_at          TIMESTAMPTZ NOT NULL
deleted_at          TIMESTAMPTZ NULL
```

### Notes

`id` is CineRec's internal identity.

It MUST NOT be assumed to equal a Google user ID or provider-specific user ID.

---

# 11. `user_identities`

Stores authentication-provider identities.

### Columns

```text
id                  UUID PRIMARY KEY
user_id             UUID NOT NULL REFERENCES users(id)
provider            TEXT NOT NULL
provider_subject    TEXT NOT NULL
email               TEXT
email_verified      BOOLEAN
created_at          TIMESTAMPTZ NOT NULL
updated_at          TIMESTAMPTZ NOT NULL
```

### Constraints

```text
UNIQUE(provider, provider_subject)
```

Potentially:

```text
UNIQUE(user_id, provider, provider_subject)
```

depending on authentication requirements.

### Example

```text
provider = "google"
provider_subject = "google-specific-subject"
```

The application does not use the Google subject as its internal user identifier.

---

# 12. `user_profiles`

Optional extended profile data can be kept separate from `users`.

### Columns

```text
user_id             UUID PRIMARY KEY REFERENCES users(id)
bio                 TEXT NULL
preferences_version INTEGER
created_at          TIMESTAMPTZ NOT NULL
updated_at          TIMESTAMPTZ NOT NULL
```

This separation prevents the core user table from becoming a miscellaneous profile table.

---

# 13. Movie Model

Movies are first-class internal domain entities.

The application must maintain its own canonical `movies` record even though TMDB supplies external metadata.

---

# 14. `movies`

### Columns

```text
id                    UUID PRIMARY KEY
title                 TEXT NOT NULL
original_title        TEXT
overview              TEXT
release_date          DATE
release_year          INTEGER
runtime_minutes       INTEGER
original_language     TEXT
poster_path           TEXT
backdrop_path         TEXT
logo_path             TEXT
status                TEXT
adult_content         BOOLEAN DEFAULT FALSE
vote_average          NUMERIC
vote_count            INTEGER
popularity_score      NUMERIC
metadata_updated_at   TIMESTAMPTZ
created_at            TIMESTAMPTZ NOT NULL
updated_at            TIMESTAMPTZ NOT NULL
```

### Constraints

`runtime_minutes`:

```text
NULL OR >= 0
```

`vote_average`:

```text
NULL OR 0 <= value <= 10
```

`vote_count`:

```text
NULL OR >= 0
```

---

# 15. `movie_provider_ids`

Stores provider-specific identifiers.

### Columns

```text
id                  UUID PRIMARY KEY
movie_id            UUID NOT NULL REFERENCES movies(id)
provider            TEXT NOT NULL
external_id         TEXT NOT NULL
created_at          TIMESTAMPTZ NOT NULL
updated_at          TIMESTAMPTZ NOT NULL
```

### Constraint

```text
UNIQUE(provider, external_id)
```

Example:

```text
movie_id      = internal UUID
provider      = "tmdb"
external_id   = "157336"
```

This is intentionally separate from `movies.id`.

---

# 16. `genres`

Normalized genre table.

### Columns

```text
id                  UUID PRIMARY KEY
name                TEXT NOT NULL
slug                TEXT NOT NULL UNIQUE
created_at          TIMESTAMPTZ NOT NULL
```

---

# 17. `movie_genres`

Many-to-many relation.

### Columns

```text
movie_id            UUID NOT NULL REFERENCES movies(id)
genre_id            UUID NOT NULL REFERENCES genres(id)
created_at          TIMESTAMPTZ NOT NULL
```

### Primary key

```text
(movie_id, genre_id)
```

---

# 18. `people`

Optional normalized representation for cast/crew.

### Columns

```text
id                  UUID PRIMARY KEY
name                TEXT NOT NULL
profile_path        TEXT
known_for_department TEXT
created_at          TIMESTAMPTZ NOT NULL
updated_at          TIMESTAMPTZ NOT NULL
```

This allows the system to represent directors, actors, writers, etc. without duplicating people across movies.

---

# 19. `movie_credits`

Represents movie/person relationships.

### Columns

```text
id                  UUID PRIMARY KEY
movie_id            UUID NOT NULL REFERENCES movies(id)
person_id           UUID NOT NULL REFERENCES people(id)
department          TEXT
job                 TEXT
character_name      TEXT
cast_order          INTEGER
created_at          TIMESTAMPTZ NOT NULL
```

Possible values:

```text
department:
Acting
Directing
Writing
Production
Camera
...
```

The detailed taxonomy can follow TMDB where useful.

---

# 20. `movie_keywords`

Stores normalized discovery keywords.

### Columns

```text
id                  UUID PRIMARY KEY
name                TEXT NOT NULL
slug                TEXT NOT NULL UNIQUE
provider_keyword_id TEXT NULL
created_at          TIMESTAMPTZ NOT NULL
```

---

# 21. `movie_keyword_links`

Many-to-many relationship.

```text
movie_id
keyword_id
```

Primary key:

```text
(movie_id, keyword_id)
```

---

# 22. Movie Themes

Themes can initially be represented through keywords or semantic metadata.

A separate `themes` model MAY be introduced later when theme-based exploration becomes a significant product capability.

Do not create a complicated ontology prematurely.

---

# 23. Movie Relations

For product features such as rabbit holes and similar movies, relationships may be stored explicitly.

## `movie_relations`

### Columns

```text
id                  UUID PRIMARY KEY
source_movie_id     UUID NOT NULL REFERENCES movies(id)
target_movie_id     UUID NOT NULL REFERENCES movies(id)
relation_type       TEXT NOT NULL
score               NUMERIC NULL
source              TEXT
created_at          TIMESTAMPTZ NOT NULL
```

Examples:

```text
SIMILAR
RECOMMENDED_WITH
SAME_DIRECTOR
SAME_FRANCHISE
```

The system should avoid storing redundant reverse relationships unless required.

---

# 24. User Ratings

## `ratings`

Represents the user's current explicit rating of a movie.

### Columns

```text
id                  UUID PRIMARY KEY
user_id             UUID NOT NULL REFERENCES users(id)
movie_id            UUID NOT NULL REFERENCES movies(id)
rating              NUMERIC NOT NULL
created_at          TIMESTAMPTZ NOT NULL
updated_at          TIMESTAMPTZ NOT NULL
```

### Constraint

One active rating per user/movie:

```text
UNIQUE(user_id, movie_id)
```

Rating range:

```text
1 <= rating <= 5
```

or another product-defined scale.

The database and application must use one consistent rating system.

---

# 25. Likes / Dislikes

Likes and dislikes MAY be modeled separately from ratings because they communicate a distinct signal.

## `movie_preferences`

### Columns

```text
id                  UUID PRIMARY KEY
user_id             UUID NOT NULL REFERENCES users(id)
movie_id            UUID NOT NULL REFERENCES movies(id)
preference          TEXT NOT NULL
created_at          TIMESTAMPTZ NOT NULL
updated_at          TIMESTAMPTZ NOT NULL
```

Possible values:

```text
LIKE
DISLIKE
```

### Constraint

```text
UNIQUE(user_id, movie_id)
```

An explicit new preference replaces the previous preference.

---

# 26. Watchlist

## `watchlists`

Represents active watchlist membership.

### Columns

```text
user_id             UUID NOT NULL REFERENCES users(id)
movie_id            UUID NOT NULL REFERENCES movies(id)
created_at          TIMESTAMPTZ NOT NULL
```

### Primary key

```text
(user_id, movie_id)
```

The system may retain watchlist history through interactions if needed rather than keeping deleted rows indefinitely.

---

# 27. Viewing History

Viewing state should be separate from watchlist.

## `viewing_history`

### Columns

```text
id                  UUID PRIMARY KEY
user_id             UUID NOT NULL REFERENCES users(id)
movie_id            UUID NOT NULL REFERENCES movies(id)
status              TEXT NOT NULL
started_at          TIMESTAMPTZ NULL
completed_at        TIMESTAMPTZ NULL
last_watched_at     TIMESTAMPTZ NULL
created_at          TIMESTAMPTZ NOT NULL
updated_at          TIMESTAMPTZ NOT NULL
```

Possible status:

```text
STARTED
COMPLETED
ABANDONED
```

The exact semantics should remain clearly defined.

A completed movie can remain in viewing history indefinitely unless deleted.

---

# 28. General Interaction Event Model

## `interactions`

This is one of the most important tables in CineRec.

It represents behavioral events used for:

* recommendation signals
* analytics
* personalization
* ML training
* product measurement

### Columns

```text
id                      UUID PRIMARY KEY
user_id                 UUID NOT NULL REFERENCES users(id)
movie_id                UUID NULL REFERENCES movies(id)
interaction_type        TEXT NOT NULL
value                   NUMERIC NULL
session_id              UUID NULL
recommendation_request_id UUID NULL
occurred_at             TIMESTAMPTZ NOT NULL
created_at              TIMESTAMPTZ NOT NULL
metadata                JSONB
```

Possible interaction types:

```text
IMPRESSION
CLICK
VIEW
WATCH_START
WATCH_COMPLETE
LIKE
DISLIKE
RATE
WATCHLIST_ADD
WATCHLIST_REMOVE
SKIP
TEMPORARY_REJECTION
SEARCH_CLICK
MOVIE_DETAIL_VIEW
```

---

# 29. Interaction Event Principles

Interactions are primarily **append-oriented events**.

Do not constantly mutate old event rows to represent new behavior.

For example:

```text
CLICK
```

should create an interaction.

Later:

```text
WATCH_START
```

creates another interaction.

Later:

```text
WATCH_COMPLETE
```

creates another interaction.

This preserves behavioral history.

---

# 30. Interaction Idempotency

Client/network retries can duplicate events.

The interaction model SHOULD support a client-generated event ID or idempotency key.

Potential field:

```text
event_key TEXT UNIQUE
```

Then:

```text
same event retry
      ↓
same event_key
      ↓
duplicate prevented
```

The exact implementation should depend on ingestion architecture.

---

# 31. Interaction Metadata

The `metadata` JSONB field MAY contain contextual details such as:

```json
{
  "surface": "home",
  "position": 2,
  "source": "collaborative_filtering"
}
```

Frequently queried dimensions SHOULD eventually receive dedicated columns rather than remaining indefinitely inside JSONB.

---

# 32. Conversation Sessions

## `conversation_sessions`

Represents a user's orb session.

### Columns

```text
id                  UUID PRIMARY KEY
user_id             UUID NOT NULL REFERENCES users(id)
status              TEXT NOT NULL
started_at          TIMESTAMPTZ NOT NULL
ended_at            TIMESTAMPTZ NULL
created_at          TIMESTAMPTZ NOT NULL
updated_at          TIMESTAMPTZ NOT NULL
```

Possible statuses:

```text
ACTIVE
COMPLETED
ABANDONED
ERROR
```

---

# 33. Conversation Messages

If conversational history is persisted, use a dedicated table.

## `conversation_messages`

### Columns

```text
id                  UUID PRIMARY KEY
session_id          UUID NOT NULL REFERENCES conversation_sessions(id)
role                TEXT NOT NULL
content             TEXT NOT NULL
sequence_number     INTEGER NOT NULL
created_at          TIMESTAMPTZ NOT NULL
metadata            JSONB
```

Roles:

```text
USER
ASSISTANT
SYSTEM
TOOL
```

### Constraint

```text
UNIQUE(session_id, sequence_number)
```

---

# 34. Conversation Storage Policy

Raw conversation storage should be minimized.

The application does not need to retain every historical conversation forever merely for personalization.

The system should distinguish:

```text
conversation history
```

from:

```text
persistent memory
```

Old conversation data may eventually be summarized, archived, or deleted according to product privacy policy.

---

# 35. Session Intent

## `conversation_intents`

Represents the current structured cinematic context.

### Columns

```text
id                  UUID PRIMARY KEY
session_id          UUID UNIQUE NOT NULL REFERENCES conversation_sessions(id)
mood                JSONB
desired_emotions    JSONB
energy_level        TEXT
emotional_intensity TEXT
complexity_level    TEXT
pacing_preference   TEXT
positive_genres     JSONB
negative_genres     JSONB
themes              JSONB
max_runtime_minutes INTEGER
min_runtime_minutes INTEGER
languages           JSONB
release_preferences JSONB
viewing_context     TEXT
exploration_level   TEXT
availability        JSONB
raw_intent_version  INTEGER
created_at          TIMESTAMPTZ NOT NULL
updated_at          TIMESTAMPTZ NOT NULL
```

The exact fields may evolve, but the architectural requirement is that current context be represented as structured application data.

---

# 36. Why Session Intent Is Separate

This must remain separate from long-term memory.

Example:

```text
Session:
"I want something comforting tonight."
```

must not automatically update:

```text
Long-term preference:
"User always wants comforting movies."
```

Session intent is temporary.

Persistent preferences are durable.

---

# 37. Persistent Memory

## `memories`

Represents user-level remembered preferences.

### Columns

```text
id                  UUID PRIMARY KEY
user_id             UUID NOT NULL REFERENCES users(id)
memory_type         TEXT NOT NULL
subject             TEXT NOT NULL
value               JSONB NOT NULL
polarity             TEXT
confidence           NUMERIC
source               TEXT NOT NULL
status               TEXT NOT NULL
evidence_count       INTEGER DEFAULT 1
last_evidence_at     TIMESTAMPTZ
created_at           TIMESTAMPTZ NOT NULL
updated_at           TIMESTAMPTZ NOT NULL
deleted_at           TIMESTAMPTZ NULL
```

Possible `memory_type`:

```text
GENRE
THEME
CREATOR
LANGUAGE
RUNTIME
STYLE
EMOTIONAL_PREFERENCE
AVERSION
VIEWING_HABIT
OTHER
```

Possible `polarity`:

```text
POSITIVE
NEGATIVE
NEUTRAL
```

Possible `source`:

```text
USER_EXPLICIT
BEHAVIOR_INFERRED
CONVERSATION_INFERRED
SYSTEM_DERIVED
```

Possible `status`:

```text
ACTIVE
DISABLED
DELETED
```

---

# 38. Memory Authority

A memory row SHOULD contain enough metadata to distinguish:

```text
explicit user statement
```

from:

```text
model inference
```

This is critical because explicit preferences should generally outrank weaker inferences.

---

# 39. Memory Evidence

The system MAY additionally maintain evidence for inferred memories.

## `memory_evidence`

### Columns

```text
id                  UUID PRIMARY KEY
memory_id           UUID NOT NULL REFERENCES memories(id)
interaction_id      UUID NULL REFERENCES interactions(id)
conversation_id     UUID NULL REFERENCES conversation_sessions(id)
evidence_type       TEXT NOT NULL
weight              NUMERIC
created_at          TIMESTAMPTZ NOT NULL
```

This allows the system to answer:

> "Why do we think this preference exists?"

without pretending that an inference is an explicit statement.

---

# 40. Taste Profile

The recommendation engine may maintain derived taste information separately from raw memories.

## `taste_profiles`

### Columns

```text
user_id             UUID PRIMARY KEY REFERENCES users(id)
profile_version     INTEGER NOT NULL
profile_data        JSONB NOT NULL
generated_at        TIMESTAMPTZ NOT NULL
updated_at          TIMESTAMPTZ NOT NULL
```

Example `profile_data`:

```json
{
  "genres": {
    "science_fiction": 0.91,
    "drama": 0.76,
    "comedy": 0.42
  },
  "styles": {
    "slow_burn": 0.71,
    "mind_bending": 0.84
  }
}
```

This is derived data, not raw user truth.

---

# 41. Taste Profile Versioning

Whenever the methodology changes materially, increment:

```text
profile_version
```

This allows us to understand which logic produced a particular profile.

---

# 42. User Embeddings

User semantic representations may later be stored using pgvector.

## `user_embeddings`

### Columns

```text
id                  UUID PRIMARY KEY
user_id             UUID NOT NULL REFERENCES users(id)
embedding_type      TEXT NOT NULL
model_name          TEXT NOT NULL
model_version       TEXT NOT NULL
embedding           VECTOR
created_at          TIMESTAMPTZ NOT NULL
```

Possible types:

```text
TASTE
SEMANTIC_PROFILE
```

A separate current/active marker may be useful.

---

# 43. Movie Embeddings

## `movie_embeddings`

### Columns

```text
id                  UUID PRIMARY KEY
movie_id            UUID NOT NULL REFERENCES movies(id)
embedding_type      TEXT NOT NULL
model_name          TEXT NOT NULL
model_version       TEXT NOT NULL
embedding           VECTOR
created_at          TIMESTAMPTZ NOT NULL
```

The vector dimension MUST match the chosen embedding model.

The exact dimension should be treated as configuration/schema design, not arbitrarily changed later.

---

# 44. Embedding Versioning

Embeddings MUST be versioned.

Example:

```text
model_name = "embedding-model-X"
model_version = "v3"
```

This prevents incompatible vectors from being mixed silently.

When the embedding model changes:

```text
new model
→ new embeddings
→ new version
```

Do not overwrite incompatible vectors without tracking their version.

---

# 45. Recommendation Requests

## `recommendation_requests`

Represents one recommendation-generation operation.

### Columns

```text
id                  UUID PRIMARY KEY
user_id             UUID NOT NULL REFERENCES users(id)
session_id          UUID NULL REFERENCES conversation_sessions(id)
surface             TEXT NOT NULL
model_version       TEXT
experiment_id       UUID NULL
experiment_variant  TEXT NULL
cache_hit           BOOLEAN DEFAULT FALSE
request_context     JSONB
created_at          TIMESTAMPTZ NOT NULL
completed_at        TIMESTAMPTZ NULL
latency_ms          INTEGER NULL
status              TEXT NOT NULL
```

Possible status:

```text
STARTED
COMPLETED
FAILED
FALLBACK
```

---

# 46. Why Recommendation Requests Exist

A simple:

```text user → movie
```

relationship isn't enough.

We need to know:

> What did the system recommend, under what context, using which model?

This table provides that traceability.

---

# 47. Recommendation Items

## `recommendation_items`

Represents movies produced by a recommendation request.

### Columns

```text
id                      UUID PRIMARY KEY
recommendation_request_id UUID NOT NULL REFERENCES recommendation_requests(id)
movie_id                UUID NOT NULL REFERENCES movies(id)
position                INTEGER NOT NULL
final_score             NUMERIC
candidate_score         NUMERIC
candidate_sources       JSONB
explanation_data        JSONB
was_displayed           BOOLEAN DEFAULT FALSE
created_at              TIMESTAMPTZ NOT NULL
```

### Constraint

```text
UNIQUE(recommendation_request_id, position)
```

Potentially:

```text
UNIQUE(recommendation_request_id, movie_id)
```

to prevent duplicate movies within a single recommendation response.

---

# 48. Candidate Source Representation

A recommendation may be discovered through several sources.

Example:

```json
{
  "sources": [
    {
      "type": "COLLABORATIVE_FILTERING",
      "score": 0.91
    },
    {
      "type": "SEMANTIC",
      "score": 0.84
    }
  ]
}
```

This information is useful for:

* debugging
* explanation generation
* experimentation
* model analysis

---

# 49. Recommendation Explanation Data

Explanation metadata SHOULD be structured.

Example:

```json
{
  "primary_reason": "CURRENT_MOOD",
  "signals": [
    "USER_LIKES_SCI_FI",
    "LOW_ENERGY_REQUEST",
    "MAX_RUNTIME_120"
  ]
}
```

The final natural-language explanation may be generated by Gemini, but it should be based on actual stored signals.

---

# 50. Recommendation Feedback

The general `interactions` table can record feedback.

A dedicated table is optional.

If fine-grained recommendation attribution becomes necessary, use:

## `recommendation_feedback`

```text
id                      UUID PRIMARY KEY
recommendation_item_id  UUID NOT NULL REFERENCES recommendation_items(id)
user_id                 UUID NOT NULL REFERENCES users(id)
feedback_type           TEXT NOT NULL
created_at              TIMESTAMPTZ NOT NULL
metadata                JSONB
```

Possible feedback:

```text
CLICKED
SAVED
WATCHED
COMPLETED
REJECTED
TEMPORARY_REJECTION
DISLIKED
```

This table MAY be introduced later if `interactions` becomes insufficiently expressive.

For MVP, `interactions` can be the canonical feedback event store.

---

# 51. Model Versions

## `model_versions`

Represents recommendation models that can be active.

### Columns

```text
id                  UUID PRIMARY KEY
model_key           TEXT NOT NULL
version             TEXT NOT NULL
algorithm           TEXT NOT NULL
training_dataset_id TEXT NULL
artifact_uri        TEXT
configuration       JSONB
metrics             JSONB
status              TEXT NOT NULL
created_at          TIMESTAMPTZ NOT NULL
activated_at        TIMESTAMPTZ NULL
retired_at          TIMESTAMPTZ NULL
```

### Constraint

```text
UNIQUE(model_key, version)
```

Possible statuses:

```text
TRAINED
EVALUATED
STAGING
ACTIVE
RETIRED
FAILED
```

---

# 52. Training Dataset Metadata

For reproducibility, model metadata should refer to the dataset used.

## `training_datasets`

### Columns

```text
id                  UUID PRIMARY KEY
name                TEXT NOT NULL
version             TEXT NOT NULL
source              TEXT
data_hash           TEXT
row_count           BIGINT
created_at          TIMESTAMPTZ NOT NULL
metadata             JSONB
```

### Constraint

```text
UNIQUE(name, version)
```

---

# 53. Experiments

## `experiments`

Future A/B and model experiments.

### Columns

```text
id                  UUID PRIMARY KEY
name                TEXT NOT NULL
description         TEXT
status              TEXT NOT NULL
configuration       JSONB
created_at          TIMESTAMPTZ NOT NULL
started_at          TIMESTAMPTZ NULL
ended_at            TIMESTAMPTZ NULL
```

---

# 54. Experiment Variants

Optional table:

## `experiment_variants`

```text
id                  UUID PRIMARY KEY
experiment_id       UUID NOT NULL REFERENCES experiments(id)
key                 TEXT NOT NULL
configuration       JSONB
created_at          TIMESTAMPTZ NOT NULL
```

Constraint:

```text
UNIQUE(experiment_id, key)
```

---

# 55. User Experiment Assignments

Future experimentation support.

## `experiment_assignments`

```text
id                  UUID PRIMARY KEY
experiment_id       UUID NOT NULL REFERENCES experiments(id)
user_id             UUID NOT NULL REFERENCES users(id)
variant_id          UUID NOT NULL REFERENCES experiment_variants(id)
assigned_at         TIMESTAMPTZ NOT NULL
```

Constraint:

```text
UNIQUE(experiment_id, user_id)
```

A user should ordinarily receive a stable variant for the duration of an experiment.

---

# 56. Movie Availability

Availability is more volatile than core movie metadata.

It SHOULD be modeled separately from `movies`.

## `movie_watch_providers`

### Columns

```text
id                  UUID PRIMARY KEY
movie_id            UUID NOT NULL REFERENCES movies(id)
region_code         TEXT NOT NULL
provider_name       TEXT NOT NULL
provider_id         TEXT NULL
availability_type   TEXT NOT NULL
url                 TEXT NULL
last_verified_at    TIMESTAMPTZ NOT NULL
expires_at          TIMESTAMPTZ NULL
metadata            JSONB
```

Possible `availability_type`:

```text
SUBSCRIPTION
RENT
BUY
FREE
ADS
```

Availability should be treated as time-sensitive information.

---

# 57. Provider Data Refresh

Provider data SHOULD be refreshable independently from the core movie record.

For example:

```text
movies
→ relatively stable

movie_watch_providers
→ frequently refreshed
```

---

# 58. Search Data

PostgreSQL should initially handle search.

The schema should support:

* normal title search
* fuzzy matching
* text search
* semantic vector search

Potential indexes:

```text
GIN / tsvector
GIN / pg_trgm
HNSW or IVFFlat / vector
```

The exact index strategy should be selected based on actual query patterns and supported PostgreSQL/pgvector versions.

---

# 59. Search Vector

A generated/search-normalized field MAY be maintained for movie search.

For example:

```text
search_document TSVECTOR
```

combining:

* title
* original title
* overview
* keywords

The application should not duplicate all searchable content into separate arbitrary search tables initially.

---

# 60. Database Index Strategy

Indexes must follow actual query patterns.

Important initial indexes include:

### Users

```text
user_identities(provider, provider_subject)
```

### Movies

```text
movies(title)
movies(release_date)
movies(original_language)
```

### Movie providers

```text
movie_provider_ids(provider, external_id)
```

### Ratings

```text
ratings(user_id)
ratings(movie_id)
ratings(user_id, updated_at)
```

### Interactions

```text
interactions(user_id, occurred_at)
interactions(movie_id, occurred_at)
interactions(interaction_type, occurred_at)
interactions(user_id, movie_id, occurred_at)
```

### Watchlist

```text
watchlists(user_id)
watchlists(movie_id)
```

### Viewing history

```text
viewing_history(user_id, last_watched_at)
viewing_history(movie_id)
```

### Memories

```text
memories(user_id, status)
memories(user_id, memory_type)
```

### Recommendations

```text
recommendation_requests(user_id, created_at)
recommendation_items(recommendation_request_id, position)
recommendation_items(movie_id)
```

Indexes should be revised when production query patterns become known.

Do not blindly index every column.

---

# 61. Composite Index Philosophy

Composite indexes should follow common query ordering.

For example:

```text
(user_id, occurred_at DESC)
```

is more useful for:

> "Give me this user's recent interactions."

than independent indexes on:

```text
user_id
occurred_at
```

for that particular query.

---

# 62. Foreign-Key Rules

Foreign keys MUST be used for core relational integrity.

Delete behavior must be chosen intentionally.

For example:

```text
users
 ↓
ratings
```

Deleting a user should trigger a deliberate privacy/data lifecycle process rather than accidentally cascading through an enormous graph without review.

Avoid using:

```text
ON DELETE CASCADE
```

everywhere.

Use it selectively.

---

# 63. User Deletion

The application should support a controlled user-deletion workflow.

Conceptually:

```text
user requests deletion
        ↓
authorization
        ↓
mark account for deletion
        ↓
delete/ anonymize user-owned data
        ↓
remove identity linkage
        ↓
remove derived personalization artifacts
        ↓
verify completion
```

The precise retention requirements belong in privacy/deployment documentation.

---

# 64. Derived Data

Some database entities are derived rather than authoritative.

Examples:

```text taste_profiles
user_embeddings
movie_embeddings
recommendation caches
preference scores
```

These should be reconstructable from authoritative data where practical.

This distinction is critical.

If the taste profile is corrupted, the system should be able to regenerate it from underlying interaction/memory data.

---

# 65. Source-of-Truth Hierarchy

The database should conceptually treat data as:

```text
AUTHORITATIVE
├── users
├── identities
├── movies
├── ratings
├── interactions
├── watchlists
├── viewing_history
└── explicit memories

DERIVED
├── taste_profiles
├── inferred memories
├── embeddings
└── recommendation artifacts
```

Derived data must not silently become the only source of user truth.

---

# 66. Recommendation Context Snapshot

For reproducibility, `recommendation_requests.request_context` SHOULD contain a compact snapshot of the relevant recommendation context.

Example:

```json
{
  "session_intent": {
    "mood": ["tired"],
    "energy": "low",
    "max_runtime": 120
  },
  "profile_version": 7,
  "memory_version": 3
}
```

This avoids needing to reconstruct historical context perfectly from mutable current data.

---

# 67. Why Context Snapshots Matter

Suppose the user changes their taste profile six months later.

A recommendation request from today should still be explainable using:

```text
what the system knew at that time
```

rather than whatever the profile happens to contain today.

---

# 68. Recommendation Model Attribution

Each recommendation request MUST be traceable to:

```text
model version
```

where model-based recommendation was used.

Fallback requests should also be distinguishable.

Example:

```text
model_version = "cf-als-v4"
status = "COMPLETED"
```

or:

```text
model_version = null
status = "FALLBACK"
```

---

# 69. Memory Versioning

User-level derived personalization can benefit from profile versions.

Example:

```text
taste profile v12
```

A recommendation request can reference:

```text
profile_version = 12
```

This provides historical reproducibility.

---

# 70. Interaction Weighting

Interaction strengths SHOULD NOT be stored solely as hardcoded model assumptions.

The raw event remains:

```text
WATCH_COMPLETE
```

The ML pipeline determines its training weight.

For example:

```text
WATCH_COMPLETE → weight X
LIKE           → weight Y
CLICK          → weight Z
```

Weights belong in model/training configuration.

This keeps raw behavioral truth separate from one specific model's interpretation.

---

# 71. Rating vs Interaction

Ratings are explicit structured user preference.

Interactions are behavioral events.

They should remain conceptually separate.

Example:

```text
User rates Interstellar = 5
```

goes to:

```text ratings
```

The act of opening the movie page goes to:

```text interactions
```

The act of completing it goes to:

```text interactions
+
possibly viewing_history
```

This avoids destroying behavioral information by reducing everything to a single rating table.

---

# 72. Watching State vs Watching Event

`viewing_history` represents the current useful state.

`interactions` preserves the behavioral event sequence.

This distinction is intentional.

Example:

```text INTERACTIONS

WATCH_START
WATCH_COMPLETE
```

while:

```text VIEWING_HISTORY

status = COMPLETED
```

Both can coexist.

---

# 73. Recommendation Impression vs Interaction

A recommendation item represents what the system generated.

An impression represents what the user was actually shown.

Therefore:

```text recommendation_items
```

and:

```text interactions: IMPRESSION
```

are not identical concepts.

A recommendation may have been generated but never displayed due to:

* navigation
* network failure
* component unmount
* pagination
* client-side filtering

The system should preserve this distinction where accurate analytics matter.

---

# 74. Duplicate Movie Prevention

A recommendation response MUST NOT present duplicate movie IDs.

The database SHOULD enforce:

```text
UNIQUE(recommendation_request_id, movie_id)
```

if no valid use case requires duplicates.

---

# 75. Duplicate Memory Prevention

The application should prevent logically identical active memories where possible.

For example:

```text
GENRE + HORROR + NEGATIVE
```

should not produce many redundant rows.

A logical uniqueness strategy may use normalized subject/value fields plus application-level reconciliation.

Do not rely solely on string equality for semantically identical memories.

---

# 76. Memory Conflict Model

A user could have:

```text
Explicit:
"Never recommend horror."
```

and later:

```text
Explicit:
"I'm actually okay with psychological horror."
```

The system should not simply delete history.

Instead, the memory subsystem should support:

* active preference
* evidence
* updates
* supersession

The application layer determines how old memories are reconciled.

---

# 77. Database-Level Constraints for Critical Invariants

The database SHOULD enforce:

```text
unique authentication identity
one rating per user/movie
one like/dislike state per user/movie
one active watchlist relationship
valid foreign keys
valid rating ranges
valid non-negative runtime
valid non-negative counts
unique provider/movie mapping
```

Application code should enforce higher-level semantic rules.

---

# 78. Concurrency Control

Potential race conditions include:

```text
two rating updates
watchlist add/remove simultaneously
memory updates
duplicate interaction ingestion
```

Where necessary:

* use transactions
* use unique constraints
* use optimistic concurrency
* use upserts
* use row-level locking selectively

Do not solve ordinary concurrency problems with distributed locks unless necessary.

---

# 79. Upsert Strategy

Operations representing a user's current state SHOULD generally support upsert semantics.

Examples:

```text
set rating
set like/dislike
add watchlist membership
```

Behavior:

```text
not present → insert
present → update
```

Event creation remains append-oriented for behavioral history.

---

# 80. Transaction Examples

## Rating update

```text
BEGIN
 ↓
upsert rating
 ↓
commit
 ↓
enqueue derived-update work
```

## Watchlist add

```text
BEGIN
 ↓
insert membership if absent
 ↓
COMMIT
```

## Explicit memory update

```text
BEGIN
 ↓
create/update memory
 ↓
update memory version
 ↓
COMMIT
```

External API calls should generally occur outside the core transaction.

---

# 81. External Provider Data Integrity

TMDB data is externally sourced.

The database should retain:

```text provider
external_id
last_synced_at
provider metadata/version information where useful
```

The application should know when its local representation was last refreshed.

---

# 82. Movie Metadata Refresh

Refreshing a movie should not require replacing the entire relational graph blindly.

For example:

```text
movie core metadata
```

can be updated independently from:

```text cast/crew
genres
keywords
availability
embeddings
```

This allows targeted refreshes.

---

# 83. Embedding Refresh Strategy

If movie metadata changes materially or the embedding model changes:

```text
movie
 ↓
embedding stale
 ↓
background job
 ↓
new embedding
 ↓
new model_version
```

Do not block a user request waiting for an embedding regeneration job.

---

# 84. pgvector Strategy

The initial vector use cases are:

```text
semantic movie search
movie similarity
contextual discovery
future user taste vectors
```

The system should start with a moderate vector dataset that PostgreSQL can handle effectively.

If vector search eventually becomes a measurable bottleneck, a dedicated vector retrieval architecture can be considered.

---

# 85. Vector Indexing

Use an appropriate pgvector index only when the dataset/query pattern justifies it.

Possible strategies include:

```text
HNSW
IVFFlat
```

The architecture should allow switching strategy without changing application-level vector APIs.

---

# 86. Fuzzy Search

`pg_trgm` can support:

* typo-tolerant title matching
* approximate search
* autocomplete-like behavior

Example:

```text
Interstelar
```

can still match:

```text
Interstellar
```

Search behavior should remain application-level rather than exposing raw PostgreSQL functions to the frontend.

---

# 87. Full-Text Search

A normalized search document can combine:

```text
title
original_title
overview
keywords
```

with weighting.

For example:

```text
title > overview > keyword
```

The exact weighting belongs to search implementation.

---

# 88. Data Retention

Different data categories have different retention requirements.

Conceptually:

```text
Core movie metadata
→ long-lived

User ratings
→ long-lived until user deletion/reset

Watchlist
→ long-lived current state

Interactions
→ potentially long-lived for personalization/analytics

Raw conversation
→ potentially shorter retention

Derived embeddings
→ regenerable

Caches
→ temporary
```

Specific retention periods should be documented separately.

---

# 89. Partitioning

Do not partition tables in the initial implementation unless actual size requires it.

The first likely candidate, if event volume becomes very large, is:

```text
interactions
```

Potential future partition key:

```text occurred_at
```

or a suitable time range.

Recommendation history may eventually become another candidate.

Partitioning should be driven by observed data size and query behavior.

---

# 90. Expected Growth Characteristics

The schema should anticipate that:

```text users
```

grow steadily,

while:

```text interactions
```

can grow much faster because one user may generate many events.

This means interaction storage should be designed with:

* efficient indexes
* time-based access patterns
* append-heavy behavior
* future partitioning capability

in mind.

---

# 91. Avoid Over-Normalizing Product-Specific Metadata

Not every TMDB attribute deserves its own table.

Use normalized tables for information that is:

* relational
* frequently queried
* reused
* constrained

Keep low-value provider-specific information in JSONB when appropriate.

The goal is a healthy balance between:

```text relational integrity
```

and:

```text schema flexibility
```

---

# 92. Database Access Boundary

Application code should access the database through repositories/data-access components.

A route should not contain arbitrary SQL.

Preferred:

```text
API
 ↓
Application Service
 ↓
Repository
 ↓
SQLAlchemy
 ↓
PostgreSQL
```

---

# 93. Migration Strategy

Alembic owns schema migrations.

Every schema modification requires a migration.

Examples:

```text
001_initial_schema
002_movie_providers
003_interactions
004_memories
005_recommendation_tables
```

Migration files MUST be committed to source control.

---

# 94. Migration Safety

Production migrations SHOULD:

* be deterministic
* be reviewable
* avoid destructive operations without explicit migration planning
* handle large-table changes carefully
* preserve compatibility during rolling deployments when necessary

---

# 95. Backward-Compatible Schema Changes

When deploying changes across multiple application versions:

Prefer:

```text
add new column
 ↓
deploy code that writes both
 ↓
backfill
 ↓
switch reads
 ↓
remove old column later
```

rather than:

```text
drop old column
 ↓
deploy new code
```

for production systems.

---

# 96. Seed Data

Development environments SHOULD provide seed data for:

* genres
* sample users
* sample movies
* sample ratings
* sample interactions
* sample memories
* sample recommendations

Seed data MUST be clearly separated from production data.

---

# 97. Test Database

Automated tests SHOULD use an isolated PostgreSQL database.

Test databases should validate:

* constraints
* migrations
* transactions
* indexing assumptions where appropriate
* repository behavior

Mocks alone are insufficient for database-level integrity testing.

---

# 98. Backup Strategy

Production PostgreSQL data should be backed up.

Important categories:

```text
transactional data
user preferences
ratings
interactions
```

Model artifacts and derived vectors should have independent regeneration/backup strategies.

---

# 99. Disaster Recovery Principle

The system should be designed so that:

```text
PostgreSQL backup
+
application code
+
migration history
+
model artifacts
+
external provider credentials
```

are sufficient to reconstruct a working deployment.

Derived data should be regenerable wherever practical.

---

# 100. Auditability

Important user-state changes should be reconstructable where practical.

At minimum, interactions and explicit memory evidence provide useful history.

A full generic audit-log table is not required for every table in the MVP.

Introduce one only where actual compliance or operational requirements justify it.

---

# 101. Database Security

The application MUST use least-privilege database access.

The runtime API should not necessarily receive administrative database privileges.

Migration tooling can use a more privileged database role.

Where deployment architecture supports it, separate:

```text
application role
migration role
read-only analytics role
```

may be used.

---

# 102. Secrets Are Not Stored in Database Tables

Do not store:

```text
Gemini API keys
TMDB API keys
Google OAuth secrets
Redis passwords
```

as ordinary database records.

Secrets belong in environment/secret-management infrastructure.

---

# 103. Row-Level Ownership

Every user-owned table MUST make user ownership explicit where practical.

Examples:

```text
ratings.user_id
watchlists.user_id
interactions.user_id
memories.user_id
conversation_sessions.user_id
recommendation_requests.user_id
```

This simplifies authorization reasoning and query construction.

---

# 104. User Data Isolation

Queries for user-owned resources SHOULD always begin from the authenticated user identity.

Preferred:

```text
WHERE user_id = authenticated_user_id
```

rather than accepting an arbitrary user ID from a client and assuming it is trustworthy.

---

# 105. Optional Row-Level Security

If the selected PostgreSQL hosting/auth architecture supports it cleanly, Row-Level Security MAY be used as an additional defense-in-depth layer.

However, RLS should not be introduced merely for appearance.

The application authorization model remains mandatory regardless of whether RLS is enabled.

---

# 106. Canonical Table Inventory

The initial schema should conceptually contain:

```text
IDENTITY
├── users
├── user_identities
└── user_profiles

MOVIES
├── movies
├── movie_provider_ids
├── genres
├── movie_genres
├── people
├── movie_credits
├── movie_keywords
├── movie_keyword_links
├── movie_relations
└── movie_watch_providers

USER ACTIVITY
├── ratings
├── movie_preferences
├── watchlists
├── viewing_history
└── interactions

CONVERSATION
├── conversation_sessions
├── conversation_messages
└── conversation_intents

PERSONALIZATION
├── memories
├── memory_evidence
├── taste_profiles
├── user_embeddings
└── movie_embeddings

RECOMMENDATIONS
├── recommendation_requests
└── recommendation_items

ML / EXPERIMENTS
├── model_versions
├── training_datasets
├── experiments
├── experiment_variants
└── experiment_assignments
```

Not every table above has to be implemented simultaneously.

The architecture supports gradual introduction.

---

# 107. MVP Table Set

The initial implementation should prioritize:

```text
users
user_identities
movies
movie_provider_ids
genres
movie_genres
ratings
movie_preferences
watchlists
viewing_history
interactions
conversation_sessions
conversation_messages
conversation_intents
memories
taste_profiles
recommendation_requests
recommendation_items
model_versions
```

The following may be added when their corresponding capabilities are implemented:

```text
people
movie_credits
movie_keywords
movie_keyword_links
movie_relations
memory_evidence
user_embeddings
movie_embeddings
movie_watch_providers
training_datasets
experiments
experiment_variants
experiment_assignments
```

---

# 108. Recommended Relationship Graph

The primary relational flow is:

```text
USER
 │
 ├── identities
 │
 ├── ratings ────────────────┐
 │                           │
 ├── preferences ────────────┤
 │                           │
 ├── watchlists ─────────────┤
 │                           │
 ├── viewing_history ────────┤
 │                           ▼
 ├── interactions ───────► MOVIE
 │                           ▲
 ├── memories                │
 │                           │
 └── conversations           │
                             │
                    recommendation_items
                             ▲
                             │
                   recommendation_requests
```

---

# 109. Critical Business Invariants

The database and application must preserve the following:

### Identity

One external authentication identity maps to one CineRec user.

### Ratings

One active rating per user/movie.

### Preference

One active like/dislike state per user/movie.

### Watchlist

One active watchlist relationship per user/movie.

### Recommendation

One movie should not appear twice in the same recommendation request.

### Memory

Persistent memories belong to exactly one user.

### Conversation

Conversation sessions belong to exactly one authenticated user.

### Recommendation request

A recommendation request belongs to exactly one user.

### Model attribution

A model version must identify the recommendation logic used where model-based recommendation is involved.

### Movie provider identity

A provider/external ID pair maps to one internal movie record.

---

# 110. Derived Data Invariants

Derived artifacts should always identify their source/version where necessary.

Examples:

```text taste_profile
→ profile_version

embedding
→ model_name + model_version

recommendation
→ model_version

memory inference
→ source + confidence
```

This avoids opaque "magic data."

---

# 111. Example User Data Flow

When a user rates a movie:

```text
USER
 ↓
rating API
 ↓
validate user/movie/rating
 ↓
transaction
 ├── upsert ratings
 └── append RATE interaction
 ↓
commit
 ↓
invalidate relevant recommendation cache
 ↓
enqueue preference/recommendation update
```

The database therefore preserves both:

```text
current rating state
```

and:

```text
behavioral event
```

---

# 112. Example Recommendation Data Flow

When recommendations are generated:

```text
recommendation request
 ↓
create recommendation_requests row
 ↓
candidate generation
 ↓
ranking
 ↓
insert recommendation_items
 ↓
return result
 ↓
frontend displays items
 ↓
IMPRESSIONS recorded
 ↓
user reacts
 ↓
interactions recorded
```

This creates an auditable recommendation trail.

---

# 113. Example Memory Flow

User says:

> "Remember that I hate horror."

Flow:

```text
conversation
 ↓
LLM intent extraction
 ↓
application validation
 ↓
explicit memory operation
 ↓
transaction
 ↓
memories row
 ↓
memory/version update
 ↓
future recommendation context
```

The database must distinguish this from a weak inferred preference.

---

# 114. Example Inferred Preference Flow

User repeatedly:

```text
rates sci-fi highly
completes sci-fi
adds sci-fi to watchlist
```

Flow:

```text
interactions
 +
ratings
 ↓
ML / preference aggregation
 ↓
taste profile update
 ↓
derived preference
```

This derived preference should be identified as inferred, not explicit.

---

# 115. Example TMDB Flow

```text
user searches "Interstellar"
 ↓
application search
 ↓
check local movie data
 ↓
movie exists?
 ├── yes → return
 └── no
      ↓
   TMDB adapter
      ↓
   normalize response
      ↓
   transaction
      ├── movies
      ├── movie_provider_ids
      ├── genres
      └── relationships
      ↓
   return
```

The frontend never treats TMDB's raw response as the application's canonical domain object.

---

# 116. Database Performance Philosophy

The database should be optimized in this order:

```text
correct schema
 ↓
correct constraints
 ↓
correct indexes
 ↓
efficient queries
 ↓
connection pooling
 ↓
caching
 ↓
query analysis
 ↓
only then advanced scaling
```

Do not use Redis to hide a fundamentally bad SQL query.

---

# 117. Query Design Requirements

Queries should:

* select only required columns where practical
* avoid unnecessary joins
* batch related data
* use indexed predicates
* use pagination for large collections
* avoid N+1 access patterns
* avoid unbounded result sets

---

# 118. Large Interaction Queries

Queries such as:

> "Get the last 1000 interactions for this user"

should use:

```text
(user_id, occurred_at DESC)
```

or an equivalent optimized index.

The database should not sort millions of rows unnecessarily for every request.

---

# 119. Recommendation History Queries

Queries such as:

> "Show my recent recommendation sessions"

should use:

```text
recommendation_requests(user_id, created_at DESC)
```

and return paginated results.

---

# 120. Watchlist Queries

Typical query:

```text
SELECT movies
FROM watchlist
WHERE user_id = ?
ORDER BY created_at DESC
LIMIT ...
```

Therefore:

```text
(user_id, created_at DESC)
```

should be considered as an appropriate composite index.

---

# 121. Rating Matrix Extraction

The ML pipeline may need:

```text
user_id
movie_id
rating
```

for explicit-feedback training.

The database should support efficient extraction without requiring application-layer iteration.

The training pipeline SHOULD query/bulk-export data in batches.

---

# 122. Interaction Matrix Extraction

For implicit-feedback models, training may use:

```text
user_id
movie_id
interaction_type
timestamp
```

with weighting performed in the ML layer.

The database should preserve raw events rather than pre-collapsing them irreversibly.

---

# 123. Recommendation Cache Relationship

Cached recommendations in Redis should be derivable from:

```text recommendation_requests
recommendation_items
```

or regenerated using the recommendation engine.

Redis must not become the historical record of recommendations.

---

# 124. Database and Redis Boundary

### PostgreSQL

Use for:

```text durable
authoritative
historical
relational
auditable
```

### Redis

Use for:

```text fast
temporary
cacheable
reconstructable
rate-limited
```

This boundary is mandatory.

---

# 125. Database and ML Boundary

PostgreSQL stores:

```text raw behavioral data
derived profiles
model metadata
embeddings
```

The ML pipeline is responsible for:

```text transformation
training
evaluation
artifact generation
```

Training code must not be embedded in SQL migrations or transactional database logic.

---

# 126. Database and LLM Boundary

PostgreSQL stores:

```text persistent memory
conversation state
structured session intent
```

Gemini may receive a controlled subset of this information.

Gemini must not get unrestricted SQL/database access.

---

# 127. Data Rebuildability

The system should aim for:

```text raw authoritative data
        ↓
derived state
```

rather than:

```text derived state
        ↓
irreversible truth
```

For example, if:

```text taste_profiles
```

are deleted, they should be regenerable from relevant user history.

---

# 128. Schema Evolution

The database design intentionally supports these future additions without restructuring its core:

```text semantic recommendations
group recommendations
voice sessions
A/B testing
new recommendation models
additional movie providers
advanced movie graph
analytics pipeline
```

Provider-specific and model-specific details should remain isolated from core user/movie identity.

---

# 129. Future Group Recommendation Schema

Not MVP.

Potential future entities:

```text recommendation_groups
group_members
group_preferences
group_sessions
```

These should not be forced into the MVP user/recommendation tables.

---

# 130. Future Voice Schema

Not MVP.

Potential future metadata:

```text conversation_messages.metadata
conversation_sessions.metadata
```

can initially hold modality information without creating a dedicated voice schema.

If voice becomes a major product surface, dedicated tables can be introduced later.

---

# 131. Future Movie Knowledge Graph

The initial normalized movie/person/genre/keyword relationship model can evolve toward richer graph-like traversal without requiring a graph database.

A graph database MUST NOT be introduced until actual relationship-query requirements justify it.

PostgreSQL relational edges are sufficient initially.

---

# 132. Future Analytics Storage

Initially:

```text PostgreSQL interactions
```

If analytical workload becomes large enough to affect application performance:

```text PostgreSQL
   ↓
analytics extraction
   ↓
analytical datastore
```

The operational schema should therefore preserve clean event semantics.

---

# 133. Recommended Initial Schema Implementation Order

Implement migrations roughly in this order:

```text
001_core_users
002_movie_catalog
003_movie_relationships
004_user_movie_state
005_interactions
006_conversations
007_memories
008_taste_profiles
009_recommendations
010_model_metadata
011_vectors
012_availability
```

Exact migration grouping may change during implementation.

Each migration must remain atomic and reviewable.

---

# 134. ER Diagram — Core MVP

```text id="iy5fki"
┌─────────────────────┐
│       users         │
├─────────────────────┤
│ id PK               │
│ display_name        │
│ avatar_url          │
│ locale              │
│ timezone            │
│ region_code         │
│ onboarding_status   │
│ created_at          │
│ updated_at          │
└──────┬──────────────┘
       │
       ├───────────────┐
       │               │
       ▼               ▼
┌──────────────┐  ┌─────────────────┐
│ identities   │  │ conversation    │
│              │  │ sessions        │
└──────────────┘  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ conversation     │
                  │ messages         │
                  └─────────────────┘

┌─────────────────────┐
│       movies        │
├─────────────────────┤
│ id PK               │
│ title               │
│ overview            │
│ release_date        │
│ runtime_minutes     │
│ original_language   │
│ poster_path         │
│ backdrop_path       │
│ ...                 │
└────────┬────────────┘
         │
         ├───────────────┐
         │               │
         ▼               ▼
┌────────────────┐  ┌───────────────┐
│ provider_ids   │  │ movie_genres  │
└────────────────┘  └───────┬───────┘
                            │
                            ▼
                         genres

users ─────┬──── ratings ───────── movies
           │
           ├──── preferences ───── movies
           │
           ├──── watchlists ─────── movies
           │
           ├──── viewing_history ── movies
           │
           └──── interactions ───── movies

users ───── memories
users ───── taste_profiles
users ───── recommendation_requests
                         │
                         ▼
                 recommendation_items
                         │
                         ▼
                       movies
```

---

# 135. Core Database Rules for Antigravity

Antigravity MUST follow these rules when implementing the database:

1. PostgreSQL is the source of truth.
2. Use migrations for every schema change.
3. Use internal UUID identifiers for application entities.
4. Keep provider IDs separate from internal IDs.
5. Use `TIMESTAMPTZ` for stored timestamps.
6. Enforce important invariants at the database level.
7. Do not put the whole application model into JSONB.
8. Do not use Redis as a durable source of truth.
9. Keep raw behavioral events separate from current state.
10. Keep session intent separate from persistent memory.
11. Keep explicit memories separate from inferred preferences.
12. Store recommendation requests and recommendation items separately.
13. Attribute recommendation behavior to model versions.
14. Version derived profiles and embeddings.
15. Avoid destructive cascade behavior unless explicitly justified.
16. Avoid N+1 query patterns.
17. Index according to real query patterns.
18. Paginate large collections.
19. Keep external-provider identifiers abstracted.
20. Derived data should be regenerable where practical.
21. Do not introduce a separate database/vector store/search engine without an ADR.
22. Do not partition tables until actual scale justifies it.
23. Do not introduce graph-database infrastructure merely because the product contains graph-like relationships.
24. Keep user-owned data explicitly associated with a user ID.
25. Never trust a client-supplied user ID for authorization.

---

# 136. Final Source-of-Truth Model

The authoritative model is:

```text
                       USER
                        │
          ┌─────────────┼───────────────┐
          │             │               │
          ▼             ▼               ▼
     User State     Conversations    Memories
          │             │               │
          │             ▼               │
          │        Session Intent       │
          │             │               │
          └─────────────┼───────────────┘
                        ▼
                 Recommendation
                    Context
                        │
                        ▼
                 Recommendation
                     Engine
                        │
           ┌────────────┼─────────────┐
           ▼            ▼             ▼
           CF        Semantic      Discovery
           │            │             │
           └────────────┼─────────────┘
                        ▼
                     Ranking
                        │
                        ▼
                   Recommendation
                     Request
                        │
                        ▼
                  Recommendation
                      Items
                        │
                        ▼
                      MOVIE
                        │
                        ▼
                       TMDB
```

The database exists to preserve the durable state underlying that system.

The central architectural distinction is:

**Raw facts and events are stored as authoritative data.**

**Profiles, embeddings, and recommendation artifacts are derived from those facts.**

That distinction must remain intact as CineRec grows.

