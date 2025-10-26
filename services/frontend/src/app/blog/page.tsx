export default function BlogPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Blog</h1>
        <div className="prose max-w-none">
          <p className="text-lg text-gray-600 mb-8">
            Stay tuned for development insights, AI coding tips, and Monkey Coder updates.
          </p>
          
          <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Coming Soon</h2>
            <p className="text-gray-600 dark:text-gray-400">
              We're working on bringing you valuable content about:
            </p>
            <ul className="mt-4 space-y-2 text-gray-600 dark:text-gray-400">
              <li>• AI-powered development workflows</li>
              <li>• Quantum routing and model selection insights</li>
              <li>• Best practices for CLI-based development</li>
              <li>• Community tutorials and use cases</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}