# CineRec — Recommendation System

**Status:** Recommendation architecture / source of truth
**Working title:** CineRec
**Version:** 1.0
**Depends on:**

* `01-product-vision.md`
* `02-functional-requirements.md`
* `03-system-architecture.md`
* `04-database-design.md`
* `05-api-contract.md`

**Primary objective:** Build a recommendation system whose personalization is grounded in actual user behavior, enhanced by current conversational context, and designed to evolve from a simple collaborative-filtering foundation into a robust hybrid recommendation architecture.

---

# 1. Recommendation System Vision

CineRec should answer:

> **"Given what this user tends to enjoy, what they want right now, what they have already seen, and what movies are currently relevant, which small set of movies should we show them?"**

The recommendation system must combine:

```text
Long-term user taste
+
Current session intent
+
Explicit preferences
+
Historical behavior
+
Movie metadata
+
Availability
+
Controlled exploration
```

The initial recommendation algorithm is **collaborative filtering**.

However, the recommendation architecture MUST be designed so that collaborative filtering is one component of a broader recommendation system rather than a permanent architectural limitation.

---

# 2. Core Recommendation Architecture

The canonical flow is:

```text id="8d8u9h"
                       Recommendation Request
                                │
                                ▼
                       Context Construction
                                │
         ┌──────────────────────┼───────────────────────┐
         │                      │                       │
         ▼                      ▼                       ▼
   Long-term taste        Current session          Explicit rules
         │                      │                       │
         └──────────────────────┼───────────────────────┘
                                ▼
                      Candidate Generation
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
            CF              Semantic          Popularity
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ▼
                       Candidate Union
                                │
                                ▼
                         Hard Filtering
                                │
                                ▼
                            Ranking
                                │
                                ▼
                      Diversity / Exploration
                                │
                                ▼
                       Recommendation Set
                                │
                                ▼
                      Explanation Metadata
                                │
                                ▼
                              User
                                │
                                ▼
                         Interaction
                                │
                                ▼
                         Learning Signal
```

---

# 3. Fundamental Separation of Responsibilities

The recommendation system MUST keep the following responsibilities distinct.

### LLM

Understands natural-language user intent.

### Collaborative filtering

Learns behavioral relationships between users and movies.

### Semantic retrieval

Finds movies semantically related to a natural-language intent or movie.

### Ranking

Combines candidate signals.

### Filtering

Enforces hard constraints.

### Diversity/exploration

Prevents repetitive or overly narrow result sets.

### TMDB

Provides movie metadata and availability information.

The LLM MUST NOT replace these systems.

---

# 4. Initial MVP Recommendation Strategy

The MVP should use:

```text id="xowt8j"
Collaborative Filtering
+
Popularity fallback
+
Explicit preference filtering
+
Basic contextual filtering
```

The system should start with a straightforward, measurable recommendation baseline before introducing more complex algorithms.

This allows every later improvement to be evaluated against a known baseline.

---

# 5. Recommendation Stages

Every recommendation request should conceptually pass through these stages:

```text id="e8bo4d"
1. Context construction
2. Candidate generation
3. Candidate normalization
4. Hard filtering
5. Candidate scoring
6. Ranking
7. Diversity adjustment
8. Exploration adjustment
9. Explanation generation
10. Final response
```

Each stage should have a clear responsibility.

---

# 6. Recommendation Context

A normalized recommendation context should contain the information required to generate recommendations.

Conceptually:

```json id="2zh2k4"
{
  "user_id": "uuid",
  "session_id": "uuid",
  "surface": "TONIGHT",
  "session_intent": {},
  "long_term_taste": {},
  "explicit_preferences": {},
  "recent_behavior": {},
  "availability": {},
  "already_seen": [],
  "previously_recommended": [],
  "exploration_level": "LOW"
}
```

The recommendation engine should consume a normalized context rather than independently querying unrelated user data.

---

# 7. Context Builder

A dedicated context-builder component should assemble:

```text id="0t4g4q"
User identity
+
Taste profile
+
Explicit memories
+
Recent interactions
+
Viewing history
+
Current conversation intent
+
Watchlist where relevant
+
Availability constraints
+
Previously shown recommendations
```

The resulting context is passed to the recommendation pipeline.

---

# 8. Context Hierarchy

Recommendation signals should follow a conceptual precedence hierarchy:

```text id="c63kpo"
1. Hard explicit current-session constraints
2. Explicit persistent preferences
3. Current-session soft preferences
4. High-confidence learned preferences
5. Recent behavioral signals
6. Long-term learned preferences
7. General popularity/discovery
```

This is a conceptual priority order, not necessarily a literal weighted score.

---

# 9. Hard vs Soft Preferences

A critical distinction:

### Hard constraint

> "Nothing over two hours."

Must exclude movies over the limit.

### Soft preference

> "I usually like shorter movies."

Should influence ranking but does not absolutely exclude longer movies.

The recommendation engine MUST preserve this distinction.

---

# 10. Collaborative Filtering

Collaborative filtering uses collective user behavior to discover relationships between users and movies.

The system learns from interactions such as:

```text id="8t6u3t"
ratings
likes
watches
completions
watchlist additions
```

and determines which movies are likely to interest a user based on patterns observed across the user population.

---

# 11. Initial CF Data Model

The primary training representation is:

```text id="rtx5pj"
user × movie × interaction signal
```

Example:

```text
User A
 ├── Interstellar       5
 ├── Arrival            5
 ├── Inception          5
 └── Her                4
```

The ML pipeline transforms raw interactions into training examples.

---

# 12. Explicit Feedback

Explicit feedback includes:

```text id="jl8gax"
ratings
likes
dislikes
```

These are generally stronger signals because the user intentionally communicated a preference.

A five-star rating should provide more information than merely opening a movie page.

---

# 13. Implicit Feedback

Implicit feedback includes:

```text id="vs9o8v"
click
view
watch_start
watch_complete
watchlist_add
search_click
```

These actions reveal preferences without an explicit rating.

The recommendation system SHOULD use both explicit and implicit signals.

---

# 14. Interaction Weighting

Raw interactions should remain unchanged in the database.

The ML training pipeline may assign weights.

Example configuration:

```text id="f4r9ak"
IMPRESSION              → very weak
CLICK                   → weak
DETAIL_VIEW             → weak
WATCH_START             → moderate
WATCH_COMPLETE          → strong
WATCHLIST_ADD           → strong
LIKE                    → very strong
RATING 5                → very strong
RATING 1                → strong negative
DISLIKE                 → strong negative
TEMPORARY_REJECTION     → contextual negative
```

These values are examples of relative semantics.

Actual numerical weights MUST live in model/training configuration and MUST be evaluated experimentally.

---

# 15. Never Destroy Raw Behavioral Information

Do not replace:

```text id="g7sjq1"
CLICK
WATCH_START
WATCH_COMPLETE
```

with a single:

```text "user likes movie"
```

at ingestion time.

Raw behavior is valuable for:

* future model experiments
* debugging
* analytics
* attribution
* temporal modeling

Derived preference scores can be generated later.

---

# 16. Item-Item Collaborative Filtering

One useful initial strategy is item-item CF.

Conceptually:

```text id="fm6afn"
User likes Interstellar
         │
         ▼
Find users who liked Interstellar
         │
         ▼
What else did those users like?
         │
         ▼
Arrival
The Martian
Contact
Her
```

The model therefore learns:

> Users who enjoy this movie also tend to enjoy these movies.

Item-item relationships are particularly useful for:

* "Because you liked..."
* movie detail pages
* recommendation refinement
* rabbit-hole discovery

---

# 17. User-User Collaborative Filtering

User-user CF identifies users with similar behavioral patterns.

Conceptually:

```text id="a4fcre"
Current user
    │
    ▼
similar users
    │
    ▼
their highly rated movies
    │
    ▼
exclude movies already seen
    │
    ▼
candidate movies
```

This should be supported by the architecture but does not necessarily need to be the first production algorithm.

---

# 18. Matrix Factorization

The initial recommendation system SHOULD support matrix-factorization-based collaborative filtering.

Conceptually:

```text id="2e7f8h"
User × Movie interaction matrix
             │
             ▼
      latent factorization
             │
      ┌──────┴──────┐
      ▼             ▼
 User vectors    Movie vectors
      │             │
      └──────┬──────┘
             ▼
        compatibility
             ↓
       recommendation
```

This enables the system to learn hidden preference dimensions rather than relying solely on explicit user similarity.

---

# 19. Candidate Generation From CF

CF should produce a candidate list, not necessarily the final presentation.

Example:

```text id="qswv49"
CF model
  ↓
500 candidates
```

Those 500 candidates then enter:

```text filtering
+
ranking
+
diversity
```

This separation allows multiple candidate sources to be combined later.

---

# 20. Candidate Source Interface

Every candidate source should conceptually expose:

```text id="7dba5e"
generate_candidates(context)
```

Potential implementations:

```text id="qoo5fs"
CollaborativeFilteringCandidateGenerator
SemanticCandidateGenerator
PopularCandidateGenerator
TrendingCandidateGenerator
ExplorationCandidateGenerator
SimilarMovieCandidateGenerator
```

