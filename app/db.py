from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase
from .config import DATABASE_URL
from sqlalchemy import Integer, Identity
from sqlalchemy.orm import Mapped, mapped_column

id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)


engine = create_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

# Option A (2.0 modern)
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


def init_db():
    from .models import User  # noqa
    Base.metadata.create_all(bind=engine)


