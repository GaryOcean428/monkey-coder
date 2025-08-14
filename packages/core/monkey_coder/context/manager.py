import asyncio
import aiosqlite
import uuid
import threading
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# --- Data Models ---

@dataclass
class Message:
    id: str
    session_id: str
    role: str  # user/assistant/system
    content: str
    token_count: int
    timestamp: datetime
    important: bool = False

@dataclass
class Session:
    id: str
    created_at: datetime
    last_active: datetime
    expired: bool = False

# --- Storage Layer (Repository Pattern) ---

class MessageRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    token_count INTEGER,
                    timestamp TEXT,
                    important INTEGER
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TEXT,
                    last_active TEXT,
                    expired INTEGER
                )
            ''')
            await db.commit()

    async def add_message(self, message: Message):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO messages (id, session_id, role, content, token_count, timestamp, important)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (message.id, message.session_id, message.role, message.content, message.token_count, message.timestamp.isoformat(), int(message.important)))
            await db.commit()

    async def get_messages(self, session_id: str) -> List[Message]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT id, session_id, role, content, token_count, timestamp, important
                FROM messages WHERE session_id = ?
                ORDER BY timestamp ASC
            ''', (session_id,))
            rows = await cursor.fetchall()
            return [
                Message(
                    id=row[0], session_id=row[1], role=row[2], content=row[3],
                    token_count=row[4], timestamp=datetime.fromisoformat(row[5]),
                    important=bool(row[6])
                ) for row in rows
            ]

    async def delete_messages(self, session_id: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
            await db.commit()

    async def add_session(self, session: Session):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO sessions (id, created_at, last_active, expired)
                VALUES (?, ?, ?, ?)
            ''', (session.id, session.created_at.isoformat(), session.last_active.isoformat(), int(session.expired)))
            await db.commit()

    async def get_session(self, session_id: str) -> Optional[Session]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT id, created_at, last_active, expired FROM sessions WHERE id = ?
            ''', (session_id,))
            row = await cursor.fetchone()
            if row:
                return Session(
                    id=row[0],
                    created_at=datetime.fromisoformat(row[1]),
                    last_active=datetime.fromisoformat(row[2]),
                    expired=bool(row[3])
                )
            return None

    async def get_all_sessions(self) -> List[Session]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT id, created_at, last_active, expired FROM sessions')
            rows = await cursor.fetchall()
            return [
                Session(
                    id=row[0],
                    created_at=datetime.fromisoformat(row[1]),
                    last_active=datetime.fromisoformat(row[2]),
                    expired=bool(row[3])
                ) for row in rows
            ]

    async def delete_session(self, session_id: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
            await db.commit()
            await self.delete_messages(session_id)

# --- Token Counting Utility ---

def count_tokens(text: str) -> int:
    # Placeholder: Replace with actual tokenizer for your AI provider
    return len(text.split())

# --- Summarization Strategy (Mock) ---

class Summarizer:
    async def summarize(self, messages: List[Message]) -> Message:
        # Replace with actual LLM summarization
        summary_content = " ".join([m.content for m in messages])
        summary_content = summary_content[:200] + "..." if len(summary_content) > 200 else summary_content
        return Message(
            id=str(uuid.uuid4()),
            session_id=messages[0].session_id,
            role="system",
            content=f"Summary: {summary_content}",
            token_count=count_tokens(summary_content),
            timestamp=datetime.utcnow(),
            important=True
        )

# --- Semantic Search Strategy (Mock) ---

class SemanticSearcher:
    async def search(self, messages: List[Message], query: str, top_k: int = 3) -> List[Message]:
        # Replace with actual embedding-based search
        return sorted(messages, key=lambda m: -m.content.lower().count(query.lower()))[:top_k]

# --- Key Info Extraction (Mock) ---

class KeyInfoExtractor:
    async def extract(self, messages: List[Message]) -> Dict[str, Any]:
        # Replace with actual NER or LLM-based extraction
        return {
            "num_messages": len(messages),
            "users": list({m.role for m in messages if m.role == "user"}),
            "last_message": messages[-1].content if messages else None
        }

# --- Context Window Manager ---

class ContextWindowManager:
    def __init__(self, token_limit: int, summarizer: Summarizer):
        self.token_limit = token_limit
        self.summarizer = summarizer

    async def get_context_window(self, messages: List[Message]) -> List[Message]:
        total_tokens = sum(m.token_count for m in messages)
        if total_tokens <= self.token_limit:
            return messages

        # Sliding window: keep recent and important messages
        important_msgs = [m for m in messages if m.important]
        recent_msgs = []
        tokens = sum(m.token_count for m in important_msgs)
        for m in reversed(messages):
            if m in important_msgs:
                continue
            if tokens + m.token_count > self.token_limit:
                break
            recent_msgs.insert(0, m)
            tokens += m.token_count

        # If still over limit, summarize older messages
        if tokens > self.token_limit:
            # Summarize all but the last N messages
            keep_n = 3
            to_summarize = messages[:-keep_n]
            summary = await self.summarizer.summarize(to_summarize)
            context = [summary] + messages[-keep_n:]
            # Recurse in case still over limit
            return await self.get_context_window(context)
        else:
            return important_msgs + recent_msgs

# --- Session Manager (Singleton, Thread-safe) ---

class SessionManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, repo: MessageRepository, session_timeout: int = 3600):
        self.repo = repo
        self.session_timeout = session_timeout  # seconds
        self._session_locks: Dict[str, asyncio.Lock] = {}

    async def create_session(self) -> Session:
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        session = Session(id=session_id, created_at=now, last_active=now)
        await self.repo.add_session(session)
        self._session_locks[session_id] = asyncio.Lock()
        return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        session = await self.repo.get_session(session_id)
        if session and not session.expired:
            # Update last_active
            session.last_active = datetime.utcnow()
            await self.repo.add_session(session)
            return session
        return None

    async def expire_sessions(self):
        sessions = await self.repo.get_all_sessions()
        now = datetime.utcnow()
        for session in sessions:
            if not session.expired and (now - session.last_active).total_seconds() > self.session_timeout:
                session.expired = True
                await self.repo.add_session(session)
                await self.repo.delete_session(session.id)
                self._session_locks.pop(session.id, None)

    def get_session_lock(self, session_id: str) -> asyncio.Lock:
        if session_id not in self._session_locks:
            self._session_locks[session_id] = asyncio.Lock()
        return self._session_locks[session_id]

