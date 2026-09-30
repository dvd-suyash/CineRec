# CineRec — Functional Requirements

**Status:** Functional specification / source of truth
**Working title:** CineRec
**Version:** 1.0
**Depends on:** `01-product-vision.md`
**Audience:** Engineering agents, developers, QA, designers, product collaborators

---

# 1. Purpose

This document translates the CineRec product vision into concrete, testable functional requirements.

It defines:

* what users can do
* what the application must do
* how major features behave
* required states and edge cases
* system responsibilities
* MVP boundaries
* acceptance criteria

This document intentionally does **not** prescribe implementation details such as specific libraries, deployment infrastructure, database internals, or class structures. Those belong in the architecture and technical design documents.

Engineering agents must treat this document as the authoritative definition of product behavior.

---

# 2. Requirement Language

The following terminology is used throughout this document:

### MUST

Mandatory for the specified scope.

### SHOULD

Strongly preferred unless there is a documented technical or product reason otherwise.

### MAY

Optional/future capability.

### MUST NOT

Explicitly prohibited behavior.

---

# 3. Functional Scope

CineRec consists of the following functional areas:

1. Landing and authentication
2. User onboarding
3. Orb conversation
4. Cinematic intent extraction
5. Recommendation generation
6. Recommendation presentation
7. Conversational refinement
8. User interactions and feedback
9. Persistent memory
10. User movie library
11. Movie details
12. Search and discovery
13. Personalized dashboard
14. Taste visualization
15. Recommendation history
16. External movie-data integration
17. Availability information
18. Administration and operational visibility
19. Privacy and user controls
20. Error handling and recovery

---

# 4. User Roles

## 4.1 Unauthenticated User

Can:

* access landing page
* understand the product
* initiate Google authentication

Cannot:

* access personalized recommendations
* access personalized memory
* access private movie history
* submit authenticated interactions

---

## 4.2 Authenticated User

Can:

* use the orb
* receive recommendations
* rate movies
* like/dislike movies
* add/remove movies from watchlist
* record watched movies
* view recommendation history
* view movie details
* search movies
* view personalized dashboard
* view taste information
* manage memories
* manage personalization settings

---

## 4.3 Administrator

Administrative capabilities are not part of the primary consumer experience but the system SHOULD provide an authenticated administrative surface for:

* system health
* recommendation metrics
* model version visibility
* ingestion status
* application metrics
* error investigation

Administrative functionality must be permission-controlled.

---

# 5. Authentication Requirements

## FR-AUTH-001 — Landing page

The application MUST provide a public landing page.

The landing page MUST contain:

* CineRec branding
* concise product explanation
* primary Google sign-in action

The landing page SHOULD visually establish the orb/product identity.

---

## FR-AUTH-002 — Google OAuth

The application MUST support Google OAuth for authentication.

The user MUST NOT be required to create a CineRec-specific password for the MVP.

---

## FR-AUTH-003 — Authentication success

After successful authentication:

* an application user profile MUST exist
* the authenticated session MUST be established
* the user MUST be redirected into the authenticated CineRec experience

---

## FR-AUTH-004 — Returning user

A returning authenticated user SHOULD bypass first-time onboarding unless onboarding is incomplete.

The system MUST preserve the user's existing personalization state.

---

## FR-AUTH-005 — Authentication failure

Authentication failures MUST:

* be handled gracefully
* provide understandable feedback
* avoid exposing sensitive implementation details

The application MUST NOT leave the user in an ambiguous authentication state.

---

## FR-AUTH-006 — Logout

Authenticated users MUST be able to log out.

Logout MUST invalidate the application session according to the authentication architecture.

---

# 6. User Onboarding Requirements

## FR-ONBOARD-001 — First-time experience

A newly authenticated user MUST be identified as a new user.

The first experience SHOULD introduce the orb before exposing a complex dashboard.

---

## FR-ONBOARD-002 — Conversational onboarding

The user MUST be able to begin personalization through natural-language interaction with the orb.

---

## FR-ONBOARD-003 — Optional favorite movies

The system SHOULD optionally allow a new user to identify several movies they already like.

This can be done through:

* search
* selection
* rating
* conversational input

The purpose is to provide an initial personalization signal before sufficient behavioral data exists.

---

## FR-ONBOARD-004 — Skip onboarding

The user MUST be able to skip optional onboarding activities.

