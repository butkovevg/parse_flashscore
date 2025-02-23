import time

from selenium.webdriver.common.by import By

from src.configs.settings import settings
from src.service.browser import BrowserService
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)


class EnrichmentStatisticService:
    @staticmethod
    def open_page_with_coefficient(link: str) -> tuple:
        full_link = f"https://www.flashscorekz.com/match/{link}/#/odds-comparison/"
        browser = BrowserService.get_webdriver()
        try:
            browser.get(full_link)
            logger.debug(f"COEFFICIENT: browser.get({full_link})")
            time.sleep(settings.PAUSE_SEC)
            return EnrichmentStatisticService.get_coefficient(browser)

        except Exception as exc:
            logger.error(f"ERROR {link=}")
            logger.error(str(exc))
            return 0, 0
        finally:
            browser.quit()

    @staticmethod
    def get_list_text_from_list_web_element(list_web_element: list) -> list:
        list_text = []
        for web_element in list_web_element:
            row_text = web_element.text
            arr_row_text = row_text.split("\n")
            list_text.append(arr_row_text)
        logger.debug(f"{list_text=}")
        return list_text
