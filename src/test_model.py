import pandas as pd
import joblib

FEATURE_FILE = "can_features.csv"
MODEL_FILE = "can_model.joblib"

features = [
    "message_count",
    "avg_interval_ms",
    "unique_payloads",
    "payload_entropy",
]

df = pd.read_csv(FEATURE_FILE)
model = joblib.load(MODEL_FILE)

X = df[features]
predictions = model.predict(X)
scores = model.decision_function(X)

df["prediction"] = [
    "NORMAL" if p == 1 else "ANOMALY"
    for p in predictions
]
df["anomaly_score"] = scores

print(df[[
    "can_id",
    "message_count",
    "prediction",
    "anomaly_score",
]].to_string(index=False))

df.to_csv("model_test_results.csv", index=False)
print("\nResults saved to model_test_results.csv")
