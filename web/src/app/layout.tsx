import type { Metadata } from 'next';
import './globals.css';

// Disable static optimisation & ISR while auth is in flux
export const dynamic = 'force-dynamic';
export const revalidate = 0;
export const fetchCache = 'force-no-store';

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
		<html lang="en">
			<head>
				<title>Vantage AI</title>
			</head>
			<body>
				{children}
			</body>
		</html>
	);
}


