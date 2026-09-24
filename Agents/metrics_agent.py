from pathlib import Path
import sys

# ---------------------------------------------------------
# Allow this file to access the project root
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.append(str(PROJECT_ROOT))


# ---------------------------------------------------------
# Import our ML detection function
# ---------------------------------------------------------

from ml.anomaly_detector import detect_anomalies


class MetricsAgent:

    def __init__(self):
        self.name = "MetricsAgent"
        self.role = "Analyze production metrics and detect abnormal behavior"

    def investigate(self):

        print("\n========================================")
        print("          METRICS AGENT")
        print("========================================\n")

        print(f"Agent: {self.name}")
        print(f"Role: {self.role}")

        # -------------------------------------------------
        # Run ML anomaly detection
        # -------------------------------------------------

        result = detect_anomalies()

        # -------------------------------------------------
        # Check whether anomalies exist
        # -------------------------------------------------

        anomalies = result["anomalies"]

        if anomalies.empty:

            print("\n✅ Metrics Agent:")
            print("No unusual production behavior detected.")

            return {
                "agent": self.name,
                "status": "NORMAL",
                "anomalies": []
            }

        # -------------------------------------------------
        # Build evidence
        # -------------------------------------------------

        evidence = []

        for _, row in anomalies.iterrows():

            evidence.append({
                "timestamp": row["timestamp"],
                "service": row["service"],
                "cpu_percent": row["cpu_percent"],
                "memory_percent": row["memory_percent"],
                "api_latency_ms": row["avg_latency_ms"],
                "error_rate": row["error_rate"],
                "db_cpu_percent": row["db_cpu_percent"],
                "db_latency_ms": row["db_latency_ms"],
                "anomaly_score": row["anomaly_score"]
            })

        # -------------------------------------------------
        # Print investigation result
        # -------------------------------------------------

        print("\n🚨 METRICS AGENT DETECTED ANOMALY")

        print(f"\nNumber of anomalies: {len(evidence)}")

        print("\nEvidence:")

        for item in evidence:

            print("\n----------------------------------------")

            print("Timestamp:", item["timestamp"])
            print("Service:", item["service"])

            print(
                "API Latency:",
                item["api_latency_ms"],
                "ms"
            )

            print(
                "Error Rate:",
                item["error_rate"],
                "%"
            )

            print(
                "DB CPU:",
                item["db_cpu_percent"],
                "%"
            )

            print(
                "DB Latency:",
                item["db_latency_ms"],
                "ms"
            )

            print(
                "Anomaly Score:",
                round(item["anomaly_score"], 4)
            )

        # -------------------------------------------------
        # Return structured information
        # -------------------------------------------------

        return {
            "agent": self.name,
            "status": "ANOMALY_DETECTED",
            "anomaly_count": len(evidence),
            "evidence": evidence
        }


# ---------------------------------------------------------
# Run agent directly
# ---------------------------------------------------------

if __name__ == "__main__":

    agent = MetricsAgent()

    result = agent.investigate()

    print("\n========================================")
    print("       METRICS AGENT COMPLETED")
    print("========================================\n")

    print("Final Agent Status:", result["status"])