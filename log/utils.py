import logging
from logging.handlers import TimedRotatingFileHandler
import os

def add_logger(name:str, log_level:int):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    path = _create_log_path(name)
    
    handler = TimedRotatingFileHandler(path, when='midnight', interval=1, backupCount=10)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def add_cli_logger(name:str, log_level:int):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def _create_log_path(name:str)->str:
    log_directory = os.path.join("log", name)
    
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    log_file = os.path.join(log_directory, f"{name}.log")
    return log_file