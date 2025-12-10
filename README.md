# ALFIE Dashboards

A unified codebase containing two data-rich dashboards plus the services and automation they depend on:
- **MEM Dashboard**: macroeconomic intelligence (BEA, FRED US/JP) served as static HTML/JS.
- **Chinese Stock Dashboard**: CSI300 company browser and stock scoring delivered via React/Vite, with legacy static pages preserved.

The repository bundles frontends, the Django REST API, data/ingestion scripts, and AWS deployment assets.

---

## What’s inside
- `src/django_api`: Django 4.2 REST API (PostgreSQL) with apps for BEA, FRED US/JP, CSI300 companies, stock scoring (AkShare-powered), policy updates, and shared content. DRF Spectacular schema lives in `schema.yaml`.
- `src/pages`, `src/assets`, `config`: static MEM dashboard entry points and runtime config (`config/api_config.js`).
- `csi300-app`: React 19 + Vite app (`src/`), generated API client, Tailwind, ESLint/Prettier/Vitest. `legacy/` holds the historic HTML/JS CSI300 experience.
- `scripts`: day-to-day automation (dev-start, deployment helpers, stock scoring, OpenAPI → TS generation).
- `aws-deployment`: ECS/S3/CloudFront infrastructure, CloudFormation templates, and runbooks.
- `data`, `tests`, `visualization`: data exports, pytest suites (backend + jsdom-based frontend), architecture/complexity reports.
- `api`: lightweight serverless fallbacks (`health.py`, `indicators.py`) for production environments that need static responses.

---

## Prerequisites
- Python 3.11+ (see `runtime.txt`), pip, and a virtualenv.
- Node.js 18+/20+ and npm for the React app.
- PostgreSQL 14+ reachable (defaults to `mem_dashboard` on localhost:5432; adjust `DATABASES` in settings if needed).
- Optional: Redis (`REDIS_URL`) for intraday/historical stock caching; AWS CLI for deployments.
- API keys: `FRED_API_KEY` (FRED data fetchers), optional `XAI_API_KEY` (CSI300 investment summary generator).

---

## Quick start (local)
### Backend API
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd src/django_api
python manage.py migrate
python manage.py runserver 0.0.0.0:8001
```
Settings load `.env.local` then `.env`. Key variables: `DJANGO_SECRET_KEY`, `DEBUG`, `CORS_*`, `FRED_API_KEY`, `REDIS_URL`; database defaults are defined directly in `django_api/settings.py`.

### MEM dashboard (static)
Serve the root or `src/pages` after the API is running:
```bash
python3 -m http.server 3000  # from repo root
```
Visit `http://localhost:3000/` (root) or `http://localhost:3000/src/pages/US.html`. `config/api_config.js` points to `http://localhost:8001/api` for local usage.

### Chinese Stock dashboard (React + legacy)
```bash
cd csi300-app
npm install
npm run dev        # http://localhost:5173
```
Set `.env.local` with at least:
```
VITE_API_BASE=http://localhost:8001
VITE_APP_NAME="Chinese Stock Dashboard"
```
Legacy static pages live in `csi300-app/legacy` (serve with `python3 -m http.server 8082` if needed). Convenience starters: `scripts/active/production/dev-start-mem.sh` (ports 8000/3000) and `scripts/active/production/dev-start-csi300.sh` (ports 8001/5173/8082).

---

## Repository map
```
src/django_api/          Django project (apps: bea, fred_us, fred_jp, csi300, stocks, policy_updates, content)
src/assets/, src/pages/  MEM static pages and shared assets
csi300-app/              React app + legacy HTML; build output in dist/
config/                  Frontend runtime config, DB helpers, SQL schemas
scripts/                 Active tools, deployment helpers, scoring utilities, OpenAPI → TS generator
aws-deployment/          ECS/S3/CloudFront IaC, scripts, env samples
data/, tests/, visualization/   Datasets, pytest suites, diagrams/reports
api/                     Serverless health/indicator fallbacks
```

---

