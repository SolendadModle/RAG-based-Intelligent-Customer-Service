# 使用指南 / Usage Guide

## 📂 项目结构 / Project Structure

```
RAG-based-Intelligent-Customer-Service/
│
├── src/                          # 源代码 / Source code
│   ├── api/                      # 后端 API / Backend API
│   │   ├── app.py               # FastAPI 主应用 / Main FastAPI app
│   │   └── models.py            # API 数据模型 / API models
│   │
│   ├── frontend/                 # 前端界面 / Frontend UI
│   │   ├── streamlit_app.py    # 基础前端 / Basic frontend
│   │   └── enhanced_app.py      # 增强版前端 / Enhanced frontend (NEW!)
│   │
│   ├── nlu/                      # 自然语言理解 / NLU
│   │   ├── intent_recognition.py
│   │   └── entity_extraction.py
│   │
│   ├── knowledge_base/           # 知识库 / Knowledge base
│   │   ├── kb_manager.py
│   │   ├── embeddings.py
│   │   └── retrieval.py
│   │
│   ├── generation/               # 生成模块 (千问API) / Generation (Qianwen API)
│   │   ├── qianwen_client.py    # 千问 API 客户端 / Qianwen client
│   │   └── rag_generator.py     # RAG 生成器 / RAG generator
│   │
│   ├── dialog/                   # 对话管理 / Dialog management
│   │   ├── dialog_handler.py
│   │   └── session_manager.py
│   │
│   ├── sentiment/                # 情感分析 / Sentiment analysis
│   │   └── sentiment_analyzer.py
│   │
│   ├── recommendation/           # 推荐引擎 / Recommendation engine
│   │   └── recommendation_engine.py
│   │
│   └── config.py                 # 配置管理 / Configuration
│
├── config/                       # 配置文件 / Config files
│   └── config.yaml
│
├── data/                         # 数据目录 / Data directory
│   ├── knowledge_base/          # 知识库文件 / KB files
│   ├── vector_store/            # 向量存储 / Vector store
│   └── logs/                    # 日志 / Logs
│
├── tests/                        # 测试 / Tests
│   └── unit/
│
├── requirements.txt              # Python 依赖 / Dependencies
├── run.py                       # 启动脚本 / Startup script
└── README.md                    # 项目说明 / Project readme
```

---

## 🎯 代码位置说明 / Code Locations

### 后端代码 / Backend Code

**位置 / Location**: `src/api/`

主要文件 / Main files:
- `app.py` - FastAPI 应用主文件，包含所有 REST API 端点
- `models.py` - API 请求/响应模型定义

**功能 / Features**:
- ✅ 15+ REST API 端点
- ✅ WebSocket 实时通信
- ✅ 自动生成的 API 文档 (Swagger)
- ✅ CORS 支持
- ✅ 错误处理和日志记录

### 前端代码 / Frontend Code

**位置 / Location**: `src/frontend/`

可用版本 / Available versions:

1. **基础版 / Basic Version**: `streamlit_app.py`
   - 简洁实用的界面
   - 基本聊天功能
   - 适合快速测试

2. **增强版 / Enhanced Version**: `enhanced_app.py` ⭐ **新增 / NEW!**
   - 🎨 现代化渐变设计
   - 📊 交互式数据可视化
   - 🎯 实时统计图表
   - ✨ 动画效果
   - 📱 响应式布局
   - 💡 优化的用户体验

---

## 🚀 如何运行 / How to Run

### 方法 1: 一键启动 (推荐) / Method 1: One-Click Start (Recommended)

```bash
# 同时启动后端和前端 / Start both backend and frontend
python run.py
```

访问 / Access:
- 🌐 **前端界面 / Frontend**: http://localhost:8501
- 🔌 **API 文档 / API Docs**: http://localhost:8000/docs
- 📡 **API 端点 / API Endpoint**: http://localhost:8000

### 方法 2: 分别启动 / Method 2: Start Separately

#### 步骤 1: 启动后端 / Step 1: Start Backend

```bash
# 方式 A: 使用 Python 模块 / Method A: Using Python module
python -m src.api.app

# 方式 B: 使用 uvicorn / Method B: Using uvicorn
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

#### 步骤 2: 启动前端 / Step 2: Start Frontend

在新的终端窗口 / In a new terminal:

```bash
# 基础版前端 / Basic frontend
streamlit run src/frontend/streamlit_app.py

