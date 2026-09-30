# 13 — Observability

**Project:** CineRec
**Document:** Observability
**Status:** Normative
**Version:** 1.0
**Primary framework:** OpenTelemetry
**Metrics backend:** Prometheus
**Visualization:** Grafana
**Logging:** Structured JSON logs
**Tracing:** OpenTelemetry traces
**Scope:** Application, API, database, cache, workers, LLM, TMDB, recommendation engine, ML pipeline, security, product behavior, and infrastructure

---

# 1. Purpose

Observability answers:

> **What is the system doing, why is it doing it, and can we prove what happened?**

CineRec contains multiple interacting systems:

```text id="4d7rsn"
Browser
→ Next.js
→ FastAPI
→ PostgreSQL
→ Redis
→ Celery
→ Recommendation Engine
→ Gemini
→ TMDB
```

A failure in one component can appear as a symptom somewhere else.

Example:

```text id="a3x0de"
User:
"Why is the orb taking forever?"

Possible causes:
→ Gemini latency
→ TMDB latency
→ recommendation query
→ PostgreSQL lock
→ Redis miss
→ worker backlog
→ network failure
```

Without end-to-end telemetry, the system cannot distinguish these.

The observability architecture therefore connects:

```text id="o3ka2f"
traces
+
metrics
+
logs
+
events
+
profiles
+
product-quality signals
```

OpenTelemetry is designed as a vendor-neutral framework for generating, collecting, and exporting telemetry such as traces, metrics, and logs.

---

# 2. Observability Philosophy

CineRec follows these principles.

## 2.1 Instrument boundaries

Every important system boundary should be observable:

```text id="q56iqf"
HTTP
database
Redis
queue
LLM
TMDB
recommendation engine
memory
```

---

## 2.2 Trace causality

A user request should be traceable across services and providers.

```text id="q5k0zz"
User request
   ↓
API
   ↓
Conversation
   ↓
Gemini
   ↓
tool call
   ↓
RecommendationEngine
   ↓
TMDB
   ↓
response
```

---

## 2.3 Metrics measure populations

Metrics answer:

```text id="4p1g4k"
How often?
How many?
How slow?
How successful?
How expensive?
```

---

## 2.4 Logs explain individual incidents

Logs answer:

```text id="0wzjqo"
What specifically happened?
```

---

## 2.5 Events represent meaningful state changes

Examples:

```text id="vv0w4w"
recommendation_generated
movie_watched
rating_created
memory_created
personalization_reset
```

OpenTelemetry's current event semantic conventions describe events as appropriate for meaningful point-in-time occurrences and state changes rather than duration-based operations, which are better represented as spans.

---

# 3. Observability Objectives

```text id="qz9n9q"
OBS-001  Diagnose production failures
OBS-002  Measure API reliability
OBS-003  Measure recommendation quality
OBS-004  Measure LLM behavior
OBS-005  Measure provider health
OBS-006  Detect security anomalies
OBS-007  Monitor background jobs
OBS-008  Monitor data quality
OBS-009  Understand user-facing latency
OBS-010  Track cost drivers
OBS-011  Support incident response
OBS-012  Support model/prompt evaluation
```

---

# 4. Signals

CineRec uses five primary observability signals:

```text id="1e2c6p"
1. Traces
2. Metrics
3. Logs
4. Events
5. Profiles
```

Profiles are optional initially.

Primary launch requirement:

```text id="9f6nrw"
traces
+
metrics
+
structured logs
```

---

# 5. OpenTelemetry

OpenTelemetry should be the common instrumentation layer.

It provides:

```text id="xaqvkt"
API
SDK
instrumentation
resource metadata
semantic conventions
exporters
context propagation
```

OpenTelemetry's documentation defines semantic conventions for common traces, metrics, logs, profiles, and resources so telemetry from different components can be correlated consistently.

---

# 6. Vendor Neutrality

Application code should not depend directly on:

```text id="tm6x87"
Grafana
Prometheus
Jaeger
vendor-specific logging backend
```

Instrumentation should primarily use:

```text id="xu1l7j"
OpenTelemetry API/SDK
```

This allows exporters and backends to change later.

---

# 7. Canonical Architecture

```text id="qtpv9c"
                    ┌──────────────┐
                    │    Browser   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Next.js   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    └──────┬───────┘
                           │
                 OpenTelemetry Context
                           │
          ┌────────────────┼───────────────────┐
          │                │                   │
          ▼                ▼                   ▼
      PostgreSQL         Redis              Gemini
          │                                    │
          │                                    ▼
          │                                  Tools
          │                                    │
          │                        ┌───────────┴───────────┐
          │                        ▼                       ▼
          │                 Recommendation             TMDB
          │
          ▼
       Workers
          │
          ▼
      Telemetry
          │
   ┌──────┼─────────┐
   ▼      ▼         ▼
 Traces Metrics    Logs
   │      │         │
   └──────┼─────────┘
          ▼
   Observability Stack
       ├── Prometheus
       ├── Grafana
       └── Trace/Log backend
```

---

# 8. Telemetry Pipeline

Recommended production architecture:

```text id="xpb33k"
Application
   ↓
OpenTelemetry SDK
   ↓
OTLP
   ↓
OpenTelemetry Collector
   ↓
┌───────┬────────┬─────────┐
▼       ▼        ▼
Traces Metrics  Logs
```

The Collector is useful because it decouples application instrumentation from telemetry storage/export destinations.

---

# 9. Initial Infrastructure

For the zero/near-zero budget target:

```text id="m6g03p"
OpenTelemetry
+
Prometheus
+
Grafana
```

can begin as self-hosted/local infrastructure.

A production deployment should choose storage based on:

```text id="3bfx43"
retention
traffic
query requirements
operational cost
```

rather than adding a large observability stack prematurely.

---

# 10. Service Identity

Every telemetry record must identify the originating service.

Recommended resource attributes:

```text id="j4t53o"
service.name
service.version
service.instance.id
deployment.environment
```

OpenTelemetry's semantic conventions define common resource attributes such as `service.name` and related telemetry metadata.

---

# 11. Service Names

Recommended:

```text id="xw09r2"
cinerec-web
cinerec-api
cinerec-worker
cinerec-ml
```

Infrastructure may have separate resource identities.

---

# 12. Environment

Telemetry must distinguish:

```text id="mqf8am"
development
test
staging
production
```

Never mix production and development telemetry in the same logical view without an explicit environment dimension.

---

# 13. Service Version

Include:

```text id="z5v7u8"
git commit SHA
release version
build version
```

Example:

```text id="h4d6mw"
service.version = "2026.09.28"
deployment.git_sha = "abc123..."
```

This is essential for correlating regressions with deployments.

---

# 14. Trace Concepts

A trace represents one logical operation across components.

Example:

```text id="0fokll"
POST /conversations/{id}/messages
```

becomes:

```text id="pqfmwa"
Trace
└── HTTP request
    ├── context_build
    ├── Gemini interaction
    │   ├── tool: search_movies
    │   │   └── TMDB request
    │   └── tool: recommendation
    │       ├── CF
    │       ├── vector search
    │       └── ranking
    └── persist_response
```

---

# 15. Trace IDs

Each distributed operation should carry:

```text id="h1x4y9"
trace_id
span_id
```

where applicable.

Trace context should propagate automatically across:

```text id="xzk46o"
HTTP
database instrumentation
messaging
background jobs
```

where supported.

---

# 16. Trace Propagation

When an API request creates a background job, preserve causal context where appropriate.

Example:

```text id="gijx7a"
API request
→ enqueue refresh
→ worker
```

The worker span should remain linkable to the originating request without forcing the entire request trace to remain open.

---

# 17. Do Not Keep Traces Open

A user HTTP request should not remain open while:

```text id="j9to2l"
Celery job
```

runs for minutes.

Use:

```text id="y0z6s2"
span link
```

or correlated event/job IDs.

---

# 18. Span Naming

Use stable operation names.

Examples:

```text id="2c6c25"
HTTP POST /conversations
db SELECT movies
tmdb GET /movie/{id}
gemini interaction
recommendation generate
memory retrieve
watchlist add
celery tmdb enrichment
```

Avoid embedding arbitrary user input into span names.

Bad:

```text id="x0u5yx"
search_movies_inception_sad_dark_120
```

Good:

```text id="l6i95a"
movie.search
```

User-specific values belong in attributes where appropriate.

---

# 19. Span Attributes

Useful attributes:

```text id="p2ffh3"
http.request.method
http.response.status_code
server.address
db.system
db.operation.name
provider.name
provider.operation
error.type
```

OpenTelemetry semantic conventions provide common attribute naming across HTTP, database, messaging, exceptions, and other operations.

---

# 20. Custom CineRec Attributes

Use a controlled namespace for product-specific telemetry.

Examples:

```text id="nkwqqr"
cinerec.user_segment
cinerec.recommendation.surface
cinerec.recommendation.model_version
cinerec.llm.provider
cinerec.llm.model
cinerec.prompt.version
cinerec.tool.name
```

