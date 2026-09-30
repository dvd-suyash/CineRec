from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore"
    )

    # API Configuration
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: SecretStr
    
    # Database Configuration
    DATABASE_URL: str
    
    # Redis Configuration
    REDIS_URL: str
    
    # External Providers
    TMDB_API_KEY: SecretStr
    GEMINI_API_KEY: SecretStr
    GROQ_API_KEY: str | None = None
    OPENROUTER_API_KEY: str | None = None
    
    # TMDB Config
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE_URL: str = "https://image.tmdb.org/t/p/"
    TMDB_DEFAULT_LANGUAGE: str = "en-US"
    TMDB_DEFAULT_REGION: str = "IN"
    TMDB_TIMEOUT_SECONDS: int = 5
    
    # Auth Providers
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: SecretStr

settings = Settings()
