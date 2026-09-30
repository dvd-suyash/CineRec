# CineRec — Product Vision

**Status:** Product vision / source of truth
**Working title:** CineRec
**Version:** 1.0
**Audience:** Engineering agents, developers, designers, product collaborators
**Primary objective:** Build a deeply personalized, conversational movie-discovery product that combines collaborative filtering, contextual understanding, persistent taste memory, and rich movie metadata into a playful cinematic experience.

---

# 1. Product Summary

CineRec is a personalized movie discovery platform built around a conversational, visual AI companion represented as a glowing orb.

The user does not need to know the name of a movie, genre, director, actor, or even exactly what they want to watch.

They can simply express a feeling, situation, preference, constraint, or vague idea:

> "I've had a terrible day. Give me something comforting."

> "I want something that makes me think, but not something depressing."

> "I want a crazy movie tonight."

> "Something like Interstellar, but less complicated."

> "I have two hours and I'm watching with three friends who can never agree."

The orb interprets the user's natural-language intent, combines it with the user's long-term taste profile and previous interactions, retrieves and ranks suitable movies, and presents a small set of recommendations with understandable reasons.

The system becomes more useful over time because it remembers the user's cinematic preferences and learns from their behavior.

CineRec should feel less like a database of movies and more like:

> **A cinematic companion that gradually gets to know your taste.**

---

# 2. Core Product Thesis

Traditional movie recommendation systems largely assume that the user knows what they want and needs help finding it.

CineRec starts from the opposite assumption:

> People often know how they feel before they know what they want to watch.

A user may know:

* their mood
* their energy level
* whether they want comfort or novelty
* whether they want to laugh or think
* how much time they have
* whether they are watching alone or with others
* what they absolutely do not want

They may not know the exact movie.

CineRec translates:

**human intent → cinematic intent → candidate movies → personalized ranking → decision**

The product should reduce choice overload while making discovery feel playful and personal.

---

# 3. Product Promise

CineRec should consistently try to answer:

> **"Given who I am, what I feel like right now, and the movies available to me, what should I watch?"**

The answer should feel:

* personal
* useful
* contextual
* explainable
* concise
* fun
* trustworthy
* easy to refine

The system should not overwhelm the user with dozens of nearly identical choices.

The default experience should generally surface a small number of highly relevant options and allow the user to continue refining naturally.

---

# 4. Product Personality

CineRec should feel:

**Curious**
It is interested in understanding what the user means rather than immediately dumping recommendations.

**Perceptive**
It remembers patterns and recognizes context.

**Playful**
It can have character and wit without becoming annoying.

**Cinematic**
The product should feel like a movie experience rather than a generic SaaS dashboard.

**Calm**
The experience should reduce decision fatigue instead of creating more of it.

**Non-judgmental**
The user's taste should never be mocked or graded as objectively good or bad.

**Useful first**
Personality should enhance utility, never interfere with it.

---

# 5. What CineRec Is Not

CineRec is not:

* a generic chatbot with a movie prompt
* a static list of popular movies
* a simple movie search engine
* a movie database UI
* an LLM that invents movie recommendations from memory
* a simple "movies similar to X" interface
* a rating prediction demo disguised as a product
* a social network for movie reviews
* a psychological profiling application

The central product is **personalized cinematic discovery**.

---

# 6. Product Experience in One Sentence

A user logs in, meets a glowing orb, talks naturally about what they feel like watching, and receives a small set of personalized movie recommendations that become better as the system learns their taste.

---

# 7. Primary User Journey

## 7.1 Landing Page

The landing page should communicate the product concept immediately.

Primary experience:

* strong visual identity
* cinematic atmosphere
* central messaging
* Google OAuth entry point
* minimal friction
* no unnecessary registration form

The primary CTA is authentication through Google.

The landing page should create curiosity around the orb without requiring the user to understand the underlying ML architecture.

---

# 8. First Login Experience

After successful authentication, the user enters the main CineRec experience.

The orb becomes the visual focal point.

The initial experience should not feel like:

> "Welcome to your dashboard."

It should feel like entering a cinematic environment.

The orb may begin with a simple invitation such as:

> **What are we feeling tonight?**

