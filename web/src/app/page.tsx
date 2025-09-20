"use client";

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Share2, Database, Zap } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();
  const [showDemo, setShowDemo] = useState(false);

  useEffect(() => {
    // Auto-redirect after 3 seconds unless user clicks demo
    const timer = setTimeout(() => {
      if (!showDemo) {
        router.push('/dashboard');
      }
    }, 3000);

    return () => clearTimeout(timer);
  }, [router, showDemo]);

  if (showDemo) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-600 to-green-700 rounded-2xl shadow-lg mb-8">
            <span className="text-white font-bold text-3xl">V</span>
          </div>
          
          <h1 className="text-4xl font-bold text-foreground mb-4">
            VANTAGE AI - Social Media Integration
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Experience our comprehensive social media integration platform
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Share2 className="h-5 w-5" />
                  Publishing
                </CardTitle>
                <CardDescription>
                  Publish to Facebook, LinkedIn, Google My Business
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1 text-left">
                  <li>• Real API integration</li>
                  <li>• Content validation</li>
                  <li>• Scheduled posting</li>
                  <li>• Media support</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  OAuth
                </CardTitle>
                <CardDescription>
                  Secure authentication with social platforms
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1 text-left">
                  <li>• Facebook OAuth</li>
                  <li>• LinkedIn OAuth</li>
                  <li>• Google OAuth</li>
                  <li>• Token management</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Webhooks
                </CardTitle>
                <CardDescription>
                  Real-time engagement tracking
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1 text-left">
                  <li>• Engagement events</li>
                  <li>• Comment tracking</li>
                  <li>• Analytics integration</li>
                  <li>• Error handling</li>
                </ul>
              </CardContent>
            </Card>
          </div>

          <div className="flex gap-4 justify-center">
            <Link href="/social-media-demo">
              <Button size="lg" className="bg-green-600 hover:bg-green-700">
                View Social Media Demo
              </Button>
            </Link>
            <Button 
              variant="outline" 
              size="lg"
              onClick={() => router.push('/dashboard')}
            >
              Go to Dashboard
            </Button>
          </div>

          <div className="mt-8 text-sm text-muted-foreground">
            <p>API Documentation: <a href="http://localhost:8000/docs" target="_blank" className="text-green-600 hover:underline">http://localhost:8000/docs</a></p>
            <p>Frontend: <a href="http://localhost:3000" target="_blank" className="text-green-600 hover:underline">http://localhost:3000</a></p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-green-600 to-green-700 rounded-2xl shadow-lg mb-6 animate-pulse">
          <span className="text-white font-bold text-2xl">V</span>
        </div>
        <p className="text-muted-foreground mb-4">Loading VANTAGE AI...</p>
        <Button 
          variant="outline" 
          onClick={() => setShowDemo(true)}
          className="mt-4"
        >
          View Social Media Integration Demo
        </Button>
      </div>
    </div>
  );
}