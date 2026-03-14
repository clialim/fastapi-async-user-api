from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import event
from database.orm import User
from sqlalchemy.orm import with_loader_criteria

DATABASE_URL = "sqlite+aiosqlite:///./db.sqlite"

engine = create_async_engine(DATABASE_URL, echo=True)


@event.listens_for(Session, "do_orm_execute")
def _add_filtering_criteria(execute_state):

    if execute_state.is_select:

        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                User,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True,
            )
        )


AsyncSessionFactory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        yield session
