import io
import os
from typing import List

import PyPDF2
from docx import Document

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    从PDF文件的字节流中提取文本。
    :param file_bytes: PDF文件的原始字节数据
    :return: 提取出的全部文本
    """
    text = ""
    try:
        # 使用PyPDF2的PdfFileReader来读取PDF文件内容
        # 注意：参数需要是一个字节流对象
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        # 遍历每一页
        for page_num in range(len(pdf_reader.pages)):
            # 提取当前页的文本
            page_text = pdf_reader.pages[page_num].extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        text = f"解析PDF时出错: {str(e)}"
    return text

def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    从Word文件的字节流中提取文本。
    :param file_bytes: Word文件的原始字节数据
    :return: 提取出的全部文本
    """
    text = ""
    try:
        # 使用python-docx的Document类读取Word文件
        # 参数需要是一个字节流对象
        doc = Document(io.BytesIO(file_bytes))
        # 遍历文档中的每一个段落
        for para in doc.paragraphs:
            if para.text:
                text += para.text + "\n"
    except Exception as e:
        text = f"解析Word文档时出错: {str(e)}"
    return text

def extract_text_from_txt(file_bytes: bytes) -> str:
    """提取TXT文件的文本"""
    try:
        # 尝试以UTF-8编码解码
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        # 如果UTF-8解码失败，尝试GBK编码（常见于中文文档）
        try:
            return file_bytes.decode("gbk")
        except Exception as e:
            return f"解析TXT文件时出错: {str(e)}"

def load_document(file) -> str:
    """
    根据文件类型路由到对应的解析函数，并返回提取的文本。
    :param file: Streamlit的UploadedFile对象
    :return: 文档的文本内容
    """
    # 获取上传文件对象的原始字节数据
    file_bytes = file.getvalue()
    # 获取文件名并转为小写以安全地判断后缀
    file_name = file.name.lower()
    
    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif file_name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif file_name.endswith(".txt"):
        return extract_text_from_txt(file_bytes)
    else:
        return "不支持的文件格式，请上传 PDF、DOCX 或 TXT 文件。"