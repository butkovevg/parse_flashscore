import asyncio
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)

async def run(id: int):
    logger.info("BEF")
    await asyncio.sleep(10)  # Имитация длительной операции
    logger.info("AFT")
    return f"Task {id} completed"