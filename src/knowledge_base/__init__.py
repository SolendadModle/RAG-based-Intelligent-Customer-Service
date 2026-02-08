"""
Knowledge Base Module - Document management and retrieval.
"""

from src.knowledge_base.kb_manager import KnowledgeBase, Document
from src.knowledge_base.embeddings import DocumentEmbedder
from src.knowledge_base.retrieval import RetrievalService

__all__ = ['KnowledgeBase', 'Document', 'DocumentEmbedder', 'RetrievalService']
