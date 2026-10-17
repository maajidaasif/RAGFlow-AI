import os

from chunking import split_text
from embedding import generate_embeddings
from services.vector_database import (
    INDEX_FILENAME,
    META_FILENAME,
    VECTOR_DB_DIR,
    VectorDatabase,
)


def _load_database():
    database = VectorDatabase()
    index_path = os.path.join(VECTOR_DB_DIR, INDEX_FILENAME)
    metadata_path = os.path.join(VECTOR_DB_DIR, META_FILENAME)

    if os.path.exists(index_path) and os.path.exists(metadata_path):
        database.load_database()

    return database


def index_paper(text, paper_id, paper_name):
    chunks = split_text(text)
    if not chunks:
        return 0

    embeddings = generate_embeddings(chunks)
    metadata = [
        {"paper_id": paper_id, "paper_name": paper_name, "chunk": chunk}
        for chunk in chunks
    ]

    database = _load_database()
    database.add_documents(embeddings, metadata)
    database.save_database()
    from routes.chat_routes import invalidate_retriever
    invalidate_retriever()
    return len(chunks)


def remove_paper_from_index(paper_id, paper_name=None):
    database = _load_database()
    if database.index is None:
        return False

    removed = database.remove_paper(paper_id, paper_name)
    if removed:
        database.save_database()
        from routes.chat_routes import invalidate_retriever
        invalidate_retriever()
    return removed