import os

from sqlalchemy import update

from src.model.tables import CurrentDBModel, AnalysisDBModel
from src.service.database import get_session
from src.service.helper import HelperService
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)


class AnalysisService:
    def __init__(self, shift_day: int = 0):
        self.session = next(get_session())
        self.shift_day = shift_day

    def is_match_leader_and_outsider(self, record: CurrentDBModel):
        if record.position_total > 10:
            if record.position1 < 4 and record.position_total - record.position2 < 4:
                self.log_match_leader_and_outsider(record)
            elif record.position2 < 4 and record.position_total - record.position1 < 4:
                self.log_match_leader_and_outsider(record)

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

    def log_match_leader_and_outsider(self, record):
        self.update(current_db_model=record)
        logger.warning(
            f"update {record.team1}:{record.team2} {record.position1}:{record.position2}==={record.position_total}")

    def main(self):
        unprocessed_records = self.get_list_from_db()
        for record in unprocessed_records:
            self.is_match_leader_and_outsider(record)
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
            # запрос для всех записей для вида спорта по дате
            query_all_record = (
                self.session
                .query(CurrentDBModel)
                .filter_by(match_date=HelperService.get_date_with_point_between_day(self.shift_day))
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


class InfoAnalysisDBService:
    def __init__(self, shift_day: int = 0):
        self.session = next(get_session())
        self.shift_day = shift_day

    def get_list_from_db(self):
        # запрос для всех записей для вида спорта по дате

        query_all_record = (
            self.session
            .query(CurrentDBModel)
            .filter_by(match_date=HelperService.get_date_with_point_between_day(day=self.shift_day))
            .filter_by(status=True)
            .order_by(CurrentDBModel.match_time)

        )

        matches = query_all_record.all()
        logger.warning(f"{matches=}")
        return matches

    def printer_link(self):
        matches = self.get_list_from_db()
        for match_index in range(len(matches)):
            match = matches[match_index]
            print(f"[{match_index} {match.match_time} {match.position_total}: "
                  f"{match.position1}-{match.position2} {match.country} {match.team1}: {match.team2}]"
                  f"(https://www.flashscorekz.com/match/{match.link}/#/standings/table/overall)")
            print()

    def main(self):
        matches = self.get_list_from_db()
        for match_index in range(len(matches)):
            match = matches[match_index]
            logger.warning(f"{str(match)=}")
            exit(-1)

    def insert(self, model: AnalysisDBModel):
        """
        """
        try:
            self.session.add(model)
            self.session.commit()
            logger.info(f'insert record: {model}')
        except Exception as exc:
            description_error = f"ERROR: {str(exc)} for {model}"
            logger.error(description_error)

    def merge(self):
        # from sqlalchemy import create_engine, MetaData, Table, select, and_, true
        # from sqlalchemy.orm import sessionmaker
        # from src.model.tables import DB_URL
        #
        # # Создание движка и сессии
        # engine = create_engine(DB_URL)
        # Session = sessionmaker(bind=engine)
        # session = Session()
        #
        # # Определение таблиц
        # metadata = MetaData()
        # current = Table('current', metadata, autoload_with=engine, schema='flashscore_new')
        # analysis = Table('analysis', metadata, autoload_with=engine, schema='flashscore_new')
        #
        # # Выполнение запроса
        # stmt = (
        #     select([current.c.id, current.c.link, analysis.c.is_match_leader_outsider, analysis.c.is_match_series])
        #     .select_from(current.outerjoin(analysis, current.c.link == analysis.c.link))
        #     .where(and_(
        #         current.c.match_date == '16.01.2024',
        #         current.c.status == true()
        #     ))
        #     .order_by(current.c.match_time)
        # )
        #
        # result = session.execute(stmt)
        # rows = result.fetchall()

        # result = self.session.query(CurrentDBModel, AnalysisDBModel) \
        #     .filter(CurrentDBModel.link == AnalysisDBModel.link) \
        #     .first()

        query_all_record = (
            self.session
            .query(CurrentDBModel, AnalysisDBModel)
            # .filter_by(match_date=HelperService.get_date_with_point_between_day(day=self.shift_day))
            # .filter_by(status=True)
            .outerjoin(AnalysisDBModel, CurrentDBModel.link == AnalysisDBModel.link)
            .filter(CurrentDBModel.match_date == HelperService.get_date_with_point_between_day(day=self.shift_day))
            .filter(CurrentDBModel.status == True)
            .order_by(CurrentDBModel.match_time)
        )
        result = query_all_record.all()
        logger.warning(f"{len(result)=}")

        results_dict = []
        for current, analysis in result:
            row_dict = {}
            for attr in dir(current):
                if not attr.startswith("_"):
                    row_dict[attr] = getattr(current, attr)
            for attr in dir(analysis):
                if not attr.startswith("_"):
                    row_dict[attr] = getattr(analysis, attr)
            row_dict.pop("metadata", None)
            row_dict.pop("registry", None)
            results_dict.append(row_dict)
        return results_dict


if __name__ == "__main__":
    # logger.info(f'Initializing test {os.path.basename(__file__)}')
    # parsing_service = AnalysisService()
    # parsing_service.main()
    # InfoAnalysisDBService().printer_link()

    logger.info(f'Initializing test {os.path.basename(__file__)}')
    parsing_service = InfoAnalysisDBService(0)
    parsing_service.merge()

    # parsing_service = InfoAnalysisDBService(-1)
    # analysis_model = AnalysisDBModel(
    #     id=1,
    #     link='vmVN9UCR',
    #     is_match_leader_outsider=True,
    #     is_match_series=False,
    #     is_hz=False,
    #     kf1=1.2,
    #     kf2=1.3,
    #     score1=8,
    #     score2=9,
    #     who_win=1,
    #     is_favorites=True,
    # )
    # parsing_service.insert(model=analysis_model)
