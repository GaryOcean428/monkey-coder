[← Back to Roadmap Index](../roadmap.md)

# Phase 1.7: Critical Implementation Gaps 🚨

**Status:** NOT STARTED  
**Priority:** P0 - CRITICAL BLOCKERS  
**Timeline:** 11-16 weeks (3-4 months)  
**Created:** 2025-01-13  
**Impact:** Without these implementations, the CLI tool is non-functional for real development work

## Executive Summary

Based on comprehensive assessment (2025-01-13), Monkey Coder is **~60-70% architecturally complete** but **0% functionally complete** for actual code generation. The system has sophisticated routing and orchestration but no real AI provider integration, making it unable to generate actual code.

### Critical Finding
**The project has a Ferrari engine without wheels** - Advanced quantum routing and multi-agent orchestration are ready, but there's nothing to route to. No actual AI API calls are implemented.

### Latest AI Model Specifications
The implementation must use the latest AI models as specified in `packages/core/monkey_coder/models.py`:

**OpenAI (Primary Provider)**
- **Default Model:** `gpt-5` (Latest flagship for coding and agentic tasks)
- **Reasoning Models:** `o3`, `o3-pro`, `o1`, `o1-mini` (for complex problem solving)
- **Fallback Models:** `gpt-5-mini`, `gpt-4.1`, `gpt-4.1-mini`

**Anthropic (Secondary Provider)**  
- **Default Model:** `claude-sonnet-4-20250514` (Per user specification)
- **Most Capable:** `claude-opus-4-1-20250805` (Latest and most powerful)
- **Fallback Models:** `claude-opus-4-20250514`, `claude-3-7-sonnet-20250219`

**Google (Tertiary Provider)**
- **Default Model:** `gemini-2.5-pro`
- **Fast Models:** `models/gemini-2.5-flash`, `models/gemini-2.0-flash`

**xAI/Grok (Experimental)**
- **Default Model:** `grok-4-latest`
- **Alternatives:** `grok-3`, `grok-3-mini`, `grok-3-fast`

All implementations must reference these exact model names and include proper fallback logic as defined in the model registry.

---

## 🔴 Phase 1.7.1: Core AI Functionality (P0 - 4-6 weeks)

**BLOCKER: Without this, the entire system is non-functional**

### 1. Real AI Provider Integration ⚠️ **CRITICAL**
```yaml
Status: NOT STARTED
Priority: P0 - Absolute Blocker
Timeline: 2 weeks
Impact: System cannot generate any real code without this

Tasks:
  - [ ] Implement OpenAI adapter with real API calls using latest models
  - [ ] Implement Anthropic adapter with real API calls using latest models
  - [ ] Add proper API key validation and management
  - [ ] Implement token counting and usage tracking
  - [ ] Add provider fallback logic for failures
  - [ ] Test with actual API calls and verify responses

Latest Model Specifications to Implement:
  OpenAI:
    - Default: gpt-5 (latest flagship model)
    - Alternatives: gpt-5-mini, gpt-4.1, o3, o3-pro
    - Reasoning: o1, o1-mini, o3-deep-research
    - Search: gpt-4o-search-preview
  
  Anthropic:
    - Default: claude-sonnet-4-20250514 (per user specification)
    - Latest: claude-opus-4-1-20250805 (most capable)
    - Alternatives: claude-opus-4-20250514, claude-3-7-sonnet-20250219
  
  Google:
    - Default: gemini-2.5-pro
    - Alternatives: models/gemini-2.5-flash, models/gemini-2.0-flash
  
  xAI/Grok:
    - Default: grok-4-latest
    - Alternatives: grok-3, grok-3-mini, grok-3-fast

Files to Modify:
  - packages/core/monkey_coder/providers/openai_adapter.py
  - packages/core/monkey_coder/providers/anthropic_adapter.py
  - packages/core/monkey_coder/providers/google_adapter.py
  - packages/core/monkey_coder/providers/grok_adapter.py
  - packages/core/monkey_coder/providers/__init__.py

Current State:
  - Adapters exist but return mock responses
  - No actual HTTP calls to AI providers
  - Token counting is simulated, not real
  - Model registry is complete with latest specifications
```

