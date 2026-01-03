# LaTeX Compiler Service

A microservice for generating PDF investment reports from LaTeX templates. Designed to run as an ECS task consuming messages from AWS SQS.

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────────┐
│   Django API    │────▶│   AWS SQS    │────▶│  LaTeX Service      │
│  (pdf_service)  │     │  (Queue)     │     │  (this container)   │
└─────────────────┘     └──────────────┘     └──────────┬──────────┘
                                                        │
                                             ┌──────────▼──────────┐
                                             │      AWS S3         │
                                             │  (charts + PDFs)    │
                                             └─────────────────────┘
```

## Features

- **SQS Consumer**: Long-polling with configurable visibility timeout
- **Chart Generation**: matplotlib-based charts (stock price, ROE, P/E ratio)
- **Template Rendering**: Jinja2 with LaTeX-safe escaping
- **PDF Compilation**: XeLaTeX with CJK font support
- **S3 Integration**: Upload charts and final PDFs
- **Status Callbacks**: Real-time progress updates to Django API
- **Graceful Shutdown**: SIGTERM/SIGINT handling for ECS

## Local Development

### Prerequisites

1. **TeX Live** with XeLaTeX and CJK support:

```bash
# macOS
brew install --cask mactex

# Ubuntu/Debian
sudo apt-get install texlive-xetex texlive-lang-chinese fonts-noto-cjk
```

2. **Python 3.12+** with dependencies:

```bash
cd latex-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```bash
# AWS Configuration
AWS_REGION=ap-east-1
PDF_SQS_QUEUE_URL=https://sqs.ap-east-1.amazonaws.com/123456789/alfie-pdf-generation
PDF_S3_BUCKET=alfie-pdf-reports

# Django Callback
DJANGO_CALLBACK_URL=http://localhost:8001/api/pdf/internal/callback/
PDF_INTERNAL_API_KEY=your-secret-key

# Worker Settings
WORKER_POLL_INTERVAL=20
WORKER_VISIBILITY_TIMEOUT=300
WORKER_MAX_MESSAGES=1

# LaTeX Settings
LATEX_TIMEOUT_SECONDS=120
LATEX_MAX_RETRIES=2
```

### Run the Worker

```bash
python worker.py
```

## Docker Build

```bash
# Build the image
docker build -f dockerfile.aw/Dockerfile.latex-service -t alfie-latex-service .

# Run locally
docker run -it --rm \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e PDF_SQS_QUEUE_URL=... \
  -e PDF_S3_BUCKET=... \
  alfie-latex-service
```

## Message Format

The worker expects SQS messages with this JSON structure:

```json
{
  "task_id": "uuid-string",
  "template_content": "LaTeX template with \\VAR{ } placeholders",
  "preamble": "Additional LaTeX packages",
  "charts_config": [
    {"type": "stock_price", "name": "stock_price"},
    {"type": "roe_trend", "name": "roe_trend"},
    {"type": "pe_ratio", "name": "pe_ratio"},
    {"type": "financial_summary", "name": "financial_summary"}
  ],
  "data": {
    "summary": {
      "company_name": "Apple Inc.",
      "business_overview": "...",
      "recommended_action": "BUY",
      "recommended_action_detail": "..."
    },
    "company": {
      "ticker": "AAPL",
      "previous_close": 178.50,
      "pe_ratio_trailing": 28.5,
      "roe_trailing": 0.175,
      "...": "..."
    }
  },
  "settings": {
    "page_size": "a4paper",
    "margins": {"top": "2.5cm", "bottom": "2.5cm"},
    "header_left": "ALFIE",
    "header_right": "Confidential"
  }
}
```

## Module Structure

| Module | Description |
|--------|-------------|
| `worker.py` | Main SQS consumer loop |
| `config.py` | Environment-based configuration |
| `chart_generator.py` | matplotlib chart generation |
| `template_renderer.py` | Jinja2 LaTeX rendering |
| `latex_utils.py` | LaTeX escaping and compilation |
| `s3_client.py` | S3 upload/download operations |
| `callback_client.py` | Django status callback client |

## Chart Types

| Type | Description |
|------|-------------|
| `stock_price` | 52-week price performance line chart |
| `roe_trend` | Historical ROE bar chart |
| `pe_ratio` | P/E ratio trend with industry average |
| `financial_summary` | Key metrics horizontal bar chart |
| `key_metrics` | Radar/spider chart (optional) |

## Template Syntax

The service uses custom Jinja2 delimiters to avoid LaTeX conflicts:

```latex
% Variables
\VAR{ company.name | escape }

% Blocks
\BLOCK{ for item in items }
    \item \VAR{ item | escape }
\BLOCK{ endfor }

% Conditionals
\BLOCK{ if condition }
    Content
\BLOCK{ endif }

% Line statements
%% if condition
Content
%% endif

% Comments (not rendered)
%# This is a comment
```

### Available Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `escape` | Escape LaTeX special chars | `\VAR{ text \| escape }` |
| `escape_para` | Escape with paragraph breaks | `\VAR{ long_text \| escape_para }` |
| `number` | Format with thousands sep | `\VAR{ value \| number }` → `1,234.56` |
| `percentage` | Format as percentage | `\VAR{ 0.15 \| percentage }` → `15.00\%` |
| `currency('USD')` | Format as currency | `\VAR{ 100 \| currency('USD') }` → `\$100.00` |
| `date` | Format date | `\VAR{ date \| date }` → `January 02, 2026` |

## ECS Deployment

The service is designed for AWS ECS Fargate:

```hcl
resource "aws_ecs_task_definition" "latex_service" {
  family                   = "alfie-latex-service"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024   # 1 vCPU
  memory                   = 4096   # 4 GB (LaTeX needs memory)

  container_definitions = jsonencode([{
    name  = "latex-worker"
    image = "${ecr_repo}:latest"
    environment = [
      { name = "PDF_SQS_QUEUE_URL", value = "..." },
      { name = "PDF_S3_BUCKET", value = "..." }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/alfie-latex-service"
        "awslogs-region"        = "ap-east-1"
        "awslogs-stream-prefix" = "latex"
      }
    }
  }])
}
```

## Testing

```bash
# Unit tests (when implemented)
pytest tests/

# Manual test with sample message
python -c "
from worker import process_message
message = {
    'Body': '{\"task_id\": \"test-123\", \"data\": {...}}'
}
process_message(message)
"
```

## Troubleshooting

### LaTeX Compilation Fails

1. Check font availability: `fc-list | grep Noto`
2. Verify XeLaTeX: `xelatex --version`
3. Check log files in `/app/tmp/latex_*/`

### Charts Not Generated

1. Verify matplotlib backend: `matplotlib.get_backend()` should be `Agg`
2. Check data format in message payload

### S3 Upload Fails

1. Verify AWS credentials and bucket permissions
2. Check bucket exists in correct region

## License

Internal use only - ALFIE Investment Analysis System

