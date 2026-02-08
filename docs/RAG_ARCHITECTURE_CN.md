# RAG架构说明：general_question处理流程与knowledge_base作用

## 问题解答

### 1. general_question 是如何生成回答的？

**答案：基于RAG（检索增强生成）回答，而非直接调用千问API。**

#### 详细流程

当系统识别到 `general_question` 意图时，处理流程如下：

```
用户问题 → NLU意图识别 → Dialog Handler → RAG Generator → 千问API
                                                ↑
                                         Knowledge Base检索
```

#### 代码实现分析

**步骤1：意图识别** (`src/nlu/intent_recognition.py`)
```python
# 当置信度低于阈值时，默认识别为 general_question
if combined_score < self.threshold:
    return "general_question", combined_score
```

**步骤2：Dialog Handler调用RAG Generator** (`src/dialog/dialog_handler.py`, 第91-97行)
```python
# generate_response默认使用RAG
use_rag = kwargs.get('use_rag', True)  # 默认为True
response = self.rag_generator.generate_response(
    query=message,
    conversation_history=formatted_history,
    use_rag=use_rag,  # 传递use_rag参数
    **kwargs
)
```

**步骤3：RAG Generator执行检索+生成** (`src/generation/rag_generator.py`, 第48-63行)
```python
if use_rag:
    # 1. 从knowledge base检索相关上下文
    context = self.retrieval_service.retrieve_context(query)
    
    # 2. 格式化对话历史
    history_str = format_conversation_history(conversation_history)
    
    # 3. 构建RAG提示词，包含检索到的上下文
    rag_template = self.prompt_templates.get('rag', '')
    prompt = rag_template.format(
        context=context,      # 检索到的知识库内容
        history=history_str,  # 对话历史
        question=query        # 用户问题
    )
else:
    # 仅在use_rag=False时才直接使用问题（不带知识库上下文）
    prompt = query
```

**步骤4：调用千问API生成最终回答** (`src/generation/rag_generator.py`, 第69-74行)
```python
# 将RAG构建的prompt（包含知识库上下文）发送给千问API
response = self.qianwen_client.generate(
    prompt=prompt,           # RAG构建的完整提示（含知识库内容）
    system_prompt=system_prompt,
    history=conversation_history,
    **kwargs
)
```

### 关键结论

1. **`general_question` 默认使用RAG**：即使是通用问题，系统也会：
   - 先从knowledge base检索相关信息
   - 将检索到的内容注入到提示词中
   - 然后调用千问API基于这些上下文生成回答

2. **不是直接调用千问API**：
   - 千问API收到的不是原始用户问题
   - 而是包含了knowledge base检索内容的完整提示词
   - 格式：`Context: {检索内容}\n\nHistory: {历史}\n\nQuestion: {问题}`

3. **可以关闭RAG**：
   - 在API调用时传递 `use_rag=False`
   - 此时才会跳过knowledge base检索，直接将问题发送给千问API

---

## 2. Knowledge Base的作用

### 核心功能

Knowledge Base在RAG系统中扮演**外部知识源**的角色，提供以下功能：

#### 2.1 文档管理 (`src/knowledge_base/kb_manager.py`)

**支持的数据源类型：**
```yaml
# config/config.yaml
knowledge_base:
  sources:
    - type: "faq"              # FAQ问答对
      path: "./data/knowledge_base/faq.json"
    - type: "documents"        # 文本文档
      path: "./data/knowledge_base/documents/"
```

**加载的文档示例：**
```python
# FAQ格式
{
  "question": "如何重置密码？",
  "answer": "您可以通过以下步骤重置密码：1. 点击登录页面的'忘记密码'...",
  "category": "account"
}

# 文档格式：纯文本文件或JSON文档
```

#### 2.2 向量检索 (`src/knowledge_base/retrieval.py`)

**技术栈：**
- **FAISS**: Facebook的向量相似度搜索库
- **sentence-transformers**: 文本嵌入模型 (all-MiniLM-L6-v2)
- **Embedding维度**: 384维向量

**检索流程：**
```python
1. 将用户问题转换为384维向量
2. 在FAISS索引中搜索最相似的top_k个文档
3. 过滤相似度 < 阈值(0.7)的结果
4. 返回相关文档内容作为context
```

**配置参数：**
```yaml
knowledge_base:
  retrieval:
    top_k: 5                    # 返回最相关的5个文档
    similarity_threshold: 0.7    # 相似度阈值
    max_context_length: 2000     # 最大上下文长度（字符）
```

#### 2.3 提供上下文给LLM

Knowledge Base检索到的内容会注入到提示词中：

```
Context: {从knowledge base检索的相关文档内容}

Conversation History: {之前的对话}

User Question: {当前问题}

Please provide a helpful and accurate response based on the context above.
```

### Knowledge Base的关键价值

1. **减少幻觉（Hallucination）**
   - 千问API基于真实的knowledge base内容回答
   - 而不是凭空生成，提高回答准确性

2. **领域知识增强**
   - 注入企业/产品特定的知识
   - 千问通用模型 + 专业知识库 = 专业客服

3. **动态更新知识**
   - 无需重新训练模型
   - 更新FAQ或文档即可改变系统行为

4. **降低API成本**
   - 提供精准上下文，减少API tokens消耗
   - 避免反复调用API澄清信息

---