The system MUST still provide a usable experience to a user with zero prior movie interactions.

---

## FR-ONBOARD-005 — Cold-start behavior

A new user with insufficient history MUST NOT receive an empty recommendation experience solely because collaborative filtering lacks sufficient data.

The system MUST fall back to one or more alternative recommendation mechanisms.

---

# 7. Orb Requirements

## FR-ORB-001 — Orb visibility

The authenticated movie-discovery experience MUST prominently display the orb.

The orb is a primary interaction surface, not merely decorative UI.

---

## FR-ORB-002 — Orb states

The orb MUST support visually distinguishable states corresponding to application state.

At minimum:

* idle
* listening/input
* processing
* recommendation retrieval
* recommendation presentation
* refinement
* error

Additional states MAY include:

* searching
* synthesizing
* remembering

---

## FR-ORB-003 — Input

The user MUST be able to communicate with the orb through text input.

The architecture SHOULD permit future voice interaction without requiring voice for MVP.

---

## FR-ORB-004 — Natural language

The orb MUST accept unconstrained natural-language descriptions.

Examples:

* "I'm exhausted."
* "I want something funny."
* "I need something emotional but hopeful."
* "Give me something weird."
* "Something like Interstellar but simpler."

Users MUST NOT be required to provide structured fields.

---

## FR-ORB-005 — No unnecessary interrogation

The orb SHOULD avoid asking questions that do not materially improve recommendation quality.

---

## FR-ORB-006 — Follow-up questions

The orb MAY ask clarifying questions when important information is missing or ambiguous.

Follow-up questions SHOULD be concise and conversational.

---

## FR-ORB-007 — Conversation continuity

Within a recommendation session, the orb MUST preserve relevant conversational context.

For example:

User:

> "Something funny."

Orb:

> recommendation

User:

> "But less stupid."

The second request MUST be interpreted as a refinement of the current session rather than an unrelated request.

---

# 8. Cinematic Intent Requirements

## FR-INTENT-001 — Intent extraction

The system MUST transform natural-language user input into structured cinematic intent before recommendation generation.

---

## FR-INTENT-002 — Supported intent dimensions

The structured representation SHOULD support, where inferable:

* mood
* desired emotional effect
* energy
* emotional intensity
* complexity
* pacing
* genre preferences
* genre exclusions
* themes
* runtime constraints
* language
* release era
* viewing context
* exploration preference
* availability/provider requirements

Not every field must be populated for every conversation.

---

## FR-INTENT-003 — Unknown fields

The system MUST permit unknown or unspecified fields.

Absence of information MUST NOT automatically become an assumption.

For example:

If the user doesn't mention runtime, the system MUST NOT automatically assume a two-hour limit.

---

## FR-INTENT-004 — Explicit constraints

Explicit user constraints MUST have higher precedence than soft recommendation preferences.

Example:

> "Nothing over two hours."

This MUST function as a hard runtime constraint unless the user later changes it.

---

## FR-INTENT-005 — Negative intent

The system MUST support negative preferences.

Examples:

* no horror
* not depressing
* no subtitles tonight
* nothing longer than two hours

---

## FR-INTENT-006 — Context expiration

Session-level intent SHOULD expire or become inactive after the recommendation session ends unless explicitly persisted as a memory.

A temporary mood MUST NOT automatically become a permanent user preference.

---

# 9. Long-Term Personalization Requirements

## FR-PERS-001 — Long-term profile

The system MUST maintain a long-term representation of the user's movie preferences.

This may include:

* genre tendencies
* theme tendencies
* pacing preferences
* runtime preferences
* director/actor preferences
* language preferences
* inferred positive preferences
* inferred negative preferences

---

## FR-PERS-002 — Multiple evidence sources

Long-term personalization SHOULD incorporate multiple behavioral signals.

Examples:

* ratings
* likes
* dislikes
* watches
* completions
* watchlist actions
* repeated skips
* recommendation outcomes

A single event SHOULD NOT be sufficient to establish a strong permanent preference unless explicitly stated by the user.

---

## FR-PERS-003 — Explicit preference precedence

An explicit user preference MUST be capable of overriding a weaker inferred preference.

Example:

A model infers that the user likes horror.

The user explicitly says:

> "I hate horror."

The explicit preference MUST take precedence.

---

## FR-PERS-004 — Personalization evolution

