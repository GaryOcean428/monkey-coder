import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Monkey Coder Documentation Sidebars
 * Simplified configuration to only reference existing documentation files
 */
const sidebars: SidebarsConfig = {
  // Main documentation sidebar with existing files only
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'index',
        'quick-start',
        'migration-guide',
      ],
    },
    {
      type: 'category',
      label: 'Core Features',
      items: [
        'quantum-tasks',
        'billing',
        'openai-response-examples',
      ],
    },
    {
      type: 'category',
      label: 'Development',
      items: [
        'contributing',
        'agent-os-standards',
        'railpack-docs-links',
      ],
    },
  ],
};

export default sidebars;
