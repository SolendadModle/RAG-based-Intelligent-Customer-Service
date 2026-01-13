"""
Core utilities and helper functions for the RAG-based Customer Service System.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """
    Load YAML configuration file.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        Dictionary containing configuration
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def load_json_file(file_path: str) -> Any:
    """
    Load JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def save_json_file(data: Any, file_path: str, indent: int = 2) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save JSON file
        indent: JSON indentation
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path object representing project root
    """
    return Path(__file__).parent.parent.parent


def ensure_directory(directory_path: str) -> None:
    """
    Ensure directory exists, create if not.
    
    Args:
        directory_path: Path to directory
    """
    os.makedirs(directory_path, exist_ok=True)


def generate_session_id(user_id: Optional[str] = None) -> str:
    """
    Generate unique session ID.
    
    Args:
        user_id: Optional user ID to include in session
        
    Returns:
        Unique session ID
    """
    timestamp = datetime.utcnow().isoformat()
    base_string = f"{user_id or 'anonymous'}_{timestamp}"
    session_id = hashlib.sha256(base_string.encode()).hexdigest()[:16]
    return session_id


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_conversation_history(history: List[Dict[str, str]], max_turns: int = 5) -> str:
    """
    Format conversation history for prompt context.
    
    Args:
        history: List of conversation turns
        max_turns: Maximum number of turns to include
        
    Returns:
        Formatted conversation history string
    """
    recent_history = history[-max_turns:] if len(history) > max_turns else history
    formatted_lines = []
    
    for turn in recent_history:
        role = turn.get('role', 'user')
        content = turn.get('content', '')
        formatted_lines.append(f"{role.capitalize()}: {content}")
    
    return "\n".join(formatted_lines)


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """
    Extract keywords from text (simple implementation).
    
    Args:
        text: Input text
        top_n: Number of top keywords to extract
        
    Returns:
        List of keywords
    """
    # Simple keyword extraction based on word frequency
    words = text.lower().split()
    # Filter out common stop words (simple list)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                  'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'should', 'could', 'may', 'might', 'can', 'i', 'you', 'he',
                  'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our',
                  'their', 'this', 'that', 'these', 'those'}
    
    filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Count word frequency
    word_freq = {}
    for word in filtered_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:top_n]]


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    # Remove potentially dangerous characters
    sanitized = text.strip()
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    return sanitized


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple text similarity (Jaccard similarity).
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-1)
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


class Timer:
    """Context manager for timing code execution."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self
    
    def __exit__(self, *args):
        self.end_time = datetime.utcnow()
        duration = (self.end_time - self.start_time).total_seconds()
        print(f"{self.name} took {duration:.3f} seconds")
    
    @property
    def duration(self) -> float:
        """Get duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
