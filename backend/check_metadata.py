import pickle

with open("vector_db/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

print("Total chunks:", len(metadata))

papers = []

for item in metadata:
    if item["paper_name"] not in papers:
        papers.append(item["paper_name"])

print("\nPaper Names:\n")

for p in papers:
    print(p)