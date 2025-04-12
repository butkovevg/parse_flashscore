import json
import os
from datetime import datetime
from datetime import timedelta
from typing import Optional

from sqlalchemy import update

from src.model.tables import CurrentDBModel, AnalysisDBModel
from src.service.database import get_session
from src.service.helper import HelperService
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)


class AnalysisService:
    def __init__(self, shift_day: int = 0):
        self.analysis_model: Optional[AnalysisDBModel] = None
        self.session = next(get_session())
        self.shift_day = shift_day

    def is_selection_by_position_table(self, record: CurrentDBModel):
        if record.position_total > 10 and record.num_games1 > 3 and record.num_games2 > 3:
            if record.position1 < 3 and record.position_total - record.position2 < 3:
                self.analysis_model.by_position_table = 1
                logger.debug(f"is_selection_by_position_table for {record.link}: {record.position1} {record.position2}")
            elif record.position2 < 3 and record.position_total - record.position1 < 3:
                if self.analysis_model.by_position_table == 0:
                    self.analysis_model.by_position_table = 2
                    logger.debug(
                        f"is_selection_by_position_table for {record.link}: {record.position1} {record.position2}")
                else:
                    logger.error(f"Error for {record.link}: {record.position1} {record.position2}")

    def is_selection_match_with_series(self, record: CurrentDBModel):
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

        if dct_series1.get("B", 0) > 4 and dct_series2.get("П", 0) > 4:
            self.analysis_model.by_series = 1
            logger.debug(
                f"is_selection_match_with_series for {record.link}: {dct_series1.get('B', 0)} {dct_series2.get('П', 0)}")

        elif dct_series2.get("B", 0) > 4 and dct_series1.get("П", 0) > 4:
            if self.analysis_model.by_series == 0:
                self.analysis_model.by_series = 2
                logger.debug(
                    f"is_selection_match_with_series for {record.link}: {dct_series1.get('П', 0)} {dct_series2.get('В', 0)}")
            else:
                logger.error(f"Error for {record.link}: {record.position1} {record.position2}")

    def is_selection_by_coefficient(self, record: CurrentDBModel):
        try:
            msg = f"{record.sport_name} {record.team1}: {record.team2} {record.kf1}: {record.kf2}"
            max_kf = 1.25
            if 1.01 < float(record.kf1) < max_kf:
                self.analysis_model.by_coefficient = 1
                logger.info(msg)
            if 1.01 < float(record.kf2) < max_kf:
                if self.analysis_model.by_coefficient == 0:
                    self.analysis_model.by_coefficient = 2
                else:
                    logger.error(f"Check low kf and {msg}")
                logger.info(msg)
        except Exception as exc:
            logger.error(exc)
    def is_need_skip(self, current_model: CurrentDBModel):
        if current_model.sport_name == "ТЕННИС":
            if "ITF" in current_model.country:
                return True
        return False

    def main(self):
        unprocessed_records = self.get_list_from_db()
        counter = 0
        length_unprocessed_records = len(unprocessed_records)
        for index in range(length_unprocessed_records):

            current_model = unprocessed_records[index]
            self.analysis_model = AnalysisDBModel(
                link=current_model.link,
                by_coefficient=0,
                by_series=0,
                by_position_table=0,
                who_must_win=0,
            )
            self.is_selection_by_coefficient(current_model)
            self.is_selection_by_position_table(current_model)
            self.is_selection_match_with_series(current_model)

            if self.is_save():
                if self.is_need_skip(current_model):
                    logger.debug(f"is_need_skip: {current_model.link}, {current_model.country}")
                else:
                    self.insert(analysis_model=self.analysis_model)
                    counter += 1
            logger.info(f"{index}/{length_unprocessed_records}. in analyze={counter}")


    def is_save(self):
        set_who_must_win = {self.analysis_model.by_coefficient, self.analysis_model.by_series, self.analysis_model.by_position_table}
        set_who_must_win.discard(0)
        if len(set_who_must_win) == 0:
            return False
        elif len(set_who_must_win) == 1:
            self.analysis_model.who_must_win = set_who_must_win.pop()
        else:
            self.analysis_model.who_must_win = 3
            self.analysis_model.comment = "ERR different "
            logger.error(f"{self.analysis_model.link}: different: {self.analysis_model.by_coefficient}/{self.analysis_model.by_series}/{self.analysis_model.by_position_table}")
        return True

    def insert(self, analysis_model: AnalysisDBModel):
        """
        """
        try:
            self.session.add(analysis_model)
            self.session.commit()
            logger.debug(f'insert record: {analysis_model}')
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
            match_date = HelperService.get_date_with_point_between_day(self.shift_day)
            logger.debug(f"get_list_from_db {match_date=}")
            # запрос для всех записей для вида спорта по дате
            query_all_record = (
                self.session
                .query(CurrentDBModel)
                .filter_by(match_date=match_date)
                # .filter(CurrentDBModel.position1 != 0)
            )

            # Необработанных записей для вида спорта по дате
            query_unprocessed_record = query_all_record.filter_by(status=None)

            len_all_record = query_all_record.count()
            len_unprocessed_record = query_unprocessed_record.count()

            logger.debug(f"{len_unprocessed_record=}/{len_all_record=}")

            # unprocessed_records = query_unprocessed_record.all()

            return query_all_record.all()
        except Exception as exc:
            logger.error(f"Подробности ошибки {str(exc)}")
        finally:
            self.session.close()


