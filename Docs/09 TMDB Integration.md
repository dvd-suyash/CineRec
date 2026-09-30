# 09 — TMDB Integration

**Project:** CineRec
**Document:** TMDB Integration
**Status:** Normative
**Version:** 1.0
**Primary provider:** The Movie Database (TMDB) API
**Scope:** Movie metadata, discovery, credits, keywords, images, videos, external identifiers, similar movies, and watch-provider availability

---

# 1. Purpose

TMDB is CineRec’s initial external movie-data provider.

The purpose of this integration is to give CineRec a reliable and normalized source for movie metadata without allowing TMDB-specific concepts, identifiers, response structures, authentication details, or availability semantics to leak into the core application.

CineRec must treat TMDB as an **external dependency**.

The architectural boundary is:

```text
                    CineRec
                       │
                       ▼
              MovieDataProvider
                       │
                       ▼
                 TMDBAdapter
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       TMDB API v3         TMDB Image CDN
```

The rest of the application must not know whether movie data came from TMDB, a local database, a future provider, or a fallback source.

The abstraction should therefore look conceptually like:

```python
class MovieDataProvider(Protocol):
    async def search_movies(...)
    async def get_movie(...)
    async def get_movie_credits(...)
    async def get_movie_keywords(...)
    async def get_movie_images(...)
    async def get_movie_videos(...)
    async def get_watch_providers(...)
    async def get_similar_movies(...)
```

The concrete implementation is:

```text
TMDBMovieDataProvider
```

Future providers can be added without changing the recommendation engine, domain model, API contracts, or frontend.

---

# 2. Integration Principles

The TMDB integration follows these principles.

## 2.1 TMDB is not the source of truth for CineRec user data

TMDB owns external movie information.

PostgreSQL owns CineRec application state.

Therefore:

```text
TMDB
→ movie metadata

PostgreSQL
→ CineRec's normalized movie records
→ user interactions
→ ratings
→ watchlists
→ viewing history
→ recommendations
→ memories
→ taste profiles
```

Never store user-specific state in TMDB.

Never depend on a user's TMDB account for CineRec personalization.

---

## 2.2 TMDB IDs are provider identifiers

TMDB's movie ID must never become CineRec's internal primary key.

Use:

```text
movies.id                → CineRec UUID
movie_provider_ids       → provider mapping
movie_provider_ids.provider = "tmdb"
movie_provider_ids.provider_movie_id = TMDB integer ID
```

Example:

```text
movies
--------------------------------------
id                  0190...
title               Inception
release_date        2010-07-16
...

movie_provider_ids
--------------------------------------
movie_id            0190...
provider            tmdb
provider_movie_id   27205
```

This protects the application from future provider changes.

It also allows:

```text
TMDB
IMDb
Wikidata
future providers
```

to coexist without changing the core movie entity.

---

# 3. TMDB API Version

CineRec should initially use the **TMDB v3 API** for read-heavy movie operations.

TMDB currently documents v3 as the API containing its available movie, TV, actor, and image methods. Application-level authentication can use either an API key or an API Read Access Token; the Bearer-token mechanism is the preferred implementation for CineRec because the token is sent through the `Authorization` header and avoids putting credentials into query strings.

Base URL:

```text
https://api.themoviedb.org/3
```

Authentication:

```http
Authorization: Bearer ${TMDB_ACCESS_TOKEN}
```

The token is a server-side secret.

It must never be sent to:

```text
browser
Next.js client bundle
mobile client
logs
analytics
URLs
query parameters
Git repository
```

---

# 4. Environment Configuration

The backend should expose TMDB configuration through environment variables.

Recommended configuration:

```env
TMDB_BASE_URL=https://api.themoviedb.org/3
TMDB_ACCESS_TOKEN=
TMDB_IMAGE_BASE_URL=
TMDB_DEFAULT_LANGUAGE=en-US
TMDB_DEFAULT_REGION=IN
TMDB_TIMEOUT_SECONDS=5
TMDB_CONNECT_TIMEOUT_SECONDS=2
TMDB_MAX_RETRIES=2

TMDB_SEARCH_CACHE_TTL_SECONDS=3600
TMDB_DETAILS_CACHE_TTL_SECONDS=86400
TMDB_IMAGES_CACHE_TTL_SECONDS=86400
TMDB_CREDITS_CACHE_TTL_SECONDS=86400
TMDB_KEYWORDS_CACHE_TTL_SECONDS=86400
TMDB_VIDEOS_CACHE_TTL_SECONDS=86400
TMDB_WATCH_PROVIDERS_CACHE_TTL_SECONDS=21600
TMDB_SIMILAR_CACHE_TTL_SECONDS=86400
```

These TTLs are **CineRec policies**, not TMDB guarantees.

Configuration must be validated at application startup.

Example:

```python
class TMDBSettings(BaseSettings):
    base_url: AnyHttpUrl
    access_token: SecretStr
    default_language: str = "en-US"
    default_region: str = "IN"
    timeout_seconds: float = 5
    connect_timeout_seconds: float = 2
    max_retries: int = 2
```

Never use:

```python
TMDB_ACCESS_TOKEN = "actual-secret-here"
```

---

# 5. Required TMDB Operations

CineRec should use a deliberately limited subset of the TMDB API.

The initial integration should support:

| Capability      | TMDB endpoint                       | Primary CineRec purpose                        |
| --------------- | ----------------------------------- | ---------------------------------------------- |
| Movie search    | `/search/movie`                     | Search and title resolution                    |
| Movie details   | `/movie/{movie_id}`                 | Core metadata                                  |
| Credits         | `/movie/{movie_id}/credits`         | Cast and crew                                  |
| Keywords        | `/movie/{movie_id}/keywords`        | Semantic/movie-theme features                  |
| Images          | `/movie/{movie_id}/images`          | Posters and backdrops                          |
| Videos          | `/movie/{movie_id}/videos`          | Trailers and media                             |
| Watch providers | `/movie/{movie_id}/watch/providers` | Streaming/rental/purchase availability         |
| Similar movies  | `/movie/{movie_id}/similar`         | Supplemental candidate generation              |
| External IDs    | `/movie/{movie_id}/external_ids`    | Cross-provider identifiers                     |
| Discover        | `/discover/movie`                   | Broad candidate ingestion/discovery            |
| Genre list      | `/genre/movie/list`                 | Genre reference data                           |
| Configuration   | `/configuration`                    | Image configuration and static API information |

These endpoints are currently documented by TMDB. Search supports original, translated, and alternative titles; movie details supports `append_to_response`; similar-movie results are based on genres and plot keywords; configuration provides valid image-address and image-size information.

---

# 6. Search

TMDB search endpoint:

```http
GET /search/movie
```

TMDB describes this endpoint as searching movies by original, translated, and alternative titles. It accepts parameters including:

```text
query
include_adult
language
primary_release_year
page
region
year
```

with `include_adult` defaulting to false and `language` defaulting to `en-US`.

Example:

```text
GET /search/movie?query=inception&language=en-US&region=IN
```

CineRec should use TMDB search primarily for:

```text
user title search
movie disambiguation
movie import
entity resolution
```

Search should not directly return raw TMDB objects to the frontend.

Instead:

```text
TMDB response
→ adapter normalization
→ application DTO
→ API response
```

---

# 7. Search Result Normalization

TMDB search results should be converted into an internal representation.

Example:

