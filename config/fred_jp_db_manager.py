#!/usr/bin/env python3
"""
日本FRED数据库管理器
基于美国FRED管理器，专用于管理日本经济指标数据
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


class JapanFREDDatabaseManager:
    """日本FRED数据库管理器"""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'mem_dashboard'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
        # 日本经济指标配置
        self.indicators_config = {
            'JPNCCPIALLMINMEI': {'name': 'Japan CPI All Items', 'type': 'inflation', 'unit': 'Index', 'freq': 'monthly'},
            'JPNGDPDEFAISMEI': {'name': 'Japan GDP Deflator', 'type': 'economic_growth', 'unit': 'Index', 'freq': 'quarterly'},
            'LRUN64TTJPQ156S': {'name': 'Japan Unemployment Rate', 'type': 'labor_market', 'unit': 'Percent', 'freq': 'monthly'},
            'INTDSRJPM193N': {'name': 'Japan Interest Rate', 'type': 'monetary_policy', 'unit': 'Percent', 'freq': 'monthly'},
            'XTEXVA01JPM667S': {'name': 'Japan Exports', 'type': 'trade', 'unit': 'Million USD', 'freq': 'monthly'},
            'XTIMVA01JPM667S': {'name': 'Japan Imports', 'type': 'trade', 'unit': 'Million USD', 'freq': 'monthly'},
            'POPTOTJPA647NWDB': {'name': 'Japan Population', 'type': 'demographics', 'unit': 'Persons', 'freq': 'annual'},
            'BPBLTT01JPQ188S': {'name': 'Japan Trade Balance', 'type': 'trade', 'unit': 'Million USD', 'freq': 'quarterly'},
            'JPNMABMM101IXNB': {'name': 'Japan Money Supply M2', 'type': 'monetary_policy', 'unit': 'Billion Yen', 'freq': 'monthly'}
        }
        
        # 表名配置
        self.table_names = {
            'indicators': 'fred_jp_indicators',
            'series_info': 'fred_jp_series_info'
        }
    
    def get_connection(self):
        """获取数据库连接"""
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("psycopg2 not available")
        
        try:
            conn = psycopg2.connect(**self.db_config)  # type: ignore
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        if not PSYCOPG2_AVAILABLE:
            return False
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def create_tables(self) -> bool:
        """创建日本FRED相关表"""
        if not PSYCOPG2_AVAILABLE:
            logger.error("Cannot create tables - psycopg2 not available")
            return False
        
        schema_file = os.path.join(os.path.dirname(__file__), 'fred_jp_schema.sql')
        
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(schema_sql)
                    conn.commit()
                    logger.info("Japan FRED tables created successfully")
                    return True
                    
        except FileNotFoundError:
            logger.error(f"Schema file not found: {schema_file}")
            return False
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False
    
    def insert_indicator_data(self, series_id: str, data_points: List[Dict]) -> bool:
        """插入指标数据到数据库"""
        if not PSYCOPG2_AVAILABLE:
            logger.error("Cannot insert data - psycopg2 not available")
            return False
        
        if not data_points:
            logger.warning(f"No data points provided for {series_id}")
            return True
        
        indicator_config = self.indicators_config.get(series_id)
        if not indicator_config:
            logger.warning(f"Unknown series_id: {series_id}")
            return False
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    insert_sql = f"""
                    INSERT INTO {self.table_names['indicators']} 
                    (series_id, indicator_name, indicator_type, date, value, unit, frequency, source, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (series_id, date) DO UPDATE SET
                        value = EXCLUDED.value,
                        updated_at = CURRENT_TIMESTAMP,
                        metadata = EXCLUDED.metadata
                    """
                    
                    for point in data_points:
                        cur.execute(insert_sql, (
                            series_id,
                            indicator_config['name'],
                            indicator_config['type'],
                            point['date'],
                            point['value'],
                            indicator_config['unit'],
                            indicator_config['freq'],
                            'FRED',
                            point.get('metadata', {})
                        ))
                    
                    conn.commit()
                    logger.info(f"Inserted {len(data_points)} data points for {series_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to insert data for {series_id}: {e}")
            return False
    
    def get_latest_data(self, series_id: str) -> Optional[Dict]:
        """获取指定系列的最新数据"""
        if not PSYCOPG2_AVAILABLE:
            return None
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = f"""
                    SELECT * FROM {self.table_names['indicators']}
                    WHERE series_id = %s
                    ORDER BY date DESC
                    LIMIT 1
                    """
                    cur.execute(query, (series_id,))
                    result = cur.fetchone()
                    return dict(result) if result else None
                    
        except Exception as e:
            logger.error(f"Failed to get latest data for {series_id}: {e}")
            return None
    
    def get_historical_data(self, series_id: str, limit: int = 100) -> List[Dict]:
        """获取指定系列的历史数据"""
        if not PSYCOPG2_AVAILABLE:
            return []
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = f"""
                    SELECT * FROM {self.table_names['indicators']}
                    WHERE series_id = %s
                    ORDER BY date DESC
                    LIMIT %s
                    """
                    cur.execute(query, (series_id, limit))
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            logger.error(f"Failed to get historical data for {series_id}: {e}")
            return []
    
    def get_all_series(self) -> List[Dict]:
        """获取所有系列信息"""
        if not PSYCOPG2_AVAILABLE:
            return []
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = f"SELECT * FROM {self.table_names['series_info']} ORDER BY series_id"
                    cur.execute(query)
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            logger.error(f"Failed to get series info: {e}")
            return []
    
    def update_series_info(self, series_id: str, metadata: Dict) -> bool:
        """更新系列信息"""
        if not PSYCOPG2_AVAILABLE:
            return False
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    update_sql = f"""
                    UPDATE {self.table_names['series_info']}
                    SET title = %s, category = %s, units = %s, 
                        frequency = %s, notes = %s, last_updated = CURRENT_TIMESTAMP
                    WHERE series_id = %s
                    """
                    cur.execute(update_sql, (
                        metadata.get('title', ''),
                        metadata.get('category', ''),
                        metadata.get('units', ''),
                        metadata.get('frequency', ''),
                        metadata.get('notes', ''),
                        series_id
                    ))
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to update series info for {series_id}: {e}")
            return False
    
    def get_database_status(self) -> Dict:
        """获取数据库状态信息"""
        status = {
            'connected': False,
            'psycopg2_available': PSYCOPG2_AVAILABLE,
            'tables_exist': False,
            'series_count': 0,
            'total_records': 0,
            'last_updated': None
        }
        
        if not PSYCOPG2_AVAILABLE:
            return status
        
        try:
            status['connected'] = self.test_connection()
            
            if status['connected']:
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        # 检查表是否存在
                        cur.execute("""
                            SELECT COUNT(*) FROM information_schema.tables 
                            WHERE table_name IN (%s, %s)
                        """, (self.table_names['indicators'], self.table_names['series_info']))
                        
                        table_count = cur.fetchone()[0]
                        status['tables_exist'] = table_count == 2
                        
                        if status['tables_exist']:
                            # 获取系列数量
                            cur.execute(f"SELECT COUNT(DISTINCT series_id) FROM {self.table_names['indicators']}")
                            status['series_count'] = cur.fetchone()[0]
                            
                            # 获取总记录数
                            cur.execute(f"SELECT COUNT(*) FROM {self.table_names['indicators']}")
                            status['total_records'] = cur.fetchone()[0]
                            
                            # 获取最后更新时间
                            cur.execute(f"SELECT MAX(updated_at) FROM {self.table_names['indicators']}")
                            last_updated = cur.fetchone()[0]
                            if last_updated:
                                status['last_updated'] = last_updated.isoformat()
                        
        except Exception as e:
            logger.error(f"Failed to get database status: {e}")
        
        return status


# 模块级别的实用函数
def get_japan_db_manager() -> JapanFREDDatabaseManager:
    """获取日本FRED数据库管理器实例"""
    return JapanFREDDatabaseManager()


def test_japan_database_connection() -> bool:
    """测试日本数据库连接"""
    manager = get_japan_db_manager()
    return manager.test_connection()


if __name__ == "__main__":
    # 测试脚本
    manager = get_japan_db_manager()
    status = manager.get_database_status()
    
    print("Japan FRED Database Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    if not status['tables_exist'] and status['connected']:
        print("\nCreating tables...")
        if manager.create_tables():
            print("Tables created successfully")
        else:
            print("Failed to create tables")
