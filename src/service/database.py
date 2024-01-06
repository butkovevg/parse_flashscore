from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.configs.settings import settings

DB_URL = f"{settings.DRIVER_NAME}://{settings.USERNAME_DB}:{settings.PASSWORD_DB}@" \
         f"{settings.HOST_DB}:{settings.PORT_DB}/{settings.DB_NAME}"
engine = create_engine(DB_URL)

Session = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
)


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()
