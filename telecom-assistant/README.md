# 📡 AI-Powered Telecom Training Assistant

An intelligent, interactive learning platform for telecommunications education,
powered by **IBM Granite** language models and **Retrieval-Augmented Generation (RAG)**.

---

## Project Overview

The Telecom Training Assistant helps students learn complex telecom concepts through:

- **RAG-based Q&A** — answers grounded in uploaded documents
- **Concept explainer** — beginner-friendly breakdowns of any telecom topic
- **AI quiz generator** — MCQ quizzes with scoring and explanations
- **Interactive chatbot** — multi-turn conversation with telecom AI
- **Knowledge base management** — upload, process, and manage learning materials

---

## Features

| Feature | Description |
|---|---|
| 📄 PDF Upload & Processing | Upload telecom PDFs; text is extracted, chunked, and embedded |
| 🔍 RAG Question Answering | Questions answered using retrieved document chunks + IBM Granite |
| 💬 Multi-turn Chatbot | Conversational interface with chat history |
| 📖 Concept Explainer | Simple explanations: definition, mechanism, example, key points |
| 📝 Quiz Generator | AI-generated MCQs by topic, difficulty, and count |
| 📊 Quiz Scoring | Instant results with per-question explanations |
| 📚 Knowledge Base View | Document stats, chunk counts, retrieval testing |
| 🔗 Source Citation | Every answer shows its source document and page number |
| 🔒 Hallucination Control | Explicit warning when context is insufficient |

---

## Architecture

```
User
 │
 ▼
Streamlit Web Interface
 │
 ├──► Document Upload Pipeline
 │        PDF → Text Extraction → Chunking → Embeddings → ChromaDB
 │
 └──► Question / Chat / Quiz Request
          │
          ▼
       Retriever (semantic search)
          │
          ▼
       ChromaDB (vector store)
          │
          ▼
       Relevant Telecom Document Chunks
          │
          ▼
       RAG Prompt (context + question)
          │
          ▼
       IBM Granite (LLM)
          │
          ▼
       Generated Answer + Sources
```

### Key Components

| Component | Technology |
|---|---|
| LLM | IBM Granite via `ibm-watsonx-ai` |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local) |
| Vector Database | ChromaDB (persistent, on-disk) |
| PDF Processing | PyMuPDF (`fitz`) |
| Web Interface | Streamlit |
| Configuration | `python-dotenv` |

---

## Installation

### Prerequisites

- Python 3.9 or higher
- IBM Watsonx account with API key and project ID

### Step 1 — Clone or Download

```bash
cd telecom-assistant
```

### Step 2 — Create a Virtual Environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** The first run downloads the `all-MiniLM-L6-v2` embedding model (~90 MB).

---

## Environment Setup

Copy the example file and fill in your credentials:

```bash
copy .env.example .env        # Windows
cp .env.example .env          # macOS/Linux
```

Edit `.env`:

```env
IBM_API_KEY=your_ibm_api_key_here
IBM_PROJECT_ID=your_ibm_project_id_here
IBM_URL=https://us-south.ml.cloud.ibm.com
IBM_MODEL_ID=ibm/granite-13b-instruct-v2
```

