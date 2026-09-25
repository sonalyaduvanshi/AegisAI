from pathlib import Path
import sys
import pandas as pd


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORT EXISTING AEGISAI ML DETECTOR
# ============================================================

from ml.anomaly_detector import detect_anomalies


# ============================================================
# DATA PATHS
# ============================================================

METRICS_PATH = (
    PROJECT_ROOT
    / "data"
    / "metric"
    / "metrics.csv"
)

LOG_PATH = (
    PROJECT_ROOT
    / "data"
    / "log"
    / "log.csv"
)

DEPLOYMENT_PATH = (
    PROJECT_ROOT
    / "data"
    / "deployments"
    / "deployments.csv"
)


# ============================================================
# INVESTIGATION AGENT
# ============================================================

class InvestigationAgent:

    def __init__(self):

        self.name = "InvestigationAgent"

        self.role = (
            "Correlate ML anomaly detection, application logs "
            "and recent deployments to investigate production incidents."
        )

        self.metrics = pd.DataFrame()
        self.logs = pd.DataFrame()
        self.deployments = pd.DataFrame()

    # ========================================================
    # LOAD RAW DATA
    # ========================================================

    def load_data(self):

        print("\n[1/5] Loading production data...")

        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        if not METRICS_PATH.exists():

            raise FileNotFoundError(
                f"Metrics file not found:\n{METRICS_PATH}"
            )

        self.metrics = pd.read_csv(
            METRICS_PATH
        )

        # ----------------------------------------------------
        # Logs
        # ----------------------------------------------------

        if not LOG_PATH.exists():

            raise FileNotFoundError(
                f"Log file not found:\n{LOG_PATH}"
            )

        self.logs = pd.read_csv(
            LOG_PATH
        )

        # ----------------------------------------------------
        # Deployments
        # ----------------------------------------------------

        if not DEPLOYMENT_PATH.exists():

            raise FileNotFoundError(
                f"Deployment file not found:\n{DEPLOYMENT_PATH}"
            )

        self.deployments = pd.read_csv(
            DEPLOYMENT_PATH
        )

        print(
            f"Metrics      : {len(self.metrics)}"
        )

        print(
            f"Logs         : {len(self.logs)}"
        )

        print(
            f"Deployments  : {len(self.deployments)}"
        )

        print("\nRaw metric columns:")

        print(
            list(self.metrics.columns)
        )

    # ========================================================
    # ML ANOMALY DETECTION
    # ========================================================

    def detect_anomalies(self):

        print("\n[2/5] Running ML anomaly detection...")

        try:

            result = detect_anomalies()

        except Exception as error:

            print(
                "\nERROR: ML anomaly detection failed."
            )

            print(error)

            return pd.DataFrame()

        # ----------------------------------------------------
        # Existing detector returns dictionary
        # ----------------------------------------------------

        if isinstance(result, dict):

            anomalies = result.get(
                "anomalies",
                []
            )

            # -----------------------------------------------
            # Convert anomaly list to DataFrame
            # -----------------------------------------------

            if isinstance(
                anomalies,
                pd.DataFrame
            ):

                anomaly_df = anomalies.copy()

            elif isinstance(
                anomalies,
                list
            ):

                anomaly_df = pd.DataFrame(
                    anomalies
                )

            else:

                anomaly_df = pd.DataFrame()

            # -----------------------------------------------
            # If detector returned complete dataframe
            # -----------------------------------------------

            if anomaly_df.empty:

                dataframe = result.get(
                    "data",
                    result.get(
                        "results",
                        None
                    )
                )

                if isinstance(
                    dataframe,
                    pd.DataFrame
                ):

                    if "status" in dataframe.columns:

                        anomaly_df = dataframe[
                            dataframe["status"]
                            .astype(str)
                            .str.upper()
                            == "ANOMALY"
                        ].copy()

        # ----------------------------------------------------
        # Detector directly returned DataFrame
        # ----------------------------------------------------

        elif isinstance(
            result,
            pd.DataFrame
        ):

            dataframe = result.copy()

            if "status" in dataframe.columns:

                anomaly_df = dataframe[
                    dataframe["status"]
                    .astype(str)
                    .str.upper()
                    == "ANOMALY"
                ].copy()

            else:

                anomaly_df = dataframe

        else:

            anomaly_df = pd.DataFrame()

        # ====================================================
        # IMPORTANT FALLBACK
        # ====================================================

        # If the detector output format is different,
        # run the same Isolation Forest logic directly
        # using the existing production metric columns.

        if anomaly_df.empty:

            print(
                "Detector output did not expose anomaly rows."
            )

            print(
                "Running Investigation fallback detector..."
            )

            anomaly_df = self.fallback_ml_detection()

        # ----------------------------------------------------
        # Normalize timestamps
        # ----------------------------------------------------

        if not anomaly_df.empty:

            if "timestamp" in anomaly_df.columns:

                anomaly_df["timestamp"] = pd.to_datetime(
                    anomaly_df["timestamp"],
                    errors="coerce"
                )

                anomaly_df = anomaly_df.sort_values(
                    "timestamp"
                )

        print(
            f"\nML anomalies detected: "
            f"{len(anomaly_df)}"
        )

        return anomaly_df

    # ========================================================
    # FALLBACK ML DETECTOR
    # ========================================================

    def fallback_ml_detection(self):

        try:

            from sklearn.ensemble import IsolationForest

        except ImportError as error:

            print(
                "scikit-learn is not available."
            )

            print(error)

            return pd.DataFrame()

        dataframe = self.metrics.copy()

        feature_columns = [
            "cpu_percent",
            "memory_percent",
            "request_count",
            "avg_latency_ms",
            "error_rate",
            "db_cpu_percent",
            "db_latency_ms"
        ]

        missing_columns = [
            column
            for column in feature_columns
            if column not in dataframe.columns
        ]

        if missing_columns:

            print(
                "\nMissing ML features:"
            )

            print(
                missing_columns
            )

            return pd.DataFrame()

        # ----------------------------------------------------
        # Numeric conversion
        # ----------------------------------------------------

        for column in feature_columns:

            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce"
            )

        dataframe = dataframe.dropna(
            subset=feature_columns
        ).copy()

        if dataframe.empty:

            return pd.DataFrame()

        # ----------------------------------------------------
        # Isolation Forest
        # ----------------------------------------------------

        model = IsolationForest(
            contamination=0.30,
            random_state=42
        )

        dataframe["prediction"] = model.fit_predict(
            dataframe[feature_columns]
        )

        dataframe["anomaly_score"] = model.decision_function(
            dataframe[feature_columns]
        )

        dataframe["status"] = dataframe[
            "prediction"
        ].map(
            {
                1: "NORMAL",
                -1: "ANOMALY"
            }
        )

        anomalies = dataframe[
            dataframe["status"] == "ANOMALY"
        ].copy()

        return anomalies

    # ========================================================
    # LOG CORRELATION
    # ========================================================

    def analyze_logs(
        self,
        service,
        incident_time
    ):

        print("\n[3/5] Correlating application logs...")

        logs = self.logs.copy()

        if logs.empty:

            return logs

        # ----------------------------------------------------
        # Timestamp
        # ----------------------------------------------------

        logs["timestamp"] = pd.to_datetime(
            logs["timestamp"],
            errors="coerce"
        )

        incident_time = pd.to_datetime(
            incident_time,
            errors="coerce"
        )

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------

        if "service" in logs.columns:

            logs = logs[
                logs["service"].astype(str)
                == str(service)
            ]

        # ----------------------------------------------------
        # Time window
        # ----------------------------------------------------

        if pd.notna(incident_time):

            start_time = (
                incident_time
                - pd.Timedelta(minutes=15)
            )

            end_time = (
                incident_time
                + pd.Timedelta(minutes=2)
            )

            logs = logs[
                (logs["timestamp"] >= start_time)
                &
                (logs["timestamp"] <= end_time)
            ]

        # ----------------------------------------------------
        # Important levels
        # ----------------------------------------------------

        if "level" in logs.columns:

            logs = logs[
                logs["level"]
                .astype(str)
                .str.upper()
                .isin(
                    [
                        "WARN",
                        "ERROR",
                        "CRITICAL"
                    ]
                )
            ]

        logs = logs.sort_values(
            "timestamp"
        )

        print(
            f"Relevant log events: "
            f"{len(logs)}"
        )

        return logs

    # ========================================================
    # DEPLOYMENT CORRELATION
    # ========================================================

    def analyze_deployments(
        self,
        service,
        incident_time
    ):

        print("\n[4/5] Correlating recent deployments...")

        deployments = self.deployments.copy()

        if deployments.empty:

            return deployments

        deployments["timestamp"] = pd.to_datetime(
            deployments["timestamp"],
            errors="coerce"
        )

        incident_time = pd.to_datetime(
            incident_time,
            errors="coerce"
        )

        # ----------------------------------------------------
        # Service
        # ----------------------------------------------------

        if "service" in deployments.columns:

            deployments = deployments[
                deployments["service"].astype(str)
                == str(service)
            ]

        if deployments.empty:

            return deployments

        # ----------------------------------------------------
        # Calculate timing
        # ----------------------------------------------------

        deployments[
            "minutes_before_incident"
        ] = (
            incident_time
            - deployments["timestamp"]
        ).dt.total_seconds() / 60

        # ----------------------------------------------------
        # Only previous 60 minutes
        # ----------------------------------------------------

        deployments = deployments[
            (
                deployments[
                    "minutes_before_incident"
                ] >= 0
            )
            &
            (
                deployments[
                    "minutes_before_incident"
                ] <= 60
            )
        ]

        deployments = deployments.sort_values(
            "minutes_before_incident"
        )

        print(
            f"Relevant deployments: "
            f"{len(deployments)}"
        )

        return deployments

    # ========================================================
    # ROOT CAUSE CORRELATION
    # ========================================================

    def investigate(self):

        print("\n")
        print("=" * 60)
        print("          AEGISAI INVESTIGATION AGENT")
        print("=" * 60)

        # ----------------------------------------------------
        # Load
        # ----------------------------------------------------

        self.load_data()

        # ----------------------------------------------------
        # ML
        # ----------------------------------------------------

        anomalies = self.detect_anomalies()

        # ----------------------------------------------------
        # No anomaly
        # ----------------------------------------------------

        if anomalies.empty:

            print("\n")
            print("=" * 60)
            print("INVESTIGATION RESULT")
            print("-" * 60)
            print(
                "No production anomaly detected."
            )
            print("=" * 60)

            return {
                "status": "NO_ANOMALY",
                "anomaly_count": 0,
                "service": "unknown",
                "logs": [],
                "deployments": [],
                "root_cause": None
            }

        # ----------------------------------------------------
        # First anomaly
        # ----------------------------------------------------

        first_anomaly = anomalies.iloc[0]

        service = str(
            first_anomaly.get(
                "service",
                "unknown"
            )
        )

        incident_time = first_anomaly.get(
            "timestamp"
        )

        # ----------------------------------------------------
        # Logs
        # ----------------------------------------------------

        logs = self.analyze_logs(
            service,
            incident_time
        )

        # ----------------------------------------------------
        # Deployments
        # ----------------------------------------------------

        deployments = self.analyze_deployments(
            service,
            incident_time
        )

        # ====================================================
        # DATABASE EVIDENCE
        # ====================================================

        database_signal = False

        database_events = []

        database_keywords = [
            "database",
            "db",
            "connection pool",
            "query latency",
            "database timeout",
            "database connection",
            "db latency"
        ]

        for _, log in logs.iterrows():

            message = str(
                log.get(
                    "message",
                    ""
                )
            ).lower()

            if any(
                keyword in message
                for keyword in database_keywords
            ):

                database_signal = True

                database_events.append(
                    {
                        "timestamp": str(
                            log.get(
                                "timestamp"
                            )
                        ),
                        "level": str(
                            log.get(
                                "level"
                            )
                        ),
                        "message": message
                    }
                )

        # ====================================================
        # DEPLOYMENT EVIDENCE
        # ====================================================

        deployment_signal = (
            not deployments.empty
        )

        latest_deployment = None

        if deployment_signal:

            latest_deployment = (
                deployments.iloc[0]
            )

        # ====================================================
        # ROOT CAUSE
        # ====================================================

        if (
            database_signal
            and deployment_signal
        ):

            root_cause = (
                "Production degradation is strongly "
                "correlated with the recent deployment "
                f"{latest_deployment.get('version', 'unknown')} "
                f"({latest_deployment.get('commit_id', 'unknown')}). "
                "The deployment occurred shortly before "
                "the anomaly, while application logs show "
                "database connection-pool and timeout failures."
            )

            confidence = "HIGH"

        elif database_signal:

            root_cause = (
                "Database-related degradation is the "
                "strongest observed signal. Application "
                "logs show database latency or connection "
                "pool failures around the incident."
            )

            confidence = "MEDIUM"

        elif deployment_signal:

            root_cause = (
                "A recent deployment is temporally "
                "correlated with the detected production "
                "anomaly."
            )

            confidence = "MEDIUM"

        else:

            root_cause = (
                "An anomaly was detected, but the "
                "available logs and deployment history "
                "do not provide enough evidence for a "
                "specific root cause."
            )

            confidence = "LOW"

        # ====================================================
        # DISPLAY RESULT
        # ====================================================

        print("\n")
        print("=" * 60)
        print("           INVESTIGATION RESULT")
        print("-" * 60)

        print(
            f"Status          : INCIDENT_DETECTED"
        )

        print(
            f"Service         : {service}"
        )

        print(
            f"First Anomaly   : {incident_time}"
        )

        print(
            f"Anomalies       : {len(anomalies)}"
        )

        print(
            f"Relevant Logs   : {len(logs)}"
        )

        print(
            f"Deployments     : {len(deployments)}"
        )

        # ----------------------------------------------------
        # Root cause
        # ----------------------------------------------------

        print("\nROOT CAUSE")
        print("-" * 60)

        print(
            root_cause
        )

        print(
            f"\nConfidence      : {confidence}"
        )

        # ----------------------------------------------------
        # Deployment
        # ----------------------------------------------------

        if latest_deployment is not None:

            print("\nDEPLOYMENT EVIDENCE")
            print("-" * 60)

            print(
                f"Time            : "
                f"{latest_deployment.get('timestamp')}"
            )

            print(
                f"Version         : "
                f"{latest_deployment.get('version')}"
            )

            print(
                f"Commit          : "
                f"{latest_deployment.get('commit_id')}"
            )

            print(
                f"Change          : "
                f"{latest_deployment.get('change')}"
            )

            print(
                f"Minutes Before  : "
                f"{latest_deployment.get('minutes_before_incident'):.2f}"
            )

        # ----------------------------------------------------
        # Log evidence
        # ----------------------------------------------------

        if database_events:

            print("\nDATABASE LOG EVIDENCE")
            print("-" * 60)

            for event in database_events:

                print(
                    f"{event['timestamp']} | "
                    f"{event['level']} | "
                    f"{event['message']}"
                )

        # ----------------------------------------------------
        # Final
        # ----------------------------------------------------

        print("\n")
        print("=" * 60)
        print("        INVESTIGATION COMPLETE")
        print("=" * 60)

        # ====================================================
        # RETURN STRUCTURED RESULT
        # ====================================================

        return {
            "status": "INCIDENT_DETECTED",
            "service": service,
            "incident_time": str(
                incident_time
            ),
            "anomaly_count": len(
                anomalies
            ),
            "anomalies": anomalies,
            "log_count": len(logs),
            "logs": logs,
            "deployment_count": len(
                deployments
            ),
            "deployments": deployments,
            "database_signal": database_signal,
            "database_events": database_events,
            "deployment_signal": deployment_signal,
            "root_cause": root_cause,
            "confidence": confidence
        }


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    agent = InvestigationAgent()

    result = agent.investigate()