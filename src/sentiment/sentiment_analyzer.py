"""
Sentiment Analysis Module - Analyze user sentiment and emotions.
"""

from typing import Dict, Optional, Tuple
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

from src.config import config_manager
from src.logger import app_logger


class SentimentAnalyzer:
    """Sentiment analysis using transformer models."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.config = config_manager.sentiment_config
        self.enabled = self.config.get('enabled', True)
        self.model_name = config_manager.settings.sentiment_model
        self.threshold = self.config.get('threshold', {})
        
        self.analyzer = None
        if self.enabled:
            self._load_model()
    
    def _load_model(self):
        """Load sentiment analysis model."""
        try:
            app_logger.info(f"Loading sentiment model: {self.model_name}")
            self.analyzer = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            app_logger.info("Sentiment model loaded successfully")
        except Exception as e:
            app_logger.error(f"Error loading sentiment model: {e}")
            self.enabled = False
    
    def analyze(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not self.enabled or not text:
            return {
                'label': 'neutral',
                'score': 0.5,
                'enabled': False
            }
        
        try:
            result = self.analyzer(text[:512])[0]  # Limit text length
            
            label = result['label'].lower()
            score = result['score']
            
            # Normalize labels
            if 'positive' in label:
                sentiment = 'positive'
            elif 'negative' in label:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Determine intensity
            intensity = 'low'
            if sentiment == 'positive':
                pos_threshold = self.threshold.get('positive', 0.7)
                if score >= pos_threshold:
                    intensity = 'high'
            elif sentiment == 'negative':
                neg_threshold = self.threshold.get('negative', 0.6)
                if score >= neg_threshold:
                    intensity = 'high'
            
            result_dict = {
                'sentiment': sentiment,
                'score': score,
                'intensity': intensity,
                'enabled': True
            }
            
            app_logger.debug(f"Sentiment analysis: {sentiment} ({score:.3f})")
            return result_dict
        
        except Exception as e:
            app_logger.error(f"Error in sentiment analysis: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.5,
                'intensity': 'low',
                'error': str(e)
            }
    
    def should_escalate(self, text: str) -> Tuple[bool, str]:
        """
        Determine if conversation should be escalated based on sentiment.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (should_escalate, reason)
        """
        if not self.enabled:
            return False, ""
        
        escalation_config = self.config.get('escalation', {})
        if not escalation_config.get('enabled', True):
            return False, ""
        
        # Analyze sentiment
        sentiment_result = self.analyze(text)
        
        # Check negative sentiment threshold
        if sentiment_result['sentiment'] == 'negative':
            neg_threshold = escalation_config.get('negative_threshold', 0.8)
            if sentiment_result['score'] >= neg_threshold:
                return True, f"High negative sentiment detected (score: {sentiment_result['score']:.2f})"
        
        # Check urgency keywords
        urgency_keywords = escalation_config.get('urgency_keywords', [])
        text_lower = text.lower()
        for keyword in urgency_keywords:
            if keyword in text_lower:
                return True, f"Urgency keyword detected: '{keyword}'"
        
        return False, ""
    
    def get_emotion_summary(self, conversation_history: list) -> Dict[str, any]:
        """
        Get emotion summary for conversation history.
        
        Args:
            conversation_history: List of conversation messages
            
        Returns:
            Dictionary with emotion summary
        """
        if not self.enabled or not conversation_history:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_trend': 'stable',
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        sentiments = []
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for message in conversation_history:
            if message.get('role') == 'user':
                content = message.get('content', '')
                result = self.analyze(content)
                sentiment = result['sentiment']
                sentiments.append(sentiment)
                sentiment_counts[sentiment] += 1
        
        # Determine overall sentiment
        if not sentiments:
            overall = 'neutral'
        else:
            max_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            overall = max_sentiment
        
        # Determine trend
        if len(sentiments) >= 3:
            recent = sentiments[-3:]
            if recent.count('negative') >= 2:
                trend = 'declining'
            elif recent.count('positive') >= 2:
                trend = 'improving'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'overall_sentiment': overall,
            'sentiment_trend': trend,
            'positive_count': sentiment_counts['positive'],
            'negative_count': sentiment_counts['negative'],
            'neutral_count': sentiment_counts['neutral']
        }