class InfoAnalysisDBService:
    def __init__(self, shift_day: int = 0):

        self.shift_day = shift_day
        self.session = next(get_session())
        self.current_time = datetime.now()
        self.query = (
            self.session
            .query(AnalysisDBModel, CurrentDBModel)
            .outerjoin(CurrentDBModel, AnalysisDBModel.link == CurrentDBModel.link)
            .filter(CurrentDBModel.match_date == HelperService.get_date_with_point_between_day(day=self.shift_day))
        )

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

        new_time = self.current_time - timedelta(minutes=90)

        query_all_record = (
            self.query
            .filter(AnalysisDBModel.is_favorites == True)
            .order_by(CurrentDBModel.match_time)
        )
        result = query_all_record.all()
        logger.warning(f"{len(result)=}")

        return self.get_list_dct_models_analysis_and_current(result)

    def merge(self):
        # new_time = self.current_time - timedelta(minutes=90)
        # time_filter = new_time.strftime('%H:%M')
        query_all_record = (
            self.query
            .order_by(CurrentDBModel.match_time)
        )
        query_all_record = query_all_record.filter(AnalysisDBModel.comment.is_(None))
        result = query_all_record.all()
        logger.warning(f"{len(result)=}")
        return self.get_list_dct_models_analysis_and_current(result)

    def get_match_today(self):
        new_time = self.current_time - timedelta(minutes=90)
        time_filter = new_time.strftime('%H:%M')
        query_all_record = self.query.filter(CurrentDBModel.match_time > time_filter)
        # query_all_record = self.query.filter(AnalysisDBModel.comment.is_(None))
        logger.warning(f"{query_all_record=}")
        query_all_record = query_all_record.order_by(CurrentDBModel.match_time)
        result = query_all_record.all()
        logger.warning(f"{len(result)=}")
        for i in result:
            logger.info(i)
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

    choice = 1
    logger.info(f'Initializing test {os.path.basename(__file__)}')
    if choice == 1:
        parsing_service = AnalysisService(shift_day=0)
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
    elif choice == 5:
        # ANALYSIS
        day = 1
        logger.debug(f"AnalysisService {day=}")
        parsing_service = AnalysisService(shift_day=day)
        parsing_service.get_tennis_main()
        logger.debug(f"FINISH {day=}")
