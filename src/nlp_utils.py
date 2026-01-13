"""
Advanced NLP utilities and text analysis for the RAG Customer Service System.
Provides additional text processing, analysis, and enhancement capabilities.
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
import math
from datetime import datetime

from src.logger import app_logger


class TextSimilarity:
    """Calculate various text similarity metrics."""
    
    def __init__(self):
        """Initialize text similarity calculator."""
        app_logger.info("Initialized Text Similarity Calculator")
    
    def jaccard_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate Jaccard similarity between two texts.
        
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
    
    def cosine_similarity_text(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts using word frequencies.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        words1 = text1.lower().split()
        words2 = text2.lower().split()
        
        # Get unique words
        unique_words = set(words1 + words2)
        
        # Create frequency vectors
        vec1 = [words1.count(word) for word in unique_words]
        vec2 = [words2.count(word) for word in unique_words]
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def levenshtein_distance(self, text1: str, text2: str) -> int:
        """
        Calculate Levenshtein edit distance.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Edit distance
        """
        if len(text1) < len(text2):
            return self.levenshtein_distance(text2, text1)
        
        if len(text2) == 0:
            return len(text1)
        
        previous_row = range(len(text2) + 1)
        for i, c1 in enumerate(text1):
            current_row = [i + 1]
            for j, c2 in enumerate(text2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def normalized_levenshtein_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate normalized Levenshtein similarity (0-1).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score
        """
        distance = self.levenshtein_distance(text1, text2)
        max_length = max(len(text1), len(text2))
        
        if max_length == 0:
            return 1.0
        
        return 1.0 - (distance / max_length)


