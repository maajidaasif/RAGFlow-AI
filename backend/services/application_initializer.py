import os

from services.resource_monitor import (
    check_available_ram,
    get_ram_status,
    show_ram_warning
)


# ============================================================
# MODULE 14
# APPLICATION INITIALIZATION & SAFETY CONTROL
# ============================================================

RAM_THRESHOLD_GB = 4


class ApplicationInitializer:

    def __init__(self):

        self.initialized = False

        self.embedding_ready = False
        self.vector_db_ready = False
        self.llm_ready = False
        self.research_engine_ready = False


    # ========================================================
    # MODULE 13 SAFETY CHECK
    # ========================================================

    def check_system_safety(self):

        ram = check_available_ram()

        status = get_ram_status(
            ram,
            RAM_THRESHOLD_GB
        )

        print("\n" + "=" * 60)
        print("RESEARCHMIND AI 2.0 - SYSTEM SAFETY CHECK")
        print("=" * 60)

        print(
            f"Available RAM : {ram:.2f} GB"
        )

        print(
            f"RAM Status    : {status}"
        )

        print("=" * 60)

        if status == "RED":

            show_ram_warning()

            return False

        return True


    # ========================================================
    # INITIALIZE EMBEDDING MODEL
    # ========================================================

    def initialize_embedding(self):

        print("\n[1/4] Initializing embedding model...")

        try:

            from embedding import initialize_embedding_model

            initialize_embedding_model()

            self.embedding_ready = True

            print(
                "      ✓ all-MiniLM-L6-v2 initialized"
            )

            return True

        except Exception as e:

            print(
                f"      ✗ Embedding initialization failed: {e}"
            )

            return False


    # ========================================================
    # INITIALIZE VECTOR DATABASE
    # ========================================================

    def initialize_vector_database(self):

        print("\n[2/4] Initializing vector database...")

        try:

            vector_index = os.path.join(
                "vector_db",
                "faiss_index.bin"
            )

            metadata = os.path.join(
                "vector_db",
                "metadata.pkl"
            )

            if not os.path.exists(vector_index):

                raise FileNotFoundError(
                    "FAISS index not found."
                )

            if not os.path.exists(metadata):

                raise FileNotFoundError(
                    "FAISS metadata not found."
                )

            self.vector_db_ready = True

            print(
                "      ✓ FAISS database available"
            )

            return True

        except Exception as e:

            print(
                f"      ✗ Vector database initialization failed: {e}"
            )

            return False


    # ========================================================
    # INITIALIZE LOCAL LLM
    # ========================================================

    def initialize_llm(self):

        print("\n[3/4] Initializing local LLM...")

        try:

            from llm.local_llm import initialize_llm

            initialize_llm()

            self.llm_ready = True

            print(
                "      ✓ Qwen2.5-3B-Instruct initialized"
            )

            return True

        except Exception as e:

            print(
                f"      ✗ LLM initialization failed: {e}"
            )

            return False


    # ========================================================
    # INITIALIZE RESEARCHMIND ENGINE
    # ========================================================

    def initialize_research_engine(self):

        print("\n[4/4] Initializing ResearchMind engine...")

        try:

            # The ResearchMind engine is considered ready
            # after the core AI components are initialized.

            if not self.embedding_ready:

                raise RuntimeError(
                    "Embedding model is not ready."
                )

            if not self.vector_db_ready:

                raise RuntimeError(
                    "Vector database is not ready."
                )

            if not self.llm_ready:

                raise RuntimeError(
                    "Local LLM is not ready."
                )

            self.research_engine_ready = True

            print(
                "      ✓ ResearchMind engine ready"
            )

            return True

        except Exception as e:

            print(
                f"      ✗ ResearchMind engine initialization failed: {e}"
            )

            return False


    # ========================================================
    # START APPLICATION
    # ========================================================

    def initialize(self):

        print("\n")
        print("=" * 60)
        print("STARTING RESEARCHMIND AI 2.0")
        print("=" * 60)

        # ---------------------------------------------
        # Step 1: Safety
        # ---------------------------------------------

        if not self.check_system_safety():

            print("\nStartup cancelled for system safety.")

            return False

        # ---------------------------------------------
        # Step 2: Embedding
        # ---------------------------------------------

        if not self.initialize_embedding():

            print("\nStartup cancelled.")

            return False

        # ---------------------------------------------
        # Step 3: Vector Database
        # ---------------------------------------------

        if not self.initialize_vector_database():

            print("\nStartup cancelled.")

            return False

        # ---------------------------------------------
        # Step 4: Local LLM
        # ---------------------------------------------

        if not self.initialize_llm():

            print("\nStartup cancelled.")

            return False

        # ---------------------------------------------
        # Step 5: ResearchMind Engine
        # ---------------------------------------------

        if not self.initialize_research_engine():

            print("\nStartup cancelled.")

            return False

        self.initialized = True

        print("\n" + "=" * 60)
        print("RESEARCHMIND AI 2.0 IS READY")
        print("=" * 60)

        return True