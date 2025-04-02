import os
import time

from sqlalchemy import select, distinct, and_, or_

from src.configs.settings import settings
from src.model.tables import AnalysisDBModel, CurrentDBModel
from src.service.database import get_session
from src.service.helper import HelperService
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.logger_handlers import get_logger
from src.service.main_page import dct_translate_sport_name_rus_eng, MainPageService

logger = get_logger(__name__)


class DataBaseOnlineService:
    def __init__(self):
        self.session = next(get_session())

    def get_list_links_from_db(self, rus_sport_name, match_date):
        try:
            # Создание запроса
            query = (
                select(AnalysisDBModel.link)
                .join(CurrentDBModel, CurrentDBModel.link == AnalysisDBModel.link, isouter=True)  # LEFT JOIN
                .where(CurrentDBModel.sport_name == rus_sport_name)
                .where(CurrentDBModel.match_date == match_date)
                .where(or_(
                    AnalysisDBModel.status.is_(None),
                    AnalysisDBModel.status.notin_(('Завершен', 'Будет доигран позже'))
                ))
            )
            # Выполнение запроса
            results = self.session.execute(query).scalars().all()
            return results
        except Exception as exc:
            logger.error(f"Error for {rus_sport_name}")
            logger.error(f"Details: {str(exc)}")
            return []
        finally:
            self.session.close()

    def get_list_sport_name(self, match_date):
        try:
            # Создание запроса
            query = (
                select(distinct(CurrentDBModel.sport_name))
                .select_from(AnalysisDBModel)  # Явное указание левой стороны JOIN
                .join(CurrentDBModel, CurrentDBModel.link == AnalysisDBModel.link, isouter=True)  # LEFT JOIN
                .where(and_(
                    AnalysisDBModel.status.is_(None),
                    CurrentDBModel.match_date == match_date
                ))
            )
            # Выполнение запроса
            results = self.session.execute(query).scalars().all()
            logger.info(f"Online update sports: {results}")
            return results

        except Exception as exc:
            logger.error(f"Error for {match_date}")
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

    def update_status_in_analysis_db(self, list_for_update_analysis: list):
        try:
            # # # Подготовка данных для массового обновления
            # # update_data = []
            # # for item in list_for_update_analysis:
            # #     update_data.append({'link': item['link'], 'status': item['status']})
            #
            # # Массовое обновление
            # self.session.bulk_update_mappings(AnalysisDBModel, list_for_update_analysis)
            #
            # # Фиксация изменений в базе данных
            # self.session.commit()
            # print("Массовое обновление завершено.")
            for item in list_for_update_analysis:
                link = item['link']
                new_status = item['status']
                result = item['result']
                who_now_win = item['who_now_win']

                # Обновление записи по полю link
                self.session.query(AnalysisDBModel).filter_by(link=link).update(
                    {'status': new_status, 'result': result, 'who_now_win': who_now_win})

            # Фиксация изменений
            self.session.commit()
            print("Обновление завершено.")

        except Exception as e:
            self.session.rollback()  # Откат изменений в случае ошибки
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    logger.info(f' Initializing API {settings.TITLE}: {settings.VERSION}')
    logger.info(f' Visit endpoint: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/online/')
    logger.info(f'Initializing file {os.path.basename(__file__)}')

    day = 0
    data_for_parsing = InputDataForParsing(sport_name="__basketball", shift_day=day)

    database_online_service = DataBaseOnlineService()
    match_date_today = HelperService.get_date_with_point_between_day(day=0)

    while True:
        list_sport_name = database_online_service.get_list_sport_name(match_date_today)
        list_sport_name = ["ФУТБОЛ"]  # ToDo: MOCK
        list_sport_name = ["БАСКЕТБОЛ"]  # ToDo: MOCK MXcYQT2d

        if len(list_sport_name) == 0:  # Если нет матчей для обновления, то засыпаем до завтра
            logger.info("list_sport_name is empty")
            HelperService.pause_until_midnight()
            break

        for rus_sport_name in list_sport_name:
            eng_sport_name = dct_translate_sport_name_rus_eng[rus_sport_name]
            database_online_service = DataBaseOnlineService()
            list_links_aft_analysis = database_online_service.get_list_links_from_db(rus_sport_name, match_date_today)
            logger.info(f"For {eng_sport_name} need update links: {list_links_aft_analysis}")

            # 02 Запрос по виду спорта для обновления
            data_for_parsing = InputDataForParsing(sport_name=eng_sport_name, shift_day=day)
            main_page_service = MainPageService(data4parsing=data_for_parsing)
            # 02 Список, который можно обновить
            list_for_update_analysis = main_page_service.get_list_for_update_analysis(
                list_links_aft_analysis=list_links_aft_analysis)
            for dct_for_update_analysis in list_for_update_analysis:
                logger.debug(f"{eng_sport_name}: {dct_for_update_analysis}")

            # 03 Обновляем и ждем
            database_online_service.update_status_in_analysis_db(list_for_update_analysis)
            logger.debug(f"Waiting {settings.PAUSE_SEC}")
            time.sleep(settings.PAUSE_SEC)

        exit()
