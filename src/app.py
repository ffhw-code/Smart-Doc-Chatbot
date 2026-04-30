import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

from src.document_loader import load_document
from src.rag_engine import RAGEngine

# 构建对话历史函数
def build_conversation_context(messages: list, max_turns: int = 5) -> str:
    """
    从消息历史中构建对话上下文
    :param messages: 消息列表，每个元素为 {"role": "user" 或 "assistant", "content": "..."}
    :param max_turns: 保留的最大对话轮数
    :return: 格式化的对话历史字符串
    """
    # 只保留最近 max_turns 轮对话
    recent_messages = messages[-(max_turns * 2):] if len(messages) > max_turns * 2 else messages
    context = ""
    for msg in recent_messages:
        if msg["role"] == "user":
            context += f"用户: {msg['content']}\n"
        else:
            context += f"助手: {msg['content']}\n"
    return context

load_dotenv()  
# 读取 API Key
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("请在 .env 文件中设置 DASHSCOPE_API_KEY")

# 页面设置
st.set_page_config(page_title="智能文档问答助手", page_icon="🤖")
st.title("📄 智能文档问答助手")
st.markdown("上传 TXT、PDF 或 Word 文档，然后问我关于文件内容的问题。")

# 建立 OpenAI 客户端（兼容阿里云）
client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

# 初始化 session_state 变量
if "doc_content" not in st.session_state:
    st.session_state.doc_content = ""

if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ========== 文件上传（支持 TXT, PDF, DOCX） ==========
uploaded_file = st.file_uploader(
    "上传文档（支持 TXT, PDF, DOCX）", 
    type=["txt", "pdf", "docx"]
)

# 处理上传的文件
if uploaded_file is not None:
    with st.spinner("正在解析文档，请稍候..."):
        content = load_document(uploaded_file)
    st.session_state.doc_content = content
    
    # 清空之前的文档内容，避免旧文档影响
    st.session_state.rag_engine.clear()
    
    # 将解析后的文档添加到 RAG 引擎
    with st.spinner("正在构建知识库索引..."):
        st.session_state.rag_engine.add_document(
            content, 
            metadata={"filename": uploaded_file.name}
        )
    
    st.success("文件上传成功！")
    # 清空文档改变前前的对话记录
    st.session_state.messages = []
    with st.expander("查看文档预览"):
        st.text(content[:500] + ("..." if len(content) > 500 else ""))

# ========== 用户输入问题 ==========
question = st.text_input("请输入你的问题：")

# ========== 回答按钮 ==========
if st.button("提问"):
    if not question:
        st.warning("请先输入问题")
    elif not st.session_state.doc_content:
        st.warning("请先上传文档")
    else:
        # 保存用户问题到历史
        st.session_state.messages.append({"role": "user", "content": question})
        
        # 检索相关内容（RAG）
        with st.spinner("正在检索相关内容..."):
            retrieved_chunks = st.session_state.rag_engine.search(question, top_k=3)
        
        if not retrieved_chunks:
            st.warning("未能找到相关内容，请尝试其他问题。")
            st.stop()
        
        # 将检索到的内容块拼接成上下文
        context = "\n\n".join([chunk for chunk, _ in retrieved_chunks])
        
        # 构建对话历史
        conversation_history = build_conversation_context(st.session_state.messages)
        
        # 构造完整的提示词
        prompt = f"""你是一个智能文档助手。请根据以下提供的文档内容回答用户的问题。
如果文档中没有相关信息，请明确说"文档中没有提到"。

提供的相关内容：
{context}

对话历史：
{conversation_history if conversation_history else "(无历史记录)"}

用户问题：{question}

请给出简洁、准确的回答："""
        
        with st.spinner("AI 思考中..."):
            response = client.chat.completions.create(
                model="qwen-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            answer = response.choices[0].message.content
        
        # 保存 AI 回答到历史
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # 显示回答
        st.success("回答：")
        st.write(answer)
        
        # 显示检索来源（可折叠）
        with st.expander("查看回答依据"):
            for i, (chunk, score) in enumerate(retrieved_chunks):
                st.markdown(f"**来源 {i+1} (相关度: {score:.2f})**")
                st.text(chunk)