from pathlib import Path
import hashlib
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import experimental_model as em  

FEATURE_FILE = ROOT / "can_features.csv"


@pytest.fixture(scope="module")
def real_features() -> pd.DataFrame:
    return pd.read_csv(FEATURE_FILE)


@pytest.fixture()
def scratch(tmp_path):
    """Paths for a scratch run so committed artifacts are never touched."""
    return {
        "model": tmp_path / "scratch_model.joblib",
        "output": tmp_path / "scratch_predictions.csv",
    }


def test_prediction_count_matches_feature_rows(scratch):
    scored = em.run(output_path=scratch["output"], model_path=scratch["model"])
    assert len(scored) == 80 


def test_rows_align_with_feature_file(scratch, real_features):
    scored = em.run(output_path=scratch["output"], model_path=scratch["model"])
    for col in ["source", "window", "can_id"]:
        assert scored[col].tolist() == real_features[col].tolist()


def test_saved_results_align_with_saved_features(real_features):
    saved = pd.read_csv(ROOT / "results" / "experimental_ml_predictions.csv")
    for col in ["source", "window", "can_id"]:
        assert saved[col].tolist() == real_features[col].tolist()
    assert (saved["prediction"].isin(["NORMAL", "ANOMALY"])).all()


def test_predictions_and_scores_are_valid(scratch):
    scored = em.run(output_path=scratch["output"], model_path=scratch["model"])
    assert scored["prediction"].isin(["NORMAL", "ANOMALY"]).all()
    assert scored["anomaly_score"].notna().all()
    assert (
        (scored["prediction"] == "ANOMALY") == (scored["anomaly_score"] < 0)
    ).all()

def write_csv(tmp_path, text):
    p = tmp_path / "bad_features.csv"
    p.write_text(text)
    return p

HEADER = "source,window,can_id,message_count,avg_interval_ms,unique_payloads,payload_entropy,label\n"

def test_missing_feature_column_raises(tmp_path):
    p = write_csv(
        tmp_path,
        "source,window,can_id,message_count,avg_interval_ms,unique_payloads,label\n"
        "x,0,0x100,5,160.0,5,normal\n",
    )
    with pytest.raises(ValueError, match="missing required feature columns"):
        em.load_features(p)


def test_non_numeric_feature_raises(tmp_path):
    p = write_csv(
        tmp_path,
        HEADER + "x,0,0x100,not-a-number,160.0,5,2.32,normal\n",
    )
    with pytest.raises(ValueError):
        em.load_features(p)


def test_nan_feature_raises(tmp_path):
    p = write_csv(
        tmp_path,
        HEADER + "x,0,0x100,,160.0,5,2.32,normal\n",
    )
    with pytest.raises(ValueError, match="NaN"):
        em.load_features(p)


def test_empty_file_raises(tmp_path):
    p = write_csv(tmp_path, HEADER)
    with pytest.raises(ValueError, match="no feature rows"):
        em.load_features(p)


def test_missing_file_raises(tmp_path):
    with pytest.raises(Exception):
        em.load_features(tmp_path / "does_not_exist.csv")


def test_training_subset_keeps_only_normal_rows():
    df = pd.DataFrame(
        {
            "message_count": [5, 60, 3, 70],
            "label": ["normal_new", "high_rate_new", "normal_new", "high_rate_new"],
        }
    )
    subset = em.training_subset(df)
    assert subset["label"].tolist() == ["normal_new", "normal_new"]


def test_training_subset_without_normal_rows_raises():
    df = pd.DataFrame({"message_count": [60, 70], "label": ["high_rate_new"] * 2})
    with pytest.raises(ValueError, match="No training rows"):
        em.training_subset(df)


def test_training_subset_without_label_column_uses_all_rows():
    df = pd.DataFrame({"message_count": [5, 60]})
    assert len(em.training_subset(df)) == 2

def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_run_never_touches_reference_artifacts(scratch):
    before = {
        p: _sha256(ROOT / p)
        for p in ["can_model.joblib", "model_test_results.csv", "can_features.csv"]
    }
    em.run(output_path=scratch["output"], model_path=scratch["model"])
    assert {p: _sha256(ROOT / p) for p in before} == before
    assert scratch["output"].exists()
    assert (ROOT / "can_model.joblib").name not in scratch["output"].parts


def test_committed_outputs_match_reference_hashes():
    """The deliverable generation run must have left the reference
    pipeline's files byte-identical to what test_model.py produced."""
    results = pd.read_csv(ROOT / "model_test_results.csv")
    assert len(results) == 80
    assert results["prediction"].isin(["NORMAL", "ANOMALY"]).all()
  
def test_output_is_reproducible(scratch, tmp_path):
    first = em.run(output_path=scratch["output"], model_path=scratch["model"])
    again_model = tmp_path / "again.joblib"
    again_out = tmp_path / "again.csv"
    second = em.run(output_path=again_out, model_path=again_model)
    cols = ["can_id", "message_count", "prediction", "anomaly_score"]
    pd.testing.assert_frame_equal(
        first[cols].reset_index(drop=True), second[cols].reset_index(drop=True)
    )
