# Penscite backend

FastAPI service. Uses [uv](https://docs.astral.sh/uv/) for Python, dependencies and commands. Run everything from `backend/`.

## Setup

```sh
uv sync                  # create .venv and install deps (including dev)
cp .env.example .env     # then fill in real values
```

The app refuses to start if a required env var is missing or invalid.

## Run

```sh
uv run uvicorn app.main:app --reload    # http://localhost:8000
```

- Health check: `GET /health`
- API docs: http://localhost:8000/docs

## Check

```sh
uv run ruff check .      # lint
uv run ruff format .     # format
uv run pytest -m "not integration"
```

## Dependencies

```sh
uv add <package>         # runtime dep (read the dependency policy in ../AGENTS.md first)
uv add --dev <package>   # dev-only dep
uv lock --upgrade        # refresh the lockfile
```

## Migrations

```sh
uv run alembic upgrade head
```

Conventions for agents and contributors live in [AGENTS.md](AGENTS.md).
