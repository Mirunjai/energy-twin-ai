import requests
import json
import time

API_URL = "http://localhost:8000/api/crisis/trigger"

# The 3 Historical Case Studies mapped from the Master Plan
CASE_STUDIES = [
    {
        "name": "Case Study 1: Houthi Attacks (August 2023)",
        "payload": {
            "corridor": "bab_el_mandeb",
            "supplier": "iraq",
            "event_type": "kinetic_incident",
            "headline": "Sustained drone and missile attacks on commercial shipping in the Red Sea"
        }
    },
    {
        "name": "Case Study 2: US-Iran Standoff (Jan-Feb 2025)",
        "payload": {
            "corridor": "strait_of_hormuz",
            "supplier": "saudi_arabia",
            "event_type": "sanctions_announcement",
            "headline": "Renewed US sanctions pressure on Iranian exports and maritime security advisories"
        }
    },
    {
        "name": "Case Study 3: Red Sea Shipping Pressure (March 2025)",
        "payload": {
            "corridor": "bab_el_mandeb",
            "supplier": "uae",
            "event_type": "kinetic_incident",
            "headline": "Sustained vessel diversions and rising insurance costs due to regional pressure"
        }
    }
]

def run_backtest():
    print("="*60)
    print("ENERGY TWIN AI - HISTORICAL BACKTEST VALIDATION")
    print("="*60 + "\n")
    
    for case in CASE_STUDIES:
        print(f"Executing {case['name']}...")
        print(f"Payload: {case['payload']['headline']}")
        
        try:
            start_time = time.time()
            response = requests.post(API_URL, json=case["payload"], headers={"Content-Type": "application/json"})
            response.raise_for_status()
            data = response.json()
            latency = round((time.time() - start_time) * 1000, 2)
            
            # Extract key metrics for the judges
            sim_context = data.get("simulation_context", {})
            metadata = sim_context.get("metadata", {}).get("agent_analysis", {})
            geo = metadata.get("geo", {})
            mc = data.get("monte_carlo_results", {})
            macro = metadata.get("macro_impacts", {})
            
            print(f"Status: SUCCESS ({latency}ms)")
            print(f"  -> Agent 1 (Geo): {geo.get('posterior_probability')} Posterior | Band: {metadata.get('reasoning_trail', {}).get('bayesian_evidence', {}).get('confidence_band')}")
            print(f"  -> Agent 3 (HMM): Hidden State Decoded as {metadata.get('current_hidden_state')} (Conf: {round(metadata.get('viterbi_confidence', 0), 2)})")
            print(f"  -> Monte Carlo:   SPR 95% CI: {mc.get('confidence_interval_str')}")
            if macro:
                print(f"  -> Macro Impact:  GDP {macro.get('gdp_trajectory', {}).get('gdp_impact_estimate_pct')}% | Power Stress: {macro.get('power_sector_stress', {}).get('power_sector_stress_multiplier')}x")
            
            escalation = metadata.get("escalation_status")
            print(f"  -> Orchestrator:  {escalation}")
            print("-" * 60)
            
        except requests.exceptions.RequestException as e:
            print(f"Status: FAILED")
            print(f"Error: {e}")
            print("-" * 60)

if __name__ == "__main__":
    run_backtest()