```python
@dataclass
class MovieSearchResult:
    provider: str
    provider_movie_id: int
    title: str
    original_title: str | None
    release_date: date | None
    overview: str | None
    poster_path: str | None
    backdrop_path: str | None
    original_language: str | None
    popularity: float | None
```

Do not expose raw TMDB response objects through the application's public API.

This prevents accidental coupling such as:

```typescript
movie.poster_path
movie.genre_ids
movie.vote_average
```

being assumed to be permanent CineRec domain fields.

The frontend should consume:

```typescript
MovieSummary
```

rather than:

```typescript
TMDBMovieResponse
```

---

# 8. Movie Details

Endpoint:

```http
GET /movie/{movie_id}
```

TMDB documents this as the top-level movie-details endpoint. It supports `language`, defaults to `en-US`, and supports `append_to_response` for combining additional endpoints within the namespace. TMDB currently documents a maximum of 20 appended endpoints.

CineRec should use movie details as the canonical provider payload for importing or refreshing a movie.

Relevant fields include concepts such as:

```text
title
original_title
overview
release_date
runtime
genres
original_language
status
popularity
vote_average
vote_count
poster_path
backdrop_path
belongs_to_collection
production_companies
production_countries
spoken_languages
adult
```

Only the subset required by CineRec should be persisted.

Avoid storing the entire provider response indiscriminately.

---

# 9. `append_to_response`

`append_to_response` can reduce network calls by combining multiple TMDB resources into one request. TMDB currently allows a comma-separated list of up to 20 endpoints for this mechanism.

Example concept:

```text
/movie/27205
?append_to_response=credits,keywords,videos,images
```

However, CineRec should not append everything by default.

Use it when:

```text
the combined response is actually needed
AND
the payload size is acceptable
AND
the resulting cache behavior remains sensible
```

Avoid:

```text
always append all available resources
```

because this increases:

```text
response size
latency
deserialization work
memory use
cache size
```

Preferred strategy:

```text
Movie detail page
→ details + selected supporting data

Recommendation candidate retrieval
→ minimal metadata

Movie deep page
→ details
→ credits
→ keywords
→ images
→ videos
→ availability
```

---

# 10. Credits

Endpoint:

```http
GET /movie/{movie_id}/credits
```

TMDB exposes movie cast and crew through this endpoint. The endpoint currently accepts a `language` parameter, defaulting to `en-US`.

CineRec should normalize credits into:

```text
people
movie_credits
```

Example:

```text
people
--------------------------------------
id
name
profile_path
provider identifiers

movie_credits
--------------------------------------
movie_id
person_id
credit_type
department
job
character
cast_order
```

Important roles for personalization include:

```text
director
writer
screenwriter
actor
composer
cinematographer
```

Do not assume every person appearing in credits has equal recommendation significance.

For example:

```text
director
→ potentially strong recurring style signal

actor
→ potentially strong but less direct style signal

crew department
→ selective usage depending on recommendation model
```

The recommendation system decides feature weight.

The TMDB adapter only supplies the underlying facts.

---

# 11. Keywords

Endpoint:

```http
GET /movie/{movie_id}/keywords
```

TMDB exposes movie keywords through this endpoint.

Keywords are particularly valuable for CineRec because genres are too coarse for nuanced cinematic preferences.

For example:

```text
Genre:
Drama

Keywords:
coming of age
loneliness
small town
friendship
identity
```

This allows CineRec to distinguish movies that share a genre but produce substantially different experiences.

Keywords should feed:

```text
semantic features
content-based similarity
candidate generation
explanation
taste profiling
```

They should not be treated as absolute truth about a user's preferences.

---

# 12. Similar Movies

Endpoint:

```http
GET /movie/{movie_id}/similar
```

TMDB describes this endpoint as generating similar movies using genres and plot keywords, and explicitly notes that the results are not guaranteed to be perfect.

Therefore:

```text
TMDB Similar Movies
```

must be considered a **candidate source**, not a recommendation engine.

Never do:

```text
User liked Movie A
→ call TMDB similar
→ return first five results
```

Instead:

```text
TMDB Similar
       │
       ▼
Candidate pool
       │
       ├── personalization
       ├── collaborative filtering
       ├── semantic similarity
       ├── availability
       ├── seen-item filtering
       ├── quality filtering
       └── diversity ranking
              │
              ▼
       Final recommendations
```

---

# 13. Discover

TMDB's movie discovery endpoint is:

```http
GET /discover/movie
```

It supports numerous filtering and sorting parameters. When a region is supplied, TMDB's documentation notes that regional release information is used instead of the primary release date. It also supports comma-separated `AND` semantics and pipe-separated `OR` semantics for a number of filters.

CineRec should use Discover primarily for:

```text
catalog expansion
offline ingestion
candidate bootstrapping
controlled discovery
```

It should not be used as a substitute for personalization.

---

# 14. External IDs

Endpoint:

```http
GET /movie/{movie_id}/external_ids
```

TMDB currently exposes external identifiers including IMDb and Wikidata IDs.

Store these separately:

```text
movie_provider_ids
```

Example:

```text
provider       provider_movie_id
---------------------------------
tmdb           27205
imdb           tt1375666
wikidata       Q25188
```

This allows CineRec to reference external systems without making those systems dependencies of its internal model.

IMDb identifiers may therefore be stored as **cross-reference metadata** without integrating IMDb's API.

---

# 15. Images

TMDB returns image paths rather than complete image URLs.

TMDB's image documentation states that a working image URL is constructed from:

```text
base_url
file_size
file_path
```

and that the required base URL and valid sizes can be obtained from `/configuration`.

Conceptually:

```text
image URL
=
TMDB base URL
+
size
+
file path
```

Example:

```text
https://image.tmdb.org/t/p/w500/<poster_path>
```

Do not hardcode image sizes throughout the frontend.

Instead create an image transformation utility:

```typescript
getMovieImageUrl({
  path,
  size: "poster"
})
```

The mapping belongs in one place.

Example internal mapping:

```text
poster_small
poster_medium
poster_large
backdrop_medium
backdrop_large
profile_medium
```

The exact TMDB image sizes should be resolved from TMDB configuration rather than scattered as magic strings.

---

# 16. Image Configuration

At startup or during periodic provider synchronization, CineRec should retrieve:

```http
GET /configuration
```

TMDB states that this endpoint provides integration information such as valid image sizes and image addresses.

Store configuration in Redis or application cache.

Do not request configuration on every image render.

Recommended behavior:

```text
startup
   ↓
configuration cache
   ↓
image URL builder
```

Refresh periodically rather than per request.

---

# 17. Posters and Backdrops

Store provider paths, not complete generated URLs.

Preferred database representation:

```text
poster_path = "/abc123.jpg"
backdrop_path = "/xyz789.jpg"
```

not:

```text
poster_url = "https://image.tmdb.org/..."
```

Why?

Because a provider image configuration can change.

Storing the raw provider path allows CineRec to reconstruct URLs according to current configuration.

---

# 18. Images Are Provider Assets

Images should not be copied into the CineRec database as binary blobs.

Do not:

```text
PostgreSQL → image bytes
```

for ordinary TMDB assets.

Prefer:

```text
PostgreSQL
→ provider image path

frontend
→ image CDN/provider URL
```

A later optimization may introduce:

```text
TMDB
→ CineRec image proxy/CDN
```

but this should only happen when bandwidth, performance, caching, or provider-policy requirements justify it.

---

# 19. Videos

Endpoint:

```http
GET /movie/{movie_id}/videos
```

TMDB provides movie videos through this endpoint.

CineRec should primarily use videos for:

