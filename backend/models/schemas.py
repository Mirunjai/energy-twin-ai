from pydantic import BaseModel, Field
from typing import Dict, Any
from .enums import EventType

class DisruptionSignal(BaseModel):
    corridor: str = Field(..., description="Target transit corridor lookup index")
    supplier: str = Field(..., description="Crude oil source country")
    event_type: EventType = Field(..., description="Validated type indicator")
    headline: str = Field(..., description="Raw text context description")

class BayesianMetrics(BaseModel):
    prior_probability: float
    prior_odds: float
    likelihood_ratio: float
    posterior_probability: float
    posterior_odds: float
    risk_delta: float
    impact_score: float

class SignalInputContext(BaseModel):
    corridor: str
    supplier: str
    headline: str

class NormalizedContext(BaseModel):
    corridor: str
    supplier: str
    event_processed: str

class GeoAgentResponse(BaseModel):
    input: SignalInputContext
    normalized: NormalizedContext
    metrics: BayesianMetrics
    formula: Dict[str, str]  # New: Displaying the math for the judges
    threat_severity: str
    reason: str
    agent_signature: str
    analysis_version: str
    timestamp: str

class CrisisRoomResponse(BaseModel):
    status: str
    execution_latency_ms: float
    geopolitical_matrix: GeoAgentResponse