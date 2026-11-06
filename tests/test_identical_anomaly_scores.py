import joblib
import numpy as np
import pandas as pd

FEATURES = [
    "message_count",
    "avg_interval_ms",
    "unique_can_ids",
    "unique_payloads",
    "payload_entropy",
]

def test_saved_model_produces_nonconstant_scores():
    model = joblib.load("can_model.joblib")
    df = pd.read_csv("results/balanced_traffic_features.csv")
    X = df[FEATURES]

    scores = model.decision_function(X)

    assert len(scores) == len(df)
    assert np.isfinite(scores).all()
    assert pd.Series(scores).round(8).nunique() > 1
    assert set(model.predict(X)) == {"NORMAL", "ANOMALY"}
