from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_metrics():
    """
    Load production metrics from the existing AegisAI dataset.
    """

    possible_paths = [
        PROJECT_ROOT / "data" / "metric" / "metrics.csv",
        PROJECT_ROOT / "data" / "metrics" / "metrics.csv",
    ]

    for path in possible_paths:
        if path.exists():
            df = pd.read_csv(path)

            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(
                    df["timestamp"],
                    errors="coerce"
                )

            return df

    return pd.DataFrame()


def load_logs():
    """
    Load existing production logs.
    """

    path = PROJECT_ROOT / "data" / "log" / "log.csv"

    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

    return df


def load_deployments():
    """
    Load existing deployment information.
    """

    path = PROJECT_ROOT / "data" / "deployments" / "deployments.csv"

    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

    return df


def get_services(metrics_df, logs_df, deployments_df):
    """
    Collect unique services from all available sources.
    """

    services = set()

    for df in [metrics_df, logs_df, deployments_df]:

        if not df.empty and "service" in df.columns:
            services.update(
                df["service"]
                .dropna()
                .astype(str)
                .tolist()
            )

    return sorted(services)


def investigate_service(service):
    """
    Build an investigation package for the selected service.
    """

    metrics = load_metrics()
    logs = load_logs()
    deployments = load_deployments()

    result = {
        "service": service,
        "metrics": pd.DataFrame(),
        "logs": pd.DataFrame(),
        "deployments": pd.DataFrame(),
        "anomalies": pd.DataFrame(),
    }

    # -----------------------------
    # METRICS
    # -----------------------------

    if not metrics.empty and "service" in metrics.columns:

        service_metrics = metrics[
            metrics["service"].astype(str) == str(service)
        ].copy()

        result["metrics"] = service_metrics

        if "status" in service_metrics.columns:

            result["anomalies"] = service_metrics[
                service_metrics["status"].astype(str).str.upper()
                == "ANOMALY"
            ].copy()

        elif "anomaly_score" in service_metrics.columns:

            result["anomalies"] = service_metrics[
                service_metrics["anomaly_score"] < 0
            ].copy()

    # -----------------------------
    # LOGS
    # -----------------------------

    if not logs.empty and "service" in logs.columns:

        result["logs"] = logs[
            logs["service"].astype(str) == str(service)
        ].copy()

    # -----------------------------
    # DEPLOYMENTS
    # -----------------------------

    if not deployments.empty and "service" in deployments.columns:

        result["deployments"] = deployments[
            deployments["service"].astype(str) == str(service)
        ].copy()

    return result


def calculate_incident_summary(investigation):
    """
    Generate high-level incident statistics.
    """

    metrics = investigation["metrics"]
    anomalies = investigation["anomalies"]
    logs = investigation["logs"]
    deployments = investigation["deployments"]

    summary = {
        "total_metrics": len(metrics),
        "anomalies": len(anomalies),
        "log_events": len(logs),
        "deployments": len(deployments),
    }

    return summary


def get_latest_deployment(deployments):
    """
    Return latest deployment.
    """

    if deployments.empty:
        return None

    if "timestamp" not in deployments.columns:
        return deployments.iloc[-1].to_dict()

    deployments = deployments.sort_values("timestamp")

    return deployments.iloc[-1].to_dict()


def get_first_anomaly(anomalies):
    """
    Return first detected anomaly.
    """

    if anomalies.empty:
        return None

    if "timestamp" in anomalies.columns:

        anomalies = anomalies.sort_values("timestamp")

    return anomalies.iloc[0].to_dict()


def build_evidence_chain(investigation):
    """
    Build a simple evidence chain connecting:

    Deployment
          ↓
    Logs
          ↓
    Anomaly
    """

    anomalies = investigation["anomalies"]
    logs = investigation["logs"]
    deployments = investigation["deployments"]

    first_anomaly = get_first_anomaly(anomalies)
    latest_deployment = get_latest_deployment(deployments)

    evidence = {
        "first_anomaly": first_anomaly,
        "latest_deployment": latest_deployment,
        "related_logs": logs,
    }

    return evidence