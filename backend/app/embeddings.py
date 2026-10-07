from sklearn.feature_extraction.text import HashingVectorizer


class EmbeddingModel:

    def __init__(self):
        print("Loading lightweight embedding model...")

        # Fixed-size vector representation.
        #
        # HashingVectorizer does not need to learn a vocabulary,
        # so document and query vectors always have the same size.
        self.vectorizer = HashingVectorizer(
            n_features=512,
            alternate_sign=False,
            norm="l2",
            lowercase=True,
            strip_accents="unicode"
        )

        print(
            "Lightweight embedding model ready."
        )

    def embed_documents(self, texts):

        vectors = self.vectorizer.transform(
            texts
        )

        return vectors.toarray().tolist()

    def embed_query(self, query):

        vector = self.vectorizer.transform(
            [query]
        )

        return vector.toarray()[0].tolist()