[← Back to Roadmap Index](../roadmap.md)

## Appendices

### Appendix A: Glossary

**Agent**: Specialized AI component designed for specific development tasks (code generation, analysis, testing, etc.)

**DQN (Deep Q-Network)**: Machine learning algorithm used for intelligent model routing and decision making

**MCP (Model Context Protocol)**: Standardized protocol for AI model communication and tool integration

**Persona**: User role-based configuration that influences AI behavior (developer, architect, tester, etc.)

**Quantum Routing**: Advanced routing system that evaluates multiple solution approaches simultaneously

**Superposition**: Quantum computing concept applied to parallel task execution and analysis

### Appendix B: API Reference

**Base URL**: `https://api.monkey-coder.com/v1`

**Authentication**: Bearer token in Authorization header

**Rate Limits**:
- Free tier: 100 requests/hour
- Pro tier: 1,000 requests/hour
- Enterprise: Custom limits

**SDKs Available**:
- Node.js/TypeScript: `npm install monkey-coder-sdk`
- Python: `pip install monkey-coder-sdk`
- REST API: Direct HTTP integration

### Appendix C: Performance Benchmarks

**Latest Benchmark Results (January 2025):**
- Average response time: 1.2s (simple tasks), 8.5s (complex tasks)
- Model selection accuracy: 94.2%
- Quantum routing speedup: 3.8x vs sequential processing
- System uptime: 99.97%
- User satisfaction score: 4.7/5.0

### Appendix D: Changelog

**Version 1.0.7 (August 8, 2025):**
- Quantum Routing Engine branch merged into main; conflicts resolved and protected models.py preserved
- Removed committed Next.js build artifacts; normalized .gitignore
- Integrated DQN training pipeline commits from copilot/fix-29
- Branch cleanup: removed local/remote feature branches; main is single active branch
- Docs: roadmap updated with post-merge status and next steps

**Version 1.0.5 (June 8, 2025):**
- Main Application Linting Fixes: Resolved all ruff linter errors in packages/core/monkey_coder/app/main.py
- JWT Authentication Improvements: Fixed missing JWTUser import and create_access_token parameter structure
- Code Quality Enhancement: Improved import organization and type safety in core FastAPI application
- Technical Debt Resolution: Addressed critical linting issues blocking development progress
- Phase 2 Quantum Routing Async/Await Fixes: Successfully resolved all async/await issues in quantum routing test suite
  - Fixed 4 locations where async methods were called without proper awaiting
  - All 26 tests in quantum routing test suite now passing
  - Eliminated coroutine object attribute errors throughout the system
- AsyncMock Formatting Fix: Resolved TypeError in main.py error handling by fixing AsyncMock parameter usage
  - Changed `patch("monkey_coder.app.main.verify_permissions", AsyncMock)` to `patch("monkey_coder.app.main.verify_permissions", new_callable=AsyncMock)`
  - Added proper mocking for quantum routing results to prevent type errors
  - All error handling tests now passing with correct async/await patterns

**Version 1.0.4 (January 31, 2025):**
- Security Implementation: httpOnly Cookie Authentication
- Website Improvements: UI/UX fixes and neon glow effects
- Enhanced persona validation with single-word input support
- Advanced orchestration patterns implementation
- Production hardening and comprehensive error handling

**Version 1.0.3 (January 28, 2025):**
- Model compliance system implementation
- Publishing infrastructure for PyPI/npm packages
- Railway deployment fixes and optimizations
- CLI chat functionality and authentication improvements
