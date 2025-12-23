# ABOUT ALFIE

## 🎯 Project Overview

**ALFIE** (Advanced Logistics for Financial Information & Economics) is a comprehensive macroeconomic data platform designed for financial analysis, investment research, and economic monitoring. The platform aggregates, processes, and visualizes economic indicators from multiple authoritative sources to provide real-time insights into global economic conditions.

Built as a full-stack web application, ALFIE serves as a central hub for monitoring key economic metrics including GDP, inflation, unemployment, monetary policy indicators, stock market data, and policy updates across multiple regions (United States, Japan, and China).

## 🌟 Key Features

### Multi-Region Economic Data
- **United States**: Real-time data from FRED (Federal Reserve Economic Data) and BEA (Bureau of Economic Analysis)
- **Japan**: Economic indicators through FRED Japan data series
- **China**: CSI300 index companies and Chinese stock market data via AkShare integration

### Core Capabilities
- **Real-time Economic Indicators**: Live updates from authoritative government data sources
- **Interactive Dashboards**: Dynamic visualization with responsive design optimized for desktop, tablet, and mobile
- **PostgreSQL Database**: Robust data persistence with advanced indexing and JSONB metadata support
- **RESTful API**: Comprehensive Django REST Framework endpoints for programmatic access
- **Multi-indicator Support**: GDP, CPI, unemployment, housing, money supply, monetary base, federal funds rate
- **Stock Market Analytics**: Integration with Chinese stock markets (CSI300, SSE, SZSE)
- **Policy Monitoring**: Federal Register integration for tracking regulatory updates
- **Cloud Deployment**: Production-ready AWS ECS deployment with Docker containerization

### Data Sources
1. **FRED API (Federal Reserve Economic Data)**: US economic indicators with historical data
2. **BEA API (Bureau of Economic Analysis)**: Detailed GDP components and national accounts
3. **AkShare**: Chinese stock market data and real-time quotes
4. **CSI300 API**: China's premier stock index companies and financials
5. **Federal Register**: US government policy updates and regulatory changes

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ALFIE Platform Architecture                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐        HTTP/REST         ┌──────────────┐
│              │ ←──────────────────────→ │              │
│   Frontend   │                           │   Backend    │
│   Layer      │                           │   Layer      │
│              │                           │              │
│ - Dashboard  │                           │ - Django API │
│ - React App  │                           │ - DRF        │
│ - Data Viz   │                           │ - Business   │
│              │                           │   Logic      │
└──────────────┘                           └──────┬───────┘
                                                  │
                                           ┌──────▼───────┐
                                           │              │
                                           │  PostgreSQL  │
                                           │   Database   │
                                           │              │
                                           │ - FRED Data  │
                                           │ - BEA Data   │
                                           │ - Stock Data │
                                           │ - Metadata   │
                                           └──────────────┘
```

### Technology Stack

#### Backend
- **Framework**: Django 4.2.7 with Django REST Framework 3.14.0
- **Language**: Python 3.13
- **Database**: PostgreSQL 12+ with psycopg2-binary
- **WSGI Server**: Gunicorn 21.2.0 for production
- **API Documentation**: drf-spectacular for OpenAPI/Swagger

#### Frontend
- **Primary**: HTML5, CSS3, JavaScript (ES6+)
- **CSS Framework**: Tailwind CSS 3.4
- **Modern UI**: React 19.2.0 (CSI300 standalone app)
- **Build Tool**: Vite 7.2.4
- **Type Safety**: TypeScript 5.9.3

#### Data & Analytics
- **Data Processing**: Pandas 2.1.4, NumPy 1.26.3
- **Visualization**: Matplotlib 3.10+
- **Chinese Market Data**: AkShare 1.17.83
- **Caching**: Redis 5.0.4

#### Deployment & DevOps
- **Containerization**: Docker
- **Cloud Platform**: AWS ECS (Elastic Container Service)
- **Infrastructure as Code**: CloudFormation templates
- **Monitoring**: Sentry SDK integration

## 📊 Database Schema

### Core Tables

#### 1. FRED Indicators (US Data)
```sql
fred_us_indicators
├── id (PRIMARY KEY)
├── series_id (VARCHAR 50) - FRED series identifier
├── indicator_name (VARCHAR 200)
├── indicator_type (VARCHAR 50)
├── date (DATE)
├── value (DECIMAL 15,4)
├── source (VARCHAR 100)
├── unit (VARCHAR 50)
├── frequency (VARCHAR 20)
├── metadata (JSONB)
└── created_at, updated_at (TIMESTAMP)

