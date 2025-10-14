import argparse
import os
from copy import deepcopy

from src.configs.settings import settings
from src.model.types_of_sports import english_list_types_sports
from src.service.analysis import AnalysisService
from src.service.current_page import CurrentPageService
from src.service.find_day_for_parsing import FindDayForParsingService
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

    def __del__(self):
        self.scan_analysis()

    def __str__(self):
        return f"{self.data_for_parsing.shift_day} {self.data_for_parsing.english_sport_name}"

    def scan_main_page(self):
        logger.info(f"   scan_main_page {self.data_for_parsing}")
        self.main_page_service.get_list_link_with_main_page()
        self.main_page_service.insert()

    def scan_current_page(self):
        logger.info(f"scan_current_page {self.data_for_parsing}")
        self.current_page_service.get_list_links_from_db()

    def scan_analysis(self):
        logger.info(f"    scan_analysis {self.data_for_parsing.shift_day}")
        self.analysis_service.main()


def get_scheduler_service(eng_sport_name: str, shift_day: int):
    return SchedulerService(eng_sport_name=eng_sport_name, shift_day=shift_day)


def run_week():
    list_week = [0, 1, 2, 3, 4, 5, 6]
    for shift_day in list_week:
        run_day(shift_day=shift_day)


def run_day(shift_day: int):
    logger.warning(f"---run_day {shift_day}")
    list_tennis_days = [0, 1]  # Нет смысла парсить теннис за два дня и более
    local_english_list_types_sports = deepcopy(english_list_types_sports)
    if day not in list_tennis_days:
        if 'tennis' in english_list_types_sports:
            local_english_list_types_sports.remove('tennis')

    list_scheduler_service = []
    for eng_sport_name in local_english_list_types_sports:
        scheduler_service = get_scheduler_service(eng_sport_name=eng_sport_name, shift_day=shift_day)
        list_scheduler_service.append(scheduler_service)

    # Чтобы для каждого дня сначала шли все MAIN_PAGE, потом все CURRENT_PAGE, потом один analysis
    is_call_method = False
    if is_call_method:
        list_methods = []
        for scheduler_service in list_scheduler_service:
            list_methods.append(lambda svc=scheduler_service: run_mode(scheduler_service=svc, mode="main"))

        for scheduler_service in list_scheduler_service:
            list_methods.append(lambda svc=scheduler_service: run_mode(scheduler_service=svc, mode="current"))

        for call_method in list_methods:
            call_method()
    else:
        # Main
        settings.IS_HEADLESS = False
        for scheduler_service in list_scheduler_service:
            run_mode(scheduler_service=scheduler_service, mode="main")

        # Current
        settings.IS_HEADLESS = True
        for scheduler_service in list_scheduler_service:
            run_mode(scheduler_service=scheduler_service, mode="current")


def run_mode(scheduler_service: SchedulerService, mode: str):
    if mode in ["main"]:
        scheduler_service.scan_main_page()
    elif mode in ["current"]:
        scheduler_service.scan_current_page()
    elif mode in ["analysis"]:
        scheduler_service.scan_analysis()
    else:
        logger.error(f"{mode} don`t found")


def main():
    pass


if __name__ == "__main__":
    logger.info(f'Initializing {os.path.basename(__file__)} {settings.VERSION}')
    if is_week:
        for day in range(0, 7):
            FindDayForParsingService().main(shift_day=day)
        run_week()
    else:
        run_day(shift_day=day)
