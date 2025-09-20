"use client";

import React from 'react';
import { ComposerForm, type ComposerData } from '@/components/composer/composer-form';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';
import { QuickHelp } from '@/components/tutorials';

export default function ComposerPage() {
  const router = useRouter();

  const handleSave = (data: ComposerData) => {
    console.log('Content saved:', data);
    // Content is already saved via API in the form
  };

  const handlePublish = (data: ComposerData) => {
    console.log('Content published:', data);
    // Content is already published via API in the form
    router.push('/content');
  };

  const handleSchedule = (data: ComposerData) => {
    console.log('Content scheduled:', data);
    // Content is already scheduled via API in the form
    router.push('/content');
  };

  return (
    <div className="h-full p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Content Composer</h1>
            <p className="text-muted-foreground mt-2">
              Create, edit, and schedule content across all your social media platforms
            </p>
          </div>
          <QuickHelp context="content-creation" />
        </div>
        
        <ComposerForm
          onSave={handleSave}
          onPublish={handlePublish}
          onSchedule={handleSchedule}
        />
      </div>
    </div>
  );
}