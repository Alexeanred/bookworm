from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/bookworm")
    sqlalchemy_string: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/bookworm")
    jwt_secret: str = os.getenv("JWT_SECRET", "your_jwt_secret_key_here")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')

settings = Settings()

if __name__ == "__main__":
    print(f"Database URL: {settings.sqlalchemy_string}")