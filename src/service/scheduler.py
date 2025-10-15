import argparse
import os
from copy import deepcopy

from src.configs.settings import settings
from src.model.types_of_sports import (
    ModeParseEnum,
    TypesOfSportsModel,
    dct_rus_to_eng,
    english_list_types_sports,
    list_mode_parse,
)
from src.service.analysis import AnalysisService
from src.service.current_page import CurrentPageService
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.logger_handlers import logger
from src.service.main_page import MainPageService

parser = argparse.ArgumentParser()
parser.add_argument('--day', type=int, default=4)
parser.add_argument('--mode', type=str, default="main")
parser.add_argument('--week', dest='week', action='store_true')
parser.add_argument('--no-week', dest='week', action='store_false')
parser.set_defaults(week=False)

args = parser.parse_args()
day = args.day
mode = args.mode.lower()
is_week = args.week


class SchedulerService:
    def __init__(self, eng_sport_name: str, shift_day: int):
        self.data_for_parsing = InputDataForParsing(english_sport_name=eng_sport_name, shift_day=shift_day)
        self.main_page_service = MainPageService(data4parsing=self.data_for_parsing)
        self.current_page_service = CurrentPageService(data4parsing=self.data_for_parsing)
        self.analysis_service = AnalysisService(shift_day=shift_day)

    # def __del__(self):
    #     self.scan_analysis()

    def __str__(self):
        return f"{self.data_for_parsing.shift_day} {self.data_for_parsing.english_sport_name}"

    def scan_main_page(self):
        logger.info(f"   scan_main_page {self.data_for_parsing}")
        # self.main_page_service.get_list_link_with_main_page()
        # self.main_page_service.insert()

    def scan_current_page(self):
        logger.info(f"scan_current_page {self.data_for_parsing}")
        # self.current_page_service.get_list_links_from_db()

    def scan_analysis(self):
        logger.info(f"    scan_analysis {self.data_for_parsing.shift_day}")
        # self.analysis_service.main()


def get_scheduler_service(eng_sport_name: str, shift_day: int):
    return SchedulerService(eng_sport_name=eng_sport_name, shift_day=shift_day)


def run_mode(scheduler_service: SchedulerService, mode: str):
    if mode in ["main"]:
        scheduler_service.scan_main_page()
    elif mode in ["current"]:
        scheduler_service.scan_current_page()
    elif mode in ["analysis"]:
        scheduler_service.scan_analysis()
    else:
        logger.error(f"{mode} don`t found")


class ManagerScheduler:
    """
    Логика отбора запуска:
    1. Какие виды спорта запускать
    2. За какие дни запускать.
    3.  Со скрытым браузером
    4. В режиме только main, current, analysis или all
    """

    def __init__(self,
                 rus_sport_name: TypesOfSportsModel,
                 shift_day: int | None = None,
                 is_hidden: bool = True,
                 mode_parse: ModeParseEnum = ModeParseEnum.main
                 ):

        # 1. Какие виды спорта запускать: конкретный вид спорта или все
        if rus_sport_name == TypesOfSportsModel.all_types_of_sports:
            self.english_list_types_sports = english_list_types_sports
        else:
            self.english_list_types_sports = [dct_rus_to_eng.get(rus_sport_name.value)]

        # 2. За какие дни запускать.
        if shift_day is None:
            self.list_days = [0, 1, 2, 3, 4, 5, 6]
        else:
            self.list_days = [shift_day]

        # 3.  Со скрытым браузером
        settings.IS_HEADLESS = is_hidden
        self.is_hidden = is_hidden

        # 4. В режиме только main, current, analysis или all
        if mode_parse == ModeParseEnum.all_mode:
            self.list_mode_parse = list_mode_parse
        else:
            self.list_mode_parse = [mode_parse.value]

    def run_week(self):
        for shift_day in self.list_days:
            self.run_day(shift_day=shift_day)

    def run_day(self, shift_day: int):
        logger.warning(f"---run_day {shift_day}")
        list_tennis_days = [0, 1]  # Нет смысла парсить теннис за два дня и более
        local_english_list_types_sports = deepcopy(self.english_list_types_sports)
        if shift_day not in list_tennis_days:
            if 'tennis' in local_english_list_types_sports:
                local_english_list_types_sports.remove('tennis')

        list_scheduler_service = []
        for eng_sport_name in local_english_list_types_sports:
            scheduler_service = get_scheduler_service(eng_sport_name=eng_sport_name, shift_day=shift_day)
            list_scheduler_service.append(scheduler_service)

        # Чтобы для каждого дня сначала шли все MAIN_PAGE, потом все CURRENT_PAGE, потом один analysis
        # Main
        if "main" in self.list_mode_parse:
            settings.IS_HEADLESS = False
            for scheduler_service in list_scheduler_service:
                run_mode(scheduler_service=scheduler_service, mode="main")

        # Current
        if "current" in self.list_mode_parse:
            settings.IS_HEADLESS = True
            for scheduler_service in list_scheduler_service:
                run_mode(scheduler_service=scheduler_service, mode="current")
        if "analysis" in self.list_mode_parse:
            if len(list_scheduler_service) > 0:
                run_mode(scheduler_service=list_scheduler_service[0], mode="analysis")


def main():
    pass


if __name__ == "__main__":
    logger.info(f'Initializing {os.path.basename(__file__)} {settings.VERSION}')
