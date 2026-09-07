# Collaborative AI Research Platform
### Multi-Agent Autonomous Research & Fact-Checking Engine
**Backend:** FastAPI &bull; **Database:** PostgreSQL / SQLAlchemy &bull; **Frontend:** Modern Vanilla HTML5 / CSS3 / JavaScript &bull; **Agents:** LangGraph / LangChain

---

## 📌 Overview

The **Collaborative AI Research Platform** is an end-to-end full-stack application that coordinates specialized AI agents to automate deep-dive research, information extraction, report synthesis, and automated peer review.

Originally prototyped as a single-file Streamlit script, this codebase has been transformed into a decoupled, production-style architecture featuring:
- **FastAPI REST API**: High-performance backend endpoints for user registration, authentication, and research execution.
- **Relational Persistence**: PostgreSQL/SQLite with SQLAlchemy ORM to track user requests, job states, and historical research reports.
- **JWT Authentication**: Secure user accounts with password hashing via `bcrypt` and signed JSON Web Tokens.
- **Decoupled Frontend**: Responsive, modern dark-glassmorphism user interface with dynamic agent stage visualization and client-side Markdown rendering.

---

## 🏛️ Architecture & System Design

```
┌───────────────────────────┐           HTTPS / JSON REST API           ┌───────────────────────────────┐
│     Modern Web Client     │ ────────────────────────────────────────► │        FastAPI Backend        │
│    (HTML5 / CSS3 / JS)    │ ◄──────────────────────────────────────── │         (Uvicorn ASGI)        │
└───────────────────────────┘                                           └───────────────┬───────────────┘
                                                                                        │
                                                     ┌──────────────────────────────────┴─────────────────────────────────┐
                                                     │                                                                    │
                                            ┌────────▼─────────┐                                                ┌─────────▼─────────┐
                                            │    PostgreSQL    │                                                │ Multi-Agent System│
                                            │  SQLAlchemy ORM  │                                                │ (LangGraph/Chains)│
                                            └──────────────────┘                                                └─────────┬─────────┘
                                                                                                                          │
                                                                                       ┌──────────────────────────────────┴──────────────────────────────────┐
                                                                                       │                                                                     │
                                                                              ┌────────▼────────┐                                                   ┌────────▼────────┐
                                                                              │  Tavily Search  │                                                   │ OpenAI (GPT-4o) │
                                                                              │    Web Search   │                                                   │ Reasoning & LLM │
                                                                              └─────────────────┘                                                   └─────────────────┘
```

---

## 🤖 Multi-Agent Workflow

The core research intelligence operates sequentially through four specialized stages:

```
[User Topic] ──► 1. Search Agent ──► 2. Reader Agent ──► 3. Writer Chain ──► 4. Critic Chain ──► [Persisted Report & Score]
                  (Tavily Tool)       (Web Scraper)       (Synthesis)        (Peer Review)
```

1. **Search Agent (`agents.py`)**: A ReAct agent equipped with the Tavily Search API that queries the web for the latest, high-relevance articles and sources.
2. **Reader Agent (`agents.py`)**: A scraping agent that extracts raw HTML from the top URL, cleans navigation/ads/scripts via BeautifulSoup, and parses deep text context.
3. **Writer Chain (`agents.py`)**: Synthesizes surface search snippets and deep scraped text into a structured Markdown document (Introduction, Key Findings, Conclusion, Sources).
4. **Critic Chain (`agents.py`)**: Evaluates the drafted report strictly for clarity, factual depth, and actionable insights, assigning a numerical score out of 10 (`Score: X/10`) alongside strengths, areas to improve, and a final verdict.

---

## 🗄️ Database Schema

Three relational tables managed via SQLAlchemy ORM:

```sql
-- 1. Users table (Authentication & identity)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Research Requests (Job lifecycle tracking)
CREATE TABLE research_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    topic VARCHAR(500) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending | done | failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Reports (Synthesized content & critic metrics)
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    request_id INTEGER REFERENCES research_requests(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    critique_feedback TEXT,
    critique_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|:---:|---|
| `GET` | `/` | ❌ | Health check and API readiness status |
| `POST` | `/signup` | ❌ | Register new account with email & password |
| `POST` | `/login` | ❌ | Authenticate credentials & receive JWT Bearer token |
| `POST` | `/research` | 🔒 | Submit topic, run 4-agent pipeline, persist and return report |
| `GET` | `/reports/{id}` | 🔒 | Fetch report content and critic review for a given report ID |
| `GET` | `/my-reports` | 🔒 | List past research requests and reports for the logged-in user |

---

## 📁 Repository Structure

```
Collaborative-AI-Research-Platform/
├── backend/
│   ├── main.py              # FastAPI app instance, CORS middleware, and REST routes
│   ├── database.py          # SQLAlchemy connection engine, SessionLocal, and get_db dependency
│   ├── models.py            # ORM models (User, ResearchRequest, Report)
│   ├── schemas.py           # Pydantic validation schemas (V2 ConfigDict)
│   ├── auth.py              # Bcrypt hashing, JWT issuance, and get_current_user dependency
│   ├── agents.py            # LangGraph ReAct agents and prompt chains
│   ├── pipeline.py          # 4-stage sequential research workflow
│   ├── tools.py             # Tavily search & BeautifulSoup web scraping tools
│   ├── test_api.py          # Automated pytest test suite
│   └── requirements.txt     # Backend Python dependencies
├── frontend/
│   ├── index.html           # Research topic dashboard with live agent progress animation
│   ├── login.html           # Authentication login page
│   ├── signup.html          # User registration page
│   ├── results.html         # Markdown report viewer & score breakdown
│   ├── style.css            # Dark-mode glassmorphism design system
│   └── script.js            # Auth state, API client fetch wrappers, and DOM handling
├── .env.example             # Template for API keys and database configuration
├── .gitignore               # Ignored secrets, virtualenvs, and database binaries
└── README.md                # Documentation and architectural guide
```

---

## 🚀 Quickstart & Local Setup

### 1. Clone & Configure Environment
```bash
git clone https://github.com/smithaherkar/Collaborative-AI-Research-Platform.git
cd Collaborative-AI-Research-Platform
```

Create your `.env` file in the root directory (or copy `.env.example`):
```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional: Configure PostgreSQL (falls back to local SQLite if left empty)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/research_db

# JWT Secret Key
SECRET_KEY=your_jwt_secret_key_here_at_least_32_characters_long
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
pytest test_api.py -v
```

### 4. Start the FastAPI Server
```bash
python -m uvicorn main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/`

### 5. Launch the Frontend
Open `frontend/index.html` (or `frontend/login.html`) directly in your browser or serve with Live Server / static file server:
```bash
# Example with Python's built-in HTTP server:
cd ../frontend
python -m http.server 5500
```
Visit `http://localhost:5500` to create an account, log in, and launch autonomous research investigations!

