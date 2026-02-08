"""
RAG Generation Module - Combines retrieval with generation.
"""

from typing import Dict, List, Optional, Any
from src.generation.qianwen_client import QianwenClient
from src.knowledge_base.retrieval import RetrievalService
from src.config import config_manager
from src.logger import app_logger
from src.utils import format_conversation_history


class RAGGenerator:
    """RAG-based response generator combining retrieval and generation."""
    
    def __init__(self, retrieval_service: Optional[RetrievalService] = None):
        """
        Initialize RAG generator.
        
        Args:
            retrieval_service: Optional RetrievalService instance
        """
        self.qianwen_client = QianwenClient()
        self.retrieval_service = retrieval_service or RetrievalService()
        self.config = config_manager.generation_config
        self.prompt_templates = self.config.get('prompt_templates', {})
        
        app_logger.info("Initialized RAG Generator")
    
    def generate_response(self, query: str, conversation_history: Optional[List[Dict[str, str]]] = None,
                         use_rag: bool = True, **kwargs) -> str:
        """
        Generate response for user query.
        
        Args:
            query: User query
            conversation_history: Optional conversation history
            use_rag: Whether to use RAG (retrieve context)
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        try:
            # Get system prompt
            system_prompt = self.prompt_templates.get('system', '')
            
            if use_rag:
                # Retrieve relevant context
                context = self.retrieval_service.retrieve_context(query)
                
                # Format conversation history
                history_str = ""
                if conversation_history:
                    history_str = format_conversation_history(conversation_history)
                
                # Build RAG prompt
                rag_template = self.prompt_templates.get('rag', '')
                prompt = rag_template.format(
                    context=context,
                    history=history_str,
                    question=query
                )
            else:
                # Direct generation without retrieval
                prompt = query
            
            # Generate response
            response = self.qianwen_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                history=conversation_history,
                **kwargs
            )
            
            if response:
                app_logger.info(f"Generated response for query: {query[:50]}...")
                return response
            else:
                return "I apologize, but I'm having trouble generating a response. Please try again."
        
        except Exception as e:
            app_logger.error(f"Error in RAG generation: {e}")
            return "I encountered an error while processing your request. Please try again."
    
    def generate_response_stream(self, query: str, conversation_history: Optional[List[Dict[str, str]]] = None,
                                use_rag: bool = True, **kwargs):
        """
        Generate streaming response for user query.
        
        Args:
            query: User query
            conversation_history: Optional conversation history
            use_rag: Whether to use RAG
            **kwargs: Additional parameters
            
        Yields:
            Response chunks
        """
        try:
            system_prompt = self.prompt_templates.get('system', '')
            
            if use_rag:
                context = self.retrieval_service.retrieve_context(query)
                
                history_str = ""
                if conversation_history:
                    history_str = format_conversation_history(conversation_history)
                
                rag_template = self.prompt_templates.get('rag', '')
                prompt = rag_template.format(
                    context=context,
                    history=history_str,
                    question=query
                )
            else:
                prompt = query
            
            # Generate streaming response
            for chunk in self.qianwen_client.generate_stream(
                prompt=prompt,
                system_prompt=system_prompt,
                history=conversation_history,
                **kwargs
            ):
                yield chunk
        
        except Exception as e:
            app_logger.error(f"Error in streaming generation: {e}")
            yield "An error occurred while processing your request."
    
    def generate_with_context(self, query: str, context: str, 
                            conversation_history: Optional[List[Dict[str, str]]] = None,
                            **kwargs) -> str:
        """
        Generate response with provided context.
        
        Args:
            query: User query
            context: Pre-retrieved context
            conversation_history: Optional conversation history
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        try:
            system_prompt = self.prompt_templates.get('system', '')
            
            history_str = ""
            if conversation_history:
                history_str = format_conversation_history(conversation_history)
            
            rag_template = self.prompt_templates.get('rag', '')
            prompt = rag_template.format(
                context=context,
                history=history_str,
                question=query
            )
            
            response = self.qianwen_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                history=conversation_history,
                **kwargs
            )
            
            return response or "I apologize, but I couldn't generate a response."
        
        except Exception as e:
            app_logger.error(f"Error in context-based generation: {e}")
            return "An error occurred while processing your request."
    
    def check_service_status(self) -> Dict[str, Any]:
        """
        Check status of generation service components.
        
        Returns:
            Dictionary with status information
        """
        status = {
            'qianwen_api': self.qianwen_client.check_api_status(),
            'retrieval_service': self.retrieval_service.get_index_stats()
        }
        return status