Avoid creating arbitrary attribute names ad hoc across the codebase.

---

# 21. Trace Attributes Must Be Low Cardinality

Do not attach unbounded values such as:

```text id="ofc37q"
full user message
full memory text
complete movie overview
full JSON prompt
```

as metric labels or high-volume trace dimensions.

---

# 22. High-Cardinality Data

Potentially high-cardinality values:

```text id="m5y15x"
user_id
conversation_id
movie_id
request_id
trace_id
query string
```

These may be acceptable as logs or individual trace attributes.

They should generally not become Prometheus metric labels.

---

# 23. Metrics Philosophy

Metrics should answer questions across many events.

Examples:

```text id="fpmvka"
How many requests fail?
How many recommendations are generated?
How long do requests take?
How many Gemini calls occur?
How many TMDB calls fail?
How many jobs are pending?
```

---

# 24. Prometheus Metric Types

Prometheus defines several metric types including:

```text id="4jqdbw"
counter
gauge
histogram
summary
```

Counters accumulate events, gauges represent values that can rise or fall, and histograms record distributions such as latency.

---

# 25. Counter Usage

Use counters for:

```text id="jr9c7e"
requests
errors
recommendations
tool calls
ratings
cache hits
provider failures
```

Examples:

```text id="l7p0hc"
cinerec_http_requests_total
cinerec_errors_total
cinerec_recommendations_total
```

---

# 26. Gauge Usage

Use gauges for current state:

```text id="gs4vja"
active requests
queue depth
memory usage
database connections
active workers
```

Prometheus recommends gauges for values that can move both upward and downward, such as current concurrency.

---

# 27. Histogram Usage

Use histograms for distributions:

```text id="j9tr4v"
HTTP latency
Gemini latency
TMDB latency
DB query latency
queue age
recommendation latency
```

Histograms are particularly useful for percentile queries and latency SLOs.

---

# 28. Metric Naming

Use a stable namespace:

```text id="x4wqzn"
cinerec_*
```

Examples:

```text id="utlwcm"
cinerec_http_requests_total
cinerec_http_request_duration_seconds
cinerec_recommendation_duration_seconds
cinerec_llm_requests_total
```

OpenTelemetry recommends consistent metric naming and generally avoiding embedding units in metric names when units can be represented through metadata.

---

# 29. Metric Labels

Recommended low-cardinality labels:

```text id="7u4b6l"
service
environment
route
method
status_class
provider
operation
model
```

Avoid:

```text id="0m5woa"
user_id
conversation_id
trace_id
query
movie_id
```

as labels.

Prometheus explicitly warns about the opportunity cost of excessive labels and recommends starting conservatively and adding labels only for concrete use cases.

---

# 30. HTTP Metrics

Required:

```text id="a9v0nn"
cinerec_http_requests_total
cinerec_http_request_duration_seconds
cinerec_http_request_errors_total
```

Dimensions:

```text id="1lmd24"
method
route
status_class
```

---

# 31. HTTP Traffic

Track:

```text id="rfcw5c"
requests/sec
requests/min
active requests
```

---

# 32. HTTP Errors

Track:

```text id="x2r2pj"
4xx rate
5xx rate
429 rate
```

Separate:

```text id="5b8k1e"
client errors
server errors
provider errors
```

---

# 33. Endpoint Latency

For important endpoints:

```text id="4dyeu9"
p50
p95
p99
```

should be observable.

---

# 34. Recommended Endpoint Groups

Monitor separately:

```text id="1mhui8"
authentication
search
movie details
recommendations
conversation
watchlist
ratings
dashboard
```

---

# 35. API SLO Candidates

Initial targets:

```text id="0kvl9z"
ordinary API p95 < 500ms
recommendation p95 < 1s
conversation p95 < 5s
```

These are engineering starting points, not permanent guarantees.

---

# 36. Availability SLO

Define:

```text id="a3uq1h"
successful requests / eligible requests
```

rather than:

```text id="lh5fk2"
server uptime only
```

A server can be "up" while every recommendation request fails.

---

# 37. User-Visible Availability

Track separately:

```text id="aqfzej"
recommendation success
conversation success
movie search success
movie detail success
```

---

# 38. Database Metrics

Monitor:

```text id="n0tsop"
query latency
connection count
connection pool utilization
transaction duration
deadlocks
locks
errors
slow queries
```

---

# 39. Database Trace Attributes

Where practical:

```text id="2sddp5"
db.system = postgresql
db.operation.name
```

Use OpenTelemetry's database conventions where available.

---

# 40. Slow Query Monitoring

Define a threshold such as:

```text id="lkgkce"
slow query > 200ms
```

as an initial diagnostic threshold.

Production thresholds should be based on measured workload.

---

# 41. Database Pool Metrics

Track:

```text id="7quq9a"
pool size
checked-out connections
idle connections
waiters
connection failures
```

Connection exhaustion can otherwise appear to users as unexplained API latency.

---

# 42. PostgreSQL Health

Track:

```text id="xq0nzu"
database availability
transaction rate
lock waits
deadlocks
disk usage
connection usage
```

---

# 43. Redis Metrics

Track:

```text id="ubm6vw"
cache hits
cache misses
latency
connections
memory
evictions
errors
```

---

# 44. Redis Application Metrics

Required:

```text id="7u9ot4"
cinerec_cache_hits_total
cinerec_cache_misses_total
cinerec_cache_stale_serves_total
cinerec_cache_errors_total
```

---

# 45. Cache Hit Rate

Track:

```text id="o35qzs"
hit rate
```

for:

```text id="4kn0u9"
TMDB metadata
movie details
recommendations
availability
```

---

# 46. Cache Stampede Metric

Track:

```text id="brm98p"
cinerec_cache_coalesced_requests_total
```

to determine whether request deduplication is working.

---

# 47. Redis Failure Behavior

If Redis is unavailable:

```text id="18q6l5"
increase error counter
increase fallback counter
```

but the application should remain usable where designed.

---

# 48. Celery Metrics

Track:

```text id="z0wb73"
jobs submitted
jobs started
jobs completed
jobs failed
jobs retried
queue depth
job age
execution duration
```

---

# 49. Worker Metrics

Examples:

```text id="3edn15"
cinerec_worker_jobs_total
cinerec_worker_job_duration_seconds
cinerec_worker_retries_total
cinerec_worker_failures_total
```

---

# 50. Queue Health

Critical signals:

```text id="bvw8gw"
queue depth
oldest job age
failure rate
retry rate
```

---

# 51. Queue Backlog Alert

Alert when:

```text id="5aw8ut"
oldest job age
```

exceeds the operational threshold.

Queue depth alone may be misleading because a large queue can contain many fast jobs.

---

# 52. Gemini Observability

Gemini is one of CineRec's most important external dependencies.

Track:

```text id="qmq1ik"
request count
latency
errors
429
timeouts
token usage
tool calls
fallbacks
model
prompt version
```

---

# 53. Gemini Request Counter

```text id="xjz77d"
cinerec_llm_requests_total
```

Labels:

```text id="5cpzsq"
provider
model
operation
status
```

---

# 54. Gemini Latency

```text id="v3u4e2"
cinerec_llm_request_duration_seconds
```

Record:

```text id="z8c01e"
p50
p95
p99
```

---

# 55. Time to First Token

For streaming:

```text id="i9zrgt"
cinerec_llm_time_to_first_token_seconds
```

This is particularly important to Orb UX.

---

# 56. Total Generation Time

Track:

```text id="e9h9ol"
time until completed assistant output
```

separately from:

```text id="46t2zq"
time to first token
```

---

# 57. Gemini Error Metrics

Track:

```text id="d9m2su"
authentication failures
rate limits
timeouts
provider errors
invalid output
tool errors
quota exhaustion
```

---

# 58. LLM Token Metrics

Track where available:

```text id="cc9s7y"
input tokens
output tokens
cached tokens
```

OpenTelemetry has emerging GenAI semantic conventions, while the application should still maintain a stable CineRec-specific usage model so provider changes do not break dashboards.

---

# 59. LLM Cost Estimation

Calculate:

```text id="x0b1zy"
estimated cost
```

from:

```text id="0jziqs"
provider
model
input usage
output usage
cached usage
```

Pricing should come from configuration, not hardcoded application logic.

---

# 60. Token Budget Monitoring

Track:

```text id="1jmqpb"
average input tokens / turn
average output tokens / turn
maximum input size
maximum output size
```

---

# 61. LLM Tool Metrics

Track:

```text id="r22i8p"
tool calls per turn
tool call failures
tool call duration
tool call loops
```

---

# 62. Tool Call Histogram

```text id="mycfp7"
cinerec_llm_tool_calls_per_turn
```

should help detect orchestration regressions.

---

# 63. Unexpected Tool Explosion

Alert on abnormal:

```text id="cqm4ge"
tool calls / conversation
```

because an orchestration bug can multiply provider and model costs.