```text
trailers
teasers
clips
featurettes
```

Do not treat every returned video as a trailer.

Normalize fields such as:

```text
video_id
name
site
key
type
official
published_at
language
country
```

The application should select appropriate video types and providers.

For example:

```text
official trailer
→ preferred

teaser
→ secondary

clip
→ tertiary
```

---

# 20. Watch Providers

Endpoint:

```http
GET /movie/{movie_id}/watch/providers
```

TMDB documents watch-provider data as being powered by a partnership with JustWatch. The endpoint provides streaming, rental, and purchase availability by country, but it does not return complete deep links to the underlying service. TMDB says the supplied TMDB URL can be used to reach the content. JustWatch attribution is required when this data is used.

This distinction is important.

CineRec must not represent the result as:

```text
Netflix definitely has this movie.
```

unless the provider data for the relevant country and moment actually says so.

Availability is inherently temporal.

---

# 21. Region Handling

CineRec must make region explicit.

Default:

```text
IN
```

but region should be derived from the user's configured preference when available rather than silently inferred from IP.

Represent region using:

```text
ISO 3166-1 country code
```

Examples:

```text
IN
US
GB
CA
AU
```

The region should affect:

```text
watch providers
regional discovery
release information
availability explanations
```

Never mix:

```text
US availability
```

with:

```text
IN availability
```

in the same user-visible response.

---

# 22. Watch Provider Data Model

Normalize provider availability separately from core movie metadata.

Example:

```text
movie_watch_providers
--------------------------------------
id
movie_id
region
provider_type
provider_id
provider_name
logo_path
display_priority
tmdb_link
observed_at
expires_at
```

Where:

```text
provider_type
=
flatrate
free
ads
rent
buy
```

The exact accepted categories should follow the current TMDB response model.

Availability should have an observation timestamp.

Example:

```text
observed_at = 2026-09-28T05:30:00Z
```

This prevents the system from pretending stale provider data is permanently true.

---

# 23. Provider Availability Freshness

Recommended internal policy:

```text
watch-provider cache
→ short TTL

movie metadata
→ longer TTL

credits
→ long TTL

keywords
→ long TTL
```

For example:

```text
metadata          24h
credits           24h
keywords          24h
images            24h
videos            24h
similar            24h
watch providers    6h
```

These values are starting points.

They must be adjusted based on:

```text
actual request volume
staleness requirements
TMDB behavior
observability
user geography
cost
```

---

# 24. Adult Content

TMDB search and discovery expose `include_adult`.

CineRec should default to:

```text
include_adult = false
```

and should not silently override a user's content policy.

CineRec's own safety/content configuration must remain an application-level concern.

The TMDB adapter should expose an explicit parameter:

```python
include_adult: bool = False
```

rather than relying on accidental provider defaults.

---

# 25. Language Strategy

Default application language:

```text
en-US
```

but language must be configurable.

The movie domain should distinguish:

```text
original title
display title
original language
translated metadata
```

Do not overwrite the original title with a translation.

Recommended internal representation:

```text
original_title
original_language
display_title
```

This is important for:

```text
foreign cinema
regional cinema
anime
multilingual movies
Indian cinema
```

---

# 26. Indian Region Support

CineRec should support:

```text
region = IN
```

as a first-class configuration.

The system should not assume that:

```text
English language
=
US region
```

or:

```text
Hindi language
=
IN region
```

Language and region are separate concepts.

For example:

```text
language = en-US
region = IN
```

is a valid CineRec request.

---

# 27. Movie Ingestion

Movie ingestion should be asynchronous.

Do not make the following happen in a user HTTP request:

```text
user asks recommendation
→ fetch 500 movies from TMDB
→ normalize 500 movies
→ write all 500
→ compute embeddings
→ train model
→ return response
```

Instead:

```text
request
→ query existing catalog
→ identify missing movies
→ enqueue enrichment
→ continue with available data
```

The ingestion pipeline:

```text
TMDB
 ↓
Raw provider response
 ↓
Schema validation
 ↓
Normalization
 ↓
Entity resolution
 ↓
PostgreSQL upsert
 ↓
Feature extraction
 ↓
Embedding generation
 ↓
Search/index refresh
```

---

# 28. Import Pipeline

Recommended ingestion sequence:

```text
1. Discover TMDB movie ID
2. Fetch movie details
3. Resolve/create internal movie
4. Store provider mapping
5. Fetch credits
6. Fetch keywords
7. Fetch external IDs
8. Fetch images when necessary
9. Fetch videos when necessary
10. Fetch watch providers when necessary
11. Generate normalized feature representation
12. Queue embedding update
```

Not every movie requires every resource immediately.

Use **progressive enrichment**.

---

# 29. Progressive Enrichment

Movie records should support a partially enriched state.

Example:

```text
DISCOVERED
    ↓
BASIC_METADATA
    ↓
ENRICHED
    ↓
FEATURE_READY
    ↓
EMBEDDING_READY
```

This is useful because recommendation systems often need only a subset of data.

For example:

```text
candidate generation
→ title + genres + overview may be enough

deep recommendation
→ keywords + credits + embeddings

movie details page
→ images + videos + providers
```

Do not pay the network and processing cost for information that is not currently needed.

---

# 30. Entity Resolution

Search results must be resolved against the internal database.

Resolution key:

```text
(provider, provider_movie_id)
```

not:

```text
title
```

and not:

```text
title + year
```

Titles can collide.

Examples:

```text
The Gift
The Gift
Suspiria
Suspiria
```

The provider identifier is authoritative for provider-level identity.

---

# 31. Upsert Rules

When importing TMDB data:

```text
existing provider ID
→ update existing movie

new provider ID
→ create movie + provider mapping
```

Do not create duplicate movies because metadata changed.

Bad:

```text
same TMDB ID
→ new row
```

Good:

```text
TMDB ID
→ stable provider mapping
→ update normalized fields
```

---

# 32. Data Ownership

For every persisted field, decide who owns the value.

Example:

| Field                      | Owner        |
| -------------------------- | ------------ |
| TMDB movie ID              | TMDB         |
| Title                      | TMDB-derived |
| Overview                   | TMDB-derived |
| Poster path                | TMDB-derived |
| Genres                     | TMDB-derived |
| User rating                | CineRec      |
| Watchlist status           | CineRec      |
| Viewing history            | CineRec      |
| Personal preference        | CineRec      |
| Taste profile              | CineRec      |
| Recommendation score       | CineRec      |
| Recommendation explanation | CineRec/LLM  |
| User memory                | CineRec      |

CineRec must never overwrite TMDB-owned facts with inferred user preferences.

---

# 33. Raw Provider Payloads

Do not use JSONB raw responses as the primary data model.

Bad:

```text
movies
  tmdb_payload JSONB
```

as the only movie representation.

Preferred:

```text
normalized relational fields
+
optional raw provider snapshot
```

A raw snapshot may be retained for debugging or migration purposes when justified.

Recommended:

```text
provider_payloads
```

or equivalent ingestion metadata, with:

```text
provider
entity_type
provider_entity_id
payload
fetched_at
```

Raw payload retention must have an explicit purpose and retention policy.

---

# 34. Caching Architecture

TMDB caching should have multiple layers.

```text
Browser cache
      ↓
Next.js/server cache where appropriate
      ↓
Redis
      ↓
PostgreSQL normalized data
      ↓
TMDB
```

The core rule:

> Do not call TMDB when CineRec already has sufficiently fresh information.

Cache keys should include all semantically relevant parameters.

Example:

