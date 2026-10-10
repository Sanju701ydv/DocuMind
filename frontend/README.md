# 📚 DocuMind — RAG Document Chatbot

An AI-powered document question-answering application that uses **Retrieval-Augmented Generation (RAG)** to answer questions based on uploaded documents.

<p align="center">
  <a href="https://docu-mind-git-main-samjhana-s-projects.vercel.app/">🌐 Live Demo</a> ·
  <a href="https://documind-backend-rl9a.onrender.com/docs">📖 API Documentation</a>
</p>

## ✨ Features

* 📄 Upload PDF, DOCX, and TXT documents.
* 🔍 Retrieve relevant document chunks using vector similarity search.
* 💬 Ask questions about uploaded documents.
* 📑 Display source references for retrieved content.
* 🛡️ Reduce hallucinations with context-grounded answers and unsupported-question handling.
* 🚫 Handle unrelated questions with guardrails.
* 📊 Evaluate retrieval and answer quality using a test dataset.
* 🗑️ Upload and delete documents through a responsive interface.

## 🛠️ Tech Stack

| Component           | Technologies                     |
| ------------------- | -------------------------------- |
| Frontend            | React, Vite, Tailwind CSS        |
| Backend             | Python, FastAPI, Uvicorn         |
| Embeddings          | Scikit-learn `HashingVectorizer` |
| Vector Database     | ChromaDB                         |
| Document Processing | PyPDF, python-docx               |
| Deployment          | Vercel, Render                   |

## 🏗️ Architecture

```text
User
  ↓
React Frontend (Vercel)
  ↓ REST API
FastAPI Backend (Render)
  ↓
Document Loading → Text Chunking → Embeddings
  ↓
ChromaDB Vector Storage
  ↓
Similarity Search → Context Construction
  ↓
Grounded Answer + Sources
```

## 🔄 How It Works

1. Upload a PDF, DOCX, or TXT document.
2. Extract text and divide it into overlapping chunks.
3. Convert text chunks into numerical vectors.
4. Store the vectors in ChromaDB.
5. Retrieve relevant chunks when a question is asked.
6. Generate an answer using the available context and return source references.

## 📊 Evaluation

The project includes 12 test questions covering retrieval, supported answers, unsupported questions, and off-topic handling.

| Evaluation Metric    | Result |
| -------------------- | -----: |
| Retrieval evaluation |   100% |
| Answer evaluation    |   100% |
| Test cases           |     12 |

*These are results from the project's current test dataset, not a guarantee of accuracy on all documents or questions.*

## 🚀 Run Locally

**1. Clone the repository**

```powershell
git clone https://github.com/Sanju701ydv/DocuMind.git
cd DocuMind
```

**2. Set up the backend**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:

```env
LLM_PROVIDER=local
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5
EMBEDDING_MODEL=lightweight-hashing
CHROMA_PATH=./data/chroma
FRONTEND_URL=http://localhost:5173
```

Start the backend:

```powershell
python -m uvicorn app.main:app --reload
```

**3. Set up the frontend**

Open another PowerShell terminal:

```powershell
cd D:\DocuMind\frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## ⚠️ Deployment Note

The current deployment uses local document and ChromaDB storage. On cloud platforms with ephemeral filesystems, uploaded files and vector data may not persist across restarts or redeployments. Persistent storage is a future improvement.

## 🔮 Future Improvements

* User authentication and document isolation
* Persistent cloud storage
* Streaming responses and conversation history
* Advanced retrieval evaluation and confidence scoring
* Support for additional LLM providers

## 👩‍💻 Author

**Samjhana Yadav**
B.Tech — Computer Science & Engineering

**Interests:** Generative AI · RAG Systems · Machine Learning · Data Analytics

---

⭐ If you find this project useful, consider starring the repository.