or another equivalent phrase.

The exact copy can evolve, but the philosophy is fixed:

**The system invites conversation rather than presenting a form.**

---

# 9. The Orb

The orb is the signature product interface.

It should be visually distinctive and feel alive.

The orb represents the conversational recommendation layer.

It can have visual states such as:

1. **Idle**
2. **Listening**
3. **Processing**
4. **Searching**
5. **Synthesizing**
6. **Recommending**
7. **Waiting for reaction**
8. **Refining**
9. **Remembering**

The visual language should communicate state without requiring the user to read technical status messages.

Animations should feel organic rather than like loading spinners.

The orb should never become visually distracting from the actual movie recommendations.

---

# 10. Orb Interaction Philosophy

The orb should not behave like a rigid questionnaire.

Bad experience:

> What genre?

> What year?

> What runtime?

> What language?

> What actor?

> What rating?

Good experience:

> User: "I want something emotional."

> Orb: "Emotional in a cry-your-eyes-out way, or emotional in a warm-and-reflective way?"

The system should ask a follow-up only when it materially improves recommendation quality.

The user should be able to answer in natural language.

---

# 11. Conversational Intent

The orb should understand several dimensions of cinematic intent.

Possible dimensions include:

### Mood

Examples:

* happy
* sad
* calm
* energetic
* lonely
* nostalgic
* curious
* restless
* hopeful
* tense
* reflective
* playful

### Desired emotional effect

Examples:

* comfort
* laughter
* catharsis
* wonder
* suspense
* inspiration
* nostalgia
* excitement
* contemplation

### Energy

Examples:

* low
* medium
* high

### Complexity

Examples:

* easy
* moderate
* intellectually demanding

### Emotional intensity

Examples:

* light
* moderate
* intense

### Pacing

Examples:

* slow
* moderate
* fast

### Genre preferences

Positive or negative.

### Themes

Examples:

* friendship
* identity
* ambition
* loneliness
* family
* technology
* time
* love
* survival

### Runtime constraints

Examples:

* under 90 minutes
* under 2 hours
* 2–3 hours
* no constraint

### Language

Examples:

* English
* Hindi
* Korean
* Japanese
* any language

### Era

Examples:

* recent
* 2000s
* classic
* any

### Context

Examples:

* watching alone
* date night
* family night
* friends
* late-night viewing
* weekend
* after a difficult day

### Exploration preference

Examples:

* safe choice
* familiar
* slightly outside taste
* experimental
* completely unexpected

This data represents **cinematic intent**, not a permanent psychological assessment.

---

# 12. Current Session vs Long-Term Taste

The system must distinguish:

## Long-term taste

What the user tends to enjoy across time.

Examples:

* frequently likes science fiction
* frequently enjoys slow-burn stories
* tends to rate psychological dramas highly
* often enjoys Christopher Nolan movies
* frequently dislikes extremely long films

## Current session intent

What the user wants right now.

Example:

* normally loves thrillers
* tonight wants something comforting
* currently has only 90 minutes
* does not want anything emotionally heavy

The recommendation engine must combine these rather than treating one as a replacement for the other.

Conceptually:

**Long-term taste + current intent + constraints → recommendation**

---

# 13. Explicit Memory

Users should be able to intentionally teach CineRec something.

Examples:

> "Remember that I hate horror."

> "Remember that I usually don't want movies longer than two hours."

> "Remember that I love Villeneuve."

The system should distinguish explicit preferences from inferred preferences.

Explicit memories carry stronger confidence because the user directly stated them.

The product should eventually allow users to review, modify, and delete remembered preferences.

---

# 14. Inferred Memory

The system may gradually infer preferences from repeated behavior.

Examples:

* user repeatedly rates science fiction highly
* user repeatedly skips horror
* user consistently finishes slower dramas
* user frequently adds psychological films to their watchlist
* user often rejects movies over a certain runtime

Inferred preferences should carry confidence and evolve over time.

The system should not treat a single skipped movie as proof of a permanent dislike.

---

# 15. Memory Principles

Memory should be:

* useful
* bounded
* editable
* understandable
* confidence-aware
* privacy-conscious

The system should not indefinitely store every conversation in raw form merely because it can.

