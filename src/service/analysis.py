import os

from sqlalchemy import update

from src.model.tables import CurrentDBModel
from src.service.database import get_session
from src.service.input_data_for_parsing import InputDataForParsing
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)


class AnalysisService:
    def __init__(self):
        self.session = next(get_session())

    def is_match_leader_and_outsder(self, record: CurrentDBModel):
        if record.position_total > 10:
            if record.position1 < 4 and record.position_total - record.position2 < 4:
                self.log_match_leader_and_outsder(record)
            elif record.position2 < 4 and record.position_total - record.position1 < 4:
                self.log_match_leader_and_outsder(record)

    def is_match_with_series(self, record: CurrentDBModel):
        dct_series1 = {}
        dct_series2 = {}
        for letter in record.series1:
            if letter in dct_series1:
                dct_series1[letter] += 1
            else:
                dct_series1[letter] = 1
        for letter in record.series2:
            if letter in dct_series2:
                dct_series2[letter] += 1
            else:
                dct_series2[letter] = 1
        if dct_series1.get("B", 0) > 2 and dct_series2.get("П", 0) > 2:
            self.log_match_with_series(record)
        elif dct_series1.get("B", 0) > 2 and dct_series2.get("П", 0) > 2:
            self.log_match_with_series(record)

    def log_match_with_series(self, record: CurrentDBModel):
        self.update(current_db_model=record)
        logger.warning(f"update {record.team1}:{record.team2} {record.series1} {record.series2}")

    def log_match_leader_and_outsder(self, record):
        self.update(current_db_model=record)
        logger.warning(
            f"update {record.team1}:{record.team2} {record.position1}:{record.position2}==={record.position_total}")

    def main(self):
        unprocessed_records = self.get_list_from_db()
        for record in unprocessed_records:
            self.is_match_leader_and_outsder(record)
            self.is_match_with_series(record)

    def update(self, current_db_model: CurrentDBModel, status: bool = True):
        """
        :param status:
        :return:
        """
        stmt = (
            update(CurrentDBModel).
            where(CurrentDBModel.id == current_db_model.id).
            values(status=status)
        )
        self.session.execute(stmt)
        self.session.commit()

    def get_list_from_db(self):
        try:
            logger.warning(f"1")
            # запрос для всех записей для вида спорта по дате
            query_all_record = (
                self.session
                .query(CurrentDBModel)
                .filter_by(match_date="12.01.2024")
                .filter(CurrentDBModel.position1 != 0)
            )

            # Необработанных записей для вида спорта по дате
            query_unprocessed_record = query_all_record.filter_by(status=None)

            len_all_record = query_all_record.count()
            len_unprocessed_record = query_unprocessed_record.count()

            logger.debug(f"{len_unprocessed_record=}/{len_all_record=}")

            unprocessed_records = query_unprocessed_record.all()

            return unprocessed_records
        except Exception as exc:
            logger.error(f"Подробности ошибки {str(exc)}")
        finally:
            self.session.close()


class InfoAnalysisDBService():
    def __init__(self):
        self.session = next(get_session())
    def get_list_from_db(self):
        # запрос для всех записей для вида спорта по дате

        query_all_record = (
            self.session
            .query(CurrentDBModel)
            .filter_by(match_date="12.01.2024")
            .filter_by(status=True)
            .order_by(CurrentDBModel.match_time)

        )

        matches = query_all_record.all()
        return matches


if __name__ == "__main__":
    logger.info(f'Initializing test {os.path.basename(__file__)}')
    # data_for_parsing1 = InputDataForParsing(sport_name="volleyball", shift_day=0)
    # data_for_parsing2 = InputDataForParsing(sport_name="football", shift_day=0)
    parsing_service = AnalysisService()
    parsing_service.main()
    # window.location.href = xhr.responseText;
    # infoanalysisdbservice= InfoAnalysisDBService()
    # infoanalysisdbservice.main()

