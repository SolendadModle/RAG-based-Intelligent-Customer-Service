# API Documentation

## Overview

The RAG Customer Service API provides comprehensive endpoints for building intelligent conversational interfaces.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI documentation.

## Core Endpoints

### POST /chat

Process chat message and generate response.

**Request:**
```json
{
  "message": "How do I reset my password?",
  "session_id": "optional",
  "use_rag": true
}
```

**Response:**
```json
{
  "session_id": "abc123",
  "response": "To reset your password...",
  "intent": "technical_support",
  "sentiment": {"sentiment": "neutral", "score": 0.7},
  "recommendations": [...]
}
```

### WebSocket /ws/chat

Real-time bidirectional chat.

### GET /health

Check system health.

### GET /statistics

Get system statistics.

For complete documentation, see the full API guide or visit `/docs`.
