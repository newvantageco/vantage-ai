"use client";

import { useDevAuth } from '@/components/DevAuthWrapper';

// Helper function to check if we should use Clerk
function shouldUseClerk(): boolean {
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  if (!publishableKey) return false;
  return publishableKey.startsWith('pk_test_') || publishableKey.startsWith('pk_live_');
}

export function useAuth() {
  // Always call devAuth to satisfy React rules
  const devAuth = useDevAuth();
  
  // If we don't have valid Clerk keys, return dev auth immediately
  if (!shouldUseClerk()) {
    return {
      isSignedIn: devAuth?.isSignedIn || false,
      isLoaded: devAuth?.isLoaded || false,
      user: devAuth?.user || null,
      signOut: () => devAuth?.signOut?.(),
    };
  }
  
  // If we have valid Clerk keys, we need to use Clerk hooks
  // But we can't call them conditionally, so we need a different approach
  // For now, return dev auth and let the components handle Clerk separately
  return {
    isSignedIn: devAuth?.isSignedIn || false,
    isLoaded: devAuth?.isLoaded || false,
    user: devAuth?.user || null,
    signOut: () => devAuth?.signOut?.(),
  };
}
