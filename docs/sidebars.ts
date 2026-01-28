import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Monkey Coder Documentation Sidebar
 * 
 * Organized following canonical naming convention:
 * - 00-overview: Introduction and getting started
 * - 01-guides: User guides and tutorials
 * - 02-architecture: System architecture and design
 * - 03-api: API documentation
 * - 04-deployment: Deployment guides
 * - 05-development: Contributing and development
 * - 99-archive: Historical and deprecated docs
 */
const sidebars: SidebarsConfig = {
  mainSidebar: [
    {
      type: 'doc',
      id: 'index',
      label: '📚 Documentation Index',
    },
    {
      type: 'category',
      label: '🎯 Overview',
      collapsible: true,
      collapsed: false,
      items: [
        'overview/index',
        'overview/README',
        'overview/roadmap',
        'overview/CLI_DOCS_INDEX',
        'overview/CLI_VISUAL_ROADMAP',
      ],
    },
    {
      type: 'category',
      label: '📖 Guides',
      collapsible: true,
      collapsed: false,
      items: [
        'guides/quick-start',
        'guides/migration-guide',
        'guides/ADVANCED_FEATURES',
        'guides/troubleshooting-guide',
        'guides/billing',
      ],
    },
    {
      type: 'category',
      label: '🏗️ Architecture',
      collapsible: true,
      collapsed: true,
      items: [
        'architecture/agent-os-standards',
        'architecture/monkey_coder_agent',
        'architecture/MONOREPO_QUICK_REFERENCE',
        'architecture/CLI_COMMAND_STRUCTURE',
        'architecture/MODEL_MANIFEST',
        'architecture/MICROSOFT_AGENT_FRAMEWORK_INTEGRATION',
        'architecture/trm-integration',
        'architecture/CLAUDE',
        'architecture/NO-REGEX-ALLOWED-PATTERNS',
      ],
    },
    {
      type: 'category',
      label: '🔌 API',
      collapsible: true,
      collapsed: true,
      items: [
        'api/api-documentation',
        'api/API_ENDPOINTS',
      ],
    },
    {
      type: 'category',
      label: '🚀 Deployment',
      collapsible: true,
      collapsed: true,
      items: [
        'deployment/DEPLOYMENT',
        'deployment/production-deployment-guide',
        'deployment/railway-configuration-quickstart',
        'deployment/railpack-docs-links',
      ],
    },
    {
      type: 'category',
      label: '💻 Development',
      collapsible: true,
      collapsed: true,
      items: [
        'development/contributing',
      ],
    },
  ],
};

export default sidebars;
