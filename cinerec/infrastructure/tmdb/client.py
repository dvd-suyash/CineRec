import httpx
from typing import Optional, Dict, Any
from cinerec.core.config import settings

class TMDBClient:
    """
    Low-level TMDB HTTP client handling authentication, base URLs, and timeouts.
    """
    def __init__(self):
        self.base_url = settings.TMDB_BASE_URL
        self.api_key = settings.TMDB_API_KEY.get_secret_value()
        self.timeout = settings.TMDB_TIMEOUT_SECONDS
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                
                # Treat 404 as a valid negative response (not found)
                if response.status_code == 404:
                    return None
                    
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Log telemetry here (metrics, error rate)
                if e.response.status_code == 429:
                    # Rate limited - handle this higher up or with a circuit breaker
                    pass
                raise
            except httpx.RequestError as e:
                # Log telemetry
                raise