---

# 64. Gemini Fallback Rate

Track:

```text id="pd0f4w"
cinerec_llm_fallbacks_total
```

A sudden increase may indicate:

```text id="95mfys"
provider outage
quota issue
prompt problem
model regression
```

---

# 65. Prompt Version Metrics

Track:

```text id="j35y4w"
prompt_version
```

in traces/logs.

Use labels only when the cardinality remains controlled.

---

# 66. Model Version Metrics

Track:

```text id="ah4w5d"
model
```

to compare:

```text id="i7e4zv"
latency
quality
cost
failure rate
```

---

# 67. Gemini Quality Metrics

Technical telemetry is insufficient.

Track product-quality signals:

```text id="qmbrce"
intent accuracy
tool correctness
unsupported-claim rate
memory false-positive rate
recommendation acceptance
clarification rate
fallback rate
```

---

# 68. LLM Grounding

Track:

```text id="ba2vwe"
cinerec_llm_unsupported_claims_total
```

This should ideally approach zero for structured movie facts.

---

# 69. TMDB Observability

Track:

```text id="f2ah9d"
requests
latency
429
4xx
5xx
timeouts
cache hits
cache misses
enrichment failures
```

---

# 70. TMDB Request Metrics

```text id="l9x5pb"
cinerec_tmdb_requests_total
cinerec_tmdb_request_duration_seconds
cinerec_tmdb_errors_total
```

Labels:

```text id="8yd64f"
operation
status_class
```

---

# 71. TMDB Rate-Limit Metric

```text id="4wqqx7"
cinerec_tmdb_rate_limited_total
```

A spike should trigger investigation.

---

# 72. TMDB Cache Effectiveness

Track:

```text id="nqz0el"
cache hit rate
provider request reduction
```

The goal is to move repeated work away from TMDB.

---

# 73. TMDB Data Freshness

Track:

```text id="a2h4f0"
metadata age
availability age
stale-serving rate
```

---

# 74. TMDB Enrichment Metrics

```text id="1a3sgk"
movies discovered
movies enriched
movies embedding-ready
enrichment failures
```

---

# 75. Recommendation Observability

The recommendation system requires both operational and quality telemetry.

Operational:

```text id="fzu0x3"
latency
errors
candidate counts
cache
```

Quality:

```text id="4pfgrk"
CTR
watch conversion
rating
acceptance
diversity
coverage
novelty
```

---

# 76. Recommendation Request Metric

```text id="x3v4aj"
cinerec_recommendation_requests_total
```

---

# 77. Recommendation Latency

```text id="bo8hf9"
cinerec_recommendation_duration_seconds
```

Measure separately:

```text id="ch7k16"
candidate generation
ranking
diversity
serialization
```

---

# 78. Candidate Counts

Track distribution of:

```text id="o6y8gu"
candidate pool size
post-filter count
ranked count
final recommendation count
```

---

# 79. Empty Recommendation Rate

Critical metric:

```text id="9z2kpi"
cinerec_recommendation_empty_total
```

and:

```text id="fx8gk5"
empty_recommendation_rate
```

A sudden increase may indicate:

```text id="jmm6ki"
filter bug
data issue
model issue
provider issue
```

---

# 80. Hard-Filter Violations

Track:

```text id="hbe7at"
cinerec_recommendation_constraint_violations_total
```

This should normally be zero.

---

# 81. Duplicate Recommendation Rate

Track:

```text id="tdm7ii"
duplicate movie recommendations
```

This can identify candidate deduplication bugs.

---

# 82. Candidate Provenance

Track aggregate candidate provenance:

```text id="ec2oiy"
CF
semantic
TMDB_SIMILAR
discovery
popularity
```

Do not put high-cardinality candidate IDs into Prometheus labels.

---

# 83. Ranking Model Metrics

Track:

```text id="2pjp41"
model version
inference latency
prediction errors
fallback rate
```

---

# 84. Recommendation Quality Metrics

Offline:

```text id="l03z3k"
Precision@K
Recall@K
NDCG@K
MAP@K
Hit Rate@K
coverage
diversity
novelty
```

Online:

```text id="r6n6wd"
click
watch
completion
rating
skip
dismissal
watchlist addition
```

---

# 85. User Segment Monitoring

Monitor recommendation outcomes by:

```text id="a5crwb"
cold start
sparse
moderate
rich history
```

to catch regressions hidden by aggregate averages.

---

# 86. Memory Observability

Track:

```text id="4xo7dq"
memory candidates
validated memories
rejected candidates
memory corrections
memory deletions
memory conflicts
```

---

# 87. Memory Quality Metrics

Important:

```text id="9h6j5b"
false-memory rate
correction rate
duplicate-memory rate
memory retrieval hit rate
memory utility
```

---

# 88. Explicit vs Inferred Memory

Track separately:

```text id="fx0oqz"
explicit memories
inferred memories
```

A sudden increase in inferred memories may indicate an overly aggressive extraction prompt.

---

# 89. Memory Correction Metric

```text id="mbf8h6"
cinerec_memory_corrections_total
```

A high correction rate is a quality warning.

---

# 90. Conversation Metrics

Track:

```text id="f1slgk"
messages
conversation starts
conversation completion
turn count
clarifications
refinements
errors
```

---

# 91. Conversation Completion

Define completion carefully.

Example:

```text id="me4mrr"
recommendation generated
+
user receives result
```

rather than:

```text id="j1f5q0"
conversation lasted 10 turns
```

---

# 92. Clarification Rate

```text id="gob60j"
cinerec_clarification_requests_total
```

A sudden increase may indicate:

```text id="f3g7yz"
prompt regression
intent model regression
poor context
```

---

# 93. Excessive Clarification

Track:

```text id="9m2j3z"
average clarifications per session
```

High values can indicate poor understanding.

---

# 94. Refinement Metrics

Track:

```text id="f9qg6h"
refinement requests
successful refinements
repeated refinements
```

Repeated corrections may indicate recommendation quality problems.

---

# 95. Orb UX Metrics

Track:

```text id="r1p4wz"
time to first visual response
time to first text
time to recommendation cards
total turn time
stream interruptions
```

---

# 96. Frontend Performance

Monitor:

```text id="zq1e9a"
page load
route transitions
API latency
render errors
JS errors
```

Use standard browser observability where appropriate.

---

# 97. Core Web Vitals

Where applicable, monitor:

```text id="h8dtgy"
LCP
INP
CLS
```

along with actual product-specific measures.

---

# 98. Frontend Errors

Track:

```text id="o7qkz1"
uncaught errors
unhandled promise rejections
failed API calls
stream failures
render failures
```

Do not send full sensitive application state to an external error tracker.

---

# 99. Streaming Observability

For SSE:

```text id="b5p0q5"
connection count
connection duration
first event latency
first token latency
completion rate
disconnect rate
```

---

# 100. Stream Failure Rate

Track:

```text id="m0w5yi"
cinerec_stream_failures_total
```

Break down:

```text id="y7nn3r"
client disconnect
server error
provider failure
timeout
```

---

# 101. Authentication Metrics

Monitor:

```text id="ag8ft3"
login success
login failures
OAuth failures
session refresh
session expiry
authorization failures
```

---

# 102. Security Metrics

Track:

```text id="jdajqa"
401 rate
403 rate
429 rate
BOLA attempts
CSRF failures
rate-limit triggers
suspicious tool calls
```

---

# 103. Authorization Failures

A sudden increase in:

```text id="vqt5qj"
403
```

can indicate:

```text id="3f2j7c"
client bug
authorization regression
active probing
```

---

# 104. Rate-Limit Metrics

Track separately:

```text id="13cx3z"
API rate limits
Gemini rate limits
TMDB rate limits
```

---

# 105. Error Taxonomy

All errors should have normalized classifications.

Example:

```text id="p0o2jp"
AUTHENTICATION
AUTHORIZATION
VALIDATION
DATABASE
CACHE
QUEUE
LLM
TMDB
RECOMMENDATION
INTERNAL
```

---

# 106. Error Codes

Examples:

```text id="y07jgx"
AUTHENTICATION_REQUIRED
FORBIDDEN
VALIDATION_ERROR
RESOURCE_NOT_FOUND
RATE_LIMITED
PROVIDER_UNAVAILABLE
LLM_TIMEOUT
TMDB_RATE_LIMITED
RECOMMENDATION_UNAVAILABLE
INTERNAL_ERROR
```

---

# 107. Structured Logging

All backend logs should be JSON structured.

Example:

```json id="c6v2qo"
{
  "timestamp": "2026-09-28T08:00:00Z",
  "level": "INFO",
  "service": "cinerec-api",
  "event": "recommendation_completed",
  "trace_id": "...",
  "request_id": "...",
  "duration_ms": 384
}
```

OpenTelemetry has a stable Logs Data Model intended to allow log records from different sources to be represented consistently.

---

# 108. Required Log Fields

Common:

```text id="6nj2m9"
timestamp
level
service
environment
event
trace_id
span_id
request_id
version
```

