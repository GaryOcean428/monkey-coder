import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';
import enhancedSidebars from './sidebars.enhanced';
import roadmapSidebars from './sidebars.roadmap';

/**
 * Monkey Coder Documentation Sidebars
 * Combining best practices from OpenAI and Anthropic documentation:
 * 
 * OpenAI Patterns:
 * - Clear hierarchical structure with progressive complexity
 * - Logical grouping of related topics
 * - md-nav__link and md-ellipsis classes for navigation styling
 * 
 * Anthropic Patterns:
 * - Utility CSS classes (pl-4, text-gray-700, flex-1)
 * - Comprehensive category organization
 * - Clear separation of concerns (First Steps, Models, Tools, etc.)
 */
const sidebars: SidebarsConfig = {
  // Enhanced documentation sidebar with utility classes
  ...enhancedSidebars,
  
  // Roadmap documentation (separate plugin instance)
  ...roadmapSidebars,
  
  // Legacy sidebar for backward compatibility
  tutorialSidebar: [
    'quick-start',
    'openai-response-examples',
    'quantum-tasks',
    'billing',
    'migration-guide',
  ],
};

export default sidebars;
