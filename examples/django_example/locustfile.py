import time
from locust import HttpUser, task, between


class DjangoUser(HttpUser):
    wait_time = between(1, 2.5)

    @task(10)
    def visit_concurrency_handler(self):
        self.client.get("/concurrency/")

    @task
    def visit_error_handler(self):
        self.client.get("/error/")

    @task
    def visit_simple_handler(self):
        self.client.get("/simple/")

    @task
    def visit_latency_handler(self):
        self.client.get("/latency/")
