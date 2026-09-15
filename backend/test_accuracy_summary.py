from llm.local_llm import ask_llm
from services.paper_comparison import PaperComparisonEngine


engine = PaperComparisonEngine()


paper_name = "paper 1.pdf"

evidence = engine.get_relevant_evidence(
    retrieval_query=(
        "What accuracy, performance score, "
        "evaluation result, or benchmark result "
        "is reported in this research paper?"
    ),
    paper_name=paper_name,
    keywords=[
        "accuracy",
        "bleu",
        "f1",
        "score",
        "results",
        "performance",
        "benchmark",
        "state-of-the-art"
    ],
    category_name="Accuracy Comparison"
)


print("\n========== RETRIEVED EVIDENCE ==========\n")
print(evidence)


question = """
Extract only the reported performance result from the context.

Rules:
- Use only facts and numbers explicitly present in the context.
- Do not add outside information.
- Do not invent a model, dataset, score, or result.
- Give a short answer.
- If no performance result is present, answer exactly:
Not available in the provided context.
"""


answer = ask_llm(
    question=question,
    context=evidence,
    max_tokens=80
)


print("\n========== LOCAL LLM ANSWER ==========\n")
print(answer)