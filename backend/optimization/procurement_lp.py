
import json
import os


from pulp import LpProblem,LpMinimize,LpVariable, value
from pulp import lpSum as lpsum


from pulp import PULP_CBC_CMD

  # msg=0 silences the solver


def load_graph_data(path: str = None) -> dict:

    if path is None:
        path = os.path.join(os.path.dirname(__file__), '..', 'data', 'supply_network.json')

    with open(path, 'r') as f:
        return json.load(f)


def optimize_procurement(graph_data: dict, disrupted_corridor: str = None, risk_posterior: float = 0.5) -> list[dict]:

    ''' Solves minimum cost network flow lp for oil'''

    ''' Returns a list of dicts matching the ProcurementAlternative schema'''


    nodes = {n["id"]: n for n in graph_data["nodes"]}
    edges = graph_data["edges"]

    suppliers = [n["id"] for n in graph_data["nodes"] if n["type"] == "supplier"]

    refineries = [n["id"] for n in graph_data["nodes"] if n["type"] == "refinery"]


    COST_PER_NM = 1500.0
    RISK_PENALTY = 100000.0


    model = LpProblem("Procurement_Optimization", LpMinimize)

    flow_vars = {}

    for i, edge in enumerate(edges):
        var_name = f"flow_{edge['source']}_{edge['target']}"
        flow_vars[i] = LpVariable(var_name, lowBound=0, upBound=edge["capacity_mbd"])
    


    objective_terms = []
    for i, edge in enumerate(edges):
        distance_cost = edge["distance_nm"] * COST_PER_NM
        
        # If this edge touches the disrupted corridor, use the high posterior risk
        risk = edge["base_risk_weight"]
        if disrupted_corridor and (edge["source"] == disrupted_corridor or edge["target"] == disrupted_corridor):
            risk = risk_posterior  # e.g. 0.85 instead of 0.1
        
        risk_cost = risk * RISK_PENALTY
        edge_cost = distance_cost + risk_cost
        
        objective_terms.append(flow_vars[i] * edge_cost)
    
    model += lpsum(objective_terms), "Total_Procurement_Cost"





    # Constraint 1: Supplier output limits
    for s_id in suppliers:
        outgoing = [flow_vars[i] for i, e in enumerate(edges) if e["source"] == s_id]
        if outgoing:
            model += lpsum(outgoing) <= nodes[s_id].get("production_mbd", 999), f"supply_{s_id}"
    
    # Constraint 2: Refinery intake limits
    for r_id in refineries:
        incoming = [flow_vars[i] for i, e in enumerate(edges) if e["target"] == r_id]
        if incoming:
            model += lpsum(incoming) <= nodes[r_id].get("capacity_mbd", 999), f"refinery_{r_id}"
    
        # Constraint: Demand — refineries MUST receive a minimum amount of oil
    DEMAND_FRACTION = 0.8  # refineries must operate at least 80% capacity
    for r_id in refineries:
        incoming = [flow_vars[i] for i, e in enumerate(edges) if e["target"] == r_id]
        if incoming:
            min_demand = nodes[r_id].get("capacity_mbd", 0) * DEMAND_FRACTION
            model += lpsum(incoming) >= min_demand, f"demand_{r_id}"

    # Constraint 3: Flow conservation at intermediate nodes (corridors, ports)
    intermediate_ids = [n["id"] for n in graph_data["nodes"] if n["type"] in ("corridor", "port")]
    for n_id in intermediate_ids:
        inflow = [flow_vars[i] for i, e in enumerate(edges) if e["target"] == n_id]
        outflow = [flow_vars[i] for i, e in enumerate(edges) if e["source"] == n_id]
        if inflow or outflow:
            model += lpsum(inflow) == lpsum(outflow), f"conservation_{n_id}"

    

    model.solve(PULP_CBC_CMD(msg=0))
    
    # Build results: only include edges with non-zero flow
    results = []
    for i, edge in enumerate(edges):
        flow = value(flow_vars[i])
        if flow and flow > 0.001:  # skip near-zero flows
            risk = edge["base_risk_weight"]
            if disrupted_corridor and (edge["source"] == disrupted_corridor or edge["target"] == disrupted_corridor):
                risk = risk_posterior
            
            results.append({
                "path_nodes": [edge["source"], edge["target"]],
                "cumulative_risk": round(risk, 4),
                "total_distance_nm": edge["distance_nm"],
                "estimated_cost_delta_per_day": round(flow * edge["distance_nm"] * COST_PER_NM, 2),
                "flow_mbd": round(flow, 4)
            })
    
    # Sort by cost so the cheapest active routes come first
    results.sort(key=lambda r: r["estimated_cost_delta_per_day"])
    
    return results


if __name__ == "__main__":
    data = load_graph_data()
    
    print("=== Normal conditions (no disruption) ===")
    normal = optimize_procurement(data)
    for r in normal:
        print(f"  {r['path_nodes'][0]} → {r['path_nodes'][1]}: {r['flow_mbd']} mbd, ${r['estimated_cost_delta_per_day']:,.0f}/day")
    
    print("\n=== Hormuz crisis (risk = 0.85) ===")
    crisis = optimize_procurement(data, disrupted_corridor="strait_of_hormuz", risk_posterior=0.85)
    for r in crisis:
        print(f"  {r['path_nodes'][0]} → {r['path_nodes'][1]}: {r['flow_mbd']} mbd, ${r['estimated_cost_delta_per_day']:,.0f}/day")

