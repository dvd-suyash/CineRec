import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cinerec.core.config import settings

from cinerec.core.telemetry import setup_logging, logger

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("application_startup", environment=settings.ENVIRONMENT)
    yield
    logger.info("application_shutdown")

app = FastAPI(
    title="CineRec API",
    description="Conversational movie recommendation API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

from cinerec.core.security_middleware import SecurityHeadersMiddleware, RateLimitMiddleware

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

@app.get("/health/liveness", tags=["System"])
async def liveness_probe():
    return {"status": "alive"}

@app.get("/health/readiness", tags=["System"])
async def readiness_probe():
    # TODO: Add database and redis ping checks here
    return {"status": "ready"}

@app.get(f"{settings.API_V1_STR}/version", tags=["System"])
async def get_version():
    return {
        "version": app.version,
        "environment": settings.ENVIRONMENT,
    }

from apps.api.app.routers import auth, users, movies, ratings, watchlists, chat, memories, interactions, recommendations, search, dashboard

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(movies.router, prefix=f"{settings.API_V1_STR}/movies", tags=["Movies"])
app.include_router(ratings.router, prefix=f"{settings.API_V1_STR}/ratings", tags=["Ratings"])
app.include_router(watchlists.router, prefix=f"{settings.API_V1_STR}/watchlists", tags=["Watchlists"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["Chat"])
app.include_router(memories.router, prefix=f"{settings.API_V1_STR}/memories", tags=["Memory"])
app.include_router(interactions.router, prefix=f"{settings.API_V1_STR}/interactions", tags=["Telemetry"])
app.include_router(recommendations.router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["Recommendations"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["Search"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
