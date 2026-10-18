"""FastAPI entrypoint for ticket priority inference."""

import os
from typing import Any

from fastapi import FastAPI, HTTPException

from app.model import DEFAULT_MODEL_PATH, ModelService, ModelUnavailableError
from app.schema import PredictionResponse, TicketRequest

model_service = ModelService(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH)))

app = FastAPI(
    title="Student Ticket Triage API",
    version="1.0.0",
    description="A small class project that predicts support-ticket priority.",
)


@app.get("/")
def home() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health")
def health() -> dict[str, Any]:
    try:
        version = model_service.bundle["metadata"]["version"]
    except ModelUnavailableError:
        return {"status": "error", "model_loaded": False}

    return {"status": "ok", "model_loaded": True, "model_version": version}


@app.post("/triage", response_model=PredictionResponse)
def triage(ticket: TicketRequest) -> dict[str, Any]:
    try:
        return model_service.predict(ticket)
    except ModelUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
