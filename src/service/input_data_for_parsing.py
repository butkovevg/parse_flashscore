from src.service.helper import HelperService


class InputDataForParsing:
    def __init__(self, english_sport_name: str, shift_day: int = 0):
        self.english_sport_name = english_sport_name
        self.shift_day = shift_day
        self.match_date = HelperService.get_date_without_point_between_day(day=shift_day)

    def __str__(self):
        return f"{self.english_sport_name}_{self.match_date}"

    def __repr__(self):
        return f"{self.english_sport_name}({self.match_date})"