Persistent memory should emphasize useful preference representations.

The system should distinguish between:

**"I hate this."**

and:

**"Not tonight."**

It should also distinguish:

**"I haven't watched this."**

from:

**"I've watched it but don't want it again."**

---

# 16. Recommendation Engine

The recommendation system is the core intelligence behind the product.

The initial system should be based on collaborative filtering, but CineRec should not remain a pure collaborative-filtering system forever.

The long-term recommendation architecture should support multiple candidate sources:

* collaborative filtering
* item similarity
* semantic similarity
* popularity
* trending content
* discovery/exploration
* contextual matching
* availability constraints

These candidates can be merged, filtered, and ranked.

---

# 17. Collaborative Filtering's Role

Collaborative filtering answers the question:

> **"Based on how this user behaves and how other users behave, which movies are likely to interest them?"**

It learns relationships from collective user behavior.

Examples:

* users with similar rating patterns
* movies commonly liked by similar users
* movies frequently enjoyed together
* latent preference patterns

Collaborative filtering should provide the **personalization backbone**.

It should not be responsible for understanding natural-language mood.

---

# 18. Contextual Recommendation

The current conversation should modify the recommendation result.

Example:

Long-term taste:

* science fiction
* psychological
* slow-burn
* complex stories

Current session:

* exhausted
* wants comfort
* low energy
* under 2 hours
* does not want anything depressing

The recommendation engine should recognize that:

> the user's general taste does not necessarily equal what they want tonight.

Therefore, the system should dynamically balance:

* long-term relevance
* current mood/context
* explicit constraints
* novelty
* diversity
* movie quality/metadata signals
* availability

---

# 19. Recommendation Sources

Every recommendation should be traceable internally to one or more sources.

Possible sources:

* collaborative filtering
* similar movie
* semantic matching
* popularity
* trending
* exploratory recommendation
* contextual match

The user does not need to see technical labels, but the system should know why an item entered the candidate pool.

---

# 20. Recommendation Explanations

Every recommendation should have the potential for a meaningful explanation.

Examples:

> "You tend to like cerebral sci-fi, but tonight you asked for something lighter."

> "You liked Interstellar, and people with similar taste also enjoyed this."

> "This is outside your usual taste, but it matches the mood you described."

> "You asked for something under two hours, so I filtered out longer options."

Explanations must reflect actual recommendation logic.

The LLM should not invent reasons that the recommendation engine did not use.

---

# 21. The Recommendation Reveal

The act of receiving recommendations should feel like part of the product experience.

Rather than immediately displaying 20 cards, the orb should be capable of "revealing" a curated selection.

Example:

> "I found three directions."

Then:

### The Safe Bet

A movie closely aligned with known taste.

### The Wild Card

A more adventurous choice.

### The Comfort Pick

A choice strongly aligned with the current mood.

The labels are product language, not hard-coded ranking categories.

---

# 22. Conversational Refinement

Recommendations should not be the end of the conversation.

The user can immediately say:

> "Too sad."

> "I've seen it."

> "Something less complicated."

> "Make it funnier."

> "No foreign-language movies tonight."

> "Give me something weirder."

The system should update the session intent and produce a new ranking without restarting the entire experience.

This creates an iterative loop:

**initial intent → recommendations → feedback → updated intent → new recommendations**

---

# 23. User Reaction Model

The product should distinguish between different forms of feedback.

Possible interactions:

* impression
* view
* click
* watch
* complete
* rate
* like
* dislike
* add to watchlist
* remove from watchlist
* skip
* temporary rejection
* permanent rejection

Not all interactions represent the same preference strength.

For example:

**"Not tonight"** should not automatically become:

**"Never recommend."**

---

# 24. Movie Dashboard / My Cinema

The authenticated product should contain a personal movie space.

This should not feel like a generic CRUD dashboard.

Possible sections:

### Watched

Movies the user has watched.

### Ratings

Movies they explicitly rated.

### Watchlist

Movies they intend to watch.

### Recently discovered

Movies they encountered through CineRec.

### Favorite movies

An explicit or inferred collection.

### Personal recommendations

Persistent recommendation surfaces.

---

# 25. Movie DNA

