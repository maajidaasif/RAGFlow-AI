import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer


class Retriever:

    def __init__(self):

        # =========================================
        # Settings
        # =========================================

        self.model_name = "all-MiniLM-L6-v2"

        # Minimum cosine similarity required
        # before a chunk is considered relevant.
        #
        # Higher value = stricter retrieval
        # Lower value = more chunks retrieved
        #
        self.similarity_threshold = 0.30

        # =========================================
        # Embedding Model
        # =========================================
        #
        # Model is NOT loaded during object creation.
        # It will be loaded only when retrieval is needed.
        #

        self.model = None

        # =========================================
        # Load Existing FAISS Index
        # =========================================

        index_path = os.path.join(
            "vector_db",
            "faiss_index.bin"
        )

        metadata_path = os.path.join(
            "vector_db",
            "metadata.pkl"
        )

        if not os.path.exists(index_path):

            raise FileNotFoundError(
                f"FAISS index not found: {index_path}"
            )

        if not os.path.exists(metadata_path):

            raise FileNotFoundError(
                f"Metadata file not found: {metadata_path}"
            )

        old_index = faiss.read_index(
            index_path
        )

        # =========================================
        # Load Metadata
        # =========================================

        with open(
            metadata_path,
            "rb"
        ) as file:

            self.metadata = pickle.load(file)

        # =========================================
        # Validate Metadata / Index
        # =========================================

        if old_index.ntotal != len(self.metadata):

            raise ValueError(
                "FAISS index and metadata count do not match.\n"
                f"FAISS vectors: {old_index.ntotal}\n"
                f"Metadata: {len(self.metadata)}\n\n"
                "Please run embedding.py again."
            )

        # =========================================
        # Convert Existing Vectors to Normalized
        # Vectors
        # =========================================
        #
        # Your embedding.py created an IndexFlatL2.
        #
        # We reconstruct those vectors and normalize
        # them here so that retrieval works using
        # cosine similarity.
        #
        # This means you do NOT have to immediately
        # recreate your PDFs.
        #

        print("\nPreparing FAISS vectors...")

        if old_index.ntotal > 0:

            vectors = old_index.reconstruct_n(
                0,
                old_index.ntotal
            )

            vectors = np.asarray(
                vectors,
                dtype="float32"
            )

            # Normalize vectors
            faiss.normalize_L2(
                vectors
            )

            # Create cosine-similarity index
            self.index = faiss.IndexFlatIP(
                vectors.shape[1]
            )

            self.index.add(
                vectors
            )

        else:

            self.index = old_index

        # =========================================
        # Print Information
        # =========================================

        print(
            f"\nTotal Metadata Chunks: "
            f"{len(self.metadata)}"
        )

        unique_papers = []

        for item in self.metadata:

            paper_name = item.get(
                "paper_name"
            )

            if (
                paper_name
                and paper_name not in unique_papers
            ):

                unique_papers.append(
                    paper_name
                )

        print("\nPaper Names Found:")

        for paper in unique_papers:

            print(
                "-",
                paper
            )

        print(
            f"\nSimilarity Threshold: "
            f"{self.similarity_threshold}"
        )

        print("=" * 60)


    # =========================================
    # Initialize Embedding Model
    # =========================================

    def initialize_model(self):

        if self.model is None:

            print("\nLoading embedding model...")

            self.model = SentenceTransformer(
                self.model_name
            )

        return self.model


    # =========================================
    # Create Question Embedding
    # =========================================

    def _create_question_embedding(
        self,
        question
    ):

        model = self.initialize_model()

        embedding = model.encode(
            question,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        embedding = np.asarray(
            [embedding],
            dtype="float32"
        )

        return embedding


    # =========================================
    # Retrieve Top K Relevant Chunks
    # =========================================

    def retrieve(
        self,
        question,
        top_k=5,
        threshold=None
    ):

        if not question:
            return []

        if self.index.ntotal == 0:
            return []

        # Use default threshold if one
        # is not provided
        if threshold is None:
            threshold = self.similarity_threshold

        # =====================================
        # Create Question Embedding
        # =====================================

        question_embedding = (
            self._create_question_embedding(
                question
            )
        )

        # =====================================
        # Search More Than top_k
        # =====================================
        #
        # We search extra chunks because some
        # results may be rejected by threshold.
        #

        search_k = min(
            max(top_k * 3, top_k),
            self.index.ntotal
        )

        similarities, indices = (
            self.index.search(
                question_embedding,
                search_k
            )
        )

        results = []

        # =====================================
        # Apply Similarity Threshold
        # =====================================

        for similarity, idx in zip(
            similarities[0],
            indices[0]
        ):

            if idx < 0:
                continue

            # Reject weak matches
            if float(similarity) < threshold:
                continue

            item = dict(
                self.metadata[idx]
            )

            # Store similarity internally
            item["_similarity"] = float(
                similarity
            )

            results.append(
                item
            )

            if len(results) >= top_k:
                break

        # =====================================
        # Debug Information
        # =====================================

        print("\n-----------------------------------")
        print("RETRIEVAL")
        print("-----------------------------------")
        print("Question:", question)
        print(
            "Chunks Retrieved:",
            len(results)
        )

        for item in results:

            print(
                f"{item.get('paper_name')} "
                f"| Similarity: "
                f"{item.get('_similarity', 0):.4f}"
            )

        print("-----------------------------------")

        return results


    # =========================================
    # Retrieve Chunks From Specific Paper
    # =========================================

    def retrieve_by_paper(
        self,
        question,
        paper_name,
        top_k=3,
        threshold=None
    ):

        if not question:
            return []

        if self.index.ntotal == 0:
            return []

        if threshold is None:
            threshold = self.similarity_threshold

        # =====================================
        # Question Embedding
        # =====================================

        question_embedding = (
            self._create_question_embedding(
                question
            )
        )

        # Search complete database
        similarities, indices = (
            self.index.search(
                question_embedding,
                self.index.ntotal
            )
        )

        results = []

        # =====================================
        # Filter By Paper
        # =====================================

        for similarity, idx in zip(
            similarities[0],
            indices[0]
        ):

            if idx < 0:
                continue

            item = self.metadata[idx]

            if item.get("paper_name") != paper_name:
                continue

            # Apply similarity threshold
            if float(similarity) < threshold:
                continue

            result_item = dict(
                item
            )

            result_item["_similarity"] = float(
                similarity
            )

            results.append(
                result_item
            )

            if len(results) >= top_k:
                break

        return results


    # =========================================
    # Merge Context From One Paper
    # =========================================

    def retrieve_context_by_paper(
        self,
        question,
        paper_name,
        top_k=3,
        threshold=None
    ):

        chunks = self.retrieve_by_paper(
            question=question,
            paper_name=paper_name,
            top_k=top_k,
            threshold=threshold
        )

        if len(chunks) == 0:
            return None

        merged_context = []

        for item in chunks:

            chunk = item.get(
                "chunk"
            )

            if chunk:

                merged_context.append(
                    chunk.strip()
                )

        if len(merged_context) == 0:
            return None

        return "\n\n".join(
            merged_context
        )


    # =========================================
    # Balanced Context From All Papers
    # =========================================

    def retrieve_balanced_context(
        self,
        question,
        chunks_per_paper=2,
        threshold=None
    ):

        unique_papers = []

        for item in self.metadata:

            paper_name = item.get(
                "paper_name"
            )

            if (
                paper_name
                and paper_name not in unique_papers
            ):

                unique_papers.append(
                    paper_name
                )

        merged_context = []

        paper_number = 1

        for paper in unique_papers:

            context = (
                self.retrieve_context_by_paper(
                    question=question,
                    paper_name=paper,
                    top_k=chunks_per_paper,
                    threshold=threshold
                )
            )

            if context:

                merged_context.append(
                    f"""
==========================================
UPLOADED PAPER {paper_number}
FILE NAME: {paper}
==========================================

{context}
"""
                )

                paper_number += 1

        if len(merged_context) == 0:

            return None

        return "\n".join(
            merged_context
        )


    # =========================================
    # Retrieve And Merge Context
    # =========================================

    def retrieve_context(
        self,
        question,
        top_k=5,
        threshold=None
    ):

        chunks = self.retrieve(
            question=question,
            top_k=top_k,
            threshold=threshold
        )

        if len(chunks) == 0:

            return None

        merged_context = []

        for item in chunks:

            chunk = item.get(
                "chunk"
            )

            paper_name = item.get(
                "paper_name",
                "Unknown Paper"
            )

            similarity = item.get(
                "_similarity"
            )

            if chunk:

                merged_context.append(
                    f"""
[Paper: {paper_name}]

{chunk.strip()}
"""
                )

        if len(merged_context) == 0:

            return None

        return "\n\n".join(
            merged_context
        )