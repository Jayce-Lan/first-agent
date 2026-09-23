import logging
import logging.config
import os
import sys
import queue
import atexit
from logging.handlers import QueueHandler, QueueListener

# ===================== 自动路径配置 =====================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_CONF_PATH = os.path.join(BASE_DIR, "logging.conf")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# 只创建 logs 文件夹，不创建任何子文件夹
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ===================== 异步日志核心 =====================
class AsyncLogger:
    _log_queue = queue.Queue(-1)
    _listener = None
    _initialized = False

    @classmethod
    def _start_async_listener(cls):
        if cls._listener is not None and cls._listener.is_alive():
            return

        logging.config.fileConfig(LOG_CONF_PATH)
        root = logging.getLogger()
        handlers = root.handlers[:]
        root.handlers.clear()
        root.addHandler(QueueHandler(cls._log_queue))

        cls._listener = QueueListener(cls._log_queue, *handlers)
        cls._listener.start()
        atexit.register(cls._listener.stop)

    @classmethod
    def get_logger(cls):
        if not cls._initialized:
            cls._start_async_listener()
            cls._initialized = True

        caller_frame = sys._getframe(1)
        filename = os.path.splitext(os.path.basename(caller_frame.f_code.co_filename))[0]
        return logging.getLogger(filename)

# 全局导出
log = AsyncLogger.get_logger()