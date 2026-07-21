#Hey Sudarshan, extend the existing SPRTracker dataclass in agents/spr_agent.py by adding this exact method. Don't touch days_remaining(), just add this below it so we can calculate when we hit the minimum threshold.


from datetime import datetime,timedelta
from dataclasses import dataclass
import math

@dataclass
class SPRTracker:
    starting_reserve_mmbbl: float = 740.0
    drawdown_mmbbl_per_day: float = 1.0
    def days_remaining(self, current_reserve_mmbbl: float | None = None) -> float:
        reserve = self.starting_reserve_mmbbl if current_reserve_mmbbl is None else current_reserve_mmbbl
        if self.drawdown_mmbbl_per_day <= 0:
            return float("inf")
        return max(reserve / self.drawdown_mmbbl_per_day, 0.0)

# Add this method inside the SPRTracker dataclass:
    def calculate_replenishment_window(
        self,
        current_reserve_mmbbl: float,
        daily_shortfall_mmbbl: float,
        minimum_reserve_mmbbl: float = 90.0,  # e.g., ~10 days of baseline cover
        start_date: datetime | None = None
    ) -> dict:
        """
        Given the current reserve and the daily shortfall projected by the simulation,
        calculate the exact date the reserve will breach the minimum threshold.
        
        Returns:
        {
            "days_until_breach": float,
            "replenishment_trigger_date": str  # ISO format YYYY-MM-DD
        }
        """

        if daily_shortfall_mmbbl <= 0:
            return {
                "days_until_breach": float('inf'),
                "replenishment_trigger_date": "Never"
            }
    
        if current_reserve_mmbbl <= minimum_reserve_mmbbl:
            return {
                "days_until_breach": 0.0,
                "replenishment_trigger_date": (start_date or datetime.now()).strftime('%Y-%m-%d')
            }
    
        usable_reserve = current_reserve_mmbbl - minimum_reserve_mmbbl
        days_until_breach = usable_reserve / daily_shortfall_mmbbl

        base_date = start_date or datetime.now()

        trigger_date = base_date + timedelta(days = math.ceil(days_until_breach))

        return {
            "days_until_breach": round(days_until_breach,2),
            "replenishment_trigger_date": trigger_date.strftime('%Y-%m-%d')
        }



    #testing

if __name__ == "__main__":
    tracker = SPRTracker()
    result = tracker.calculate_replenishment_window(
        current_reserve_mmbbl=740.0,
        daily_shortfall_mmbbl=2.5,
        minimum_reserve_mmbbl=90.0
    )
    print(result)
    # Expected: days_until_breach = 260.0, trigger date = ~April 2027
