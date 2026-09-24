from pathlib import Path
import pandas as pd


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# =========================================================
# DEPLOYMENT FILE
#
# Actual project structure:
#
# AegisAI
# └── data
#     └── deployments
#         └── deployments.csv
# =========================================================

DEPLOYMENT_FILE = (
    PROJECT_ROOT
    / "data"
    / "deployments"
    / "deployments.csv"
)


class DeploymentAgent:

    def __init__(self):

        self.name = "DeploymentAgent"

        self.role = (
            "Analyze recent deployments and correlate "
            "code changes with production anomalies"
        )


    # =====================================================
    # INVESTIGATE DEPLOYMENTS
    # =====================================================

    def investigate(self):

        print("\n========================================")
        print("        DEPLOYMENT AGENT")
        print("========================================\n")

        print(f"Agent: {self.name}")
        print(f"Role: {self.role}")


        # =================================================
        # CHECK FILE
        # =================================================

        print("\nLooking for deployment file:")
        print(DEPLOYMENT_FILE)


        if not DEPLOYMENT_FILE.exists():

            print("\n❌ Deployment file not found!")

            print("\nExpected location:")
            print(DEPLOYMENT_FILE)

            return {
                "agent": self.name,
                "status": "ERROR",
                "evidence": []
            }


        print("\n✅ Deployment file found.")


        # =================================================
        # LOAD DEPLOYMENT DATA
        # =================================================

        try:

            deployments = pd.read_csv(
                DEPLOYMENT_FILE
            )

        except Exception as error:

            print("\n❌ Could not read deployment file.")

            print("Error:", error)

            return {
                "agent": self.name,
                "status": "ERROR",
                "evidence": []
            }


        print(
            f"Total deployments: {len(deployments)}"
        )


        # =================================================
        # CHECK REQUIRED COLUMNS
        # =================================================

        required_columns = [
            "timestamp",
            "service",
            "version",
            "commit_id",
            "developer",
            "change"
        ]


        missing_columns = [
            column
            for column in required_columns
            if column not in deployments.columns
        ]


        if missing_columns:

            print("\n❌ Required deployment columns missing:")

            for column in missing_columns:

                print("-", column)


            return {
                "agent": self.name,
                "status": "INVALID_DEPLOYMENT_FORMAT",
                "evidence": []
            }


        # =================================================
        # CONVERT TIMESTAMP
        # =================================================

        deployments["timestamp"] = pd.to_datetime(
            deployments["timestamp"]
        )


        # =================================================
        # SORT DEPLOYMENTS
        # =================================================

        deployments = deployments.sort_values(
            "timestamp"
        )


        # =================================================
        # DISPLAY DEPLOYMENTS
        # =================================================

        print("\n========================================")
        print("        RECENT DEPLOYMENTS")
        print("========================================")


        for _, row in deployments.iterrows():

            print("\n----------------------------------------")

            print(
                "Timestamp:",
                row["timestamp"]
            )

            print(
                "Service:",
                row["service"]
            )

            print(
                "Version:",
                row["version"]
            )

            print(
                "Commit:",
                row["commit_id"]
            )

            print(
                "Developer:",
                row["developer"]
            )

            print(
                "Change:",
                row["change"]
            )


        # =================================================
        # FIND LATEST DEPLOYMENT
        # =================================================

        latest = deployments.iloc[-1]


        print("\n========================================")
        print("        LATEST DEPLOYMENT")
        print("========================================\n")


        print(
            "Timestamp:",
            latest["timestamp"]
        )

        print(
            "Service:",
            latest["service"]
        )

        print(
            "Version:",
            latest["version"]
        )

        print(
            "Commit:",
            latest["commit_id"]
        )

        print(
            "Developer:",
            latest["developer"]
        )

        print(
            "Change:",
            latest["change"]
        )


        # =================================================
        # CREATE STRUCTURED EVIDENCE
        # =================================================

        evidence = []


        for _, row in deployments.iterrows():

            evidence.append({

                "timestamp": str(
                    row["timestamp"]
                ),

                "service": str(
                    row["service"]
                ),

                "version": str(
                    row["version"]
                ),

                "commit_id": str(
                    row["commit_id"]
                ),

                "developer": str(
                    row["developer"]
                ),

                "change": str(
                    row["change"]
                )

            })


        # =================================================
        # RETURN RESULT
        # =================================================

        return {

            "agent": self.name,

            "status": "DEPLOYMENTS_FOUND",

            "deployment_count": len(evidence),

            "latest_deployment": {

                "timestamp": str(
                    latest["timestamp"]
                ),

                "service": str(
                    latest["service"]
                ),

                "version": str(
                    latest["version"]
                ),

                "commit_id": str(
                    latest["commit_id"]
                ),

                "developer": str(
                    latest["developer"]
                ),

                "change": str(
                    latest["change"]
                )

            },

            "evidence": evidence

        }


# =========================================================
# RUN DEPLOYMENT AGENT DIRECTLY
# =========================================================

if __name__ == "__main__":

    agent = DeploymentAgent()

    result = agent.investigate()


    print("\n========================================")
    print("      DEPLOYMENT AGENT COMPLETED")
    print("========================================\n")


    print(
        "Final Agent Status:",
        result["status"]
    )


    print(
        "Deployments Found:",
        result.get(
            "deployment_count",
            0
        )
    )