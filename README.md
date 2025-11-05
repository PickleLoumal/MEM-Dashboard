# MEM Dashboard - Macroeconomic Indicator Platform

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://postgresql.org)


> A comprehensive web-based dashboard for monitoring and analyzing macroeconomic indicators, featuring real-time data visualization, PostgreSQL database integration, and Django REST Framework.

## Features

- **Real-time Economic Data**: Live updates from FRED and BEA APIs
- **Interactive Dashboard**: Dynamic visualization with responsive design  
- **PostgreSQL Integration**: Persistent data storage and fast queries
- **Django REST API**: Robust backend with comprehensive endpoints
- **Multi-indicator Support**: GDP, CPI, Unemployment, Housing, Money Supply
- **Cloud Deployment**: AWS ECS deployment with Docker

## Database Architecture

### **Database Configuration**
- **Database**: PostgreSQL 12+
- **Name**: `mem_dashboard`
- **Connection**: Django ORM + psycopg2
- **Host**: `localhost:5432` (configurable via environment variables)

### **Database Schema Overview**

```
+------------------+    +------------------+    +------------------+
|  FRED Tables     |    |  BEA Tables      |    |  Django Tables   |
+------------------+    +------------------+    +------------------+
| fred_indicators  |    | bea_indicators   |    | auth_user        |
| fred_series_info |    | bea_series_info  |    | django_sessions  |
|                  |    | bea_indicator_   |    | django_migrations|
|                  |    | configs          |    | django_admin_log |
+------------------+    +------------------+    +------------------+
         |                        |                        |
         |                        |                        |
         +------------------------+------------------------+
                                  |
                         +------------------+
                         | Legacy Tables    |
                         +------------------+
                         | debt_to_gdp      |
                         | economic_        |
                         | indicators       |
                         +------------------+
```

### **Core Database Tables**

#### **1. FRED Economic Indicators (`fred_indicators`)**
```sql
Table Structure:
- id (SERIAL PRIMARY KEY)
- series_id (VARCHAR(50)) - FRED Series ID (M2SL, UNRATE, etc.)
- indicator_name (VARCHAR(200)) - Human readable name
- indicator_type (VARCHAR(50)) - Category (monetary, employment, etc.)
- date (DATE) - Data date
- value (DECIMAL(15,4)) - Indicator value
- source (VARCHAR(100)) - Data source (FRED)
- unit (VARCHAR(50)) - Measurement unit
- frequency (VARCHAR(20)) - Data frequency (monthly, quarterly)
- metadata (JSONB) - Additional metadata
- created_at, updated_at (TIMESTAMP)

Indexes:
- idx_fred_indicators_series_date (series_id, date DESC)
- idx_fred_indicators_type_date (indicator_type, date DESC)
- UNIQUE constraint on (series_id, date)
```

#### **2. BEA Economic Indicators (`bea_indicators`)**
```sql
Table Structure:
- id (SERIAL PRIMARY KEY)
- series_id (VARCHAR(50)) - BEA Series ID
- indicator_name (VARCHAR(200)) - Human readable name
- indicator_type (VARCHAR(50)) - Category type
- table_name (VARCHAR(50)) - BEA table reference
- line_number (VARCHAR(10)) - BEA line reference
- date (DATE) - Data date
- time_period (VARCHAR(10)) - BEA time format (2025Q1)
- value (DECIMAL(15,4)) - Indicator value
- source (VARCHAR(100)) - Data source (BEA)
- unit (VARCHAR(50)) - Measurement unit
- frequency (VARCHAR(20)) - Data frequency
- dataset_name (VARCHAR(50)) - BEA dataset name
- metadata (JSONB) - Additional metadata
- created_at, updated_at (TIMESTAMP)

Indexes:
- idx_bea_indicators_series_date (series_id, date DESC)
- idx_bea_indicators_table (table_name, line_number)
- UNIQUE constraint on (series_id, time_period)
```

#### **3. BEA Dynamic Configuration (`bea_indicator_configs`)**
```sql
Table Structure:
- series_id (VARCHAR(50) PRIMARY KEY) - Unique BEA series ID
- name (VARCHAR(200)) - Configuration name
- description (TEXT) - Detailed description
- table_name (VARCHAR(50)) - BEA table reference
- line_description (VARCHAR(500)) - BEA line description for matching
- line_number (INTEGER) - BEA line number
- units (VARCHAR(100)) - Measurement units
- frequency (VARCHAR(20)) - Data frequency
- years (VARCHAR(100)) - Year range configuration
- category (VARCHAR(100)) - Indicator category
- fallback_value (DECIMAL(15,4)) - Default fallback value
- api_endpoint (VARCHAR(100) UNIQUE) - API endpoint path
- priority (INTEGER) - Processing priority
- is_active (BOOLEAN) - Enable/disable indicator
- auto_fetch (BOOLEAN) - Automatic data fetching
- dataset_name (VARCHAR(50)) - BEA dataset name
- additional_config (JSONB) - Extended JSON configuration
- created_at, updated_at (TIMESTAMP)
- created_by, updated_by (VARCHAR(100)) - Audit fields
```

