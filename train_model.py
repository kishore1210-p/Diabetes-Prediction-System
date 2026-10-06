"""Train, compare, and persist diabetes prediction models.

Run from the project root:
    python train_model.py
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from preprocess import (
    DEFAULT_DATASET_PATH,
    FEATURE_COLUMNS,
    PROJECT_ROOT,
    TARGET_COLUMN,
    build_preprocessor,
    load_clean_dataset,
    read_dataset,
)


RANDOM_STATE = 42


def model_catalogue() -> tuple[dict[str, BaseEstimator], list[dict[str, str]]]:
    """Create candidate classifiers and record intentionally skipped optional models."""
    models: dict[str, BaseEstimator] = {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            solver="liblinear",
            random_state=RANDOM_STATE,
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=12,
            min_samples_leaf=12,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=180,
            max_depth=18,
            min_samples_leaf=5,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }
    skipped: list[dict[str, str]] = []

    try:
        from xgboost import XGBClassifier

        models["XGBoost"] = XGBClassifier(
            n_estimators=240,
            max_depth=4,
            learning_rate=0.06,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    except ImportError:
        skipped.append(
            {
                "model": "XGBoost",
                "status": "Skipped",
                "reason": "Optional dependency xgboost is not installed.",
            }
        )
    return models, skipped


def evaluate(model: Pipeline, x_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float]:
    """Calculate classification metrics from a held-out test set."""
    predictions = model.predict(x_test)
    probabilities = model.predict_proba(x_test)[:, 1]
    return {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1_score": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
    }


def extract_feature_importance(model: Pipeline) -> list[dict[str, float | str]]:
    """Create a display-ready feature-importance list from the selected model."""
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]
    names = list(preprocessor.get_feature_names_out())

    if hasattr(classifier, "feature_importances_"):
        importance = np.asarray(classifier.feature_importances_, dtype=float)
    elif hasattr(classifier, "coef_"):
        coefficients = np.asarray(classifier.coef_, dtype=float)
        importance = np.abs(coefficients[0])
    else:
        return []

    feature_data = pd.DataFrame({"feature": names, "importance": importance})
    feature_data["feature"] = feature_data["feature"].str.replace("_", " ").str.title()
    feature_data = feature_data.sort_values("importance", ascending=False)
    return [
        {"feature": str(row.feature), "importance": float(row.importance)}
        for row in feature_data.itertuples(index=False)
    ]


def train(data_path: Path, output_dir: Path) -> dict[str, Any]:
    """Train all available models and persist the strongest ROC-AUC model."""
    raw = read_dataset(data_path)
    cleaned = load_clean_dataset(data_path)
    x = cleaned[FEATURE_COLUMNS]
    y = cleaned[TARGET_COLUMN]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.20,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    candidates, skipped_models = model_catalogue()
    comparison: list[dict[str, Any]] = []
    fitted_models: dict[str, Pipeline] = {}

    for name, classifier in candidates.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                ("classifier", classifier),
            ]
        )
        pipeline.fit(x_train, y_train)
        metrics = evaluate(pipeline, x_test, y_test)
        comparison.append({"model": name, "status": "Trained", **metrics})
        fitted_models[name] = pipeline
        print(f"{name:<20} ROC AUC: {metrics['roc_auc']:.4f} | F1: {metrics['f1_score']:.4f}")

    if not fitted_models:
        raise RuntimeError("No models were available to train.")

    best_row = max(comparison, key=lambda row: row["roc_auc"])
    best_name = str(best_row["model"])
    best_model = fitted_models[best_name]
    importance = extract_feature_importance(best_model)

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "diabetes_model.joblib"
    comparison_path = output_dir / "model_comparison.csv"
    importance_path = output_dir / "feature_importance.csv"
    metadata_path = output_dir / "model_metadata.json"

    training_summary = {
        "raw_rows": int(len(raw)),
        "clean_rows": int(len(cleaned)),
        "duplicates_removed": int(len(raw) - len(cleaned)),
        "feature_count": len(FEATURE_COLUMNS),
        "target_distribution": {
            "non_diabetic": int((y == 0).sum()),
            "diabetic": int((y == 1).sum()),
        },
        "test_rows": int(len(x_test)),
        "random_state": RANDOM_STATE,
    }
    metadata: dict[str, Any] = {
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_name": data_path.name,
        "training_summary": training_summary,
        "best_model": best_name,
        "best_metrics": {key: float(best_row[key]) for key in ("accuracy", "precision", "recall", "f1_score", "roc_auc")},
        "model_comparison": comparison,
        "skipped_models": skipped_models,
        "feature_importance": importance,
        "feature_columns": FEATURE_COLUMNS,
    }

    bundle = {"pipeline": best_model, "metadata": metadata}
    joblib.dump(bundle, model_path, compress=3)
    pd.DataFrame(comparison).to_csv(comparison_path, index=False)
    pd.DataFrame(importance).to_csv(importance_path, index=False)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"\nBest model: {best_name}")
    print(f"Saved model: {model_path}")
    print(f"Saved metadata: {metadata_path}")
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the diabetes risk prediction models.")
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to diabetes_prediction_dataset.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "model",
        help="Directory for joblib model and report files",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    train(arguments.data, arguments.output_dir)
