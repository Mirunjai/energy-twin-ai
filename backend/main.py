import time
import sys
import uuid
import contextvars
import logging.config
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# Bring in the full ecosystem
from config.settings import settings
from agents.geo_agent import GeopoliticalAgent
from agents.comm_agent import CommodityAgent      # 1. FIXED: Imported missing Agent 2
from services.orchestrator import CrisisOrchestrator # 2. FIXED: Linked to unified agents dir
from graph.network_graph import SupplyChainGraph
from models.schemas import DisruptionSignal, CrisisRoomResponse
from simulations.monte_carlo import MonteCarloEngine

# Context variable to hold the Request ID across async boundaries
request_id_var = contextvars.ContextVar("request_id", default="system")

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {
            "()": RequestIdFilter
        }
    },
    "formatters": {
        "standard": {
            "format": "%(asctime)s | [%(request_id)s] | %(name)s | %(levelname)s | %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
            "filters": ["request_id"]
        }
    },
    "loggers": {
        "energy_twin": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logging.Formatter.converter = time.gmtime  
logger = logging.getLogger("energy_twin.backend.api")

START_EPOCH = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Energy Twin AI Engine initializing",
        extra={
            "version": app.version,
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "start_epoch": START_EPOCH,
        }
    )
    yield
    logger.info("Energy Twin AI Engine shutting down")

app = FastAPI(
    title="Energy Twin AI Engine",
    description="Multi-Agent Cryptogeopolitical Core for Supply Chain Resilience Optimization",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the ecosystem globally so it persists across requests
geo_agent = GeopoliticalAgent(app_settings=settings)
comm_agent = CommodityAgent() # 3. FIXED: Instantiated the logistics tracking instance
canonical_graph = SupplyChainGraph(data_path="data/supply_network.json")
mc_engine = MonteCarloEngine()

# 4. FIXED: Passed complete parameters including Agent 2 matching __init__ expectations
orchestrator = CrisisOrchestrator(
    geo_agent=geo_agent, 
    comm_agent=comm_agent,
    mc_engine=mc_engine,
    canonical_graph=canonical_graph 
)

@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    req_id = str(uuid.uuid4())[:8]
    token = request_id_var.set(req_id)
    start_time = time.perf_counter()
    
    try:
        response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000
        
        response.headers["X-Request-ID"] = req_id
        response.headers["X-System-Latency-MS"] = f"{process_time:.2f}"
        
        logger.info(
            "Request completed",
            extra={
                "status_code": response.status_code,
                "latency_ms": round(process_time, 2),
            }
        )
        return response
    finally:
        request_id_var.reset(token)

@app.get("/api/health")
async def health_check():
    return {
        "status": "operational",
        "version": app.version,
        "agents_loaded": ["GeopoliticalAgent", "CommodityAgent", "CrisisOrchestrator", "MonteCarloEngine"],
        "uptime_seconds": round(time.time() - START_EPOCH, 2)
    }

@app.post("/api/crisis/trigger", response_model=CrisisRoomResponse)
async def trigger_crisis_room(signal: DisruptionSignal):
    start_time = time.perf_counter()
    logger.info(f"Incoming disruption signal: {signal.event_type.value} in {signal.corridor}")
    
    try:
        # Route through the Orchestrator's Context Pipeline
        sim_context = orchestrator.process_disruption(signal)
    except ValueError as ve:
        logger.warning(f"Validation error on input: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        logger.exception("Orchestrator runtime fault")
        raise HTTPException(status_code=500, detail="Internal processing failure.")
        
    latency = (time.perf_counter() - start_time) * 1000
    
    return CrisisRoomResponse(
        status="processed",
        execution_latency_ms=round(latency, 2),
        simulation_context=sim_context
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)