---

# 109. Domain Log Fields

Use as appropriate:

```text id="x7rqf2"
user_id_hash
movie_id
recommendation_request_id
conversation_id
model_version
provider
operation
```

Only where required for diagnosis and with appropriate privacy handling.

---

# 110. Do Not Log Secrets

Never log:

```text id="3fuy0z"
API keys
OAuth tokens
refresh tokens
session cookies
database passwords
authorization headers
```

---

# 111. Do Not Log Full User Context

Avoid logging:

```text id="ipj6oz"
full conversation
full memory
full taste profile
full watch history
```

unless deliberately captured in a secure debugging environment.

---

# 112. Log Redaction

Implement centralized log redaction:

```text id="t8q4bg"
redact secrets
redact cookies
redact auth headers
redact sensitive fields
```

Do not rely on developers remembering to redact every field manually.

---

# 113. Exception Logging

Every unexpected exception should have:

```text id="r4h4or"
exception type
trace ID
service
operation
stack trace
```

but not unnecessary personal data.

OpenTelemetry's current semantic conventions include standardized exception attributes and exception events.

---

# 114. Log Levels

Recommended:

```text id="bti6i3"
DEBUG
development diagnostics

INFO
normal lifecycle events

WARN
degraded but recoverable condition

ERROR
failed operation

CRITICAL
major service/incident condition
```

---

# 115. Avoid Log Spam

Do not log every:

```text id="rjkb9y"
cache lookup
database row
token
stream chunk
```

at INFO level.

High-volume diagnostics belong at DEBUG or aggregate metrics.

---

# 116. Sampling Logs

High-volume systems may sample repetitive logs.

Never sample away:

```text id="hv6mp5"
security events
critical failures
deployment events
data corruption signals
```

without deliberate policy.

---

# 117. Events

Events represent meaningful state changes.

Examples:

```text id="4i1qxw"
user_signed_in
recommendation_generated
recommendation_clicked
movie_watched
rating_created
memory_created
memory_corrected
watchlist_added
personalization_reset
```

---

# 118. Event Naming

Use stable past-tense or lifecycle naming:

```text id="c7f2d3"
recommendation_generated
```

rather than:

```text id="a9l2wq"
doRecommendationThing
```

---

# 119. Event Schema

Example:

```json id="k5b4r8"
{
  "event_name": "recommendation_generated",
  "event_version": 1,
  "timestamp": "...",
  "request_id": "...",
  "user_id": "...",
  "recommendation_request_id": "...",
  "model_version": "...",
  "count": 4
}
```

---

# 120. Event Versioning

Events are contracts.

When an event changes:

```text id="x3mgfc"
increment event_version
```

when semantics materially change.

---

# 121. Product Analytics vs Observability

These are related but not identical.

Observability:

```text id="ow8n2w"
Why did the request fail?
```

Product analytics:

```text id="5rrw2f"
What did users do?
```

CineRec needs both, but they should not become one giant data-collection system.

---

# 122. Product Event Privacy

Product events should contain only required fields.

Avoid:

```text id="a3isn4"
full conversation text
full memory text
```

when simple event attributes are sufficient.

---

# 123. Correlation IDs

Use:

```text id="3cgizp"
request_id
trace_id
recommendation_request_id
conversation_id
job_id
```

as appropriate.

---

# 124. Request ID

Every API request gets a request ID.

If the client supplies one, validate and bound it rather than blindly trusting arbitrary large strings.

---

# 125. Trace-to-Log Correlation

Logs generated during a request should contain:

```text id="dn11oh"
trace_id
span_id
```

This enables jumping from:

```text id="7e5q5o"
dashboard alert
```

to:

```text id="l7gc2k"
individual trace
```

and then:

```text id="1kh6iv"
individual logs
```

---

# 126. Trace-to-Event Correlation

Important domain events should contain:

```text id="h05xj0"
trace_id
request_id
```

where useful.

---

# 127. Dashboard Design

Do not create one giant dashboard.

Create focused dashboards.

---

# 128. Dashboard 1 — System Overview

Display:

```text id="wq8jc3"
request rate
error rate
p95 latency
active requests
DB health
Redis health
worker backlog
Gemini health
TMDB health
```

---

# 129. Dashboard 2 — API

Display:

```text id="d5f2u8"
requests
4xx
5xx
p50/p95/p99
slow endpoints
```

---

# 130. Dashboard 3 — Orb

Display:

```text id="m5psxg"
messages
conversation completion
first-token latency
total turn latency
stream failures
clarification rate
fallback rate
```

---

# 131. Dashboard 4 — Gemini

Display:

```text id="v9a7v3"
request rate
error rate
429
latency
token usage
cost estimate
tool calls
fallbacks
model distribution
```

---

# 132. Dashboard 5 — TMDB

Display:

```text id="ov8g3x"
request rate
error rate
429
latency
cache hit rate
enrichment failures
```

---

# 133. Dashboard 6 — Recommendation

Display:

```text id="n9v3f8"
request rate
latency
empty results
candidate counts
constraint violations
model version
online feedback
coverage
diversity
```

---

# 134. Dashboard 7 — Workers

Display:

```text id="v6u76l"
queue depth
oldest job
throughput
failures
retries
job duration
```

---

# 135. Dashboard 8 — Database

Display:

```text id="ll7jo6"
connections
CPU
memory
query latency
slow queries
locks
deadlocks
disk usage
```

---

# 136. Dashboard 9 — Security

Display:

```text id="zfdj9l"
401
403
429
authorization failures
suspicious tool calls
rate-limit events
```

---

# 137. Dashboard 10 — Product Quality

Display:

```text id="8m4u0y"
recommendation acceptance
watch conversion
refinement rate
memory correction rate
empty recommendations
LLM grounding
```

---

# 138. Alerting Philosophy

Alert on:

```text id="q8v2w0"
user impact
sustained degradation
security risk
resource exhaustion
data integrity risk
provider failure
```

Do not alert on every individual error.

---

# 139. Alert Severity

Use:

```text id="9j1p6w"
P0
major outage / security incident

P1
major degradation

P2
contained but important issue

P3
diagnostic / non-urgent
```

---

# 140. API Alerts

Examples:

```text id="t4cn5b"
5xx rate > threshold for sustained window
p95 latency > SLO
```

---

# 141. Database Alerts

Examples:

```text id="pztj9h"
connection exhaustion
disk nearly full
deadlock spike
replication/backup issue if applicable
```

---

# 142. Redis Alerts

Examples:

```text id="h6o63b"
memory pressure
eviction spike
latency spike
availability failure
```

---

# 143. Worker Alerts

Examples:

```text id="7a1nco"
queue backlog growing
oldest job too old
failure rate spike
retry storm
```

---

# 144. Gemini Alerts

Examples:

```text id="0cxjkr"
429 spike
timeout spike
error-rate spike
fallback spike
cost spike
```

---

# 145. TMDB Alerts

Examples:

```text id="gcwq76"
429 spike
provider timeout spike
5xx spike
enrichment backlog
```

---

# 146. Recommendation Alerts

Examples:

```text id="x5u8b1"
empty recommendations spike
constraint violations > zero
ranking latency spike
candidate count collapse
```

---

# 147. Security Alerts

Examples:

```text id="pp7x3g"
authorization failure spike
credential abuse pattern
tool abuse
unusual request volume
```

---

# 148. Alert Deduplication

Multiple symptoms may come from one root cause.

For example:

```text id="u1f1yy"
Gemini outage
→ conversation failures
→ recommendation fallback
→ higher latency
```

Prefer a root-cause alert rather than flooding operators with related symptoms.

---

# 149. Alert Annotations

Every production alert should link to:

```text id="yq0vvc"
runbook
dashboard
service owner
severity
```

---

# 150. Runbooks

Maintain:

```text id="5fks1f"
docs/observability/runbooks/
├── api-latency.md
├── database-degraded.md
├── redis-degraded.md
├── gemini-outage.md
├── tmdb-outage.md
├── worker-backlog.md
├── recommendation-quality.md
└── security-anomaly.md
```

---

# 151. API Latency Runbook

Checklist:

```text id="ji6zqk"
1. Check p95/p99.
2. Identify affected routes.
3. Inspect traces.
4. Check DB latency.
5. Check Redis.
6. Check Gemini/TMDB.
7. Check recent deployment.
8. Compare error rate.
```

---

# 152. Gemini Outage Runbook

```text id="6tqg9w"
1. Check provider error rate.
2. Check 429/5xx distribution.
3. Check token usage.
4. Verify fallback path.
5. Verify cached/provider-independent recommendation path.
6. Check whether a deployment caused the increase.
```

---

# 153. TMDB Outage Runbook

```text id="v0krv7"
1. Check TMDB errors.
2. Check cache hit rate.
3. Check stale-serving rate.
4. Verify local movie catalog.
5. Check enrichment queue.
6. Confirm recommendation system remains operational.
```

---

