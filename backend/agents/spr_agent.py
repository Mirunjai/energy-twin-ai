from datetime import datetime, timedelta
from dataclasses import dataclass
import math

@dataclass
class SPRTracker:
    starting_reserve_mmbbl: float = 45.0
    drawdown_mmbbl_per_day: float = 1.0

    def days_remaining(self, current_reserve_mmbbl: float | None = None) -> float:
        reserve = self.starting_reserve_mmbbl if current_reserve_mmbbl is None else current_reserve_mmbbl
        if self.drawdown_mmbbl_per_day <= 0:
            return float("inf")
        return max(reserve / self.drawdown_mmbbl_per_day, 0.0)

    def calculate_replenishment_window(
        self,
        daily_shortfall_mmbbl: float,
        current_reserve_mmbbl: float | None = None,
        minimum_reserve_mmbbl: float = 9.0,  # ~10 days of baseline cover
        start_date: datetime | None = None
    ) -> dict:
        """
        Given the current reserve and the daily shortfall projected by the simulation,
        calculate the exact date the reserve will breach the minimum threshold.
        """
        current_reserve = self.starting_reserve_mmbbl if current_reserve_mmbbl is None else current_reserve_mmbbl
        
        if daily_shortfall_mmbbl <= 0:
            return {
                "days_until_breach": float('inf'),
                "replenishment_trigger_date": "Never"
            }
    
        if current_reserve <= minimum_reserve_mmbbl:
            return {
                "days_until_breach": 0.0,
                "replenishment_trigger_date": (start_date or datetime.now()).strftime('%Y-%m-%d')
            }
    
        usable_reserve = current_reserve - minimum_reserve_mmbbl
        days_until_breach = usable_reserve / daily_shortfall_mmbbl

        base_date = start_date or datetime.now()
        trigger_date = base_date + timedelta(days=math.ceil(days_until_breach))

        return {
            "days_until_breach": round(days_until_breach, 2),
            "replenishment_trigger_date": trigger_date.strftime('%Y-%m-%d')
        }

if __name__ == "__main__":
    tracker = SPRTracker()
    # Testing with India-scale defaults
    result = tracker.calculate_replenishment_window(
        daily_shortfall_mmbbl=2.5
    )
    print(result)