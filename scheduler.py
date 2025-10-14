import argparse
import os

from src.configs.settings import settings
from src.model.types_of_sports import dct_rus_to_eng
from src.service.analysis import AnalysisService
from src.service.current_page import CurrentPageService
from src.service.find_day_for_parsing import FindDayForParsingService
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.logger_handlers import get_logger
from src.service.main_page import MainPageService

logger = get_logger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('--day', type=int, default=4)
parser.add_argument('--start', type=str, default="main")
parser.add_argument('--week', dest='week', action='store_true')
parser.add_argument('--no-week', dest='week', action='store_false')
parser.set_defaults(week=False)

args = parser.parse_args()
day = args.day
start = args.start.lower()
is_week = args.week


class SchedulerService:
    def __init__(self, eng_sport_name: str, shift_day: int):
        self.data_for_parsing = InputDataForParsing(english_sport_name=eng_sport_name, shift_day=shift_day)
        self.main_page_service = MainPageService(data4parsing=self.data_for_parsing)
        self.current_page_service = CurrentPageService(data4parsing=self.data_for_parsing)
        self.analysis_service = AnalysisService(shift_day=shift_day)

    def scan_main_page(self):
        logger.info(f"scan_main_page {self.data_for_parsing}")
        self.main_page_service.get_list_link_with_main_page()
        self.main_page_service.insert()

    def scan_current_page(self):
        logger.info(f"scan_current_page {self.data_for_parsing}")
        self.current_page_service.get_list_links_from_db()

    def scan_analysis(self):
        logger.debug(f"scan_analysis {day=}")
        self.analysis_service.main()


def run_scheduler(rus_sport_name, day_number, mode):
    eng_sport_name = dct_rus_to_eng.get(rus_sport_name)
    scheduler_service = SchedulerService(eng_sport_name=eng_sport_name, shift_day=day_number)
    if mode in ["main"]:
        scheduler_service.scan_main_page()
    elif mode in ["current"]:
        scheduler_service.scan_current_page()
    elif mode in ["analysis"]:
        scheduler_service.scan_analysis()
    else:
        logger.error(f"{mode} don`t found")


def main():
    settings.IS_HEADLESS = False
    logger.debug(f"{day=}")
    list_sport_name_for_parsing = [
        "volleyball",
        "football",
        "basketball",
        "handball",
    ]
    list_tennis_days = [0, 1]  # Нет смысла парсить теннис за два дня и более
    if day in list_tennis_days:
        logger.debug("ADD tennis in list_sport_name_for_parsing")
        list_sport_name_for_parsing.append("tennis")

    if start in ["main"]:
        # MAIN_PAGE
        for sport_name in list_sport_name_for_parsing:
            data_for_parsing = InputDataForParsing(english_sport_name=sport_name, shift_day=day)
            parsing_service = MainPageService(data4parsing=data_for_parsing)
            logger.debug(f"MAIN_PAGE {data_for_parsing}")
            parsing_service.get_list_link_with_main_page()
            parsing_service.insert()

    if start in ["main", "current"]:
        # CURRENT_PAGE
        for sport_name in list_sport_name_for_parsing:
            data_for_parsing = InputDataForParsing(english_sport_name=sport_name, shift_day=day)
            logger.debug(f"CURRENT_PAGE {data_for_parsing}")
            parsing_service = CurrentPageService(data4parsing=data_for_parsing)
            parsing_service.get_list_links_from_db()

    # ANALYSIS
    logger.debug(f"AnalysisService {day=}")
    parsing_service = AnalysisService(shift_day=day)
    parsing_service.main()
    logger.debug(f"FINISH {day=}")


if __name__ == "__main__":
    logger.info(f'Initializing {os.path.basename(__file__)} {settings.VERSION}')
    is_week = True
    if is_week:
        for day in range(0, 5):
            logger.warning(f"WEEK_SCAN {day=}")
            FindDayForParsingService().main(shift_day=day)
            main()

    else:
        FindDayForParsingService().main(shift_day=day)
        main()
