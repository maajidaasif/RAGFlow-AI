"""
Module 10 - Literature Survey Generator

This module generates an integrated literature survey
from summaries of uploaded research papers.
"""

from services.retriever import Retriever
from llm.local_llm import ask_llm
from literature.paper_summarizer import PaperSummarizer
from literature.domain_detector import DomainDetector


class LiteratureSurveyGenerator:

    def __init__(self):
        self.retriever = Retriever()
        self.paper_summarizer = PaperSummarizer()
        self.domain_detector = DomainDetector()

    # ---------------------------------
    # Generate summaries for all papers
    # ---------------------------------
    def get_all_paper_summaries(self):

        unique_papers = []

        for item in self.retriever.metadata:
            if item["paper_name"] not in unique_papers:
                unique_papers.append(item["paper_name"])

        summaries = []

        for i, paper in enumerate(unique_papers, start=1):

            print(f"Summarizing {paper}...")

            summary = self.paper_summarizer.summarize_paper(paper)

            if summary:

                summaries.append(
                    f"""
==================================================
Paper {i}
File Name : {paper}
==================================================

{summary}
"""
                )

        return summaries

    # ---------------------------------
    # Literature Survey Prompt
    # ---------------------------------
    def build_prompt(self, domain):

        return f"""
You are an expert academic research assistant.

Research Domain:
{domain}

You are provided ONLY with summaries of uploaded research papers.

==================================================
CRITICAL INSTRUCTIONS
==================================================

1. Use ONLY the uploaded paper summaries.

2. NEVER use your own knowledge.

3. NEVER mention any paper, author, dataset,
algorithm, model or technique that is NOT present
in the uploaded summaries.

4. NEVER mix another research domain.

Example:
If the detected domain is
Natural Language Processing,
DO NOT discuss Computer Vision,
Vision Transformers,
Image Classification,
Object Detection,
Medical Imaging,
or any unrelated topic.

5. Every statement must be supported by the uploaded papers.

6. If information is unavailable, write exactly:

"Not discussed in the uploaded research papers."

7. Do NOT invent citations.

8. Do NOT invent results.

9. Do NOT invent future work beyond what is supported.

==================================================
TASK
==================================================

Generate ONE integrated literature survey.

DO NOT summarize paper by paper.

Instead, synthesize the information across all papers.

Generate the report using the following headings exactly.

# Introduction

# Research Trends

# Existing Methods

# Comparative Analysis

# Research Gaps

# Future Research Directions

# Conclusion

Write in formal IEEE-style academic language.

Return ONLY the literature survey.
"""

    # ---------------------------------
    # Generate Literature Survey
    # ---------------------------------
    def generate_literature_survey(self):

        summaries = self.get_all_paper_summaries()

        if not summaries:
            return {
                "success": False,
                "message": "No research papers found."
            }

        # Detect Domain
        domain = self.domain_detector.detect_domain(summaries)

        print("=" * 60)
        print("Detected Domain :", domain)
        print("=" * 60)

        prompt = self.build_prompt(domain)

        report = ask_llm(
            question=prompt,
            context="\n\n".join(summaries),
            max_tokens=1800
        )

        return {
            "success": True,
            "domain": domain,
            "literature_survey": report
        }