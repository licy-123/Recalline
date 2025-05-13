from dotenv import load_dotenv

from openai import OpenAI

import os

load_dotenv()

vision_llm = OpenAI(
    api_key=os.getenv("QIANWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