The application should not need to know how each candidate source works internally.

---

# 21. Candidate Metadata

Every generated candidate SHOULD carry provenance.

Example:

```json id="jw7g9x"
{
  "movie_id": "uuid",
  "source": "COLLABORATIVE_FILTERING",
  "source_score": 0.92
}
```

A movie may be returned from multiple candidate sources.

Example:

```json id="syqm1j"
{
  "movie_id": "uuid",
  "sources": [
    {
      "type": "COLLABORATIVE_FILTERING",
      "score": 0.92
    },
    {
      "type": "SEMANTIC",
      "score": 0.86
    }
  ]
}
```

---

# 22. Candidate Union

The system should combine candidate sets:

```text id="qlu0y3"
CF candidates
      +
semantic candidates
      +
popular candidates
      +
exploration candidates
```

Duplicate movie IDs must be deduplicated.

Candidate provenance should be merged rather than discarded.

---

# 23. Candidate Pool Size

The recommendation engine SHOULD operate internally on a candidate pool considerably larger than the number presented to the user.

Example:

```text id="3a0gsi"
5 final recommendations

could originate from:

500+ CF candidates
+
100 semantic candidates
+
50 popularity candidates
+
20 exploration candidates
```

The exact numbers are configurable.

The user-facing API should remain small.

---

# 24. Hard Filtering

Before final ranking, apply hard exclusions.

Potential filters:

```text id="7od9d4"
already watched
explicitly blocked
wrong language
runtime violation
provider unavailable
invalid movie
duplicate movie
age/content constraints where applicable
```

Hard filters MUST be implemented by application logic.

They MUST NOT depend solely on the LLM.

---

# 25. Already-Watched Filtering

By default, recommendation surfaces should generally exclude movies the user has already completed.

Exceptions MAY exist for:

* rewatches
* nostalgia
* explicit requests
* "favorite movies"
* movie history exploration

The surface/request should determine whether watched content is eligible.

---

# 26. Watchlist Handling

Watchlist membership is not necessarily an exclusion.

A movie already on the watchlist may still be recommended as:

> "You saved this earlier."

The recommendation engine should therefore treat watchlist state as contextual information rather than automatically excluding it.

---

# 27. Explicit Dislike Handling

Explicitly disliked movies should generally be excluded from future recommendation candidate sets.

The application should support a clear mechanism for reversing the dislike.

---

# 28. Temporary Rejection

A temporary rejection such as:

> "Not tonight."

should normally affect:

```text current session
```

rather than create a permanent dislike.

The system may reduce the movie's score for the active session without permanently removing it from future recommendations.

---

# 29. Runtime Filtering

Runtime requirements should support:

```text id="5v0gq9"
minimum runtime
maximum runtime
preferred runtime range
```

Hard constraints exclude.

Soft preferences rank.

---

# 30. Language Filtering

Language should similarly support:

```text id="5d4mpp"
required languages
preferred languages
excluded languages
```

The difference between:

> "English only"

and:

> "I'd prefer English"

must remain explicit.

---

# 31. Availability Filtering

If the user explicitly says:

> "I have Netflix."

the recommendation engine should be capable of filtering candidates according to known provider/region availability.

Availability data may be stale.

Therefore the system should treat availability as a data source with freshness metadata rather than absolute permanent truth.

---

# 32. Ranking

After filtering:

```text id="6bxlqq"
candidate pool
    ↓
ranking function
    ↓
ordered candidate set
```

Ranking combines multiple signals.

Conceptually:

```text id="yoq9w5"
Final score =
    personalization
  + current-context match
  + semantic relevance
  + quality/popularity
  + exploration
  + novelty
  - negative preference penalties
  - repetition penalties
```

The exact scoring function is configurable and versioned.

---

# 33. Personalization Score

The personalization component estimates:

> How strongly does this movie fit the user's historical taste?

Possible sources:

* CF predicted preference
* user/movie latent similarity
* creator preference
* genre preference
* theme preference
* historical interactions

---

# 34. Current Context Score

The context component estimates:

> How well does this movie fit what the user wants right now?

Possible signals:

```text id="b4t6v3"
mood
desired emotion
energy
complexity
pacing
runtime
language
theme
current situation
```

This prevents long-term taste from dominating current intent.

---

# 35. Semantic Score

Later, semantic retrieval can estimate:

> How semantically related is this movie to the user's natural-language request?

Example:

```text id="g2r9pu"
"I want something lonely but ultimately hopeful"
```

can be converted into a representation suitable for semantic retrieval.

---

# 36. Popularity Score

Popularity may provide:

* cold-start support
* fallback recommendations
* quality/stability signal

Popularity MUST NOT automatically dominate personalized recommendations.

---

# 37. Exploration Score

Exploration rewards candidates that are:

* novel for the user
* slightly outside usual taste
* still contextually relevant

The exploration score should increase when the user requests:

> "Surprise me."

and decrease when the user says:

> "Just give me something I know I'll love."

---

# 38. Negative Preference Penalty

Explicit negative preferences should create strong penalties or hard exclusions depending on the user's wording.

Example:

> "I don't want horror tonight."

Current-session exclusion.

Example:

> "I hate horror. Never recommend it."

Persistent exclusion.

---

# 39. Repetition Penalty

The system should reduce scores for movies that were:

* recently shown
* repeatedly skipped
* recently rejected

unless the user explicitly requests them.

This prevents the system from repeatedly recommending the same content.

---

# 40. Ranking Formula

A conceptual initial scoring structure:

```text id="zzkmee"
score(movie, user, context) =

    w_cf          × cf_score
  + w_context     × context_score
  + w_semantic    × semantic_score
  + w_quality     × quality_score
  + w_exploration × exploration_score
  + w_novelty     × novelty_score
  - w_repeat      × repetition_penalty
  - w_negative    × negative_preference_penalty
```

The weights MUST be configurable.

Weights MUST NOT be hardcoded across many files.

---

# 41. Hard Constraints vs Score

Do not encode every rule as a penalty.

For example:

> Maximum runtime = 120 minutes.

Should normally be:

```text candidate > 120
→ remove
```

rather than:

```text candidate > 120
→ subtract 0.12 points
```

Explicit hard requirements should remain hard.

---

# 42. Score Normalization

Candidate sources may produce scores with different ranges.

For example:

```text CF:        0–1
semantic:     cosine-like score
popularity:   arbitrary magnitude
```

These MUST be normalized before combination.

The normalization method should be part of the recommendation configuration.

---

# 43. Ranking Model Evolution

Start with a transparent weighted ranker.

Later, the system MAY evolve toward:

```text id="9n7fgx"
hand-tuned weighted ranker
        ↓
learning-to-rank
        ↓
neural ranker
```

The API contract should remain unchanged.

---

# 44. Why Not Start With Deep Learning?

The initial system should not use a complicated neural ranking model simply because it sounds advanced.

Deep ranking models require:

* more data
* more tuning
* more compute
* more evaluation complexity
* more difficult debugging

A strong modular baseline is preferable.

Complexity should be earned by evidence.

---

# 45. Diversity

The final recommendations should not all be nearly identical.

Suppose the candidate pool contains:

```text
10 similar Nolan sci-fi films
```

A good final set might include:

```text
one close match
one adjacent genre
one different emotional approach
one wildcard
```

where appropriate.

---

# 46. Diversity Algorithm

The ranking stage MAY eventually use a method such as:

```text id="5v0bxd"
relevance
-
λ × similarity_to_already_selected
```

The principle is:

> Highly relevant candidates should still compete against each other, but redundant candidates should incur a diversity penalty.

The specific algorithm can evolve.

---

# 47. Exploration / Exploitation

CineRec should balance:

```text id="we44fl"
EXPLOITATION
→ likely to satisfy existing taste

EXPLORATION
→ potentially expands taste
```

The user should have influence over this balance.

Possible levels:

```text id="f8f6uw"
LOW
MEDIUM
HIGH
```

or an equivalent representation.

---

# 48. Surface-Specific Recommendation Behavior

Different product surfaces should have different objective functions.

### Tonight

Optimize strongly for current context.

### For You

Optimize for long-term personalization.

### Because You Liked X

Optimize for item similarity.

### Wildcard

Optimize for novelty and controlled exploration.

### Movie Detail

Optimize for similarity/contextual relevance.

### Trending for You

Combine popularity and personalization.

The same engine can serve all of these by receiving different surface configuration.

---

# 49. Surface Configuration

Recommendation surfaces SHOULD use configuration objects rather than duplicated ranking logic.

Conceptually:

```json id="k80mjc"
{
  "surface": "TONIGHT",
  "exploration_weight": 0.15,
  "context_weight": 0.40,
  "personalization_weight": 0.35,
  "diversity_weight": 0.10
}
```

These values are illustrative.

Actual values belong in configuration and experimentation.

---

# 50. "Because You Liked..." Flow

The system should support:

```text id="ry15n2"
Movie X
   ↓
find related candidates
   ↓
combine item-CF / semantic similarity
   ↓
exclude seen/rejected
   ↓
rank
   ↓
recommend
```

This provides a simple, intuitive recommendation surface.

