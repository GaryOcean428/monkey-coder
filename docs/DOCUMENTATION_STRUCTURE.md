# Monkey Coder Documentation Structure

## Overview

This document outlines the documentation structure for Monkey Coder, following best practices from OpenAI Agents Python documentation.

## Navigation Best Practices Applied

### 1. **Hierarchical Organization**
Following OpenAI's pattern, our documentation is organized in a clear hierarchy:
- **Getting Started** → **Core Concepts** → **Advanced Features** → **Reference** → **Resources**

### 2. **CSS Classes for Navigation**
All navigation items use the following classes for consistency:
- `md-nav__link` - Base navigation link styling
- `md-ellipsis` - Text overflow handling for long titles

### 3. **Logical Grouping**
Documentation is grouped by functional areas:
- **CLI Reference** - All command-line interface documentation
- **API Reference** - All API endpoint documentation  
- **SDK & Integration** - Language-specific SDK documentation
- **Deployment** - Infrastructure and deployment guides

## File Structure

```
docs/
├── sidebars.ts              # Main sidebar configuration
├── sidebars.main.ts         # Primary documentation sidebar
├── sidebars.roadmap.ts      # Roadmap-specific sidebar
├── src/
│   └── css/
│       ├── custom.css       # Main custom styles
│       └── custom-nav.css   # Navigation-specific styles
└── docs/
    ├── index.md             # Documentation home page
    ├── quick-start.md
    ├── installation.md
    ├── agents.md
    ├── cli/
    │   ├── commands.md
    │   ├── implement.md
    │   ├── analyze.md
    │   └── ...
    ├── api/
    │   ├── overview.md
    │   ├── execute.md
    │   ├── streaming.md
    │   └── ...
    └── sdk/
        ├── ts/
        │   └── ...
        └── python/
            └── ...
```

## Navigation Categories

### 1. Getting Started
Entry point for new users with progressive complexity:
- Quick Start
- Installation
- Your First Project
- Migration Guide

### 2. Core Concepts
Fundamental concepts that power Monkey Coder:
- Agents
- Personas
- Orchestration
- Quantum Tasks
- Model Routing

### 3. CLI Reference
Complete command-line interface documentation:
- Commands Overview
- Individual command pages (implement, analyze, build, test, chat)
- Authentication
- Usage Tracking
- MCP Commands

### 4. API Reference
Comprehensive API documentation:
- Overview
- Execute Endpoint
- Streaming
- Models
- Providers
- Billing API
- Capabilities
- Health Checks
- Response Examples

### 5. Advanced Features
Advanced capabilities and integrations:
- Multi-Agent Orchestration
- Context Management
- Guardrails
- Tracing
- MCP Integration
- Agent Handoffs
- Custom Tools

### 6. SDK & Integration
Language-specific SDK documentation:
- TypeScript SDK (installation, client, examples)
- Python SDK (installation, client, examples)
- Integration Patterns

### 7. Deployment
Production deployment guides:
- Railway Deployment
- Docker
- Configuration
- Monitoring
- Scaling

### 8. Development
For contributors and developers:
- Contributing
- Development Workflow
- Testing Strategies
- Agent OS Standards
- Troubleshooting

### 9. Resources
Additional resources and references:
- Billing & Pricing
- Model Inventory
- Performance Benchmarks
- Security
- Changelog
- FAQ

## Styling Guidelines

### Navigation Link Styling
```css
.md-nav__link {
  /* Consistent padding and typography */
  padding: 0.625em 1.25em;
  font-weight: 500;
  
  /* Smooth transitions */
  transition: color 0.125s, background-color 0.125s;
  
  /* Rounded corners for modern look */
  border-radius: 0.25rem;
}

.md-ellipsis {
  /* Handle long navigation items gracefully */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

### Category Headers
Categories use uppercase styling with increased letter spacing for clear visual hierarchy:
```css
.menu__list-item-collapsible .md-nav__link {
  text-transform: uppercase;
  letter-spacing: 0.025em;
}
```

### Active State Indicators
Active links have visual indicators:
- Background color change
- Left border accent
- Increased font weight

## Key Improvements

1. **Progressive Complexity**: Documentation flows from simple (Getting Started) to complex (Advanced Features)
2. **Clear Categories**: Each section has a clear purpose and audience
3. **Consistent Styling**: All navigation uses the same CSS classes and patterns
4. **External Link Indicators**: External links show ↗ symbol
5. **Responsive Design**: Navigation adapts to mobile and desktop
6. **Dark Mode Support**: Full dark mode compatibility
7. **Accessibility**: Focus states and ARIA labels for screen readers

## Migration from Old Structure

The old flat structure has been reorganized into logical categories:
- `quick-start` → Getting Started section
- `openai-response-examples` → API Reference section
- `quantum-tasks` → Core Concepts section
- `billing` → Resources section
- `migration-guide` → Getting Started section

## Future Enhancements

1. **Search Integration**: Add Algolia DocSearch for instant search
2. **Version Dropdown**: Support multiple documentation versions
3. **Language Switcher**: Multi-language documentation support
4. **Interactive Examples**: Embedded code playgrounds
5. **API Explorer**: Interactive API testing interface

## Maintenance

To maintain documentation quality:
1. Keep navigation hierarchy shallow (max 3 levels)
2. Use consistent naming conventions
3. Update sidebar configuration when adding new pages
4. Test navigation on mobile and desktop
5. Ensure all links are functional
6. Keep category sizes balanced (5-10 items per category)