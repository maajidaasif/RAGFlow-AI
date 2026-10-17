import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.retriever import Retriever
import re


retriever = Retriever()

paper_name = "paper 1.pdf"


results = retriever.retrieve_by_paper(
    question=(
        "What future work or future improvements "
        "do the authors plan? We plan to extend "
        "future research investigate future work"
    ),
    paper_name=paper_name,
    top_k=5
)


strong_future_phrases = [
    "we plan",
    "plan to",
    "plans to",
    "future work",
    "future research",
    "we intend",
    "we hope",
    "we will",
    "research goals"
]


best_chunk = None
best_score = 0


for item in results:

    chunk_text = item["chunk"].strip()
    text = chunk_text.lower()

    score = 0

    for phrase in strong_future_phrases:
        if phrase in text:
            score += 5

    if score > best_score:
        best_score = score
        best_chunk = chunk_text


print("\n========== RETRIEVED EVIDENCE ==========\n")
print(best_chunk)


def extract_future_work(text):

    if not text:
        return "Not available in the provided context."

    # Clean line breaks
    clean_text = re.sub(r"\s+", " ", text).strip()

    # Split into sentences
    sentences = re.split(
        r"(?<=[.!?])\s+",
        clean_text
    )

    future_phrases = [
        "plan to",
        "plans to",
        "we plan",
        "we intend",
        "we hope",
        "we will",
        "future work",
        "future research",
        "research goals"
    ]

    selected_sentences = []

    for sentence in sentences:

        sentence_lower = sentence.lower()

        if any(
            phrase in sentence_lower
            for phrase in future_phrases
        ):
            selected_sentences.append(
                sentence.strip()
            )

    if not selected_sentences:
        return "Not available in the provided context."

    return " ".join(selected_sentences)


answer = extract_future_work(best_chunk)


print("\n========== CLEAN FUTURE WORK ==========\n")
print(answer)