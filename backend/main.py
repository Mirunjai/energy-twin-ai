import time
import sys
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any
from agents.geo_agent import GeopoliticalAgent, EventType

# Initialize uptime baseline variables
START_EPOCH = time.time()

app = FastAPI(
    title="Energy Twin AI Engine",
    description="Multi-Agent Cryptogeopolitical Core for Supply Chain Resilience Optimization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active agent instances
geo_agent = GeopoliticalAgent()

class DisruptionSignal(BaseModel):
    corridor: str = Field(..., description="Target transit corridor lookup index")
    supplier: str = Field(..., description="Crude oil source country")
    event_type: EventType = Field(..., description="Validated type indicator")
    headline: str = Field(..., description="Raw text context description")

class CrisisRoomResponse(BaseModel):
    status: str
    execution_latency_ms: float
    geopolitical_matrix: Dict[str, Any]

@app.middleware("http")
async def add_telemetry_headers(request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    
    response.headers["X-System-Latency-MS"] = f"{process_time:.2f}"
    response.headers["X-Agent"] = "Geo"
    return response

@app.get("/api/health")
async def health_check():
    return {
        "status": "operational",
        "version": "1.0.0",
        "agents_loaded": ["GeopoliticalAgent"],
        "uptime_seconds": round(time.time() - START_EPOCH, 2),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }

@app.post("/api/crisis/trigger", response_model=CrisisRoomResponse)
async def trigger_crisis_room(signal: DisruptionSignal):
    start_time = time.perf_counter()
    
    try:
        geo_output = geo_agent.analyze_signal(
            corridor=signal.corridor,
            supplier=signal.supplier,
            event_type=signal.event_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geopolitical Agent runtime fault: {str(e)}")
        
    # TODO: Sequence subsequent modules (Comm -> Graph -> Monte Carlo -> Optimization)
    
    latency = (time.perf_counter() - start_time) * 1000
    
    return CrisisRoomResponse(
        status="processed",
        execution_latency_ms=round(latency, 2),
        geopolitical_matrix=geo_output
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
