'use client';

import { useEffect, useState } from 'react';

export default function OfflinePage() {
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    // Check initial status
    setIsOnline(navigator.onLine);

    // Listen for online/offline events
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleRetry = () => {
    if (isOnline) {
      window.location.href = '/';
    } else {
      window.location.reload();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {/* Offline Icon */}
        <div className="mx-auto w-24 h-24 bg-gray-200 rounded-full flex items-center justify-center mb-6">
          <svg
            className="w-12 h-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192L5.636 18.364M12 2.25a9.75 9.75 0 100 19.5 9.75 9.75 0 000-19.5z"
            />
          </svg>
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          You're Offline
        </h1>

        {/* Description */}
        <p className="text-gray-600 mb-8">
          {isOnline
            ? 'Connection restored! You can now continue using Vantage AI.'
            : 'It looks like you\'re not connected to the internet. Some features may not be available.'}
        </p>

        {/* Status Indicator */}
        <div className="flex items-center justify-center mb-8">
          <div
            className={`w-3 h-3 rounded-full mr-2 ${
              isOnline ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="text-sm text-gray-600">
            {isOnline ? 'Online' : 'Offline'}
          </span>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={handleRetry}
            className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            {isOnline ? 'Continue to App' : 'Try Again'}
          </button>

          <button
            onClick={() => window.history.back()}
            className="w-full bg-gray-200 text-gray-800 px-6 py-3 rounded-lg font-medium hover:bg-gray-300 transition-colors"
          >
            Go Back
          </button>
        </div>

        {/* Offline Features Info */}
        {!isOnline && (
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h3 className="text-sm font-medium text-blue-900 mb-2">
              Available Offline
            </h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• View cached content</li>
              <li>• Access previously loaded pages</li>
              <li>• Basic navigation</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
