#!/usr/bin/env python3
"""
统一的FRED数据库管理器
合并debt-to-gdp和universal_indicators功能,支持所有经济指标
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    psycopg2 = None  # type: ignore
    RealDictCursor = None  # type: ignore
    PSYCOPG2_AVAILABLE = False
    logger.warning("psycopg2 not available - database features will be disabled")

class FREDDatabaseManager:
    """统一的FRED数据库管理器"""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'mem_dashboard'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
        # 支持的经济指标配置
        self.indicators_config = {
            'M2SL': {'name': 'M2 Money Stock', 'type': 'monetary', 'unit': 'Billions', 'freq': 'monthly'},
            'M1SL': {'name': 'M1 Money Stock', 'type': 'monetary', 'unit': 'Billions', 'freq': 'monthly'},
            'M2V': {'name': 'Velocity of M2 Money Stock', 'type': 'monetary', 'unit': 'Ratio', 'freq': 'quarterly'},
            'BOGMBASE': {'name': 'Monetary Base', 'type': 'monetary', 'unit': 'Billions', 'freq': 'monthly'},
            'GFDEGDQ188S': {'name': 'Federal Debt to GDP Ratio', 'type': 'fiscal', 'unit': 'Percent', 'freq': 'quarterly'},
            'CPIAUCSL': {'name': 'Consumer Price Index', 'type': 'prices', 'unit': 'Index', 'freq': 'monthly'},
            'UNRATE': {'name': 'Unemployment Rate', 'type': 'employment', 'unit': 'Percent', 'freq': 'monthly'},
            'HOUST': {'name': 'Housing Starts', 'type': 'housing', 'unit': 'Thousands', 'freq': 'monthly'},
            'FEDFUNDS': {'name': 'Federal Funds Rate', 'type': 'monetary', 'unit': 'Percent', 'freq': 'monthly'},
            # Consumer and Household Debt Indicators
            'HDTGPDUSQ163N': {'name': 'Household Debt to GDP for United States', 'type': 'debt', 'unit': 'Ratio', 'freq': 'quarterly'},
            'TDSP': {'name': 'Household Debt Service Payments as a Percent of Disposable Personal Income', 'type': 'debt', 'unit': 'Percent', 'freq': 'quarterly'},
            'MDOAH': {'name': 'Mortgage Debt Outstanding, All holders (DISCONTINUED)', 'type': 'debt', 'unit': 'Millions of Dollars', 'freq': 'quarterly'},
            'RCCCBBALTOT': {'name': 'Large Bank Consumer Credit Card Balances: Total Balances', 'type': 'debt', 'unit': 'Billions of U.S. Dollars', 'freq': 'quarterly'},
            'SLOASM': {'name': 'Student Loans Owned and Securitized', 'type': 'debt', 'unit': 'Millions of U.S. Dollars', 'freq': 'monthly'},
            'TOTALSL': {'name': 'Total Consumer Credit Outstanding', 'type': 'debt', 'unit': 'Millions of Dollars', 'freq': 'monthly'},
            'DTCOLNVHFNM': {'name': 'Household Debt: Total', 'type': 'debt', 'unit': 'Millions of Dollars', 'freq': 'monthly'}
        }
        
        self.connection_available = False
        self._test_connection()
    
    def _test_connection(self):
        """测试数据库连接"""
        if not PSYCOPG2_AVAILABLE:
            self.connection_available = False
            logger.warning("psycopg2不可用, 数据库功能将被禁用")
            return
            
        try:
            conn = self.get_connection()
            if conn:
                conn.close()
                self.connection_available = True
                logger.info("数据库连接测试成功")
            else:
                self.connection_available = False
                logger.warning("数据库连接不可用")
        except Exception as e:
            self.connection_available = False
            logger.error(f"数据库连接测试失败: {e}")
    
    def get_connection(self):
        """获取数据库连接"""
        if not PSYCOPG2_AVAILABLE or psycopg2 is None:
            logger.error("psycopg2不可用, 无法连接数据库")
            return None
            
        try:
            connection = psycopg2.connect(**self.db_config)
            return connection
        except Exception as e:
            logger.error(f"数据库连接错误: {e}")
            return None
    
    def initialize_tables(self):
        """初始化统一的FRED数据库表"""
        if not self.connection_available:
            logger.error("数据库不可用，无法初始化表")
            return False
        
        connection = self.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # 创建统一的fred_indicators表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fred_indicators (
                    id SERIAL PRIMARY KEY,
                    series_id VARCHAR(50) NOT NULL,
                    indicator_name VARCHAR(200) NOT NULL,
                    indicator_type VARCHAR(50) NOT NULL,
                    date DATE NOT NULL,
                    value DECIMAL(15, 4) NOT NULL,
                    source VARCHAR(100) NOT NULL DEFAULT 'FRED',
                    unit VARCHAR(50),
                    frequency VARCHAR(20),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(series_id, date)
                );
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fred_indicators_series_date 
                ON fred_indicators(series_id, date DESC);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fred_indicators_type_date 
                ON fred_indicators(indicator_type, date DESC);
            """)
            
            # 创建series_info表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fred_series_info (
                    series_id VARCHAR(50) PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    category VARCHAR(100),
                    units VARCHAR(50),
                    frequency VARCHAR(20),
                    seasonal_adjustment VARCHAR(50),
                    notes TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # 插入指标元信息
            for series_id, config in self.indicators_config.items():
                cursor.execute("""
                    INSERT INTO fred_series_info 
                    (series_id, title, category, units, frequency) 
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (series_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        category = EXCLUDED.category,
                        units = EXCLUDED.units,
                        frequency = EXCLUDED.frequency,
                        last_updated = CURRENT_TIMESTAMP;
                """, (series_id, config['name'], config['type'], config['unit'], config['freq']))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logger.info("FRED数据库表初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"数据库表初始化失败: {e}")
            connection.rollback()
            connection.close()
            return False
    
    def store_indicator_data(self, series_id: str, observations: List[Dict]):
        """存储指标数据到数据库"""
        if not self.connection_available:
            logger.warning(f"数据库不可用，跳过存储 {series_id}")
            return False
        
        if series_id not in self.indicators_config:
            logger.error(f"不支持的指标: {series_id}")
            return False
        
        connection = self.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            config = self.indicators_config[series_id]
            stored_count = 0
            
            for obs in observations:
                if obs.get('value') and obs.get('value') != '.':
                    try:
                        cursor.execute("""
                            INSERT INTO fred_indicators 
                            (series_id, indicator_name, indicator_type, date, value, unit, frequency)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (series_id, date) DO UPDATE SET
                                value = EXCLUDED.value,
                                updated_at = CURRENT_TIMESTAMP;
                        """, (
                            series_id,
                            config['name'],
                            config['type'],
                            obs['date'],
                            float(obs['value']),
                            config['unit'],
                            config['freq']
                        ))
                        stored_count += 1
                    except (ValueError, KeyError) as e:
                        logger.warning(f"跳过无效数据点 {series_id}: {e}")
                        continue
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logger.info(f"成功存储 {stored_count} 条 {series_id} 数据")
            return True
            
        except Exception as e:
            logger.error(f"存储 {series_id} 数据失败: {e}")
            connection.rollback()
            connection.close()
            return False
    
    def get_indicator_data(self, series_id: str, limit: int = 100) -> Optional[List[Dict]]:
        """从数据库获取指标数据"""
        if not self.connection_available:
            return None
        
        connection = self.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT date, value, indicator_name, indicator_type, unit, frequency, created_at
                FROM fred_indicators 
                WHERE series_id = %s
                ORDER BY date DESC 
                LIMIT %s
            """, (series_id, limit))
            
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            
            if rows:
                observations = []
                for row in rows:
                    observations.append({
                        'date': row[0].isoformat(),
                        'value': str(row[1]),
                        'indicator_name': row[2],
                        'indicator_type': row[3],
                        'unit': row[4],
                        'frequency': row[5],
                        'created_at': row[6].isoformat() if row[6] else None
                    })
                
                return observations
            
            return None
            
        except Exception as e:
            logger.error(f"获取 {series_id} 数据失败: {e}")
            connection.close()
            return None
    
    def get_latest_value(self, series_id: str) -> Optional[Dict]:
        """获取指标的最新值"""
        data = self.get_indicator_data(series_id, limit=1)
        if data and len(data) > 0:
            return data[0]
        return None
    
    def get_database_status(self) -> Dict:
        """获取数据库状态"""
        if not self.connection_available:
            return {
                'database_available': False,
                'connection_status': 'failed',
                'indicators_count': 0,
                'supported_indicators': list(self.indicators_config.keys())
            }
        
        connection = self.get_connection()
        if not connection:
            return {
                'database_available': False,
                'connection_status': 'failed',
                'indicators_count': 0,
                'supported_indicators': list(self.indicators_config.keys())
            }
        
        try:
            cursor = connection.cursor()
            
            # 获取每个指标的记录数
            cursor.execute("""
                SELECT series_id, COUNT(*) as count, MAX(date) as latest_date
                FROM fred_indicators 
                GROUP BY series_id
                ORDER BY series_id
            """)
            
            indicators_status = {}
            total_records = 0
            
            for row in cursor.fetchall():
                series_id, count, latest_date = row
                indicators_status[series_id] = {
                    'records': count,
                    'latest_date': latest_date.isoformat() if latest_date else None
                }
                total_records += count
            
            cursor.close()
            connection.close()
            
            return {
                'database_available': True,
                'connection_status': 'connected',
                'total_records': total_records,
                'indicators_count': len(indicators_status),
                'indicators_status': indicators_status,
                'supported_indicators': list(self.indicators_config.keys())
            }
            
        except Exception as e:
            logger.error(f"获取数据库状态失败: {e}")
            connection.close()
            return {
                'database_available': False,
                'connection_status': 'error',
                'error': str(e),
                'supported_indicators': list(self.indicators_config.keys())
            }


# 全局实例
fred_db_manager = FREDDatabaseManager()
