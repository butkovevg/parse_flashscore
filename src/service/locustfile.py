from locust import HttpUser, between, task


class FastAPITestUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Задержка между запросами

    @task
    def get_home(self):
        self.client.get("/")

    @task(3)
    def post_predict(self):
        payload = {"text": "Hello FastAPI"}
        self.client.post("/predict", json=payload)