#### **4. Series Information Tables**
```sql
fred_series_info:
- series_id (VARCHAR(50) PRIMARY KEY)
- title (VARCHAR(200)) - Official FRED title
- category (VARCHAR(100)) - FRED category
- units (VARCHAR(50)) - Measurement units
- frequency (VARCHAR(20)) - Data frequency
- seasonal_adjustment (VARCHAR(50)) - Seasonal adjustment info
- notes (TEXT) - Additional notes
- last_updated (TIMESTAMP)

bea_series_info:
- series_id (VARCHAR(50) PRIMARY KEY)
- title (VARCHAR(200)) - Official BEA title
- category (VARCHAR(100)) - BEA category
- table_name (VARCHAR(50)) - BEA table reference
- line_number, line_description - BEA line info
- units, frequency, dataset_name - Data specifications
- notes (TEXT), last_updated (TIMESTAMP)
```

### **Data Sources & Coverage**

#### **FRED API Integration**
- **M2 Money Stock** (`M2SL`) - Monthly, Seasonally Adjusted
- **M1 Money Stock** (`M1SL`) - Monthly, Seasonally Adjusted  
- **M2 Velocity** (`M2V`) - Quarterly, Seasonally Adjusted
- **Monetary Base** (`BOGMBASE`) - Monthly, Seasonally Adjusted
- **Federal Debt to GDP** (`GFDEGDQ188S`) - Quarterly
- **Consumer Price Index** (`CPIAUCSL`) - Monthly
- **Unemployment Rate** (`UNRATE`) - Monthly
- **Housing Starts** (`HOUST`) - Monthly
- **Federal Funds Rate** (`FEDFUNDS`) - Monthly

#### **BEA API Integration**
- **GDP Components** - Quarterly National Accounts
- **Consumer Spending** - Monthly Personal Consumption
- **Business Investment** - Quarterly Fixed Assets
- **Government Spending** - Quarterly Government Accounts
- **Trade Balance** - Monthly International Trade

### **Database Performance**
- **Indexed Queries**: All major query patterns are indexed
- **JSONB Metadata**: Flexible metadata storage with query support
- **Unique Constraints**: Prevent duplicate data entries
- **Timestamp Tracking**: Full audit trail for all data changes

## Database Statistics

### **Current Data Volume**
- **Total Tables**: 12 (4 core economic, 8 Django system tables)
- **FRED Indicators**: ~2,000+ data points across 9 major series
- **BEA Indicators**: ~500+ data points across multiple datasets  
- **Time Range**: Historical data from 1990s to present
- **Update Frequency**: Real-time via API synchronization

## System Architecture

```
+-----------------------------------------------------------------------+
|                         MEM Dashboard System                          |
|                  Macroeconomic Indicator Platform                     |
+-----------------------------------------------------------------------+

+----------------+    HTTP/REST API    +-----------------+    SQL    +----------------+
|                | <-----------------> |                 | <-------> |                |
| Frontend Layer |                     | Backend Layer   |           | Database Layer |
|                |                     |                 |           |                |
| HTML/CSS/JS    |                     | Django API      |           | PostgreSQL     |
|                |                     |                 |           |                |
| - Dashboard UI |                     | - REST Endpoints|           | - FRED Tables  |
| - Data Viz     |                     | - Data Process  |           | - BEA Tables   |
| - User Input   |                     | - Business Logic|           | - Indicators   |
| - API Client   |                     | - Admin Panel   |           | - Metadata     |
+----------------+                     +------------—----+           +----------------+
         |                                      |
         |                                      |
         |               +----------------------------------+
         |               |        External APIs             |
         |               |                                  |
         +---------------+ - FRED API (Federal Reserve)     |
                         | - BEA API  (Bureau of Analysis)  |
                         |                                  |
                         | - Real-time Indicators           |
                         | - Historical Data                |
                         | - Data Synchronization           |
                         +----------------------------------+

+-----------------------------------------------------------------------+
|                         Technology Stack                              |
+----------------+----------------+----------------+--------------------+
|  Frontend Tech |  Backend Tech  | Database Tech  | Deployment Tech    |
+----------------+----------------+----------------+--------------------+
| - HTML5/CSS3   | - Django 4.2.7 | - PostgreSQL   | - AWS ECS          |
| - JavaScript   | - Django REST  | - psycopg2     | - Docker           |
| - Tailwind CSS | - Python 3.13  | - Migrations   | - CloudFormation   |
| - Responsive   | - CORS Support | - Indexing     | - Shell Scripts    |
+----------------+----------------+----------------+--------------------+
```

## Project Structure

