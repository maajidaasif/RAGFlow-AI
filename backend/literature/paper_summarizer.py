"""
Module 10 - Paper Summarizer

Summarizes each uploaded research paper.
If a summary already exists, it is loaded from disk
instead of regenerating it.
"""

from services.retriever import Retriever
from llm.local_llm import ask_llm
from summaries.summary_storage import SummaryStorage


class PaperSummarizer:

    def __init__(self):

        self.retriever = Retriever()
        self.storage = SummaryStorage()

    # ---------------------------------
    # Summarize One Paper
    # ---------------------------------
    def summarize_paper(self, paper_name):

        # Check if summary already exists
        saved_summary = self.storage.load_summary(
            paper_name
        )

        if saved_summary:

            print(f"Loaded summary: {paper_name}")

            return saved_summary

        print(f"Generating summary: {paper_name}")

        context = self.retriever.retrieve_context_by_paper(
            question="Summarize this research paper.",
            paper_name=paper_name,
            top_k=10
        )

        if context is None:
            return None

        prompt = """
You are an expert academic research paper analyst.

You are analyzing ONLY ONE uploaded research paper.

IMPORTANT RULES

1. Use ONLY the provided research paper context.
2. Never use outside knowledge.
3. Never invent information.
4. Never guess missing details.
5. If a section is unavailable, write:
   "Not discussed in the uploaded research paper."

Generate the following sections.

# Paper Title

# Research Problem

# Research Objective

# Methodology

# Dataset (if available)

# Model / Algorithm Used

# Main Contributions

# Advantages

# Limitations

# Future Work

Write concise academic content.
"""

        summary = ask_llm(
            question=prompt,
            context=context,
            max_tokens=700
        )

        # Save summary
        self.storage.save_summary(
            paper_name,
            summary
        )

        return summary