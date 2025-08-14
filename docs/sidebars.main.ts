import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

/**
 * Main documentation sidebar following OpenAI Agents Python documentation best practices
 * Structure: Getting Started → Core Concepts → Advanced Features → Reference → Resources
 */
const sidebars: SidebarsConfig = {
  docs: [
    // Getting Started
    {
      type: 'category',
      label: 'Getting Started',
      className: 'md-nav__link md-ellipsis',
      items: [
        { type: 'doc', id: 'quick-start', label: 'Quick Start' },
        { type: 'doc', id: 'installation', label: 'Installation' },
        { type: 'doc', id: 'first-project', label: 'Your First Project' },
        { type: 'doc', id: 'migration-guide', label: 'Migration Guide' },
      ],
    },

    // Core Concepts
    {
      type: 'category',
      label: 'Core Concepts',
      className: 'md-nav__link md-ellipsis',
      items: [
        { type: 'doc', id: 'agents', label: 'Agents' },
        { type: 'doc', id: 'personas', label: 'Personas' },
        { type: 'doc', id: 'orchestration', label: 'Orchestration' },
        { type: 'doc', id: 'quantum-tasks', label: 'Quantum Tasks' },
        { type: 'doc', id: 'routing', label: 'Model Routing' },
      ],
    },

    // CLI Reference
    {
      type: 'category',
      label: 'CLI Reference',
      className: 'md-nav__link md-ellipsis',
      items: [
        { type: 'doc', id: 'cli/commands', label: 'Commands' },
        { type: 'doc', id: 'cli/implement', label: 'Implement' },
        { type: 'doc', id: 'cli/analyze', label: 'Analyze' },
        { type: 'doc', id: 'cli/build', label: 'Build' },
        { type: 'doc', id: 'cli/test', label: 'Test' },
        { type: 'doc', id: 'cli/chat', label: 'Chat' },
        { type: 'doc', id: 'cli/auth', label: 'Authentication' },
        { type: 'doc', id: 'cli/usage', label: 'Usage Tracking' },
        { type: 'doc', id: 'cli/mcp', label: 'MCP Commands' },
      ],
    },

    // API Reference
    {
      type: 'category',
      label: 'API Reference',
      className: 'md-nav__link md-ellipsis',
      items: [
        { type: 'doc', id: 'api/overview', label: 'Overview' },
        { type: 'doc', id: 'api/execute', label: 'Execute Endpoint' },
        { type: 'doc', id: 'api/streaming', label: 'Streaming' },
        { type: 'doc', id: 'api/models', label: 'Models' },
        { type: 'doc', id: 'api/providers', label: 'Providers' },
        { type: 'doc', id: 'api/billing', label: 'Billing API' },
        { type: 'doc', id: 'api/capabilities', label: 'Capabilities' },
        { type: 'doc', id: 'api/health', label: 'Health Checks' },
        { type: 'doc', id: 'openai-response-examples', label: 'Response Examples' },
      ],
    },

    // Advanced Features
    {
      type: 'category',
      label: 'Advanced Features',
      className: 'md-nav__link md-ellipsis',
      items: [
        { type: 'doc', id: 'multi-agent', label: 'Multi-Agent Orchestration' },
        { type: 'doc', id: 'context-management', label: 'Context Management' },
        { type: 'doc', id: 'guardrails', label: 'Guardrails' },
        { type: 'doc', id: 'tracing', label: 'Tracing' },
        { type: 'doc', id: 'mcp-integration', label: 'MCP Integration' },
        { type: 'doc', id: 'handoffs', label: 'Agent Handoffs' },
        { type: 'doc', id: 'tools', label: 'Custom Tools' },
      ],
    },

    // SDK & Integration
    {
      type: 'category',
      label: 'SDK & Integration',
      className: 'md-nav__link md-ellipsis',
      items: [
        {
          type: 'category',
          label: 'TypeScript SDK',
          items: [
            { type: 'doc', id: 'sdk/ts/installation', label: 'Installation' },
            { type: 'doc', id: 'sdk/ts/client', label: 'Client' },
            { type: 'doc', id: 'sdk/ts/examples', label: 'Examples' },
          ],
        },
        {
          type: 'category',
          label: 'Python SDK',
          items: [
            { type: 'doc', id: 'sdk/python/installation', label: 'Installation' },
            { type: 'doc', id: 'sdk/python/client', label: 'Client' },
            { type: 'doc', id: 'sdk/python/examples', label: 'Examples' },
          ],
        },
        { type: 'doc', id: 'integration-patterns', label: 'Integration Patterns' },
      ],
    },

    // Deployment
    {
      type: 'category',
      label: 'Deployment',
      className: 'md-nav__link md-ellipsis',
      items: [
        { type: 'doc', id: 'deployment/railway', label: 'Railway Deployment' },
        { type: 'doc', id: 'deployment/docker', label: 'Docker' },
        { type: 'doc', id: 'deployment/configuration', label: 'Configuration' },
        { type: 'doc', id: 'deployment/monitoring', label: 'Monitoring' },
        { type: 'doc', id: 'deployment/scaling', label: 'Scaling' },
      ],
    },

    // Development
    {
      type: 'category',
      label: 'Development',
      className: 'md-nav__link md-ellipsis',
      items: [
        { type: 'doc', id: 'contributing', label: 'Contributing' },
        { type: 'doc', id: 'development-workflow', label: 'Development Workflow' },
        { type: 'doc', id: 'testing-strategies', label: 'Testing' },
        { type: 'doc', id: 'agent-os-standards', label: 'Agent OS Standards' },
        { type: 'doc', id: 'troubleshooting', label: 'Troubleshooting' },
      ],
    },

    // Resources
    {
      type: 'category',
      label: 'Resources',
      className: 'md-nav__link md-ellipsis',
      items: [
        { type: 'doc', id: 'billing', label: 'Billing & Pricing' },
        { type: 'doc', id: 'models-inventory', label: 'Model Inventory' },
        { type: 'doc', id: 'performance-benchmarks', label: 'Performance Benchmarks' },
        { type: 'doc', id: 'security', label: 'Security' },
        { type: 'doc', id: 'changelog', label: 'Changelog' },
        { type: 'doc', id: 'faq', label: 'FAQ' },
      ],
    },

    // External Links
    {
      type: 'category',
      label: 'Links',
      className: 'md-nav__link md-ellipsis',
      items: [
        {
          type: 'link',
          label: 'GitHub',
          href: 'https://github.com/GaryOcean428/monkey-coder',
        },
        {
          type: 'link',
          label: 'PyPI',
          href: 'https://pypi.org/project/monkey-coder-core/',
        },
        {
          type: 'link',
          label: 'npm',
          href: 'https://www.npmjs.com/package/monkey-coder-cli',
        },
      ],
    },
  ],

  // API-specific sidebar for detailed API documentation
  api: [
    { type: 'doc', id: 'api/overview', label: 'API Overview' },
    {
      type: 'category',
      label: 'Endpoints',
      className: 'md-nav__link md-ellipsis',
      items: [
        { type: 'doc', id: 'api/v1/execute', label: 'POST /v1/execute' },
        { type: 'doc', id: 'api/v1/chat', label: 'POST /v1/chat' },
        { type: 'doc', id: 'api/v1/capabilities', label: 'GET /v1/capabilities' },
        { type: 'doc', id: 'api/v1/models', label: 'GET /v1/models' },
        { type: 'doc', id: 'api/v1/health', label: 'GET /v1/health' },
        { type: 'doc', id: 'api/v1/usage', label: 'GET /v1/usage' },
      ],
    },
    {
      type: 'category',
      label: 'Authentication',
      className: 'md-nav__link md-ellipsis',
      items: [
        { type: 'doc', id: 'api/auth/overview', label: 'Overview' },
        { type: 'doc', id: 'api/auth/api-keys', label: 'API Keys' },
        { type: 'doc', id: 'api/auth/jwt', label: 'JWT Tokens' },
        { type: 'doc', id: 'api/auth/oauth', label: 'OAuth' },
      ],
    },
    {
      type: 'category',
      label: 'Data Models',
      className: 'md-nav__link md-ellipsis',
      items: [
        { type: 'doc', id: 'api/models/request', label: 'Request Models' },
        { type: 'doc', id: 'api/models/response', label: 'Response Models' },
        { type: 'doc', id: 'api/models/errors', label: 'Error Models' },
      ],
    },
    {
      type: 'category',
      label: 'Examples',
      className: 'md-nav__link md-ellipsis',
      items: [
        { type: 'doc', id: 'api/examples/curl', label: 'cURL' },
        { type: 'doc', id: 'api/examples/typescript', label: 'TypeScript' },
        { type: 'doc', id: 'api/examples/python', label: 'Python' },
        { type: 'doc', id: 'api/examples/streaming', label: 'Streaming' },
      ],
    },
  ],
};

export default sidebars;