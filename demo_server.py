#!/usr/bin/env python3
"""
VANTAGE AI Demo Server
A simple working demonstration of the VANTAGE AI platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ok",
        "database": "connected",
        "api": "running",
        "version": "1.0.0"
    }

# AI Content Generation endpoint
@app.post("/api/v1/ai/generate")
async def generate_content(request: dict):
    """Generate AI-powered content"""
    prompt = request.get("prompt", "")
    platform = request.get("platform", "general")
    
    # Mock AI responses based on prompt
    ai_responses = {
        "product launch": "Exciting news! We're thrilled to announce our latest innovation that will revolutionize your workflow. This game-changing feature combines cutting-edge technology with user-friendly design. Ready to experience the future? Try it free today! #Innovation #Tech #ProductLaunch",
        "sale": "Don't miss out! For a limited time, get 50% off our premium features. This exclusive offer won't last long - upgrade now and unlock the full potential of your marketing strategy. Limited time only! #Sale #Deal #Marketing",
        "tips": "Pro tip: Consistency is key in social media marketing. Post regularly, engage with your audience, and always provide value. What's your favorite social media strategy? Share in the comments! #SocialMediaTips #Marketing #Growth",
        "default": "Creating amazing content is an art and a science. With the right strategy, creativity, and consistency, you can build a powerful online presence that resonates with your audience. What story will you tell today? #ContentCreation #Marketing #Strategy"
    }
    
    # Find the best response based on prompt keywords
    prompt_lower = prompt.lower()
    generated_content = ai_responses["default"]
    
    for key, response in ai_responses.items():
        if key in prompt_lower:
            generated_content = response
            break
    
    return {
        "content": generated_content,
        "platform": platform,
        "prompt": prompt,
        "status": "success"
    }

# Content suggestions endpoint
@app.get("/api/v1/ai/suggestions")
async def get_suggestions(platform: str = "general"):
    """Get AI-powered content suggestions"""
    
    suggestions = [
        {
            "title": "Product Feature Highlight",
            "content": "Discover the power of our latest feature! This game-changing update will transform how you work. Try it free today! #Innovation #ProductUpdate",
            "hashtags": ["#Innovation", "#ProductUpdate", "#Tech"],
            "platform": platform
        },
        {
            "title": "Behind the Scenes",
            "content": "Take a peek behind the curtain! Our team is working hard to bring you amazing features. Here's what's coming next... #Team #CompanyCulture #BehindTheScenes",
            "hashtags": ["#Team", "#CompanyCulture", "#BehindTheScenes"],
            "platform": platform
        },
        {
            "title": "Industry Insights",
            "content": "The future of marketing is here! AI-powered tools are revolutionizing how we connect with audiences. What trends are you seeing? #Marketing #AI #Future",
            "hashtags": ["#Marketing", "#AI", "#Future", "#Trends"],
            "platform": platform
        },
        {
            "title": "Customer Success Story",
            "content": "Amazing results from our latest customer! They increased engagement by 300% using our platform. Ready to see similar results? #Success #CustomerStory #Results",
            "hashtags": ["#Success", "#CustomerStory", "#Results"],
            "platform": platform
        },
        {
            "title": "Educational Content",
            "content": "Knowledge is power! Here are 5 proven strategies to boost your social media engagement. Which one will you try first? #Education #Tips #SocialMedia",
            "hashtags": ["#Education", "#Tips", "#SocialMedia", "#Growth"],
            "platform": platform
        }
    ]
    
    return {
        "suggestions": suggestions,
        "platform": platform,
        "status": "success"
    }

# Dashboard data endpoint
@app.get("/api/v1/dashboard")
async def get_dashboard():
    """Get dashboard overview data"""
    return {
        "overview": {
            "total_posts": 156,
            "total_organizations": 12,
            "total_channels": 8,
            "recent_activity": "24 posts scheduled"
        },
        "analytics": {
            "metrics": {
                "total_posts": 156,
                "engagement_rate": "12.5%",
                "reach": 12500,
                "total_clicks": 3420
            },
            "trends": {
                "posts_this_week": 23,
                "engagement_up": "+15%",
                "reach_up": "+8%"
            }
        },
        "recent_posts": [
            {
                "id": 1,
                "content": "Creating amazing content is an art and a science...",
                "platform": "LinkedIn",
                "status": "published",
                "engagement": 45
            },
            {
                "id": 2,
                "content": "Pro tip: Consistency is key in social media marketing...",
                "platform": "Twitter",
                "status": "scheduled",
                "engagement": 0
            }
        ]
    }

# Main dashboard page
@app.get("/")
async def dashboard():
    """Main dashboard page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VANTAGE AI - Marketing Platform</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { 
                text-align: center; 
                color: white; 
                margin-bottom: 40px;
                padding: 40px 0;
            }
            .header h1 { font-size: 3rem; margin-bottom: 10px; font-weight: 700; }
            .header p { font-size: 1.2rem; opacity: 0.9; }
            .dashboard { 
                background: white; 
                border-radius: 20px; 
                padding: 40px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .stats { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
                margin-bottom: 40px;
            }
            .stat-card { 
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white; 
                padding: 30px; 
                border-radius: 15px; 
                text-align: center;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }
            .stat-card h3 { font-size: 2.5rem; margin-bottom: 10px; }
            .stat-card p { opacity: 0.9; font-size: 1.1rem; }
            .features { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px;
            }
            .feature { 
                background: #f8f9fa; 
                padding: 30px; 
                border-radius: 15px; 
                border-left: 5px solid #667eea;
            }
            .feature h3 { color: #667eea; margin-bottom: 15px; font-size: 1.3rem; }
            .feature p { color: #666; line-height: 1.6; }
            .api-info { 
                background: #e3f2fd; 
                padding: 20px; 
                border-radius: 10px; 
                margin-top: 30px;
                border-left: 5px solid #2196f3;
            }
            .api-info h3 { color: #1976d2; margin-bottom: 15px; }
            .api-endpoint { 
                background: #263238; 
                color: #4caf50; 
                padding: 10px; 
                border-radius: 5px; 
                font-family: 'Courier New', monospace;
                margin: 5px 0;
            }
            .status { 
                display: inline-block; 
                background: #4caf50; 
                color: white; 
                padding: 5px 15px; 
                border-radius: 20px; 
                font-size: 0.9rem;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>VANTAGE AI</h1>
                <p>AI-Powered Marketing Platform</p>
                <span class="status">LIVE</span>
            </div>
            
            <div class="dashboard">
                <h2 style="margin-bottom: 30px; color: #333; text-align: center;">Platform Overview</h2>
                
                <div class="stats">
                    <div class="stat-card">
                        <h3>156</h3>
                        <p>Total Posts</p>
                    </div>
                    <div class="stat-card">
                        <h3>12</h3>
                        <p>Organizations</p>
                    </div>
                    <div class="stat-card">
                        <h3>8</h3>
                        <p>Channels</p>
                    </div>
                    <div class="stat-card">
                        <h3>12.5%</h3>
                        <p>Engagement Rate</p>
                    </div>
                </div>
                
                <div class="features">
                    <div class="feature">
                        <h3>AI Content Generation</h3>
                        <p>Generate engaging, platform-optimized content using advanced AI. Create posts for LinkedIn, Twitter, Facebook, and more with just a few clicks.</p>
                    </div>
                    <div class="feature">
                        <h3>Multi-Platform Publishing</h3>
                        <p>Schedule and publish content across multiple social media platforms simultaneously. Manage all your channels from one unified dashboard.</p>
                    </div>
                    <div class="feature">
                        <h3>Analytics & Insights</h3>
                        <p>Track performance with detailed analytics, engagement metrics, and AI-powered insights to optimize your content strategy.</p>
                    </div>
                    <div class="feature">
                        <h3>Team Collaboration</h3>
                        <p>Work together with your team, manage permissions, and streamline your content creation workflow with collaborative tools.</p>
                    </div>
                </div>
                
                <div class="api-info">
                    <h3>API Endpoints Available</h3>
                    <div class="api-endpoint">GET /api/v1/health - Health check</div>
                    <div class="api-endpoint">POST /api/v1/ai/generate - Generate AI content</div>
                    <div class="api-endpoint">GET /api/v1/ai/suggestions - Get content suggestions</div>
                    <div class="api-endpoint">GET /api/v1/dashboard - Dashboard data</div>
                    <div class="api-endpoint">GET /docs - API documentation</div>
                </div>
            </div>
        </div>
        
        <script>
            // Test API connectivity
            fetch('/api/v1/health')
                .then(response => response.json())
                .then(data => {
                    console.log('API Status:', data);
                    if (data.status === 'ok') {
                        document.querySelector('.status').textContent = 'CONNECTED';
                        document.querySelector('.status').style.background = '#4caf50';
                    }
                })
                .catch(error => {
                    console.error('API Error:', error);
                    document.querySelector('.status').textContent = 'ERROR';
                    document.querySelector('.status').style.background = '#f44336';
                });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🚀 Starting VANTAGE AI Demo Server...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("🌐 Dashboard: http://localhost:8000")
    print("❤️  Health Check: http://localhost:8000/api/v1/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)
