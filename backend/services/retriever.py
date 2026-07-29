import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer


class Retriever:

    def __init__(self):

        #print("=" * 60)
        #print("Retriever Current Working Directory:")
        #print(os.getcwd())

        #print("\nFAISS Index Path:")
        #print(os.path.abspath("vector_db/faiss_index.bin"))

        #print("\nMetadata Path:")
        #print(os.path.abspath("vector_db/metadata.pkl"))
        #print("=" * 60)

        # Load embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Load FAISS index
        self.index = faiss.read_index(
            "vector_db/faiss_index.bin"
        )

        # Load metadata
        with open(
            "vector_db/metadata.pkl",
            "rb"
        ) as file:

            self.metadata = pickle.load(file)

            #print(
             #   "\nFirst paper in retriever:",
              #  self.metadata[0]["paper_name"]
            #)

        print(f"\nTotal Metadata Chunks: {len(self.metadata)}")

        unique_papers = []

        for item in self.metadata:
            if item["paper_name"] not in unique_papers:
                unique_papers.append(item["paper_name"])
        
        print("\nPaper Names Found:")

        for paper in unique_papers:
            print("-", paper)

        print("=" * 60)

    # ---------------------------------
    # Retrieve Top K Chunks
    # ---------------------------------
    def retrieve(
        self,
        question,
        top_k=3
    ):

        question_embedding = self.model.encode(question)

        question_embedding = np.array(
            [question_embedding],
            dtype="float32"
        )

        distances, indices = self.index.search(
            question_embedding,
            top_k
        )

        results = []

        for idx in indices[0]:
            results.append(self.metadata[idx])

        return results

    # ---------------------------------
    # Retrieve Chunks By Paper
    # ---------------------------------
    def retrieve_by_paper(
        self,
        question,
        paper_name,
        top_k=3
    ):

        question_embedding = self.model.encode(question)

        question_embedding = np.array(
            [question_embedding],
            dtype="float32"
        )

        total_chunks = len(self.metadata)

        distances, indices = self.index.search(
            question_embedding,
            total_chunks
        )

        results = []

        for idx in indices[0]:

            item = self.metadata[idx]

            if item["paper_name"] == paper_name:
                results.append(item)

            if len(results) >= top_k:
                break

        return results

    # ---------------------------------
    # Merge Context From One Paper
    # ---------------------------------
    def retrieve_context_by_paper(
        self,
        question,
        paper_name,
        top_k=3
    ):

        chunks = self.retrieve_by_paper(
            question=question,
            paper_name=paper_name,
            top_k=top_k
        )

        if len(chunks) == 0:
            return None

        merged_context = []

        for item in chunks:

            chunk = item.get("chunk")

            if chunk:
                merged_context.append(chunk.strip())

        if len(merged_context) == 0:
            return None

        return "\n\n".join(merged_context)

    # ---------------------------------
    # Balanced Context From All Papers
    # ---------------------------------
    def retrieve_balanced_context(
        self,
        question,
        chunks_per_paper=1
    ):

        unique_papers = []

        for item in self.metadata:
            if item["paper_name"] not in unique_papers:
                unique_papers.append(item["paper_name"])

        merged_context = []

        paper_number = 1

        for paper in unique_papers:

            context = self.retrieve_context_by_paper(
                question=question,
                paper_name=paper,
                top_k=chunks_per_paper
            )

            if context:

                merged_context.append(
                    f"""
==========================================
Uploaded Paper {paper_number}
File Name : {paper}
==========================================

{context}
"""
                )

                paper_number += 1

        if len(merged_context) == 0:
            return None

        return "\n".join(merged_context)

    # ---------------------------------
    # Merge Context From All Papers
    # ---------------------------------
    def retrieve_context(
        self,
        question,
        top_k=10
    ):

        chunks = self.retrieve(
            question=question,
            top_k=top_k
        )

        if len(chunks) == 0:
            return None

        merged_context = []

        for item in chunks:

            chunk = item.get("chunk")

            if chunk:
                merged_context.append(chunk.strip())

        if len(merged_context) == 0:
            return None

        return "\n\n".join(merged_context)