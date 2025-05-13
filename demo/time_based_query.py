from screen_capture_processor import ScreenCaptureProcessor

from query_system import QuerySystem

screen_capture_processor = ScreenCaptureProcessor()
query_system = QuerySystem(screen_capture_processor)
print(query_system.time_based_query(start_time="2025-5-13 17:00:00", end_time="2025-5-13 18:00:00"))
