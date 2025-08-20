from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


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
    ADMIN_ID: List[int]   

    @field_validator("ADMIN_ID", mode="before")
    def split_admins(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",")]
        return v

    class Config:
        env_file = ".env"


settings = Settings()
