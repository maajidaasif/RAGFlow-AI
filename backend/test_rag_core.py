import numpy as np

import services.retriever as retriever_module
import services.vector_database as vector_database_module
from chunking import split_text
from services.retriever import Retriever
from services.vector_database import VectorDatabase


def test_split_text_splits_long_text_into_bounded_chunks():
    chunks = split_text("research " * 300)

    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_retriever_starts_empty_without_index_files(tmp_path, monkeypatch):
    monkeypatch.setattr(retriever_module, "VECTOR_DB_DIR", str(tmp_path))

    retriever = Retriever()

    assert retriever.index.ntotal == 0
    assert retriever.metadata == []
    assert retriever.retrieve("research question") == []


def test_vector_database_add_remove_and_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_database_module, "VECTOR_DB_DIR", str(tmp_path))
    embeddings = np.eye(3, 384, dtype="float32")
    metadata = [
        {"paper_id": 10, "paper_name": "a.pdf", "chunk": "keep"},
        {"paper_id": 11, "paper_name": "b.pdf", "chunk": "remove"},
        {"paper_id": 12, "paper_name": "c.pdf", "chunk": "keep too"},
    ]

    database = VectorDatabase()
    database.create_database(embeddings, metadata)
    database.save_database()

    loaded = VectorDatabase()
    loaded.load_database()
    assert loaded.remove_paper(11)
    loaded.save_database()

    reloaded = VectorDatabase()
    reloaded.load_database()
    assert reloaded.index.ntotal == 2
    assert [item["paper_id"] for item in reloaded.metadata] == [10, 12]
    assert reloaded.index.metric_type == vector_database_module.faiss.METRIC_INNER_PRODUCT


def test_normalized_index_adds_new_paper_vectors():
    database = VectorDatabase()
    database.add_documents(
        np.array([[3.0] + [0.0] * 383], dtype="float32"),
        [{"paper_id": 15, "paper_name": "d.pdf", "chunk": "new"}],
    )

    assert database.index.ntotal == 1
    assert np.isclose(database.index.reconstruct(0)[0], 1.0)