---

# 51. "Tonight" Flow

The canonical orb flow:

```text id="j1sfpk"
User message
      ↓
Gemini
      ↓
structured session intent
      ↓
context builder
      ↓
CF candidate retrieval
      +
semantic retrieval
      +
availability
      ↓
hard filters
      ↓
contextual ranker
      ↓
diversity
      ↓
3–5 movies
```

---

# 52. Recommendation Context Example

User:

> "I've had a long day. Something funny, warm, under two hours. Nothing depressing."

Context:

```json id="p9jl2e"
{
  "mood": ["LOW"],
  "desired_emotions": ["COMFORT", "HUMOR"],
  "energy": "LOW",
  "emotional_intensity": "LOW",
  "max_runtime_minutes": 120,
  "negative_emotions": ["DEPRESSING"]
}
```

Long-term profile:

```json id="8amk66"
{
  "genres": {
    "SCIENCE_FICTION": 0.91,
    "DRAMA": 0.76,
    "COMEDY": 0.52
  },
  "styles": {
    "SLOW_BURN": 0.71
  }
}
```

The recommendation system should combine both.

---

# 53. Cold Start — New User

A new user has no collaborative history.

The system should use:

```text id="mt3d7h"
conversation
+
favorite-movie onboarding
+
initial ratings
+
popular movies
+
semantic/contextual matching
```

As interactions accumulate:

```text id="e6bvyh"
new behavior
 ↓
taste profile
 ↓
CF personalization
```

---

# 54. New User Bootstrap

The orb SHOULD be able to ask something like:

> "Give me three movies you love."

The user can search/select them.

These become seed preferences.

This is preferable to forcing a lengthy questionnaire.

---

# 55. New Movie Cold Start

A movie with little collaborative history can still enter candidate pools through:

```text id="09y2t2"
metadata
genres
keywords
cast/crew
semantic embeddings
popularity
```

This avoids permanently excluding new content.

---

# 56. Popularity Fallback

If personalized CF is unavailable or insufficient:

```text id="6n3k3u"
quality-filtered popular movies
```

can provide recommendations.

Popularity should be region-aware where relevant.

---

# 57. Model Training Dataset

Initial training data may come from MovieLens or another legally usable dataset.

The system should clearly distinguish:

```text id="cbpwwz"
bootstrap training data
```

from:

```text production user interactions
```

As production data accumulates, it can become an increasingly important training source.

---

# 58. Training Data Pipeline

Canonical pipeline:

```text id="xclt5w"
Production interactions
        +
Bootstrap dataset
        ↓
Data extraction
        ↓
Validation
        ↓
Cleaning
        ↓
Temporal splitting
        ↓
Interaction weighting
        ↓
Training matrix
        ↓
Model training
        ↓
Evaluation
```

---

# 59. Temporal Evaluation

Recommendation evaluation SHOULD consider temporal ordering.

Preferred:

```text id="h3g4qs"
Past interactions
      ↓
training
      ↓
future interactions
      ↓
test
```

This more closely reflects the real-world task.

---

# 60. Train/Validation/Test

Where sufficient data exists:

```text id="uz8axm"
TRAIN
→ older interactions

VALIDATION
→ later interactions

TEST
→ newest held-out interactions
```

Exact proportions are dataset/model dependent.

The test set should remain untouched during model tuning.

---

# 61. Evaluation Metrics

At minimum evaluate:

```text id="38w4tq"
Precision@K
Recall@K
Hit Rate@K
NDCG@K
MAP@K
```

The recommendation system SHOULD also evaluate:

```text id="6smm3n"
catalog coverage
diversity
novelty
```

---

# 62. Offline vs Online Metrics

Offline ML metrics:

```text id="2v3sq1"
Precision@K
Recall@K
NDCG@K
```

measure model behavior against historical data.

Online product metrics:

```text id="r3r7w7"
click-through
watchlist addition
watch rate
completion
repeat usage
```

measure actual user behavior.

They MUST NOT be treated as interchangeable.

---

# 63. Popularity Baseline

Before claiming the CF model is useful, the system MUST have a simple baseline.

For example:

```text id="yoe4lm"
global popularity
```

or:

```text regional popularity
```

The CF model should demonstrate measurable improvement against the baseline on appropriate evaluation data.

---

# 64. Model Comparison

The ML pipeline SHOULD support comparisons such as:

```text id="8w2fkn"
Popularity
      ↓
Item-Item CF
      ↓
Matrix Factorization
      ↓
Hybrid Ranker
```

Actual metrics must be generated from experiments.

Never hardcode or invent performance numbers.

---

# 65. Model Versioning

Each recommendation model MUST have a unique version.

Example:

```text id="09nqsl"
cf-als-v1
cf-als-v2
hybrid-v3
```

Recommendation requests SHOULD record the version used.

---

# 66. Model Metadata

Each model version SHOULD record:

```text id="7l7jch"
algorithm
training dataset version
feature configuration
hyperparameters
evaluation metrics
artifact location
creation timestamp
status
```

This makes model behavior reproducible.

---

# 67. Model Lifecycle

Expected lifecycle:

```text id="iqedmb"
TRAINED
   ↓
EVALUATED
   ↓
REGISTERED
   ↓
STAGING
   ↓
ACTIVE
   ↓
RETIRED
```

A failed experiment should never accidentally become the active production model.

---

# 68. Model Loading

The active model should be loaded for inference.

Normal recommendation requests should NOT retrain the model.

Conceptually:

```text id="4r7se0"
service startup
 ↓
load active model
 ↓
ready for inference
```

---

# 69. Model Artifact Separation

Model artifacts should be separate from transactional application data.

For example:

```text id="c0imf4"
model artifact
```

plus:

```text model_versions
```

metadata in PostgreSQL.

---

# 70. Retraining

Initial retraining can be scheduled periodically.

Example:

```text id="gpejm0"
weekly
```

or whenever sufficient new interaction data becomes available.

The cadence should be configuration-driven and based on actual data volume.

---

# 71. Incremental vs Full Retraining

MVP:

```text id="g5gl1w"
periodic full retraining
```

Future:

```text id="0fj6id"
incremental updates
+
periodic full retraining
```

The system should not implement complex online learning until enough data and operational need exist.

---

# 72. Near-Real-Time Personalization

A user's latest action can influence short-term recommendations without retraining the entire model.

Example:

```text id="dd2oj9"
user rates Arrival 5
       ↓
update recent preference state
       ↓
invalidate/refresh recommendation cache
       ↓
next request reflects Arrival
```

This provides freshness without expensive model retraining.

---

# 73. Preference Aggregation

A separate preference aggregation layer can convert raw behavior into:

```text id="t5m2m3"
genre scores
theme scores
creator affinity
style preferences
runtime tendencies
```

These derived signals can complement CF.

---

# 74. Taste Profile

The taste profile is a derived representation.

Example:

```json id="uvkyq2"
{
  "genres": {
    "science_fiction": 0.91,
    "drama": 0.76
  },
  "themes": {
    "identity": 0.84,
    "loneliness": 0.68
  }
}
```

The system should version this profile.

---

# 75. Taste Profile vs CF Model

These are related but distinct.

### Taste profile

Human-readable/structured derived preference representation.

### CF model

Statistical model trained from many users and items.

The application may use both.

---

# 76. Semantic Movie Representation

For future hybrid recommendation, movie content can be represented semantically.

Potential input:

```text id="0prj2e"
title
overview
genres
keywords
themes
creator information
```

This can be transformed into an embedding.

---

# 77. Semantic Candidate Generation

Potential future flow:

```text id="k8n9v1"
Current user intent
        ↓
semantic representation
        ↓
vector retrieval
        ↓
nearest movies
```

This is particularly useful when the user gives a highly nuanced request that collaborative filtering cannot directly understand.

---

# 78. User Semantic Representation

The architecture MAY eventually maintain a semantic representation of long-term taste.

For example:

```text id="54i4oo"
user preferences
      ↓
taste representation
      ↓
embedding
```

The exact representation should be model/version specific.

---

# 79. Hybrid Recommendation

The long-term target architecture is:

```text id="p7xc4l"
                         Candidate Sources
                                │
         ┌──────────────────────┼────────────────────┐
         ▼                      ▼                    ▼
       CF                     Semantic            Popular
         │                      │                    │
         └──────────────────────┼────────────────────┘
                                ▼
                        Candidate Union
                                │
                                ▼
                         Hard Filtering
                                │
                                ▼
                              Ranker
                                │
                                ▼
                         Diversity Layer
                                │
                                ▼
                           Final Top-N
```

---

# 80. Hybrid Ranker Responsibility

The hybrid ranker should combine:

```text id="hsvqi5"
CF relevance
semantic relevance
context relevance
quality
novelty
exploration
```

while respecting:

```text hard filters
explicit negative preferences
```

---

# 81. Explanations

The recommendation pipeline should generate structured explanation signals before any natural-language explanation is created.

Example:

```json id="uhovb0"
{
  "primary_reason": "CURRENT_CONTEXT",
  "signals": [
    "LOW_ENERGY",
    "COMEDY_MATCH",
    "LONG_TERM_SCI_FI_PREFERENCE"
  ]
}
```

