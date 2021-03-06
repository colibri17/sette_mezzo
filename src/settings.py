import inspect
import logging.config
import os
import shutil
import sys


def clean_dirs(dirs):
    for path in dirs:
        if os.path.exists(path):
            shutil.rmtree(path)
        if not os.path.exists(path):
            os.makedirs(path)


def create_dirs(dirs):
    for path in dirs:
        if not os.path.exists(path):
            os.makedirs(path)


CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
BASE_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

dirs_to_create = [DATA_DIR, LOGS_DIR]
create_dirs(dirs_to_create)

dirs_to_clean = []
clean_dirs(dirs_to_clean)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'debug_file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'filename': os.path.join(LOGS_DIR, 'debug_logs.log'),
            'mode': 'w'
        },
        'permanent_debug_file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'filename': os.path.join(LOGS_DIR, 'permanent_debug_logs.log'),
            'mode': 'a'
        },
        'info_file': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'filename': os.path.join(LOGS_DIR, 'info_logs.log'),
            'mode': 'w'
        },
    },
    'loggers': {
        'sette-mezzo': {
            'level': 'INFO',
            'handlers': ['console', 'debug_file', 'info_file', 'permanent_debug_file']
        }
    }
}

logging.config.dictConfig(LOGGING)