```text
tmdb:movie:27205:en-US
tmdb:credits:27205:en-US
tmdb:watch-providers:27205:IN
tmdb:search:inception:en-US:IN:1
```

Never use:

```text
tmdb:search:inception
```

if language, region, or page changes the result.

---

# 35. Cache-aside Strategy

Preferred pattern:

```text
request
 ↓
Redis cache?
 ├── HIT → return
 └── MISS
       ↓
PostgreSQL sufficiently fresh?
 ├── YES → return/update cache
 └── NO
       ↓
TMDB
 ↓
normalize
 ↓
PostgreSQL
 ↓
Redis
 ↓
return
```

This minimizes external API pressure.

---

# 36. Cache Stampede Prevention

When many users simultaneously request the same uncached movie:

```text
100 users
→ 100 TMDB requests
```

must be avoided.

Use request coalescing or a Redis lock.

Conceptually:

```text
first request
→ obtains lock
→ fetches TMDB
→ populates cache

other requests
→ wait briefly
→ read populated cache
```

This is especially important for:

```text
popular movies
newly trending movies
homepage candidates
high-traffic recommendation results
```

---

# 37. Negative Caching

Provider errors such as:

```text
404 movie not found
```

may be negative-cached briefly.

Example:

```text
tmdb:not-found:movie:123456
TTL = 5–30 minutes
```

Do not negative-cache transient failures such as:

```text
429
500
502
503
504
```

because these may recover.

---

# 38. Rate Limiting

TMDB states that its legacy limit of 40 requests per 10 seconds was disabled in 2019, but it still maintains upper limits intended to mitigate excessive bulk scraping. Its current documentation describes these as being around the 40 requests/second range and explicitly says the limit can change and that clients should respect HTTP `429` responses.

CineRec therefore must implement its own conservative rate limiter.

Do not build the system around:

```text
40 req/sec
```

as an entitlement.

Treat that as a provider-side operational boundary that may change.

---

# 39. Internal Rate Limiter

Use a centralized rate limiter:

```text
TMDB requests
      ↓
Redis-backed limiter
      ↓
TMDB
```

All workers and API processes must share the same limiter.

Do not create:

```text
web worker limiter
celery worker limiter
cron limiter
```

independently.

Otherwise total application traffic can exceed the intended envelope.

---

# 40. Handling HTTP 429

When TMDB returns:

```http
429 Too Many Requests
```

CineRec must:

```text
1. stop immediate retry loops
2. honor Retry-After when available
3. apply exponential backoff
4. add jitter
5. reduce concurrency
6. record telemetry
```

Retrying immediately is prohibited.

Bad:

```python
for _ in range(10):
    request()
```

Better:

```text
retry
→ 0.5s
→ 1s
→ 2s
```

with jitter and provider-aware limits.

---

# 41. Retryable Errors

Reasonable retry candidates:

```text
408
429
500
502
503
504
network timeout
connection reset
```

Usually non-retryable:

```text
400
401
403
404
422
```

unless application logic specifically determines otherwise.

Never retry an invalid request repeatedly.

---

# 42. Timeout Policy

TMDB requests must have explicit timeouts.

Never allow an external provider to hold an HTTP request indefinitely.

Recommended conceptual limits:

```text
connect timeout
≈ 2 seconds

overall request timeout
≈ 5 seconds
```

The exact production values must be validated through observability.

Timeouts should be configurable.

---

# 43. Circuit Breaker

A circuit breaker should be added around TMDB once traffic justifies it.

State model:

```text
CLOSED
   ↓ repeated failures
OPEN
   ↓ cooldown
HALF_OPEN
   ↓ success
CLOSED
```

While OPEN:

```text
do not call TMDB
```

Instead use:

```text
PostgreSQL cached metadata
Redis
precomputed recommendations
fallback candidate sources
```

This prevents provider outages from becoming CineRec outages.

---

# 44. Failure Hierarchy

For movie metadata:

```text
1. Fresh PostgreSQL data
2. Stale-but-usable PostgreSQL data
3. Redis cache
4. TMDB
5. graceful degradation
```

For recommendations:

```text
personalized model
→ cached recommendation
→ popularity baseline
→ content similarity
→ safe default discovery
```

The user should receive a useful experience even when TMDB is unavailable.

---

# 45. Stale-While-Revalidate

For non-critical metadata, CineRec may return slightly stale data while refreshing it asynchronously.

Example:

```text
movie data is 25h old
↓
serve current data
↓
enqueue refresh
```

This is preferable to making the user wait for an external provider.

Watch-provider information may use a shorter staleness window because availability changes more frequently.

---

# 46. Background Synchronization

Celery workers should handle provider synchronization.

Typical jobs:

```text
tmdb.refresh_configuration
tmdb.import_movie
tmdb.refresh_movie
tmdb.refresh_watch_providers
tmdb.refresh_videos
tmdb.refresh_images
tmdb.refresh_credits
tmdb.refresh_keywords
tmdb.refresh_discover_page
```

The API request should enqueue jobs rather than performing large synchronization tasks synchronously.

---

# 47. TMDB Adapter Architecture

Recommended backend structure:

```text
apps/api/app/
├── domain/
│   └── movie/
│
├── application/
│   └── movie/
│
├── infrastructure/
│   └── providers/
│       └── tmdb/
│           ├── client.py
│           ├── models.py
│           ├── mapper.py
│           ├── repository.py
│           ├── cache.py
│           ├── rate_limiter.py
│           └── errors.py
│
└── api/
```

---

# 48. TMDB Client

The low-level client should handle:

```text
HTTP
authentication
timeouts
serialization
retries
provider errors
request metrics
```

It should not handle:

```text
user preferences
recommendation ranking
taste profiles
memory
watchlist logic
```

Example interface:

```python
class TMDBClient:
    async def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...
```

---

# 49. TMDB Mapper

Mapping responsibilities:

```text
TMDB JSON
→ validated provider model
→ CineRec domain DTO
```

Example:

```python
def map_movie(payload: TMDBMovieResponse) -> MovieProviderRecord:
    return MovieProviderRecord(
        provider="tmdb",
        provider_movie_id=payload.id,
        title=payload.title,
        original_title=payload.original_title,
        overview=payload.overview,
        release_date=parse_date(payload.release_date),
        runtime=payload.runtime,
    )
```

No recommendation logic belongs here.

---

# 50. Provider Errors

Never leak raw TMDB exceptions to users.

Create internal error types:

```text
ProviderAuthenticationError
ProviderRateLimitError
ProviderNotFoundError
ProviderUnavailableError
ProviderTimeoutError
ProviderValidationError
```

Then map them at the application layer.

Example:

```text
TMDB 429
→ ProviderRateLimitError
→ cached response / fallback
```

not:

```text
"TMDB returned HTTP 429"
```

to the user.

---

# 51. Observability

Every TMDB request should emit structured telemetry.

Recommended fields:

```text
provider = tmdb
endpoint
method
status_code
duration_ms
cache_hit
retry_count
request_id
correlation_id
region
language
error_type
```

Never log:

```text
Authorization header
access token
full URLs containing secrets
```

---

# 52. Metrics

Track:

```text
tmdb_requests_total
tmdb_request_errors_total
tmdb_request_latency_ms
tmdb_429_total
tmdb_cache_hits_total
tmdb_cache_misses_total
tmdb_stale_serves_total
tmdb_imports_total
tmdb_import_failures_total
tmdb_not_found_total
```

Derived metrics:

