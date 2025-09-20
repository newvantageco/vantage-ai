"""
Custom Reports API Router
Handles dynamic report generation and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.models.cms import UserAccount
from app.services.report_generator import ReportGenerator

router = APIRouter()


class ReportConfig(BaseModel):
    """Report configuration schema"""
    name: str
    description: Optional[str] = None
    date_range: Dict[str, str]  # {"start_date": "2024-01-01", "end_date": "2024-01-31"}
    platforms: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    group_by: str = "day"  # day, week, month
    format: str = "json"  # json, csv, html, pdf


class ReportTemplate(BaseModel):
    """Report template schema"""
    name: str
    description: str
    config: ReportConfig
    is_public: bool = False


@router.post("/reports/generate")
async def generate_custom_report(
    report_config: ReportConfig,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate a custom analytics report.
    """
    try:
        report_generator = ReportGenerator(db)
        
        # Generate the report
        result = report_generator.generate_report(
            org_id=current_user.organization_id,
            report_config=report_config.dict(),
            format=report_config.format
        )
        
        if isinstance(result, StreamingResponse):
            return {"message": "Report generated successfully", "format": report_config.format}
        else:
            return result
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post("/reports/generate/download")
async def generate_custom_report_download(
    report_config: ReportConfig,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> StreamingResponse:
    """
    Generate and download a custom analytics report.
    """
    try:
        report_generator = ReportGenerator(db)
        
        # Generate the report
        result = report_generator.generate_report(
            org_id=current_user.organization_id,
            report_config=report_config.dict(),
            format=report_config.format
        )
        
        if isinstance(result, StreamingResponse):
            return result
        else:
            # Convert JSON to CSV for download
            report_config.format = "csv"
            result = report_generator.generate_report(
                org_id=current_user.organization_id,
                report_config=report_config.dict(),
                format="csv"
            )
            return result
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/reports/templates")
async def get_report_templates(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get available report templates.
    """
    # Predefined report templates
    templates = [
        {
            "id": "daily_summary",
            "name": "Daily Summary Report",
            "description": "Daily overview of key metrics and performance",
            "config": {
                "date_range": {
                    "start_date": (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d"),
                    "end_date": datetime.utcnow().strftime("%Y-%m-%d")
                },
                "platforms": [],
                "metrics": ["total_impressions", "total_engagements", "avg_engagement_rate", "avg_ctr"],
                "filters": {},
                "group_by": "day",
                "format": "json"
            }
        },
        {
            "id": "weekly_performance",
            "name": "Weekly Performance Report",
            "description": "Weekly performance analysis with trends",
            "config": {
                "date_range": {
                    "start_date": (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    "end_date": datetime.utcnow().strftime("%Y-%m-%d")
                },
                "platforms": [],
                "metrics": ["total_impressions", "total_engagements", "avg_engagement_rate", "avg_ctr", "total_conversions"],
                "filters": {},
                "group_by": "day",
                "format": "json"
            }
        },
        {
            "id": "monthly_analytics",
            "name": "Monthly Analytics Report",
            "description": "Comprehensive monthly analytics with platform breakdown",
            "config": {
                "date_range": {
                    "start_date": (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "end_date": datetime.utcnow().strftime("%Y-%m-%d")
                },
                "platforms": [],
                "metrics": ["total_impressions", "total_engagements", "avg_engagement_rate", "avg_ctr", "total_conversions", "avg_conversion_rate"],
                "filters": {},
                "group_by": "week",
                "format": "json"
            }
        },
        {
            "id": "platform_comparison",
            "name": "Platform Comparison Report",
            "description": "Compare performance across different platforms",
            "config": {
                "date_range": {
                    "start_date": (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "end_date": datetime.utcnow().strftime("%Y-%m-%d")
                },
                "platforms": [],
                "metrics": ["total_impressions", "total_engagements", "avg_engagement_rate", "avg_ctr"],
                "filters": {},
                "group_by": "day",
                "format": "json"
            }
        },
        {
            "id": "top_content_analysis",
            "name": "Top Content Analysis",
            "description": "Analysis of top performing content",
            "config": {
                "date_range": {
                    "start_date": (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "end_date": datetime.utcnow().strftime("%Y-%m-%d")
                },
                "platforms": [],
                "metrics": ["engagement_rate", "impressions", "clicks", "shares"],
                "filters": {"min_impressions": 100},
                "group_by": "day",
                "format": "json"
            }
        }
    ]
    
    return templates


@router.post("/reports/templates/{template_id}/generate")
async def generate_report_from_template(
    template_id: str,
    custom_config: Optional[Dict[str, Any]] = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate a report using a predefined template.
    """
    try:
        # Get template
        templates = await get_report_templates(db, current_user)
        template = next((t for t in templates if t["id"] == template_id), None)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found"
            )
        
        # Use template config as base
        config = template["config"].copy()
        
        # Apply custom overrides
        if custom_config:
            config.update(custom_config)
        
        # Override format if specified
        config["format"] = format
        
        # Generate report
        report_generator = ReportGenerator(db)
        result = report_generator.generate_report(
            org_id=current_user.organization_id,
            report_config=config,
            format=format
        )
        
        if isinstance(result, StreamingResponse):
            return {"message": "Report generated successfully", "format": format}
        else:
            return result
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report from template: {str(e)}"
        )


@router.get("/reports/available-metrics")
async def get_available_metrics(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[Dict[str, str]]:
    """
    Get list of available metrics for report configuration.
    """
    metrics = [
        {"key": "total_posts", "name": "Total Posts", "description": "Total number of posts published"},
        {"key": "total_impressions", "name": "Total Impressions", "description": "Total number of impressions"},
        {"key": "total_reach", "name": "Total Reach", "description": "Total number of unique users reached"},
        {"key": "total_clicks", "name": "Total Clicks", "description": "Total number of clicks"},
        {"key": "total_engagements", "name": "Total Engagements", "description": "Total number of engagements"},
        {"key": "total_conversions", "name": "Total Conversions", "description": "Total number of conversions"},
        {"key": "avg_engagement_rate", "name": "Average Engagement Rate", "description": "Average engagement rate percentage"},
        {"key": "avg_ctr", "name": "Average CTR", "description": "Average click-through rate percentage"},
        {"key": "avg_conversion_rate", "name": "Average Conversion Rate", "description": "Average conversion rate percentage"}
    ]
    
    return metrics


@router.get("/reports/available-platforms")
async def get_available_platforms(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[str]:
    """
    Get list of available platforms for report configuration.
    """
    from app.models.publishing import ExternalReference
    from sqlalchemy import distinct
    
    platforms = db.query(distinct(ExternalReference.platform)).filter(
        ExternalReference.organization_id == current_user.organization_id
    ).all()
    
    return [platform[0] for platform in platforms]


@router.get("/reports/export-formats")
async def get_export_formats() -> List[Dict[str, str]]:
    """
    Get list of available export formats.
    """
    formats = [
        {"key": "json", "name": "JSON", "description": "JSON format for API consumption"},
        {"key": "csv", "name": "CSV", "description": "CSV format for spreadsheet applications"},
        {"key": "html", "name": "HTML", "description": "HTML format for web viewing"},
        {"key": "pdf", "name": "PDF", "description": "PDF format for printing and sharing"}
    ]
    
    return formats
