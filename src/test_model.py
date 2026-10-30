import pandas as pd
import joblib
from integration_test import extract_features, FEATURES, RESULTS_DIR

model = joblib.load("can_model.joblib")
rows = []

for filename, expected in [
    ("normal_traffic.csv", "NORMAL"),
    ("high_rate_traffic.csv", "ANOMALY"),
]:
    df = pd.DataFrame(extract_features(RESULTS_DIR / filename))
    X = df[FEATURES]
    predictions = model.predict(X)
    scores = model.decision_function(X)

    for i, prediction in enumerate(predictions):
        rows.append({
            "source_file": filename,
            "expected": expected,
            "prediction": prediction,
            "anomaly_score": scores[i],
        })

results = pd.DataFrame(rows)
results.to_csv("model_test_results.csv", index=False)

print(results.groupby(["source_file", "expected", "prediction"]).size())
print("Unique scores:", results["anomaly_score"].round(8).nunique())
print("Results saved to model_test_results.csv")
