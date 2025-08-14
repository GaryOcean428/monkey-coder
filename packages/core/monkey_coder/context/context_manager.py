"""
Context Management System for Multi-turn Conversations

This module provides a comprehensive context management system that handles:
- Conversation history storage
- Context window management with token counting
- Project context extraction
- Semantic search with embeddings
- Session persistence across requests
"""

import os
import json
import logging
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import asyncio
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.exc import SQLAlchemyError
import tiktoken
from sentence_transformers import SentenceTransformer, util
import numpy as np

logger = logging.getLogger(__name__)

Base = declarative_base()


# Database Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = 'user_sessions'
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    user = relationship("User", back_populates="sessions")
    conversations = relationship("Conversation", back_populates="session", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_id = Column(String(36), ForeignKey('user_sessions.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    context_window = Column(JSON, default={})
    
    user = relationship("User", back_populates="conversations")
    session = relationship("UserSession", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    conversation = relationship("Conversation", back_populates="messages")


class ProjectContext(Base):
    __tablename__ = 'project_contexts'
    
    id = Column(Integer, primary_key=True)
    project_path = Column(String(500), unique=True, nullable=False)
    content_hash = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    file_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    embeddings = relationship("ContextEmbedding", back_populates="project_context", cascade="all, delete-orphan")


class ContextEmbedding(Base):
    __tablename__ = 'context_embeddings'
    
    id = Column(Integer, primary_key=True)
    project_context_id = Column(Integer, ForeignKey('project_contexts.id'))
    chunk_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False)  # Store as JSON array
    chunk_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project_context = relationship("ProjectContext", back_populates="embeddings")


@dataclass
class ContextConfig:
    """Configuration for context management."""
    max_window_size: int = 4096
    overlap_tokens: int = 200
    embedding_dimension: int = 384
    context_ttl: timedelta = timedelta(hours=24)
    chunk_size: int = 512
    search_top_k: int = 5
    database_url: str = "sqlite:///context.db"
    embedding_model: str = "all-MiniLM-L6-v2"


class TokenCounter:
    """Handles token counting for different models."""
    
    def __init__(self, model_name: str = "gpt-4"):
        try:
            self.encoder = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))
    
    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to maximum token count."""
        tokens = self.encoder.encode(text)
        if len(tokens) <= max_tokens:
            return text
        truncated_tokens = tokens[:max_tokens]
        return self.encoder.decode(truncated_tokens)


class ContextManager:
    """Main context management system."""
    
    def __init__(self, config: Optional[ContextConfig] = None):
        self.config = config or ContextConfig()
        self.engine = create_engine(self.config.database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.token_counter = TokenCounter()
        self.embedding_model = SentenceTransformer(self.config.embedding_model)
        self._lock = asyncio.Lock()
    
    async def get_or_create_user(self, username: str) -> User:
        """Get or create a user."""
        async with self._lock:
            session = self.SessionLocal()
            try:
                user = session.query(User).filter_by(username=username).first()
                if not user:
                    user = User(username=username)
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                return user
            finally:
                session.close()
    
    async def get_or_create_session(self, user_id: int, session_id: str) -> UserSession:
        """Get or create a user session."""
        async with self._lock:
            session = self.SessionLocal()
            try:
                user_session = session.query(UserSession).filter_by(id=session_id).first()
                if not user_session:
                    user_session = UserSession(id=session_id, user_id=user_id)
                    session.add(user_session)
                    session.commit()
                    session.refresh(user_session)
                else:
                    user_session.last_active = datetime.utcnow()
                    session.commit()
                return user_session
            finally:
                session.close()
    
    async def create_conversation(self, user_id: int, session_id: str) -> Conversation:
        """Create a new conversation."""
        async with self._lock:
            session = self.SessionLocal()
            try:
                conversation = Conversation(user_id=user_id, session_id=session_id)
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
                return conversation
            finally:
                session.close()
    
    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Add a message to a conversation."""
        async with self._lock:
            session = self.SessionLocal()
            try:
                token_count = self.token_counter.count_tokens(content)
                message = Message(
                    conversation_id=conversation_id,
                    role=role,
                    content=content,
                    token_count=token_count,
                    metadata=metadata or {}
                )
                session.add(message)
                session.commit()
                session.refresh(message)
                
                # Update conversation context window
                await self._update_context_window(session, conversation_id)
                
                return message
            finally:
                session.close()
    
    async def _update_context_window(self, session: Session, conversation_id: int):
        """Update the context window for a conversation."""
        conversation = session.query(Conversation).filter_by(id=conversation_id).first()
        if not conversation:
            return
        
        messages = conversation.messages
        total_tokens = sum(msg.token_count for msg in messages)
        
        # If exceeding max window size, truncate older messages
        if total_tokens > self.config.max_window_size:
            cumulative_tokens = 0
            kept_messages = []
            
            # Keep messages from the end until we reach the limit
            for msg in reversed(messages):
                if cumulative_tokens + msg.token_count <= self.config.max_window_size:
                    cumulative_tokens += msg.token_count
                    kept_messages.insert(0, msg)
                else:
                    break
            
            # Store the context window
            conversation.context_window = {
                "message_ids": [msg.id for msg in kept_messages],
                "total_tokens": cumulative_tokens,
                "truncated": True
            }
        else:
            conversation.context_window = {
                "message_ids": [msg.id for msg in messages],
                "total_tokens": total_tokens,
                "truncated": False
            }
        
        session.commit()
    
    async def get_conversation_context(
        self,
        conversation_id: int,
        include_system: bool = True
    ) -> List[Dict[str, Any]]:
        """Get the current context window for a conversation."""
        session = self.SessionLocal()
        try:
            conversation = session.query(Conversation).filter_by(id=conversation_id).first()
            if not conversation:
                return []
            
            context_info = conversation.context_window or {}
            message_ids = context_info.get("message_ids", [])
            
            if not message_ids:
                messages = conversation.messages
            else:
                messages = session.query(Message).filter(Message.id.in_(message_ids)).order_by(Message.created_at).all()
            
            result = []
            for msg in messages:
                if not include_system and msg.role == "system":
                    continue
                result.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat(),
                    "token_count": msg.token_count
                })
            
            return result
        finally:
            session.close()
    
    async def extract_project_context(
        self,
        project_path: str,
        file_extensions: Optional[List[str]] = None
    ) -> ProjectContext:
        """Extract context from a project directory."""
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.md', '.txt']
        
        project_path = Path(project_path)
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        
        content_parts = []
        file_count = 0
        
        for ext in file_extensions:
            for file_path in project_path.rglob(f"*{ext}"):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            content_parts.append(f"# File: {file_path.relative_to(project_path)}\n{content}\n")
                            file_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to read file {file_path}: {e}")
        
        full_content = "\n".join(content_parts)
        content_hash = hashlib.sha256(full_content.encode()).hexdigest()
        
        async with self._lock:
            session = self.SessionLocal()
            try:
                # Check if context already exists
                existing = session.query(ProjectContext).filter_by(project_path=str(project_path)).first()
                if existing and existing.content_hash == content_hash:
                    return existing
                
                # Create or update project context
                if existing:
                    existing.content = full_content
                    existing.content_hash = content_hash
                    existing.file_count = file_count
                    existing.updated_at = datetime.utcnow()
                    project_context = existing
                else:
                    project_context = ProjectContext(
                        project_path=str(project_path),
                        content=full_content,
                        content_hash=content_hash,
                        file_count=file_count
                    )
                    session.add(project_context)
                
                session.commit()
                session.refresh(project_context)
                
                # Generate embeddings
                await self._generate_embeddings(session, project_context)
                
                return project_context
            finally:
                session.close()
    
    async def _generate_embeddings(self, session: Session, project_context: ProjectContext):
        """Generate embeddings for project context."""
        # Delete old embeddings
        session.query(ContextEmbedding).filter_by(project_context_id=project_context.id).delete()
        
        # Split content into chunks
        chunks = self._split_into_chunks(project_context.content, self.config.chunk_size)
        
        # Generate embeddings for each chunk
        for i, chunk in enumerate(chunks):
            embedding = self.embedding_model.encode(chunk).tolist()
            context_embedding = ContextEmbedding(
                project_context_id=project_context.id,
                chunk_text=chunk,
                embedding=embedding,
                chunk_index=i
            )
            session.add(context_embedding)
        
        session.commit()
    
    def _split_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks of approximately chunk_size tokens."""
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        sentences = text.split('\n')
        for sentence in sentences:
            sentence_tokens = self.token_counter.count_tokens(sentence)
            
            if current_tokens + sentence_tokens > chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [sentence]
                current_tokens = sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    async def semantic_search(
        self,
        query: str,
        project_path: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> List[Tuple[str, float]]:
        """Perform semantic search on project contexts."""
        if top_k is None:
            top_k = self.config.search_top_k
        
        query_embedding = self.embedding_model.encode(query)
        
        session = self.SessionLocal()
        try:
            # Build query
            embeddings_query = session.query(ContextEmbedding)
            if project_path:
                project_context = session.query(ProjectContext).filter_by(project_path=project_path).first()
                if project_context:
                    embeddings_query = embeddings_query.filter_by(project_context_id=project_context.id)
            
            embeddings = embeddings_query.all()
            
            if not embeddings:
                return []
            
            # Calculate similarities
            results = []
            for embedding in embeddings:
                stored_embedding = np.array(embedding.embedding)
                similarity = util.pytorch_cos_sim(query_embedding, stored_embedding).item()
                results.append((embedding.chunk_text, similarity))
            
            # Sort by similarity and return top k
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
        finally:
            session.close()
    
    async def get_conversation_history(
        self,
        user_id: int,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a user."""
        session = self.SessionLocal()
        try:
            query = session.query(Conversation).filter_by(user_id=user_id)
            if session_id:
                query = query.filter_by(session_id=session_id)
            
            conversations = query.order_by(Conversation.updated_at.desc()).limit(limit).all()
            
            result = []
            for conv in conversations:
                result.append({
                    "id": conv.id,
                    "session_id": conv.session_id,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "message_count": len(conv.messages),
                    "context_window": conv.context_window
                })
            
            return result
        finally:
            session.close()
    
    async def cleanup_old_sessions(self, ttl: Optional[timedelta] = None):
        """Clean up old sessions and conversations."""
        if ttl is None:
            ttl = self.config.context_ttl
        
        cutoff_time = datetime.utcnow() - ttl
        
        async with self._lock:
            session = self.SessionLocal()
            try:
                # Delete old sessions
                old_sessions = session.query(UserSession).filter(UserSession.last_active < cutoff_time).all()
                for old_session in old_sessions:
                    session.delete(old_session)
                
                session.commit()
                logger.info(f"Cleaned up {len(old_sessions)} old sessions")
            finally:
                session.close()