The UI/LLM can then turn this into:

> "You usually like cerebral sci-fi, but tonight you asked for something warmer and lighter."

---

# 82. Explanation Grounding

The explanation generator MUST receive actual recommendation evidence.

Bad:

```text id="0w4u6u"
LLM:
"I recommended this because you love space movies."
```

when no such preference exists.

Good:

```text id="7y9sne"
ranker:
user_sci_fi_affinity = 0.91
current_energy = LOW
runtime_match = TRUE
```

Then the LLM explains those actual signals.

---

# 83. Explanation Signal Types

Potential signal IDs:

```text id="7ad4em"
LONG_TERM_TASTE
CURRENT_MOOD
CURRENT_CONTEXT
EXPLICIT_PREFERENCE
SIMILAR_USERS
SIMILAR_MOVIE
SEMANTIC_MATCH
RUNTIME_MATCH
LANGUAGE_MATCH
AVAILABILITY_MATCH
EXPLORATION
NOVELTY
POPULARITY
```

---

# 84. Avoiding Recommendation Loops

The system should track recently recommended items.

Candidate filtering should account for:

```text id="3ys2k5"
recently recommended
recently rejected
already watched
already disliked
```

This reduces repetitive sessions.

---

# 85. Session-Level Exclusions

The active recommendation session should maintain a temporary exclusion set.

Example:

```text id="2z1m0n"
User:
"No, not that."

→ add movie to current session exclusion
```

This should affect subsequent recommendations immediately.

---

# 86. Session-Level Positive Signals

Similarly:

> "More like that."

should increase emphasis on characteristics of the selected/referenced movie.

Potential signals:

```text id="7bqsoz"
movie
genre
theme
creator
semantic representation
CF relationships
```

---

# 87. "More Like This"

When the user says:

> "More like this."

the system should not simply duplicate a generic `/similar` result.

It should combine:

```text id="gq4w7n"
selected movie
+
current session context
+
user taste
```

Then produce a personalized ranking.

---

# 88. "Less Like This"

Likewise:

> "Too complicated."

should lower the relevance of candidates associated with high complexity.

The system should modify the current session context rather than permanently change the user's taste profile unless explicitly requested.

---

# 89. User Feedback as Training Signal

A recommendation interaction is not merely analytics.

Examples:

```text id="c1yxwm"
click
watchlist
watch
complete
like
dislike
```

can become future model training signals.

However, the ML pipeline should use carefully designed weighting and temporal treatment rather than assuming:

```text click = love
```

---

# 90. Negative Feedback

Negative signals should include:

```text id="z4rv7m"
dislike
explicit "never recommend"
repeated skips
temporary rejection
abandonment
```

Their meanings differ.

A one-time skip is weaker evidence than an explicit permanent dislike.

---

# 91. Temporal Preferences

Taste can change.

The model should support recent behavior having more relevance when appropriate.

For example:

```text id="vv41h6"
last month:
mostly comedies

two years ago:
mostly action
```

Recent behavior may be more useful for short-term personalization.

The exact decay strategy belongs to the ML pipeline.

---

# 92. Preference Decay

Derived preferences MAY use time decay.

Conceptually:

```text id="nfo4he"
older evidence
→ lower weight

newer evidence
→ higher weight
```

However, explicit permanent preferences should not automatically decay merely because time passed.

---

# 93. Explicit Preference Override

If the user explicitly says:

> "I no longer want horror."

the recommendation engine should immediately respect it even if historic data indicates otherwise.

---

# 94. Recommending Already-Rated Movies

A rated movie is not necessarily watched state in every imaginable data source, but within the product a rating strongly implies the movie was experienced.

The application should define clear semantics.

By default, explicitly rated movies should be treated as seen and excluded from ordinary recommendation results.

---

# 95. Rewatch Recommendations

Future functionality MAY allow:

> "I want something I know I'll love."

In this mode, previously enjoyed movies may become eligible.

The recommendation request surface should explicitly signal that rewatches are allowed.

---

# 96. Recommendation Diversity by Creator

The final recommendation set should avoid unnecessarily producing:

```text id="0wsm4j"
Christopher Nolan
Christopher Nolan
Christopher Nolan
Christopher Nolan
```

unless that is exactly what the user asked for.

Creator-level diversity can be a ranking constraint.

---

# 97. Recommendation Diversity by Genre

Likewise:

```text id="sj3kva"
Sci-Fi
Sci-Fi
Sci-Fi
Sci-Fi
```

may be undesirable in a discovery-oriented surface.

However, genre diversity should not override a strong explicit preference.

---

# 98. Recommendation Categories

Recommendation items MAY be assigned presentation categories:

```text id="8snf7n"
SAFE_BET
COMFORT_PICK
WILDCARD
HIDDEN_GEM
```

The category should arise from the recommendation context and ranking behavior.

It should not simply correspond to fixed database rows.

---

# 99. Safe Bet

A Safe Bet should emphasize:

```text id="6n7bcv"
strong personalization
high confidence
lower exploration
```

It is designed to minimize decision risk.

---

# 100. Comfort Pick

A Comfort Pick should emphasize:

```text id="83x9h1"
current emotional/contextual suitability
+
known positive preferences
```

This category is especially relevant to orb sessions.

---

# 101. Wildcard

A Wildcard should emphasize:

```text id="8sxqak"
novelty
exploration
contextual relevance
```

It should not be randomly selected.

The system should still have evidence for why the candidate may work.

---

# 102. Hidden Gem

A Hidden Gem may emphasize:

```text id="j4r6eg"
lower popularity
strong relevance
```

Popularity should not be treated as the same thing as quality.

---

# 103. Recommendation Count

The UI should generally receive a small recommendation set.

Typical orb session:

```text id="qfozxq"
3–5 recommendations
```

The backend may generate many more candidates internally.

---

# 104. Recommendation Ordering

Ordering matters.

Position should reflect the final ranking objective.

The system SHOULD record:

```text id="o0h2im"
position
score
category
candidate sources
```

This enables later attribution.

---

# 105. Position Bias

User interaction is often influenced by position.

Therefore analytics and offline evaluation should consider that:

> A movie displayed first has a greater opportunity to be clicked.

The recommendation system should record position so future analysis can account for this.

---

# 106. Recommendation Impressions

When recommendations are actually displayed, the application should generate impression events.

Generated but never displayed recommendations should not be falsely counted as impressions.

---

# 107. Recommendation Attribution

Each recommendation item should be traceable to:

```text id="et2vg9"
recommendation_request_id
model_version
candidate sources
position
surface
```

This supports analysis such as:

> Which recommendation strategy produced this successful watch?

---

# 108. Recommendation Cache

Recommendations can be cached where appropriate.

Examples:

```text id="h16nk4"
user:{id}:recommendations:home
user:{id}:recommendations:tonight
```

However:

Current orb sessions are highly contextual and may have lower cacheability than static home recommendations.

The recommendation architecture must not assume that every request should be cached.

---

# 109. Cache Invalidation

Caches SHOULD be invalidated or refreshed after major preference-changing events:

```text id="w9cgzo"
rating
like/dislike
explicit memory update
major watch completion
taste profile change
model change
```

The exact policy depends on the surface.

---

# 110. Precomputed Recommendations

For non-conversational surfaces such as:

```text id="u6k2ve"
For You
Trending for You
```

the system MAY precompute recommendations asynchronously.

This reduces request latency.

---

# 111. On-Demand Recommendations

For:

```text id="c3v9ke"
Tonight
conversation
custom query
```

recommendations should generally be generated on demand because current intent matters.

---

# 112. Recommendation Latency Strategy

A conversational request should avoid unnecessary sequential work.

Prefer:

```text id="zhbn2j"
load context
+
load candidates
+
parallelizable metadata retrieval
```

where feasible.

Do not make ten serial upstream API calls just to generate five movies.

---

# 113. TMDB Dependency

TMDB is primarily responsible for movie facts and metadata.

The recommendation engine should not require a live TMDB request for every candidate if sufficient internal movie data already exists.

---

# 114. External Metadata Enrichment

Preferred flow:

```text id="q7e3lm"
candidate movie IDs
       ↓
internal movie lookup
       ↓
missing metadata?
       ↓
TMDB enrichment
```

The recommendation engine should work primarily from internal data.

---

# 115. Recommendation Candidate Integrity

Every final candidate MUST resolve to a valid internal movie record.

Do not return:

```text id="0l2d5a"
movie title only
```

without an internal movie identity.

---

# 116. Unknown / Removed Movies

If a candidate points to a movie whose metadata is no longer valid:

```text id="i4frrh"
remove candidate
```

Do not return broken movie cards.

---

# 117. Model Failure

If the active CF model cannot be loaded or is unavailable:

```text id="5stmr1"
CF
 ↓
failure
 ↓
fallback candidate generation
```

The system should remain useful where possible.

---

# 118. Recommendation Fallback Hierarchy

Conceptually:

```text id="z2t7dr"
Hybrid personalized
        ↓
Collaborative filtering
        ↓
Semantic/content matching
        ↓
Popularity/trending
        ↓
basic catalog discovery
```

