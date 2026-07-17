"""Strategic Petroleum Reserve (SPR) tracking utilities."""

from dataclasses import dataclass


@dataclass
class SPRTracker:
    starting_reserve_mmbbl: float = 740.0
    drawdown_mmbbl_per_day: float = 1.0

    def days_remaining(self, current_reserve_mmbbl: float | None = None) -> float:
        reserve = self.starting_reserve_mmbbl if current_reserve_mmbbl is None else current_reserve_mmbbl
        if self.drawdown_mmbbl_per_day <= 0:
            return float("inf")
        return max(reserve / self.drawdown_mmbbl_per_day, 0.0)
