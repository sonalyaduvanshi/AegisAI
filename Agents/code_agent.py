from pathlib import Path
import re


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# =========================================================
# CODE DIRECTORIES
# =========================================================

CODE_DIRECTORIES = [
    PROJECT_ROOT / "backend",
    PROJECT_ROOT / "src",
    PROJECT_ROOT / "app",
    PROJECT_ROOT / "api",
]


class CodeAgent:

    def __init__(self):

        self.name = "CodeAgent"

        self.role = (
            "Inspect application code for risky database, "
            "query, connection, and performance patterns"
        )


    # =====================================================
    # FIND SOURCE CODE
    # =====================================================

    def find_code_files(self):

        files = []

        for directory in CODE_DIRECTORIES:

            if directory.exists():

                for file in directory.rglob("*"):

                    if file.is_file():

                        if file.suffix.lower() in [
                            ".py",
                            ".js",
                            ".ts",
                            ".java",
                            ".sql"
                        ]:

                            files.append(file)

        return files


    # =====================================================
    # ANALYZE SINGLE FILE
    # =====================================================

    def analyze_file(self, file_path):

        findings = []

        try:

            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception:

            return findings


        # -------------------------------------------------
        # Database query patterns
        # -------------------------------------------------

        query_patterns = [

            (
                r"\.execute\s*\(",
                "Database execute() call detected"
            ),

            (
                r"SELECT\s+.*\s+FROM",
                "SQL SELECT query detected"
            ),

            (
                r"INSERT\s+INTO",
                "SQL INSERT query detected"
            ),

            (
                r"UPDATE\s+.*\s+SET",
                "SQL UPDATE query detected"
            ),

            (
                r"DELETE\s+FROM",
                "SQL DELETE query detected"
            ),

        ]


        for pattern, description in query_patterns:

            if re.search(
                pattern,
                content,
                re.IGNORECASE
            ):

                findings.append({

                    "file": str(file_path.relative_to(
                        PROJECT_ROOT
                    )),

                    "type": "DATABASE_QUERY",

                    "severity": "MEDIUM",

                    "finding": description

                })


        # -------------------------------------------------
        # SELECT *
        # -------------------------------------------------

        if re.search(
            r"SELECT\s+\*",
            content,
            re.IGNORECASE
        ):

            findings.append({

                "file": str(file_path.relative_to(
                    PROJECT_ROOT
                )),

                "type": "PERFORMANCE",

                "severity": "MEDIUM",

                "finding":
                    "SELECT * detected; unnecessary "
                    "columns may increase database load"

            })


        # -------------------------------------------------
        # Possible missing connection pooling
        # -------------------------------------------------

        connection_patterns = [

            r"create_engine\s*\(",

            r"connect\s*\(",

            r"MongoClient\s*\(",

            r"mysql\.connector",

            r"psycopg2\.connect"

        ]


        connection_found = False


        for pattern in connection_patterns:

            if re.search(
                pattern,
                content,
                re.IGNORECASE
            ):

                connection_found = True

                break


        if connection_found:

            findings.append({

                "file": str(file_path.relative_to(
                    PROJECT_ROOT
                )),

                "type": "DATABASE_CONNECTION",

                "severity": "MEDIUM",

                "finding":
                    "Database connection creation detected; "
                    "connection pooling should be reviewed"

            })


        # -------------------------------------------------
        # Potential unbounded query
        # -------------------------------------------------

        if re.search(
            r"SELECT\s+.*FROM\s+\w+",
            content,
            re.IGNORECASE
        ):

            if "LIMIT" not in content.upper():

                findings.append({

                    "file": str(file_path.relative_to(
                        PROJECT_ROOT
                    )),

                    "type": "QUERY_PERFORMANCE",

                    "severity": "MEDIUM",

                    "finding":
                        "SQL query without visible LIMIT; "
                        "large result sets may increase latency"

                })


        return findings


    # =====================================================
    # INVESTIGATE
    # =====================================================

    def investigate(self):

        print("\n========================================")
        print("            CODE AGENT")
        print("========================================\n")

        print(
            f"Agent: {self.name}"
        )

        print(
            f"Role: {self.role}"
        )


        # =================================================
        # FIND CODE
        # =================================================

        code_files = self.find_code_files()


        print("\nCode files discovered:")

        print(
            len(code_files)
        )


        if not code_files:

            print(
                "\n⚠️ No supported application "
                "source files found."
            )

            print(
                "\nSearched directories:"
            )

            for directory in CODE_DIRECTORIES:

                print(
                    "-",
                    directory
                )


            return {

                "agent": self.name,

                "status": "NO_CODE_FOUND",

                "findings": []

            }


        # =================================================
        # ANALYZE ALL FILES
        # =================================================

        all_findings = []


        for file_path in code_files:

            findings = self.analyze_file(
                file_path
            )

            all_findings.extend(
                findings
            )


        # =================================================
        # DISPLAY FINDINGS
        # =================================================

        print("\n========================================")
        print("        CODE INTELLIGENCE RESULTS")
        print("========================================")


        if not all_findings:

            print(
                "\n✅ No obvious risky "
                "patterns detected."
            )


            return {

                "agent": self.name,

                "status": "NO_RISK_FOUND",

                "finding_count": 0,

                "findings": []

            }


        print(
            f"\n⚠️ Findings detected: "
            f"{len(all_findings)}"
        )


        for finding in all_findings:

            print(
                "\n----------------------------------------"
            )

            print(
                "File:",
                finding["file"]
            )

            print(
                "Type:",
                finding["type"]
            )

            print(
                "Severity:",
                finding["severity"]
            )

            print(
                "Finding:",
                finding["finding"]
            )


        # =================================================
        # DETERMINE RISK LEVEL
        # =================================================

        high_count = sum(
            1
            for finding in all_findings
            if finding["severity"] == "HIGH"
        )

        medium_count = sum(
            1
            for finding in all_findings
            if finding["severity"] == "MEDIUM"
        )


        if high_count > 0:

            risk_level = "HIGH"

        elif medium_count > 0:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"


        # =================================================
        # FINAL CODE ASSESSMENT
        # =================================================

        print("\n========================================")
        print("          CODE RISK ASSESSMENT")
        print("========================================\n")

        print(
            "Risk Level:",
            risk_level
        )

        print(
            "Total Findings:",
            len(all_findings)
        )


        # =================================================
        # RETURN STRUCTURED RESULT
        # =================================================

        return {

            "agent": self.name,

            "status": "CODE_ANALYZED",

            "risk_level": risk_level,

            "finding_count": len(
                all_findings
            ),

            "findings": all_findings

        }


# =========================================================
# RUN CODE AGENT DIRECTLY
# =========================================================

if __name__ == "__main__":

    agent = CodeAgent()

    result = agent.investigate()


    print("\n========================================")
    print("         CODE AGENT COMPLETED")
    print("========================================\n")

    print(
        "Final Status:",
        result["status"]
    )

    print(
        "Risk Level:",
        result.get(
            "risk_level",
            "N/A"
        )
    )

    print(
        "Findings:",
        result.get(
            "finding_count",
            0
        )
    )