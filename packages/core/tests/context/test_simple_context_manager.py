import asyncio
import pytest
from datetime import timedelta, datetime

from monkey_coder.context.simple_manager import SimpleContextManager


@pytest.mark.asyncio
async def test_add_message_creates_conversation():
    cm = SimpleContextManager()
    msg = await cm.add_message("user1", "sess1", "user", "Hello world", {})
    stats = cm.get_stats()
    assert msg.content == "Hello world"
    assert stats["total_conversations"] == 1
    assert stats["total_messages"] == 1


@pytest.mark.asyncio
async def test_context_window_truncation():
    cm = SimpleContextManager()
    conv = await cm.get_or_create_conversation("user1", "sess1")
    conv.max_context_tokens = 10  # force aggressive truncation
    # Add several messages exceeding token limit
    for i in range(5):
        await cm.add_message("user1", "sess1", "user", f"message {i} extra words", {})
    # After truncation, token budget should be within limit
    total_tokens = sum(m.token_count for m in conv.messages)
    assert total_tokens <= conv.max_context_tokens
    # Ensure we still have at least one recent message
    assert len(conv.messages) >= 1


@pytest.mark.asyncio
async def test_cleanup_expired_sessions():
    cm = SimpleContextManager(session_timeout=timedelta(seconds=1))
    await cm.add_message("user1", "sess1", "user", "hi", {})
    # Manually age the conversation
    for conv in cm.conversations.values():
        conv.last_active = datetime.utcnow() - timedelta(seconds=3600)
    await cm.cleanup_expired_sessions()
    stats = cm.get_stats()
    assert stats["total_conversations"] == 0
    assert stats["evictions"] >= 1


@pytest.mark.asyncio
async def test_concurrent_add_message():
    cm = SimpleContextManager()

    async def worker(i):
        await cm.add_message("user1", "sess1", "user", f"hello {i}", {})

    await asyncio.gather(*[worker(i) for i in range(20)])
    stats = cm.get_stats()
    assert stats["total_conversations"] == 1
    assert stats["total_messages"] == 20
