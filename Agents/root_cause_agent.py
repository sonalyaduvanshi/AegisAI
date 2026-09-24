from pathlib import Path
import sys
import pandas as pd


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.append(str(PROJECT_ROOT))


# =========================================================
# IMPORT AGENTS
# =========================================================
# Because this file is being run directly using:
#
# python agents/root_cause_agent.py
#
# we import files from the same agents folder directly.

from metrics_agent import MetricsAgent
from log_agent import LogAgent
from deployment_agent import DeploymentAgent


class RootCauseAgent:

    def __init__(self):

        self.name = "RootCauseAgent"

        self.role = (
            "Correlate metrics, logs, and deployments "
            "to identify the most likely root cause"
        )


    # =====================================================
    # MAIN INVESTIGATION
    # =====================================================

    def investigate(self):

        print("\n========================================")
        print("          ROOT CAUSE AGENT")
        print("========================================\n")

        print(f"Agent: {self.name}")
        print(f"Role: {self.role}")


        # =================================================
        # 1. METRICS AGENT
        # =================================================

        print("\n\n[1/3] Running Metrics Agent...")

        metrics_agent = MetricsAgent()

        metrics_result = metrics_agent.investigate()


        # =================================================
        # 2. LOG AGENT
        # =================================================

        print("\n\n[2/3] Running Log Agent...")

        log_agent = LogAgent()

        log_result = log_agent.investigate()


        # =================================================
        # 3. DEPLOYMENT AGENT
        # =================================================

        print("\n\n[3/3] Running Deployment Agent...")

        deployment_agent = DeploymentAgent()

        deployment_result = deployment_agent.investigate()


        # =================================================
        # GET ANOMALIES
        # =================================================

        anomalies = metrics_result.get(
            "evidence",
            []
        )

        anomaly_count = len(anomalies)


        if anomaly_count == 0:

            print("\n========================================")
            print("       NO ROOT CAUSE FOUND")
            print("========================================")

            print(
                "\nMetrics Agent did not detect "
                "any production anomaly."
            )

            return {
                "agent": self.name,
                "status": "NO_ANOMALY",
                "root_cause": None,
                "confidence": "N/A"
            }


        # =================================================
        # FIRST ANOMALY
        # =================================================

        first_anomaly = anomalies[0]

        anomaly_time = pd.to_datetime(
            first_anomaly["timestamp"]
        )

        anomaly_service = (
            first_anomaly["service"]
        )


        # =================================================
        # DEPLOYMENT CORRELATION
        # =================================================

        deployment_evidence = deployment_result.get(
            "evidence",
            []
        )

        correlated_deployments = []


        for deployment in deployment_evidence:

            deployment_time = pd.to_datetime(
                deployment["timestamp"]
            )

            time_difference = (
                anomaly_time - deployment_time
            ).total_seconds() / 60


            # Deployment occurred before anomaly
            # within 30 minutes

            if 0 <= time_difference <= 30:

                correlated_deployments.append({

                    "deployment": deployment,

                    "minutes_before_anomaly":
                        round(
                            time_difference,
                            2
                        )

                })


        # =================================================
        # LOG CORRELATION
        # =================================================

        log_evidence = log_result.get(
            "evidence",
            []
        )

        correlated_logs = []


        for log in log_evidence:

            log_time = pd.to_datetime(
                log["timestamp"]
            )

            time_difference = (
                log_time - anomaly_time
            ).total_seconds() / 60


            # Logs within 5 minutes before
            # or 10 minutes after anomaly

            if -5 <= time_difference <= 10:

                correlated_logs.append(log)


        # =================================================
        # CORRELATION REPORT
        # =================================================

        print("\n========================================")
        print("       ROOT CAUSE CORRELATION")
        print("========================================")


        print("\nFirst detected anomaly:")

        print(
            "Time:",
            first_anomaly["timestamp"]
        )

        print(
            "Service:",
            anomaly_service
        )

        print(
            "API Latency:",
            first_anomaly["api_latency_ms"],
            "ms"
        )

        print(
            "Error Rate:",
            first_anomaly["error_rate"],
            "%"
        )

        print(
            "DB CPU:",
            first_anomaly["db_cpu_percent"],
            "%"
        )

        print(
            "DB Latency:",
            first_anomaly["db_latency_ms"],
            "ms"
        )


        # =================================================
        # DEPLOYMENT EVIDENCE
        # =================================================

        print("\n\nDeployment Evidence:")


        if correlated_deployments:

            for item in correlated_deployments:

                deployment = item["deployment"]

                print("\n----------------------------------------")

                print(
                    "Deployment Time:",
                    deployment["timestamp"]
                )

                print(
                    "Version:",
                    deployment["version"]
                )

                print(
                    "Commit:",
                    deployment["commit_id"]
                )

                print(
                    "Developer:",
                    deployment["developer"]
                )

                print(
                    "Change:",
                    deployment["change"]
                )

                print(
                    "Minutes Before Anomaly:",
                    item["minutes_before_anomaly"]
                )

        else:

            print(
                "\nNo deployment found within "
                "30 minutes before anomaly."
            )


        # =================================================
        # LOG EVIDENCE
        # =================================================

        print("\n\nLog Evidence:")


        if correlated_logs:

            for log in correlated_logs:

                print("\n----------------------------------------")

                print(
                    "Time:",
                    log["timestamp"]
                )

                print(
                    "Service:",
                    log["service"]
                )

                print(
                    "Level:",
                    log["level"]
                )

                print(
                    "Message:",
                    log["message"]
                )

        else:

            print(
                "\nNo relevant log events found "
                "around anomaly."
            )


        # =================================================
        # ROOT CAUSE ASSESSMENT
        # =================================================

        root_cause = None

        confidence = "LOW"


        # -------------------------------------------------
        # Deployment + Logs
        # -------------------------------------------------

        if correlated_deployments and correlated_logs:

            latest_deployment = (
                correlated_deployments[-1]["deployment"]
            )

            root_cause = (
                "Production degradation is strongly "
                "correlated with the recent deployment "
                f"{latest_deployment['version']} "
                f"({latest_deployment['commit_id']}). "
                "The deployment was followed by increasing "
                "API latency, database load, and error rate, "
                "while application logs also reported "
                "related issues."
            )

            confidence = "HIGH"


        # -------------------------------------------------
        # Deployment only
        # -------------------------------------------------

        elif correlated_deployments:

            latest_deployment = (
                correlated_deployments[-1]["deployment"]
            )

            root_cause = (
                "Production degradation is temporally "
                "correlated with the recent deployment "
                f"{latest_deployment['version']} "
                f"({latest_deployment['commit_id']}). "
                "Further log or code-level evidence is "
                "required to confirm causality."
            )

            confidence = "MEDIUM"


        # -------------------------------------------------
        # Logs only
        # -------------------------------------------------

        elif correlated_logs:

            root_cause = (
                "Production degradation is supported by "
                "application log evidence around the time "
                "of the detected anomaly. No closely timed "
                "deployment was identified."
            )

            confidence = "MEDIUM"


        # -------------------------------------------------
        # No supporting evidence
        # -------------------------------------------------

        else:

            root_cause = (
                "Anomaly detected, but the available "
                "deployment and log evidence is insufficient "
                "to determine the root cause."
            )

            confidence = "LOW"


        # =================================================
        # FINAL ANALYSIS
        # =================================================

        print("\n\n========================================")
        print("          ROOT CAUSE ANALYSIS")
        print("========================================")


        print("\nService:")

        print(
            anomaly_service
        )


        print("\nFirst Anomaly:")

        print(
            first_anomaly["timestamp"]
        )


        print("\nRoot Cause Assessment:")

        print(
            root_cause
        )


        print("\nConfidence:")

        print(
            confidence
        )


        # =================================================
        # STRUCTURED RESULT
        # =================================================

        return {

            "agent": self.name,

            "status": "ROOT_CAUSE_IDENTIFIED",

            "service": anomaly_service,

            "first_anomaly": first_anomaly,

            "correlated_deployments":
                correlated_deployments,

            "correlated_logs":
                correlated_logs,

            "root_cause":
                root_cause,

            "confidence":
                confidence

        }


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    agent = RootCauseAgent()

    result = agent.investigate()


    print("\n========================================")
    print("       ROOT CAUSE AGENT COMPLETED")
    print("========================================\n")


    print(
        "Final Status:",
        result["status"]
    )


    print(
        "Confidence:",
        result.get(
            "confidence",
            "N/A"
        )
    )