The exact fallback policy can vary by surface.

---

# 119. Recommendation Failure Observability

The system should record:

```text id="a5cddv"
fallback_used
fallback_reason
model_version
candidate_source
latency
```

This allows us to identify reliability problems.

---

# 120. Offline Model Evaluation Pipeline

A reproducible evaluation command should conceptually perform:

```text id="qv7q6w"
load dataset
 ↓
split temporally
 ↓
train model
 ↓
generate Top-K
 ↓
exclude known training interactions
 ↓
compare with held-out future interactions
 ↓
compute metrics
 ↓
store evaluation result
```

---

# 121. Evaluation Reproducibility

Each evaluation should record:

```text id="ik01qp"
dataset version
model version
configuration
metrics
timestamp
```

A future developer should be able to understand why model A was promoted over model B.

---

# 122. Hyperparameters

Model hyperparameters must not be scattered throughout code.

Examples:

```text id="nfsu5k"
latent_dimensions
regularization
iterations
learning_rate
interaction_weights
negative_sampling
```

Store them in model configuration.

---

# 123. Configuration Versioning

Model configurations SHOULD be versioned alongside model artifacts.

Example:

```text id="h7c1vk"
model:
  version: cf-als-v5

config:
  latent_dimensions: 128
  regularization: 0.1
  iterations: 30
```

The exact values are experimental.

---

# 124. Negative Sampling

For implicit-feedback models that require negative examples, the ML pipeline should define an explicit negative-sampling strategy.

It should not arbitrarily interpret every unseen movie as a negative preference.

Unseen means:

> unknown.

Not:

> disliked.

---

# 125. Unknown vs Negative

This distinction is critical.

```text id="1m0gqb"
NOT WATCHED
≠
DISLIKED
```

The training pipeline must preserve that distinction.

---

# 126. Exposure Bias

An item not interacted with may never have been shown to the user.

Therefore:

```text id="e3lkt4"
no interaction
```

does not automatically imply:

```text user rejected item
```

Future recommendation evaluation should account for exposure where possible.

---

# 127. Interaction Weighting and Exposure

When an item is displayed and skipped, that is more informative than a movie that was never displayed.

The recommendation system should preserve impression data so such distinctions remain possible.

---

# 128. Session Feedback Loop

A conversational session should have a rapid feedback loop:

```text id="jr3q5f"
recommend
 ↓
user reaction
 ↓
session update
 ↓
re-rank
 ↓
new recommendation
```

No complete model retraining is necessary for this.

---

# 129. Session Preference Updates

Examples:

```text id="5vcgyp"
"Too sad"
→ lower emotional intensity

"Too slow"
→ increase pacing preference

"Something funnier"
→ increase humor/comedy signal

"Nothing foreign tonight"
→ language exclusion

"More like the second one"
→ increase similarity to selected movie
```

These changes should generally remain session-specific.

---

# 130. Session Recommendation State

The active session can maintain:

```text id="3esj4u"
current intent
candidate exclusions
selected references
recent recommendations
recent feedback
exploration preference
```

This state enables conversational refinement.

---

# 131. "I Have Already Seen It"

When the user says:

> "I've seen that."

The system should:

1. mark or confirm viewing state if appropriate
2. add the movie to current session exclusion
3. generate a replacement recommendation
4. optionally use the movie as a positive similarity anchor if the context implies they liked it

The system must not automatically infer whether the user liked the movie merely because they watched it.

---

# 132. "I Loved It"

If the user says:

> "I loved that."

This may create:

```text id="umg8tn"
strong positive session signal
```

and MAY also contribute to long-term preference learning through an interaction event.

---

# 133. "I Hated It"

A strong negative response can produce:

```text id="9h1cvx"
negative session signal
```

and, when explicit enough:

```text persistent negative preference
```

The application should distinguish the two.

---

# 134. Movie Similarity

Similarity can be generated through multiple mechanisms:

```text id="qixonm"
collaborative similarity
metadata similarity
semantic similarity
creator similarity
theme similarity
```

The product should not expose the implementation as fact unless necessary.

---

# 135. Creator Affinity

The system may derive affinity for:

* directors
* actors
* writers

from user interactions.

This should be a supplementary signal, not necessarily the primary CF representation.

---

# 136. Genre Affinity

The system can derive genre preferences from:

* ratings
* likes
* watches
* completions
* watchlist
* repeated behavior

Genre preference should not be inferred from one isolated interaction.

---

# 137. Theme Affinity

Theme signals may come from movie metadata and semantic representations.

Examples:

```text id="3y6bbo"
identity
loneliness
friendship
ambition
time
family
survival
```

These can help contextual recommendation.

---

# 138. Quality Signals

Movie quality MAY incorporate:

* provider rating
* vote count
* popularity
* internal engagement
* recommendation success

Quality should not overwhelm user relevance.

A globally popular movie is not automatically the right movie for a particular user.

---

# 139. Novelty

Novelty can measure how unfamiliar a movie is to the user.

For example:

```text id="1h7xyj"
never seen
not recently shown
not in watchlist
not heavily represented in history
```

This can support discovery.

---

# 140. Diversity vs Novelty

These are different:

### Diversity

Different recommendations are meaningfully different from one another.

### Novelty

Recommendations are less familiar to the user.

The system should optimize both independently.

---

# 141. Coverage

Catalog coverage measures how much of the available catalog is ever recommended.

A model that recommends only 50 blockbuster movies to everyone may have good short-term engagement but poor discovery breadth.

Coverage should therefore be monitored.

---

# 142. Recommendation Quality Dashboard

The recommendation system should eventually expose:

```text id="sx8r5w"
Model
Training dataset
Precision@K
Recall@K
NDCG@K
MAP@K
Hit Rate
Coverage
Diversity
Novelty
Fallback rate
Latency
```

These metrics must be backed by actual measurements.

---

# 143. User-Level Recommendation Metrics

Where appropriate, evaluate recommendation quality across users rather than only globally.

This can reveal whether a model works well for:

* heavy users
* light users
* new users
* users with sparse data

---

# 144. Segment Awareness

The recommendation system should recognize that:

```text id="k88y2w"
new user
```

and:

```text experienced user
```

require different strategies.

Potential segments:

```text id="xdr2f7"
cold
sparse
moderate-history
rich-history
```

The exact thresholds should be configuration.

---

# 145. Sparse User Strategy

For users with only a few interactions:

```text id="8c7x4m"
CF
+
semantic/contextual
+
popular
```

should be combined.

Pure CF should not dominate until sufficient data exists.

---

# 146. Rich User Strategy

For users with extensive history:

```text id="3u7wmh"
CF
+
taste profile
+
context
+
semantic retrieval
+
exploration
```

can provide deeper personalization.

---

# 147. Personalized Exploration

Exploration should depend on the user.

A user who constantly requests:

> "Give me something new."

should receive more exploration.

A user who consistently wants:

> "Something safe."

should receive less.

This can be modeled as a user/session-level exploration preference.

---

# 148. User-Controlled Recommendation Style

The orb may eventually support explicit controls:

```text id="yiy5ai"
SAFE
BALANCED
SURPRISING
```

These controls should modify ranking weights rather than invoke entirely unrelated algorithms.

---

# 149. Model Architecture Interface

The application should conceptually expose:

```text id="tt6c03"
RecommendationEngine
```

with operations such as:

```text recommend(context)
generate_candidates(context)
rank(candidates, context)
explain(recommendation)
```

The exact interface belongs to implementation, but the conceptual separation is mandatory.

---

# 150. Candidate Generator Interface

Conceptually:

```text id="xpkp6t"
CandidateGenerator
        │
        ├── CFGenerator
        ├── SemanticGenerator
        ├── PopularGenerator
        ├── SimilarMovieGenerator
        └── ExplorationGenerator
```

Each returns candidates plus source metadata.

---

# 151. Ranker Interface

Conceptually:

```text id="1p4z6j"
Ranker
   ↓
rank(candidates, context)
```

Potential implementations:

```text id="ax40yr"
WeightedRanker
LearningToRank
NeuralRanker
```

The application should not care which one is active.

---

# 152. Filter Interface

Conceptually:

```text id="zjzr3y"
CandidateFilter
   │
   ├── SeenFilter
   ├── PreferenceFilter
   ├── RuntimeFilter
   ├── LanguageFilter
   └── AvailabilityFilter
```

Filters should be composable.

---

# 153. Explanation Interface

Conceptually:

```text id="v0g4l1"
RecommendationExplainer
        ↓
structured evidence
        ↓
natural language
```

The explanation layer should never alter the recommendation ranking.

---

# 154. Recommendation Purity

Recommendation generation should ideally behave as a mostly deterministic function of:

```text id="y3566a"
context
+
model
+
configuration
+
candidate data
```

Randomness for exploration should be controlled and reproducible where practical.

---

# 155. Randomness

If randomization is used:

* control it with a seed where reproducibility matters
* do not let arbitrary randomness destroy recommendation quality
* retain enough information to understand the selection

---

# 156. Recommendation Determinism

The same request/context may produce slightly different results when exploration is intentionally enabled.

