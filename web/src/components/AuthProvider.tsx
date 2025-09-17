'use client'

import { ClerkProvider } from '@clerk/nextjs'
import { ReactNode } from 'react'

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  return (
    <ClerkProvider
      publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      appearance={{
        elements: {
          formButtonPrimary: 'bg-blue-600 hover:bg-blue-700 text-white',
          card: 'shadow-lg border border-gray-200',
          headerTitle: 'text-gray-900 font-semibold',
          headerSubtitle: 'text-gray-600',
          socialButtonsBlockButton: 'border border-gray-300 hover:bg-gray-50',
          formFieldInput: 'border border-gray-300 rounded-md px-3 py-2',
          footerActionLink: 'text-blue-600 hover:text-blue-700',
        },
        variables: {
          colorPrimary: '#3b82f6',
          colorBackground: '#ffffff',
          colorInputBackground: '#ffffff',
          colorInputText: '#000000',
        },
      }}
    >
      {children}
    </ClerkProvider>
  )
}