A playful summary of the user's cinematic taste.

Example:

**Your Movie DNA**

* cerebral
* atmospheric
* emotional
* slow-burn
* science fiction
* existential
* character-driven
* dark humor

The system can express relative tendencies visually.

This should be presented as a **playful interpretation of viewing behavior**, not as objective scientific personality profiling.

---

# 26. Taste Evolution

CineRec should eventually show how the user's viewing interests have changed over time.

Example:

**January**

Comedy
Action
Mainstream releases

↓

**June**

Drama
Sci-Fi
Psychological

↓

**September**

International cinema
Slow-burn
Existential themes

This feature converts raw viewing history into an understandable narrative.

---

# 27. Cinematic Eras

The system may optionally identify informal periods in the user's viewing behavior.

Examples:

> "The Nolan Phase"

> "Comfort Movie Month"

> "Your Sci-Fi Spiral"

> "The International Cinema Era"

These labels should be generated from observable behavior and should feel playful rather than authoritative.

---

# 28. Discovery / Exploration

CineRec should not optimize exclusively for familiar preferences.

A good recommendation system should allow discovery.

Introduce an exploration concept:

**Known → Adjacent → Unfamiliar**

For example:

A user likes psychological science fiction.

The system may progressively expose:

* related sci-fi
* philosophical dramas
* international psychological films
* unusual genres sharing the same emotional/thematic characteristics

This should allow users to discover new interests rather than trapping them in a narrow recommendation bubble.

---

# 29. Wild Card Recommendations

A dedicated exploration surface can intentionally recommend something outside the user's normal patterns.

The system should know:

* why the item is unusual for this user
* what property makes it potentially relevant
* how far outside the normal taste it is

The purpose is discovery, not randomness.

---

# 30. Rabbit Holes

CineRec should eventually support cinematic exploration through interconnected movie knowledge.

For example:

**Movie → Director → Actor → Theme → Similar Movie → Another Movie**

A user could select:

> **Go down the rabbit hole**

and explore related movies and cinematic connections.

The purpose is to turn movie discovery into exploration rather than only ranking.

---

# 31. Movie Knowledge Layer

The product should maintain rich movie knowledge through TMDB.

Relevant information may include:

* movie title
* release date
* overview
* genres
* runtime
* cast
* crew
* images
* popularity
* ratings metadata
* keywords
* external identifiers
* regional availability information where provided

TMDB is the primary external movie metadata provider for the initial product.

The product should be designed around TMDB's API usage, attribution, rate limits, and licensing requirements.

The application should not assume permanent ownership of external provider data.

---

# 32. Movie Data Strategy

CineRec should not attempt to mirror an entire external movie catalog.

Movie information should be acquired as needed and persisted selectively where beneficial.

The product should maintain an internal canonical movie representation linked to external provider identifiers.

The system should not make the frontend directly dependent on raw TMDB responses.

This allows CineRec to:

* cache useful information
* control its own data model
* change providers later if necessary
* enrich movies with internal recommendation information
* reduce unnecessary external requests

---

# 33. Search

Search should eventually accept both precise and natural-language queries.

Examples:

> "Interstellar"

> "Nolan"

> "movies under 2 hours"

> "sad but hopeful sci-fi"

> "movies like Her"

> "funny movies for a group"

Search should eventually support:

* keyword matching
* fuzzy matching
* semantic similarity
* metadata filters
* personalized ranking

Search and conversational discovery should feel like complementary interfaces rather than completely separate products.

---

# 34. Where Can I Watch It?

A movie recommendation is significantly more useful when the user can act on it.

Movie pages should eventually surface availability information where reliable regional provider information is available.

The user's region should be treated as a contextual constraint for availability.

The product should avoid presenting stale or unsupported availability as guaranteed fact.

---

# 35. Group Movie Mode

A future product feature should allow multiple people to participate in a movie decision.

Example:

**Movie Night**

Participants:

* User A
* User B
* User C

Each participant can specify:

* must-have preferences
* dislikes
* mood
* runtime constraints
* language
* genre restrictions

CineRec then searches for the intersection.

The system should prioritize compatibility rather than simply averaging everybody's taste.

---

# 36. Movie Night Mode

