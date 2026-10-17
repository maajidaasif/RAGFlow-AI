import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.retriever import Retriever
from llm.local_llm import ask_llm


retriever = Retriever()


results = retriever.retrieve_by_paper(
    question=(
        "What accuracy, performance score, evaluation result, "
        "or benchmark result is reported in this research paper?"
    ),
    paper_name="paper 1.pdf",
    top_k=1
)


chunk_text = results[0]["chunk"]


print("\n========== RETRIEVED EVIDENCE ==========\n")

print(chunk_text)


question = """
Complete this sentence using only the numerical performance results stated in the context:

The reported performance results are

Write only the completion.
"""


answer = ask_llm(
    question=question,
    context=chunk_text,
    max_tokens=60
)


print("\n========== TINYLLAMA ANSWER ==========\n")

print(answer)