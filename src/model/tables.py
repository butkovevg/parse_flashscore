from sqlalchemy import VARCHAR, INTEGER, Boolean

from src.configs.settings import settings

DB_URL = f"{settings.DRIVER_NAME}://{settings.USERNAME_DB}:{settings.PASSWORD_DB}@" \
         f"{settings.HOST_DB}:{settings.PORT_DB}/{settings.DB_NAME}"
from sqlalchemy import create_engine, Column, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
from src.configs.settings import settings

# Делаем модель для работы с данными из БД
Base = declarative_base()


class MainDBModel(Base):
    __table_args__ = (

        UniqueConstraint('id', 'link'),
        {"schema": settings.SCHEME_NAME},
    )
    __tablename__ = settings.TABLE_NAME_MAIN

    id = Column(INTEGER, primary_key=True, nullable=False)
    link = Column(VARCHAR, unique=True, nullable=False)
    sport_name = Column(VARCHAR, nullable=False)
    match_date = Column(VARCHAR, nullable=False)
    status = Column(Boolean, default=None)

    def __str__(self):
        return f"ID: {self.id}, Link: {self.link}, Sport Name: {self.sport_name}, Match Date: {self.match_date}, Status: {self.status}"
    # def __str__(self):
    #     return f"{self.id=}, {self.link=}, {self.match_date=}, {self.sport_name=}, {self.status=}"
    # # def __str__(self):
    # #     return f"MainDBModel"


class CurrentDBModel(Base):
    __table_args__ = (

        UniqueConstraint('id', 'link'),
        {"schema": settings.SCHEME_NAME},
    )
    __tablename__ = settings.TABLE_NAME_CURRENT

    id = Column(INTEGER, primary_key=True, nullable=False)
    link = Column(VARCHAR, unique=True, nullable=False)
    # 01 ВИД СПОРТА ВОЛЕЙБОЛ
    sport_name = Column(VARCHAR, nullable=False)
    # 02 ДАТА И ВРЕМЯ:
    match_date = Column(VARCHAR, nullable=False)
    match_time = Column(VARCHAR, nullable=False)
    # 03 СТРАНА/ТУРНИР/ТУР:
    country = Column(VARCHAR, nullable=False)
    tournament = Column(VARCHAR, nullable=False)
    tour = Column(VARCHAR, nullable=False)
    # 04 КОМАНДЫ:
    team1 = Column(VARCHAR, nullable=False)
    team2 = Column(VARCHAR, nullable=False)
    # 05 СЧЁТ И СТАТУС:
    score1 = Column(VARCHAR, nullable=False)
    score2 = Column(VARCHAR, nullable=False)
    match_status = Column(VARCHAR, nullable=False)
    # 06 ПОЗИЦИЯ
    position1 = Column(INTEGER, nullable=False)
    position2 = Column(INTEGER, nullable=False)
    position_total = Column(INTEGER, nullable=False)

    # 07 КОЛИЧЕСТВО ИГР:
    num_games1 = Column(INTEGER, nullable=False)
    num_games2 = Column(INTEGER, nullable=False)
    # 08 ОЧКИ:
    points1 = Column(INTEGER, nullable=False)
    points2 = Column(INTEGER, nullable=False)
    # 09 СЕРИЯ
    series1 = Column(VARCHAR, nullable=False)
    series2 = Column(VARCHAR, nullable=False)
    # 10 ПРОЧЕЕ:
    status = Column(Boolean, default=None)

    def __str__(self):
        return f"ID: {self.id}, Link: {self.link}, Sport Name: {self.sport_name}, Match Date: {self.match_date}, Match Time: {self.match_time}, Country: {self.country}, Tournament: {self.tournament}, Tour: {self.tour}, Team1: {self.team1}, Team2: {self.team2}, Score1: {self.score1}, Score2: {self.score2}, Match Status: {self.match_status}, Position1: {self.position1}, Position2: {self.position2}, Position Total: {self.position_total}, Num Games1: {self.num_games1}, Num Games2: {self.num_games2}, Points1: {self.points1}, Points2: {self.points2}, Series1: {self.series1}, Series2: {self.series2}, Status: {self.status}"


if __name__ == "__main__":
    engine = create_engine(DB_URL)

    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(bind=engine)
