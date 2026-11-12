# 🔬 ResearchAI — Autonomous Multi-Agent Research Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-FF4F00?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)

> **An end-to-end autonomous research engine that coordinates specialized AI agents to discover, scrape, synthesize, and peer-review deep technical reports with zero manual overhead.**

---

### 📊 Performance & Key Metrics

| Average Latency | Average Quality Score | Manual Effort Saved |
| :---: | :---: | :---: |
| **~92 seconds** | **7.8 / 10** | **~35 mins / query** |
| Complete 4-stage pipeline run | Strict automated critic review | Replaces 15+ browser tabs |

---

## 🎯 Problem Statement

Conducting thorough web research manually is fragmented and slow:
1. **Tab Exhaustion**: Searching, opening 15+ tabs, filtering noise, and taking notes typically takes **30–45 minutes** per topic.
2. **LLM Hallucinations**: Standard LLM chats lack real-time web retrieval, operate with fixed knowledge cutoffs, and produce unsourced claims with no provenance.
3. **Inconsistent Quality**: Hand-crafted summaries often lack standardized structure and objective fact-checking.

**Solution:** An autonomous multi-agent pipeline where specialized agents discover sources and scrape live body text, while deterministic chains synthesize structured Markdown reports and evaluate them with an automated critic.

---

## 🏛️ System Architecture

```
                                  [ User Research Query ]
                                             │
                                             ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               4-STAGE RESEARCH PIPELINE                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [ Stage 1: Search Agent ] (LangGraph ReAct)                                           │
│  └─► Queries live web via Tavily Search API                                            │
│  └─► Filters and returns top authoritative URLs + search snippets                     │
│                                            │                                           │
│                                            ▼                                           │
│  [ Stage 2: Reader Agent ] (LangGraph ReAct)                                           │
│  └─► Selects candidate URL and performs deep page retrieval                            │
│  └─► Strips ads, scripts, and navigation using BeautifulSoup4                          │
│                                            │                                           │
│                                            ▼                                           │
│  [ Stage 3: Writer Chain ] (LangChain LCEL)                                            │
│  └─► Combines snippets + raw scraped text                                              │
│  └─► Deterministically drafts executive summary, key findings, and cited sources       │
│                                            │                                           │
│                                            ▼                                           │
│  [ Stage 4: Critic Chain ] (LangChain LCEL)                                            │
│  └─► Objectively grades the draft (Score: X/10)                                        │
│  └─► Compiles actionable strengths, gaps, and a final verdict                          │
│                                                                                        │
└────────────────────────────────────────────┬───────────────────────────────────────────┘
                                             │
                                             ▼
                        [ SQLite / PostgreSQL Persistence (SQLAlchemy) ]
                                             │
                                             ▼
                      [ Modern Glassmorphic Web Dashboard (FastAPI) ]
```

---

## 💡 Key Architectural Decisions

### 1. Separation of Agents (Exploration) vs. Chains (Deterministic Synthesis)
* **Agents (LangGraph ReAct)**: Used strictly for **Search** and **Reader** stages. Agentic loops are ideal here because the model must dynamically decide which queries to run and which URLs to extract.
* **Chains (LangChain LCEL)**: Used for **Writer** and **Critic** stages. Once source context is collected, synthesizing a report and reviewing it requires predictable, fast, single-pass generation—not unpredictable tool-calling loops.

### 2. Deep Web Scraping Beyond Surface Snippets
Many AI search tools only rely on 200-character search snippets. This system passes the highest-relevance URL to an automated **Reader Agent** that scrapes full document text, enabling technical depth that snippet-only summaries cannot achieve.

### 3. Automated Peer Review (The Critic)
Every report is automatically graded by an independent Critic prompt that scores the text out of 10 and identifies missing data or weak points before the user reviews it.

### 4. Decoupled Production-Ready Backend
* **FastAPI**: Asynchronous REST API with auto-generated OpenAPI documentation (`/docs`).
* **JWT Authentication**: Password hashing with `bcrypt` and signed Bearer token route authorization.
* **Unified Serving**: FastAPI mounts and serves the responsive Tailwind/Stitch frontend directly on port 8000, eliminating CORS issues.

---

## 🔬 Empirical Benchmarks

The pipeline was evaluated across 5 diverse research domains:

| # | Topic Domain | Latency | Report Length | Critic Score |
|---|--------------|:-------:|:-------------:|:------------:|
| 1 | **Chemistry**: *Redox Reactions & Half-Cell Potential* | **78s** | 1,550 words | **8.5 / 10** |
| 2 | **Entertainment**: *Beast Games & High-Stakes Reality* | **85s** | 1,600 words | **7.5 / 10** |
| 3 | **Career & Tech**: *Data Analyst Job Market & Skills* | **137s** | 2,500 words | **7.5 / 10** |
| 4 | **AI Architecture**: *KV Cache Compression in LLMs* | **82s** | 1,700 words | **8.0 / 10** |
| 5 | **Materials Science**: *Solid-State Battery Breakthroughs* | **79s** | 1,620 words | **7.5 / 10** |
| **Avg** | **Overall System Average** | **~92s** | **~1,794 words** | **7.8 / 10** |