User preference representations MUST be capable of changing over time.

The system MUST NOT permanently lock a user into an early preference profile.

---

# 10. Memory Requirements

## FR-MEM-001 — Explicit memory creation

The user MUST be able to intentionally create persistent preferences through language.

Example:

> "Remember that I hate horror."

The system SHOULD recognize this as a persistent-memory request.

---

## FR-MEM-002 — Explicit memory confirmation

When the user makes an explicit memory request, the system SHOULD acknowledge what it understood.

Example:

> "Got it. I'll avoid horror in your recommendations."

---

## FR-MEM-003 — Memory candidate extraction

The system MAY identify potentially useful preferences from normal conversation.

However, inferred memories MUST NOT automatically be treated as explicit user statements.

---

## FR-MEM-004 — Memory confidence

Inferred memory SHOULD carry an associated confidence or evidence strength.

---

## FR-MEM-005 — Memory distinction

The system MUST distinguish between:

* explicit preference
* inferred preference
* session context
* temporary rejection
* permanent rejection

---

## FR-MEM-006 — Memory inspection

Authenticated users SHOULD be able to inspect important remembered preferences.

---

## FR-MEM-007 — Memory deletion

Users MUST be able to delete persistent memories.

Deleted memories MUST no longer influence future recommendation generation after propagation through relevant systems.

---

## FR-MEM-008 — Memory correction

Users MUST be able to correct inaccurate remembered preferences.

---

## FR-MEM-009 — Memory reset

The system SHOULD provide a mechanism to reset the user's personalization profile.

Reset behavior MUST be clearly communicated before destructive operations occur.

---

# 11. Recommendation Requirements

## FR-REC-001 — Recommendation generation

Authenticated users MUST be able to request personalized movie recommendations.

---

## FR-REC-002 — Collaborative filtering

The initial personalization system MUST include collaborative filtering.

Collaborative filtering MUST operate as a recommendation signal rather than as the conversational interface.

---

## FR-REC-003 — Candidate generation

Recommendations SHOULD be generated through a candidate-generation stage before final ranking.

Potential candidate sources include:

* collaborative filtering
* item similarity
* semantic similarity
* popularity
* trending
* exploration

---

## FR-REC-004 — Candidate filtering

Candidates MUST be filtered according to relevant hard constraints.

Examples:

* already watched
* explicitly blocked
* runtime constraint
* language constraint
* unavailable provider when explicitly required
* known invalid/unavailable movie

---

## FR-REC-005 — Personalization

Final recommendations MUST consider the user's long-term taste where sufficient data exists.

---

## FR-REC-006 — Current context

Final recommendations MUST consider the user's current conversational context when such context exists.

---

## FR-REC-007 — Context precedence

Hard current-session constraints MUST override soft long-term preferences.

Example:

Long-term preference:

> frequently likes long movies

Current request:

> "I only have 90 minutes."

The recommendation system MUST respect the current runtime requirement.

---

## FR-REC-008 — Diversity

The recommendation set SHOULD contain meaningful diversity.

The system SHOULD avoid returning many effectively interchangeable movies unless the user explicitly requests narrow similarity.

---

## FR-REC-009 — Exploration

The recommendation engine SHOULD support controlled exploration outside established preferences.

Exploration MUST be intentional rather than random.

---

## FR-REC-010 — Small recommendation set

The default recommendation experience SHOULD present a small curated selection rather than a massive list.

The exact number MAY be tuned based on product experimentation.

---

# 12. Recommendation Categories

The system SHOULD conceptually support recommendation roles such as:

### Safe Bet

Strong alignment with established taste.

### Comfort Pick

Strong alignment with current session mood and desired emotional effect.

### Wild Card

Outside-normal-taste recommendation with meaningful contextual justification.

These categories SHOULD be treated as presentation concepts rather than immutable ranking rules.

---

# 13. Recommendation Explanation Requirements

## FR-EXP-001 — Explainability

Each recommendation SHOULD be explainable in user-understandable language.

---

## FR-EXP-002 — Grounded explanation

The explanation MUST be based on actual recommendation signals.

The LLM MUST NOT invent a justification unrelated to the recommendation engine's evidence.

---

## FR-EXP-003 — Explanation examples

Valid explanations may include:

> "You tend to enjoy slow-burn sci-fi, and tonight you asked for something lighter."

