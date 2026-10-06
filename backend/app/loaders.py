from pathlib import Path
from pypdf import PdfReader
from docx import Document


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}


def load_pdf(file_path):
    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "text": text,
                "page": page_number
            })

    return pages


def load_docx(file_path):
    document = Document(file_path)

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    )

    return [{
        "text": text,
        "page": None
    }]


def load_txt(file_path):
    text = Path(file_path).read_text(
        encoding="utf-8",
        errors="ignore"
    )

    return [{
        "text": text,
        "page": None
    }]


def load_document(file_path):
    file_path = Path(file_path)

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path)

    if extension == ".docx":
        return load_docx(file_path)

    if extension == ".txt":
        return load_txt(file_path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )