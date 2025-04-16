import sys

from loguru import logger


def configurate_logger() -> None:
    logger.remove()
    logger.add(
        sink=sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | - <level>{message}</level>",
        colorize=True,
    )
