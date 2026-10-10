# 📚 DocuMind — RAG Document Chatbot

An AI-powered document question-answering application built with **Retrieval-Augmented Generation (RAG)** to answer questions using uploaded documents.

🌐 **[Live Demo](https://docu-mind-git-main-samjhana-s-projects.vercel.app/)** · 📖 **[API Documentation](https://documind-backend-rl9a.onrender.com/docs)** · 💻 **[GitHub Repository](https://github.com/Sanju701ydv/DocuMind)**

## ✨ Features

* 📄 Upload PDF, DOCX, and TXT documents.
* 🔍 Retrieve relevant document chunks using vector similarity search.
* 💬 Ask natural-language questions about uploaded documents.
* 📑 Display source references for retrieved content.
* 🛡️ Reduce hallucinations with context-grounded answers.
* 🚫 Handle unsupported and unrelated questions.
* 📊 Evaluate retrieval and answer quality using a test dataset.
* 🗑️ Upload and delete documents through a responsive interface.

## 🖼️ Screenshots

### DocuMind — Main Interface

![DocuMind Main Interface](docs/screenshots/home.png)



## 🛠️ Tech Stack

| Component           | Technologies                   |
| ------------------- | ------------------------------ |
| Frontend            | React, Vite, Tailwind CSS      |
| Backend             | Python, FastAPI, Uvicorn       |
| Embeddings          | Scikit-learn HashingVectorizer |
| Vector Database     | ChromaDB                       |
| Document Processing | PyPDF, python-docx             |
| Deployment          | Vercel, Render                 |

## 🏗️ Architecture

```text
              User
               ↓
       React Frontend
           (Vercel)
               ↓
          REST API
               ↓
       FastAPI Backend
           (Render)
               ↓
    Document Processing
               ↓
        Text Chunking
               ↓
     Embedding Generation
               ↓
          ChromaDB
               ↓
       Similarity Search
               ↓
     Context Construction
               ↓
     Grounded Answer
       + Source References
```

## 🔄 How It Works

1. Upload a PDF, DOCX, or TXT document.
2. Extract text and split it into overlapping chunks.
3. Convert text chunks into numerical vectors.
4. Store the vectors in ChromaDB.
5. Retrieve relevant chunks for each question.
6. Generate a context-grounded answer and display source references.

## 📊 Evaluation

The project includes 12 test questions covering retrieval, supported answers, unsupported questions, and off-topic handling.

| Metric               | Result |
| -------------------- | -----: |
| Retrieval evaluation |   100% |
| Answer evaluation    |   100% |
| Test cases           |     12 |

*Results reflect the current test dataset and do not guarantee accuracy for every document or question.*

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Sanju701ydv/DocuMind.git
cd DocuMind
```

### 2. Set up the backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
```

Create `backend/.env` with the following configuration:

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

Backend: `http://127.0.0.1:8000`
API documentation: `http://127.0.0.1:8000/docs`

### 3. Set up the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

## ⚠️ Deployment Note

The current deployment uses local document and ChromaDB storage. On cloud platforms with ephemeral filesystems, uploaded files and vector data may not persist after restarts or redeployments. Persistent storage is a planned improvement.

## 🔮 Future Improvements

* User authentication and document isolation
* Persistent cloud document and vector storage
* Streaming responses and conversation history
* Advanced retrieval evaluation and confidence scoring
* Support for additional LLM providers

## 👩‍💻 Author

**Samjhana Yadav**
B.Tech — Computer Science & Engineering

**Interests:** Generative AI · RAG Systems · Machine Learning · Data Analytics

---

⭐ If you find this project useful, consider starring the repository.