### 2. Streaming Response Implementation ⚠️ **CRITICAL**
```yaml
Status: PARTIAL
Priority: P0 - Major UX Blocker
Timeline: 1 week
Impact: Poor user experience, appears frozen during generation

Tasks:
  - [ ] Implement SSE (Server-Sent Events) in FastAPI
  - [ ] Add streaming support to provider adapters
  - [ ] Update CLI to handle streaming responses properly
  - [ ] Add progress indicators for long operations
  - [ ] Implement timeout handling for stuck streams

Files to Modify:
  - packages/core/monkey_coder/app/main.py (add SSE endpoints)
  - packages/cli/src/api-client.ts (fix streaming handler)
  - packages/core/monkey_coder/core/orchestrator.py

Current State:
  - CLI expects streaming but backend doesn't provide it
  - Mock streaming exists but not connected to real providers
```

### 3. File System Operations ⚠️ **CRITICAL**
```yaml
Status: NOT STARTED
Priority: P0 - Core Functionality
Timeline: 1.5 weeks
Impact: Cannot read or write actual code files

Tasks:
  - [ ] Implement safe file reading with path validation
  - [ ] Add file writing with backup creation
  - [ ] Implement project structure analysis
  - [ ] Add code parsing for context extraction
  - [ ] Implement diff generation for modifications
  - [ ] Add file watching for auto-reload

Files to Create:
  - packages/core/monkey_coder/filesystem/__init__.py
  - packages/core/monkey_coder/filesystem/operations.py
  - packages/core/monkey_coder/filesystem/project_analyzer.py

Current State:
  - No file system integration exists
  - CLI can't read project files for context
  - Can't write generated code to disk
```

### 4. CLI-Backend Authentication Flow ⚠️ **CRITICAL**
```yaml
Status: BROKEN
Priority: P0 - Blocks All Usage
Timeline: 1 week
Impact: Users cannot authenticate to use the system

Tasks:
  - [ ] Fix API key generation and validation
  - [ ] Implement proper CLI auth storage
  - [ ] Add session management
  - [ ] Fix cookie handling between CLI and backend
  - [ ] Add auth retry logic
  - [ ] Implement offline mode detection

Files to Modify:
  - packages/cli/src/commands/auth.ts
  - packages/core/monkey_coder/auth/api_key_manager.py
  - packages/cli/src/api-client.ts

Current State:
  - Auth endpoints exist but don't properly validate
  - CLI can't maintain authenticated sessions
  - API keys aren't properly validated
```

### 5. Context Management System ⚠️ **CRITICAL**
```yaml
Status: NOT STARTED
Priority: P0 - Required for Multi-turn
Timeline: 1.5 weeks
Impact: No conversation memory, each request is isolated

Tasks:
  - [ ] Implement conversation history storage
  - [ ] Add context window management
  - [ ] Implement semantic search for relevant context
  - [ ] Add project context extraction
  - [ ] Implement context pruning strategies
  - [ ] Add context persistence across sessions

Files to Create:
  - packages/core/monkey_coder/context/__init__.py
  - packages/core/monkey_coder/context/manager.py
  - packages/core/monkey_coder/context/storage.py

Current State:
  - No context management exists
  - Each request is completely isolated
  - No conversation memory
```

---

## 🟡 Phase 1.7.2: Essential Features (P1 - 3-4 weeks)

### 6. Real Code Generation & Analysis
```yaml
Status: NOT STARTED
Priority: P1 - Core Feature
Timeline: 2 weeks

Tasks:
  - [ ] Implement syntax validation
  - [ ] Add language-specific formatting
  - [ ] Implement import resolution
  - [ ] Add dependency detection
  - [ ] Implement test generation
  - [ ] Add documentation generation
```

### 7. Project-Aware Context
```yaml
Status: NOT STARTED  
Priority: P1 - Major Feature
Timeline: 1 week

Tasks:
  - [ ] Parse package.json/requirements.txt
  - [ ] Detect project type and framework
  - [ ] Extract project dependencies
  - [ ] Identify coding patterns
  - [ ] Load project-specific configs
```

### 8. Error Handling & Recovery
```yaml
Status: PARTIAL
Priority: P1 - Reliability
Timeline: 1 week

Tasks:
  - [ ] Add comprehensive error catching
  - [ ] Implement retry logic with backoff
  - [ ] Add fallback providers
  - [ ] Implement graceful degradation
  - [ ] Add error reporting to users
```

---

## 🟢 Phase 1.7.3: Production Readiness (P2 - 2-3 weeks)

### 9. Deployment Configuration
```yaml
Status: MISSING
Priority: P2 - Deployment Blocker
Timeline: 3 days

Tasks:
  - [ ] Create Procfile for Railway
  - [ ] Add production environment config
  - [ ] Setup proper logging
  - [ ] Configure monitoring
  - [ ] Add health checks
```