# 或使用增强版前端 (推荐) / Or use enhanced frontend (recommended)
streamlit run src/frontend/enhanced_app.py
```

### 方法 3: 自定义端口 / Method 3: Custom Ports

```bash
# 后端使用自定义端口 / Backend with custom port
uvicorn src.api.app:app --host 0.0.0.0 --port 8080

# 前端使用自定义端口 / Frontend with custom port
streamlit run src/frontend/enhanced_app.py --server.port 8502
```

---

## 🎨 前端功能对比 / Frontend Feature Comparison

| 功能 / Feature | 基础版 / Basic | 增强版 / Enhanced |
|---------------|---------------|-------------------|
| 聊天功能 / Chat | ✅ | ✅ |
| 意图识别显示 / Intent Display | ✅ | ✅ |
| 情感分析 / Sentiment | ✅ | ✅ |
| 推荐系统 / Recommendations | ✅ | ✅ |
| 现代化设计 / Modern Design | ❌ | ✅ |
| 渐变背景 / Gradient | ❌ | ✅ |
| 动画效果 / Animations | ❌ | ✅ |
| 交互式图表 / Interactive Charts | ❌ | ✅ |
| 实时统计 / Live Statistics | 基础 | 增强 |
| 响应式布局 / Responsive | 基础 | 优化 |

---

## 🔧 配置说明 / Configuration

### 必须配置 / Required Configuration

**文件 / File**: `.env`

```bash
# 从示例文件复制 / Copy from example
cp .env.example .env

# 编辑并添加您的千问 API 密钥 / Edit and add your Qianwen API key
nano .env
```

**必须修改 / Must modify**:
```bash
DASHSCOPE_API_KEY=your_actual_api_key_here  # 替换为真实密钥 / Replace with real key
```

### 可选配置 / Optional Configuration

**文件 / File**: `config/config.yaml`

可以调整 / You can adjust:
- 模型参数 / Model parameters
- 检索设置 / Retrieval settings
- 对话管理 / Dialog management
- 推荐阈值 / Recommendation thresholds

---

## 📖 API 使用示例 / API Usage Examples

### 1. 发送聊天消息 / Send Chat Message

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I reset my password?",
    "session_id": null,
    "use_rag": true
  }'
```

### 2. 意图识别 / Intent Recognition

```bash
curl -X POST "http://localhost:8000/nlu/intent" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I want to track my order"
  }'
```

### 3. 知识库搜索 / Knowledge Base Search

```bash
curl -X POST "http://localhost:8000/retrieval/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "password reset",
    "top_k": 5
  }'
```

### 4. 情感分析 / Sentiment Analysis

```bash
curl -X POST "http://localhost:8000/sentiment/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This service is amazing!"
  }'
```

---

## 🎯 前端使用说明 / Frontend Usage Guide

### 基础操作 / Basic Operations

1. **开始对话 / Start Conversation**
   - 在底部输入框输入消息 / Type message in bottom input
   - 按回车或点击发送 / Press Enter or click send

2. **查看信息 / View Information**
   - 右侧面板显示意图、情感和状态 / Right panel shows intent, sentiment, state
   - 推荐内容自动显示 / Recommendations display automatically

3. **会话管理 / Session Management**
   - 侧边栏点击"新对话"重置会话 / Click "New Conversation" in sidebar to reset
   - 会话 ID 自动管理 / Session ID managed automatically

4. **知识库搜索 / Knowledge Search**
   - 侧边栏点击"搜索知识库" / Click "Search Knowledge" in sidebar
   - 输入查询并搜索 / Enter query and search

### 高级功能 / Advanced Features

1. **启用/禁用 RAG / Enable/Disable RAG**
   - 侧边栏勾选"启用知识库检索" / Check "Enable Knowledge Base Search" in sidebar
   - 关闭后将使用纯生成模式 / Disable for pure generation mode

2. **查看统计 / View Statistics**
   - 侧边栏展开"详细分析" / Expand "Detailed Analytics" in sidebar
   - 查看意图和情感分布图表 / View intent and sentiment distribution charts

