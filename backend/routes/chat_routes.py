from flask import Blueprint, request, jsonify

from services.retriever import Retriever
from llm.local_llm import ask_llm
from comparison.paper_comparison import PaperComparisonEngine


# ============================================================
# CHAT BLUEPRINT
# ============================================================

chat_bp = Blueprint("chat", __name__)


# ============================================================
# RETRIEVER
# ============================================================
#
# Retriever is initialized only when it is actually needed.
# This prevents heavy components from loading during import.
#

retriever = None


def get_retriever():

    global retriever

    if retriever is None:

        print("\nInitializing ResearchMind Retriever...")

        retriever = Retriever()

    return retriever


# ============================================================
# RESEARCHMIND AI PROJECT INFORMATION
# ============================================================

PROJECT_CONTEXT = """
ResearchMind AI is an Offline AI Research Intelligence System.

PURPOSE
-------
ResearchMind AI helps users upload research papers and understand,
analyze, compare, and interact with those papers using a local AI
system.

PDF WORKFLOW
------------
1. User uploads research papers as PDF files.
2. PDF text is extracted.
3. Extracted text is cleaned and divided into smaller chunks.
4. Sentence Transformers convert chunks into embeddings.
5. The embedding model used is all-MiniLM-L6-v2.
6. The embeddings are stored in FAISS.
7. When a user asks a question, FAISS retrieves relevant chunks.
8. The retrieved research context is sent to Qwen2.5-3B-Instruct.
9. Qwen2.5-3B-Instruct generates the final response.

RAG
---
ResearchMind AI uses Retrieval-Augmented Generation (RAG).

RAG combines:
- Retrieval of relevant information from uploaded research papers.
- Generation of an answer using the local Qwen2.5-3B-Instruct model.

FAISS performs similarity-based retrieval from the stored
research-paper embeddings.

LLM
---
The local Large Language Model used by ResearchMind AI is:

Qwen2.5-3B-Instruct.

The model runs locally.

The project does not use OpenAI API for the chatbot.
The project does not use Gemini API for the chatbot.
The project does not use Claude API for the chatbot.
The project does not depend on paid external AI APIs.

EMBEDDING MODEL
---------------
The embedding model is:

all-MiniLM-L6-v2

It is used with Sentence Transformers to convert research-paper
text chunks into numerical vector representations.

VECTOR DATABASE
---------------
FAISS is used as the vector database/index for storing and
retrieving research-paper embeddings.

FINE-TUNING
-----------
ResearchMind AI does NOT use LoRA fine-tuning.

ResearchMind AI does NOT train Qwen2.5-3B-Instruct from scratch.

The local Qwen2.5-3B-Instruct model is used as the generation model.

ARCHITECTURE
------------
PDF Upload
    ->
PDF Text Extraction
    ->
Text Cleaning
    ->
Chunking
    ->
Sentence Transformer Embeddings
    ->
FAISS Vector Database
    ->
User Question
    ->
Relevant Context Retrieval
    ->
Qwen2.5-3B-Instruct
    ->
Final Answer

DOMAINS
-------
ResearchMind AI is not restricted to one research domain.

Users can upload papers from different domains such as:

Medical
Healthcare
Agriculture
Finance
Cybersecurity
Natural Language Processing
Computer Vision
Education
Engineering
Physics
Biology
and other research areas.

The domain should be determined from the uploaded research papers.

CHATBOT
-------
The Research Assistant can answer questions about:

- ResearchMind AI
- Uploaded research papers
- Research domains
- Research methodology
- Research problems
- Objectives
- Models
- Datasets
- Experiments
- Results
- Findings
- Limitations
- Conclusions
- Research gaps
- Paper comparisons
- RAG
- FAISS
- Embeddings
- Sentence Transformers
- Qwen2.5-3B-Instruct
- Local LLM
- Offline architecture
- Project architecture
- Project technologies
"""


# ============================================================
# COMMON RESPONSE
# ============================================================

UNRELATED_MESSAGE = (
    "I can help with questions about your uploaded research papers "
    "and the ResearchMind AI project."
)


# ============================================================
# NORMALIZE QUESTION
# ============================================================

def normalize_question(question):

    return (
        question
        .lower()
        .strip()
        .replace("-", " ")
        .replace("_", " ")
    )


