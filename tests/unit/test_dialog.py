"""
Unit tests for dialog management.
"""

import pytest
from src.dialog.session_manager import SessionManager, ConversationSession
from src.dialog.dialog_handler import DialogHandler


class TestConversationSession:
    """Test ConversationSession class."""
    
    def test_session_creation(self):
        """Test session creation."""
        session = ConversationSession(session_id="test123", user_id="user456")
        assert session.session_id == "test123"
        assert session.user_id == "user456"
        assert session.state == "initial"
        assert len(session.history) == 0
    
    def test_add_message(self):
        """Test adding message to session."""
        session = ConversationSession(session_id="test123")
        session.add_message("user", "Hello")
        assert len(session.history) == 1
        assert session.history[0]['role'] == "user"
        assert session.history[0]['content'] == "Hello"
    
    def test_get_history(self):
        """Test getting conversation history."""
        session = ConversationSession(session_id="test123")
        session.add_message("user", "Message 1")
        session.add_message("assistant", "Response 1")
        session.add_message("user", "Message 2")
        
        history = session.get_history(max_turns=2)
        assert len(history) == 2
        assert history[0]['content'] == "Response 1"
    
    def test_set_state(self):
        """Test setting session state."""
        session = ConversationSession(session_id="test123")
        session.set_state("processing")
        assert session.state == "processing"
    
    def test_context_management(self):
        """Test context management."""
        session = ConversationSession(session_id="test123")
        session.update_context("user_name", "John")
        assert session.get_context("user_name") == "John"
        assert session.get_context("nonexistent", "default") == "default"


class TestSessionManager:
    """Test SessionManager functionality."""
    
    @pytest.fixture
    def session_manager(self):
        """Create session manager instance."""
        return SessionManager()
    
    def test_create_session(self, session_manager):
        """Test session creation."""
        session = session_manager.create_session(user_id="user123")
        assert session is not None
        assert session.user_id == "user123"
        assert session.session_id in session_manager.sessions
    
    def test_get_session(self, session_manager):
        """Test getting session by ID."""
        session = session_manager.create_session()
        retrieved = session_manager.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
    
    def test_get_or_create_session(self, session_manager):
        """Test get or create session."""
        # Create new session
        session1 = session_manager.get_or_create_session()
        assert session1 is not None
        
        # Get existing session
        session2 = session_manager.get_or_create_session(session_id=session1.session_id)
        assert session2.session_id == session1.session_id
    
    def test_delete_session(self, session_manager):
        """Test session deletion."""
        session = session_manager.create_session()
        session_id = session.session_id
        session_manager.delete_session(session_id)
        assert session_id not in session_manager.sessions
    
    def test_statistics(self, session_manager):
        """Test session statistics."""
        session_manager.create_session(user_id="user1")
        session_manager.create_session(user_id="user2")
        stats = session_manager.get_statistics()
        assert stats['total_sessions'] == 2
        assert stats['active_users'] == 2


class TestDialogHandler:
    """Test DialogHandler functionality."""
    
    @pytest.fixture
    def dialog_handler(self):
        """Create dialog handler instance."""
        # Note: This will initialize full dependencies
        # In a real test, we might want to mock these
        return DialogHandler()
    
    def test_process_message(self, dialog_handler):
        """Test message processing."""
        result = dialog_handler.process_message(
            message="Hello, I need help",
            user_id="test_user"
        )
        
        assert 'session_id' in result
        assert 'response' in result
        assert 'intent' in result
        assert 'state' in result
    
    def test_get_session_info(self, dialog_handler):
        """Test getting session info."""
        result = dialog_handler.process_message(
            message="Test message",
            user_id="test_user"
        )
        
        session_id = result['session_id']
        session_info = dialog_handler.get_session_info(session_id)
        assert session_info is not None
        assert session_info['session_id'] == session_id
    
    def test_end_session(self, dialog_handler):
        """Test ending session."""
        result = dialog_handler.process_message(message="Test", user_id="test_user")
        session_id = result['session_id']
        
        dialog_handler.end_session(session_id)
        session_info = dialog_handler.get_session_info(session_id)
        assert session_info is None