3. **获取推荐 / Get Recommendations**
   - 侧边栏点击"获取推荐" / Click "Get Recommendations" in sidebar
   - 查看个性化推荐内容 / View personalized recommendations

---

## 🎨 自定义前端 / Customize Frontend

### 修改样式 / Modify Styles

编辑 `enhanced_app.py` 中的 CSS:

```python
st.markdown("""
<style>
    .main-header {
        /* 修改标题样式 / Modify header style */
        background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
    }
    
    .user-message {
        /* 修改用户消息样式 / Modify user message style */
        background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
    }
</style>
""", unsafe_allow_html=True)
```

### 更改主题颜色 / Change Theme Colors

在代码中搜索并替换这些颜色值 / Search and replace these color values:
- `#667eea` - 主要紫色 / Primary purple
- `#764ba2` - 次要紫色 / Secondary purple
- `#f093fb` - 粉红色 / Pink
- `#f5576c` - 红色 / Red

---

## 🐛 故障排除 / Troubleshooting

### 问题 1: 无法连接到 API / Problem 1: Cannot Connect to API

**症状 / Symptoms**: 前端显示 "系统离线" / Frontend shows "System Offline"

**解决方案 / Solutions**:
1. 确保后端正在运行 / Make sure backend is running:
   ```bash
   python -m src.api.app
   ```

2. 检查端口是否正确 / Check if port is correct:
   ```bash
   # 检查 8000 端口是否被占用 / Check if port 8000 is in use
   lsof -i :8000  # Mac/Linux
   netstat -ano | findstr :8000  # Windows
   ```

3. 检查防火墙设置 / Check firewall settings

### 问题 2: 千问 API 错误 / Problem 2: Qianwen API Error

**症状 / Symptoms**: 收到 "API 服务未正确配置" / "API service not properly configured"

**解决方案 / Solutions**:
1. 确认 `.env` 文件中的 API 密钥正确 / Verify API key in `.env`:
   ```bash
   cat .env | grep DASHSCOPE_API_KEY
   ```

2. 测试 API 密钥 / Test API key:
   ```python
   import dashscope
   dashscope.api_key = "your_key"
   # 尝试调用 / Try calling
   ```

3. 检查网络连接和 API 配额 / Check network and API quota

### 问题 3: 依赖安装失败 / Problem 3: Dependency Installation Failed

**解决方案 / Solutions**:
```bash
# 升级 pip / Upgrade pip
pip install --upgrade pip

# 分步安装 / Install step by step
pip install fastapi uvicorn
pip install streamlit
pip install transformers torch
pip install sentence-transformers
pip install dashscope
```

### 问题 4: spaCy 模型未找到 / Problem 4: spaCy Model Not Found

**解决方案 / Solutions**:
```bash
# 下载 spaCy 英语模型 / Download spaCy English model
python -m spacy download en_core_web_sm

# 如果上述命令失败 / If above fails
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0.tar.gz
```

---

## 📚 更多资源 / More Resources

- **API 文档 / API Documentation**: `docs/API.md`
- **部署指南 / Deployment Guide**: `docs/DEPLOYMENT.md`
- **安全说明 / Security**: `SECURITY.md`
- **实现总结 / Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`

---

## 💡 使用建议 / Usage Tips

1. **首次运行 / First Run**:
   - 使用增强版前端获得最佳体验 / Use enhanced frontend for best experience
   - 启用 RAG 模式获得更准确的回答 / Enable RAG for more accurate answers

2. **性能优化 / Performance Optimization**:
   - 如果响应慢，检查知识库大小 / If slow, check knowledge base size
   - 考虑使用 Redis 缓存 / Consider using Redis cache

3. **开发建议 / Development Tips**:
   - 使用 `--reload` 参数自动重载 / Use `--reload` for auto-reload
   - 查看日志文件排查问题 / Check log files for troubleshooting

---

## 📞 支持 / Support

如有问题，请：
If you have issues:

1. 查看日志文件 / Check log files: `data/logs/`
2. 阅读完整文档 / Read full documentation
3. 提交 Issue 到 GitHub / Submit issue to GitHub

---

**祝使用愉快！/ Enjoy using the system!** 🚀
