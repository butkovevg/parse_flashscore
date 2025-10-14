import os
import time
from random import randint

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from sqlalchemy.exc import IntegrityError

from src.configs.settings import settings
from src.model.tables import MainDBModel
from src.service.browser import BrowserService
from src.service.database import get_session
from src.service.helper import HelperService
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)

dict_link = {
    "football": {
        "link": "https://www.flashscorekz.com/?rd=flashscore.ru",
        "delimiter": "g_1_",
        "number_games": 2,
        "points": 8,
        "series": 9,
        "sport_name": "ФУТБОЛ",
        "sportName": "soccer",  # Для онлайн  счета и статуса матча
    },
    "volleyball": {
        "link": "https://www.flashscorekz.com/volleyball/",
        "delimiter": "g_12_",
        "number_games": 2,
        "points": 6,
        "series": 7,
        "sport_name": "ВОЛЕЙБОЛ",
        "sportName": "volleyball",  # Для онлайн  счета и статуса матча
    },
    "basketball": {
        "link": "https://www.flashscorekz.com/basketball/",
        "delimiter": "g_3_",
        "number_games": 2,
        "points": 6,
        "series": 7,
        "sport_name": "БАСКЕТБОЛ",
        "sportName": "basketball",  # Для онлайн  счета и статуса матча
    },
    "handball": {
        "link": "https://www.flashscorekz.com/handball/",
        "delimiter": "g_7_",
        "number_games": 2,
        "points": 6,
        "series": 7,
        "sport_name": "ГАНДБОЛ",
        "sportName": "handball",  # Для онлайн  счета и статуса матча
    },
    "tennis": {
        "link": "https://www.flashscorekz.com/tennis/",
        "delimiter": "g_2_",
        "number_games": 2,
        "points": 6,
        "series": 7,
        "sport_name": "ТЕННИС",
        "sportName": "tennis",  # Для онлайн  счета и статуса матча
    },
}
dct_translate_sport_name_rus_eng = {
    "ФУТБОЛ": "football",
    "ВОЛЕЙБОЛ": "volleyball",
    "БАСКЕТБОЛ": "basketball",
    "ГАНДБОЛ": "handball",
    "ТЕННИС": "tennis",
}