```text
cache hit rate
error rate
p95 latency
p99 latency
429 rate
provider availability
successful enrichment rate
```

---

# 53. Provider Health

CineRec should expose internal health information such as:

```text
TMDB provider reachable
TMDB provider error rate
TMDB last successful request
configuration cache freshness
```

However, `/health` and `/ready` should not become dependent on TMDB for ordinary availability.

A third-party outage should not necessarily make CineRec's application container appear dead.

Use:

```text
liveness
→ application process is alive

readiness
→ critical local dependencies available

provider health
→ separate observability signal
```

---

# 54. Security

The TMDB access token must be:

```text
server-side only
```

Use:

```text
environment variable
secret manager
deployment secret
```

Never:

```text
NEXT_PUBLIC_TMDB_ACCESS_TOKEN
```

Never place TMDB credentials in:

```text
frontend source
Git history
Docker image layers
client local storage
cookies
analytics events
```

Backend endpoints must act as the trust boundary.

---

# 55. No Direct Frontend-to-TMDB Dependency

The frontend should call:

```text
CineRec API
```

not:

```text
TMDB directly
```

Preferred:

```text
Browser
  ↓
CineRec API
  ↓
MovieDataProvider
  ↓
TMDB
```

This enables:

```text
authorization
caching
normalization
rate limiting
observability
provider substitution
consistent API contracts
```

---

# 56. TMDB Should Not Be the Recommendation Engine

TMDB provides data.

It does not understand:

```text
Suyash's taste
current mood
recent viewing
implicit preferences
long-term taste vector
collaborative filtering
session corrections
```

Therefore:

```text
TMDB Similar
≠
CineRec Recommendation
```

The recommendation architecture remains:

```text
User context
      ↓
Candidate generation
      ├── collaborative filtering
      ├── semantic retrieval
      ├── TMDB similarity
      ├── popularity
      ├── discovery
      └── user history
      ↓
Hard filters
      ↓
Ranking
      ↓
Diversity
      ↓
Explanation
```

---

# 57. TMDB as Candidate Source

TMDB can contribute candidates through:

```text
Discover
Similar
Search
metadata lookup
```

Each candidate should retain provenance.

Example:

```text
candidate.source =
    TMDB_SIMILAR
```

or:

```text
candidate.source =
    TMDB_DISCOVER
```

This allows recommendation traces to answer:

```text
Why did CineRec consider this movie?
```

---

# 58. Recommendation Metadata vs Provider Metadata

Do not mix:

```text
tmdb popularity
```

with:

```text
CineRec personalized score
```

For example:

```text
provider_popularity = 812.4
personalized_score = 0.87
```

These are completely different concepts.

Store them separately.

The recommendation engine decides how, or whether, provider popularity contributes to ranking.

---

# 59. Metadata Quality

TMDB metadata should be considered high-value provider data, but not infallible ground truth for subjective judgments.

For example:

```text
runtime
→ relatively objective

release date
→ structured metadata

genre
→ provider classification

"feel-good"
→ potentially derived/inferred
```

CineRec should distinguish:

```text
provider-provided fact
```

from:

```text
CineRec-generated semantic interpretation
```

This matters when generating explanations.

---

# 60. LLM Integration Boundary

Gemini must not freely browse TMDB.

The backend should provide controlled tools such as:

```text
search_movie
get_movie
get_movie_availability
get_movie_similar
```

Tool execution must pass through CineRec's provider abstraction.

Architecture:

```text
Gemini
  ↓
tool call
  ↓
Application Service
  ↓
MovieDataProvider
  ↓
TMDB
```

Never:

```text
Gemini
  ↓
raw HTTP access
  ↓
TMDB
```

This prevents:

```text
credential leakage
arbitrary API calls
excessive requests
unvalidated identifiers
prompt-injection-driven provider access
```

---

# 61. Movie ID Safety

LLM-generated movie IDs must never be trusted blindly.

Bad:

```text
Gemini says movie_id = 27205
→ database query
```

Better:

```text
Gemini selects an existing candidate
→ application validates candidate
→ provider mapping resolves ID
→ data returned
```

The model can suggest an entity.

The application verifies the entity.

---

# 62. Recommendation Explanation Grounding

A recommendation explanation may say:

```text
"I picked this because you liked slow-burn psychological dramas."
```

That statement must come from CineRec's personalization state.

It must not be generated from invented TMDB metadata.

Likewise:

```text
"This movie is available on Netflix in India."
```

must only be said when current provider data supports that claim.

The LLM should synthesize explanations from structured facts.

---

# 63. Data Freshness Metadata

Every provider-derived entity should record:

```text
provider_fetched_at
provider_updated_at
```

where meaningful.

At minimum:

```text
fetched_at
```

must be retained.

For mutable resources:

```text
movie_watch_providers
movie_videos
movie_metadata
```

freshness should be explicitly tracked.

---

# 64. Provider Data Refresh

Movie refresh priority should depend on usage.

Suggested strategy:

```text
frequently viewed movie
→ refresh more aggressively

recently recommended movie
→ refresh normally

rarely accessed movie
→ refresh lazily

historical inactive movie
→ refresh only when requested
```

This keeps the zero/near-zero budget architecture efficient.

Do not continuously synchronize the entire TMDB catalog.

---

# 65. Catalog Expansion

CineRec should not attempt to ingest all TMDB movies.

Instead maintain a controlled catalog.

Sources:

```text
popular movies
trending/discovery inputs
user searches
recommendation candidates
onboarding movies
recent releases
genre exploration
known movie relations
```

Then progressively enrich records that demonstrate demand.

This gives a dramatically better cost/utility profile than full-catalog ingestion.

---

# 66. Cold Start Strategy

During initial deployment, CineRec may have relatively few user interactions.

TMDB can provide the movie catalog while MovieLens or another suitable public dataset can bootstrap model experimentation.

Architecture:

```text
TMDB
→ production movie metadata

public dataset
→ model training/bootstrap

CineRec interactions
→ production personalization
```

Do not treat TMDB public ratings or popularity as equivalent to CineRec user feedback.

---

# 67. Production Feedback Loop

Once CineRec has real user interactions:

```text
user behavior
→ interactions
→ feature generation
→ recommendation model
→ recommendations
→ exposure
→ feedback
→ new interactions
```

TMDB remains the metadata provider.

The recommender becomes increasingly driven by CineRec's own behavioral data.

---

# 68. Database Synchronization

Movie metadata synchronization must be idempotent.

Running:

```text
refresh_movie(27205)
```

five times should not create:

```text
five movies
five genre links
five credits
```

Use deterministic provider mappings and unique constraints.

Recommended uniqueness:

```text
UNIQUE(provider, provider_movie_id)
```

and appropriate uniqueness on relationship tables.

---

# 69. Transaction Boundaries

Provider requests should not hold a long database transaction open.

Bad:

```text
BEGIN
→ TMDB HTTP request
→ process response
→ many writes
→ COMMIT
```

Better:

```text
TMDB HTTP request
↓
validate response
↓
BEGIN
↓
write normalized data
↓
COMMIT
```

Never keep PostgreSQL transactions open while waiting on a remote API.

---

# 70. Concurrency

Parallel fetching can reduce latency:

```text
details
credits
keywords
videos
```

may be fetched concurrently when genuinely necessary.

However, concurrency must pass through:

```text
rate limiter
connection limits
provider concurrency budget
```

Do not use unbounded:

```python
asyncio.gather(*thousands_of_requests)
```

for provider ingestion.

---

# 71. Bulk Ingestion

