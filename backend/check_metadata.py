import json
import os

META_PATH = os.path.join("vector_db", "metadata.json")
OLD_PKL   = os.path.join("vector_db", "metadata.pkl")

if not os.path.exists(META_PATH):
    if os.path.exists(OLD_PKL):
        print(
            "ERROR: metadata.json not found.\n"
            "An old metadata.pkl file was detected.\n"
            "Run the migration script first:\n"
            "  python migrate_metadata.py"
        )
    else:
        print(f"ERROR: {META_PATH} not found. Run embedding.py first.")
    exit(1)

with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

print("Total chunks:", len(metadata))

papers = []

for item in metadata:
    if item["paper_name"] not in papers:
        papers.append(item["paper_name"])

print("\nPaper Names:\n")

for p in papers:
    print(p)