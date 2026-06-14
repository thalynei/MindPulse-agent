# MindPulse Agent

The AI core module of the MindPulse system, serving as an independent microservice providing natural language analysis capabilities for the Java backend.

## Features

- **Task Analysis** - Parse natural language task descriptions, extract title, due date, priority, category, and tags
- **Note Summary** - AI-generated note summaries and tag recommendations
- **Study Insights** - Generate insights and recommendations based on study session data

All features support **Ollama AI + Rule-based Fallback** dual paths, ensuring high availability.

## Tech Stack

| Component | Description |
|-----------|-------------|
| Python | 3.10+ |
| Web Framework | FastAPI + Uvicorn |
| AI Engine | Ollama (qwen2.5:1.5b) |
| HTTP Client | aiohttp (connection pool reuse) |
| Date Parsing | dateparser |

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Ollama (Optional)

```bash
ollama pull qwen2.5:1.5b
ollama serve
```

### 3. Start Service

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Task analysis
curl -X POST http://localhost:8000/api/v1/analyze/task \
  -H "Content-Type: application/json" \
  -d '{"task_description": "Submit math homework by 3pm tomorrow"}'

# Note summary
curl -X POST http://localhost:8000/api/v1/analyze/generate_summary \
  -H "Content-Type: application/json" \
  -d '{"note_content": "# Quantum Mechanics\nWave-particle duality is the foundation of quantum mechanics."}'

# Study insights
curl -X POST http://localhost:8000/api/v1/analyze/study-insight \
  -H "Content-Type: application/json" \
  -d '{"sessions": [{"actualMinutes": 60, "status": "completed"}], "tasks": []}'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/analyze/task` | POST | Single task analysis |
| `/api/v1/analyze/batch-analyze` | POST | Batch task analysis |
| `/api/v1/analyze/generate_summary` | POST | Note summary generation |
| `/api/v1/analyze/study-insight` | POST | Study insight generation |

Detailed API documentation: [agentapi.md](agentapi.md).

## Configuration

Configure via environment variables (or `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Service port |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama server URL |
| `OLLAMA_MODEL` | qwen2.5:1.5b | Model name |
| `OLLAMA_ENABLED` | true | Enable Ollama |
| `OLLAMA_TIMEOUT` | 30 | Ollama timeout (seconds) |

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Unit tests only
pytest tests/unit

# Integration tests
pytest tests/integration
```

## Docker Deployment

```bash
# Build image
docker build -t mindpulse-agent .

# Run container
docker run -p 8000:8000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  mindpulse-agent

# Or use docker-compose
docker-compose up -d
```

## Project Structure

```
MindPulse-agent/
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── core/
│   │   ├── config.py              # Configuration management
│   │   └── ollama_client.py       # Ollama HTTP client (connection pool)
│   ├── api/v1/endpoints/
│   │   ├── tasks.py               # Task analysis endpoints
│   │   ├── notes.py               # Note summary endpoints
│   │   └── study_insight.py       # Study insight endpoints
│   ├── agents/
│   │   ├── task_analyzer.py       # Task analysis agent
│   │   ├── note_summarizer.py     # Note summary agent
│   │   └── study_insight_agent.py # Study insight agent
│   └── utils/
│       ├── task_parser.py         # Task rule-based parser
│       ├── note_parser.py         # Note rule-based parser
│       └── study_insight_parser.py # Study insight rule-based parser
├── tests/                         # Unit + integration tests
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Dev dependencies
├── Dockerfile                     # Multi-stage build
├── docker-compose.yml             # Container orchestration
└── agentapi.md                    # API documentation
```

## Architecture

```
Request → FastAPI → Agent (Ollama AI)
                    ↓ (on failure)
               Rule Parser → Return structured JSON
```

- **Ollama AI**: Uses `format: "json"` for structured output, connection pool reuse
- **Rule-based Fallback**: Auto-fallback when Ollama unavailable, ensures service availability
- **Connection Pre-check**: Checks Ollama availability on startup, caches result to avoid无效等待

## License

MIT
