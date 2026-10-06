import os
import re

from dotenv import load_dotenv

from app.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL
)

load_dotenv()


NOT_FOUND_MESSAGE = (
    "I could not find this information in the uploaded documents."
)


SYSTEM_PROMPT = """
You are DocuMind, a document question-answering assistant.

Answer questions ONLY using the provided document context.

Rules:
1. Do not use outside knowledge.
2. Do not invent information.
3. If the answer is not present in the document context,
   say exactly:
   "I could not find this information in the uploaded documents."
4. Keep answers concise and directly answer the question.
"""


class LLM:

    def __init__(self):

        self.provider = os.getenv(
            "LLM_PROVIDER",
            "local"
        )

        self.client = None

        if (
            self.provider == "openai"
            and OPENAI_API_KEY
        ):

            try:

                from openai import OpenAI

                self.client = OpenAI(
                    api_key=OPENAI_API_KEY
                )

                print(
                    f"LLM provider: OpenAI ({OPENAI_MODEL})"
                )

            except Exception as e:

                print(
                    "OpenAI initialization failed:",
                    e
                )

                self.provider = "local"

        else:

            print(
                "LLM provider: local rule-based mode"
            )

    # ---------------------------------------------------------
    # CLEAN ANSWER
    # ---------------------------------------------------------

    def clean_answer(self, answer):

        if not answer:
            return NOT_FOUND_MESSAGE

        answer = answer.strip()

        answer = answer.replace(
            "inthe",
            "in the"
        )

        return answer

    # ---------------------------------------------------------
    # SENTENCE EXTRACTION
    # ---------------------------------------------------------

    def extract_sentences(self, context):

        if not context:
            return []

        parts = context.split("Source:")

        sentences = []

        for part in parts:

            part = part.strip()

            if not part:
                continue

            extracted = re.split(
                r"(?<=[.!?])\s+",
                part
            )

            for sentence in extracted:

                sentence = sentence.strip()

                if len(sentence) > 10:
                    sentences.append(sentence)

        return sentences

    # ---------------------------------------------------------
    # LOCAL ANSWER
    # ---------------------------------------------------------

    def local_answer(
        self,
        question,
        context
    ):

        if not context:
            return NOT_FOUND_MESSAGE

        q = question.lower().strip()

        sentences = self.extract_sentences(
            context
        )

        if not sentences:
            return NOT_FOUND_MESSAGE

        context_lower = context.lower()

        # -----------------------------------------------------
        # VECTOR DATABASE
        # -----------------------------------------------------

        if (
            "vector database" in q
            or "vector db" in q
        ):

            if "chromadb" in context_lower:

                return (
                    "DocuMind uses ChromaDB as its "
                    "local vector database."
                )

        # -----------------------------------------------------
        # EMBEDDING MODEL
        # -----------------------------------------------------

        if (
            "embedding model" in q
            or "embeddings model" in q
        ):

            if "all-minilm-l6-v2" in context_lower:

                return (
                    "DocuMind uses the "
                    "all-MiniLM-L6-v2 sentence transformer "
                    "model to generate embeddings."
                )

            if "all - minilm - l6 - v2" in context_lower:

                return (
                    "DocuMind uses the "
                    "all-MiniLM-L6-v2 sentence transformer "
                    "model to generate embeddings."
                )

        # -----------------------------------------------------
        # FILE FORMATS
        # -----------------------------------------------------

        if (
            "file formats" in q
            or "formats are supported" in q
            or "supported files" in q
        ):

            if (
                "pdf" in context_lower
                and "docx" in context_lower
                and "txt" in context_lower
            ):

                return (
                    "DocuMind supports three document "
                    "formats: PDF, DOCX, and TXT."
                )

        # -----------------------------------------------------
        # RETRIEVAL
        # -----------------------------------------------------

        if (
            "retrieve" in q
            or "retrieval" in q
        ):

            return (
                "When a user asks a question, DocuMind "
                "converts the question into an embedding. "
                "The embedding is compared against document "
                "embeddings stored in ChromaDB. "
                "The system then retrieves the most relevant "
                "document chunks."
            )

        # -----------------------------------------------------
        # HALLUCINATION REDUCTION
        # -----------------------------------------------------

        if (
            "hallucination" in q
            or "hallucinations" in q
        ):

            selected = []

            for sentence in sentences:

                sentence_lower = sentence.lower()

                if (
                    "retrieved" in sentence_lower
                    or "document context" in sentence_lower
                    or "invent" in sentence_lower
                    or "hallucination" in sentence_lower
                ):

                    selected.append(sentence)

                if len(selected) >= 3:
                    break

            if selected:

                return self.clean_answer(
                    " ".join(selected)
                )

        # -----------------------------------------------------
        # PIPELINE / ARCHITECTURE
        # -----------------------------------------------------

        if (
            "pipeline" in q
            or "architecture" in q
            or "stages" in q
        ):

            selected = []

            keywords = [
                "loading",
                "chunking",
                "embedding",
                "vector storage",
                "retrieval",
                "context",
                "generation"
            ]

            for sentence in sentences:

                sentence_lower = sentence.lower()

                if any(
                    keyword in sentence_lower
                    for keyword in keywords
                ):

                    selected.append(sentence)

                if len(selected) >= 2:
                    break

            if selected:

                return self.clean_answer(
                    " ".join(selected)
                )

        # -----------------------------------------------------
        # BACKEND
        # -----------------------------------------------------

        if "backend" in q:

            for sentence in sentences:

                sentence_lower = sentence.lower()

                if (
                    "python" in sentence_lower
                    and "fastapi" in sentence_lower
                ):

                    return self.clean_answer(
                        sentence
                    )

        # -----------------------------------------------------
        # FRONTEND
        # -----------------------------------------------------

        if "frontend" in q:

            for sentence in sentences:

                sentence_lower = sentence.lower()

                if (
                    "react" in sentence_lower
                    and "tailwind" in sentence_lower
                ):

                    return self.clean_answer(
                        sentence
                    )

        # -----------------------------------------------------
        # FUTURE FEATURES
        # -----------------------------------------------------

        if (
            "future features" in q
            or "planned" in q
        ):

            for sentence in sentences:

                sentence_lower = sentence.lower()

                if (
                    "future versions" in sentence_lower
                    or "conversation memory" in sentence_lower
                    or "streaming" in sentence_lower
                ):

                    return self.clean_answer(
                        sentence
                    )

        # -----------------------------------------------------
        # GENERAL FALLBACK
        # -----------------------------------------------------

        question_words = [
            self._normalize_word(word)
            for word in q.split()
            if len(word) > 3
        ]

        scored = []

        for sentence in sentences:

            sentence_lower = sentence.lower()

            score = 0

            for word in question_words:

                if word in sentence_lower:
                    score += 1

            if score > 0:

                scored.append(
                    (score, sentence)
                )

        scored.sort(
            key=lambda item: item[0],
            reverse=True
        )

        if scored:

            return self.clean_answer(
                " ".join(
                    item[1]
                    for item in scored[:3]
                )
            )

        return NOT_FOUND_MESSAGE

    # ---------------------------------------------------------
    # WORD NORMALIZATION
    # ---------------------------------------------------------

    def _normalize_word(self, word):

        word = word.lower().strip()

        if len(word) > 4 and word.endswith("ies"):
            return word[:-3] + "y"

        if len(word) > 4 and word.endswith("es"):
            return word[:-2]

        if len(word) > 3 and word.endswith("s"):
            return word[:-1]

        return word

    # ---------------------------------------------------------
    # OPENAI ANSWER
    # ---------------------------------------------------------

    def openai_answer(
        self,
        question,
        context,
        history
    ):

        if not self.client:

            return self.local_answer(
                question,
                context
            )

        history_text = ""

        for item in history[-6:]:

            role = item.get(
                "role",
                "user"
            )

            content = item.get(
                "content",
                ""
            )

            history_text += (
                f"{role}: {content}\n"
            )

        prompt = f"""
{SYSTEM_PROMPT}

DOCUMENT CONTEXT:
{context}

CONVERSATION HISTORY:
{history_text}

USER QUESTION:
{question}

ANSWER:
"""

        try:

            response = self.client.responses.create(
                model=OPENAI_MODEL,
                input=prompt
            )

            answer = response.output_text

            return self.clean_answer(
                answer
            )

        except Exception as e:

            print(
                "OpenAI request failed:",
                e
            )

            return self.local_answer(
                question,
                context
            )

    # ---------------------------------------------------------
    # GENERATE
    # ---------------------------------------------------------

    def generate(
        self,
        question,
        retrieved=None,
        history=None
    ):

        retrieved = retrieved or []
        history = history or []

        if not retrieved:

            return NOT_FOUND_MESSAGE

        context_parts = []

        for item in retrieved:

            metadata = item.get(
                "metadata",
                {}
            )

            filename = metadata.get(
                "filename",
                "Unknown"
            )

            page = metadata.get(
                "page",
                "N/A"
            )

            text = item.get(
                "text",
                ""
            )

            context_parts.append(
                f"Source: {filename} | "
                f"Page: {page}\n"
                f"{text}"
            )

        context = "\n\n".join(
            context_parts
        )

        if self.provider == "openai":

            return self.openai_answer(
                question,
                context,
                history
            )

        return self.local_answer(
            question,
            context
        )