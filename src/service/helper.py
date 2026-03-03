import datetime
import time
from typing import Any

from src.service.logger_handlers import get_logger

logger = get_logger(__name__)


class HelperService:
    @staticmethod
    def get_full_link(english_sport_name: str, link: str):
        base_link = f"https://www.flashscorekz.com/match/{english_sport_name}/{link}"
        fragment_table = "#/standings/table/overall"
        full_link = f"{base_link}/{fragment_table}"
        return full_link

    @staticmethod
    def get_day_name(date_str):
        date_obj = datetime.datetime.strptime(date_str, "%d.%m.%Y")

        # Номер дня недели (0 = понедельник, 6 = воскресенье)
        weekday_num = date_obj.weekday()

        # Название дня недели на русском
        days_ru = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        day_name = days_ru[weekday_num]
        return day_name

    @staticmethod
    def get_new_date(day: int) -> datetime.date:
        """
        Возвращает новую дату, сдвинутую на указанное количество дней.
        :param day: int - Количество дней, на которое нужно сдвинуть текущую дату.
        :return: datetime.date Новая дата.
        """
        current_date = datetime.date.today()
        new_date = current_date + datetime.timedelta(days=day)
        # logger.debug(f"get_new_date({day=}): return {new_date}")
        return new_date

    @staticmethod
    def get_date_without_point_between_day(day: int) -> str:
        """
        Возвращает новую дату, сдвинутую на указанное количество дней, в формате 'YYYYMMDD'.
        :param day: int - Количество дней, на которое нужно сдвинуть текущую дату.
        :return: datetime.date Новая дата в формате 'YYYYMMDD'.
        """
        new_date = HelperService.get_new_date(day=day)
        return new_date.strftime('%Y%m%d')

    @staticmethod
    def get_date_with_point_between_day(day: int) -> str:
        """
        Возвращает новую дату, сдвинутую на указанное количество дней, в формате 'DD.MM.YYYY'.
        :param day: int - Количество дней, на которое нужно сдвинуть текущую дату.
        :return: datetime.date Новая дата в формате 'DD.MM.YYYY'.
        """
        new_date = HelperService.get_new_date(day=day)
        return new_date.strftime('%d.%m.%Y')

    @staticmethod
    def get_element_for_list(lst: list[Any], index: int, default_value: Any) -> Any:
        """
        Возвращает элемент списка по указанному индексу или значение по умолчанию, если такой элемент не существует.
        :param lst: list - Список, из которого нужно получить элемент.
        :param index: int - Индекс элемента в списке.
        :param default_value: - Any Значение, которое будет возвращено, если элемента с указанным индексом не существует
        в списке.
        :return: datetime.date Новая дата в формате 'DD.MM.YYYY'.
        """
        try:
            return lst[index]
        except IndexError:
            return default_value

    @staticmethod
    def pause_until_midnight():
        # Текущее время
        now = datetime.datetime.now()
        # Время полуночи следующего дня
        midnight = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        # Разница между текущим временем и полуночью
        sleep_duration = (midnight - now).total_seconds()
        # Приостановка программы
        logger.info(f"Приостановка программы на {sleep_duration:.0f} секунд до полуночи...")
        time.sleep(sleep_duration)

    @staticmethod
    def get_who_now_win(result: str):
        """Логика описана в /model/tables/AnalysisDB"""
        number_of_results_per_match = 2  # Кол-во результатов в матче
        if "-:-" in result:
            return None
        try:
            list_result = result.split(":")

            if len(list_result) != number_of_results_per_match:
                logger.warning(f"No 2 result for {result}:{list_result}")
            res_team1 = int(list_result[0])
            res_team2 = int(list_result[1])
            if res_team1 > res_team2:
                return 1
            elif res_team1 < res_team2:
                return 2
            elif res_team1 == res_team2:
                return 3
            else:  # Такого не может быть)))
                logger.warning(f"Look case {result}")
                return 4
        except ValueError:
            logger.error("result format INT:INT")
        except Exception as exc:
            logger.error(f"New err for {result}")
            logger.error(exc)
            return None


if __name__ == "__main__":
    import os

    logger.info(f'Initializing test {os.path.basename(__file__)}')
    list_sport_name_rus_eng = [
        "football",
        "volleyball",
        "basketball",
        "handball",
        "tennis",
    ]
    logger.info(HelperService.get_full_link(english_sport_name="football", link="UZ73R5LF"))