class MainPageService:
    def __init__(self, data4parsing: InputDataForParsing):
        self.session = next(get_session())
        self.data4parsing = data4parsing
        self.list_link = []

    def get_list_link_with_main_page(self):
        try:
            link = dict_link.get(self.data4parsing.english_sport_name).get("link")
            delimiter = dict_link.get(self.data4parsing.english_sport_name).get("delimiter")
            browser = BrowserService.get_webdriver(is_headless=settings.IS_HEADLESS)
            browser.get(link)
            time.sleep(randint(settings.PAUSE_SEC, settings.PAUSE_SEC + 10))

            # Кликаем на следующий день, если day > 0
            while abs(self.data4parsing.shift_day) > 0:
                # button_move_day = browser.find_element(By.XPATH, "/html/body/div[4]/div[1]/div/div[1]/main/div[5]/div[2]/div/div[1]/div[2]/div/button[3]")
                button_move_day = browser.find_element(By.CSS_SELECTOR, 'button[data-day-picker-arrow="next"]')
                # button_move_day = browser.find_element(By.XPATH, "//button[@title='Следующий день']")
                # button_move_day = browser.find_element.find_element(By.XPATH, "//button[contains(@class, 'calendar__navigation--tomorrow')]")
                #
                # from selenium.webdriver.common.by import By
                # from selenium.webdriver.support.ui import WebDriverWait
                # from selenium.webdriver.support import expected_conditions as EC
                # # Явное ожидание появления кнопки
                # wait = WebDriverWait(browser, 10)  # Максимальное время ожидания — 10 секунд
                # button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Следующий день']")))
                if self.data4parsing.shift_day < 0:  # Если отрицательное число
                    self.data4parsing.shift_day += 1
                    button_move_day = browser.find_element(By.CSS_SELECTOR, "[title='Предыдущий день']")
                else:  # Если положительное число
                    self.data4parsing.shift_day -= 1
                button_move_day.click()
                time.sleep(randint(settings.PAUSE_SEC, settings.PAUSE_SEC + 10))

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
        logger.warning(f" {self.data4parsing}: get_links({length_list_link})")
        for index_link in range(length_list_link):
            try:
                link = self.list_link[index_link]
                self.session.add(MainDBModel(
                    link=link,
                    sport_name=dict_link[self.data4parsing.english_sport_name]["sport_name"],
                    match_date=self.data4parsing.match_date,
                ))
                self.session.commit()
                logger.info(f'insert record({index_link + 1}/{length_list_link}): {link}')
            except IntegrityError:
                logger.warning(f"psycopg2.errors.UniqueViolation: {link}")
                self.session.rollback()
            except Exception as exc:
                description_error = f"insert2: {str(exc)}"
                logger.error(description_error)

    def get_list_for_update_analysis(self, list_links_aft_analysis: list):
        try:
            link = dict_link.get(self.data4parsing.english_sport_name).get("link")
            browser = BrowserService.get_webdriver(is_headless=settings.IS_HEADLESS)
            browser.get(link)
            time.sleep(randint(settings.PAUSE_SEC, settings.PAUSE_SEC + 10))
            page_source = browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            delimiter = dict_link.get(self.data4parsing.english_sport_name).get("delimiter")

            # Поиск по CSS-селектору
            sportName = dict_link[self.data4parsing.english_sport_name]['sportName']
            css_selector = f'div.sportName.{sportName}'
            divs_sportname = soup.select(css_selector)

            # # 1. Сохранение HTML-кода в файл
            # with open("file_name_for_html.html", 'w', encoding='utf-8') as file:
            #     file.write(page_source)
            #     logger.info("Save in file")
            # with open(file_name_for_html, 'r', encoding='utf-8') as file:
            #     logger.info("Open file")
            #     saved_html = file.read()

            # print(type(divs_sportname))
            # for div in divs_sportname:
            #     print(type(div), div.select('div'))
            #     print("*"*88)

            # Список для дальнейшего UPDATE(link, status)
            # Список для хранения результатов
            # Список для хранения результатов
            # Список для хранения результатов
            output_list = []
            list_links_for_logger = []

            # Перебираем каждый элемент в ResultSet
            for div in divs_sportname:
                # Находим все матчи внутри текущего блока
                matches = div.find_all('div', class_='event__match')
                # for match in matches:
                for index in range(0, len(matches)):
                    match = matches[index]
                    # Извлекаем id (если существует)
                    link = match.get('id', None)
                    if link is not None:
                        link = link.replace(delimiter, "")
                    else:
                        continue

                    # Извлекаем текст (если элементы существуют)
                    status = match.find('div', class_='event__stage--block')
                    status = status.text.strip() if status else None

                    scores = soup.find_all('span', class_='event__score')
                    try:
                        res1 = scores[index * 2].text.strip()
                        res2 = scores[index * 2 + 1].text.strip()
                        res = f"{res1}:{res2}"
                    except Exception as exc:
                        print("ERR", link, exc)
                        res = "Error -:-"


                    if link in list_links_aft_analysis:
                        # Добавляем данные в список
                        who_now_win = HelperService.get_who_now_win(res)
                        logger.debug(f"{who_now_win=}")
                        output_list.append({
                            'link': link,
                            'status': status,
                            'result': res,
                            'who_now_win': who_now_win,
                        })
                        logger.info(f"for {link=} {status=} {res=}")
                        list_links_for_logger.append(link)
                    else:
                        logger.debug(f"{link} {status=} {res=}")
            logger.info(f"{len(output_list)} record(s) update: {list_links_for_logger}")
            logger.debug(f"{output_list=}")
            browser.quit()
            return output_list, list_links_for_logger
        except Exception as exc:
            logger.error(str(exc))
            return [], []

        # button_move_day = browser.find_element(By.CSS_SELECTOR, "[title='Предыдущий день']")
        # # Перебор найденных элементов
        # for idx, volleyball_div in enumerate(volleyball_divs, start=1):
        #     logger.debug(f"Элемент {idx}:")
        #     # print(volleyball_div.prettify())
        #     # exit(0)

        # ids_filtered = filter(lambda x: x.startswith(delimiter), ids)
        # self.list_link = [link.replace(delimiter, "") for link in ids_filtered]
        # print(self.list_link)  # Вывод тега <title>
        # print(soup.p.text)  # Вывод текста внутри тега <p>


if __name__ == "__main__":
    logger.info(f'Initializing test {os.path.basename(__file__)}')
    # day = 1
    # data_for_parsing1 = InputDataForParsing(sport_name="volleyball", shift_day=day)
    # data_for_parsing2 = InputDataForParsing(sport_name="football", shift_day=day)
    # data_for_parsing3 = InputDataForParsing(sport_name="basketball", shift_day=day)
    # data_for_parsing4 = InputDataForParsing(sport_name="handball", shift_day=day)
    # data_for_parsing5 = InputDataForParsing(sport_name="tennis", shift_day=day)
    # list_data_for_parsing = [data_for_parsing1,
    #                          data_for_parsing2,
    #                          data_for_parsing3,
    #                          data_for_parsing4,
    #                          data_for_parsing5,
    #                          ]
    #
    # for data_for_parsing in list_data_for_parsing:
    #     parsing_service = MainPageService(data4parsing=data_for_parsing)
    #     parsing_service.get_list_link_with_main_page()
    #     parsing_service.insert()

    sport_name = "basketball"
    day = 5
    data_for_parsing = InputDataForParsing(sport_name=sport_name, shift_day=day)
    parsing_service = MainPageService(data4parsing=data_for_parsing)

    list_links_aft_analysis = ["b1wdKc75"]
    parsing_service.get_list_for_update_analysis(list_links_aft_analysis)