Indexes:
- idx_fred_us_series_date (series_id, date DESC)
- idx_fred_us_type_date (indicator_type, date DESC)
- UNIQUE (series_id, date)
```

#### 2. BEA Indicators
```sql
bea_indicators
├── id (PRIMARY KEY)
├── series_id (VARCHAR 50)
├── indicator_name (VARCHAR 200)
├── table_name (VARCHAR 50)
├── line_number (VARCHAR 10)
├── date (DATE)
├── time_period (VARCHAR 10)
├── value (DECIMAL 15,4)
├── dataset_name (VARCHAR 50)
├── metadata (JSONB)
└── created_at, updated_at (TIMESTAMP)
```

#### 3. Stock Data (AkShare Integration)
```sql
stocks_data
├── id (PRIMARY KEY)
├── symbol (VARCHAR 20)
├── name (VARCHAR 200)
├── date (DATE)
├── open, high, low, close (DECIMAL)
├── volume (BIGINT)
├── market (VARCHAR 20) - SSE, SZSE, CSI300
└── metadata (JSONB)
```

#### 4. CSI300 Companies
```sql
csi300_companies
├── id (PRIMARY KEY)
├── symbol (VARCHAR 20)
├── company_name (VARCHAR 200)
├── sector (VARCHAR 100)
├── market_cap (DECIMAL)
├── financial_metrics (JSONB)
└── last_updated (TIMESTAMP)
```

## 📁 Project Structure

```
ALFIE/
├── README.md                          # Project documentation
├── ABOUT.md                           # This file
├── requirements.txt                   # Python dependencies
├── runtime.txt                        # Python version
├── index.html                         # Main dashboard entry
│
├── config/                            # Configuration files
│   ├── api_config.js                  # API configuration
│   ├── db_config.py                   # Database settings
│   └── fred_db_manager.py             # FRED data manager
│
├── src/                               # Source code
│   ├── django_api/                    # Django backend
│   │   ├── manage.py                  # Django management
│   │   ├── django_api/                # Core Django project
│   │   │   ├── settings.py            # Project settings
│   │   │   ├── urls.py                # URL routing
│   │   │   └── wsgi.py                # WSGI config
│   │   │
│   │   ├── fred_us/                   # US FRED indicators
│   │   │   ├── models.py              # Data models
│   │   │   ├── views.py               # API endpoints
│   │   │   ├── serializers.py         # Data serialization
│   │   │   └── data_fetcher.py        # FRED API client
│   │   │
│   │   ├── fred_jp/                   # Japan FRED indicators
│   │   ├── bea/                       # BEA data integration
│   │   ├── csi300/                    # CSI300 companies
│   │   ├── stocks/                    # Stock market data
│   │   ├── policy_updates/            # Federal Register
│   │   ├── content/                   # CMS features
│   │   └── indicators/                # Generic indicators
│   │
│   ├── assets/                        # Frontend assets
│   │   ├── css/base/main.css          # Styles
│   │   └── js/
│   │       ├── core/                  # Core JS modules
│   │       ├── utils/                 # Utilities
│   │       └── components/            # UI components
│   │
│   └── pages/                         # HTML pages
│
├── csi300-app/                        # CSI300 Standalone App
│   ├── package.json                   # Node dependencies
│   ├── vite.config.ts                 # Vite configuration
│   ├── src/                           # React source
│   │   ├── pages/                     # Page components
│   │   ├── components/                # Reusable components
│   │   └── shared/                    # Shared utilities
│   └── dist/                          # Build output
│
├── api/                               # Serverless API
│   ├── health.py                      # Health check
│   └── indicators.py                  # Indicator endpoints
│
├── aws-deployment/                    # AWS deployment
│   ├── scripts/                       # Deployment scripts
│   ├── cloudformation/                # IaC templates
│   └── frontend/                      # Frontend config
│
├── tests/                             # Test suite
│   ├── test_api.py                    # API tests
│   └── test_models.py                 # Model tests
│
├── visualization/                     # Analysis tools
│   ├── analyze_complexity.py          # Code analysis
│   ├── draw_architecture.py           # Architecture diagrams
│   └── audit_report.html              # Technical audit
│
└── data/                              # Data files
```

## 🚀 Quick Start

### Prerequisites
- Python 3.13 or higher
- PostgreSQL 12 or higher
- Node.js 18+ (for CSI300 React app)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/PickleLoumal/ALFIE.git
cd ALFIE
```

