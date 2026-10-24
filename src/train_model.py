import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

DATA_FILE = "can_features.csv"
MODEL_FILE = "can_model.joblib"

df = pd.read_csv(DATA_FILE)

features = [
    "message_count",
    "avg_interval_ms",
    "unique_payloads",
    "payload_entropy",
]

if len(df) < 10:
    raise ValueError(
        "Training data is very low. "
        "First collect more traffic samples."
    )

X = df[features].apply(pd.to_numeric, errors="raise")

model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42,
)

model.fit(X)
joblib.dump(model, MODEL_FILE)

print(f"Model trained on {len(X)} samples.")
print(f"Model saved to {MODEL_FILE}")
