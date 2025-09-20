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

interface SimpleTutorialProps {
  onClose?: () => void;
}

const tutorials = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    description: 'Learn the basics of VANTAGE AI',
    icon: <BookOpen className="h-5 w-5" />,
    steps: [
      'Welcome to VANTAGE AI! This platform helps you manage social media with AI.',
      'Navigate using the sidebar menu on the left.',
      'Connect your social media accounts in the Integrations section.',
      'Create content using the AI Composer.',
      'Schedule posts using the Calendar.',
      'Track performance in Analytics.'
    ]
  },
  {
    id: 'content-creation',
    title: 'AI Content Creation',
    description: 'Create engaging content with AI',
    icon: <Lightbulb className="h-5 w-5" />,
    steps: [
      'Go to the Composer page to create new content.',
      'Enter your topic or idea in the prompt field.',
      'Select your target platform (Facebook, Instagram, LinkedIn).',
      'Click "Generate with AI" to create content.',
      'Review and edit the generated content.',
      'Save as draft or publish immediately.'
    ]
  },
  {
    id: 'scheduling',
    title: 'Smart Scheduling',
    description: 'Schedule posts at optimal times',
    icon: <Calendar className="h-5 w-5" />,
    steps: [
      'Go to the Calendar page to schedule content.',
      'Click on any date to schedule a post.',
      'Select your content and target platforms.',
      'Choose optimal posting times (AI-suggested).',
      'Set up recurring posts for consistency.',
      'Monitor your scheduled content.'
    ]
  },
  {
    id: 'analytics',
    title: 'Analytics & Insights',
    description: 'Track your performance',
    icon: <BarChart3 className="h-5 w-5" />,
    steps: [
      'Visit the Analytics page to see your performance.',
      'View key metrics like views, likes, and engagement.',
      'Analyze which content performs best.',
      'Identify optimal posting times.',
      'Export reports for stakeholders.',
      'Use insights to improve your strategy.'
    ]
  },
  {
    id: 'automation',
    title: 'Automation',
    description: 'Set up automated workflows',
    icon: <Zap className="h-5 w-5" />,
    steps: [
      'Go to the Automation page to set up rules.',
      'Create rules for content approval.',
      'Set up automated posting schedules.',
      'Configure performance-based actions.',
      'Monitor your automated workflows.',
      'Adjust rules based on results.'
    ]
  }
];

export function SimpleTutorial({ onClose }: SimpleTutorialProps) {
  const [selectedTutorial, setSelectedTutorial] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);

  const selectedTutorialData = tutorials.find(t => t.id === selectedTutorial);

  if (selectedTutorialData) {
    const isLastStep = currentStep >= selectedTutorialData.steps.length - 1;
    
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <Card className="w-full max-w-2xl mx-4">
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {selectedTutorialData.icon}
                <div>
                  <CardTitle className="text-lg">{selectedTutorialData.title}</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Step {currentStep + 1} of {selectedTutorialData.steps.length}
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setSelectedTutorial(null)}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm">{selectedTutorialData.steps[currentStep]}</p>
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
                {selectedTutorialData.steps.length} steps
              </Badge>
              <Button onClick={() => {
                if (isLastStep) {
                  setSelectedTutorial(null);
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

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden">
        <CardHeader className="border-b">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">Tutorials & Help</CardTitle>
              <p className="text-muted-foreground">
                Learn how to use VANTAGE AI effectively
              </p>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-6 overflow-y-auto max-h-[70vh]">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tutorials.map((tutorial) => (
              <Card 
                key={tutorial.id} 
                className="cursor-pointer transition-all hover:shadow-md hover:bg-muted/50"
                onClick={() => setSelectedTutorial(tutorial.id)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center space-x-2">
                    {tutorial.icon}
                    <Badge variant="outline" className="bg-green-100 text-green-800">
                      Beginner
                    </Badge>
                  </div>
                  <CardTitle className="text-lg">{tutorial.title}</CardTitle>
                  <p className="text-sm text-muted-foreground">{tutorial.description}</p>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">
                      {tutorial.steps.length} steps
                    </span>
                    <Button size="sm" variant="outline" className="h-6 px-2">
                      Start
                    </Button>
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
