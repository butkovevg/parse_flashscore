from sqlalchemy import func

from src.configs.settings import settings
from src.model.tables import MainDBModel, CurrentDBModel, AnalysisDBModel
from src.service.database import get_session
from src.service.helper import HelperService
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)


class FindDayForParsingService:

    def __init__(self):
        self.session = next(get_session())
        self.output_dict = {}

    def add_to_dict(self, key: str, list_touple_sport_value:list):
        self.output_dict[key]={}
        for touple_sport_value in list_touple_sport_value:
            sport, value = touple_sport_value
            self.output_dict[key][sport] = value

    def all(self):
        for shift_day in range(7):
            self.main(shift_day)

    def main(self, shift_day):
        date_without_point_between_day = HelperService.get_date_without_point_between_day(day=shift_day)
        date_with_point_between_day = HelperService.get_date_with_point_between_day(day=shift_day)
        self.add_to_dict(key="main", list_touple_sport_value=self.get_main(match_date=date_without_point_between_day))
        self.add_to_dict(key="curr", list_touple_sport_value=self.get_current(match_date=date_with_point_between_day))
        self.add_to_dict(key="anal", list_touple_sport_value=self.get_analysis(match_date=date_with_point_between_day))
        print(f"{shift_day}_{date_with_point_between_day}_V____________F____________B____________G_")
        for stage_proc in ["main", "curr", "anal"]:
            v = self.output_dict.get(stage_proc).get('ВОЛЕЙБОЛ', 0)
            f = self.output_dict.get(stage_proc).get('ФУТБОЛ', 0)
            b = self.output_dict.get(stage_proc).get('БАСКЕТБОЛ', 0)
            g = self.output_dict.get(stage_proc).get('ГАНДБОЛ', 0)
            print(f"{stage_proc:<10}   {v:<10}   {f:<10}   {b:<10}   {g:<10}")
        print("_"*54)
    def get_main(self, match_date):
        try:
            query = (
                self.session
                .query(MainDBModel.sport_name, func.count(MainDBModel.sport_name))
                .filter(MainDBModel.match_date == match_date)
                .group_by(MainDBModel.sport_name)
            )
            results = query.all()
            return results
        except Exception as exc:
            logger.error(f"Подробности ошибки {str(exc)}")
        finally:
            self.session.close()
    def get_current(self, match_date):
        try:
            query = (
                self.session
                .query(CurrentDBModel.sport_name, func.count(CurrentDBModel.sport_name))
                .filter(CurrentDBModel.match_date == match_date)
                .group_by(CurrentDBModel.sport_name)
            )
            results = query.all()
            return results
        except Exception as exc:
            logger.error(f"Подробности ошибки {str(exc)}")
        finally:
            self.session.close()
    def get_analysis(self, match_date):
        try:
            query = (
                self.session.query(CurrentDBModel.sport_name, func.count(CurrentDBModel.sport_name)) \
                .select_from(AnalysisDBModel) \
                .outerjoin(CurrentDBModel, AnalysisDBModel.link == CurrentDBModel.link) \
                .filter(CurrentDBModel.match_date == match_date) \
                .group_by(CurrentDBModel.sport_name) \
                )
            results = query.all()
            return results
        except Exception as exc:
            logger.error(f"Подробности ошибки {str(exc)}")
        finally:
            self.session.close()


if __name__ == '__main__':
    logger.info(f'Initializing FindDayForParsingService: {settings.VERSION}')
    service = FindDayForParsingService()
    service.main(shift_day=1)
    # service.all()
