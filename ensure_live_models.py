#!/usr/bin/env python3
"""
Use Monkey Coder to ensure all model responses are live (not mocked) 
and respect MODEL_MANIFEST.md as the canonical source of truth.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import sys
sys.path.insert(0, 'packages/core')

from monkey_coder.core.agent_executor import AgentExecutor
from monkey_coder.providers import ProviderRegistry
from monkey_coder.filesystem import write_file, read_file

# Load environment
env_path = Path('packages/core/.env.local')
if env_path.exists():
    load_dotenv(env_path)
    print(f'Loaded {env_path}')

async def ensure_live_models():
    """Use Monkey Coder to ensure all models are live and canonical."""
    registry = ProviderRegistry()
    await registry.initialize_all()
    executor = AgentExecutor(registry)
    
    print("=" * 60)
    print("MONKEY CODER: ENSURING LIVE MODELS & CANONICAL MANIFEST")
    print("=" * 60)
    
    # Read MODEL_MANIFEST.md
    manifest_content = read_file('MODEL_MANIFEST.md')
    
    # Get Monkey Coder to analyze and fix the system
    result = await executor.execute_agent_task(
        agent_type='developer',
        prompt=f"""CRITICAL TASK: Ensure Monkey Coder uses ONLY live AI models and respects MODEL_MANIFEST.md as canonical.

MODEL_MANIFEST.md is the SINGLE SOURCE OF TRUTH for all AI models. This file contains:
{manifest_content[:3000]}...

Your tasks:
1. Analyze the codebase to find ANY mock models, fake responses, or hardcoded test data
2. Identify any code that doesn't respect MODEL_MANIFEST.md as canonical
3. Find any places where deprecated models are still being referenced
4. Ensure ALL model calls go through real AI provider APIs (no mocking)
5. Verify the ModelManifestValidator is being used everywhere

Check these critical files:
- packages/core/monkey_coder/providers/*
- packages/core/monkey_coder/core/agent_executor.py
- packages/core/monkey_coder/core/orchestrator.py
- packages/core/monkey_coder/models.py
- packages/core/monkey_coder/models/model_validator.py

Generate a detailed report of:
1. Any mock models or fake responses found
2. Any violations of MODEL_MANIFEST.md
3. Any deprecated model references
4. Recommendations to ensure only live models are used
5. Code changes needed to enforce MODEL_MANIFEST.md everywhere

BE THOROUGH. This is critical for production readiness.""",
        provider='openai',
        model='gpt-4.1',  # Using canonical model from manifest
        max_tokens=4000
    )
    
    if result.get('status') == 'completed':
        analysis = result.get('output', '')
        
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS:")
        print("=" * 60)
        print(analysis)
        
        fixes = ""  # Initialize fixes variable
        
        # Now get Monkey to generate fixes
        fix_result = await executor.execute_agent_task(
            agent_type='developer',
            prompt=f"""Based on the analysis, create Python code to:

1. Add model manifest validation to EVERY provider
2. Remove or disable ANY mock models or test responses
3. Ensure MODEL_MANIFEST.md is checked before any model call
4. Add runtime validation that rejects non-canonical models
5. Create a startup check that validates all configured models

Generate the complete Python code changes needed to enforce this.
Focus on these key areas:
- Provider initialization must validate models
- Agent executor must check models before execution
- Orchestrator must use only canonical models
- Add logging for any model validation issues

Provide complete, production-ready code that can be directly applied.""",
            provider='openai',
            model='gpt-4.1',  # Using standard model that supports max_tokens
            max_tokens=4000
        )
        
        if fix_result.get('status') == 'completed':
            fixes = fix_result.get('output', '')
            
            # Save the fixes to a file
            write_file('model_compliance_fixes.py', fixes)
            
            print("\n" + "=" * 60)
            print("GENERATED FIXES:")
            print("=" * 60)
            print(fixes[:2000] + "..." if len(fixes) > 2000 else fixes)
            
            print("\n✅ Model compliance fixes saved to model_compliance_fixes.py")
            print("📝 Review and apply these changes to ensure canonical model usage")
        
        return analysis, fixes
    else:
        raise Exception(f"Analysis failed: {result.get('error')}")

async def validate_live_connections():
    """Validate that all providers are making real API calls."""
    registry = ProviderRegistry()
    await registry.initialize_all()
    executor = AgentExecutor(registry)
    
    print("\n" + "=" * 60)
    print("VALIDATING LIVE CONNECTIONS:")
    print("=" * 60)
    
    # Test each provider with a simple prompt
    providers_to_test = [
        ('openai', 'gpt-4.1-mini'),
        ('anthropic', 'claude-3-5-haiku-20241022'),
        ('google', 'gemini-2.5-flash-lite'),
        ('groq', 'llama-3.1-8b-instant'),
    ]
    
    for provider, model in providers_to_test:
        try:
            print(f"\nTesting {provider}/{model}...")
            result = await executor.execute_agent_task(
                agent_type='developer',
                prompt="Say 'LIVE' if you're a real AI model, not a mock.",
                provider=provider,
                model=model,
                max_tokens=50
            )
            
            if result.get('status') == 'completed':
                response = result.get('output', '')
                if 'LIVE' in response.upper() or 'REAL' in response.upper():
                    print(f"✅ {provider}/{model}: CONFIRMED LIVE")
                else:
                    print(f"⚠️  {provider}/{model}: Response unclear: {response[:100]}")
            else:
                print(f"❌ {provider}/{model}: Failed - {result.get('error')}")
                
        except Exception as e:
            print(f"❌ {provider}/{model}: Error - {str(e)}")
    
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)

async def main():
    try:
        # Ensure live models and canonical manifest
        analysis, fixes = await ensure_live_models()
        
        # Validate live connections
        await validate_live_connections()
        
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("1. Review model_compliance_fixes.py")
        print("2. Apply the fixes to enforce MODEL_MANIFEST.md")
        print("3. Run tests to verify all models are live")
        print("4. Remove any mock/test model code")
        print("5. Add startup validation for model compliance")
        print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())