### 10. Usage Tracking & Rate Limiting
```yaml
Status: MOCKED
Priority: P2 - Business Critical
Timeline: 1 week

Tasks:
  - [ ] Implement real token counting
  - [ ] Add usage database storage
  - [ ] Implement rate limiting
  - [ ] Add billing integration
  - [ ] Create usage dashboards
```

### 11. Performance Optimization
```yaml
Status: NOT STARTED
Priority: P2 - Performance
Timeline: 1 week

Tasks:
  - [ ] Add response caching
  - [ ] Implement connection pooling
  - [ ] Optimize database queries
  - [ ] Add CDN for static assets
  - [ ] Implement lazy loading
```

---

## 📊 Comparison Matrix: Current vs Required

| Component | Current State | Required State | Gap Severity |
|-----------|--------------|----------------|--------------|
| **AI Provider Calls** | Mock responses only | Real API integration with gpt-5/claude-sonnet-4 | 🔴 CRITICAL |
| **Code Generation** | Returns empty results | Actual code generation using latest models | 🔴 CRITICAL |
| **Model Registry** | Complete with latest specs | Use gpt-5, claude-sonnet-4-20250514 defaults | 🔴 CRITICAL |
| **File Operations** | None | Read/write project files | 🔴 CRITICAL |
| **Streaming** | Broken | Real-time streaming from providers | 🔴 CRITICAL |
| **Authentication** | Partially broken | Working CLI auth | 🔴 CRITICAL |
| **Context Management** | None | Multi-turn memory | 🟡 MAJOR |
| **Project Awareness** | None | Framework detection | 🟡 MAJOR |
| **Error Handling** | Basic | Comprehensive with fallbacks | 🟡 MAJOR |
| **Deployment** | Incomplete | Production ready | 🟢 IMPORTANT |
| **Usage Tracking** | Mocked | Real metrics with token counting | 🟢 IMPORTANT |

---

## 🎯 Implementation Strategy

### Week 1-2: Unblock Core Functionality
1. **Day 1-3:** Implement OpenAI provider with real API calls
   - Priority models: gpt-5, gpt-4.1, o3 (for reasoning tasks)
   - Add model validation and fallback logic
2. **Day 4-5:** Fix CLI-Backend authentication flow
   - Validate API keys with actual provider endpoints
3. **Day 6-7:** Add basic file read operations
   - Project structure analysis with framework detection
4. **Day 8-10:** Implement streaming responses
   - Test with gpt-5 and claude-sonnet-4-20250514
5. **Day 11-14:** Add basic context management
   - Support for multi-turn conversations with model memory

### Week 3-4: Make It Usable
1. Complete Anthropic provider integration (claude-sonnet-4-20250514 default)
2. Add file write operations with safety and backup
3. Implement project context extraction with language detection
4. Add comprehensive error handling with provider fallbacks

### Week 5-6: Production Features  
1. Add usage tracking with accurate token counting per model
2. Complete deployment configuration for Railway
3. Implement caching and optimization for expensive models
4. Add monitoring and alerting with provider-specific metrics

### Week 7-8: Testing & Polish
1. Comprehensive integration testing with all latest models
2. Performance optimization for gpt-5 and claude-4 models
3. Documentation updates with model specifications
4. User acceptance testing with real AI code generation

---

## 🚀 Quick Wins (Can implement immediately)

### 1. OpenAI Integration (2-3 days)
```python
# packages/core/monkey_coder/providers/openai_adapter.py
# Replace mock with real implementation using latest models:

async def generate(self, prompt: str, **kwargs):
    # Use default gpt-5 or fallback to gpt-4.1
    model = kwargs.get("model", "gpt-5") or "gpt-4.1"
    
    response = await self.client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=kwargs.get("stream", False),
        max_tokens=kwargs.get("max_tokens", 4096),
        temperature=kwargs.get("temperature", 0.1)
    )
    
    if kwargs.get("stream"):
        return response  # Return streaming response
    else:
        return response.choices[0].message.content

# Model validation using latest specifications
def validate_model(self, model: str) -> str:
    """Validate and resolve model name with latest specifications."""
    from ..models import MODEL_REGISTRY, MODEL_ALIASES, resolve_model
    
    resolved = resolve_model(model, ProviderType.OPENAI)
    if resolved in MODEL_REGISTRY[ProviderType.OPENAI]:
        return resolved
    
    # Fallback to default gpt-5
    logger.warning(f"Model {model} not found, using default gpt-5")
    return "gpt-5"
```

