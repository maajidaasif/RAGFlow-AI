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

---

## ⚙️ Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11.x |
| Node.js | 18+ |
| RAM (available) | 4 GB minimum |
| Disk space for model | ~2 GB |

---

### 1. Clone the Repository

```bash
git clone https://github.com/maajidaasif/RAGFlow-AI.git
cd RAGFlow-AI
```

---

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 3. 🤖 Local LLM Setup (Required)

> **This step is mandatory.** The application will not start without the GGUF model file in place.

#### What the application uses

| Property | Value |
|---|---|
| **Library** | `llama-cpp-python` (NOT Ollama) |
| **Model** | Qwen2.5-3B-Instruct |
| **Quantization** | Q4_K_M (GGUF format) |
| **Exact filename** | `qwen2.5-3b-instruct-q4_k_m.gguf` |
| **Expected path** | `backend/models/qwen2.5-3b-instruct-q4_k_m.gguf` |
| **Context window** | 4096 tokens |
| **GPU offload** | Disabled (CPU-only, `n_gpu_layers=0`) |
| **Threads** | 8 |

#### Step 1 — Create the models/ directory

```bash
# Run from the backend/ folder
mkdir models
```

#### Step 2 — Download the GGUF model

Download the file from the official Hugging Face repository:

**Model source:**
```
https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF
```

**Direct file to download:**
```
qwen2.5-3b-instruct-q4_k_m.gguf
```

You can download it via browser, or using `huggingface-hub`:

```bash
pip install huggingface-hub

python -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='Qwen/Qwen2.5-3B-Instruct-GGUF',
    filename='qwen2.5-3b-instruct-q4_k_m.gguf',
    local_dir='models'
)
"
```

#### Step 3 — Verify the file is in the correct location

```
backend/
└── models/
    └── qwen2.5-3b-instruct-q4_k_m.gguf   ✅  (~2 GB)
```

> ⚠️ The filename must match **exactly**: `qwen2.5-3b-instruct-q4_k_m.gguf`  
> Any rename will cause a `FileNotFoundError` on startup.

#### Step 4 — Verify the model loads

```bash
# From the backend/ folder, with venv active
python -c "from llm.local_llm import initialize_llm; initialize_llm(); print('Model loaded successfully')"
```

Expected output:
```
Loading Qwen2.5-3B-Instruct...
Model loaded successfully
```

---

### 4. FAISS Vector Database

Uploading a PDF through the app now chunks, embeds, and indexes it immediately. To rebuild the entire index from the PDFs in `uploads/`, run:

```bash
# From the backend/ folder
python embedding.py
```

This creates `backend/vector_db/faiss_index.bin` and JSON metadata in `backend/vector_db/metadata.json`.

---

### 5. Run the Backend

```bash
# From the backend/ folder, with venv active
python app.py
```

For a new database, apply the committed baseline migration before starting Flask:

```powershell
cd backend
flask --app app db upgrade
```

For an existing database previously created with `db.create_all()`, back it up and verify its schema matches the baseline, then run `flask --app app db stamp head` once. After changing a model, create and apply a migration with `flask --app app db migrate -m "describe change"` and `flask --app app db upgrade`.

The Flask server starts at: `http://localhost:5000`

---

### 6. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The React app starts at: `http://localhost:5173`

---

## 📋 Notes

- The application checks available RAM at startup. A minimum of **2 GB free RAM** is required to proceed.
- The FAISS vector database must be built (step 4) before using the chatbot or analysis features.
- The local LLM runs entirely on CPU by default. Performance depends on your machine's CPU and available RAM.
- No OpenAI, Gemini, or Claude API keys are required.