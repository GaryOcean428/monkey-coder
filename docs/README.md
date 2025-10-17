# Documentation Index

## 🚀 Getting Started

- **[Setup Guide](../AGENTS.md)** - Complete setup, build, and deployment instructions
- **[Main README](../README.md)** - Project overview and quick start
- [Troubleshooting Guide](troubleshooting-guide.md) - Common issues and solutions

## 🏗️ Architecture & Development

- [Advanced Features](ADVANCED_FEATURES.md) - Platform capabilities and features
- [Model Manifest](../MODEL_MANIFEST.md) - AI model configurations and capabilities
- [API Documentation](api-documentation.md) - API reference and usage
- [Microsoft Agent Framework Integration](MICROSOFT_AGENT_FRAMEWORK_INTEGRATION.md) - Agent framework integration

## 📦 Deployment

- **[Railway Deployment](deployment/RAILWAY_DEPLOYMENT.md)** - Authoritative Railway configuration guide
- **[Deployment Guide](DEPLOYMENT.md)** - Overview of deployment architectures and strategies
- [Production Deployment Guide](production-deployment-guide.md) - Production best practices
- [Deployment Details](deployment/) - Detailed deployment documentation
  - [Railway Optimization](deployment/railway-optimization.md) - Performance and monitoring
  - [Railway Architecture](deployment/railway-architecture.md) - Architecture diagrams
  - [Railway Services Setup](deployment/railway-services-setup.md) - Service configuration
  - [System Resource Limits](deployment/SYSTEM_RESOURCE_LIMITS.md) - Resource management

## 🗺️ Roadmap & Planning

- **[Comprehensive Roadmap Index](roadmap.md)** - Authoritative roadmap with 36+ detailed sub-documents
  - Version 4.1.0, last updated 2025-08-21
  - Covers all phases, technical specs, implementation guidelines
- **[Quick Roadmap Summary](../ROADMAP.md)** - Executive summary at repository root
- [Roadmap Details](roadmap/) - Detailed roadmap documentation directory
  - [Current Development](roadmap/current-development.md) - Active work in progress
  - [Backlog & Priorities](roadmap/backlog-and-priorities.md) - Prioritized tasks (P0-P2)
  - [Technical Architecture](roadmap/technical-architecture.md) - Architecture decisions
  - [Phase 1.7 Critical Gaps](roadmap/phase-1-7-critical-gaps.md) - ✅ Complete
  - [Phase 2.0 Production Deployment](roadmap/phase-2-0-production-deployment.md) - 🚧 Current

## 🔧 Specialized Topics

- [TRM Integration](trm-integration.md) - TRM system integration
- [Monkey Coder Agent](monkey_coder_agent.md) - Agent system documentation

## 📚 Historical Documentation

- **[Archive](../archive/reports/2025/)** - Historical reports and documentation
  - Phase completion reports
  - Session summaries  
  - Build tool evaluations
  - Railway troubleshooting history

## Docusaurus Site

This directory also contains the Docusaurus-based documentation site:

### 📚 Features
- **Docusaurus 3.8.1**: Latest version with TypeScript support
- **Yarn 4.9.2**: Consistent package management across the monorepo
- **Link Validation**: Automated link checking with `linkinator`
- **Modern Theme**: Dark/light mode support with custom styling

## Project Structure

```text
docs/
├── blog/                     # Blog posts and announcements
├── docs/                     # Documentation markdown files
│   ├── quick-start.md       # Main getting started guide
│   ├── quantum-tasks.md     # Advanced features documentation
│   ├── billing.md           # Pricing and usage information
│   └── migration-guide.md   # Qwen3-Coder migration guide
├── src/
│   ├── components/
│   │   ├── JSRepl/          # WebContainer-based JavaScript REPL
│   │   ├── PythonRepl/      # Replit-based Python REPL
│   │   └── HomepageFeatures/ # Landing page feature cards
│   ├── css/                 # Custom styling
│   └── pages/               # Static pages
├── static/                  # Static assets (images, icons, etc.)
├── docusaurus.config.ts     # Main configuration file
├── sidebars.ts             # Documentation navigation structure
└── package.json            # Dependencies and scripts
```

