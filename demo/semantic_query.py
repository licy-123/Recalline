from screen_capture_processor import ScreenCaptureProcessor

from query_system import QuerySystem

screen_capture_processor = ScreenCaptureProcessor()
query_system = QuerySystem(screen_capture_processor)
print(query_system.semantic_query("什么是云端协同"))
