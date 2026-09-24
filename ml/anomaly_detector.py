from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies():

    # =====================================================
    # 1. FIND PROJECT ROOT
    # =====================================================

    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    METRICS_FILE = (
        PROJECT_ROOT
        / "data"
        / "metric"
        / "metrics.csv"
    )


    # =====================================================
    # 2. CHECK FILE
    # =====================================================

    if not METRICS_FILE.exists():

        raise FileNotFoundError(
            f"Metrics file not found: {METRICS_FILE}"
        )


    # =====================================================
    # 3. LOAD DATA
    # =====================================================

    data = pd.read_csv(METRICS_FILE)


    # =====================================================
    # 4. SELECT FEATURES
    # =====================================================

    features = [
        "cpu_percent",
        "memory_percent",
        "request_count",
        "avg_latency_ms",
        "error_rate",
        "db_cpu_percent",
        "db_latency_ms"
    ]

    X = data[features]


    # =====================================================
    # 5. CREATE MODEL
    # =====================================================

    model = IsolationForest(
        contamination=0.30,
        random_state=42
    )


    # =====================================================
    # 6. TRAIN MODEL
    # =====================================================

    model.fit(X)


    # =====================================================
    # 7. PREDICT
    # =====================================================

    data["anomaly"] = model.predict(X)


    # =====================================================
    # 8. CALCULATE ANOMALY SCORE
    # =====================================================

    data["anomaly_score"] = model.decision_function(X)


    # =====================================================
    # 9. CREATE STATUS
    # =====================================================

    data["status"] = data["anomaly"].map({
        1: "NORMAL",
        -1: "ANOMALY"
    })


    # =====================================================
    # 10. GET ONLY ANOMALIES
    # =====================================================

    anomalies = data[
        data["status"] == "ANOMALY"
    ].copy()


    # =====================================================
    # 11. RETURN RESULT TO AGENT
    # =====================================================

    return {
        "data": data,
        "anomalies": anomalies
    }


# =========================================================
# TEST THE ML MODULE DIRECTLY
# =========================================================

if __name__ == "__main__":

    result = detect_anomalies()

    data = result["data"]
    anomalies = result["anomalies"]

    print("\n========================================")
    print("       AEGISAI ML ANOMALY DETECTION")
    print("========================================\n")

    print(
        data[
            [
                "timestamp",
                "service",
                "avg_latency_ms",
                "error_rate",
                "db_cpu_percent",
                "db_latency_ms",
                "anomaly_score",
                "status"
            ]
        ].to_string(index=False)
    )

    print("\n========================================")
    print("          DETECTED ANOMALIES")
    print("========================================\n")

    print(
        anomalies[
            [
                "timestamp",
                "service",
                "cpu_percent",
                "avg_latency_ms",
                "error_rate",
                "db_cpu_percent",
                "db_latency_ms",
                "anomaly_score"
            ]
        ].to_string(index=False)
    )

    print("\n========================================")
    print("Total observations:", len(data))
    print("Anomalies detected:", len(anomalies))
    print("========================================")