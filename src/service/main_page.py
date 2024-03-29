import os
import time

from bs4 import BeautifulSoup

from sqlalchemy.exc import IntegrityError
from selenium.webdriver.common.by import By
from src.model.tables import MainDBModel
from src.service.browser import BrowserService
from src.service.database import get_session
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)

# number_games2 = arr_row[2]
# points2 = arr_row[8]
# series2 = "".join(arr_row[9:]).replace("?", "")
# number_of_teams_in_the_league = len(rows)

dict_link = {
    "football": {
        "link": "https://www.flashscorekz.com/?rd=flashscore.ru",
        "delimiter": "g_1_",
        "number_games": 2,
        "points": 8,
        "series": 9,

    },
    "volleyball": {
        "link": "https://www.flashscorekz.com/volleyball/",
        "delimiter": "g_12_",
        "number_games": 2,
        "points": 6,
        "series": 7,
    },
    "basketball": {
        "link": "https://www.flashscorekz.com/basketball/",
        "delimiter": "g_3_",
        "number_games": 2,
        "points": 6,
        "series": 7,
    },
}


class MainPageService:
    def __init__(self, data4parsing: InputDataForParsing):
        self.session = next(get_session())
        self.data4parsing = data4parsing

    def get_list_link_with_main_page(self):
        try:
            link = dict_link.get(self.data4parsing.sport_name).get("link")
            delimiter = dict_link.get(self.data4parsing.sport_name).get("delimiter")
            browser = BrowserService.get_webdriver()
            browser.get(link)
            time.sleep(3)

            # Кликаем на следующий день, если day > 0
            while abs(self.data4parsing.shift_day) > 0:
                button_move_day = browser.find_element(By.CSS_SELECTOR, "[title='Следующий день']")
                if self.data4parsing.shift_day < 0:  # Если отрицательное число
                    self.data4parsing.shift_day += 1
                    button_move_day = browser.find_element(By.CSS_SELECTOR, "[title='Предыдущий день']")
                else:  # Если положительное число
                    self.data4parsing.shift_day -= 1
                button_move_day.click()
                time.sleep(5)

            page_source = browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            ids = [tag['id'] for tag in soup.select('div[id]')]
            ids_filtered = filter(lambda x: x.startswith(delimiter), ids)
            self.list_link = [link.replace(delimiter, "") for link in ids_filtered]
            browser.quit()

        except Exception as exc:
            logger.error(str(exc))
            return []

    def insert(self) -> None:
        """

        """
        length_list_link = len(self.list_link)
        logger.info(f"Получено ссылок {length_list_link}")
        for index_link in range(length_list_link):
            try:
                link = self.list_link[index_link]
                self.session.add(MainDBModel(
                    link=link,
                    sport_name=self.data4parsing.sport_name,
                    match_date=self.data4parsing.match_date,
                ))
                self.session.commit()
                logger.info(f'insert record({index_link + 1}/{length_list_link}): {link}')
            except IntegrityError as exc:
                description_error = f"insert1: {str(exc)}"
                logger.warning(description_error)
                self.session.rollback()
            except Exception as exc:
                description_error = f"insert2: {str(exc)}"
                logger.error(description_error)


if __name__ == "__main__":
    logger.info(f'Initializing test {os.path.basename(__file__)}')
    data_for_parsing1 = InputDataForParsing(sport_name="volleyball", shift_day=0)
    data_for_parsing2 = InputDataForParsing(sport_name="football", shift_day=0)
    data_for_parsing3 = InputDataForParsing(sport_name="basketball", shift_day=0)
    parsing_service = MainPageService(data4parsing=data_for_parsing3)
    parsing_service.get_list_link_with_main_page()
    parsing_service.insert()
