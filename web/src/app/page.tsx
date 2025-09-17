'use client'

import { useState, useEffect } from 'react'

interface DashboardData {
  overview: {
    total_content: number
    published_content: number
    scheduled_content: number
    total_organizations: number
    total_channels: number
    recent_activity: number
  }
  status: string
}

interface AnalyticsData {
  period: string
  metrics: {
    total_posts: number
    engagement_rate: string
    total_reach: number
    total_clicks: number
    avg_engagement_per_post: number
  }
  trends: {
    posts_trend: string
    engagement_trend: string
    reach_trend: string
  }
}

export default function VantageAIDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const [aiPrompt, setAiPrompt] = useState('')
  const [generatedContent, setGeneratedContent] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    fetchDashboardData()
    fetchAnalyticsData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/dashboard')
      if (response.ok) {
        const data = await response.json()
        setDashboardData(data)
      } else {
        // Fallback to demo data if API is not available
        setDashboardData({
          status: 'demo',
          overview: {
            total_content: 12,
            published_content: 8,
            scheduled_content: 4,
            total_organizations: 3,
            total_channels: 6,
            recent_activity: 15
          }
        })
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      // Fallback to demo data
      setDashboardData({
        status: 'demo',
        overview: {
          total_content: 12,
          published_content: 8,
          scheduled_content: 4,
          total_organizations: 3,
          total_channels: 6,
          recent_activity: 15
        }
      })
    }
  }

  const fetchAnalyticsData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/analytics/overview?org_id=demo-org&days=30')
      if (response.ok) {
        const data = await response.json()
        setAnalyticsData(data)
      } else {
        // Fallback to demo data
        setAnalyticsData({
          period: 'last_30_days',
          metrics: {
            total_posts: 24,
            engagement_rate: '4.2%',
            total_reach: 12500,
            total_clicks: 340,
            avg_engagement_per_post: 18
          },
          trends: {
            posts_trend: '↗️ +12%',
            engagement_trend: '↗️ +8%',
            reach_trend: '↗️ +15%'
          }
        })
      }
    } catch (error) {
      console.error('Error fetching analytics data:', error)
      // Fallback to demo data
      setAnalyticsData({
        period: 'last_30_days',
        metrics: {
          total_posts: 24,
          engagement_rate: '4.2%',
          total_reach: 12500,
          total_clicks: 340,
          avg_engagement_per_post: 18
        },
        trends: {
          posts_trend: '↗️ +12%',
          engagement_trend: '↗️ +8%',
          reach_trend: '↗️ +15%'
        }
      })
    } finally {
      setLoading(false)
    }
  }

  const generateContent = async () => {
    if (!aiPrompt.trim()) return
    
    setIsGenerating(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/ai/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: aiPrompt,
          content_type: 'social_media_post',
          platform: 'general',
          tone: 'professional'
        })
      })
      
      const data = await response.json()
      setGeneratedContent(data.generated_content)
    } catch (error) {
      console.error('Error generating content:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const createContent = async (title: string, content: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/content/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          content,
          platform: 'general',
          org_id: 'demo-org'
        })
      })
      
      const data = await response.json()
      alert(`Content created successfully! ID: ${data.id}`)
      fetchDashboardData() // Refresh dashboard
    } catch (error) {
      console.error('Error creating content:', error)
      alert('Error creating content')
    }
  }

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '50px', 
            height: '50px', 
            border: '5px solid #f3f3f3',
            borderTop: '5px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px'
          }}></div>
          <p>Loading VANTAGE AI Dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ 
      fontFamily: 'system-ui, -apple-system, sans-serif',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white'
    }}>
      {/* Header */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        padding: '1rem 2rem',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
      }}>
        <div style={{ 
          maxWidth: '1200px', 
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h1 style={{ 
            fontSize: '2rem', 
            fontWeight: 'bold',
            margin: 0,
            background: 'linear-gradient(45deg, #fff, #f0f0f0)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            VANTAGE AI Marketing Platform
          </h1>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button style={{
              background: 'rgba(255, 255, 255, 0.2)',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              cursor: 'pointer'
            }}>
              Sign In
            </button>
            <button style={{
              background: '#3b82f6',
              border: 'none',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              cursor: 'pointer'
            }}>
              Get Started
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        
        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          gap: '1rem',
          marginBottom: '2rem',
          background: 'rgba(255, 255, 255, 0.1)',
          padding: '0.5rem',
          borderRadius: '12px',
          backdropFilter: 'blur(10px)'
        }}>
          {['overview', 'content', 'analytics', 'schedule', 'team'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                background: activeTab === tab ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
                border: 'none',
                color: 'white',
                padding: '0.75rem 1.5rem',
                borderRadius: '8px',
                cursor: 'pointer',
                textTransform: 'capitalize',
                fontWeight: activeTab === tab ? '600' : '400'
              }}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Dashboard Overview</h2>
            
            {/* Stats Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '1.5rem',
              marginBottom: '2rem'
            }}>
              {(dashboardData?.overview ? [
                { label: 'Total Content', value: dashboardData.overview.total_content || 0, icon: '📝' },
                { label: 'Published', value: dashboardData.overview.published_content || 0, icon: '✅' },
                { label: 'Scheduled', value: dashboardData.overview.scheduled_content || 0, icon: '⏰' },
                { label: 'Organizations', value: dashboardData.overview.total_organizations || 0, icon: '🏢' },
                { label: 'Channels', value: dashboardData.overview.total_channels || 0, icon: '📱' },
                { label: 'Recent Activity', value: dashboardData.overview.recent_activity || 0, icon: '🔥' }
              ] : [
                { label: 'Total Content', value: 0, icon: '📝' },
                { label: 'Published', value: 0, icon: '✅' },
                { label: 'Scheduled', value: 0, icon: '⏰' },
                { label: 'Organizations', value: 0, icon: '🏢' },
                { label: 'Channels', value: 0, icon: '📱' },
                { label: 'Recent Activity', value: 0, icon: '🔥' }
              ]).map((stat, index) => (
                <div key={index} style={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  padding: '1.5rem',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{stat.icon}</div>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                    {stat.value}
                  </div>
                  <div style={{ opacity: 0.8 }}>{stat.label}</div>
                </div>
              ))}
            </div>

            {/* Quick Actions */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              padding: '2rem',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <h3 style={{ marginBottom: '1rem' }}>Quick Actions</h3>
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                <button style={{
                  background: '#10b981',
                  border: 'none',
                  color: 'white',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}>
                  + Create Content
                </button>
                <button style={{
                  background: '#3b82f6',
                  border: 'none',
                  color: 'white',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}>
                  📅 Schedule Post
                </button>
                <button style={{
                  background: '#8b5cf6',
                  border: 'none',
                  color: 'white',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}>
                  🤖 AI Assistant
                </button>
                <button style={{
                  background: '#f59e0b',
                  border: 'none',
                  color: 'white',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}>
                  View Analytics
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Content Tab */}
        {activeTab === 'content' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Content Management</h2>
            
            {/* AI Content Generation */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              padding: '2rem',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              marginBottom: '2rem'
            }}>
              <h3 style={{ marginBottom: '1rem' }}>🤖 AI Content Generator</h3>
              <div style={{ marginBottom: '1rem' }}>
                <textarea
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  placeholder="Describe what content you want to create... (e.g., 'Create a post about our new product launch')"
                  style={{
                    width: '100%',
                    minHeight: '100px',
                    padding: '1rem',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    background: 'rgba(255, 255, 255, 0.1)',
                    color: 'white',
                    fontSize: '1rem',
                    resize: 'vertical'
                  }}
                />
              </div>
              <button
                onClick={generateContent}
                disabled={isGenerating || !aiPrompt.trim()}
                style={{
                  background: isGenerating ? '#6b7280' : '#3b82f6',
                  border: 'none',
                  color: 'white',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '8px',
                  cursor: isGenerating ? 'not-allowed' : 'pointer',
                  marginRight: '1rem'
                }}
              >
                {isGenerating ? 'Generating...' : 'Generate Content'}
              </button>
              
              {generatedContent && (
                <div style={{
                  marginTop: '1rem',
                  padding: '1rem',
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '8px',
                  border: '1px solid rgba(255, 255, 255, 0.2)'
                }}>
                  <h4 style={{ marginBottom: '0.5rem' }}>Generated Content:</h4>
                  <p style={{ marginBottom: '1rem', lineHeight: '1.6' }}>{generatedContent}</p>
                  <button
                    onClick={() => createContent('AI Generated Post', generatedContent)}
                    style={{
                      background: '#10b981',
                      border: 'none',
                      color: 'white',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    Save as Content
                  </button>
                </div>
              )}
            </div>

            {/* Content List */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              padding: '2rem',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <h3 style={{ marginBottom: '1rem' }}>Recent Content</h3>
              <div style={{ opacity: 0.7 }}>
                <p>📝 No content yet. Create your first post using the AI generator above!</p>
              </div>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && analyticsData && (
          <div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Analytics & Performance</h2>
            
            {/* Metrics Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1.5rem',
              marginBottom: '2rem'
            }}>
              {(analyticsData?.metrics ? [
                { label: 'Total Posts', value: analyticsData.metrics.total_posts || 0, icon: '📊' },
                { label: 'Engagement Rate', value: analyticsData.metrics.engagement_rate || '0%', icon: '❤️' },
                { label: 'Total Reach', value: (analyticsData.metrics.total_reach || 0).toLocaleString(), icon: '👥' },
                { label: 'Total Clicks', value: (analyticsData.metrics.total_clicks || 0).toLocaleString(), icon: '🖱️' },
                { label: 'Avg Engagement', value: analyticsData.metrics.avg_engagement_per_post || 0, icon: '📈' }
              ] : [
                { label: 'Total Posts', value: 0, icon: '📊' },
                { label: 'Engagement Rate', value: '0%', icon: '❤️' },
                { label: 'Total Reach', value: '0', icon: '👥' },
                { label: 'Total Clicks', value: '0', icon: '🖱️' },
                { label: 'Avg Engagement', value: 0, icon: '📈' }
              ]).map((metric, index) => (
                <div key={index} style={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  padding: '1.5rem',
                  borderRadius: '12px',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{metric.icon}</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                    {metric.value}
                  </div>
                  <div style={{ opacity: 0.8 }}>{metric.label}</div>
                </div>
              ))}
            </div>

            {/* Trends */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              padding: '2rem',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <h3 style={{ marginBottom: '1rem' }}>Performance Trends</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
                {Object.entries(analyticsData?.trends || {}).map(([key, trend]) => (
                  <div key={key} style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    padding: '1rem',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <div style={{ textTransform: 'capitalize', marginBottom: '0.5rem' }}>
                      {key.replace('_', ' ')}
                    </div>
                    <div style={{ 
                      fontSize: '1.2rem',
                      color: trend === 'up' ? '#10b981' : trend === 'down' ? '#ef4444' : '#f59e0b'
                    }}>
                      {trend === 'up' ? '📈' : trend === 'down' ? '📉' : '➡️'} {trend}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Schedule Tab */}
        {activeTab === 'schedule' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Content Scheduling</h2>
            
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              padding: '2rem',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <h3 style={{ marginBottom: '1rem' }}>📅 Content Calendar</h3>
              <div style={{ opacity: 0.7 }}>
                <p>📝 No scheduled content yet. Create content and schedule it for optimal posting times!</p>
              </div>
            </div>
          </div>
        )}

        {/* Team Tab */}
        {activeTab === 'team' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Team Collaboration</h2>
            
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              padding: '2rem',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <h3 style={{ marginBottom: '1rem' }}>👥 Team Members</h3>
              <div style={{ opacity: 0.7 }}>
                <p>👤 John Doe - Content Manager</p>
                <p>👤 Jane Smith - Social Media Specialist</p>
                <p>👤 Mike Johnson - Analytics Manager</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{
        background: 'rgba(0, 0, 0, 0.2)',
        padding: '2rem',
        textAlign: 'center',
        marginTop: '3rem'
      }}>
        <p style={{ opacity: 0.8, margin: 0 }}>
          🚀 VANTAGE AI Marketing Platform - AI-Powered Content Management & Social Media Automation
        </p>
        <p style={{ opacity: 0.6, margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
          API: http://localhost:8000 | Web: http://localhost:3000 | Docs: http://localhost:8000/docs
        </p>
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}