> "You liked Interstellar, and people with similar taste also enjoyed this."

> "This one is outside your usual taste, but it matches the mood you described."

---

## FR-EXP-004 — Technical transparency

The user SHOULD NOT need to understand concepts such as latent embeddings or collaborative-filtering matrices to understand an explanation.

---

# 14. Conversational Refinement Requirements

## FR-REFINE-001 — Recommendation refinement

Users MUST be able to refine recommendations conversationally.

Examples:

* "Too sad."
* "I've already seen that."
* "Something funnier."
* "Less complicated."
* "Give me something weirder."

---

## FR-REFINE-002 — Incremental intent updates

Refinement MUST modify the relevant session intent rather than restarting from zero.

---

## FR-REFINE-003 — Re-ranking

After meaningful refinement, the system SHOULD regenerate or re-rank recommendations.

---

## FR-REFINE-004 — Rejection semantics

The system MUST distinguish between:

* "I don't want this right now."
* "I never want to see this."
* "I've already watched this."

---

# 15. Movie Interaction Requirements

## FR-INT-001 — Movie click

Users MUST be able to open a movie from recommendation and discovery surfaces.

---

## FR-INT-002 — Rating

Users SHOULD be able to provide an explicit movie rating.

Rating updates MUST replace or update the user's current rating rather than create contradictory active ratings.

---

## FR-INT-003 — Like

Users SHOULD be able to explicitly like a movie.

---

## FR-INT-004 — Dislike

Users SHOULD be able to explicitly dislike a movie.

---

## FR-INT-005 — Watchlist

Users MUST be able to:

* add movie to watchlist
* remove movie from watchlist
* inspect watchlist

---

## FR-INT-006 — Watched state

Users SHOULD be able to mark a movie as watched.

---

## FR-INT-007 — Completion

The system SHOULD support a distinction between starting and completing a movie where the application has sufficient information to do so.

---

## FR-INT-008 — Temporary skip

Users SHOULD be able to communicate that a recommendation is unsuitable for the current session without permanently rejecting it.

---

## FR-INT-009 — Interaction recording

Relevant user interactions MUST be recorded as recommendation signals.

---

# 16. Recommendation Impression Requirements

## FR-IMP-001 — Recommendation impression

The system MUST be capable of recording when a recommendation is presented to the user.

---

## FR-IMP-002 — Recommendation request identity

A recommendation generation request MUST have a unique identifier.

---

## FR-IMP-003 — Model identity

Recommendations MUST be attributable to a specific recommendation-model version where a model is involved.

---

## FR-IMP-004 — Position

The system SHOULD record the position/order in which recommended items were presented.

---

## FR-IMP-005 — Context

Recommendation impressions SHOULD retain sufficient context to support later evaluation.

---

# 17. Movie Details Requirements

## FR-MOV-001 — Movie details page

Each supported movie MUST have a dedicated details experience.

---

## FR-MOV-002 — Core metadata

The movie experience SHOULD support:

* title
* poster
* backdrop
* overview
* release date/year
* runtime
* genres
* cast
* crew

---

## FR-MOV-003 — Personal state

The movie page SHOULD show the user's relationship to the movie where applicable:

* watched
* rating
* liked/disliked
* watchlist status

---

## FR-MOV-004 — Similar movies

The movie page SHOULD provide similar or related movies.

---

## FR-MOV-005 — Personal explanation

When the user arrived through a recommendation, the system SHOULD be able to surface why the movie was recommended.

---

## FR-MOV-006 — Availability

Where reliable data exists, the movie page SHOULD show relevant regional viewing availability.

Availability information MUST NOT be presented as guaranteed if the underlying source is stale or uncertain.

---

# 18. Search Requirements

## FR-SEARCH-001 — Movie search

Users MUST be able to search for movies by title or relevant metadata.

---

## FR-SEARCH-002 — Fuzzy matching

Search SHOULD tolerate common spelling mistakes and approximate matching.

---

## FR-SEARCH-003 — Natural-language discovery

The system SHOULD eventually support natural-language search/discovery such as:

> "sad but hopeful sci-fi under two hours"

---

## FR-SEARCH-004 — Personalized search

Where sufficient data exists, search results SHOULD be capable of being personalized.

---

## FR-SEARCH-005 — Search and orb relationship

Search and conversational discovery SHOULD share compatible movie and recommendation infrastructure.

