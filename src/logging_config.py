from loguru import logger
import sys

from src.config.base_config import settings


def setup_logging() -> None:
    """Configure loguru logging for the application."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
    )
    logger.add(
        f"logs/{settings.log_file}",
        rotation="500 MB",
        retention="10 days",
        level=settings.log_level,
    )
