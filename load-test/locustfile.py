from locust import HttpUser, task, between
import random

class PrimeGeneratorUser(HttpUser):
    """
    Locust user class that simulates users interacting with the prime generator API.
    
    Each "user" will:
    1. Generate prime tasks with varying sizes
    2. Poll for task status until completion
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts. Initialize any user-specific state."""
        self.request_ids = []  # Store request IDs for status checking
    
    @task(3)
    def generate_primes(self):
        """
        Generate a prime task with random size.
        Weight: 3 (this task runs 3x more often than check_status)
        """
        n = random.choice([
            random.randint(10, 50),
            random.randint(100, 500),
            random.randint(1000, 5000),
        ])
        
        with self.client.post(
            "/generate",
            params={"n": n},
            catch_response=True,
            name="/generate"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                if request_id:
                    self.request_ids.append(request_id)
                    response.success()
                else:
                    response.failure("No request_id in response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def check_status(self):
        """
        Check the status of a previously generated task.
        Weight: 1 (runs less frequently than generate)
        """
        if not self.request_ids:
            return
        
        request_id = random.choice(self.request_ids)
        
        with self.client.get(
            f"/status/{request_id}",
            catch_response=True,
            name="/status/{request_id}"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                if status == "complete":
                    if request_id in self.request_ids:
                        self.request_ids.remove(request_id)
                    response.success()
                elif status == "pending":
                    response.success()
                else:
                    response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

