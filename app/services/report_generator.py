"""
Custom Report Generator Service
Handles dynamic report generation with various formats and templates
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
import json
import csv
import io
from fastapi.responses import StreamingResponse
from jinja2 import Template
import logging

from app.models.analytics import PostMetrics, AnalyticsSummary
from app.models.publishing import ExternalReference, PublishingStatus
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Service for generating custom analytics reports"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)
    
    def generate_report(
        self,
        org_id: int,
        report_config: Dict[str, Any],
        format: str = "json"
    ) -> Union[Dict[str, Any], StreamingResponse]:
        """
        Generate a custom report based on configuration
        
        Args:
            org_id: Organization ID
            report_config: Report configuration
            format: Output format (json, csv, html, pdf)
            
        Returns:
            Report data or streaming response
        """
        try:
            # Parse report configuration
            date_range = report_config.get("date_range", {})
            start_date = datetime.fromisoformat(date_range.get("start_date"))
            end_date = datetime.fromisoformat(date_range.get("end_date"))
            
            platforms = report_config.get("platforms", [])
            metrics = report_config.get("metrics", [])
            filters = report_config.get("filters", {})
            group_by = report_config.get("group_by", "day")
            
            # Generate report data
            report_data = self._generate_report_data(
                org_id=org_id,
                start_date=start_date,
                end_date=end_date,
                platforms=platforms,
                metrics=metrics,
                filters=filters,
                group_by=group_by
            )
            
            # Format output based on requested format
            if format == "json":
                return report_data
            elif format == "csv":
                return self._generate_csv_response(report_data, report_config)
            elif format == "html":
                return self._generate_html_response(report_data, report_config)
            elif format == "pdf":
                return self._generate_pdf_response(report_data, report_config)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    def _generate_report_data(
        self,
        org_id: int,
        start_date: datetime,
        end_date: datetime,
        platforms: List[str],
        metrics: List[str],
        filters: Dict[str, Any],
        group_by: str
    ) -> Dict[str, Any]:
        """Generate the actual report data"""
        
        # Base query for post metrics
        query = self.db.query(PostMetrics).filter(
            PostMetrics.organization_id == org_id,
            PostMetrics.metric_date >= start_date,
            PostMetrics.metric_date <= end_date
        )
        
        # Apply platform filter
        if platforms:
            query = query.filter(PostMetrics.platform.in_(platforms))
        
        # Apply additional filters
        if filters.get("min_impressions"):
            query = query.filter(PostMetrics.impressions >= filters["min_impressions"])
        
        if filters.get("min_engagement_rate"):
            query = query.filter(PostMetrics.engagement_rate >= filters["min_engagement_rate"])
        
        if filters.get("data_source"):
            query = query.filter(PostMetrics.data_source == filters["data_source"])
        
        # Get all metrics
        all_metrics = query.all()
        
        if not all_metrics:
            return {
                "report_info": {
                    "org_id": org_id,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "platforms": platforms,
                    "metrics": metrics,
                    "total_posts": 0
                },
                "summary": {},
                "timeseries_data": [],
                "platform_breakdown": {},
                "top_content": []
            }
        
        # Calculate summary metrics
        summary = self._calculate_summary_metrics(all_metrics, metrics)
        
        # Generate timeseries data
        timeseries_data = self._generate_timeseries_data(all_metrics, group_by)
        
        # Generate platform breakdown
        platform_breakdown = self._generate_platform_breakdown(all_metrics)
        
        # Get top performing content
        top_content = self._get_top_content(all_metrics, limit=10)
        
        return {
            "report_info": {
                "org_id": org_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "platforms": platforms,
                "metrics": metrics,
                "total_posts": len(all_metrics),
                "generated_at": datetime.utcnow().isoformat()
            },
            "summary": summary,
            "timeseries_data": timeseries_data,
            "platform_breakdown": platform_breakdown,
            "top_content": top_content
        }
    
    def _calculate_summary_metrics(self, metrics: List[PostMetrics], requested_metrics: List[str]) -> Dict[str, Any]:
        """Calculate summary metrics from the data"""
        if not metrics:
            return {}
        
        summary = {
            "total_posts": len(metrics),
            "total_impressions": sum(m.impressions for m in metrics),
            "total_reach": sum(m.reach for m in metrics),
            "total_clicks": sum(m.clicks for m in metrics),
            "total_engagements": sum(m.engagements for m in metrics),
            "total_conversions": sum(m.conversions for m in metrics),
            "avg_engagement_rate": sum(m.engagement_rate for m in metrics) / len(metrics),
            "avg_ctr": sum(m.ctr for m in metrics) / len(metrics),
            "avg_conversion_rate": sum(m.conversion_rate for m in metrics) / len(metrics)
        }
        
        # Only include requested metrics
        if requested_metrics:
            filtered_summary = {}
            for metric in requested_metrics:
                if metric in summary:
                    filtered_summary[metric] = round(summary[metric], 2)
            return filtered_summary
        
        return {k: round(v, 2) for k, v in summary.items()}
    
    def _generate_timeseries_data(self, metrics: List[PostMetrics], group_by: str) -> List[Dict[str, Any]]:
        """Generate timeseries data grouped by the specified period"""
        if not metrics:
            return []
        
        # Group metrics by date
        grouped_data = {}
        for metric in metrics:
            if group_by == "day":
                date_key = metric.metric_date.date()
            elif group_by == "week":
                # Get Monday of the week
                date_key = metric.metric_date.date() - timedelta(days=metric.metric_date.weekday())
            elif group_by == "month":
                date_key = metric.metric_date.date().replace(day=1)
            else:
                date_key = metric.metric_date.date()
            
            if date_key not in grouped_data:
                grouped_data[date_key] = []
            grouped_data[date_key].append(metric)
        
        # Calculate aggregated metrics for each period
        timeseries_data = []
        for date_key, period_metrics in grouped_data.items():
            period_summary = self._calculate_summary_metrics(period_metrics, [])
            timeseries_data.append({
                "date": date_key.isoformat(),
                "total_posts": period_summary.get("total_posts", 0),
                "total_impressions": period_summary.get("total_impressions", 0),
                "total_engagements": period_summary.get("total_engagements", 0),
                "avg_engagement_rate": period_summary.get("avg_engagement_rate", 0),
                "avg_ctr": period_summary.get("avg_ctr", 0)
            })
        
        return sorted(timeseries_data, key=lambda x: x["date"])
    
    def _generate_platform_breakdown(self, metrics: List[PostMetrics]) -> Dict[str, Any]:
        """Generate platform breakdown data"""
        if not metrics:
            return {}
        
        platform_data = {}
        for metric in metrics:
            platform = metric.platform
            if platform not in platform_data:
                platform_data[platform] = {
                    "posts": 0,
                    "impressions": 0,
                    "reach": 0,
                    "clicks": 0,
                    "engagements": 0,
                    "conversions": 0
                }
            
            platform_data[platform]["posts"] += 1
            platform_data[platform]["impressions"] += metric.impressions
            platform_data[platform]["reach"] += metric.reach
            platform_data[platform]["clicks"] += metric.clicks
            platform_data[platform]["engagements"] += metric.engagements
            platform_data[platform]["conversions"] += metric.conversions
        
        # Calculate averages
        for platform, data in platform_data.items():
            if data["posts"] > 0:
                data["avg_engagement_rate"] = (data["engagements"] / data["reach"] * 100) if data["reach"] > 0 else 0
                data["avg_ctr"] = (data["clicks"] / data["impressions"] * 100) if data["impressions"] > 0 else 0
                data["avg_conversion_rate"] = (data["conversions"] / data["clicks"] * 100) if data["clicks"] > 0 else 0
        
        return platform_data
    
    def _get_top_content(self, metrics: List[PostMetrics], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing content"""
        if not metrics:
            return []
        
        # Sort by engagement rate
        top_metrics = sorted(metrics, key=lambda x: x.engagement_rate, reverse=True)[:limit]
        
        top_content = []
        for metric in top_metrics:
            top_content.append({
                "platform": metric.platform,
                "external_id": metric.external_id,
                "engagement_rate": round(metric.engagement_rate, 2),
                "impressions": metric.impressions,
                "reach": metric.reach,
                "clicks": metric.clicks,
                "engagements": metric.engagements,
                "ctr": round(metric.ctr, 2),
                "conversion_rate": round(metric.conversion_rate, 2),
                "metric_date": metric.metric_date.isoformat()
            })
        
        return top_content
    
    def _generate_csv_response(self, report_data: Dict[str, Any], report_config: Dict[str, Any]) -> StreamingResponse:
        """Generate CSV response"""
        def generate_csv():
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write report info
            writer.writerow(["Report Information"])
            writer.writerow(["Organization ID", report_data["report_info"]["org_id"]])
            writer.writerow(["Start Date", report_data["report_info"]["start_date"]])
            writer.writerow(["End Date", report_data["report_info"]["end_date"]])
            writer.writerow(["Total Posts", report_data["report_info"]["total_posts"]])
            writer.writerow(["Generated At", report_data["report_info"]["generated_at"]])
            writer.writerow([])
            
            # Write summary
            writer.writerow(["Summary Metrics"])
            for key, value in report_data["summary"].items():
                writer.writerow([key, value])
            writer.writerow([])
            
            # Write timeseries data
            writer.writerow(["Timeseries Data"])
            if report_data["timeseries_data"]:
                writer.writerow(["Date", "Total Posts", "Total Impressions", "Total Engagements", "Avg Engagement Rate", "Avg CTR"])
                for data_point in report_data["timeseries_data"]:
                    writer.writerow([
                        data_point["date"],
                        data_point["total_posts"],
                        data_point["total_impressions"],
                        data_point["total_engagements"],
                        data_point["avg_engagement_rate"],
                        data_point["avg_ctr"]
                    ])
            writer.writerow([])
            
            # Write platform breakdown
            writer.writerow(["Platform Breakdown"])
            if report_data["platform_breakdown"]:
                writer.writerow(["Platform", "Posts", "Impressions", "Reach", "Clicks", "Engagements", "Avg Engagement Rate", "Avg CTR"])
                for platform, data in report_data["platform_breakdown"].items():
                    writer.writerow([
                        platform,
                        data["posts"],
                        data["impressions"],
                        data["reach"],
                        data["clicks"],
                        data["engagements"],
                        data.get("avg_engagement_rate", 0),
                        data.get("avg_ctr", 0)
                    ])
            writer.writerow([])
            
            # Write top content
            writer.writerow(["Top Performing Content"])
            if report_data["top_content"]:
                writer.writerow(["Platform", "External ID", "Engagement Rate", "Impressions", "Reach", "Clicks", "Engagements", "CTR", "Conversion Rate", "Date"])
                for content in report_data["top_content"]:
                    writer.writerow([
                        content["platform"],
                        content["external_id"],
                        content["engagement_rate"],
                        content["impressions"],
                        content["reach"],
                        content["clicks"],
                        content["engagements"],
                        content["ctr"],
                        content["conversion_rate"],
                        content["metric_date"]
                    ])
            
            yield output.getvalue()
        
        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=custom_report.csv"}
        )
    
    def _generate_html_response(self, report_data: Dict[str, Any], report_config: Dict[str, Any]) -> StreamingResponse:
        """Generate HTML response"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analytics Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f5f5f5; padding: 20px; border-radius: 5px; }
                .section { margin: 20px 0; }
                .metric { display: inline-block; margin: 10px; padding: 10px; background-color: #e9ecef; border-radius: 3px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Analytics Report</h1>
                <p><strong>Organization ID:</strong> {{ report_info.org_id }}</p>
                <p><strong>Period:</strong> {{ report_info.start_date }} to {{ report_info.end_date }}</p>
                <p><strong>Total Posts:</strong> {{ report_info.total_posts }}</p>
                <p><strong>Generated:</strong> {{ report_info.generated_at }}</p>
            </div>
            
            <div class="section">
                <h2>Summary Metrics</h2>
                {% for key, value in summary.items() %}
                <div class="metric">
                    <strong>{{ key.replace('_', ' ').title() }}:</strong> {{ value }}
                </div>
                {% endfor %}
            </div>
            
            <div class="section">
                <h2>Platform Breakdown</h2>
                <table>
                    <tr>
                        <th>Platform</th>
                        <th>Posts</th>
                        <th>Impressions</th>
                        <th>Reach</th>
                        <th>Clicks</th>
                        <th>Engagements</th>
                        <th>Avg Engagement Rate</th>
                        <th>Avg CTR</th>
                    </tr>
                    {% for platform, data in platform_breakdown.items() %}
                    <tr>
                        <td>{{ platform }}</td>
                        <td>{{ data.posts }}</td>
                        <td>{{ data.impressions }}</td>
                        <td>{{ data.reach }}</td>
                        <td>{{ data.clicks }}</td>
                        <td>{{ data.engagements }}</td>
                        <td>{{ "%.2f"|format(data.get('avg_engagement_rate', 0)) }}%</td>
                        <td>{{ "%.2f"|format(data.get('avg_ctr', 0)) }}%</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="section">
                <h2>Top Performing Content</h2>
                <table>
                    <tr>
                        <th>Platform</th>
                        <th>External ID</th>
                        <th>Engagement Rate</th>
                        <th>Impressions</th>
                        <th>Reach</th>
                        <th>Clicks</th>
                        <th>Engagements</th>
                        <th>CTR</th>
                        <th>Date</th>
                    </tr>
                    {% for content in top_content %}
                    <tr>
                        <td>{{ content.platform }}</td>
                        <td>{{ content.external_id }}</td>
                        <td>{{ "%.2f"|format(content.engagement_rate) }}%</td>
                        <td>{{ content.impressions }}</td>
                        <td>{{ content.reach }}</td>
                        <td>{{ content.clicks }}</td>
                        <td>{{ content.engagements }}</td>
                        <td>{{ "%.2f"|format(content.ctr) }}%</td>
                        <td>{{ content.metric_date }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            report_info=report_data["report_info"],
            summary=report_data["summary"],
            platform_breakdown=report_data["platform_breakdown"],
            top_content=report_data["top_content"]
        )
        
        return StreamingResponse(
            io.BytesIO(html_content.encode()),
            media_type="text/html",
            headers={"Content-Disposition": "attachment; filename=custom_report.html"}
        )
    
    def _generate_pdf_response(self, report_data: Dict[str, Any], report_config: Dict[str, Any]) -> StreamingResponse:
        """Generate PDF response (placeholder - would need a PDF library like reportlab)"""
        # For now, return HTML as PDF
        # In production, you would use a library like reportlab or weasyprint
        html_response = self._generate_html_response(report_data, report_config)
        return html_response