# ============================================================
# GREETING
# ============================================================

def is_greeting(question):

    greetings = [
        "hi",
        "hello",
        "hey",
        "hai",
        "hii",
        "hiii",
        "good morning",
        "good afternoon",
        "good evening"
    ]

    return question in greetings


# ============================================================
# PAPER COMPARISON QUESTION DETECTION
# ============================================================

def is_comparison_question(question):

    comparison_terms = [

        "compare the papers",
        "compare papers",
        "compare my papers",
        "compare my uploaded papers",
        "compare uploaded papers",
        "compare the uploaded papers",
        "compare all papers",
        "compare these papers",
        "compare them",

        "comparison of papers",
        "comparison between papers",
        "comparison of the papers",

        "how are the papers different",
        "how are these papers different",

        "difference between the papers",
        "differences between the papers",
        "difference between papers",
        "differences between papers",

        "similarity between the papers",
        "similarities between the papers",
        "similarity between papers",
        "similarities between papers",

        "which paper is better",
        "which paper has better results",
        "which paper has the best results",

        "compare their methods",
        "compare their results",
        "compare their objectives",
        "compare their datasets",
        "compare their methodologies",
        "compare the methodologies",
        "compare the methods",
        "compare the results",
        "compare the objectives",
        "compare the datasets"
    ]

    return any(
        term in question
        for term in comparison_terms
    )


# ============================================================
# PROJECT QUESTION DETECTION
# ============================================================

def is_project_question(question):

    project_terms = [

        # ResearchMind
        "researchmind",
        "researchmind ai",

        # Website / Project
        "this website",
        "this web site",
        "this project",
        "this system",
        "this application",
        "this app",
        "your website",
        "your project",
        "your system",

        "what is researchmind",
        "what is researchmind ai",

        "what is this website",
        "what is this project",
        "what is this system",

        "what does this website do",
        "what does this project do",
        "what does this system do",

        "purpose of this website",
        "purpose of this project",
        "purpose of this system",
        "purpose of researchmind",

        "how does this website work",
        "how does this project work",
        "how does this system work",
        "how does researchmind work",

        # LLM
        "llm",
        "large language model",
        "language model",
        "which llm",
        "what llm",
        "which model",
        "what model",
        "which llm model",
        "what llm model",
        "which model are you using",
        "what model are you using",
        "which llm are you using",
        "what llm are you using",
        "which language model are you using",
        "what language model are you using",
        "what model do you use",
        "which model do you use",

        # Qwen
        "qwen",
        "qwen2.5",
        "qwen2.5 3b",
        "qwen2.5 3b instruct",
        "why qwen",
        "why use qwen",
        "why did you choose qwen",

        # Local model
        "local llm",
        "local model",
        "local language model",
        "why local llm",
        "why use local llm",
        "why did you choose local llm",
        "is the llm local",
        "is your llm local",
        "does the model run locally",

        # RAG
        "rag",
        "retrieval augmented generation",
        "retrieval augmented",
        "what is rag",
        "what does rag mean",
        "how does rag work",
        "why rag",
        "why use rag",
        "are you using rag",
        "do you use rag",

        # FAISS
        "faiss",
        "vector database",
        "vector db",
        "what is faiss",
        "why faiss",
        "why use faiss",
        "why did you choose faiss",
        "are you using faiss",
        "do you use faiss",

        # Embeddings
        "embedding",
        "embeddings",
        "embedding model",
        "embedding models",
        "what is an embedding",
        "what are embeddings",
        "which embedding model",
        "what embedding model",
        "sentence transformer",
        "sentence transformers",
        "minilm",
        "all minilm",
        "all minilm l6 v2",

        # APIs
        "openai",
        "open ai",
        "gemini",
        "google gemini",
        "claude",
        "api",
        "apis",
        "external api",
        "external apis",
        "paid api",

        # Fine tuning
        "fine tuning",
        "finetuning",
        "fine tune",
        "fine tuned",
        "fine-tuning",
        "lora",

        # Training
        "training",
        "train llm",
        "train your own llm",
        "training your own llm",
        "train our own llm",
        "training our own llm",
        "are you training your own llm",
        "do you train your own llm",

        # Architecture
        "architecture",
        "system architecture",
        "project architecture",
        "tech stack",
        "technology",
        "technologies",
        "technologies used",
        "technology used",

        # Offline
        "offline",
        "offline ai",
        "offline system",
        "without api",
        "no api",
        "without external api",

        # PDF processing
        "pdf processing",
        "pdf extraction",
        "text extraction",
        "text processing",
        "chunking",
        "how are pdfs processed",
        "how is pdf processed",

        # Chatbot
        "chatbot",
        "research assistant",
        "how does the chatbot work",
        "how does chatbot work",
        "how does research assistant work"
    ]

    return any(
        term in question
        for term in project_terms
    )


