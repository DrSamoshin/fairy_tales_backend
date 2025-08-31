import logging
import uvicorn
from app.core.configs import settings

# Configure logging for detailed debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)-8s %(asctime)s - %(name)-20s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def run():
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
