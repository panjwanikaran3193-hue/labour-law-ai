# Labour Law AI — Folder Structure

```
labour_law_ai/
│
├── .env.example          ← copy to .env and fill in your API keys
├── .env                  ← your secrets (git-ignored)
├── .gitignore
│
├── config.py             ← central config (all settings, paths, logging)
├── requirements.txt      ← all Python dependencies with comments
│
├── main.py               ← entry point (starts FastAPI + Streamlit)
│
├── api/                  ← FastAPI route handlers
│   ├── __init__.py
│   ├── routes_qa.py      ← Legal Q&A endpoints
│   ├── routes_quiz.py    ← Quiz / game endpoints
│   ├── routes_ingest.py  ← Document upload & processing
│   └── routes_gaps.py    ← Missing knowledge detection
│
├── core/                 ← AI modules (import these anywhere)
│   ├── __init__.py
│   ├── ingestor.py       ← PDF parsing, OCR, text chunking
│   ├── embedder.py       ← sentence-transformers + ChromaDB storage
│   ├── retriever.py      ← RAG pipeline (LangChain + ChromaDB query)
│   ├── quiz_engine.py    ← MCQ generation, scoring, rope-climb game logic
│   ├── gap_detector.py   ← Detects unanswered / low-confidence queries
│   ├── summariser.py     ← Auto-summary generation for acts/judgments
│   └── gboy_agent.py     ← GBoy AI chat agent (LangChain agent executor)
│
├── ui/                   ← Streamlit page modules
│   ├── __init__.py
│   ├── page_home.py
│   ├── page_digest.py    ← Knowledge Digest viewer
│   ├── page_qa.py        ← Legal Q&A chat
│   ├── page_quiz.py      ← Quiz system
│   ├── page_rope.py      ← Rope climbing quiz game
│   ├── page_gaps.py      ← Missing knowledge dashboard
│   └── components.py     ← Shared UI components
│
├── utils/                ← Shared helpers
│   ├── __init__.py
│   ├── file_utils.py     ← Safe path handling, Windows-compat file ops
│   ├── text_utils.py     ← Cleaning, normalisation, language detection
│   └── db_utils.py       ← SQLAlchemy session helpers
│
├── tests/                ← pytest test suite
│   ├── test_ingestor.py
│   ├── test_retriever.py
│   └── test_quiz.py
│
│   ── Document stores ──────────────────────────────────────────────────
├── acts/                 ← Labour Act PDFs (e.g. Industrial Disputes Act)
├── rules/                ← Subsidiary rules and regulations
├── judgments/            ← Court and tribunal judgments
├── circulars/            ← Government circulars and notifications
├── forms/                ← Statutory forms (Form A, Form B, etc.)
├── faq/                  ← Curated FAQ markdown files
├── summaries/            ← Auto-generated summaries (JSON/Markdown)
├── quiz/                 ← Quiz question bank (JSON files)
│
│   ── Generated data ────────────────────────────────────────────────────
├── embeddings/           ← ChromaDB persistent storage (auto-generated)
├── database/             ← SQLite file: labour_law.db (auto-generated)
└── logs/                 ← Rotating log files (auto-generated)
```

## Quick start (Windows)

```bat
REM 1. Clone / download the project
cd C:\Projects\labour_law_ai

REM 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

REM 3. Install dependencies
pip install -r requirements.txt

REM 4. Set up config
copy .env.example .env
REM  → open .env in Notepad and add your OPENAI_API_KEY

REM 5. Run Streamlit UI
streamlit run ui/page_home.py

REM 6. (Optional) Run FastAPI in a separate terminal
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```
