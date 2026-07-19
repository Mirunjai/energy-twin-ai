import numpy as np
from scipy.integrate import odeint

class CommodityLogisticsAgent:
    def __init__(self):
        self.critical_capacity_threshold = 60.0  # 60% usable capacity remaining
        
        # 1. Dynamic c: Escort effectiveness mapping
        self.escort_mapping = {
            "high": 0.03,   # US Navy / Coalition heavy
            "medium": 0.06, # Regional escort
            "low": 0.09,    # Minimal escort
            "none": 0.12    # No escort
        }
        
        # 3. Threat Modifiers
        self.threat_multipliers = {
            "mine_laying": 1.5,
            "drone_attacks": 1.2,
            "missile_attacks": 1.8,
            "naval_blockade": 2.0,
            "insurance_shock": 1.0,
            "political_sanctions": 0.5,
            "default": 1.0
        }

    def _get_defense_factor(self, escort_level):
        return self.escort_mapping.get(escort_level.lower(), 0.06)

    def _lanchester_attrition(self, M, t, N_time_series, t_points, c):
        """
        The Lanchester Square Law ODE: dM/dt = -c * N(t)^2
        Uses np.interp to evaluate time-varying N at specific solver steps.
        """
        N_t = np.interp(t, t_points, N_time_series)
        dMdt = -c * (N_t ** 2)
        return dMdt

    def fetch_logistics_signals(self, corridor_id):
        """
        4. Broader Agent 2 Logistics Connections.
        In a production environment, this queries FRED, AIS Hub, and Insurance indices.
        """
        return {
            "brent_wti_spread_volatility": "elevated",
            "ais_diversion_rate": 0.15, # 15% of traffic actively diverting
            "insurance_premium_spike": True
        }

    def evaluate_corridor_capacity(self, geo_payload, escort_level="medium", days_to_simulate=30):
        """
        Projects shipping capacity erosion using dynamic Lanchester ODE.
        geo_payload: Dict containing posterior_probability and threat_type.
        """
        threat_posterior = geo_payload.get("posterior_probability", 0.5)
        threat_type = geo_payload.get("threat_type", "default")
        
        # Determine dynamic defense factor (c)
        c = self._get_defense_factor(escort_level)
        
        # Calculate base intensity using threat-specific multipliers
        multiplier = self.threat_multipliers.get(threat_type, 1.0)
        base_N = (threat_posterior * 10.0) * multiplier
        
        # 2. Time-varying N(t): Simulate conflict escalation over time
        # This creates a curve that ramps up, peaks, and stabilizes
        t_points = np.arange(days_to_simulate + 1)
        escalation_curve = np.clip(np.sin(t_points / 5.0) * 0.4 + 1.0, 0.8, 1.5)
        N_time_series = base_N * escalation_curve
        
        # Initial merchant capacity (100%)
        M0 = 100.0
        
        # Solve the ODE
        M_t = odeint(
            self._lanchester_attrition, 
            M0, 
            t_points, 
            args=(N_time_series, t_points, c)
        ).flatten()
        
        # Capacity cannot drop below 0%
        M_t = np.maximum(M_t, 0)
        
        # Extract analytical results using idiomatic NumPy
        final_capacity = M_t[-1]
        critical_indices = np.where(M_t < self.critical_capacity_threshold)[0]
        days_to_critical = int(critical_indices[0]) if len(critical_indices) > 0 else None
        
        # Combine Lanchester output with broader logistics signals
        logistics_signals = self.fetch_logistics_signals(geo_payload.get("corridor_id"))
        
        return {
            "initial_capacity": M0,
            "final_capacity": round(float(final_capacity), 2),
            "is_critical": len(critical_indices) > 0,
            "days_to_critical": days_to_critical,
            "capacity_trajectory": np.round(M_t, 1).tolist(),
            "logistics_signals": logistics_signals
        }