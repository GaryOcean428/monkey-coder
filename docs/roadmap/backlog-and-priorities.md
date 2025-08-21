[← Back to Roadmap Index](./index.md)

##### Critical Issues (Priority 0 - Must Complete)

- [x] **Web Package Testing** - Comprehensive test coverage for React components `S` ✅
  - ✅ **Component Tests**: Added tests for Button, Input, Card components (66 tests)
  - ✅ **Removed passWithNoTests**: Web package now has proper test coverage
  - ✅ **CI Integration**: Tests run successfully in CI pipeline

- [x] **CI/CD Coverage Gates** - Add test coverage thresholds and PR annotations `S` ✅
  - ✅ **Coverage Thresholds**: Added 70% minimum coverage check in CI
  - ✅ **PR Comments**: Added automated coverage reporting to PRs
  - ✅ **JUnit Reports**: Upload test results as artifacts

- [x] **ESLint v9 Migration** - Upgrade to ESLint v9 flat config format `S` ✅
  - ✅ **Flat Config**: Created eslint.config.mjs with new flat config format
  - ✅ **Fixed Errors**: Resolved @ts-ignore and Next.js document import issues
  - ✅ **All Packages Pass**: Lint passes with no errors across all workspaces

- [ ] **CLI Testing & Validation** - Comprehensive testing of CLI commands and MCP integration `M`
  - ✅ **CLI Implementation**: Complete CLI with auth, MCP, and core commands
  - ✅ **MCP Commands**: Full MCP server management functionality
  - ✅ **Security Module**: Created packages/core/monkey_coder/security_enhanced.py
  - 🚧 **Unit Tests**: Added utils tests, config tests need fixing
  - 📅 **End-to-End Testing**: Test all CLI commands with live API
  - 📅 **MCP Integration Testing**: Validate MCP server operations
  - 📅 **Performance Testing**: Measure CLI response times and resource usage

- [ ] **Security Enhancement** - Replace localStorage token storage with httpOnly cookies, secure CLI token storage `M`
  - ✅ **Frontend Implementation**: Created packages/web/src/lib/auth.ts and auth-context.tsx
  - ✅ **Security Module**: Created packages/core/monkey_coder/security_enhanced.py
  - 📅 **Backend Integration**: Implement server-side httpOnly cookie handling
  - 📅 **Component Migration**: Update all components to use new auth system
  - 📅 **CLI Security**: Implement secure token storage with keytar

- [ ] **Core Routing Refactor** - Modularize monolithic AdvancedRouter with pluggable scoring strategies `L`
  - [ ] Extract scoring interfaces and implementations
  - [ ] Implement strategy pattern for routing decisions
  - [ ] Externalize routing heuristics to YAML configuration
  - [ ] Add comprehensive routing tests

- [ ] **Type Safety Improvements** - Replace `any` types, add comprehensive TypeScript interfaces, Python type hints `S`
  - [ ] TypeScript: Replace all `any` types with proper interfaces
  - [ ] Python: Add comprehensive type hints across all modules
  - [x] API Models: Fix naming inconsistencies (superclause_config → persona_config) ✅
  - [ ] Request Models: Split heavy ExecuteRequest model into focused components

##### Important Improvements (Priority 1 - Should Complete)

- [x] **Quantum Tests Validation** - Ensure quantum features are properly tested `S` ✅
  - ✅ **Test Fixes**: Fixed Experience buffer timestamp issues
  - ✅ **Performance Tests**: All 6 buffer performance tests passing
  - ✅ **Training Pipeline**: Fixed numpy enum handling and convergence tests
  - ✅ **CI Integration**: Quantum tests run in separate CI job (164 tests, 161 passing, 3 skipped)

- [ ] **MCP Server Manager** - Replace blocking subprocess calls with async operations, modular health checks `M`
  - [ ] Convert all subprocess calls to async/await patterns
  - [ ] Implement proper error handling and retry logic
  - [ ] Add modular health check system
  - [ ] Improve server discovery and registration

- [ ] **CLI Error Handling** - Implement unified error handling, remove premature process.exit calls `S`
  - [ ] Create centralized error management system
  - [ ] Replace all process.exit calls with proper exception handling
  - [ ] Add user-friendly error messages
  - [ ] Implement error recovery mechanisms

