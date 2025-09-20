"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  HelpCircle, 
  BookOpen
} from 'lucide-react';
import { WorkingTutorial } from './WorkingTutorial';
import { ComprehensiveTutorial } from './ComprehensiveTutorial';
import { cn } from '@/lib/utils';

interface WorkingTutorialButtonProps {
  variant?: 'default' | 'floating' | 'inline';
  className?: string;
}

export function WorkingTutorialButton({ 
  variant = 'default', 
  className 
}: WorkingTutorialButtonProps) {
  const [showTutorial, setShowTutorial] = useState(false);
  const [showComprehensive, setShowComprehensive] = useState(false);

  const handleTutorialClick = () => {
    console.log('Tutorial button clicked!'); // Debug log
    setShowComprehensive(true);
  };

  const handleClose = () => {
    setShowTutorial(false);
    setShowComprehensive(false);
  };

  if (variant === 'floating') {
    return (
      <>
        <Button
          onClick={handleTutorialClick}
          size="lg"
          className={cn(
            "fixed bottom-6 right-6 z-40 rounded-full shadow-lg hover:shadow-xl transition-all",
            "bg-primary hover:bg-primary/90 text-primary-foreground",
            "h-14 w-14 p-0",
            className
          )}
        >
          <BookOpen className="h-6 w-6" />
        </Button>
        
        {showComprehensive && (
          <ComprehensiveTutorial onClose={handleClose} />
        )}
      </>
    );
  }

  if (variant === 'inline') {
    return (
      <>
        <Button
          onClick={handleTutorialClick}
          variant="outline"
          size="sm"
          className={cn(
            "flex items-center space-x-2",
            className
          )}
        >
          <BookOpen className="h-4 w-4" />
          <span>Get Started</span>
          <Badge variant="secondary" className="ml-1">
            New
          </Badge>
        </Button>
        
        {showComprehensive && (
          <ComprehensiveTutorial onClose={handleClose} />
        )}
      </>
    );
  }

  return (
    <>
      <Button
        onClick={handleTutorialClick}
        variant="outline"
        className={cn(
          "flex items-center space-x-2",
          className
        )}
      >
        <HelpCircle className="h-4 w-4" />
        <span>Help & Tutorials</span>
      </Button>
      
      {showTutorial && (
        <WorkingTutorial onClose={handleClose} />
      )}
    </>
  );
}
