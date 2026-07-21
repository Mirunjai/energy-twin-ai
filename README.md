# energy-twin-ai

**An agentic digital twin of India's crude oil supply chain**, built for ET AI Hackathon 2026 (Challenge 2 — AI-Driven Energy Supply Chain Resilience for Import-Dependent Economies).

Feed it a disruption signal — a drone strike near the Strait of Hormuz, a sanctions announcement, an insurance-premium spike — and it reasons about it the way a crisis-response team would: how much to believe the threat, how fast usable shipping capacity erodes under it, whether this has happened before and what happened last time, how many days of strategic reserve that buys the country, and where to reroute procurement instead.

## Why this exists

India sources ~88% of its crude oil from imports, with 40–45% transiting the Strait of Hormuz, and holds roughly 9.5 days of Strategic Petroleum Reserve cover. Traditional supply-chain planning tools have no way to model geopolitical scenario impacts in real time. This system replaces a single opaque risk score with cooperating agents that each own a named, citable mathematical model — so the answer to "is this just an LLM wrapper?" is specific and checkable, not a shrug.

## Architecture, in one diagram

```
news/AIS/OFAC ->  Agent 1: Geopolitical Risk     Bayesian posterior per corridor
                   (geo_agent.py)                  P(H|E) = P(E|H)P(H) / P(E)
                        |
                        v
                  Agent 2: Commodity/Logistics    Lanchester attrition ODE
                   (comm_agent.py)                  dM/dt = -c.N^2 + recovery
                        |
Chroma vector DB   Agent 3: RAG + Hidden State    Viterbi-decoded corridor state
(historical  ---->  (rag_agent.py, rag/)            (NORMAL -> CRITICAL) + cited
 case studies)                                       historical analogues
                        |
                        v
                  Orchestrator                    disagreement/escalation logic,
                   (services/orchestrator.py)        system confidence, reasoning trail
                        |
              +---------+---------+
              v                   v
   Monte Carlo engine      Graph reroute search
   (SPR days, 95% CI)      (k-shortest-path over
                            risk-weighted supply graph)
              +---------+---------+
                        v
              CrisisRoomResponse (JSON)
                        |
                        v
              React frontend — live digital twin (Mapbox)
```

Full architecture detail (component-by-component, request lifecycle, deliberate divergences from the original plan) is in [`Architecture_Update.docx`](./Architecture_Update.docx).

## The five agents, one line each

1. **Geopolitical Risk Agent** — Bayesian posterior-probability update per corridor, driven by classified evidence (hostile statements, sanctions, insurance spikes, kinetic incidents).
2. **Commodity & Logistics Agent** — solves a Lanchester attrition ODE to model corridor shipping-capacity erosion under sustained threat pressure, with a market-recovery term.
3. **RAG + Hidden-State Agent** — retrieves cited historical analogues from a vector store and decodes the corridor's hidden threat state (NORMAL → CRITICAL) via a hand-rolled Viterbi implementation.
4. **Orchestrator** — resolves disagreement between Agents 1 and 2 (e.g. "news calm, shipping data alarming") into an explicit escalate-to-human decision rather than silently averaging conflicting signals.
5. **Strategic Reserve Agent** — turns a scenario's projected shortfall into an SPR-days-remaining estimate with a Monte Carlo–derived 95% confidence interval, plus (in progress) a replenishment-window recommendation.

## Tech stack

- **Backend:** Python, FastAPI, NetworkX (supply-chain graph), SciPy (ODE solving), Chroma + sentence-transformers (RAG vector store), NumPy (Monte Carlo sampling)
- **Frontend:** React, Vite, Tailwind CSS, Mapbox GL / react-map-gl, Recharts
- **Data:** a hand-curated supply-chain graph (`backend/data/supply_network.json`) covering major suppliers, maritime corridors, Indian ports, and refineries; a seeded set of cited historical disruption case studies for the RAG layer

## Project structure

```
backend/
  agents/          geo_agent, comm_agent, rag_agent, spr_agent
  graph/           supply-chain graph loading, per-request snapshotting, reroute search
  rag/             vector store + retriever for historical case-study evidence
  simulations/     Monte Carlo engine, scenario severity profiles
  services/        orchestrator — the pipeline that ties every agent together
  supply_math/     pure math functions (Bayesian update, etc.)
  models/          Pydantic schemas and enums shared across the app
  config/          settings and threat-profile calibration data
  data/            the canonical supply-chain graph dataset
  main.py          FastAPI app entrypoint
frontend/
  src/components/  MapView (digital twin), ThreatFeed (incident trigger), DockContainer (analysis panels)
  src/context/     UI phase state machine, simulation/API state
  src/services/    API client
```

## Setup & run

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env           # fill in NEWS_API_KEY / OPENAI_API_KEY as needed
uvicorn main:app --reload --port 8000
```
Health check: `GET http://localhost:8000/api/health`

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local        # set VITE_MAPBOX_TOKEN
npm run dev
```
Opens at `http://localhost:5173`.

## Development status

This is an active hackathon build, not a finished product — treating it as anything else would be dishonest to the next person reading this repo. Known bugs, their root causes, and exact fixes are tracked in [`BUG_FIX_LIST.md`](./BUG_FIX_LIST.md). Feature ownership and what's still in progress vs. deliberately descoped is tracked in [`TASK_ASSIGNMENT.md`](./TASK_ASSIGNMENT.md). The Temporal Restricted Boltzmann Machine referenced in the architecture is intentionally kept at roadmap/cited-equation level rather than implemented live — see the architecture doc for the reasoning.

## Team

Built by Mirun, Sudarshan, and Narendra for ET AI Hackathon 2026, mentored within the CSE (AI & ML) capstone track.

## References

Every mathematical model used here is grounded in a real, checked citation (Bayesian text classification, Lanchester's Square Law for irregular warfare, Hidden Markov Models for supply-sequence modeling, Monte Carlo methods for multi-echelon supply-chain disruption risk) — full references in the architecture document.