### 2. Anthropic Integration (2-3 days)
```python
# packages/core/monkey_coder/providers/anthropic_adapter.py
# Implement real integration using latest Claude models:

async def generate(self, prompt: str, **kwargs):
    # Use default claude-sonnet-4-20250514 per user specification
    model = kwargs.get("model", "claude-sonnet-4-20250514")
    
    response = await self.client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=kwargs.get("max_tokens", 4096),
        temperature=kwargs.get("temperature", 0.1),
        stream=kwargs.get("stream", False)
    )
    
    return response.content[0].text if response.content else ""
```

### 2. Fix Authentication (1 day)
```typescript
// packages/cli/src/commands/auth.ts
// Add proper API key storage and validation

import { APIClient } from '../api-client';
import { config } from '../config';

export async function loginCommand(apiKey?: string) {
    try {
        const client = new APIClient(apiKey);
        const response = await client.validateApiKey();
        
        if (response.valid) {
            config.set('apiKey', apiKey);
            console.log('✅ Authentication successful');
        } else {
            throw new Error('Invalid API key');
        }
    } catch (error) {
        console.error('❌ Authentication failed:', error.message);
        process.exit(1);
    }
}
```

### 3. Basic File Operations (1 day)
```python
# packages/core/monkey_coder/filesystem/operations.py
# Add simple file reading for context with safety checks

import os
from pathlib import Path
from typing import Dict, List, Optional

def read_project_file(filepath: str) -> str:
    """Safely read a project file with validation."""
    path = Path(filepath).resolve()
    
    # Security check - ensure file is in allowed directory
    if not is_safe_path(path):
        raise ValueError(f"Access denied to file: {filepath}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding for binary files
        with open(path, 'r', encoding='latin-1') as f:
            return f.read()

def analyze_project_structure(root_path: str) -> Dict:
    """Analyze project structure for context."""
    structure = {
        'files': [],
        'directories': [],
        'framework': None,
        'language': None
    }
    
    root = Path(root_path)
    
    # Detect framework/project type
    if (root / 'package.json').exists():
        structure['framework'] = 'nodejs'
        structure['language'] = 'javascript'
    elif (root / 'requirements.txt').exists() or (root / 'pyproject.toml').exists():
        structure['framework'] = 'python'
        structure['language'] = 'python'
    
    return structure

def is_safe_path(path: Path) -> bool:
    """Check if path is safe to access (no directory traversal)."""
    try:
        path.resolve().relative_to(Path.cwd().resolve())
        return True
    except ValueError:
        return False
```

---

## 📈 Success Metrics

### Phase 1 Completion Criteria
- [ ] Can generate real code using gpt-5 and claude-sonnet-4-20250514
- [ ] CLI can authenticate and maintain sessions
- [ ] Can read and write project files safely
- [ ] Streaming responses work end-to-end with all providers
- [ ] Basic context management across turns
- [ ] Model fallback logic works (gpt-5 → gpt-4.1 → gpt-5-mini)

### Phase 2 Completion Criteria  
- [ ] Project-aware context extraction works
- [ ] Error handling prevents crashes with provider fallbacks
- [ ] Usage tracking records real metrics with accurate token counts
- [ ] 90% of commands execute successfully
- [ ] Support for reasoning models (o3, o3-pro) implemented

### Phase 3 Completion Criteria
- [ ] Deployed to Railway successfully
- [ ] Performance meets targets (under 2s response time for gpt-5)
- [ ] Monitoring alerts work with provider-specific metrics
- [ ] Documentation includes latest model specifications

---

## ⚠️ Risk Mitigation

### High Risk Items
1. **Provider API Changes:** Implement version checking and fallbacks
2. **Rate Limiting:** Add queueing and retry logic
3. **Context Overflow:** Implement smart pruning algorithms
4. **Authentication Issues:** Add multiple auth methods

### Mitigation Strategies
- Start with OpenAI (most stable API)
- Implement gradual rollout with feature flags
- Add comprehensive logging from day 1
- Create integration test suite early

---

## 📝 Notes

- The quantum routing system, while impressive, is currently routing to nowhere
- Multi-agent orchestration is ready but has no real agents to orchestrate  
- The web frontend exists but the API it calls doesn't do anything real
- Authentication system is 90% complete but the final 10% blocks everything
- **Model specifications are up-to-date:** The `models.py` file contains the latest model definitions including gpt-5, claude-4.1 family, gemini-2.5, and grok-4
- **Implementation priority:** Focus on gpt-5 and claude-sonnet-4-20250514 as primary models for initial implementation

**Bottom Line:** The architecture is solid, but without real AI provider integration using the latest models, this is essentially a very sophisticated mock system. Priority must be on implementing actual AI API calls with gpt-5 and claude-sonnet-4-20250514 before any other enhancements.