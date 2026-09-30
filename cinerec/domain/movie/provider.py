from typing import Protocol, Optional, List, Dict, Any

class MovieDataProvider(Protocol):
    """
    Abstract interface for external movie data providers (e.g., TMDB).
    This protocol ensures the core domain remains decoupled from any specific external API.
    """
    
    async def get_movie(self, provider_movie_id: str, language: str = "en-US") -> Optional[Dict[str, Any]]:
        """Fetch normalized movie metadata by the provider's ID."""
        ...
        
    async def get_movie_credits(self, provider_movie_id: str, language: str = "en-US") -> Optional[Dict[str, Any]]:
        """Fetch cast and crew for a movie."""
        ...
        
    async def get_movie_keywords(self, provider_movie_id: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch keywords associated with a movie."""
        ...
        
    async def get_watch_providers(self, provider_movie_id: str, region: str = "US") -> Optional[Dict[str, Any]]:
        """Fetch watch providers (streaming/rent/buy) for a movie in a specific region."""
        ...
        
    async def search_movies(self, query: str, language: str = "en-US", page: int = 1, region: Optional[str] = None) -> Dict[str, Any]:
        """Search for movies by text query."""
        ...
        
    async def get_similar_movies(self, provider_movie_id: str, language: str = "en-US", page: int = 1) -> Dict[str, Any]:
        """Fetch movies similar to the given movie."""
        ...
