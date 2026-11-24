import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DB_PATH = os.path.join(_PROJECT_ROOT, 'data', 'dndpy.db')


class Base(DeclarativeBase):
    pass


def get_engine(db_path: str = _DB_PATH):
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def init_db(db_path: str = None):
    path = db_path or _DB_PATH
    engine = get_engine(path)
    from dndpy.db import models  # noqa: F401 — registers all ORM models
    Base.metadata.create_all(engine)
    return engine


def get_session(engine=None):
    if engine is None:
        engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
