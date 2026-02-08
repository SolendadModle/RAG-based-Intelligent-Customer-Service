"""
Unit tests for knowledge base and retrieval.
"""

import pytest
import numpy as np
from src.knowledge_base.kb_manager import KnowledgeBase, Document
from src.knowledge_base.embeddings import DocumentEmbedder
from src.knowledge_base.retrieval import RetrievalService


class TestDocument:
    """Test Document class."""
    
    def test_document_creation(self):
        """Test document creation."""
        doc = Document(content="Test content", metadata={'type': 'test'})
        assert doc.content == "Test content"
        assert doc.metadata['type'] == 'test'
        assert doc.doc_id is not None
    
    def test_document_to_dict(self):
        """Test document serialization."""
        doc = Document(content="Test", metadata={'key': 'value'})
        doc_dict = doc.to_dict()
        assert 'doc_id' in doc_dict
        assert 'content' in doc_dict
        assert 'metadata' in doc_dict
    
    def test_document_from_dict(self):
        """Test document deserialization."""
        data = {
            'content': 'Test content',
            'metadata': {'type': 'test'},
            'doc_id': 'test123'
        }
        doc = Document.from_dict(data)
        assert doc.content == 'Test content'
        assert doc.doc_id == 'test123'


class TestKnowledgeBase:
    """Test KnowledgeBase functionality."""
    
    @pytest.fixture
    def kb(self):
        """Create knowledge base instance."""
        return KnowledgeBase()
    
    def test_add_document(self, kb):
        """Test adding document to knowledge base."""
        doc = Document(content="Test document")
        kb.add_document(doc)
        assert len(kb.documents) == 1
        assert doc.doc_id in kb.document_index
    
    def test_get_document(self, kb):
        """Test retrieving document by ID."""
        doc = Document(content="Test document")
        kb.add_document(doc)
        retrieved = kb.get_document(doc.doc_id)
        assert retrieved is not None
        assert retrieved.content == doc.content
    
    def test_keyword_search(self, kb):
        """Test keyword search."""
        doc1 = Document(content="Python programming tutorial")
        doc2 = Document(content="Java development guide")
        kb.add_document(doc1)
        kb.add_document(doc2)
        
        results = kb.search_by_keyword("Python")
        assert len(results) == 1
        assert results[0].content == doc1.content


class TestDocumentEmbedder:
    """Test DocumentEmbedder functionality."""
    
    @pytest.fixture
    def embedder(self):
        """Create document embedder instance."""
        return DocumentEmbedder()
    
    def test_embed_text(self, embedder):
        """Test single text embedding."""
        text = "This is a test sentence"
        embedding = embedder.embed_text(text)
        assert isinstance(embedding, np.ndarray)
        assert len(embedding.shape) == 1
        assert embedding.shape[0] > 0
    
    def test_embed_multiple_texts(self, embedder):
        """Test multiple text embeddings."""
        texts = ["First sentence", "Second sentence", "Third sentence"]
        embeddings = embedder.embed_texts(texts)
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 3
        assert embeddings.shape[1] > 0
    
    def test_embed_document(self, embedder):
        """Test document embedding."""
        doc = Document(content="Test document content")
        embedding = embedder.embed_document(doc)
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] > 0


class TestRetrievalService:
    """Test RetrievalService functionality."""
    
    @pytest.fixture
    def retrieval_service(self):
        """Create retrieval service instance."""
        kb = KnowledgeBase()
        # Add test documents
        kb.add_document(Document(content="Python is a programming language", metadata={'topic': 'programming'}))
        kb.add_document(Document(content="Machine learning uses algorithms", metadata={'topic': 'ml'}))
        kb.add_document(Document(content="Web development with JavaScript", metadata={'topic': 'web'}))
        
        service = RetrievalService(knowledge_base=kb)
        service.build_index()
        return service
    
    def test_build_index(self, retrieval_service):
        """Test index building."""
        assert retrieval_service.index is not None
        assert retrieval_service.index.ntotal > 0
    
    def test_retrieve(self, retrieval_service):
        """Test document retrieval."""
        results = retrieval_service.retrieve("programming language", top_k=2)
        assert isinstance(results, list)
        assert len(results) <= 2
        if results:
            doc, score = results[0]
            assert isinstance(doc, Document)
            assert isinstance(score, float)
    
    def test_retrieve_context(self, retrieval_service):
        """Test context retrieval."""
        context = retrieval_service.retrieve_context("machine learning")
        assert isinstance(context, str)
        assert len(context) > 0
