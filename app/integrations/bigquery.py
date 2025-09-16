"""
BigQuery integration for data exports.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    bigquery = None
    service_account = None

logger = logging.getLogger(__name__)


class BigQueryExporter:
    """Export data to BigQuery."""
    
    def __init__(self, credentials: Dict[str, Any]):
        if not BIGQUERY_AVAILABLE:
            raise ImportError("BigQuery client not available. Install with: pip install google-cloud-bigquery")
        
        self.credentials = credentials
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize BigQuery client with credentials."""
        try:
            if 'service_account_info' in self.credentials:
                # Use service account JSON
                credentials = service_account.Credentials.from_service_account_info(
                    self.credentials['service_account_info']
                )
            elif 'service_account_file' in self.credentials:
                # Use service account file path
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials['service_account_file']
                )
            else:
                # Use default credentials
                credentials = None
            
            self.client = bigquery.Client(credentials=credentials)
            logger.info("BigQuery client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test BigQuery connection."""
        try:
            # Try to list datasets
            datasets = list(self.client.list_datasets(max_results=1))
            logger.info("BigQuery connection test successful")
            return True
        except Exception as e:
            logger.error(f"BigQuery connection test failed: {e}")
            return False
    
    def create_dataset(self, dataset_id: str, location: str = "US") -> bool:
        """Create a BigQuery dataset if it doesn't exist."""
        try:
            dataset_ref = self.client.dataset(dataset_id)
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = location
            dataset.description = f"Vantage AI export dataset created on {datetime.utcnow().isoformat()}"
            
            dataset = self.client.create_dataset(dataset, exists_ok=True)
            logger.info(f"BigQuery dataset {dataset_id} created or already exists")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create BigQuery dataset {dataset_id}: {e}")
            return False
    
    def export_table(self, 
                    dataset_id: str, 
                    table_id: str, 
                    data: List[Dict[str, Any]], 
                    schema: Dict[str, str],
                    write_disposition: str = "WRITE_TRUNCATE") -> bool:
        """Export data to a BigQuery table."""
        try:
            if not data:
                logger.warning(f"No data to export for table {table_id}")
                return True
            
            # Create dataset if it doesn't exist
            if not self.create_dataset(dataset_id):
                return False
            
            # Convert schema to BigQuery format
            bq_schema = self._convert_schema(schema)
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Convert datetime columns
            for column, dtype in schema.items():
                if dtype == "datetime" and column in df.columns:
                    df[column] = pd.to_datetime(df[column], errors='coerce')
                elif dtype == "date" and column in df.columns:
                    df[column] = pd.to_datetime(df[column], errors='coerce').dt.date
            
            # Define table reference
            table_ref = self.client.dataset(dataset_id).table(table_id)
            
            # Configure job
            job_config = bigquery.LoadJobConfig(
                schema=bq_schema,
                write_disposition=write_disposition,
                create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED
            )
            
            # Load data
            job = self.client.load_table_from_dataframe(
                df, table_ref, job_config=job_config
            )
            
            # Wait for job to complete
            job.result()
            
            logger.info(f"Successfully exported {len(data)} rows to BigQuery table {dataset_id}.{table_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export data to BigQuery table {table_id}: {e}")
            return False
    
    def _convert_schema(self, schema: Dict[str, str]) -> List[bigquery.SchemaField]:
        """Convert internal schema to BigQuery schema format."""
        type_mapping = {
            "string": bigquery.SqlTypeNames.STRING,
            "integer": bigquery.SqlTypeNames.INTEGER,
            "float": bigquery.SqlTypeNames.FLOAT,
            "boolean": bigquery.SqlTypeNames.BOOLEAN,
            "datetime": bigquery.SqlTypeNames.TIMESTAMP,
            "date": bigquery.SqlTypeNames.DATE,
            "json": bigquery.SqlTypeNames.JSON
        }
        
        bq_schema = []
        for field_name, field_type in schema.items():
            bq_type = type_mapping.get(field_type, bigquery.SqlTypeNames.STRING)
            bq_schema.append(bigquery.SchemaField(field_name, bq_type))
        
        return bq_schema
    
    def get_table_info(self, dataset_id: str, table_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a BigQuery table."""
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            table = self.client.get_table(table_ref)
            
            return {
                "table_id": table.table_id,
                "dataset_id": table.dataset_id,
                "project_id": table.project,
                "num_rows": table.num_rows,
                "num_bytes": table.num_bytes,
                "created": table.created.isoformat() if table.created else None,
                "modified": table.modified.isoformat() if table.modified else None,
                "schema": [
                    {
                        "name": field.name,
                        "type": field.field_type,
                        "mode": field.mode
                    }
                    for field in table.schema
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get table info for {dataset_id}.{table_id}: {e}")
            return None
    
    def delete_table(self, dataset_id: str, table_id: str) -> bool:
        """Delete a BigQuery table."""
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            self.client.delete_table(table_ref, not_found_ok=True)
            logger.info(f"Deleted BigQuery table {dataset_id}.{table_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete BigQuery table {dataset_id}.{table_id}: {e}")
            return False
    
    def list_tables(self, dataset_id: str) -> List[str]:
        """List tables in a dataset."""
        try:
            dataset_ref = self.client.dataset(dataset_id)
            tables = list(self.client.list_tables(dataset_ref))
            return [table.table_id for table in tables]
            
        except Exception as e:
            logger.error(f"Failed to list tables in dataset {dataset_id}: {e}")
            return []
    
    def query_data(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results."""
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            data = []
            for row in results:
                data.append(dict(row))
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to execute BigQuery query: {e}")
            return []


def create_bigquery_exporter(credentials: Dict[str, Any]) -> BigQueryExporter:
    """Create a BigQuery exporter instance."""
    return BigQueryExporter(credentials)


def validate_bigquery_credentials(credentials: Dict[str, Any]) -> Dict[str, Any]:
    """Validate BigQuery credentials and return validation result."""
    try:
        exporter = BigQueryExporter(credentials)
        is_valid = exporter.test_connection()
        
        return {
            "valid": is_valid,
            "message": "Connection successful" if is_valid else "Connection failed",
            "details": {
                "project_id": credentials.get("project_id", "Unknown"),
                "dataset_id": credentials.get("dataset_id", "Unknown")
            }
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation failed: {str(e)}",
            "details": {}
        }
