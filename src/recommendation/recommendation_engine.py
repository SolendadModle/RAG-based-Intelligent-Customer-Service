"""
Recommendation Engine - Provide personalized recommendations.
"""

from typing import List, Dict, Optional, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.config import config_manager
from src.logger import app_logger
from src.knowledge_base.embeddings import DocumentEmbedder


class RecommendationEngine:
    """Recommendation engine for products, services, and solutions."""
    
    def __init__(self):
        """Initialize recommendation engine."""
        self.config = config_manager.recommendation_config
        self.enabled = self.config.get('enabled', True)
        self.max_recommendations = config_manager.settings.max_recommendations
        self.similarity_threshold = config_manager.settings.recommendation_threshold
        self.categories = self.config.get('categories', [])
        
        self.embedder = DocumentEmbedder()
        
        # Recommendation catalog
        self.catalog = self._load_catalog()
        self.catalog_embeddings = None
        
        if self.enabled and self.catalog:
            self._build_embeddings()
        
        app_logger.info("Initialized Recommendation Engine")
    
    def _load_catalog(self) -> List[Dict[str, Any]]:
        """
        Load recommendation catalog.
        
        Returns:
            List of catalog items
        """
        # Default catalog - in production, this would be loaded from a database
        catalog = [
            {
                'id': 'prod_001',
                'name': 'Premium Support Plan',
                'category': 'services',
                'description': 'Get 24/7 priority support with dedicated account manager and faster response times.',
                'tags': ['support', 'premium', 'priority']
            },
            {
                'id': 'prod_002',
                'name': 'Enterprise Cloud Solution',
                'category': 'products',
                'description': 'Scalable cloud infrastructure with advanced security and compliance features.',
                'tags': ['cloud', 'enterprise', 'scalable']
            },
            {
                'id': 'sol_001',
                'name': 'Data Migration Service',
                'category': 'solutions',
                'description': 'Professional data migration service with zero downtime and data integrity guarantee.',
                'tags': ['migration', 'data', 'professional']
            },
            {
                'id': 'prod_003',
                'name': 'AI-Powered Analytics',
                'category': 'products',
                'description': 'Advanced analytics platform with machine learning capabilities for business insights.',
                'tags': ['analytics', 'ai', 'insights']
            },
            {
                'id': 'res_001',
                'name': 'Integration Guide',
                'category': 'resources',
                'description': 'Step-by-step guide for integrating our services with your existing systems.',
                'tags': ['integration', 'guide', 'documentation']
            },
            {
                'id': 'prod_004',
                'name': 'API Gateway',
                'category': 'products',
                'description': 'Secure and scalable API gateway for managing your API ecosystem.',
                'tags': ['api', 'gateway', 'security']
            },
            {
                'id': 'sol_002',
                'name': 'Performance Optimization',
                'category': 'solutions',
                'description': 'Expert consultation to optimize system performance and reduce costs.',
                'tags': ['performance', 'optimization', 'consultation']
            },
            {
                'id': 'serv_001',
                'name': 'Training Workshop',
                'category': 'services',
                'description': 'Comprehensive training program for your team on our platform and best practices.',
                'tags': ['training', 'workshop', 'education']
            }
        ]
        return catalog
    
    def _build_embeddings(self):
        """Build embeddings for catalog items."""
        try:
            texts = [f"{item['name']} {item['description']}" for item in self.catalog]
            self.catalog_embeddings = self.embedder.embed_texts(texts)
            app_logger.info(f"Built embeddings for {len(self.catalog)} catalog items")
        except Exception as e:
            app_logger.error(f"Error building catalog embeddings: {e}")
    
    def recommend(self, query: str, category: Optional[str] = None,
                  context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get recommendations based on query.
        
        Args:
            query: User query or context
            category: Optional category filter
            context: Optional additional context
            
        Returns:
            List of recommended items
        """
        if not self.enabled or not self.catalog:
            return []
        
        try:
            # Filter by category if specified
            filtered_catalog = self.catalog
            if category and category in self.categories:
                filtered_catalog = [
                    item for item in self.catalog
                    if item['category'] == category
                ]
            
            if not filtered_catalog:
                return []
            
            # Generate query embedding
            query_embedding = self.embedder.embed_text(query)
            
            # Get embeddings for filtered catalog
            if category:
                indices = [i for i, item in enumerate(self.catalog) if item in filtered_catalog]
                catalog_embeddings = self.catalog_embeddings[indices]
            else:
                catalog_embeddings = self.catalog_embeddings
            
            # Calculate similarities
            similarities = cosine_similarity([query_embedding], catalog_embeddings)[0]
            
            # Get top recommendations
            top_indices = np.argsort(similarities)[::-1][:self.max_recommendations]
            
            recommendations = []
            for idx in top_indices:
                similarity = similarities[idx]
                
                # Apply threshold
                if similarity < self.similarity_threshold:
                    continue
                
                if category:
                    catalog_idx = indices[idx]
                else:
                    catalog_idx = idx
                
                item = self.catalog[catalog_idx].copy()
                item['relevance_score'] = float(similarity)
                recommendations.append(item)
            
            app_logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
        
        except Exception as e:
            app_logger.error(f"Error generating recommendations: {e}")
            return []
    
    def recommend_by_intent(self, intent: str, entities: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Get recommendations based on detected intent.
        
        Args:
            intent: Detected user intent
            entities: Extracted entities
            
        Returns:
            List of recommended items
        """
        # Map intents to recommendation categories
        intent_mapping = {
            'product_inquiry': 'products',
            'technical_support': 'solutions',
            'billing_inquiry': 'services',
            'general_question': 'resources'
        }
        
        category = intent_mapping.get(intent)
        query = intent.replace('_', ' ')
        
        return self.recommend(query, category=category)
    
    def recommend_based_on_history(self, conversation_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get recommendations based on conversation history.
        
        Args:
            conversation_history: List of conversation messages
            
        Returns:
            List of recommended items
        """
        if not conversation_history:
            return []
        
        # Combine recent user messages
        user_messages = [
            msg['content'] for msg in conversation_history[-5:]
            if msg.get('role') == 'user'
        ]
        
        combined_query = ' '.join(user_messages)
        return self.recommend(combined_query)
    
    def get_popular_items(self, category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get popular/featured items.
        
        Args:
            category: Optional category filter
            limit: Maximum number of items
            
        Returns:
            List of popular items
        """
        filtered_catalog = self.catalog
        
        if category:
            filtered_catalog = [
                item for item in self.catalog
                if item['category'] == category
            ]
        
        # In production, this would be based on actual popularity metrics
        return filtered_catalog[:limit]
    
    def add_catalog_item(self, item: Dict[str, Any]):
        """
        Add item to catalog.
        
        Args:
            item: Catalog item
        """
        self.catalog.append(item)
        # Rebuild embeddings
        if self.enabled:
            self._build_embeddings()
        app_logger.info(f"Added catalog item: {item['id']}")
