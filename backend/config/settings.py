from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict

class Settings(BaseSettings):
    analysis_version: str = "1.1.0"
    debug: bool = False
    
    # Safely isolated mutable default
    graph_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "risk": 1000.0,
            "distance": 0.1,
            "alpha": 1.0,
            "beta": 0.5,
        }
    )

settings = Settings()