---

# 19. My Cinema Requirements

## FR-LIB-001 — Personal movie library

Authenticated users MUST have a private movie-library area.

---

## FR-LIB-002 — Watched

Users MUST be able to view their watched movies.

---

## FR-LIB-003 — Watchlist

Users MUST be able to view their watchlist.

---

## FR-LIB-004 — Ratings

Users SHOULD be able to view movies they have rated.

---

## FR-LIB-005 — Recently discovered

The system SHOULD provide a view of movies recently encountered through CineRec.

---

## FR-LIB-006 — Personal recommendations

The dashboard SHOULD expose relevant personalized recommendation surfaces.

---

# 20. Taste Visualization Requirements

## FR-TASTE-001 — Taste profile

The authenticated experience SHOULD provide a visual summary of the user's cinematic tendencies once sufficient data exists.

---

## FR-TASTE-002 — Movie DNA

The product SHOULD provide a playful "Movie DNA" representation.

This representation MUST be framed as an interpretation of viewing behavior rather than objective psychological truth.

---

## FR-TASTE-003 — Taste evolution

The system SHOULD eventually display changes in viewing interests over time.

---

## FR-TASTE-004 — Cinematic eras

The system MAY identify playful viewing periods such as:

* "The Nolan Phase"
* "Comfort Movie Month"
* "Your Sci-Fi Spiral"

Such labels MUST be based on observable viewing behavior.

---

# 21. Recommendation History Requirements

## FR-HIST-001 — Recommendation history

The system SHOULD retain a usable history of prior recommendation sessions.

---

## FR-HIST-002 — Historical lookup

Users SHOULD be able to retrieve previously recommended movies.

Example:

> "What did you recommend yesterday?"

---

## FR-HIST-003 — Recommendation context

Where practical, historical recommendations SHOULD retain their originating context.

---

# 22. TMDB Integration Requirements

## FR-TMDB-001 — Primary external movie provider

TMDB MUST be the initial external source for movie metadata.

---

## FR-TMDB-002 — Internal movie model

The application MUST maintain an internal movie representation rather than exposing raw provider objects as the application's permanent domain model.

---

## FR-TMDB-003 — External identifiers

Movies SHOULD retain relevant external identifiers needed for provider mapping.

---

## FR-TMDB-004 — Provider failure

If TMDB is temporarily unavailable:

* cached/internal information SHOULD remain available where possible
* the application SHOULD degrade gracefully
* unrelated application functionality SHOULD continue operating

---

## FR-TMDB-005 — Provider rate limits

The application MUST respect external provider limits and SHOULD minimize unnecessary repeated requests.

---

## FR-TMDB-006 — Attribution and licensing

The application MUST follow TMDB's current attribution, API-use, and licensing requirements applicable to the deployment.

---

# 23. LLM Functional Requirements

## FR-LLM-001 — Conversational model

The application MUST use an LLM for the conversational orb experience.

The initial provider is Gemini.

---

## FR-LLM-002 — Structured intent

The LLM MUST be capable of producing structured cinematic intent that can be validated by application code.

---

## FR-LLM-003 — Tool interaction

The conversational layer SHOULD be able to request application capabilities such as:

* movie search
* movie lookup
* recommendation generation
* user preference retrieval
* memory operations

Application code MUST execute and authorize tool operations.

---

## FR-LLM-004 — No direct database authority

The LLM MUST NOT have unrestricted direct database access.

---

## FR-LLM-005 — No fabricated movie facts

The LLM MUST NOT be treated as an authoritative movie database.

Movie identifiers and factual metadata used by the application MUST originate from trusted application data.

---

## FR-LLM-006 — Validation

LLM-generated structured data MUST be validated before being used by downstream application logic.

---

## FR-LLM-007 — Provider abstraction

The application SHOULD expose the LLM through an internal abstraction so that the provider can be changed later without redesigning the product.

---

# 24. Memory and LLM Interaction

## FR-MEMAI-001

The application MUST distinguish between:

* a conversational statement
* a temporary session preference
* an explicit memory request
* an inferred preference

---

## FR-MEMAI-002

The LLM MUST NOT silently turn every conversational statement into permanent memory.

---

## FR-MEMAI-003

When a memory operation modifies persistent user state, the application layer MUST validate and authorize that operation.

---

# 25. Availability Requirements

## FR-AVAIL-001