# 154. Worker Backlog Runbook

```text id="b2t7kk"
1. Inspect queue depth.
2. Inspect oldest job.
3. Inspect worker count.
4. Inspect retry rate.
5. Check provider health.
6. Identify poison jobs.
```

---

# 155. Recommendation Quality Runbook

```text id="o5c4od"
1. Compare current metrics with baseline.
2. Inspect model version.
3. Inspect prompt version if LLM involvement changed.
4. Inspect candidate counts.
5. Inspect hard-filter violations.
6. Check recent data pipeline changes.
```

---

# 156. Error Budgets

For important services, define:

```text id="z0a87r"
SLO
↓
error budget
↓
release decision
```

The concept is more useful than trying to maximize uptime to an arbitrary number.

---

# 157. Initial SLO Categories

Start with:

```text id="kw5e3t"
API availability
recommendation availability
conversation success
stream success
```

---

# 158. Recommendation SLO

Example:

```text id="in9x3n"
≥ 99% of valid recommendation requests
produce a usable response
```

where a usable response includes an explicit fallback.

---

# 159. Conversation SLO

Example:

```text id="4d6m2q"
≥ 99% of valid conversation turns
complete without internal failure
```

Provider-specific failures can be tracked separately.

---

# 160. Latency SLO

Define:

```text id="x7tv1s"
p95
```

targets rather than relying only on averages.

---

# 161. Error Budget Usage

Track:

```text id="a7n6ks"
budget remaining
budget consumed
```

---

# 162. Deployment and Error Budget

Repeated deployment-induced failures should reduce deployment confidence even when average uptime remains high.

---

# 163. Burn-Rate Alerts

For mature deployment, use fast/slow burn-rate alerting for SLO violations rather than a huge number of static threshold alerts.

---

# 164. Trace Sampling

Trace every request in development/test.

In production:

```text id="qeqsgb"
sampling policy
```

should balance:

```text id="3hl9wo"
diagnostic value
storage cost
privacy
```

---

# 165. Error Trace Sampling

Always retain traces for important failures where feasible.

Example:

```text id="4f4u7z"
5xx
security event
critical recommendation failure
```

should have higher sampling priority.

---

# 166. Tail Sampling

A mature deployment may use tail-based sampling to retain:

```text id="uwm0yg"
slow traces
failed traces
interesting traces
```

while reducing storage of ordinary successful traffic.

---

# 167. Trace Privacy

Do not assume traces are private just because they are internal.

Treat trace storage as another data system.

---

# 168. Trace Redaction

Do not put:

```text id="xolh5e"
full prompts
memory values
full conversations
```

into trace attributes.

---

# 169. Database Trace Privacy

Do not record sensitive SQL parameter values by default.

---

# 170. Provider Trace Privacy

Record:

```text id="f0u6sw"
provider
operation
status
latency
```

rather than full request payloads.

---

# 171. LLM Trace Privacy

Prefer:

```text id="mzd25o"
model
prompt_version
input_token_count
output_token_count
tool_count
status
```

rather than full user context.

---

# 172. Logs vs Traces

Use traces for:

```text id="0t1xpp"
causal flow
latency
dependencies
```

Use logs for:

```text id="t7l54l"
specific diagnostic details
```

Do not put every piece of information into both.

---

# 173. Metrics vs Logs

Use metrics for:

```text id="pddhtx"
rates
counts
distributions
```

Use logs for:

```text id="jinh7m"
specific occurrences
```

---

# 174. Events vs Metrics

Use events for:

```text id="8s6x99"
state changes
user/product actions
```

Metrics aggregate those events.

---

# 175. Metrics Cardinality Budget

Set an explicit cardinality budget for custom Prometheus metrics.

Example:

```text id="1xj4fn"
avoid labels whose distinct values scale with user/movie/request count
```

---

# 176. High-Cardinality Query Strategy

When investigation requires:

```text id="1yy2so"
user_id
movie_id
request_id
```

use:

```text id="wvqd5l"
logs
traces
event store
```

not high-cardinality metric labels.

---

# 177. Logging Storage Retention

Define retention separately for:

```text id="r7my1z"
application logs
audit logs
security logs
debug logs
```

Security/audit retention may differ from normal operational logs.

---

# 178. Metrics Retention

Metrics should be retained long enough to identify:

```text id="5btxz6"
weekly trends
release regressions
model changes
seasonality
```

Long-term raw high-resolution data can be expensive.

---

# 179. Trace Retention

Detailed traces generally require shorter retention than aggregated metrics.

---

# 180. Cost Observability

Observability itself has a cost.

Track:

```text id="f6v4pm"
telemetry volume
metric series count
log volume
trace volume
storage
```

---

# 181. Observability Cost Metrics

Examples:

```text id="zde9vf"
logs/day
GB/day
active metric series
traces/min
```

---

# 182. Sampling Strategy

Do not collect:

```text id="r1wo8z"
100% debug logs
100% full traces
full prompts
```

in production indefinitely.

---

# 183. Production Debug Mode

Avoid permanent production debug mode.

Use controlled temporary diagnostics:

```text id="o3ugyw"
feature flag
operator-approved configuration
time-limited duration
```

---

# 184. Runtime Configuration Changes

Security/observability configuration changes should be auditable.

Example:

```text id="1u6o5m"
log level changed
trace sampling changed
provider disabled
```

---

# 185. Deployment Correlation

Dashboards should display deployments alongside metrics.

Example:

```text id="o56w1g"
5xx spike
   ↑
deployment at 13:10
```

---

# 186. Release Metadata

Emit a startup event:

```text id="h4r8oz"
service_started
```

with:

```text id="3r0yln"
version
commit
environment
```

---

# 187. Configuration Observability

Do not expose sensitive configuration, but record non-secret configuration metadata such as:

```text id="1gdip0"
model
feature flags
deployment version
```

where useful.

---

# 188. Feature Flag Observability

Track:

```text id="xjcbw3"
feature
variant
environment
```

Do not use user IDs as metric labels.

---

# 189. Model Deployment Observability

Each recommendation model release should publish:

```text id="m9lv35"
model version
dataset version
feature version
deployment timestamp
```

---

# 190. Prompt Deployment Observability

Likewise:

```text id="r2v7jr"
prompt version
model
deployment timestamp
```

---

# 191. Experiment Observability

Track:

```text id="2h1a7a"
experiment
variant
population
outcome
```

with appropriately privacy-minimized dimensions.

---

# 192. Recommendation Experiment Health

For each variant, compare:

```text id="s8rt92"
latency
empty rate
constraint violations
acceptance
feedback
```

---

# 193. AI Cost Per Active User

Useful aggregate:

```text id="l8tf6c"
estimated Gemini cost
/
active users
```

This helps identify economic regressions.

---

# 194. Recommendation Cost

Track resource consumption:

```text id="2c7t2j"
CPU
DB queries
vector searches
Gemini calls
TMDB calls
```

for recommendation generation.

---

# 195. Cost Per Recommendation Request

Estimate:

```text id="l4h1yr"
provider cost
+
compute cost
```

This should remain a product-level engineering metric.

---

# 196. TMDB Efficiency

Track:

```text id="iq8i6b"
TMDB requests
/
successful movie operations
```

Lower is generally better, subject to freshness requirements.

---

# 197. Gemini Efficiency

Track:

```text id="z1iwaz"
Gemini calls
/
completed conversations
```

and:

```text id="9c7m06"
tool calls
/
LLM interaction
```

---

# 198. Cache Efficiency

Track:

```text id="euz0v2"
cache hits
/
cache lookups
```

for each important cache group.

---

# 199. Background Efficiency

Track:

```text id="3hmwbi"
successful jobs
/
attempted jobs
```

and:

```text id="6xwrcx"
average retries
```

---

# 200. Product Health Signals

A healthy CineRec system should show:

```text id="03z5g1"
low empty recommendation rate
low constraint violation rate
stable recommendation latency
stable conversation latency
low LLM fallback rate
healthy TMDB cache hit rate
healthy worker backlog
low memory correction rate
```

---

# 201. Observability of Data Pipelines

Track:

```text id="etm9bp"
data ingestion throughput
failed imports
stale movies
embedding backlog
training dataset freshness
```

---

# 202. Feature Pipeline

Monitor:

```text id="tx63jb"
feature generation duration
feature failures
missing feature rate
```

---

# 203. Embedding Pipeline

Monitor:

```text id="s6s4rn"
embedding jobs
success rate
latency
stale embedding count
dimension mismatches
```

---

# 204. Training Pipeline

Track:

```text id="c4t5q9"
dataset version
training duration
training failures
evaluation duration
model artifact generation
```

---

# 205. ML Evaluation Observability

Every experiment should record:

```text id="uf3g8h"
experiment
model
dataset
metrics
runtime
seed
configuration
```

---

# 206. Data Quality Alerts

Alert on:

```text id="ptd63n"
sudden null increase
duplicate spike
orphan records
invalid ratings
invalid provider mappings
embedding mismatch
```

