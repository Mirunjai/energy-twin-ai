import numpy as np
import json
from scipy.integrate import odeint
import os

class CommodityLogisticsAgent:
    def __init__(self):
        self.critical_capacity_threshold = 60.0
        self.max_capacity = 100.0
        self._load_threat_profiles()
        
    def _load_threat_profiles(self):
        config_path = os.path.join(os.path.dirname(__file__), '../config/threat_profiles.json')
        try:
            with open(config_path, 'r') as f:
                self.threat_configs = json.load(f)
        except FileNotFoundError:
            # Fallback for demonstration if file is missing
            self.threat_configs = {"default": {"multiplier": 1.0, "profile_type": "slow_burn"}}

    def _generate_escalation_curve(self, profile_type, days):
        """
        Maps theoretical escalation profiles to historical case studies.
        """
        t = np.arange(days + 1)
        if profile_type == "rapid":
            # Models August 2023 Houthi escalation: fast peak, sustained plateau
            return 1.0 - np.exp(-t / 3.0) + 0.5 
        elif profile_type == "shock":
            # Immediate spike followed by gradual decay as markets adapt
            return np.where(t < 2, 2.0, 2.0 * np.exp(-(t-2)/10.0))
        elif profile_type == "slow_burn":
            # Models January 2025 US-Iran standoff: gradual tension build-up
            return 0.5 + (t / days) * 1.5 
        else:
            return np.ones_like(t)

    def _lanchester_with_recovery(self, M, t, N_time_series, t_points, c, r):
        """
        Lanchester ODE with a market adaptation/recovery term.
        dM/dt = -c * N(t)^2 + r * (M_max - M)
        """
        N_t = np.interp(t, t_points, N_time_series)
        attrition = -c * (N_t ** 2)
        recovery = r * (self.max_capacity - M)
        return attrition + recovery

    def fetch_logistics_signals(self, corridor_id):
        """
        Integrates Agent 2's core mandate: Brent/WTI volatility, AIS, and insurance data.
        """
        # In production, query FRED, Quandl, and AIS Hub APIs here.
        return {
            "brent_wti_spread_volatility": 0.45,  # High volatility
            "ais_diversion_rate": 0.15,           # 15% traffic actively diverting
            "insurance_premium_spike": True,
            "tanker_availability_index": 0.82     # Squeezed but available
        }

    def evaluate_corridor_capacity(self, geo_payload, escort_strength=0.5, days_to_simulate=30):
        threat_type = geo_payload.get("threat_type", "default")
        threat_posterior = geo_payload.get("posterior_probability", 0.5)
        
        # 1. Continuous Escort Strength [0.0 to 1.0]
        # 0.0 = No escort (c=0.12), 1.0 = Heavy Navy coalition (c=0.03)
        c = 0.12 - (np.clip(escort_strength, 0.0, 1.0) * 0.09)
        
        # 2. Data-Driven Threat Multipliers
        config = self.threat_configs.get(threat_type, self.threat_configs["default"])
        multiplier = config.get("multiplier", 1.0)
        profile_type = config.get("profile_type", "slow_burn")
        
        # 3. Dynamic Escalation Curve
        base_N = (threat_posterior * 10.0) * multiplier
        t_points = np.arange(days_to_simulate + 1)
        escalation_curve = self._generate_escalation_curve(profile_type, days_to_simulate)
        N_time_series = base_N * escalation_curve
        
        # 4. Integrate Logistics Signals into Recovery Term
        logistics_signals = self.fetch_logistics_signals(geo_payload.get("corridor_id"))
        
        # Calculate recovery rate (r) based on market adaptation capability
        # High AIS diversion means the market is adapting, increasing the recovery coefficient
        base_recovery = 0.05
        ais_adaptation = logistics_signals["ais_diversion_rate"] * 0.1
        insurance_drag = -0.02 if logistics_signals["insurance_premium_spike"] else 0.01
        r = max(0.01, base_recovery + ais_adaptation + insurance_drag)
        
        # 5. Solve the ODE
        M0 = self.max_capacity
        M_t = odeint(
            self._lanchester_with_recovery, 
            M0, 
            t_points, 
            args=(N_time_series, t_points, c, r)
        ).flatten()
        
        M_t = np.clip(M_t, 0, 100)
        
        final_capacity = M_t[-1]
        critical_indices = np.where(M_t < self.critical_capacity_threshold)[0]
        days_to_critical = int(critical_indices[0]) if len(critical_indices) > 0 else None
        
        return {
            "initial_capacity": M0,
            "final_capacity": round(float(final_capacity), 2),
            "is_critical": len(critical_indices) > 0,
            "days_to_critical": days_to_critical,
            "capacity_trajectory": np.round(M_t, 1).tolist(),
            "logistics_signals": logistics_signals,
            "mathematical_context": {
                "escort_coefficient": round(c, 3),
                "recovery_coefficient": round(r, 3),
                "profile_type": profile_type
            }
        }