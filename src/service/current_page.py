import os

import time
from random import randint

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from src.model.response import ResponseModel, StatusModel
from src.model.tables import MainDBModel, CurrentDBModel
from src.service.browser import BrowserService
from src.service.database import get_session
from src.service.helper import HelperService
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.logger_handlers import get_logger
from src.service.main_page import dict_link

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
                    unprocessed_record = unprocessed_records[index_record]
                    logger.warning(f"2 {unprocessed_record=}")
                    logger.warning(f"{unprocessed_record.id=}")
                    logger.info(f"process: {index_record + 1}/{len_unprocessed_record} {unprocessed_record}")
                    response = self.get_current_match(link=unprocessed_record.link)
                    if response.status == StatusModel.SUCCESS:
                        self.update(main_db_model=unprocessed_record, status=True)
                    elif response.status == StatusModel.ERROR:
                        logger.warning(f"1 {unprocessed_record=}")
                        logger.warning("3")

                        self.update(main_db_model=unprocessed_record, status=False)
                    else:
                        logger.error("an unhandled error")
            else:
                logger.info(f"Все ссылки обработаны для {self.data4parsing}")
        except Exception as exc:
            logger.error(f"Ошибка при получении статуса для {self.data4parsing}")
            logger.error(f"Подробности ошибки {str(exc)}")
        finally:
            self.session.close()

    def insert(self, model) -> ResponseModel:
        """
        """
        try:

            self.session.add(model)
            self.session.commit()
            logger.info(f'insert record')
            return ResponseModel(status=StatusModel.SUCCESS)
        except IntegrityError as exc:
            description_error = f"insert1: {str(exc)}"
            logger.warning(description_error)
            self.session.rollback()
            return ResponseModel(status=StatusModel.SUCCESS)
        except Exception as exc:
            description_error = f"insert2: {str(exc)}"
            logger.error(description_error)
            return ResponseModel(status=StatusModel.ERROR)

    def update(self, main_db_model, status=True):
        """
        :param status:
        :return:
        ToDo:
        """
        try:
            logger.warning("111")
            stmt = (
                update(MainDBModel).
                where(MainDBModel.id == main_db_model.id).
                values(status=status)
            )
            logger.warning("222")

            self.session.execute(stmt)
            self.session.commit()

        except:
            logger.error(main_db_model.link)
            self.session.rollback()

    def get_current_match(self, link):
        full_link = f"https://www.flashscorekz.com/match/{link}/#/standings/table/overall"
        try:
            browser = BrowserService.get_webdriver()
            browser.get(full_link)
            logger.debug(f"browser.get({full_link})")
            time.sleep(randint(5, 15))

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
            list_country_tournament_tour = tournament_header_country.split(": ")
            country = HelperService.get_element_for_list(lst=list_country_tournament_tour, index=0,
                                                         default_value="NO_INFO")
            tournament_tour = HelperService.get_element_for_list(lst=list_country_tournament_tour, index=1,
                                                                 default_value="NO_INFO")
            list_tournament_tour = tournament_tour.split(" - ")
            tournament = HelperService.get_element_for_list(lst=list_tournament_tour, index=1, default_value="NO_INFO")
            tour = HelperService.get_element_for_list(lst=list_tournament_tour, index=0, default_value="NO_INFO")
            logger.debug(f"#03 страна/турнир/тур: {country} {tournament_tour} {tour}".upper())

            # 04 Команды
            team1_name = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div[2]/a").text
            team2_name = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[4]/div[3]/div[1]/a").text
            logger.debug(f"#04 Команды: {team1_name} - {team2_name}".upper())

            # 05 счёт и статус
            try:
                status = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[3]/div/div[2]/span").text
                score1 = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[3]/div/div[1]/span[1]").text
                score2 = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[3]/div/div[1]/span[3]").text
                score = f"{score1}:{score2}"
            except NoSuchElementException:
                status = "TKP - ТОЛЬКО КОНЕЧНЫЙ РЕЗУЛЬТАТ."
                score1 = ""
                score2 = ""
                score = "Нет данных" + score1 + score2
            logger.debug(f"#05 счёт и статус {score}, {status}".upper())

            # Блок, определяет из таблицы:
            pos1, pos2 = 0, 0
            number_games1, number_games2 = 0, 0
            points1, points2 = 0, 0
            series1, series2 = "NO_INFO", "NO_INFO"
            # 06 позиции
            # 07 количество игр
            # 08 очки
            # 09 серия
            rows = browser.find_elements(By.CSS_SELECTOR, ".ui-table__row")

            count = 0
            for i in rows:
                count += 1
                row = i.text

                arr_row = row.split("\n")
                logger.warning(f"{arr_row=}")
                team = arr_row[1]
                # ['4.', 'Лубе Чивитанова', '12', '8', '4', '26:20', '22', '?', 'B', 'П', 'B', 'B', 'П']
                # ['2.', 'ЕС Сетиф',        '11', '6', '2', '3', '16:13', '3', '20', '?', 'B', 'B', 'B', 'Н', 'Н']
                # ['6.', 'Атлетик (Б)',      '3', '0', '1', '2', '2:4', '-2', '1', '?', 'П', 'П', 'Н']
                dct_parametrs = dict_link[self.data4parsing.sport_name]
                if team == team1_name:
                    pos1 = int((arr_row[0].strip(".")))
                    if pos1 != count:
                        raise ValueError("Таблиц несколько")
                    number_games1 = arr_row[dct_parametrs["number_games"]]
                    points1 = arr_row[dct_parametrs["points"]]
                    series1 = "".join(arr_row[dct_parametrs["series"]:]).replace("?", "")
                elif team == team2_name:
                    pos2 = int(arr_row[0].strip("."))
                    if pos2 != count:
                        raise ValueError("Таблиц несколько")
                    number_games2 = arr_row[dct_parametrs["number_games"]]
                    points2 = arr_row[dct_parametrs["points"]]
                    series2 = "".join(arr_row[dct_parametrs["series"]:]).replace("?", "")
            number_of_teams_in_the_league = len(rows)
            logger.debug(f"#06 ПОЗИЦИЯ {pos1}/{number_of_teams_in_the_league} {pos2}/{number_of_teams_in_the_league}")
            logger.debug(f"#07 КОЛИЧЕСТВО ИГР: {number_games1}, {number_games2}")
            logger.debug(f"#08 ОЧКИ: {points1}, {points2}")
            logger.debug(f"#09 СЕРИЯ: {series1}, {series2}")
            current_db_model = CurrentDBModel(
                link=link,
                sport_name=sport,
                match_date=date_game,
                match_time=time_game,
                country=country,
                tournament=tournament,
                tour=tour,
                team1=team1_name,
                team2=team2_name,
                score1=score1,
                score2=score2,
                match_status=status,
                position1=pos1,
                position2=pos2,
                position_total=number_of_teams_in_the_league,
                num_games1=number_games1,
                num_games2=number_games2,
                points1=points1,
                points2=points2,
                series1=series1,
                series2=series2,
            )
            response_insert = self.insert(model=current_db_model)
            if response_insert.status == StatusModel.SUCCESS:
                logger.warning("1")
                return ResponseModel(status=StatusModel.SUCCESS, )
            else:
                logger.warning("2")

                return ResponseModel(status=StatusModel.ERROR, )
        except Exception as exc:
            logger.error(f"ERROR {link=}")
            logger.error(str(exc))
            return ResponseModel(status=StatusModel.ERROR, )
        finally:
            browser.quit()


if __name__ == "__main__":
    logger.info(f'Initializing test {os.path.basename(__file__)}')
    day=1
    data_for_parsing1 = InputDataForParsing(sport_name="volleyball", shift_day=day)
    data_for_parsing2 = InputDataForParsing(sport_name="football", shift_day=day)
    data_for_parsing3 = InputDataForParsing(sport_name="basketball", shift_day=day)
    parsing_service = CurrentPageService(data4parsing=data_for_parsing1)
    parsing_service.get_list_links_from_db()
