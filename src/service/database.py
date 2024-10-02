from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.configs.settings import settings

DB_URL = f"{settings.DRIVER_NAME}://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@" \
         f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_engine(
    url=DB_URL,
    echo=False,  # log_to_console
    pool_size=15,  # number_connection
    max_overflow=30,  # over_connection
)

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
