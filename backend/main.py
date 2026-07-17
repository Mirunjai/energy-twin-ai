"""FastAPI entry point for disruption scenario orchestration."""

import asyncio
import uuid
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.agents.orchestrator import run_orchestration


app = FastAPI(title="Energy Twin AI Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScenarioRequest(BaseModel):
    scenario_type: str = Field(default="chokepoint_disruption")
    payload: dict[str, Any] = Field(default_factory=dict)


class ScenarioResponse(BaseModel):
    run_id: str
    status: str


scenario_runs: dict[str, dict[str, Any]] = {}


async def _run_scenario(run_id: str, request: ScenarioRequest) -> None:
    scenario_runs[run_id]["status"] = "running"
    result = await run_orchestration(request.scenario_type, request.payload)
    scenario_runs[run_id].update({"status": "completed", "result": result})


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/scenarios/trigger", response_model=ScenarioResponse)
async def trigger_scenario(request: ScenarioRequest) -> ScenarioResponse:
    run_id = str(uuid.uuid4())
    scenario_runs[run_id] = {
        "scenario_type": request.scenario_type,
        "payload": request.payload,
        "status": "queued",
    }
    asyncio.create_task(_run_scenario(run_id, request))
    return ScenarioResponse(run_id=run_id, status="queued")


@app.get("/scenarios/{run_id}")
async def get_scenario(run_id: str) -> dict[str, Any]:
    return scenario_runs.get(run_id, {"status": "not_found"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
