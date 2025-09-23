"""
OpenAI Response Examples - Python Implementation
==============================================

This module provides practical examples of OpenAI client response patterns
for different GPT-5 model variants. These examples can be used as templates
for integrating OpenAI responses in Python applications.

Usage:
    python openai_response_examples.py

Requirements:
    pip install openai python-dotenv
"""

import os
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass

try:
    from openai import OpenAI, AsyncOpenAI
except ImportError:
    print("OpenAI package not installed. Install with: pip install openai")
    exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Install with: pip install python-dotenv")


@dataclass
class ModelConfig:
    """Configuration for different model types"""
    name: str
    temperature: Optional[float] = None
    max_output_tokens: Optional[int] = None
    top_p: Optional[float] = None
    text_config: Optional[Dict[str, Any]] = None
    reasoning_config: Optional[Dict[str, Any]] = None


class OpenAIResponseExamples:
    """
    Examples of OpenAI response patterns for different model configurations.
    
    Note: GPT-5 models shown are conceptual examples for future reference.
    Please refer to the Models Manifest for currently supported models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        
        # Model configurations
        self.models = {
            'chat_latest': ModelConfig(
                name='gpt-5-chat-latest',
                temperature=2,
                max_output_tokens=16384,
                top_p=1,
                text_config={},
                reasoning_config={}
            ),
            'mini': ModelConfig(
                name='gpt-5-mini',
                text_config={
                    'format': {'type': 'text'},
                    'verbosity': 'high'
                },
                reasoning_config={
                    'effort': 'high',
                    'summary': 'auto'
                }
            ),
            'nano': ModelConfig(
                name='gpt-5-nano',
                text_config={
                    'format': {'type': 'text'},
                    'verbosity': 'low'
                },
                reasoning_config={
                    'effort': 'minimal',
                    'summary': 'detailed'
                }
            )
        }
    
    def create_gpt5_chat_latest_response(self, system_prompt: str) -> Dict[str, Any]:
        """
        Create a response using GPT-5 Chat Latest configuration.
        Optimized for complex reasoning and creative tasks.
        
        Args:
            system_prompt: The system prompt to use
            
        Returns:
            Response configuration dictionary
        """
        config = self.models['chat_latest']
        
        try:
            response = self.client.responses.create(
                model=config.name,
                input=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "input_text",
                                "text": system_prompt
                            }
                        ]
                    }
                ],
                text=config.text_config,
                reasoning=config.reasoning_config,
                tools=[],
                temperature=config.temperature,
                max_output_tokens=config.max_output_tokens,
                top_p=config.top_p,
                store=True
            )
            return response
        except Exception as e:
            print(f"Note: This is a conceptual example. Current error: {e}")
            return self._mock_response('gpt-5-chat-latest', system_prompt)
    
    def create_gpt5_mini_response(self, system_prompt: str) -> Dict[str, Any]:
        """
        Create a response using GPT-5 Mini configuration.
        Balanced performance for general development tasks.
        
        Args:
            system_prompt: The system prompt to use
            
        Returns:
            Response configuration dictionary
        """
        config = self.models['mini']
        
        try:
            response = self.client.responses.create(
                model=config.name,
                input=[
                    {
                        "role": "developer",
                        "content": [
                            {
                                "type": "input_text",
                                "text": system_prompt
                            }
                        ]
                    }
                ],
                text=config.text_config,
                reasoning=config.reasoning_config,
                tools=[],
                store=True
            )
            return response
        except Exception as e:
            print(f"Note: This is a conceptual example. Current error: {e}")
            return self._mock_response('gpt-5-mini', system_prompt)
    
    def create_gpt5_nano_response(self, system_prompt: str) -> Dict[str, Any]:
        """
        Create a response using GPT-5 Nano configuration.
        Lightweight and efficient for simple tasks.
        
        Args:
            system_prompt: The system prompt to use
            
        Returns:
            Response configuration dictionary
        """
        config = self.models['nano']
        
        try:
            response = self.client.responses.create(
                model=config.name,
                input=[
                    {
                        "role": "developer",
                        "content": [
                            {
                                "type": "input_text",
                                "text": system_prompt
                            }
                        ]
                    }
                ],
                text=config.text_config,
                reasoning=config.reasoning_config,
                tools=[],
                store=True
            )
            return response
        except Exception as e:
            print(f"Note: This is a conceptual example. Current error: {e}")
            return self._mock_response('gpt-5-nano', system_prompt)
    
    async def create_async_response(self, model_type: str, system_prompt: str) -> Dict[str, Any]:
        """
        Create an asynchronous response using the specified model type.
        
        Args:
            model_type: One of 'chat_latest', 'mini', 'nano'
            system_prompt: The system prompt to use
            
        Returns:
            Response configuration dictionary
        """
        if model_type not in self.models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        config = self.models[model_type]
        
        try:
            response = await self.async_client.responses.create(
                model=config.name,
                input=[
                    {
                        "role": "developer" if model_type != 'chat_latest' else "system",
                        "content": [
                            {
                                "type": "input_text",
                                "text": system_prompt
                            }
                        ]
                    }
                ],
                text=config.text_config or {},
                reasoning=config.reasoning_config or {},
                tools=[],
                **({"temperature": config.temperature} if config.temperature else {}),
                **({"max_output_tokens": config.max_output_tokens} if config.max_output_tokens else {}),
                **({"top_p": config.top_p} if config.top_p else {}),
                store=True
            )
            return response
        except Exception as e:
            print(f"Note: This is a conceptual example. Current error: {e}")
            return self._mock_response(config.name, system_prompt)
    
    def _mock_response(self, model: str, prompt: str) -> Dict[str, Any]:
        """
        Create a mock response for demonstration purposes.
        
        Args:
            model: Model name
            prompt: Input prompt
            
        Returns:
            Mock response dictionary
        """
        return {
            "id": "example-response",
            "object": "response",
            "created": 1640995200,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"This is a conceptual example response from {model} for prompt: '{prompt[:50]}...'"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 30,
                "total_tokens": 50
            }
        }
    
    def demonstrate_all_models(self):
        """Demonstrate all three model configurations"""
        
        print("OpenAI Response Examples - Python Implementation")
        print("=" * 50)
        print()
        
        system_prompt = "You are a helpful AI assistant for code generation and analysis."
        
        # GPT-5 Chat Latest
        print("1. GPT-5 Chat Latest (High Performance)")
        print("-" * 40)
        response = self.create_gpt5_chat_latest_response(system_prompt)
        print(f"Model: {response.get('model', 'N/A')}")
        print(f"Response: {response.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
        print()
        
        # GPT-5 Mini
        print("2. GPT-5 Mini (Balanced Performance)")
        print("-" * 40)
        response = self.create_gpt5_mini_response(system_prompt)
        print(f"Model: {response.get('model', 'N/A')}")
        print(f"Response: {response.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
        print()
        
        # GPT-5 Nano
        print("3. GPT-5 Nano (Lightweight Performance)")
        print("-" * 40)
        response = self.create_gpt5_nano_response(system_prompt)
        print(f"Model: {response.get('model', 'N/A')}")
        print(f"Response: {response.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
        print()
        
        print("Note: These are conceptual examples for future OpenAI models.")
        print("Please refer to the Models Manifest for currently supported models.")


async def async_example():
    """Demonstrate asynchronous usage"""
    print("\nAsynchronous Example:")
    print("-" * 20)
    
    try:
        examples = OpenAIResponseExamples()
        response = await examples.create_async_response(
            'mini', 
            'Generate a simple Python function for string reversal.'
        )
        print(f"Async Response: {response.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Example error (expected for conceptual models): {e}")


if __name__ == "__main__":
    try:
        # Synchronous examples
        examples = OpenAIResponseExamples()
        examples.demonstrate_all_models()
        
        # Asynchronous example
        asyncio.run(async_example())
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set your OPENAI_API_KEY environment variable.")
    except Exception as e:
        print(f"Example error (expected for conceptual models): {e}")