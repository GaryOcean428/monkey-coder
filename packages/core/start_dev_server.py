#!/usr/bin/env python3
"""Start the development server with environment variables loaded."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env.local from the root directory
root_dir = Path(__file__).parent.parent.parent
env_file = root_dir / ".env.local"

if env_file.exists():
    print(f"Loading environment from: {env_file}")
    load_dotenv(env_file, override=True)
    
    # Verify some keys are loaded
    if os.getenv("GROQ_API_KEY"):
        print("✅ Groq API key loaded")
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API key loaded")
    if os.getenv("ANTHROPIC_API_KEY"):
        print("✅ Anthropic API key loaded")
else:
    print(f"❌ Environment file not found: {env_file}")
    sys.exit(1)

# Now import and run the server
from monkey_coder.app.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Reload doesn't work with direct app import
        log_level="info"
    )