A solo or group "movie night" workflow can combine:

* runtime
* current mood
* availability
* group compatibility
* familiar vs exploratory preference

Possible output:

**Tonight's Pick**

**Backup**

**Wildcard**

**Why these**

**Where to watch**

This should feel like a decision assistant rather than a search result.

---

# 37. The "Not Tonight" Concept

This is a first-class product concept.

The user can reject a movie temporarily.

Example:

> "Looks good, but not tonight."

The system should preserve the distinction between:

* not interested
* already watched
* temporarily unsuitable
* explicitly disliked
* unavailable

A temporarily rejected movie may become appropriate in a future context.

---

# 38. Memory as a Product Feature

Memory should be visible enough that the user understands that CineRec learns, but not so intrusive that it feels creepy.

Possible UI:

> "I remember you usually like..."

or:

> "You told me you don't want horror."

Users should be able to inspect important memories.

Possible controls:

* edit
* delete
* disable a preference
* clear memory
* clear viewing history
* reset taste profile

---

# 39. Trust and Accuracy

CineRec must not fabricate movie information.

The product should distinguish:

### Known facts

Obtained from trusted movie metadata.

### Inferred preference

Derived from user behavior.

### Recommendation reasoning

Produced from actual ranking signals.

### Conversational interpretation

Generated by the LLM from user input.

The LLM must not be treated as the authoritative source for movie facts.

---

# 40. AI Philosophy

The LLM is an **interpreter and conversational layer**, not the recommendation database.

Its primary responsibilities are:

* understand user language
* identify intent
* ask useful follow-up questions
* transform natural language into structured cinematic context
* invoke permitted application capabilities
* help communicate recommendation reasoning
* help manage memory candidates

The LLM should not:

* directly access the database
* invent movie IDs
* invent metadata
* bypass authorization
* decide persistent preferences without application validation
* replace the recommendation engine
* become the sole source of recommendation quality

---

# 41. Recommendation Philosophy

Recommendations should be produced by a dedicated recommendation system.

The LLM can help interpret and explain.

The recommendation engine determines what candidates are actually eligible and how they should be ranked.

This separation should remain fundamental.

---

# 42. LLM Provider Strategy

The initial LLM provider is Gemini.

However, the product should conceptually depend on an internal LLM abstraction rather than a provider-specific implementation.

This preserves the ability to change providers later without redesigning the product.

The product itself should remain provider-agnostic.

---

# 43. Personalization Loop

CineRec should continuously improve through feedback.

Conceptually:

**User input**

↓

**Intent**

↓

**Candidate generation**

↓

**Recommendation**

↓

**User interaction**

↓

**Preference update**

↓

**Future recommendations**

This creates a feedback loop.

The product should treat recommendations as an evolving process rather than a static prediction.

---

# 44. User Profile Model

The user's profile should eventually reflect several layers.

### Identity

Authentication and basic profile data.

### Explicit preferences

Directly stated preferences.

### Behavioral preferences

Patterns learned from interactions.

### Session preferences

Current cinematic context.

### Viewing history

Movies consumed.

### Recommendation history

Movies previously surfaced.

### Interaction history

Clicks, views, likes, dislikes, watchlist actions, etc.

These should remain conceptually distinct.

---

# 45. Recommendation History

The system should remember what it recommended.

This enables questions such as:

> "What were those three movies you suggested yesterday?"

or:

> "You recommended something about space last week."

Recommendation history also enables future evaluation of recommendation quality.

---

# 46. "Why This Movie?"

Every recommendation surface should have a way to answer:

> **Why am I seeing this?**

The answer should be understandable without ML jargon.

Possible forms:

> "You liked Arrival."

> "You tend to enjoy slow-burn science fiction."

> "This matches the low-energy mood you described."

> "This is your wildcard: it is outside your usual taste but shares themes you like."

---

# 47. Personalized Recommendation Surfaces

The product should eventually support multiple recommendation contexts.

### For You

General personalized recommendations.

### Because You Liked...

Movie-specific recommendations.

### Tonight

Current session context.

### Wildcards

Outside-normal-taste exploration.

### Hidden Gems

Potentially lesser-known recommendations.

### Trending for You