#### 2. Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Configure Database
```bash
# Create PostgreSQL database
createdb mem_dashboard

# Copy and configure database settings
cp config/db_config.py.example config/db_config.py
# Edit db_config.py with your database credentials
```

#### 4. Run Django Migrations
```bash
cd src/django_api
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

#### 5. Start Development Server
```bash
# Start Django backend (from src/django_api/)
python manage.py runserver 8001

# In another terminal, serve frontend
cd ../..
python -m http.server 8000
```

#### 6. Access the Application
- **Dashboard**: http://localhost:8000/
- **API Root**: http://localhost:8001/api/
- **Django Admin**: http://localhost:8001/admin/

### CSI300 React App Setup (Optional)
```bash
cd csi300-app
npm install
npm run dev  # Development server on http://localhost:5173
npm run build  # Production build
```

## 📡 API Endpoints

### Core Endpoints

#### Health Check
```
GET /api/health/
Response: {"status": "healthy", "timestamp": "2025-12-05T00:00:00Z"}
```

#### FRED US Indicators
```
GET /api/fred-us/indicators/
GET /api/fred-us/indicators/{id}/
GET /api/fred-us/series/{series_id}/latest/
GET /api/fred-us/series/{series_id}/historical/
```

#### BEA Indicators
```
GET /api/bea/indicators/
GET /api/bea/indicators/{id}/
GET /api/bea/gdp/components/
```

#### Stock Data
```
GET /api/stocks/data/
GET /api/stocks/data/{symbol}/
GET /api/stocks/quotes/realtime/
```

#### CSI300 Companies
```
GET /api/csi300/api/companies/
GET /api/csi300/api/companies/{id}/
GET /api/csi300/api/companies/filter_options/
GET /api/csi300/api/companies/search/
```

#### Policy Updates
```
GET /api/policy-updates/
GET /api/policy-updates/{id}/
```

### API Documentation
- **Swagger UI**: http://localhost:8001/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8001/api/schema/redoc/
- **OpenAPI Schema**: http://localhost:8001/api/schema/

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_NAME=mem_dashboard
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# API Keys
FRED_API_KEY=your-fred-api-key
BEA_API_KEY=your-bea-api-key

# AWS (for production)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

### Database Configuration
Edit `config/db_config.py`:
```python
DB_CONFIG = {
    'dbname': 'mem_dashboard',
    'user': 'postgres',
    'password': 'your-password',
    'host': 'localhost',
    'port': 5432
}
```

## 🏢 Deployment

### Docker Deployment
```bash
# Build Docker image
docker build -t alfie-dashboard .

# Run container
docker run -p 8000:8000 -e DATABASE_URL=postgresql://... alfie-dashboard
```

### AWS ECS Deployment
```bash
cd aws-deployment/scripts
./deploy-to-ecs.sh
```

The deployment includes:
- ECS Task Definition with container specifications
- Application Load Balancer for traffic distribution
- RDS PostgreSQL instance for production database
- CloudWatch logs for monitoring
- Auto-scaling configuration

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/django_api

# Run specific test file
pytest tests/test_api.py

# Run Django tests
cd src/django_api
python manage.py test
```

### Linting and Code Quality
```bash
# Python linting
flake8 src/
black src/  # Code formatting

# JavaScript linting (CSI300 app)
cd csi300-app
npm run lint
npm run format
```

## 📈 Data Management

### Fetching Economic Data
```bash
cd src/django_api

# Fetch latest FRED data
python manage.py update_fred_data

# Fetch BEA data
python bea_management.py fetch_all

# Update stock data
python manage.py update_stock_data
```

