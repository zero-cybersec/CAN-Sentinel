
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, accuracy_score


# ==============================================================================
# 1. FEATURE EXTRACTION PIPELINE
# ==============================================================================

def extract_can_window_features(
    df_raw: pd.DataFrame, 
    source_name: str, 
    ground_truth_label: str,
    window_sec: float = 1.0
) -> pd.DataFrame:
    """
    Transforms raw packet-level CAN logs into 1-second window feature vectors per CAN ID.
    """
    df = df_raw.copy()
    t_start = df['timestamp_s'].min()
    df['window'] = np.floor((df['timestamp_s'] - t_start) / window_sec).astype(int)
    
    unique_ids = sorted(df['can_id'].unique())
    unique_windows = range(df['window'].min(), df['window'].max() + 1)
    
    grouped = df.groupby(['window', 'can_id'])
    records = []
    
    for win in unique_windows:
        for cid in unique_ids:
            if (win, cid) in grouped.groups:
                grp = grouped.get_group((win, cid))
                count = len(grp)
                
                # Inter-arrival intervals in milliseconds
                if count > 1:
                    intervals_ms = grp['timestamp_s'].diff().dropna() * 1000.0
                    avg_int_ms = intervals_ms.mean()
                else:
                    avg_int_ms = window_sec * 1000.0
                
                # Payload diversity and Shannon entropy: H(X) = -sum(p * log2(p))
                unique_p = grp['data'].nunique()
                probs = grp['data'].value_counts() / count
                entropy = -np.sum(probs * np.log2(probs)) if count > 0 else 0.0
            else:
                # Inactive / starved CAN ID in this window
                count = 0
                avg_int_ms = window_sec * 1000.0
                unique_p = 0
                entropy = 0.0
                
            records.append({
                'source': source_name,
                'window': int(win),
                'can_id': cid,
                'message_count': int(count),
                'avg_interval_ms': round(float(avg_int_ms), 3),
                'unique_payloads': int(unique_p),
                'payload_entropy': round(float(entropy), 4),
                'label': ground_truth_label
            })
            
    return pd.DataFrame(records)


# ==============================================================================
# 2. MODEL TRAINING & SCORING
# ==============================================================================

def train_isolation_forest(
    train_features_df: pd.DataFrame, 
    feature_cols: list,
    contamination: float = 0.05,
    random_state: int = 42
) -> IsolationForest:
    """
    Fits an Isolation Forest anomaly detector on nominal training features.
    """
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=random_state
    )
    model.fit(train_features_df[feature_cols])
    return model


def predict_anomalies(
    model: IsolationForest, 
    features_df: pd.DataFrame, 
    feature_cols: list
) -> pd.DataFrame:
    """
    Scores feature vectors and outputs continuous anomaly scores and labels.
    - decision_function >= 0 -> NORMAL (inlier)
    - decision_function < 0  -> ANOMALY (outlier)
    """
    df = features_df.copy()
    scores = model.decision_function(df[feature_cols])
    preds_raw = model.predict(df[feature_cols])
    
    df['anomaly_score'] = scores
    df['prediction'] = np.where(preds_raw == -1, 'ANOMALY', 'NORMAL')
    return df


# ==============================================================================
# 3. EVALUATION METRICS & SCORE SEPARATION
# ==============================================================================

