import datetime
from typing import List, Any


class HelperService:

    @staticmethod
    def get_new_date(day: int) -> datetime.date:
        """
        Возвращает новую дату, сдвинутую на указанное количество дней.
        :param day: int - Количество дней, на которое нужно сдвинуть текущую дату.
        :return: datetime.date Новая дата.
        """
        current_date = datetime.date.today()
        new_date = current_date + datetime.timedelta(days=day)
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
    def get_element_for_list(lst: List, index: int, default_value: Any) -> Any:
        """
        Возвращает элемент списка по указанному индексу или значение по умолчанию, если такой элемент не существует.
        :param lst: List - Список, из которого нужно получить элемент.
        :param index: int - Индекс элемента в списке.
        :param default_value: - Any Значение, которое будет возвращено, если элемента с указанным индексом не существует в списке.
        :return: datetime.date Новая дата в формате 'DD.MM.YYYY'.
        """
        try:
            return lst[index]
        except IndexError:
            return default_value
