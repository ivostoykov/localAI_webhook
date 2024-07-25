# logger.py
import logging
import os
from datetime import datetime

def init_logging(log_dir=None, consoleLog=True):
    # Ensure log directory exists
    if log_dir is None:
        log_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(log_dir, exist_ok=True)

    # Create a log file based on the current date
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{current_date}.log")

    # Configure basic logging to file
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=log_file,
                        filemode='a')  # Append mode

    # Get the default logger
    logger = logging.getLogger()

    # Add stream handler if consoleLog is True
    if consoleLog:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger

# Initialize logging when the module is imported
logger = init_logging(consoleLog=True)
