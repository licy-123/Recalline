from langchain_core.embeddings import Embeddings

from dotenv import load_dotenv

import requests

import os

from typing import List

from tenacity import retry, stop_after_attempt, wait_exponential

# 加载环境
load_dotenv()


class GuiJiEmbedding(Embeddings):
    """
    增强版的词嵌入类，包含错误处理和重试机制
    """

    def __init__(self):
        self.model = "BAAI/bge-m3"
        self.api_key = os.getenv("GUIJI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到GUIJI_API_KEY环境变量")

        self.url = "https://api.siliconflow.cn/v1/embeddings"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.timeout = 30  # 请求超时时间(秒)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _call_api(self, payload: dict) -> dict:
        """封装API调用逻辑"""
        try:
            response = requests.post(
                self.url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()  # 自动处理HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API请求失败: {str(e)}")

    def _validate_response(self, res: dict) -> None:
        """验证API返回格式"""
        if not isinstance(res, dict):
            raise ValueError("API返回格式无效: 非字典类型")
        if 'data' not in res or not isinstance(res['data'], list):
            raise ValueError("API返回缺少data字段或data非列表")
        if len(res['data']) == 0:
            raise ValueError("API返回的data为空")

    def embed_query(self, text: str) -> List[float]:
        """嵌入单个文档（带完整错误处理）"""
        if not text or not isinstance(text, str):
            raise ValueError("输入文本必须是非空字符串")

        payload = {
            "model": self.model,
            "input": text,
            "encoding_format": "float"
        }

        try:
            res = self._call_api(payload)
            self._validate_response(res)
            return res['data'][0]['embedding']
        except Exception as e:
            # 生产环境建议记录日志
            print(f"嵌入查询失败: {str(e)}")
            return [0.0] * 1024  # 返回与模型维度相同的零向量

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入多个文档（带完整错误处理）"""
        if not texts or not isinstance(texts, list):
            raise ValueError("输入必须是非空字符串列表")

        payload = {
            "model": self.model,
            "input": texts,
            "encoding_format": "float"
        }

        try:
            res = self._call_api(payload)
            self._validate_response(res)
            return [item['embedding'] for item in res['data']]
        except Exception as e:
            print(f"批量嵌入失败: {str(e)}")
            return [[0.0] * 1024 for _ in texts]  # 返回与模型维度相同的零向量列表

