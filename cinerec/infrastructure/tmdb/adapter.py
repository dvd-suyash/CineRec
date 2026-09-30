from typing import Optional, List, Dict, Any
from cinerec.domain.movie.provider import MovieDataProvider
from cinerec.infrastructure.tmdb.client import TMDBClient
from cinerec.infrastructure.redis.cache import redis_cache

class TMDBAdapter(MovieDataProvider):
    """
    Concrete implementation of MovieDataProvider using TMDB.
    Incorporates Redis cache-aside with stampede prevention.
    """
    def __init__(self):
        self.client = TMDBClient()
        self.cache = redis_cache
        self.cache_ttl = 86400  # 24 hours standard TTL

    async def get_movie(self, provider_movie_id: str, language: str = "en-US") -> Optional[Dict[str, Any]]:
        cache_key = f"tmdb:movie:{provider_movie_id}:{language}"
        
        async def fetcher():
            params = {
                "language": language,
                "append_to_response": "credits,keywords,videos,images"
            }
            return await self.client.get(f"/movie/{provider_movie_id}", params=params)

        return await self.cache.get_or_set(cache_key, fetcher, ttl_seconds=self.cache_ttl)
        
    async def get_movie_credits(self, provider_movie_id: str, language: str = "en-US") -> Optional[Dict[str, Any]]:
        cache_key = f"tmdb:credits:{provider_movie_id}:{language}"
        
        async def fetcher():
            params = {"language": language}
            return await self.client.get(f"/movie/{provider_movie_id}/credits", params=params)

        return await self.cache.get_or_set(cache_key, fetcher, ttl_seconds=self.cache_ttl)
        
    async def get_movie_keywords(self, provider_movie_id: str) -> Optional[List[Dict[str, Any]]]:
        cache_key = f"tmdb:keywords:{provider_movie_id}"
        
        async def fetcher():
            res = await self.client.get(f"/movie/{provider_movie_id}/keywords")
            if res and "keywords" in res:
                return res["keywords"]
            return None

        return await self.cache.get_or_set(cache_key, fetcher, ttl_seconds=self.cache_ttl)
        
    async def get_watch_providers(self, provider_movie_id: str, region: str = "US") -> Optional[Dict[str, Any]]:
        cache_key = f"tmdb:watch-providers:{provider_movie_id}:{region}"
        
        async def fetcher():
            res = await self.client.get(f"/movie/{provider_movie_id}/watch/providers")
            if res and "results" in res and region in res["results"]:
                return res["results"][region]
            return None

        return await self.cache.get_or_set(cache_key, fetcher, ttl_seconds=self.cache_ttl)
        
    async def search_movies(self, query: str, language: str = "en-US", page: int = 1, region: Optional[str] = None) -> Dict[str, Any]:
        normalized_query = query.strip().lower()
        cache_key = f"tmdb:search:{normalized_query}:{language}:{region or 'none'}:{page}"
        
        async def fetcher():
            params = {
                "query": normalized_query,
                "language": language,
                "page": page,
                "include_adult": "false"
            }
            if region:
                params["region"] = region
            return await self.client.get("/search/movie", params=params)

        result = await self.cache.get_or_set(cache_key, fetcher, ttl_seconds=3600) # 1 hour for search
        return result or {"results": [], "total_results": 0, "total_pages": 0}
        
    async def get_similar_movies(self, provider_movie_id: str, language: str = "en-US", page: int = 1) -> Dict[str, Any]:
        cache_key = f"tmdb:similar:{provider_movie_id}:{language}:{page}"
        
        async def fetcher():
            params = {
                "language": language,
                "page": page
            }
            return await self.client.get(f"/movie/{provider_movie_id}/similar", params=params)

        result = await self.cache.get_or_set(cache_key, fetcher, ttl_seconds=self.cache_ttl)
        return result or {"results": [], "total_results": 0, "total_pages": 0}
