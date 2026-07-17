from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional
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
    corridor_id: str
    supplier_id: str
    event_processed: str

class GeoAgentResponse(BaseModel):
    input: SignalInputContext
    normalized: NormalizedContext
    metrics: BayesianMetrics
    formula: Dict[str, str]
    threat_severity: str
    reason: str
    agent_signature: str
    analysis_version: str
    timestamp: str

class ProcurementAlternative(BaseModel):
    path_nodes: List[str]
    cumulative_risk: float
    total_distance_nm: float
    estimated_cost_delta_per_day: float

class MonteCarloResults(BaseModel):
    iterations: int
    spr_days_remaining_mean: float
    spr_days_remaining_p5: float  # 5th percentile (Worst case)
    spr_days_remaining_p95: float # 95th percentile (Best case)
    expected_shortfall_mbd: float
    confidence_interval_str: str

class SimulationContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    signal: DisruptionSignal
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Internal state (Excluded from final API JSON payload)
    graph_snapshot: Any = Field(default=None, exclude=True) 

    # Agent Outputs
    geo_response: Optional[GeoAgentResponse] = None
    procurement_alternatives: List[ProcurementAlternative] = Field(default_factory=list)
    monte_carlo_results: Optional[MonteCarloResults] = None
    # [Future: graphrag_results, communication_results]

class CrisisRoomResponse(BaseModel):
    status: str
    execution_latency_ms: float
    simulation_context: SimulationContext