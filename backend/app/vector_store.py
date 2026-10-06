import chromadb

from app.config import (
    CHROMA_PATH,
    COLLECTION_NAME
)


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=COLLECTION_NAME
            )
        )

    # ==================================================
    # ADD / UPDATE DOCUMENTS
    # ==================================================

    def add_documents(
        self,
        chunks,
        embeddings
    ):

        documents = [
            chunk["text"]
            for chunk in chunks
        ]

        ids = [
            chunk["id"]
            for chunk in chunks
        ]

        metadatas = [
            chunk["metadata"]
            for chunk in chunks
        ]

        self.collection.upsert(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    # ==================================================
    # SEARCH
    # ==================================================

    def search(
        self,
        query_embedding,
        top_k=5
    ):

        if self.collection.count() == 0:

            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

        document_count = (
            self.collection.count()
        )

        n_results = min(
            top_k,
            document_count
        )

        results = self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=n_results
        )

        return results

    # ==================================================
    # DELETE ENTIRE DOCUMENT
    # ==================================================

    def delete_document(
        self,
        filename
    ):

        self.collection.delete(
            where={
                "filename": filename
            }
        )

    # ==================================================
    # DELETE A SPECIFIC DOCUMENT IF NEEDED
    # ==================================================

    def delete_by_filename(
        self,
        filename
    ):

        self.collection.delete(
            where={
                "filename": filename
            }
        )

        print(
            f"Deleted '{filename}' from ChromaDB."
        )

    # ==================================================
    # LIST STORED DOCUMENTS
    # ==================================================

    def get_all_metadata(self):

        result = self.collection.get(
            include=[
                "metadatas"
            ]
        )

        return result.get(
            "metadatas",
            []
        )