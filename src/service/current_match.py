from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.model.tables import CurrentDBModel
from src.service.helper import HelperService
from src.service.logger_handlers import get_logger
from src.service.main_page import dict_link

logger = get_logger(__name__)


class ValidationCurrentMatch:
    @staticmethod
    def is_validate(text: str, input_value, input_type):
        if type(input_value) == input_type:
            logger.debug(f"{str(text):<20}: {str(input_type):<12}-->{str(input_value):<20}".upper())
        else:
            logger.error(f"{text}: expect {input_type}-->{input_value} reality-->{type(input_value)}".upper())

    @staticmethod
    def get_integer_value(input_value):
        try:
            if type(input_value) == int:
                return input_value
            elif type(input_value) == str:
                output_value = int(input_value.split(".")[0])
                return output_value
        except ValueError:
            logger.error(f"ValueError no integer: {type(input_value)} {input_value}")
            return 0
        except Exception as exc:
            logger.error(str(exc))
            logger.error(f"no integer: {type(input_value)} {input_value}")
            return 0


class CurrentMatchService:
    def __init__(self, browser, data4parsing):
        self.driver = browser
        self.data4parsing = data4parsing

    def get_current_match_model(self, link):
        logger.debug("*" * 88)
        ValidationCurrentMatch.is_validate(text="#00 ссылка", input_value=link, input_type=str)
        # 01 вид спорта
        sport_name = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/span[1]/a").text
        ValidationCurrentMatch.is_validate(text="#01 вид спорта", input_value=sport_name, input_type=str)

        # 02 дата и время
        dt = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[1]/div").text
        date_game, time_game = dt.split(" ")
        ValidationCurrentMatch.is_validate(text="#02 дата", input_value=date_game, input_type=str)
        ValidationCurrentMatch.is_validate(text="#02 время", input_value=time_game, input_type=str)

        # 03 страна/турнир/тур
        tournament_header_country = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/span[3]").text
        list_country_tournament_tour = tournament_header_country.split(": ")
        country = str(HelperService.get_element_for_list(lst=list_country_tournament_tour, index=0, default_value=""))
        tournament_tour = str(HelperService.get_element_for_list(lst=list_country_tournament_tour, index=1,
                                                                 default_value=""))
        list_tournament_tour = tournament_tour.split(" - ")
        tournament = HelperService.get_element_for_list(lst=list_tournament_tour, index=1, default_value="")
        tour = HelperService.get_element_for_list(lst=list_tournament_tour, index=0, default_value="")
        ValidationCurrentMatch.is_validate(text="#03 страна", input_value=country, input_type=str)
        ValidationCurrentMatch.is_validate(text="#03 турнир", input_value=tournament_tour, input_type=str)
        ValidationCurrentMatch.is_validate(text="#03 тур", input_value=tour, input_type=str)

        # 04 Команды
        team1_name = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div[2]/a").text
        team2_name = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[4]/div[3]/div[1]/a").text
        ValidationCurrentMatch.is_validate(text="#04 команда№1", input_value=team1_name, input_type=str)
        ValidationCurrentMatch.is_validate(text="#04 команда№2", input_value=team2_name, input_type=str)

        # 05 счёт и статус
        try:
            status = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[3]/div/div[2]/span").text
            score1 = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[3]/div/div[1]/span[1]").text
            score2 = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[3]/div/div[1]/span[3]").text
            score = f"{score1}:{score2}"
        except NoSuchElementException:
            status = "TKP - ТОЛЬКО КОНЕЧНЫЙ РЕЗУЛЬТАТ."
            score1 = ""
            score2 = ""
            score = "Нет данных" + score1 + score2
        ValidationCurrentMatch.is_validate(text="#05 счёт", input_value=score, input_type=str)
        ValidationCurrentMatch.is_validate(text="#05 статус", input_value=status, input_type=str)

        # Блок, определяет из таблицы:
        pos1, pos2 = 0, 0
        number_games1, number_games2 = 0, 0
        points1, points2 = 0, 0
        series1, series2 = "", ""
        # 06 позиции
        # 07 количество игр
        # 08 очки
        # 09 серия
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".ui-table__row")

        count = 0
        for i in rows:
            count += 1
            row = i.text
            arr_row = row.split("\n")
            team = arr_row[1]
            dct_parameters = dict_link[self.data4parsing.sport_name]
            if team == team1_name:
                pos1 = int((arr_row[0].strip(".")))
                if pos1 != count:
                    raise ValueError("Таблиц несколько")
                number_games1 = ValidationCurrentMatch.get_integer_value(arr_row[dct_parameters["number_games"]])
                points1 = ValidationCurrentMatch.get_integer_value(arr_row[dct_parameters["points"]])
                series1 = "".join(arr_row[dct_parameters["series"]:]).replace("?", "")
            elif team == team2_name:
                pos2 = int(arr_row[0].strip("."))
                if pos2 != count:
                    raise ValueError("Таблиц несколько")
                number_games2 = ValidationCurrentMatch.get_integer_value(arr_row[dct_parameters["number_games"]])
                points2 = ValidationCurrentMatch.get_integer_value(arr_row[dct_parameters["points"]])
                series2 = "".join(arr_row[dct_parameters["series"]:]).replace("?", "")
        number_of_teams_in_the_league = len(rows)

        ValidationCurrentMatch.is_validate(text="#06 ПОЗИЦИЯ_1", input_value=pos1, input_type=int)
        ValidationCurrentMatch.is_validate(text="#06 ПОЗИЦИЯ_2", input_value=pos2, input_type=int)
        ValidationCurrentMatch.is_validate(text="#06 ПОЗИЦИЯ_всего", input_value=number_of_teams_in_the_league,
                                           input_type=int)

        ValidationCurrentMatch.is_validate(text="#07 КОЛИЧЕСТВО ИГР1", input_value=number_games1, input_type=int)
        ValidationCurrentMatch.is_validate(text="#07 КОЛИЧЕСТВО ИГР2", input_value=number_games2, input_type=int)

        ValidationCurrentMatch.is_validate(text="#08 ОЧКИ1", input_value=points1, input_type=int)
        ValidationCurrentMatch.is_validate(text="#08 ОЧКИ2", input_value=points2, input_type=int)

        ValidationCurrentMatch.is_validate(text="#09 СЕРИЯ", input_value=series1, input_type=str)
        ValidationCurrentMatch.is_validate(text="#09 СЕРИЯ", input_value=series2, input_type=str)
        logger.debug("*" * 88)

        current_db_model = CurrentDBModel(
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
            position1=pos1,
            position2=pos2,
            position_total=number_of_teams_in_the_league,
            num_games1=number_games1,
            num_games2=number_games2,
            points1=points1,
            points2=points2,
            series1=series1,
            series2=series2,
        )
        logger.debug("*" * 88)
        return current_db_model
