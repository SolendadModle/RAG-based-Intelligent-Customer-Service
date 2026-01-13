"""
Dialog Handler - Orchestrates conversation flow with multi-turn dialog support.
"""

from typing import Dict, List, Optional, Any
from src.dialog.session_manager import SessionManager, ConversationSession
from src.generation.rag_generator import RAGGenerator
from src.nlu.entity_extraction import NLUService
from src.config import config_manager
from src.logger import app_logger, log_manager


class DialogHandler:
    """Handle multi-turn dialog with context awareness."""
    
    def __init__(self, rag_generator: Optional[RAGGenerator] = None,
                 nlu_service: Optional[NLUService] = None,
                 session_manager: Optional[SessionManager] = None):
        """
        Initialize dialog handler.
        
        Args:
            rag_generator: Optional RAGGenerator instance
            nlu_service: Optional NLUService instance
            session_manager: Optional SessionManager instance
        """
        self.rag_generator = rag_generator or RAGGenerator()
        self.nlu_service = nlu_service or NLUService()
        self.session_manager = session_manager or SessionManager()
        
        self.config = config_manager.dialog_config
        self.context_window = self.config.get('context_window', 5)
        self.state_tracking_enabled = self.config.get('state_tracking', {}).get('enabled', True)
        self.supported_states = self.config.get('state_tracking', {}).get('states', [])
        
        app_logger.info("Initialized Dialog Handler")
    
    def process_message(self, message: str, session_id: Optional[str] = None,
                       user_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Process user message and generate response.
        
        Args:
            message: User message
            session_id: Optional session identifier
            user_id: Optional user identifier
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Get or create session
            session = self.session_manager.get_or_create_session(session_id, user_id)
            
            # Analyze message with NLU
            nlu_result = self.nlu_service.analyze(message)
            intent = nlu_result['intent']['name']
            intent_confidence = nlu_result['intent']['confidence']
            entities = nlu_result['entities']
            
            # Add user message to history
            session.add_message('user', message, metadata={
                'intent': intent,
                'intent_confidence': intent_confidence,
                'entities': entities
            })
            
            # Update session context with extracted entities
            for entity_type, entity_list in entities.items():
                if entity_list:
                    session.update_context(f'last_{entity_type.lower()}', entity_list[0])
            
            # Determine conversation state
            if self.state_tracking_enabled:
                new_state = self._determine_state(intent, session)
                session.set_state(new_state)
            
            # Get conversation history for context
            history = session.get_history(max_turns=self.context_window)
            
            # Format history for generation (exclude current message)
            formatted_history = []
            for turn in history[:-1]:  # Exclude the just-added user message
                formatted_history.append({
                    'role': turn['role'],
                    'content': turn['content']
                })
            
            # Generate response
            use_rag = kwargs.get('use_rag', True)
            response = self.rag_generator.generate_response(
                query=message,
                conversation_history=formatted_history,
                use_rag=use_rag,
                **kwargs
            )
            
            # Add assistant response to history
            session.add_message('assistant', response, metadata={
                'intent': intent,
                'state': session.state
            })
            
            # Log conversation
            log_manager.log_conversation(
                session_id=session.session_id,
                user_message=message,
                bot_response=response,
                intent=intent,
                sentiment=None  # Will be added with sentiment analysis
            )
            
            # Prepare result
            result = {
                'session_id': session.session_id,
                'response': response,
                'intent': intent,
                'intent_confidence': intent_confidence,
                'entities': entities,
                'state': session.state,
                'turn_count': len(session.history) // 2
            }
            
            app_logger.info(f"Processed message in session {session.session_id}")
            return result
        
        except Exception as e:
            app_logger.error(f"Error processing message: {e}")
            return {
                'session_id': session_id,
                'response': "I apologize, but I encountered an error. Please try again.",
                'error': str(e)
            }
    
    def process_message_stream(self, message: str, session_id: Optional[str] = None,
                              user_id: Optional[str] = None, **kwargs):
        """
        Process message with streaming response.
        
        Args:
            message: User message
            session_id: Optional session identifier
            user_id: Optional user identifier
            **kwargs: Additional parameters
            
        Yields:
            Response chunks and metadata
        """
        try:
            # Get or create session
            session = self.session_manager.get_or_create_session(session_id, user_id)
            
            # Analyze message
            nlu_result = self.nlu_service.analyze(message)
            intent = nlu_result['intent']['name']
            entities = nlu_result['entities']
            
            # Add user message
            session.add_message('user', message, metadata={
                'intent': intent,
                'entities': entities
            })
            
            # Update state
            if self.state_tracking_enabled:
                new_state = self._determine_state(intent, session)
                session.set_state(new_state)
            
            # Get history
            history = session.get_history(max_turns=self.context_window)
            formatted_history = [
                {'role': turn['role'], 'content': turn['content']}
                for turn in history[:-1]
            ]
            
            # Yield metadata first
            yield {
                'type': 'metadata',
                'session_id': session.session_id,
                'intent': intent,
                'entities': entities,
                'state': session.state
            }
            
            # Generate and stream response
            response_chunks = []
            use_rag = kwargs.get('use_rag', True)
            
            for chunk in self.rag_generator.generate_response_stream(
                query=message,
                conversation_history=formatted_history,
                use_rag=use_rag,
                **kwargs
            ):
                response_chunks.append(chunk)
                yield {
                    'type': 'content',
                    'chunk': chunk
                }
            
            # Add complete response to history
            full_response = ''.join(response_chunks)
            session.add_message('assistant', full_response, metadata={
                'intent': intent,
                'state': session.state
            })
            
            # Log conversation
            log_manager.log_conversation(
                session_id=session.session_id,
                user_message=message,
                bot_response=full_response,
                intent=intent
            )
        
        except Exception as e:
            app_logger.error(f"Error in streaming message processing: {e}")
            yield {
                'type': 'error',
                'error': str(e)
            }
    
    def _determine_state(self, intent: str, session: ConversationSession) -> str:
        """
        Determine conversation state based on intent and history.
        
        Args:
            intent: Detected intent
            session: Current session
            
        Returns:
            New conversation state
        """
        current_state = session.state
        
        # State transition logic
        if intent in ['greeting']:
            return 'initial'
        elif intent in ['farewell']:
            return 'closed'
        elif intent in ['product_inquiry', 'technical_support', 'billing_inquiry']:
            return 'information_gathering'
        elif intent in ['complaint']:
            return 'escalation'
        elif current_state == 'information_gathering' and len(session.history) > 4:
            return 'processing'
        
        return current_state
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session information dictionary
        """
        session = self.session_manager.get_session(session_id)
        if session:
            return session.to_dict()
        return None
    
    def end_session(self, session_id: str):
        """
        End conversation session.
        
        Args:
            session_id: Session identifier
        """
        self.session_manager.delete_session(session_id)
        app_logger.info(f"Ended session: {session_id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get dialog handler statistics.
        
        Returns:
            Statistics dictionary
        """
        return self.session_manager.get_statistics()
