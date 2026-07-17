from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    analysis_version: str = "1.1.0"
    debug: bool = False
    
    # Future integration stubs
    # mongo_uri: str = "mongodb://localhost:27017"
    # redis_url: str = "redis://localhost:6379"

settings = Settings()