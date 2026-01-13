# Deployment Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- 4GB RAM minimum (8GB recommended)
- Internet connection for API access
- Qianwen API key from Alibaba Cloud DashScope

## Environment Setup

### 1. System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv
```

**macOS:**
```bash
brew install python3
```

**Windows:**
Download and install Python from python.org

### 2. Clone Repository

```bash
git clone https://github.com/SolendadModle/RAG-based-Intelligent-Customer-Service.git
cd RAG-based-Intelligent-Customer-Service
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 5. Configuration

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
DASHSCOPE_API_KEY=your_actual_api_key_here
QIANWEN_MODEL=qwen-turbo
```

## Development Deployment

### Quick Start

```bash
python run.py
```

This will start both the API server and Streamlit frontend.

### Manual Start

**Terminal 1 - API Server:**
```bash
python -m src.api.app
```

**Terminal 2 - Frontend:**
```bash
streamlit run src/frontend/streamlit_app.py
```

### Verify Deployment

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:8501

## Production Deployment

### Using Gunicorn (Recommended for API)

```bash
pip install gunicorn
gunicorn src.api.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

**Create Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "src.api.app"]
```

**Build and Run:**
```bash
docker build -t rag-customer-service .
docker run -d -p 8000:8000 --env-file .env rag-customer-service
```

### Using Docker Compose

**Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    build: .
    command: streamlit run src/frontend/streamlit_app.py
    ports:
      - "8501:8501"
    depends_on:
      - api
    environment:
      - API_BASE_URL=http://api:8000
    restart: unless-stopped
```

**Start services:**
```bash
docker-compose up -d
```

## Cloud Deployment

### AWS EC2

1. Launch EC2 instance (t2.medium or larger)
2. Install Docker
3. Clone repository
4. Configure security groups (ports 8000, 8501)
5. Run with Docker Compose

### Google Cloud Platform

```bash
gcloud run deploy rag-customer-service \
  --source . \
  --port 8000 \
  --allow-unauthenticated
```

### Azure

```bash
az container create \
  --resource-group myResourceGroup \
  --name rag-customer-service \
  --image rag-customer-service:latest \
  --ports 8000 \
  --environment-variables DASHSCOPE_API_KEY=your_key
```

## Nginx Configuration

**Create /etc/nginx/sites-available/rag-service:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/rag-service /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL/HTTPS Setup

### Using Certbot

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring & Logging

### View Logs

```bash
# Application logs
tail -f data/logs/app_*.log

# API access logs
tail -f data/logs/api_calls_*.log

# Conversation logs
tail -f data/logs/conversations_*.log
```

### Monitor with systemd

**Create /etc/systemd/system/rag-api.service:**
```ini
[Unit]
Description=RAG Customer Service API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/rag-customer-service
Environment="PATH=/opt/rag-customer-service/venv/bin"
ExecStart=/opt/rag-customer-service/venv/bin/python -m src.api.app
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl enable rag-api
sudo systemctl start rag-api
sudo systemctl status rag-api
```

## Performance Tuning

### Optimize Vector Store

```python
# Build optimized index
from src.knowledge_base.retrieval import RetrievalService

service = RetrievalService()
service.build_index(force_rebuild=True)
```

### Enable Caching

In `config/config.yaml`:
```yaml
cache:
  enabled: true
  backend: "redis"  # Requires Redis setup
  ttl: 3600
```

### Configure Workers

```bash
# For high traffic
gunicorn src.api.app:app -w 8 -k uvicorn.workers.UvicornWorker
```

## Backup & Recovery

### Backup Data

```bash
# Backup knowledge base
tar -czf kb_backup_$(date +%Y%m%d).tar.gz data/knowledge_base/

# Backup vector store
tar -czf vector_backup_$(date +%Y%m%d).tar.gz data/vector_store/

# Backup logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz data/logs/
```

### Restore

```bash
tar -xzf kb_backup_YYYYMMDD.tar.gz -C data/
tar -xzf vector_backup_YYYYMMDD.tar.gz -C data/
```

## Troubleshooting

### Common Issues

**API won't start:**
```bash
# Check if port is in use
lsof -i :8000

# Check logs
tail -f data/logs/app_*.log
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**spaCy model missing:**
```bash
python -m spacy download en_core_web_sm
```

**Qianwen API errors:**
- Verify API key in `.env`
- Check API quota limits
- Ensure network connectivity

### Performance Issues

- Increase worker count
- Enable caching
- Optimize vector store index
- Add more RAM to server

## Health Checks

```bash
# API health
curl http://localhost:8000/health

# Check all services
curl http://localhost:8000/statistics
```

## Maintenance

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Clean Logs

```bash
find data/logs -name "*.gz" -mtime +30 -delete
```

### Rebuild Index

```bash
python -c "from src.knowledge_base.retrieval import RetrievalService; \
           service = RetrievalService(); \
           service.build_index(force_rebuild=True)"
```

## Security Checklist

- [ ] Change default API keys
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable authentication
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Audit logging enabled

## Support

For deployment issues:
1. Check logs in `data/logs/`
2. Review configuration in `config/config.yaml`
3. Verify environment variables in `.env`
4. Open GitHub issue with details
