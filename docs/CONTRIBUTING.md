# Contributing to MindPulse Agent

Thank you for your interest in contributing to MindPulse Agent! This guide will help you get started with the development workflow, coding standards, and best practices for this project.

MindPulse Agent is the AI core of the MindPulse system — a Python microservice that provides natural language task analysis, note summarization, and study insights for college students. It runs on FastAPI + Ollama with rule-based fallback.

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Docker](#docker)
- [Reporting Issues](#reporting-issues)
- [Pull Request Checklist](#pull-request-checklist)

---

## Getting Started

### Prerequisites

- **Python 3.10+** (3.10, 3.11, or 3.12)
- **Ollama** with `qwen2.5:1.5b` model (optional for development — the service degrades gracefully to rule-based parsing)
- **Docker & Docker Compose** (optional, for containerized development)
- **Git**

### Fork and Clone

1. Fork this repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/MindPulse-agent.git
   cd MindPulse-agent
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/<org>/MindPulse-agent.git
   ```

### Environment Setup

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install development dependencies (includes production deps)
pip install -r requirements-dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env to configure OLLAMA_BASE_URL, OLLAMA_MODEL, etc.
```

### Verify Setup

```bash
# Run the test suite to confirm everything works
make test

# Start the development server
make run
# Server will be available at http://localhost:8000
```

---

## Project Structure

```
MindPulse-agent/
├── app/
│   ├── main.py                       # FastAPI application entry point
│   ├── core/
│   │   ├── config.py                 # Settings via pydantic-settings (env vars)
│   │   └── ollama_client.py          # Ollama HTTP client (connection pool reuse)
│   ├── api/v1/endpoints/
│   │   ├── tasks.py                  # Task analysis endpoint
│   │   ├── notes.py                  # Note summarization endpoint
│   │   └── study_insight.py          # Study insight endpoint
│   ├── agents/
│   │   ├── task_analyzer.py          # Task analysis agent (Ollama + fallback)
│   │   ├── note_summarizer.py        # Note summarization agent (Ollama + fallback)
│   │   └── study_insight_agent.py    # Study insight agent (Ollama + fallback)
│   └── utils/
│       ├── task_parser.py            # Rule-based task parser (fallback)
│       ├── note_parser.py            # Rule-based note parser (fallback)
│       └── study_insight_parser.py   # Rule-based study insight parser (fallback)
├── tests/
│   ├── conftest.py                   # Shared fixtures (TestClient, sample data)
│   ├── unit/                         # Unit tests (parsers, agents, client)
│   └── integration/                  # Integration tests (API endpoints)
├── scripts/
│   ├── setup.sh                      # One-step environment setup
│   ├── run_tests.sh                  # Full test suite runner
│   ├── lint.sh                       # Code quality checks
│   └── test_all_endpoints.py         # Live endpoint smoke tests
├── docs/                             # Project documentation
├── requirements.txt                  # Production dependencies
├── requirements-dev.txt              # Development dependencies
├── pyproject.toml                    # Project metadata + tool config
├── Makefile                          # Development commands
├── Dockerfile                        # Multi-stage production build
├── docker-compose.yml                # Container orchestration
└── .env.example                      # Environment variable template
```

---

## Development Workflow

### Branch Naming

Create a descriptive branch from `main`:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New functionality | `feature/batch-priority-sorting` |
| `fix/` | Bug fixes | `fix/date-parser-weekday-offset` |
| `docs/` | Documentation changes | `docs/api-examples` |
| `refactor/` | Code restructuring | `refactor/extract-common-prompt` |
| `test/` | Adding or updating tests | `test/edge-cases-note-parser` |
| `chore/` | Build, tooling, dependencies | `chore/update-fastapi-0.115` |

```bash
git checkout -b feature/your-feature-name
```

### Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

| Type | When to Use |
|------|-------------|
| `feat` | A new feature or endpoint |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `style` | Formatting, whitespace (no logic change) |
| `refactor` | Code restructuring (no behavior change) |
| `test` | Adding or updating tests |
| `chore` | Build, CI, tooling, dependencies |
| `perf` | Performance improvement |

**Examples:**

```
feat(agents): add priority-based task sorting

Implement weighted scoring for task urgency based on due date
proximity and explicit priority keywords.

Closes #42
```

```
fix(parser): handle "day after tomorrow" correctly

The date parser was off by one day when processing Chinese
relative date expressions like 后天.
```

### Pull Request Process

1. Keep your branch up to date with `main`:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```
2. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
3. Open a Pull Request against `main`
4. Fill in the PR template with a clear description of what changed and why
5. Link any related issues
6. Wait for review and address feedback

---

## Running the Application

### Local Development

```bash
# Start with auto-reload (recommended for development)
make run
# Equivalent to: uvicorn app.main:app --reload --port 8000

# Start in production mode (no auto-reload, binds to 0.0.0.0)
make run-prod
```

The API will be available at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

### Environment Variables

Configure via `.env` file (copy from `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | Model to use for inference |
| `OLLAMA_ENABLED` | `true` | Set to `false` to use rule-based parsing only |

### Makefile Commands

Run `make help` to see all available targets:

| Command | Description |
|---------|-------------|
| `make install` | Install production dependencies |
| `make dev` | Install all dependencies (production + dev tools) |
| `make run` | Start development server with auto-reload |
| `make run-prod` | Start production server |
| `make test` | Run all tests |
| `make test-unit` | Run unit tests only |
| `make test-integration` | Run integration tests only |
| `make test-cov` | Run tests with HTML + terminal coverage report |
| `make lint` | Run flake8 + mypy |
| `make format` | Auto-format with black + isort |
| `make clean` | Remove cache files, build artifacts, coverage data |
| `make docker-build` | Build Docker image |
| `make docker-up` | Start Docker container |
| `make docker-down` | Stop Docker container |

---

## Testing

### Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── unit/
│   ├── test_task_parser.py         # Rule-based parser tests
│   ├── test_note_parser.py         # Note parser tests
│   ├── test_study_insight_parser.py # Study insight parser tests
│   ├── test_task_analyzer.py       # TaskAnalyzerAgent tests (mocked Ollama)
│   ├── test_note_summarizer.py     # NoteSummarizerAgent tests (mocked Ollama)
│   ├── test_study_insight_agent.py # StudyInsightAgent tests (mocked Ollama)
│   └── test_ollama_client.py       # OllamaClient tests (mocked aiohttp)
└── integration/
    └── test_api.py             # API endpoint tests via TestClient
```

### Running Tests

```bash
# Run all tests
make test

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Run tests with coverage report (HTML + terminal)
make test-cov
# HTML report generated at htmlcov/index.html

# Run a specific test file
pytest tests/unit/test_task_parser.py -v

# Run tests matching a keyword
pytest -k "test_parse_date" -v
```

### Writing Tests

**Async tests** — use `@pytest.mark.asyncio` (or omit it; `asyncio_mode = "auto"` is configured):

```python
async def test_analyze_task_returns_title():
    result = await analyzer.analyze("Submit math homework tomorrow")
    assert result["title"] is not None
```

**Mocking Ollama** — agent tests must mock the Ollama client to avoid requiring a running model:

```python
from unittest.mock import patch, AsyncMock

@patch("app.agents.task_analyzer.ollama_client")
async def test_with_mock_ollama(mock_client):
    mock_client.generate = AsyncMock(return_value='{"title": "Homework"}')
    result = await analyzer.analyze("do homework")
    assert result["title"] == "Homework"
```

**Shared fixtures** — defined in `tests/conftest.py`:

| Fixture | Description |
|---------|-------------|
| `client` | FastAPI `TestClient` instance |
| `sample_task` | Single task description string |
| `sample_tasks` | List of task description strings |
| `sample_note` | Sample note content string |

**Markers** — use pytest markers to categorize tests:

```python
@pytest.mark.slow
async def test_large_batch_analysis():
    ...

@pytest.mark.integration
class TestTaskEndpoint:
    ...
```

### Coverage

Aim for high coverage on utility parsers and agent logic. Run `make test-cov` to generate a report. The coverage report highlights untested branches in the rule-based parsers, which are the most error-prone code paths.

---

## Code Quality

### Formatting

We use **Black** (code formatter) and **isort** (import sorter) with a line length of **100 characters**.

```bash
# Auto-format all code
make format

# Check formatting without modifying files
black --check app/ tests/
isort --check-only app/ tests/
```

### Linting

We use **Flake8** (style checker) and **mypy** (static type checker).

```bash
# Run all linters
make lint

# Individual tools
flake8 app/ tests/
mypy app/
```

### Style Rules

| Rule | Details |
|------|---------|
| **Line length** | 100 characters max |
| **Type hints** | Required on all function parameters and return values |
| **Logging** | Use the `logging` module — never `print()` |
| **Request/Response** | Define Pydantic models for all API inputs and outputs |
| **Batch operations** | Use `asyncio.gather()` instead of sequential loops |
| **Configuration** | Use `pydantic-settings` `BaseSettings` — never `os.getenv()` directly |
| **Docstrings** | Write docstrings for public functions and classes |
| **Naming** | `snake_case` for functions/variables, `PascalCase` for classes |
| **Imports** | Grouped and sorted by isort (stdlib → third-party → first-party) |

### Tool Configuration

All tool settings are centralized in `pyproject.toml`:

- `[tool.black]` — line-length 100, targets py310-py312
- `[tool.isort]` — profile "black", known first-party `["app"]`
- `[tool.mypy]` — strict mode with `disallow_untyped_defs`
- `[tool.flake8]` — max-line-length 100, ignores E501 and W503
- `[tool.pytest.ini_options]` — asyncio auto mode, markers for `slow`/`integration`/`unit`

---

## Docker

### Build and Run

```bash
# Build the image
make docker-build

# Start the container
make docker-up

# Stop the container
make docker-down
```

### Docker Compose Configuration

The `docker-compose.yml` defines a single `web` service that:

- Builds from the local `Dockerfile` (multi-stage: builder + runtime)
- Maps port `8000:8000`
- Passes Ollama configuration via environment variables
- Includes a health check on `/health`
- Runs as a non-root `appuser`

### Connecting to Ollama

When running in Docker, Ollama must be accessible from the container. If Ollama runs on the host machine:

```bash
# Use host networking (Linux)
docker run --network host ...

# Or use host.docker.internal (macOS/Windows)
# Set OLLAMA_BASE_URL=http://host.docker.internal:11434 in .env
```

---

## Reporting Issues

Use [GitHub Issues](../../issues) to report bugs or request features. Please include:

**For bug reports:**

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Error logs or stack traces (if applicable)
- Environment: Python version, OS, Ollama version

**For feature requests:**

- A clear description of the feature
- Use case — why is this needed?
- Proposed API design (if applicable)

---

## Pull Request Checklist

Before submitting a PR, confirm:

- [ ] Code is formatted with `make format`
- [ ] All linters pass with `make lint`
- [ ] All tests pass with `make test`
- [ ] New code has type hints on all function signatures
- [ ] New features have corresponding tests
- [ ] No `print()` statements — use `logging` instead
- [ ] Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] Branch is up to date with `main`
- [ ] Documentation is updated if the API surface changed

---

## Questions?

If you have questions about contributing, feel free to open a discussion in [GitHub Issues](../../issues) or reach out to the maintainers. We're happy to help!