# FastAPI Integration
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid


class MessageRequest(BaseModel):
    user_id: int
    session_id: Optional[str] = None
    message: str
    include_project_context: bool = False
    project_path: Optional[str] = None


class ContextResponse(BaseModel):
    conversation_id: int
    context: List[Dict[str, Any]]
    tokens_used: int
    truncated: bool


# Create global context manager instance
context_manager = ContextManager()


async def get_context_manager() -> ContextManager:
    """Dependency to get context manager instance."""
    return context_manager


def create_context_api(app: FastAPI):
    """Create FastAPI endpoints for context management."""
    
    @app.post("/context/message", response_model=ContextResponse)
    async def add_message(
        request: MessageRequest,
        background_tasks: BackgroundTasks,
        cm: ContextManager = Depends(get_context_manager)
    ):
        """Add a message to the conversation context."""
        try:
            # Get or create session
            if not request.session_id:
                request.session_id = str(uuid.uuid4())
            
            user = await cm.get_or_create_user(f"user_{request.user_id}")
            session = await cm.get_or_create_session(user.id, request.session_id)
            
            # Create conversation
            conversation = await cm.create_conversation(user.id, session.id)
            
            # Add user message
            await cm.add_message(conversation.id, "user", request.message)
            
            # Include project context if requested
            if request.include_project_context and request.project_path:
                project_context = await cm.extract_project_context(request.project_path)
                # Perform semantic search to find relevant context
                relevant_chunks = await cm.semantic_search(request.message, request.project_path)
                if relevant_chunks:
                    context_text = "\n".join([chunk[0] for chunk in relevant_chunks[:3]])
                    await cm.add_message(conversation.id, "system", f"Relevant project context:\n{context_text}")
            
            # Get updated context
            context = await cm.get_conversation_context(conversation.id)
            
            # Schedule cleanup in background
            background_tasks.add_task(cm.cleanup_old_sessions)
            
            return ContextResponse(
                conversation_id=conversation.id,
                context=context,
                tokens_used=sum(msg.get("token_count", 0) for msg in context),
                truncated=conversation.context_window.get("truncated", False) if conversation.context_window else False
            )
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/context/search")
    async def semantic_search(
        query: str,
        project_path: Optional[str] = None,
        top_k: int = 5,
        cm: ContextManager = Depends(get_context_manager)
    ):
        """Perform semantic search on project contexts."""
        try:
            results = await cm.semantic_search(query, project_path, top_k)
            return {
                "query": query,
                "results": [
                    {"text": text, "similarity": score}
                    for text, score in results
                ]
            }
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/context/history/{user_id}")
    async def get_history(
        user_id: int,
        session_id: Optional[str] = None,
        limit: int = 10,
        cm: ContextManager = Depends(get_context_manager)
    ):
        """Get conversation history for a user."""
        try:
            history = await cm.get_conversation_history(user_id, session_id, limit)
            return {"user_id": user_id, "history": history}
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/context/extract-project")
    async def extract_project(
        project_path: str,
        cm: ContextManager = Depends(get_context_manager)
    ):
        """Extract and index project context."""
        try:
            project_context = await cm.extract_project_context(project_path)
            return {
                "project_path": project_context.project_path,
                "file_count": project_context.file_count,
                "content_hash": project_context.content_hash,
                "updated_at": project_context.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error extracting project context: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Streaming endpoint for real-time responses
    @app.post("/context/stream")
    async def stream_with_context(
        request: MessageRequest,
        cm: ContextManager = Depends(get_context_manager)
    ):
        """Stream responses with context management."""
        async def generate():
            # Add message to context
            user = await cm.get_or_create_user(f"user_{request.user_id}")
            session = await cm.get_or_create_session(user.id, request.session_id or str(uuid.uuid4()))
            conversation = await cm.create_conversation(user.id, session.id)
            await cm.add_message(conversation.id, "user", request.message)
            
            # Get context
            context = await cm.get_conversation_context(conversation.id)
            
            # Stream the context as SSE
            yield f"data: {json.dumps({'type': 'context', 'data': context})}\n\n"
            
            # Here you would integrate with your AI provider for streaming responses
            # For now, we'll just echo the context
            yield f"data: {json.dumps({'type': 'complete', 'message': 'Context loaded successfully'})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")


# Export all components
__all__ = [
    "ContextManager",
    "ContextConfig",
    "TokenCounter",
    "User",
    "UserSession",
    "Conversation",
    "Message",
    "ProjectContext",
    "ContextEmbedding",
    "create_context_api"
]