---

# 207. Data Drift Metrics

Monitor distribution changes in:

```text id="dspoxh"
rating values
interaction types
genres
release years
user activity
```

---

# 208. Model Drift

Track:

```text id="3j3l5p"
prediction distribution
recommendation distribution
feedback distribution
```

---

# 209. Recommendation Distribution Monitoring

Detect if CineRec suddenly recommends:

```text id="8pfv70"
one movie repeatedly
one genre overwhelmingly
one creator overwhelmingly
```

without product justification.

---

# 210. Popularity Bias Monitoring

Track the distribution of:

```text id="y07w9s"
popular
mid-tail
long-tail
```

recommendations.

---

# 211. Diversity Monitoring

Track:

```text id="18du1l"
intra-list similarity
genre diversity
creator diversity
```

---

# 212. Novelty Monitoring

Track whether recommendations are becoming increasingly familiar.

---

# 213. Cold-Start Monitoring

Monitor separate performance for:

```text id="5j53rp"
new users
new movies
```

---

# 214. User Feedback as Observability

Important feedback signals:

```text id="4n7viy"
liked
disliked
seen
not tonight
more like this
less like this
watchlist
completed
```

These are both product events and recommendation diagnostics.

---

# 215. Negative Feedback Monitoring

A sudden increase in:

```text id="fkc3vv"
"too dark"
"already seen"
"not relevant"
```

can indicate recommendation quality regression.

---

# 216. Recommendation Correction Metric

Track:

```text id="v4mk3h"
recommendation corrections
/
recommendation sessions
```

This is a strong quality indicator.

---

# 217. Session Success Metric

Define a meaningful successful session such as:

```text id="7m2z9g"
recommendation delivered
+
no immediate rejection
```

and separately track stronger outcomes such as:

```text id="pf2y8w"
watchlist
watch
completion
rating
```

---

# 218. Observability Sampling by User Segment

Aggregate metrics should preserve visibility across:

```text id="ms6v3j"
cold start
sparse
active
rich history
```

without putting raw user identity into metric labels.

---

# 219. Security + Observability Boundary

Observability must not become a data-exfiltration path.

Particularly protect:

```text id="0qqm5z"
memory
conversation
OAuth
API keys
```

---

# 220. Audit Logs vs Operational Logs

Audit logs:

```text id="o7cz69"
who did what
when
to which resource
```

Operational logs:

```text id="t5zpy5"
what the system did
```

Keep these concepts distinct.

---

# 221. Audit Event Examples

```text id="2b4wz8"
user_signed_in
session_revoked
memory_deleted
personalization_reset
admin_action
provider_key_rotated
```

---

# 222. Audit Log Integrity

Audit logs should not be editable by ordinary application users.

---

# 223. Privacy-Aware Audit Logs

Do not put full sensitive payloads into audit entries merely to prove an action happened.

Store:

```text id="9w0f2q"
actor
target
action
timestamp
resource identifier
result
```

---

# 224. Incident Investigation Workflow

```text id="td2k4r"
Alert
 ↓
Dashboard
 ↓
Trace
 ↓
Logs
 ↓
Events
 ↓
Database/provider state
 ↓
Root cause
 ↓
Mitigation
 ↓
Regression test
```

---

# 225. Golden Trace

Maintain a representative known-good trace for major workflows.

Example:

```text id="zpt9c8"
recommendation turn
```

This becomes a debugging reference.

---

# 226. Trace Comparison

When a workflow becomes slow:

```text id="cnmy2n"
current trace
vs
golden/previous trace
```

can expose:

```text id="gq3j1t"
extra provider call
extra DB query
extra LLM turn
```

---

# 227. N+1 Observability

Track database query count per critical request.

A dashboard can surface:

```text id="zizjg5"
endpoint
average query count
p95 query count
```

---

# 228. Dependency Maps

Tracing should make dependency relationships visible:

```text id="m4f8tw"
API
 ├── PostgreSQL
 ├── Redis
 ├── Gemini
 └── TMDB
```

---

# 229. Service Dependency Health

For each dependency:

```text id="y0z38p"
availability
latency
error rate
```

---

# 230. External Provider Health Score

Internally calculate a descriptive health signal:

```text id="2r2l4s"
provider
success rate
latency
rate-limit rate
```

Do not present a single composite score as objective quality; preserve the underlying dimensions.

---

# 231. Dependency Budget

Each request should have a rough dependency budget.

Example:

```text id="6iaa4b"
recommendation
→ ≤ 1 Gemini interaction
→ ≤ bounded TMDB calls
→ bounded DB queries
```

Telemetry should detect budget violations.

---

# 232. Trace-Based Cost Debugging

A single conversation trace should reveal:

```text id="jpejwc"
LLM tokens
TMDB calls
DB queries
cache misses
worker calls
```

This lets the team explain expensive requests.

---

# 233. Performance Regression Detection

Compare:

```text id="vi2yih"
current release
vs
previous release
```

for:

```text id="m5g1xw"
p95 latency
DB query count
provider calls
LLM token usage
```

---

# 234. Deployment Markers

Every dashboard should support filtering by:

```text id="y9hcr1"
version
commit
environment
```

---

# 235. Canary Observability

When canary deployments are introduced:

```text id="y67znb"
canary
vs
stable
```

should be compared on:

```text id="63z2z7"
latency
errors
quality
cost
```

---

# 236. Rollout Monitoring

After deployment, monitor especially:

```text id="g48cmz"
first 15 minutes
first hour
first day
```

for unexpected changes.

---

# 237. Health Endpoints

`/health` should expose minimal status.

`/ready` should indicate whether critical local dependencies are ready.

Do not expose:

```text id="jlb2xq"
API keys
provider credentials
internal topology
sensitive errors
```

---

# 238. Health Metrics

Track:

```text id="9ce8ns"
service up
DB reachable
Redis reachable
worker healthy
```

---

# 239. Provider Health Endpoints

Do not make application liveness dependent on TMDB or Gemini.

Track provider health separately.

---

# 240. OpenTelemetry Python Integration

The OpenTelemetry Python documentation currently describes stable tracing and metrics APIs/SDKs and provides instrumentation libraries for supported frameworks and libraries.

CineRec should use official/current instrumentation packages where available.

---

# 241. FastAPI Instrumentation

FastAPI should be automatically or programmatically instrumented where appropriate.

The exact initialization pattern must follow the version of the OpenTelemetry instrumentation installed in the project.

---

# 242. HTTP Client Instrumentation

Instrument outbound clients used for:

```text id="dmw3z5"
TMDB
Gemini
other HTTP providers
```

where supported.

OpenTelemetry's Python instrumentation ecosystem includes libraries for HTTP clients such as HTTPX.

---

# 243. Database Instrumentation

Instrument PostgreSQL/SQLAlchemy activity where supported.

---

# 244. Redis Instrumentation

Instrument Redis operations where practical.

---

# 245. Celery Instrumentation

Trace job submission and execution.

If official instrumentation does not cover a specific path adequately, add manual spans.

---

# 246. Manual Instrumentation

Manual spans should be used for important CineRec domain operations.

Examples:

```text id="yg8s3k"
recommendation.generate
conversation.build_context
memory.retrieve
memory.persist
recommendation.rank
recommendation.diversify
```

OpenTelemetry's Python documentation explicitly supports manual instrumentation through its API and SDK.

---

# 247. Manual Span Boundaries

Create spans around meaningful operations, not every function.

Bad:

```text id="bq5yw0"
span for every helper function
```

Good:

```text id="v1i0f1"
span for candidate generation
span for ranking
span for provider call
```

---

# 248. Span Duration

A span should represent a meaningful operation with measurable duration.

---

# 249. Event vs Span Rule

Use a span when:

```text id="dpcg4e"
operation has duration
```

Use an event when:

```text id="hkq6pt"
something meaningful happened at a point in time
```

This follows the current OpenTelemetry event guidance.

---

# 250. Metrics Instrumentation Rule

Metrics should be created at stable business/operational boundaries.

Avoid creating one metric per internal helper.

---

# 251. Log Instrumentation Rule

Logs should explain anomalies that metrics cannot explain.

---

# 252. Observability Testing

Observability code itself must be tested.

Verify:

```text id="u7mko6"
trace exists
metrics increment
logs contain correlation IDs
errors are classified
secrets are redacted
```

---

# 253. Trace Tests

An integration test should verify a representative workflow produces:

```text id="gqn8da"
root span
DB span
provider span
application span
```

---

# 254. Metric Tests

Verify critical operations increment:

```text id="4fhl5e"
request counter
error counter
recommendation counter
provider counter
```

---

# 255. Log Tests

Test that critical errors produce:

```text id="x95ny7"
event
trace ID
request ID
error code
```

---

# 256. Redaction Tests

Provide a fake:

```text id="hj38u9"
API key
cookie
Authorization header
```

and verify telemetry contains none of them.

---

# 257. Observability Failure

Telemetry should not break the application.

If:

