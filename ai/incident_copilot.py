from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_metrics():
    path = PROJECT_ROOT / "data" / "metric" / "metrics.csv"

    if not path.exists():
        raise FileNotFoundError(f"Metrics file not found: {path}")

    return pd.read_csv(path)


def load_logs():
    path = PROJECT_ROOT / "data" / "log" / "log.csv"

    if not path.exists():
        raise FileNotFoundError(f"Logs file not found: {path}")

    return pd.read_csv(path)


def load_deployments():
    path = PROJECT_ROOT / "data" / "deployments" / "deployments.csv"

    if not path.exists():
        raise FileNotFoundError(f"Deployments file not found: {path}")

    return pd.read_csv(path)


def build_incident_context():

    metrics = load_metrics()
    logs = load_logs()
    deployments = load_deployments()

    metrics["timestamp"] = pd.to_datetime(metrics["timestamp"])
    logs["timestamp"] = pd.to_datetime(logs["timestamp"])
    deployments["timestamp"] = pd.to_datetime(deployments["timestamp"])

    # Detect production degradation directly from raw metrics
    anomaly_mask = (
        (metrics["avg_latency_ms"] > 1000)
        | (metrics["error_rate"] > 10)
        | (metrics["db_cpu_percent"] > 90)
        | (metrics["db_latency_ms"] > 100)
    )

    anomalies = metrics[anomaly_mask].copy()

    if anomalies.empty:
        return {
            "status": "NO_INCIDENT",
            "message": "No significant production degradation detected.",
        }

    anomalies = anomalies.sort_values("timestamp")

    first_anomaly = anomalies.iloc[0]
    service = first_anomaly["service"]

    first_anomaly_time = first_anomaly["timestamp"]

    # Relevant logs
    relevant_logs = logs[
        (logs["timestamp"] >= first_anomaly_time - pd.Timedelta(minutes=5))
        & (logs["timestamp"] <= first_anomaly_time + pd.Timedelta(minutes=10))
    ].copy()

    # Relevant deployments
    relevant_deployments = deployments[
        (deployments["timestamp"] <= first_anomaly_time)
        & (
            deployments["timestamp"]
            >= first_anomaly_time - pd.Timedelta(hours=2)
        )
    ].copy()

    relevant_deployments = relevant_deployments.sort_values(
        "timestamp",
        ascending=False
    )

    latest_deployment = (
        relevant_deployments.iloc[0]
        if not relevant_deployments.empty
        else None
    )

    # Root cause reasoning
    root_cause = "Unknown"

    if latest_deployment is not None:

        deployment_time = latest_deployment["timestamp"]

        minutes_before = (
            first_anomaly_time - deployment_time
        ).total_seconds() / 60

        database_failure = relevant_logs[
            relevant_logs["message"]
            .astype(str)
            .str.lower()
            .str.contains(
                "database|connection pool|timeout",
                regex=True
            )
        ]

        if 0 <= minutes_before <= 30 and not database_failure.empty:

            root_cause = (
                f"Production degradation is strongly correlated with "
                f"deployment {latest_deployment['version']} "
                f"({latest_deployment['commit_id']}). "
                f"The deployment occurred {minutes_before:.2f} minutes "
                f"before the first anomaly, while logs show database "
                f"connection-pool and timeout failures."
            )

    context = {
        "status": "INCIDENT_DETECTED",
        "service": service,
        "first_anomaly": str(first_anomaly_time),
        "anomaly_count": len(anomalies),
        "relevant_log_count": len(relevant_logs),
        "deployment_count": len(relevant_deployments),
        "root_cause": root_cause,
        "anomalies": anomalies,
        "logs": relevant_logs,
        "deployments": relevant_deployments,
    }

    return context


def answer_question(question: str):

    context = build_incident_context()

    if context["status"] == "NO_INCIDENT":
        return context["message"]

    question_lower = question.lower()

    if "why" in question_lower or "root cause" in question_lower:

        return (
            f"Root Cause Analysis\n\n"
            f"Service: {context['service']}\n"
            f"First anomaly: {context['first_anomaly']}\n\n"
            f"{context['root_cause']}\n\n"
            f"Evidence:\n"
            f"- {context['anomaly_count']} anomalies detected\n"
            f"- {context['relevant_log_count']} relevant log events\n"
            f"- {context['deployment_count']} recent deployments correlated"
        )

    if "deployment" in question_lower:

        if context["deployments"].empty:
            return "No relevant deployment was found."

        deployment = context["deployments"].iloc[0]

        return (
            f"Latest relevant deployment:\n\n"
            f"Version: {deployment['version']}\n"
            f"Commit: {deployment['commit_id']}\n"
            f"Time: {deployment['timestamp']}\n"
            f"Developer: {deployment['developer']}\n"
            f"Change: {deployment['change']}"
        )

    if "log" in question_lower:

        logs = context["logs"]

        if logs.empty:
            return "No relevant logs found."

        output = "Relevant production logs:\n\n"

        for _, row in logs.iterrows():

            output += (
                f"{row['timestamp']} | "
                f"{row['level']} | "
                f"{row['message']}\n"
            )

        return output

    if "anomal" in question_lower or "metric" in question_lower:

        anomalies = context["anomalies"]

        output = (
            f"Detected {len(anomalies)} anomalous metric records.\n\n"
        )

        for _, row in anomalies.iterrows():

            output += (
                f"{row['timestamp']} | "
                f"{row['service']} | "
                f"Latency: {row['avg_latency_ms']} ms | "
                f"Error rate: {row['error_rate']}% | "
                f"DB CPU: {row['db_cpu_percent']}% | "
                f"DB latency: {row['db_latency_ms']} ms\n"
            )

        return output

    return (
        f"Incident detected for {context['service']}.\n\n"
        f"First anomaly: {context['first_anomaly']}\n"
        f"Anomalies: {context['anomaly_count']}\n"
        f"Relevant logs: {context['relevant_log_count']}\n"
        f"Recent deployments: {context['deployment_count']}\n\n"
        f"Root Cause:\n{context['root_cause']}"
    )


if __name__ == "__main__":

    print("=" * 70)
    print("              AEGISAI INCIDENT COPILOT")
    print("=" * 70)

    context = build_incident_context()

    print("\nINCIDENT STATUS")
    print("-" * 70)

    print(f"Status       : {context['status']}")

    if context["status"] == "INCIDENT_DETECTED":

        print(f"Service      : {context['service']}")
        print(f"First Anomaly: {context['first_anomaly']}")
        print(f"Anomalies    : {context['anomaly_count']}")
        print(f"Logs         : {context['relevant_log_count']}")
        print(f"Deployments  : {context['deployment_count']}")

        print("\nROOT CAUSE")
        print("-" * 70)
        print(context["root_cause"])

    print("\n" + "=" * 70)
    print("              COPILOT READY")
    print("=" * 70)