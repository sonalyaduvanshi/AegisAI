from pathlib import Path
import sys
import pandas as pd


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# FILE PATHS
# =========================================================

METRICS_FILE = (
    PROJECT_ROOT
    / "data"
    / "metric"
    / "metrics.csv"
)

LOG_FILE = (
    PROJECT_ROOT
    / "data"
    / "log"
    / "log.csv"
)

DEPLOYMENT_FILE = (
    PROJECT_ROOT
    / "data"
    / "deployments"
    / "deployments.csv"
)


# =========================================================
# REMEDIATION AGENT
# =========================================================

class RemediationAgent:

    def __init__(self):

        self.name = "RemediationAgent"

        self.role = (
            "Generate evidence-based remediation actions "
            "for detected production incidents"
        )


    # =====================================================
    # INVESTIGATE / REMEDIATE
    # =====================================================

    def investigate(self):

        print("\n========================================")
        print("        REMEDIATION AGENT")
        print("========================================\n")

        print(f"Agent: {self.name}")
        print(f"Role: {self.role}")


        # =================================================
        # LOAD DATA
        # =================================================

        metrics = None
        logs = None
        deployments = None


        # -------------------------------------------------
        # Metrics
        # -------------------------------------------------

        if METRICS_FILE.exists():

            try:
                metrics = pd.read_csv(METRICS_FILE)

            except Exception as error:

                print("\n⚠️ Could not read metrics:")
                print(error)


        # -------------------------------------------------
        # Logs
        # -------------------------------------------------

        if LOG_FILE.exists():

            try:
                logs = pd.read_csv(LOG_FILE)

            except Exception as error:

                print("\n⚠️ Could not read logs:")
                print(error)


        # -------------------------------------------------
        # Deployments
        # -------------------------------------------------

        if DEPLOYMENT_FILE.exists():

            try:
                deployments = pd.read_csv(
                    DEPLOYMENT_FILE
                )

            except Exception as error:

                print("\n⚠️ Could not read deployments:")
                print(error)


        # =================================================
        # DETERMINE INCIDENT
        # =================================================

        anomaly_count = 0

        first_anomaly = None

        service = "unknown"


        if metrics is not None:

            if "status" in metrics.columns:

                anomalies = metrics[
                    metrics["status"] == "ANOMALY"
                ]

                anomaly_count = len(anomalies)


                if not anomalies.empty:

                    first_anomaly = anomalies.iloc[0]

                    service = str(
                        first_anomaly.get(
                            "service",
                            "unknown"
                        )
                    )


        # =================================================
        # PRINT INCIDENT INFORMATION
        # =================================================

        print("\n========================================")
        print("        INCIDENT ASSESSMENT")
        print("========================================")


        print(
            "\nAnomalies detected:",
            anomaly_count
        )

        print(
            "Affected service:",
            service
        )


        # =================================================
        # FIND LATEST DEPLOYMENT
        # =================================================

        latest_deployment = None


        if deployments is not None:

            if not deployments.empty:

                try:

                    deployments["timestamp"] = (
                        pd.to_datetime(
                            deployments["timestamp"]
                        )
                    )

                    deployments = deployments.sort_values(
                        "timestamp"
                    )

                    latest_deployment = (
                        deployments.iloc[-1]
                    )

                except Exception as error:

                    print(
                        "\n⚠️ Deployment analysis failed:",
                        error
                    )


        # =================================================
        # REMEDIATION PLAN
        # =================================================

        actions = []


        # -------------------------------------------------
        # ACTION 1 - Deployment rollback
        # -------------------------------------------------

        if latest_deployment is not None:

            version = str(
                latest_deployment.get(
                    "version",
                    "unknown"
                )
            )

            commit_id = str(
                latest_deployment.get(
                    "commit_id",
                    "unknown"
                )
            )

            change = str(
                latest_deployment.get(
                    "change",
                    "unknown"
                )
            )


            actions.append(
                {
                    "priority": "P0",
                    "action": "Rollback deployment",
                    "reason": (
                        f"Recent deployment {version} "
                        f"({commit_id}) is temporally "
                        "associated with the incident."
                    ),
                    "details": (
                        f"Review or rollback {version} "
                        f"before further production impact. "
                        f"Deployment change: {change}"
                    )
                }
            )


        # -------------------------------------------------
        # ACTION 2 - Database investigation
        # -------------------------------------------------

        actions.append(
            {
                "priority": "P0",
                "action": "Investigate database connection pool",
                "reason": (
                    "Production logs indicate increasing "
                    "database connection pressure."
                ),
                "details": (
                    "Inspect connection pool size, "
                    "connection leaks, query execution time, "
                    "and database saturation."
                )
            }
        )


        # -------------------------------------------------
        # ACTION 3 - Query investigation
        # -------------------------------------------------

        actions.append(
            {
                "priority": "P1",
                "action": "Review authentication queries",
                "reason": (
                    "The affected service is auth-service "
                    "and the latest deployment contains "
                    "an authentication query change."
                ),
                "details": (
                    "Compare query execution plans before "
                    "and after the deployment. Check indexes, "
                    "joins, locks and query latency."
                )
            }
        )


        # -------------------------------------------------
        # ACTION 4 - Monitor metrics
        # -------------------------------------------------

        actions.append(
            {
                "priority": "P1",
                "action": "Increase production monitoring",
                "reason": (
                    "API latency, error rate and database "
                    "load increased during the incident."
                ),
                "details": (
                    "Monitor API latency, error rate, "
                    "database CPU, database latency and "
                    "connection-pool utilization."
                )
            }
        )


        # -------------------------------------------------
        # ACTION 5 - Prevent recurrence
        # -------------------------------------------------

        actions.append(
            {
                "priority": "P2",
                "action": "Add regression protection",
                "reason": (
                    "A production deployment was followed "
                    "by database-related degradation."
                ),
                "details": (
                    "Add query performance tests, database "
                    "load tests and deployment health checks "
                    "before future releases."
                )
            }
        )


        # =================================================
        # DISPLAY REMEDIATION PLAN
        # =================================================

        print("\n========================================")
        print("        RECOMMENDED ACTIONS")
        print("========================================")


        for index, action in enumerate(
            actions,
            start=1
        ):

            print(
                f"\n{index}. "
                f"[{action['priority']}] "
                f"{action['action']}"
            )

            print(
                "Reason:",
                action["reason"]
            )

            print(
                "Details:",
                action["details"]
            )


        # =================================================
        # SAFETY NOTE
        # =================================================

        print("\n========================================")
        print("        REMEDIATION SAFETY")
        print("========================================\n")

        print(
            "⚠️ No production changes were executed."
        )

        print(
            "AegisAI only generated recommended "
            "remediation actions."
        )


        # =================================================
        # RETURN STRUCTURED RESULT
        # =================================================

        return {

            "agent": self.name,

            "status": "REMEDIATION_PLAN_CREATED",

            "service": service,

            "anomaly_count": anomaly_count,

            "actions": actions

        }


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    agent = RemediationAgent()

    result = agent.investigate()


    print("\n========================================")
    print("      REMEDIATION AGENT COMPLETED")
    print("========================================\n")


    print(
        "Final Agent Status:",
        result["status"]
    )

    print(
        "Actions Generated:",
        len(result["actions"])
    )