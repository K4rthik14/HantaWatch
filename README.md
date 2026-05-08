# HantaWatch — Multi-Agent Threat Monitor (MATM)

> AI-assisted infectious disease surveillance platform — Phase 0 Foundation

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ed?logo=docker)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

MATM is a lean, production-grade infectious disease surveillance system that ingests
signals from WHO RSS feeds, ProMED reports, and other public health sources, then
uses a multi-agent AI pipeline backed by a local LLM (Ollama) and a vector store
(ChromaDB) to detect, score, and alert on emerging threats.

### Architecture (Phase 0)

```
┌─────────────────────────────────────────────┐
│                  MATM Stack                  │
├───────────┬──────────────┬───────────────────┤
│  Backend  │  PostgreSQL  │     ChromaDB      │
│  FastAPI  │  (asyncpg)   │  (vector store)   │
├───────────┴──────────────┴───────────────────┤
│          Redis (task queue / cache)           │
└─────────────────────────────────────────────┘
```

---

## Quickstart

### Prerequisites

- Docker + Docker Compose v2
- Python 3.12+ (for local dev)
- [uv](https://github.com/astral-sh/uv) (for fast dependency management)

### 1. Clone & configure environment

```bash
git clone git@github.com:K4rthik14/HantaWatch.git
cd HantaWatch
cp .env.example .env
# Edit .env with your values (SECRET_KEY is required in production)
```

### 2. Run with Docker Compose

```bash
# Production-like stack
docker compose up -d

# Development (with hot-reload)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### 3. Local development (without Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install uv
uv pip install -e ".[dev]"
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

### Health Check

```bash
curl http://localhost:8000/health
# {"status":"ok","env":"dev","version":"0.1.0"}
```

---

## Project Structure

```
HantaWatch/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application entry point
│   │   └── core/
│   │       ├── config.py    # Pydantic-settings configuration
│   │       ├── logging.py   # Structlog setup
│   │       ├── exceptions.py# Domain exception hierarchy
│   │       └── dependencies.py # FastAPI dependency injection
│   ├── tests/
│   │   └── conftest.py      # Pytest fixtures
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                # (Phase 1+)
├── docker-compose.yml       # Production stack
├── docker-compose.dev.yml   # Dev overrides
└── .env.example
```

---

## Services

| Service   | Port  | Description                        |
|-----------|-------|------------------------------------|
| Backend   | 8000  | FastAPI REST API                   |
| Postgres  | 5432  | Primary relational database        |
| ChromaDB  | 8001  | Vector store for RAG pipeline      |
| Redis     | 6379  | Task queue and caching             |

---

## Development

### Run tests

```bash
cd backend
pytest --cov=app tests/
```

### Lint & format

```bash
ruff check app/
ruff format app/
mypy app/
```

---

## Roadmap

- **Phase 0** ✅ — Project scaffold, core config, health endpoint
- **Phase 1** — Data ingestion agents (WHO RSS, ProMED)
- **Phase 2** — RAG pipeline + ChromaDB integration
- **Phase 3** — Threat scoring + alerting
- **Phase 4** — Frontend dashboard

---

## License

MIT © 2025 K4rthik14
