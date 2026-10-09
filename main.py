import json
from datetime import datetime
from sensors.simulator.garden_state import get_simulated_garden
from memory.database.schema import initialize_database
from memory.repositories.sqlite_memory import SQLiteMemoryRepository
from memory.models.quest_record import QuestRecord
from quests.quest_engine.engine import QuestEngine
from verification.rules.quest_validator import validate_quest

QUEST_CATALOG = [
    {
        "type": "explorer",
        "title": "The Unnoticed Garden Corner",
        "story": "Every corner has a story. Today, you are investigating {area}.",
        "instructions": [
            "With an adult's permission, look around {area} without moving anything.",
            "Find one detail you have never noticed before, such as a leaf shape, a shadow, or a colour.",
            "Describe your discovery to an adult and explain why it caught your attention."
        ],
        "verification": "Share one new observation and explain where you found it."
    },
    {
        "type": "explorer",
        "title": "The Garden Sound Map",
        "story": "Become a sound explorer and discover what the garden sounds like.",
        "instructions": [
            "Stand safely in the garden and stay still for one quiet minute.",
            "Listen for three different sounds, such as birds, leaves, or distant traffic.",
            "Tell an adult which sound was loudest and which was hardest to notice."
        ],
        "verification": "Identify three sounds and compare two of them."
    },
    {
        "type": "explorer",
        "title": "The Shadow Tracker",
        "story": "Shadows change throughout the day. Find one and study its shape.",
        "instructions": [
            "With an adult, find a safe garden object casting a shadow.",
            "Look carefully at the shadow's outline and direction without moving the object.",
            "Describe its shape and predict whether it might look different later."
        ],
        "verification": "Describe a shadow and make one prediction about it."
    },
    {
        "type": "treasure",
        "title": "The Three-Colour Treasure Hunt",
        "story": "The garden is hiding a colour collection in plain sight.",
        "instructions": [
            "Find three different colours in the garden without picking anything.",
            "For each colour, point out the object or natural feature where you found it.",
            "Choose the most surprising colour and explain why it stood out."
        ],
        "verification": "Identify three colours and where each was found."
    },
    {
        "type": "treasure",
        "title": "The Pattern Collector",
        "story": "Repeating patterns are everywhere. Uncover two natural patterns.",
        "instructions": [
            "Look for a pattern in leaves, petals, bark, or stones.",
            "Find a second pattern somewhere else in the permitted garden area.",
            "Explain one way the patterns are alike and one way they differ."
        ],
        "verification": "Describe two patterns and compare them."
    },
    {
        "type": "treasure",
        "title": "The Tiny-Detail Challenge",
        "story": "The smallest details can be the most surprising discoveries.",
        "instructions": [
            "Choose a plant you can observe safely without touching it.",
            "Look closely at its visible details, such as leaf edges, veins, or petal shapes.",
            "Describe one tiny detail that you might have missed from farther away."
        ],
        "verification": "Describe one specific detail that was easier to notice up close."
    },
    {
        "type": "detective",
        "title": "The Leaf-Vein Detective",
        "story": "A leaf holds clues in its shape and branching veins.",
        "instructions": [
            "Find two fallen leaves or two leaves you can see without touching the plant.",
            "Compare their outlines, sizes, and visible vein patterns.",
            "Tell an adult one similarity and one difference."
        ],
        "verification": "Report one similarity and one difference between two leaves."
    },
    {
        "type": "detective",
        "title": "Who Visited This Flower?",
        "story": "Garden detectives look for clues without disturbing wildlife.",
        "instructions": [
            "From a comfortable distance, observe a flower or flowering plant.",
            "Look for visible clues of insect activity, but do not touch or approach insects.",
            "If you see no insects, report what you observed instead of guessing."
        ],
        "verification": "Share an observation and distinguish what you saw from what you inferred."
    },
    {
        "type": "detective",
        "title": "The Mystery of the Missing Sunlight",
        "story": "Some parts of a garden are sunny, while others stay shaded.",
        "instructions": [
            "With an adult, identify one sunny spot and one shaded spot.",
            "Compare the light reaching each spot without touching plants or equipment.",
            "Predict which spot might receive more direct sunlight later and explain why."
        ],
        "verification": "Compare two spots and give a reasoned prediction."
    },
    {
        "type": "scientist",
        "title": "The Soil-Moisture Scientist",
        "story": "Scientists use evidence rather than guesses to understand a garden.",
        "instructions": [
            "Ask an adult to show you the garden's soil-moisture reading, if available.",
            "Record the reading and whether the soil looks wet, damp, or dry.",
            "Share your observation with an adult; do not water anything unless asked."
        ],
        "verification": "Report the available reading and one observation. If no sensor is available, report that limitation."
    },
    {
        "type": "scientist",
        "title": "The Leaf Shape Lab",
        "story": "Today, you are investigating how different leaves can look.",
        "instructions": [
            "Choose two visible leaves on different plants.",
            "Compare their outlines, approximate sizes, and colours.",
            "Describe one difference and suggest a question you would investigate next."
        ],
        "verification": "Describe one observable difference and one follow-up question."
    },
    {
        "type": "scientist",
        "title": "The Weather Observer",
        "story": "Weather affects the garden. Collect a few careful observations.",
        "instructions": [
            "With an adult, observe the sky and whether the air feels still or breezy.",
            "Notice whether the garden has direct sunlight, shade, or cloud cover.",
            "Share two observations without touching plants or weather equipment."
        ],
        "verification": "Report two observations about the current weather."
    },
    {
        "type": "artist",
        "title": "The Secret Geometry",
        "story": "The garden is full of shapes. Become an artist who discovers them.",
        "instructions": [
            "Observe {plant} without touching or picking it.",
            "Find three shapes in its visible petals, leaves, or outline.",
            "Draw the shapes from memory on paper, then compare them with what you saw."
        ],
        "verification": "Show a drawing containing three observed shapes."
    },
    {
        "type": "artist",
        "title": "The Living Colour Palette",
        "story": "An artist's palette can come straight from the natural world.",
        "instructions": [
            "Find three colours in different parts of the garden.",
            "Arrange the colours in a drawing using pencils or crayons.",
            "Give your colour collection a name inspired by the garden."
        ],
        "verification": "Show a three-colour drawing and name the palette."
    },
    {
        "type": "artist",
        "title": "The Garden Storyboard",
        "story": "Turn one small garden observation into a tiny story.",
        "instructions": [
            "Choose a plant, shadow, or other garden feature to observe.",
            "Draw three simple panels showing what you noticed, what you wondered, and what you discovered.",
            "Tell your three-panel story to an adult."
        ],
        "verification": "Present three panels and explain the story they tell."
    },
    {
        "type": "rescue",
        "title": "The Garden Guardian Check",
        "story": "A guardian observes carefully and asks for help when something needs attention.",
        "instructions": [
            "From a safe distance, look for a plant that appears wilted or has damaged leaves.",
            "Describe what you actually see without pulling leaves or touching the plant.",
            "Tell an adult what you noticed and let them decide whether anything needs doing."
        ],
        "verification": "Report an observation to an adult, or explain that no obvious concern was found."
    },
    {
        "type": "rescue",
        "title": "The Safe Garden Scout",
        "story": "A good guardian helps keep the garden safe for people and wildlife.",
        "instructions": [
            "Look around the permitted garden area without touching anything.",
            "Notice a possible trip hazard or an object that an adult should check.",
            "Tell an adult about it and leave any cleanup or handling to them."
        ],
        "verification": "Identify a possible concern for an adult, or report that none was noticed."
    },
    {
        "type": "rescue",
        "title": "The Gentle Observer",
        "story": "Protecting a garden begins with noticing how to give living things space.",
        "instructions": [
            "Choose a spot where you can observe plants and wildlife from a safe distance.",
            "Look for ways to avoid disturbing leaves, insects, or other small animals.",
            "Tell an adult one action that helps you observe without causing disturbance."
        ],
        "verification": "Describe one way to observe the garden without disturbing living things."
    }
]