Where provider availability data exists, the system SHOULD be able to constrain recommendations by streaming/provider availability.

---

## FR-AVAIL-002

Provider and region requirements SHOULD be treated as explicit constraints when stated by the user.

Example:

> "What can I watch on Netflix?"

---

## FR-AVAIL-003

The system SHOULD make the applicable region clear where availability is shown.

---

# 26. Group Recommendation Requirements — Future

These requirements are future scope and are not mandatory for MVP.

## FR-GROUP-001

Users MAY create a movie session involving multiple participants.

---

## FR-GROUP-002

Each participant MAY provide:

* preferences
* dislikes
* current mood
* runtime constraints
* language constraints
* genre constraints

---

## FR-GROUP-003

The system SHOULD optimize recommendations for group compatibility.

---

## FR-GROUP-004

Individual preferences MUST NOT become public to other participants unless the product explicitly requires and communicates that sharing.

---

# 27. Movie Night Requirements — Future

A future Movie Night experience MAY provide:

* primary pick
* backup
* wildcard
* runtime
* mood
* group compatibility
* availability

The feature SHOULD minimize decision-making effort.

---

# 28. Rabbit Hole Requirements — Future

## FR-RABBIT-001

Users SHOULD be able to explore relationships between movies and related cinematic entities.

Potential relationships:

* director
* actor
* writer
* genre
* theme
* franchise
* related movie

---

## FR-RABBIT-002

Rabbit-hole exploration SHOULD allow movement from one movie to another through meaningful relationships.

---

# 29. Discovery Requirements

## FR-DISC-001

The system SHOULD expose recommendations outside pure historical similarity.

---

## FR-DISC-002

Users SHOULD eventually be able to explicitly request:

* familiar
* adventurous
* surprise
* outside my comfort zone

---

## FR-DISC-003

Exploration recommendations SHOULD remain contextually relevant.

---

# 30. Dashboard Requirements

The authenticated dashboard SHOULD provide access to:

* current recommendations
* My Cinema
* watchlist
* watched movies
* ratings
* taste visualization
* recommendation history
* memory/personalization controls

The dashboard MUST NOT expose another user's personal data.

---

# 31. Privacy and User-Control Requirements

## FR-PRIV-001

Personalized movie history MUST be private to the authenticated user unless explicitly shared.

---

## FR-PRIV-002

Users MUST be able to manage important persistent memories.

---

## FR-PRIV-003

Users MUST be able to delete or reset personalization-related data according to supported product functionality.

---

## FR-PRIV-004

Emotional or mood-related conversation context MUST be treated as entertainment context, not as a medical or psychological diagnosis.

---

## FR-PRIV-005

The system MUST NOT infer or expose sensitive personal attributes merely from movie preferences.

---

# 32. Error Handling Requirements

Every major user operation MUST have meaningful:

* loading state
* success state
* empty state
* failure state

---

## FR-ERR-001 — LLM failure

If the LLM is unavailable, the system SHOULD provide a graceful fallback where possible.

For example:

* ordinary movie search
* non-conversational recommendations
* previously cached recommendations

---

## FR-ERR-002 — Recommendation failure

If personalized recommendations cannot be generated, the system SHOULD provide an alternative recommendation mode rather than an empty application state.

---

## FR-ERR-003 — TMDB failure

Movie metadata requests MUST fail gracefully.

The application SHOULD reuse cached/internal information where available.

---

## FR-ERR-004 — Network interruption

The frontend SHOULD provide recoverable states for temporary network failures.

---

## FR-ERR-005 — Invalid AI output

If LLM output fails validation:

* downstream recommendation logic MUST NOT consume the invalid object
* the application SHOULD retry or fall back appropriately
* the user SHOULD receive a graceful conversational response

---

# 33. Performance-Related Functional Requirements

These are product-level requirements; detailed performance architecture belongs elsewhere.

## FR-PERF-001

Normal application interactions SHOULD feel responsive.

---

## FR-PERF-002

Long-running tasks MUST NOT block ordinary user interactions unnecessarily.

---

## FR-PERF-003

Recommendation generation SHOULD use cached/precomputed information when possible.

---

## FR-PERF-004

External API calls SHOULD NOT occur unnecessarily for data already available through valid local state.

---

# 34. Accessibility Requirements

## FR-A11Y-001

Core functionality MUST remain usable without relying exclusively on animation.

