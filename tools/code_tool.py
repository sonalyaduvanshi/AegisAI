from pathlib import Path
import subprocess
import re


class CodeTool:

    def __init__(self):

        self.project_root = (
            Path(__file__).resolve().parent.parent
        )


    # =====================================================
    # RUN GIT COMMAND
    # =====================================================

    def run_git(self, *args):

        result = subprocess.run(
            ["git", *args],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if result.returncode != 0:

            raise RuntimeError(
                result.stderr.strip()
            )

        return result.stdout.strip()


    # =====================================================
    # RECENT COMMITS
    # =====================================================

    def get_recent_commits(self, limit=5):

        output = self.run_git(
            "log",
            f"-{limit}",
            "--pretty=format:%H|%s"
        )

        commits = []

        if not output:
            return commits


        for line in output.splitlines():

            parts = line.split(
                "|",
                1
            )

            if len(parts) != 2:
                continue

            commits.append({
                "commit": parts[0],
                "message": parts[1]
            })


        return commits


    # =====================================================
    # GET CHANGED FILES
    # =====================================================

    def get_changed_files(
        self,
        commit
    ):

        # -------------------------------------------------
        # Initial commit
        # -------------------------------------------------

        parents = self.run_git(
            "rev-list",
            "--parents",
            "-n",
            "1",
            commit
        ).split()

        if len(parents) == 1:

            output = self.run_git(
                "show",
                "--format=",
                "--name-status",
                commit
            )

        else:

            parent = parents[1]

            output = self.run_git(
                "diff",
                "--name-status",
                parent,
                commit
            )


        files = []


        for line in output.splitlines():

            if not line.strip():
                continue

            parts = line.split(
                "\t",
                1
            )

            if len(parts) != 2:
                continue

            status = parts[0]
            file_name = parts[1]


            files.append({
                "status": status,
                "file": file_name
            })


        return files


    # =====================================================
    # GET ACTUAL DIFF
    # =====================================================

    def get_diff(
        self,
        commit
    ):

        parents = self.run_git(
            "rev-list",
            "--parents",
            "-n",
            "1",
            commit
        ).split()


        if len(parents) == 1:

            diff = self.run_git(
                "show",
                "--format=",
                "--unified=3",
                commit
            )

        else:

            parent = parents[1]

            diff = self.run_git(
                "diff",
                parent,
                commit,
                "--unified=3"
            )


        return diff


    # =====================================================
    # RISK PATTERN ANALYSIS
    # =====================================================

    def analyze_diff(
        self,
        diff
    ):

        findings = []


        # -------------------------------------------------
        # Only inspect ADDED lines
        # -------------------------------------------------

        added_lines = []

        for line in diff.splitlines():

            if (
                line.startswith("+")
                and not line.startswith("+++")
            ):

                added_lines.append(
                    line[1:]
                )


        added_text = "\n".join(
            added_lines
        )


        # -------------------------------------------------
        # DATABASE PATTERNS
        # -------------------------------------------------

        database_patterns = {

            r"\bSELECT\b":
                "SQL SELECT query added",

            r"\bINSERT\b":
                "SQL INSERT query added",

            r"\bUPDATE\b":
                "SQL UPDATE query added",

            r"\bDELETE\b":
                "SQL DELETE query added",

            r"\bSELECT\s+\*":
                "SELECT * query detected",

            r"\bJOIN\b":
                "SQL JOIN detected",

            r"\bCREATE\s+INDEX\b":
                "Database index change detected",

            r"\bconnection\b":
                "Database connection logic changed",

            r"\bpool\b":
                "Connection pool logic changed",

            r"\bexecute\s*\(":
                "Database execute operation detected"
        }


        # -------------------------------------------------
        # PERFORMANCE PATTERNS
        # -------------------------------------------------

        performance_patterns = {

            r"\bwhile\s*\(":
                "while loop added",

            r"\bfor\s+\w+\s+in\s+":
                "for-loop added",

            r"\btime\.sleep\s*\(":
                "Blocking sleep detected",

            r"\btimeout\b":
                "Timeout configuration changed",

            r"\bcache\b":
                "Cache logic changed",

            r"\blatency\b":
                "Latency-related logic changed"
        }


        # -------------------------------------------------
        # CONFIGURATION
        # -------------------------------------------------

        configuration_patterns = {

            r"\.env":
                "Environment configuration changed",

            r"\bos\.environ":
                "Environment variable access changed",

            r"\bconfig\b":
                "Configuration logic changed"
        }


        # -------------------------------------------------
        # SECURITY
        # -------------------------------------------------

        security_patterns = {

            r"\bpassword\b":
                "Password-related code changed",

            r"\bsecret\b":
                "Secret-related code changed",

            r"\btoken\b":
                "Token-related code changed",

            r"\bapi[_-]?key\b":
                "API key-related code changed"
        }


        # -------------------------------------------------
        # RUN PATTERN DETECTION
        # -------------------------------------------------

        def scan_patterns(
            patterns,
            category
        ):

            for pattern, message in patterns.items():

                if re.search(
                    pattern,
                    added_text,
                    re.IGNORECASE
                ):

                    findings.append({

                        "category":
                            category,

                        "signal":
                            message
                    })


        scan_patterns(
            database_patterns,
            "DATABASE"
        )

        scan_patterns(
            performance_patterns,
            "PERFORMANCE"
        )

        scan_patterns(
            configuration_patterns,
            "CONFIGURATION"
        )

        scan_patterns(
            security_patterns,
            "SECURITY"
        )


        return findings


    # =====================================================
    # COMPLETE COMMIT ANALYSIS
    # =====================================================

    def analyze_commit(
        self,
        commit
    ):

        changed_files = (
            self.get_changed_files(
                commit
            )
        )


        diff = self.get_diff(
            commit
        )


        risk_signals = (
            self.analyze_diff(
                diff
            )
        )


        return {

            "commit":
                commit,

            "changed_files":
                changed_files,

            "diff":
                diff,

            "risk_signals":
                risk_signals
        }


# =========================================================
# DIRECT TEST
# =========================================================

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        "        AEGISAI CODE TOOL"
    )

    print(
        "========================================\n"
    )


    tool = CodeTool()


    commits = (
        tool.get_recent_commits(
            limit=5
        )
    )


    print(
        "Recent commits:\n"
    )


    for item in commits:

        print(
            f"{item['commit'][:7]} - "
            f"{item['message']}"
        )


    if commits:

        latest = commits[0]["commit"]


        print(
            "\nAnalyzing latest commit:",
            latest
        )


        result = (
            tool.analyze_commit(
                latest
            )
        )


        print(
            "\nChanged files:"
        )


        for item in result[
            "changed_files"
        ]:

            print(
                item["status"],
                item["file"]
            )


        print(
            "\nActual added-code risk signals:"
        )


        if not result[
            "risk_signals"
        ]:

            print(
                "✅ No risky code changes detected."
            )

        else:

            for signal in result[
                "risk_signals"
            ]:

                print(
                    "-",
                    signal["category"],
                    ":",
                    signal["signal"]
                )