# NexusCRM

> **Enterprise-Grade, AI-Native Customer Relationship Management Platform** powered by **Agentic Harness**, **Model Context Protocol (MCP)**, **Google Agent-to-Agent (A2A) Protocol**, **LlamaIndex PageIndex Hybrid RAG**, **Predictive ML (XGBoost/LightGBM/Prophet)**, and **LangSmith/Langfuse Observability**.

---

## Technical Highlights

- **Package & Environment Management**: Managed via **`uv`** (Python 3.12).
- **Core Backend**: FastAPI async REST framework + SQLAlchemy 2.0 + AsyncPG/SQLite + Alembic migrations.
- **Multi-Agent System**: **LangGraph v1.2** Orchestrator DAG with state checkpointing, HITL interrupt nodes, delegating to **CrewAI** Sales & Support Crews via **Google A2A Protocol (JSON-RPC 2.0)**.
- **Tool Standard**: 4 dedicated **Model Context Protocol (MCP)** Servers (CRM, Email, Search, Analytics) exposing dynamic tools over streamable HTTP endpoints.
- **RAG Engine**: **LlamaIndex PageIndex** page-aware chunking + Qdrant Dense Vector + BM25 Sparse hybrid search fused via **Reciprocal Rank Fusion (RRF)** with **RAGAS Evaluation**.
- **Predictive Machine Learning**:
  - **XGBoost Churn Risk Model** (AUC-ROC: `0.9647`) with **SHAP TreeExplainer** feature attribution.
  - **LightGBM Lead Scoring Model** (AUC-ROC: `0.9887`) with probability calibration.
  - **Prophet Time-Series Revenue Forecast Model**.
  - **MLflow Tracking Registry** for experiment metrics and model artifacts.
- **Agentic Harness**: 4-Tier Memory System (Short-term, Episodic, Long-term facts, Semantic RAG), PII & Prompt Injection Safety Guardrails, Time-Aware Stale Deal Velocity Scheduler, and Feedback Loop Collectors.
- **Interactive UI**: Glassmorphic dark mode single-page dashboard with real-time SSE streaming agent workspace, HITL manager approval modals, and Chart.js forecast charts.

---

## Full Tech Stack

| Domain | Technology | Key Usage |
|--------|------------|-----------|
| **Environment** | `uv` | Dependency resolution, virtualenv management |
| **Backend** | FastAPI, Pydantic v2 | Async REST APIs & OpenAPI documentation |
| **Database** | SQLAlchemy 2.0, PostgreSQL / SQLite | Async ORM with soft deletes & UUIDs |
| **Security** | PyJWT, `bcrypt` | OAuth2 Bearer token authentication & password hashing |
| **Orchestration** | LangGraph v1.2 | Multi-agent DAG planner & HITL interrupt gate |
| **Agent Crews** | CrewAI, Google A2A | Role-based agent crews & JSON-RPC 2.0 protocol |
| **Tool Protocol** | Model Context Protocol (MCP) | Dynamic tool discovery & execution servers |
| **RAG Engine** | LlamaIndex, PageIndex, Qdrant, BM25 | Page-level hybrid retrieval & RAGAS evals |
| **Predictive ML** | XGBoost, LightGBM, Prophet, SHAP | Churn risk, lead scoring, and revenue forecast |
| **Experiment Tracking** | MLflow | Metric logging & model artifact registry |
| **Frontend** | Vanilla JS, CSS Glassmorphic Dark Mode | Real-time SSE streaming UI & Chart.js |

---

## Directory Structure

```
d:\NexusCRM\
├── pyproject.toml                # Managed via uv
├── SHOWCASE_RECRUITER_GUIDE.md   # Presentation script & resume bullet points
├── docker-compose.yml            # Postgres, Redis, Qdrant, MLflow
├── .gitignore                    # Python, uv, DB & secret ignores
├── .dockerignore                 # Docker build ignore rules
├── docs/                         # Phase-by-Phase Documentation (Phase 00 to Phase 07)
├── scripts/
│   ├── seed_db.py                # Database seeder using Faker
│   └── generate_ml_dataset.py    # 1,500 enterprise dataset generator
├── src/nexuscrm/
│   ├── core/                     # Config, DB, Security, Logging
│   ├── models/                   # SQLAlchemy 2.0 Async ORM Models
│   ├── schemas/                  # Pydantic v2 Schemas
│   ├── api/                      # FastAPI Routers (Auth, Contacts, Deals, RAG, Agents, Analytics)
│   ├── mcp_servers/              # 4 MCP Servers (CRM: 8010, Email: 8011, Search: 8012, Analytics: 8013)
│   ├── rag/                      # PageIndex LlamaIndex RAG Engine & RAGAS Evaluator
│   ├── agents/                   # LangGraph Orchestrator, CrewAI Sales/Support Crews, A2A Client, Harness
│   ├── ml/                       # XGBoost, LightGBM, Prophet Models & MLflow Trainer
│   └── web/                      # HTML, CSS Glassmorphism, JS UI
└── tests/                        # 16 Pytest Unit & Integration Test Suites
```

---

## Quick Start Guide

### 1. Clone & Sync Dependencies via `uv`

```bash
uv sync
```

### 2. Generate Dataset & Seed Database

```bash
uv run python scripts/generate_ml_dataset.py
uv run python scripts/seed_db.py
```

### 3. Train ML Models & Log to MLflow

```bash
uv run python src/nexuscrm/ml/trainer.py
```

### 4. Run Pytest Suite

```bash
uv run pytest
```

### 5. Launch Interactive Dashboard & APIs

```bash
uv run uvicorn nexuscrm.main:app --reload --port 8000
```

- **Interactive UI**: `http://localhost:8000/`
- **OpenAPI Docs**: `http://localhost:8000/docs`
