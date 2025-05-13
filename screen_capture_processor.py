from data_process.vision.auto_screen_capture import ScreenCapturer

from data_process.vision.image_extractor import ImageExtractor

from data_process.vision.image_to_base64 import ImageProcessor

from LLM.embedding_llm import GuiJiEmbedding

from langchain_chroma import Chroma

from langchain_core.documents import Document

import os

class ScreenCaptureProcessor:
    """
    进行屏幕截屏以
    及查询和检索
    """
    def __init__(self):
        # 创建专用保存截取图片的文件夹(但每张图片处理完后会立即删掉)
        self.save_dir = "screen_capture_save"

        # 实例化各个组件
        self.image_processor = ImageProcessor()
        self.image_extractor = ImageExtractor()
        self.screen_capture = ScreenCapturer(self.save_dir)
        self.guiji_embedding = GuiJiEmbedding()

        # 创建Chroma数据库(使用余弦相似度)
        self.vector_store = Chroma(
            collection_name="ScreenInformation",
            embedding_function=self.guiji_embedding,
            persist_directory="./chroma_langchain_db",
            collection_metadata={"hnsw:space": "cosine"}
        )

    def process_screen_capture(self, n=100):
        """
        用于进行自动化截屏
        、处理、入库的操作
        """
        # 获取屏幕生成器实例
        generator = self.screen_capture.screen_capture_generator()
        for _ in range(n):
            # 获取生成器数据，返回值为列表，第一个返回值代表文件路径，第二个返回值代表unix时间戳，类型为float类型
            res = next(generator)
            filepath, unix_timestamp = res[0], res[1]

            # 处理图像
            base64_filepath = self.image_processor.image_to_base64(image_path=filepath)
            print(base64_filepath)
            text = self.image_extractor.extract_one(base64_filepath)

            # 创建文档并持久化添加到向量数据库中
            documents = [
                Document(
                    page_content=text,
                    metadata={
                        "unix_timestamp": unix_timestamp
                    }
                )
            ]
            self.vector_store.add_documents(documents=documents)

            # 删除图像文件
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                print(f"文件删除失败{filepath}, 错误是{e}")
        