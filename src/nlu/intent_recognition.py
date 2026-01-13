"""
Intent Recognition Module for Natural Language Understanding.
"""

from typing import Dict, List, Optional, Tuple
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from src.config import config_manager
from src.logger import app_logger


class IntentRecognizer:
    """Intent recognition using pattern matching and similarity scoring."""
    
    def __init__(self):
        """Initialize intent recognizer."""
        self.config = config_manager.nlu_config.get('intent_recognition', {})
        self.threshold = self.config.get('threshold', 0.7)
        self.supported_intents = self.config.get('supported_intents', [])
        
        # Load spaCy model
        try:
            self.nlp = spacy.load(config_manager.settings.nlu_model)
            app_logger.info(f"Loaded spaCy model: {config_manager.settings.nlu_model}")
        except OSError:
            app_logger.warning(f"spaCy model not found. Using blank English model.")
            self.nlp = spacy.blank("en")
        
        # Intent patterns - training examples for each intent
        self.intent_patterns = self._load_intent_patterns()
        
        # Initialize vectorizer
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
        self._train_vectorizer()
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """
        Load intent patterns (training examples).
        
        Returns:
            Dictionary mapping intents to example phrases
        """
        patterns = {
            "greeting": [
                "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
                "greetings", "hi there", "hey there", "howdy", "what's up"
            ],
            "farewell": [
                "goodbye", "bye", "see you", "take care", "farewell", "catch you later",
                "have a good day", "talk to you later", "bye bye", "good night"
            ],
            "product_inquiry": [
                "tell me about product", "product information", "what products do you have",
                "show me products", "product details", "available products", "product catalog",
                "i want to know about", "information on product", "product specs", "product features"
            ],
            "technical_support": [
                "technical issue", "not working", "error message", "problem with",
                "troubleshoot", "fix", "repair", "technical help", "support needed",
                "something is broken", "malfunction", "issue with", "help me fix"
            ],
            "billing_inquiry": [
                "billing question", "invoice", "payment", "charge", "subscription",
                "bill amount", "payment method", "refund", "pricing", "cost",
                "how much", "charges", "receipt", "transaction"
            ],
            "complaint": [
                "i am not satisfied", "disappointed", "poor service", "bad experience",
                "unhappy with", "complaint", "not good", "terrible", "awful",
                "unacceptable", "frustrated", "angry about", "dissatisfied"
            ],
            "feedback": [
                "feedback", "suggestion", "recommend", "improvement", "opinion",
                "thought about", "would like to see", "feature request", "my experience",
                "testimonial", "review", "comment on"
            ],
            "order_status": [
                "order status", "where is my order", "track order", "delivery status",
                "shipping information", "when will it arrive", "order tracking",
                "check order", "order update", "estimated delivery", "order number"
            ],
            "return_request": [
                "return product", "want to return", "refund request", "send back",
                "not satisfied with product", "return policy", "exchange",
                "return authorization", "send it back", "return process"
            ],
            "general_question": [
                "what is", "how does", "can you", "do you", "tell me",
                "explain", "i want to know", "question about", "curious about",
                "information on", "help me understand", "clarify"
            ]
        }
        return patterns
    
    def _train_vectorizer(self):
        """Train TF-IDF vectorizer on intent patterns."""
        all_patterns = []
        for patterns in self.intent_patterns.values():
            all_patterns.extend(patterns)
        
        if all_patterns:
            self.vectorizer.fit(all_patterns)
            app_logger.info(f"Trained intent vectorizer on {len(all_patterns)} patterns")
    
    def recognize(self, text: str) -> Tuple[Optional[str], float]:
        """
        Recognize intent from text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        if not text or not text.strip():
            return None, 0.0
        
        text_lower = text.lower().strip()
        
        # Rule-based matching for high-confidence cases
        rule_intent, rule_score = self._rule_based_matching(text_lower)
        if rule_score >= 0.9:
            app_logger.debug(f"Rule-based intent: {rule_intent} (confidence: {rule_score:.3f})")
            return rule_intent, rule_score
        
        # Similarity-based matching
        similarity_intent, similarity_score = self._similarity_based_matching(text_lower)
        
        # Combine scores (weighted average)
        if rule_intent == similarity_intent:
            combined_score = 0.6 * rule_score + 0.4 * similarity_score
            final_intent = rule_intent
        else:
            if rule_score > similarity_score:
                final_intent = rule_intent
                combined_score = rule_score
            else:
                final_intent = similarity_intent
                combined_score = similarity_score
        
        # Apply threshold
        if combined_score < self.threshold:
            app_logger.debug(f"Intent confidence below threshold: {combined_score:.3f} < {self.threshold}")
            return "general_question", combined_score
        
        app_logger.debug(f"Recognized intent: {final_intent} (confidence: {combined_score:.3f})")
        return final_intent, combined_score
    
    def _rule_based_matching(self, text: str) -> Tuple[Optional[str], float]:
        """
        Rule-based intent matching using keyword patterns.
        
        Args:
            text: Input text (lowercase)
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        best_intent = None
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    # Exact match gets high score
                    if text == pattern:
                        return intent, 1.0
                    
                    # Partial match - calculate score based on pattern length
                    score = min(len(pattern) / len(text), 0.95)
                    if score > best_score:
                        best_score = score
                        best_intent = intent
        
        return best_intent, best_score
    
    def _similarity_based_matching(self, text: str) -> Tuple[Optional[str], float]:
        """
        Similarity-based intent matching using TF-IDF and cosine similarity.
        
        Args:
            text: Input text (lowercase)
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        try:
            # Transform input text
            text_vector = self.vectorizer.transform([text])
            
            best_intent = None
            best_score = 0.0
            
            # Compare with each intent's patterns
            for intent, patterns in self.intent_patterns.items():
                pattern_vectors = self.vectorizer.transform(patterns)
                similarities = cosine_similarity(text_vector, pattern_vectors)
                max_similarity = np.max(similarities)
                
                if max_similarity > best_score:
                    best_score = max_similarity
                    best_intent = intent
            
            return best_intent, float(best_score)
        
        except Exception as e:
            app_logger.error(f"Error in similarity-based matching: {e}")
            return None, 0.0
    
    def get_supported_intents(self) -> List[str]:
        """
        Get list of supported intents.
        
        Returns:
            List of intent names
        """
        return self.supported_intents
    
    def add_intent_pattern(self, intent: str, pattern: str):
        """
        Add new pattern for an intent.
        
        Args:
            intent: Intent name
            pattern: Pattern string
        """
        if intent not in self.intent_patterns:
            self.intent_patterns[intent] = []
        
        self.intent_patterns[intent].append(pattern.lower())
        app_logger.info(f"Added pattern for intent '{intent}': {pattern}")
        
        # Retrain vectorizer
        self._train_vectorizer()