# ============================================================
# DIRECT PROJECT ANSWERS
# ============================================================

def get_direct_project_answer(question):

    q = normalize_question(question)

    # ========================================================
    # QWEN / LLM
    # ========================================================

    if (
        "which llm" in q
        or "what llm" in q
        or "which llm model" in q
        or "what llm model" in q
        or "which model are you using" in q
        or "what model are you using" in q
        or "which llm are you using" in q
        or "what llm are you using" in q
        or "which model do you use" in q
        or "what model do you use" in q
        or "which language model are you using" in q
        or "what language model are you using" in q
    ):

        return (
            "ResearchMind AI uses **Qwen2.5-3B-Instruct** "
            "as its local Large Language Model (LLM).\n\n"
            "The model runs locally and generates answers using "
            "the relevant research-paper context retrieved through "
            "the RAG pipeline."
        )


    # ========================================================
    # WHY QWEN
    # ========================================================

    if (
        "why qwen" in q
        or "why use qwen" in q
        or "why did you choose qwen" in q
    ):

        return (
            "ResearchMind AI uses **Qwen2.5-3B-Instruct** as the "
            "local generation model because the project is designed "
            "to run its AI pipeline locally without relying on "
            "external generative-AI APIs."
        )


    # ========================================================
    # LOCAL LLM
    # ========================================================

    if (
        "why local llm" in q
        or "why use local llm" in q
        or "why did you choose local llm" in q
    ):

        return (
            "ResearchMind AI uses a **local LLM** so the core chatbot "
            "generation can run locally without depending on OpenAI, "
            "Gemini, Claude, or other paid external AI APIs."
        )


    if (
        "is the llm local" in q
        or "is your llm local" in q
        or "does the model run locally" in q
    ):

        return (
            "Yes. ResearchMind AI uses **Qwen2.5-3B-Instruct** "
            "as a local LLM."
        )


    # ========================================================
    # RAG
    # ========================================================

    if (
        q == "rag"
        or "what is rag" in q
        or "what does rag mean" in q
    ):

        return (
            "**RAG** stands for **Retrieval-Augmented Generation**.\n\n"
            "In ResearchMind AI:\n\n"
            "1. **Retrieval** – FAISS retrieves relevant chunks "
            "from uploaded research papers.\n"
            "2. **Generation** – Qwen2.5-3B-Instruct uses the "
            "retrieved context to generate the answer.\n\n"
            "**User Question → FAISS → Relevant Context → "
            "Qwen2.5-3B-Instruct → Answer**"
        )


    if (
        "are you using rag" in q
        or "do you use rag" in q
        or "why rag" in q
        or "why use rag" in q
    ):

        return (
            "Yes. ResearchMind AI uses **Retrieval-Augmented "
            "Generation (RAG)** to retrieve relevant information "
            "from uploaded research papers before generating an answer."
        )


    # ========================================================
    # FAISS
    # ========================================================

    if (
        q == "faiss"
        or "what is faiss" in q
    ):

        return (
            "**FAISS** is the vector search/index used by "
            "ResearchMind AI to store and retrieve research-paper "
            "embeddings efficiently."
        )


    if (
        "why faiss" in q
        or "why use faiss" in q
        or "why did you choose faiss" in q
        or "are you using faiss" in q
        or "do you use faiss" in q
    ):

        return (
            "ResearchMind AI uses **FAISS** for efficient "
            "similarity-based retrieval of relevant research-paper "
            "chunks from the stored embeddings."
        )


    # ========================================================
    # EMBEDDINGS
    # ========================================================

    if (
        "which embedding model" in q
        or "what embedding model" in q
        or "embedding model are you using" in q
    ):

        return (
            "ResearchMind AI uses **all-MiniLM-L6-v2** with "
            "**Sentence Transformers** to generate embeddings "
            "from research-paper text chunks."
        )


    if (
        "what is an embedding" in q
        or "what are embeddings" in q
        or q == "embedding"
        or q == "embeddings"
    ):

        return (
            "An embedding is a numerical vector representation "
            "of text. ResearchMind AI converts research-paper "
            "chunks into embeddings so FAISS can retrieve text "
            "relevant to a user's question."
        )


    # ========================================================
    # API
    # ========================================================

    if "openai" in q or "open ai" in q:

        return (
            "No. The core ResearchMind AI chatbot does **not use "
            "the OpenAI API**. It uses the local "
            "**Qwen2.5-3B-Instruct** model."
        )


    if "gemini" in q:

        return (
            "No. The core ResearchMind AI chatbot does **not use "
            "the Gemini API**. It uses the local "
            "**Qwen2.5-3B-Instruct** model."
        )


    if "claude" in q:

        return (
            "No. ResearchMind AI does **not use Claude API**. "
            "The chatbot uses the local "
            "**Qwen2.5-3B-Instruct** model."
        )


    # ========================================================
    # FINE TUNING
    # ========================================================

    if (
        "fine tuning" in q
        or "finetuning" in q
        or "fine tune" in q
        or "fine tuned" in q
        or "lora" in q
    ):

        return (
            "No. ResearchMind AI does **not use LoRA fine-tuning** "
            "for Qwen2.5-3B-Instruct. The project uses the local "
            "Qwen2.5-3B-Instruct model together with RAG."
        )


    # ========================================================
    # TRAINING
    # ========================================================

    if (
        "training your own llm" in q
        or "train your own llm" in q
        or "training our own llm" in q
        or "train our own llm" in q
        or "are you training your own llm" in q
        or "do you train your own llm" in q
    ):

        return (
            "No. ResearchMind AI does **not train an LLM from "
            "scratch**. It uses the existing local "
            "**Qwen2.5-3B-Instruct** model for generation."
        )


    # ========================================================
    # OFFLINE
    # ========================================================

    if (
        "offline" in q
        or "without api" in q
        or "no api" in q
    ):

        return (
            "Yes. ResearchMind AI is designed as an **offline "
            "AI research system**. Its core AI pipeline uses "
            "local models instead of external generative-AI APIs."
        )


    # ========================================================
    # PURPOSE
    # ========================================================

    if (
        "purpose" in q
        or "what is researchmind" in q
        or "what does this project do" in q
        or "what does this website do" in q
        or "what is this project" in q
        or "what is this website" in q
    ):

        return (
            "**ResearchMind AI** is an offline AI Research "
            "Intelligence System designed to help users "
            "understand and analyze uploaded research papers.\n\n"
            "Users upload PDFs, the system extracts and chunks "
            "their text, creates embeddings, stores them in FAISS, "
            "retrieves relevant information using RAG, and uses "
            "Qwen2.5-3B-Instruct to generate answers locally."
        )


    # ========================================================
    # ARCHITECTURE
    # ========================================================

    if (
        "architecture" in q
        or "tech stack" in q
        or "technologies used" in q
        or "technology used" in q
    ):

        return (
            "The main ResearchMind AI architecture consists of:\n\n"
            "- **PDF Processing** – extracts research-paper text.\n"
            "- **Chunking** – divides text into smaller chunks.\n"
            "- **Sentence Transformers** – generates embeddings "
            "using all-MiniLM-L6-v2.\n"
            "- **FAISS** – stores and retrieves embeddings.\n"
            "- **RAG** – retrieves relevant paper context.\n"
            "- **Qwen2.5-3B-Instruct** – generates the final answer "
            "locally."
        )


    # ========================================================
    # PDF PROCESSING
    # ========================================================

    if (
        "pdf processing" in q
        or "pdf extraction" in q
        or "text extraction" in q
        or "chunking" in q
        or "how are pdfs processed" in q
        or "how is pdf processed" in q
    ):

        return (
            "ResearchMind AI processes uploaded PDFs by extracting "
            "their text, cleaning the content, dividing it into "
            "smaller chunks, generating embeddings for those chunks, "
            "and storing the embeddings in FAISS for later retrieval."
        )


    # ========================================================
    # CHATBOT
    # ========================================================

    if (
        "chatbot" in q
        or "research assistant" in q
        or "how does the chatbot work" in q
        or "how does chatbot work" in q
    ):

        return (
            "The ResearchMind AI chatbot uses a **RAG pipeline**. "
            "When you ask a question, FAISS searches the vector "
            "database for relevant research-paper chunks. Those "
            "chunks are provided to the local Qwen2.5-3B-Instruct "
            "model, which generates the answer."
        )


    return None


