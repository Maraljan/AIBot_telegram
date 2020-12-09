import sys
import logging


LOG_BASE_NAME = 'AIBot'
LOG_FORMAT = '%(asctime)s %(levelname)-7s %(name)-15s: %(message)s'
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def logger_config(level: str = 'DEBUG', root_level: str = 'WARNING'):

    log_handler = logging.StreamHandler(stream=sys.stdout)

    log_formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    log_handler.setFormatter(log_formatter)

    # root logger
    logging.getLogger('').addHandler(log_handler)
    logging.getLogger('').setLevel(root_level)

    # bot logger
    logging.getLogger(LOG_BASE_NAME).setLevel(level)


def get_logger(name: str):
    return logging.getLogger(f'{LOG_BASE_NAME}.{name}')
