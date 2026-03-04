from copy import deepcopy
from typing import Any

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

    def for_stat(self, data: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """
        Обрабатывает статистику по видам спорта.

        Возвращает словарь с тремя наборами данных:
        1. daily_totals: Суммы по дням (main, curr, anal).
        2. sport_totals: Суммы по видам спорта за весь период.
        3. percentages: Отношения curr/main и anal/curr в процентах по дням.
        """
        if not data:
            return {"daily_totals": [], "sport_totals": {}, "percentages": []}

        # 1. Расчет сумм по дням (data_for_stat_day)
        daily_totals = []
        for entry in data:
            # sum(dict.values()) быстрее и читаемее ручного цикла
            daily_totals.append({
                "dt": entry["dt"],
                "shift_day": entry["shift_day"],
                "main": sum(entry["main"].values()),
                "curr": sum(entry["curr"].values()),
                "anal": sum(entry["anal"].values())
            })
        logger.info(f"Daily totals calculated: {daily_totals}")

        # 2. Расчет сумм по видам спорта (dict_counter_for_stat_types_of_sports)
        # Инициализируем нулями на основе ключей dct_types_of_sports
        categories = ['main', 'curr', 'anal']
        sport_totals = {
            cat: {sport: 0 for sport in self.dct_types_of_sports}
            for cat in categories
        }

        for entry in data:
            for cat in categories:
                for sport in self.dct_types_of_sports:
                    # Используем .get(), чтобы избежать KeyError, если спорт вдруг отсутствует в entry
                    sport_totals[cat][sport] += entry.get(cat, {}).get(sport, 0)

        logger.info(f"Sport totals calculated: {sport_totals}")

        # 3. Расчет процентов (percent_for_main_curr_anal)
        percentages = []
        for entry in data:
            row = {
                "dt": entry["dt"],
                "shift_day": entry["shift_day"]
            }
            for sport in self.dct_types_of_sports:
                main_val = entry["main"].get(sport, 0)
                curr_val = entry["curr"].get(sport, 0)
                anal_val = entry["anal"].get(sport, 0)

                # Безопасный расчет процента
                curr_to_main = round(curr_val * 100 / main_val) if main_val else 0
                anal_to_curr = round(anal_val * 100 / curr_val) if curr_val else 0

                row[sport] = f"{curr_to_main}/{anal_to_curr}"

            percentages.append(row)
        logger.info(f"Percentages calculated: {percentages}")

        return {
            "daily_totals": daily_totals,
            "sport_totals": sport_totals,
            "percentages": percentages
        }


if __name__ == '__main__':
    logger.info(f'Initializing FindDayForParsingService: {settings.VERSION}')
    service = FindDayForParsingService()
    # service.main(shift_day=3)
    service.main(0)
