# Windows 用户指南 / Windows User Guide

## 🪟 Windows 平台运行指南

本文档专门为 Windows 用户提供详细的安装和运行指南。

---

## 📋 常见问题解答

### ❓ 什么是 `#!/usr/bin/env python3`？

这是一个 **Shebang**（释伴）行，是 Unix/Linux 系统的特殊标记：

- **作用**: 告诉 Unix/Linux 系统使用哪个解释器来运行脚本
- **格式**: `#!` + 解释器路径
- **位置**: 必须在文件第一行

**重要**: Windows 系统**不支持** shebang，会将其视为普通注释。

---

### ❌ 为什么出现 "无法将 '/usr/bin/env' 项识别为 cmdlet" 错误？

**错误原因**:
- PowerShell 试图将 shebang 行当作命令执行
- `/usr/bin/env` 是 Unix/Linux 路径，Windows 中不存在

**解决方案**:
在 Windows 上运行 Python 脚本时，**必须显式使用 `python` 命令**：

```powershell
# ❌ 错误的运行方式（Unix/Linux 风格）
./run.py
.\run.py

# ✅ 正确的运行方式（Windows）
python run.py
```

---

## 🚀 在 Windows 上运行项目

### 步骤 1: 检查 Python 安装

```powershell
# 检查 Python 版本（需要 3.8+）
python --version

# 如果上面的命令不工作，尝试
python3 --version
py --version
```

**没有安装 Python？**
- 访问: https://www.python.org/downloads/
- 下载并安装 Python 3.8 或更高版本
- ⚠️ 安装时勾选 "Add Python to PATH"

---

### 步骤 2: 克隆项目到 D 盘

```powershell
# 进入 D 盘
D:

# 创建项目文件夹（例如）
mkdir D:\Projects
cd D:\Projects

# 克隆仓库
git clone https://github.com/SolendadModle/RAG-based-Intelligent-Customer-Service.git

# 进入项目目录
cd RAG-based-Intelligent-Customer-Service

# 切换到开发分支
git checkout copilot/design-customer-service-system
```

---

### 步骤 3: 创建虚拟环境

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（PowerShell）
.\venv\Scripts\Activate.ps1

# 如果遇到执行策略错误，运行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 或者使用 CMD 激活：
# venv\Scripts\activate.bat
```

---

### 步骤 4: 安装依赖

```powershell
# 升级 pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 下载 spaCy 模型
python -m spacy download en_core_web_sm
```

---

### 步骤 5: 配置环境变量

```powershell
# 复制配置文件
copy .env.example .env

# 使用记事本编辑 .env 文件
notepad .env
```

在 `.env` 文件中配置您的 Qianwen API 密钥：
```bash
DASHSCOPE_API_KEY=sk-your-actual-api-key-here
QIANWEN_MODEL=qwen-turbo
```

---

### 步骤 6: 运行项目

#### 方式 1: 一键启动（推荐）

```powershell
# 同时启动后端和前端
python run.py
```

#### 方式 2: 分别启动

**终端 1 - 启动后端**:
```powershell
python -m src.api.app
```

**终端 2 - 启动前端**（选择一个）:
```powershell
# 基础版前端
streamlit run src/frontend/streamlit_app.py

# 增强版前端（推荐）
streamlit run src/frontend/enhanced_app.py
```

---

## 🔧 Windows 特定问题排查

### 问题 1: 命令未找到错误

**错误**: `'python' 不是内部或外部命令`

**解决方案**:
1. 检查 Python 是否已安装
2. 将 Python 添加到系统 PATH:
   - 右键"此电脑" → "属性" → "高级系统设置"
   - "环境变量" → 编辑 "Path"
   - 添加 Python 安装路径（例如: `C:\Python39\`）

---

### 问题 2: 执行策略错误

**错误**: `无法加载文件，因为在此系统上禁止运行脚本`

**解决方案**:
```powershell
# 更改执行策略（管理员权限）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### 问题 3: 端口被占用

**错误**: `Port 8000 is already in use`

**解决方案**:
```powershell
# 查找占用端口的进程
netstat -ano | findstr :8000

# 结束进程（将 PID 替换为实际进程 ID）
taskkill /PID <PID> /F
```

---

### 问题 4: 模块导入错误

**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```powershell
# 确保虚拟环境已激活
.\venv\Scripts\Activate.ps1

# 重新安装依赖
pip install -r requirements.txt
```

---

## 📝 Windows 运行脚本对比

### Unix/Linux 风格（❌ Windows 不支持）
```bash
#!/usr/bin/env python3  # Shebang 行
chmod +x run.py         # 添加执行权限
./run.py                # 直接运行
```

### Windows 风格（✅ 正确方式）
```powershell
# 不需要 shebang 或执行权限
python run.py           # 使用 python 命令运行
```

---

## 🎯 快速命令参考

```powershell
# 检查 Python 版本
python --version

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（PowerShell）
.\venv\Scripts\Activate.ps1

# 激活虚拟环境（CMD）
venv\Scripts\activate.bat

# 安装依赖
pip install -r requirements.txt

# 运行项目
python run.py

# 停止服务
# 按 Ctrl + C
```

---

## 💡 最佳实践

1. **使用 PowerShell 或 CMD**
   - PowerShell（推荐）: 功能更强大
   - CMD: 传统命令行，兼容性好

2. **使用虚拟环境**
   - 隔离项目依赖
   - 避免包版本冲突

3. **配置正确的路径**
   - 使用绝对路径或相对路径
   - Windows 使用反斜杠 `\` 或正斜杠 `/`

4. **注意文件编码**
   - 推荐使用 UTF-8 编码
   - 避免中文路径名称

---

## 📞 获取帮助

如果遇到其他问题：

1. 查看完整文档: `docs/USAGE_GUIDE.md`
2. 查看 API 文档: `docs/API.md`
3. 检查 GitHub Issues
4. 查看项目 README.md

---

## 🌟 Windows 推荐工具

- **Windows Terminal**: 现代化终端（推荐）
- **Git for Windows**: Git 客户端
- **VS Code**: 代码编辑器
- **PyCharm**: Python IDE

---

**最后更新**: 2026-01-13  
**版本**: 1.0.0
