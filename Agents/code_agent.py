from pathlib import Path
import sys


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.append(str(PROJECT_ROOT))


# =========================================================
# IMPORT CODE TOOL
# =========================================================

from tools.code_tool import CodeTool


class CodeAgent:

    def __init__(self):

        self.name = "CodeAgent"

        self.role = (
            "Inspect Git code changes for database, "
            "performance, configuration and reliability risks"
        )

        self.tool = CodeTool()


    # =====================================================
    # ANALYZE
    # =====================================================

    def analyze(self, commit=None):

        print("\n========================================")
        print("            CODE AGENT")
        print("========================================\n")

        print("Agent:", self.name)
        print("Role:", self.role)


        # -------------------------------------------------
        # Get latest commit if none supplied
        # -------------------------------------------------

        if commit is None:

            commits = self.tool.get_recent_commits(
                limit=5
            )

            if not commits:

                print(
                    "\n❌ No Git commits found."
                )

                return {
                    "agent": self.name,
                    "status": "ERROR",
                    "findings": []
                }

            commit = commits[0]["commit"]


        print(
            "\nAnalyzing Git commit:",
            commit
        )


        # -------------------------------------------------
        # Analyze commit
        # -------------------------------------------------

        result = self.tool.analyze_commit(
            commit
        )


        # -------------------------------------------------
        # Changed files
        # -------------------------------------------------

        changed_files = result[
            "changed_files"
        ]

        print(
            "\nChanged files:",
            len(changed_files)
        )


        for item in changed_files:

            print(
                f"  [{item['status']}]",
                item["file"]
            )


        # -------------------------------------------------
        # Risk signals
        # -------------------------------------------------

        signals = result[
            "risk_signals"
        ]


        print(
            "\n========================================"
        )

        print(
            "        CODE INTELLIGENCE RESULTS"
        )

        print(
            "========================================"
        )


        if not signals:

            print(
                "\n✅ No obvious risky patterns detected."
            )

            return {

                "agent":
                    self.name,

                "status":
                    "NO_RISK_FOUND",

                "commit":
                    commit,

                "findings":
                    []

            }


        # -------------------------------------------------
        # Deduplicate signals
        # -------------------------------------------------

        unique_signals = []

        seen = set()


        for signal in signals:

            key = (
                signal["category"],
                signal["signal"]
            )

            if key not in seen:

                seen.add(key)

                unique_signals.append(
                    signal
                )


        # -------------------------------------------------
        # Print findings
        # -------------------------------------------------

        print(
            "\n⚠️ Potential code risks detected:"
        )


        for index, signal in enumerate(
            unique_signals,
            start=1
        ):

            print(
                f"\n{index}. "
                f"[{signal['category']}]"
            )

            print(
                "   ",
                signal["signal"]
            )


        # -------------------------------------------------
        # Calculate risk level
        # -------------------------------------------------

        database_count = len([
            x for x in unique_signals
            if x["category"] == "DATABASE"
        ])

        performance_count = len([
            x for x in unique_signals
            if x["category"] == "PERFORMANCE"
        ])

        configuration_count = len([
            x for x in unique_signals
            if x["category"] == "CONFIGURATION"
        ])


        total = len(unique_signals)


        if database_count >= 3:

            risk_level = "HIGH"

        elif total >= 2:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"


        # -------------------------------------------------
        # Final result
        # -------------------------------------------------

        print(
            "\n========================================"
        )

        print(
            "Risk Level:",
            risk_level
        )

        print(
            "Total Findings:",
            total
        )

        print(
            "========================================"
        )


        return {

            "agent":
                self.name,

            "status":
                "RISK_FOUND",

            "commit":
                commit,

            "risk_level":
                risk_level,

            "findings":
                unique_signals,

            "summary": {

                "database":
                    database_count,

                "performance":
                    performance_count,

                "configuration":
                    configuration_count

            }

        }


# =========================================================
# DIRECT EXECUTION
# =========================================================

if __name__ == "__main__":

    agent = CodeAgent()

    result = agent.analyze()


    print(
        "\n========================================"
    )

    print(
        "         CODE AGENT COMPLETED"
    )

    print(
        "========================================\n"
    )

    print(
        "Final Status:",
        result["status"]
    )


    if "risk_level" in result:

        print(
            "Risk Level:",
            result["risk_level"]
        )

    print(
        "Findings:",
        len(
            result.get(
                "findings",
                []
            )
        )
    )