'use client';

import { useEffect, useState, createContext, useContext, ReactNode } from 'react';
import { 
  isPWAEnabled, 
  registerServiceWorker, 
  isRunningAsPWA,
  listenForInstallPrompt,
  markAppAsInstalled,
  trackPWAInstall,
  listenForSWUpdate
} from '@/lib/pwa';

interface PWAContextType {
  isPWAEnabled: boolean;
  isRunningAsPWA: boolean;
  isInstalled: boolean;
  installPrompt: any;
  showInstallPrompt: boolean;
  installApp: () => Promise<void>;
  updateAvailable: boolean;
  updateApp: () => Promise<void>;
}

const PWAContext = createContext<PWAContextType | undefined>(undefined);

export const usePWA = () => {
  const context = useContext(PWAContext);
  if (context === undefined) {
    throw new Error('usePWA must be used within a PWAProvider');
  }
  return context;
};

interface PWAProviderProps {
  children: ReactNode;
}

export function PWAProvider({ children }: PWAProviderProps) {
  const [isInstalled, setIsInstalled] = useState(false);
  const [installPrompt, setInstallPrompt] = useState<any>(null);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [updateAvailable, setUpdateAvailable] = useState(false);

  const pwaEnabled = isPWAEnabled();
  const runningAsPWA = isRunningAsPWA();

  useEffect(() => {
    if (!pwaEnabled) return;

    // Register service worker
    registerServiceWorker().then((registration) => {
      if (registration) {
        console.log('Service Worker registered successfully');
      }
    });

    // Check if app is already installed
    setIsInstalled(runningAsPWA);

    // Listen for install prompt
    const removeInstallListener = listenForInstallPrompt((prompt) => {
      setInstallPrompt(prompt);
      setShowInstallPrompt(true);
    });

    // Listen for service worker updates
    const removeUpdateListener = listenForSWUpdate(() => {
      setUpdateAvailable(true);
    });

    return () => {
      removeInstallListener();
      removeUpdateListener();
    };
  }, [pwaEnabled, runningAsPWA]);

  const installApp = async () => {
    if (!installPrompt) return;

    try {
      await installPrompt.prompt();
      const { outcome } = await installPrompt.userChoice;
      
      if (outcome === 'accepted') {
        markAppAsInstalled();
        trackPWAInstall();
        setIsInstalled(true);
        setShowInstallPrompt(false);
        setInstallPrompt(null);
      }
    } catch (error) {
      console.error('Failed to install app:', error);
    }
  };

  const updateApp = async () => {
    try {
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.getRegistration();
        if (registration) {
          await registration.update();
          window.location.reload();
        }
      }
    } catch (error) {
      console.error('Failed to update app:', error);
    }
  };

  const value: PWAContextType = {
    isPWAEnabled: pwaEnabled,
    isRunningAsPWA: runningAsPWA,
    isInstalled,
    installPrompt,
    showInstallPrompt,
    installApp,
    updateAvailable,
    updateApp,
  };

  return (
    <PWAContext.Provider value={value}>
      {children}
      {pwaEnabled && <PWAInstallPrompt />}
      {pwaEnabled && <PWAUpdatePrompt />}
    </PWAContext.Provider>
  );
}

// Install prompt component
function PWAInstallPrompt() {
  const { showInstallPrompt, installApp, isInstalled } = usePWA();
  const [dismissed, setDismissed] = useState(false);

  if (!showInstallPrompt || isInstalled || dismissed) {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 right-4 z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-4 max-w-sm mx-auto">
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-gray-900">
            Install Vantage AI
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            Add to your home screen for quick access and offline support.
          </p>
          <div className="mt-3 flex space-x-2">
            <button
              onClick={installApp}
              className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-md hover:bg-blue-700 transition-colors"
            >
              Install
            </button>
            <button
              onClick={() => setDismissed(true)}
              className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
            >
              Not now
            </button>
          </div>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}

// Update prompt component
function PWAUpdatePrompt() {
  const { updateAvailable, updateApp } = usePWA();
  const [dismissed, setDismissed] = useState(false);

  if (!updateAvailable || dismissed) {
    return null;
  }

  return (
    <div className="fixed top-4 left-4 right-4 z-50 bg-green-50 border border-green-200 rounded-lg shadow-lg p-4 max-w-sm mx-auto">
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-green-900">
            Update Available
          </h3>
          <p className="text-sm text-green-700 mt-1">
            A new version of Vantage AI is available.
          </p>
          <div className="mt-3 flex space-x-2">
            <button
              onClick={updateApp}
              className="text-sm bg-green-600 text-white px-3 py-1.5 rounded-md hover:bg-green-700 transition-colors"
            >
              Update
            </button>
            <button
              onClick={() => setDismissed(true)}
              className="text-sm text-green-600 hover:text-green-800 transition-colors"
            >
              Later
            </button>
          </div>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="flex-shrink-0 text-green-400 hover:text-green-600 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}
