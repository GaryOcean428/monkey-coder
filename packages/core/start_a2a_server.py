#!/usr/bin/env python3
"""
Standalone A2A Server startup script for Monkey-Coder Agent

This script can be used to run the A2A server independently of the main FastAPI application.
Useful for microservice deployment or development testing.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from monkey_coder.a2a_server import MonkeyCoderA2AAgent

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('a2a_server.log')
        ]
    )

async def main():
    """Main entry point for standalone A2A server"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Get configuration from environment
    port = int(os.getenv("A2A_PORT", "7702"))
    
    logger.info(f"Starting Monkey-Coder A2A server on port {port}")
    
    # Create and start agent
    agent = MonkeyCoderA2AAgent(port=port)
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"A2A server error: {e}")
        raise
    finally:
        await agent.stop()
        logger.info("A2A server stopped")

if __name__ == "__main__":
    asyncio.run(main())