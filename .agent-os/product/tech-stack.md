# Technical Stack

> Last Updated: 2025-01-29
> Version: 1.0.1
> Status: Production Ready

## Application Framework
- **Framework:** Node.js + Python FastAPI Hybrid Architecture
- **Version:** Node.js 20+ (enforced >=20.0.0) / Python 3.13 (production)
- **CLI Framework:** TypeScript 5.8.3 with Commander.js for CLI interface
- **Backend Framework:** Python FastAPI for AI orchestration and quantum routing
- **Monorepo Management:** Yarn 4.9.2 workspaces with enforced constraints

## Database System
- **Primary Database:** PostgreSQL (for production)
- **Development Database:** SQLite
- **Caching Layer:** Redis (for model routing cache and session management)
- **Vector Database:** ChromaDB (for AI context and embeddings)

## JavaScript Framework
- **Frontend Framework:** Next.js 15.2.3 with React 18.2.0
- **CLI Framework:** TypeScript 5.8.3 with Commander.js and Chalk for CLI interface
- **Package Manager:** Yarn 4.9.2 (Workspaces with constraints)
- **Module System:** ESM with TypeScript
- **Workspace Configuration:** 
  - Global cache enabled for performance
  - Hardlinks for node_modules optimization
  - Constraints via yarn.config.cjs
  - Workspace protocol for internal dependencies

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
- **Repository:** <https://github.com/GaryOcean428/monkey-coder>
- **License:** MIT License
- **Version Control:** Git with conventional commits
- **Package Management:** yarn workspaces for monorepo structure

## AI & ML Infrastructure
- **Model Providers:** OpenAI, Anthropic, Google GenAI, Groq
- **Provider Consolidation:** Qwen and Moonshot models served through Groq provider
- **Routing Engine:** Advanced persona-aware routing with intelligent validation
- **Orchestration Framework:** Multi-strategy coordination (Sequential, Parallel, Quantum, Hybrid)
- **Persona Validation:** Enhanced validation with single-word input support and edge case handling
- **Multi-Agent System:** Python-based agent orchestration with advanced coordination patterns
- **Quantum Framework:** Framework ready for quantum computing principles implementation
- **Health Monitoring:** Component-by-component validation and startup checks

### Complete Model Inventory (27 Models Across 4 Providers)

#### OpenAI Provider (11 Models)
**Reasoning Models (o1/o3/o4 Series):**
- `o4-mini` - Fast, affordable reasoning with advanced problem-solving
- `o3-pro` - Most powerful reasoning with extended compute for complex tasks
- `o3` - Powerful reasoning for complex problem-solving and analysis
- `o3-mini` - Compact reasoning optimized for speed and efficiency
- `o1` - Advanced reasoning with extended thinking for complex problems
- `o1-mini` - Faster reasoning for coding and STEM tasks

**GPT-4.1 Family:**
- `gpt-4.1` - Flagship model for complex conversational tasks
- `gpt-4.1-mini` - Efficient model optimized for fast, lightweight tasks
- `gpt-4.1-vision` - Optimized for vision and multimodal understanding

#### Anthropic Provider (6 Models - Claude 3.5+ Only)
- `claude-opus-4-20250514` - Most capable and intelligent model
- `claude-sonnet-4-20250514` - High-performance with exceptional reasoning
- `claude-3-7-sonnet-20250219` - High-performance with early extended thinking
- `claude-3-5-sonnet-20241022` - Upgraded version with enhanced capabilities
- `claude-3-5-sonnet-20240620` - Original version with high intelligence
- `claude-3-5-haiku-20241022` - Intelligence at blazing speeds

#### Google Provider (4 Models - Gemini 2.5 Series)
- `gemini-2.5-pro` - State-of-the-art for complex reasoning in code, math, and STEM
- `gemini-2.5-flash` - Best price-performance for large-scale, low-latency tasks
- `gemini-2.5-flash-lite` - Cost-efficient and high-throughput version
- `gemini-2.0-flash` - Next-gen features with superior speed, native tool use

