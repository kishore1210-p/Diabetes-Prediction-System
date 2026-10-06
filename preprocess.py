"""Dataset cleaning and feature preprocessing for diabetes risk prediction."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET_PATH = PROJECT_ROOT / "dataset" / "diabetes_prediction_dataset.csv"
TARGET_COLUMN = "diabetes"
FEATURE_COLUMNS = [
    "gender",
    "age",
    "hypertension",
    "heart_disease",
    "smoking_history",
    "bmi",
    "HbA1c_level",
    "blood_glucose_level",
]
CATEGORICAL_COLUMNS = ["gender", "smoking_history"]
NUMERIC_COLUMNS = [column for column in FEATURE_COLUMNS if column not in CATEGORICAL_COLUMNS]


def read_dataset(path: str | Path = DEFAULT_DATASET_PATH) -> pd.DataFrame:
    """Load the source CSV and check that its expected schema is present."""
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {dataset_path}. Place diabetes_prediction_dataset.csv in dataset/."
        )

    frame = pd.read_csv(dataset_path)
    required = set(FEATURE_COLUMNS + [TARGET_COLUMN])
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
    return frame


def clean_dataset(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned model-ready copy of the supplied diabetes dataset."""
    cleaned = frame.loc[:, FEATURE_COLUMNS + [TARGET_COLUMN]].copy()

    for column in NUMERIC_COLUMNS + [TARGET_COLUMN]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    for column in CATEGORICAL_COLUMNS:
        cleaned[column] = cleaned[column].astype("string").str.strip().replace({"": pd.NA})

    cleaned = cleaned.dropna(subset=[TARGET_COLUMN])
    cleaned[TARGET_COLUMN] = cleaned[TARGET_COLUMN].astype(int)
    invalid_targets = set(cleaned[TARGET_COLUMN].unique()).difference({0, 1})
    if invalid_targets:
        raise ValueError("The diabetes target must contain only binary values 0 and 1.")

    return cleaned.drop_duplicates().reset_index(drop=True)


def load_clean_dataset(path: str | Path = DEFAULT_DATASET_PATH) -> pd.DataFrame:
    """Load and clean the dataset in one operation."""
    return clean_dataset(read_dataset(path))


def build_preprocessor() -> ColumnTransformer:
    """Build a leakage-safe transformer for numeric and categorical patient inputs."""
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    encoder_parameters: dict[str, Any] = {"handle_unknown": "ignore"}
    if "sparse_output" in inspect.signature(OneHotEncoder).parameters:
        encoder_parameters["sparse_output"] = False
    else:  # Compatibility with older scikit-learn releases.
        encoder_parameters["sparse"] = False

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(**encoder_parameters)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_COLUMNS),
            ("categorical", categorical_pipeline, CATEGORICAL_COLUMNS),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def patient_frame(values: dict[str, Any]) -> pd.DataFrame:
    """Convert one set of form values into a correctly ordered input DataFrame."""
    missing = set(FEATURE_COLUMNS).difference(values)
    if missing:
        raise ValueError(f"Patient input is missing: {', '.join(sorted(missing))}")
    return pd.DataFrame([{column: values[column] for column in FEATURE_COLUMNS}])
