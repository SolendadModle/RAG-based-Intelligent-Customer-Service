"""
API Models - Pydantic models for request/response validation.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for continuing conversation")
    user_id: Optional[str] = Field(None, description="User ID")
    use_rag: bool = Field(True, description="Whether to use RAG for response generation")
    stream: bool = Field(False, description="Whether to stream response")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    session_id: str = Field(..., description="Session ID")
    response: str = Field(..., description="Bot response")
    intent: Optional[str] = Field(None, description="Detected intent")
    intent_confidence: Optional[float] = Field(None, description="Intent confidence score")
    entities: Optional[Dict[str, List[Dict]]] = Field(None, description="Extracted entities")
    sentiment: Optional[Dict[str, Any]] = Field(None, description="Sentiment analysis result")
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Recommendations")
    state: Optional[str] = Field(None, description="Conversation state")
    turn_count: Optional[int] = Field(None, description="Number of conversation turns")


class SessionInfo(BaseModel):
    """Session information model."""
    session_id: str
    user_id: Optional[str]
    created_at: str
    last_activity: str
    state: str
    turn_count: int
    history: List[Dict[str, Any]]


class NLURequest(BaseModel):
    """Request model for NLU analysis."""
    text: str = Field(..., description="Text to analyze", min_length=1)


class NLUResponse(BaseModel):
    """Response model for NLU analysis."""
    text: str
    intent: Dict[str, Any]
    entities: Dict[str, List[Dict]]


class RetrievalRequest(BaseModel):
    """Request model for knowledge retrieval."""
    query: str = Field(..., description="Search query", min_length=1)
    top_k: Optional[int] = Field(5, description="Number of results to retrieve", ge=1, le=20)


class RetrievalResponse(BaseModel):
    """Response model for knowledge retrieval."""
    query: str
    results: List[Dict[str, Any]]
    count: int


class RecommendationRequest(BaseModel):
    """Request model for recommendations."""
    query: Optional[str] = Field(None, description="Query for recommendations")
    intent: Optional[str] = Field(None, description="User intent")
    category: Optional[str] = Field(None, description="Category filter")
    session_id: Optional[str] = Field(None, description="Session ID for history-based recommendations")


class RecommendationResponse(BaseModel):
    """Response model for recommendations."""
    recommendations: List[Dict[str, Any]]
    count: int


class SentimentRequest(BaseModel):
    """Request model for sentiment analysis."""
    text: str = Field(..., description="Text to analyze", min_length=1)


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis."""
    sentiment: str
    score: float
    intensity: str
    should_escalate: bool
    escalation_reason: Optional[str]


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    services: Dict[str, Any]


class StatisticsResponse(BaseModel):
    """Response model for statistics."""
    sessions: Dict[str, Any]
    knowledge_base: Dict[str, Any]
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str]
    timestamp: str