For batch imports:

```text
discover
→ queue jobs
→ bounded worker concurrency
→ provider rate limiting
→ retries
→ backoff
→ persistence
```

Batch processing should be resumable.

Each job should have:

```text
job_id
provider
entity
attempt
status
started_at
completed_at
last_error
```

Failures should not force the entire batch to restart.

---

# 72. Dead-Letter Handling

Repeated provider failures should eventually move to a dead-letter or failed-job state.

Example:

```text
PENDING
→ PROCESSING
→ RETRY
→ RETRY
→ FAILED
```

Failed jobs should remain inspectable.

Do not endlessly retry a malformed response.

---

# 73. Schema Validation

Provider responses should be validated before being trusted.

Use Pydantic models:

```python
class TMDBMovieResponse(BaseModel):
    id: int
    title: str
    overview: str | None = None
    release_date: str | None = None
```

Do not assume that every field:

```text
exists
has expected type
is non-null
is complete
```

Provider data is external input.

---

# 74. Defensive Parsing

Dates are a common example.

A movie may have:

```text
release_date = ""
```

or:

```text
release_date = null
```

Normalize safely:

```python
def parse_optional_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)
```

Do not let one malformed field crash the entire ingestion pipeline.

---

# 75. API Contract Isolation

CineRec's public API must not expose raw provider-specific fields unless the field is deliberately part of the product contract.

Avoid:

```json
{
  "tmdb_response": {...}
}
```

Prefer:

```json
{
  "id": "cine-rec-movie-id",
  "title": "Inception",
  "release_year": 2010,
  "poster_url": "...",
  "genres": ["Science Fiction", "Thriller"]
}
```

Provider information can be included explicitly where useful:

```json
{
  "external_ids": {
    "tmdb": 27205,
    "imdb": "tt1375666"
  }
}
```

but the internal API should not become a pass-through wrapper around TMDB.

---

# 76. Attribution and Legal Requirements

TMDB's current FAQ states that its API is free for non-commercial purposes when TMDB is properly attributed. It also states that projects considered commercial should use its commercial service/licensing path.

CineRec must therefore distinguish between:

```text
development/demo/non-commercial usage
```

and:

```text
commercial product usage
```

Do not assume that free developer API usage automatically grants commercial rights.

Before commercial deployment, review the then-current TMDB terms and licensing requirements.

---

# 77. TMDB Attribution

TMDB currently requires use of its logo and a prominent notice in the application identifying the TMDB API usage; its FAQ specifies that attribution should be included in an application's About/Credits-type section and provides the required notice wording.

CineRec should therefore contain an:

```text
About / Credits
```

section containing appropriate TMDB attribution.

The product UI must not imply:

```text
"Powered by TMDB"
```

in a way that suggests endorsement unless explicitly permitted.

The TMDB logo must follow the provider's current branding requirements.

---

# 78. JustWatch Attribution

If CineRec uses TMDB watch-provider data, the relevant data is powered by JustWatch.

TMDB explicitly requires JustWatch attribution for use of this data and states that non-compliant use can result in API access being revoked.

Therefore the application must include appropriate:

```text
JustWatch attribution
```

alongside the relevant availability experience or credits section according to the current requirements.

---

# 79. Attribution Architecture

Attribution should be implemented centrally.

Do not scatter:

```text
"TMDB"
"JustWatch"
```

through arbitrary frontend components.

Create a controlled component:

```text
ProviderAttribution
```

or:

```text
CreditsFooter
```

Example:

```text
Movie Data: TMDB
Streaming availability: JustWatch
```

with required official wording and branding.

Legal/product requirements should be updated whenever provider terms change.

---

# 80. Commercialization Guardrail

Before:

```text
paid subscription
advertising
revenue-generating primary use
commercial launch
```

CineRec must re-check TMDB licensing/terms.

The FAQ currently defines a project as commercial when its primary purpose is to create revenue for the benefit of the owner and directs commercial projects toward its commercial API/service.

Therefore this document does **not** authorize commercial TMDB use merely because a token works.

---

# 81. No SLA Assumption

TMDB currently states that it does not provide an SLA.

Therefore CineRec must not architect the service around the assumption that TMDB will always be:

```text
available
fast
fresh
reachable
```

The application must remain useful during provider degradation.

---

# 82. Resilience Design

For every important TMDB operation, define:

```text
freshness policy
timeout
retry policy
fallback
cache behavior
user-visible degradation
telemetry
```

Example:

```text
Watch Providers
    ↓
Redis fresh?
    ├── yes → return
    └── no
         ↓
TMDB
    ├── success → cache + return
    └── failure
         ↓
stale DB/cache?
    ├── yes → return stale with no warning unless necessary
    └── no → "Availability temporarily unavailable"
```

Never allow one provider failure to cascade into the entire recommendation pipeline.

---

# 83. Request Deduplication

Identical concurrent requests should be deduplicated where possible.

Example:

```text
10 users request Inception details
```

should preferably result in:

```text
1 provider request
10 consumers of the resulting cache entry
```

Use:

```text
cache
single-flight
distributed lock
```

as appropriate.

---

# 84. Search Cache

Search has high repetition.

Queries such as:

```text
batman
inception
interstellar
joker
```

are likely to repeat.

Cache:

```text
normalized query
language
region
page
adult policy
year filters
```

for an appropriate TTL.

Normalize query strings:

```text
" Inception "
→
"inception"
```

while preserving semantics such as language and region.

---

# 85. Database vs Redis

Redis is for:

```text
short-lived cache
locks
rate limiting
job coordination
provider response caching
```

PostgreSQL is for:

```text
normalized movie records
provider mappings
persistent freshness metadata
```

Do not make Redis the only copy of TMDB-derived movie data.

Redis loss must not destroy CineRec's movie catalog.

---

# 86. Recommendation-Time TMDB Policy

The recommendation path should minimize live TMDB calls.

Preferred:

```text
Recommendation request
→ local candidate pool
→ local metadata
→ local embeddings
→ local ranking
```

not:

```text
Recommendation request
→ call TMDB for every candidate
```

TMDB calls should primarily happen during:

```text
catalog enrichment
candidate acquisition
missing-data resolution
availability checks
```

This is essential for both scalability and cost control.

---

# 87. Availability at Recommendation Time

Streaming availability should generally be treated as a post-ranking filter or late-stage ranking feature.

Example:

```text
candidate generation
→ ranking
→ availability filter
→ diversity
```

or:

```text
candidate generation
→ ranking using availability preference
→ final filtering
```

depending on product requirements.

Do not use availability as the only recommendation criterion.

A great movie being unavailable should not distort the entire taste model.

---

# 88. Missing Metadata

A movie with incomplete metadata should not automatically be discarded.

Example:

```text
overview missing
keywords missing
poster missing
```

The system may still use:

```text
title
year
genres
credits
collaborative signals
```

Missing feature values should be represented explicitly.

Use:

```text
missing
```

rather than:

```text
fake value
```

For example:

```text
unknown runtime
≠
runtime = 0
```

---

# 89. Data Quality Checks

During ingestion, validate:

```text
TMDB ID exists
title is usable
release date parses
genres are valid
provider mapping is unique
image paths have expected structure
credit relationships are deduplicated
external IDs do not overwrite another provider
```

Unexpected provider changes should produce alerts or logged validation errors.

---

# 90. Provider Contract Tests

Create automated contract tests for the TMDB adapter.

Tests should cover:

```text
search
movie details
credits
keywords
images
videos
watch providers
similar
external IDs
configuration
```

