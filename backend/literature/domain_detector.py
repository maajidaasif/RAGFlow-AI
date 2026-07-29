from llm.local_llm import ask_llm


class DomainDetector:

    def detect_domain(self, paper_summaries):
        """
        Detect the overall research domain
        from all uploaded paper summaries.
        """

        if not paper_summaries:
            return "Unknown"

        # Limit each paper summary to avoid exceeding the model context window
        limited_summaries = []

        for summary in paper_summaries:

            if summary:
                limited_summaries.append(summary[:300])

        summaries = "\n\n".join(limited_summaries)

        question = f"""
You are a research domain classifier.

Based ONLY on the paper summaries below,
identify the SINGLE overall research domain.

Rules:
- Return only ONE domain.
- Return ONLY the domain name.
- Do not explain.
- Do not write complete sentences.

Possible domains include:

Artificial Intelligence
Machine Learning
Deep Learning
Natural Language Processing
Computer Vision
Medical
Healthcare
Internet of Things (IoT)
Cybersecurity
Cloud Computing
Data Mining
Software Engineering
Robotics
Agriculture

Paper Summaries:

{summaries}
"""

        try:

            domain = ask_llm(
                question=question,
                context="",
                max_tokens=20
            )

            if domain is None:
                return "Unknown"

            domain = str(domain).strip()

            if domain == "":
                return "Unknown"

            return domain

        except Exception as e:

            print(f"Domain Detection Error: {e}")

            return "Unknown"