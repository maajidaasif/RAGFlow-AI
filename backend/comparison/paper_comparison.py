import re

from llm.local_llm import ask_llm
from services.retriever import Retriever
from literature.domain_detector import DomainDetector


class PaperComparisonEngine:

    def __init__(self):

        self.retriever = Retriever()
        self.domain_detector = DomainDetector()

    def get_paper_names(self):

        paper_names = []

        for item in self.retriever.metadata:

            paper_name = item["paper_name"]

            if paper_name not in paper_names:
                paper_names.append(paper_name)

        return paper_names

    def clean_text(self, text):

        if text is None:
            return ""

        text = str(text)

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def extract_metrics(self, context):

        if context is None:
            return None

        patterns = [

            r"BLEU\s*(?:score)?\s*(?:of)?\s*[:=]?\s*(\d+\.\d+)",
            r"Accuracy\s*[:=]?\s*(\d+\.?\d*%)",
            r"Accuracy\s*[:=]?\s*(\d+\.\d+)",
            r"F1\s*(?:score)?\s*[:=]?\s*(\d+\.\d+)",
            r"ROUGE[- ]?[L12]?\s*[:=]?\s*(\d+\.\d+)",
            r"Precision\s*[:=]?\s*(\d+\.\d+)",
            r"Recall\s*[:=]?\s*(\d+\.\d+)"

        ]

        results = []

        for pattern in patterns:

            matches = re.findall(
                pattern,
                context,
                flags=re.IGNORECASE
            )

            for match in matches:

                if match not in results:
                    results.append(match)

        if len(results) == 0:
            return None

        return "\n".join(results)

    def get_best_context(
        self,
        paper_name,
        query
    ):

        context = self.retriever.retrieve_context_by_paper(
            question=query,
            paper_name=paper_name,
            top_k=6
        )

        if context is None:
            return None

        context = self.clean_text(context)

        if context == "":
            return None

        return context

    def get_all_paper_summaries(self):

        paper_names = self.get_paper_names()

        summaries = []

        query = (
            "Summarize this research paper including "
            "objective, methodology, dataset, model, "
            "contributions, limitations and future work."
        )

        for paper_name in paper_names:

            context = self.get_best_context(
                paper_name=paper_name,
                query=query
            )

            if context:
                summaries.append(context)

        return summaries

    def get_prompt(
        self,
        category
    ):

        prompts = {

            "Methodology Comparison":
            """
        Extract ONLY the methodology used in this research paper.

        Return:
        - Model
        - Architecture
        - Approach

        Maximum 2 sentences.
        """,

            "Accuracy Comparison":
            """
        Extract ONLY the evaluation results mentioned in the context.

        Rules:
        - Copy ONLY numerical values from the context.
        - Include BLEU, Accuracy, F1, Precision, Recall, ROUGE and Benchmark scores if available.
        - Do NOT explain.
        - Do NOT summarize.
        - Do NOT infer.
        - If multiple values exist, list all of them.

        Example:

        BLEU:
        28.4
        41.0

        Accuracy:
        92.5%

        If no numerical result exists, reply:
        I could not find the answer in the uploaded research papers.
        """,

            "Dataset Comparison":
            """
        Extract ONLY the datasets used.

        Return:
        - Dataset names
        - Corpus names
        - Training data

        Do not explain.
        """,

            "Advantages":
            """
        Extract ONLY the advantages or strengths
        of the proposed method.

        Maximum 2 sentences.
        """,

            "Limitations":
            """
        Extract ONLY the limitations,
        weaknesses or challenges.

        Maximum 2 sentences.
        """,

            "Future Work Comparison":
            """
        Extract ONLY the future work
        mentioned by the authors.

        Maximum 2 sentences.
        """
        }

        return prompts.get(
            category,
            "Summarize the context."
        )

    def summarize_context(
        self,
        context,
        category
    ):

        if context is None:

            return (
                "Not available in the provided context."
            )

        # Use Regex first for Accuracy
        if category == "Accuracy Comparison":

            metrics = self.extract_metrics(
                context
            )

            if metrics is not None:

                return metrics

        question = self.get_prompt(
            category
        )

        answer = ask_llm(
            question=question,
            context=context,
            max_tokens=120
        )

        answer = self.clean_text(
            answer
        )

        if answer == "":

            return (
                "Not available in the provided context."
            )

        return answer

    def compare_category(
        self,
        category_name,
        query
    ):

        paper_names = self.get_paper_names()

        results = []

        for paper_name in paper_names:

            context = self.get_best_context(
                paper_name=paper_name,
                query=query
            )

            print("\n========================")
            print("CATEGORY:", category_name)
            print("PAPER:", paper_name)

            if context is not None:

                print("CONTEXT PREVIEW:")
                print(context[:500])

            else:

                print("No context retrieved.")

            summary = self.summarize_context(
                context=context,
                category=category_name
            )

            print("\nLLM OUTPUT:")
            print(summary)

            results.append(
                f"{paper_name}:\n{summary}"
            )

        return (
            f"{category_name}\n\n"
            + "\n\n".join(results)
        )

    def compare_papers(self):

        categories = [

            (
                "Methodology Comparison",
                "What methodology, model architecture, model, approach, Transformer architecture, encoder, decoder, attention mechanism is used in this research paper?"
            ),

            (
                "Accuracy Comparison",
                "What accuracy, BLEU score, F1 score, benchmark result, evaluation result or performance score is reported in this research paper?"
            ),

            (
                "Dataset Comparison",
                "What dataset, training dataset, benchmark dataset, corpus, BooksCorpus, Wikipedia, Common Crawl, CC-News, OpenWebText, WMT or GLUE dataset is used in this research paper?"
            ),

            (
                "Advantages",
                "What are the main advantages, strengths, benefits, improvements or contributions of the proposed method?"
            ),

            (
                "Limitations",
                "What are the limitations, weaknesses, drawbacks, challenges or problems discussed in this research paper?"
            ),

            (
                "Future Work Comparison",
                "What future work, future research, future improvements or future directions are suggested by the authors?"
            )

        ]

        # ---------------------------------------
        # Detect Research Domain
        # ---------------------------------------

        paper_summaries = self.get_all_paper_summaries()

        domain = self.domain_detector.detect_domain(
            paper_summaries
        )

        print("\n===================================")
        print("DETECTED DOMAIN:", domain)
        print("===================================\n")

        # ---------------------------------------
        # Generate Comparison
        # ---------------------------------------

        comparison_results = []

        for category_name, query in categories:

            result = self.compare_category(
                category_name=category_name,
                query=query
            )

            comparison_results.append(result)

        final_report = (

            "\n\n"

            "========================================"

            "\n\n"

        ).join(comparison_results)

        return {

            "success": True,

            "domain": domain,

            "comparison": final_report

        }