Trending items filtered through personal taste.

### Continue Exploring

Items from current discovery sessions.

---

# 48. Choice Architecture

CineRec should generally minimize decision fatigue.

Instead of showing 50 recommendations, it should frequently present a meaningful set.

A useful default pattern is:

* one highly confident recommendation
* one alternative
* one wildcard

The exact number can evolve through experimentation.

The product should optimize for successful decisions, not raw number of recommendations displayed.

---

# 49. Success Definition

A recommendation is not successful merely because the user clicked it.

Possible positive outcomes include:

* user saves it
* user chooses to watch it
* user completes it
* user gives a high rating
* user returns for further recommendations
* user discovers a movie they genuinely enjoy

The system should avoid reducing recommendation quality to one simplistic metric.

---

# 50. Product Success Metrics

The product should eventually measure:

### Activation

Percentage of new users who complete initial discovery and receive recommendations.

### Recommendation engagement

Clicks, saves, watchlist additions, watches, completions.

### Recommendation quality

Offline recommendation metrics such as:

* Precision@K
* Recall@K
* NDCG@K
* MAP@K
* Hit Rate@K

### Product quality

* recommendation refinement rate
* successful-session rate
* repeat usage
* discovery of new genres
* diversity
* catalog coverage

### Performance

* orb response latency
* recommendation latency
* API latency
* cache hit rate
* error rate

---

# 51. MVP Definition

The first product release should focus on the core loop.

## Authentication

* Google OAuth
* authenticated sessions
* user profile

## Orb

* visual orb
* text-based conversation
* natural-language movie intent
* concise follow-up questions
* recommendation reveal

## Movie system

* TMDB integration
* movie search
* movie details
* posters/backdrops
* genres
* cast/crew
* runtime and other useful metadata

## Personalization

* movie ratings
* likes/dislikes
* watchlist
* watched interactions
* basic persistent preferences

## Recommendation

* initial collaborative filtering
* popularity fallback
* basic contextual filtering
* recommendation explanations

## Personal cinema dashboard

* watched
* watchlist
* ratings
* basic taste visualization

## Quality

* reliable loading/error states
* responsive experience
* basic analytics
* tests
* privacy-conscious memory

The MVP should be polished rather than enormous.

---

# 52. MVP Non-Goals

The first release should not require:

* microservices
* Kubernetes
* distributed model serving
* real-time collaborative filtering updates
* complex social features
* sophisticated group recommendations
* advanced A/B experimentation
* a dedicated search cluster
* a separate vector database
* a custom-trained large language model
* a fully autonomous agent architecture
* a complete replica of an external movie database

These may become future capabilities if justified.

---

# 53. Cold Start

A new user has no historical behavior, so collaborative filtering alone cannot personalize effectively.

The product should address this through:

* conversational onboarding
* optional selection of favorite movies
* initial ratings
* popular/high-quality movie candidates
* contextual recommendations from the orb
* semantic/content-based signals where available

As users interact more, collaborative filtering should become increasingly important.

---

# 54. New Movie Cold Start

A newly introduced movie may have little or no interaction data.

The system should be capable of using:

* metadata
* genres
* themes
* keywords
* cast/crew
* semantic representations
* popularity signals

until sufficient collaborative data exists.

---

# 55. Exploration vs Exploitation

The recommendation system should balance:

### Exploitation

Recommend movies strongly aligned with known preferences.

### Exploration

Introduce movies that may expand the user's taste.

CineRec should support both.

A good system should sometimes say:

> "I know you'll probably like this."

and sometimes:

> "This is unusual for you, but I think it is worth trying."

---

# 56. Personalization Should Not Become a Filter Bubble

The product should not continuously recommend the same narrow genre because the user has historically watched it.

Diversity and discovery should be deliberate design principles.

Possible controls:

* more familiar
* more adventurous
* surprise me
* stay within my taste
* get me out of my comfort zone

---

# 57. Privacy Principles

CineRec will process personal preference and behavioral information.

The product should therefore follow:

* data minimization
* least-privilege access
* secure authentication
* user-controlled memory
* clear deletion paths
* no unnecessary retention
* careful handling of LLM inputs
* no exposure of private user data to unauthorized users