However, the system should not produce wildly inconsistent recommendations due to uncontrolled randomness.

---

# 157. Feature Flags

Recommendation behavior should support feature flags such as:

```text id="18x3v0"
ENABLE_SEMANTIC_RETRIEVAL
ENABLE_HYBRID_RANKER
ENABLE_EXPLORATION
ENABLE_DIVERSITY
```

This permits safer rollout.

---

# 158. A/B Experimentation

Future recommendation experiments can compare:

```text id="5e3ql7"
Model A
vs
Model B
```

with assignment at the user level.

The system should record:

```text experiment
variant
model version
recommendation request
outcome
```

---

# 159. Experiment Isolation

An experiment should change only the intended recommendation behavior.

The system should preserve:

```text id="af44m0"
user identity
user history
privacy
```

regardless of model variant.

---

# 160. Experiment Metrics

Potential metrics:

```text id="xjhh3n"
CTR
watchlist addition
watch start
completion
rating
session continuation
diversity
novelty
```

Metrics should be interpreted carefully because each measures a different stage of the user journey.

---

# 161. Avoiding Optimizing for Clickbait

A model should not be considered better merely because it generates more clicks.

A movie could receive clicks without being watched or enjoyed.

Recommendation evaluation should therefore include downstream outcomes where measurable.

---

# 162. Recommendation Funnel

Useful conceptual funnel:

```text id="kp9ykg"
IMPRESSION
    ↓
CLICK
    ↓
DETAIL VIEW
    ↓
WATCH
    ↓
COMPLETE
    ↓
LIKE / RATING
```

Each stage provides a different quality signal.

---

# 163. Position-Aware Evaluation

Because position affects exposure, recommendation analysis should retain position.

Future experimentation may consider position-adjusted evaluation methods.

---

# 164. User Feedback Quality

Explicit feedback is valuable.

The product should therefore make feedback lightweight:

```text id="m7z5kq"
❤️ Loved it
👍 Like
😐 Not tonight
👎 Not for me
```

The system can map these to different interaction strengths.

---

# 165. Interaction-to-Model Pipeline

Canonical learning loop:

```text id="2zmnby"
User behavior
     ↓
Interaction event
     ↓
PostgreSQL
     ↓
training-data extraction
     ↓
ML preprocessing
     ↓
model training
     ↓
evaluation
     ↓
model registry
     ↓
active model
```

---

# 166. No Direct Online Training

Normal user actions MUST NOT trigger full model training synchronously.

Training is an offline process.

---

# 167. Near-Term Personalization Without Training

User actions can update:

```text id="2qd6qf"
recent preferences
cache state
session state
```

This provides a fast personalization response.

---

# 168. Example Feedback Cycle

User:

> "Show me something like Arrival."

System produces:

```text id="cjyq1m"
Arrival
similar candidate set
```

User:

> "I loved the second recommendation."

System:

```text id="lf8m6r"
record positive feedback
+
session preference update
+
future learning signal
```

Next request can immediately exploit the positive signal.

---

# 169. Memory vs Recommendation Learning

Explicit memory:

> "Remember I hate horror."

becomes persistent user preference.

Behavioral learning:

> user repeatedly skips horror

becomes inferred preference.

These should never be conflated.

---

# 170. Recommendation Context vs Memory

Session:

> "Tonight I don't want sad movies."

should remain contextual.

Memory:

> "I generally avoid depressing movies."

should persist.

The context builder should combine both correctly.

---

# 171. User Corrections

If the user says:

> "You keep recommending things I hate."

the application should allow correction.

The system should not blindly defend its model.

User feedback should be able to override inferred assumptions.

---

# 172. Transparency

Where appropriate, users should be able to see:

```text id="9imttb"
why this
```

but they should not need to understand:

```text latent dimensions
cosine similarity
ALS
```

The technical system can remain sophisticated underneath a simple interface.

---

# 173. Recommendation Privacy

Recommendations should never reveal information about other users.

Acceptable:

> "People with similar taste enjoyed this."

Not acceptable:

> "Suyash's friend Rahul rated this 5 stars."

unless explicit social sharing is introduced.

---

# 174. User-Specific Model Artifacts

Avoid storing a full independent model for every user in the initial system.

The primary model should be shared across users.

Per-user personalization should use:

```text id="xj2tub"
user state
taste profile
recent signals
embeddings where necessary
```

This keeps storage and inference manageable.

---

# 175. Model Memory Footprint

The initial CF model should be small enough to load into application memory.

Model size should be monitored.

If it becomes too large:

```text id="i9k6ht"
model serving architecture
```

can be revisited later.

---

# 176. No Giant LLM for Ranking

The LLM should not score thousands of candidate movies individually.

That is inefficient and unnecessary.

Use deterministic/statistical ranking for candidate scoring.

The LLM is used primarily for:

* intent interpretation
* tool orchestration
* explanation

---

# 177. LLM-Assisted Re-ranking

A future experimental path MAY use an LLM on a **very small final candidate set** for nuanced explanation or tie-breaking.

This is optional and should not become the default ranking mechanism.

---

# 178. Semantic Embeddings

Embedding generation should happen asynchronously or offline.

Do not generate embeddings for hundreds of movies during a user HTTP request.

---

# 179. Embedding Cache

Movie embeddings should be reusable.

If a movie embedding already exists for the active model version, do not regenerate it unnecessarily.

---

# 180. Embedding Versioning

Every embedding must identify:

```text id="a6od7o"
model_name
model_version
embedding_type
```

Incompatible vectors must not be silently mixed.

---

# 181. Recommendation Model Version

The following should remain distinguishable:

```text id="0z0z9f"
LLM model
embedding model
recommendation model
taste-profile version
```

They are separate versions.

---

# 182. Recommendation Reproducibility

Given:

```text id="jw7al8"
recommendation request
model version
profile version
context snapshot
candidate data
```

the system should be able to understand how the recommendation was produced.

Exact bit-for-bit reproducibility is not required for every future randomized component, but traceability is required.

---

# 183. Recommendation Debugging

An internal debug representation should be able to answer:

```text id="pny0wr"
Why was Movie X selected?
```

Potential answer:

```text id="l7f8cq"
CF score: 0.91
Context score: 0.83
Semantic score: 0.79
Runtime match: true
Explicit exclusions: none
Exploration boost: 0.05
Final score: ...
```

These details may remain internal.

---

# 184. Recommendation Trace

Each recommendation should carry a trace internally.

Conceptually:

```text id="atc5bh"
request
 ↓
context version
 ↓
candidate sources
 ↓
filters applied
 ↓
ranker
 ↓
diversity step
 ↓
final item
```

This is invaluable for debugging.

---

# 185. Recommendation Fail-Safe

If a ranking configuration becomes invalid:

* fail validation
* do not silently use arbitrary weights
* fall back to a known-good configuration/model

---

# 186. Configuration Safety

Recommendation weights and thresholds should be schema-validated.

Invalid configurations MUST NOT become active.

---

# 187. Model Rollback

The recommendation system must support returning to the previous active model.

Example:

```text id="v1"
v7 active
 ↓
v8 deployed
 ↓
quality issue
 ↓
rollback v7
```

Rollback should not require a code deployment when the architecture supports model selection independently.

---

# 188. Recommendation Health Metrics

Monitor:

```text id="xnfyxb"
recommendation success rate
fallback rate
latency
candidate count
filtered count
empty-result rate
cache hit rate
model error rate
```

---

# 189. Empty Recommendation Protection

The recommendation system should attempt to avoid:

```text
[]
```

for ordinary users.

Fallback strategies should be available.

An empty result may still be valid when the user specifies impossible constraints, but the system should explain that situation.

---

# 190. Impossible Request

Example:

> "Give me an English movie under 10 minutes with an IMAX release."

If no valid movie exists:

```text id="1vfy2w"
```

the system should not fabricate one.

Instead it should explain that no matching title was found and relax constraints only if the user permits.

---

# 191. Constraint Relaxation

A future enhancement may allow the engine to determine:

> "I couldn't satisfy every constraint."

Then it can present:

```text id="t8d2yq"
Closest match
```

while clearly indicating which constraint was relaxed.

The system must not silently violate explicit hard constraints.

---

# 192. Recommendation Request Context Snapshot

Every recommendation request should retain a compact representation of:

```text id="k97h8n"
session intent
profile version
memory version
surface
major constraints
exploration setting
```

This supports later explanation and debugging.

---

# 193. Recommendation Request ID

Every recommendation request has a stable identifier.

This connects:

```text id="1ne2fx"
request
→ items
→ impressions
→ feedback
→ outcomes
```

---

# 194. Model Attribution

Each model-produced request should record:

```text id="sv8wyf"
model_version
```

Fallback requests should indicate fallback status.

---

# 195. Recommendation API Independence

The public API should not change when:

```text id="9x9n3h"
ALS
```

becomes:

```text id="l7p8e4"
hybrid model
```

The API should continue to expose:

```text recommendations
```

rather than algorithm-specific details.

---

# 196. Recommendation Engine Evolution

Expected progression:

