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

        print("Initializing DocuMind RAG pipeline...")

        self.chunker = DocumentChunker(
            EMBEDDING_MODEL
        )

        self.embedding_model = EmbeddingModel()

        self.vector_store = VectorStore()

        self.llm = LLM()

        print("DocuMind RAG pipeline ready.")


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

        # ----------------------------------------------
        # Delete old chunks for same document
        # ----------------------------------------------

        try:
            self.vector_store.delete_by_filename(
                filename
            )
        except Exception as e:
            print(
                "Warning while deleting old chunks:",
                e
            )

        # ----------------------------------------------
        # Load document
        # ----------------------------------------------

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

        # ----------------------------------------------
        # Create chunks
        # ----------------------------------------------

        chunks = self.chunker.create_chunks(
            pages,
            filename
        )

        if not chunks:
            raise ValueError(
                "No text chunks could be created from the document."
            )

        print(
            f"Created {len(chunks)} chunks."
        )

        # ----------------------------------------------
        # Generate embeddings
        # ----------------------------------------------

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        print(
            "Generating embeddings..."
        )

        embeddings = (
            self.embedding_model.embed_documents(
                texts
            )
        )

        # ----------------------------------------------
        # Store in ChromaDB
        # ----------------------------------------------

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
    # NORMALIZE WORD
    # ==================================================

    def normalize_word(self, word):

        word = word.lower().strip()

        if word.endswith("ies"):
            return word[:-3] + "y"

        if word.endswith("s") and not word.endswith("ss"):
            return word[:-1]

        return word


    # ==================================================
    # QUESTION SUPPORT CHECK
    # ==================================================

    def has_question_support(
        self,
        question,
        retrieved
    ):

        if not retrieved:
            return False

        question_text = question.lower()

        retrieved_text = " ".join(
            item["text"].lower()
            for item in retrieved
        )

        # ----------------------------------------------
        # Direct keyword matching
        # ----------------------------------------------

        question_words = [
            self.normalize_word(word)
            for word in question_text.split()
            if len(word) > 3
        ]

        direct_matches = 0

        for word in question_words:

            normalized_text = self.normalize_word(
                word
            )

            if normalized_text in retrieved_text:
                direct_matches += 1

        if direct_matches >= 1:
            return True

        # ----------------------------------------------
        # Conceptual matching
        # ----------------------------------------------

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

        for concept, evidence_terms in conceptual_groups.items():

            concept_present = (
                concept in question_text
            )

            if not concept_present:
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

    def is_relevant(self, retrieved):

        if not retrieved:
            return False

        best_distance = min(
            item["distance"]
            for item in retrieved
        )

        return (
            best_distance <=
            DISTANCE_THRESHOLD
        )


    # ==================================================
    # STRONG SUPPORT CHECK
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
    # SHOULD REJECT
    # ==================================================

    def should_reject(
        self,
        question,
        retrieved
    ):

        if not retrieved:
            return True

        # Strong textual support should be allowed
        # even if semantic distance is slightly high.

        if self.is_strongly_supported(
            question,
            retrieved
        ):
            return False

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

        query_embedding = (
            self.embedding_model.embed_query(
                question
            )
        )

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

        retrieved = self.retrieve(
            question
        )

        # ----------------------------------------------
        # Reject unsupported questions
        # ----------------------------------------------

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

        # ----------------------------------------------
        # Generate answer
        # ----------------------------------------------

        answer = self.llm.generate(
            question=question,
            retrieved=retrieved,
            history=history or []
        )

        # ----------------------------------------------
        # Sources
        # ----------------------------------------------

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

        return {
            "answer": answer,
            "sources": sources
        }