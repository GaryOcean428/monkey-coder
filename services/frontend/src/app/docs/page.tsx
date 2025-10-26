export default function DocsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Documentation</h1>
        <div className="prose max-w-none">
          <p className="text-lg text-gray-600 mb-8">
            Comprehensive documentation for Monkey Coder is coming soon.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4">Quick Links</h2>
          <ul className="space-y-2">
            <li>
              <a href="/api/docs" className="text-blue-600 hover:underline">
                API Documentation (Swagger)
              </a>
            </li>
            <li>
              <a href="/api/redoc" className="text-blue-600 hover:underline">
                API Documentation (ReDoc)
              </a>
            </li>
            <li>
              <a href="/health" className="text-blue-600 hover:underline">
                System Health Check
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}