Fixtures should represent:

```text
normal response
missing fields
empty results
404
429
500
malformed response
slow response
provider schema change
```

The recommendation engine should be testable without TMDB.

---

# 91. Mocking Strategy

Unit tests:

```text
mock TMDB client
```

Integration tests:

```text
local HTTP mock
```

Optional provider tests:

```text
real TMDB sandbox/request
```

Do not make ordinary CI tests depend on live TMDB availability.

Otherwise:

```text
TMDB outage
→ GitHub Actions failure
→ false-negative build
```

---

# 92. Contract Fixture Versioning

Provider fixtures should identify:

```text
endpoint
fixture version
captured timestamp
response shape
```

Example:

```text
tests/fixtures/tmdb/
├── movie_details.json
├── movie_credits.json
├── movie_keywords.json
├── movie_images.json
├── movie_videos.json
├── watch_providers.json
└── search_movie.json
```

When the provider schema changes:

```text
update fixture
→ update parser
→ update tests
→ document impact
```

---

# 93. Provider Abstraction Tests

Every implementation of:

```text
MovieDataProvider
```

must satisfy the same behavioral contract.

Example:

```text
TMDBMovieDataProvider
FutureMovieDataProvider
MockMovieDataProvider
```

can all be tested against the same interface-level test suite.

This makes provider replacement realistic rather than theoretical.

---

# 94. TMDB Client Interface

Recommended abstraction:

```python
class MovieDataProvider(Protocol):
    async def search_movies(
        self,
        query: str,
        *,
        language: str = "en-US",
        region: str | None = None,
        page: int = 1,
    ) -> MovieSearchPage:
        ...

    async def get_movie(
        self,
        provider_movie_id: int,
        *,
        language: str = "en-US",
    ) -> MovieRecord:
        ...

    async def get_movie_credits(
        self,
        provider_movie_id: int,
        *,
        language: str = "en-US",
    ) -> MovieCredits:
        ...

    async def get_movie_keywords(
        self,
        provider_movie_id: int,
    ) -> list[MovieKeyword]:
        ...

    async def get_movie_images(
        self,
        provider_movie_id: int,
        *,
        language: str = "en-US",
    ) -> MovieImages:
        ...

    async def get_movie_videos(
        self,
        provider_movie_id: int,
        *,
        language: str = "en-US",
    ) -> MovieVideos:
        ...

    async def get_watch_providers(
        self,
        provider_movie_id: int,
    ) -> MovieAvailability:
        ...

    async def get_similar_movies(
        self,
        provider_movie_id: int,
        *,
        language: str = "en-US",
        page: int = 1,
    ) -> MovieSearchPage:
        ...
```

The application should depend on this interface.

---

# 95. What the TMDB Adapter Must Never Do

The TMDB adapter must not:

```text
rank recommendations
calculate taste scores
modify user memories
write watchlist state
write ratings
call Gemini
decide whether a movie is emotionally appropriate
select final recommendations
access arbitrary user data
perform recommendation experiments
```

Those belong elsewhere.

Correct separation:

```text
TMDB adapter
→ movie facts

Recommendation engine
→ movie suitability

Memory system
→ persistent user preferences

Conversation engine
→ human interaction
```

---

# 96. Recommended Service Boundaries

```text
MovieCatalogService
        ↓
MovieDataProvider
        ↓
TMDBMovieDataProvider

RecommendationService
        ↓
RecommendationEngine
        ↓
local movie catalog

AvailabilityService
        ↓
MovieDataProvider
```

This keeps the integration composable.

---

# 97. TMDB Data Lifecycle

A movie should move through this lifecycle:

```text
UNKNOWN
   ↓
DISCOVERED
   ↓
IMPORTED
   ↓
ENRICHED
   ↓
FEATURED
   ↓
EMBEDDED
   ↓
ACTIVE
```

A movie can later become:

```text
STALE
```

and then:

```text
REFRESHED
```

The lifecycle is internal to CineRec.

TMDB does not define CineRec's application state.

---

# 98. Refresh Triggers

Refresh should happen when:

```text
movie requested and stale
movie recommended and stale
movie searched and missing
user opens movie detail page
availability cache expires
background refresh scheduled
provider-specific data appears incomplete
```

Do not refresh every movie continuously.

---

# 99. User Search Flow

When a user types:

```text
"Inception"
```

flow:

```text
Frontend
 ↓
GET /movies/search?q=Inception
 ↓
MovieSearchService
 ↓
local PostgreSQL search
 ↓
if coverage insufficient
 ↓
TMDB search
 ↓
normalize
 ↓
upsert discovered records
 ↓
return CineRec MovieSummary
```

This makes repeated searches increasingly local.

---

# 100. Movie Detail Flow

```text
GET /movies/{id}
       ↓
PostgreSQL
       ↓
fresh enough?
  ├── yes → return
  └── no
       ↓
refresh from TMDB
       ↓
persist
       ↓
return
```

Provider calls remain invisible to the frontend.

---

# 101. Missing Movie Flow

If CineRec receives a valid TMDB identifier that is not locally present:

```text
resolve provider mapping
→ fetch details
→ create internal movie
→ persist mapping
→ enqueue enrichment
→ return movie
```

The request should not wait for all enrichment.

---

# 102. Deleted/Unavailable Provider Content

Provider records may disappear or change.

CineRec should not blindly delete internal movie records.

Instead distinguish:

```text
provider_active
provider_missing
provider_unavailable
```

Historical user interactions must remain intact.

Example:

```text
user watched movie in 2025
TMDB data changes in 2026
```

The user's historical interaction must not disappear.

---

# 103. Historical Integrity

User events are CineRec records.

Never rewrite:

```text
rating
watch history
interaction
recommendation exposure
```

because TMDB metadata changed.

Historical recommendation records should retain enough information to explain what was shown at the time.

---

# 104. Recommendation Reproducibility

Recommendation requests should record:

```text
movie data snapshot/version where relevant
recommendation model version
taste profile version
candidate sources
ranking policy
```

This allows CineRec to reconstruct:

```text
Why was Movie X recommended?
```

even if TMDB metadata later changes.

---

# 105. Candidate Provenance

Each candidate may record:

```text
source = CF
source = TMDB_SIMILAR
source = TMDB_DISCOVER
source = SEMANTIC
source = POPULARITY
```

Potentially:

```text
candidate_provenance = {
    "source": "tmdb_similar",
    "seed_movie_id": "...",
}
```

This metadata belongs to recommendation internals, not TMDB itself.

---

# 106. Search vs Recommendation

These flows must remain separate.

Search:

```text
"I want to find Interstellar."
```

means:

```text
entity retrieval
```

Recommendation:

```text
"I want something like Interstellar but less depressing."
```

means:

```text
intent understanding
→ candidate retrieval
→ personalization
→ ranking
```

TMDB can support both, but CineRec's application logic determines which flow occurs.

---

# 107. Discovery Quality

TMDB's built-in `similar` endpoint uses genres and plot keywords. TMDB itself cautions that these results are not always perfect.

Therefore CineRec should evaluate TMDB-derived candidates using:

```text
Precision@K
Recall@K
NDCG@K
coverage
diversity
novelty
user feedback
```

A provider feature being available does not mean it is useful.

---

# 108. Cost Strategy

The integration must optimize for the project's near-zero budget.

Primary cost controls:

```text
cache aggressively
avoid duplicate requests
store normalized data
progressively enrich
use asynchronous jobs
avoid full-catalog ingestion
reuse movie metadata
batch where useful
rate-limit centrally
avoid live TMDB calls inside ranking loops
```

