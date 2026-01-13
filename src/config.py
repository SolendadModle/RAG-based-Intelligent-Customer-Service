"""
Configuration management for the RAG-based Customer Service System.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

from src.utils import load_yaml_config, get_project_root


# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables and config files."""
    
    # Qianwen API Configuration
    dashscope_api_key: str = Field(default="", alias="DASHSCOPE_API_KEY")
    qianwen_model: str = Field(default="qwen-turbo", alias="QIANWEN_MODEL")
    
    # Vector Store Configuration
    vector_store_type: str = Field(default="faiss", alias="VECTOR_STORE_TYPE")
    vector_store_path: str = Field(default="./data/vector_store", alias="VECTOR_STORE_PATH")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    
    # NLU Configuration
    nlu_model: str = Field(default="en_core_web_sm", alias="NLU_MODEL")
    intent_threshold: float = Field(default=0.7, alias="INTENT_THRESHOLD")
    entity_threshold: float = Field(default=0.6, alias="ENTITY_THRESHOLD")
    
    # Knowledge Base Configuration
    knowledge_base_path: str = Field(default="./data/knowledge_base", alias="KNOWLEDGE_BASE_PATH")
    faq_file: str = Field(default="./data/knowledge_base/faq.json", alias="FAQ_FILE")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_debug: bool = Field(default=True, alias="API_DEBUG")
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")
    
    # Redis Configuration
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_path: str = Field(default="./data/logs", alias="LOG_PATH")
    
    # Sentiment Analysis
    sentiment_model: str = Field(default="distilbert-base-uncased-finetuned-sst-2-english", alias="SENTIMENT_MODEL")
    
    # Recommendation Engine
    max_recommendations: int = Field(default=5, alias="MAX_RECOMMENDATIONS")
    recommendation_threshold: float = Field(default=0.65, alias="RECOMMENDATION_THRESHOLD")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class ConfigManager:
    """Manage application configuration from multiple sources."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to YAML config file. If None, uses default path.
        """
        self.settings = Settings()
        
        # Load YAML configuration
        if config_path is None:
            config_path = os.path.join(get_project_root(), "config", "config.yaml")
        
        self.yaml_config = {}
        if os.path.exists(config_path):
            self.yaml_config = load_yaml_config(config_path)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        # Try to get from environment settings first
        if hasattr(self.settings, key.lower().replace('.', '_')):
            return getattr(self.settings, key.lower().replace('.', '_'))
        
        # Try to get from YAML config
        keys = key.split('.')
        value = self.yaml_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Dictionary containing section configuration
        """
        return self.yaml_config.get(section, {})
    
    @property
    def nlu_config(self) -> Dict[str, Any]:
        """Get NLU configuration section."""
        return self.get_section('nlu')
    
    @property
    def knowledge_base_config(self) -> Dict[str, Any]:
        """Get knowledge base configuration section."""
        return self.get_section('knowledge_base')
    
    @property
    def generation_config(self) -> Dict[str, Any]:
        """Get generation configuration section."""
        return self.get_section('generation')
    
    @property
    def dialog_config(self) -> Dict[str, Any]:
        """Get dialog configuration section."""
        return self.get_section('dialog')
    
    @property
    def sentiment_config(self) -> Dict[str, Any]:
        """Get sentiment configuration section."""
        return self.get_section('sentiment')
    
    @property
    def recommendation_config(self) -> Dict[str, Any]:
        """Get recommendation configuration section."""
        return self.get_section('recommendation')
    
    @property
    def api_config(self) -> Dict[str, Any]:
        """Get API configuration section."""
        return self.get_section('api')
    
    @property
    def logging_config(self) -> Dict[str, Any]:
        """Get logging configuration section."""
        return self.get_section('logging')


# Global configuration instance
config_manager = ConfigManager()
