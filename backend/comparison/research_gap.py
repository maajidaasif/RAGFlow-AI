from llm.local_llm import ask_llm
from services.retriever import Retriever


class ResearchGapEngine:

    def __init__(self):
        self.retriever = Retriever()

    def detect_research_gap(self):

        context = self.retriever.retrieve_context(
            question="""
Find the research gaps, limitations, missing problems,
future opportunities and unexplored areas discussed
across all uploaded research papers.
""",
            top_k=12
        )

        if not context:
            return {
                "success": False,
                "message": "No research papers found."
            }

        prompt = """
You are an expert AI research assistant.

First identify the overall research domain.

Examples:
- Natural Language Processing
- Computer Vision
- Healthcare AI
- Cyber Security
- Robotics
- Data Mining

Then generate the report exactly in this format.

Domain:
<Detected Domain>

Research Gaps
- ...

Limitations
- ...

Future Research Opportunities
- ...

Potential Research Ideas
- ...

Return only the report.
"""

        answer = ask_llm(
            question=prompt,
            context=context,
            max_tokens=800
        )

        # Default domain
        domain = "Unknown"

        try:
            lines = answer.splitlines()

            for i, line in enumerate(lines):
                if line.strip().lower().startswith("domain"):
                    # Get the first non-empty line after "Domain:"
                    for next_line in lines[i + 1:]:
                        if next_line.strip():
                            domain = next_line.strip()
                            break
                    break

        except Exception:
            pass

        return {
            "success": True,
            "domain": domain,
            "research_gap": answer
        }