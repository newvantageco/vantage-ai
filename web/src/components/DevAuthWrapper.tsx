"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';

interface DevUser {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  imageUrl: string;
}

interface DevAuthContextType {
  user: DevUser | null;
  isLoaded: boolean;
  isSignedIn: boolean;
  signOut: () => void;
}

const DevAuthContext = createContext<DevAuthContextType | undefined>(undefined);

export function DevAuthWrapper({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<DevUser | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Simulate loading and auto-login for development
    const timer = setTimeout(() => {
      setUser({
        id: 'dev-user-123',
        email: 'dev@vantage-ai.com',
        firstName: 'Dev',
        lastName: 'User',
        imageUrl: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face'
      });
      setIsLoaded(true);
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  const signOut = () => {
    setUser(null);
  };

  const value: DevAuthContextType = {
    user,
    isLoaded,
    isSignedIn: !!user,
    signOut
  };

  return (
    <DevAuthContext.Provider value={value}>
      {children}
    </DevAuthContext.Provider>
  );
}

export function useDevAuth() {
  const context = useContext(DevAuthContext);
  if (context === undefined) {
    throw new Error('useDevAuth must be used within a DevAuthWrapper');
  }
  return context;
}
