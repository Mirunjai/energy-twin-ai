from pydantic import BaseModel, Field
from typing import Dict, Any
from models.enums import EventType

class DisruptionSignal(BaseModel):
    corridor: str = Field(..., description="Target transit corridor lookup index")
    supplier: str = Field(..., description="Crude oil source country")
    event_type: EventType = Field(..., description="Validated type indicator")
    headline: str = Field(..., description="Raw text context description")

class CrisisRoomResponse(BaseModel):
    status: str
    execution_latency_ms: float
    geopolitical_matrix: Dict[str, Any]