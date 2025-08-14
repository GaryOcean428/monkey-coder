#!/bin/bash

echo "========================================="
echo "MONKEY CODER QUICK TEST"
echo "========================================="

# Test using the CLI directly
echo ""
echo "Test 1: Using the CLI to implement a function"
echo "----------------------------------------"
yarn workspace monkey-coder-cli implement "Create a Python function that validates email addresses using regex"

echo ""
echo "Test 2: Using the CLI to analyze code"
echo "----------------------------------------"
yarn workspace monkey-coder-cli analyze "What design patterns are used in packages/core/monkey_coder/core/orchestrator.py?"

echo ""
echo "Test 3: Direct Python test with file operations"
echo "----------------------------------------"
python test_monkey_coder.py

echo ""
echo "========================================="
echo "TESTS COMPLETE!"
echo "========================================="