```text id="i6e4mg"
V1
Popularity baseline
        ↓
V2
Item-Item CF
        ↓
V3
Matrix Factorization
        ↓
V4
CF + contextual ranking
        ↓
V5
CF + semantic retrieval
        ↓
V6
Hybrid candidate generation
        ↓
V7
Learning-to-rank
```

This is a conceptual roadmap rather than a fixed release schedule.

---

# 197. MVP Model

The first production recommendation system should ideally be:

```text id="8fl5hr"
Popularity baseline
+
Item-item / matrix-factorization CF
+
explicit preference filtering
+
basic session constraints
```

This is sufficient to establish the core recommendation architecture.

---

# 198. V2 Hybrid Model

Next:

```text id="o23hf9"
CF
+
semantic retrieval
+
taste profile
+
contextual ranking
+
diversity
```

This is where the product begins to match the full orb vision.

---

# 199. V3 Advanced Model

Eventually:

```text id="f9m7wu"
multiple candidate generators
+
learning-to-rank
+
online experimentation
+
richer temporal preferences
+
real-time personalization
```

Only introduce this when enough data exists.

---

# 200. Recommendation System Non-Goals

The MVP recommendation engine does NOT need:

* deep neural recommendation models
* reinforcement learning
* real-time distributed training
* large-scale feature stores
* dedicated recommendation clusters
* graph databases
* neural LLM ranking of thousands of items
* complex online learning
* massive candidate catalogs

These can be evaluated later.

---

# 201. Performance Principle

Recommendation requests should be computationally bounded.

The system should not:

```text id="nfyvgj"
scan millions of movies
```

for every user request.

Instead:

```text id="dg7x66"
candidate retrieval
→ manageable candidate set
→ ranking
```

---

# 202. Precomputation Strategy

For stable surfaces:

```text id="4vdbzz"
precompute top candidates
```

For dynamic surfaces:

```text id="c1yq0w"
generate on demand
```

This lets the system balance quality and latency.

---

# 203. Cache Strategy by Surface

Conceptually:

| Surface                   | Cache suitability |
| ------------------------- | ----------------- |
| For You                   | High              |
| Trending for You          | High              |
| Movie Similar             | High              |
| Because You Liked         | Medium            |
| Tonight                   | Low/Medium        |
| Conversational refinement | Low               |

Actual behavior should be measured.

---

# 204. Recommendation Freshness

Recommendations should become stale when:

* user preferences change significantly
* model changes
* movie availability changes
* current session context changes

Cache invalidation should account for this.

---

# 205. Recommendation Quality vs Latency

The product should not make the user wait excessively for marginal ranking improvements.

A simple fast recommendation is preferable to a theoretically superior recommendation that creates poor UX.

Latency targets should be defined in deployment/observability documentation.

---

# 206. Multi-Stage Ranking

The architecture should eventually follow:

```text id="xy4cbf"
large candidate pool
        ↓
cheap scoring
        ↓
smaller candidate pool
        ↓
expensive ranking
        ↓
tiny final set
```

This is more scalable than using the most expensive algorithm on every movie.

---

# 207. Example Two-Stage System

```text id="2yqy44"
10,000 candidates
      ↓
CF retrieval
      ↓
500
      ↓
contextual ranker
      ↓
50
      ↓
diversity/exploration
      ↓
5
```

---

# 208. Candidate Retrieval Efficiency

Candidate retrieval should use efficient structures:

* latent factor indexes where relevant
* vector indexes where relevant
* database indexes for metadata filters
* precomputed popular/trending lists

The specific data structures belong to implementation.

---

# 209. Query Efficiency

Avoid per-movie database queries inside the ranking loop.

Preferred:

```text id="a4xfl0"
retrieve candidate IDs
 ↓
batch-load metadata
 ↓
rank in memory
```

---

# 210. Ranking Data Availability

The ranker should receive all required information in a preloaded candidate representation.

It should not perform arbitrary network requests.

---

# 211. External Provider Constraint

The recommendation engine must never depend on a live LLM/TMDB call for every candidate.

External requests should be bounded and preferably performed before ranking through controlled adapters.

---

# 212. Recommendation Data Contract

Each internal candidate should conceptually contain:

```json id="2vt9sa"
{
  "movie_id": "uuid",
  "sources": [],
  "signals": {},
  "metadata": {}
}
```

The final recommendation object adds:

```text id="y4izbt"
final_score
position
category
explanation_signals
```

---

# 213. Explainability Data vs User Output

Internal:

```text id="vmtldo"
cf_score = 0.83
semantic_score = 0.78
context_score = 0.91
```

User-facing:

> "You tend to like thoughtful sci-fi, and tonight you asked for something lighter."

The API should expose only the amount of scoring information the product actually needs.

---

# 214. Recommendation Security

Recommendation endpoints MUST ensure that:

* user context belongs to authenticated user
* recommendation history is private
* memory data is private
* candidate debug traces are not exposed publicly
* model artifacts are not downloadable by users

---

# 215. Recommendation Data Privacy

Training pipelines should avoid unnecessary use of raw conversational content.

Structured intent should generally be preferred for recommendation learning when possible.

---

# 216. Conversation Privacy

The recommendation engine does not need the user's entire chat transcript.

It should receive:

```text id="gof0eu"
structured current intent
+
relevant recent context
+
safe long-term preference summary
```

---

# 217. Training Data Privacy

Before using production user behavior for future training:

* respect user deletion requirements
* exclude data that should not participate in model training
* document which events are used
* retain only necessary attributes

---

# 218. User Deletion Impact

When a user is deleted, the system must consider:

```text id="y8g9x7"
ratings
interactions
memories
taste profiles
embeddings
recommendation history
training data
```

Derived artifacts may need regeneration or retraining depending on the model.

---

# 219. Model Retraining After Deletion

The system does not necessarily need immediate full retraining after every deletion.

Instead, model-training workflows should have a documented policy for:

* exclusion from future datasets
* model refresh
* affected derived artifacts

---

# 220. Dataset Drift

As CineRec accumulates its own data, the production interaction distribution may differ substantially from the bootstrap dataset.

The ML pipeline SHOULD monitor this.

Example:

```text id="x6z7zy"
MovieLens behavior
       ≠
CineRec behavior
```

Model performance should eventually be evaluated on CineRec's actual population.

---

# 221. Bootstrap-to-Production Transition

Initial phase:

```text id="55b7pd"
MovieLens-heavy
```

Later:

```text id="9q52ye"
production-user-heavy
```

Eventually:

```text id="46a8c5"
production interactions
+
carefully combined external data
```

The exact weighting should be experimentally determined.

---

# 222. Model Training Population

Training data may include users who are:

* active
* inactive
* new
* highly active

The pipeline should avoid accidental bias toward whichever group generates the most events unless that is intended.

---

# 223. Interaction Frequency Bias

Heavy users can generate many more events than light users.

The training pipeline should consider whether users with massive event counts are disproportionately influencing the model.

Potential strategies include:

* per-user normalization
* sampling
* event caps
* temporal weighting

These are model-specific decisions.

---

# 224. Popularity Bias

Popular movies naturally generate more interactions.

The system should monitor whether recommendations become excessively concentrated around a small group of movies.

Coverage and diversity metrics help detect this.

---

# 225. Long-Tail Discovery

Exploration mechanisms should create opportunities for less popular but relevant movies.

This is especially important for:

> Hidden Gems

and:

> Wildcards.

---

# 226. User Preference Stability

A single unusual interaction should not completely reshape long-term taste.

Preference aggregation should require sufficient evidence or use confidence-aware updates.

---

# 227. Confidence

Derived preference signals MAY include:

```text id="7yg3pr"
score
confidence
evidence_count
last_evidence_at
```

For example:

```text high score + one interaction
```

should not necessarily equal:

```text high-confidence preference
```

---

# 228. Recent Behavior

Recent interactions can be maintained as a lightweight context window.

For example:

```text id="63i8m7"
last 10–50 meaningful movie interactions
```

The exact window should be configurable.

---

# 229. Behavioral Context

Recent behavior can help answer:

> What has this user been into lately?

This can be distinct from long-term taste.

---

# 230. Recent Taste Drift

The system may detect:

```text id="4s9a5a"
historically:
action

recently:
drama + romance
```

and incorporate this shift without discarding the long-term profile.

---

# 231. Recommendation Surfaces and Memory

Different surfaces can use different time horizons.

```text id="5a33sa"
Tonight
→ recent/session-heavy

For You
→ long-term-heavy

Taste Evolution
→ historical
```

---

# 232. Contextual Bandit — Future

A future advanced system may formalize exploration/exploitation using contextual bandit techniques.

This is not required for MVP.

The architecture should, however, avoid making such future development impossible.

---

# 233. Reinforcement Learning — Not MVP

Do not implement reinforcement learning for recommendation in the initial project.

The data volume and operational complexity are not justified at this stage.

---

# 234. Graph Recommendation — Future

A graph-based recommender MAY eventually use:

```text id="sj26a7"
movie
actor
director
genre
theme
franchise
```

relationships.

The initial system should achieve these effects through relational and vector retrieval rather than requiring a graph database.

---

# 235. Recommendation Explainability Requirement

