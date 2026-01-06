/**
 * Barrel export for all components
 * Simplifies imports: import { SiteHeader, SiteFooter, ThemeProvider } from '@/components'
 */

// Error Handling
export { ErrorBoundary } from './ErrorBoundary';

// Accessibility
export { VisuallyHidden } from './VisuallyHidden';

// Advanced UI
export { CommandPalette, useCommandPalette } from './CommandPalette';

// Layout components
export { SiteHeader } from './site-header';
export { SiteFooter } from './site-footer';
export { ThemeProvider } from './theme-provider';
export { ThemeToggle } from './theme-toggle';

// Marketing components
export { PricingCard } from './pricing-card';
export { default as ColorPalette } from './ColorPalette';
export { default as NeonShowcase } from './NeonShowcase';

// UI components (re-export from ui directory)
export * from './ui';

// Export types
export type { CommandItem, CommandPaletteProps } from './CommandPalette';
