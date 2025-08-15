#!/usr/bin/env python3
"""
Simple test of Monkey Coder generating unified SDK code.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent / "packages" / "core"))
load_dotenv(".env.local")

from monkey_coder.providers import ProviderRegistry
from monkey_coder.models import ExecuteRequest, PersonaConfig, ExecutionContext, TaskType, PersonaType
from monkey_coder.core.orchestrator import MultiAgentOrchestrator


async def test_simple_generation():
    print("🧪 Simple Unified SDK Generation Test")
    print("="*80)
    
    # Initialize
    print("Initializing...")
    registry = ProviderRegistry()
    await registry.initialize_all()
    orchestrator = MultiAgentOrchestrator(provider_registry=registry)
    
    # Simple request
    request = ExecuteRequest(
        prompt="Write a simple Python class that adds two numbers",
        task_type=TaskType.CODE_GENERATION,
        persona="developer",
        context=ExecutionContext(
            user_id="test",
            project_path=".",
            language="python"
        ),
        persona_config=PersonaConfig(persona="developer")
    )
    
    print("Executing...")
    try:
        response = await orchestrator.orchestrate(
            request=request,
            persona_context={"selected_persona": PersonaType.DEVELOPER}
        )
        
        if hasattr(response, 'model_dump'):
            result = response.model_dump()
        else:
            result = response
            
        print(f"Status: {result.get('status')}")
        if result.get('result'):
            res = result['result']
            if isinstance(res, dict):
                code = res.get('code', res.get('message', str(res)))
            else:
                code = str(res)
            print(f"Generated: {code[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        await registry.cleanup_all()


if __name__ == "__main__":
    asyncio.run(test_simple_generation())