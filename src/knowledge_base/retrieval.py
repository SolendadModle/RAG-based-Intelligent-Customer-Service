"""
Retrieval Service - FAISS-based vector search for knowledge retrieval.
"""

import os
import pickle
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import faiss

from src.config import config_manager
from src.logger import app_logger
from src.knowledge_base.kb_manager import KnowledgeBase, Document
from src.knowledge_base.embeddings import DocumentEmbedder
from src.utils import ensure_directory


class RetrievalService:
    """FAISS-based retrieval service for knowledge base."""
    
    def __init__(self, knowledge_base: Optional[KnowledgeBase] = None):
        """
        Initialize retrieval service.
        
        Args:
            knowledge_base: Optional KnowledgeBase instance
        """
        self.config = config_manager.knowledge_base_config.get('retrieval', {})
        self.top_k = self.config.get('top_k', 5)
        self.similarity_threshold = self.config.get('similarity_threshold', 0.7)
        self.max_context_length = self.config.get('max_context_length', 2000)
        
        self.kb = knowledge_base or KnowledgeBase()
        self.embedder = DocumentEmbedder()
        
        self.index: Optional[faiss.IndexFlatIP] = None  # Inner Product (cosine similarity with normalized vectors)
        self.document_ids: List[str] = []
        
        self.vector_store_path = config_manager.settings.vector_store_path
        ensure_directory(self.vector_store_path)
        
        app_logger.info("Initialized Retrieval Service")
    
    def build_index(self, force_rebuild: bool = False):
        """
        Build FAISS index from knowledge base documents.
        
        Args:
            force_rebuild: Force rebuild even if index exists
        """
        index_file = os.path.join(self.vector_store_path, "faiss_index.bin")
        doc_ids_file = os.path.join(self.vector_store_path, "document_ids.pkl")
        
        # Try to load existing index
        if not force_rebuild and os.path.exists(index_file) and os.path.exists(doc_ids_file):
            try:
                self.load_index(index_file, doc_ids_file)
                app_logger.info("Loaded existing FAISS index")
                return
            except Exception as e:
                app_logger.warning(f"Failed to load existing index: {e}")
        
        # Build new index
        app_logger.info("Building new FAISS index...")
        
        # Load documents if not already loaded
        if not self.kb.documents:
            self.kb.load_documents()
        
        documents = self.kb.get_all_documents()
        
        if not documents:
            app_logger.warning("No documents to index")
            return
        
        # Generate embeddings
        app_logger.info(f"Generating embeddings for {len(documents)} documents...")
        embeddings = self.embedder.embed_documents(documents, show_progress=True)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product for normalized vectors = cosine similarity
        self.index.add(embeddings)
        
        # Store document IDs
        self.document_ids = [doc.doc_id for doc in documents]
        
        # Save index
        self.save_index(index_file, doc_ids_file)
        
        app_logger.info(f"Built FAISS index with {len(documents)} documents")
    
    def save_index(self, index_file: str, doc_ids_file: str):
        """
        Save FAISS index and document IDs to files.
        
        Args:
            index_file: Path to save FAISS index
            doc_ids_file: Path to save document IDs
        """
        try:
            faiss.write_index(self.index, index_file)
            with open(doc_ids_file, 'wb') as f:
                pickle.dump(self.document_ids, f)
            app_logger.info(f"Saved FAISS index to {index_file}")
        except Exception as e:
            app_logger.error(f"Error saving index: {e}")
    
    def load_index(self, index_file: str, doc_ids_file: str):
        """
        Load FAISS index and document IDs from files.
        
        Args:
            index_file: Path to FAISS index file
            doc_ids_file: Path to document IDs file
        """
        try:
            self.index = faiss.read_index(index_file)
            with open(doc_ids_file, 'rb') as f:
                self.document_ids = pickle.load(f)
            app_logger.info(f"Loaded FAISS index from {index_file}")
        except Exception as e:
            app_logger.error(f"Error loading index: {e}")
            raise
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Tuple[Document, float]]:
        """
        Retrieve relevant documents for query.
        
        Args:
            query: Query text
            top_k: Number of results to return (uses default if None)
            
        Returns:
            List of (Document, score) tuples
        """
        if self.index is None:
            app_logger.warning("Index not built. Building now...")
            self.build_index()
        
        if self.index is None or self.index.ntotal == 0:
            app_logger.warning("No documents in index")
            return []
        
        k = top_k or self.top_k
        
        # Generate query embedding
        query_embedding = self.embedder.embed_text(query)
        query_embedding = query_embedding.reshape(1, -1)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        # Get results
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx == -1:  # FAISS returns -1 for invalid indices
                continue
            
            # Apply similarity threshold
            if score < self.similarity_threshold:
                continue
            
            doc_id = self.document_ids[idx]
            document = self.kb.get_document(doc_id)
            
            if document:
                results.append((document, float(score)))
        
        app_logger.debug(f"Retrieved {len(results)} documents for query")
        return results
    
    def retrieve_context(self, query: str, top_k: Optional[int] = None) -> str:
        """
        Retrieve and format context for RAG.
        
        Args:
            query: Query text
            top_k: Number of results to retrieve
            
        Returns:
            Formatted context string
        """
        results = self.retrieve(query, top_k)
        
        if not results:
            return "No relevant context found."
        
        # Format context
        context_parts = []
        current_length = 0
        
        for doc, score in results:
            content = doc.content
            
            # Check if adding this document would exceed max length
            if current_length + len(content) > self.max_context_length:
                # Truncate if needed
                remaining = self.max_context_length - current_length
                if remaining > 100:  # Only add if we have reasonable space
                    content = content[:remaining] + "..."
                else:
                    break
            
            context_parts.append(f"[Relevance: {score:.3f}]\n{content}")
            current_length += len(content)
        
        context = "\n\n---\n\n".join(context_parts)
        return context
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Returns:
            Dictionary with index statistics
        """
        if self.index is None:
            return {'status': 'not_built'}
        
        return {
            'status': 'ready',
            'total_documents': self.index.ntotal,
            'dimension': self.index.d,
            'top_k': self.top_k,
            'similarity_threshold': self.similarity_threshold
        }
