from LLM.vision_llm import vision_llm

class ImageExtractor:
    """一个用于利用视觉模型提取图片信息的类"""
    def __init__(self):
        self.vision_llm = vision_llm
        self.system_prompt = """
        你是一个信息提取专家，负责提取图片中的信息，你的任务是完整提取桌面上正在运行的应用里的信息。
        注意：不需要提取桌面上的信息，也不需要提取应用本身不变的静态信息，只需提取应用中不同场景都不一样的动态信息，
        并且不要说其他任何多余的话。
        """
        self.user_instruction = """
        你是一个信息提取专家，负责提取图片中的信息，你的任务是完整提取桌面上正在运行的应用里的信息。
        注意：不需要提取桌面上的信息，也不需要提取应用本身不变的静态信息，只需提取应用中不同场景都不一样的动态信息，
        并且不要说其他任何多余的话。
        """
    def extract_one(self, base64_filepath: str) -> str:
        """利用视觉模型来提取经过Base64编码后的图片中的信息"""
        try:
            completion = self.vision_llm.chat.completions.create(
                model="qwen2.5-vl-72b-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": self.system_prompt}],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": base64_filepath
                                },
                            },
                            {"type": "text", "text": self.user_instruction},
                        ],
                    },
                ],
            )
            print(completion.choices[0].message.content)
            return completion.choices[0].message.content
        except Exception as e:
            print(f"API调用失败: {str(e)}")
            return "信息提取失败"  # 或抛出特定异常