# ============================================================
# CHAT API
# ============================================================

@chat_bp.route("/api/chat", methods=["POST"])
def chat():

    # ========================================================
    # REQUEST
    # ========================================================

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400


    question = data.get(
        "question",
        ""
    ).strip()


    if not question:

        return jsonify({
            "success": False,
            "message": "Please enter a question."
        }), 400


    question_lower = normalize_question(
        question
    )


    # ========================================================
    # 1. GREETING
    # ========================================================

    if is_greeting(question_lower):

        return jsonify({
            "success": True,
            "answer": (
                "Hi! 👋 I'm your Research Assistant.\n\n"
                "You can ask me about your uploaded research "
                "papers or anything about the ResearchMind AI project."
            )
        })


    # ========================================================
    # 2. BASIC CONVERSATION
    # ========================================================

    if question_lower in [
        "how are you",
        "how are you?",
        "are you fine",
        "are you okay",
        "how do you feel"
    ]:

        return jsonify({
            "success": True,
            "answer": (
                "I'm doing well! 😊 "
                "I'm ready to help you with your research "
                "papers and the ResearchMind AI project."
            )
        })


    # ========================================================
    # 3. PAPER COMPARISON
    # ========================================================
    #
    # IMPORTANT:
    # Comparison questions must NOT go through normal
    # FAISS RAG retrieval.
    #
    # They must directly use PaperComparisonEngine.
    #

    if is_comparison_question(question_lower):

        print("\n===================================")
        print("CHATBOT: PAPER COMPARISON")
        print("Question:", question)
        print("===================================")

        try:

            comparison_engine = PaperComparisonEngine()

            result = comparison_engine.compare_papers()

        except Exception as e:

            print(
                "Paper Comparison Error:",
                e
            )

            return jsonify({
                "success": True,
                "answer": (
                    "I couldn't compare the uploaded papers "
                    "right now. Please make sure that the papers "
                    "are uploaded correctly."
                )
            })


        # -----------------------------------------
        # Successful comparison
        # -----------------------------------------

        if result.get("success"):

            comparison = result.get(
                "comparison"
            )

            if comparison:

                return jsonify({
                    "success": True,
                    "answer": comparison
                })


        # -----------------------------------------
        # Comparison failed
        # -----------------------------------------

        return jsonify({
            "success": True,
            "answer": (
                "I couldn't compare the uploaded papers "
                "right now. Please make sure that the required "
                "research papers are uploaded."
            )
        })


    # ========================================================
    # 4. DIRECT PROJECT ANSWER
    # ========================================================

    direct_answer = get_direct_project_answer(
        question
    )

    if direct_answer:

        return jsonify({
            "success": True,
            "answer": direct_answer
        })


    # ========================================================
    # 5. GENERAL PROJECT QUESTION
    # ========================================================

    if is_project_question(
        question_lower
    ):

        project_prompt = f"""
You are the ResearchMind AI Project Assistant.

Answer ONLY using the project information below.

STRICT RULES:

1. Do not use outside knowledge.
2. Do not guess.
3. Do not assume.
4. Do not invent features.
5. Do not invent technologies.
6. Do not invent model names.
7. Do not invent APIs.
8. Do not invent project capabilities.
9. Every factual statement must be supported by the
   PROJECT INFORMATION.
10. Give a direct and simple answer.

PROJECT INFORMATION
===================

{PROJECT_CONTEXT}

USER QUESTION
=============

{question}

Answer only from the project information.
"""


        try:

            answer = ask_llm(
                question=question,
                context=project_prompt,
                max_tokens=300
            )

        except Exception as e:

            print(
                "Project LLM Error:",
                e
            )

            return jsonify({
                "success": True,
                "answer": UNRELATED_MESSAGE
            })


        return jsonify({
            "success": True,
            "answer": answer.strip()
        })


    # ========================================================
    # 6. RESEARCH QUESTION DETECTION
    # ========================================================

    research_keywords = [

        "paper",
        "papers",
        "research",
        "study",
        "studies",

        "method",
        "methodology",
        "approach",
        "algorithm",

        "model",
        "dataset",
        "data",

        "experiment",
        "experiments",

        "result",
        "results",

        "finding",
        "findings",

        "conclusion",

        "abstract",
        "introduction",

        "literature",
        "literature review",

        "research gap",
        "gap",

        "limitation",
        "limitations",

        "future work",
        "future research",

        "objective",
        "objectives",

        "problem statement",

        "technique",
        "techniques",

        "performance",
        "accuracy",

        "comparison",
        "compare",

        "summarize",
        "summary",

        "explain",

        "author",
        "authors",

        "publication",
        "journal",
        "conference",

        "domain",
        "research domain",

        "research field",
        "research area",

        "topic",
        "subject"
    ]


    is_research_question = any(
        keyword in question_lower
        for keyword in research_keywords
    )


    # ========================================================
    # 7. BLOCK UNRELATED QUESTIONS
    # ========================================================

    if not is_research_question:

        return jsonify({
            "success": True,
            "answer": UNRELATED_MESSAGE
        })


    # ========================================================
    # 8. RETRIEVE RESEARCH CONTEXT
    # ========================================================

    try:

        context = get_retriever().retrieve_context(
            question=question,
            top_k=10
        )

    except Exception as e:

        print(
            "Retriever Error:",
            e
        )

        return jsonify({
            "success": True,
            "answer": (
                "I couldn't retrieve the research-paper "
                "information right now. Please try again."
            )
        })


    # ========================================================
    # 9. NO CONTEXT
    # ========================================================

    if not context:

        return jsonify({
            "success": True,
            "answer": "Not Available"
        })


    # ========================================================
    # 10. STRICT RAG PROMPT
    # ========================================================

    research_prompt = f"""
You are the Research Assistant inside ResearchMind AI.

Your ONLY source of factual information is the
RESEARCH PAPER CONTEXT provided below.

============================================================
STRICT ANTI-HALLUCINATION RULES
============================================================

RULE 1:
Answer ONLY from the supplied research-paper context.

RULE 2:
DO NOT use your pretrained/general knowledge.

RULE 3:
DO NOT guess.

RULE 4:
DO NOT assume.

RULE 5:
DO NOT fill missing information with common knowledge.

RULE 6:
DO NOT invent authors.

RULE 7:
DO NOT invent datasets.

RULE 8:
DO NOT invent methods.

RULE 9:
DO NOT invent models.

RULE 10:
DO NOT invent results.

RULE 11:
DO NOT invent numbers or statistics.

RULE 12:
DO NOT invent conclusions.

RULE 13:
DO NOT invent citations or references.

RULE 14:
If the context supports the answer, answer it clearly.

RULE 15:
If the context does NOT support the requested information,
return exactly:

Not Available

RULE 16:
If the user asks for an explanation, explain only the
information supported by the context.

RULE 17:
If the user asks "what is this paper about", determine
the answer from the title, abstract, introduction, problem,
methodology, and other supplied content.

RULE 18:
If multiple papers appear in the context, do not mix facts
between papers.

RULE 19:
If the user names a specific paper, answer using that paper's
information when available.

RULE 20:
Never create an answer simply because the question sounds
reasonable.

============================================================
RESEARCH PAPER CONTEXT
============================================================

{context}

============================================================
USER QUESTION
============================================================

{question}

============================================================

Now answer the user.

Remember:

FACTS MUST COME FROM THE CONTEXT.

If unsupported:

Not Available
"""


    # ========================================================
    # 11. GENERATE ANSWER
    # ========================================================

    try:

        answer = ask_llm(
            question=question,
            context=research_prompt,
            max_tokens=400
        )

    except Exception as e:

        print(
            "LLM Error:",
            e
        )

        return jsonify({
            "success": True,
            "answer": (
                "I couldn't generate the answer right now. "
                "Please try again."
            )
        })


    # ========================================================
    # 12. CLEAN ANSWER
    # ========================================================

    answer = answer.strip()


    if not answer:

        answer = "Not Available"


    # ========================================================
    # 13. RETURN
    # ========================================================

    return jsonify({
        "success": True,
        "answer": answer
    })