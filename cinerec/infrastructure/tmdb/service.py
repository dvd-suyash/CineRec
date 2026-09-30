import httpx
import asyncio
from cinerec.core.config import settings

class TMDBService:
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY.get_secret_value() if settings.TMDB_API_KEY else ""
        
    async def resolve_movies(self, movies: list[dict]) -> list[dict]:
        """Takes a list of movies with 'title' and 'year', returns them enriched with tmdb_id and poster_path."""
        async with httpx.AsyncClient() as client:
            tasks = [self._search_movie(client, m) for m in movies]
            results = await asyncio.gather(*tasks)
            return results

    async def _search_movie(self, client: httpx.AsyncClient, movie: dict) -> dict:
        title = movie.get("title", "")
        year = movie.get("year", "")
        
        url = "https://api.tmdb.org/3/search/multi"
        params = {
            "query": title,
            "page": 1,
            "include_adult": False
        }
        # Note: /search/multi doesn't support primary_release_year directly, 
        # but the query string fuzzy matches extremely well.
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "accept": "application/json"
        }
            
        try:
            res = await client.get(url, params=params, headers=headers, timeout=5.0)
            if res.status_code == 200:
                data = res.json()
                if data.get("results"):
                    # Filter out 'person' media types
                    valid_results = [r for r in data["results"] if r.get("media_type") in ["movie", "tv"]]
                    if valid_results:
                        best = valid_results[0]
                        
                        # If the LLM provided a year, try to match it
                        if year:
                            year_str = str(year).strip()
                            for r in valid_results:
                                release_date = r.get("release_date") or r.get("first_air_date") or ""
                                if release_date.startswith(year_str):
                                    best = r
                                    break
                                    
                        movie["tmdb_id"] = best.get("id")
                        movie["poster_path"] = best.get("poster_path")
                        movie["rating"] = round(best.get("vote_average", 0.0), 1)
        except Exception as e:
            print(f"TMDB search failed for {title}: {repr(e)}")
            
        return movie

tmdb_service = TMDBService()
