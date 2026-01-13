"""
Document Embedding Module - Convert documents to vector embeddings.
"""

import os
import pickle
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import config_manager
from src.logger import app_logger
from src.knowledge_base.kb_manager import Document
from src.utils import ensure_directory


class DocumentEmbedder:
    """Generate embeddings for documents using sentence transformers."""
    
    def __init__(self):
        """Initialize document embedder."""
        self.config = config_manager.knowledge_base_config.get('embedding', {})
        self.model_name = config_manager.settings.embedding_model
        self.dimension = self.config.get('dimension', 384)
        self.batch_size = self.config.get('batch_size', 32)
        
        # Load embedding model
        app_logger.info(f"Loading embedding model: {self.model_name}")
        try:
            self.model = SentenceTransformer(self.model_name)
            app_logger.info(f"Loaded embedding model successfully")
        except Exception as e:
            app_logger.error(f"Error loading embedding model: {e}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            app_logger.error(f"Error generating embedding: {e}")
            return np.zeros(self.dimension)
    
    def embed_texts(self, texts: List[str], show_progress: bool = False) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            show_progress: Whether to show progress bar
            
        Returns:
            Array of embedding vectors
        """
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            return embeddings
        except Exception as e:
            app_logger.error(f"Error generating embeddings: {e}")
            return np.zeros((len(texts), self.dimension))
    
    def embed_document(self, document: Document) -> np.ndarray:
        """
        Generate embedding for document.
        
        Args:
            document: Document object
            
        Returns:
            Embedding vector
        """
        return self.embed_text(document.content)
    
    def embed_documents(self, documents: List[Document], show_progress: bool = False) -> np.ndarray:
        """
        Generate embeddings for multiple documents.
        
        Args:
            documents: List of Document objects
            show_progress: Whether to show progress bar
            
        Returns:
            Array of embedding vectors
        """
        texts = [doc.content for doc in documents]
        return self.embed_texts(texts, show_progress=show_progress)
    
    def save_embeddings(self, embeddings: np.ndarray, file_path: str):
        """
        Save embeddings to file.
        
        Args:
            embeddings: Embedding array
            file_path: Path to save embeddings
        """
        try:
            ensure_directory(os.path.dirname(file_path))
            with open(file_path, 'wb') as f:
                pickle.dump(embeddings, f)
            app_logger.info(f"Saved embeddings to {file_path}")
        except Exception as e:
            app_logger.error(f"Error saving embeddings: {e}")
    
    def load_embeddings(self, file_path: str) -> Optional[np.ndarray]:
        """
        Load embeddings from file.
        
        Args:
            file_path: Path to embeddings file
            
        Returns:
            Embedding array if successful, None otherwise
        """
        try:
            if not os.path.exists(file_path):
                app_logger.warning(f"Embeddings file not found: {file_path}")
                return None
            
            with open(file_path, 'rb') as f:
                embeddings = pickle.load(f)
            app_logger.info(f"Loaded embeddings from {file_path}")
            return embeddings
        except Exception as e:
            app_logger.error(f"Error loading embeddings: {e}")
            return None
    
    def get_embedding_dimension(self) -> int:
        """
        Get embedding dimension.
        
        Returns:
            Embedding dimension
        """
        return self.model.get_sentence_embedding_dimension()
