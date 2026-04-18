from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Auth Service"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    MONGODB_URL: str
    MONGODB_DB_NAME: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
