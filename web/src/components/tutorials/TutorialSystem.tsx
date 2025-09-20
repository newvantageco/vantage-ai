"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Play, 
  CheckCircle, 
  Circle, 
  ArrowRight, 
  ArrowLeft, 
  X, 
  BookOpen, 
  Lightbulb, 
  Target,
  Users,
  BarChart3,
  Calendar,
  Zap,
  Settings,
  HelpCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface TutorialStep {
  id: string;
  title: string;
  description: string;
  content: React.ReactNode;
  completed: boolean;
  estimatedTime: string;
  category: string;
}

interface Tutorial {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime: string;
  steps: TutorialStep[];
  completed: boolean;
  progress: number;
}

interface TutorialSystemProps {
  onClose?: () => void;
  showWelcome?: boolean;
}

const tutorials: Tutorial[] = [
  {
    id: 'getting-started',
    title: 'Getting Started with VANTAGE AI',
    description: 'Learn the basics of using VANTAGE AI for social media management',
    icon: <BookOpen className="h-6 w-6" />,
    category: 'onboarding',
    difficulty: 'beginner',
    estimatedTime: '10 min',
    completed: false,
    progress: 0,
    steps: [
      {
        id: 'welcome',
        title: 'Welcome to VANTAGE AI',
        description: 'Introduction to the platform and its capabilities',
        content: (
          <div className="space-y-4">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-primary mb-2">Welcome to VANTAGE AI! 🚀</h3>
              <p className="text-muted-foreground">
                Your AI-powered social media management platform that helps you create, schedule, and optimize content across multiple platforms.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
              <div className="text-center p-4 border rounded-lg">
                <Target className="h-8 w-8 mx-auto mb-2 text-blue-500" />
                <h4 className="font-semibold">AI Content Creation</h4>
                <p className="text-sm text-muted-foreground">Generate engaging content with AI</p>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <Calendar className="h-8 w-8 mx-auto mb-2 text-green-500" />
                <h4 className="font-semibold">Smart Scheduling</h4>
                <p className="text-sm text-muted-foreground">Schedule posts at optimal times</p>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <BarChart3 className="h-8 w-8 mx-auto mb-2 text-purple-500" />
                <h4 className="font-semibold">Analytics & Insights</h4>
                <p className="text-sm text-muted-foreground">Track performance and optimize</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '2 min',
        category: 'onboarding'
      },
      {
        id: 'dashboard-overview',
        title: 'Dashboard Overview',
        description: 'Navigate the main dashboard and understand the layout',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Dashboard Navigation</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 border rounded-lg">
                <h4 className="font-medium">📊 Analytics</h4>
                <p className="text-sm text-muted-foreground">View performance metrics</p>
              </div>
              <div className="p-3 border rounded-lg">
                <h4 className="font-medium">✍️ Composer</h4>
                <p className="text-sm text-muted-foreground">Create new content</p>
              </div>
              <div className="p-3 border rounded-lg">
                <h4 className="font-medium">📅 Calendar</h4>
                <p className="text-sm text-muted-foreground">Schedule and plan posts</p>
              </div>
              <div className="p-3 border rounded-lg">
                <h4 className="font-medium">🔗 Integrations</h4>
                <p className="text-sm text-muted-foreground">Connect social accounts</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '3 min',
        category: 'onboarding'
      },
      {
        id: 'first-integration',
        title: 'Connect Your First Social Account',
        description: 'Learn how to connect Facebook, Instagram, or LinkedIn',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Connect Social Media Accounts</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 p-3 border rounded-lg">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">f</div>
                <div>
                  <h4 className="font-medium">Facebook & Instagram</h4>
                  <p className="text-sm text-muted-foreground">Connect your Meta Business account</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-3 border rounded-lg">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">in</div>
                <div>
                  <h4 className="font-medium">LinkedIn</h4>
                  <p className="text-sm text-muted-foreground">Connect your LinkedIn company page</p>
                </div>
              </div>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm">
                <strong>Tip:</strong> You can connect multiple accounts and manage them all from one dashboard!
              </p>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '5 min',
        category: 'onboarding'
      }
    ]
  },
  {
    id: 'content-creation',
    title: 'AI Content Creation',
    description: 'Master the art of creating engaging content with AI assistance',
    icon: <Lightbulb className="h-6 w-6" />,
    category: 'content',
    difficulty: 'beginner',
    estimatedTime: '15 min',
    completed: false,
    progress: 0,
    steps: [
      {
        id: 'ai-composer',
        title: 'Using the AI Composer',
        description: 'Create content with AI assistance',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">AI Content Composer</h3>
            <div className="space-y-3">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">1. Choose Your Topic</h4>
                <p className="text-sm text-muted-foreground">Enter a topic, keyword, or idea for your content</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">2. Select Platform</h4>
                <p className="text-sm text-muted-foreground">Choose Facebook, Instagram, LinkedIn, or Twitter</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">3. AI Generates Content</h4>
                <p className="text-sm text-muted-foreground">Our AI creates platform-optimized content</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">4. Review & Edit</h4>
                <p className="text-sm text-muted-foreground">Customize the content to match your brand voice</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '5 min',
        category: 'content'
      },
      {
        id: 'content-variations',
        title: 'Creating Content Variations',
        description: 'Generate multiple versions of your content for different platforms',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Content Variations</h3>
            <p className="text-muted-foreground">
              Create multiple versions of your content optimized for different platforms and audiences.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">Facebook Post</h4>
                <p className="text-sm text-muted-foreground">Longer, more detailed content with hashtags</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">Instagram Caption</h4>
                <p className="text-sm text-muted-foreground">Visual-focused with emojis and relevant hashtags</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">LinkedIn Post</h4>
                <p className="text-sm text-muted-foreground">Professional tone with industry insights</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">Twitter Tweet</h4>
                <p className="text-sm text-muted-foreground">Concise, engaging content under 280 characters</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '5 min',
        category: 'content'
      },
      {
        id: 'brand-voice',
        title: 'Setting Up Brand Voice',
        description: 'Configure your brand voice for consistent AI-generated content',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Brand Voice Configuration</h3>
            <p className="text-muted-foreground">
              Define your brand's personality to ensure AI-generated content matches your style.
            </p>
            <div className="space-y-3">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">Tone of Voice</h4>
                <p className="text-sm text-muted-foreground">Professional, Casual, Friendly, Authoritative, etc.</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">Key Messages</h4>
                <p className="text-sm text-muted-foreground">Core values and messages your brand represents</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">Avoided Terms</h4>
                <p className="text-sm text-muted-foreground">Words or phrases your brand doesn't use</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '5 min',
        category: 'content'
      }
    ]
  },
  {
    id: 'scheduling',
    title: 'Smart Scheduling',
    description: 'Learn how to schedule content at optimal times',
    icon: <Calendar className="h-6 w-6" />,
    category: 'scheduling',
    difficulty: 'beginner',
    estimatedTime: '10 min',
    completed: false,
    progress: 0,
    steps: [
      {
        id: 'calendar-overview',
        title: 'Calendar Interface',
        description: 'Navigate the scheduling calendar',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Scheduling Calendar</h3>
            <div className="space-y-3">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📅 Monthly View</h4>
                <p className="text-sm text-muted-foreground">See all scheduled posts for the month</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📊 Optimal Times</h4>
                <p className="text-sm text-muted-foreground">AI suggests best times to post based on your audience</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">🔄 Drag & Drop</h4>
                <p className="text-sm text-muted-foreground">Easily reschedule posts by dragging them</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '3 min',
        category: 'scheduling'
      },
      {
        id: 'optimal-timing',
        title: 'Optimal Timing',
        description: 'Understand how AI determines the best posting times',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">AI-Powered Optimal Timing</h3>
            <p className="text-muted-foreground">
              Our AI analyzes your audience behavior to suggest the best times to post.
            </p>
            <div className="space-y-3">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📈 Engagement Patterns</h4>
                <p className="text-sm text-muted-foreground">Analyzes when your audience is most active</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">🌍 Time Zones</h4>
                <p className="text-sm text-muted-foreground">Considers your audience's time zones</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📊 Historical Data</h4>
                <p className="text-sm text-muted-foreground">Uses past performance to predict future success</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '4 min',
        category: 'scheduling'
      },
      {
        id: 'bulk-scheduling',
        title: 'Bulk Scheduling',
        description: 'Schedule multiple posts efficiently',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Bulk Scheduling</h3>
            <p className="text-muted-foreground">
              Schedule multiple posts at once to save time and maintain consistency.
            </p>
            <div className="space-y-3">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📝 Content Library</h4>
                <p className="text-sm text-muted-foreground">Select multiple posts from your content library</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">⏰ Time Spacing</h4>
                <p className="text-sm text-muted-foreground">Set intervals between posts (e.g., every 2 hours)</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">🎯 Platform Selection</h4>
                <p className="text-sm text-muted-foreground">Choose which platforms to publish to</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '3 min',
        category: 'scheduling'
      }
    ]
  },
  {
    id: 'analytics',
    title: 'Analytics & Insights',
    description: 'Understand your content performance and optimize your strategy',
    icon: <BarChart3 className="h-6 w-6" />,
    category: 'analytics',
    difficulty: 'intermediate',
    estimatedTime: '12 min',
    completed: false,
    progress: 0,
    steps: [
      {
        id: 'analytics-dashboard',
        title: 'Analytics Dashboard',
        description: 'Navigate the analytics dashboard',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Analytics Dashboard</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📊 Key Metrics</h4>
                <p className="text-sm text-muted-foreground">Views, likes, shares, comments</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📈 Performance Trends</h4>
                <p className="text-sm text-muted-foreground">Track growth over time</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">🎯 Top Performing Content</h4>
                <p className="text-sm text-muted-foreground">See what resonates with your audience</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">⏰ Best Posting Times</h4>
                <p className="text-sm text-muted-foreground">When your audience is most engaged</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '4 min',
        category: 'analytics'
      },
      {
        id: 'performance-insights',
        title: 'Performance Insights',
        description: 'Understand what makes content successful',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Performance Insights</h3>
            <p className="text-muted-foreground">
              AI analyzes your content performance to provide actionable insights.
            </p>
            <div className="space-y-3">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">🎨 Content Themes</h4>
                <p className="text-sm text-muted-foreground">Which topics perform best with your audience</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📝 Content Length</h4>
                <p className="text-sm text-muted-foreground">Optimal post length for each platform</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">🏷️ Hashtag Performance</h4>
                <p className="text-sm text-muted-foreground">Which hashtags drive the most engagement</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '4 min',
        category: 'analytics'
      },
      {
        id: 'optimization-tips',
        title: 'Content Optimization Tips',
        description: 'Learn how to improve your content based on analytics',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Content Optimization</h3>
            <p className="text-muted-foreground">
              Use analytics data to continuously improve your content strategy.
            </p>
            <div className="space-y-3">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📊 A/B Testing</h4>
                <p className="text-sm text-muted-foreground">Test different versions of your content</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">🔄 Content Recycling</h4>
                <p className="text-sm text-muted-foreground">Repurpose high-performing content</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📈 Trend Analysis</h4>
                <p className="text-sm text-muted-foreground">Identify patterns in successful content</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '4 min',
        category: 'analytics'
      }
    ]
  },
  {
    id: 'automation',
    title: 'Automation & Rules',
    description: 'Set up automated workflows and content rules',
    icon: <Zap className="h-6 w-6" />,
    category: 'automation',
    difficulty: 'advanced',
    estimatedTime: '20 min',
    completed: false,
    progress: 0,
    steps: [
      {
        id: 'automation-overview',
        title: 'Automation Overview',
        description: 'Introduction to automation features',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Automation Features</h3>
            <p className="text-muted-foreground">
              Automate repetitive tasks and create intelligent workflows.
            </p>
            <div className="space-y-3">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">🤖 Auto-Posting</h4>
                <p className="text-sm text-muted-foreground">Automatically publish content at scheduled times</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📊 Auto-Analytics</h4>
                <p className="text-sm text-muted-foreground">Automatically collect performance data</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">🔄 Content Recycling</h4>
                <p className="text-sm text-muted-foreground">Automatically repost high-performing content</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '5 min',
        category: 'automation'
      },
      {
        id: 'rules-engine',
        title: 'Rules Engine',
        description: 'Create custom rules for content management',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Rules Engine</h3>
            <p className="text-muted-foreground">
              Create intelligent rules to automate content decisions.
            </p>
            <div className="space-y-3">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📝 Content Rules</h4>
                <p className="text-sm text-muted-foreground">Automatically approve or reject content based on criteria</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">⏰ Time Rules</h4>
                <p className="text-sm text-muted-foreground">Schedule content based on time-based conditions</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">🎯 Performance Rules</h4>
                <p className="text-sm text-muted-foreground">Take actions based on content performance</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '8 min',
        category: 'automation'
      },
      {
        id: 'workflows',
        title: 'Workflow Automation',
        description: 'Set up complex workflows for content management',
        content: (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Workflow Automation</h3>
            <p className="text-muted-foreground">
              Create multi-step workflows to streamline your content process.
            </p>
            <div className="space-y-3">
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">🔄 Content Pipeline</h4>
                <p className="text-sm text-muted-foreground">Automated content creation → review → approval → publishing</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">📊 Analytics Pipeline</h4>
                <p className="text-sm text-muted-foreground">Collect data → analyze → generate reports → send notifications</p>
              </div>
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium">🎯 Engagement Pipeline</h4>
                <p className="text-sm text-muted-foreground">Monitor mentions → respond → escalate if needed</p>
              </div>
            </div>
          </div>
        ),
        completed: false,
        estimatedTime: '7 min',
        category: 'automation'
      }
    ]
  }
];

export function TutorialSystem({ onClose, showWelcome = false }: TutorialSystemProps) {
  const [currentTutorial, setCurrentTutorial] = useState<Tutorial | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [tutorialsState, setTutorialsState] = useState<Tutorial[]>(tutorials);
  const [showTutorialList, setShowTutorialList] = useState(true);

  useEffect(() => {
    // Load tutorial progress from localStorage - safely
    if (typeof window !== 'undefined') {
      const savedProgress = localStorage.getItem('vantage-tutorial-progress');
      if (savedProgress) {
        try {
          const progress = JSON.parse(savedProgress);
          setTutorialsState(progress);
        } catch (error) {
          console.error('Error loading tutorial progress:', error);
        }
      }
    }
  }, []);

  useEffect(() => {
    // Save tutorial progress to localStorage - safely
    if (typeof window !== 'undefined') {
      localStorage.setItem('vantage-tutorial-progress', JSON.stringify(tutorialsState));
    }
  }, [tutorialsState]);

  const startTutorial = (tutorial: Tutorial) => {
    setCurrentTutorial(tutorial);
    setCurrentStepIndex(0);
    setShowTutorialList(false);
  };

  const completeStep = (tutorialId: string, stepId: string) => {
    setTutorialsState(prev => prev.map(tutorial => {
      if (tutorial.id === tutorialId) {
        const updatedSteps = tutorial.steps.map(step => 
          step.id === stepId ? { ...step, completed: true } : step
        );
        const completedSteps = updatedSteps.filter(step => step.completed).length;
        const progress = (completedSteps / updatedSteps.length) * 100;
        const completed = completedSteps === updatedSteps.length;
        
        return {
          ...tutorial,
          steps: updatedSteps,
          progress,
          completed
        };
      }
      return tutorial;
    }));
  };

  const nextStep = () => {
    if (currentTutorial && currentStepIndex < currentTutorial.steps.length - 1) {
      const currentStep = currentTutorial.steps[currentStepIndex];
      completeStep(currentTutorial.id, currentStep.id);
      setCurrentStepIndex(prev => prev + 1);
    } else if (currentTutorial) {
      // Complete the tutorial
      const currentStep = currentTutorial.steps[currentStepIndex];
      completeStep(currentTutorial.id, currentStep.id);
      setCurrentTutorial(null);
      setCurrentStepIndex(0);
      setShowTutorialList(true);
    }
  };

  const previousStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'onboarding': return <BookOpen className="h-4 w-4" />;
      case 'content': return <Lightbulb className="h-4 w-4" />;
      case 'scheduling': return <Calendar className="h-4 w-4" />;
      case 'analytics': return <BarChart3 className="h-4 w-4" />;
      case 'automation': return <Zap className="h-4 w-4" />;
      default: return <HelpCircle className="h-4 w-4" />;
    }
  };

  if (showWelcome) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <Card className="w-full max-w-2xl mx-4">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Welcome to VANTAGE AI! 🎉</CardTitle>
            <p className="text-muted-foreground">
              Let's get you started with a quick tutorial to help you make the most of your new social media management platform.
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button 
                onClick={() => startTutorial(tutorials[0])} 
                className="h-auto p-4 flex flex-col items-center space-y-2"
              >
                <BookOpen className="h-6 w-6" />
                <span>Start Tutorial</span>
                <span className="text-xs opacity-75">10 minutes</span>
              </Button>
              <Button 
                variant="outline" 
                onClick={onClose}
                className="h-auto p-4 flex flex-col items-center space-y-2"
              >
                <X className="h-6 w-6" />
                <span>Skip for Now</span>
                <span className="text-xs opacity-75">I'll explore myself</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (currentTutorial && !showTutorialList) {
    const currentStep = currentTutorial.steps[currentStepIndex];
    const progress = ((currentStepIndex + 1) / currentTutorial.steps.length) * 100;

    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <Card className="w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden">
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {currentTutorial.icon}
                <div>
                  <CardTitle className="text-lg">{currentTutorial.title}</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Step {currentStepIndex + 1} of {currentTutorial.steps.length}
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setShowTutorialList(true)}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <Progress value={progress} className="mt-2" />
          </CardHeader>
          <CardContent className="p-6 overflow-y-auto max-h-[60vh]">
            <div className="space-y-4">
              <div>
                <h3 className="text-xl font-semibold mb-2">{currentStep.title}</h3>
                <p className="text-muted-foreground mb-4">{currentStep.description}</p>
              </div>
              {currentStep.content}
            </div>
          </CardContent>
          <div className="border-t p-4 flex justify-between">
            <Button 
              variant="outline" 
              onClick={previousStep}
              disabled={currentStepIndex === 0}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="text-xs">
                {currentStep.estimatedTime}
              </Badge>
              <Button onClick={nextStep}>
                {currentStepIndex === currentTutorial.steps.length - 1 ? 'Complete' : 'Next'}
                {currentStepIndex === currentTutorial.steps.length - 1 ? (
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

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-6xl mx-4 max-h-[90vh] overflow-hidden">
        <CardHeader className="border-b">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">Tutorials & Help Center</CardTitle>
              <p className="text-muted-foreground">
                Learn how to use VANTAGE AI effectively with our comprehensive tutorials
              </p>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-6 overflow-y-auto max-h-[70vh]">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tutorialsState.map((tutorial) => (
              <Card 
                key={tutorial.id} 
                className={cn(
                  "cursor-pointer transition-all hover:shadow-md",
                  tutorial.completed && "border-green-200 bg-green-50"
                )}
                onClick={() => startTutorial(tutorial)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {tutorial.icon}
                      <Badge variant="outline" className={getDifficultyColor(tutorial.difficulty)}>
                        {tutorial.difficulty}
                      </Badge>
                    </div>
                    {tutorial.completed && (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    )}
                  </div>
                  <CardTitle className="text-lg">{tutorial.title}</CardTitle>
                  <p className="text-sm text-muted-foreground">{tutorial.description}</p>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="flex items-center space-x-1">
                        {getCategoryIcon(tutorial.category)}
                        <span className="capitalize">{tutorial.category}</span>
                      </span>
                      <span className="text-muted-foreground">{tutorial.estimatedTime}</span>
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span>Progress</span>
                        <span>{Math.round(tutorial.progress)}%</span>
                      </div>
                      <Progress value={tutorial.progress} className="h-2" />
                    </div>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{tutorial.steps.filter(s => s.completed).length} of {tutorial.steps.length} steps</span>
                      <Button size="sm" variant="outline" className="h-6 px-2">
                        <Play className="h-3 w-3 mr-1" />
                        Start
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
