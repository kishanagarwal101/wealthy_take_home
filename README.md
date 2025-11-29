# Async Prime Generator System

This project implements an asynchronous prime number generator using FastAPI, Celery, and Redis, with comprehensive observability (OpenTelemetry, VictoriaMetrics, Grafana) and load testing capabilities (Locust).

## Quick Start with Docker (Recommended)

### Prerequisites

*   Docker and Docker Compose installed.

### Running the Application

1.  Navigate to the project's root directory.

2.  Build and start all services:

    ```bash
    docker-compose up --build
    ```

    This will start:
    *   **Redis** - Message broker and result backend for Celery
    *   **FastAPI application** - Available at `http://localhost:8000`
    *   **Celery worker** - Processes prime generation tasks asynchronously
    *   **OpenTelemetry Collector** - Collects traces and metrics
    *   **VictoriaMetrics** - Time-series database for metrics (available at `http://localhost:8428`)
    *   **Grafana** - Metrics visualization dashboard (available at `http://localhost:3000`, login: `admin/admin`)
    *   **Locust** - Load testing tool (available at `http://localhost:8089`)

3.  To run in detached mode (background):

    ```bash
    docker-compose up -d --build
    ```

4.  To view logs:

    ```bash
    docker-compose logs -f
    ```

5.  To stop all services:

    ```bash
    docker-compose down
    ```

6.  To stop and remove volumes (clears Redis data):

    ```bash
    docker-compose down -v
    ```

### Testing the API

Once all services are running:

*   **Access OpenAPI Docs:** Open your browser and go to `http://localhost:8000/docs` to interact with the API.

*   **POST /generate:**
    1.  Use the `/generate` endpoint to queue a prime generation task. Provide an integer `n` (e.g., 10) to specify how many prime numbers to compute.
    2.  The API will return a `request_id` (UUID).

*   **GET /status/{request_id}:**
    1.  Use the `request_id` obtained from the `/generate` endpoint.
    2.  Access `http://localhost:8000/status/{your_request_id}` in your browser or through the docs to check the task's status.
    3.  Initially, it will show `"status": "pending"`. Once the Celery worker completes the task, it will show `"status": "complete"` with the `result`.

### Observability and Monitoring

#### Grafana Dashboards

1.  Access Grafana at `http://localhost:3000`
2.  Login with credentials:
    *   Username: `admin`
    *   Password: `admin`
3.  Navigate to **Dashboards** → **Prime Generator Dashboard** to view:
    *   API request metrics (latency, throughput)
    *   Celery task duration metrics (p50, p95, p99)
    *   Custom prime task duration histogram with fine-grained millisecond buckets
    *   Request rates and error rates

#### VictoriaMetrics

VictoriaMetrics is available at `http://localhost:8428` and provides a Prometheus-compatible API for querying metrics directly.

### Load Testing with Locust

1.  Access Locust Web UI at `http://localhost:8089`
2.  Configure your load test:
    *   **Number of users:** Total concurrent users (start with 10-20)
    *   **Spawn rate:** Users per second to add (e.g., 2 users/sec)
    *   **Host:** Should be pre-filled as `http://api:8000`
3.  Click **"Start swarming"** to begin the load test
4.  Monitor results:
    *   **Locust UI:** Real-time statistics, response times, failure rates
    *   **Grafana:** Watch API latency, task duration, and throughput metrics update in real-time
    *   **Docker logs:** `docker-compose logs -f api celery-worker` to see application logs

#### Recommended Test Scenarios

*   **Light Load (Baseline):**
    *   Users: 10
    *   Spawn rate: 2/sec
    *   Duration: 2-3 minutes

*   **Medium Load:**
    *   Users: 50
    *   Spawn rate: 5/sec
    *   Duration: 5 minutes

*   **Stress Test:**
    *   Users: 100+
    *   Spawn rate: 10/sec
    *   Duration: 5-10 minutes

The Locust test simulates realistic user behavior:
*   Users generating prime tasks with varying sizes (small: 10-50, medium: 100-500, large: 1000-5000 primes)
*   Users checking task status
*   Realistic wait times between actions (1-3 seconds)

---

## Local Setup and Running (Without Docker)

### 1. Prerequisites

*   Python 3.8+ installed.
*   Redis server installed and running. You can download Redis from [redis.io](https://redis.io/download/) and start it by running `redis-server` in your terminal.

### 2. Installation

Navigate to the project's root directory and install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Running the Application

Open **three separate terminal windows** in the project's root directory.

#### a. Start Redis (if not already running)

```bash
redis-server
```

#### b. Start the Celery Worker

In the second terminal, run the Celery worker:

```bash
python -m celery -A api.celery_app worker --loglevel=info
```

#### c. Start the FastAPI Application

In the third terminal, run the FastAPI application:

```bash
python -m uvicorn api.main:app --reload
```

### 4. Testing the API

Once all three components are running:

*   **Access OpenAPI Docs:** Open your browser and go to `http://127.0.0.1:8000/docs` to interact with the API.

*   **POST /generate:**
    1.  Use the `/generate` endpoint to queue a prime generation task. Provide an integer `n` (e.g., 10) to specify how many prime numbers to compute.
    2.  The API will return a `request_id` (UUID).

*   **GET /status/{request_id}:**
    1.  Use the `request_id` obtained from the `/generate` endpoint.
    2.  Access `http://127.0.0.1:8000/status/{your_request_id}` in your browser or through the docs to check the task's status.
    3.  Initially, it will show `"status": "pending"`. Once the Celery worker completes the task, it will show `"status": "complete"` with the `result`.

---

## Architecture

The system consists of:

*   **FastAPI** - REST API for generating primes and checking task status
*   **Celery** - Asynchronous task queue for CPU-intensive prime generation
*   **Redis** - Message broker and result backend for Celery
*   **OpenTelemetry** - Distributed tracing and metrics collection
*   **VictoriaMetrics** - Time-series database for storing metrics
*   **Grafana** - Visualization and monitoring dashboards
*   **Locust** - Load testing framework

All components are containerized and orchestrated using Docker Compose.
