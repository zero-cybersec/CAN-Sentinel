def sequence_match_ratio(window):
    sequence = (
        window["can_id"].astype(str) + "|" +
        window["data"].astype(str)
    ).tolist()

    comparisons = len(sequence) - 3
    if comparisons <= 0:
        return 0.0

    matches = sum(
        sequence[i] == sequence[i - 3]
        for i in range(3, len(sequence))
    )
    return matches / comparisons


def hybrid_prediction(rate_label, sequence_label, ml_label):
    if rate_label == "HIGH_RATE_SUSPECTED":
        return "HIGH_RATE_SUSPECTED"
    if sequence_label == "REPLAY_SUSPECTED":
        return "REPLAY_SUSPECTED"
    return ml_label
