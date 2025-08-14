"""
Streaming Module for Monkey Coder

Provides SSE streaming capabilities for real-time AI responses.
"""

import asyncio
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class StreamManager:
    """
    Manager for streaming connections and lifecycle.
    """
    
    def __init__(self):
        self.active_streams: Dict[str, Any] = {}
        self.initialized = False
        
    async def start(self):
        """Start the stream manager."""
        logger.info("StreamManager starting...")
        self.initialized = True
        logger.info("StreamManager started successfully")
        
    async def stop(self):
        """Stop the stream manager and clean up resources."""
        logger.info("StreamManager stopping...")
        # Clean up any active streams
        for stream_id in list(self.active_streams.keys()):
            await self.close_stream(stream_id)
        self.initialized = False
        logger.info("StreamManager stopped")
        
    async def close_stream(self, stream_id: str):
        """Close a specific stream."""
        if stream_id in self.active_streams:
            # Clean up stream resources
            del self.active_streams[stream_id]
            logger.debug(f"Closed stream {stream_id}")
    
    def register_stream(self, stream_id: str, metadata: Optional[Dict[str, Any]] = None):
        """Register a new stream."""
        self.active_streams[stream_id] = {
            "metadata": metadata or {},
            "created_at": asyncio.get_event_loop().time()
        }
        logger.debug(f"Registered stream {stream_id}")
    
    def get_stream_info(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a stream."""
        return self.active_streams.get(stream_id)
    
    def get_active_streams(self) -> Dict[str, Any]:
        """Get all active streams."""
        return self.active_streams.copy()


# Global stream manager instance
stream_manager = StreamManager()

__all__ = ["stream_manager", "StreamManager"]