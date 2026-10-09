
"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles, Leaf, Sun, Camera, CheckCircle2, RotateCcw } from "lucide-react";

type Screen = "home" | "discover" | "review" | "adventure";
type Plant = { name: string; area: string; confidence: number; evidence: string; confirmed: boolean };
type Quest = {
  title: string;
  type: string;
  duration_minutes: number;
  difficulty: number;
  story: string;
  instructions: string[];
  verification: string;
  safety_notes: string[];
};
const API = "http://127.0.0.1:8000";
const leaves = Array.from({ length: 16 }, (_, i) => ({ id: i, left: `${35 + ((i * 19) % 60)}%`, delay: i * -1.7, duration: 7 + (i % 5) }));
const flowers = Array.from({ length: 36 }, (_, i) => ({ id: i, left: `${(i * 37) % 100}%`, bottom: `${(i * 13) % 24}%`, color: ["pink", "yellow", "purple", "white", "orange"][i % 5], size: 10 + (i % 4) * 3 }));

export default function Home() {
  const [screen, setScreen] = useState<Screen>("home");
  const [quest, setQuest] = useState<Quest | null>(null);
  const [plants, setPlants] = useState<Plant[]>([]);
  const [photo, setPhoto] = useState<File | null>(null);
  const [location, setLocation] = useState("home_garden");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState<boolean | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function analyzeGarden() {
    if (!photo) {
      setError("Choose a garden photo first.");
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const form = new FormData();
      form.append("photo", photo);
      const response = await fetch(`${API}/api/garden/analyze`, { method: "POST", body: form });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Garden analysis failed.");
      setPlants((data.plants || []).map((plant: Omit<Plant, "confirmed">) => ({ ...plant, confirmed: true })));
      if (!data.plants?.length) {
        setError("We couldn't identify any plants confidently. Try a clearer photo with visible leaves or flowers.");
        return;
      }
      setScreen("review");
    } catch (e) {
      setError(e instanceof Error ? e.message : "We couldn't analyze that photo. Check that the API is running.");
    } finally {
      setLoading(false);
    }
  }

  function updatePlant(index: number, changes: Partial<Plant>) {
    setPlants(current => current.map((plant, i) => i === index ? { ...plant, ...changes } : plant));
  }

  async function saveGarden() {
    const confirmed = plants.filter(plant => plant.confirmed && plant.name.trim());
    if (!confirmed.length) {
      setError("Confirm at least one plant before saving your garden.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const response = await fetch(`${API}/api/garden/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location, plants: confirmed.map(plant => plant.name.trim()) })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "The garden profile could not be saved.");
      setMessage(`${confirmed.length} plants saved to your garden memory.`);
      setScreen("home");
    } catch (e) {
      setError(e instanceof Error ? e.message : "We couldn't save your garden.");
    } finally {
      setSaving(false);
    }
  }

  async function beginAdventure() {
    setScreen("adventure");
    setLoading(true);
    setError("");
    setMessage("");
    setSaved(null);
    try {
      const response = await fetch(`${API}/api/quest`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "The garden couldn't prepare a quest. Please try again.");
      setQuest(data.quest);
      if (data.garden_source === "simulator") {
        setMessage("You're exploring the sample garden. Discover your own garden to personalize future quests.");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "We couldn't reach the garden. Check that the Python API is running.");
    } finally {
      setLoading(false);
    }
  }

  async function saveOutcome(completed: boolean) {
    if (!quest) return;
    setSaving(true);
    setError("");
    try {
      const response = await fetch(`${API}/api/quest/complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quest_type: quest.type, title: quest.title, difficulty: quest.difficulty, completed })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "The outcome could not be saved.");
      setSaved(completed);
      setMessage(data.message);
    } catch (e) {
      setError(e instanceof Error ? e.message : "We couldn't save your quest outcome.");
    } finally {
      setSaving(false);
    }
  }

  function goHome() {
    setScreen("home");
    setQuest(null);
    setSaved(null);
    setError("");
    setMessage("");
  }

  return (
    <main className="garden-world">
      <div className="sky-glow" />
      <div className="sun"><Sun size={32} /></div>
      <div className="cloud cloud-one"><i /><i /><i /></div>
      <div className="cloud cloud-two"><i /><i /><i /></div>
      <div className="cloud cloud-three"><i /><i /><i /></div>
      <div className="hill hill-back" />
      <div className="hill hill-middle" />
      <div className="hill hill-front" />
      <div className="tree" aria-hidden="true">
        <div className="tree-trunk" /><div className="tree-branch branch-left" /><div className="tree-branch branch-right" />
        <div className="canopy canopy-one" /><div className="canopy canopy-two" /><div className="canopy canopy-three" />
        <div className="canopy canopy-four" /><div className="canopy canopy-five" /><div className="canopy canopy-six" />
      </div>
      <div className="falling-leaves" aria-hidden="true">
        {leaves.map(leaf => <motion.span key={leaf.id} className="falling-leaf" style={{ left: leaf.left }}
          initial={{ y: -40, opacity: 0 }}
          animate={{ y: ["0vh", "85vh"], x: [0, 30, -25, 40, 0], rotate: [0, 140, 300, 480], opacity: [0, 1, 1, 0] }}
          transition={{ duration: leaf.duration, delay: leaf.delay, repeat: Infinity, ease: "linear" }} />)}
      </div>
      <div className="garden-path" />
      <div className="garden-grass" />
      <div className="flower-field" aria-hidden="true">
        {flowers.map(flower => <span key={flower.id} className={`garden-flower flower-${flower.color}`}
          style={{ left: flower.left, bottom: flower.bottom, width: flower.size, height: flower.size }}><i /></span>)}
      </div>

      <header className="garden-header">
        <div className="brand-symbol"><Leaf size={21} /></div>
        <div className="brand-caption">A LITTLE WORLD OF WONDER</div>
        <div className="header-sparkle"><Sparkles size={22} /></div>
      </header>

      <section className="story-content">
        <motion.div key={screen} className="title-wrap"
          initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <div className="eyebrow"><span className="eyebrow-dot" />
            {screen === "home" ? "A NEW ADVENTURE IS GROWING" : screen === "discover" ? "LET'S MEET YOUR GARDEN" : screen === "review" ? "MEET YOUR PLANTS" : "YOUR LITTLE WORLD AWAITS"}
            <span className="eyebrow-dot" />
          </div>
          <h1 className="hero-title">Empress<span>of Dirt</span></h1>
          <div className="title-decoration"><span /><Leaf size={18} /><span /></div>

          {screen === "home" && (
            <>
              <p className="hero-description">A tiny garden. A thousand discoveries.<br />A whole world waiting for you.</p>
              {message && <p className="verification-note">{message}</p>}
              <div className="home-actions">
                <button className="adventure-button" onClick={() => { setScreen("discover"); setError(""); }}>
                  <Camera size={19} /> <span>Discover your garden</span><ArrowRight size={19} />
                </button>
                <button className="adventure-button" onClick={beginAdventure}>
                  <span>Begin your adventure</span><ArrowRight size={19} />
                </button>
              </div>
              <div className="hero-footnote"><Sparkles size={14} /> BIG ADVENTURES GROW OUTSIDE <Sparkles size={14} /></div>
            </>
          )}

          {screen === "discover" && (
            <div className="quest-panel">
              <h2>What grows in your world?</h2>
              <p>Choose a garden photo. Gemma will suggest plants based on visible features. You'll review every suggestion before saving.</p>
              <label className="photo-picker">
                <Camera size={28} />
                <span>{photo ? photo.name : "Choose a garden photo"}</span>
                <input type="file" accept="image/png,image/jpeg,image/webp" onChange={e => { setPhoto(e.target.files?.[0] || null); setError(""); }} />
              </label>
              <label className="garden-location-label">
                Garden name or area
                <input value={location} onChange={e => setLocation(e.target.value)} maxLength={80} placeholder="e.g. Backyard" />
              </label>
              <button className="adventure-button" disabled={loading || !photo} onClick={analyzeGarden}>
                {loading ? "Looking closely..." : "Discover plants"} <ArrowRight size={18} />
              </button>
              {loading && <p>Looking at leaf shapes, flowers, and other visible clues…</p>}
              {error && <p className="api-error">{error}</p>}
              <button className="back-link" onClick={goHome}>← Back to the garden</button>
            </div>
          )}

          {screen === "review" && (
            <div className="quest-panel">
              <h2>Are these your plants?</h2>
              <p>Gemma's suggestions are guesses, not facts. Confirm the ones you recognize, edit a name, or leave a plant unchecked.</p>
              {plants.map((plant, index) => (
                <div className="plant-review" key={`${plant.area}-${index}`}>
                  <label className="plant-check">
                    <input type="checkbox" checked={plant.confirmed} onChange={e => updatePlant(index, { confirmed: e.target.checked })} />
                    <span>{plant.name}</span>
                  </label>
                  <label className="plant-name-label">Plant name
                    <input value={plant.name} onChange={e => updatePlant(index, { name: e.target.value })} maxLength={100} />
                  </label>
                  <div className="plant-meta"><span>{plant.area}</span><span>{Math.round(plant.confidence * 100)}% model confidence</span></div>
                  <p className="plant-evidence">{plant.evidence || "No visual evidence supplied."}</p>
                </div>
              ))}
              <button className="adventure-button" disabled={saving || !plants.some(p => p.confirmed && p.name.trim())} onClick={saveGarden}>
                {saving ? "Saving your garden..." : "Remember my garden"} <CheckCircle2 size={18} />
              </button>
              {error && <p className="api-error">{error}</p>}
              <button className="back-link" onClick={() => { setScreen("discover"); setError(""); }}><RotateCcw size={14} /> Try another photo</button>
            </div>
          )}

          {screen === "adventure" && (
            <div className="quest-panel">
              {loading ? <div className="quest-status"><Sparkles size={30} /><h2>Something is growing...</h2><p>The garden is preparing your next adventure.</p></div>
              : error && !quest ? <div className="quest-status"><h2>Let's try again!</h2><p>{error}</p><button className="adventure-button" onClick={beginAdventure}>Try again <ArrowRight size={18} /></button></div>
              : quest ? <>
                <span className="quest-label"><Leaf size={15} /> YOUR GARDEN QUEST</span>
                <h2>{quest.title}</h2><p>{quest.story}</p>
                <div className="quest-meta"><span>{quest.duration_minutes} MINUTES</span><span>LEVEL {quest.difficulty}</span><span>{quest.type.toUpperCase()}</span></div>
                <div className="quest-instructions"><h3>Your mission</h3><ol>{quest.instructions.map((instruction, index) => <li key={index}>{instruction}</li>)}</ol></div>
                <div className="quest-safety"><strong>A little garden wisdom</strong><ul>{quest.safety_notes.map((note, index) => <li key={index}>{note}</li>)}</ul></div>
                {saved === null ? <div className="quest-actions">
                  <p className="verification-note"><strong>How to finish:</strong> {quest.verification}</p>
                  <button className="adventure-button" disabled={saving} onClick={() => saveOutcome(true)}>{saving ? "Saving..." : "I completed my quest"} <ArrowRight size={18} /></button>
                  <button className="back-link" disabled={saving} onClick={() => saveOutcome(false)}>Not this time</button>
                </div> : <div className="quest-success">
                  <Sparkles size={24} /><strong>{saved ? "Wonderful exploring!" : "Every adventure takes practice!"}</strong>
                  <span>{message} Your next quest can adapt to your history.</span>
                  <button className="adventure-button" onClick={beginAdventure}>Discover another quest <ArrowRight size={18} /></button>
                </div>}
                {error && <p className="api-error">{error}</p>}
              </> : null}
              <button className="back-link" onClick={goHome}>← Back to the garden</button>
            </div>
          )}
        </motion.div>
      </section>
      <footer className="garden-footer"><span>GROW CURIOUS</span><i /><span>WANDER GENTLY</span><i /><span>DISCOVER MAGIC</span></footer>
    </main>
  );
}