```text id="50sqag"
Prometheus unavailable
trace exporter unavailable
log backend unavailable
```

the primary application must continue where possible.

---

# 258. Non-Blocking Export

Telemetry export should not hold user requests hostage.

Use asynchronous/batched export where supported.

---

# 259. Telemetry Backpressure

Define behavior when the telemetry pipeline is overloaded:

```text id="twtrbl"
buffer
sample
drop low-priority telemetry
preserve critical telemetry
```

---

# 260. No Telemetry Cascade

An observability backend outage must not become:

```text id="jfpz9x"
observability failure
→ application outage
```

---

# 261. Metrics Backend Failure

Application request processing should continue even if Prometheus is unavailable.

---

# 262. Trace Backend Failure

Application request processing should continue if traces cannot be exported.

---

# 263. Log Backend Failure

Critical logs should have a local/alternate fallback appropriate to the deployment environment.

---

# 264. Telemetry Buffer Limits

Buffers must be bounded.

Never allow:

```text id="sx7n64"
unbounded telemetry queue
```

to exhaust application memory.

---

# 265. Startup Observability

At application startup emit:

```text id="v0nm2q"
service_started
```

with:

```text id="3b3m2z"
service
version
environment
```

---

# 266. Shutdown Observability

Emit:

```text id="d0sbrq"
service_stopping
```

where graceful shutdown supports it.

---

# 267. Configuration Observability

Record safe configuration metadata.

Example:

```text id="5ue6l4"
model = gemini-3.8-flash
environment = production
feature = streaming
```

Never record secrets.

---

# 268. Runtime Dependency Inventory

Maintain an observable inventory of:

```text id="znaz6z"
service
version
dependency
provider
model
```

This is useful for incident response.

---

# 269. Provider Version Monitoring

Track:

```text id="fytf3m"
Gemini model
TMDB API version
library versions
```

where meaningful.

---

# 270. Model Deprecation Awareness

A scheduled operational check should detect when configured AI models or external APIs approach deprecation.

Do not rely on telemetry alone.

---

# 271. Recommendation Model Monitoring

Every inference should know:

```text id="p4b5c7"
model_version
feature_version
```

where the system uses explicit versioning.

---

# 272. Feature Version Monitoring

If recommendation features change:

```text id="3l4i8a"
feature_version
```

should be recorded.

---

# 273. Data Snapshot Monitoring

For reproducibility, retain:

```text id="z7n9bq"
dataset_version
```

for model-training/evaluation telemetry.

---

# 274. Experiment Assignment Telemetry

Record:

```text id="3gnp66"
experiment
variant
model
```

for recommendation/LLM experiments where needed.

---

# 275. User-Level Debugging

Support operators should be able to debug a user request using:

```text id="u8ef0x"
request_id
trace_id
```

without requiring direct access to all personal data.

---

# 276. Privacy-Safe Support

Support tooling should favor:

```text id="pg9j56"
technical context
```

over:

```text id="jdiwqd"
full personal history
```

---

# 277. Diagnostic Context

For a failed recommendation, an operator should be able to determine:

```text id="v9w7w3"
request
candidate count
filter count
model version
latency
fallback
errors
```

without exposing unnecessary personal data.

---

# 278. Failed Recommendation Trace

Expected structure:

```text id="wa1n8b"
recommendation.generate
├── context.build
├── candidate.cf
├── candidate.semantic
├── candidate.tmdb
├── hard_filter
├── ranking
├── diversity
└── response.serialize
```

---

# 279. Failed Conversation Trace

Expected:

```text id="a1l66j"
conversation.turn
├── context.build
├── gemini.interaction
│   ├── tool.search
│   │   └── tmdb.request
│   └── tool.recommendation
│       └── recommendation.generate
├── gemini.synthesis
└── persist
```

---

# 280. Operational Golden Paths

Monitor these end-to-end:

```text id="g5w5ut"
login
movie search
movie details
recommendation
conversation
watchlist
rating
dashboard
```

---

# 281. Golden Path SLOs

Each critical journey should have:

```text id="c00dk3"
success criterion
latency target
error target
```

---

# 282. Synthetic Monitoring

A synthetic test can periodically exercise:

```text id="j3k8sm"
homepage
search
recommendation
conversation
```

against a safe synthetic/test environment.

---

# 283. Production Synthetic Monitoring

Production synthetic checks should:

```text id="2f1h6f"
avoid modifying real user state
use dedicated test identity if authenticated
avoid consuming large provider quotas
```

---

# 284. Synthetic Test Identity

Use a dedicated service/test identity rather than an employee's personal account.

---

# 285. Synthetic Movie Set

Use a small known set of movies to make production smoke tests deterministic.

---

# 286. Observability Acceptance Criteria

The system must allow operators to answer:

```text id="f2pkr3"
Why did this request fail?

Why was it slow?

Which dependency caused the latency?

Which model produced this response?

Which prompt version ran?

Which tools were executed?

Which recommendation model generated the candidates?

Was TMDB called?

Was Redis hit?

Which deployment version handled the request?
```

---

# 287. Critical Metrics

At minimum:

```text id="f2nq3j"
HTTP request rate
HTTP error rate
HTTP latency
DB latency
DB connections
Redis hit/miss
worker queue depth
worker failures
Gemini latency
Gemini errors
Gemini token usage
TMDB latency
TMDB errors
recommendation latency
empty recommendations
recommendation constraint violations
conversation failures
stream failures
```

---

# 288. Critical Traces

At minimum:

```text id="w7zj13"
API request
recommendation generation
conversation turn
Gemini interaction
TMDB request
database query group
worker execution
```

---

# 289. Critical Logs

At minimum:

```text id="f0f8z6"
deployment
startup
provider failures
application errors
security events
migration events
worker failures
recommendation failures
LLM fallback
```

---

# 290. Critical Events

At minimum:

```text id="k9uj3d"
user_signed_in
recommendation_generated
recommendation_feedback
movie_watched
rating_created
watchlist_updated
memory_created
memory_corrected
personalization_reset
```

---

# 291. Minimum Grafana Dashboards

Required:

```text id="5h5pg3"
System Overview
API
Gemini
TMDB
Recommendation
Workers
Database
Security
Product Quality
```

---

# 292. Minimum Alerts

Required:

```text id="q0n3c0"
API 5xx spike
API latency violation
DB exhaustion
Redis failure
worker backlog
Gemini outage/rate-limit spike
TMDB outage/rate-limit spike
recommendation empty-rate spike
security anomaly
```

---

# 293. Development Observability

Local development should make it easy to inspect:

```text id="u51o0p"
logs
traces
metrics
```

without needing a complex cloud stack.

---

# 294. Docker Compose Observability

A development stack may eventually include:

```text id="e6j25w"
api
web
postgres
redis
worker
otel-collector
prometheus
grafana
```

Optional components should remain profiles rather than mandatory services when possible.

---

# 295. Local Debugging Workflow

```text id="qy1cpl"
run request
↓
open trace
↓
inspect spans
↓
jump to logs
↓
inspect metrics
```

---

# 296. Production Observability Workflow

```text id="0q6jtb"
alert
↓
system dashboard
↓
affected subsystem
↓
trace
↓
logs
↓
recent deployment
↓
dependency health
↓
mitigation
```

---

# 297. Observability Documentation

Maintain:

```text id="qfmj05"
docs/observability/
├── architecture.md
├── metrics.md
├── tracing.md
├── logging.md
├── dashboards.md
├── alerts.md
├── runbooks/
└── privacy.md
```

---

# 298. Metric Registry

Maintain a central list of important custom metrics.

Example:

```text id="j9i08s"
metric name
type
unit
labels
description
owner
dashboard
```

This avoids metric sprawl.

---

# 299. Event Registry

Likewise maintain:

```text id="5k9k8h"
event name
version
schema
owner
privacy classification
```

---

# 300. Naming Governance

Before creating a new metric/event/log field, ask:

```text id="rd7o6x"
Does an existing signal already answer this question?
```

Avoid duplicates such as:

```text id="u11q8s"
request_latency
http_duration
api_duration
request_time
```

for the same concept.

---

# 301. Semantic Convention Rule

Use OpenTelemetry semantic conventions when a standard convention exists.

Only create CineRec-specific attributes where the domain requires them.

This improves cross-library and cross-service correlation.

---

# 302. Versioning

Observability schemas should be versioned when semantics change.

Apply to:

```text id="l3gddc"
events
metric contracts
structured logs
AI execution records
```

---

# 303. Backward Compatibility

Dashboards should survive minor application releases.

Avoid renaming critical metrics casually.

---

# 304. Deprecating Metrics

When removing a metric:

```text id="v4vzgi"
mark deprecated
→ update dashboards
→ migrate alerts
→ remove
```

---

# 305. Observability Test Fixtures

Create test fixtures for:

```text id="75pmeu"
successful trace
failed trace
Gemini timeout
TMDB 429
DB timeout
worker failure
```

---

# 306. Alert Testing

