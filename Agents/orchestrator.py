from pathlib import Path
import sys


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# IMPORT AGENTS
# =========================================================

from Agents.metrics_agent import MetricsAgent
from Agents.log_agent import LogAgent
from Agents.deployment_agent import DeploymentAgent
from Agents.code_agent import CodeAgent
from Agents.root_cause_agent import RootCauseAgent
from Agents.knowledge_agent import KnowledgeAgent
from Agents.remediation_agent import RemediationAgent


# =========================================================
# AEGISAI ORCHESTRATOR
# =========================================================

class AegisOrchestrator:

    def __init__(self):

        self.name = "AegisOrchestrator"

        self.role = (
            "Coordinate multiple specialized agents "
            "to investigate production incidents"
        )

    # =====================================================
    # SAFE AGENT EXECUTION
    # =====================================================

    def execute_agent(
        self,
        agent,
        agent_name
    ):

        print("\n----------------------------------------")
        print(
            f"Executing {agent_name}"
        )
        print("----------------------------------------")

        try:

            if hasattr(
                agent,
                "investigate"
            ):

                return agent.investigate()

            elif hasattr(
                agent,
                "analyze"
            ):

                return agent.analyze()

            elif hasattr(
                agent,
                "run"
            ):

                return agent.run()

            else:

                print(
                    f"{agent_name} does not expose "
                    "investigate(), analyze(), or run()."
                )

                return {

                    "agent":
                        agent_name,

                    "status":
                        "METHOD_NOT_FOUND"
                }

        except Exception as error:

            print(
                f"{agent_name} failed:"
            )

            print(
                type(error).__name__,
                ":",
                error
            )

            return {

                "agent":
                    agent_name,

                "status":
                    "ERROR",

                "error":
                    str(error)
            }

    # =====================================================
    # RUN FULL INVESTIGATION
    # =====================================================

    def run(self):

        print("\n========================================")
        print("        AEGISAI ORCHESTRATOR")
        print("========================================\n")

        print(
            "Orchestrator:",
            self.name
        )

        print(
            "Role:",
            self.role
        )

        # =================================================
        # 1. METRICS AGENT
        # =================================================

        print(
            "\n[1/7] Running Metrics Agent..."
        )

        metrics_agent = MetricsAgent()

        metrics_result = self.execute_agent(
            metrics_agent,
            "MetricsAgent"
        )

        # =================================================
        # 2. LOG AGENT
        # =================================================

        print(
            "\n[2/7] Running Log Agent..."
        )

        log_agent = LogAgent()

        log_result = self.execute_agent(
            log_agent,
            "LogAgent"
        )

        # =================================================
        # 3. DEPLOYMENT AGENT
        # =================================================

        print(
            "\n[3/7] Running Deployment Agent..."
        )

        deployment_agent = (
            DeploymentAgent()
        )

        deployment_result = (
            self.execute_agent(
                deployment_agent,
                "DeploymentAgent"
            )
        )

        # =================================================
        # 4. CODE AGENT
        # =================================================

        print(
            "\n[4/7] Running Code Agent..."
        )

        code_agent = CodeAgent()

        code_result = self.execute_agent(
            code_agent,
            "CodeAgent"
        )

        # =================================================
        # 5. ROOT CAUSE AGENT
        # =================================================

        print(
            "\n[5/7] Running Root Cause Agent..."
        )

        root_cause_agent = (
            RootCauseAgent()
        )

        root_cause_result = (
            self.execute_agent(
                root_cause_agent,
                "RootCauseAgent"
            )
        )

        # =================================================
        # 6. KNOWLEDGE AGENT
        # =================================================

        print(
            "\n[6/7] Running Knowledge Agent..."
        )

        knowledge_agent = (
            KnowledgeAgent()
        )

        knowledge_result = (
            self.execute_agent(
                knowledge_agent,
                "KnowledgeAgent"
            )
        )

        # =================================================
        # 7. REMEDIATION AGENT
        # =================================================

        print(
            "\n[7/7] Running Remediation Agent..."
        )

        remediation_agent = (
            RemediationAgent()
        )

        # IMPORTANT:
        # Pass previous agent results to remediation

        remediation_result = (
            remediation_agent.investigate(
                metrics_result=metrics_result,
                log_result=log_result,
                deployment_result=deployment_result,
                root_cause_result=root_cause_result
            )
        )

        # =================================================
        # INVESTIGATION SUMMARY
        # =================================================

        print("\n========================================")
        print(
            "       AEGISAI INVESTIGATION SUMMARY"
        )
        print("========================================\n")

        print(
            "Metrics Agent:",
            metrics_result.get(
                "status",
                "UNKNOWN"
            )
        )

        print(
            "Log Agent:",
            log_result.get(
                "status",
                "UNKNOWN"
            )
        )

        print(
            "Deployment Agent:",
            deployment_result.get(
                "status",
                "UNKNOWN"
            )
        )

        print(
            "Code Agent:",
            code_result.get(
                "status",
                "UNKNOWN"
            )
        )

        print(
            "Root Cause Agent:",
            root_cause_result.get(
                "status",
                "UNKNOWN"
            )
        )

        print(
            "Knowledge Agent:",
            knowledge_result.get(
                "status",
                "UNKNOWN"
            )
        )

        print(
            "Remediation Agent:",
            remediation_result.get(
                "status",
                "UNKNOWN"
            )
        )

        # =================================================
        # FINAL INCIDENT RESULT
        # =================================================

        print("\n========================================")
        print(
            "       AEGISAI FINAL INCIDENT RESULT"
        )
        print("========================================\n")

        # =================================================
        # ROOT CAUSE
        # =================================================

        print("ROOT CAUSE")

        print(
            "Confidence:",
            root_cause_result.get(
                "confidence",
                "UNKNOWN"
            )
        )

        print(
            "Assessment:",
            root_cause_result.get(
                "root_cause",
                root_cause_result.get(
                    "message",
                    "UNKNOWN"
                )
            )
        )

        # =================================================
        # KNOWLEDGE
        # =================================================

        print("\nKNOWLEDGE")

        knowledge_matches = (
            knowledge_result.get(
                "matches",
                []
            )
        )

        print(
            "Historical Matches:",
            len(knowledge_matches)
        )

        for index, match in enumerate(
            knowledge_matches,
            start=1
        ):

            incident = match.get(
                "incident",
                {}
            )

            print(
                f"\nHistorical Match {index}:"
            )

            print(
                "Incident:",
                incident.get(
                    "incident_id",
                    "UNKNOWN"
                )
            )

            print(
                "Title:",
                incident.get(
                    "title",
                    "UNKNOWN"
                )
            )

            print(
                "Service:",
                incident.get(
                    "service",
                    "UNKNOWN"
                )
            )

            print(
                "Severity:",
                incident.get(
                    "severity",
                    "UNKNOWN"
                )
            )

            print(
                "Root Cause:",
                incident.get(
                    "root_cause",
                    "UNKNOWN"
                )
            )

            print(
                "Resolution:",
                incident.get(
                    "resolution",
                    "UNKNOWN"
                )
            )

            print(
                "Affected Version:",
                incident.get(
                    "affected_version",
                    "UNKNOWN"
                )
            )

        # =================================================
        # REMEDIATION
        # =================================================

        print("\nREMEDIATION")

        remediation_actions = (
            remediation_result.get(
                "actions",
                []
            )
        )

        print(
            "Recommended Actions:",
            len(remediation_actions)
        )

        for index, action in enumerate(
            remediation_actions,
            start=1
        ):

            print(
                f"{index}. "
                f"[{action.get('priority', 'UNKNOWN')}] "
                f"{action.get('action', 'UNKNOWN')}"
            )

        # =================================================
        # COMPLETE RESULT
        # =================================================

        result = {

            "orchestrator":
                self.name,

            "status":
                "COMPLETED",

            "metrics":
                metrics_result,

            "logs":
                log_result,

            "deployments":
                deployment_result,

            "code":
                code_result,

            "root_cause":
                root_cause_result,

            "knowledge":
                knowledge_result,

            "remediation":
                remediation_result
        }

        return result


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    orchestrator = AegisOrchestrator()

    result = orchestrator.run()

    print("\n========================================")
    print(
        "      ORCHESTRATION COMPLETED"
    )
    print("========================================\n")

    print(
        "Final Orchestrator Status:",
        result["status"]
    )