---

## FR-A11Y-002

Interactive elements MUST be keyboard accessible.

---

## FR-A11Y-003

Important system states MUST have non-visual equivalents.

---

## FR-A11Y-004

The orb MUST remain understandable when reduced-motion accessibility settings are enabled.

---

# 35. Mobile Requirements

## FR-MOB-001

The core orb experience MUST function on mobile layouts.

---

## FR-MOB-002

Movie discovery, recommendation, and watchlist functionality MUST remain usable on smaller screens.

---

## FR-MOB-003

The orb MUST adapt its visual scale and interaction layout to mobile dimensions.

---

# 36. Data Integrity Requirements

## FR-DATA-001

A user MUST NOT be able to create or modify another user's private movie state.

---

## FR-DATA-002

A movie rating MUST have unambiguous ownership.

---

## FR-DATA-003

Watchlist state MUST remain consistent.

---

## FR-DATA-004

Persistent memory changes MUST be attributable to a specific user.

---

## FR-DATA-005

Recommendation impressions MUST be associated with the appropriate recommendation request where applicable.

---

# 37. Recommendation Quality Requirements

## FR-QUAL-001

The system SHOULD maintain measurable offline recommendation quality.

---

## FR-QUAL-002

The system SHOULD support evaluation of:

* Precision@K
* Recall@K
* NDCG@K
* MAP@K
* Hit Rate@K

---

## FR-QUAL-003

The system SHOULD additionally evaluate:

* diversity
* novelty
* catalog coverage

---

## FR-QUAL-004

Recommendation evaluation SHOULD distinguish between model quality and product engagement metrics.

---

# 38. Cold-Start Requirements

## FR-COLD-001 — New user

Users without interaction history MUST still receive a functional discovery experience.

---

## FR-COLD-002 — New movie

Movies with insufficient collaborative data SHOULD be eligible for recommendation through alternative signals such as metadata or semantic similarity.

---

## FR-COLD-003 — Progressive personalization

As a user's interactions accumulate, recommendation behavior SHOULD progressively become more personalized.

---

# 39. Safety / Trust Requirements for Recommendations

## FR-TRUST-001

The system MUST NOT fabricate nonexistent movies as recommendations.

---

## FR-TRUST-002

Every recommended movie MUST correspond to a valid movie record known by the application's movie-data layer.

---

## FR-TRUST-003

Recommendation explanations MUST NOT claim user behavior that did not occur.

---

## FR-TRUST-004

A recommendation MUST NOT be justified using information unavailable to the application unless clearly framed as general conversational reasoning rather than observed user behavior.

---

# 40. MVP Acceptance Criteria

The MVP is considered functionally complete when all of the following are demonstrably operational.

## Authentication

* landing page exists
* Google OAuth works
* authenticated sessions work
* logout works

## Orb

* orb is visible after authentication
* text conversation works
* conversational context persists during the session
* the system can identify cinematic intent
* the orb can ask concise follow-up questions

## Movie data

* TMDB movie search works
* movie details work
* posters/backdrops work
* core metadata works

## Personalization

* user can rate movies
* user can like/dislike movies
* user can maintain a watchlist
* user can mark movies watched
* interactions are persisted

## Recommendation

* collaborative filtering exists
* cold-start fallback exists
* current session intent affects results
* previously watched/disallowed movies can be filtered
* recommendations are presented in a curated form
* recommendation explanations are grounded in known signals

## Memory

* explicit preferences can be saved
* persistent memories are distinguishable from session context
* user can inspect important memories
* user can delete memories

## Dashboard

* watched movies visible
* watchlist visible
* ratings visible
* personalized information visible once sufficient data exists

## Reliability

* meaningful loading states exist
* meaningful empty states exist
* major external-service failures degrade gracefully
* invalid LLM output does not break the application

---

# 41. MVP Explicitly Excluded

The following are not required for MVP:

* voice conversation
* multi-user movie rooms
* social profiles
* public reviews
* friend systems
* real-time collaborative filtering
* full automated retraining pipeline
* advanced A/B testing
* dedicated distributed search infrastructure
* microservices
* Kubernetes
* dedicated vector database
* highly sophisticated neural recommendation models
* fully autonomous agent behavior

These may be added later if justified by product requirements.

---

# 42. User Stories

## Authentication

**US-001**

