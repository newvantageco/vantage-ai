'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Channel, BrandGuide, Campaign, ContentItem } from '@/lib/types';

interface OnboardingWizardProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

interface WizardStep {
  id: string;
  title: string;
  description: string;
  component: React.ComponentType<WizardStepProps>;
  isCompleted: boolean;
  isOptional: boolean;
}

interface WizardStepProps {
  onNext: (data?: any) => void;
  onBack: () => void;
  onSkip: () => void;
  data: any;
  setData: (data: any) => void;
}

export function OnboardingWizard({ isOpen, onClose, onComplete }: OnboardingWizardProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [wizardData, setWizardData] = useState<any>({});
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const steps: WizardStep[] = [
    {
      id: 'channels',
      title: 'Connect Your Channels',
      description: 'Connect your social media accounts to get started',
      component: ConnectChannelsStep,
      isCompleted: false,
      isOptional: false,
    },
    {
      id: 'brand-guide',
      title: 'Set Up Brand Guide',
      description: 'Define your brand voice and guidelines',
      component: BrandGuideStep,
      isCompleted: false,
      isOptional: true,
    },
    {
      id: 'campaign',
      title: 'Create Your First Campaign',
      description: 'Create a campaign to organize your content',
      component: CreateCampaignStep,
      isCompleted: false,
      isOptional: true,
    },
    {
      id: 'schedule',
      title: 'Schedule Your First Post',
      description: 'Schedule your first social media post',
      component: SchedulePostStep,
      isCompleted: false,
      isOptional: false,
    },
  ];

  const handleNext = async (data?: any) => {
    setIsLoading(true);
    
    try {
      // Save step data
      if (data) {
        setWizardData((prev: any) => ({ ...prev, ...data }));
      }

      // Mark current step as completed
      const updatedSteps = [...steps];
      updatedSteps[currentStep].isCompleted = true;

      // Move to next step
      if (currentStep < steps.length - 1) {
        setCurrentStep(currentStep + 1);
      } else {
        // Wizard completed
        await handleWizardComplete();
      }
    } catch (error) {
      console.error('Error in wizard step:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleWizardComplete();
    }
  };

  const handleWizardComplete = async () => {
    try {
      // Save all wizard data
      await saveWizardData();
      
      // Mark onboarding as completed
      localStorage.setItem('onboarding-completed', 'true');
      
      // Close wizard and redirect
      onComplete();
      router.push('/dashboard');
    } catch (error) {
      console.error('Error completing wizard:', error);
    }
  };

  const saveWizardData = async () => {
    // Save channels
    if (wizardData.channels) {
      for (const channel of wizardData.channels) {
        await fetch('/api/v1/channels', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(channel),
        });
      }
    }

    // Save brand guide
    if (wizardData.brandGuide) {
      await fetch('/api/v1/brand-guide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(wizardData.brandGuide),
      });
    }

    // Save campaign
    if (wizardData.campaign) {
      await fetch('/api/v1/campaigns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(wizardData.campaign),
      });
    }

    // Save scheduled post
    if (wizardData.scheduledPost) {
      await fetch('/api/v1/schedules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(wizardData.scheduledPost),
      });
    }
  };

  if (!isOpen) return null;

  const CurrentStepComponent = steps[currentStep].component;
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Welcome to Vantage AI</h2>
              <p className="text-blue-100 mt-1">Let's get you set up in just a few steps</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* Progress bar */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-blue-100 mb-2">
              <span>Step {currentStep + 1} of {steps.length}</span>
              <span>{Math.round(progress)}% Complete</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div 
                className="bg-white h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>

        {/* Step Navigation */}
        <div className="bg-gray-50 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex space-x-4">
              {steps.map((step, index) => (
                <div
                  key={step.id}
                  className={`flex items-center space-x-2 ${
                    index <= currentStep ? 'text-blue-600' : 'text-gray-400'
                  }`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                      index < currentStep
                        ? 'bg-green-500 text-white'
                        : index === currentStep
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-500'
                    }`}
                  >
                    {index < currentStep ? '✓' : index + 1}
                  </div>
                  <span className="text-sm font-medium">{step.title}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Step Content */}
        <div className="p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-900">
              {steps[currentStep].title}
            </h3>
            <p className="text-gray-600 mt-1">
              {steps[currentStep].description}
            </p>
          </div>

          <CurrentStepComponent
            onNext={handleNext}
            onBack={handleBack}
            onSkip={handleSkip}
            data={wizardData}
            setData={setWizardData}
          />
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 flex justify-between">
          <button
            onClick={handleBack}
            disabled={currentStep === 0}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Back
          </button>
          
          <div className="flex space-x-3">
            {steps[currentStep].isOptional && (
              <button
                onClick={handleSkip}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Skip
              </button>
            )}
            
            <button
              onClick={() => handleNext()}
              disabled={isLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Saving...' : currentStep === steps.length - 1 ? 'Complete' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Step 1: Connect Channels
function ConnectChannelsStep({ onNext, data, setData }: WizardStepProps) {
  const [channels, setChannels] = useState<Channel[]>(data.channels || []);
  const [availableProviders, setAvailableProviders] = useState([
    { id: 'meta', name: 'Meta (Facebook & Instagram)', icon: '📘', connected: false },
    { id: 'linkedin', name: 'LinkedIn', icon: '💼', connected: false },
    { id: 'tiktok', name: 'TikTok', icon: '🎵', connected: false },
    { id: 'twitter', name: 'Twitter', icon: '🐦', connected: false },
  ]);

  const handleConnect = async (provider: string) => {
    try {
      // Redirect to OAuth flow
      window.location.href = `/api/v1/oauth/${provider}`;
    } catch (error) {
      console.error('Error connecting channel:', error);
    }
  };

  const handleNext = () => {
    setData({ ...data, channels });
    onNext({ channels });
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {availableProviders.map((provider) => (
          <div
            key={provider.id}
            className={`border rounded-lg p-4 ${
              provider.connected ? 'border-green-500 bg-green-50' : 'border-gray-200'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{provider.icon}</span>
                <div>
                  <h4 className="font-medium text-gray-900">{provider.name}</h4>
                  <p className="text-sm text-gray-500">
                    {provider.connected ? 'Connected' : 'Not connected'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleConnect(provider.id)}
                disabled={provider.connected}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  provider.connected
                    ? 'bg-green-100 text-green-800 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {provider.connected ? 'Connected' : 'Connect'}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 className="font-medium text-blue-900">Why connect channels?</h4>
            <p className="text-sm text-blue-700 mt-1">
              Connecting your social media accounts allows Vantage AI to schedule posts, 
              analyze performance, and manage your content across all platforms.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Step 2: Brand Guide
function BrandGuideStep({ onNext, data, setData }: WizardStepProps) {
  const [brandGuide, setBrandGuide] = useState({
    voice: data.brandGuide?.voice || '',
    audience: data.brandGuide?.audience || '',
    pillars: data.brandGuide?.pillars || '',
  });

  const handleNext = () => {
    setData({ ...data, brandGuide });
    onNext({ brandGuide });
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Brand Voice
          </label>
          <textarea
            value={brandGuide.voice}
            onChange={(e) => setBrandGuide({ ...brandGuide, voice: e.target.value })}
            placeholder="Describe your brand's personality and tone (e.g., professional, friendly, authoritative, playful)"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Audience
          </label>
          <textarea
            value={brandGuide.audience}
            onChange={(e) => setBrandGuide({ ...brandGuide, audience: e.target.value })}
            placeholder="Describe your target audience (e.g., professionals aged 25-40, small business owners, tech enthusiasts)"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Content Pillars
          </label>
          <textarea
            value={brandGuide.pillars}
            onChange={(e) => setBrandGuide({ ...brandGuide, pillars: e.target.value })}
            placeholder="Define your main content themes (e.g., industry insights, product updates, company culture, customer success stories)"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
          />
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <svg className="w-5 h-5 text-yellow-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <div>
            <h4 className="font-medium text-yellow-900">Optional but Recommended</h4>
            <p className="text-sm text-yellow-700 mt-1">
              Setting up your brand guide helps AI generate content that matches your brand's voice and resonates with your audience.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Step 3: Create Campaign
function CreateCampaignStep({ onNext, data, setData }: WizardStepProps) {
  const [campaign, setCampaign] = useState({
    name: data.campaign?.name || '',
    objective: data.campaign?.objective || '',
    startDate: data.campaign?.startDate || '',
    endDate: data.campaign?.endDate || '',
  });

  const handleNext = () => {
    setData({ ...data, campaign });
    onNext({ campaign });
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Campaign Name
          </label>
          <input
            type="text"
            value={campaign.name}
            onChange={(e) => setCampaign({ ...campaign, name: e.target.value })}
            placeholder="e.g., Q1 Product Launch, Holiday Campaign"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Campaign Objective
          </label>
          <textarea
            value={campaign.objective}
            onChange={(e) => setCampaign({ ...campaign, objective: e.target.value })}
            placeholder="What do you want to achieve with this campaign? (e.g., increase brand awareness, drive sales, generate leads)"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={campaign.startDate}
              onChange={(e) => setCampaign({ ...campaign, startDate: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              End Date
            </label>
            <input
              type="date"
              value={campaign.endDate}
              onChange={(e) => setCampaign({ ...campaign, endDate: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <svg className="w-5 h-5 text-green-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 className="font-medium text-green-900">Campaign Benefits</h4>
            <p className="text-sm text-green-700 mt-1">
              Campaigns help you organize your content, track performance, and maintain consistency across your social media presence.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Step 4: Schedule Post
function SchedulePostStep({ onNext, data, setData }: WizardStepProps) {
  const [scheduledPost, setScheduledPost] = useState({
    title: data.scheduledPost?.title || '',
    caption: data.scheduledPost?.caption || '',
    scheduledAt: data.scheduledPost?.scheduledAt || '',
    channelId: data.scheduledPost?.channelId || '',
  });

  const handleNext = () => {
    setData({ ...data, scheduledPost });
    onNext({ scheduledPost });
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Post Title
          </label>
          <input
            type="text"
            value={scheduledPost.title}
            onChange={(e) => setScheduledPost({ ...scheduledPost, title: e.target.value })}
            placeholder="e.g., Welcome to Vantage AI!"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Post Caption
          </label>
          <textarea
            value={scheduledPost.caption}
            onChange={(e) => setScheduledPost({ ...scheduledPost, caption: e.target.value })}
            placeholder="Write your post caption here..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={4}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Schedule Date & Time
            </label>
            <input
              type="datetime-local"
              value={scheduledPost.scheduledAt}
              onChange={(e) => setScheduledPost({ ...scheduledPost, scheduledAt: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Channel
            </label>
            <select
              value={scheduledPost.channelId}
              onChange={(e) => setScheduledPost({ ...scheduledPost, channelId: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select a channel</option>
              <option value="meta">Meta (Facebook & Instagram)</option>
              <option value="linkedin">LinkedIn</option>
              <option value="tiktok">TikTok</option>
              <option value="twitter">Twitter</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <svg className="w-5 h-5 text-purple-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 className="font-medium text-purple-900">You're Almost Done!</h4>
            <p className="text-sm text-purple-700 mt-1">
              Once you schedule your first post, you'll be ready to start using Vantage AI to manage your social media presence.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
