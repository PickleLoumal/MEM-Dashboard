# Justfile for Project

set shell := ["bash", "-c"]

# Start Django development server
django:
    #!/bin/bash
    echo "🐍 Starting Django API server on http://localhost:8001..."
    export PYTHONPATH=$PYTHONPATH:$(pwd)/src/django_api
    ./venv/bin/python src/django_api/manage.py migrate --verbosity=1
    ./venv/bin/python src/django_api/manage.py runserver 0.0.0.0:8001

# Start full development environment (Django + React)
dev:
    bash scripts/active/production/dev-start-csi300.sh

# Build and preview React frontend (production mode)
start:
    bash scripts/active/production/build_csi300_frontend.sh
    bash scripts/active/production/start_csi300_preview.sh

# 2. Install: Install Python dependencies from requirements.txt
install:
    #!/bin/bash
    set -e
    echo "📦 Installing Python dependencies from requirements.txt..."
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
    echo "✅ Dependencies installed successfully!"

# 3. Deploy CSI300 Frontend: Deploy the CSI300 React app to AWS
deploy-csi300-frontend:
    bash scripts/active/deployment/deploy-csi300-frontend-to-aws.sh

# 4. Deploy ECS: Deploy the backend to AWS ECS
deploy-ecs:
    ./venv/bin/python scripts/active/deployment/deploy_to_ecs.py

# 5. Sync Data: Sync local database data to RDS (push)
sync-data:
    ./venv/bin/python scripts/active/deployment/sync_data_to_rds.py

# 5b. Pull Data: Pull data from AWS RDS to local database
pull-data:
    ./venv/bin/python scripts/active/deployment/sync_data_from_rds.py

# 6. Deploy MEM Frontend: Deploy the MEM Dashboard frontend to AWS
deploy-mem-frontend:
    bash scripts/active/deployment/deploy-mem-frontend-to-aws.sh

# 7. Generate TypeScript types from Django OpenAPI schema
codegen:
    #!/bin/bash
    set -e
    echo "📄 Exporting OpenAPI schema from Django..."
    ./venv/bin/python src/django_api/manage.py spectacular --file schema.yaml
    echo "🔧 Generating TypeScript types..."
    (cd csi300-app && npm run generate-api)
    echo "✅ Codegen complete! Types updated in csi300-app/src/shared/api/generated/"

# 8. Generate investment summaries for all companies
summary-all:
    #!/bin/bash
    echo "🚀 Starting batch generation of investment summaries..."
    export PYTHONPATH=$PYTHONPATH:$(pwd)/src/django_api
    ./venv/bin/python -m csi300.services.cli

# 9. Lint: Run Ruff linter on Python code (src only)
lint:
    @echo "🔍 Running Ruff linter on src/..."
    ./venv/bin/ruff check src

# 10. Lint Fix: Run Ruff linter with auto-fix
lint-fix:
    @echo "🔧 Running Ruff linter with auto-fix..."
    ./venv/bin/ruff check --fix src

# 11. Format: Run Ruff formatter on Python code
format:
    @echo "✨ Running Ruff formatter..."
    ./venv/bin/ruff format src

# 12. Format Check: Check if code is formatted correctly
format-check:
    @echo "📋 Checking code formatting..."
    ./venv/bin/ruff format --check src

# 13. Check: Run all code quality checks (lint + format check)
check:
    @echo "🔍 Running all code quality checks on src/..."
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    @echo "📋 Step 1: Checking code formatting..."
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ./venv/bin/ruff format --check src
    @echo ""
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    @echo "🔍 Step 2: Running linter..."
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ./venv/bin/ruff check src
    @echo ""
    @echo "✅ All checks passed!"

# 14. Fix: Run all auto-fixes (format + lint fix)
fix:
    @echo "🔧 Running all auto-fixes on src/..."
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    @echo "✨ Step 1: Formatting code..."
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ./venv/bin/ruff format src
    @echo ""
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    @echo "🔧 Step 2: Auto-fixing linter issues..."
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ./venv/bin/ruff check --fix src
    @echo ""
    @echo "✅ All fixes applied!"

# 15. Deploy PDF Service: Deploy PDF generation infrastructure to AWS
deploy-pdf-service:
    #!/bin/bash
    echo "📄 Deploying PDF Service Infrastructure to AWS..."
    chmod +x aws-deployment/scripts/deploy-pdf-service.sh
    bash aws-deployment/scripts/deploy-pdf-service.sh

# 16. Deploy PDF Service (skip Docker build): Deploy infrastructure only
deploy-pdf-service-infra:
    #!/bin/bash
    echo "📄 Deploying PDF Service Infrastructure (skip Docker build)..."
    chmod +x aws-deployment/scripts/deploy-pdf-service.sh
    bash aws-deployment/scripts/deploy-pdf-service.sh --skip-build

# 17. Build LaTeX Service Image: Build and push LaTeX Docker image only
build-latex-service:
    #!/bin/bash
    echo "🐳 Building LaTeX Service Docker image..."
    chmod +x aws-deployment/scripts/deploy-pdf-service.sh
    bash aws-deployment/scripts/deploy-pdf-service.sh --skip-infra
