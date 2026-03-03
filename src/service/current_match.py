import os

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.model.tables import CurrentDBModel
from src.service.helper import HelperService
from src.service.logger_handlers import logger
from src.service.main_page import dict_link


class ValidationCurrentMatch:
    @staticmethod
    def is_validate(text: str, input_value, input_type):
        if isinstance(input_value, input_type):
            logger.debug(f"{str(text):<20}: {str(input_type):<12}-->{str(input_value):<20}".upper())
        else:
            logger.error(f"{text}: expect {input_type}-->{input_value} reality-->{type(input_value)}".upper())

    @staticmethod
    def get_integer_value(input_value):
        try:
            if isinstance(input_value, int):
                return input_value
            elif isinstance(input_value, str):
                output_value = int(input_value.split(".")[0])
                return output_value
        except ValueError:
            logger.debug(f"ValueError no integer: {type(input_value)} {input_value}")
            return 0
        except Exception as exc:
            logger.error(str(exc))
            logger.error(f"no integer: {type(input_value)} {input_value}")
            return 0


class CurrentMatchService:
    def __init__(self, browser, data4parsing):
        self.driver = browser
        self.data4parsing = data4parsing

    # pylint: disable=too-many-statements
    def get_current_match_model(self, link):
        """Публичный метод-оркестратор: собирает модель матча из данных на странице"""
        ValidationCurrentMatch.is_validate(text="#00 ссылка", input_value=link, input_type=str)

        sport_name = self._extract_sport_name()
        date_game, time_game = self._extract_date_time()
        country, tournament, tour = self._extract_tournament_info()
        team1_name, team2_name = self._extract_teams_name()
        status, score1, score2 = self._extract_status_scores()
        table_data = self._extract_table_data(team1_name, team2_name)

        self._validate_extracted_data(sport_name, date_game, time_game, table_data)

        kf1, kf2 = self._extract_coefficients()

        return self._build_model(
            link=link,
            sport_name=sport_name,
            date_game=date_game,
            time_game=time_game,
            country=country,
            tournament=tournament,
            tour=tour,
            team1_name=team1_name,
            team2_name=team2_name,
            score1=score1,
            score2=score2,
            status=status,
            table_data=table_data,
            kf1=kf1,
            kf2=kf2,
        )

    def _extract_sport_name(self) -> str:
        """01. Извлечение вида спорта"""
        sport_name = self.driver.find_element(
            By.XPATH,
            "/html/body/div[4]/div[1]/div/div[1]/main/div[5]/div[1]/div[1]/nav/ol/li[1]/a/span"
        ).text
        ValidationCurrentMatch.is_validate(text="#01 вид спорта", input_value=sport_name, input_type=str)
        return sport_name

    def _extract_date_time(self) -> tuple[str, str]:
        """02. Извлечение даты и времени"""
        dt = self.driver.find_element(
            By.XPATH,
            "/html/body/div[4]/div[1]/div/div[1]/main/div[5]/div[1]/div[2]/div[1]/div[1]/div"
        ).text
        date_game, time_game = dt.split(" ")
        ValidationCurrentMatch.is_validate(text="#02 дата", input_value=date_game, input_type=str)
        ValidationCurrentMatch.is_validate(text="#02 время", input_value=time_game, input_type=str)
        return date_game, time_game

    def _extract_tournament_info(self) -> tuple[str, str, str]:
        """03. Извлечение страны/турнира/тура"""
        return self.get_country_tournament_tour()

    def _extract_teams_name(self) -> tuple[str, str]:
        """04. Извлечение названий команд"""
        return self.get_teams_name()

    def _extract_status_scores(self) -> tuple[str, str, str]:
        """05. Извлечение статуса и счёта"""
        return self.get_status_scores()

    def _extract_table_data(self, team1_name: str, team2_name: str) -> dict:
        """06-09. Извлечение данных из таблицы (позиции, игры, очки, серия)"""
        pos1, pos2 = 0, 0
        number_games1, number_games2 = 0, 0
        points1, points2 = 0, 0
        series1, series2 = "", ""

        rows = self.driver.find_elements(By.CSS_SELECTOR, ".ui-table__row")
        dct_parameters = dict_link[self.data4parsing.english_sport_name]

        for count, row_element in enumerate(rows, start=1):
            row_text = row_element.text
            arr_row = row_text.split("\n")

            MIN_ROW_LENGTH = 2  # Минимальная длина строки таблицы для валидации
            if len(arr_row) < MIN_ROW_LENGTH:
                continue

            team = arr_row[1]

            if team == team1_name:
                pos1 = int(arr_row[0].strip("."))
                if pos1 != count:
                    raise ValueError("Tables > 1")
                number_games1 = ValidationCurrentMatch.get_integer_value(arr_row[dct_parameters["number_games"]])
                points1 = ValidationCurrentMatch.get_integer_value(arr_row[dct_parameters["points"]])
                series1 = "".join(arr_row[dct_parameters["series"]:]).replace("?", "")

            elif team == team2_name:
                pos2 = int(arr_row[0].strip("."))
                if pos2 != count:
                    raise ValueError("Tables > 1")
                number_games2 = ValidationCurrentMatch.get_integer_value(arr_row[dct_parameters["number_games"]])
                points2 = ValidationCurrentMatch.get_integer_value(arr_row[dct_parameters["points"]])
                series2 = "".join(arr_row[dct_parameters["series"]:]).replace("?", "")

        return {
            "pos1": pos1,
            "pos2": pos2,
            "position_total": len(rows),
            "number_games1": number_games1,
            "number_games2": number_games2,
            "points1": points1,
            "points2": points2,
            "series1": series1,
            "series2": series2,
        }

    def _validate_extracted_data(self, sport_name: str, date_game: str, time_game: str, table_data: dict):
        """Валидация всех извлечённых данных"""
        ValidationCurrentMatch.is_validate(text="#06 ПОЗИЦИЯ_1", input_value=table_data["pos1"], input_type=int)
        ValidationCurrentMatch.is_validate(text="#06 ПОЗИЦИЯ_2", input_value=table_data["pos2"], input_type=int)
        ValidationCurrentMatch.is_validate(
            text="#06 ПОЗИЦИЯ_всего",
            input_value=table_data["position_total"],
            input_type=int
        )
        ValidationCurrentMatch.is_validate(
            text="#07 КОЛИЧЕСТВО ИГР1",
            input_value=table_data["number_games1"],
            input_type=int
        )
        ValidationCurrentMatch.is_validate(
            text="#07 КОЛИЧЕСТВО ИГР2",
            input_value=table_data["number_games2"],
            input_type=int
        )
        ValidationCurrentMatch.is_validate(text="#08 ОЧКИ1", input_value=table_data["points1"], input_type=int)
        ValidationCurrentMatch.is_validate(text="#08 ОЧКИ2", input_value=table_data["points2"], input_type=int)
        ValidationCurrentMatch.is_validate(text="#09 СЕРИЯ", input_value=table_data["series1"], input_type=str)
        ValidationCurrentMatch.is_validate(text="#09 СЕРИЯ", input_value=table_data["series2"], input_type=str)
        logger.debug("*" * 88)

    def _extract_coefficients(self) -> tuple[int, int]:
        """Извлечение коэффициентов (если включено)"""
        if self.data4parsing.should_fetch_odds:
            return self.get_coefficient()
        return 0, 0

    def _build_model(  # noqa: PLR0913
            self,
            link: str,
            sport_name: str,
            date_game: str,
            time_game: str,
            country: str,
            tournament: str,
            tour: str,
            team1_name: str,
            team2_name: str,
            score1: str,
            score2: str,
            status: str,
            table_data: dict,
            kf1: int,
            kf2: int,
    ) -> CurrentDBModel:  # pylint: disable=too-many-arguments
        """Создание и возврат модели CurrentDBModel"""
        return CurrentDBModel(
            link=link,
            sport_name=sport_name,
            match_date=date_game,
            match_time=time_game,
            country=country,
            tournament=tournament,
            tour=tour,
            team1=team1_name,
            team2=team2_name,
            score1=score1,
            score2=score2,
            match_status=status,
            position1=table_data["pos1"],
            position2=table_data["pos2"],
            position_total=table_data["position_total"],
            num_games1=table_data["number_games1"],
            num_games2=table_data["number_games2"],
            points1=table_data["points1"],
            points2=table_data["points2"],
            series1=table_data["series1"],
            series2=table_data["series2"],
            kf1=kf1,
            kf2=kf2,
        )

    def get_country_tournament_tour(self):
        country = self.driver.find_element(By.XPATH,
                                           "/html/body/div[4]/div[1]/div/div[1]/main/div[5]/div[1]/div[1]/nav/ol/li[2]/a/span").text
        ValidationCurrentMatch.is_validate(text="#03 страна", input_value=country, input_type=str)
        tournament_header = self.driver.find_element(By.XPATH,
                                                     "/html/body/div[4]/div[1]/div/div[1]/main/div[5]/div[1]/div[1]/nav/ol/li[3]/a/span").text
        list_tournament_tour = tournament_header.split(" - ")
        tournament = HelperService.get_element_for_list(lst=list_tournament_tour, index=0, default_value="")
        tour = HelperService.get_element_for_list(lst=list_tournament_tour, index=1, default_value="")
        ValidationCurrentMatch.is_validate(text="#03 турнир", input_value=tournament, input_type=str)
        ValidationCurrentMatch.is_validate(text="#03 тур", input_value=tour, input_type=str)

        return country, tournament, tour

    def get_teams_name(self):
        team1_name = self.driver.find_element(By.XPATH,
                                              "/html/body/div[4]/div[1]/div/div[1]/main/div[5]/div[1]/div[2]/div[1]/div[2]/div[3]/div[2]/a").text
        team2_name = self.driver.find_element(By.XPATH,
                                              "/html/body/div[4]/div[1]/div/div[1]/main/div[5]/div[1]/div[2]/div[1]/div[4]/div[3]/div[1]/a").text
        ValidationCurrentMatch.is_validate(text="#04 команда№1", input_value=team1_name, input_type=str)
        ValidationCurrentMatch.is_validate(text="#04 команда№2", input_value=team2_name, input_type=str)
        return team1_name, team2_name

    def get_status_scores(self):
        try:
            status = self.driver.find_element(By.CSS_SELECTOR, "div.detailScore__status span.fixedHeaderDuel__detailStatus").text
            score1 = self.driver.find_element(By.XPATH,
                                              "/html/body/div[4]/div[1]/div/div[1]/main/div[5]/div[1]/div[2]/div[1]/div[3]/div/div[1]/span[1]").text
            score2 = self.driver.find_element(By.XPATH,
                                              "/html/body/div[4]/div[1]/div/div[1]/main/div[5]/div[1]/div[2]/div[1]/div[3]/div/div[1]/span[3]").text
            score = f"{score1}:{score2}"
        except NoSuchElementException:
            status = "TKP - ТОЛЬКО КОНЕЧНЫЙ РЕЗУЛЬТАТ."
            score1 = "-"
            score2 = "-"
            score = "Нет данных" + score1 + score2
        ValidationCurrentMatch.is_validate(text="#05 счёт", input_value=score, input_type=str)
        ValidationCurrentMatch.is_validate(text="#05 статус", input_value=status, input_type=str)
        return status, score1, score2

    def get_coefficient(self):

        # new_fragment = "#/match-summary/match-summary"
        # self.driver.execute_script(f"window.location.hash = '{new_fragment}'")
        # time.sleep(5)

        full_url = self.driver.current_url
        # logger.debug(f"Switched to section: {full_url}")

        try:
            try:
                # Найти все элементы с коэффициентами
                odds_elements = self.driver.find_elements(By.XPATH, '//span[@data-testid="wcl-oddsValue"]')

                # Отфильтровать только те, где текст — число (а не "-")
                valid_odds = []
                for el in odds_elements:
                    text = el.text.strip()
                    if text and text != '-' and text.replace('.', '', 1).isdigit():
                        valid_odds.append(text)

                logger.debug(f"Найденные коэффициенты({len(valid_odds)}):  {valid_odds}")
            except TypeError:
                logger.error("ERR TMP1")
            except Exception as e:
                logger.error(f"ERR TMP3 {str(e)}")

            number_kf_with_draw = [3, 6, 9, 12]  # Если в матче м.б. Ничья, то бывает три коэффициента
            number_kf_without_draw = [2, 4, 6, 8, 10]  # Если в матче м.б. Ничья, то бывает три коэффициента
            if len(valid_odds) in number_kf_with_draw:
                kf1 = float(valid_odds[0])
                kf2 = float(valid_odds[2])
            elif len(valid_odds) in number_kf_without_draw:
                kf1 = float(valid_odds[0])
                kf2 = float(valid_odds[1])
            else:
                kf1 = 0
                kf2 = 0
                logger.debug(f"WebElement not found  for KF {full_url=}")

            if kf1 != 0 and kf2 != 0:
                logger.debug(f"KF {kf1} {kf2}")  # 2.00
            return kf1, kf2
        except ValueError:
            logger.warning(f"ValueError for KF {full_url=}")
            return 0, 0
        except NoSuchElementException:
            logger.warning(f"NoSuchElementException for KF {full_url=}")
            return 0, 0
        except Exception as exc:
            logger.error(f"ERROR {full_url=}")
            logger.error(str(exc))
            logger.error(exc)
            return 0, 0


if __name__ == "__main__":
    logger.info(f'Initializing test {os.path.basename(__file__)}')
