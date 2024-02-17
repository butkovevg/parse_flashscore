import os
from src.configs.settings import settings
from src.service.analysis import AnalysisService
from src.service.logger_handlers import get_logger

from src.service.current_page import CurrentPageService
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.main_page import MainPageService

logger = get_logger(__name__)
if __name__ == "__main__":
    logger.info(f'Initializing scheduler {os.path.basename(__file__)} {settings.VERSION}')
    list_day = [1,2,3]
    for day in list_day:
        logger.debug(f"{day=}")
        list_sport_name_for_parsing = ["volleyball", "football", "basketball", "handball"]

        # MAIN_PAGE
        for sport_name in list_sport_name_for_parsing:
            data_for_parsing = InputDataForParsing(sport_name=sport_name, shift_day=day)
            parsing_service = MainPageService(data4parsing=data_for_parsing)
            logger.debug(f"MAIN_PAGE {data_for_parsing}")
            parsing_service.get_list_link_with_main_page()
            parsing_service.insert()

        # CURRENT_PAGE
        for sport_name in list_sport_name_for_parsing:
            data_for_parsing = InputDataForParsing(sport_name=sport_name, shift_day=day)
            logger.debug(f"CURRENT_PAGE {data_for_parsing}")
            parsing_service = CurrentPageService(data4parsing=data_for_parsing)
            parsing_service.get_list_links_from_db()

        # ANALYSIS
        logger.debug(f"AnalysisService {day=}")
        parsing_service = AnalysisService(shift_day=day)
        parsing_service.main()
