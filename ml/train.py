"""Train and log a ticket priority classifier with MLflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import mlflow
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

from ml.data_pipeline import LABELS, build_model, validate_training_frame

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = REPO_ROOT / "ml" / "artifacts"
MLFLOW_DIR = (
    Path(os.environ["MLFLOW_TRACKING_DIR"])
    if "MLFLOW_TRACKING_DIR" in os.environ
    else REPO_ROOT / "mlruns"
)


def git_commit() -> str:
    git = shutil.which("git")
    if git is None:
        return "unknown"
    try:
        result = subprocess.run(  # noqa: S603 - resolved absolute path
            [git, "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip()


def dataset_identity(dataset_path: Path) -> str:
    """Return DVC MD5 when available, or a stable SHA256 fallback."""
    pointer_path = dataset_path.with_name(f"{dataset_path.name}.dvc")
    if pointer_path.is_file():
        match = re.search(r"md5: ([0-9a-f]{32})", pointer_path.read_text(encoding="utf-8"))
        if match:
            return match.group(1)

    return hashlib.sha256(dataset_path.read_bytes()).hexdigest()


def load_config(config_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    required = {
        "experiment_name",
        "dataset_path",
        "dataset_version",
        "test_size",
        "random_state",
        "model_params",
    }
    missing = required - config.keys()
    if missing:
        raise ValueError(f"Config is missing keys: {sorted(missing)}")
    return config


def train(config_path: Path, quiet: bool = False) -> dict[str, Any]:
    config = load_config(config_path)
    dataset_path = REPO_ROOT / config["dataset_path"]
    frame = pd.read_csv(dataset_path)
    validate_training_frame(frame)

    features = frame[["text", "customer_tier", "monthly_revenue"]]
    target = frame["priority"]
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=float(config["test_size"]),
        random_state=int(config["random_state"]),
        stratify=target,
    )

    pipeline = build_model(config["model_params"])
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)

    report = classification_report(
        y_test, predictions, labels=LABELS, zero_division=0, output_dict=True
    )
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "macro_f1": float(
            f1_score(y_test, predictions, labels=LABELS, average="macro", zero_division=0)
        ),
        "weighted_f1": float(
            f1_score(y_test, predictions, labels=LABELS, average="weighted", zero_division=0)
        ),
    }

    experiment_name = str(config["experiment_name"])
    dataset_md5 = dataset_identity(dataset_path)
    commit = git_commit()
    model_path = ARTIFACT_DIR / f"{config['dataset_version']}_logistic_regression.joblib"
    metrics_path = ARTIFACT_DIR / f"{config['dataset_version']}_metrics.json"
    confusion_path = ARTIFACT_DIR / f"{config['dataset_version']}_confusion_matrix.csv"
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    metadata: dict[str, Any] = {
        "version": config["dataset_version"],
        "experiment_name": experiment_name,
        "git_commit": commit,
        "dataset_md5": dataset_md5,
        "trained_at_utc": datetime.now(UTC).isoformat(),
        "feature_columns": ["text", "customer_tier", "monthly_revenue"],
        "test_metrics": metrics,
    }
    joblib.dump({"pipeline": pipeline, "metadata": metadata}, model_path)
    metrics_path.write_text(
        json.dumps({"metrics": metrics, "report": report}, indent=2), encoding="utf-8"
    )

    matrix = confusion_matrix(y_test, predictions, labels=LABELS)
    pd.DataFrame(matrix, index=LABELS, columns=LABELS).to_csv(confusion_path, index_label="actual")

    # MLflow 3.17 requires an explicit opt-in for its assignment-friendly local file backend.
    os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")
    mlflow.set_tracking_uri(MLFLOW_DIR.resolve().as_uri())
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run(run_name=f"{config['dataset_version']}-{commit[:8]}"):
        mlflow.set_tags(
            {
                "stage": "development",
                "dataset_version": config["dataset_version"],
                "project": "ticket-triage",
            }
        )
        mlflow.log_params(
            {
                "git_commit": commit,
                "dataset_version": config["dataset_version"],
                "dataset_md5": dataset_md5,
                "dataset_rows": len(frame),
                "test_size": config["test_size"],
                "random_state": config["random_state"],
                **config["model_params"],
            }
        )
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(model_path), artifact_path="model")
        mlflow.log_artifact(str(metrics_path), artifact_path="metrics")
        mlflow.log_artifact(str(confusion_path), artifact_path="plots")

    if not quiet:
        print(json.dumps({"model": str(model_path), "metadata": metadata}, indent=2))

    return {"metadata": metadata, "model_path": model_path}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "ml" / "configs" / "improved.json",
        help="Path to a JSON training config.",
    )
    args = parser.parse_args()
    train(args.config)


if __name__ == "__main__":
    main()