# --- Context Manager (Main API) ---

class ContextManager:
    def __init__(
        self,
        repo: MessageRepository,
        session_manager: SessionManager,
        window_manager: ContextWindowManager,
        semantic_searcher: SemanticSearcher,
        key_info_extractor: KeyInfoExtractor
    ):
        self.repo = repo
        self.session_manager = session_manager
        self.window_manager = window_manager
        self.semantic_searcher = semantic_searcher
        self.key_info_extractor = key_info_extractor

    async def add_message(
        self, session_id: str, role: str, content: str, important: bool = False
    ) -> Message:
        session = await self.session_manager.get_session(session_id)
        if not session:
            raise ValueError("Session not found or expired")
        message = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            token_count=count_tokens(content),
            timestamp=datetime.utcnow(),
            important=important
        )
        lock = self.session_manager.get_session_lock(session_id)
        async with lock:
            await self.repo.add_message(message)
        return message

    async def get_full_history(self, session_id: str) -> List[Message]:
        return await self.repo.get_messages(session_id)

    async def get_context(self, session_id: str) -> List[Message]:
        messages = await self.repo.get_messages(session_id)
        return await self.window_manager.get_context_window(messages)

    async def semantic_search(self, session_id: str, query: str, top_k: int = 3) -> List[Message]:
        messages = await self.repo.get_messages(session_id)
        return await self.semantic_searcher.search(messages, query, top_k)

    async def extract_key_info(self, session_id: str) -> Dict[str, Any]:
        messages = await self.repo.get_messages(session_id)
        return await self.key_info_extractor.extract(messages)

    async def cleanup_expired_sessions(self):
        await self.session_manager.expire_sessions()

# --- Integration Example ---

async def main():
    repo = MessageRepository("conversations.db")
    await repo.init()
    summarizer = Summarizer()
    window_manager = ContextWindowManager(token_limit=2048, summarizer=summarizer)
    semantic_searcher = SemanticSearcher()
    key_info_extractor = KeyInfoExtractor()
    session_manager = SessionManager(repo)
    context_manager = ContextManager(
        repo, session_manager, window_manager, semantic_searcher, key_info_extractor
    )

    # Create session
    session = await session_manager.create_session()
    print(f"Session created: {session.id}")

    # Add messages
    await context_manager.add_message(session.id, "user", "Hello, how are you?")
    await context_manager.add_message(session.id, "assistant", "I'm good, thank you!")
    await context_manager.add_message(session.id, "user", "Tell me a joke.", important=True)
    await context_manager.add_message(session.id, "assistant", "Why did the chicken cross the road?")

    # Get context within token limit
    context = await context_manager.get_context(session.id)
    print("Context window:")
    for msg in context:
        print(f"{msg.role}: {msg.content}")

    # Semantic search
    results = await context_manager.semantic_search(session.id, "joke")
    print("Semantic search results:")
    for msg in results:
        print(f"{msg.role}: {msg.content}")

    # Key info extraction
    key_info = await context_manager.extract_key_info(session.id)
    print("Key info:", key_info)

    # Cleanup expired sessions
    await context_manager.cleanup_expired_sessions()

if __name__ == "__main__":
    asyncio.run(main())