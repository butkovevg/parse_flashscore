from selenium.common.exceptions import NoSuchElementException
import os
import time
from selenium.webdriver.common.by import By
from src.model.tables import MainDBModel
from src.service.browser import BrowserService
from src.service.database import get_session
from src.service.logger_handlers import get_logger

from src.service.input_data_for_parsing import InputDataForParsing

logger = get_logger(__name__)


class CurrentPageService:
    def __init__(self, data4parsing: InputDataForParsing):
        self.session = next(get_session())
        self.data4parsing = data4parsing

    def get_list_links_from_db(self):
        try:

            # запрос для всех записей для вида спорта по дате
            query_all_record = (
                self.session
                .query(MainDBModel)
                .filter_by(match_date=self.data4parsing.match_date)
                .filter_by(sport_name=self.data4parsing.sport_name)
            )

            # Необработанных записей для вида спорта по дате
            query_unprocessed_record = query_all_record.filter_by(status=None)

            len_all_record = query_all_record.count()
            len_unprocessed_record = query_unprocessed_record.count()

            logger.debug(f"{len_unprocessed_record=}/{len_all_record=}")
            if len_all_record == 0:
                logger.info(f"Нет ссылок для       {self.data4parsing.sport_name} {self.data4parsing.match_date}")
                logger.info(f"Запускаем парсер для общей станицы")
                # # парсер общей странице
                # parsing_service = ParsingService()
                # link_list = parsing_service.get_list_link_with_main_page(sport=self.sport)
                #
                # # Заносим ссылки в таблицу расписания
                # self.insert_schedule(input_list=link_list)
                #
                # # парсер конкретных матчей
                # current_num = 1
                # total___num = len(link_list)
                # for link in link_list:
                #     logger.info(f"process {current_num}/{total___num} ---{link}")
                #     response = parsing_service.get_current_match(link=link)
                #     if response.status.value == "success":
                #         pass
                #     elif response.status.value == "error":
                #         pass
                #     else:
                #         logger.error(f"Неожиданная ошибка при обработке матча {link}")
                #     current_num += 1
            elif len_unprocessed_record > 0:
                logger.debug(f"Необработанные ссылки для {self.data4parsing}")
                logger.debug(f"Осталось обработать {len_unprocessed_record}/{len_all_record}")
                # парсер конкретных матчей
                unprocessed_records = query_unprocessed_record.all()
                for index_record in range(len_unprocessed_record):
                    unprocessed_record=unprocessed_records[index_record]
                    logger.info(f"process: {index_record+1}/{len_unprocessed_record} {unprocessed_record}")
                    self.get_current_match(link=unprocessed_record.link)
                    exit(-1)
            else:
                logger.info(f"Все ссылки обработаны для {self.data4parsing}")
        except Exception as exc:
            logger.error(f"Ошибка при получении статуса для {self.data4parsing}")
            logger.error(f"Подробности ошибки {str(exc)}")
        finally:
            self.session.close()

    def get_current_match(self, link):
        link = f"https://www.flashscorekz.com/match/{link}/#/standings/table/overall"
        try:
            browser = BrowserService.get_webdriver()
            browser.get(link)
            logger.debug(f"browser.get({link})")
            time.sleep(2)













            # 00 Блок о матче
            logger.debug("#00 Блок о матче")

            # 01 вид спорта
            sport = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/span[1]/a").text
            logger.debug(f"#01 вид спорта {sport}".upper())

            # 02 дата и время
            dt = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[1]/div").text
            date_game, time_game = dt.split(" ")
            logger.debug(f"#02 дата и время: {date_game} {time_game}".upper())

            # 03 страна/турнир
            tournament_header_country = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/span[3]").text
            country, tournament_tour = tournament_header_country.split(": ")
            tournament, tour = tournament_tour.split(" - ")
            logger.debug(f"#03 страна/турнир/тур: {country} {tournament_tour} {tour}".upper())

            # 04 Команды
            team1_name = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div[2]/a").text
            team2_name = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[4]/div[3]/div[1]/a").text
            logger.debug(f"#04 Команды: {team1_name} - {team2_name}".upper())

            # 05 счёт и статус
            status = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[3]/div/div[2]/span").text
            try:
                score1 = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[3]/div/div[1]/span[1]").text
                score2 = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[3]/div/div[1]/span[3]").text
                score = f"{score1}:{score2}"
            except NoSuchElementException:
                score1 = ""
                score2 = ""
                score = "Нет данных" + score1 + score2
            logger.debug(f"#05 счёт и статус {score}, {status}".upper())

            # Блок, определяет из таблицы:
            # 06 позиции
            # 07 количество игр
            # 08 разница мячей
            # 09 очки
            # 10 серия"
            rows = browser.find_elements(By.CSS_SELECTOR, ".ui-table__row")
            for i in rows:
                row = i.text
                arr_row = row.split("\n")
                team = arr_row[1]
                logger.warning(f"{arr_row=}")

                if team == team1_name:
                    pos1 = arr_row[0].strip(".")
                    number_games1 = arr_row[2]
                    delta_ball1 = arr_row[6]
                    points1 = arr_row[7]
                    series1 = "".join(arr_row[8:]).replace("?", "")
                elif team == team2_name:
                    pos2 = arr_row[0].strip(".")
                    number_games2 = arr_row[2]
                    delta_ball2 = arr_row[6]
                    points2 = arr_row[7]
                    series2 = "".join(arr_row[8:]).replace("?", "")
            number_of_teams_in_the_league = len(rows)
            logger.debug(f"#06 позиция {pos1}/{number_of_teams_in_the_league} {pos2}/{number_of_teams_in_the_league}")
            logger.debug(f"#07 количество игр: {number_games1}, {number_games2}")
            logger.debug(f"#08 разница мячей: {delta_ball1}, {delta_ball2}")
            logger.debug(f"#09 очки: {points1}, {points2}")
            logger.debug(f"#10 серия: {series1}, {series2}")
        except Exception as exc:
            logger.error(str(exc))
        finally:
            browser.quit()

if __name__ == "__main__":
    logger.info(f'Initializing test {os.path.basename(__file__)}')
    data_for_parsing = InputDataForParsing(sport_name="volleyball", shift_day=0)
    parsing_service = CurrentPageService(data4parsing=data_for_parsing)
    parsing_service.get_list_links_from_db()
