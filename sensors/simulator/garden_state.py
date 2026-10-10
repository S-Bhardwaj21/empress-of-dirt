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

def get_simulated_garden_scenario(scenario: str) -> GardenState:
    scenarios = {
        "healthy_garden": {
            "soil_moisture": 42,
            "temperature": 26.0,
            "humidity": 64,
            "weather": "clear",
            "time_of_day": "morning"
        },
        "dry_soil": {
            "soil_moisture": 12,
            "temperature": 30.0,
            "humidity": 35,
            "weather": "clear",
            "time_of_day": "morning"
        },
        "hot_afternoon": {
            "soil_moisture": 28,
            "temperature": 39.0,
            "humidity": 25,
            "weather": "sunny",
            "time_of_day": "afternoon"
        },
        "low_light": {
            "soil_moisture": 42,
            "temperature": 24.0,
            "humidity": 60,
            "weather": "cloudy",
            "time_of_day": "evening"
        }
    }
    if scenario not in scenarios:
        raise ValueError(
            f"Unknown scenario '{scenario}'. Choose one of: {', '.join(scenarios)}"
        )
    garden = get_simulated_garden()
    for key, value in scenarios[scenario].items():
        setattr(garden, key, value)
    return garden