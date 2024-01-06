from src.service.helper import HelperService


class InputDataForParsing:
    def __init__(self, sport_name: str = "football", shift_day: int = 0):
        self.sport_name = sport_name
        self.shift_day = shift_day
        self.match_date = HelperService.get_date_between_day(day=shift_day)

    def __str__(self):
        return f"STR: {self.sport_name}({self.match_date})"

    def __repr__(self):
        return f"REPR: {self.sport_name}({self.match_date})"
