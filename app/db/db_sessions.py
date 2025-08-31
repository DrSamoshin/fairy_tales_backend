import logging
import os
from functools import wraps
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from cachetools import TTLCache
from threading import Lock

from app.core.configs import settings


DB_ENGINES = TTLCache(maxsize=100, ttl=3600)

engine_lock = Lock()


def _create_db_engine(url: str, pool_size: int = None, max_overflow: int = None):
    logging.info("Creating database engine with optimized settings")
    
    # Use settings from config if not provided
    if pool_size is None:
        pool_size = settings.data_base.DB_POOL_SIZE
    if max_overflow is None:
        max_overflow = settings.data_base.DB_MAX_OVERFLOW
    
    try:
        db_engine = create_engine(
            url,
            # Connection pool optimization
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=settings.data_base.DB_POOL_TIMEOUT,
            pool_recycle=settings.data_base.DB_POOL_RECYCLE,
            pool_pre_ping=True,  # Enables pessimistic disconnect handling
            
            # Connection settings
            connect_args={
                "connect_timeout": settings.data_base.DB_CONNECT_TIMEOUT,
                "options": "-c timezone=utc"  # Set timezone
            },
            
            # Echo SQL queries in development (can be controlled via env)
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            
            # Connection event handling
            pool_reset_on_return="commit",  # Reset connections on return
        )
        
        # Test the connection
        with db_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
    except Exception as e:
        logging.error(f"Failed to create database engine: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database engine creation failed: {str(e)}"
        )
    else:
        logging.info(f"Database engine created successfully with pool_size={pool_size}, max_overflow={max_overflow}")
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


def _get_db_engine():
    logging.info("call method _get_db_engine")
    with engine_lock:
        if not DB_ENGINES.get("fairy_tales"):
            try:
                db_engine = _create_db_engine(
                    settings.data_base.get_db_url()
                )
            except Exception as error:
                raise error
            else:
                DB_ENGINES["fairy_tales"] = db_engine
        return DB_ENGINES.get("fairy_tales")


def get_db():
    logging.info("call method get_db")
    try:
        db_engine = _get_db_engine()
        logging.info(f"DB_ENGINES: {len(DB_ENGINES)}")
        db = _get_db_session(db_engine)
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
