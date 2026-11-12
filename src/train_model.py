import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from integration_test import extract_features, FEATURES, RESULTS_DIR

normal_path = RESULTS_DIR / "normal_traffic.csv"
attack_path = RESULTS_DIR / "high_rate_traffic.csv"

normal = pd.DataFrame(extract_features(normal_path))
attack = pd.DataFrame(extract_features(attack_path))

normal["label"] = "NORMAL"
attack["label"] = "ANOMALY"

data = pd.concat([normal, attack], ignore_index=True)

X = data[FEATURES].apply(pd.to_numeric, errors="raise")
y = data["label"]

if len(data) < 20 or y.nunique() != 2:
    raise ValueError("Insufficient training windows or missing class.")

model = Pipeline([
    ("standardscaler", StandardScaler()),
    ("svc", SVC(
        kernel="rbf",
        gamma="scale",
        class_weight="balanced"
    ))
])

model.fit(X, y)
joblib.dump(model, "can_model.joblib")

print("Model trained and saved to can_model.joblib")
print("Training windows:", len(data))
print("Class distribution:", y.value_counts().to_dict())
print("Training predictions:", pd.Series(model.predict(X)).value_counts().to_dict())