class TextEnhancer:
    """Enhance and improve text quality."""
    
    def __init__(self):
        """Initialize text enhancer."""
        self.contractions = self._load_contractions()
        app_logger.info("Initialized Text Enhancer")
    
    def _load_contractions(self) -> Dict[str, str]:
        """Load contraction mappings."""
        return {
            "ain't": "am not", "aren't": "are not", "can't": "cannot",
            "can't've": "cannot have", "could've": "could have",
            "couldn't": "could not", "didn't": "did not",
            "doesn't": "does not", "don't": "do not", "hadn't": "had not",
            "hasn't": "has not", "haven't": "have not", "he'd": "he would",
            "he'll": "he will", "he's": "he is", "how'd": "how did",
            "how'll": "how will", "how's": "how is", "i'd": "i would",
            "i'll": "i will", "i'm": "i am", "i've": "i have",
            "isn't": "is not", "it'd": "it would", "it'll": "it will",
            "it's": "it is", "let's": "let us", "shouldn't": "should not",
            "that's": "that is", "there's": "there is", "they'd": "they would",
            "they'll": "they will", "they're": "they are",
            "they've": "they have", "wasn't": "was not", "we'd": "we would",
            "we'll": "we will", "we're": "we are", "we've": "we have",
            "weren't": "were not", "what'll": "what will", "what're": "what are",
            "what's": "what is", "what've": "what have", "where's": "where is",
            "who'd": "who would", "who'll": "who will", "who're": "who are",
            "who's": "who is", "who've": "who have", "won't": "will not",
            "wouldn't": "would not", "you'd": "you would", "you'll": "you will",
            "you're": "you are", "you've": "you have"
        }
    
    def expand_contractions(self, text: str) -> str:
        """
        Expand contractions in text.
        
        Args:
            text: Input text
            
        Returns:
            Text with expanded contractions
        """
        words = text.split()
        expanded_words = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower in self.contractions:
                expanded_words.append(self.contractions[word_lower])
            else:
                expanded_words.append(word)
        
        return ' '.join(expanded_words)
    
    def fix_common_typos(self, text: str) -> str:
        """
        Fix common typos in text.
        
        Args:
            text: Input text
            
        Returns:
            Text with typos fixed
        """
        typos = {
            'teh': 'the', 'taht': 'that', 'waht': 'what',
            'wiht': 'with', 'recieve': 'receive', 'occured': 'occurred',
            'seperate': 'separate', 'definately': 'definitely',
            'untill': 'until', 'sucessful': 'successful'
        }
        
        words = text.split()
        fixed_words = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower in typos:
                fixed_words.append(typos[word_lower])
            else:
                fixed_words.append(word)
        
        return ' '.join(fixed_words)
    
    def improve_readability(self, text: str) -> str:
        """
        Improve text readability.
        
        Args:
            text: Input text
            
        Returns:
            Improved text
        """
        # Capitalize first letter of sentences
        text = re.sub(r'(^|[.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
        
        # Fix multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', text)
        
        return text.strip()


class TopicExtractor:
    """Extract topics and themes from text."""
    
    def __init__(self):
        """Initialize topic extractor."""
        self.domain_keywords = self._load_domain_keywords()
        app_logger.info("Initialized Topic Extractor")
    
    def _load_domain_keywords(self) -> Dict[str, List[str]]:
        """Load domain-specific keywords."""
        return {
            'technical': [
                'error', 'bug', 'issue', 'problem', 'crash', 'freeze',
                'slow', 'performance', 'install', 'configure', 'setup',
                'api', 'integration', 'connection', 'timeout', 'failure'
            ],
            'billing': [
                'payment', 'charge', 'invoice', 'subscription', 'refund',
                'price', 'cost', 'billing', 'transaction', 'receipt',
                'credit card', 'paypal', 'bank', 'money', 'fee'
            ],
            'account': [
                'account', 'profile', 'password', 'login', 'logout',
                'username', 'email', 'register', 'signup', 'signin',
                'settings', 'preferences', 'security', 'verification'
            ],
            'product': [
                'product', 'feature', 'functionality', 'capability',
                'service', 'plan', 'tier', 'upgrade', 'downgrade',
                'demo', 'trial', 'version', 'release', 'update'
            ],
            'support': [
                'help', 'support', 'assistance', 'guide', 'documentation',
                'tutorial', 'howto', 'manual', 'faq', 'question',
                'contact', 'chat', 'call', 'email', 'ticket'
            ]
        }
    
    def extract_topics(self, text: str) -> List[Tuple[str, float]]:
        """
        Extract topics from text with confidence scores.
        
        Args:
            text: Input text
            
        Returns:
            List of (topic, confidence) tuples
        """
        text_lower = text.lower()
        topic_scores = {}
        
        for topic, keywords in self.domain_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                topic_scores[topic] = confidence
        
        # Sort by confidence
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_topics
    
    def get_primary_topic(self, text: str) -> Optional[str]:
        """
        Get primary topic of text.
        
        Args:
            text: Input text
            
        Returns:
            Primary topic or None
        """
        topics = self.extract_topics(text)
        return topics[0][0] if topics else None
    
    def categorize_text(self, text: str, threshold: float = 0.2) -> List[str]:
        """
        Categorize text into multiple topics.
        
        Args:
            text: Input text
            threshold: Minimum confidence threshold
            
        Returns:
            List of relevant topics
        """
        topics = self.extract_topics(text)
        return [topic for topic, conf in topics if conf >= threshold]


class LanguageDetector:
    """Detect language patterns and characteristics."""
    
    def __init__(self):
        """Initialize language detector."""
        self.language_patterns = self._load_language_patterns()
        app_logger.info("Initialized Language Detector")
    
    def _load_language_patterns(self) -> Dict[str, List[str]]:
        """Load common words for different languages."""
        return {
            'english': ['the', 'is', 'and', 'to', 'of', 'in', 'a', 'that', 'it', 'for'],
            'spanish': ['el', 'la', 'de', 'que', 'y', 'es', 'en', 'un', 'por', 'con'],
            'french': ['le', 'de', 'un', 'être', 'et', 'à', 'il', 'avoir', 'ne', 'je'],
            'german': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
            'chinese': ['的', '一', '是', '在', '不', '了', '有', '和', '人', '这']
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text (simple implementation).
        
        Args:
            text: Input text
            
        Returns:
            Detected language
        """
        text_lower = text.lower()
        scores = {}
        
        for lang, patterns in self.language_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in text_lower)
            scores[lang] = matches
        
        if not scores or max(scores.values()) == 0:
            return 'unknown'
        
        return max(scores, key=scores.get)
    
    def is_formal_language(self, text: str) -> bool:
        """
        Determine if text uses formal language.
        
        Args:
            text: Input text
            
        Returns:
            True if formal
        """
        formal_indicators = [
            'please', 'kindly', 'would', 'could', 'may i',
            'thank you', 'regards', 'sincerely', 'respectfully'
        ]
        
        informal_indicators = [
            'hey', 'yeah', 'nope', 'gonna', 'wanna', 'gotta',
            'lol', 'omg', 'btw', 'asap'
        ]
        
        text_lower = text.lower()
        formal_count = sum(1 for ind in formal_indicators if ind in text_lower)
        informal_count = sum(1 for ind in informal_indicators if ind in text_lower)
        
        return formal_count > informal_count


class SemanticAnalyzer:
    """Analyze semantic properties of text."""
    
    def __init__(self):
        """Initialize semantic analyzer."""
        self.positive_words = self._load_positive_words()
        self.negative_words = self._load_negative_words()
        app_logger.info("Initialized Semantic Analyzer")
    
    def _load_positive_words(self) -> Set[str]:
        """Load positive sentiment words."""
        return {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'awesome', 'perfect', 'love', 'best', 'happy', 'pleased',
            'satisfied', 'delighted', 'impressed', 'helpful', 'useful'
        }
    
    def _load_negative_words(self) -> Set[str]:
        """Load negative sentiment words."""
        return {
            'bad', 'poor', 'terrible', 'awful', 'horrible', 'worst',
            'hate', 'disappointed', 'frustrated', 'angry', 'annoyed',
            'useless', 'broken', 'failed', 'problem', 'issue', 'error'
        }
    
    def calculate_polarity(self, text: str) -> float:
        """
        Calculate text polarity (-1 to 1).
        
        Args:
            text: Input text
            
        Returns:
            Polarity score
        """
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0
        
        return (positive_count - negative_count) / total_sentiment_words
    
    def extract_named_entities_simple(self, text: str) -> List[str]:
        """
        Simple named entity extraction (capitalized words).
        
        Args:
            text: Input text
            
        Returns:
            List of potential named entities
        """
        # Find capitalized words (simple approach)
        words = text.split()
        entities = []
        
        for i, word in enumerate(words):
            # Skip first word of sentence
            if i > 0 and word[0].isupper() and word.lower() not in ['i', 'a']:
                entities.append(word)
        
        return entities
    
    def identify_questions(self, text: str) -> List[str]:
        """
        Identify questions in text.
        
        Args:
            text: Input text
            
        Returns:
            List of questions
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        questions = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence.endswith('?') or any(
                sentence.lower().startswith(qw)
                for qw in ['what', 'when', 'where', 'who', 'why', 'how', 'which']
            ):
                questions.append(sentence)
        
        return questions


class TextMetrics:
    """Calculate various text metrics."""
    
    def __init__(self):
        """Initialize text metrics calculator."""
        app_logger.info("Initialized Text Metrics Calculator")
    
    def word_count(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    def character_count(self, text: str, include_spaces: bool = True) -> int:
        """Count characters in text."""
        if include_spaces:
            return len(text)
        return len(text.replace(' ', ''))
    
    def sentence_count(self, text: str) -> int:
        """Count sentences in text."""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    def avg_word_length(self, text: str) -> float:
        """Calculate average word length."""
        words = text.split()
        if not words:
            return 0.0
        return sum(len(word) for word in words) / len(words)
    
    def avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length in words."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        total_words = sum(len(s.split()) for s in sentences)
        return total_words / len(sentences)
    
    def lexical_diversity(self, text: str) -> float:
        """
        Calculate lexical diversity (unique words / total words).
        
        Args:
            text: Input text
            
        Returns:
            Diversity score (0-1)
        """
        words = text.lower().split()
        if not words:
            return 0.0
        
        unique_words = set(words)
        return len(unique_words) / len(words)
    
    def reading_ease(self, text: str) -> float:
        """
        Calculate simplified reading ease score (0-100).
        Higher scores indicate easier text.
        
        Args:
            text: Input text
            
        Returns:
            Reading ease score
        """
        words = self.word_count(text)
        sentences = self.sentence_count(text)
        
        if sentences == 0 or words == 0:
            return 0.0
        
        avg_sentence_len = words / sentences
        avg_word_len = self.avg_word_length(text)
        
        # Simplified formula
        score = 100 - (avg_sentence_len * 1.5) - (avg_word_len * 10)
        
        return max(0, min(100, score))
    
    def get_all_metrics(self, text: str) -> Dict[str, Any]:
        """
        Get all text metrics.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with all metrics
        """
        return {
            'word_count': self.word_count(text),
            'character_count': self.character_count(text),
            'sentence_count': self.sentence_count(text),
            'avg_word_length': self.avg_word_length(text),
            'avg_sentence_length': self.avg_sentence_length(text),
            'lexical_diversity': self.lexical_diversity(text),
            'reading_ease': self.reading_ease(text)
        }


# Global instances
text_similarity = TextSimilarity()
text_enhancer = TextEnhancer()
topic_extractor = TopicExtractor()
language_detector = LanguageDetector()
semantic_analyzer = SemanticAnalyzer()
text_metrics = TextMetrics()
