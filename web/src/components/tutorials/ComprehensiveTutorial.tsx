"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  X, 
  BookOpen, 
  Lightbulb, 
  Calendar,
  BarChart3,
  Zap,
  ArrowRight,
  CheckCircle,
  Users,
  Settings,
  Database,
  Globe,
  Shield,
  Target,
  TrendingUp,
  FileText,
  Image,
  Video,
  Link,
  MessageSquare,
  Bell,
  Search,
  Filter,
  Download,
  Upload,
  Play,
  Pause,
  Edit,
  Trash2,
  Copy,
  Share,
  Heart,
  ThumbsUp,
  Eye,
  MousePointer,
  Keyboard,
  Monitor,
  Smartphone,
  Tablet
} from 'lucide-react';

interface ComprehensiveTutorialProps {
  onClose?: () => void;
}

export function ComprehensiveTutorial({ onClose }: ComprehensiveTutorialProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [currentStep, setCurrentStep] = useState(0);

  const tutorialCategories = {
    overview: {
      title: "Platform Overview",
      icon: <Globe className="h-5 w-5" />,
      steps: [
        {
          title: "Welcome to VANTAGE AI! 🚀",
          content: "Your comprehensive AI-powered marketing automation platform with 67 API endpoints and 15 dashboard pages.",
          features: ["Enterprise-grade architecture", "Multi-tenant support", "Real-time processing", "Scalable infrastructure"]
        },
        {
          title: "Platform Architecture 🏗️",
          content: "Built with FastAPI backend, Next.js frontend, PostgreSQL with pgvector, Redis caching, and Celery workers.",
          features: ["Microservices architecture", "Docker containerization", "Health monitoring", "Background processing"]
        },
        {
          title: "Key Capabilities 🎯",
          content: "AI content generation, multi-platform publishing, advanced analytics, team collaboration, and automation.",
          features: ["AI-powered content", "Social media management", "Performance analytics", "Workflow automation"]
        }
      ]
    },
    content: {
      title: "Content Creation",
      icon: <FileText className="h-5 w-5" />,
      steps: [
        {
          title: "AI Content Composer ✍️",
          content: "Create engaging content with AI assistance. Generate platform-specific posts, variations, and maintain brand voice.",
          features: ["Multi-provider AI", "Platform optimization", "Brand voice consistency", "Content variations"]
        },
        {
          title: "Content Library 📚",
          content: "Organize and manage all your content. Access templates, media assets, and content variations for easy reuse.",
          features: ["Content organization", "Template library", "Media management", "Version control"]
        },
        {
          title: "Media Management 🖼️",
          content: "Upload, organize, and optimize images, videos, and other media assets for your content campaigns.",
          features: ["Media upload", "Asset optimization", "CDN integration", "Bulk operations"]
        },
        {
          title: "Content Planning 📋",
          content: "Strategic content planning with AI-powered recommendations, trend analysis, and campaign planning tools.",
          features: ["Strategic planning", "Trend analysis", "Campaign planning", "Content calendar"]
        }
      ]
    },
    publishing: {
      title: "Publishing & Scheduling",
      icon: <Calendar className="h-5 w-5" />,
      steps: [
        {
          title: "Multi-Platform Publishing 📱",
          content: "Publish to Facebook, Instagram, LinkedIn, Twitter, TikTok, WhatsApp, and more from one interface.",
          features: ["Multi-platform support", "OAuth integration", "Bulk publishing", "Platform optimization"]
        },
        {
          title: "Smart Scheduling 📅",
          content: "AI-powered optimal timing recommendations based on audience behavior and engagement patterns.",
          features: ["Optimal timing", "Audience analysis", "Engagement prediction", "Bulk scheduling"]
        },
        {
          title: "Content Calendar 🗓️",
          content: "Visual calendar interface for planning, scheduling, and managing your content across all platforms.",
          features: ["Visual planning", "Drag-and-drop", "Campaign tracking", "Content preview"]
        },
        {
          title: "Automated Publishing 🤖",
          content: "Set up automated workflows for content publishing, reposting, and cross-platform distribution.",
          features: ["Workflow automation", "Trigger-based actions", "Cross-platform sync", "Reposting rules"]
        }
      ]
    },
    analytics: {
      title: "Analytics & Insights",
      icon: <BarChart3 className="h-5 w-5" />,
      steps: [
        {
          title: "Real-time Analytics 📊",
          content: "Track performance metrics in real-time with comprehensive dashboards and customizable reports.",
          features: ["Real-time metrics", "Custom dashboards", "Performance tracking", "Engagement analysis"]
        },
        {
          title: "Advanced Reporting 📈",
          content: "Create custom reports with detailed insights, competitor analysis, and audience demographics.",
          features: ["Custom reports", "Competitor analysis", "Audience insights", "Export capabilities"]
        },
        {
          title: "Performance Prediction 🔮",
          content: "AI-powered content performance prediction and optimization recommendations.",
          features: ["Performance prediction", "Optimization tips", "Trend forecasting", "ROI analysis"]
        },
        {
          title: "Audience Insights 👥",
          content: "Deep audience analysis with demographics, behavior patterns, and engagement preferences.",
          features: ["Demographic analysis", "Behavior tracking", "Engagement patterns", "Audience segmentation"]
        }
      ]
    },
    automation: {
      title: "Automation & AI",
      icon: <Zap className="h-5 w-5" />,
      steps: [
        {
          title: "Workflow Automation ⚡",
          content: "Set up intelligent workflows and automation rules to streamline your social media management.",
          features: ["Rule-based automation", "Trigger actions", "Workflow templates", "Conditional logic"]
        },
        {
          title: "AI Optimization 🤖",
          content: "Advanced AI engines for content optimization, performance prediction, and smart recommendations.",
          features: ["Content optimization", "Performance prediction", "Smart recommendations", "A/B testing"]
        },
        {
          title: "Smart Rules 🎯",
          content: "Create intelligent rules for content approval, posting schedules, and engagement responses.",
          features: ["Approval workflows", "Scheduling rules", "Engagement automation", "Quality control"]
        },
        {
          title: "Bulk Operations 🔧",
          content: "Efficiently manage large-scale campaigns with bulk operations and batch processing tools.",
          features: ["Bulk editing", "Batch processing", "Mass operations", "Campaign management"]
        }
      ]
    },
    collaboration: {
      title: "Team & Collaboration",
      icon: <Users className="h-5 w-5" />,
      steps: [
        {
          title: "Team Management 👥",
          content: "Manage team members, set permissions, and control access to different platform features.",
          features: ["User management", "Role-based access", "Permission control", "Team organization"]
        },
        {
          title: "Content Approval ✅",
          content: "Review and approve content before publishing with collaborative feedback and version control.",
          features: ["Approval workflows", "Collaborative feedback", "Version control", "Comment system"]
        },
        {
          title: "Collaboration Tools 💬",
          content: "Communicate with team members, share feedback, and collaborate on content creation.",
          features: ["Team communication", "Feedback sharing", "Collaborative editing", "Notification system"]
        },
        {
          title: "Organization Management 🏢",
          content: "Manage multiple organizations, clients, or brands from a single platform interface.",
          features: ["Multi-tenant support", "Client management", "Brand separation", "Billing management"]
        }
      ]
    },
    integrations: {
      title: "Integrations & APIs",
      icon: <Link className="h-5 w-5" />,
      steps: [
        {
          title: "Social Media Platforms 📱",
          content: "Connect Facebook, Instagram, LinkedIn, Twitter, TikTok, WhatsApp, and more with secure OAuth.",
          features: ["OAuth integration", "Platform APIs", "Secure connections", "Account management"]
        },
        {
          title: "Third-party Integrations 🔌",
          content: "Integrate with CRM systems, email marketing, analytics tools, and other business applications.",
          features: ["CRM integration", "Email marketing", "Analytics tools", "Business apps"]
        },
        {
          title: "API Access 🔑",
          content: "Access the platform through REST APIs for custom integrations and automated workflows.",
          features: ["REST APIs", "Webhook support", "Custom integrations", "Developer tools"]
        },
        {
          title: "Webhook Support 🔗",
          content: "Set up webhooks for real-time notifications and automated responses to platform events.",
          features: ["Real-time notifications", "Event triggers", "Automated responses", "Custom endpoints"]
        }
      ]
    },
    settings: {
      title: "Settings & Configuration",
      icon: <Settings className="h-5 w-5" />,
      steps: [
        {
          title: "Platform Settings ⚙️",
          content: "Configure platform preferences, notifications, and workspace customization options.",
          features: ["User preferences", "Notification settings", "Workspace customization", "Theme options"]
        },
        {
          title: "Privacy & Security 🔒",
          content: "Manage data privacy, security settings, and compliance with GDPR and other regulations.",
          features: ["Data privacy", "Security controls", "GDPR compliance", "Access logs"]
        },
        {
          title: "Billing & Subscriptions 💳",
          content: "Manage subscription plans, billing information, and feature access based on your plan.",
          features: ["Subscription management", "Billing history", "Plan upgrades", "Payment methods"]
        },
        {
          title: "Account Management 👤",
          content: "Manage your account profile, organization settings, and user preferences.",
          features: ["Profile management", "Organization settings", "User preferences", "Account security"]
        }
      ]
    }
  };

  const currentCategory = tutorialCategories[activeTab as keyof typeof tutorialCategories];
  const currentStepData = currentCategory.steps[currentStep];
  const isLastStep = currentStep >= currentCategory.steps.length - 1;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-6xl mx-4 max-h-[90vh] overflow-hidden">
        <CardHeader className="border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <BookOpen className="h-6 w-6" />
              <div>
                <CardTitle className="text-lg">VANTAGE AI Platform Tutorial</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Comprehensive guide to all platform features
                </p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="p-0">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
            <div className="flex h-[600px]">
              {/* Sidebar */}
              <div className="w-64 border-r bg-muted/50 p-4">
                <TabsList className="grid w-full grid-cols-1 gap-2 h-auto">
                  {Object.entries(tutorialCategories).map(([key, category]) => (
                    <TabsTrigger 
                      key={key} 
                      value={key} 
                      className="flex items-center space-x-2 justify-start p-3 h-auto"
                    >
                      {category.icon}
                      <span className="text-sm">{category.title}</span>
                    </TabsTrigger>
                  ))}
                </TabsList>
              </div>
              
              {/* Content */}
              <div className="flex-1 p-6">
                <TabsContent value={activeTab} className="h-full">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xl font-semibold">{currentCategory.title}</h3>
                      <Badge variant="outline">
                        Step {currentStep + 1} of {currentCategory.steps.length}
                      </Badge>
                    </div>
                    
                    <div className="p-4 bg-muted rounded-lg">
                      <h4 className="text-lg font-semibold mb-2">{currentStepData.title}</h4>
                      <p className="text-sm leading-relaxed mb-4">{currentStepData.content}</p>
                      
                      <div className="grid grid-cols-2 gap-2">
                        {currentStepData.features.map((feature, index) => (
                          <div key={index} className="flex items-center space-x-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-green-500" />
                            <span>{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {/* Progress indicator */}
                    <div className="flex space-x-2">
                      {currentCategory.steps.map((_, index) => (
                        <div
                          key={index}
                          className={`h-2 flex-1 rounded-full ${
                            index <= currentStep ? 'bg-primary' : 'bg-muted'
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                </TabsContent>
              </div>
            </div>
          </Tabs>
        </CardContent>
        
        <div className="border-t p-4 flex justify-between">
          <Button 
            variant="outline" 
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
          >
            Previous
          </Button>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="text-xs">
              {Object.keys(tutorialCategories).length} categories
            </Badge>
            <Button onClick={() => {
              if (isLastStep) {
                onClose?.();
              } else {
                setCurrentStep(currentStep + 1);
              }
            }}>
              {isLastStep ? 'Complete' : 'Next'}
              {isLastStep ? (
                <CheckCircle className="h-4 w-4 ml-2" />
              ) : (
                <ArrowRight className="h-4 w-4 ml-2" />
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