## Backend (Django API)
- **Apps and endpoints**: BEA (`/api/bea`), FRED US/JP (`/api/fred-us`, `/api/fred-jp`), CSI300 companies (`/api/csi300/api/companies/…`), stocks (`/api/stocks/…` for list, intraday, historical, top-picks, scoring), policy updates, health/status endpoints. See each app’s `urls.py`.
- **Data ingest and scoring**:
  - Management commands: `fetch_japan_data`, `update_series_info`, `categorize_*` (FRED); `update_market_cap`, `update_stock_prices`, `import_investment_summary` (CSI300); `update_stocks` (stocks).
  - Scoring/analysis scripts in `scripts/active`: `daily_score_calculator_db.py`, `vectorized_batch_calculator.py`, `Batch Stock Analyzer.py`, plus `update_api_types.sh` to refresh `schema.yaml` and regenerate the TS client.
  - AkShare powers intraday/daily retrieval; Redis caching is optional via `REDIS_URL`.
- **API schema and types**: generate/update OpenAPI with `python src/django_api/manage.py spectacular --file schema.yaml` or run `scripts/active/update_api_types.sh` (also executes `npm run generate-api` in `csi300-app`).
- **Settings**: permissive CORS defaults for local/static origins; logging writes to `logs/django_api.log`; database defaults to `mem_dashboard` on localhost:5432.

---

## Frontends
- **MEM static**: `index.html` and `src/pages/US.html`/`JP.html` pull data from the Django API using `config/api_config.js`. Deployable to any static host; `aws-deployment/frontend` contains S3/CloudFront sync scripts.
- **Chinese Stock React app**: feature-based structure in `csi300-app/src` with aliases (`@`, `@features`, `@shared`, etc.). Build with `npm run build` (output to `dist/`); uses generated axios client from `schema.yaml`.
- **Legacy CSI300**: preserved in `csi300-app/legacy` and root-level HTML for compatibility; config in `legacy/config/csi300_api_config.js`.

---

## Automation, scripts, and ops
- **Dev/start helpers**: `scripts/active/production/dev-start-mem.sh` and `dev-start-csi300.sh` boot API + static/React servers with port hygiene and migration checks.
- **Deployment**: `scripts/active/deployment/*.sh` for S3/CloudFront sync and ECS helpers; full IaC and runbooks in `aws-deployment/README.md`.
- **Database and tooling**: SQL schemas and dynamic configs under `config/`; utility scripts in `scripts/tools` (cert generation, DB export, script validation).
- **Serverless/edge**: `api/health.py` and `api/indicators.py` act as lightweight production fallbacks when a full API is unavailable.

---

## Testing and quality

### Code Quality (Ruff)
The project uses [Ruff](https://docs.astral.sh/ruff/) for Python linting and formatting - an extremely fast linter written in Rust that replaces Flake8, isort, Black, and more.

```bash
# Quick commands (using Justfile)
just check      # Run all checks (lint + format check)
just fix        # Auto-fix all issues (format + lint fix)

# Individual commands
just lint           # Run linter only
just lint-fix       # Run linter with auto-fix
just format         # Format code
just format-check   # Check formatting without changes
```

Configuration is in `pyproject.toml`. Ruff enforces:
- PEP 8 compliance (pycodestyle)
- Import sorting (isort)
- Django best practices
- Modern Python patterns (pyupgrade)
- Security checks (flake8-bugbear)
- Type safety patterns

See `.cursor/rules/project-rules/ruff-integration.mdc` for detailed usage guide.

### Testing
- **Backend**: `pytest` (configured via `pyproject.toml` with `DJANGO_SETTINGS_MODULE=django_api.settings`) or `python src/django_api/manage.py test`. Reuse DB with `--reuse-db`.
- **Frontend**: from `csi300-app`, run `npm run lint`, `npm run typecheck`, and `npm run test` (Vitest + Testing Library with jsdom setup in `tests/frontend/setup.ts`).

---

## Documentation and troubleshooting
- Scripts catalog: `scripts/README.md` and `scripts/QUICK_START.md`.
- React restructure notes: `docs/2025-11-30/project-restructure.md` (feature-based layout and aliases).
- Deployment guides: `aws-deployment/README.md` and `aws-deployment/docs/*`.
- Logs: backend writes to `logs/django_api.log`; app/server startup scripts echo URLs and health checks.
- Common fixes: ensure migrations run, Postgres reachable, CORS covers your origin, `FRED_API_KEY` configured for indicator fetchers, and AkShare/Redis installed if using stock services.
