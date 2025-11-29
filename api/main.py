from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

from .celery_app import celery_app
from .prime_logic import prime_task

app = FastAPI()

class GenerateResponse(BaseModel):
    request_id: str

class StatusResponse(BaseModel):
    status: str
    result: List[int] | None = None
    
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/generate", response_model=GenerateResponse)
async def generate_primes(n: int):
    if n <= 0:
        raise HTTPException(status_code=400, detail="n must be a positive integer")
    
    # Queue Celery task
    request_id = str(uuid.uuid4())
    task = prime_task.delay(n, request_id)
    # Return Celery task ID as request_id for status checking
    return GenerateResponse(request_id=task.id)

@app.get("/status/{request_id}", response_model=StatusResponse)
async def get_status(request_id: str):
    task = celery_app.AsyncResult(request_id)
    
    if task.state == 'PENDING':
        return StatusResponse(status="pending")
    elif task.state == 'SUCCESS':
        return StatusResponse(status="complete", result=task.result)
    else:
        # For other states like 'FAILURE', 'RETRY', etc.
        return StatusResponse(status=task.state.lower())
