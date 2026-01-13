"""
Logging configuration and utilities for the RAG-based Customer Service System.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from datetime import datetime

from src.config import config_manager
from src.utils import ensure_directory


class LogManager:
    """Manage application logging with Loguru."""
    
    def __init__(self):
        """Initialize log manager."""
        self.log_path = config_manager.settings.log_path
        ensure_directory(self.log_path)
        
        # Remove default handler
        logger.remove()
        
        # Configure logging
        self._configure_logging()
    
    def _configure_logging(self):
        """Configure logging handlers based on configuration."""
        log_config = config_manager.logging_config
        log_level = config_manager.settings.log_level
        
        # Console handler
        console_config = log_config.get('handlers', {}).get('console', {})
        if console_config.get('enabled', True):
            logger.add(
                sys.stdout,
                level=console_config.get('level', log_level),
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                colorize=True
            )
        
        # File handler
        file_config = log_config.get('handlers', {}).get('file', {})
        if file_config.get('enabled', True):
            log_file = os.path.join(self.log_path, "app_{time:YYYY-MM-DD}.log")
            logger.add(
                log_file,
                level=file_config.get('level', 'DEBUG'),
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation=file_config.get('rotation', '100 MB'),
                retention=file_config.get('retention', '30 days'),
                compression="zip"
            )
        
        # Conversation log handler
        if log_config.get('log_conversations', True):
            conversation_log = os.path.join(self.log_path, "conversations_{time:YYYY-MM-DD}.log")
            logger.add(
                conversation_log,
                level="INFO",
                format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
                filter=lambda record: record["extra"].get("type") == "conversation",
                rotation="00:00",
                retention="90 days",
                compression="zip"
            )
        
        # API call log handler
        if log_config.get('log_api_calls', True):
            api_log = os.path.join(self.log_path, "api_calls_{time:YYYY-MM-DD}.log")
            logger.add(
                api_log,
                level="INFO",
                format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
                filter=lambda record: record["extra"].get("type") == "api_call",
                rotation="00:00",
                retention="30 days",
                compression="zip"
            )
    
    def get_logger(self, name: Optional[str] = None):
        """
        Get logger instance.
        
        Args:
            name: Optional logger name
            
        Returns:
            Logger instance
        """
        if name:
            return logger.bind(name=name)
        return logger
    
    def log_conversation(self, session_id: str, user_message: str, bot_response: str, 
                        intent: Optional[str] = None, sentiment: Optional[str] = None):
        """
        Log conversation turn.
        
        Args:
            session_id: Session identifier
            user_message: User's message
            bot_response: Bot's response
            intent: Detected intent
            sentiment: Detected sentiment
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "intent": intent,
            "sentiment": sentiment
        }
        logger.bind(type="conversation").info(f"CONVERSATION: {log_entry}")
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, 
                    duration: float, error: Optional[str] = None):
        """
        Log API call.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            duration: Request duration in seconds
            error: Error message if any
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "error": error
        }
        logger.bind(type="api_call").info(f"API_CALL: {log_entry}")
    
    def log_error(self, error: Exception, context: Optional[str] = None):
        """
        Log error with context.
        
        Args:
            error: Exception object
            context: Additional context information
        """
        logger.error(f"Error in {context or 'application'}: {str(error)}", exc_info=True)


# Global log manager instance
log_manager = LogManager()
app_logger = log_manager.get_logger("app")
