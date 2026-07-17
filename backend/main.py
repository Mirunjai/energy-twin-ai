import time
import sys
import logging.config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents.geo_agent import GeopoliticalAgent
from models.schemas import DisruptionSignal, CrisisRoomResponse

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        }
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True
        }
    }
}
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

START_EPOCH = time.time()

app = FastAPI(
    title="Energy Twin AI Engine",
    description="Multi-Agent Cryptogeopolitical Core for Supply Chain Resilience Optimization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constructor now allows mapping configs, future-proofing for GraphRAG and historical DBs
geo_agent = GeopoliticalAgent(config={"analysis_version": "1.1.0"})

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
            event_type=signal.event_type,
            raw_text=signal.headline
        )
    except ValueError as ve:
        logger.warning(f"Validation error on input: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Geopolitical Agent runtime fault: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal agent processing failure.")
        
    latency = (time.perf_counter() - start_time) * 1000
    
    return CrisisRoomResponse(
        status="processed",
        execution_latency_ms=round(latency, 2),
        geopolitical_matrix=geo_output
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)