The application should spend external API calls where they provide the highest product value.

---

# 109. Zero-Budget Deployment Model

Initial model:

```text
User
 ↓
Next.js
 ↓
FastAPI
 ↓
PostgreSQL
 ↓
Redis
 ↓
TMDB
```

TMDB requests should be relatively infrequent compared with user-level application reads.

The system becomes scalable by moving repeated reads from:

```text
TMDB
```

to:

```text
PostgreSQL + Redis
```

rather than by scaling provider calls linearly with users.

---

# 110. Anti-Patterns

The following are prohibited.

### Anti-pattern 1 — Frontend directly calling TMDB

```text
React
→ TMDB
```

Reason:

```text
credential exposure
no centralized caching
no normalization
no rate control
provider coupling
```

---

### Anti-pattern 2 — TMDB as primary database

```text
Every page load
→ TMDB
```

Reason:

```text
slow
fragile
rate-limited
non-deterministic
```

---

### Anti-pattern 3 — TMDB Similar as final recommender

```text
Movie A
→ TMDB Similar
→ first five
```

Reason:

```text
ignores user taste
ignores collaboration
ignores history
ignores current intent
```

---

### Anti-pattern 4 — Raw TMDB JSON as domain model

```text
Movie = TMDBResponse
```

Reason:

```text
tight coupling
provider leakage
brittle schema
difficult provider replacement
```

---

### Anti-pattern 5 — Live TMDB calls for every candidate

```text
500 candidates
→ 500 TMDB calls
```

Reason:

```text
terrible latency
rate-limit risk
unnecessary network cost
```

---

### Anti-pattern 6 — Infinite retries

```text
429
→ retry
→ retry
→ retry
→ retry
```

Reason:

```text
amplifies provider overload
```

---

### Anti-pattern 7 — Hardcoding image URLs everywhere

Bad:

```typescript
`https://image.tmdb.org/t/p/w500${movie.poster_path}`
```

across dozens of components.

Correct:

```typescript
getMovieImageUrl(movie.posterPath, "posterMedium")
```

---

# 111. Initial Endpoint Priority

Not every TMDB endpoint is equally important during implementation.

## P0

```text
/movie/{id}
/search/movie
/configuration
/genre/movie/list
/movie/{id}/credits
/movie/{id}/keywords
/movie/{id}/watch/providers
```

## P1

```text
/movie/{id}/images
/movie/{id}/videos
/movie/{id}/similar
/movie/{id}/external_ids
/discover/movie
```

## P2

Additional endpoints should be added only when a product feature actually requires them.

---

# 112. Initial Implementation Order

Implement in this sequence:

```text
1. TMDB configuration
2. authentication
3. HTTP client
4. Pydantic provider models
5. error mapping
6. rate limiting
7. caching
8. movie search
9. movie details
10. normalization
11. database upserts
12. credits
13. keywords
14. images
15. videos
16. watch providers
17. similar movies
18. discover
19. background enrichment
20. observability
21. contract tests
```

Do not start with the entire API surface.

---

# 113. Acceptance Criteria

The TMDB integration is considered complete when:

### Authentication

```text
TMDB token is server-side only
```

### Search

```text
movie search works
language/region are handled explicitly
results are normalized
```

### Metadata

```text
movie details are persisted
provider IDs are separate from internal IDs
```

### Enrichment

```text
credits and keywords can be imported
```

### Media

```text
poster/backdrop paths can produce valid image URLs
videos can be surfaced
```

### Availability

```text
regional provider data can be retrieved
JustWatch attribution is implemented
```

### Resilience

```text
timeouts exist
429 is handled
retries are bounded
cache fallback exists
```

### Scalability

```text
duplicate requests are reduced
batch jobs are bounded
TMDB is not called per recommendation candidate
```

### Security

```text
token is not client-visible
token is not logged
```

### Testing

```text
mocked contract tests exist
error paths are covered
```

### Legal

```text
TMDB attribution exists
commercial licensing assumptions are not made
```

---

# 114. Definition of Done

The integration must satisfy all of the following before being considered production-ready:

```text
[ ] TMDB provider abstraction implemented
[ ] TMDB client isolated from domain
[ ] Bearer token authentication implemented
[ ] secrets managed through environment/config
[ ] request timeout configured
[ ] retry policy implemented
[ ] 429 handling implemented
[ ] centralized provider rate limiting implemented
[ ] Redis caching implemented
[ ] normalized PostgreSQL persistence implemented
[ ] provider ID uniqueness enforced
[ ] movie search implemented
[ ] movie details implemented
[ ] credits implemented
[ ] keywords implemented
[ ] images implemented
[ ] videos implemented
[ ] watch providers implemented
[ ] similar movies implemented
[ ] external IDs implemented
[ ] configuration caching implemented
[ ] background enrichment implemented
[ ] provider failure fallback implemented
[ ] structured provider telemetry implemented
[ ] provider contract tests implemented
[ ] raw provider payloads not exposed through public API
[ ] frontend does not call TMDB directly
[ ] TMDB attribution implemented
[ ] JustWatch attribution implemented where required
[ ] commercial licensing assumption documented
[ ] recommendation engine does not depend on live TMDB calls
```

---

# 115. Canonical Architecture

The final intended design is:

```text
                         ┌──────────────────┐
                         │      Frontend    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    CineRec API   │
                         └────────┬─────────┘
                                  │
                  ┌───────────────┼────────────────┐
                  │               │                │
                  ▼               ▼                ▼
          MovieCatalog      Recommendation    Conversation
             Service            Engine           Engine
                  │               │                │
                  │               │                ▼
                  │               │             Gemini
                  │               │
                  ▼               ▼
          MovieDataProvider   Candidate Sources
                  │               │
                  ▼               │
            TMDB Adapter ◄───────┘
                  │
          ┌───────┴─────────┐
          ▼                 ▼
       TMDB API          TMDB Images
          │
          ▼
      External Data

Persistence:

PostgreSQL
├── movies
├── movie_provider_ids
├── genres
├── movie_genres
├── people
├── movie_credits
├── movie_keywords
├── movie_keyword_links
├── movie_watch_providers
└── recommendation data

Redis
├── TMDB response cache
├── locks
├── rate limiter
└── ephemeral coordination

Celery
├── TMDB enrichment
├── refresh jobs
├── catalog ingestion
└── background processing
```

---

# 116. Architectural Invariant

The most important invariant of this integration is:

> **CineRec must remain functional when TMDB is slow, unavailable, rate-limited, changed, or eventually replaced.**

Therefore:

```text
TMDB is a provider.
TMDB is not the application.
TMDB is not the recommendation engine.
TMDB is not the database.
TMDB is not the user's profile.
TMDB is not the source of truth for CineRec behavior.
```

The provider boundary must remain explicit throughout the codebase.

---

# 117. Final Design Rule

CineRec should use TMDB for what TMDB is good at:

```text
movie metadata
identification
credits
keywords
images
videos
availability
discovery primitives
```

CineRec should own what makes CineRec intelligent:

```text
user identity
interaction history
ratings
preferences
memory
taste representation
collaborative filtering
candidate fusion
ranking
diversity
exploration
recommendation explanations
conversation state
```

The resulting system is:

```text
TMDB
   ↓
Movie knowledge

CineRec
   ↓
Personalized intelligence
```

That separation is fundamental to making the product scalable, testable, provider-independent, and genuinely personalized.

