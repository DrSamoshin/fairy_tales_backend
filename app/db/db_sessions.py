import logging
from uuid import UUID
from functools import wraps
from fastapi import HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from cachetools import TTLCache
from threading import Lock

from app.core.configs import settings


USERS_DB_ENGINES = TTLCache(maxsize=10, ttl=3600)
POINT_DB_ENGINES = TTLCache(maxsize=100, ttl=3600)
POINT_URLS = TTLCache(maxsize=100, ttl=3600)

point_engine_lock = Lock()
user_engine_lock = Lock()


def _create_db_engine(url: str, pool_size: int = 3, max_overflow: int = 1):
    logging.info("call method _create_db_engine")
    try:
        db_engine = create_engine(
            url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3},
        )
    except Exception:
        raise HTTPException(
            status_code=500, detail="DB engine is not created. db_url: {url}"
        )
    else:
        logging.info(f"db engine: {db_engine}, db_url: {url}")
        return db_engine


def _get_db_session(user_db_engine):
    try:
        _session = sessionmaker(autocommit=False, autoflush=False, bind=user_db_engine)
        session = _session()
        session.connection()
    except Exception:
        raise HTTPException(
            status_code=500, detail="database is temporarily unavailable"
        )
    else:
        return session


def check_users_db_availability():
    logging.info("call method check_users_db_availability")
    try:
        users_db_engine = _get_users_db_engine()
        db = _get_db_session(users_db_engine)
        logging.info(f"users DB is available, db: {db}")
    except OperationalError as error:
        settings.data_base.DB_AVAILABLE = False
        logging.info(error)
        logging.error("users DB is not available")
    except Exception as error:
        logging.error(f"{error}")
        raise error


def _get_users_db_engine():
    logging.info("call method _get_users_db_engine")
    with user_engine_lock:
        if not USERS_DB_ENGINES.get("users"):
            try:
                users_db_engine = _create_db_engine(
                    settings.data_base.get_db_url("users"), 3, 2
                )
            except Exception as error:
                raise error
            else:
                USERS_DB_ENGINES["users"] = users_db_engine
        return USERS_DB_ENGINES.get("users")


def get_users_db():
    logging.info("call method get_users_db")
    try:
        users_db_engine = _get_users_db_engine()
        logging.info(f"USERS_DB_ENGINES: {len(USERS_DB_ENGINES)}")
        db = _get_db_session(users_db_engine)
    except Exception as error:
        logging.error(f"{error}")
        raise error
    else:
        try:
            yield db
        finally:
            db.close()


def db_safe(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OperationalError:
            raise HTTPException(
                status_code=503, detail="database is temporarily unavailable"
            )

    return wrapper
