import os
from pathlib import Path

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.rag import RAGPipeline


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="DocuMind API",
    description="RAG-based document question answering API",
    version="1.0.0"
)


# ==================================================
# CORS
# ==================================================

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

if FRONTEND_URL:
    ALLOWED_ORIGINS.append(
        FRONTEND_URL.rstrip("/")
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(ALLOWED_ORIGINS)),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# DIRECTORIES
# ==================================================

DOCUMENTS_DIR = Path("data/documents")

DOCUMENTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# RAG PIPELINE
# ==================================================

rag = RAGPipeline()


# ==================================================
# REQUEST MODEL
# ==================================================

class ChatRequest(BaseModel):
    question: str
    history: list[dict] = []


# ==================================================
# ROOT
# ==================================================

@app.get("/")
def root():
    return {
        "message": "DocuMind API is running"
    }


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ==================================================
# UPLOAD DOCUMENT
# ==================================================

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    # ----------------------------------------------
    # Validate filename
    # ----------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    # ----------------------------------------------
    # Validate extension
    # ----------------------------------------------

    extension = Path(
        file.filename
    ).suffix.lower()

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt"
    }

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Only PDF, DOCX and TXT files are allowed."
            )
        )

    # ----------------------------------------------
    # Prevent unsafe path names
    # ----------------------------------------------

    safe_filename = Path(
        file.filename
    ).name

    file_path = (
        DOCUMENTS_DIR /
        safe_filename
    )

    try:

        # ------------------------------------------
        # Read uploaded file
        # ------------------------------------------

        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        # ------------------------------------------
        # Save uploaded file
        # ------------------------------------------

        file_path.write_bytes(contents)

        print(
            f"Received upload: {safe_filename}"
        )

        print(
            f"Saved file to: {file_path}"
        )

        # ------------------------------------------
        # Ingest document into RAG pipeline
        # ------------------------------------------

        chunk_count = rag.ingest(
            str(file_path)
        )

        print(
            f"Created {chunk_count} chunks "
            f"for {safe_filename}"
        )

        # ------------------------------------------
        # Success response
        # ------------------------------------------

        return {
            "message": "Document uploaded successfully.",
            "filename": safe_filename,
            "chunks_created": chunk_count
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            "UPLOAD ERROR:",
            repr(e)
        )

        # ------------------------------------------
        # Remove partially uploaded file
        # ------------------------------------------

        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================================
# LIST DOCUMENTS
# ==================================================

@app.get("/api/documents")
def list_documents():

    documents = []

    try:

        for file_path in DOCUMENTS_DIR.iterdir():

            if not file_path.is_file():
                continue

            extension = (
                file_path.suffix.lower()
            )

            if extension not in {
                ".pdf",
                ".docx",
                ".txt"
            }:
                continue

            documents.append({
                "filename": file_path.name,
                "file_type": (
                    extension
                    .replace(".", "")
                    .upper()
                ),
                "size_bytes": file_path.stat().st_size
            })

        return {
            "documents": documents
        }

    except Exception as e:

        print(
            "DOCUMENT LIST ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================================
# CHAT
# ==================================================

@app.post("/api/chat")
def chat(request: ChatRequest):

    question = request.question.strip()

    # ----------------------------------------------
    # Validate question
    # ----------------------------------------------

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        print(
            f"Question received: {question}"
        )

        # ------------------------------------------
        # Ask RAG pipeline
        # ------------------------------------------

        result = rag.ask(
            question,
            request.history
        )

        # ------------------------------------------
        # Return answer + sources
        # ------------------------------------------

        return {
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as e:

        print(
            "CHAT ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================================
# DELETE DOCUMENT
# ==================================================

@app.delete(
    "/api/documents/{filename}"
)
def delete_document(
    filename: str
):

    # ----------------------------------------------
    # Prevent unsafe path names
    # ----------------------------------------------

    safe_filename = Path(
        filename
    ).name

    file_path = (
        DOCUMENTS_DIR /
        safe_filename
    )

    # ----------------------------------------------
    # Check file exists
    # ----------------------------------------------

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    try:

        # ------------------------------------------
        # Delete vectors from ChromaDB
        # ------------------------------------------

        rag.vector_store.delete_document(
            safe_filename
        )

        # ------------------------------------------
        # Delete physical file
        # ------------------------------------------

        file_path.unlink()

        print(
            f"Deleted document: {safe_filename}"
        )

        return {
            "message": "Document deleted successfully.",
            "filename": safe_filename
        }

    except Exception as e:

        print(
            "DELETE ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )