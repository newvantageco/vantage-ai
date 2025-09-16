import Link from 'next/link';

export default function Home() {
	return (
		<main className="p-6 min-h-screen bg-background">
			<header className="flex justify-between items-center mb-8">
				<h1 className="text-3xl font-bold text-foreground">Vantage AI</h1>
				<div className="text-sm text-gray-500">Welcome to Vantage AI</div>
			</header>
			<nav className="mt-4">
				<Link 
					href="/calendar"
					className="inline-block bg-secondary hover:bg-secondary/80 text-secondary-foreground px-4 py-2 rounded-2xl shadow-card transition-all hover:shadow-lg"
				>
					Calendar
				</Link>
			</nav>
		</main>
	);
}


