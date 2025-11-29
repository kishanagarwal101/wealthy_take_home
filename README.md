# Async Prime Generator System

This project implements an asynchronous prime number generator using FastAPI, Celery, and Redis.

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
    *   Redis server
    *   FastAPI application (available at `http://localhost:8000`)
    *   Celery worker

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
