import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

/**
 * Enhanced documentation sidebar combining OpenAI and Anthropic best practices
 * Features:
 * - Clear hierarchical structure with logical grouping
 * - Utility CSS classes for consistent styling
 * - Progressive complexity flow
 * - Comprehensive coverage of all documentation areas
 */
const enhancedSidebars: SidebarsConfig = {
  docs: [
    // ==================== FIRST STEPS ====================
    {
      type: 'category',
      label: 'First Steps',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'intro', 
          label: 'Intro to Monkey Coder',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'quick-start', 
          label: 'Get Started',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'installation', 
          label: 'Installation Guide',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'first-project', 
          label: 'Your First Project',
          className: 'flex-1'
        },
      ],
    },

    // ==================== MODELS & PRICING ====================
    {
      type: 'category',
      label: 'Models & Pricing',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'models/choosing-a-model', 
          label: 'Choosing a Model',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'models/models-overview', 
          label: 'Models Overview',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'models/model-inventory', 
          label: 'Complete Model Inventory',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'models/provider-comparison', 
          label: 'Provider Comparison',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'pricing', 
          label: 'Pricing',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'billing', 
          label: 'Billing & Usage',
          className: 'flex-1'
        },
      ],
    },

    // ==================== LEARN ABOUT MONKEY CODER ====================
    {
      type: 'category',
      label: 'Learn About Monkey Coder',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'overview', 
          label: 'Building with Monkey Coder',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'features-overview', 
          label: 'Features Overview',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'quantum-routing', 
          label: 'Quantum Routing',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'context-windows', 
          label: 'Context Windows',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'glossary', 
          label: 'Glossary',
          className: 'flex-1'
        },
      ],
    },

    // ==================== CAPABILITIES ====================
    {
      type: 'category',
      label: 'Capabilities',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'capabilities/quantum-tasks', 
          label: 'Quantum Tasks',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'capabilities/intelligent-routing', 
          label: 'Intelligent Model Routing',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'capabilities/streaming', 
          label: 'Streaming Messages',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'capabilities/batch-processing', 
          label: 'Batch Processing',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'capabilities/multi-agent', 
          label: 'Multi-Agent Orchestration',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'capabilities/context-management', 
          label: 'Context Management',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'capabilities/token-counting', 
          label: 'Token Counting',
          className: 'flex-1'
        },
      ],
    },

    // ==================== TOOLS ====================
    {
      type: 'category',
      label: 'Tools',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'tools/overview', 
          label: 'Overview',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'tools/cli-commands', 
          label: 'CLI Commands',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'tools/implement', 
          label: 'Implement Tool',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'tools/analyze', 
          label: 'Analyze Tool',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'tools/build', 
          label: 'Build Tool',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'tools/test', 
          label: 'Test Tool',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'tools/chat', 
          label: 'Chat Tool',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'tools/custom-tools', 
          label: 'Custom Tools',
          className: 'flex-1'
        },
      ],
    },

    // ==================== MODEL CONTEXT PROTOCOL (MCP) ====================
    {
      type: 'category',
      label: 'Model Context Protocol (MCP)',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'mcp/overview', 
          label: 'MCP Overview',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'mcp/integration', 
          label: 'MCP Integration',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'mcp/servers', 
          label: 'MCP Servers',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'mcp/remote-servers', 
          label: 'Remote MCP Servers',
          className: 'flex-1'
        },
      ],
    },

    // ==================== USE CASES ====================
    {
      type: 'category',
      label: 'Use Cases',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'use-cases/overview', 
          label: 'Overview',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'use-cases/code-generation', 
          label: 'Code Generation',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'use-cases/code-analysis', 
          label: 'Code Analysis',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'use-cases/debugging', 
          label: 'Debugging Assistant',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'use-cases/refactoring', 
          label: 'Code Refactoring',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'use-cases/documentation', 
          label: 'Documentation Generation',
          className: 'flex-1'
        },
      ],
    },

    // ==================== PROMPT ENGINEERING ====================
    {
      type: 'category',
      label: 'Prompt Engineering',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'prompts/overview', 
          label: 'Overview',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'prompts/best-practices', 
          label: 'Best Practices',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'prompts/personas', 
          label: 'Using Personas',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'prompts/templates', 
          label: 'Prompt Templates',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'prompts/examples', 
          label: 'Example Prompts',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'prompts/chain-of-thought', 
          label: 'Chain of Thought',
          className: 'flex-1'
        },
      ],
    },

    // ==================== TEST & EVALUATE ====================
    {
      type: 'category',
      label: 'Test & Evaluate',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'testing/define-success', 
          label: 'Define Success Criteria',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'testing/develop-tests', 
          label: 'Develop Test Cases',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'testing/performance', 
          label: 'Performance Testing',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'testing/benchmarks', 
          label: 'Benchmarks',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'testing/evaluation-tool', 
          label: 'Evaluation Tool',
          className: 'flex-1'
        },
      ],
    },

    // ==================== STRENGTHEN GUARDRAILS ====================
    {
      type: 'category',
      label: 'Strengthen Guardrails',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'guardrails/reduce-hallucinations', 
          label: 'Reduce Hallucinations',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'guardrails/increase-consistency', 
          label: 'Increase Output Consistency',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'guardrails/security', 
          label: 'Security Best Practices',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'guardrails/error-handling', 
          label: 'Error Handling',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'guardrails/validation', 
          label: 'Input Validation',
          className: 'flex-1'
        },
      ],
    },

    // ==================== API REFERENCE ====================
    {
      type: 'category',
      label: 'API Reference',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'api/getting-started', 
          label: 'Getting Started',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'api/authentication', 
          label: 'Authentication',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'api/endpoints', 
          label: 'Endpoints',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'api/execute', 
          label: 'Execute API',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'api/streaming', 
          label: 'Streaming API',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'api/models', 
          label: 'Models API',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'api/errors', 
          label: 'Error Handling',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'openai-response-examples', 
          label: 'Response Examples',
          className: 'flex-1'
        },
      ],
    },

    // ==================== SDK & LIBRARIES ====================
    {
      type: 'category',
      label: 'SDK & Libraries',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        {
          type: 'category',
          label: 'TypeScript SDK',
          className: 'pl-8',
          items: [
            { 
              type: 'doc', 
              id: 'sdk/typescript/quickstart', 
              label: 'Quick Start',
              className: 'flex-1'
            },
            { 
              type: 'doc', 
              id: 'sdk/typescript/client', 
              label: 'Client Reference',
              className: 'flex-1'
            },
            { 
              type: 'doc', 
              id: 'sdk/typescript/examples', 
              label: 'Examples',
              className: 'flex-1'
            },
          ],
        },
        {
          type: 'category',
          label: 'Python SDK',
          className: 'pl-8',
          items: [
            { 
              type: 'doc', 
              id: 'sdk/python/quickstart', 
              label: 'Quick Start',
              className: 'flex-1'
            },
            { 
              type: 'doc', 
              id: 'sdk/python/client', 
              label: 'Client Reference',
              className: 'flex-1'
            },
            { 
              type: 'doc', 
              id: 'sdk/python/examples', 
              label: 'Examples',
              className: 'flex-1'
            },
          ],
        },
      ],
    },

    // ==================== DEPLOYMENT & OPERATIONS ====================
    {
      type: 'category',
      label: 'Deployment & Operations',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'deployment/overview', 
          label: 'Deployment Overview',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'deployment/railway', 
          label: 'Railway Deployment',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'deployment/docker', 
          label: 'Docker Deployment',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'deployment/configuration', 
          label: 'Configuration',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'deployment/monitoring', 
          label: 'Monitoring & Observability',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'deployment/scaling', 
          label: 'Scaling & Performance',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'deployment/security', 
          label: 'Security',
          className: 'flex-1'
        },
      ],
    },

    // ==================== DEVELOPER RESOURCES ====================
    {
      type: 'category',
      label: 'Developer Resources',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'contributing', 
          label: 'Contributing Guide',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'development-workflow', 
          label: 'Development Workflow',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'testing-guide', 
          label: 'Testing Guide',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'agent-os-standards', 
          label: 'Agent OS Standards',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'troubleshooting', 
          label: 'Troubleshooting',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'faq', 
          label: 'FAQ',
          className: 'flex-1'
        },
      ],
    },

    // ==================== LEGAL & COMPLIANCE ====================
    {
      type: 'category',
      label: 'Legal & Compliance',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'legal/privacy-policy', 
          label: 'Privacy Policy',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'legal/terms-of-service', 
          label: 'Terms of Service',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'legal/security-compliance', 
          label: 'Security & Compliance',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'legal/data-protection', 
          label: 'Data Protection',
          className: 'flex-1'
        },
      ],
    },

    // ==================== MIGRATION & CHANGELOG ====================
    {
      type: 'category',
      label: 'Migration & Updates',
      className: 'md-nav__link md-ellipsis pl-4 text-gray-700',
      items: [
        { 
          type: 'doc', 
          id: 'migration-guide', 
          label: 'Migration Guide',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'changelog', 
          label: 'Changelog',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'roadmap', 
          label: 'Product Roadmap',
          className: 'flex-1'
        },
        { 
          type: 'doc', 
          id: 'release-notes', 
          label: 'Release Notes',
          className: 'flex-1'
        },
      ],
    },
  ],
};

export default enhancedSidebars;