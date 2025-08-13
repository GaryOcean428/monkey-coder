import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

// Sidebar for the Roadmap docs plugin instance
const sidebars: SidebarsConfig = {
  roadmap: [
    { type: 'doc', id: 'index', label: 'Roadmap Overview' },

    {
      type: 'category',
      label: 'Overview',
      items: ['executive-summary', 'technical-architecture'],
    },
    {
      type: 'category',
      label: 'Models and Compliance',
      items: ['models-compliance-and-inventory'],
    },
    {
      type: 'category',
      label: 'Status and Milestones',
      items: ['milestones-completed', 'current-development'],
    },
    {
      type: 'category',
      label: 'Phase Details',
      items: ['phase-1-5-technical-debt-security', 'phase-1-6-auth-unification'],
    },
    {
      type: 'category',
      label: 'Achievements and Backlog',
      items: ['technical-achievements', 'backlog-and-priorities'],
    },
    {
      type: 'category',
      label: 'MCP & Publishing',
      items: ['mcp-integration', 'publishing'],
    },
    {
      type: 'category',
      label: 'Web Frontend & Deployment',
      items: ['web-frontend-and-deployment'],
    },
    {
      type: 'category',
      label: 'Future Plans',
      items: ['future-roadmap'],
    },
    {
      type: 'category',
      label: 'Tracking and Specs',
      items: ['task-tracking', 'technical-specifications', 'api-documentation-standards'],
    },
    {
      type: 'category',
      label: 'Implementation & Workflow',
      items: ['implementation-guidelines', 'development-workflow'],
    },
    {
      type: 'category',
      label: 'Testing & Quality',
      items: ['testing-strategies', 'quality-assurance', 'performance-benchmarks'],
    },
    {
      type: 'category',
      label: 'Deployment & Infra',
      items: ['deployment-strategies'],
    },
    {
      type: 'category',
      label: 'Integrations & Migration',
      items: ['integration-patterns', 'migration-strategies'],
    },
    {
      type: 'category',
      label: 'Resources & Community',
      items: ['educational-resources', 'resource-requirements', 'community'],
    },
    {
      type: 'category',
      label: 'Risk & References',
      items: ['risk-assessment', 'references'],
    },
    {
      type: 'category',
      label: 'Appendices & Document Meta',
      items: ['appendices', 'document-metadata'],
    },
  ],
};

export default sidebars;
