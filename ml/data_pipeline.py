"""Shared ML preprocessing and model construction."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TEXT_COLUMN = "text"
CATEGORICAL_COLUMNS = ["customer_tier"]
NUMERIC_COLUMNS = ["monthly_revenue"]
LABELS = ["urgent", "high", "normal", "low"]


def build_preprocessor() -> ColumnTransformer:
    """Create the deterministic feature transformation used for training and serving."""
    return ColumnTransformer(
        transformers=[
            (
                "text_tfidf",
                TfidfVectorizer(
                    strip_accents="unicode",
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=1,
                    sublinear_tf=True,
                ),
                TEXT_COLUMN,
            ),
            (
                "tier_onehot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=True),
                CATEGORICAL_COLUMNS,
            ),
            (
                "economics_scaled",
                StandardScaler(),
                NUMERIC_COLUMNS,
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )


def build_model(params: dict[str, Any] | None = None) -> Pipeline:
    """Create a configurable logistic-regression classifier pipeline."""
    model_params = {
        "C": 2.0,
        "max_iter": 1000,
        "class_weight": None,
        "random_state": 42,
    }
    model_params.update(params or {})
    return Pipeline(
        [
            ("features", build_preprocessor()),
            (
                "classifier",
                LogisticRegression(
                    C=float(model_params["C"]),
                    max_iter=int(model_params["max_iter"]),
                    class_weight=model_params["class_weight"],
                    random_state=int(model_params["random_state"]),
                ),
            ),
        ]
    )


def validate_training_frame(frame: pd.DataFrame) -> None:
    """Fail early when a training dataset does not match the serving contract."""
    required = {TEXT_COLUMN, *CATEGORICAL_COLUMNS, *NUMERIC_COLUMNS, "priority"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Training data is missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Training data must not be empty")
    if frame[list(required)].isna().any().any():
        raise ValueError("Training data contains missing values")
    unexpected = set(frame["priority"].unique()) - set(LABELS)
    if unexpected:
        raise ValueError(f"Unexpected priority labels: {sorted(unexpected)}")
