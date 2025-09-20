import { type Metadata } from 'next'
import { QueryProvider } from '@/providers/QueryProvider'
import { AuthProvider } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/components/theme-provider'
import './globals.css'

export const metadata: Metadata = {
  title: 'VANTAGE AI - Content Management Platform',
  description: 'AI-powered content optimization and scheduling platform',
  keywords: 'content management, AI, social media, scheduling, analytics',
  authors: [{ name: 'VANTAGE AI Team' }],
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
    <html lang="en" className="h-full" suppressHydrationWarning>
      <body className="antialiased h-full bg-background text-foreground">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          themes={["light", "dark", "sky-blue"]}
          disableTransitionOnChange
        >
          <QueryProvider>
            <AuthProvider>
              {children}
            </AuthProvider>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}