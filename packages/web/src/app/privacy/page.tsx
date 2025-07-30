export default function PrivacyPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>
        <div className="prose max-w-none space-y-6">
          <p className="text-sm text-gray-500">
            Last updated: January 29, 2025
          </p>
          
          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Information We Collect</h2>
            <div className="space-y-3">
              <h3 className="text-lg font-medium">Account Information</h3>
              <p className="text-gray-700 dark:text-gray-300">
                We collect information you provide directly to us, such as when you create an 
                account, including your name, email address, and authentication credentials.
              </p>
              
              <h3 className="text-lg font-medium">Usage Data</h3>
              <p className="text-gray-700 dark:text-gray-300">
                We collect information about how you use our service, including commands executed, 
                response times, and usage patterns to improve our AI models and service quality.
              </p>
              
              <h3 className="text-lg font-medium">Code and Content</h3>
              <p className="text-gray-700 dark:text-gray-300">
                When you use our AI assistance features, we process the code and prompts you provide 
                to generate responses. This data is used solely to provide the requested service.
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">2. How We Use Your Information</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
              <li>Provide and maintain our service</li>
              <li>Process and respond to your requests</li>
              <li>Improve our AI models and service quality</li>
              <li>Communicate with you about your account and our service</li>
              <li>Ensure the security and integrity of our platform</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">3. Data Security</h2>
            <p className="text-gray-700 dark:text-gray-300">
              We implement appropriate technical and organizational measures to protect your 
              personal information against unauthorized access, alteration, disclosure, or destruction. 
              This includes encryption, secure transmission protocols, and access controls.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibent mb-4">4. Data Sharing</h2>
            <p className="text-gray-700 dark:text-gray-300">
              We do not sell, trade, or otherwise transfer your personal information to third parties 
              except as described in this policy. We may share data with:
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1 text-gray-700 dark:text-gray-300">
              <li>AI model providers for processing your requests</li>
              <li>Service providers who assist in operating our platform</li>
              <li>Legal authorities when required by law</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Data Retention</h2>
            <p className="text-gray-700 dark:text-gray-300">
              We retain your personal information only as long as necessary to provide our services 
              and fulfill the purposes outlined in this policy. Usage data may be retained in 
              aggregated, anonymized form for service improvement purposes.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Your Rights</h2>
            <p className="text-gray-700 dark:text-gray-300">
              You have the right to access, update, or delete your personal information. 
              You may also request to export your data or restrict processing. Contact us 
              to exercise these rights.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">7. Changes to This Policy</h2>
            <p className="text-gray-700 dark:text-gray-300">
              We may update this privacy policy from time to time. We will notify you of any 
              significant changes by posting the new policy on this page and updating the 
              "last updated" date.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">8. Contact Us</h2>
            <p className="text-gray-700 dark:text-gray-300">
              If you have any questions about this Privacy Policy, please contact us through 
              our support channels.
            </p>
          </section>

          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              <strong>Note:</strong> This is a comprehensive privacy policy template. 
              Final legal terms will be reviewed by legal counsel before production deployment.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}