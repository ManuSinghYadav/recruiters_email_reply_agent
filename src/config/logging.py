import logging
from rich.logging import RichHandler

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Rich handler for terminal
    rich_handler = RichHandler()
    rich_handler.setFormatter(logging.Formatter("%(message)s"))

    # File handler
    file_handler = logging.FileHandler("src/logs/logs.log", "w")
    file_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%Y (%I:%M:%S %p)"
))

    logger.addHandler(rich_handler)
    logger.addHandler(file_handler)

    return logger