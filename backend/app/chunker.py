import re

from app.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)


class DocumentChunker:

    def __init__(self, model_name=None):

        # model_name is kept in the constructor so that
        # the existing RAGPipeline does not need to change.
        self.model_name = model_name

    def count_tokens(self, text):

        # Lightweight approximation of token count.
        # This avoids loading a tokenizer/model.
        words = re.findall(
            r"\S+",
            text
        )

        return len(words)

    def chunk_text(self, text):

        # Convert text into words.
        words = re.findall(
            r"\S+",
            text
        )

        if not words:
            return []

        chunks = []

        start = 0

        while start < len(words):

            end = min(
                start + CHUNK_SIZE,
                len(words)
            )

            chunk_words = words[start:end]

            chunk_text = " ".join(
                chunk_words
            )

            if chunk_text.strip():
                chunks.append(
                    chunk_text.strip()
                )

            if end >= len(words):
                break

            start = max(
                end - CHUNK_OVERLAP,
                start + 1
            )

        return chunks

    def create_chunks(
        self,
        pages,
        filename
    ):

        all_chunks = []

        chunk_id = 0

        for page in pages:

            page_chunks = self.chunk_text(
                page["text"]
            )

            for chunk in page_chunks:

                all_chunks.append({
                    "id": (
                        f"{filename}_"
                        f"{chunk_id}"
                    ),

                    "text": chunk,

                    "metadata": {
                        "filename": filename,
                        "page": page["page"],
                        "chunk_id": chunk_id
                    }
                })

                chunk_id += 1

        return all_chunks