"""
Qianwen API Client - Interface for Alibaba's Qianwen language model.
"""

import os
from typing import Dict, List, Optional, Any
import dashscope
from dashscope import Generation

from src.config import config_manager
from src.logger import app_logger


class QianwenClient:
    """Client for Qianwen API integration."""
    
    def __init__(self):
        """Initialize Qianwen API client."""
        self.config = config_manager.generation_config
        self.api_key = config_manager.settings.dashscope_api_key
        self.model = self.config.get('model', 'qwen-turbo')
        self.parameters = self.config.get('parameters', {})
        
        # Set API key
        if self.api_key:
            dashscope.api_key = self.api_key
            app_logger.info("Initialized Qianwen API client")
        else:
            app_logger.warning("Qianwen API key not set. Set DASHSCOPE_API_KEY environment variable.")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                 history: Optional[List[Dict[str, str]]] = None,
                 **kwargs) -> Optional[str]:
        """
        Generate response using Qianwen API.
        
        Args:
            prompt: User prompt/query
            system_prompt: Optional system prompt
            history: Optional conversation history
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Generated response text
        """
        if not self.api_key:
            app_logger.error("Cannot generate: API key not set")
            return "I apologize, but the AI service is not properly configured. Please contact support."
        
        try:
            # Prepare messages
            messages = []
            
            # Add system message if provided
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            # Add conversation history
            if history:
                for turn in history:
                    messages.append(turn)
            
            # Add current user message
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            # Merge parameters
            params = {**self.parameters, **kwargs}
            
            # Call Qianwen API
            response = Generation.call(
                model=self.model,
                messages=messages,
                result_format='message',
                temperature=params.get('temperature', 0.7),
                top_p=params.get('top_p', 0.9),
                max_tokens=params.get('max_tokens', 1000),
                repetition_penalty=params.get('repetition_penalty', 1.1)
            )
            
            # Extract response
            if response.status_code == 200:
                result = response.output.choices[0].message.content
                app_logger.debug(f"Generated response: {result[:100]}...")
                return result
            else:
                app_logger.error(f"Qianwen API error: {response.code} - {response.message}")
                return None
        
        except Exception as e:
            app_logger.error(f"Error calling Qianwen API: {e}")
            return None
    
    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None,
                       history: Optional[List[Dict[str, str]]] = None,
                       **kwargs):
        """
        Generate streaming response using Qianwen API.
        
        Args:
            prompt: User prompt/query
            system_prompt: Optional system prompt
            history: Optional conversation history
            **kwargs: Additional parameters
            
        Yields:
            Response chunks
        """
        if not self.api_key:
            app_logger.error("Cannot generate: API key not set")
            yield "I apologize, but the AI service is not properly configured."
            return
        
        try:
            # Prepare messages
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            if history:
                for turn in history:
                    messages.append(turn)
            
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            # Merge parameters
            params = {**self.parameters, **kwargs}
            
            # Call Qianwen API with streaming
            responses = Generation.call(
                model=self.model,
                messages=messages,
                result_format='message',
                stream=True,
                temperature=params.get('temperature', 0.7),
                top_p=params.get('top_p', 0.9),
                max_tokens=params.get('max_tokens', 1000),
                repetition_penalty=params.get('repetition_penalty', 1.1),
                incremental_output=True
            )
            
            for response in responses:
                if response.status_code == 200:
                    chunk = response.output.choices[0].message.content
                    yield chunk
                else:
                    app_logger.error(f"Qianwen API error: {response.code}")
                    break
        
        except Exception as e:
            app_logger.error(f"Error in streaming generation: {e}")
            yield "An error occurred during response generation."
    
    def check_api_status(self) -> bool:
        """
        Check if API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            # Simple test call
            response = Generation.call(
                model=self.model,
                messages=[{'role': 'user', 'content': 'test'}],
                max_tokens=10
            )
            return response.status_code == 200
        except Exception as e:
            app_logger.error(f"API status check failed: {e}")
            return False
