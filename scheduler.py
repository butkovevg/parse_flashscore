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
    def __str__(self):
        return str(self.data_for_parsing.shift_day)
    def scan_main_page(self):
        logger.info(f"   scan_main_page {self.data_for_parsing}")
        # self.main_page_service.get_list_link_with_main_page()
        # self.main_page_service.insert()

    def scan_current_page(self):
        logger.info(f"scan_current_page {self.data_for_parsing}")
        # self.current_page_service.get_list_links_from_db()

    def scan_analysis(self):
        logger.info(f"    scan_analysis {self.data_for_parsing}")
        # self.analysis_service.main()



def get_scheduler_service(eng_sport_name, shift_day: int):
    return SchedulerService(eng_sport_name=eng_sport_name, shift_day=shift_day)


def run_week():
    list_week = [0, 1, 2, 3, 4, 5, 6]
    for shift_day in list_week:
        run_day(shift_day=shift_day)


def run_day(shift_day: int):
    logger.warning(f"--- {shift_day}")
    list_tennis_days = [0, 1]  # Нет смысла парсить теннис за два дня и более
    local_english_list_types_sports = deepcopy(english_list_types_sports)
    if day not in list_tennis_days:
        if 'tennis' in english_list_types_sports:
            local_english_list_types_sports.remove('tennis')

    # list_scheduler_service = []
    for number_of_list, eng_sport_name in enumerate(local_english_list_types_sports):
        scheduler_service = get_scheduler_service(eng_sport_name=eng_sport_name, shift_day=shift_day)
        run_mode(scheduler_service, mode="main")
        run_mode(scheduler_service, mode="current")
        if number_of_list == len(local_english_list_types_sports) - 1:  # Если это последний элемент
            run_mode(scheduler_service, mode="analysis")


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
    # settings.IS_HEADLESS = False
    run_week()

if __name__ == "__main__":
    logger.info(f'Initializing {os.path.basename(__file__)} {settings.VERSION}')
    is_week = True
    if is_week:
        for day in range(0,7):
            FindDayForParsingService().main(shift_day=day)
        run_week()
    else:
        run_day(shift_day=day)
