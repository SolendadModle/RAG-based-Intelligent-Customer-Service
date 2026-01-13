"""
FastAPI Application - Main API server for RAG Customer Service System.
"""

import os
import time
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn

from src.api.models import (
    ChatRequest, ChatResponse, SessionInfo, NLURequest, NLUResponse,
    RetrievalRequest, RetrievalResponse, RecommendationRequest, RecommendationResponse,
    SentimentRequest, SentimentResponse, HealthResponse, StatisticsResponse, ErrorResponse
)
from src.config import config_manager
from src.logger import app_logger, log_manager
from src.dialog.dialog_handler import DialogHandler
from src.nlu.entity_extraction import NLUService
from src.knowledge_base.retrieval import RetrievalService
from src.sentiment.sentiment_analyzer import SentimentAnalyzer
from src.recommendation.recommendation_engine import RecommendationEngine
from src.utils import sanitize_input


# Global service instances
dialog_handler: Optional[DialogHandler] = None
nlu_service: Optional[NLUService] = None
retrieval_service: Optional[RetrievalService] = None
sentiment_analyzer: Optional[SentimentAnalyzer] = None
recommendation_engine: Optional[RecommendationEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    global dialog_handler, nlu_service, retrieval_service, sentiment_analyzer, recommendation_engine
    
    app_logger.info("Starting RAG Customer Service API...")
    
    try:
        # Initialize services
        app_logger.info("Initializing services...")
        
        nlu_service = NLUService()
        retrieval_service = RetrievalService()
        sentiment_analyzer = SentimentAnalyzer()
        recommendation_engine = RecommendationEngine()
        dialog_handler = DialogHandler(
            nlu_service=nlu_service,
            session_manager=None  # Will use default
        )
        
        # Build knowledge base index
        app_logger.info("Building knowledge base index...")
        retrieval_service.build_index()
        
        app_logger.info("All services initialized successfully")
        
    except Exception as e:
        app_logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down RAG Customer Service API...")


# Create FastAPI application
app = FastAPI(
    title="RAG-based Intelligent Customer Service API",
    description="API for RAG-based customer service system with Qianwen integration",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
api_config = config_manager.api_config
cors_config = api_config.get('cors', {})

if cors_config.get('enabled', True):
    origins = cors_config.get('origins', ['*'])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=cors_config.get('methods', ['*']),
        allow_headers=cors_config.get('headers', ['*'])
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    app_logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": "RAG Customer Service API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        services = {
            'nlu': nlu_service is not None,
            'retrieval': retrieval_service is not None and retrieval_service.index is not None,
            'sentiment': sentiment_analyzer is not None,
            'recommendation': recommendation_engine is not None,
            'dialog': dialog_handler is not None
        }
        
        return HealthResponse(
            status="healthy" if all(services.values()) else "degraded",
            timestamp=datetime.utcnow().isoformat(),
            services=services
        )
    except Exception as e:
        app_logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Process chat message and generate response.
    """
    start_time = time.time()
    
    try:
        # Sanitize input
        message = sanitize_input(request.message)
        
        # Process message
        result = dialog_handler.process_message(
            message=message,
            session_id=request.session_id,
            user_id=request.user_id,
            use_rag=request.use_rag
        )
        
        # Analyze sentiment
        sentiment_result = sentiment_analyzer.analyze(message)
        should_escalate, escalation_reason = sentiment_analyzer.should_escalate(message)
        
        # Get recommendations
        recommendations = recommendation_engine.recommend_by_intent(
            intent=result.get('intent'),
            entities=result.get('entities')
        )
        
        # Log API call
        duration = time.time() - start_time
        log_manager.log_api_call(
            endpoint="/chat",
            method="POST",
            status_code=200,
            duration=duration
        )
        
        return ChatResponse(
            session_id=result['session_id'],
            response=result['response'],
            intent=result.get('intent'),
            intent_confidence=result.get('intent_confidence'),
            entities=result.get('entities'),
            sentiment=sentiment_result,
            recommendations=recommendations[:3] if recommendations else None,
            state=result.get('state'),
            turn_count=result.get('turn_count')
        )
    
    except Exception as e:
        app_logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest):
    """
    Process chat message with streaming response.
    """
    try:
        message = sanitize_input(request.message)
        
        async def generate():
            """Generate streaming response."""
            try:
                for chunk in dialog_handler.process_message_stream(
                    message=message,
                    session_id=request.session_id,
                    user_id=request.user_id,
                    use_rag=request.use_rag
                ):
                    if chunk['type'] == 'content':
                        yield chunk['chunk']
            except Exception as e:
                app_logger.error(f"Error in streaming: {e}")
                yield f"\n[Error: {str(e)}]"
        
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        app_logger.error(f"Error in chat stream endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}", response_model=SessionInfo, tags=["Session"])
async def get_session(session_id: str):
    """Get session information."""
    try:
        session_info = dialog_handler.get_session_info(session_id)
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionInfo(
            session_id=session_info['session_id'],
            user_id=session_info.get('user_id'),
            created_at=session_info['created_at'],
            last_activity=session_info['last_activity'],
            state=session_info['state'],
            turn_count=len(session_info['history']) // 2,
            history=session_info['history']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/session/{session_id}", tags=["Session"])
async def delete_session(session_id: str):
    """End session."""
    try:
        dialog_handler.end_session(session_id)
        return {"message": f"Session {session_id} ended successfully"}
    except Exception as e:
        app_logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/nlu/analyze", response_model=NLUResponse, tags=["NLU"])
async def analyze_nlu(request: NLURequest):
    """Analyze text for intent and entities."""
    try:
        text = sanitize_input(request.text)
        result = nlu_service.analyze(text)
        
        return NLUResponse(
            text=result['text'],
            intent=result['intent'],
            entities=result['entities']
        )
    except Exception as e:
        app_logger.error(f"Error in NLU analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieval/search", response_model=RetrievalResponse, tags=["Retrieval"])
async def search_knowledge_base(request: RetrievalRequest):
    """Search knowledge base."""
    try:
        query = sanitize_input(request.query)
        results = retrieval_service.retrieve(query, top_k=request.top_k)
        
        formatted_results = [
            {
                'content': doc.content,
                'metadata': doc.metadata,
                'score': score
            }
            for doc, score in results
        ]
        
        return RetrievalResponse(
            query=query,
            results=formatted_results,
            count=len(formatted_results)
        )
    except Exception as e:
        app_logger.error(f"Error in retrieval: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommendations", response_model=RecommendationResponse, tags=["Recommendations"])
async def get_recommendations(request: RecommendationRequest):
    """Get recommendations."""
    try:
        if request.session_id:
            session_info = dialog_handler.get_session_info(request.session_id)
            if session_info:
                recommendations = recommendation_engine.recommend_based_on_history(
                    session_info['history']
                )
            else:
                recommendations = []
        elif request.intent:
            recommendations = recommendation_engine.recommend_by_intent(
                intent=request.intent
            )
        elif request.query:
            recommendations = recommendation_engine.recommend(
                query=request.query,
                category=request.category
            )
        else:
            recommendations = recommendation_engine.get_popular_items()
        
        return RecommendationResponse(
            recommendations=recommendations,
            count=len(recommendations)
        )
    except Exception as e:
        app_logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sentiment/analyze", response_model=SentimentResponse, tags=["Sentiment"])
async def analyze_sentiment(request: SentimentRequest):
    """Analyze sentiment of text."""
    try:
        text = sanitize_input(request.text)
        result = sentiment_analyzer.analyze(text)
        should_escalate, reason = sentiment_analyzer.should_escalate(text)
        
        return SentimentResponse(
            sentiment=result['sentiment'],
            score=result['score'],
            intensity=result['intensity'],
            should_escalate=should_escalate,
            escalation_reason=reason if should_escalate else None
        )
    except Exception as e:
        app_logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics", response_model=StatisticsResponse, tags=["Statistics"])
async def get_statistics():
    """Get system statistics."""
    try:
        stats = {
            'sessions': dialog_handler.get_statistics(),
            'knowledge_base': retrieval_service.get_index_stats(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return StatisticsResponse(**stats)
    except Exception as e:
        app_logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    session_id = None
    
    try:
        app_logger.info("WebSocket connection established")
        
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = sanitize_input(data.get('message', ''))
            
            if not message:
                continue
            
            # Process message
            result = dialog_handler.process_message(
                message=message,
                session_id=session_id,
                user_id=data.get('user_id')
            )
            
            session_id = result['session_id']
            
            # Send response
            await websocket.send_json({
                'type': 'response',
                'session_id': session_id,
                'response': result['response'],
                'intent': result.get('intent'),
                'state': result.get('state')
            })
    
    except WebSocketDisconnect:
        app_logger.info("WebSocket connection closed")
    except Exception as e:
        app_logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                'type': 'error',
                'error': str(e)
            })
        except:
            pass


if __name__ == "__main__":
    # Run the application
    host = config_manager.settings.api_host
    port = config_manager.settings.api_port
    debug = config_manager.settings.api_debug
    
    uvicorn.run(
        "src.api.app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