---

## 🛠️ Tech Stack

* **AI & Orchestration**:
  * [LangGraph](https://langchain-ai.github.io/langgraph/) — Prebuilt ReAct agent orchestration and cyclic tool-calling loops.
  * [LangChain (LCEL)](https://python.langchain.com/) — Deterministic pipeline synthesis, prompt chaining, and output parsing.
  * [Mistral AI](https://mistral.ai/) / [OpenAI](https://openai.com/) — High-throughput inference for synthesis and critique.
* **Information Retrieval**:
  * [Tavily Search API](https://tavily.com/) — Search engine optimized specifically for autonomous LLM agents.
  * [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) + [Requests](https://requests.readthedocs.io/) — DOM cleaning, navigation removal, and raw body text extraction.
* **Backend & Security**:
  * [FastAPI](https://fastapi.tiangolo.com/) — High-performance Python ASGI backend.
  * [SQLAlchemy](https://www.sqlalchemy.org/) — Relational ORM (default: SQLite; production-ready: PostgreSQL).
  * [Passlib (Bcrypt)](https://passlib.readthedocs.io/) & [Python-Jose (JWT)](https://python-jose.readthedocs.io/) — Secure authentication and session management.
* **Frontend**:
  * [TailwindCSS](https://tailwindcss.com/) & [Google Stitch](https://stitch.withgoogle.com/) — Responsive dark-mode command center with glassmorphic cards and live agent progress animation.
  * [Marked.js](https://marked.js.org/) — Client-side Markdown rendering with clipboard export.

---

## 📁 Repository Structure

```
Multi-agent-research-system-main/
├── backend/
│   ├── main.py              # FastAPI app instance, CORS, static mounting & REST routes
│   ├── pipeline.py          # 4-stage sequential agent orchestration
│   ├── agents.py            # LangGraph ReAct agents & LangChain LCEL chains
│   ├── tools.py             # Tavily search & BeautifulSoup extraction tools
│   ├── models.py            # SQLAlchemy database models (User, Request, Report)
│   ├── schemas.py           # Pydantic validation schemas (V2 ConfigDict)
│   ├── database.py          # Database session handling (SQLite / PostgreSQL)
│   ├── auth.py              # Password hashing & JWT token issuance
│   ├── test_api.py          # Automated Pytest suite
│   └── requirements.txt     # Python backend dependencies
├── frontend/
│   ├── index.html           # Research command center & live agent progress tracker
│   ├── results.html         # Markdown report reader & critic score card
│   ├── login.html           # Glassmorphic user login interface
│   ├── signup.html          # Researcher account registration
│   ├── style.css            # Custom animations, agent stage pulses & scrollbars
│   └── script.js            # Frontend state, JWT handling & API fetch client
├── .env.example             # Configuration template for API keys & database URLs
├── .gitignore               # Ignored environments, databases, and secrets
└── README.md                # Technical overview & system documentation
```

---

## 🔌 API Reference

| Method | Endpoint | Access | Description |
|---|---|:---:|---|
| `GET` | `/` | Public | System health check and API status |
| `POST` | `/signup` | Public | Register new user account with hashed password |
| `POST` | `/login` | Public | Authenticate credentials and return signed JWT Bearer token |
| `POST` | `/research` | Protected | Submit research topic, execute 4-stage pipeline, save report |
| `GET` | `/reports/{id}` | Protected | Retrieve synthesized report and critic scores by ID |
| `GET` | `/my-reports` | Protected | List historical research runs for logged-in user |
| `GET` | `/docs` | Public | Interactive Swagger / OpenAPI documentation |

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
* Python 3.10+
* Tavily API Key ([Get free API key](https://tavily.com))
* Mistral API Key ([Get free API key](https://console.mistral.ai)) or OpenAI Key

### 2. Clone the Repository
```bash
git clone https://github.com/smithaherkar/Collaborative-AI-Research-Platform.git
cd Collaborative-AI-Research-Platform
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```env
MISTRAL_API_KEY="your_mistral_api_key_here"
TAVILY_API_KEY="your_tavily_api_key_here"

# Optional: Default is local SQLite (research.db). Add PostgreSQL URL for production:
# DATABASE_URL="postgresql://user:password@localhost:5432/research_db"

# JWT Secret Key (generate any random 32+ character string)
SECRET_KEY="super_secret_jwt_key_for_signing_tokens_change_in_production"
```

### 4. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. Run the Application
Start the unified server with a single command:
```bash
python -m uvicorn main:app --reload --port 8000
```

* **Frontend Dashboard**: Open [http://localhost:8000/login.html](http://localhost:8000/login.html) in your browser.
* **Interactive API Docs**: Explore endpoints at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🧪 Testing

Execute the automated test suite covering authentication, database persistence, and API routing:
```bash
cd backend
pytest test_api.py -v
```
