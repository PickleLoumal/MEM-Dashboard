# Justfile for MEM Dashboard 2

set shell := ["bash", "-c"]

# Start Django development server
django:
    #!/bin/bash
    echo "🐍 Starting Django API server on http://localhost:8001..."
    cd src/django_api
    ../../venv/bin/python manage.py migrate --verbosity=1
    ../../venv/bin/python manage.py runserver 8001

# Start full development environment (Django + React)
dev:
    bash scripts/active/production/dev-start-csi300.sh

# Build and preview React frontend (production mode)
start:
    bash scripts/active/production/build_csi300_frontend.sh
    bash scripts/active/production/start_csi300_preview.sh

# 2. Install: Install Python dependencies from requirements.txt
install:
    ./venv/bin/pip install -r requirements.txt

# 3. Deploy CSI300 Frontend: Deploy the CSI300 React app to AWS
deploy-csi300-frontend:
    bash scripts/active/deployment/deploy-csi300-frontend-to-aws.sh

# 4. Deploy ECS: Deploy the backend to AWS ECS
deploy-ecs:
    ./venv/bin/python scripts/active/deployment/deploy_to_ecs.py

# 5. Sync Data: Sync local database data to RDS
sync-data:
    ./venv/bin/python scripts/active/deployment/sync_data_to_rds.py

# 6. Deploy MEM Frontend: Deploy the MEM Dashboard frontend to AWS
deploy-mem-frontend:
    bash scripts/active/deployment/deploy-mem-frontend-to-aws.sh

# 7. Generate TypeScript types from Django OpenAPI schema
codegen:
    #!/bin/bash
    set -e
    echo "📄 Exporting OpenAPI schema from Django..."
    (cd src/django_api && ../../venv/bin/python manage.py spectacular --file ../../schema.yaml)
    echo "🔧 Generating TypeScript types..."
    (cd csi300-app && npm run generate-api)
    echo "✅ Codegen complete! Types updated in csi300-app/src/shared/api/generated/"

# 8. Generate investment summaries for all companies
summary-all:
    @echo "🚀 Starting batch generation of investment summaries..."
    ./venv/bin/python src/django_api/csi300/services/investment_summary_generator.py
