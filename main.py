import threading

from langchain_core.documents import Document

from screen_capture_processor import ScreenCaptureProcessor

from query_system import QuerySystem

from concurrent.futures import ThreadPoolExecutor

from typing import Union

from dataclasses import dataclass

import time

@dataclass
class TaskConfig:
    """任务配置类"""
    name: str
    method: str
    kwargs: dict
    daemon: bool = True

class TaskManager:
    def __init__(self):
        # 初始化核心组件
        self.screen_capture_processor = ScreenCaptureProcessor()
        self.query_system = QuerySystem(self.screen_capture_processor)

        # 线程控制相关
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        self._active_tasks = dict()
        self._lock = threading.Lock()

    def _run_task(self, config: TaskConfig):
        """实际执行任务的内部方法"""
        try:
            if config.method == "capture":
                self.screen_capture_processor.process_screen_capture(**config.kwargs)
            elif config.method == "time_query":
                return self.query_system.time_based_query(**config.kwargs)
            elif config.method == "semantic_query":
                return self.query_system.semantic_query(**config.kwargs)
        except Exception as e:
            print(f"{config.name}任务执行失败:{e}")
        finally:
            with self._lock:
                del self._active_tasks[config.name]

    def start_task(self, config: TaskConfig):
        """
        启动新任务线程
        :param config:任务配置
        """
        with self._lock:
            if config.name in self._active_tasks:
                raise ValueError(f"任务名称冲突:{config.name}")

            future = self._thread_pool.submit(self._run_task, config)
            self._active_tasks[config.name] = future

    def stop_task(self, task_name: str):
        """停止指定任务"""
        with self._lock:
            if future := self._active_tasks.get(task_name):
                future.cancel()
                del self._active_tasks[task_name]

    def get_task_result(self, task_name: str, timeout:float=None) -> Union[list[Document], str, None]:
        """
        获取任务结果
        :param task_name: 任务名称
        :param timeout: 超时时间(秒)
        :return: 各方法的类型：
        - capture: None
        - time_query: list[Document]
        - semantic_query: str
        """
        with self._lock:
            if future := self._active_tasks.get(task_name):
                return future.result(timeout=timeout)

    def shutdown(self):
        """安全关闭所有任务"""
        self._thread_pool.shutdown(wait=True)


if __name__ == "__main__":
    # 实例化任务管理器对象
    manager = TaskManager()

    try:
        # 启动
        manager.start_task(TaskConfig(
            name="实时截屏",
            method="capture",
            kwargs={"n": 10},
            daemon=True
        ))

        # 主线程等待，防止立即退出
        while True:
            # 这里可以添加其他逻辑或简单的sleep
            # 或者等待用户输入来退出
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n接收到中断信号，准备退出...")
    finally:
        # 确保资源被正确清理
        manager.shutdown()
        print("程序已安全退出")