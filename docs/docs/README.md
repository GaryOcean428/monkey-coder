# Documentation Organization

This directory follows the canonical naming convention adopted from the pantheon-chat repository, which provides a clear, numbered folder structure for organizing documentation.

## Directory Structure

### Active Documentation

- **00-overview/** - Platform overview, getting started guides, and roadmap
  - Main entry point for new users
  - High-level architecture and concepts
  - Project roadmap and vision

- **01-guides/** - User guides, tutorials, and how-to documentation
  - Quick start guides
  - Feature guides
  - Troubleshooting guides
  - Billing and usage information

- **02-architecture/** - Technical architecture and design documentation
  - Agent system architecture
  - Multi-agent orchestration
  - Integration patterns
  - Technical design decisions

- **03-api/** - API reference documentation
  - REST API endpoints
  - SDK documentation
  - Integration guides

- **04-deployment/** - Deployment guides and infrastructure documentation
  - Railway deployment
  - Production deployment guides
  - Configuration management
  - Infrastructure as code

- **05-development/** - Development guidelines and contributing documentation
  - Contributing guidelines
  - Development setup
  - Coding standards
  - Testing guidelines

### Archive

- **99-archive/** - Historical documentation and deprecated content
  - Implementation summaries
  - PR summaries and reports
  - Railway fix summaries
  - Session reports
  - **Note:** This directory is excluded from Docusaurus builds

## Naming Conventions

### Folder Naming
Folders use a numbered prefix (e.g., `00-`, `01-`, `99-`) to maintain a consistent ordering and make the hierarchy clear. Docusaurus automatically strips these prefixes when generating URLs.

### File Naming

#### Standard Documentation
- Use descriptive, lowercase names with hyphens: `quick-start.md`, `api-documentation.md`
- For proper nouns or abbreviations, maintain casing: `CLAUDE.md`, `MODEL_MANIFEST.md`

#### Dated Documents (Archive)
For historical records and implementation summaries, use the pattern:
```
YYYYMMDD-document-name-version-status.md
```

Example: `20260126-feature-implementation-1.00W.md`

**Status Codes:**
- `.00F` - Frozen (finalized, immutable)
- `.00W` - Working (active development)
- `.00H` - Hypothesis (experimental)
- `.00D` - Deprecated (superseded)
- `.00R` - Review (awaiting approval)
- `.00A` - Approved (management sign-off)

## Document Organization Best Practices

1. **Keep documentation close to code** - For package-specific docs, consider keeping them in the package directory
2. **Single source of truth** - Avoid duplicating content across multiple files
3. **Clear hierarchy** - Use the numbered folders to maintain a clear information architecture
4. **Regular maintenance** - Archive outdated documentation rather than deleting it
5. **Consistent formatting** - Follow markdown best practices and include frontmatter where appropriate

## Adding New Documentation

When adding new documentation:

1. **Determine the category** - Choose the appropriate numbered folder
2. **Follow naming conventions** - Use descriptive names and appropriate casing
3. **Update the sidebar** - Add your document to `docs/sidebars.ts`
4. **Test locally** - Run `yarn build` in the docs directory to verify
5. **Update index** - If adding a major new section, update `index.md`

## Maintenance

### Moving Documentation
When reorganizing:
- Maintain redirects for external links
- Update all internal cross-references
- Test the build after changes

### Archiving
To archive outdated documentation:
1. Move to appropriate subdirectory in `99-archive/`
2. Add date prefix if not already present
3. Update internal links that referenced the document
4. The archive is automatically excluded from builds

## Related Files

- `/docs/sidebars.ts` - Sidebar configuration for Docusaurus
- `/docs/docusaurus.config.ts` - Main Docusaurus configuration
- `/docs/docs/index.md` - Main documentation index page

---

For questions about documentation organization, please refer to the [Contributing Guide](./05-development/contributing.md) or open an issue on GitHub.
