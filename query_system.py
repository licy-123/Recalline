from typing import Optional

from LLM.chat_llm import chat_llm

from data_process.time_str_processor import StrTimeProcessor

class QuerySystem:
    def __init__(self, processor):
        self.processor = processor
        self.vector_store = processor.vector_store
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )
        self.chat_llm = chat_llm
        self.str_time_processor = StrTimeProcessor()

    def semantic_query(self, question: str) -> str:
        # 输入验证
        question = str(question).strip()
        if not question:
            return "问题不能为空"

        try:
            # 1. 获取上下文（使用新版invoke API）
            docs = self.retriever.invoke(question)
            context = "\n".join(d.page_content for d in docs) if docs else "无相关上下文"

            # 2. 构造纯文本提示
            prompt_text = f"""
                根据以下上下文回答问题：

                上下文：
                {context}

                问题：
                {question}

                请直接给出答案：
                """

            # 3. 获取LLM响应并清理内容
            response = self.chat_llm.invoke(prompt_text)
            content = response.content

            # 清理代码块标记
            clean_content = content.replace('```python', '').replace('```', '').strip()

            return clean_content

        except Exception as e:
            return f"查询失败：{str(e)}"


    def time_based_query(self, target_time: Optional[str] = None,
                         start_time: Optional[str] = None,
                         end_time: Optional[str] = None) -> str:
        """
        基于时间查询信息，返回已清理和格式化的内容字符串

        参数:
            target_time: 精确查询时间点
            start_time: 范围查询开始时间
            end_time: 范围查询结束时间

        返回:
            格式化后的内容字符串，包含所有匹配文档的核心内容，
            保持原始格式并用双换行分隔不同文档
        """
        # 构建时间过滤条件
        if target_time is not None:
            target_time = self.str_time_processor.time_str_to_unix_timestamp(target_time)
            where = {"unix_timestamp": {"$eq": target_time}}
        elif start_time is not None and end_time is not None:
            start_time = self.str_time_processor.time_str_to_unix_timestamp(start_time)
            end_time = self.str_time_processor.time_str_to_unix_timestamp(end_time)
            where = {
                "$and": [
                    {"unix_timestamp": {"$gte": start_time}},
                    {"unix_timestamp": {"$lte": end_time}}
                ]
            }
        else:
            raise ValueError("必须提供target_time或(start_time和end_time)")

        try:
            # 获取原始结果
            results = self.vector_store._collection.get(
                where=where,
                include=["documents"]
            )

            # 内容处理流程
            seen = set()  # 去重
            formatted_blocks = []

            for doc in results.get("documents", []):
                # 1. 基础清理
                content = doc.replace('```python', '').replace('```', '').strip()

                # 2. 按行处理
                lines = []
                for line in content.split('\n'):
                    line = line.strip()
                    # 过滤条件：非空行且不是Base64字符串
                    if line and not (line.startswith('+') and len(line) > 20):
                        lines.append(line)

                # 3. 重组内容块
                clean_block = '\n'.join(lines)

                # 4. 去重并收集
                if clean_block and clean_block not in seen:
                    seen.add(clean_block)
                    formatted_blocks.append(clean_block)

            # 5. 用双换行连接所有内容块
            return '\n\n'.join(formatted_blocks)

        except Exception as e:
            print(f"时间查询失败: {str(e)}")
            return ""
