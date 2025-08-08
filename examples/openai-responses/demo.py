#!/usr/bin/env python3
"""
OpenAI Response Examples - Quick Demo
=====================================

This script demonstrates the OpenAI response examples in action.
It shows all three model configurations and their outputs.

Usage:
    python demo.py
    
Note: This script uses mock responses since the GPT-5 models are conceptual.
For real API integration, set your OPENAI_API_KEY environment variable.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from openai_response_examples import OpenAIResponseExamples
except ImportError:
    print("Error: Could not import OpenAI response examples.")
    print("Please ensure you're running this script from the examples/openai-responses directory.")
    sys.exit(1)


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{title}")
    print("-" * len(title))


def print_response(response):
    """Print formatted response details"""
    print(f"Model: {response.get('model', 'N/A')}")
    print(f"Response ID: {response.get('id', 'N/A')}")
    
    if 'choices' in response and response['choices']:
        content = response['choices'][0].get('message', {}).get('content', 'N/A')
        print(f"Content: {content}")
    
    if 'usage' in response:
        usage = response['usage']
        print(f"Tokens - Prompt: {usage.get('prompt_tokens', 0)}, "
              f"Completion: {usage.get('completion_tokens', 0)}, "
              f"Total: {usage.get('total_tokens', 0)}")


async def run_async_demo():
    """Demonstrate async functionality"""
    print_section("Asynchronous Example")
    
    try:
        # Create examples instance (will use mock responses)
        examples = OpenAIResponseExamples()
        
        # Test async response generation
        response = await examples.create_async_response(
            'mini', 
            'Generate a Python function to calculate fibonacci numbers.'
        )
        
        print("✅ Async Response Generated:")
        print_response(response)
        
    except ValueError as e:
        print(f"ℹ️  Configuration Note: {e}")
        print("   (This is expected when OPENAI_API_KEY is not set)")
    except Exception as e:
        print(f"ℹ️  Demo Note: {e}")
        print("   (Using mock responses for demonstration)")


def run_sync_demo():
    """Demonstrate synchronous functionality"""
    print_section("Synchronous Examples")
    
    try:
        # Create examples instance (will use mock responses)
        examples = OpenAIResponseExamples()
        
        # Test all three model configurations
        system_prompt = "You are a helpful AI assistant specialized in code generation and analysis."
        
        # GPT-5 Chat Latest
        print("\n🚀 GPT-5 Chat Latest (High Performance):")
        response1 = examples.create_gpt5_chat_latest_response(system_prompt)
        print_response(response1)
        
        # GPT-5 Mini
        print("\n⚡ GPT-5 Mini (Balanced Performance):")
        response2 = examples.create_gpt5_mini_response(system_prompt)
        print_response(response2)
        
        # GPT-5 Nano
        print("\n💡 GPT-5 Nano (Lightweight Performance):")
        response3 = examples.create_gpt5_nano_response(system_prompt)
        print_response(response3)
        
        print("\n✅ All model configurations demonstrated successfully!")
        
    except ValueError as e:
        print(f"ℹ️  Configuration Note: {e}")
        print("   Set OPENAI_API_KEY environment variable for real API calls")
    except Exception as e:
        print(f"ℹ️  Demo Note: {e}")
        print("   Using mock responses for demonstration purposes")


def show_model_configs():
    """Display model configuration details"""
    print_section("Model Configuration Details")
    
    configs = {
        'GPT-5 Chat Latest': {
            'Temperature': '2.0 (Maximum creativity)',
            'Max Tokens': '16,384',
            'Top P': '1.0 (Full vocabulary)',
            'Best For': 'Complex reasoning, creative tasks'
        },
        'GPT-5 Mini': {
            'Text Format': 'High verbosity structured output',
            'Reasoning': 'High effort with auto summary',
            'Best For': 'Development tasks, code generation'
        },
        'GPT-5 Nano': {
            'Text Format': 'Low verbosity structured output',
            'Reasoning': 'Minimal effort with detailed summary',
            'Best For': 'Quick responses, simple tasks'
        }
    }
    
    for model, config in configs.items():
        print(f"\n📋 {model}:")
        for key, value in config.items():
            print(f"   {key}: {value}")


def show_usage_examples():
    """Show practical usage examples"""
    print_section("Practical Usage Examples")
    
    print("""
🔧 Integration Patterns:

1. **Python Backend**:
   ```python
   examples = OpenAIResponseExamples()
   response = examples.create_gpt5_mini_response("Your prompt here")
   ```

2. **TypeScript/JavaScript Frontend**:
   ```typescript
   const examples = new OpenAIResponseExamples();
   const response = await examples.createGpt5MiniResponse("Your prompt here");
   ```

3. **React Hook**:
   ```jsx
   const { generateResponse, loading } = useOpenAIResponses();
   const result = await generateResponse('mini', 'Your prompt');
   ```

4. **Express Middleware**:
   ```javascript
   app.post('/api/generate', middleware.generateResponse);
   ```

🌐 Accessibility Features:
✅ Both Python and TypeScript implementations
✅ Async/await support for modern applications  
✅ Error handling and validation
✅ Mock responses for testing and development
✅ Comprehensive documentation and examples
    """)


def main():
    """Main demo function"""
    print_header("OpenAI Response Examples - Interactive Demo")
    
    print("""
Welcome to the OpenAI Response Examples demonstration!

This demo showcases three conceptual GPT-5 model configurations:
• GPT-5 Chat Latest: High-performance complex reasoning
• GPT-5 Mini: Balanced general-purpose development  
• GPT-5 Nano: Lightweight efficient processing

Note: These are conceptual examples for future OpenAI models.
      Please refer to the Models Manifest for currently supported models.
    """)
    
    # Show model configurations
    show_model_configs()
    
    # Run synchronous demo
    run_sync_demo()
    
    # Run asynchronous demo
    print_section("Running Async Demo...")
    asyncio.run(run_async_demo())
    
    # Show usage examples
    show_usage_examples()
    
    print_header("Demo Complete")
    print("""
🎉 Demo completed successfully!

Next Steps:
1. Explore the full documentation: docs/docs/openai-response-examples.md
2. Check out the implementation files in this directory
3. Set OPENAI_API_KEY environment variable for real API integration
4. Refer to the Models Manifest for currently supported models

Happy coding! 🚀
    """)


if __name__ == "__main__":
    main()