#Hey Sudarshan, extend the existing SPRTracker dataclass in agents/spr_agent.py by adding this exact method. Don't touch days_remaining(), just add this below it so we can calculate when we hit the minimum threshold.


from datetime import datetime

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