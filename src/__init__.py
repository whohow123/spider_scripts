import os
import sys
import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
import logging.config
from configure import config


class LogFormat(object):
    def main(self):
        """log 日志配置"""
        if not os.path.exists(config.LOG_DIR):
            # 创建路径
            os.makedirs(config.LOG_DIR)

        log_file = datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    'format': '%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
                },
                'standard': {
                    'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
                },
            },

            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout"
                },

                "default": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    "filename": os.path.join(config.LOG_DIR, log_file),
                    'mode': 'w+',
                    "maxBytes": 1024*1024*5,  # 5 MB
                    "backupCount": 20,
                    "encoding": "utf8"
                },
            },
            "root": {
                'handlers': ['default'],
                'level': "INFO",
                'propagate': False
            }
        }

        logging.config.dictConfig(log_config)
