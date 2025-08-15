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
    
    # Connection pool settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    DB_CONNECT_TIMEOUT: int = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))

    def get_db_url(self, db_name: str) -> str:
        if self.USE_CLOUD_SQL_PROXY:
            return (
                f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@/{db_name}"
                f"?host=/cloudsql/{self.INSTANCE_CONNECTION_NAME}"
            )
        else:
            return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{db_name}"


class JWTToken(BaseModel):
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"


class OpenAI(BaseModel):
    API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL: str = "gpt-4o-mini"
    MAX_TOKENS: int = 1500
    TEMPERATURE: float = 0.7


class AppleSignIn(BaseModel):
    TEAM_ID: str = os.getenv("APPLE_TEAM_ID", "")
    KEY_ID: str = os.getenv("APPLE_KEY_ID", "")
    CLIENT_ID: str = os.getenv("APPLE_CLIENT_ID", "")
    PRIVATE_KEY_PATH: str = os.getenv("APPLE_PRIVATE_KEY_PATH", "")
    # Alternative: store private key content directly
    PRIVATE_KEY_CONTENT: str = os.getenv("APPLE_PRIVATE_KEY_CONTENT", "")


class Settings(BaseSettings):
    logging: Logging = Logging()
    run: Run = Run()
    app_data: AppData = AppData()
    data_base: DataBase = DataBase()
    jwt_token: JWTToken = JWTToken()
    openai: OpenAI = OpenAI()
    apple_signin: AppleSignIn = AppleSignIn()


settings = Settings()
