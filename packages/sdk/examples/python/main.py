#!/usr/bin/env python3
"""
Python Example - Monkey Coder SDK

This example demonstrates how to use the Monkey Coder SDK in Python.
Run with: python main.py
"""

import os
import asyncio
from monkey_coder_sdk import (
    MonkeyCoderClient,
    MonkeyCoderClientConfig,
    create_code_generation_request,
    create_security_analysis_request,
    create_file_data,
    ExecutionContext,
    PersonaType,
    TaskType,
)


def handle_stream_event(event):
    """Handle streaming events from the API."""
    if event.type == 'start':
        print('🚀 Execution started...')
    elif event.type == 'progress':
        if event.progress and event.progress.percentage:
            bar = '█' * int(event.progress.percentage // 5)
            empty = '░' * (20 - int(event.progress.percentage // 5))
            print(f'📊 [{bar}{empty}] {event.progress.percentage}% - {event.progress.step}')
    elif event.type == 'result':
        print('📝 Intermediate result received')
    elif event.type == 'complete':
        print('✅ Execution completed!')
        if hasattr(event.data, 'result') and event.data.result:
            print('\nFinal result:')
            print(event.data.result.result)
    elif event.type == 'error':
        print(f'❌ Error: {event.error.message}')


def main():
    """Main function demonstrating SDK usage."""
    print('🐍 Python + Monkey Coder SDK Example')
    
    # Initialize the client
    config = MonkeyCoderClientConfig(
        base_url=os.getenv('MONKEY_CODER_BASE_URL', 'http://localhost:8000'),
        api_key=os.getenv('MONKEY_CODER_API_KEY'),
        timeout=60.0,  # 1 minute
        retries=3,
        retry_delay=1.0,
        max_retry_delay=10.0
    )
    
    client = MonkeyCoderClient(config)
    
    try:
        # Health check
        print('Checking API health...')
        health = client.health()
        print(f'✅ API Health: {health.status} (version {health.version})')
        
        # Code generation example
        print('\n📝 Generating Python code...')
        request = create_code_generation_request(
            prompt='Create a Python FastAPI server with authentication middleware and rate limiting',
            user_id='python-user',
            language='python',
            temperature=0.2,
            max_tokens=2048
        )
        
        response = client.execute(request)
        print(f'Code generation completed: {response.status}')
        print(f'Execution time: {response.execution_time}s')
        print(f'Tokens used: {response.usage.tokens_used if response.usage else "N/A"}')
        
        if response.result:
            print('\nGenerated code:')
            print('=' * 50)
            print(response.result.result)
            print('=' * 50)
        
        # Security analysis example
        print('\n🔒 Performing security analysis...')
        
        # Sample vulnerable code
        vulnerable_code = '''
import os
import sqlite3
from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Vulnerable SQL query
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    conn = sqlite3.connect('database.db')
    result = conn.execute(query).fetchone()
    
    if result:
        return "Login successful"
    return "Login failed"

@app.route('/file')
def read_file():
    filename = request.args.get('file')
    # Vulnerable file access
    with open(filename, 'r') as f:
        return f.read()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))  # Debug mode in production
        '''
        
        files = [create_file_data('./app.py', vulnerable_code, 'python')]
        
        security_request = create_security_analysis_request(
            prompt='Analyze this Flask application for security vulnerabilities',
            user_id='python-user',
            files=files,
            security_standards=['OWASP Top 10', 'CWE']
        )
        
        # Use streaming for security analysis
        print('Starting streaming security analysis...')
        client.execute_stream(security_request, handle_stream_event)
        
        # List available models
        print('\n🤖 Available Models:')
        models = client.list_models()
        for provider, model_list in models.get('models', {}).items():
            print(f'  {provider}: {len(model_list)} models')
            for model in model_list[:3]:  # Show first 3 models
                print(f'    - {model}')
            if len(model_list) > 3:
                print(f'    ... and {len(model_list) - 3} more')
        
        # Usage metrics
        print('\n📊 Usage Metrics:')
        usage = client.get_usage({
            'granularity': 'daily',
            'include_details': True
        })
        print(f'Total requests: {usage.get("total_requests", 0)}')
        print(f'Total tokens: {usage.get("total_tokens", 0)}')
        print(f'Total cost: ${usage.get("total_cost", 0.0):.4f}')
        
        # Debug routing example
        print('\n🧭 Debug Routing:')
        debug_info = client.debug_routing(request)
        print(f'Selected provider: {debug_info.get("debug_info", {}).get("selected_provider")}')
        print(f'Selected model: {debug_info.get("debug_info", {}).get("selected_model")}')
        print(f'Reasoning: {debug_info.get("debug_info", {}).get("reasoning", "N/A")[:100]}...')
        
    except Exception as error:
        print(f'💥 Error: {error}')
        if hasattr(error, 'status_code'):
            print(f'Status code: {error.status_code}')
        if hasattr(error, 'details'):
            print(f'Details: {error.details}')
    
    print('\n👋 Example completed!')


if __name__ == '__main__':
    main()
