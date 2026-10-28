from pathlib import Path
import os
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_DIR / "results"
MODEL_FILE = PROJECT_DIR / "can_model.joblib"

REQUIRED_INPUTS = [
    RESULTS_DIR / "normal_traffic.csv",
    RESULTS_DIR / "high_rate_traffic.csv",
]

REQUIRED_COLUMNS = {"timestamp_s", "can_id", "data"}


def check_file(path, label):
    if not path.is_file():
        return False, f"FAIL: {label} not found: {path.name}"
    return True, f"PASS: {label} found: {path.name}"


def check_csv(path):
    if not path.is_file():
        return False, f"FAIL: Input CSV missing: {path.name}"

    try:
        columns = set(pd.read_csv(path, nrows=0).columns)
    except Exception as exc:
        return False, f"FAIL: Cannot read {path.name}: {exc}"

    missing = REQUIRED_COLUMNS - columns
    if missing:
        return False, (
            f"FAIL: {path.name} missing required columns: "
            + ", ".join(sorted(missing))
        )

    return True, f"PASS: CSV headers valid: {path.name}"


def check_results_directory():
    if not RESULTS_DIR.is_dir():
        return False, f"FAIL: Results directory missing: {RESULTS_DIR}"

    if not os.access(RESULTS_DIR, os.W_OK):
        return False, "FAIL: Results directory is not writable"

    return True, "PASS: Results directory exists and is writable"


def run_checks():
    checks = []

    for path in REQUIRED_INPUTS:
        checks.append(check_csv(path))

    checks.append(check_file(MODEL_FILE, "Model"))
    checks.append(check_results_directory())

    print("CAN-Sentinel Pipeline Preflight")
    print("=" * 32)

    for passed, message in checks:
        print(message)

    failed = sum(not passed for passed, _ in checks)
    print(f"\nSummary: {len(checks) - failed}/{len(checks)} checks passed")

    return failed == 0


if __name__ == "__main__":
    raise SystemExit(0 if run_checks() else 1)
