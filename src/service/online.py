import os

from src.configs.settings import settings
from src.model.tables import AnalysisDBModel, CurrentDBModel
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.logger_handlers import get_logger
from src.service.main_page import MainPageService, dict_link
from sqlalchemy import Table, MetaData, select
from src.service.database import get_session

logger = get_logger(__name__)


class DataBaseOnlineService:
    def __init__(self, data4parsing: InputDataForParsing):
        self.data4parsing = data4parsing
        self.session = next(get_session())

    def get_list_links_from_db(self):
        try:
            # Создание запроса
            query = (
                select(AnalysisDBModel.link)
                .join(CurrentDBModel, CurrentDBModel.link == AnalysisDBModel.link, isouter=True)  # LEFT JOIN
                .where(CurrentDBModel.sport_name == 'БАСКЕТБОЛ')
                .where(CurrentDBModel.match_date == '28.03.2025')
            )
            # Выполнение запроса
            results = self.session.execute(query).scalars().all()
            return results
        except Exception as exc:
            logger.error(f"Error for {self.data4parsing}")
            logger.error(f"Details: {str(exc)}")
            return []
        finally:
            self.session.close()

        #     translate_sport_name = dict_link[self.data4parsing.sport_name]["sport_name"]
        #     en_sport_name = self.data4parsing.sport_name
        #     logger.warning(f"{en_sport_name}")
        #     # запрос для всех записей для вида спорта по дате
        #     logger.warning(f"{self.data4parsing.match_date=}")
        #     logger.warning(f"{translate_sport_name=}")
        #     query_all_record = (
        #         self.session
        #         .query(AnalysisDBModel)
        #         .filter_by(match_date=self.data4parsing.match_date)
        #         .filter_by(sport_name=translate_sport_name)
        #     )
        #
        #     # Необработанных записей для вида спорта по дате
        #     query_unprocessed_record = query_all_record.filter_by(status=None)
        #
        #     len_all_record = query_all_record.count()
        #     len_unprocessed_record = query_unprocessed_record.count()
        #
        #     logger.debug(f"{len_unprocessed_record=}/{len_all_record=}")
        #     if len_all_record == 0:
        #         logger.info(f"NO LINK  {self.data4parsing.sport_name} {self.data4parsing.match_date}")
        #     elif len_unprocessed_record > 0:
        #         logger.debug(f"Raw links for {self.data4parsing}")
        #         logger.debug(f"It remains to process {len_unprocessed_record}/{len_all_record}")
        #         # парсер конкретных матчей
        #         unprocessed_records = query_unprocessed_record.all()
        #         for index_record in range(len_unprocessed_record):
        #             unprocessed_record = unprocessed_records[index_record]
        #             logger.info(
        #                 f"process {unprocessed_record}({en_sport_name}): {index_record + 1}/{len_unprocessed_record} ")
        #             if self.data4parsing.sport_name == "tennis":
        #                 response = self.get_tennis_match(link=unprocessed_record.link)
        #             else:
        #                 response = self.get_current_match(link=unprocessed_record.link)
        #
        #             if response.status == StatusModel.SUCCESS:
        #                 self.update(main_db_model=unprocessed_record, status=True)
        #             elif response.status == StatusModel.ERROR:
        #
        #                 self.update(main_db_model=unprocessed_record, status=False)
        #             else:
        #                 logger.error("an unhandled error")
        #     else:
        #         logger.info(f"All link processed {self.data4parsing}")


if __name__ == "__main__":
    logger.info(f' Initializing API {settings.TITLE}: {settings.VERSION}')
    logger.info(f' Visit endpoint: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/online/')
    logger.info(f'Initializing file {os.path.basename(__file__)}')


    sport_name = "basketball"
    day = 0


    data_for_parsing = InputDataForParsing(sport_name=sport_name, shift_day=day)
    main_page_service = MainPageService(data4parsing=data_for_parsing)
    list_links_aft_analysis = DataBaseOnlineService(data_for_parsing).get_list_links_from_db()

    file_name_for_html = f"{sport_name}_{data_for_parsing.match_date}.html"
    if not os.path.exists(file_name_for_html):
        logger.info("Файл не найден!")
        main_page_service.save_html_for_online(file_name_for_html)
    print("*"*88)
    main_page_service.open_html_for_online(file_name_for_html, list_links_aft_analysis)

