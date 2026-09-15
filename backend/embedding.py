import os
from sentence_transformers import SentenceTransformer

from chunking import split_text
from services.pdf_processing import process_pdf
from services.vector_database import VectorDatabase


# Embedding model will be loaded only when required
embedding_model = None


def initialize_embedding_model():
    global embedding_model

    if embedding_model is None:
        print("\nLoading embedding model...")
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    return embedding_model


def generate_embeddings(chunks, batch_size=32):

    model = initialize_embedding_model()

    print("\nGenerating embeddings...")

    embeddings = model.encode(
        chunks,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    return embeddings


if __name__ == "__main__":

    all_chunks = []
    metadata = []

    uploads_folder = "uploads"

    pdf_files = [
        file for file in os.listdir(uploads_folder)
        if file.lower().endswith(".pdf")
    ]

    print(f"\nFound {len(pdf_files)} PDF(s).\n")

    if len(pdf_files) == 0:
        print("No PDF files found in uploads folder.")
        exit()

    for pdf_file in pdf_files:

        pdf_path = os.path.join(uploads_folder, pdf_file)

        print(f"\nProcessing: {pdf_file}")

        cleaned_text = process_pdf(pdf_path)

        chunks = split_text(cleaned_text)

        print(f"Chunks created: {len(chunks)}")

        all_chunks.extend(chunks)

        for chunk in chunks:
            metadata.append({
                "paper_name": pdf_file,
                "chunk": chunk
            })

        print(f"{pdf_file} processed successfully.")

    print(f"\nTotal Chunks: {len(all_chunks)}")

    embeddings = generate_embeddings(all_chunks)

    db = VectorDatabase()

    db.create_database(embeddings, metadata)
    db.save_database()

    print("\n===================================")
    print("FAISS Database Created Successfully!")
    print("===================================")
    print(f"Total PDFs       : {len(pdf_files)}")
    print(f"Total Chunks     : {len(all_chunks)}")
    print(f"Total Embeddings : {len(embeddings)}")