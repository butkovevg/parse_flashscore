import os
import time

from sqlalchemy import Time, and_, cast, distinct, or_, select

from src.configs.settings import settings
from src.model.response import ResponseModel, StatusModel
from src.model.tables import AnalysisDBModel, CurrentDBModel
from src.service.current_page import CurrentPageService
from src.service.database import get_session
from src.service.helper import HelperService
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.logger_handlers import logger
from src.service.main_page import MainPageService, dct_translate_sport_name_rus_eng


class DataBaseOnlineService:
    finished_status = (
        'Завершен',
        'ЗАВЕРШЕН',
        'Будет доигран позже',
        'Неявка',
        'Послеовертайма',
        'Перенесен',
        'Завершен(отказ)',
        'ОТМЕНЕН',
        'ТЕХ. ПОРАЖЕНИЕ',
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

    def get_list_links_analysys_for_day(self, match_date):
        try:
            # Создание запроса
            query = (
                select(
                    CurrentDBModel.link,
                    CurrentDBModel.sport_name,
                    CurrentDBModel.status,
                    AnalysisDBModel.who_must_win)
                .select_from(AnalysisDBModel)  # Явное указание левой стороны JOIN
                .join(CurrentDBModel, CurrentDBModel.link == AnalysisDBModel.link, isouter=True)  # LEFT JOIN
                .where(and_(
                    or_(
                        AnalysisDBModel.status.is_(None),
                        AnalysisDBModel.status.notin_(DataBaseOnlineService.finished_status)),
                    CurrentDBModel.match_date == match_date,
                    AnalysisDBModel.comment.is_(None)

                ))
            )
            # Выполнение запроса
            results = self.session.execute(query).all()
            logger.info(f"get_list_links_analysys_for_day({len(results)})")
            return results

        except Exception as exc:
            logger.error(f"Error for {match_date}")
            logger.error(f"Details: {str(exc)}")
            return []
        finally:
            self.session.close()

    def get_historical_analytics(self, match_date: str = "03.02.2026"):
        list_links_analysis_for_day = self.get_list_links_analysys_for_day(match_date=match_date)

        counter = 0
        for tuple_from_db in list_links_analysis_for_day:
            link = tuple_from_db[0]
            rus_translate_sport_name = tuple_from_db[1]
            english_sport_name = dct_translate_sport_name_rus_eng[rus_translate_sport_name.upper()]

            logger.debug(
                f" {link=}  {rus_translate_sport_name}({english_sport_name}) status {tuple_from_db[2]} who_must_win {tuple_from_db[3]}")
            data4parsing = InputDataForParsing(english_sport_name=english_sport_name, should_fetch_odds=False)

            current_page_service = CurrentPageService(data4parsing=data4parsing)
            response: StatusModel = current_page_service.get_current_match(link=link, mode="update")

            counter += 1
            if response.status == StatusModel.SUCCESS:
                service = DataBaseOnlineService()
                dct = response.data
                status = dct.get('status', 'NO_STATUS')
                if status not in DataBaseOnlineService.finished_status:
                    logger.error(f"{link} {status=} for {DataBaseOnlineService.finished_status=}")
                    logger.error(f"{HelperService.get_full_link(english_sport_name=english_sport_name, link=link)}")
                if status == 'TKP - ТОЛЬКО КОНЕЧНЫЙ РЕЗУЛЬТАТ.' or  "ОТКАЗ" in status:
                    dct['status'] = "ОТМЕНЕН"
                logger.info(
                    f"{english_sport_name:10} {match_date}({counter}/{len(list_links_analysis_for_day)}) for {dct.get('link', 'NO_LINK')} {dct.get('status', 'NO_STATUS')}({dct.get('result', 'NO_RESULT')}<{dct.get('who_now_win', 'NO_who_now_win')}>)")

                service.update_analysis_db([dct])
            else:
                logger.error(f"Error for {link}")
                logger.error(f"{HelperService.get_full_link(english_sport_name=english_sport_name, link=link)}")
        return ResponseModel()


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
    endpoint_name = "offline"
    logger.info(f' Initializing API {settings.TITLE}: {settings.VERSION}')
    logger.info(f' Visit endpoint: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/{endpoint_name}/')
    logger.info(f'Initializing file {os.path.basename(__file__)}')
    database_online_service = DataBaseOnlineService()

    if endpoint_name == "online":
        shift_day = 0
        data_for_parsing = InputDataForParsing(english_sport_name="handball", shift_day=shift_day)

        match_date_today = HelperService.get_date_with_point_between_day(day=shift_day)

        while True:
            # Список видов спорта, которые есть в ТБ анализв
            list_sport_name = database_online_service.get_list_sport_name(match_date_today)
            logger.warning(list_sport_name)
            # list_sport_name = ["ТЕННИС"]

            if len(list_sport_name) == 0:  # Если нет матчей для обновления, то засыпаем до завтра
                logger.info("list_sport_name is empty")
                # HelperService.pause_until_midnight()
            else:
                for rus_sport_name in list_sport_name:
                    eng_sport_name = dct_translate_sport_name_rus_eng[rus_sport_name]
                    database_online_service = DataBaseOnlineService()
                    list_links_bef_update = database_online_service.get_list_links_from_db(rus_sport_name,
                                                                                           match_date_today)
                    logger.warning(f"________________________{eng_sport_name.upper()}________________________")
                    logger.info(
                        f"for {eng_sport_name.upper()} need update links({len(list_links_bef_update)}): {list_links_bef_update}")

                    # 02 Запрос по виду спорта для обновления
                    data_for_parsing = InputDataForParsing(english_sport_name=eng_sport_name, shift_day=shift_day)
                    main_page_service = MainPageService(data4parsing=data_for_parsing)
                    # 02 Список, который можно обновить
                    list_for_update_analysis, list_links_aft_update = main_page_service.get_list_for_update_analysis(
                        list_links_aft_analysis=list_links_bef_update)

                    # 03 Если есть ссылки, которые не обновились, то убираем их с comment="NO_UPDATE"
                    logging_difference_list(list_links_bef_update, list_links_aft_update, eng_sport_name)

                    # 04 Обновляем
                    database_online_service.update_analysis_db(list_for_update_analysis)
            logger.info("waiting 120 sec")
            time.sleep(120)
            # Если ссылка не обновляется, то возможно полностью обновлять запись

    elif endpoint_name == "offline":
        from datetime import datetime, timedelta

        # Вчерашняя дата
        yesterday = datetime.now() - timedelta(days=1)
        # 5 лет назад
        start_date = yesterday - timedelta(days=5 * 365)

        # Цикл от сегодняшней даты назад к 5 годам назад
        current_date = yesterday
        while current_date >= start_date:
            match_date = current_date.strftime("%d.%m.%Y")
            logger.info(f"{'-' * 99}Start {match_date}({HelperService.get_day_name(date_str=match_date)})")
            database_online_service.get_historical_analytics(match_date=match_date)
            current_date -= timedelta(days=1)  # шаг на 1 день назад