- [ ] **Configuration Management** - Externalize routing heuristics to YAML, environment variable expansion `S`
  - [ ] Create YAML-based configuration system
  - [ ] Implement environment variable expansion
  - [ ] Add configuration validation and schema checking
  - [ ] Support multiple configuration profiles

##### Testing & Quality (Priority 2 - Nice to Have)

- [ ] **Testing Infrastructure** - Add unit tests for routing logic, CLI commands, API endpoints `L`
  - [ ] Implement comprehensive unit test coverage
  - [ ] Add integration tests for critical workflows
  - [ ] Create performance benchmarking tests
  - [ ] Set up automated testing pipeline

- [ ] **Documentation Updates** - Fix package.JSON metadata, update README links, add CONTRIBUTING.md `S`
  - [ ] Update all package.JSON files with correct metadata
  - [ ] Fix broken links and references
  - [ ] Create comprehensive CONTRIBUTING.md
  - [ ] Add API documentation generation

- [ ] **Design System** - Implement consistent UI components and styling across web frontend `M`
- [ ] **Internationalization** - Extract hardcoded strings, add i18n support `L`
- [ ] **Performance Monitoring** - Add instrumentation for routing performance, cache frequently used prompts `S`

##### Security & Performance Improvements

###### Security Enhancements
- [ ] **Token Security Audit** - Replace localStorage with httpOnly cookies, implement secure CLI token storage with keytar
- [ ] **Input Validation** - Add comprehensive input sanitization and validation across all API endpoints
- [ ] **Dependency Security** - Run bandit (Python) and npm audit, integrate Snyk security scanning
- [ ] **CSRF Protection** - Implement CSRF tokens for state-changing operations
- [ ] **Rate Limiting** - Add intelligent rate limiting to prevent abuse

###### Performance Optimizations
- [ ] **Router Performance** - Instrument scoring functions, add caching for repeated prompts
- [ ] **Async Operations** - Convert blocking operations to async/await patterns
- [ ] **Bundle Optimization** - Optimize frontend bundle size and loading performance
- [ ] **Database Performance** - Add connection pooling and query optimization
- [ ] **Monitoring Integration** - Add performance metrics collection and alerting

###### Technical Debt Priority Matrix

| Issue | Impact | Complexity | Priority | Status |
|-------|--------|------------|----------|---------|
| API model inconsistencies (superclause_config) | Low | Low | P2 | ✅ Complete |
| Security vulnerabilities (token storage) | High | Medium | P0 | In Progress |
| Monolithic router architecture | High | Medium | P0 | Planned |
| Type safety gaps | Medium | Low | P1 | Planned |
| MCP blocking operations | Medium | Medium | P1 | Planned |

###### Dependencies & Timeline

- **Dependencies:** Phase 1 completion ✅, QA analysis ✅, Security implementation 🚧
- **Estimated Duration:** 2-3 weeks
- **Team Allocation:** Security specialist, Backend engineer, Frontend engineer
- **Risk Level:** HIGH - Critical technical debt blocking future development

##### Newly Added (Aug 2025) – Operational & Observability Roadmap

- [ ] **CI Workflow Implementation** `P0`
  - [ ] Add GitHub Actions pipeline (uv sync, pytest, yarn workspaces build, markdownlint, drift check)
  - [ ] Enforce non-drift between pyproject.toml and requirements.txt
  - [ ] Publish coverage + JUnit summaries as PR check
- [ ] **Advanced Context Decision Record** `P1`
  - [ ] Evaluate restoring DB + semantic search context vs. redesign
  - [ ] Produce ADR with scope, acceptance criteria, migration plan
- [ ] **Quantum Performance Instrumentation** `P1`
  - [ ] Add latency & strategy distribution counters
  - [ ] Define SLOs and baseline metrics
- [ ] **Caching & Performance RFC (Phase 2.4 Prep)** `P2`
  - [ ] Draft caching architecture (routing/model selection layers)
  - [ ] Define cache invalidation & metrics plan
- [ ] **Markdown Lint Compliance Policy** `P2`
  - [ ] Decide on remediation vs. selective ignore list
  - [ ] Automate lint in CI with clear contribution guidance
- [ ] **Dependency Drift Enforcement** `P0`
  - [ ] Integrate scripts/check_python_deps_sync.sh into CI fail-fast job (Python dependency drift)
  - [ ] Document workflow in CONTRIBUTING (future)
