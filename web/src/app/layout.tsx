import { type Metadata } from 'next'
import {
  ClerkProvider,
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from '@clerk/nextjs'
import './globals.css'

export const metadata: Metadata = {
  title: 'VANTAGE AI - Content Management Platform',
  description: 'AI-powered content optimization and scheduling platform',
  keywords: 'content management, AI, social media, scheduling, analytics',
  authors: [{ name: 'VANTAGE AI Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
  openGraph: {
    title: 'VANTAGE AI - Content Management Platform',
    description: 'AI-powered content optimization and scheduling platform',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'VANTAGE AI - Content Management Platform',
    description: 'AI-powered content optimization and scheduling platform',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <ClerkProvider>
      <html lang="en" className="h-full">
        <body className="antialiased h-full bg-gray-50" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>
          <header className="flex justify-between items-center p-4 gap-4 h-16 bg-white shadow-sm border-b">
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-gray-900">VANTAGE AI</h1>
            </div>
            <div className="flex items-center gap-4">
              <SignedOut>
                <SignInButton mode="modal">
                  <button className="bg-[#6c47ff] text-white rounded-full font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 cursor-pointer hover:bg-[#5a3ae6] transition-colors">
                    Sign In
                  </button>
                </SignInButton>
                <SignUpButton mode="modal">
                  <button className="bg-green-500 text-white rounded-full font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 cursor-pointer hover:bg-green-600 transition-colors">
                    Sign Up
                  </button>
                </SignUpButton>
              </SignedOut>
              <SignedIn>
                <UserButton 
                  appearance={{
                    elements: {
                      avatarBox: "w-10 h-10"
                    }
                  }}
                />
              </SignedIn>
            </div>
          </header>
          <main className="flex-1">
            {children}
          </main>
        </body>
      </html>
    </ClerkProvider>
  )
}