```
MEM Dashboard/
├── Frontend Entry
│   ├── index.html                          # Main dashboard page
│   └── src/pages/index.html                # Page components
│
├── Project Configuration
│   ├── .env.example                        # Environment variables template
│   ├── .gitignore                          # Git ignore rules
│   ├── requirements.txt                    # Python dependencies
│   ├── runtime.txt                         # Python runtime version
│   ├── pyrightconfig.json                  # Python type checking config
│   └── README.md                           # Project documentation
│
├── API Configuration (config/)
│   ├── api_config.js                       # Main API config (Django)
│   ├── api_config_django_only.js           # Django-only configuration
│   ├── db_config.py                        # Database configuration
│   └── fred_db_manager.py                  # FRED database manager
│
├── Django API (src/django_api/)
│   ├── manage.py                           # Django management script
│   ├── bea_management.py                   # BEA management tool
│   ├── django_requirements.txt             # Django dependencies
│   │
│   ├── django_api/                         # Django project config
│   │   ├── __init__.py                     # Initialization file
│   │   ├── settings.py                     # Settings file
│   │   ├── urls.py                         # Main URL routing
│   │   ├── views.py                        # API overview views
│   │   ├── wsgi.py                         # WSGI configuration
│   │   └── asgi.py                         # ASGI configuration
│   │
│   ├── fred/                               # FRED data module
│   │   ├── __init__.py                     # Initialization file
│   │   ├── models.py                       # FRED data models
│   │   ├── views.py                        # FRED API views
│   │   ├── urls.py                         # FRED routing
│   │   ├── serializers.py                  # Data serialization
│   │   ├── admin.py                        # Admin configuration
│   │   ├── apps.py                         # App configuration
│   │   ├── tests.py                        # Unit tests
│   │   └── migrations/
│   │       ├── __init__.py                 # Migration initialization
│   │       └── 0001_initial.py             # Initial migration
│   │
│   ├── bea/                                # BEA data module
│   │   ├── __init__.py                     # Initialization file
│   │   ├── models.py                       # BEA data models
│   │   ├── views.py                        # BEA API views
│   │   ├── urls.py                         # BEA routing
│   │   ├── serializers.py                  # Data serialization
│   │   ├── admin.py                        # Admin configuration
│   │   ├── apps.py                         # App configuration
│   │   ├── dynamic_config.py               # Dynamic config management
│   │   └── indicator_processor.py          # Indicator processor
│   │
│   └── indicators/                         # Indicator management module
│       ├── __init__.py                     # Initialization file
│       ├── models.py                       # Generic indicator models
│       ├── views.py                        # Indicator API views
│       ├── urls.py                         # Indicator routing
│       ├── admin.py                        # Admin configuration
│       ├── apps.py                         # App configuration
│       ├── tests.py                        # Unit tests
│       └── migrations/
│           └── __init__.py                 # Migration initialization
│
├── Frontend Assets (src/assets/)
│   ├── css/base/
│   │   └── main.css                        # Main stylesheet
│   │
│   └── js/
│       ├── core/                           # JavaScript core modules
│       │   ├── main-dashboard.js           # Main dashboard logic
│       │   ├── dashboard-init.js           # Initialization script
│       │   └── navigation.js               # Navigation control
│       │
│       ├── utils/                          # Utility library
│       │   ├── api_client.js               # API client
│       │   └── money_supply_fix.js         # Money supply fix
│       │
│       └── components/                     # UI components
│           ├── exchange-rate-manager.js    # Exchange rate manager
│           ├── exchange-rate-display.js    # Exchange rate display component
│           └── generic-pagination.js       # Generic pagination component
│
└── Serverless API (api/)
    ├── health.py                           # Health check endpoint
    └── indicators.py                       # Indicator data endpoint
```

## File Statistics

### **Total Project Files**: 60

- **Python Files**: 39 (Django apps, configurations, API endpoints)
- **JavaScript Files**: 10 (core modules, utilities, UI components)  
- **Frontend Files**: 3 (HTML pages, CSS stylesheets)
- **Configuration Files**: 6 (project config, environment, documentation)
- **Other Files**: 2 (README.md, .gitignore)

## Quick Start

### Prerequisites
- Python 3.13+
- PostgreSQL 12+
- Modern web browser

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure database
cp config/db_config.py.example config/db_config.py

# Run Django migrations
cd src/django_api
python manage.py migrate

# Start development server
python manage.py runserver 8001
```

### Deployment
```bash
# Deploy to AWS ECS
cd aws-deployment/scripts
./deploy-to-ecs.sh
```

## API Endpoints

### Core Endpoints
- `/api/health` - System health check
- `/api/fred/` - FRED economic indicators
- `/api/bea/` - BEA economic data
- `/api/indicators/` - Generic indicator management

### Django Admin
- `/admin/` - Django admin panel for data management

## Tech Stack

- **Backend**: Django 4.2.7, Django REST Framework, Python 3.13
- **Database**: PostgreSQL with psycopg2
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **Deployment**: AWS ECS with Docker
- **APIs**: FRED API, BEA API integration

---

## Testing Linear Integration

This section is added to test Linear and GitHub synchronization (JJJ-24).

- Branch: `jjj-24-alternative-data-source`
- Purpose: Verify Linear issue tracking integration
- Date: 2025-11-05

---

**License**: Educational Research License  
**Last Updated**: June 2025
