from locust import HttpUser, task, between
import json

class CineRecUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def test_search(self):
        self.client.get("/api/v1/movies/search?q=inception")

    @task(1)
    def test_baseline_recommendations(self):
        self.client.get("/api/v1/recommendations/baseline?limit=20")
        
    @task(2)
    def test_chat_interaction(self):
        # Stub for streaming endpoint load testing
        pass
