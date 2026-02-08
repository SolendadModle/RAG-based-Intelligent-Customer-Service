"""
Cache management for the RAG Customer Service System.
Provides caching capabilities for API responses, embeddings, and retrievals.
"""

import time
import hashlib
import pickle
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
from collections import OrderedDict
import threading

from src.logger import app_logger


class CacheEntry:
    """Represents a single cache entry."""
    
    def __init__(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Initialize cache entry.
        
        Args:
            key: Cache key
            value: Cached value
            ttl: Time to live in seconds
        """
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl is None:
            return False
        return (time.time() - self.created_at) > self.ttl
    
    def access(self):
        """Record access to this entry."""
        self.access_count += 1
        self.last_accessed = time.time()


class LRUCache:
    """Least Recently Used (LRU) cache implementation."""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = 3600):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default time to live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.Lock()
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        app_logger.info(f"Initialized LRU Cache (max_size={max_size}, ttl={default_ttl}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry.access()
            
            self.hits += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live (uses default if None)
        """
        with self.lock:
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl
            
            # Remove oldest entry if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                self.cache.popitem(last=False)
                self.evictions += 1
            
            # Add or update entry
            entry = CacheEntry(key, value, ttl)
            self.cache[key] = entry
            self.cache.move_to_end(key)
    
    def delete(self, key: str) -> bool:
        """
        Delete entry from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            app_logger.info("Cleared cache")
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries.
        
        Returns:
            Number of entries removed
        """
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            if expired_keys:
                app_logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'evictions': self.evictions
            }


class ResponseCache:
    """Cache for API responses."""
    
    def __init__(self, cache: Optional[LRUCache] = None):
        """
        Initialize response cache.
        
        Args:
            cache: Optional LRUCache instance
        """
        self.cache = cache or LRUCache(max_size=1000, default_ttl=3600)
        app_logger.info("Initialized Response Cache")
    
    def get_response(self, query: str, use_rag: bool = True) -> Optional[str]:
        """
        Get cached response for query.
        
        Args:
            query: User query
            use_rag: Whether RAG was used
            
        Returns:
            Cached response or None
        """
        key = self._generate_key(query, use_rag)
        return self.cache.get(key)
    
    def set_response(self, query: str, response: str, use_rag: bool = True, ttl: Optional[int] = None):
        """
        Cache response for query.
        
        Args:
            query: User query
            response: Generated response
            use_rag: Whether RAG was used
            ttl: Time to live
        """
        key = self._generate_key(query, use_rag)
        self.cache.set(key, response, ttl)
    
    def _generate_key(self, query: str, use_rag: bool) -> str:
        """Generate cache key."""
        content = f"{query}|{use_rag}"
        return hashlib.md5(content.encode()).hexdigest()


class EmbeddingCache:
    """Cache for text embeddings."""
    
    def __init__(self, cache: Optional[LRUCache] = None):
        """
        Initialize embedding cache.
        
        Args:
            cache: Optional LRUCache instance
        """
        self.cache = cache or LRUCache(max_size=5000, default_ttl=7200)
        app_logger.info("Initialized Embedding Cache")
    
    def get_embedding(self, text: str) -> Optional[Any]:
        """
        Get cached embedding for text.
        
        Args:
            text: Input text
            
        Returns:
            Cached embedding or None
        """
        key = self._generate_key(text)
        return self.cache.get(key)
    
    def set_embedding(self, text: str, embedding: Any, ttl: Optional[int] = None):
        """
        Cache embedding for text.
        
        Args:
            text: Input text
            embedding: Embedding vector
            ttl: Time to live
        """
        key = self._generate_key(text)
        self.cache.set(key, embedding, ttl)
    
    def _generate_key(self, text: str) -> str:
        """Generate cache key."""
        return hashlib.md5(text.encode()).hexdigest()


class RetrievalCache:
    """Cache for retrieval results."""
    
    def __init__(self, cache: Optional[LRUCache] = None):
        """
        Initialize retrieval cache.
        
        Args:
            cache: Optional LRUCache instance
        """
        self.cache = cache or LRUCache(max_size=2000, default_ttl=1800)
        app_logger.info("Initialized Retrieval Cache")
    
    def get_results(self, query: str, top_k: int = 5) -> Optional[Any]:
        """
        Get cached retrieval results.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            Cached results or None
        """
        key = self._generate_key(query, top_k)
        return self.cache.get(key)
    
    def set_results(self, query: str, results: Any, top_k: int = 5, ttl: Optional[int] = None):
        """
        Cache retrieval results.
        
        Args:
            query: Search query
            results: Retrieval results
            top_k: Number of results
            ttl: Time to live
        """
        key = self._generate_key(query, top_k)
        self.cache.set(key, results, ttl)
    
    def _generate_key(self, query: str, top_k: int) -> str:
        """Generate cache key."""
        content = f"{query}|{top_k}"
        return hashlib.md5(content.encode()).hexdigest()


def cached(ttl: Optional[int] = None, cache_instance: Optional[LRUCache] = None):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds
        cache_instance: Optional cache instance to use
        
    Returns:
        Decorated function
    """
    if cache_instance is None:
        cache_instance = LRUCache()
    
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key = hashlib.md5('|'.join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            result = cache_instance.get(key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache_instance.set(key, result, ttl)
            return result
        
        return wrapper
    return decorator


class CacheManager:
    """Manage multiple cache instances."""
    
    def __init__(self):
        """Initialize cache manager."""
        self.response_cache = ResponseCache()
        self.embedding_cache = EmbeddingCache()
        self.retrieval_cache = RetrievalCache()
        
        app_logger.info("Initialized Cache Manager")
    
    def get_all_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all caches.
        
        Returns:
            Dictionary with all cache statistics
        """
        return {
            'response_cache': self.response_cache.cache.get_stats(),
            'embedding_cache': self.embedding_cache.cache.get_stats(),
            'retrieval_cache': self.retrieval_cache.cache.get_stats()
        }
    
    def cleanup_all(self):
        """Cleanup expired entries in all caches."""
        total_cleaned = 0
        total_cleaned += self.response_cache.cache.cleanup_expired()
        total_cleaned += self.embedding_cache.cache.cleanup_expired()
        total_cleaned += self.retrieval_cache.cache.cleanup_expired()
        
        if total_cleaned > 0:
            app_logger.info(f"Cleaned up {total_cleaned} total expired entries across all caches")
        
        return total_cleaned
    
    def clear_all(self):
        """Clear all caches."""
        self.response_cache.cache.clear()
        self.embedding_cache.cache.clear()
        self.retrieval_cache.cache.clear()
        app_logger.info("Cleared all caches")


# Global cache manager instance
cache_manager = CacheManager()
