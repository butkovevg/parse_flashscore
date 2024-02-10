import json
import os
from datetime import datetime
from datetime import timedelta

from sqlalchemy import update

from src.model.tables import CurrentDBModel, AnalysisDBModel
from src.service.database import get_session
from src.service.enrichment_statistic import EnrichmentStatisticService
from src.service.helper import HelperService
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)


class AnalysisService:
    def __init__(self, shift_day: int = 0):
        self.session = next(get_session())
        self.shift_day = shift_day

    def is_match_leader_and_outsider(self, record: CurrentDBModel):
        if record.position_total > 10 and record.num_games1 > 3 and record.num_games2 > 3:
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
        self.analysis_model.is_match_series = True
        logger.warning(f"update {record.team1}:{record.team2} {record.series1} {record.series2}")

    def log_match_leader_and_outsider(self, record):
        self.analysis_model.is_match_leader_outsider = True
        logger.warning(
            f"update {record.team1}:{record.team2} {record.position1}:{record.position2}==={record.position_total}")

    def main(self):
        unprocessed_records = self.get_list_from_db()
        counter = 0
        length_unprocessed_records = len(unprocessed_records)
        for index in range(length_unprocessed_records):
            current_model = unprocessed_records[index]
            self.analysis_model = AnalysisDBModel(
                link=current_model.link,
                is_match_leader_outsider=False,
                is_match_series=False,
                is_hz=False,
                kf1=-1,
                kf2=-1,
                score1=-1,
                score2=-1,
                who_win=0,
                is_favorites=False,
            )
            self.is_match_leader_and_outsider(current_model)
            self.is_match_with_series(current_model)

            if self.analysis_model.is_match_leader_outsider or self.analysis_model.is_match_series:
                enrichment_statistic_service = EnrichmentStatisticService()
                coefficient_tuple = enrichment_statistic_service.open_page_with_coefficient(
                    link=self.analysis_model.link)
                self.analysis_model.kf1 = coefficient_tuple[0]
                self.analysis_model.kf2 = coefficient_tuple[1]
                self.insert(analysis_model=self.analysis_model)
                counter += 1
            logger.info(f"{index}/{length_unprocessed_records}. in analyze={counter}")

    def insert(self, analysis_model: AnalysisDBModel):
        """
        """
        try:
            self.session.add(analysis_model)
            self.session.commit()
            logger.info(f'insert record: {analysis_model}')
        except Exception as exc:
            description_error = f"ERROR: {str(exc)} for {analysis_model}"
            logger.error(description_error)
            self.session.rollback()

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

            return query_all_record.all()
        except Exception as exc:
            logger.error(f"Подробности ошибки {str(exc)}")
        finally:
            self.session.close()


class InfoAnalysisDBService:
    def __init__(self, shift_day: int = 0):
        self.session = next(get_session())
        self.shift_day = shift_day
        self.query = (self.session
                      .query(AnalysisDBModel, CurrentDBModel)
                      .outerjoin(CurrentDBModel, AnalysisDBModel.link == CurrentDBModel.link)
                      .filter(
            CurrentDBModel.match_date == HelperService.get_date_with_point_between_day(day=self.shift_day)))

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
            record = matches[match_index]
            logger.warning(f"{str(record)=}")

    def get_favorites(self):
        current_time = datetime.now()
        new_time = current_time - timedelta(minutes=90)

        query_all_record = (
            self.query
            .filter(AnalysisDBModel.is_favorites == True)
            .order_by(CurrentDBModel.match_time)
        )
        result = query_all_record.all()
        logger.warning(f"{len(result)=}")

        return self.get_list_dct_models_analysis_and_current(result)

    def merge(self):
        current_time = datetime.now()
        new_time = current_time - timedelta(minutes=90)
        time_filter = new_time.strftime('%H:%M')
        query_all_record = (
            self.query
            .order_by(CurrentDBModel.match_time)
        )
        # if self.shift_day == 0:
        #     query_all_record = query_all_record.filter(CurrentDBModel.match_time > time_filter)
        result = query_all_record.all()
        logger.warning(f"{len(result)=}")
        return self.get_list_dct_models_analysis_and_current(result)

    def get_match_today(self):
        current_time = datetime.now()
        new_time = current_time - timedelta(minutes=90)
        time_filter = new_time.strftime('%H:%M')
        query_all_record = self.query.filter(CurrentDBModel.match_time > time_filter)
        query_all_record = query_all_record.order_by(CurrentDBModel.match_time)
        result = query_all_record.all()
        logger.warning(f"{len(result)=}")
        return self.get_list_dct_models_analysis_and_current(result)

    def get_list_dct_models_analysis_and_current(self, result):
        output_list = []
        for analysis, current in result:
            row_dict = {}
            for attr in dir(current):
                if not attr.startswith("_"):
                    row_dict[attr] = getattr(current, attr)
            for attr in dir(analysis):
                if not attr.startswith("_"):
                    if attr == "id":
                        row_dict["analysis_id"] = getattr(analysis, attr)
                    else:
                        row_dict[attr] = getattr(analysis, attr)

            row_dict.pop("metadata", None)
            row_dict.pop("registry", None)
            output_list.append(row_dict)
        return output_list

    def update_favorites(self, analysis_id: int):
        query_link = (
            self.session
            .query(AnalysisDBModel)
            .filter(AnalysisDBModel.id == analysis_id)
        )
        analysis_db_model = query_link.all()[0]
        print(analysis_db_model)
        logger.warning(f"{analysis_db_model=}")

        stmt = (
            update(AnalysisDBModel).
            where(AnalysisDBModel.id == analysis_id).
            values(is_favorites=not analysis_db_model.is_favorites)
        )
        self.session.execute(stmt)
        self.session.commit()
        logger.warning(f"ok")


if __name__ == "__main__":
    # 1: "Запись в БД после анализа",
    # 2: "",
    choice = 1
    logger.info(f'Initializing test {os.path.basename(__file__)}')

    if choice == 1:
        parsing_service = AnalysisService(shift_day=2)
        parsing_service.main()
    elif choice == 2:
        InfoAnalysisDBService().printer_link()
    elif choice == 3:
        parsing_service = InfoAnalysisDBService(0)
        list_analysis_dct = parsing_service.merge()

        js = json.dumps(list_analysis_dct[0], indent=4, ensure_ascii=False)
        print(js)
    elif choice == 4:
        parsing_service = InfoAnalysisDBService(0)
        parsing_service.update_favorities(link="l8camAxG")

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
