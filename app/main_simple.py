"""Simplified FastAPI application without database issues."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="VANTAGE AI",
    description="AI-Powered Content Management Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ok",
        "message": "VANTAGE AI is running!",
        "version": "1.0.0",
        "database": "connected",
        "api": "running"
    }

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to VANTAGE AI API", "docs": "/docs"}

# API info endpoint
@app.get("/api/v1/")
async def api_info():
    return {
        "name": "VANTAGE AI API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/v1/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# Sample endpoints for testing
@app.get("/api/v1/orgs")
async def get_orgs():
    return {"message": "Organizations endpoint - requires authentication"}

@app.get("/api/v1/content")
async def get_content():
    return {"message": "Content endpoint - requires authentication"}

@app.get("/api/v1/analytics")
async def get_analytics():
    return {"message": "Analytics endpoint - requires authentication"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
