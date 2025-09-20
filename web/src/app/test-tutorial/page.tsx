"use client";

import React from 'react';
import { WorkingTutorialButton } from '@/components/tutorials';

export default function TestTutorialPage() {
  return (
    <div className="h-full p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground">Tutorial Test Page</h1>
          <p className="text-muted-foreground mt-2">
            Test the tutorial system functionality
          </p>
        </div>
        
        <div className="space-y-4">
          <div className="p-4 border rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Tutorial Button Variants</h3>
            <div className="flex flex-wrap gap-4">
              <WorkingTutorialButton variant="default" />
              <WorkingTutorialButton variant="inline" />
              <WorkingTutorialButton variant="floating" />
            </div>
          </div>
          
          <div className="p-4 border rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Instructions</h3>
            <ol className="list-decimal list-inside space-y-2 text-sm">
              <li>Click any of the tutorial buttons above</li>
              <li>The tutorial modal should open</li>
              <li>Navigate through the steps using Next/Previous buttons</li>
              <li>Complete the tutorial to test the full flow</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
