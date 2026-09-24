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

    def execute_agent(self, agent, agent_name):

        print("\n----------------------------------------")
        print(f"Executing {agent_name}")
        print("----------------------------------------")

        try:

            # Most AegisAI agents use investigate()
            if hasattr(agent, "investigate"):

                return agent.investigate()


            # Some agents may use analyze()
            elif hasattr(agent, "analyze"):

                return agent.analyze()


            # Some agents may use run()
            elif hasattr(agent, "run"):

                return agent.run()


            else:

                print(
                    f"❌ {agent_name} does not expose "
                    "investigate(), analyze(), or run()."
                )

                return {
                    "agent": agent_name,
                    "status": "METHOD_NOT_FOUND"
                }


        except Exception as error:

            print(f"❌ {agent_name} failed:")

            print(
                type(error).__name__,
                ":",
                error
            )

            return {
                "agent": agent_name,
                "status": "ERROR",
                "error": str(error)
            }


    # =====================================================
    # RUN FULL INVESTIGATION
    # =====================================================

    def run(self):

        print("\n========================================")
        print("        AEGISAI ORCHESTRATOR")
        print("========================================\n")

        print("Orchestrator:", self.name)
        print("Role:", self.role)


        # =================================================
        # 1. METRICS AGENT
        # =================================================

        print("\n[1/7] Running Metrics Agent...")

        metrics_agent = MetricsAgent()

        metrics_result = self.execute_agent(
            metrics_agent,
            "MetricsAgent"
        )


        # =================================================
        # 2. LOG AGENT
        # =================================================

        print("\n[2/7] Running Log Agent...")

        log_agent = LogAgent()

        log_result = self.execute_agent(
            log_agent,
            "LogAgent"
        )


        # =================================================
        # 3. DEPLOYMENT AGENT
        # =================================================

        print("\n[3/7] Running Deployment Agent...")

        deployment_agent = DeploymentAgent()

        deployment_result = self.execute_agent(
            deployment_agent,
            "DeploymentAgent"
        )


        # =================================================
        # 4. CODE AGENT
        # =================================================

        print("\n[4/7] Running Code Agent...")

        code_agent = CodeAgent()

        code_result = self.execute_agent(
            code_agent,
            "CodeAgent"
        )


        # =================================================
        # 5. ROOT CAUSE AGENT
        # =================================================

        print("\n[5/7] Running Root Cause Agent...")

        root_cause_agent = RootCauseAgent()

        root_cause_result = self.execute_agent(
            root_cause_agent,
            "RootCauseAgent"
        )


        # =================================================
        # 6. KNOWLEDGE AGENT
        # =================================================

        print("\n[6/7] Running Knowledge Agent...")

        knowledge_agent = KnowledgeAgent()

        knowledge_result = self.execute_agent(
            knowledge_agent,
            "KnowledgeAgent"
        )


        # =================================================
        # 7. REMEDIATION AGENT
        # =================================================

        print("\n[7/7] Running Remediation Agent...")

        remediation_agent = RemediationAgent()

        remediation_result = self.execute_agent(
            remediation_agent,
            "RemediationAgent"
        )


        # =================================================
        # INVESTIGATION SUMMARY
        # =================================================

        print("\n========================================")
        print("       AEGISAI INVESTIGATION SUMMARY")
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
        print("       AEGISAI FINAL INCIDENT RESULT")
        print("========================================\n")


        # -------------------------------------------------
        # ROOT CAUSE
        # -------------------------------------------------

        print("ROOT CAUSE")

        if "confidence" in root_cause_result:

            print(
                "Confidence:",
                root_cause_result["confidence"]
            )


        if "root_cause" in root_cause_result:

            print(
                "Assessment:",
                root_cause_result["root_cause"]
            )


        if "message" in root_cause_result:

            print(
                "Message:",
                root_cause_result["message"]
            )


        # -------------------------------------------------
        # KNOWLEDGE
        # -------------------------------------------------

        print("\nKNOWLEDGE")

        if "match_count" in knowledge_result:

            print(
                "Historical Matches:",
                knowledge_result["match_count"]
            )


        if "matches" in knowledge_result:

            for index, match in enumerate(
                knowledge_result["matches"],
                start=1
            ):

                print(
                    f"\nHistorical Match {index}:"
                )

                if isinstance(match, dict):

                    print(
                        "Incident:",
                        match.get(
                            "incident_id",
                            "UNKNOWN"
                        )
                    )

                    print(
                        "Title:",
                        match.get(
                            "title",
                            "UNKNOWN"
                        )
                    )

                    print(
                        "Root Cause:",
                        match.get(
                            "root_cause",
                            "UNKNOWN"
                        )
                    )

                    print(
                        "Resolution:",
                        match.get(
                            "resolution",
                            "UNKNOWN"
                        )
                    )


        # -------------------------------------------------
        # REMEDIATION
        # -------------------------------------------------

        print("\nREMEDIATION")

        if "action_count" in remediation_result:

            print(
                "Recommended Actions:",
                remediation_result["action_count"]
            )

        elif "actions_generated" in remediation_result:

            print(
                "Recommended Actions:",
                remediation_result["actions_generated"]
            )

        elif "actions" in remediation_result:

            print(
                "Recommended Actions:",
                len(remediation_result["actions"])
            )


        # =================================================
        # RETURN COMPLETE INVESTIGATION
        # =================================================

        return {

            "orchestrator": self.name,

            "status": "COMPLETED",

            "metrics": metrics_result,

            "logs": log_result,

            "deployments": deployment_result,

            "code": code_result,

            "root_cause": root_cause_result,

            "knowledge": knowledge_result,

            "remediation": remediation_result

        }


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    orchestrator = AegisOrchestrator()

    result = orchestrator.run()


    print("\n========================================")
    print("      ORCHESTRATION COMPLETED")
    print("========================================\n")

    print(
        "Final Orchestrator Status:",
        result["status"]
    )