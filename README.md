# ALFIE Dashboards

A unified codebase containing two data-rich dashboards backed by a common Django + PostgreSQL API:

1. **MEM Dashboard** – macroeconomic intelligence with BEA and FRED coverage.
2. **Chinese Stock Dashboard** – CSI300 company and stock-scoring experience delivered via a modern React frontend.

The repository ships both frontends, the shared backend services, and the deployment artifacts required to run locally or in cloud environments.

---

## Architecture at a Glance

- **Backend**: Django 4.2 REST API in `src/django_api` with apps for BEA, FRED (US/JP), CSI300 companies, stock scoring, policy updates, and shared content.
- **Database**: PostgreSQL (`mem_dashboard`) storing macroeconomic series, BEA configs, CSI300 companies, stock scores, and Django system tables.
- **Frontends**:
  - **MEM Dashboard**: static HTML/CSS/JS pages under `src/pages` and `src/assets`, deployable to S3/CloudFront or any static host.
  - **Chinese Stock Dashboard**: React + Vite app in `csi300-app` that consumes the Django API; legacy static CSI300 pages are preserved for backwards compatibility.
- **Data ingest & scoring**: management commands and scripts under `src/django_api/*/management` plus `scripts/active` for daily stock scoring.

Directory highlights:

```
src/
  django_api/           # Django project (API, models, services, management commands)
  assets/, pages/       # MEM Dashboard static assets and HTML entry points
csi300-app/             # React/Vite Chinese Stock Dashboard (shared API client)
config/                 # Frontend configuration (API endpoints, manifests)
aws-deployment/         # Deployment scripts (e.g., S3/CloudFront sync)
data/, tests/, api/     # Supporting datasets, pytest suites, and API schema
```

---

## Backend (Django API)

### Features
- **Macroeconomic data**: BEA and FRED ingestion, indicator metadata, and REST endpoints for US and JP coverage.
- **Chinese equity data**: CSI300 company fundamentals, intraday/historical pricing, VWAP utilities, and daily stock scoring (`stocks` app).
- **Policy updates**: Federal Register integration (`policy_updates` app).
- **API documentation**: DRF Spectacular schema with OpenAPI generation (consumed by the React app via `schema.yaml`).

### Configuration
- Python 3.13+ recommended.
- Primary settings in `src/django_api/django_api/settings.py` with dotenv support for overrides (`.env.local`, `.env`). Key variables:
  - `DJANGO_SECRET_KEY` – secret key for production.
  - `DEBUG` – enable/disable debug mode (default `True`).
  - `DATABASE_URL` equivalent vars: `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT` under `DATABASES['default']` (defaults target `mem_dashboard` on localhost:5432).
  - `CORS_*` – permissive defaults for local React/static origins.

### Local Development
1. **Install dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Run migrations (if needed)**
   ```bash
   cd src/django_api
   python manage.py migrate
   ```
3. **Start the API**
   ```bash
   cd src/django_api
   python manage.py runserver 0.0.0.0:8000
   ```
   Swagger/OpenAPI can be exposed through DRF Spectacular if routed (see `django_api/urls.py`).

### Key Endpoints (selected)
- **CSI300/Stocks** (`src/django_api/stocks`):
  - `GET /api/stocks/list/` – CSI300 company tickers and metadata.
  - `GET /api/stocks/intraday/?symbol=...` – 1m intraday data + VWAP context.
  - `GET /api/stocks/history/?symbol=...` – historical OHLCV with interval/period options.
  - `POST /api/stocks/score/` – trigger daily scoring for a symbol (imports `scripts/active/daily_score_calculator_db.py` or runs as a subprocess fallback).
- **CSI300 Companies** (`src/django_api/csi300`): company details, filter/search endpoints consumed by both CSI300 frontends.
- **FRED/BEA**: macro indicator retrieval and configuration management across US/JP namespaces.
- **Policy Updates**: recent federal register entries and search utilities.

> Tip: inspect each app’s `urls.py` and DRF `views.py` for the full list of available routes and serializer contracts.

---

## MEM Dashboard Frontend (Static)

- Location: `src/pages` (entry pages) with shared assets in `src/assets` and API configs in `config/`.
- Deployment: `aws-deployment/frontend/deploy-frontend.sh` syncs `src/` to S3/CloudFront; paths are relative so the bundle can also be served from any static host.
- Usage: open `src/pages/US.html` (or `index.html`) for the US macro view; static JS pulls data from the Django API using the manifests under `config/`.

---

## Chinese Stock Dashboard Frontend (React)

### Features
- CSI300 company browser, detail views, filters, and mobile-responsive layouts.
- REST integration via generated axios client (`npm run generate-api` uses `schema.yaml`).
- Modern toolchain: React 19, Vite, TailwindCSS, ESLint/Prettier, Vitest + Testing Library.

### Local Development
```bash
cd csi300-app
npm install
npm run dev        # Vite dev server (defaults to :5173)
```
Set environment in `.env.local` (or `.env`) with at least:
```bash
VITE_API_BASE=http://localhost:8000
VITE_APP_NAME="Chinese Stock Dashboard"
```

### Production Build
```bash
cd csi300-app
npm run build
```
Artifacts are emitted to `dist/` (React outputs into `dist/react/` alongside legacy static assets). Deploy the `csi300-app` directory to your static host or pair with the Django backend behind the same domain.

### Legacy CSI300 Pages
Legacy static pages (`browser.html`, `detail.html`, `landing.html`, etc.) remain under `csi300-app/legacy` and root-level HTML for compatibility; they load configuration from `config/` and talk to the same Django endpoints.

---

## Testing
- **Backend**: `pytest` or `python manage.py test` from `src/django_api`.
- **Frontend (React)**: `npm run lint`, `npm run typecheck`, and `npm run test`/`vitest` inside `csi300-app`.

---

## Deployment Notes
- **Static Frontends**: suitable for S3/CloudFront, Netlify, or any static server; ensure `config/api_config.js` and `.env` values point to the live API.
- **Django API**: run under Gunicorn or another WSGI host; containerization supported via `dockerfile.aw` and `runtime.txt`. Configure environment variables and database connectivity accordingly.
- **Shared Database**: both dashboards rely on the same PostgreSQL schema; migrations live with each Django app under `src/django_api/*/migrations`.

---

## Support & Troubleshooting
- Verify PostgreSQL connectivity and that migrations have run.
- Ensure CORS settings cover your frontend origin.
- For CSI300 scoring, confirm `scripts/active/daily_score_calculator_db.py` is available and that market data dependencies (e.g., AkShare) are installed.
- Check browser dev tools network tab to validate API responses for both dashboards.