> Obtain credentials from [IBM Cloud](https://cloud.ibm.com) → Watsonx → Projects.

---

## Running the Application

```bash
streamlit run app.py
```

The application opens at `http://localhost:8501`.

---

## How to Use

### 1. Upload a PDF

1. Navigate to **Upload Materials** in the sidebar.
2. Click **Browse files** and select one or more telecom PDF files.
3. Adjust chunk size / overlap if desired.
4. Click **Process and Add to Knowledge Base**.
5. Wait for the success message confirming chunks were added.

**Example documents to upload:**
- 5G network architecture documentation
- LTE/4G fundamentals
- Wireless communication textbook chapters
- Signal processing notes
- Network protocol specifications

### 2. Ask a Question

1. Navigate to **Ask Telecom Assistant**.
2. Type your question in the text area.
3. Click **Get Answer**.
4. View the AI-generated answer and the source documents used.

**Example questions:**
- "What is the difference between 4G and 5G?"
- "Explain OFDM in simple words."
- "What is beamforming?"
- "How does handover work in LTE?"

### 3. Use the Chatbot

1. Navigate to **Chatbot**.
2. Type in the chat input at the bottom.
3. The assistant maintains conversation history for the session.
4. Click **Clear Chat History** to start fresh.

### 4. Explain a Concept

1. Navigate to **Explain Concept**.
2. Select a concept from the dropdown or type a custom one.
3. Click **Explain Simply**.
4. Receive a structured explanation with definition, mechanism, example, and key points.

### 5. Generate a Quiz

1. Navigate to **Generate Quiz**.
2. Select topic, difficulty (Easy / Medium / Hard), and number of questions.
3. Click **Generate Quiz**.
4. Answer the multiple-choice questions using the radio buttons.
5. Click **Submit Quiz** to see your score and explanations.

### 6. View Knowledge Base

1. Navigate to **Knowledge Base**.
2. See the number of documents and chunks.
3. Use the **Test Retrieval** section to verify retrieval works correctly.

---

## Project Structure

```
telecom-assistant/
│
├── app.py                    # Main Streamlit entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── gitignore.txt             # Rename to .gitignore
├── README.md
│
├── config/
│   └── settings.py           # Load and validate environment variables
│
├── rag/
│   ├── document_loader.py    # PDF text extraction (PyMuPDF)
│   ├── text_splitter.py      # Character-based chunking with overlap
│   ├── embeddings.py         # SentenceTransformer embeddings
│   ├── vector_store.py       # ChromaDB CRUD operations
│   └── retriever.py          # Semantic search + context formatting
│
├── models/
│   └── granite_model.py      # IBM Granite LLM wrapper
│
├── services/
│   ├── qa_service.py         # RAG question answering
│   ├── quiz_service.py       # Quiz generation and scoring
│   └── explanation_service.py# Concept explanation
│
├── ui/
│   ├── home.py               # Home page
│   ├── ask.py                # Ask Telecom Assistant page
│   ├── chatbot.py            # Chatbot page
│   ├── explain.py            # Explain Concept page
│   ├── quiz.py               # Quiz generation and results
│   ├── upload.py             # Upload Materials page
│   └── knowledge_base.py     # Knowledge Base page
│
├── data/
│   ├── documents/            # Uploaded PDF files
│   └── vectorstore/          # ChromaDB persistent storage
│
└── utils/
    └── helpers.py            # Utility functions
```

---

## How RAG Works in This Project

1. **Document Ingestion:**
   - PDF is loaded with PyMuPDF page by page.
   - Pages are split into overlapping chunks (default 1000 chars, 200 overlap).
   - Each chunk is embedded with `sentence-transformers/all-MiniLM-L6-v2`.
   - Embeddings + text are stored in ChromaDB on disk.

2. **Query Time:**
   - The student's question is embedded with the same model.
   - ChromaDB finds the top-K most similar chunks (cosine similarity).
   - Retrieved chunks are formatted into a context string.
   - A structured RAG prompt is built: `system + context + question`.
   - IBM Granite generates a response conditioned on that context.
   - Sources (filename + page) are extracted and displayed.

---

## How IBM Granite Is Used

IBM Granite is accessed via the `ibm-watsonx-ai` Python SDK:

```python
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

model = ModelInference(
    model_id="ibm/granite-13b-instruct-v2",
    credentials=Credentials(url=..., api_key=...),
    project_id=...,
    params={...}
)
response = model.generate_text(prompt=prompt)
```

The model is used for:
- RAG-based Q&A (grounded in retrieved document context)
- Concept explanations (structured pedagogical format)
- Quiz generation (JSON-formatted MCQs)
- Chatbot responses (multi-turn with history)

---

## Remaining Configuration Requirements

1. **IBM API Key** — required for Granite model access.
2. **IBM Project ID** — required; create a project in IBM Watsonx.
3. **IBM URL** — regional endpoint (default: `https://us-south.ml.cloud.ibm.com`).
4. **Model ID** — default `ibm/granite-13b-instruct-v2`; can be changed in `.env`.
5. **Rename `gitignore.txt` to `.gitignore`** before committing to a repository.

---

## Example Questions for Demo

**Question Answering:**
- "Explain the 5G core network."
- "What is the difference between TDD and FDD?"
- "What are the frequency bands used in 5G?"

**Concept Explanations:**
- "OFDM", "MIMO", "Network Slicing", "Beamforming", "mmWave"

**Quiz Topics:**
- 5G (Medium, 5 questions)
- LTE (Easy, 3 questions)
- Signal Processing (Hard, 10 questions)

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `IBM credentials are not configured` | Check `.env` file values |
| `Failed to open PDF` | Ensure the file is a valid, non-scanned PDF |
| `No text could be extracted` | PDF may be image-based; use a text-based PDF |
| `Model generation failed` | Verify IBM API key and project ID are correct |
| Embedding model slow on first run | Normal — model downloads once (~90 MB) |
| `chromadb` version conflict | Run `pip install chromadb>=0.4.24` |
