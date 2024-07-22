from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Surge Sentinel"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()
