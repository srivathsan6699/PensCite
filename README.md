# Penscite

An AI research assistant for UK pensions professionals. Ask a question in plain English and get an answer grounded in official UK pensions sources, with a citation to the exact page.

## Who it's for

Paraplanners, financial advisers, pension administrators, trustees and payroll teams who spend hours finding the right page in HMRC's Pensions Tax Manual and other official guidance. Penscite gives them a cited answer and the source passage in seconds. It gives information, not advice.

## Stack

| Layer              | Choice                                               |
| ------------------ | ---------------------------------------------------- |
| Backend            | Python + FastAPI                                     |
| Frontend           | Vite + React SPA + TypeScript                        |
| Database           | Supabase Postgres (users, chats, documents, chunks)  |
| Migrations         | SQLAlchemy models + Alembic                          |
| Retrieval          | Supabase `pgvector` + Postgres full-text search      |
| Auth               | Supabase Auth (email only)                           |
| Hosting            | Railway                                              |
| LLM + embeddings   | OpenAI                                               |

## Repo layout

```text
penscite/
├── README.md           # this file
├── data/               # local corpus + download script (payloads gitignored)
├── docs/
│   └── guides/         # setup guides (Supabase, backend, frontend)
├── backend/            # FastAPI service
└── frontend/           # React SPA (Vite)
```

## Prerequisites

Install these before setting up `backend/` or `frontend/`:

| Tool | Version | Used for | Install |
| ---- | ------- | -------- | ------- |
| [Python](https://www.python.org/downloads/) | 3.12+ | Backend runtime | OS package manager or python.org |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | latest | Backend deps + `data/download.py` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| [Node.js](https://nodejs.org/) | 20+ (LTS) | Frontend toolchain | nodejs.org or `nvm install --lts` |
| [pnpm](https://pnpm.io/installation) | latest | Frontend package manager | `corepack enable && corepack prepare pnpm@latest --activate` |

You also need accounts/keys for external services once the app is wired up. Start with [docs/guides/supabase-setup.md](docs/guides/supabase-setup.md) (account + project), then create an [OpenAI API key](https://platform.openai.com/api-keys) when the LLM layer is wired up.

## Running locally

To be added during the build. Setup guides:

- [Supabase](docs/guides/supabase-setup.md) — account, hosted project (dashboard or CLI)
- [Backend](docs/guides/backend-setup.md)
- [Frontend](docs/guides/frontend-setup.md)

## Sample data

The corpus is official UK pensions guidance fetched through the GOV.UK Content API: the HMRC Pensions Tax Manual, HMRC Pension Schemes Newsletters, and GOV.UK workplace pension guidance. Sources are used under the Open Government Licence v3.0. Run the standalone downloader from the repo root:

```bash
uv run data/download.py
```

It saves raw pages under `data/downloads/` and writes a `manifest.json`.
Downloaded files are gitignored; the `data/` folder itself stays in git for the script and notes.
