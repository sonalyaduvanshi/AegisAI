from pathlib import Path
import sys
import json


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# KNOWLEDGE SOURCES
# =========================================================

INCIDENT_FILE = (
    PROJECT_ROOT
    / "data"
    / "incidents"
    / "incidents.json"
)

README_FILE = PROJECT_ROOT / "README.md"


# =========================================================
# KNOWLEDGE AGENT
# =========================================================

class KnowledgeAgent:

    def __init__(self):

        self.name = "KnowledgeAgent"

        self.role = (
            "Retrieve relevant historical incident knowledge "
            "and engineering guidance for production failures"
        )


    # =====================================================
    # LOAD INCIDENT KNOWLEDGE
    # =====================================================

    def load_incidents(self):

        if not INCIDENT_FILE.exists():

            print(
                "\n⚠️ Incident knowledge file not found:"
            )

            print(INCIDENT_FILE)

            return []


        try:

            with open(
                INCIDENT_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)


            if isinstance(data, list):

                return data


            if isinstance(data, dict):

                if "incidents" in data:

                    return data["incidents"]

                return [data]


        except Exception as error:

            print(
                "\n❌ Could not load incident knowledge:"
            )

            print(error)


        return []


    # =====================================================
    # SEARCH KNOWLEDGE
    # =====================================================

    def search_knowledge(
        self,
        query
    ):

        incidents = self.load_incidents()

        query_words = set(
            str(query)
            .lower()
            .split()
        )


        results = []


        for incident in incidents:

            text = json.dumps(
                incident
            ).lower()


            score = 0


            for word in query_words:

                if len(word) > 2 and word in text:

                    score += 1


            if score > 0:

                results.append(
                    {
                        "score": score,
                        "incident": incident
                    }
                )


        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )


        return results


    # =====================================================
    # INVESTIGATE
    # =====================================================

    def investigate(
        self,
        query="database authentication deployment"
    ):

        print("\n========================================")
        print("        KNOWLEDGE AGENT")
        print("========================================\n")


        print(
            f"Agent: {self.name}"
        )

        print(
            f"Role: {self.role}"
        )


        print(
            "\nKnowledge query:"
        )

        print(query)


        # =================================================
        # LOAD KNOWLEDGE
        # =================================================

        incidents = self.load_incidents()


        print(
            "\nHistorical incidents available:",
            len(incidents)
        )


        # =================================================
        # SEARCH
        # =================================================

        results = self.search_knowledge(
            query
        )


        print("\n========================================")
        print("       KNOWLEDGE RETRIEVAL")
        print("========================================")


        if not results:

            print(
                "\n⚠️ No matching historical incidents found."
            )

            return {

                "agent": self.name,

                "status": "NO_KNOWLEDGE_FOUND",

                "query": query,

                "matches": []

            }


        # =================================================
        # DISPLAY MATCHES
        # =================================================

        for index, result in enumerate(
            results[:5],
            start=1
        ):

            incident = result["incident"]

            score = result["score"]


            print(
                f"\n[{index}] "
                f"Knowledge Match"
            )

            print(
                "Relevance Score:",
                score
            )


            if isinstance(
                incident,
                dict
            ):

                for key, value in incident.items():

                    print(
                        f"{key}: {value}"
                    )

            else:

                print(
                    "Incident:",
                    incident
                )


        # =================================================
        # RETURN STRUCTURED KNOWLEDGE
        # =================================================

        matches = []


        for result in results[:5]:

            matches.append(
                {
                    "score": result["score"],
                    "incident": result["incident"]
                }
            )


        return {

            "agent": self.name,

            "status": "KNOWLEDGE_FOUND",

            "query": query,

            "match_count": len(matches),

            "matches": matches

        }


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    agent = KnowledgeAgent()


    result = agent.investigate(
        "database authentication deployment"
    )


    print("\n========================================")
    print("      KNOWLEDGE AGENT COMPLETED")
    print("========================================\n")


    print(
        "Final Agent Status:",
        result["status"]
    )


    print(
        "Knowledge Matches:",
        result.get(
            "match_count",
            0
        )
    )