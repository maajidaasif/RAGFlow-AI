# 📚 RAGFlow AI

 RAGFlow AI is an AI-powered research paper analysis platform that enables users to upload research papers, generate summaries, compare multiple papers, retrieve relevant information using Retrieval-Augmented Generation (RAG), and interact with a Local Large Language Model (LLM) for intelligent research assistance.

The platform is designed to simplify the process of understanding research papers by providing AI-driven insights, comparisons, and question-answering capabilities.

---

# 🚀 Features

- 📄 Upload research papers in PDF format
- 📝 AI-powered research paper summarization
- 🔍 Compare multiple research papers
- 📚 Extract future work from research papers
- 🎯 Accuracy analysis
- 💬 Ask questions using a Local LLM
- ⚡ Fast document retrieval using FAISS Vector Database
- 🤖 Retrieval-Augmented Generation (RAG)
- 📖 Intelligent research assistant
- 🔒 Runs with a Local LLM for privacy

---

# 🛠 Tech Stack

## Frontend
- React.js
- Vite
- CSS

## Backend
- Python
- Flask

## AI & NLP
- Sentence Transformers
- FAISS
-Qwen2.5-3B-Instruct
- Retrieval-Augmented Generation (RAG)

## Database
- SQLite

---

# 📂 Project Structure

```text
ResearchMind-AI
│
├── backend
│   ├── comparison
│   ├── llm
│   ├── models
│   ├── routes
│   ├── services
│   ├── app.py
│   ├── embedding.py
│   ├── chunking.py
│   ├── database.py
│   └── requirements.txt
│
├── frontend
│   ├── src
│   ├── public
│   ├── package.json
│   └── vite.config.js
│
├── README.md
└── .gitignore
```

---

# ⚙️ Installation

## Clone the Repository

```bash
git clone https://github.com/maajidaasif/ResearchMind-AI.git
```

---

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

# 🔄 Project Workflow

```text
Upload Research Paper (PDF)
          │
          ▼
Text Extraction
          │
          ▼
Text Chunking
          │
          ▼
Embedding Generation
          │
          ▼
FAISS Vector Database
          │
          ▼
Local LLM + RAG
          │
          ▼
Summary • Comparison • Question Answering
```

---

# 📸 Screenshots

Screenshots will be added after the project is completed.

---

# 🔮 Future Enhancements

- 🌍 Multi-language support
- 📑 Automatic citation generation
- 🤖 Research paper recommendation system
- ☁️ Cloud deployment
- 📊 Interactive analytics dashboard
- 🧠 Support for more Local LLMs

---

# 👩‍💻 Author

**Maajida A**

Final Year Computer Science Engineering Student

Interested in:
- Artificial Intelligence
- Machine Learning
- Natural Language Processing
- Large Language Models (LLMs)
- Full Stack Development

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

It motivates me to continue building and improving AI projects.
