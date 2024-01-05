import os
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.service.browser import BrowserService
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)

dict_link = {
    "football": "https://www.flashscorekz.com/?rd=flashscore.ru"
}


class MainPageService:
    def get_list_link_with_main_page(self, sport: str, shift_day: int = 0):
        try:
            self.link = dict_link.get(sport)
            browser = BrowserService.get_webdriver()
            browser.get(self.link)
            time.sleep(3)
            # Кликаем на следующий день, если day > 0
            while shift_day > 0:
                shift_day -= 1
                # код клика
            page_source = browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            ids = [tag['id'] for tag in soup.select('div[id]')]
            ids_filtered = filter(lambda x: x.startswith("g_1_"), ids)
            ids_filtered = [link.replace("g_1_", "") for link in ids_filtered]
            logger.info(f"Получено ссылок {len(ids_filtered)}")
            browser.quit()
            return ids_filtered
        except Exception as exc:
            logger.error(str(exc))
            return []



    def get_current_match(self, link):
        link = f"https://www.flashscorekz.com/match/{link}/#/standings/table/overall"
        try:
            browser = BrowserService.get_webdriver()
            browser.get(link)
            logger.debug(f"browser.get({link})")
            time.sleep(2)

            # 00 Блок о матче
            logger.debug("#00 Блок о матче")

            # 01 вид спорта
            sport = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/span[1]/a").text
            logger.debug(f"#01 вид спорта {sport}".upper())

            # 02 дата и время
            dt = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[1]/div").text
            date_game, time_game = dt.split(" ")
            logger.debug(f"#02 дата и время: {date_game} {time_game}".upper())

            # 03 страна/турнир
            tournament_header_country = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/span[3]").text
            country, tournament_tour = tournament_header_country.split(": ")
            tournament, tour = tournament_tour.split(" - ")
            logger.debug(f"#03 страна/турнир/тур: {country} {tournament_tour} {tour}".upper())

            # 04 Команды
            team1_name = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[2]/div[3]/div[2]/a").text
            team2_name = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[4]/div[3]/div[1]/a").text
            logger.debug(f"#04 Команды: {team1_name} - {team2_name}".upper())

            # 05 счёт и статус
            status = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[3]/div/div[2]/span").text
            try:
                score1 = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[3]/div/div[1]/span[1]").text
                score2 = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[3]/div/div[1]/span[3]").text
                score = f"{score1}:{score2}"
            except NoSuchElementException:
                score1 = ""
                score2 = ""
                score = "Нет данных" + score1 + score2
            logger.debug(f"#05 счёт и статус {score}, {status}".upper())

            # Блок, определяет из таблицы:
            # 06 позиции
            # 07 количество игр
            # 08 разница мячей
            # 09 очки
            # 10 серия"
            rows = browser.find_elements(By.CSS_SELECTOR, ".ui-table__row")
            for i in rows:
                row = i.text
                arr_row = row.split("\n")
                team = arr_row[1]

                if team == team1_name:
                    pos1 = arr_row[0].strip(".")
                    number_games1 = arr_row[2]
                    delta_ball1 = arr_row[6]
                    points1 = arr_row[8]
                    series1 = "".join(arr_row[9:]).replace("?", "")
                elif team == team2_name:
                    pos2 = arr_row[0].strip(".")
                    number_games2 = arr_row[2]
                    delta_ball2 = arr_row[6]
                    points2 = arr_row[8]
                    series2 = "".join(arr_row[9:]).replace("?", "")
            number_of_teams_in_the_league = len(rows)
            logger.debug(f"#06 позиция {pos1}/{number_of_teams_in_the_league} {pos2}/{number_of_teams_in_the_league}")
            logger.debug(f"#07 количество игр: {number_games1}, {number_games2}")
            logger.debug(f"#08 разница мячей: {delta_ball1}, {delta_ball2}")
            logger.debug(f"#09 очки: {points1}, {points2}")
            logger.debug(f"#10 серия: {series1}, {series2}")
        except Exception as exc:
            logger.error(str(exc))
        finally:
            browser.quit()


if __name__ == "__main__":
    logger.info(f'Initializing test {os.path.basename(__file__)}')
    parsing_service = MainPageService()
    # parsing_service.get_current_match(link="CAKtamhe")
    parsing_service.get_list_link_with_main_page(sport="football")
