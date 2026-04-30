import hashlib
from typing import List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

class RAGEngine:
    """一个集成了文本分块、向量化和检索的RAG引擎"""
    
    def __init__(self, collection_name: str = "doc_collection"):
        # 1. 初始化嵌入模型（使用本地模型，免费且隐私安全）
        # 这是一个轻量级的多语言模型，完全免费，能在你的电脑上运行
        self.embedding_model = SentenceTransformer('/home/lty/.cache/huggingface/hub/models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2/snapshots/e8f8c211226b894fcb81acc59f3b34ba3efd5f42')
        
        # 2. 初始化ChromaDB客户端（使用本地持久化存储）
        # 这样即使程序重启，已处理的文档也无需重复处理
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # 3. 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度进行检索
        )
        
        # 4. 初始化文本分割器
        # 将长文本分割成适合检索的小块
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,      # 每个文本块的最大长度（字符数）
            chunk_overlap=50,    # 相邻块之间的重叠字符数，保持上下文连贯性
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )
    
    def _get_document_hash(self, text: str) -> str:
        """计算文档的哈希值，用于判断文档是否已存在"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def add_document(self, doc_text: str, metadata: dict = None):
        """
        将文档添加到向量数据库
        :param doc_text: 文档的原始文本
        :param metadata: 文档的元数据，如文件名
        """
        # 检查文档是否已存在
        doc_hash = self._get_document_hash(doc_text)
        existing = self.collection.get(where={"doc_hash": doc_hash})
        if existing['ids']:
            return
        
        # 1. 文本分块
        chunks = self.text_splitter.split_text(doc_text)
        
        if not chunks:
            return
            
        # 2. 生成嵌入向量
        embeddings = self.embedding_model.encode(chunks)
        
        # 3. 准备数据并存入ChromaDB
        ids = [f"{doc_hash}_{i}" for i in range(len(chunks))]
        metadatas = [{"doc_hash": doc_hash, "chunk_index": i, **(metadata or {})} for i in range(len(chunks))]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=metadatas
        )
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        根据查询文本检索最相关的内容块
        :param query: 用户问题
        :param top_k: 返回最相关的内容块数量
        :return: 内容块列表，每个元素为 (文本内容, 相关度分数)
        """
        if self.collection.count() == 0:
            return []
        
        # 1. 将查询文本转换为向量
        query_embedding = self.embedding_model.encode([query])[0]
        
        # 2. 在集合中检索相似内容
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # 3. 整理检索结果
        retrieved_chunks = []
        if results['documents'] and results['distances']:
            for doc, dist in zip(results['documents'][0], results['distances'][0]):
                retrieved_chunks.append((doc, 1 - dist))  # 将余弦距离转换为相似度
        return retrieved_chunks
    
    def clear(self):
        """清空当前集合中的所有数据"""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def get_document_count(self) -> int:
        """获取当前数据库中的文档数量"""
        return self.collection.count()