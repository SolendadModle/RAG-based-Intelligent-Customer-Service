"""
Data validation and preprocessing utilities for the RAG Customer Service System.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import string
from enum import Enum

from src.logger import app_logger


class InputValidationError(Exception):
    """Exception raised for input validation errors."""
    pass


class MessageType(Enum):
    """Types of messages."""
    QUERY = "query"
    STATEMENT = "statement"
    QUESTION = "question"
    COMMAND = "command"
    GREETING = "greeting"
    FAREWELL = "farewell"


class TextPreprocessor:
    """Preprocess text for NLU and generation."""
    
    def __init__(self):
        """Initialize text preprocessor."""
        self.stop_words = self._load_stop_words()
        app_logger.info("Initialized Text Preprocessor")
    
    def _load_stop_words(self) -> set:
        """Load English stop words."""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'can', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our',
            'their', 'this', 'that', 'these', 'those', 'what', 'which', 'who',
            'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'just', 'don', 'now'
        }
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove control characters
        text = ''.join(char for char in text if char.isprintable() or char.isspace())
        
        return text.strip()
    
    def normalize_text(self, text: str, lowercase: bool = True, 
                      remove_punctuation: bool = False) -> str:
        """
        Normalize text for processing.
        
        Args:
            text: Input text
            lowercase: Convert to lowercase
            remove_punctuation: Remove punctuation
            
        Returns:
            Normalized text
        """
        text = self.clean_text(text)
        
        if lowercase:
            text = text.lower()
        
        if remove_punctuation:
            text = text.translate(str.maketrans('', '', string.punctuation))
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Simple word tokenization.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Clean text
        text = self.clean_text(text)
        
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        return tokens
    
    def remove_stop_words(self, tokens: List[str]) -> List[str]:
        """
        Remove stop words from tokens.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered tokens
        """
        return [token for token in tokens if token.lower() not in self.stop_words]
    
    def detect_message_type(self, text: str) -> MessageType:
        """
        Detect the type of message.
        
        Args:
            text: Input text
            
        Returns:
            MessageType
        """
        text_lower = text.lower().strip()
        
        # Greeting patterns
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(pattern in text_lower for pattern in greeting_patterns):
            return MessageType.GREETING
        
        # Farewell patterns
        farewell_patterns = ['goodbye', 'bye', 'see you', 'take care', 'farewell']
        if any(pattern in text_lower for pattern in farewell_patterns):
            return MessageType.FAREWELL
        
        # Question detection
        question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'which', 'can', 'could', 'would', 'should']
        if text.strip().endswith('?') or any(text_lower.startswith(word) for word in question_words):
            return MessageType.QUESTION
        
        # Command detection
        command_words = ['show', 'tell', 'give', 'send', 'help', 'get', 'find', 'search']
        if any(text_lower.startswith(word) for word in command_words):
            return MessageType.COMMAND
        
        # Query detection (contains question words)
        if any(word in text_lower for word in question_words):
            return MessageType.QUERY
        
        return MessageType.STATEMENT
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Extract keywords with simple TF scoring.
        
        Args:
            text: Input text
            top_n: Number of keywords to extract
            
        Returns:
            List of (keyword, score) tuples
        """
        # Tokenize and clean
        tokens = self.tokenize(text)
        tokens = self.remove_stop_words(tokens)
        
        # Count frequencies
        freq = {}
        for token in tokens:
            if len(token) > 2:  # Filter short tokens
                freq[token] = freq.get(token, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        # Normalize scores
        if sorted_keywords:
            max_freq = sorted_keywords[0][1]
            scored_keywords = [
                (word, count / max_freq)
                for word, count in sorted_keywords[:top_n]
            ]
            return scored_keywords
        
        return []
    
    def summarize_text(self, text: str, max_length: int = 100) -> str:
        """
        Create a simple text summary.
        
        Args:
            text: Input text
            max_length: Maximum summary length
            
        Returns:
            Summary text
        """
        if len(text) <= max_length:
            return text
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Take first sentence or truncate
        summary = sentences[0].strip()
        if len(summary) > max_length:
            summary = summary[:max_length - 3] + "..."
        
        return summary


class InputValidator:
    """Validate user inputs."""
    
    def __init__(self):
        """Initialize input validator."""
        self.max_message_length = 2000
        self.min_message_length = 1
        
        # Patterns for detecting potentially harmful inputs
        self.sql_injection_patterns = [
            r"(\bselect\b.*\bfrom\b)",
            r"(\bunion\b.*\bselect\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bupdate\b.*\bset\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bdrop\b.*\btable\b)"
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onclick\s*="
        ]
        
        app_logger.info("Initialized Input Validator")
    
    def validate_message(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user message.
        
        Args:
            message: User message
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if empty
        if not message or not message.strip():
            return False, "Message cannot be empty"
        
        # Check length
        if len(message) < self.min_message_length:
            return False, f"Message too short (minimum {self.min_message_length} characters)"
        
        if len(message) > self.max_message_length:
            return False, f"Message too long (maximum {self.max_message_length} characters)"
        
        # Check for SQL injection
        message_lower = message.lower()
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                app_logger.warning(f"Potential SQL injection detected: {message[:50]}")
                return False, "Invalid input detected"
        
        # Check for XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                app_logger.warning(f"Potential XSS detected: {message[:50]}")
                return False, "Invalid input detected"
        
        return True, None
    
    def validate_session_id(self, session_id: str) -> bool:
        """
        Validate session ID format.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if valid
        """
        # Check format (hexadecimal, 16 characters)
        return bool(re.match(r'^[0-9a-f]{16}$', session_id))
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address.
        
        Args:
            email: Email address
            
        Returns:
            True if valid
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str) -> bool:
        """
        Validate phone number.
        
        Args:
            phone: Phone number
            
        Returns:
            True if valid
        """
        # Remove common separators
        cleaned = re.sub(r'[-.()\s]', '', phone)
        
        # Check if it's a valid number (10-15 digits)
        return cleaned.isdigit() and 10 <= len(cleaned) <= 15
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input.
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text
        """
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove script tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove other potentially dangerous HTML
        text = re.sub(r'<[^>]*>', '', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text


class ConversationAnalyzer:
    """Analyze conversation patterns and quality."""
    
    def __init__(self):
        """Initialize conversation analyzer."""
        self.preprocessor = TextPreprocessor()
        app_logger.info("Initialized Conversation Analyzer")
    
    def analyze_conversation_flow(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze conversation flow and patterns.
        
        Args:
            history: Conversation history
            
        Returns:
            Analysis results
        """
        if not history:
            return {
                'turn_count': 0,
                'user_turns': 0,
                'bot_turns': 0,
                'avg_user_message_length': 0,
                'avg_bot_message_length': 0
            }
        
        user_messages = [msg for msg in history if msg.get('role') == 'user']
        bot_messages = [msg for msg in history if msg.get('role') == 'assistant']
        
        user_lengths = [len(msg.get('content', '')) for msg in user_messages]
        bot_lengths = [len(msg.get('content', '')) for msg in bot_messages]
        
        return {
            'turn_count': len(history),
            'user_turns': len(user_messages),
            'bot_turns': len(bot_messages),
            'avg_user_message_length': sum(user_lengths) / len(user_lengths) if user_lengths else 0,
            'avg_bot_message_length': sum(bot_lengths) / len(bot_lengths) if bot_lengths else 0,
            'conversation_balance': len(user_messages) / len(bot_messages) if bot_messages else 0
        }
    
    def detect_conversation_issues(self, history: List[Dict[str, Any]]) -> List[str]:
        """
        Detect potential issues in conversation.
        
        Args:
            history: Conversation history
            
        Returns:
            List of detected issues
        """
        issues = []
        
        if not history:
            return issues
        
        # Check for repetition
        user_messages = [msg.get('content', '') for msg in history if msg.get('role') == 'user']
        if len(user_messages) != len(set(user_messages)):
            issues.append("User is repeating messages")
        
        # Check for very short responses
        recent_bot = [msg for msg in history[-5:] if msg.get('role') == 'assistant']
        if recent_bot:
            avg_length = sum(len(msg.get('content', '')) for msg in recent_bot) / len(recent_bot)
            if avg_length < 20:
                issues.append("Bot responses are too short")
        
        # Check for long conversation without resolution
        if len(history) > 20:
            issues.append("Conversation is very long - may need escalation")
        
        # Check for negative sentiment persistence
        recent_user = history[-3:] if len(history) >= 3 else history
        negative_count = sum(
            1 for msg in recent_user
            if msg.get('role') == 'user' and
            msg.get('metadata', {}).get('sentiment') == 'negative'
        )
        if negative_count >= 2:
            issues.append("Persistent negative sentiment detected")
        
        return issues
    
    def calculate_conversation_quality(self, history: List[Dict[str, Any]]) -> float:
        """
        Calculate conversation quality score (0-1).
        
        Args:
            history: Conversation history
            
        Returns:
            Quality score
        """
        if not history:
            return 0.5  # Neutral for empty conversation
        
        score = 1.0
        
        # Penalize for detected issues
        issues = self.detect_conversation_issues(history)
        score -= len(issues) * 0.1
        
        # Penalize for very short or very long conversations
        if len(history) < 2:
            score -= 0.2
        elif len(history) > 30:
            score -= 0.2
        
        # Bonus for balanced conversation
        flow = self.analyze_conversation_flow(history)
        balance = flow.get('conversation_balance', 0)
        if 0.8 <= balance <= 1.2:
            score += 0.1
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))
    
    def generate_conversation_summary(self, history: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of the conversation.
        
        Args:
            history: Conversation history
            
        Returns:
            Summary text
        """
        if not history:
            return "No conversation history."
        
        flow = self.analyze_conversation_flow(history)
        issues = self.detect_conversation_issues(history)
        quality = self.calculate_conversation_quality(history)
        
        summary_parts = [
            f"Conversation with {flow['turn_count']} total turns",
            f"({flow['user_turns']} user, {flow['bot_turns']} bot)",
            f"Quality score: {quality:.2f}"
        ]
        
        if issues:
            summary_parts.append(f"Issues: {', '.join(issues)}")
        
        # Extract main topics (simplified)
        user_messages = [msg.get('content', '') for msg in history if msg.get('role') == 'user']
        if user_messages:
            combined_text = ' '.join(user_messages)
            keywords = self.preprocessor.extract_keywords(combined_text, top_n=3)
            if keywords:
                topics = ', '.join([kw for kw, _ in keywords])
                summary_parts.append(f"Main topics: {topics}")
        
        return '. '.join(summary_parts) + '.'


# Global instances
text_preprocessor = TextPreprocessor()
input_validator = InputValidator()
conversation_analyzer = ConversationAnalyzer()
