import datetime


class HelperService:
    @staticmethod
    def get_date_between_day(day: int):
        current_date = datetime.date.today()
        new_date = current_date + datetime.timedelta(days=day)
        return new_date.strftime('%Y%m%d')