import datetime
from typing import List, Any


class HelperService:
    @staticmethod
    def get_date_between_day(day: int):
        current_date = datetime.date.today()
        new_date = current_date + datetime.timedelta(days=day)
        return new_date.strftime('%Y%m%d')

    @staticmethod
    def get_element_for_list(lst: List, index: int, default_value: Any):
        try:
            return lst[index]
        except IndexError:
            return default_value
