from dotenv import load_dotenv

load_dotenv()

import logging
import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Run(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    ADMIN_MODE: bool = os.getenv("ADMIN_MODE", "true").lower() == "true"


class AppData(BaseModel):
    title: str = "Fairy Tales"
    version: str = "1.0.0"
    openapi_version: str = "3.1.0"
    description: str = (
        "This backend application is built on FastAPI and implements the full logic of cafe management."
    )


class Logging(BaseModel):
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)-9s %(asctime)s - %(module)-15s - %(message)s",
    )


class DataBase(BaseModel):
    DB_AVAILABLE: bool = True
    # google proxy connection
    USE_CLOUD_SQL_PROXY: bool = (
        os.getenv("USE_CLOUD_SQL_PROXY", "false").lower() == "true"
    )
    INSTANCE_CONNECTION_NAME: str = os.getenv("INSTANCE_CONNECTION_NAME")
    # local connection
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")  # should be without special symbols

    def get_db_url(self, db_name: str) -> str:
        if self.USE_CLOUD_SQL_PROXY:
            return (
                f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@/{db_name}"
                f"?host=/cloudsql/{self.INSTANCE_CONNECTION_NAME}"
            )
        else:
            return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{db_name}"


class JWTToken(BaseModel):
    JWT_SECRET_KEY: str = os.getenv("JWT_POINT_SECRET_KEY")
    ALGORITHM: str = "HS256"


class Settings(BaseSettings):
    logging: Logging = Logging()
    run: Run = Run()
    app_data: AppData = AppData()
    data_base: DataBase = DataBase()
    jwt_token: JWTToken = JWTToken()


settings = Settings()
