from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from src.configs.settings import settings


class Base(DeclarativeBase):
    __abstract__ = True
    __table_args__ = {"schema": settings.SCHEME_NAME}

    @declared_attr
    def __tablename__(cls, *args, **kwargs) -> str:
        return f"{settings.TITLE}_app_{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(primary_key=True)


class DataBaseHelper:
    def __init__(self, url: str = settings.DATABASE_URL_ASYNCPG, echo: bool = settings.DB_ECHO):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,

        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session
            await session.close()

    async def scoped_session_dependency(self) -> AsyncSession:
        session = self.get_scoped_session()
        yield session
        await session.close()


db_helper = DataBaseHelper(url=settings.DATABASE_URL_ASYNCPG, echo=settings.DB_ECHO)


async def create_metadata():
    async with db_helper.engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    db_helper = DataBaseHelper(url=settings.DATABASE_URL_ASYNCPG, echo=settings.DB_ECHO)
