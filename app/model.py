"""Model loading and inference helpers."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.schema import TicketRequest

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = REPO_ROOT / "ml" / "artifacts" / "v2_logistic_regression.joblib"
SUPPORTED_LABELS = ("urgent", "high", "normal", "low")


class ModelUnavailableError(RuntimeError):
    """Raised when the configured production model cannot be loaded."""


def _ticket_frame(ticket: TicketRequest) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "text": [ticket.text],
            "customer_tier": [ticket.customer_tier],
            "monthly_revenue": [ticket.monthly_revenue],
        }
    )


class ModelService:
    """Lazy-loading wrapper around the serialized scikit-learn pipeline."""

    def __init__(self, model_path: str | Path = DEFAULT_MODEL_PATH) -> None:
        self.model_path = Path(model_path)

    @cached_property
    def bundle(self) -> dict[str, Any]:
        if not self.model_path.is_file():
            raise ModelUnavailableError(f"Model file not found: {self.model_path}")

        loaded = joblib.load(self.model_path)
        if not isinstance(loaded, dict) or "pipeline" not in loaded or "metadata" not in loaded:
            raise ModelUnavailableError("Model bundle must contain 'pipeline' and 'metadata'")

        metadata = loaded["metadata"]
        if not isinstance(metadata, dict) or not {"version", "dataset_md5"}.issubset(metadata):
            raise ModelUnavailableError("Model metadata is incomplete")
        return loaded

    def predict(self, ticket: TicketRequest) -> dict[str, Any]:
        pipeline = self.bundle["pipeline"]
        metadata = self.bundle["metadata"]

        probabilities = pipeline.predict_proba(_ticket_frame(ticket))[0]
        classes = [str(label) for label in pipeline.classes_]
        ranked = sorted(
            zip(classes, probabilities, strict=True), key=lambda pair: pair[1], reverse=True
        )
        priority, confidence = ranked[0]

        if priority not in SUPPORTED_LABELS:
            raise ModelUnavailableError(f"Model returned unsupported priority: {priority}")

        return {
            "priority": priority,
            "confidence": float(confidence),
            "probabilities": {label: float(score) for label, score in ranked},
            "model_version": str(metadata["version"]),
        }
