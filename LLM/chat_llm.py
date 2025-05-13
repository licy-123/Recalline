from langchain_deepseek import ChatDeepSeek

from dotenv import load_dotenv

import os

load_dotenv()

chat_llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)