## Available Scripts

### Development
```bash
yarn docs:dev          # Start development server
yarn docs:build        # Build for production
yarn docs:serve        # Serve built site locally
```

### Quality Assurance
```bash
yarn docs:validate-links     # Check for broken links (CSV format)
yarn docs:validate-links:json # Check for broken links (JSON format)
```

## Interactive Components

### JavaScript/TypeScript REPL
```jsx
import JSRepl from '@site/src/components/JSRepl';

<JSRepl
  initialCode="console.log('Hello Monkey Coder!');"
  language="typescript"
  title="TypeScript Example"
  showConsole={true}
  height="500px"
/>
```

### Python REPL
```jsx
import PythonRepl from '@site/src/components/PythonRepl';

<PythonRepl
  initialCode="print('Hello from Python!')"
  title="Python Example"
  height="600px"
/>
```

### Live Code Blocks
Use the `jsx live` syntax for interactive React components:

````markdown
```jsx live
function Example() {
  const [count, setCount] = React.useState(0);
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```
````

## Configuration

### Key Configuration Options

- **Base URL**: `/monkey-coder/` (for GitHub Pages deployment)
- **Repository**: `GaryOcean428/monkey-coder`
- **Edit URLs**: Point to the GitHub repository for easy contributions
- **Live Code Blocks**: Enabled with bottom playground position
- **Link Checking**: Strict mode with automatic validation

### Theme Customization

The site uses Docusaurus's classic theme with:
- Custom color scheme for Monkey Coder branding
- Dark/light mode toggle
- Responsive navigation
- Code syntax highlighting with Prism

## Deployment

The documentation is configured for GitHub Pages deployment:

1. **Automatic Deployment**: Push to main branch triggers GitHub Actions
2. **Manual Deployment**: Run `yarn deploy` from the docs directory
3. **Custom Domain**: Configurable via `CNAME` file in static directory

### Deployment Configuration
```typescript
// docusaurus.config.ts
{
  url: 'https://garyocean428.github.io',
  baseUrl: '/monkey-coder/',
  organizationName: 'GaryOcean428',
  projectName: 'monkey-coder',
}
```

## Link Validation

The documentation includes automated link validation:

```bash
# Validate all links in the built site
yarn docs:validate-links

# Example output shows:
# - ✅ Working links (200 status)
# - ❌ Broken links (404 status)
# - 🔄 Redirects (3xx status)
```

## Contributing

1. **Edit Documentation**: Modify markdown files in `docs/docs/`
2. **Add Interactive Examples**: Use live code blocks or custom components
3. **Test Changes**: Run `yarn docs:dev` to preview changes
4. **Validate Links**: Run `yarn docs:validate-links` before submitting
5. **Build Check**: Ensure `yarn docs:build` succeeds

## Migration from MkDocs

This site replaces the previous MkDocs setup with enhanced features:

- ✅ **Interactive Examples**: Live code execution
- ✅ **Better Performance**: Static site generation
- ✅ **Modern UI**: React-based components
- ✅ **Better SEO**: Optimized for search engines
- ✅ **Version Control**: Git-based workflow integration

## Troubleshooting

### Common Issues

1. **Build Failures**: Check for broken internal links
2. **WebContainer Issues**: Ensure modern browser with WebAssembly support
3. **Link Validation Errors**: External links may be temporarily unavailable
4. **Port Conflicts**: Default dev server runs on port 3000

### Debug Commands
```bash
# Clear Docusaurus cache
yarn docs:clear

# Type check
yarn docs:typecheck

# Detailed build logs
DEBUG=* yarn docs:build
```

For more information, see the main project README or visit the [Docusaurus documentation](https://docusaurus.io/).
