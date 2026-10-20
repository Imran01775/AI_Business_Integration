# AI platform package

Installable Python package (`ai_platform`) used by the backend and optionally as a standalone gateway (Phase 07).

## Install

```bash
cd ai-platform
uv sync
```

## Quality commands

```bash
uv run ruff check .
uv run mypy src
uv run pytest
```

STT provider evaluation: `tests/eval/stt/README.md`.
