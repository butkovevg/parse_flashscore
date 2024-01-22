import os

from src.service.analysis import AnalysisService
from src.service.logger_handlers import get_logger




from src.service.current_page import CurrentPageService
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.main_page import MainPageService

logger = get_logger(__name__)
if __name__ == "__main__":
    logger.info(f'Initializing scheduler {os.path.basename(__file__)}')
    list_day = [3]
    for day in list_day:
        data_for_parsing1 = InputDataForParsing(sport_name="volleyball", shift_day=day)
        data_for_parsing2 = InputDataForParsing(sport_name="football", shift_day=day)
        data_for_parsing3 = InputDataForParsing(sport_name="basketball", shift_day=day)
        data_for_parsing4 = InputDataForParsing(sport_name="handball", shift_day=day)
        logger.warning(f"{day=}")
        list_data_for_parsing = [data_for_parsing1,
                                 data_for_parsing2,
                                 data_for_parsing3,
                                 data_for_parsing4,
                                 ]
        for data_for_parsing in list_data_for_parsing:
            parsing_service = MainPageService(data4parsing=data_for_parsing)
            logger.warning(f"MAIN {data_for_parsing}")
            parsing_service.get_list_link_with_main_page()
            parsing_service.insert()

        for data_for_parsing in list_data_for_parsing:
            logger.warning(f"CURRENT {data_for_parsing}")
            parsing_service = CurrentPageService(data4parsing=data_for_parsing)
            parsing_service.get_list_links_from_db()
        logger.warning(f"AnalysisService {day=}")
        parsing_service = AnalysisService(shift_day=day)
        parsing_service.main()
