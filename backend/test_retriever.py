import os

print("Current Working Directory:")
print(os.getcwd())


from services.retriever import Retriever

retriever = Retriever()

paper_names = []

for item in retriever.metadata:

    if item["paper_name"] not in paper_names:

        paper_names.append(item["paper_name"])

print("\nPaper Names in metadata:\n")

for paper in paper_names:
    print(paper)