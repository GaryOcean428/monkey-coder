# Documentation Index

## Getting Started

- [Setup Guide](../SETUP_GUIDE.md) - Installation and configuration
- [Testing Guide](../TESTING_GUIDE.md) - Running tests across the monorepo
- [Troubleshooting Guide](troubleshooting-guide.md) - Common issues and solutions

## Architecture & Development

- [Yarn Workspace Optimizations](yarn-workspace-optimizations.md) - Performance and configuration
- [Model Manifest](../MODEL_MANIFEST.md) - AI model configurations and capabilities
- [Model Compliance](MODEL_COMPLIANCE.md) - Model validation and compliance rules
- [Quantum Routing Progress](QUANTUM_ROUTING_PROGRESS.md) - Advanced routing implementation

## Deployment

- [Deployment Guide](DEPLOYMENT.md) - Railway deployment and local development
- [Railway Deployment Guide](railway-deployment-guide.md) - Railway-specific optimizations
- [Build Outputs and Ignores](BUILD_OUTPUTS_AND_IGNORES.md) - Build configuration

## Workflows

- [AI Automated Workflows](AI_AUTOMATED_WORKFLOWS.md) - Automation patterns
- [Documentation Structure](DOCUMENTATION_STRUCTURE.md) - Documentation organization
- [Navigation Best Practices](NAVIGATION_BEST_PRACTICES.md) - UI/UX guidelines

## Roadmap

- [Project Roadmap](roadmap.md) - Development roadmap and milestones

## Reference

- [Railway Docs Links](railway-docs-links.md) - Railway documentation references
- [Railpack Docs Links](railpack-docs-links.md) - Railpack configuration references
- [Changelog](../CHANGELOG.md) - Version history

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
