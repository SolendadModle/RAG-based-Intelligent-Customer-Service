"""
Session Management - Manage conversation sessions and state.
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

from src.config import config_manager
from src.logger import app_logger
from src.utils import generate_session_id


class ConversationSession:
    """Represents a single conversation session."""
    
    def __init__(self, session_id: str, user_id: Optional[str] = None):
        """
        Initialize conversation session.
        
        Args:
            session_id: Unique session identifier
            user_id: Optional user identifier
        """
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.state = "initial"
        self.history: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add message to conversation history.
        
        Args:
            role: Message role (user/assistant)
            content: Message content
            metadata: Optional metadata
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }
        self.history.append(message)
        self.last_activity = datetime.utcnow()
    
    def get_history(self, max_turns: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            max_turns: Maximum number of turns to return
            
        Returns:
            List of conversation messages
        """
        if max_turns:
            return self.history[-max_turns:]
        return self.history
    
    def set_state(self, state: str):
        """
        Set conversation state.
        
        Args:
            state: New state
        """
        self.state = state
        self.last_activity = datetime.utcnow()
        app_logger.debug(f"Session {self.session_id} state changed to: {state}")
    
    def update_context(self, key: str, value: Any):
        """
        Update session context.
        
        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
        self.last_activity = datetime.utcnow()
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get context value.
        
        Args:
            key: Context key
            default: Default value if key not found
            
        Returns:
            Context value
        """
        return self.context.get(key, default)
    
    def is_expired(self, timeout_seconds: int) -> bool:
        """
        Check if session is expired.
        
        Args:
            timeout_seconds: Session timeout in seconds
            
        Returns:
            True if expired, False otherwise
        """
        elapsed = (datetime.utcnow() - self.last_activity).total_seconds()
        return elapsed > timeout_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'state': self.state,
            'history': self.history,
            'metadata': self.metadata,
            'context': self.context
        }


class SessionManager:
    """Manage multiple conversation sessions."""
    
    def __init__(self):
        """Initialize session manager."""
        self.config = config_manager.dialog_config
        self.session_timeout = self.config.get('session_timeout', 1800)
        self.max_history_turns = self.config.get('max_history_turns', 10)
        
        self.sessions: Dict[str, ConversationSession] = {}
        self.user_sessions: Dict[str, List[str]] = defaultdict(list)
        
        app_logger.info("Initialized Session Manager")
    
    def create_session(self, user_id: Optional[str] = None) -> ConversationSession:
        """
        Create new conversation session.
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            New ConversationSession instance
        """
        session_id = generate_session_id(user_id)
        session = ConversationSession(session_id, user_id)
        
        self.sessions[session_id] = session
        
        if user_id:
            self.user_sessions[user_id].append(session_id)
        
        app_logger.info(f"Created new session: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationSession if found and not expired, None otherwise
        """
        session = self.sessions.get(session_id)
        
        if session:
            if session.is_expired(self.session_timeout):
                app_logger.info(f"Session {session_id} expired")
                self.delete_session(session_id)
                return None
            return session
        
        return None
    
    def get_or_create_session(self, session_id: Optional[str] = None, 
                             user_id: Optional[str] = None) -> ConversationSession:
        """
        Get existing session or create new one.
        
        Args:
            session_id: Optional session identifier
            user_id: Optional user identifier
            
        Returns:
            ConversationSession instance
        """
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session
        
        return self.create_session(user_id)
    
    def delete_session(self, session_id: str):
        """
        Delete session.
        
        Args:
            session_id: Session identifier
        """
        session = self.sessions.get(session_id)
        if session:
            if session.user_id:
                self.user_sessions[session.user_id].remove(session_id)
            del self.sessions[session_id]
            app_logger.info(f"Deleted session: {session_id}")
    
    def get_user_sessions(self, user_id: str) -> List[ConversationSession]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of ConversationSession instances
        """
        session_ids = self.user_sessions.get(user_id, [])
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(self.session_timeout)
        ]
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        if expired_sessions:
            app_logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get session statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_sessions = len(self.sessions)
        active_users = len([uid for uid, sids in self.user_sessions.items() if sids])
        
        states = defaultdict(int)
        for session in self.sessions.values():
            states[session.state] += 1
        
        return {
            'total_sessions': total_sessions,
            'active_users': active_users,
            'states': dict(states),
            'session_timeout': self.session_timeout
        }
