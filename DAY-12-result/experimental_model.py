from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parent

FEATURES = [
    "message_count",
    "avg_interval_ms",
    "unique_payloads",
    "payload_entropy",
]

FEATURE_FILE = ROOT / "can_features.csv"
EXPERIMENTAL_MODEL_FILE = ROOT / "experimental_can_model.joblib"
EXPERIMENTAL_RESULTS_FILE = ROOT / "results" / "experimental_ml_predictions.csv"

REFERENCE_MODEL_FILE = ROOT / "can_model.joblib"
REFERENCE_RESULTS_FILE = ROOT / "model_test_results.csv"

EXPERIMENTAL_CONFIG = {
    "n_estimators": 200,
    "contamination": 0.01,
    "random_state": 42,
}

TRAIN_LABEL_PATTERN = "normal"


def load_features(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and validate a can_features.csv-format file.

    Raises ValueError with a clear message for missing feature columns,
    non-numeric feature values, or NaNs. Returns (raw_df, numeric_X).
    """
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"{path}: file has no feature rows.")
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"{path}: missing required feature columns: {missing}")
    X = df[FEATURES].apply(pd.to_numeric, errors="raise")
    if X.isna().any().any():
        bad = X.columns[X.isna().any()].tolist()
        raise ValueError(f"{path}: feature columns contain NaN values: {bad}")
    return df, X


def training_subset(df: pd.DataFrame) -> pd.DataFrame:
    """Rows the model is fitted on: clean/normal traffic only, matching
    the reference workflow's 'train on clean traffic only' protocol."""
    if "label" not in df.columns:
        return df
    mask = df["label"].astype(str).str.lower().str.contains(TRAIN_LABEL_PATTERN)
    subset = df[mask]
    if subset.empty:
        raise ValueError("No training rows found (no normal-labeled windows).")
    return subset


def train_experimental(X: pd.DataFrame) -> IsolationForest:
    """Fit the experimental IsolationForest (does not touch any file)."""
    model = IsolationForest(**EXPERIMENTAL_CONFIG)
    model.fit(X)
    return model


def score(model, df: pd.DataFrame) -> pd.DataFrame:
    """Score a feature frame in the same shape as test_model.py output."""
    X = df[FEATURES].apply(pd.to_numeric, errors="raise")
    out = df.copy()
    out["prediction"] = ["NORMAL" if p == 1 else "ANOMALY" for p in model.predict(X)]
    out["anomaly_score"] = model.decision_function(X)
    return out


def add_reference_scores(scored: pd.DataFrame) -> pd.DataFrame:
    """Attach the reference model's prediction/score for comparison, if
    can_model.joblib is available. The reference model is only read,
    never retrained or overwritten."""
    if not REFERENCE_MODEL_FILE.exists():
        return scored
    out = scored.copy()
    ref = joblib.load(REFERENCE_MODEL_FILE)
    X = out[FEATURES].apply(pd.to_numeric, errors="raise")
    out["reference_prediction"] = [
        "NORMAL" if p == 1 else "ANOMALY" for p in ref.predict(X)
    ]
    out["reference_anomaly_score"] = ref.decision_function(X)
    return out


def run(
    features_path: Path = FEATURE_FILE,
    model_path: Path = EXPERIMENTAL_MODEL_FILE,
    output_path: Path = EXPERIMENTAL_RESULTS_FILE,
    retrain: bool = True,
) -> pd.DataFrame:
    """Train (or load) the experimental model, score the feature file and
    write the results CSV. Returns the scored frame."""
    df, X = load_features(features_path)
    if retrain or not Path(model_path).exists():
        train_df = training_subset(df)
        model = train_experimental(train_df[FEATURES])
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
    else:
        model = joblib.load(model_path)
    scored = score(model, df)
    scored = add_reference_scores(scored)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_path, index=False)
    return scored


def main() -> None:
    scored = run()
    print(f"Experimental model: IsolationForest({EXPERIMENTAL_CONFIG})")
    print(f"Trained on clean/normal windows only, scored {len(scored)} rows.")
    if "label" in scored.columns:
        summary = scored.groupby("label")["prediction"].value_counts()
        print(summary.to_string())
    if "reference_prediction" in scored.columns:
        diff = (scored["prediction"] != scored["reference_prediction"]).sum()
        print(f"Rows where experimental != reference prediction: {diff}")
    print("Reference artifacts untouched: can_model.joblib, model_test_results.csv")


if __name__ == "__main__":
    main()
