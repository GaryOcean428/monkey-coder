# Monkey Coder Naming Manifest

> **Version:** 1.0.0  
> **Date:** 2025-01-31  
> **Purpose:** Establish consistent naming conventions across the Monkey Coder platform

## Core Principles

1. **Descriptive over Cryptic**: Names should clearly indicate functionality
2. **Consistency**: Use the same naming pattern across languages and modules
3. **Future-Proof**: Names should remain relevant as the system evolves
4. **Professional**: Avoid temporary/inspiration references in production code

## Component Naming Standards

### Primary Components

| Component | Correct Name | Purpose | Replaces |
|-----------|--------------|---------|----------|
| **Core Router** | `AdvancedRouter` | Base intelligent routing system | ~~Gary8D~~ |
| **Quantum Router** | `QuantumAdvancedRouter` | Quantum-enhanced routing system | ~~Gary8D Quantum~~ |
| **Persona System** | `PersonaRouter` | Persona-based routing | ~~SuperClaude~~ |
| **Configuration** | `PersonaConfig` | Persona configuration | ~~SuperClaudeConfig~~ |
| **Field Names** | `persona_config` | API field names | ~~superclause_config~~ |

### Routing System Hierarchy

```
AdvancedRouter (Base)
├── QuantumAdvancedRouter (Quantum-enhanced)
├── PersonaRouter (Persona-focused)
└── MultiAgentRouter (Multi-agent coordination)
```

### Configuration Naming

| Configuration Type | Class Name | Field Name | Purpose |
|-------------------|------------|------------|---------|
| Persona Configuration | `PersonaConfig` | `persona_config` | Persona and persona-related settings |
| Orchestration Configuration | `OrchestrationConfig` | `orchestration_config` | Multi-agent coordination settings |
| Quantum Configuration | `QuantumConfig` | `quantum_config` | Quantum routing settings |

### API Field Naming Conventions

**Current (Incorrect)**:
```json
{
  "superclause_config": { "persona": "developer" },
  "gary8d_config": { "parallel_futures": true }
}
```

**Correct**:
```json
{
  "persona_config": { "persona": "developer" },
  "quantum_config": { "parallel_execution": true }
}
```

## Module Naming Standards

### File and Class Names

| Module | File Name | Main Class | Purpose |
|--------|-----------|------------|---------|
| **Core Routing** | `routing.py` | `AdvancedRouter` | Base routing intelligence |
| **Quantum Routing** | `quantum_routing.py` | `QuantumAdvancedRouter` | Quantum-enhanced routing |
| **Persona Routing** | `persona_router.py` | `PersonaRouter` | Persona-based routing |
| **State Encoding** | `state_encoder.py` | `AdvancedStateEncoder` | 112-dimensional state representation |
| **DQN Integration** | `router_integration.py` | `DQNRouterBridge` | DQN-router integration |

### Package Structure

```
monkey_coder/
├── core/                   # Core routing and orchestration
│   ├── routing.py         # AdvancedRouter (base system)
│   ├── quantum_routing.py # QuantumAdvancedRouter
│   ├── persona_router.py  # PersonaRouter
│   └── orchestrator.py    # MultiAgentOrchestrator
├── quantum/               # Quantum routing components
│   ├── state_encoder.py   # AdvancedStateEncoder
│   ├── dqn_agent.py      # DQN routing agent
│   └── manager.py        # QuantumManager
└── models.py             # Data models and configurations
```

## Documentation Standards

### Comments and Docstrings

**Avoid**:
- References to inspiration projects (Gary8D, monkey1, etc.)
- Temporary or placeholder names
- Cryptic abbreviations

**Use**:
- Clear, functional descriptions
- Purpose-driven naming
- Professional terminology

**Example**:

```python
class QuantumAdvancedRouter(AdvancedRouter):
    """
    Quantum-enhanced router with 112-dimensional state representation.
    
    Extends the base AdvancedRouter with:
    - Advanced state encoding using multi-dimensional features
    - DQN-compatible routing decisions
    - Performance-based model selection
    - User preference learning
    """
```

## Migration Strategy

### Phase 1: Core Components (Current)
- ✅ Update quantum routing implementation with proper naming
- ✅ Create naming manifest
- 📅 Fix API model field names
- 📅 Update configuration classes

### Phase 2: API Consistency 
- 📅 Update `superclause_config` → `persona_config`
- 📅 Update `gary8d_config` → `quantum_config`
- 📅 Update all API endpoints and documentation
- 📅 Maintain backward compatibility during transition

### Phase 3: Documentation Cleanup
- 📅 Remove inspiration project references
- 📅 Update all docstrings and comments
- 📅 Standardize technical documentation
- 📅 Update roadmap and specifications

## Backward Compatibility

During the migration period:

1. **Maintain Aliases**: Keep old field names as aliases
2. **Deprecation Warnings**: Log warnings for deprecated names
3. **Gradual Migration**: Phase out old names over 2-3 releases
4. **Clear Documentation**: Document migration path for users

## Reference Project Handling

### Inspiration Attribution

When referencing inspiration from other projects:

**In Comments/Documentation**:
```python
# Advanced routing patterns inspired by quantum computing principles
# and multi-agent coordination research
```

**NOT**:
```python
# Gary8D-inspired router
# monkey1 patterns
```

### Technical Debt Items

| Current Reference | Replacement | Priority |
|-------------------|-------------|----------|
| Gary8D Router | AdvancedRouter | High |
| SuperClaude | PersonaRouter | High |
| superclause_config | persona_config | Critical |
| gary8d_config | quantum_config | Medium |

## Implementation Guidelines

### Code Review Checklist

- [ ] No inspiration project names in production code
- [ ] Consistent naming across TypeScript and Python
- [ ] Clear, descriptive class and method names
- [ ] Proper API field naming conventions
- [ ] Professional documentation and comments

### Testing Naming

Test files and classes should follow the same conventions:

```python
class TestQuantumAdvancedRouter:
    """Test quantum-enhanced routing functionality."""

class TestPersonaRouter:
    """Test persona-based routing decisions."""
```

## Exceptions

### Acceptable References

1. **Historical Context**: In CHANGELOG.md or migration guides
2. **Research Citations**: When citing academic or technical sources
3. **Internal Development**: In development notes or technical specs
4. **Version History**: In git commit messages or release notes

### Protected Terms

These terms are reserved for Monkey Coder platform:

- **Monkey Coder**: Platform name
- **Quantum Routing**: Core technology
- **Advanced Router**: Base routing system
- **Persona Router**: Persona system
- **DQN Agent**: Deep Q-Network routing agent

## Version History

- **v1.0.0** (2025-01-31): Initial naming manifest
- Future versions will track naming changes and migrations