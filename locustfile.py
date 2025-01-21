from locust import HttpUser, task

class DjangoUser(HttpUser):
    host = "http://127.0.0.1:8000"  # Define the base host here
    
    @task
    def home_page(self):
        self.client.get("/")  # Relative path (uses the `host` attribute)