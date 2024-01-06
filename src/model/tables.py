from sqlalchemy import Column, VARCHAR, INTEGER, Boolean, UniqueConstraint
from sqlalchemy.orm import declarative_base
from src.configs.settings import settings

DB_URL = f"{settings.DRIVER_NAME}://{settings.USERNAME_DB}:{settings.PASSWORD_DB}@" \
         f"{settings.HOST_DB}:{settings.PORT_DB}/{settings.DB_NAME}"
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
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
        return f"MainDBModel(id={self.id}, link={self.link}, " \
               f"status={self.status})"

    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":
    engine = create_engine(DB_URL)

    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(bind=engine)