#### Groq Provider (6 Models - Hardware Accelerated)
**Llama Models:**
- `llama-3.1-8b-instant` - Fast, lightweight model
- `llama-3.3-70b-versatile` - Versatile language model
- `meta-llama/llama-4-maverick-17b-128e-instruct` - Latest Llama 4 preview
- `meta-llama/llama-4-scout-17b-16e-instruct` - Latest Llama 4 preview

**Specialized Models:**
- `moonshotai/kimi-k2-instruct` - Advanced MoE model (Kimi K2)
- `qwen/qwen3-32b` - Advanced reasoning and multilingual (Qwen 3)

#### xAI Provider (6 Models - Grok Series)
**Grok Models:**
- `grok-4-latest` - xAI's most advanced reasoning model
- `grok-4` - Advanced reasoning and conversation model
- `grok-3` - Strong reasoning capabilities for general use
- `grok-3-mini` - Efficient model for everyday tasks
- `grok-3-mini-fast` - Ultra-fast responses for simple tasks
- `grok-3-fast` - Balance of speed and capability

### Model Compliance System
- **Automatic Legacy Model Replacement:** Deprecated models automatically replaced with current versions
- **Validation at Every Layer:** Model names validated against official provider documentation
- **Cost Transparency:** Per-token pricing with real-time usage tracking
- **Capability Mapping:** Detailed model capabilities and use case recommendations
- **Provider Fallback:** Intelligent fallback between providers for reliability

## Configuration Management
- **Environment Configuration:** Centralized type-safe configuration management
- **Validation System:** Comprehensive environment variable validation and health checking
- **Configuration Classes:** DatabaseConfig, AIProviderConfig, SecurityConfig, ServerConfig, MonitoringConfig
- **Development vs Production:** Environment-aware configuration with appropriate defaults
- **Security:** Secure handling of sensitive configuration without logging secrets

## Development Tools
- **Language:** TypeScript 5.8.3 + Python 3.13
- **Testing:** Jest ^30.0.5 (TypeScript), Jest ^29.7.0 (Next.js), Pytest (Python)
- **Linting:** ESLint ^9.32.0 + Prettier ^3.6.2 (TypeScript), Black + isort (Python)
- **Type Checking:** TypeScript compiler + mypy (Python)
- **Documentation:** Docusaurus for project documentation
- **Package Management:** 
  - Yarn 4.9.2 with Corepack
  - Global cache and hardlinks enabled
  - Workspace constraints enforcement
  - Security auditing via `yarn npm audit`

## Security & Monitoring
- **Error Tracking:** Sentry integration across all components
- **Authentication:** CRITICAL - Authentication System Unification in Progress (Phase 1.6)
  - **Current Issue:** 3 separate authentication modules creating security risks and maintenance burden
  - **Modules Being Consolidated:** security_enhanced.py, enhanced_cookie_auth.py, cookie_auth.py
  - **Target:** Unified authentication module with httpOnly cookies, consistent security model
  - **Timeline:** 4 weeks development effort (P0 - BLOCKS PRODUCT COMPLETION)
- **API Security:** FastAPI security middleware with rate limiting
- **Environment Management:** Centralized secure environment variable handling with validation
- **Health Monitoring:** /health and /healthz endpoints with component status
- **Performance Monitoring:** Request metrics with X-Process-Time headers
- **System Metrics:** Prometheus endpoint for infrastructure monitoring
- **Production Logging:** Railway-optimized structured logging
- **Capabilities Endpoint:** /v1/capabilities for comprehensive system status and feature documentation
- **Security Hardening:** In-progress implementation of httpOnly cookies, CSRF protection, and unified session management

## Enhanced Features (Phase 1 Completion)
- **Single-Word Input Support:** Users can enter commands like "build", "test", "debug"
- **Edge Case Handling:** Intelligent prompt enhancement for minimal inputs
- **Advanced Orchestration:** 5 orchestration strategies with intelligent selection
- **Production Hardening:** Comprehensive error handling and monitoring
- **Configuration Validation:** Type-safe environment configuration with health checks
- **Frontend Fallback:** Professional error pages when static assets are unavailable