The system should avoid treating emotional language as a medical or psychological profile.

Mood is a **current entertainment context**.

---

# 58. User Control

Users should be able to:

* inspect important remembered preferences
* delete memories
* clear recommendation history
* clear viewing history where supported
* remove ratings
* remove watchlist items
* explicitly block genres or movies
* reset personalization

The user remains in control of their cinematic profile.

---

# 59. Accessibility

The orb should not depend entirely on animation or color.

Important states must also be communicated through:

* text
* semantic labels
* accessible focus states
* keyboard interaction
* sufficient contrast
* reduced-motion support

Core movie discovery must remain usable without animations.

---

# 60. Mobile and Responsive Experience

The primary experience should work on desktop and mobile.

The orb should scale and reposition intelligently.

Movie cards should remain visually rich without consuming excessive screen space.

The conversational flow should be usable through:

* keyboard input
* touch
* potentially voice input in a future phase

---

# 61. Voice as a Future Direction

The orb could eventually support voice conversation.

Example:

> "I don't know, just give me something tonight."

The architecture should leave room for voice input/output but should not make voice a dependency for MVP.

Text interaction must remain fully functional.

---

# 62. Social Features as Future Scope

Possible later capabilities:

* share a recommendation
* send a movie to a friend
* group movie rooms
* collaborative watchlists
* shared movie nights
* friend taste comparisons

These should not dominate the initial product.

CineRec is primarily a personal discovery product.

---

# 63. Future "Cinematic Companion" Features

Potential advanced experiences include:

### Mood memory

> "Last time you wanted this kind of comfort, you enjoyed..."

### Taste evolution

> "Your taste has been moving toward international dramas."

### Movie rituals

The system can recognize recurring viewing patterns.

### Discovery chains

> "Start here → then watch this → then this."

### Director journeys

> "You've liked three Villeneuve movies. Want to explore his filmography?"

### Actor rabbit holes

> "You liked this performance. Here's where to go next."

### Theme journeys

> "You seem interested in stories about identity. Here's a five-film journey."

---

# 64. Long-Term Product Vision

The long-term vision is not merely a better recommendation list.

It is:

> **A personal cinematic intelligence layer.**

The user should eventually be able to ask:

> "What should I watch?"

but also:

> "What kind of movies have I been gravitating toward?"

> "What should I explore next?"

> "What was that movie you recommended to me months ago?"

> "Give me something completely outside my comfort zone."

> "Plan a movie night for four people."

> "I want a movie like the feeling I had after watching Arrival."

The system should understand both:

**the movie universe**

and:

**the user's relationship with that universe.**

---

# 65. Product Architecture Principles

The following product principles are mandatory.

### Principle 1 — The orb is the experience, not decoration.

Its interaction should materially improve movie discovery.

### Principle 2 — Personalization must be grounded in behavior.

Recommendations should not be generated solely from an LLM's general knowledge.

### Principle 3 — Context matters.

What the user wants tonight can differ from what they generally like.

### Principle 4 — Memory should improve usefulness.

Do not store information merely because it can be stored.

### Principle 5 — Recommendations must be explainable.

The system should be capable of answering "why?"

### Principle 6 — Discovery matters.

The system should not trap users in their existing preferences.

### Principle 7 — External data should be treated as external.

TMDB is an upstream provider, not the application's entire internal model.

### Principle 8 — User control matters.

Users should be able to correct the system.

### Principle 9 — Minimize choice overload.

Prefer meaningful recommendations over massive lists.

### Principle 10 — Complexity must be earned.

Do not add infrastructure or technical complexity without a product or scaling reason.

---

# 66. Core Product Loop

The core CineRec loop is:

```text
USER
  ↓
Expresses mood / desire / constraints
  ↓
ORB
  ↓
Understands cinematic intent
  ↓
Combines with persistent taste
  ↓
Generates candidates
  ↓
Collaborative filtering + contextual/semantic signals
  ↓
Filters and ranks
  ↓
Presents a small recommendation set
  ↓
User reacts
  ↓
System learns
  ↓
Future recommendations improve
```

This loop is the heart of the product.

Every major feature should strengthen this loop rather than distract from it.

---

# 67. Example End-to-End Session

