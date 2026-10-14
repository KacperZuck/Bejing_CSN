import logging
import os
from datetime import datetime


def setup_logger():
    """Configures session logging to a file and the console."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(base_dir, "logs")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"session_{session_time}.log")

    logger = logging.getLogger("EmailClient")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(levelname)s] %(asctime)s.%(msecs)03d - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()