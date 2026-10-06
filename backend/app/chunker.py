from sentence_transformers import SentenceTransformer

from app.config import CHUNK_SIZE, CHUNK_OVERLAP


class DocumentChunker:

    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        self.tokenizer = self.model.tokenizer

    def count_tokens(self, text):
        tokens = self.tokenizer.encode(
            text,
            add_special_tokens=False
        )

        return len(tokens)

    def chunk_text(self, text):
        tokens = self.tokenizer.encode(
            text,
            add_special_tokens=False
        )

        chunks = []

        start = 0

        while start < len(tokens):

            end = min(
                start + CHUNK_SIZE,
                len(tokens)
            )

            chunk_tokens = tokens[start:end]

            chunk_text = self.tokenizer.decode(
                chunk_tokens,
                skip_special_tokens=True
            )

            if chunk_text.strip():
                chunks.append(chunk_text.strip())

            if end >= len(tokens):
                break

            start = end - CHUNK_OVERLAP

        return chunks

    def create_chunks(self, pages, filename):

        all_chunks = []

        chunk_id = 0

        for page in pages:

            page_chunks = self.chunk_text(
                page["text"]
            )

            for chunk in page_chunks:

                all_chunks.append({
                    "id": f"{filename}_{chunk_id}",
                    "text": chunk,
                    "metadata": {
                        "filename": filename,
                        "page": page["page"],
                        "chunk_id": chunk_id
                    }
                })

                chunk_id += 1

        return all_chunks