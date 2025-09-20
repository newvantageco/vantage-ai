"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  X, 
  BookOpen, 
  Lightbulb, 
  Calendar,
  BarChart3,
  Zap,
  ArrowRight,
  CheckCircle
} from 'lucide-react';

interface WorkingTutorialProps {
  onClose?: () => void;
}

export function WorkingTutorial({ onClose }: WorkingTutorialProps) {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title: "Welcome to VANTAGE AI! 🚀",
      content: "Your comprehensive AI-powered marketing automation platform. This platform has 67 API endpoints and 15 dashboard pages with enterprise-grade features.",
      icon: <BookOpen className="h-6 w-6" />
    },
    {
      title: "Dashboard Overview 📊",
      content: "Your main dashboard shows real-time metrics, quick actions, and recent activity. Navigate to different sections using the sidebar menu.",
      icon: <BarChart3 className="h-6 w-6" />
    },
    {
      title: "AI Content Composer ✍️",
      content: "Create engaging content with AI assistance. Generate platform-specific posts, variations, and maintain consistent brand voice across all channels.",
      icon: <Lightbulb className="h-6 w-6" />
    },
    {
      title: "Content Library 📚",
      content: "Organize and manage all your content in one place. Access templates, media assets, and content variations for easy reuse.",
      icon: <BookOpen className="h-6 w-6" />
    },
    {
      title: "Smart Calendar 📅",
      content: "Schedule content at optimal times using AI-powered recommendations. Plan campaigns, bulk schedule posts, and track your content calendar.",
      icon: <Calendar className="h-6 w-6" />
    },
    {
      title: "Advanced Analytics 📈",
      content: "Track performance with detailed analytics, custom reports, competitive analysis, and audience insights. Make data-driven decisions.",
      icon: <BarChart3 className="h-6 w-6" />
    },
    {
      title: "Automation Rules ⚡",
      content: "Set up intelligent workflows and automation rules. A/B test content, trigger actions based on events, and streamline your processes.",
      icon: <Zap className="h-6 w-6" />
    },
    {
      title: "Team Collaboration 👥",
      content: "Manage team members, set permissions, approve content, and collaborate on campaigns. Version control and feedback systems included.",
      icon: <Calendar className="h-6 w-6" />
    },
    {
      title: "Integrations 🔌",
      content: "Connect Facebook, Instagram, LinkedIn, Twitter, TikTok, WhatsApp, and more. OAuth integration with secure account management.",
      icon: <Zap className="h-6 w-6" />
    },
    {
      title: "AI Engines 🤖",
      content: "Advanced AI optimization engines for content performance prediction, trend analysis, audience insights, and smart recommendations.",
      icon: <Lightbulb className="h-6 w-6" />
    },
    {
      title: "Operations & Bulk Tools 🔧",
      content: "Bulk operations, media management, content exports, and advanced operational tools for managing large-scale campaigns.",
      icon: <Zap className="h-6 w-6" />
    },
    {
      title: "Settings & Privacy ⚙️",
      content: "Configure platform settings, manage privacy controls, set up billing, and customize your workspace preferences.",
      icon: <Calendar className="h-6 w-6" />
    }
  ];

  const currentStepData = steps[currentStep];
  const isLastStep = currentStep >= steps.length - 1;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl mx-4">
        <CardHeader className="border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {currentStepData.icon}
              <div>
                <CardTitle className="text-lg">{currentStepData.title}</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Step {currentStep + 1} of {steps.length}
                </p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm leading-relaxed">{currentStepData.content}</p>
            </div>
            
            {/* Progress indicator */}
            <div className="flex space-x-2">
              {steps.map((_, index) => (
                <div
                  key={index}
                  className={`h-2 flex-1 rounded-full ${
                    index <= currentStep ? 'bg-primary' : 'bg-muted'
                  }`}
                />
              ))}
            </div>
          </div>
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
              {steps.length} steps
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