def build_fallback_quest(plan, recent_titles=None):
    recent_titles = set(recent_titles or [])
    matching = [
        item for item in QUEST_CATALOG
        if item["type"] == plan.quest_type.value
    ]
    available = [
        item for item in matching
        if item["title"] not in recent_titles
    ]
    if not available:
        available = matching
    if not available:
        raise ValueError(
            f"No quest templates exist for type: {plan.quest_type.value}"
        )

    template = available[0]
    area = plan.target_area.replace("_", " ")
    plant = plan.target_plant.replace("_", " ")

    title = template["title"]
    if title == "The Secret Geometry":
        title = f"The {plant.title()}'s Secret Geometry"

    return {
        "title": title,
        "type": template["type"],
        "duration_minutes": plan.duration_minutes,
        "difficulty": plan.difficulty,
        "story": template["story"].format(area=area, plant=plant),
        "instructions": [
            instruction.format(area=area, plant=plant)
            for instruction in template["instructions"]
        ],
        "verification": template["verification"],
        "safety_notes": [
            "Stay in the permitted garden area and follow an adult's instructions.",
            "Do not eat, pick, or damage plants.",
            "Observe insects and animals without touching them."
        ]
    }

def main():
    initialize_database()
    memory = SQLiteMemoryRepository()
    garden = get_simulated_garden()
    engine = QuestEngine(memory)
    plan = engine.create_plan(garden)
    quest = build_fallback_quest(plan)

    is_valid, errors = validate_quest(quest, plan)
    if not is_valid:
        print("QUEST VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return

    print("EMPRESS OF DIRT")
    print("=" * 40)
    print(json.dumps(quest, indent=2, ensure_ascii=False))

    answer = input("\nDid the child complete this quest? (y/n): ").strip().lower()
    memory.add_quest(QuestRecord(
        quest_type=plan.quest_type,
        title=quest["title"],
        difficulty=quest["difficulty"],
        completed=answer == "y",
        completed_at=datetime.now()
    ))

    print("\nQuest saved to local memory.")
    print("Outcome:", "Completed" if answer == "y" else "Not completed")
    print("Next quest difficulty will adapt based on this history.")

if __name__ == "__main__":
    main()

