import time

from src.service.browser import BrowserService
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)

class MegamarketService:
    def __init__(self):
        self.browser = BrowserService.get_webdriver()

    def __del__(self):
        try:
            logger.info(f'Подготовка удаления объекта browser')
            self.browser.quit(is_headless=False)
            logger.info(f'Объект browser удален')
        except Exception as exc:
            logger.error(str(exc))

    def get_page(self, link: str):
        try:
            self.browser.get(link)
            time.sleep(15)
        except Exception as exc:
            logger.error(str(exc))
            return []



if __name__ == '__main__':
    service = MegamarketService()
    service.get_page(link="https://megamarket.ru/shop/megamarket-moskva-hlebnikovo-so-sklada-megamarket/")
