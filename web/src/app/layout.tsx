import type { Metadata } from 'next';
import { ClerkProvider } from '@clerk/nextjs';
import { PWAProvider } from '@/components/PWAProvider';
import { ThemeProvider } from '@/components/theme-provider';
import { HelpButton } from '@/components/HelpModal';
import { Toaster } from 'react-hot-toast';
import './globals.css';

export const metadata: Metadata = {
	title: 'Vantage AI',
	description: 'AI Marketing SaaS',
	manifest: '/manifest.json',
	themeColor: '#3b82f6',
	viewport: 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no',
	appleWebApp: {
		capable: true,
		statusBarStyle: 'default',
		title: 'Vantage AI',
	},
	formatDetection: {
		telephone: false,
	},
	icons: {
		icon: '/icons/icon-192x192.png',
		apple: '/icons/icon-192x192.png',
	},
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
	return (
		<ClerkProvider>
			<html lang="en">
				<head>
					<link rel="manifest" href="/manifest.json" />
					<meta name="theme-color" content="#3b82f6" />
					<meta name="apple-mobile-web-app-capable" content="yes" />
					<meta name="apple-mobile-web-app-status-bar-style" content="default" />
					<meta name="apple-mobile-web-app-title" content="Vantage AI" />
					<link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
					<meta name="msapplication-TileImage" content="/icons/icon-144x144.png" />
					<meta name="msapplication-TileColor" content="#3b82f6" />
				</head>
				<body>
					<ThemeProvider
						attribute="class"
						defaultTheme="system"
						enableSystem
						disableTransitionOnChange
					>
						<PWAProvider>
							{children}
							<HelpButton />
							<Toaster
								position="top-right"
								toastOptions={{
									duration: 4000,
									style: {
										background: 'hsl(var(--background))',
										color: 'hsl(var(--foreground))',
										border: '1px solid hsl(var(--border))',
									},
									success: {
										iconTheme: {
											primary: 'hsl(var(--primary))',
											secondary: 'hsl(var(--primary-foreground))',
										},
									},
									error: {
										iconTheme: {
											primary: 'hsl(var(--destructive))',
											secondary: 'hsl(var(--destructive-foreground))',
										},
									},
								}}
							/>
						</PWAProvider>
					</ThemeProvider>
				</body>
			</html>
		</ClerkProvider>
	);
}