### User enters

> "I need something tonight."

Orb:

> "What's the vibe?"

User:

> "I'm exhausted. Something warm, funny, maybe a little emotional. Nothing too heavy."

System extracts:

* low energy
* comfort
* humor
* moderate emotion
* avoid heavy/depressing
* current session

The system consults:

* user's long-term preferences
* viewing history
* ratings
* current watchlist
* recommendation history
* eligible TMDB metadata
* collaborative filtering candidates
* contextual filters

The system produces:

### Comfort Pick

A movie strongly aligned with the user's current mood and established taste.

### Safe Bet

A movie the user's historical behavior strongly supports.

### Wild Card

A slightly less obvious movie that matches the emotional/contextual request.

Orb explains each briefly.

User:

> "The wild card looks good."

The user opens the movie.

Later:

> watched

Then:

> rated 5/5

The interaction is recorded.

The system now has another useful signal.

Future recommendations may become more accurate.

---

# 68. Example of Long-Term Memory

Months later:

User:

> "Give me something for another terrible day."

CineRec remembers that the user historically responds well to:

* hopeful emotional stories
* moderate humor
* lower emotional intensity
* movies around two hours
* certain genres/directors

The system also remembers that the user's previous "bad day" session resulted in a highly rated film.

The new recommendation can use that context without requiring the user to repeat themselves.

That is what should make the product feel personal.

---

# 69. Example of Correction

Suppose CineRec believes the user likes horror because of a single rating.

User says:

> "Actually, I don't like horror. That rating was a joke."

The explicit correction should override the weaker inference.

The product should make room for human correction.

The user must always be able to tell the system:

> **"You misunderstood me."**

---

# 70. Product Quality Bar

CineRec should not ship merely because:

* the frontend renders
* the API works
* Gemini returns text
* recommendations technically appear

The experience should be considered successful only when:

1. Authentication is smooth.
2. The orb feels intentionally designed.
3. Conversation feels natural rather than form-like.
4. Recommendations are actually grounded in available movie data.
5. Long-term taste affects recommendations.
6. Current context affects recommendations.
7. Feedback changes subsequent recommendations.
8. Memory is useful and controllable.
9. Movie metadata is reliable.
10. The product remains responsive.
11. Errors are handled gracefully.
12. The architecture allows the recommendation system to evolve.

---

# 71. Technical Requirements Implied by the Product

Although architecture belongs in separate documents, the product vision establishes these requirements:

* Google OAuth is the primary authentication experience.
* TMDB is the initial movie metadata source.
* Gemini is the initial conversational LLM.
* Collaborative filtering is the initial personalization algorithm.
* Persistent user memory is required.
* User interactions must be captured as meaningful signals.
* Recommendations need identifiable request/context information.
* The system must distinguish long-term preferences from session context.
* The recommendation system must be replaceable/evolvable.
* The application must remain capable of operating within a low/zero-budget infrastructure strategy.
* The browser must never receive server-side secrets.
* The user must be able to correct or remove important personalization information.

---

# 72. Definition of a Great CineRec Experience

A user should be able to enter the app knowing only:

> "I want to watch something."

Within a few conversational turns, CineRec should understand what they mean well enough to make several recommendations that feel personally relevant.

The user should be able to say:

> "No."

and the system should understand what "no" means in context.

The user should be able to say:

> "More like this."

and the system should refine intelligently.

The user should eventually feel:

> **"It actually knows what I like."**

That is the ultimate product success criterion.

---

# 73. North Star

The North Star of CineRec is:

> **Turn the vague question "What should I watch?" into an effortless, personalized, and enjoyable cinematic decision.**

The product should combine:

**Conversation**

* **Memory**

* **Collaborative intelligence**

* **Movie knowledge**

* **Context**

* **Discovery**

into one coherent experience.

The orb is how the user interacts with that intelligence.

---

# 74. Final Product Statement

CineRec is a conversational movie discovery system that learns a user's cinematic taste over time, understands what they want in the moment, and translates that understanding into personalized movie recommendations.

It should feel less like querying a database and more like talking to a companion who gradually gets better at answering:

> **"You know me. What should I watch tonight?"**

That feeling is the product.

