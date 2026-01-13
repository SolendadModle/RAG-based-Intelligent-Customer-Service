"""
Entity Extraction Module for Natural Language Understanding.
"""

from typing import Dict, List, Optional, Tuple
import spacy
import re
from datetime import datetime

from src.config import config_manager
from src.logger import app_logger


class EntityExtractor:
    """Entity extraction using spaCy and custom patterns."""
    
    def __init__(self):
        """Initialize entity extractor."""
        self.config = config_manager.nlu_config.get('entity_extraction', {})
        self.enabled = self.config.get('enabled', True)
        self.entity_types = self.config.get('entities', [])
        
        # Load spaCy model with NER
        try:
            self.nlp = spacy.load(config_manager.settings.nlu_model)
            app_logger.info(f"Loaded spaCy model for entity extraction: {config_manager.settings.nlu_model}")
        except OSError:
            app_logger.warning(f"spaCy model not found. Using blank English model.")
            self.nlp = spacy.blank("en")
        
        # Custom entity patterns
        self.custom_patterns = self._load_custom_patterns()
    
    def _load_custom_patterns(self) -> Dict[str, List[str]]:
        """
        Load custom regex patterns for entity extraction.
        
        Returns:
            Dictionary mapping entity types to regex patterns
        """
        patterns = {
            "ORDER_ID": [
                r"\b[A-Z]{2,3}\d{6,10}\b",  # e.g., ORD12345678
                r"\b\d{8,12}\b",  # numeric order IDs
                r"#\d{6,10}",  # e.g., #12345678
            ],
            "EMAIL": [
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            ],
            "PHONE": [
                r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # e.g., 123-456-7890
                r"\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b",  # e.g., (123) 456-7890
            ],
            "PRODUCT_CODE": [
                r"\b[A-Z]{2,4}-\d{3,6}\b",  # e.g., PROD-12345
                r"\bSKU-?\d{4,8}\b",  # e.g., SKU12345678
            ],
            "URL": [
                r"https?://[^\s]+"
            ],
            "MONEY": [
                r"\$\d+(?:\.\d{2})?",  # e.g., $99.99
                r"\d+(?:\.\d{2})?\s*(?:dollars|USD|usd)",
            ],
            "DATE": [
                r"\d{1,2}/\d{1,2}/\d{2,4}",  # e.g., 12/31/2023
                r"\d{4}-\d{2}-\d{2}",  # e.g., 2023-12-31
                r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}",
            ]
        }
        return patterns
    
    def extract(self, text: str) -> Dict[str, List[Dict[str, any]]]:
        """
        Extract entities from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary mapping entity types to lists of extracted entities
        """
        if not self.enabled or not text:
            return {}
        
        entities = {}
        
        # Extract using spaCy NER
        spacy_entities = self._extract_with_spacy(text)
        entities.update(spacy_entities)
        
        # Extract using custom patterns
        custom_entities = self._extract_with_patterns(text)
        
        # Merge custom entities
        for entity_type, entity_list in custom_entities.items():
            if entity_type in entities:
                entities[entity_type].extend(entity_list)
            else:
                entities[entity_type] = entity_list
        
        # Remove duplicates
        for entity_type in entities:
            seen = set()
            unique_entities = []
            for entity in entities[entity_type]:
                entity_key = (entity['text'], entity['label'])
                if entity_key not in seen:
                    seen.add(entity_key)
                    unique_entities.append(entity)
            entities[entity_type] = unique_entities
        
        app_logger.debug(f"Extracted entities: {entities}")
        return entities
    
    def _extract_with_spacy(self, text: str) -> Dict[str, List[Dict[str, any]]]:
        """
        Extract entities using spaCy NER.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                # Filter by configured entity types if specified
                if self.entity_types and ent.label_ not in self.entity_types:
                    continue
                
                entity_info = {
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 1.0  # spaCy doesn't provide confidence scores by default
                }
                
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(entity_info)
        
        except Exception as e:
            app_logger.error(f"Error in spaCy entity extraction: {e}")
        
        return entities
    
    def _extract_with_patterns(self, text: str) -> Dict[str, List[Dict[str, any]]]:
        """
        Extract entities using custom regex patterns.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        for entity_type, patterns in self.custom_patterns.items():
            # Filter by configured entity types if specified
            if self.entity_types and entity_type not in self.entity_types:
                continue
            
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        entity_info = {
                            'text': match.group(),
                            'label': entity_type,
                            'start': match.start(),
                            'end': match.end(),
                            'confidence': 0.95  # High confidence for pattern matches
                        }
                        
                        if entity_type not in entities:
                            entities[entity_type] = []
                        entities[entity_type].append(entity_info)
                
                except Exception as e:
                    app_logger.error(f"Error in pattern matching for {entity_type}: {e}")
        
        return entities
    
    def extract_specific_entity(self, text: str, entity_type: str) -> List[Dict[str, any]]:
        """
        Extract specific entity type from text.
        
        Args:
            text: Input text
            entity_type: Type of entity to extract
            
        Returns:
            List of extracted entities of specified type
        """
        all_entities = self.extract(text)
        return all_entities.get(entity_type, [])
    
    def get_supported_entities(self) -> List[str]:
        """
        Get list of supported entity types.
        
        Returns:
            List of entity type names
        """
        return self.entity_types
    
    def add_custom_pattern(self, entity_type: str, pattern: str):
        """
        Add custom pattern for entity extraction.
        
        Args:
            entity_type: Type of entity
            pattern: Regex pattern
        """
        if entity_type not in self.custom_patterns:
            self.custom_patterns[entity_type] = []
        
        self.custom_patterns[entity_type].append(pattern)
        app_logger.info(f"Added custom pattern for entity type '{entity_type}': {pattern}")


class NLUService:
    """Combined NLU service for intent recognition and entity extraction."""
    
    def __init__(self):
        """Initialize NLU service."""
        self.intent_recognizer = IntentRecognizer()
        self.entity_extractor = EntityExtractor()
        app_logger.info("Initialized NLU service")
    
    def analyze(self, text: str) -> Dict[str, any]:
        """
        Analyze text for intent and entities.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing intent and entities
        """
        # Recognize intent
        intent, confidence = self.intent_recognizer.recognize(text)
        
        # Extract entities
        entities = self.entity_extractor.extract(text)
        
        result = {
            'text': text,
            'intent': {
                'name': intent,
                'confidence': confidence
            },
            'entities': entities
        }
        
        app_logger.info(f"NLU analysis - Intent: {intent} ({confidence:.3f}), Entities: {len(entities)} types")
        return result
