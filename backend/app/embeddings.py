from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL


class EmbeddingModel:

    def __init__(self):
        print(
            f"Loading embedding model: {EMBEDDING_MODEL}"
        )

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )

    def embed_documents(self, texts):
        return self.model.encode(
            texts,
            normalize_embeddings=True
        ).tolist()

    def embed_query(self, query):
        return self.model.encode(
            [query],
            normalize_embeddings=True
        )[0].tolist()