### Database Maintenance
```bash
# Create database backup
pg_dump mem_dashboard > backup_$(date +%Y%m%d).sql

# Restore from backup
psql mem_dashboard < backup_20251205.sql

# Optimize database
python manage.py sqlsequencereset fred_us bea stocks | python manage.py dbshell
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style Guidelines
- **Python**: Follow PEP 8, use Black for formatting
- **JavaScript**: Follow Airbnb style guide, use Prettier
- **TypeScript**: Use strict mode, document complex types
- **Git Commits**: Use conventional commits format

### Project Conventions
- Use meaningful variable and function names
- Document complex business logic
- Write unit tests for new features
- Update API documentation when adding endpoints
- Keep database migrations reversible

## 📊 Database Statistics

### Current Data Volume
- **Total Tables**: 12 core tables + 8 Django system tables
- **FRED US Indicators**: ~2,000+ data points across 9+ major series
- **FRED JP Indicators**: ~500+ data points
- **BEA Indicators**: ~500+ data points across multiple datasets
- **Stock Data**: Real-time quotes and historical data
- **CSI300 Companies**: 300 companies with financial metrics
- **Time Range**: Historical data from 1990s to present
- **Update Frequency**: Real-time via scheduled API synchronization

## 🔐 Security

### Security Features
- CSRF protection enabled
- SQL injection prevention via ORM
- XSS protection with Django templates
- CORS configuration for API access
- Environment variable management for secrets
- Sentry integration for error monitoring

### Security Best Practices
- Never commit API keys or secrets
- Use environment variables for configuration
- Keep dependencies updated
- Regular security audits with tools
- Monitor logs for suspicious activity

## 📝 License

This project is licensed under the **Educational Research License**.

### Usage Terms
- ✅ Free for educational and research purposes
- ✅ Open source collaboration welcome
- ✅ Academic citation appreciated
- ❌ Commercial use requires written permission
- ❌ Redistribution must retain original license

## 📞 Contact & Support

### Project Maintainer
- **Organization**: MEM Family Office Technology Division
- **Repository**: [PickleLoumal/ALFIE](https://github.com/PickleLoumal/ALFIE)
- **Documentation**: See README.md for detailed guides

### Getting Help
- 📖 **Documentation**: Check README.md and inline code comments
- 🐛 **Bug Reports**: Open an issue on GitHub
- 💡 **Feature Requests**: Submit an issue with [Feature Request] tag
- 💬 **Discussions**: Use GitHub Discussions for questions

## 🎓 Academic Use

### Citation
If you use ALFIE in academic research, please cite:
```bibtex
@software{alfie2025,
  title={ALFIE: Advanced Logistics for Financial Information & Economics},
  author={MEM Family Office},
  year={2025},
  url={https://github.com/PickleLoumal/ALFIE}
}
```

## 🗺️ Roadmap

### Completed Features ✅
- Multi-region economic data integration (US, Japan, China)
- Real-time FRED and BEA API integration
- PostgreSQL database with advanced indexing
- Django REST API with comprehensive endpoints
- Responsive web dashboard
- Stock market data integration (AkShare)
- CSI300 standalone React application
- AWS ECS deployment support
- Federal Register policy updates
- Technical audit and visualization tools

### Upcoming Features 🚀
- [ ] Real-time WebSocket data streaming
- [ ] Advanced charting and technical analysis
- [ ] Machine learning predictive models
- [ ] Multi-language support (i18n)
- [ ] Mobile native applications
- [ ] Enhanced data export capabilities
- [ ] User authentication and portfolios
- [ ] Customizable alert system
- [ ] API rate limiting and throttling
- [ ] GraphQL API alternative

## 🙏 Acknowledgments

### Data Sources
- **Federal Reserve Economic Data (FRED)** - St. Louis Federal Reserve
- **Bureau of Economic Analysis (BEA)** - U.S. Department of Commerce
- **AkShare** - Chinese financial data library
- **Federal Register** - U.S. Government Publishing Office

### Technology Credits
- Django Software Foundation
- PostgreSQL Global Development Group
- React Core Team
- All open source contributors

---

**Last Updated**: December 2025  
**Version**: 1.0.0  
**Status**: Active Development  
**ALFIE Technology Division** • Generated with care for the developer community
