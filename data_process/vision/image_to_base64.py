from PIL import Image

import base64

import io

class ImageProcessor:
    '''
    def image_to_base64(self, image_path: str) -> str:
        """将输入的图片转为Base64格式"""
        with Image.open(image_path) as img:
            # 创建一个二进制字节流缓冲区
            buffer = io.BytesIO()

            # 将图片保存为字节流
            img.save(buffer, format="PNG")

            # 获取字节数据并编码为Base64格式
            img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return img_base64'''

    def image_to_base64(self, image_path: str, format: str = "PNG") -> str:  # 设置默认值
        with Image.open(image_path) as img:
            buffer = io.BytesIO()
            img.save(buffer, format=format)  # 直接使用参数值
            return f"data:image/{format.lower()};base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
