"""
Knowledge Base Module - Document loading and management.
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np

from src.config import config_manager
from src.logger import app_logger
from src.utils import load_json_file, ensure_directory


class Document:
    """Represents a document in the knowledge base."""
    
    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None, doc_id: Optional[str] = None):
        """
        Initialize document.
        
        Args:
            content: Document content/text
            metadata: Optional metadata dictionary
            doc_id: Optional document ID
        """
        self.content = content
        self.metadata = metadata or {}
        self.doc_id = doc_id or self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique document ID based on content hash."""
        import hashlib
        return hashlib.md5(self.content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        return {
            'doc_id': self.doc_id,
            'content': self.content,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create document from dictionary."""
        return cls(
            content=data['content'],
            metadata=data.get('metadata', {}),
            doc_id=data.get('doc_id')
        )


class KnowledgeBase:
    """Manage knowledge base documents."""
    
    def __init__(self):
        """Initialize knowledge base."""
        self.config = config_manager.knowledge_base_config
        self.kb_path = config_manager.settings.knowledge_base_path
        ensure_directory(self.kb_path)
        
        self.documents: List[Document] = []
        self.document_index: Dict[str, Document] = {}
        
        app_logger.info("Initialized Knowledge Base")
    
    def load_documents(self):
        """Load all documents from configured sources."""
        sources = self.config.get('sources', [])
        
        for source in sources:
            source_type = source.get('type')
            source_path = source.get('path')
            
            if source_type == 'faq':
                self._load_faq(source_path)
            elif source_type == 'documents':
                self._load_documents_directory(source_path)
            else:
                app_logger.warning(f"Unknown source type: {source_type}")
        
        app_logger.info(f"Loaded {len(self.documents)} documents into knowledge base")
    
    def _load_faq(self, faq_path: str):
        """
        Load FAQ documents from JSON file.
        
        Args:
            faq_path: Path to FAQ JSON file
        """
        if not os.path.exists(faq_path):
            app_logger.warning(f"FAQ file not found: {faq_path}")
            return
        
        try:
            faq_data = load_json_file(faq_path)
            
            for item in faq_data:
                question = item.get('question', '')
                answer = item.get('answer', '')
                category = item.get('category', 'general')
                
                # Create document from FAQ item
                content = f"Q: {question}\nA: {answer}"
                metadata = {
                    'type': 'faq',
                    'category': category,
                    'question': question,
                    'answer': answer
                }
                
                doc = Document(content=content, metadata=metadata)
                self.add_document(doc)
            
            app_logger.info(f"Loaded {len(faq_data)} FAQ items")
        
        except Exception as e:
            app_logger.error(f"Error loading FAQ file: {e}")
    
    def _load_documents_directory(self, dir_path: str):
        """
        Load documents from directory.
        
        Args:
            dir_path: Path to documents directory
        """
        if not os.path.exists(dir_path):
            app_logger.warning(f"Documents directory not found: {dir_path}")
            return
        
        try:
            # Load .txt and .json files
            for file_path in Path(dir_path).rglob('*'):
                if file_path.is_file():
                    if file_path.suffix == '.txt':
                        self._load_text_file(str(file_path))
                    elif file_path.suffix == '.json':
                        self._load_json_document(str(file_path))
        
        except Exception as e:
            app_logger.error(f"Error loading documents directory: {e}")
    
    def _load_text_file(self, file_path: str):
        """Load plain text file as document."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {
                'type': 'text',
                'source_file': file_path,
                'filename': os.path.basename(file_path)
            }
            
            doc = Document(content=content, metadata=metadata)
            self.add_document(doc)
        
        except Exception as e:
            app_logger.error(f"Error loading text file {file_path}: {e}")
    
    def _load_json_document(self, file_path: str):
        """Load JSON document file."""
        try:
            data = load_json_file(file_path)
            
            if isinstance(data, list):
                for item in data:
                    self._process_json_item(item, file_path)
            else:
                self._process_json_item(data, file_path)
        
        except Exception as e:
            app_logger.error(f"Error loading JSON document {file_path}: {e}")
    
    def _process_json_item(self, item: Dict[str, Any], source_file: str):
        """Process single JSON item as document."""
        content = item.get('content') or item.get('text') or str(item)
        metadata = {
            'type': 'json',
            'source_file': source_file,
            **{k: v for k, v in item.items() if k not in ['content', 'text']}
        }
        
        doc = Document(content=content, metadata=metadata)
        self.add_document(doc)
    
    def add_document(self, document: Document):
        """
        Add document to knowledge base.
        
        Args:
            document: Document to add
        """
        self.documents.append(document)
        self.document_index[document.doc_id] = document
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """
        Get document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document if found, None otherwise
        """
        return self.document_index.get(doc_id)
    
    def get_all_documents(self) -> List[Document]:
        """Get all documents."""
        return self.documents
    
    def search_by_keyword(self, keyword: str, top_k: int = 5) -> List[Document]:
        """
        Simple keyword search in documents.
        
        Args:
            keyword: Search keyword
            top_k: Number of top results to return
            
        Returns:
            List of matching documents
        """
        keyword_lower = keyword.lower()
        results = []
        
        for doc in self.documents:
            if keyword_lower in doc.content.lower():
                results.append(doc)
        
        return results[:top_k]
    
    def get_documents_by_category(self, category: str) -> List[Document]:
        """
        Get documents by category.
        
        Args:
            category: Category name
            
        Returns:
            List of documents in category
        """
        return [doc for doc in self.documents 
                if doc.metadata.get('category') == category]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_documents': len(self.documents),
            'document_types': {},
            'categories': {}
        }
        
        for doc in self.documents:
            doc_type = doc.metadata.get('type', 'unknown')
            stats['document_types'][doc_type] = stats['document_types'].get(doc_type, 0) + 1
            
            category = doc.metadata.get('category')
            if category:
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
        
        return stats
