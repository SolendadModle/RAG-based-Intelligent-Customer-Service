# RAG-based Intelligent Customer Service System

A comprehensive end-to-end intelligent customer service system powered by Retrieval-Augmented Generation (RAG) and integrated with Alibaba's Qianwen API for advanced natural language understanding and generation.

## 🌟 Features

### Core Capabilities

1. **Natural Language Understanding (NLU)**
   - Intent recognition with pattern matching and similarity scoring
   - Entity extraction using spaCy and custom regex patterns
   - Support for 10+ common customer service intents
   - Custom entity types including ORDER_ID, EMAIL, PHONE, etc.

2. **Knowledge Base Integration**
   - FAISS-based vector search for efficient retrieval
   - Support for multiple document sources (FAQ, documents, JSON)
   - Sentence transformer embeddings for semantic search
   - Configurable similarity thresholds and context limits

3. **RAG Generation Module**
   - Integration with Alibaba Qianwen API (DashScope)
   - Context-aware response generation
   - Streaming response support
   - Customizable prompt templates

4. **Multi-turn Dialog Management**
   - Session-based conversation tracking
   - Conversation state management (initial, processing, escalation, etc.)
   - Context preservation across turns
   - Configurable session timeout

5. **Sentiment Analysis**
   - Real-time sentiment detection (positive/negative/neutral)
   - Escalation triggers based on negative sentiment
   - Urgency keyword detection
   - Emotion trend analysis

6. **Recommendation Engine**
   - Content-based recommendations using embeddings
   - Intent-based suggestions
   - Conversation history analysis
   - Configurable relevance thresholds

7. **REST API Backend**
   - FastAPI-based RESTful API
   - WebSocket support for real-time chat
   - Comprehensive API documentation (Swagger/OpenAPI)
   - CORS support and security features

8. **Interactive Frontend**
   - Streamlit-based web interface
   - Real-time chat with bot
   - Session management
   - Statistics and analytics dashboard

## 📋 Requirements

- Python 3.8+
- 4GB+ RAM (8GB recommended for optimal performance)
- Internet connection for API access

## 🚀 Quick Start

> **🪟 Windows Users**: See [Windows Setup Guide](docs/WINDOWS_GUIDE.md) for detailed Windows-specific instructions.

### 1. Clone and Install

```bash
git clone https://github.com/SolendadModle/RAG-based-Intelligent-Customer-Service.git
cd RAG-based-Intelligent-Customer-Service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your Qianwen API key
```

### 3. Run

```bash
# Option 1: Run both services (recommended)
python run.py

# Option 2: Run separately
# Terminal 1 - Backend API
python -m src.api.app

# Terminal 2 - Frontend (choose one)
streamlit run src/frontend/streamlit_app.py          # Basic UI
streamlit run src/frontend/enhanced_app.py           # Enhanced UI (Recommended ⭐)
```

### 4. Access

- **Web Interface**: http://localhost:8501 (Frontend)
- **API Documentation**: http://localhost:8000/docs (Interactive API docs)
- **API Endpoint**: http://localhost:8000 (Backend)

### Frontend Options

1. **Basic Frontend** (`streamlit_app.py`) - Simple and functional interface
2. **Enhanced Frontend** (`enhanced_app.py`) ⭐ **NEW!** - Modern design with:
   - 🎨 Beautiful gradient design
   - 📊 Interactive charts and analytics
   - ✨ Smooth animations
   - 📱 Responsive layout
   - 💡 Improved user experience

## 📁 Project Structure

```
RAG-based-Intelligent-Customer-Service/
├── src/
│   ├── nlu/                    # Natural Language Understanding
│   ├── knowledge_base/         # Knowledge Base & Retrieval
│   ├── generation/             # RAG Generation with Qianwen
│   ├── dialog/                 # Multi-turn Dialog Management
│   ├── sentiment/              # Sentiment Analysis
│   ├── recommendation/         # Recommendation Engine
│   ├── api/                    # FastAPI Backend
│   └── frontend/               # Streamlit Frontend
├── tests/                      # Unit & Integration Tests
├── data/                       # Data Files
│   ├── knowledge_base/         # FAQ and Documents
│   ├── logs/                   # Application Logs
│   └── vector_store/           # FAISS Index
├── config/                     # Configuration Files
└── docs/                       # Documentation
```

