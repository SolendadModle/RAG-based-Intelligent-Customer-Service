"""
Advanced monitoring and metrics collection for the RAG Customer Service System.
"""

import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from dataclasses import dataclass, asdict

from src.logger import app_logger


@dataclass
class MetricData:
    """Represents a single metric data point."""
    timestamp: datetime
    value: float
    tags: Dict[str, str]


class MetricsCollector:
    """Collect and aggregate system metrics."""
    
    def __init__(self, retention_hours: int = 24):
        """
        Initialize metrics collector.
        
        Args:
            retention_hours: How long to retain metrics data
        """
        self.retention_hours = retention_hours
        self.retention_seconds = retention_hours * 3600
        
        # Metrics storage
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.timers: Dict[str, List[float]] = defaultdict(list)
        
        # Time series data
        self.time_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1440))  # 24h at 1min resolution
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        app_logger.info("Initialized Metrics Collector")
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric.
        
        Args:
            name: Metric name
            value: Value to add
            tags: Optional tags
        """
        with self.lock:
            key = self._get_metric_key(name, tags)
            self.counters[key] += value
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric value.
        
        Args:
            name: Metric name
            value: Current value
            tags: Optional tags
        """
        with self.lock:
            key = self._get_metric_key(name, tags)
            self.gauges[key] = value
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a histogram value.
        
        Args:
            name: Metric name
            value: Value to record
            tags: Optional tags
        """
        with self.lock:
            key = self._get_metric_key(name, tags)
            self.histograms[key].append(value)
    
    def record_timer(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a timer duration.
        
        Args:
            name: Metric name
            duration: Duration in seconds
            tags: Optional tags
        """
        with self.lock:
            key = self._get_metric_key(name, tags)
            self.timers[key].append(duration)
            
            # Also record in histogram for percentile calculations
            self.histograms[f"{key}_duration"].append(duration)
    
    def record_time_series(self, name: str, value: float, timestamp: Optional[datetime] = None):
        """
        Record a time series data point.
        
        Args:
            name: Metric name
            value: Value to record
            timestamp: Optional timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        with self.lock:
            self.time_series[name].append(MetricData(
                timestamp=timestamp,
                value=value,
                tags={}
            ))
    
    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> int:
        """Get counter value."""
        key = self._get_metric_key(name, tags)
        return self.counters.get(key, 0)
    
    def get_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get gauge value."""
        key = self._get_metric_key(name, tags)
        return self.gauges.get(key, 0.0)
    
    def get_histogram_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """
        Get histogram statistics.
        
        Args:
            name: Metric name
            tags: Optional tags
            
        Returns:
            Dictionary with min, max, mean, median, p95, p99
        """
        key = self._get_metric_key(name, tags)
        values = list(self.histograms.get(key, []))
        
        if not values:
            return {
                'count': 0,
                'min': 0.0,
                'max': 0.0,
                'mean': 0.0,
                'median': 0.0,
                'p95': 0.0,
                'p99': 0.0
            }
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            'count': count,
            'min': sorted_values[0],
            'max': sorted_values[-1],
            'mean': sum(sorted_values) / count,
            'median': self._percentile(sorted_values, 50),
            'p95': self._percentile(sorted_values, 95),
            'p99': self._percentile(sorted_values, 99)
        }
    
    def get_timer_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get timer statistics."""
        key = self._get_metric_key(name, tags)
        durations = self.timers.get(key, [])
        
        if not durations:
            return {'count': 0, 'total': 0.0, 'mean': 0.0}
        
        return {
            'count': len(durations),
            'total': sum(durations),
            'mean': sum(durations) / len(durations)
        }
    
    def get_time_series_data(self, name: str, duration_minutes: int = 60) -> List[MetricData]:
        """
        Get time series data for the last N minutes.
        
        Args:
            name: Metric name
            duration_minutes: Duration to retrieve
            
        Returns:
            List of MetricData points
        """
        cutoff = datetime.utcnow() - timedelta(minutes=duration_minutes)
        
        with self.lock:
            series = self.time_series.get(name, deque())
            return [
                point for point in series
                if point.timestamp >= cutoff
            ]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics.
        
        Returns:
            Dictionary with all metrics
        """
        with self.lock:
            return {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {
                    name: self.get_histogram_stats(name.split('|')[0])
                    for name in self.histograms.keys()
                },
                'timers': {
                    name: self.get_timer_stats(name.split('|')[0])
                    for name in self.timers.keys()
                }
            }
    
    def reset_metrics(self):
        """Reset all metrics."""
        with self.lock:
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.timers.clear()
            self.time_series.clear()
            app_logger.info("Reset all metrics")
    
    def _get_metric_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """
        Generate metric key with tags.
        
        Args:
            name: Metric name
            tags: Optional tags
            
        Returns:
            Metric key string
        """
        if not tags:
            return name
        
        tag_str = ','.join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}|{tag_str}"
    
    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """
        Calculate percentile value.
        
        Args:
            sorted_values: Sorted list of values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not sorted_values:
            return 0.0
        
        k = (len(sorted_values) - 1) * (percentile / 100)
        f = int(k)
        c = f + 1
        
        if c >= len(sorted_values):
            return sorted_values[-1]
        
        return sorted_values[f] + (k - f) * (sorted_values[c] - sorted_values[f])


class PerformanceMonitor:
    """Monitor system performance metrics."""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        """
        Initialize performance monitor.
        
        Args:
            metrics_collector: Optional MetricsCollector instance
        """
        self.metrics = metrics_collector or MetricsCollector()
        self.start_time = datetime.utcnow()
        
        # Performance thresholds
        self.thresholds = {
            'response_time_warning': 2.0,  # seconds
            'response_time_critical': 5.0,
            'error_rate_warning': 0.05,  # 5%
            'error_rate_critical': 0.10   # 10%
        }
        
        app_logger.info("Initialized Performance Monitor")
    
    def record_api_call(self, endpoint: str, method: str, duration: float, 
                       status_code: int, error: Optional[str] = None):
        """
        Record API call metrics.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            duration: Request duration
            status_code: Response status code
            error: Optional error message
        """
        tags = {'endpoint': endpoint, 'method': method}
        
        # Record counter
        self.metrics.increment_counter('api.requests.total', tags=tags)
        
        # Record duration
        self.metrics.record_timer('api.request.duration', duration, tags=tags)
        
        # Record status
        if 200 <= status_code < 300:
            self.metrics.increment_counter('api.requests.success', tags=tags)
        elif 400 <= status_code < 500:
            self.metrics.increment_counter('api.requests.client_error', tags=tags)
        elif 500 <= status_code < 600:
            self.metrics.increment_counter('api.requests.server_error', tags=tags)
        
        # Check thresholds
        if duration > self.thresholds['response_time_critical']:
            app_logger.warning(f"Critical response time: {duration:.2f}s for {endpoint}")
        elif duration > self.thresholds['response_time_warning']:
            app_logger.info(f"Slow response: {duration:.2f}s for {endpoint}")
    
    def record_conversation_metrics(self, session_id: str, turn_count: int, 
                                   intent: str, sentiment: str):
        """
        Record conversation-related metrics.
        
        Args:
            session_id: Session ID
            turn_count: Number of turns
            intent: Detected intent
            sentiment: Detected sentiment
        """
        # Intent distribution
        self.metrics.increment_counter('conversation.intents', tags={'intent': intent})
        
        # Sentiment distribution
        self.metrics.increment_counter('conversation.sentiments', tags={'sentiment': sentiment})
        
        # Turn count histogram
        self.metrics.record_histogram('conversation.turn_count', turn_count)
        
        # Active sessions gauge
        self.metrics.set_gauge('conversation.active_sessions', self._get_active_sessions_count())
    
    def record_retrieval_metrics(self, query: str, num_results: int, duration: float):
        """
        Record retrieval metrics.
        
        Args:
            query: Search query
            num_results: Number of results returned
            duration: Retrieval duration
        """
        self.metrics.increment_counter('retrieval.queries.total')
        self.metrics.record_timer('retrieval.duration', duration)
        self.metrics.record_histogram('retrieval.results_count', num_results)
    
    def record_generation_metrics(self, tokens: int, duration: float, cache_hit: bool = False):
        """
        Record generation metrics.
        
        Args:
            tokens: Number of tokens generated
            duration: Generation duration
            cache_hit: Whether response was from cache
        """
        self.metrics.increment_counter('generation.requests.total')
        self.metrics.record_timer('generation.duration', duration)
        self.metrics.record_histogram('generation.tokens', tokens)
        
        if cache_hit:
            self.metrics.increment_counter('generation.cache.hits')
        else:
            self.metrics.increment_counter('generation.cache.misses')
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary.
        
        Returns:
            Dictionary with performance metrics
        """
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        api_stats = self.metrics.get_histogram_stats('api.request.duration')
        
        total_requests = self.metrics.get_counter('api.requests.total')
        success_requests = self.metrics.get_counter('api.requests.success')
        error_requests = (
            self.metrics.get_counter('api.requests.client_error') +
            self.metrics.get_counter('api.requests.server_error')
        )
        
        success_rate = success_requests / total_requests if total_requests > 0 else 0
        error_rate = error_requests / total_requests if total_requests > 0 else 0
        
        return {
            'uptime_seconds': uptime,
            'api': {
                'total_requests': total_requests,
                'success_rate': success_rate,
                'error_rate': error_rate,
                'response_times': api_stats
            },
            'retrieval': {
                'total_queries': self.metrics.get_counter('retrieval.queries.total'),
                'avg_duration': self.metrics.get_timer_stats('retrieval.duration').get('mean', 0)
            },
            'generation': {
                'total_requests': self.metrics.get_counter('generation.requests.total'),
                'cache_hit_rate': self._calculate_cache_hit_rate()
            },
            'conversations': {
                'active_sessions': self.metrics.get_gauge('conversation.active_sessions'),
                'intent_distribution': self._get_intent_distribution(),
                'sentiment_distribution': self._get_sentiment_distribution()
            }
        }
    
    def _get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        # This would be implemented with actual session manager
        return 0
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        hits = self.metrics.get_counter('generation.cache.hits')
        misses = self.metrics.get_counter('generation.cache.misses')
        total = hits + misses
        return hits / total if total > 0 else 0.0
    
    def _get_intent_distribution(self) -> Dict[str, int]:
        """Get intent distribution."""
        # Simplified version - would need to parse counter keys
        return {}
    
    def _get_sentiment_distribution(self) -> Dict[str, int]:
        """Get sentiment distribution."""
        # Simplified version - would need to parse counter keys
        return {}


# Global instances
metrics_collector = MetricsCollector()
performance_monitor = PerformanceMonitor(metrics_collector)