## 3. 完整数据流示例

### 用户提问："你们的退货政策是什么？"

#### Step 1: 意图识别
```
输入: "你们的退货政策是什么？"
输出: intent="general_question", confidence=0.75
```

#### Step 2: Knowledge Base检索
```python
# 查询向量化
query_vector = embed("你们的退货政策是什么？")

# FAISS搜索
top_documents = faiss_index.search(query_vector, k=5)

# 检索结果（示例）
context = """
1. 退货政策FAQ: 我们提供30天无理由退货服务。商品需保持原包装完好...
2. 退货流程文档: 第一步：登录账户，找到订单...
3. 退货条件说明: 不影响二次销售的商品可以退货...
"""
```

#### Step 3: 构建RAG提示
```
Context: 
1. 退货政策FAQ: 我们提供30天无理由退货服务。商品需保持原包装完好...
2. 退货流程文档: 第一步：登录账户，找到订单...
3. 退货条件说明: 不影响二次销售的商品可以退货...

Conversation History: (空)

User Question: 你们的退货政策是什么？

Please provide a helpful and accurate response based on the context above.
```

#### Step 4: 千问API生成回答
```
千问接收到包含knowledge base上下文的完整提示
↓
基于上下文生成准确回答
↓
返回: "我们为您提供30天无理由退货服务。退货条件如下：
1. 商品需保持原包装完好，不影响二次销售
2. 退货流程：登录账户 → 找到订单 → 申请退货 → 等待审核
..."
```

---

## 4. 与纯LLM对话的对比

### 场景：询问公司特定的退货政策

| 方式 | 处理流程 | 回答质量 | 风险 |
|------|---------|---------|------|
| **纯千问API** | 直接发送问题给千问 | 可能给出通用答案 | 可能不符合公司实际政策（幻觉风险） |
| **RAG系统** | 检索知识库 → 注入上下文 → 千问生成 | 基于真实政策文档 | 低风险，答案准确且符合实际 |

### 示例对比

**纯千问API回答（无知识库）：**
```
"一般情况下，商品在收到后7-14天内可以退货，具体取决于商品类别..."
```
❌ 可能与公司实际30天政策不符

**RAG系统回答（有知识库）：**
```
"根据我们的退货政策，您可以在收到商品后30天内申请无理由退货。
退货需满足以下条件：1. 商品包装完好 2. 不影响二次销售..."
```
✅ 准确反映knowledge base中的真实政策

---

## 5. 技术架构图

```
┌─────────────────────────────────────────────────────────────┐
│                       用户输入问题                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   NLU意图识别与实体提取        │
        │  (intent_recognition.py)      │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │      Dialog Handler           │
        │   (dialog_handler.py)         │
        │   - 会话管理                   │
        │   - 状态追踪                   │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │      RAG Generator            │
        │   (rag_generator.py)          │
        └───────────┬───────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────────┐   ┌─────────────────────┐
│ Knowledge Base   │   │   Qianwen API       │
│ Retrieval        │   │   (DashScope)       │
│ (FAISS + Vector) │   │                     │
└────────┬─────────┘   └──────────┬──────────┘
         │                        │
         │   检索相关上下文         │
         └────────►  组合  ◄────────┘
                    │
                    ▼
            ┌───────────────┐
            │  最终回答      │
            └───────────────┘
```

---

## 6. 配置说明

### 启用/禁用RAG

在API调用中控制：

```python
# 方式1：使用RAG（默认）
response = dialog_handler.process_message(
    message="你们的退货政策是什么？",
    use_rag=True  # 或省略此参数，默认为True
)

# 方式2：禁用RAG，直接调用千问
response = dialog_handler.process_message(
    message="你们的退货政策是什么？",
    use_rag=False  # 跳过knowledge base检索
)
```

### REST API调用

```bash
# 使用RAG（推荐）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你们的退货政策是什么？",
    "use_rag": true
  }'

# 不使用RAG
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你们的退货政策是什么？",
    "use_rag": false
  }'
```

---

## 7. 总结

### general_question的处理方式

✅ **默认使用RAG**：
- Knowledge Base检索 → 上下文注入 → 千问API生成
- 确保回答基于真实知识，减少幻觉

❌ **不是直接调用千问API**：
- 仅在显式设置 `use_rag=False` 时才跳过检索

### Knowledge Base的核心作用

1. **作为外部知识源**：存储FAQ、文档、政策等结构化/非结构化知识
2. **提供检索服务**：使用FAISS向量检索快速找到相关内容
3. **增强生成质量**：为LLM提供准确上下文，避免幻觉
4. **支持知识更新**：无需重训模型，更新文档即可改变系统行为

### 系统优势

- **准确性**：基于真实知识库而非模型记忆
- **可控性**：通过管理知识库内容控制回答
- **可扩展性**：轻松添加新知识而无需重新训练
- **成本优化**：精准上下文减少API tokens消耗

---

## 参考代码位置

- 对话处理：`src/dialog/dialog_handler.py` (第91-97行)
- RAG生成器：`src/generation/rag_generator.py` (第30-84行)
- 知识库管理：`src/knowledge_base/kb_manager.py`
- 检索服务：`src/knowledge_base/retrieval.py`
- 意图识别：`src/nlu/intent_recognition.py` (第146-150行)
- 配置文件：`config/config.yaml` (第38-55行)
