export default function TermsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Terms of Service</h1>
        <div className="prose max-w-none space-y-6">
          <p className="text-sm text-gray-500">
            Last updated: January 29, 2025
          </p>
          
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Acceptance of Terms</h2>
            <p className="text-gray-700 dark:text-gray-300">
              By accessing and using Monkey Coder, you accept and agree to be bound by the terms 
              and provision of this agreement. If you do not agree to abide by the above, please 
              do not use this service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Service Description</h2>
            <p className="text-gray-700 dark:text-gray-300">
              Monkey Coder is an AI-powered development toolkit that provides intelligent code 
              generation, analysis, and assistance through a command-line interface and web platform.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">3. User Responsibilities</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
              <li>Use the service in compliance with all applicable laws and regulations</li>
              <li>Maintain the security of your account credentials</li>
              <li>Not attempt to reverse engineer or abuse the service</li>
              <li>Respect intellectual property rights</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">4. Privacy</h2>
            <p className="text-gray-700 dark:text-gray-300">
              Your privacy is important to us. Please review our Privacy Policy to understand 
              how we collect, use, and protect your information.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Limitation of Liability</h2>
            <p className="text-gray-700 dark:text-gray-300">
              Monkey Coder is provided "as is" without warranty of any kind. We shall not be 
              liable for any direct, indirect, incidental, or consequential damages resulting 
              from the use of our service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Contact Information</h2>
            <p className="text-gray-700 dark:text-gray-300">
              For questions about these Terms of Service, please contact us through our 
              support channels.
            </p>
          </section>

          <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              <strong>Note:</strong> This is a simplified terms of service template. 
              Complete legal terms will be available soon.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}