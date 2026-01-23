from copy import deepcopy

from sqlalchemy import func

from src.configs.settings import settings
from src.model.tables import AnalysisDBModel, CurrentDBModel, MainDBModel
from src.service.database import get_session
from src.service.helper import HelperService
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)


class FindDayForParsingService:
    dct_types_of_sports = {'ВОЛЕЙБОЛ': 0, 'ФУТБОЛ': 0, 'БАСКЕТБОЛ': 0, 'ГАНДБОЛ': 0, 'ТЕННИС': 0, }

    def __init__(self):
        self.session = next(get_session())
        self.output_dict = {}

    def add_to_dict(self, key: str, list_tuple_sport_value: list):
        self.output_dict[key] = {}
        for tuple_sport_value in list_tuple_sport_value:
            sport, value = tuple_sport_value
            self.output_dict[key][sport] = value

    def all(self):
        output_list = []
        for shift_day in range(7):
            v = self.main(shift_day)
            output_list.append(v)
        return output_list

    def main(self, shift_day):
        date_without_point_between_day = HelperService.get_date_without_point_between_day(day=shift_day)
        date_with_point_between_day = HelperService.get_date_with_point_between_day(day=shift_day)
        output_dict = {
            "dt": date_with_point_between_day,
            "shift_day": shift_day,
            "main": deepcopy(FindDayForParsingService.dct_types_of_sports),
            "curr": deepcopy(FindDayForParsingService.dct_types_of_sports),
            "anal": deepcopy(FindDayForParsingService.dct_types_of_sports),
        }
        # output_dict = deepcopy(pattern_output_dict)
        self.add_to_dict(key="main", list_tuple_sport_value=self.get_main(match_date=date_without_point_between_day))
        self.add_to_dict(key="curr", list_tuple_sport_value=self.get_current(match_date=date_with_point_between_day))
        self.add_to_dict(key="anal", list_tuple_sport_value=self.get_analysis(match_date=date_with_point_between_day))

        for standing_data in ["main", "curr", "anal"]:
            for type_of_sports in FindDayForParsingService.dct_types_of_sports:
                value = self.output_dict.get(standing_data).get(type_of_sports, 0)
                output_dict[standing_data][type_of_sports] = value
        logger.info(output_dict)
        return output_dict

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
            return []
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
                self.session.query(CurrentDBModel.sport_name, func.count(CurrentDBModel.sport_name))
                .select_from(AnalysisDBModel)
                .outerjoin(CurrentDBModel, AnalysisDBModel.link == CurrentDBModel.link)
                .filter(CurrentDBModel.match_date == match_date)
                .group_by(CurrentDBModel.sport_name)
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
    # service.main(shift_day=3)
    service.main(0)
