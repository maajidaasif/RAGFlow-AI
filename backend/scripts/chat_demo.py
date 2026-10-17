import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.retriever import Retriever
from llm.local_llm import ask_llm

print("Loading ResearchMind AI...")

retriever = Retriever()

question = input("\nEnter your question: ")

results = retriever.retrieve(question)

context = ""

print("\nRetrieved Papers:")

for result in results:
    print("-", result["paper_name"])
    context += result["chunk"] + "\n\n"

answer = ask_llm(question, context)

print("\n==============================")
print("Answer")
print("==============================\n")

print(answer)