Periodically simulate:

```text id="84srsb"
provider failure
DB slowdown
queue growth
```

and verify alerts fire.

---

# 307. Alert Fatigue

Monitor:

```text id="05z0j3"
number of alerts
false positives
duplicate alerts
```

An alert that operators ignore is effectively useless.

---

# 308. Alert Ownership

Every alert must have:

```text id="f5if1k"
owner
severity
runbook
resolution expectation
```

---

# 309. Observability Security

Telemetry infrastructure must have:

```text id="w6a4o0"
authentication
authorization
network restriction
retention policy
```

because telemetry can contain sensitive application metadata.

---

# 310. Grafana Security

Restrict:

```text id="3xij8c"
who can view dashboards
who can edit dashboards
who can administer data sources
```

---

# 311. Prometheus Security

Prometheus should not be exposed publicly without appropriate protection.

---

# 312. Collector Security

The OpenTelemetry Collector should:

```text id="u4qjw6"
accept only intended telemetry
validate exporters
limit resource usage
avoid public unauthenticated ingestion
```

---

# 313. Telemetry Network

Prefer:

```text id="77j2ba"
application
→ internal telemetry endpoint
```

rather than public telemetry ingestion.

---

# 314. PII Classification

Telemetry fields should be classified:

```text id="h0h3wo"
safe
internal
user-private
secret
```

and processed accordingly.

---

# 315. No Secret Telemetry

The telemetry pipeline should reject/redact:

```text id="h77myb"
API keys
tokens
cookies
passwords
private credentials
```

---

# 316. Trace Sampling + Privacy

Sampling should not be used to justify collecting sensitive content.

The correct sequence is:

```text id="m0giy3"
minimize sensitive data
→ then sample telemetry
```

not:

```text id="1x1g2a"
collect everything
→ sample later
```

---

# 317. Observability Reliability

Observability must itself have:

```text id="opg8a0"
health
capacity
retention
alerts
```

---

# 318. Monitoring Monitoring

Track telemetry infrastructure:

```text id="9j3f4w"
collector health
Prometheus health
Grafana health
storage capacity
dropped telemetry
```

---

# 319. Dropped Telemetry

Track:

```text id="f6yq74"
spans dropped
metrics dropped
logs dropped
```

A silent telemetry pipeline failure is dangerous because it creates false confidence.

---

# 320. Observability Completeness

A useful measure:

```text id="o4d8vu"
critical workflows with trace coverage
/
critical workflows total
```

---

# 321. Critical-Path Coverage

At launch, target complete observability across:

```text id="z2xwq0"
login
recommendation
conversation
movie search
movie detail
watchlist
rating
background enrichment
```

---

# 322. Recommendation Trace Coverage

Every production recommendation request should ideally have a corresponding trace or sampled diagnostic representation.

---

# 323. AI Trace Coverage

Every Gemini interaction should record:

```text id="akz4w0"
provider
model
prompt version
status
latency
usage
```

without secrets.

---

# 324. TMDB Trace Coverage

Every TMDB request should be attributable to:

```text id="bq8l0g"
operation
request trace
provider status
latency
```

---

# 325. Worker Trace Coverage

Every important background job should have:

```text id="h4ojx8"
job ID
trace/link
status
duration
retry count
```

---

# 326. Observability Debt

Track missing instrumentation as technical debt.

Examples:

```text id="9a8z4p"
untraced provider
missing latency metric
unstructured error logs
missing worker metrics
```

---

# 327. No Blind Spots

A subsystem that cannot answer:

```text id="c4n5kk"
how often?
how slow?
how often failing?
```

is an observability gap.

---

# 328. First Implementation Phase

Start with:

```text id="ls5o2u"
1. OpenTelemetry SDK
2. FastAPI instrumentation
3. HTTP client instrumentation
4. DB instrumentation
5. structured logging
6. Prometheus metrics
7. basic Grafana dashboard
8. request correlation
```

---

# 329. Second Implementation Phase

Add:

```text id="5d1n0m"
Gemini telemetry
TMDB telemetry
recommendation traces
worker traces
cache metrics
```

---

# 330. Third Implementation Phase

Add:

```text id="0b7u6s"
SLOs
alerts
runbooks
product-quality metrics
AI quality metrics
data-quality monitoring
```

---

# 331. Fourth Implementation Phase

Only when scale requires it:

```text id="c9n0bz"
tail sampling
advanced profiling
long-term metrics
distributed tracing optimization
advanced anomaly detection
```

---

# 332. No Premature Observability Infrastructure

Do not start with:

```text id="ro6b6r"
Kubernetes
Loki
Tempo
Mimir
multiple collectors
SIEM
```

just because they appear in enterprise diagrams.

The first version can be substantially simpler.

---

# 333. Production Minimum

Required:

```text id="4uhy8z"
OpenTelemetry
Prometheus
Grafana
structured logs
critical traces
critical alerts
```

---

# 334. Definition of Done — Instrumentation

```text id="l07bvo"
[ ] OpenTelemetry configured
[ ] service metadata configured
[ ] trace propagation configured
[ ] FastAPI instrumented
[ ] outbound HTTP instrumented
[ ] PostgreSQL instrumented
[ ] Redis instrumented
[ ] Celery instrumented
[ ] manual recommendation spans
[ ] manual conversation spans
[ ] Gemini telemetry
[ ] TMDB telemetry
```

---

# 335. Definition of Done — Metrics

```text id="y9d1w4"
[ ] HTTP metrics
[ ] DB metrics
[ ] Redis metrics
[ ] worker metrics
[ ] Gemini metrics
[ ] TMDB metrics
[ ] recommendation metrics
[ ] conversation metrics
[ ] security metrics
[ ] product-quality metrics
```

---

# 336. Definition of Done — Logs

```text id="l4hp6u"
[ ] JSON logs
[ ] correlation IDs
[ ] normalized error fields
[ ] secret redaction
[ ] privacy minimization
[ ] deployment logging
[ ] provider error logging
[ ] security event logging
```

---

# 337. Definition of Done — Events

```text id="al3syc"
[ ] event taxonomy
[ ] schemas
[ ] versions
[ ] product events
[ ] audit events
[ ] correlation
```

---

# 338. Definition of Done — Dashboards

```text id="w4xxuh"
[ ] system overview
[ ] API
[ ] Gemini
[ ] TMDB
[ ] recommendation
[ ] workers
[ ] database
[ ] security
[ ] product quality
```

---

# 339. Definition of Done — Alerts

```text id="b0fcf7"
[ ] API outage
[ ] latency violation
[ ] DB exhaustion
[ ] Redis outage
[ ] worker backlog
[ ] Gemini outage
[ ] TMDB outage
[ ] recommendation degradation
[ ] security anomaly
```

---

# 340. Definition of Done — Operations

```text id="p18a36"
[ ] runbooks
[ ] incident correlation
[ ] deployment markers
[ ] telemetry retention
[ ] telemetry security
[ ] alert ownership
[ ] observability tests
```

---

# 341. Canonical Observability Flow

```text id="1z8zj6"
                         USER
                           │
                           ▼
                     Browser Request
                           │
                           ▼
                        FastAPI
                           │
                       Trace ID
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   PostgreSQL            Redis             Gemini
        │                                     │
        │                                     ▼
        │                                   Tools
        │                                     │
        │                           ┌─────────┴─────────┐
        │                           ▼                   ▼
        │                    Recommendation           TMDB
        │
        ▼
      Worker
        │
        └──────────────► Telemetry
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
              Trace        Metrics       Logs
                │            │            │
                └────────────┼────────────┘
                             ▼
                      Grafana / Storage
                             │
                             ▼
                         Operator
```

---

# 342. Final Operational Principle

> **Every important user-visible operation must be explainable after the fact.**

For example, for:

```text id="tm8l6q"
"I asked for a recommendation and it took 4 seconds."
```

CineRec should be able to determine:

```text id="5s0ukm"
request latency
→ context-build latency
→ recommendation latency
→ Gemini latency
→ TMDB latency
→ DB latency
→ cache behavior
→ final response
```

---

# 343. Final Quality Principle

Operational observability and product observability must converge.

The system must let engineers see both:

```text id="1g7bpj"
"the API is healthy"
```

and:

```text id="5po2bn"
"the recommendations are actually getting better."
```

A technically healthy recommender that users consistently reject is not a healthy product.

---

# 344. Final Engineering Principle

CineRec's observability stack should answer five questions:

```text id="7a9cw7"
1. Is the system working?
2. Is it fast enough?
3. If not, where is it failing?
4. Is the AI/recommendation experience getting better?
5. Can we explain what happened without exposing private data?
```

The canonical answer is:

```text id="8d33r8"
Metrics
→ tell us that something is wrong.

Traces
→ tell us where and why.

Logs
→ tell us the specific details.

Events
→ tell us what changed.

Product/ML telemetry
→ tells us whether CineRec itself is getting better.
```

That is the observability contract for the entire CineRec architecture.

