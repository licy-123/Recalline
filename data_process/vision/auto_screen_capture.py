import pyautogui

import time

from typing import Optional, Iterator, Union

from datetime import datetime

import os

class ScreenCapturer:
    """
    定时截屏处理后即时删除(删除文件的操作再主函数中)
    interval：截屏间隔(s)
    max_captures：最大截屏次数(None代表时间无限)
    默认截屏时间间隔为1s，最大截屏次数为无限次
    """
    def __init__(self, save_dir: str, interval: int = 1, max_captures: Optional[int] = None):
        self.interval = interval
        self.max_captures = max_captures
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)  # 自动创建目录

    def screen_capture_generator(self) -> Iterator[list[Union[str, float]]]:
        """返回一个生成器对象，每次截屏的文件名"""
        count = 0
        while True:
            if self.max_captures and count >= self.max_captures:
                break

            # timestamp1是用于计算的Unix时间戳，timestamp2是用于文件名后缀的时间戳str
            unix_timestamp = datetime.now().replace(microsecond=0).timestamp()
            str_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.save_dir, f"screen_capture_{str_timestamp}.png")

            # 截屏保存并返回filename和timestamp
            pyautogui.screenshot(filepath)
            yield [filepath, unix_timestamp]

            count += 1
            time.sleep(self.interval)
