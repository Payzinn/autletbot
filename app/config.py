from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    CHAT_ID: int
    DB_USER: str
    DB_PORT: int
    DB_PASS: str
    DB_NAME: str
    DB_HOST: str
    DEFAULT_REF_LINK: str
    CHECK_LINK: str


    class Config:
        env_file = ".env"

settings = Settings()