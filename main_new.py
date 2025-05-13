import threading

from screen_capture_processor import ScreenCaptureProcessor

from query_system import QuerySystem

from concurrent.futures import ThreadPoolExecutor, as_completed

from typing import Union, Optional, Set

from dataclasses import dataclass

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
        self.screen_capture_processor = ScreenCaptureProcessor()  # 确保导入
        self.query_system = QuerySystem(self.screen_capture_processor)

        # 线程控制
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        self._active_futures: Set = set()
        self._lock = threading.Lock()
        self._shutdown_initiated = False

    def start_task(self, config: TaskConfig) -> Optional[str]:
        """启动任务并返回任务ID"""
        with self._lock:
            if self._shutdown_initiated:
                raise RuntimeError("任务管理器正在关闭，无法启动新任务")

            future = self._thread_pool.submit(self._safe_run_task, config)
            self._active_futures.add(future)
            future.add_done_callback(lambda f: self._active_futures.discard(f))
            return f"task_{id(future)}"

    def _safe_run_task(self, config: TaskConfig):
        """安全执行任务，捕获所有异常"""
        try:
            if config.method == "capture":
                self.screen_capture_processor.process_screen_capture(**config.kwargs)
            elif config.method == "time_query":
                return self.query_system.time_based_query(**config.kwargs)
            elif config.method == "semantic_query":
                return self.query_system.semantic_query(**config.kwargs)
        except Exception as e:
            print(f"任务失败 [{config.name}]: {str(e)}")
            raise  # 可选：重新抛出异常

    def shutdown(self, timeout: float = 5.0):
        """安全关闭线程池"""
        with self._lock:
            self._shutdown_initiated = True

            # 1. 取消所有未开始的任务
            for future in list(self._active_futures):
                if not future.running():
                    future.cancel()

            # 2. 等待正在运行的任务完成
            done, not_done = [], list(self._active_futures)
            if not_done:
                done, not_done = as_completed(not_done, timeout=timeout), []
                for future in done:
                    if future.exception():
                        print(f"任务异常: {future.exception()}")

            # 3. 强制关闭线程池
            self._thread_pool.shutdown(wait=False)

            if not_done:
                print(f"警告: {len(not_done)}个任务未完成")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

if __name__ == "__main__":

    # 实例化任务管理器对象
    manager = TaskManager()

    # 启动
    manager.start_task(TaskConfig(
        name="实时截屏",
        method="capture",
        kwargs={"n": 10000},
        daemon=True
    ))
