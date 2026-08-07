from models.analysis_model import Analysis
from database import db
from llm.local_llm import ask_llm


class ReportGenerator:

    def get_latest_analysis(self, analysis_type):

        return (
            Analysis.query
            .filter_by(analysis_type=analysis_type)
            .order_by(Analysis.created_at.desc())
            .first()
        )

    def generate_report(self):

        print("Reading latest Literature Survey...")

        literature = self.get_latest_analysis(
            "Literature Survey"
        )

        print("Reading latest Paper Comparison...")

        comparison = self.get_latest_analysis(
            "Paper Comparison"
        )

        print("Reading latest Research Gap...")

        gap = self.get_latest_analysis(
            "Research Gap Detection"
        )

        if literature is None:
            raise Exception(
                "Please generate Literature Survey first."
            )

        if comparison is None:
            raise Exception(
                "Please generate Paper Comparison first."
            )

        if gap is None:
            raise Exception(
                "Please generate Research Gap first."
            )

        context = f"""
==========================
LITERATURE SURVEY
==========================

{literature.result}

==========================
PAPER COMPARISON
==========================

{comparison.result}

==========================
RESEARCH GAP
==========================

{gap.result}
"""

        question = """
You are an experienced research analyst.

Generate a professional research report using ONLY the supplied context.

STRICT RULES

1. Do NOT invent any information.
2. Do NOT use outside knowledge.
3. Do NOT repeat the same points in multiple sections.
4. Use formal academic English.
5. Use only the uploaded papers.
6. Include ALL uploaded papers in the ranking whenever possible.
7. If some information is unavailable, write "Not Available".
8. Keep the report concise and professional.

Generate the report in Markdown.

# Executive Summary

- Write one well-structured paragraph summarizing the overall research.

# Key Findings

- Present 5–8 bullet points.
- Each point should describe a unique finding.
- Avoid repeating information.

# Best Paper Recommendation

Include:

- Paper Name
- Reason for Recommendation
- Major Strengths
- Possible Limitations

# Paper Ranking

Rank every uploaded paper.

Use the format:

1. Paper Name
   - Strengths
   - Reason for Rank

2. Paper Name
   - Strengths
   - Reason for Rank

Continue until every uploaded paper is ranked.

# Final Conclusion

Summarize the overall contribution of the uploaded papers in one paragraph.

# Future Scope

Provide 4–6 bullet points describing future research opportunities based ONLY on the supplied context.

Return ONLY Markdown.
"""

        print("Generating Final Report...")

        report = ask_llm(
            question=question,
            context=context,
            max_tokens=1000
        )

        print("Saving Report...")

        analysis = Analysis(
            analysis_type="Research Report",
            analysis_name="Research Report",
            domain=literature.domain,
            papers=literature.papers,
            result=report
        )

        db.session.add(analysis)
        db.session.commit()

        print("Report Generated Successfully.")

        return report