Every final recommendation SHOULD have enough structured metadata to answer:

> Why did this enter the final set?

At minimum, the system should know:

```text id="l6gk85"
candidate source
major ranking signals
applicable constraints
model version
```

---

# 236. Recommendation Auditability

An internal engineer should be able to inspect a recommendation request and determine:

1. what context existed
2. what candidate sources were used
3. which candidates were filtered
4. what ranker was used
5. what model version was active
6. why the final movie was selected

---

# 237. Recommendation Debug Mode

A protected administrative/debug mode MAY expose internal recommendation traces.

This MUST require administrative authorization.

Regular users must not receive raw model internals.

---

# 238. Logging Recommendation Decisions

Logs SHOULD record summary information such as:

```text id="56vkqv"
request_id
user_id
surface
model_version
candidate_count
filtered_count
final_count
latency
cache_hit
fallback
```

Do not log full personal profiles unnecessarily.

---

# 239. Recommendation Evaluation by Surface

The system should eventually evaluate:

```text id="4oywcx"
home recommendation quality
tonight recommendation quality
because-you-liked quality
wildcard quality
```

Separately where appropriate.

A model can perform well globally while failing at one particular surface.

---

# 240. Recommendation Evaluation by User Segment

Evaluate at least conceptually across:

```text id="y0k44d"
cold-start
sparse history
moderate history
rich history
```

This helps identify personalization weaknesses.

---

# 241. Recommendation Evaluation by Constraint Density

Highly constrained requests behave differently from unconstrained recommendations.

Potential segments:

```text id="o2kgxq"
few constraints
moderate constraints
highly constrained
```

A recommendation system should not optimize solely for generic recommendation requests.

---

# 242. Recommendation Quality for Wildcards

Wildcards should have their own evaluation criteria:

* novelty
* relevance
* downstream engagement
* discovery of new genres/themes

A wildcard does not need to maximize pure historical similarity.

---

# 243. Recommendation Quality for Safe Bets

Safe Bets emphasize:

* strong predicted relevance
* low unexpectedness
* consistency

Again, this is a different objective.

---

# 244. Recommendation Quality for Comfort Picks

Comfort Picks emphasize:

* context match
* emotional suitability
* low contradiction with explicit constraints

---

# 245. Recommendation Diversity Evaluation

Potential diversity measurements:

```text id="bgz10k"
intra-list diversity
genre coverage
creator diversity
language diversity
semantic diversity
```

The implementation may select an appropriate subset.

---

# 246. Recommendation Novelty Evaluation

Novelty can estimate:

> How unfamiliar was the recommendation relative to the user's history?

It should be measured separately from relevance.

---

# 247. Recommendation Coverage Evaluation

Coverage can measure:

> What fraction of eligible catalog items can ever receive meaningful recommendation exposure?

Coverage should not be optimized blindly; relevance remains primary.

---

# 248. Recommendation Calibration — Future

Future systems may estimate:

> How aligned is the distribution of recommended content with the user's actual preferences?

This can help prevent overconfidence in narrow recommendation patterns.

---

# 249. Diversity Guardrails

The system should prevent pathological recommendation sets.

Examples:

```text id="u0kl2o"
all same movie
all same creator
all already seen
all same genre
all ultra-popular
```

unless explicitly requested.

---

# 250. Recommendation Request Types

Internally classify requests as:

```text id="j6o0bj"
PERSONALIZED
CONTEXTUAL
SIMILAR
DISCOVERY
POPULARITY
FALLBACK
```

This helps analytics and model selection.

---

# 251. Personalized Request

Long-term taste is important.

Example:

> "What should I watch?"

---

# 252. Contextual Request

Current session context dominates.

Example:

> "I'm exhausted. Give me something comforting."

---

# 253. Similarity Request

A specific movie is the anchor.

Example:

> "Something like Arrival."

---

# 254. Discovery Request

Exploration matters.

Example:

> "Show me something I've probably never heard of."

---

# 255. Popularity Request

The user wants what is broadly popular.

Example:

> "What's good right now?"

Personalization may still apply if desired.

---

# 256. Fallback Request

Used when the primary model cannot produce valid recommendations.

---

# 257. Recommendation Model Selection

A future model-selection layer MAY choose different recommendation strategies depending on:

```text id="4f3h0f"
user history size
surface
current context
data availability
```

For example:

```text cold user
→ semantic + popularity

rich-history user
→ CF + semantic
```

---

# 258. Recommendation Engine Contract

The application should conceptually expose:

```python
id="4tjlfq"
recommend(
    context: RecommendationContext
) -> RecommendationResult
```

The engine should not require the caller to know:

```text ALS
SVD
BPR
embedding retrieval
```

---

# 259. Recommendation Result Contract

The internal result should conceptually contain:

```text id="c8n7qh"
request_id
items
model_version
fallback_state
explanation_metadata
```

Each item should contain:

```text id="f4tyx9"
movie_id
position
category
final_score
sources
explanation_signals
```

---

# 260. Final Recommendation Pipeline

The authoritative recommendation sequence is:

```text id="kx8y9k"
REQUEST
   ↓
CONTEXT BUILDER
   ↓
USER TASTE
   +
SESSION INTENT
   +
MEMORY
   +
BEHAVIOR
   +
CONSTRAINTS
   ↓
CANDIDATE GENERATION
   ├── CF
   ├── semantic
   ├── similarity
   ├── popularity
   └── exploration
   ↓
CANDIDATE UNION
   ↓
HARD FILTERING
   ↓
NORMALIZATION
   ↓
RANKING
   ↓
DIVERSITY
   ↓
EXPLORATION
   ↓
TOP-N
   ↓
EXPLANATION SIGNALS
   ↓
TMDB / INTERNAL METADATA ENRICHMENT
   ↓
API RESPONSE
   ↓
USER
   ↓
INTERACTION
   ↓
PERSONALIZATION UPDATE
```

---

# 261. Initial Implementation Order

Recommendation functionality should be implemented in this sequence:

```text id="jsb9u2"
1. Popularity baseline
2. Interaction weighting
3. Item-item CF
4. Matrix-factorization CF
5. Offline evaluation
6. RecommendationEngine abstraction
7. Context builder
8. Hard filtering
9. Basic contextual ranking
10. Recommendation explanations
11. Recommendation attribution
12. Redis caching
13. Semantic candidate generation
14. Hybrid ranking
15. Diversity
16. Exploration
17. Model versioning
18. Automated evaluation
19. Experimentation
20. Advanced ranking
```

---

# 262. MVP Recommendation Definition

The MVP recommendation system is considered complete when it can:

* train a collaborative-filtering model
* evaluate it against a baseline
* generate candidates for a user
* handle users with sparse/no history
* incorporate explicit user preferences
* incorporate current session constraints
* exclude inappropriate candidates
* rank the remaining candidates
* return a small recommendation set
* record recommendation attribution
* record subsequent user feedback
* support model versioning

---

# 263. Non-Negotiable Recommendation Principles

1. **Never let the LLM hallucinate movie recommendations into the final result.**
2. **Never treat absence of interaction as explicit dislike.**
3. **Never let soft preferences silently override hard constraints.**
4. **Never allow explicit user preferences to be ignored by weaker inferred preferences.**
5. **Never train the recommendation model synchronously during normal user requests.**
6. **Never expose another user's behavioral information.**
7. **Never make the API depend on a specific recommendation algorithm.**
8. **Never allow derived preference profiles to become the only source of truth.**
9. **Never return an invalid or nonexistent movie.**
10. **Never sacrifice all diversity for pure similarity.**
11. **Never introduce a complex ML technique without measurable justification.**
12. **Every recommendation model must be measurable, versioned, and rollbackable.**

---

# 264. Final Recommendation Philosophy

CineRec should not optimize for:

> **"What movie has the highest statistical score?"**

It should optimize for:

> **"What small set of movies gives this specific person the best chance of finding something they genuinely want to watch right now?"**

That requires recognizing that recommendation is a combination of:

```text id="vczb6q"
WHAT THIS PERSON USUALLY LIKES
+
WHAT THIS PERSON WANTS RIGHT NOW
+
WHAT THIS PERSON HAS ALREADY SEEN
+
WHAT THIS PERSON HAS EXPLICITLY REJECTED
+
WHAT THIS PERSON MIGHT ENJOY DISCOVERING
+
WHAT IS ACTUALLY AVAILABLE
```

Collaborative filtering provides the initial personalization backbone.

Context transforms that personalization into a useful **"tonight"** recommendation.

Semantic retrieval expands the system's ability to understand nuanced natural-language requests.

Ranking turns multiple signals into an ordered candidate set.

Diversity and exploration prevent the system from becoming repetitive.

Feedback makes the system progressively better.

The resulting recommendation loop is:

```text id="adq6ey"
              UNDERSTAND
                   ↓
                RETRIEVE
                   ↓
                 FILTER
                   ↓
                  RANK
                   ↓
               DIVERSIFY
                   ↓
              RECOMMEND
                   ↓
               OBSERVE
                   ↓
                LEARN
                   ↓
              RECOMMEND BETTER
```

This loop is the core intelligence of CineRec.

