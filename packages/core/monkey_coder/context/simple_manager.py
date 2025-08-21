"""
Simple in-memory context manager for immediate deployment.
This provides basic conversation history without external dependencies.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    # Metrics are optional; fall back gracefully
    from ..monitoring.context_metrics import (
        set_conversations,
        set_messages,
        inc_evictions,
        inc_conversations,
    )
except Exception:  # pragma: no cover - metrics optional
    def set_conversations(v: int):
        pass
    def set_messages(v: int):
        pass
    def inc_evictions(n: int = 1):
        pass
    def inc_conversations(n: int = 1):
        pass

logger = logging.getLogger(__name__)


@dataclass
class SimpleMessage:
    """Simple message data structure."""
    id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "token_count": self.token_count
        }


@dataclass
class SimpleConversation:
    """Simple conversation data structure."""
    id: str
    user_id: str
    session_id: str
    messages: List[SimpleMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    max_context_tokens: int = 4096

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> SimpleMessage:
        """Add a message to the conversation."""
        message = SimpleMessage(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
            token_count=self._estimate_tokens(content)
        )
        self.messages.append(message)
        self.last_active = datetime.utcnow()
        self._maintain_context_window()
        return message

    def _estimate_tokens(self, text: str) -> int:
        """Simple token estimation (words * 1.3)."""
        return int(len(text.split()) * 1.3)

    def _maintain_context_window(self):
        """Maintain context window within token limits."""
        total_tokens = sum(msg.token_count for msg in self.messages)

        if total_tokens <= self.max_context_tokens:
            return

        # Keep recent messages and system messages
        system_messages = [msg for msg in self.messages if msg.role == "system"]
        non_system_messages = [msg for msg in self.messages if msg.role != "system"]

        # Keep most recent non-system messages
        kept_messages = []
        current_tokens = sum(msg.token_count for msg in system_messages)

        for msg in reversed(non_system_messages):
            if current_tokens + msg.token_count <= self.max_context_tokens:
                kept_messages.insert(0, msg)
                current_tokens += msg.token_count
            else:
                break

        self.messages = system_messages + kept_messages
        logger.info(f"Context window maintained: {len(self.messages)} messages, {current_tokens} tokens")

    def get_context(self, include_system: bool = True) -> List[Dict[str, Any]]:
        """Get conversation context as a list of message dictionaries."""
        if include_system:
            return [msg.to_dict() for msg in self.messages]
        else:
            return [msg.to_dict() for msg in self.messages if msg.role != "system"]


class SimpleContextManager:
    """Simple in-memory context manager for conversations."""

    def __init__(self, session_timeout: timedelta = timedelta(hours=24)):
        self.conversations: Dict[str, SimpleConversation] = {}
        self.user_sessions: Dict[str, Dict[str, str]] = {}  # user_id -> {session_id: conversation_id}
        self.session_timeout = session_timeout
        self._lock = asyncio.Lock()
        self._evictions = 0
        # Initialize metrics baseline
        set_conversations(0)
        set_messages(0)

    async def get_or_create_conversation(
        self,
        user_id: str,
        session_id: str
    ) -> SimpleConversation:
        """Get or create a conversation for the user session."""
        async with self._lock:
            # Check if user has existing conversation for this session
            if user_id in self.user_sessions and session_id in self.user_sessions[user_id]:
                conversation_id = self.user_sessions[user_id][session_id]
                if conversation_id in self.conversations:
                    conversation = self.conversations[conversation_id]
                    conversation.last_active = datetime.utcnow()
                    return conversation

            # Create new conversation
            conversation_id = str(uuid.uuid4())
            conversation = SimpleConversation(
                id=conversation_id,
                user_id=user_id,
                session_id=session_id
            )

            self.conversations[conversation_id] = conversation

            # Track user session mapping
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {}
            self.user_sessions[user_id][session_id] = conversation_id

            inc_conversations()
            self._refresh_metrics_unlocked()
            logger.info(f"Created new conversation {conversation_id} for user {user_id}, session {session_id}")
            return conversation

    async def add_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SimpleMessage:
        """Add a message to the conversation."""
        conversation = await self.get_or_create_conversation(user_id, session_id)
        msg = conversation.add_message(role, content, metadata)
        # Refresh metrics asynchronously (schedule so we don't hold caller path)
        self._refresh_metrics()
        return msg

    async def get_conversation_context(
        self,
        user_id: str,
        session_id: str,
        include_system: bool = True
    ) -> List[Dict[str, Any]]:
        """Get conversation context for the session."""
        conversation = await self.get_or_create_conversation(user_id, session_id)
        return conversation.get_context(include_system)

    async def get_conversation_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent conversations for a user."""
        async with self._lock:
            user_conversations = []

            if user_id in self.user_sessions:
                for session_id, conversation_id in self.user_sessions[user_id].items():
                    if conversation_id in self.conversations:
                        conv = self.conversations[conversation_id]
                        user_conversations.append({
                            "id": conv.id,
                            "session_id": conv.session_id,
                            "created_at": conv.created_at.isoformat(),
                            "last_active": conv.last_active.isoformat(),
                            "message_count": len(conv.messages)
                        })

            # Sort by last active and limit
            user_conversations.sort(key=lambda x: x["last_active"], reverse=True)
            return user_conversations[:limit]

    async def cleanup_expired_sessions(self):
        """Clean up expired conversations."""
        async with self._lock:
            cutoff_time = datetime.utcnow() - self.session_timeout
            expired_conversations = []

            for conversation_id, conversation in self.conversations.items():
                if conversation.last_active < cutoff_time:
                    expired_conversations.append(conversation_id)

            for conversation_id in expired_conversations:
                conversation = self.conversations.pop(conversation_id, None)
                if conversation:
                    # Remove from user sessions mapping
                    user_id = conversation.user_id
                    session_id = conversation.session_id
                    if user_id in self.user_sessions and session_id in self.user_sessions[user_id]:
                        del self.user_sessions[user_id][session_id]
                        if not self.user_sessions[user_id]:
                            del self.user_sessions[user_id]

            if expired_conversations:
                self._evictions += len(expired_conversations)
                inc_evictions(len(expired_conversations))
                logger.info(f"Cleaned up {len(expired_conversations)} expired conversations")
            self._refresh_metrics_unlocked()

    async def save_to_file(self, filepath: str):
        """Save conversations to file for persistence."""
        async with self._lock:
            data = {
                "conversations": {},
                "user_sessions": self.user_sessions,
                "saved_at": datetime.utcnow().isoformat()
            }

            for conv_id, conversation in self.conversations.items():
                data["conversations"][conv_id] = {
                    "id": conversation.id,
                    "user_id": conversation.user_id,
                    "session_id": conversation.session_id,
                    "created_at": conversation.created_at.isoformat(),
                    "last_active": conversation.last_active.isoformat(),
                    "max_context_tokens": conversation.max_context_tokens,
                    "messages": [msg.to_dict() for msg in conversation.messages]
                }

            try:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Saved {len(self.conversations)} conversations to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save conversations to file: {e}")

    async def load_from_file(self, filepath: str):
        """Load conversations from file."""
        if not Path(filepath).exists():
            logger.info(f"No existing conversation file found at {filepath}")
            return

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            async with self._lock:
                self.user_sessions = data.get("user_sessions", {})
                conversations_data = data.get("conversations", {})

                for conv_id, conv_data in conversations_data.items():
                    conversation = SimpleConversation(
                        id=conv_data["id"],
                        user_id=conv_data["user_id"],
                        session_id=conv_data["session_id"],
                        created_at=datetime.fromisoformat(conv_data["created_at"]),
                        last_active=datetime.fromisoformat(conv_data["last_active"]),
                        max_context_tokens=conv_data.get("max_context_tokens", 4096)
                    )

                    # Restore messages
                    for msg_data in conv_data.get("messages", []):
                        message = SimpleMessage(
                            id=msg_data["id"],
                            role=msg_data["role"],
                            content=msg_data["content"],
                            timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                            metadata=msg_data.get("metadata", {}),
                            token_count=msg_data.get("token_count", 0)
                        )
                        conversation.messages.append(message)

                    self.conversations[conv_id] = conversation

                logger.info(f"Loaded {len(self.conversations)} conversations from {filepath}")

        except Exception as e:
            logger.error(f"Failed to load conversations from file: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get context manager statistics."""
        total_messages = sum(len(conv.messages) for conv in self.conversations.values())
        active_sessions = len(self.user_sessions)

        return {
            "total_conversations": len(self.conversations),
            "total_messages": total_messages,
            "active_users": len(self.user_sessions),
            "active_sessions": active_sessions,
            "memory_usage_mb": self._estimate_memory_usage(),
            "evictions": self._evictions
        }

    def _refresh_metrics(self):
        """Schedule async metrics refresh (non-blocking)."""
        if self._lock.locked():
            asyncio.create_task(self._refresh_metrics_async())
        else:
            asyncio.create_task(self._refresh_metrics_async())

    async def _refresh_metrics_async(self):  # pragma: no cover - timing sensitive
        async with self._lock:
            self._refresh_metrics_unlocked()

    def _refresh_metrics_unlocked(self):
        total_messages = sum(len(c.messages) for c in self.conversations.values())
        set_conversations(len(self.conversations))
        set_messages(total_messages)

    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        total_chars = 0
        for conversation in self.conversations.values():
            for message in conversation.messages:
                total_chars += len(message.content) + len(str(message.metadata))

        # Rough estimation: chars * 2 bytes + overhead
        return (total_chars * 2 + len(self.conversations) * 1000) / (1024 * 1024)


# Global instance for easy access
_global_context_manager = None


def get_simple_context_manager() -> SimpleContextManager:
    """Get the global simple context manager instance."""
    global _global_context_manager
    if _global_context_manager is None:
        _global_context_manager = SimpleContextManager()
    return _global_context_manager