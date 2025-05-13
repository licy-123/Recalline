from datetime import datetime


class StrTimeProcessor:
    """将输入的时间转换为时间戳，便于直接检索"""

    def time_str_to_unix_timestamp(self, time_str):
        """要求输入格式为Y%-m%-d% H%:M%:S%"""

        # 转换为datetime对象
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        # 转换为unix_timestamp
        return dt.timestamp()