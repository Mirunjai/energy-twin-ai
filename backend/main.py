import time
import sys
import uuid
import contextvars
import logging.config
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from agents.geo_agent import GeopoliticalAgent
from models.schemas import DisruptionSignal, CrisisRoomResponse

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
logging.Formatter.converter = time.gmtime  # Enforce UTC timestamps
logger = logging.getLogger("energy_twin.api")

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

geo_agent = GeopoliticalAgent(config={"analysis_version": "1.1.0"})

@app.on_event("startup")
async def startup_event():
    logger.info(
        "Energy Twin AI Engine initializing",
        extra={
            "version": app.version,
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "start_epoch": START_EPOCH,
        }
    )

@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    # Generate and set the UUID for this specific request
    req_id = str(uuid.uuid4())[:8] # Short UUID for cleaner terminal readability
    token = request_id_var.set(req_id)
    
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    
    response.headers["X-Request-ID"] = req_id
    response.headers["X-System-Latency-MS"] = f"{process_time:.2f}"
    
    request_id_var.reset(token)
    return response

@app.get("/api/health")
async def health_check():
    return {
        "status": "operational",
        "version": app.version,
        "agents_loaded": ["GeopoliticalAgent"],
        "uptime_seconds": round(time.time() - START_EPOCH, 2)
    }

@app.post("/api/crisis/trigger", response_model=CrisisRoomResponse)
async def trigger_crisis_room(signal: DisruptionSignal):
    start_time = time.perf_counter()
    logger.info(f"Incoming disruption signal: {signal.event_type.value} in {signal.corridor}")
    
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
    logger.info(f"Crisis evaluation complete in {latency:.2f}ms")
    
    return CrisisRoomResponse(
        status="processed",
        execution_latency_ms=round(latency, 2),
        geopolitical_matrix=geo_output
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)