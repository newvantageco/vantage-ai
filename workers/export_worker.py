"""
Export worker for processing data warehouse exports.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List
import asyncio

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.exports import ExportJob, ExportStatus, ExportTarget, EXPORT_TABLES
from app.models.content import Schedule
from app.models.post_metrics import PostMetrics
from app.models.conversations import Conversation
from app.models.entities import Organization

logger = logging.getLogger(__name__)


async def process_export_job(job_id: str):
    """Process an export job."""
    db = next(get_db())
    
    try:
        # Get the export job
        export_job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
        if not export_job:
            logger.error(f"Export job {job_id} not found")
            return
        
        # Update status to running
        export_job.status = ExportStatus.running
        export_job.started_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Starting export job {job_id} for target {export_job.target}")
        
        # Get target configuration
        target_config = export_job.get_target_config()
        tables = export_job.get_tables()
        
        # Process each table
        total_records = 0
        exported_records = 0
        
        for i, table_name in enumerate(tables):
            try:
                export_job.current_table = table_name
                export_job.progress_percent = int((i / len(tables)) * 100)
                db.commit()
                
                logger.info(f"Exporting table {table_name}")
                
                # Get table data
                table_data = await get_table_data(table_name, export_job.org_id, db)
                total_records += len(table_data)
                
                if not table_data:
                    logger.warning(f"No data found for table {table_name}")
                    continue
                
                # Export to target
                success = await export_to_target(
                    export_job.target,
                    target_config,
                    table_name,
                    table_data,
                    EXPORT_TABLES[table_name]["schema"]
                )
                
                if success:
                    exported_records += len(table_data)
                    logger.info(f"Successfully exported {len(table_data)} records from {table_name}")
                else:
                    logger.error(f"Failed to export table {table_name}")
                    export_job.status = ExportStatus.failed
                    export_job.error_message = f"Failed to export table {table_name}"
                    break
                
            except Exception as e:
                logger.error(f"Error exporting table {table_name}: {e}")
                export_job.status = ExportStatus.failed
                export_job.error_message = f"Error exporting table {table_name}: {str(e)}"
                break
        
        # Update final status
        if export_job.status == ExportStatus.running:
            export_job.status = ExportStatus.completed
            export_job.progress_percent = 100
            export_job.records_exported = exported_records
            export_job.total_records = total_records
            export_job.finished_at = datetime.utcnow()
            
            logger.info(f"Export job {job_id} completed successfully. Exported {exported_records}/{total_records} records")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error processing export job {job_id}: {e}")
        
        # Update job status to failed
        export_job.status = ExportStatus.failed
        export_job.error_message = str(e)
        export_job.finished_at = datetime.utcnow()
        db.commit()
        
    finally:
        db.close()


async def get_table_data(table_name: str, org_id: str, db: Session) -> List[Dict[str, Any]]:
    """Get data for a specific table."""
    try:
        if table_name == "schedules":
            return await get_schedules_data(org_id, db)
        elif table_name == "post_metrics":
            return await get_post_metrics_data(org_id, db)
        elif table_name == "conversations":
            return await get_conversations_data(org_id, db)
        elif table_name == "ad_metrics":
            return await get_ad_metrics_data(org_id, db)
        else:
            logger.error(f"Unknown table: {table_name}")
            return []
    
    except Exception as e:
        logger.error(f"Error getting data for table {table_name}: {e}")
        return []


async def get_schedules_data(org_id: str, db: Session) -> List[Dict[str, Any]]:
    """Get schedules data for export."""
    schedules = db.query(Schedule).filter(Schedule.org_id == org_id).all()
    
    data = []
    for schedule in schedules:
        data.append({
            "id": schedule.id,
            "org_id": schedule.org_id,
            "content_item_id": schedule.content_item_id,
            "channel_id": schedule.channel_id,
            "scheduled_at": schedule.scheduled_at.isoformat() if schedule.scheduled_at else None,
            "status": schedule.status.value if schedule.status else None,
            "error_message": schedule.error_message,
            "created_at": schedule.created_at.isoformat() if schedule.created_at else None
        })
    
    return data


async def get_post_metrics_data(org_id: str, db: Session) -> List[Dict[str, Any]]:
    """Get post metrics data for export."""
    # Get metrics for schedules belonging to the org
    metrics = db.query(PostMetrics).join(Schedule).filter(Schedule.org_id == org_id).all()
    
    data = []
    for metric in metrics:
        data.append({
            "id": metric.id,
            "schedule_id": metric.schedule_id,
            "impressions": metric.impressions,
            "reach": metric.reach,
            "likes": metric.likes,
            "comments": metric.comments,
            "shares": metric.shares,
            "clicks": metric.clicks,
            "video_views": metric.video_views,
            "saves": metric.saves,
            "cost_cents": metric.cost_cents,
            "fetched_at": metric.fetched_at.isoformat() if metric.fetched_at else None,
            "created_at": metric.created_at.isoformat() if metric.created_at else None
        })
    
    return data


async def get_conversations_data(org_id: str, db: Session) -> List[Dict[str, Any]]:
    """Get conversations data for export."""
    # This would need to be implemented based on your conversations model
    # For now, return empty list
    return []


async def get_ad_metrics_data(org_id: str, db: Session) -> List[Dict[str, Any]]:
    """Get ad metrics data for export."""
    # This would need to be implemented based on your ad metrics model
    # For now, return empty list
    return []


async def export_to_target(
    target: ExportTarget,
    target_config: Dict[str, Any],
    table_name: str,
    data: List[Dict[str, Any]],
    schema: Dict[str, str]
) -> bool:
    """Export data to the specified target."""
    try:
        if target == ExportTarget.bigquery:
            return await export_to_bigquery(target_config, table_name, data, schema)
        elif target == ExportTarget.snowflake:
            return await export_to_snowflake(target_config, table_name, data, schema)
        elif target == ExportTarget.s3:
            return await export_to_s3(target_config, table_name, data, schema)
        elif target == ExportTarget.csv:
            return await export_to_csv(target_config, table_name, data, schema)
        else:
            logger.error(f"Unknown export target: {target}")
            return False
    
    except Exception as e:
        logger.error(f"Error exporting to {target}: {e}")
        return False


async def export_to_bigquery(
    target_config: Dict[str, Any],
    table_name: str,
    data: List[Dict[str, Any]],
    schema: Dict[str, str]
) -> bool:
    """Export data to BigQuery."""
    try:
        from app.integrations.bigquery import create_bigquery_exporter
        
        exporter = create_bigquery_exporter(target_config)
        
        dataset_id = target_config.get("dataset_id", "vantage_ai")
        success = exporter.export_table(dataset_id, table_name, data, schema)
        
        return success
    
    except Exception as e:
        logger.error(f"Error exporting to BigQuery: {e}")
        return False


async def export_to_snowflake(
    target_config: Dict[str, Any],
    table_name: str,
    data: List[Dict[str, Any]],
    schema: Dict[str, str]
) -> bool:
    """Export data to Snowflake."""
    try:
        from app.integrations.snowflake import create_snowflake_exporter
        
        exporter = create_snowflake_exporter(target_config)
        
        database_name = target_config.get("database", "VANTAGE_AI")
        schema_name = target_config.get("schema", "PUBLIC")
        
        success = exporter.export_table(database_name, schema_name, table_name, data, schema)
        exporter.close()
        
        return success
    
    except Exception as e:
        logger.error(f"Error exporting to Snowflake: {e}")
        return False


async def export_to_s3(
    target_config: Dict[str, Any],
    table_name: str,
    data: List[Dict[str, Any]],
    schema: Dict[str, str]
) -> bool:
    """Export data to S3."""
    try:
        import boto3
        import pandas as pd
        import io
        
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=target_config["access_key_id"],
            aws_secret_access_key=target_config["secret_access_key"],
            region_name=target_config["region"]
        )
        
        # Convert data to CSV
        df = pd.DataFrame(data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        
        # Upload to S3
        bucket = target_config["bucket"]
        key = f"exports/{table_name}/{datetime.utcnow().strftime('%Y/%m/%d')}/{table_name}.csv"
        
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )
        
        logger.info(f"Successfully uploaded {table_name} to S3: s3://{bucket}/{key}")
        return True
    
    except Exception as e:
        logger.error(f"Error exporting to S3: {e}")
        return False


async def export_to_csv(
    target_config: Dict[str, Any],
    table_name: str,
    data: List[Dict[str, Any]],
    schema: Dict[str, str]
) -> bool:
    """Export data to CSV file."""
    try:
        import pandas as pd
        import os
        
        # Create output directory
        output_dir = target_config.get("output_dir", "/tmp/exports")
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert data to CSV
        df = pd.DataFrame(data)
        file_path = os.path.join(output_dir, f"{table_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv")
        df.to_csv(file_path, index=False)
        
        logger.info(f"Successfully exported {table_name} to CSV: {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return False


if __name__ == "__main__":
    # This can be run as a standalone worker
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python export_worker.py <job_id>")
        sys.exit(1)
    
    job_id = sys.argv[1]
    asyncio.run(process_export_job(job_id))
