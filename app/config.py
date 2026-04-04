from pydantic_settings import BaseSettings

from app.get_secret import get_secret

class Settings(BaseSettings):

    _postgres_password = get_secret('postgres')
    DATABASE_URL: str = f'postgresql://postgres:{_postgres_password}@localhost:5432/fastapi_db'

    SECRET_KEY: str = get_secret('secret_key')
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = '.env'

settings = Settings()
