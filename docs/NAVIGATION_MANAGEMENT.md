# Navigation Management Best Practices

This document outlines the best practices for managing navigation across the Monkey Coder web application.

## Overview

The navigation system has been consolidated to eliminate duplication and ensure consistency across all components. This document explains the new structure and how to maintain it.

## Architecture

### Centralized Configuration

All navigation data is managed through a single configuration file:

```
packages/web/src/config/navigation.ts
```

This file exports:
- `mainNavigation`: Primary header navigation links
- `simpleNavigation`: Simplified navigation for minimal headers  
- `productNavigation`: Product-related footer links
- `companyNavigation`: Company-related footer links
- `legalNavigation`: Legal footer links
- `socialNavigation`: Social media links

### Component Structure

```
packages/web/src/components/
├── marketing/
│   ├── header.tsx     # Comprehensive marketing header
│   └── footer.tsx     # Comprehensive marketing footer
├── site-header.tsx    # Simplified site header
└── site-footer.tsx    # Simplified site footer
```

## Navigation Configuration

### Main Navigation

Used in marketing header and mobile menus:

```typescript
export const mainNavigation: NavigationItem[] = [
  { name: 'Getting Started', href: '/getting-started' },
  { name: 'Features', href: '/#features' },
  { name: 'Pricing', href: '/pricing' },
  { name: 'Docs', href: '/docs' },
  { name: 'API Keys', href: '/api-keys' },
  { name: 'Contact', href: '/contact' },
];
```

### Simple Navigation

Used in minimal site header:

```typescript
export const simpleNavigation: NavigationItem[] = [
  { name: 'Home', href: '/' },
  { name: 'Pricing', href: '/pricing' },
  { name: 'Docs', href: '/docs' },
  { name: 'Contact', href: '/contact' },
];
```

### Footer Navigation

Organized into logical groups:

```typescript
// Product links
export const productNavigation: NavigationItem[] = [
  { name: 'Features', href: '/#features' },
  { name: 'Pricing', href: '/pricing' },
  { name: 'Documentation', href: '/docs' },
  { name: 'Projects', href: '/projects' },
  { name: 'Blog', href: '/blog' },
];

// Company links
export const companyNavigation: NavigationItem[] = [
  { name: 'Blog', href: '/blog' },
  { name: 'Contact', href: '/contact' },
];

// Legal links
export const legalNavigation: NavigationItem[] = [
  { name: 'Privacy', href: '/privacy' },
  { name: 'Terms', href: '/terms' },
];
```

## Usage Guidelines

### Adding New Navigation Items

1. **Verify the page exists** in `packages/web/src/app/`
2. **Choose the appropriate navigation array** based on the link's purpose
3. **Add the item** to the configuration file
4. **Test** that the link works correctly

### Modifying Existing Items

1. **Update the configuration file** only
2. **Avoid** modifying individual components
3. **Ensure consistency** across all navigation uses

### Component Integration

Import and use the shared configuration:

```typescript
import { mainNavigation, productNavigation } from '@/config/navigation';

// Use in component
{mainNavigation.map((item) => (
  <Link key={item.name} href={item.href}>
    {item.name}
  </Link>
))}
```

## Link Validation

### Required Page Structure

All navigation links must point to existing pages in:

```
packages/web/src/app/[route]/page.tsx
```

### Current Valid Routes

- `/` - Home page
- `/getting-started` - Getting started guide
- `/pricing` - Pricing information  
- `/docs` - Documentation entry
- `/docs/cli` - CLI documentation
- `/api-keys` - API key management
- `/contact` - Contact form
- `/projects` - User projects
- `/blog` - Blog posts
- `/privacy` - Privacy policy
- `/terms` - Terms of service
- `/login` - User login
- `/signup` - User registration
- `/dashboard` - User dashboard

### Hash Fragment Links

For same-page navigation, use hash fragments:

- `/#features` - Features section on home page
- `/#pricing` - Pricing section on home page

## Styling Consistency

### CSS Classes

All navigation components use consistent Tailwind CSS classes:

```typescript
// Base navigation link styles
className="text-sm font-semibold leading-6 text-muted-foreground hover:text-foreground transition-colors"

// Active state styles
className="text-foreground bg-muted"

// Mobile menu styles
className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-foreground hover:bg-gray-50 dark:hover:bg-gray-800"
```

### Responsive Behavior

- **Desktop**: Horizontal navigation with hover states
- **Mobile**: Collapsible hamburger menu with vertical layout
- **Focus States**: Keyboard navigation support with visible focus indicators

## Accessibility

### ARIA Labels

```typescript
// Mobile menu
role="dialog" aria-modal="true"

// Navigation lists  
role="list"

// Screen reader text
<span className="sr-only">Navigation</span>
```

### Keyboard Navigation

- Tab order follows visual layout
- Focus indicators are clearly visible
- Escape key closes mobile menu
- Enter/Space activates links

## Maintenance

### Regular Checks

1. **Validate Links**: Ensure all navigation links point to existing pages
2. **Test Mobile**: Verify mobile menu functionality  
3. **Check Accessibility**: Test with keyboard navigation
4. **Update Configuration**: Add new pages to appropriate navigation arrays

### Best Practices

1. **Single Source of Truth**: Always update the configuration file, not individual components
2. **Page Validation**: Verify pages exist before adding navigation links  
3. **Logical Grouping**: Keep related links together in appropriate navigation arrays
4. **Consistent Naming**: Use clear, descriptive names for navigation items
5. **Mobile First**: Consider mobile navigation experience when adding items

### Testing

Run these commands after navigation changes:

```bash
# Type checking
yarn workspace @monkey-coder/web typecheck

# Component tests  
yarn workspace @monkey-coder/web test

# Manual testing
yarn workspace @monkey-coder/web dev
```

## Documentation Sidebars

The documentation uses a separate sidebar system managed by Docusaurus:

- **Main Configuration**: `docs/sidebars.ts`
- **Enhanced Sidebar**: `docs/sidebars.enhanced.ts` (comprehensive)
- **Roadmap Sidebar**: `docs/sidebars.roadmap.ts` (separate section)

The enhanced sidebar follows best practices from OpenAI and Anthropic documentation with:
- Clear hierarchical structure
- Progressive complexity flow  
- Utility CSS classes for styling
- Comprehensive topic coverage

## Migration from Old System

### Before (Duplicated)

- `marketing/header.tsx`: Custom navigation array
- `site-header.tsx`: Custom navigation array  
- `marketing/footer.tsx`: Custom navigation object
- `site-footer.tsx`: Custom navigation links

### After (Consolidated)

- All components import from `@/config/navigation`
- Single source of truth for all navigation data
- Consistent links across all components
- Easy maintenance and updates

## Future Considerations

1. **Dynamic Navigation**: Consider database-driven navigation for user-specific content
2. **Internationalization**: Prepare navigation structure for multi-language support
3. **Analytics**: Track navigation usage to optimize user flows
4. **Performance**: Monitor navigation component rendering performance