
import json
import os
import re
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from sensors.simulator.garden_state import get_simulated_garden
from memory.database.schema import initialize_database
from memory.database.connection import get_connection
from memory.repositories.sqlite_memory import SQLiteMemoryRepository
from memory.models.quest_record import QuestRecord
from quests.quest_engine.engine import QuestEngine
from quests.quest_types.types import QuestType
from verification.rules.quest_validator import validate_quest
from main import build_fallback_quest

app = FastAPI(title="Empress of Dirt API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_database()

connection = get_connection()
connection.execute("""
    CREATE TABLE IF NOT EXISTS quest_impressions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quest_type TEXT NOT NULL,
        title TEXT NOT NULL,
        shown_at TEXT NOT NULL
    )
""")
connection.commit()
connection.close()

class CompletionRequest(BaseModel):
    quest_type: str
    title: str
    difficulty: int
    completed: bool

class GardenProfileRequest(BaseModel):
    location: str = "home_garden"
    plants: list[str] = Field(min_length=1, max_length=50)

def get_saved_garden_profile():
    connection = get_connection()
    row = connection.execute(
        "SELECT location, plants_json FROM garden_profile WHERE id = 1"
    ).fetchone()
    connection.close()
    if not row:
        return None
    return {"location": row[0], "plants": json.loads(row[1])}

def get_garden_for_quests():
    garden = get_simulated_garden()
    profile = get_saved_garden_profile()
    if profile:
        garden.location = profile["location"]
        garden.plants = profile["plants"]
    return garden

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Empress of Dirt"}

@app.post("/api/garden/analyze")
async def analyze_garden(photo: UploadFile = File(...)):
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if photo.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Upload a JPG, PNG, or WEBP garden photo.")
    image_bytes = await photo.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Please use an image smaller than 10 MB.")
    api_key = os.getenv("GEMMA_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Garden vision is not configured. Set the GEMMA_API_KEY environment variable."
        )
    
    prompt = """
You are a cautious plant-observation assistant for a child-friendly garden app.
Analyze the uploaded garden photograph and identify plants using VISUAL BOTANICAL FEATURES ONLY.

CRITICAL ANTI-LABEL RULES:
- Do NOT read, use, or rely on text labels, captions, arrows, watermarks, signs, or written plant names in the image.
- Treat all visible text as irrelevant to plant identification.
- Never identify a plant merely because a label points to it.
- Base each identification on visible morphology: leaf shape and arrangement, leaf edges, stem structure, flower shape and color, growth habit, and visible fruit.
- Explain the actual visual features supporting each proposed identification. Do not say "the label says" or refer to text as evidence.
- If the image does not show enough detail to distinguish a species, use a broader group such as "succulent" or "mint-family herb", or state that the plant is unidentified.
- Do not invent details that cannot be seen. Do not force a species-level identification.
- Use conservative confidence scores. A plausible guess is not certainty; do not assign 1.0 confidence.
- Multiple views of the same plant should not be counted as different plants.
- Identify only plants visibly present in the photograph.
- Do not infer soil moisture, plant health, species-specific care needs, or hidden objects from the photo.

Return ONLY valid JSON with this structure:
{
  "plants": [
    {
      "name": "likely common name or broader plant group",
      "area": "short visual location in the image",
      "confidence": 0.0,
      "evidence": "specific visible botanical features supporting this identification"
    }
  ],
  "observations": ["short observations of visible garden features"]
}

Confidence must be a number from 0.0 to 1.0.
If no plant can be identified from visual features, return an empty plants array.
"""
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemma-4-26b-a4b-it",
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=photo.content_type
                ),
                prompt
            ]
        )
        raw_text = response.text or ""
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            raise ValueError("The model did not return JSON.")
        result = json.loads(match.group(0))
        candidates = []
        for item in result.get("plants", []):
            name = str(item.get("name", "")).strip()
            if not name:
                continue
            try:
                confidence = max(0.0, min(1.0, float(item.get("confidence", 0.0))))
            except (TypeError, ValueError):
                confidence = 0.0
            candidates.append({
                "name": name,
                "area": str(item.get("area", "garden")),
                "confidence": confidence,
                "evidence": str(item.get("evidence", ""))
            })
        return {
            "plants": candidates,
            "observations": result.get("observations", []),
            "requires_confirmation": True
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Garden photo analysis failed: {str(exc)[:250]}"
        )

@app.get("/api/garden/profile")
def get_garden_profile():
    profile = get_saved_garden_profile()
    return {"configured": profile is not None, "profile": profile}

@app.post("/api/garden/profile")
def save_garden_profile(request: GardenProfileRequest):
    plants = list(dict.fromkeys(
        plant.strip() for plant in request.plants if plant.strip()
    ))
    if not plants:
        raise HTTPException(status_code=400, detail="Confirm at least one plant.")
    location = request.location.strip() or "home_garden"
    connection = get_connection()
    connection.execute("""
        INSERT INTO garden_profile (id, location, plants_json, updated_at)
        VALUES (1, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            location = excluded.location,
            plants_json = excluded.plants_json,
            updated_at = excluded.updated_at
    """, (location, json.dumps(plants), datetime.now().isoformat()))
    connection.commit()
    connection.close()
    return {
        "saved": True,
        "profile": {"location": location, "plants": plants},
        "message": "Your confirmed garden profile was saved locally."
    }

@app.post("/api/quest")
def generate_quest():
    memory = SQLiteMemoryRepository()
    garden = get_garden_for_quests()
    engine = QuestEngine(memory)
    plan = engine.create_plan(garden)
    connection = get_connection()
    recent_rows = connection.execute(
        "SELECT title FROM quest_impressions ORDER BY id DESC LIMIT 12"
    ).fetchall()
    recent_titles = [row[0] for row in recent_rows]
    connection.close()
    quest = build_fallback_quest(plan, recent_titles)
    is_valid, errors = validate_quest(quest, plan)
    if not is_valid:
        raise HTTPException(status_code=500, detail={"errors": errors})
    connection = get_connection()
    connection.execute(
        "INSERT INTO quest_impressions (quest_type, title, shown_at) VALUES (?, ?, ?)",
        (quest["type"], quest["title"], datetime.now().isoformat())
    )
    connection.commit()
    connection.close()
    return {
        "quest": quest,
        "target_area": plan.target_area,
        "target_plant": plan.target_plant,
        "reason": plan.reason,
        "garden_source": "confirmed_profile" if get_saved_garden_profile() else "simulator"
    }

@app.post("/api/quest/complete")
def complete_quest(request: CompletionRequest):
    try:
        quest_type = QuestType(request.quest_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Unknown quest type.")
    if not 1 <= request.difficulty <= 5:
        raise HTTPException(status_code=400, detail="Invalid difficulty.")
    memory = SQLiteMemoryRepository()
    memory.add_quest(
        QuestRecord(
            quest_type=quest_type,
            title=request.title,
            difficulty=request.difficulty,
            completed=request.completed,
            completed_at=datetime.now(),
        )
    )
    return {
        "saved": True,
        "completed": request.completed,
        "message": "Quest outcome saved to local memory."
    }