"""
Events API endpoints for real-time event streaming
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json
import time
from datetime import datetime

router = APIRouter()

@router.get("/stream")
async def stream_events():
    """
    Server-Sent Events endpoint for real-time event streaming
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate server-sent events"""
        try:
            # Send a limited number of events to prevent resource exhaustion
            max_events = 100  # Limit to prevent infinite resource consumption
            event_count = 0
            
            while event_count < max_events:
                # Generate a sample event
                event_data = {
                    "id": f"event_{int(time.time())}_{event_count}",
                    "timestamp": datetime.now().isoformat(),
                    "type": "info",
                    "category": "system",
                    "title": "System Status",
                    "description": "System is running normally",
                    "source": "vantage-ai",
                    "severity": "low"
                }
                
                # Send the event as SSE
                yield f"data: {json.dumps(event_data)}\n\n"
                
                event_count += 1
                
                # Wait before sending the next event (reduced from 5 to 2 seconds)
                await asyncio.sleep(2)
                
        except asyncio.CancelledError:
            # Client disconnected
            pass
        except Exception as e:
            # Send error event
            error_event = {
                "id": f"error_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "category": "system",
                "title": "Connection Error",
                "description": str(e),
                "source": "vantage-ai",
                "severity": "high"
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@router.get("/")
async def get_events():
    """
    Get recent events
    """
    return {
        "events": [
            {
                "id": "event_1",
                "timestamp": datetime.now().isoformat(),
                "type": "info",
                "category": "system",
                "title": "System Started",
                "description": "VANTAGE AI system is running",
                "source": "vantage-ai",
                "severity": "low"
            }
        ],
        "total": 1
    }
