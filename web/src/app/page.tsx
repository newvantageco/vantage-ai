// Phase 2: Progressive Component Testing
// Start with minimal page to isolate clientModules error

export default function Home() {
	return (
		<div className="min-h-screen flex items-center justify-center bg-gray-50">
			<div className="text-center">
				<h1 className="text-4xl font-bold text-gray-900 mb-4">
					Vantage AI
				</h1>
				<p className="text-gray-600 mb-8">
					Minimal test page - Phase 2 of clientModules debugging
				</p>
				<div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
					✅ Page loaded successfully without clientModules error
				</div>
			</div>
		</div>
	);
}


