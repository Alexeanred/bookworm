from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    sqlalchemy_string: str = "postgresql://duytien:okbaby@localhost:5432/bookworm"
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
settings = Settings()

if __name__ == "__main__":
    print(f"Database URL: {settings.sqlalchemy_string}")