# Web Search Implementation for Monkey Coder Agents

## Overview

This document describes the web search capabilities that have been added to the Monkey Coder agent system, enabling agents to verify current information and maintain date awareness.

## What Was Implemented

### 1. Enhanced Agent Executor (`agent_executor_enhanced.py`)

A new enhanced version of the agent executor that includes:

- **Date Awareness**: All agents know the current date and include it in their prompts
- **Web Search Tools**: Provider-specific web search configurations
- **Verification Reminders**: Instructions to verify technical information through web search
- **Confidence Boost**: Higher confidence scores when web search is used

#### Key Features:

```python
# Date awareness in every prompt
current_date = datetime.utcnow().strftime("%B %d, %Y")
system_prompt = f"You are an expert developer. Today's date is {current_date}..."

# Web search tools for each provider
tools = {
    "openai": {"type": "web_search_preview"},
    "groq": {"type": "web_search"},
    "grok": {"type": "live_search"},
    "anthropic": # Uses search result injection
}
```

### 2. Enhanced System Prompts

Each agent type now has enhanced prompts with specific web search instructions:

- **Developer**: Verify library versions, API changes, security updates
- **Reviewer**: Cross-check CVEs, verify deprecated methods, confirm best practices
- **Architect**: Research current patterns, verify framework capabilities
- **Tester**: Verify testing framework syntax, research test patterns
- **Documenter**: Verify API documentation, check terminology
- **Security**: Search for recent CVEs, verify OWASP recommendations
- **Researcher**: Use web search extensively, cross-reference sources

### 3. Web Search Configuration (`web_search_config.py`)

A comprehensive configuration system for web search:

- **Provider Settings**: Specific configurations for OpenAI, Anthropic, Groq, and Grok
- **Search Prompts**: Reusable prompts for date awareness and verification
- **Phase-Specific Reminders**: Tailored search instructions for each orchestration phase
- **Metrics Tracking**: Track web search usage and confidence improvements

### 4. Integration with Orchestration

The orchestration coordinator can now:

- Use the enhanced executor when available
- Enable web search for appropriate phases (analysis, implementation, testing, review)
- Pass web search parameters to agents
- Track web search usage in results

## How It Works

### Agent Execution Flow with Web Search

1. **Agent receives task** from orchestrator
2. **System prompt includes**:
   - Current date awareness
   - Role-specific web search reminders
   - Instructions to verify information
3. **Tools configured** based on provider:
   - OpenAI: `web_search_preview`
   - Groq: `web_search`
   - Grok/xAI: `live_search`
   - Anthropic: Search result injection
4. **Agent makes API call** with tools enabled
5. **Response includes**:
   - Web search results used
   - Higher confidence score
   - Date-aware content

### Example Usage

```python
# Create enhanced executor
executor = EnhancedAgentExecutor(provider_registry=registry)

# Execute with web search
result = await executor.execute_agent_task(
    agent_type="developer",
    prompt="Create a React component using the latest hooks",
    enable_web_search=True  # Enables web search tools
)

# Result includes web search metadata
print(f"Web search used: {result['web_search_used']}")
print(f"Date aware: {result['current_date_aware']}")
print(f"Confidence: {result['confidence']}")
```

## Benefits

### 1. **Current Information**
- Agents verify library versions before suggesting code
- Check for deprecated APIs and methods
- Find recent security vulnerabilities

### 2. **Better Accuracy**
- Cross-reference multiple sources
- Verify technical specifications
- Confirm best practices are current

### 3. **Date Awareness**
- Agents know the current date
- Can assess information currency
- Understand temporal context

### 4. **Higher Confidence**
- Web search boosts confidence scores
- More reliable code generation
- Better informed decisions

## Testing

A comprehensive test suite (`test_web_search_integration.py`) verifies:

- Date awareness in all prompts
- Proper tool configuration for each provider
- Web search enablement for appropriate phases
- Confidence boost with web search
- Metrics tracking

## Next Steps

To fully activate web search in production:

1. **Update Provider Adapters**: Modify each provider adapter to handle the tools parameter
2. **API Key Configuration**: Ensure providers that support web search have proper API access
3. **Enable in Orchestrator**: Set `use_enhanced_executor=True` in production
4. **Monitor Metrics**: Track web search usage and impact on quality

## Configuration

### Environment Variables

```bash
# Enable web search features
ENABLE_WEB_SEARCH=true
WEB_SEARCH_CONTEXT_SIZE=high

# Provider-specific settings (if needed)
OPENAI_WEB_SEARCH_ENABLED=true
GROQ_WEB_SEARCH_ENABLED=true
GROK_LIVE_SEARCH_ENABLED=true
```

### Python Configuration

```python
from monkey_coder.config.web_search_config import WebSearchConfig

# Configure web search
config = WebSearchConfig(
    enabled=True,
    verify_technical_info=True,
    check_library_versions=True,
    verify_security_updates=True
)
```

## Impact

With web search enabled, the Monkey Coder system will:

- Generate more accurate and current code
- Avoid suggesting deprecated libraries or patterns
- Identify security issues proactively
- Provide better informed architectural decisions
- Create more reliable test cases
- Write more accurate documentation

This positions Monkey Coder as a premium AI development tool that stays current with the rapidly evolving software ecosystem.