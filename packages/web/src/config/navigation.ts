/**
 * Shared Navigation Configuration
 * Centralizes navigation data to eliminate duplication across components
 */

export interface NavigationItem {
  name: string;
  href: string;
  external?: boolean;
}

export interface SocialItem extends NavigationItem {
  icon: string; // Will be imported from lucide-react
}

export interface NavigationConfig {
  main: NavigationItem[];
  product: NavigationItem[];
  company: NavigationItem[];
  legal: NavigationItem[];
  social: SocialItem[];
}

/**
 * Main navigation items used in headers
 * Consolidated from marketing/header.tsx and site-header.tsx
 */
export const mainNavigation: NavigationItem[] = [
  { name: 'Getting Started', href: '/getting-started' },
  { name: 'Features', href: '/#features' },
  { name: 'Pricing', href: '/pricing' },
  { name: 'Docs', href: '/docs' }, // Standardized to /docs (not /docs/cli)
  { name: 'API Keys', href: '/api-keys' },
  { name: 'Contact', href: '/contact' },
];

/**
 * Product navigation items for footers
 */
export const productNavigation: NavigationItem[] = [
  { name: 'Features', href: '/#features' },
  { name: 'Pricing', href: '/pricing' },
  { name: 'Documentation', href: '/docs' },
  { name: 'Projects', href: '/projects' },
  { name: 'Blog', href: '/blog' }, // Updated from changelog to blog (which exists)
];

/**
 * Company navigation items for footers
 */
export const companyNavigation: NavigationItem[] = [
  { name: 'Blog', href: '/blog' }, // Updated: blog exists, about/careers don't
  { name: 'Contact', href: '/contact' },
];

/**
 * Legal navigation items for footers  
 */
export const legalNavigation: NavigationItem[] = [
  { name: 'Privacy', href: '/privacy' },
  { name: 'Terms', href: '/terms' },
  // Removed 'Security' as /security page doesn't exist
];

/**
 * Social media links
 */
export const socialNavigation: SocialItem[] = [
  {
    name: 'GitHub',
    href: 'https://github.com/GaryOcean428/monkey-coder',
    icon: 'Github',
    external: true,
  },
  {
    name: 'Twitter',
    href: 'https://twitter.com/monkeycoder',
    icon: 'Twitter',
    external: true,
  },
];

/**
 * Complete navigation configuration
 */
export const navigationConfig: NavigationConfig = {
  main: mainNavigation,
  product: productNavigation,
  company: companyNavigation,
  legal: legalNavigation,
  social: socialNavigation,
};

/**
 * Unified navigation for site header (now includes all essential items)
 * Replaces both simpleNavigation and mainNavigation to eliminate duplication
 */
export const unifiedNavigation: NavigationItem[] = [
  { name: 'Getting Started', href: '/getting-started' },
  { name: 'Features', href: '/#features' },
  { name: 'Pricing', href: '/pricing' },
  { name: 'Docs', href: '/docs' },
  { name: 'API Keys', href: '/api-keys' },
  { name: 'Contact', href: '/contact' },
];

/**
 * @deprecated Use unifiedNavigation instead
 * Kept for backward compatibility during transition
 */
export const simpleNavigation: NavigationItem[] = unifiedNavigation;