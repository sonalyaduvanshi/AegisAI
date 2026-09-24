from pathlib import Path
import pandas as pd
import subprocess


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# =========================================================
# DEPLOYMENT FILE
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
    # VERIFY COMMIT IN GIT
    # =====================================================

    def verify_git_commit(self, commit_id):

        try:

            result = subprocess.run(
                [
                    "git",
                    "cat-file",
                    "-t",
                    commit_id
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:

                return True

            return False

        except Exception:

            return False

    # =====================================================
    # GET LATEST GIT COMMIT
    # =====================================================

    def get_latest_git_commit(self):

        try:

            result = subprocess.run(
                [
                    "git",
                    "rev-parse",
                    "HEAD"
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:

                return result.stdout.strip()

            return None

        except Exception:

            return None

    # =====================================================
    # GET COMMIT MESSAGE
    # =====================================================

    def get_commit_message(self, commit_id):

        try:

            result = subprocess.run(
                [
                    "git",
                    "log",
                    "-1",
                    "--pretty=%s",
                    commit_id
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:

                return result.stdout.strip()

            return None

        except Exception:

            return None

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
        # GIT VERIFICATION
        # =================================================

        deployment_commit = str(
            latest["commit_id"]
        ).strip()

        print("\n========================================")
        print("          GIT VERIFICATION")
        print("========================================\n")

        print(
            "Deployment Commit:",
            deployment_commit
        )

        commit_exists = self.verify_git_commit(
            deployment_commit
        )

        if commit_exists:

            print(
                "✅ Deployment commit exists in Git."
            )

            git_commit = deployment_commit

        else:

            print(
                "⚠️ Deployment commit was not found in local Git."
            )

            print(
                "This can happen when deployment metadata "
                "comes from another repository/environment."
            )

            git_commit = None

        # =================================================
        # CURRENT GIT COMMIT
        # =================================================

        latest_git_commit = self.get_latest_git_commit()

        print(
            "\nCurrent Git HEAD:",
            latest_git_commit
            if latest_git_commit
            else "Unavailable"
        )

        # =================================================
        # CURRENT COMMIT MESSAGE
        # =================================================

        current_commit_message = None

        if latest_git_commit:

            current_commit_message = (
                self.get_commit_message(
                    latest_git_commit
                )
            )

        if current_commit_message:

            print(
                "Current Commit Message:",
                current_commit_message
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
        # STRUCTURED LATEST DEPLOYMENT
        # =================================================

        latest_deployment = {

            "timestamp": str(
                latest["timestamp"]
            ),

            "service": str(
                latest["service"]
            ),

            "version": str(
                latest["version"]
            ),

            "commit_id": deployment_commit,

            "developer": str(
                latest["developer"]
            ),

            "change": str(
                latest["change"]
            ),

            "git_commit_exists": commit_exists,

            "current_git_head": latest_git_commit,

            "current_git_message": current_commit_message

        }

        # =================================================
        # RETURN RESULT
        # =================================================

        return {

            "agent": self.name,

            "status": "DEPLOYMENTS_FOUND",

            "deployment_count": len(
                evidence
            ),

            "latest_deployment":
                latest_deployment,

            "evidence":
                evidence

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