from .celery_app import celery_app
import time
from opentelemetry import metrics

# Get the meter for custom metrics
meter = metrics.get_meter(__name__)

# Create custom histogram with smaller bucket sizes (in milliseconds)
# Buckets: 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1000ms, 2500ms, 5000ms, 10000ms, 30000ms, 60000ms
custom_task_duration_histogram = meter.create_histogram(
    name="prime_task_duration_milliseconds",
    description="Custom histogram for prime task duration with fine-grained buckets",
    unit="ms",
)

def is_prime(num: int) -> bool:
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

@celery_app.task(name="prime_generator.prime_task")
def prime_task(n: int, request_id: str):
    start_time = time.time()
    primes = []
    num = 2
    while len(primes) < n:
        if is_prime(num):
            primes.append(num)
        num += 1
    
    duration_ms = (time.time() - start_time) * 1000
    custom_task_duration_histogram.record(
        duration_ms,
        attributes={"task_name": "prime_generator.prime_task", "n": str(n)}
    )
    
    return primes
