from pathlib import Path

from app.config import (
    EMBEDDING_MODEL,
    TOP_K,
    DISTANCE_THRESHOLD
)

from app.loaders import load_document
from app.chunker import DocumentChunker
from app.embeddings import EmbeddingModel
from app.vector_store import VectorStore
from app.llm import LLM


class RAGPipeline:

    def __init__(self):

        print(
            "Initializing DocuMind RAG pipeline..."
        )

        self.chunker = DocumentChunker(
            EMBEDDING_MODEL
        )

        self.embedding_model = EmbeddingModel()

        self.vector_store = VectorStore()

        self.llm = LLM()

        print(
            "DocuMind RAG pipeline ready."
        )

    # ==================================================
    # INGEST DOCUMENT
    # ==================================================

    def ingest(self, file_path):

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        filename = file_path.name

        print(
            f"Loading document: {filename}"
        )

        # Remove old chunks for this document
        # before inserting the new version.
        try:

            self.vector_store.delete_by_filename(
                filename
            )

        except Exception as e:

            print(
                "Warning while deleting old chunks:",
                e
            )

        # --------------------------------------------------
        # LOAD
        # --------------------------------------------------

        pages = load_document(
            str(file_path)
        )

        if not pages:

            raise ValueError(
                "No readable text was found in the document."
            )

        print(
            f"Loaded {len(pages)} page/section(s)."
        )

        # --------------------------------------------------
        # CHUNK
        # --------------------------------------------------

        chunks = self.chunker.create_chunks(
            pages,
            filename
        )

        if not chunks:

            raise ValueError(
                "No text chunks could be created "
                "from the document."
            )

        print(
            f"Created {len(chunks)} chunks."
        )

        # --------------------------------------------------
        # EMBEDDINGS
        # --------------------------------------------------

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        print(
            "Generating lightweight embeddings..."
        )

        embeddings = (
            self.embedding_model.embed_documents(
                texts
            )
        )

        # --------------------------------------------------
        # VECTOR STORAGE
        # --------------------------------------------------

        print(
            "Storing chunks in ChromaDB..."
        )

        self.vector_store.add_documents(
            chunks,
            embeddings
        )

        print(
            f"Successfully indexed {filename}"
        )

        return len(chunks)

    # ==================================================
    # WORD NORMALIZATION
    # ==================================================

    def normalize_word(self, word):

        word = word.lower().strip()

        if word.endswith("ies"):

            return (
                word[:-3] + "y"
            )

        if (
            word.endswith("s")
            and not word.endswith("ss")
        ):

            return word[:-1]

        return word

    # ==================================================
    # QUESTION TYPE CHECK
    # ==================================================

    def is_clearly_off_topic(
        self,
        question
    ):
        """
        Detect requests that ask DocuMind to perform
        a programming/task operation instead of answering
        from uploaded documents.
        """

        question_text = (
            question.lower().strip()
        )

        task_phrases = [

            "write a program",

            "write python code",

            "write code",

            "generate code",

            "create a program",

            "make a program",

            "solve this coding problem",

            "code for",

            "program to",

            "python program",

            "implement",

            "write an algorithm",

            "generate an algorithm"

        ]

        for phrase in task_phrases:

            if phrase in question_text:

                return True

        return False

    # ==================================================
    # QUERY EXPANSION
    # ==================================================

    def expand_query(
        self,
        question
    ):
        """
        Expand broad architecture/pipeline questions
        with important document terms.

        This improves retrieval when using the lightweight
        HashingVectorizer embedding model.
        """

        question_text = (
            question.lower().strip()
        )

        pipeline_question = (

            "main stages" in question_text

            or "pipeline stages" in question_text

            or "stages of the pipeline" in question_text

            or "documind pipeline" in question_text

            or "pipeline" in question_text

            or "architecture" in question_text

        )

        if pipeline_question:

            return (
                question
                + " "
                + "document loading "
                + "text chunking "
                + "embedding generation "
                + "vector storage "
                + "retrieval "
                + "context construction "
                + "language model generation "
                + "architecture stages"
            )

        return question

    # ==================================================
    # DOCUMENT SUPPORT CHECK
    # ==================================================

    def has_question_support(
        self,
        question,
        retrieved
    ):

        if not retrieved:

            return False

        question_text = (
            question.lower()
        )

        # Explicit off-topic protection
        if self.is_clearly_off_topic(
            question
        ):

            return False

        retrieved_text = " ".join(

            item["text"].lower()

            for item in retrieved

        )

        # --------------------------------------------------
        # PIPELINE / ARCHITECTURE QUESTIONS
        # --------------------------------------------------

        pipeline_phrases = [

            "main stages",

            "stages of the pipeline",

            "pipeline stages",

            "architecture",

            "how does the pipeline work",

            "pipeline consists",

            "documind pipeline"

        ]

        if any(
            phrase in question_text
            for phrase in pipeline_phrases
        ):

            architecture_terms = [

                "loading",

                "chunking",

                "embedding",

                "vector storage",

                "retrieval",

                "context",

                "generation"

            ]

            matches = sum(

                1

                for term in architecture_terms

                if term in retrieved_text

            )

            # Architecture questions need multiple
            # pieces of evidence rather than one keyword.

            if matches >= 2:

                return True

        # --------------------------------------------------
        # DIRECT WORD MATCH
        # --------------------------------------------------

        question_words = [

            self.normalize_word(word)

            for word in question_text.split()

            if len(word) > 3

        ]

        direct_matches = 0

        for word in question_words:

            normalized_word = (
                self.normalize_word(word)
            )

            if normalized_word in retrieved_text:

                direct_matches += 1

        if direct_matches >= 1:

            return True

        # --------------------------------------------------
        # CONCEPTUAL GROUPS
        # --------------------------------------------------

        conceptual_groups = {

            "hallucination": [

                "hallucination",

                "invent",

                "retrieved",

                "document context",

                "cannot be found"

            ],

            "retrieval": [

                "retrieval",

                "retrieve",

                "embedding",

                "similarity",

                "relevant",

                "chunks"

            ],

            "embedding": [

                "embedding",

                "vector",

                "sentence transformer"

            ],

            "architecture": [

                "loading",

                "chunking",

                "embedding",

                "storage",

                "retrieval",

                "context",

                "generation"

            ],

            "file": [

                "pdf",

                "docx",

                "txt",

                "document formats"

            ]

        }

        for concept, evidence_terms in (
            conceptual_groups.items()
        ):

            if concept not in question_text:

                continue

            evidence_matches = sum(

                1

                for term in evidence_terms

                if term in retrieved_text

            )

            if evidence_matches >= 2:

                return True

        return False

    # ==================================================
    # RELEVANCE CHECK
    # ==================================================

    def is_relevant(
        self,
        retrieved
    ):

        if not retrieved:

            return False

        valid_distances = [

            item["distance"]

            for item in retrieved

            if item["distance"] is not None

        ]

        if not valid_distances:

            return False

        best_distance = min(
            valid_distances
        )

        print(
            f"Best retrieval distance: "
            f"{best_distance:.4f}"
        )

        print(
            f"Distance threshold: "
            f"{DISTANCE_THRESHOLD:.4f}"
        )

        return (
            best_distance
            <= DISTANCE_THRESHOLD
        )

    # ==================================================
    # STRONG SUPPORT
    # ==================================================

    def is_strongly_supported(
        self,
        question,
        retrieved
    ):

        return self.has_question_support(
            question,
            retrieved
        )

    # ==================================================
    # REJECTION LOGIC
    # ==================================================

    def should_reject(
        self,
        question,
        retrieved
    ):

        # Programming/task requests are always rejected
        # because DocuMind answers from uploaded documents.

        if self.is_clearly_off_topic(
            question
        ):

            return True

        if not retrieved:

            return True

        # If the retrieved context clearly supports
        # the question, allow the LLM to answer.

        if self.is_strongly_supported(
            question,
            retrieved
        ):

            return False

        # Otherwise use the vector similarity threshold.

        if self.is_relevant(
            retrieved
        ):

            return False

        return True

    # ==================================================
    # RETRIEVE
    # ==================================================

    def retrieve(
        self,
        question
    ):

        # --------------------------------------------------
        # EXPAND QUERY BEFORE EMBEDDING
        # --------------------------------------------------

        expanded_question = (
            self.expand_query(
                question
            )
        )

        if expanded_question != question:

            print(
                "Expanded retrieval query:"
            )

            print(
                expanded_question
            )

        # --------------------------------------------------
        # CREATE QUERY EMBEDDING
        # --------------------------------------------------

        query_embedding = (
            self.embedding_model.embed_query(
                expanded_question
            )
        )

        # --------------------------------------------------
        # SEARCH CHROMADB
        # --------------------------------------------------

        results = (
            self.vector_store.search(
                query_embedding,
                TOP_K
            )
        )

        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        retrieved = []

        for index in range(
            len(documents)
        ):

            metadata = (

                metadatas[index]

                if index < len(metadatas)

                else {}

            )

            distance = (

                distances[index]

                if index < len(distances)

                else None

            )

            retrieved.append({

                "text": documents[index],

                "metadata": metadata,

                "distance": distance

            })

        return retrieved

    # ==================================================
    # ASK
    # ==================================================

    def ask(
        self,
        question,
        history=None
    ):

        # --------------------------------------------------
        # OFF-TOPIC CHECK
        # --------------------------------------------------

        if self.is_clearly_off_topic(
            question
        ):

            return {

                "answer": (
                    "I could not find this information "
                    "in the uploaded documents."
                ),

                "sources": []

            }

        # --------------------------------------------------
        # RETRIEVE
        # --------------------------------------------------

        retrieved = self.retrieve(
            question
        )

        # --------------------------------------------------
        # REJECTION CHECK
        # --------------------------------------------------

        if self.should_reject(
            question,
            retrieved
        ):

            return {

                "answer": (
                    "I could not find this information "
                    "in the uploaded documents."
                ),

                "sources": []

            }

        # --------------------------------------------------
        # GENERATE ANSWER
        # --------------------------------------------------

        answer = self.llm.generate(

            question=question,

            retrieved=retrieved,

            history=history or []

        )

        # --------------------------------------------------
        # BUILD SOURCES
        # --------------------------------------------------

        sources = []

        for item in retrieved[:2]:

            metadata = item.get(
                "metadata",
                {}
            )

            distance = item.get(
                "distance"
            )

            relevance = None

            if distance is not None:

                relevance = max(

                    0,

                    min(

                        100,

                        (1 - distance) * 100

                    )

                )

            sources.append({

                "filename": metadata.get(
                    "filename",
                    "Unknown"
                ),

                "page": metadata.get(
                    "page"
                ),

                "chunk_id": metadata.get(
                    "chunk_id"
                ),

                "distance": distance,

                "relevance": relevance

            })

        # --------------------------------------------------
        # RETURN
        # --------------------------------------------------

        return {

            "answer": answer,

            "sources": sources

        }