## 🎯 Usage Examples

### Chat API

```python
import requests

response = requests.post('http://localhost:8000/chat', json={
    'message': 'How do I reset my password?',
    'use_rag': True
})

print(response.json())
```

### WebSocket Chat

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Bot:', data.response);
};
ws.send(JSON.stringify({message: 'Hello'}));
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/unit/test_nlu.py -v
```

## 📊 System Architecture

```
User Input → NLU → Intent & Entities
              ↓
        Dialog Manager
              ↓
    Knowledge Retrieval (FAISS)
              ↓
    RAG Generation (Qianwen)
              ↓
    Sentiment Analysis → Escalation?
              ↓
    Recommendations
              ↓
         Response
```

## 🔧 Configuration

Edit `config/config.yaml` to customize:

- NLU thresholds and supported intents
- Knowledge base sources and retrieval parameters
- Qianwen API settings and prompt templates
- Dialog states and session timeouts
- Sentiment analysis and escalation rules
- Recommendation categories and thresholds

## 🌐 API Endpoints

### Core Endpoints
- `POST /chat` - Process chat message
- `POST /chat/stream` - Streaming response
- `WS /ws/chat` - WebSocket chat
- `GET /health` - Health check
- `GET /statistics` - System stats

### Analysis Endpoints
- `POST /nlu/analyze` - Intent & entity analysis
- `POST /sentiment/analyze` - Sentiment analysis
- `POST /retrieval/search` - Knowledge search
- `POST /recommendations` - Get recommendations

See [API Documentation](docs/API.md) for complete details.

## 🔒 Security

- Input sanitization for all user inputs
- API key authentication for Qianwen
- CORS configuration
- Session timeout management
- Request validation with Pydantic

## 📝 Code Quality

The codebase includes:
- **6000+ lines of code** across all modules
- Comprehensive docstrings for all functions
- Type hints throughout
- Unit tests with pytest
- Modular architecture
- Industry-standard practices

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && python -m spacy download en_core_web_sm
COPY . .
CMD ["python", "-m", "src.api.app"]
```

```bash
docker build -t rag-customer-service .
docker run -p 8000:8000 --env-file .env rag-customer-service
```

## 📈 Performance

- **Response Time**: < 2s for RAG queries
- **Retrieval**: < 100ms for vector search
- **Concurrent Users**: 100+ (with proper scaling)
- **Knowledge Base**: Supports 10,000+ documents

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is provided as-is for educational and commercial use.

## 🙏 Acknowledgments

- **Alibaba Cloud** - Qianwen API
- **Sentence Transformers** - Text embeddings
- **FAISS** - Vector search
- **FastAPI** - Web framework
- **Streamlit** - Frontend interface

## 📚 Additional Documentation

- **[Usage Guide](docs/USAGE_GUIDE.md)** - Comprehensive bilingual (EN/CN) guide
- **[Windows Guide](docs/WINDOWS_GUIDE.md)** - 🪟 Windows-specific setup and troubleshooting
- **[Frontend Comparison](docs/FRONTEND_COMPARISON.md)** - Compare Basic vs Enhanced UI
- **[API Documentation](docs/API.md)** - Complete API reference
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Security Guide](docs/SECURITY.md)** - Security best practices

## 📞 Support

For issues or questions, please open an issue on GitHub.

## 🔄 Version

**v1.0.0** - Full RAG-based customer service system with Qianwen integration

---

**Note**: Requires a Qianwen API key from Alibaba Cloud DashScope. Register at https://dashscope.aliyun.com/