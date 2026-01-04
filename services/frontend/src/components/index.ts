/**
 * Barrel export for all components
 * Simplifies imports: import { SiteHeader, SiteFooter, ThemeProvider } from '@/components'
 */

// Error Handling
export { ErrorBoundary } from './ErrorBoundary';

// Layout components
export { default as SiteHeader } from './site-header';
export { default as SiteFooter } from './site-footer';
export { ThemeProvider } from './theme-provider';
export { ThemeToggle } from './theme-toggle';

// Marketing components
export { default as PricingCard } from './pricing-card';
export { default as ColorPalette } from './ColorPalette';
export { default as NeonShowcase } from './NeonShowcase';

// UI components (re-export from ui directory)
export * from './ui';
