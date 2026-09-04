# Fetal Ultrasound Biometry Agent

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** ISUOG Fetal Biometry Practice Guidelines, CAP / CLSI / ISO Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Fetal Ultrasound Biometry Agent is a clinical decision support system that evaluates fetal ultrasound measurements against established reference standards. It provides:

- **Automated biometry evaluation** with multi-worker consensus
- **Risk stratification** (Routine / Elevated / Critical-STAT) based on measurement thresholds
- **Zero-PHI outbound guard** that blocks protected health information from leaving the system
- **Tamper-evident HMAC-SHA256 audit trail** for every evaluation
- **FastAPI REST API** with Prometheus-compatible metrics
- **CLI** for interactive use, batch CSV processing, and server deployment

---

## ⚙️ Key Capabilities & Algorithmic Modules

| Module | Description |
|:-------|:------------|
| `agents/supervisor.py` | Master orchestrator coordinating multi-worker evaluations |
| `agents/workers.py` | Specialized workers: QC Invariant, Safety Escalation, Protocol Conformance |
| `agents/base.py` | PHI guard, HMAC-SHA256 audit trail, security exceptions |
| `agents/api.py` | FastAPI REST endpoints with admin token protection |
| `agents/models.py` | Pydantic v2 schemas for payloads, alerts, and dossiers |
| `agents/llm_factory.py` | Pluggable LLM adapter (mock, Ollama, Claude, OpenAI) |
| `agents/metrics.py` | Prometheus operational metrics exporter |
| `agents/learning.py` | Bayesian calibration and active learning feedback engine |
| `agents/streamer.py` | WebSocket telemetry broadcaster |
| `enrichment.py` | Domain-specific enrichment feature suite (8 engines) |

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/fetal-ultrasound-biometry-agent.git
cd fetal-ultrasound-biometry-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Environment Variables

| Variable | Required | Description |
|:---------|:---------|:------------|
| `AUDIT_SECRET_KEY` | Yes (production) | HMAC-SHA256 signing key (min 32 chars). Must be set in production. |
| `API_ADMIN_TOKEN` | No | Bearer token for `/api/audit/logs` endpoint. If unset, endpoint returns 503. |
| `MODEL_PROVIDER` | No | LLM provider: `mock` (default), `ollama`, `claude`, `openai` |

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Supervisory Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Flag | Type | Default | Description |
|:-----|:-----|:--------|:------------|
| `--task-id` | str | `TASK-2026-001` | Unique task / case identifier |
| `--target` | str | `KEY-TARGET-01` | Entity or specimen target identifier |
| `--primary` | float | `28.5` | Primary measurement value (e.g., BPD, HC, AC, FL) |
| `--secondary` | float | `14.2` | Secondary measurement or kinetic index |
| `--critical` | flag | `False` | Trigger emergency escalation |
| `--status` | str | `DISCORDANT` | Status descriptor (NOMINAL, DISCORDANT, ANOMALY, etc.) |

### Input Data Schema (Batch CSV)

| Field | Type | Description | Requirement |
|:------|:-----|:------------|:------------|
| `task_id` | str | Unique task / case identifier | Required |
| `target_identifier` | str | Entity or specimen target | Required |
| `primary_metric` | float | Primary measurement value | Required |
| `secondary_metric` | float | Secondary measurement | Optional (default: 0.0) |
| `is_critical_flag` | bool | Emergency escalation flag | Optional (default: false) |
| `status_descriptor` | str | Status code or phenotype | Optional (default: NOMINAL) |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOBs, and patient names.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation. Requires `AUDIT_SECRET_KEY` (min 32 chars).
* **Admin Token Protection:** `/api/audit/logs` endpoint requires `API_ADMIN_TOKEN` bearer authentication.
* **Path Traversal Prevention:** Batch CLI validates input paths remain within the working directory.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the full test suite:

```bash
pytest -v
```

Run with coverage:

```bash
pytest -v --cov=agents --cov-report=html
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

### Docker
```bash
# Create .env file
echo "AUDIT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" > .env

# Build and run
docker build -t fetal-ultrasound-biometry-agent .
docker run -p 8000:8000 --env-file .env fetal-ultrasound-biometry-agent
```

### Docker Compose
```bash
# Set your audit key
export AUDIT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Launch
docker compose up -d
```

---

## 📁 Project Structure

```
fetal-ultrasound-biometry-agent/
├── agents/                  # Core agent modules
│   ├── __init__.py
│   ├── api.py              # FastAPI REST server
│   ├── base.py             # PHI guard, HMAC audit trail
│   ├── learning.py         # Bayesian calibration engine
│   ├── llm_factory.py      # LLM provider factory
│   ├── metrics.py          # Prometheus metrics
│   ├── models.py           # Pydantic schemas
│   ├── streamer.py         # WebSocket telemetry
│   ├── supervisor.py       # Master orchestrator
│   └── workers.py          # Specialized evaluation workers
├── fetal_echo_ai/          # Frontier domain engine (v2)
│   ├── agents.py
│   ├── cli.py
│   ├── engine.py
│   ├── models.py
│   └── server.py
├── tests/                  # Pytest test suite
│   ├── conftest.py
│   ├── test_enrichment.py
│   ├── test_fetal_echo_ai.py
│   ├── test_fetal_ultrasound_biometry_agent.py
│   └── test_security_and_api.py
├── web/index.html          # Operations console UI
├── .github/workflows/ci.yml
├── cli.py                  # Main CLI entry point
├── enrichment.py           # Domain enrichment engines
├── simulator.py            # Load testing simulator
├── sample.csv              # Sample batch input
├── sample_payload.json     # Sample API payload
├── benchmark_dataset.json  # Golden benchmark test cases
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── LICENSE
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
