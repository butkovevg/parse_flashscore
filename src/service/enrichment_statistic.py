import time
from selenium.webdriver.common.by import By
from src.configs.settings import settings
from src.service.current_match import ValidationCurrentMatch
from src.service.logger_handlers import get_logger
from src.service.browser import BrowserService

logger = get_logger(__name__)


class EnrichmentStatisticService:
    def get_coefficient(self, link: str = "NO"):
        logger.warning(f"EnrichmentStatisticService1: {link=}")
        return {}

    def open_page_with_coefficient(self, link: str) -> tuple:
        full_link = f"https://www.flashscorekz.com/match/{link}/#/odds-comparison/"
        try:
            browser = BrowserService.get_webdriver()
            browser.get(full_link)
            logger.info(f"COEFFICIENT: browser.get({full_link})")
            time.sleep(settings.PAUSE_SEC)
            return self.get_coefficient1(browser)

        except Exception as exc:
            logger.error(f"ERROR {link=}")
            logger.error(str(exc))
            return (0, 0)
        finally:
            browser.quit()

    def get_list_text_from_list_webelement(self, list_web_element: list) -> list:
        list_text = []
        for webelement in list_web_element:
            row_text = webelement.text
            arr_row_text = row_text.split("\n")
            list_text.append(arr_row_text)
        logger.debug(f"{list_text=}")
        return list_text

    def validate_coefficient(self, input_value) -> float:
        if input_value == "-":
            return 0
        return float(input_value)

    def export_coefficient_from_list(self, list_text_coefficients: list, list_text_header: list) -> tuple:
        """
        :param list_text_coefficients:  ['4.45', '1.17'] or ['1.19', '6.20', '21.00']
        :param list_text_header:  ['БУКМЕКЕР', '1', '2'] or ['БУКМЕКЕР', '1', 'X', '2']
        :return:
        """
        output_tuple = (0, 0)
        if len(list_text_coefficients) == 0:
            logger.debug("NO COEFFICIENT")
        elif len(list_text_header) == 0:
            logger.debug("NO HEADER")
        elif len(list_text_coefficients) > 1:
            logger.error("*" * 88)
            logger.error(f" list_text_coefficients > 1: {list_text_coefficients}")
            logger.error(f" list_text_coefficients > 1: {list_text_header}")
        elif len(list_text_coefficients) == 1:
            kf1, kf2 = 0, 0
            list1_from_list_text_header = list_text_header[0]
            if len(list1_from_list_text_header) == 3:
                kf1 = self.validate_coefficient(list_text_coefficients[0][0])
                kf2 = self.validate_coefficient(list_text_coefficients[0][1])
            elif len(list1_from_list_text_header) == 4:
                kf1 = self.validate_coefficient(list_text_coefficients[0][0])
                kf2 = self.validate_coefficient(list_text_coefficients[0][2])
            else:
                logger.error(f"НЕБРАБОТАННЫЕ СИТАУЦИИ1: {list_text_coefficients=}")
                logger.error(f"НЕБРАБОТАННЫЕ СИТАУЦИИ2: {list_text_header=}")
            output_tuple = (kf1, kf2)
        else:
            logger.error(f"НЕБРАБОТАННЫЕ СИТАУЦИИ2: {list_text_coefficients=}")
            logger.error(f"НЕБРАБОТАННЫЕ СИТАУЦИИ3: {list_text_header=}")
        return output_tuple

    def get_coefficient1(self, browser):
        output_tuple = (0, 0)
        try:

            rows_coefficients = browser.find_elements(By.CSS_SELECTOR, ".ui-table__row")
            list_text_coefficients = self.get_list_text_from_list_webelement(list_web_element=rows_coefficients)
            header_coefficients = browser.find_elements(By.CSS_SELECTOR, ".ui-table__header")
            list_text_header = self.get_list_text_from_list_webelement(list_web_element=header_coefficients)

            output_tuple = self.export_coefficient_from_list(list_text_coefficients, list_text_header)
            logger.info(f"{output_tuple=}")
            return output_tuple

            # ValidationCurrentMatch.is_validate(text="#00 ссылка", input_value="link", input_type=str)
            # sport_name = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/span[1]/a").text
        except Exception as exc:
            logger.error(str(exc))

            return output_tuple


if __name__ == "__main__":
    service = EnrichmentStatisticService()
    a = service.open_page_with_coefficient(link="viLatFGL")
    logger.critical(f"{a=}")
    service.open_page_with_coefficient(link="YLvr9jHa")
    service.open_page_with_coefficient(link="AFmEcv5j")
    service.open_page_with_coefficient(link="4SDknHSa")
    service.open_page_with_coefficient(link="QyFomcDg")
    service.open_page_with_coefficient(link="M38foyr6")
    service.open_page_with_coefficient(link="CUUFhmQC")
    service.open_page_with_coefficient(link="0f7bpecC")
    service.open_page_with_coefficient(link="829ElZtK")
    service.open_page_with_coefficient(link="fRuw7Hi6")
    service.open_page_with_coefficient(link="v9Gdrrso")
    service.open_page_with_coefficient(link="lQ0N1niE")
    service.open_page_with_coefficient(link="CtioHgRc")
    service.open_page_with_coefficient(link="bN4OSRkL")
    service.open_page_with_coefficient(link="tnfTRo5R")
    service.open_page_with_coefficient(link="Gl8CNfUp")
    service.open_page_with_coefficient(link="lbbR4mJ4")
    service.open_page_with_coefficient(link="vPxWKlyN")
    service.open_page_with_coefficient(link="Awnj6Rdr")
    service.open_page_with_coefficient(link="8h0lOICq")
    service.open_page_with_coefficient(link="W0dY2Wit")
    service.open_page_with_coefficient(link="f3FP17q2")
    service.open_page_with_coefficient(link="CzbRe8Df")
    service.open_page_with_coefficient(link="E9Fxpff0")
    service.open_page_with_coefficient(link="6w39E1uJ")
    service.open_page_with_coefficient(link="4rjPItDt")
    service.open_page_with_coefficient(link="UkL7vshO")
    service.open_page_with_coefficient(link="EDXHUYjE")
    service.open_page_with_coefficient(link="O8t1nTPm")
