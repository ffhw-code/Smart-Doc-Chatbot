# 智能文档问答助手

基于 RAG（检索增强生成）的文档智能问答系统。支持上传 TXT、PDF、Word 文档，通过大语言模型（阿里云百炼）和本地向量检索，实现精准、可追溯的对话式问答。

##  功能特点

-  支持多种文档格式：TXT、PDF、DOCX
-  基于 RAG 的智能检索：先检索相关片段，再生成回答
-  多轮对话记忆：保留对话历史，支持上下文连续提问
-  检索来源可视化：展示参考答案的文档片段和相似度
-  本地向量数据库（ChromaDB），无需联网即可检索
-  清爽的 Web 界面（Streamlit），开箱即用

##  技术栈

| 类别 | 技术 |
|------|------|
| 前端/界面 | Streamlit |
| 大模型 API | 阿里云百炼（兼容 OpenAI 接口） |
| 文本分割 | LangChain Text Splitters |
| 嵌入模型 | sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2) |
| 向量数据库 | ChromaDB |
| 文件解析 | PyPDF2, python-docx |
| 环境管理 | Python-dotenv |

## 项目结构
```
AI_QA/
├── src/
│   ├── app.py
│   ├── document_loader.py
│   └── rag_engine.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```



## 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/你的用户名/仓库名.git
cd 仓库名
```

### 2. 创建并激活虚拟环境（推荐 conda）
```bash
conda create -n doc_qa python=3.10 -y
conda activate doc_qa
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```
> 注意：sentence-transformers 会下载模型（约 1.2 GB），首次运行会自动下载到 `~/.cache/huggingface/`。

### 4. 配置 API 密钥
复制 `.env.example` 为 `.env`，并填入你的阿里云百炼 API Key：
```bash
cp .env.example .env
```
编辑 `.env` 文件：
```
DASHSCOPE_API_KEY=sk-你的真实密钥
```
> 如果不想用 `.env`，也可以在系统环境变量中设置 `DASHSCOPE_API_KEY`。

### 5. 运行应用
```bash
streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
```
然后在浏览器中打开 `http://localhost:8501`。


## 使用说明

1. 上传文档（TXT/PDF/DOCX）
2. 等待文档解析和向量索引完成（首次会稍慢）
3. 在输入框中提问，点击“提问”
4. 获得基于文档内容的回答，并可展开查看检索来源
5. 支持连续提问，模型会记住历史对话

## 注意事项

- **嵌入模型路径**：当前 `rag_engine.py` 中使用了绝对路径加载 sentence-transformers 模型。如果你的模型缓存位置不同，请修改为你的实际路径，或者改为自动下载模式（注释掉长路径，直接使用模型名称 `paraphrase-multilingual-MiniLM-L12-v2`）。
- **向量数据库**：ChromaDB 会在项目根目录创建 `chroma_db/` 文件夹，请勿手动删除。该文件夹已加入 `.gitignore`，不会上传至 GitHub。
- **API 调用**：使用阿里云百炼服务，新用户有免费额度（百万 tokens）。确保你的账户已开通百炼服务并有余额/免费额度。

## 贡献与反馈

欢迎提交 Issue 或 Pull Request。如有任何问题，请联系 [3498139556@qq.com] 或提交 GitHub Issue。

## 许可证

MIT

## 致谢

- 阿里云百炼提供的模型 API
- LangChain、sentence-transformers、ChromaDB 等开源项目
- DeepSeek 在开发过程中提供的代码辅助