from pathlib import Path
import pandas as pd


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# =========================================================
# LOG FILE
# Actual project structure:
#
# AegisAI
# └── data
#     └── log
#         └── log.csv
# =========================================================

LOG_FILE = (
    PROJECT_ROOT
    / "data"
    / "log"
    / "log.csv"
)


class LogAgent:

    def __init__(self):

        self.name = "LogAgent"

        self.role = (
            "Analyze application logs and identify "
            "warnings, errors, and critical failures"
        )


    # =====================================================
    # INVESTIGATE LOGS
    # =====================================================

    def investigate(self):

        print("\n========================================")
        print("             LOG AGENT")
        print("========================================\n")

        print(f"Agent: {self.name}")
        print(f"Role: {self.role}")


        # =================================================
        # CHECK LOG FILE
        # =================================================

        print("\nLooking for log file:")
        print(LOG_FILE)


        if not LOG_FILE.exists():

            print("\n❌ Log file not found!")

            print("\nExpected location:")
            print(LOG_FILE)

            return {
                "agent": self.name,
                "status": "ERROR",
                "evidence": []
            }


        print("\n✅ Log file found.")


        # =================================================
        # LOAD LOG DATA
        # =================================================

        try:

            logs = pd.read_csv(LOG_FILE)

        except Exception as error:

            print("\n❌ Could not read log file.")

            print("Error:", error)

            return {
                "agent": self.name,
                "status": "ERROR",
                "evidence": []
            }


        print(
            f"Total log entries: {len(logs)}"
        )


        # =================================================
        # SHOW AVAILABLE COLUMNS
        # =================================================

        print("\nLog columns:")

        print(
            list(logs.columns)
        )


        # =================================================
        # CHECK REQUIRED COLUMNS
        # =================================================

        required_columns = [
            "timestamp",
            "service",
            "level",
            "message"
        ]


        missing_columns = [
            column
            for column in required_columns
            if column not in logs.columns
        ]


        if missing_columns:

            print("\n❌ Required columns are missing:")

            for column in missing_columns:

                print("-", column)


            return {
                "agent": self.name,
                "status": "INVALID_LOG_FORMAT",
                "evidence": []
            }


        # =================================================
        # FIND IMPORTANT LOG LEVELS
        # =================================================

        important_logs = logs[
            logs["level"].astype(str).str.upper().isin(
                ["WARN", "WARNING", "ERROR", "CRITICAL"]
            )
        ].copy()


        # =================================================
        # NO ISSUES FOUND
        # =================================================

        if important_logs.empty:

            print("\n✅ No warnings or errors found.")

            return {
                "agent": self.name,
                "status": "NORMAL",
                "issue_count": 0,
                "evidence": []
            }


        # =================================================
        # DISPLAY IMPORTANT LOGS
        # =================================================

        print("\n========================================")
        print("        IMPORTANT LOG EVENTS")
        print("========================================")


        for _, row in important_logs.iterrows():

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
                "Level:",
                row["level"]
            )

            print(
                "Message:",
                row["message"]
            )


        # =================================================
        # CREATE STRUCTURED EVIDENCE
        # =================================================

        evidence = []


        for _, row in important_logs.iterrows():

            evidence.append({

                "timestamp": str(
                    row["timestamp"]
                ),

                "service": str(
                    row["service"]
                ),

                "level": str(
                    row["level"]
                ),

                "message": str(
                    row["message"]
                )

            })


        # =================================================
        # RETURN RESULT
        # =================================================

        return {

            "agent": self.name,

            "status": "ISSUES_FOUND",

            "issue_count": len(evidence),

            "evidence": evidence

        }


# =========================================================
# RUN LOG AGENT DIRECTLY
# =========================================================

if __name__ == "__main__":

    agent = LogAgent()

    result = agent.investigate()


    print("\n========================================")
    print("         LOG AGENT COMPLETED")
    print("========================================\n")


    print(
        "Final Agent Status:",
        result["status"]
    )


    print(
        "Issues Found:",
        result.get("issue_count", 0)
    )