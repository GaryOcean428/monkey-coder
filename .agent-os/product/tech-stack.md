# Technical Stack

> Last Updated: 2025-01-29
> Version: 1.0.1
> Status: Production Ready

## Application Framework
- **Framework:** Node.js + Python FastAPI Hybrid Architecture
- **Version:** Node.js 20+ / Python 3.8+
- **CLI Framework:** TypeScript with Commander.js for CLI interface
- **Backend Framework:** Python FastAPI for AI orchestration and quantum routing

## Database System
- **Primary Database:** PostgreSQL (for production)
- **Development Database:** SQLite
- **Caching Layer:** Redis (for model routing cache and session management)
- **Vector Database:** ChromaDB (for AI context and embeddings)

## JavaScript Framework
- **Frontend Framework:** Next.js 14+ with React 18+
- **CLI Framework:** TypeScript with Commander.js and Chalk for CLI interface
- **Package Manager:** Yarn 4.9.2 (Workspaces)
- **Module System:** ESM with TypeScript

## Import Strategy
- **Strategy:** Node.js modules with TypeScript compilation
- **CLI Distribution:** npm packages with TypeScript build
- **Python Distribution:** PyPI packages with setuptools

## CSS Framework
- **Framework:** Tailwind CSS 3.x
- **Version:** Latest stable
- **Configuration:** PostCSS with custom design tokens
- **Component Styling:** CSS modules for component isolation

## UI Component Library
- **Primary Library:** Radix UI primitives with custom styling
- **CLI Components:** Chalk, Ora, Inquirer for terminal UI
- **Design System:** Custom components built on Radix primitives

## Fonts Provider
- **Primary Font:** Inter (Google Fonts)
- **Monospace Font:** JetBrains Mono for code display
- **CLI Font:** System monospace fonts

## Icon Library
- **Icon Library:** Lucide React for web interface
- **CLI Icons:** Unicode symbols and ASCII art
- **System Icons:** Native system icons where applicable

## Application Hosting
- **Primary Hosting:** Railway.app (Single unified service)
- **Architecture:** FastAPI backend with Next.js static serving
- **Static Assets:** FastAPI StaticFiles with multi-path fallback system
- **CLI Distribution:** npm registry
- **Python Distribution:** PyPI registry
- **Container Runtime:** Docker with multi-stage builds

## Database Hosting
- **Primary Database:** Railway PostgreSQL addon
- **Caching:** Railway Redis addon
- **Development:** Local SQLite with optional PostgreSQL
- **Backup Strategy:** Railway automated backups

## Asset Hosting
- **Static Assets:** Railway static hosting
- **CDN:** Railway's integrated CDN
- **Image Assets:** Co-located with application
- **Documentation Assets:** Docusaurus static hosting

## Deployment Solution
- **Primary Deployment:** Railway automated deployments
- **CI/CD Pipeline:** GitHub Actions with Railway integration
- **Container Strategy:** Docker multi-stage builds
- **Monitoring:** Sentry for error tracking and performance monitoring

## Code Repository URL
- **Repository:** https://github.com/GaryOcean428/monkey-coder
- **License:** MIT License
- **Version Control:** Git with conventional commits
- **Package Management:** Yarn workspaces for monorepo structure

## AI & ML Infrastructure
- **Model Providers:** OpenAI, Anthropic, Google GenAI, Groq, Grok
- **Provider Consolidation:** Qwen and Moonshot models served through Groq provider
- **Routing Engine:** Basic provider selection with foundations for Q-learning implementation
- **Quantum Framework:** Framework ready for quantum computing principles implementation
- **Multi-Agent System:** Python-based agent orchestration with FastAPI
- **Health Monitoring:** Component-by-component validation and startup checks

## Development Tools
- **Language:** TypeScript + Python
- **Testing:** Jest (TypeScript), Pytest (Python)
- **Linting:** ESLint + Prettier (TypeScript), Black + isort (Python)
- **Type Checking:** TypeScript compiler + mypy (Python)
- **Documentation:** Docusaurus for project documentation

## Security & Monitoring
- **Error Tracking:** Sentry integration across all components
- **Authentication:** JWT-based authentication system
- **API Security:** FastAPI security middleware with rate limiting
- **Environment Management:** Secure environment variable handling
- **Health Monitoring:** /health and /healthz endpoints with component status
- **Performance Monitoring:** Request metrics with X-Process-Time headers
- **System Metrics:** Prometheus endpoint for infrastructure monitoring
- **Production Logging:** Railway-optimized structured logging