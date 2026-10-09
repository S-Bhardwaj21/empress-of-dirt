from dataclasses import dataclass, field
from typing import List

@dataclass
class GardenState:
    location: str
    soil_moisture: int
    temperature: float
    humidity: int
    weather: str
    time_of_day: str
    plants: List[str] = field(default_factory=list)
    recent_discoveries: List[str] = field(default_factory=list)
    unexplored_areas: List[str] = field(default_factory=list)

def get_simulated_garden() -> GardenState:
    return GardenState(
        location="nani_garden",
        soil_moisture=42,
        temperature=29.5,
        humidity=64,
        weather="clear",
        time_of_day="morning",
        plants=["tulsi", "rose", "hibiscus", "money_plant", "mint"],
        recent_discoveries=[],
        unexplored_areas=[
            "back_garden_corner",
            "behind_rose_bush",
            "near_water_tap"
        ]
    )