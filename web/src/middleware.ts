import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Check if Clerk is properly configured
const isClerkConfigured = () => {
  const clerkPublishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  return clerkPublishableKey && 
    clerkPublishableKey !== 'pk_test_development_key_placeholder' &&
    clerkPublishableKey !== 'pk_test_dummy_key_for_development' &&
    !clerkPublishableKey.includes('placeholder') &&
    !clerkPublishableKey.includes('pk_test_xxx') &&
    !clerkPublishableKey.includes('dummy') &&
    clerkPublishableKey !== '';
};

// Define public routes that don't require authentication
const isPublicRoute = (pathname: string) => {
  const publicRoutes = [
    '/',
    '/login',
    '/sign-up',
    '/api/webhooks',
    '/healthz',
    '/offline',
    '/public-calendar',
    '/dashboard',
  ];
  
  return publicRoutes.some(route => 
    pathname === route || pathname.startsWith(route + '/')
  );
};

export default function middleware(request: NextRequest) {
  // Skip middleware entirely in development mode
  if (process.env.NODE_ENV === 'development') {
    return NextResponse.next();
  }
  
  // If Clerk is not configured, allow all routes
  if (!isClerkConfigured()) {
    return NextResponse.next();
  }

  // If it's a public route, allow access
  if (isPublicRoute(request.nextUrl.pathname)) {
    return NextResponse.next();
  }

  // For authenticated routes, redirect to dashboard
  return NextResponse.redirect(new URL('/dashboard', request.url));
}

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};