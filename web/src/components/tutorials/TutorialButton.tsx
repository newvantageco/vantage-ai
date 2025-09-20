"use client";

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  HelpCircle, 
  BookOpen, 
  Lightbulb, 
  Play,
  CheckCircle
} from 'lucide-react';
import { TutorialSystem } from './TutorialSystem';
import { cn } from '@/lib/utils';

interface TutorialButtonProps {
  variant?: 'default' | 'floating' | 'inline';
  showProgress?: boolean;
  className?: string;
}

export function TutorialButton({ 
  variant = 'default', 
  showProgress = true,
  className 
}: TutorialButtonProps) {
  const [showTutorials, setShowTutorials] = useState(false);
  const [showWelcome, setShowWelcome] = useState(false);
  const [isNewUser, setIsNewUser] = useState(false);

  // Check if user is new (first time visiting) - safely
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const completed = localStorage.getItem('vantage-tutorial-completed');
      setIsNewUser(!completed);
    }
  }, []);

  const handleTutorialClick = () => {
    console.log('Tutorial button clicked!'); // Debug log
    if (isNewUser) {
      setShowWelcome(true);
    } else {
      setShowTutorials(true);
    }
  };

  const handleClose = () => {
    setShowTutorials(false);
    setShowWelcome(false);
    if (isNewUser && typeof window !== 'undefined') {
      localStorage.setItem('vantage-tutorial-completed', 'true');
      setIsNewUser(false);
    }
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
            isNewUser && "animate-pulse",
            className
          )}
        >
          {isNewUser ? (
            <BookOpen className="h-6 w-6" />
          ) : (
            <HelpCircle className="h-6 w-6" />
          )}
        </Button>
        
        {showTutorials && (
          <TutorialSystem onClose={handleClose} />
        )}
        
        {showWelcome && (
          <TutorialSystem onClose={handleClose} showWelcome={true} />
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
            isNewUser && "border-primary bg-primary/5",
            className
          )}
        >
          {isNewUser ? (
            <>
              <BookOpen className="h-4 w-4" />
              <span>Get Started</span>
              <Badge variant="secondary" className="ml-1">
                New
              </Badge>
            </>
          ) : (
            <>
              <HelpCircle className="h-4 w-4" />
              <span>Tutorials</span>
            </>
          )}
        </Button>
        
        {showTutorials && (
          <TutorialSystem onClose={handleClose} />
        )}
        
        {showWelcome && (
          <TutorialSystem onClose={handleClose} showWelcome={true} />
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
          isNewUser && "border-primary bg-primary/5",
          className
        )}
      >
        {isNewUser ? (
          <>
            <BookOpen className="h-4 w-4" />
            <span>Start Tutorial</span>
            <Badge variant="secondary" className="ml-1">
              New User
            </Badge>
          </>
        ) : (
          <>
            <HelpCircle className="h-4 w-4" />
            <span>Help & Tutorials</span>
          </>
        )}
      </Button>
      
      {showTutorials && (
        <TutorialSystem onClose={handleClose} />
      )}
      
      {showWelcome && (
        <TutorialSystem onClose={handleClose} showWelcome={true} />
      )}
    </>
  );
}
