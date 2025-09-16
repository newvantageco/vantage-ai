"""
Snowflake integration for data exports.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd

try:
    import snowflake.connector
    from snowflake.connector.pandas_tools import write_pandas
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    snowflake = None

logger = logging.getLogger(__name__)


class SnowflakeExporter:
    """Export data to Snowflake."""
    
    def __init__(self, credentials: Dict[str, Any]):
        if not SNOWFLAKE_AVAILABLE:
            raise ImportError("Snowflake connector not available. Install with: pip install snowflake-connector-python")
        
        self.credentials = credentials
        self.connection = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Snowflake connection."""
        try:
            self.connection = snowflake.connector.connect(
                user=self.credentials['user'],
                password=self.credentials['password'],
                account=self.credentials['account'],
                warehouse=self.credentials.get('warehouse'),
                database=self.credentials.get('database'),
                schema=self.credentials.get('schema', 'PUBLIC'),
                role=self.credentials.get('role')
            )
            logger.info("Snowflake connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Snowflake connection: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Snowflake connection."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()
            cursor.close()
            
            logger.info(f"Snowflake connection test successful. Version: {version[0] if version else 'Unknown'}")
            return True
            
        except Exception as e:
            logger.error(f"Snowflake connection test failed: {e}")
            return False
    
    def create_database(self, database_name: str) -> bool:
        """Create a Snowflake database if it doesn't exist."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            cursor.close()
            
            logger.info(f"Snowflake database {database_name} created or already exists")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Snowflake database {database_name}: {e}")
            return False
    
    def create_schema(self, database_name: str, schema_name: str) -> bool:
        """Create a Snowflake schema if it doesn't exist."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {database_name}.{schema_name}")
            cursor.close()
            
            logger.info(f"Snowflake schema {database_name}.{schema_name} created or already exists")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Snowflake schema {database_name}.{schema_name}: {e}")
            return False
    
    def export_table(self, 
                    database_name: str,
                    schema_name: str,
                    table_name: str, 
                    data: List[Dict[str, Any]], 
                    schema: Dict[str, str],
                    write_mode: str = "replace") -> bool:
        """Export data to a Snowflake table."""
        try:
            if not data:
                logger.warning(f"No data to export for table {table_name}")
                return True
            
            # Create database and schema if they don't exist
            if not self.create_database(database_name):
                return False
            
            if not self.create_schema(database_name, schema_name):
                return False
            
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            
            # Convert datetime columns
            for column, dtype in schema.items():
                if dtype == "datetime" and column in df.columns:
                    df[column] = pd.to_datetime(df[column], errors='coerce')
                elif dtype == "date" and column in df.columns:
                    df[column] = pd.to_datetime(df[column], errors='coerce').dt.date
            
            # Create table name
            full_table_name = f"{database_name}.{schema_name}.{table_name}"
            
            # Export data
            success, nchunks, nrows, _ = write_pandas(
                self.connection,
                df,
                table_name=full_table_name,
                database=database_name,
                schema=schema_name,
                auto_create_table=True,
                overwrite=(write_mode == "replace")
            )
            
            if success:
                logger.info(f"Successfully exported {nrows} rows to Snowflake table {full_table_name}")
                return True
            else:
                logger.error(f"Failed to export data to Snowflake table {full_table_name}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to export data to Snowflake table {table_name}: {e}")
            return False
    
    def get_table_info(self, database_name: str, schema_name: str, table_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a Snowflake table."""
        try:
            cursor = self.connection.cursor()
            
            # Get table information
            cursor.execute(f"""
                SELECT 
                    TABLE_NAME,
                    ROW_COUNT,
                    BYTES,
                    CREATED,
                    LAST_ALTERED
                FROM {database_name}.INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = '{schema_name}' 
                AND TABLE_NAME = '{table_name}'
            """)
            
            table_info = cursor.fetchone()
            
            if not table_info:
                cursor.close()
                return None
            
            # Get column information
            cursor.execute(f"""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT
                FROM {database_name}.INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = '{schema_name}' 
                AND TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            cursor.close()
            
            return {
                "table_name": table_info[0],
                "row_count": table_info[1],
                "bytes": table_info[2],
                "created": table_info[3].isoformat() if table_info[3] else None,
                "last_altered": table_info[4].isoformat() if table_info[4] else None,
                "columns": [
                    {
                        "name": col[0],
                        "type": col[1],
                        "nullable": col[2] == "YES",
                        "default": col[3]
                    }
                    for col in columns
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get table info for {database_name}.{schema_name}.{table_name}: {e}")
            return None
    
    def delete_table(self, database_name: str, schema_name: str, table_name: str) -> bool:
        """Delete a Snowflake table."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {database_name}.{schema_name}.{table_name}")
            cursor.close()
            
            logger.info(f"Deleted Snowflake table {database_name}.{schema_name}.{table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Snowflake table {database_name}.{schema_name}.{table_name}: {e}")
            return False
    
    def list_tables(self, database_name: str, schema_name: str) -> List[str]:
        """List tables in a schema."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                SELECT TABLE_NAME 
                FROM {database_name}.INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = '{schema_name}'
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            return tables
            
        except Exception as e:
            logger.error(f"Failed to list tables in {database_name}.{schema_name}: {e}")
            return []
    
    def query_data(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch all rows
            rows = cursor.fetchall()
            cursor.close()
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to execute Snowflake query: {e}")
            return []
    
    def close(self):
        """Close the Snowflake connection."""
        if self.connection:
            self.connection.close()
            logger.info("Snowflake connection closed")


def create_snowflake_exporter(credentials: Dict[str, Any]) -> SnowflakeExporter:
    """Create a Snowflake exporter instance."""
    return SnowflakeExporter(credentials)


def validate_snowflake_credentials(credentials: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Snowflake credentials and return validation result."""
    try:
        exporter = SnowflakeExporter(credentials)
        is_valid = exporter.test_connection()
        
        # Get account info
        cursor = exporter.connection.cursor()
        cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
        account_info = cursor.fetchone()
        cursor.close()
        
        exporter.close()
        
        return {
            "valid": is_valid,
            "message": "Connection successful" if is_valid else "Connection failed",
            "details": {
                "account": account_info[0] if account_info else "Unknown",
                "database": account_info[1] if account_info else "Unknown",
                "schema": account_info[2] if account_info else "Unknown"
            }
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation failed: {str(e)}",
            "details": {}
        }