def evaluate_performance(df_results: pd.DataFrame) -> dict:
    """
    Calculates confusion matrices, latency, and score separation statistics.
    """
    y_true = np.where(df_results['label'] == 'high_rate', 1, 0)
    y_pred = np.where(df_results['prediction'] == 'ANOMALY', 1, 0)
    
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    precision = precision_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    acc = accuracy_score(y_true, y_pred)
    
    normal_scores = df_results[df_results['label'] == 'normal']['anomaly_score']
    attack_scores = df_results[df_results['label'] == 'high_rate']['anomaly_score']
    
    # Delta_s: separation gap between lowest normal score and highest attack score
    delta_s = normal_scores.min() - attack_scores.max()
    
    # Per-CAN ID metrics breakdown
    per_id_metrics = {}
    for cid, grp in df_results.groupby('can_id'):
        yt_sub = np.where(grp['label'] == 'high_rate', 1, 0)
        yp_sub = np.where(grp['prediction'] == 'ANOMALY', 1, 0)
        c_tn, c_fp, c_fn, c_tp = confusion_matrix(yt_sub, yp_sub, labels=[0, 1]).ravel()
        
        cid_normal = grp[grp['label'] == 'normal']['anomaly_score']
        cid_attack = grp[grp['label'] == 'high_rate']['anomaly_score']
        
        per_id_metrics[cid] = {
            'TP': int(c_tp), 'FP': int(c_fp), 'TN': int(c_tn), 'FN': int(c_fn),
            'Recall (TPR)': round(c_tp / (c_tp + c_fn) if (c_tp + c_fn) > 0 else 0.0, 4),
            'FPR': round(c_fp / (c_fp + c_tn) if (c_fp + c_tn) > 0 else 0.0, 4),
            'Precision': round(c_tp / (c_tp + c_fp) if (c_tp + c_fp) > 0 else 0.0, 4),
            'Mean Score (Normal)': round(float(cid_normal.mean()), 4) if len(cid_normal) else None,
            'Mean Score (Attack)': round(float(cid_attack.mean()), 4) if len(cid_attack) else None,
            'Separation Delta': round(float(cid_normal.min() - cid_attack.max()), 4) if (len(cid_normal) and len(cid_attack)) else None
        }
        
    # Detection Latency (window index of first confirmed attack alert)
    attack_windows = df_results[(df_results['label'] == 'high_rate') & (df_results['prediction'] == 'ANOMALY')]
    first_detected_window = attack_windows['window'].min() if len(attack_windows) > 0 else None
    
    return {
        'Global Metrics': {
            'TP': int(tp), 'FP': int(fp), 'TN': int(tn), 'FN': int(fn),
            'Detection Rate (Recall / TPR)': round(tpr, 4),
            'False Positive Rate (FPR)': round(fpr, 4),
            'Precision': round(precision, 4),
            'F1-Score': round(f1, 4),
            'Accuracy': round(acc, 4),
            'Min Normal Score': round(float(normal_scores.min()), 5),
            'Max Attack Score': round(float(attack_scores.max()), 5),
            'Separation Margin (Delta_s)': round(float(delta_s), 5),
            'First Detected Window Index': int(first_detected_window) if first_detected_window is not None else None,
            'Detection Latency Bound': f"<= {int(first_detected_window + 1) * 1000} ms" if first_detected_window is not None else "N/A"
        },
        'Per-CAN ID Metrics': per_id_metrics
    }


# ==============================================================================
# 4. EXECUTION DRIVER
# ==============================================================================

def run_evaluation(
    normal_csv_path: str, 
    high_rate_csv_path: str, 
    output_results_path: str = "evaluated_model_results.csv"
):
    print("=" * 70)
    print("CAN-SENTINEL: STARTING EVALUATION PIPELINE")
    print("=" * 70)
    
    # 1. Load raw datasets
    raw_normal = pd.read_csv(normal_csv_path)
    raw_high_rate = pd.read_csv(high_rate_csv_path)
    
    # 2. Extract window features
    print("[*] Extracting window features (1.0s window per CAN ID)...")
    feat_normal = extract_can_window_features(raw_normal, source_name="normal_traffic", ground_truth_label="normal")
    feat_high_rate = extract_can_window_features(raw_high_rate, source_name="high_rate_traffic", ground_truth_label="high_rate")
    
    feature_cols = ['message_count', 'avg_interval_ms', 'unique_payloads', 'payload_entropy']
    
    # 3. Train model on baseline
    print("[*] Fitting Isolation Forest on nominal baseline...")
    model = train_isolation_forest(feat_normal, feature_cols, contamination=0.05, random_state=42)
    
    # 4. Inference
    print("[*] Scoring normal traffic...")
    scored_normal = predict_anomalies(model, feat_normal, feature_cols)
    print("[*] Scoring high-rate traffic...")
    scored_high_rate = predict_anomalies(model, feat_high_rate, feature_cols)
    
    all_results = pd.concat([scored_normal, scored_high_rate], ignore_index=True)
    
    # 5. Evaluate
    metrics = evaluate_performance(all_results)
    
    print("\n" + "=" * 70)
    print("EVALUATION RESULTS & SCORECARD")
    print("=" * 70)
    for k, v in metrics['Global Metrics'].items():
        print(f"  {k:30s}: {v}")
        
    print("\n" + "-" * 70)
    print("PER-CAN ID PERFORMANCE:")
    print("-" * 70)
    df_per_id = pd.DataFrame(metrics['Per-CAN ID Metrics']).T
    print(df_per_id.to_string())
    
    # 6. Save results matching schema
    all_results.to_csv(output_results_path, index=False)
    print(f"\n[+] Standardized predictions saved to: {output_results_path}")
    print("=" * 70)
    
    return all_results, metrics


if __name__ == '__main__':
    run_evaluation(
        normal_csv_path="normal_traffic.csv",
        high_rate_csv_path="high_rate_traffic.csv",
        output_results_path="evaluated_model_results.csv"
    )
