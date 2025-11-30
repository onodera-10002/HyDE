import logging
import sys
import os
from src import config
# loggerの下準備の部分
# logをコンソール出力するメゾっト
# logをlog.txtに保存するメゾッド
# errorをerror.txtに保存するメゾッド


class LoggerManager:
    _FORMAT = '[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
    _DATEFORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self):
        self._log_dir = config.LOG_DIR
        self._formatter = logging.Formatter(self._FORMAT, self._DATEFORMAT)
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)
    
    def _create_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(self._format, self._dateformat)
        console_handler.setFormatter(console_formatter)
        return console_handler
    
    def _create_file_handler(self, filename:str, level:int):
        file_handler = logging.FileHandler(
            os.path.join(self._log_dir, filename), 
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(self._format, self._dateformat)
        file_handler.setFormatter(file_formatter)
        return file_handler
    
    def get_logger(self, module_name:str):
        logger = logging.getLogger(module_name)

        if logger.hasHandlers():
            return logger

        logger.setLevel(logging.INFO)
        logger.addHandler(self._create_console_handler())
        logger.addHandler(self._create_file_handler('log.txt', logging.INFO))
        logger.addHandler(self._create_file_handler('error.txt', logging.ERROR))
        return logger
    