As a visitor, I want to sign in with Google so that I can begin using CineRec without creating another password.

**Acceptance criteria:**

* Google sign-in is available on landing page.
* Successful authentication creates/retrieves the user.
* User enters authenticated experience.

---

## Discovery

**US-002**

As a user, I want to tell CineRec how I feel in natural language so that I don't have to understand movie genres or recommendation filters.

**Acceptance criteria:**

* Free-form text is accepted.
* Intent is extracted.
* Recommendations can be generated from the intent.

---

## Refinement

**US-003**

As a user, I want to reject or refine a recommendation conversationally so that I don't have to restart the search.

**Acceptance criteria:**

* "Too sad" modifies current recommendation context.
* New recommendations reflect the refinement.

---

## Memory

**US-004**

As a user, I want CineRec to remember important preferences so that I don't have to repeat myself.

**Acceptance criteria:**

* Explicit memory requests are recognized.
* The preference persists.
* The preference influences future recommendations.
* The preference can be removed.

---

## Personalization

**US-005**

As a returning user, I want recommendations to reflect what I have historically enjoyed.

**Acceptance criteria:**

* Prior interactions influence recommendation output.
* Collaborative filtering is used when sufficient data exists.

---

## Exploration

**US-006**

As a user, I want recommendations outside my normal taste so that CineRec can help me discover new kinds of movies.

**Acceptance criteria:**

* An exploration mechanism exists.
* Exploration is not equivalent to random movie selection.
* Recommendations retain contextual relevance.

---

## Understanding

**US-007**

As a user, I want to know why a movie was recommended so that recommendations do not feel arbitrary.

**Acceptance criteria:**

* Recommendation explanations are available.
* Explanations reflect actual available recommendation signals.

---

## Personal Archive

**US-008**

As a user, I want a place to see my watched movies, watchlist, and ratings so that CineRec becomes my personal movie archive.

**Acceptance criteria:**

* Personal movie data is accessible.
* Data belongs only to the authenticated user.

---

# 43. Functional Priority

## P0 — Must Have

* Google OAuth
* authenticated user
* orb
* conversational text interaction
* cinematic intent extraction
* TMDB movie integration
* movie details
* movie search
* ratings
* watchlist
* watched state
* interaction tracking
* initial collaborative filtering
* cold-start fallback
* contextual filtering
* recommendations
* recommendation explanations
* basic persistent memory
* basic personal movie dashboard

---

## P1 — Should Have

* Movie DNA
* recommendation history
* taste visualization
* explicit memory-management UI
* semantic search
* richer discovery
* wildcard recommendations
* availability-aware recommendations
* recommendation diversity controls

---

## P2 — Future

* voice orb
* movie-night mode
* group recommendations
* rabbit holes
* cinematic journeys
* advanced experimentation
* deeper recommendation personalization
* real-time adaptation

---

# 44. Functional Invariants

The following behaviors MUST remain true even as the implementation evolves.

### Invariant 1

The LLM understands user intent; it is not the authoritative recommendation engine.

### Invariant 2

Collaborative filtering contributes behavioral personalization.

### Invariant 3

Current-session context can override soft long-term preferences.

### Invariant 4

Explicit user preferences can override inferred preferences.

### Invariant 5

Temporary session context does not automatically become permanent memory.

### Invariant 6

Recommendations must reference valid movie records.

### Invariant 7

Recommendation explanations must be grounded in available evidence.

### Invariant 8

Users can correct the personalization system.

### Invariant 9

Failure of one external AI/data provider should not destroy unrelated application functionality.

### Invariant 10

Product behavior should remain usable without advanced infrastructure.

---

# 45. Final Functional Model

At the highest level, CineRec MUST implement this loop:

```text
USER
  ↓
Natural-language input
  ↓
Cinematic intent
  ↓
Current session context
  +
Long-term taste
  +
Explicit preferences
  +
Behavioral history
  ↓
Candidate generation
  ↓
Collaborative filtering
  +
Semantic/contextual signals
  +
Discovery signals
  ↓
Hard filtering
  ↓
Ranking
  ↓
Small recommendation set
  ↓
Explanation
  ↓
User interaction
  ↓
New behavioral signal
  ↓
Updated personalization
```

The system should progressively become better at answering:

> **"You know what I like. What should I watch right now?"**

This interaction loop is the primary functional objective of CineRec.

