from dotenv import load_dotenv

load_dotenv()

import logging
import os
from urllib.parse import quote_plus
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
    DB_PASS: str = os.getenv("DB_PASS")  # now supports special symbols (URL-encoded)
    DB_NAME: str = os.getenv("DB_NAME", "fairy_tales")
    
    # Connection pool settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "1"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "2"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    DB_CONNECT_TIMEOUT: int = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))

    def get_db_url(self) -> str:
        # URL-encode password to handle special characters like @
        encoded_password = quote_plus(self.DB_PASS) if self.DB_PASS else ""
        encoded_user = quote_plus(self.DB_USER) if self.DB_USER else ""
        
        if self.USE_CLOUD_SQL_PROXY:
            return (
                f"postgresql+psycopg2://{encoded_user}:{encoded_password}@/{self.DB_NAME}"
                f"?host=/cloudsql/{self.INSTANCE_CONNECTION_NAME}"
            )
        else:
            return f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class JWTToken(BaseModel):
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"


class OpenAI(BaseModel):
    API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL: str = "gpt-4o-mini"
    MAX_TOKENS: int = 1500
    TEMPERATURE: float = 0.7


class AppleSignIn(BaseModel):
    # iOS App Configuration
    TEAM_ID: str = os.getenv("APPLE_TEAM_ID", "AWDSZNV22L")
    BUNDLE_ID: str = os.getenv("APPLE_BUNDLE_ID", "com.samoshynsiarhei.FairyTales")
    
    # Web Services Configuration (optional for Sign in with Apple for Web)
    SERVICES_ID: str = os.getenv("APPLE_SERVICES_ID", "")  # For web sign in
    KEY_ID: str = os.getenv("APPLE_KEY_ID", "")           # For generating tokens
    PRIVATE_KEY_PATH: str = os.getenv("APPLE_PRIVATE_KEY_PATH", "")
    PRIVATE_KEY_CONTENT: str = os.getenv("APPLE_PRIVATE_KEY_CONTENT", "")
    
    # Token Verification Settings
    APPLE_KEYS_URL: str = "https://appleid.apple.com/auth/keys"
    APPLE_ISSUER: str = "https://appleid.apple.com"
    TOKEN_CACHE_TTL: int = int(os.getenv("APPLE_TOKEN_CACHE_TTL", "3600"))  # 1 hour


class Settings(BaseSettings):
    logging: Logging = Logging()
    run: Run = Run()
    app_data: AppData = AppData()
    data_base: DataBase = DataBase()
    jwt_token: JWTToken = JWTToken()
    openai: OpenAI = OpenAI()
    apple_signin: AppleSignIn = AppleSignIn()


settings = Settings()
