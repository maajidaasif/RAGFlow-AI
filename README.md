# 🧠 RAGFlow AI

### Domain-Independent Local Research Intelligence Platform

RAGFlow AI is an AI-powered research intelligence system that helps users analyze, summarize, compare, and interact with research papers using a **local Large Language Model (LLM)** and **Retrieval-Augmented Generation (RAG)**.

The system processes uploaded PDF research papers, extracts and chunks the content, generates embeddings, stores them in a FAISS vector database, and uses a local Qwen2.5-3B-Instruct model to generate context-aware responses.

---

## 🚀 Features

- 📄 Upload research papers in PDF format
- 🔍 Extract text from research papers
- ✂️ Intelligent document chunking
- 🧠 Semantic embedding generation
- 🗂️ FAISS vector database
- 🤖 Local Qwen2.5-3B-Instruct LLM
- 📝 Research paper summarization
- 🔬 Research paper comparison
- 📚 Literature survey generation
- 📊 Automatic research report generation
- 💬 Context-aware research chatbot
- 🔎 Research question answering
- 📑 Research gap identification
- 🔐 JWT-based authentication
- 👤 User-specific research data
- 📴 Local LLM processing without external LLM APIs

---

## 🛠️ Tech Stack

### Frontend

- React.js
- Vite
- JavaScript
- CSS

### Backend

- Python
- Flask
- Flask-CORS
- Flask-JWT-Extended
- Flask-SQLAlchemy

### Database

- SQLite
- SQLAlchemy

### AI / Machine Learning

- Qwen2.5-3B-Instruct
- GGUF
- llama.cpp
- Sentence Transformers
- all-MiniLM-L6-v2
- FAISS
- LangChain Text Splitters

### Document Processing

- PyMuPDF
- PDF text extraction
- Text cleaning
- Document chunking

---

## 🧠 AI Architecture

```text
                    ┌─────────────────────┐
                    │       User          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Flask Backend    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    PDF Upload       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Text Extraction    │
                    │      PyMuPDF        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Text Cleaning &     │
                    │ Document Chunking   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Embedding Model     │
                    │ all-MiniLM-L6-v2    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FAISS Vector     │
                    │      Database       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Semantic Retrieval │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Qwen2.5-3B-Instruct │
                    │    Local LLM        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Research Response   │
                    └─────────────────────┘

                    RAGFlow-AI/
│
├── backend/
│   │
│   ├── comparison/
│   ├── literature/
│   ├── llm/
│   ├── models/
│   │   └── qwen2.5-3b-instruct-q4_k_m.gguf
│   ├── prompts/
│   ├── routes/
│   ├── services/
│   ├── uploads/
│   ├── processed/
│   ├── summaries/
│   ├── vector_db/
│   │
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── embedding.py
│   ├── chunking.py
│   ├── requirements.txt
│   └── ...
│
├── database/
│   └── researchmind.db
│
├── documents/
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── App.jsx
│   ├── App.css
│   ├── index.css
│   ├── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
├── README.md
└── ...