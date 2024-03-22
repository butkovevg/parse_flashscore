import os
import time
from random import randint

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from src.configs.settings import settings
from src.model.response import ResponseModel, StatusModel
from src.model.tables import MainDBModel
from src.service.browser import BrowserService
from src.service.current_match import CurrentMatchService
from src.service.database import get_session
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.logger_handlers import get_logger

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
                    logger.info(f"process: {index_record + 1}/{len_unprocessed_record} {unprocessed_record}")
                    response = self.get_current_match(link=unprocessed_record.link)
                    if response.status == StatusModel.SUCCESS:
                        self.update(main_db_model=unprocessed_record, status=True)
                    elif response.status == StatusModel.ERROR:

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
            logger.debug(f'insert record: {model}')
            return ResponseModel(status=StatusModel.SUCCESS)
        except IntegrityError as exc:
            description_error = f"IntegrityError: {str(exc)} for {model}"
            logger.warning(description_error)
            self.session.rollback()
            return ResponseModel(status=StatusModel.SUCCESS)
        except Exception as exc:
            description_error = f"ERROR: {str(exc)} for {model}"
            logger.error(description_error)
            return ResponseModel(status=StatusModel.ERROR)

    def update(self, main_db_model, status=True):
        """
        :param main_db_model:
        :param status:
        :return:
        ToDo: DELETED TRY/EXCEPT
        """
        try:
            stmt = (
                update(MainDBModel).
                where(MainDBModel.id == main_db_model.id).
                values(status=status)
            )

            self.session.execute(stmt)
            self.session.commit()

        except Exception as exc:
            logger.error(str(exc))
            logger.error(main_db_model.link)
            self.session.rollback()

    def get_current_match(self, link):
        full_link = f"https://www.flashscorekz.com/match/{link}/#/standings/table/overall"
        try:
            browser = BrowserService.get_webdriver()
            browser.get(full_link)
            logger.debug(f"browser.get({full_link})")
            time.sleep(randint(settings.PAUSE_SEC, settings.PAUSE_SEC + 10))
            current_db_model = CurrentMatchService(browser, self.data4parsing).get_current_match_model(link)
            response_insert = self.insert(model=current_db_model)
            if response_insert.status == StatusModel.SUCCESS:
                return ResponseModel(status=StatusModel.SUCCESS, )
            else:
                return ResponseModel(status=StatusModel.ERROR, )
        except ValueError as exc:
            logger.warning(f"ERROR {full_link}")
            logger.warning(str(exc))
            return ResponseModel(status=StatusModel.ERROR, )
        except Exception as exc:
            logger.error(f"ERROR {full_link}")
            logger.error(str(exc))
            return ResponseModel(status=StatusModel.ERROR, )
        finally:
            browser.quit()


if __name__ == "__main__":
    logger.info(f'Initializing test {os.path.basename(__file__)}')
    day = 3
    data_for_parsing1 = InputDataForParsing(sport_name="volleyball", shift_day=day)
    data_for_parsing2 = InputDataForParsing(sport_name="football", shift_day=day)
    data_for_parsing3 = InputDataForParsing(sport_name="basketball", shift_day=day)
    data_for_parsing4 = InputDataForParsing(sport_name="handball", shift_day=day)
    list_data_for_parsing = [data_for_parsing1,
                             data_for_parsing2,
                             data_for_parsing3,
                             data_for_parsing4,
                             ]
    for data_for_parsing in list_data_for_parsing:
        parsing_service = CurrentPageService(data4parsing=data_for_parsing)
        parsing_service.get_list_links_from_db()

    # parsing_service = CurrentPageService(data4parsing=data_for_parsing3)
    # parsing_service.get_current_match(link="lSB2WTpB")
