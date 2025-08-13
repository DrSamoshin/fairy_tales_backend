import logging
import uvicorn
from app.core.configs import settings
from app.db.db_sessions import check_users_db_availability


def run():
    check_users_db_availability()
    logging.info("check DB")
    try:
        uvicorn.run(
            "app.main:main_app",
            host=settings.run.host,
            port=settings.run.port,
            reload=True,
        )
    except Exception as error:
        logging.error(error)


if __name__ == "__main__":
    run()
