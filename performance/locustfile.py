from locust import HttpUser, task, between
import random

class VantageAIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/api/v1/dashboard")
    
    @task(2)
    def list_content(self):
        self.client.get("/api/v1/cms/content")
    
    @task(1)
    def create_content(self):
        content_data = {
            "title": f"Test Content {random.randint(1, 1000)}",
            "content": "This is a test content for performance testing",
            "platform": random.choice(["facebook", "twitter", "linkedin"])
        }
        self.client.post("/api/v1/cms/content", json=content_data)
