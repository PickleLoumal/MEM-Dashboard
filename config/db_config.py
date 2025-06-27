"""
DEPRECATED: This file is largely obsolete and has been replaced by fred_db_manager.py

Database Configuration for MEM Dashboard
⚠️  WARNING: Most functionality has been moved to config/fred_db_manager.py
⚠️  Only basic database configuration remains for backward compatibility

For all economic indicators functionality, use:
    from config.fred_db_manager import fred_db_manager
"""

import os

# Basic database configuration - used by fred_db_manager.py
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'mem_dashboard'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

# Connection pool settings
CONNECTION_POOL_CONFIG = {
    'min_connections': int(os.getenv('DB_MIN_CONNECTIONS', '1')),
    'max_connections': int(os.getenv('DB_MAX_CONNECTIONS', '10'))
}

# Legacy compatibility - redirect to fred_db_manager
try:
    from .fred_db_manager import fred_db_manager
    
    # Backward compatibility aliases
    db_config = fred_db_manager
    debt_manager = fred_db_manager  # debt functionality is now in fred_db_manager
    
    print("⚠️  DEPRECATION WARNING: db_config.py is deprecated. Use fred_db_manager instead.")
    
except ImportError:
    print("❌ ERROR: fred_db_manager not available. Please check your configuration.")
    db_config = None
    debt_manager = None
