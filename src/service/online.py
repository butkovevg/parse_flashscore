import os
import time
from datetime import datetime

from sqlalchemy import Time, and_, cast, distinct, or_, select

from src.configs.settings import settings
from src.model.tables import AnalysisDBModel, CurrentDBModel
from src.service.database import get_session
from src.service.helper import HelperService
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.logger_handlers import get_logger
from src.service.main_page import MainPageService, dct_translate_sport_name_rus_eng

logger = get_logger(__name__)


class DataBaseOnlineService:
    finished_status = (
        'Завершен',
        'Будет доигран позже',
        'Неявка',
        'Послеовертайма',
        'Перенесен',
        'Завершен(отказ)',
        'Отменен',
    )

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
                .where(AnalysisDBModel.comment.is_(None))
                .where(or_(
                    AnalysisDBModel.status.is_(None),
                    AnalysisDBModel.status.notin_(DataBaseOnlineService.finished_status)
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
            time_now = datetime.now().strftime("%H:%M")
            query = (
                select(distinct(CurrentDBModel.sport_name))
                .select_from(AnalysisDBModel)  # Явное указание левой стороны JOIN
                .join(CurrentDBModel, CurrentDBModel.link == AnalysisDBModel.link, isouter=True)  # LEFT JOIN
                .where(cast(CurrentDBModel.match_time, Time) < time_now)
                .where(and_(
                    or_(
                        AnalysisDBModel.status.is_(None),
                        AnalysisDBModel.status.notin_(DataBaseOnlineService.finished_status)),
                    CurrentDBModel.match_date == match_date,
                    AnalysisDBModel.comment.is_(None)

                ))
            )
            # Выполнение запроса
            results = self.session.execute(query).scalars().all()
            logger.info(f"Online update sports({len(results)}): {results}")
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

    def update_comment(self, link: str, comment: str):
        list_for_update_analysis = [
            {"link": link,
             "comment": comment,
             },
        ]
        logger.info(f"update_comment {list_for_update_analysis}")
        self.update_analysis_db(list_for_update_analysis)

    def update_analysis_db(self, list_for_update_analysis: list):
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
            for dct_for_update_analysis in list_for_update_analysis:
                link = dct_for_update_analysis['link']
                dct_for_update_analysis.pop('link')

                # Обновление записи по полю link
                self.session.query(AnalysisDBModel).filter_by(link=link).update(dct_for_update_analysis)

            # Фиксация изменений
            self.session.commit()
            logger.debug("Обновление завершено.")

        except Exception as e:
            self.session.rollback()  # Откат изменений в случае ошибки
            logger.error(f"Ошибка: {e}")


def logging_difference_list(list_bef_update, list_aft_update, eng_sport_name):
    if len(list_links_bef_update) != len(list_links_aft_update):
        # Преобразуем списки в множества
        set_aft_update = set(list_aft_update)
        set_bef_update = set(list_bef_update)

        # Находим разницу
        difference = set_bef_update - set_aft_update

        # Преобразуем результат обратно в список (если нужно)
        difference_list = list(difference)

        for link in difference_list:
            base_link = f"https://www.flashscorekz.com/match/{eng_sport_name}/{link}"
            logger.error(f"NO_UPDATE: {base_link}")
            DataBaseOnlineService().update_comment(link=link, comment="NO_UPDATE")


if __name__ == "__main__":
    logger.info(f' Initializing API {settings.TITLE}: {settings.VERSION}')
    logger.info(f' Visit endpoint: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/online/')
    logger.info(f'Initializing file {os.path.basename(__file__)}')

    shift_day = 0
    data_for_parsing = InputDataForParsing(english_sport_name="handball", shift_day=shift_day)

    database_online_service = DataBaseOnlineService()
    match_date_today = HelperService.get_date_with_point_between_day(day=shift_day)

    while True:
        # Список видов спорта, которые есть в ТБ анализв
        list_sport_name = database_online_service.get_list_sport_name(match_date_today)
        list_sport_name = ["ГАНДБОЛ"]

        if len(list_sport_name) == 0:  # Если нет матчей для обновления, то засыпаем до завтра
            logger.info("list_sport_name is empty")
            # HelperService.pause_until_midnight()
        else:
            for rus_sport_name in list_sport_name:
                eng_sport_name = dct_translate_sport_name_rus_eng[rus_sport_name]
                database_online_service = DataBaseOnlineService()
                list_links_bef_update = database_online_service.get_list_links_from_db(rus_sport_name, match_date_today)
                logger.warning(f"________________________{eng_sport_name.upper()}________________________")
                logger.info(f"for {eng_sport_name.upper()} need update links({len(list_links_bef_update)}): {list_links_bef_update}")

                # 02 Запрос по виду спорта для обновления
                data_for_parsing = InputDataForParsing(english_sport_name=eng_sport_name, shift_day=shift_day)
                main_page_service = MainPageService(data4parsing=data_for_parsing)
                # 02 Список, который можно обновить
                list_for_update_analysis, list_links_aft_update = main_page_service.get_list_for_update_analysis(list_links_aft_analysis=list_links_bef_update)

                # 03 Если есть ссылки, которые не обновились, то убираем их с comment="NO_UPDATE"
                logging_difference_list(list_links_bef_update, list_links_aft_update, eng_sport_name)

                # 04 Обновляем
                database_online_service.update_analysis_db(list_for_update_analysis)
        logger.info("waiting 120 sec")
        time.sleep(120)
# Если ссылка не обновляется, то возможно полностью обновлять запись
