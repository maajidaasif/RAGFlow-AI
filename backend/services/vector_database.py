import os
import json
import faiss
import numpy as np


# Path constants — kept in one place so VectorDatabase and
# Retriever always agree on exactly the same file names.
VECTOR_DB_DIR  = "vector_db"
INDEX_FILENAME = "faiss_index.bin"
META_FILENAME  = "metadata.json"


def as_cosine_index(index):
    if index.metric_type == faiss.METRIC_INNER_PRODUCT:
        return index
    if index.metric_type != faiss.METRIC_L2 or index.ntotal == 0:
        return index

    vectors = np.asarray(
        index.reconstruct_n(0, index.ntotal),
        dtype="float32"
    )
    faiss.normalize_L2(vectors)
    cosine_index = faiss.IndexFlatIP(index.d)
    cosine_index.add(vectors)
    return cosine_index


class VectorDatabase:

    def __init__(self):

        self.index = None

        self.metadata = []

        self.dimension = 384


    def create_database(self, embeddings, metadata):

        vectors = np.array(embeddings).astype("float32")

        if vectors.size:
            self.dimension = vectors.shape[1]
            faiss.normalize_L2(vectors)

        self.index = faiss.IndexFlatIP(self.dimension)

        self.index.add(vectors)

        self.metadata = metadata


    def save_database(self):
        """Persist the FAISS index and JSON metadata to disk.

        The FAISS index is written with faiss.write_index() (its own
        documented binary format — not pickle).  The metadata list
        (list[dict[str, str]]) is serialised with json.dump() so the
        file is human-readable, diffable, and safe to load on any
        Python version without the deserialization risks of pickle.
        """

        os.makedirs(VECTOR_DB_DIR, exist_ok=True)

        # ── FAISS index ──────────────────────────────────────────────
        # faiss.write_index uses FAISS's own binary format, NOT pickle.
        # Do NOT replace this call with pickle.
        faiss.write_index(
            self.index,
            os.path.join(VECTOR_DB_DIR, INDEX_FILENAME)
        )

        # ── Metadata (JSON) ──────────────────────────────────────────
        # Each entry is {"paper_name": str, "chunk": str} — fully
        # JSON-serialisable, so json.dump() is safe and correct.
        meta_path = os.path.join(VECTOR_DB_DIR, META_FILENAME)

        with open(meta_path, "w", encoding="utf-8") as file:

            json.dump(
                self.metadata,
                file,
                ensure_ascii=False,
                indent=2
            )


    def load_database(self):
        """Load the FAISS index and JSON metadata from disk."""

        index_path = os.path.join(VECTOR_DB_DIR, INDEX_FILENAME)
        meta_path  = os.path.join(VECTOR_DB_DIR, META_FILENAME)

        self.index = faiss.read_index(index_path)

        with open(meta_path, "r", encoding="utf-8") as file:

            self.metadata = json.load(file)

        self.dimension = self.index.d
        original_index = self.index
        self.index = as_cosine_index(self.index)
        if self.index is not original_index:
            faiss.write_index(self.index, index_path)

    def add_documents(self, embeddings, metadata):
        vectors = np.asarray(embeddings, dtype="float32")
        if vectors.size == 0:
            return

        faiss.normalize_L2(vectors)
        if self.index is None:
            self.index = faiss.IndexFlatIP(vectors.shape[1])
            self.dimension = vectors.shape[1]

        self.index.add(vectors)
        self.metadata.extend(metadata)

    def remove_paper(self, paper_id, paper_name=None):
        keep_indices = [
            index for index, item in enumerate(self.metadata)
            if not (
                item.get("paper_id") == paper_id
                or (
                    paper_name
                    and "paper_id" not in item
                    and item.get("paper_name") == paper_name
                )
            )
        ]

        if len(keep_indices) == len(self.metadata):
            return False

        vectors = (
            self.index.reconstruct_n(0, self.index.ntotal)[keep_indices]
            if keep_indices else np.empty((0, self.dimension), dtype="float32")
        )
        metadata = [self.metadata[index] for index in keep_indices]
        self.create_database(vectors, metadata)
        return True