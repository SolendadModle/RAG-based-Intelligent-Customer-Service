"""
Unit tests for NLU module.
"""

import pytest
from src.nlu.intent_recognition import IntentRecognizer
from src.nlu.entity_extraction import EntityExtractor, NLUService


class TestIntentRecognizer:
    """Test intent recognition functionality."""
    
    @pytest.fixture
    def recognizer(self):
        """Create intent recognizer instance."""
        return IntentRecognizer()
    
    def test_greeting_intent(self, recognizer):
        """Test greeting intent recognition."""
        text = "Hello, how are you?"
        intent, confidence = recognizer.recognize(text)
        assert intent == "greeting"
        assert confidence > 0.7
    
    def test_product_inquiry_intent(self, recognizer):
        """Test product inquiry intent."""
        text = "Tell me about your products"
        intent, confidence = recognizer.recognize(text)
        assert intent == "product_inquiry"
        assert confidence > 0.5
    
    def test_technical_support_intent(self, recognizer):
        """Test technical support intent."""
        text = "I'm having a technical issue with my account"
        intent, confidence = recognizer.recognize(text)
        assert intent == "technical_support"
        assert confidence > 0.5
    
    def test_empty_text(self, recognizer):
        """Test empty text handling."""
        intent, confidence = recognizer.recognize("")
        assert intent is None
        assert confidence == 0.0


class TestEntityExtractor:
    """Test entity extraction functionality."""
    
    @pytest.fixture
    def extractor(self):
        """Create entity extractor instance."""
        return EntityExtractor()
    
    def test_email_extraction(self, extractor):
        """Test email entity extraction."""
        text = "Please contact me at john.doe@example.com"
        entities = extractor.extract(text)
        assert 'EMAIL' in entities
        assert len(entities['EMAIL']) > 0
        assert 'john.doe@example.com' in entities['EMAIL'][0]['text']
    
    def test_order_id_extraction(self, extractor):
        """Test order ID extraction."""
        text = "My order number is ORD12345678"
        entities = extractor.extract(text)
        assert 'ORDER_ID' in entities
        assert len(entities['ORDER_ID']) > 0
    
    def test_no_entities(self, extractor):
        """Test text with no entities."""
        text = "Hello how are you"
        entities = extractor.extract(text)
        # Should return empty dict or dict with empty lists
        assert isinstance(entities, dict)


class TestNLUService:
    """Test combined NLU service."""
    
    @pytest.fixture
    def nlu_service(self):
        """Create NLU service instance."""
        return NLUService()
    
    def test_analyze(self, nlu_service):
        """Test full NLU analysis."""
        text = "I have a problem with order ORD12345678"
        result = nlu_service.analyze(text)
        
        assert 'text' in result
        assert 'intent' in result
        assert 'entities' in result
        assert result['intent']['name'] is not None
        assert isinstance(result['intent']['confidence'], float)
