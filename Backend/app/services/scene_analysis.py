"""
Crime Scene Analysis Service
Uses Groq (LLaMA) as the primary extraction engine — Gemini kept as optional upgrade.
Rule-based keyword fallback always returns clean, usable values (no 'See transcript' junk).
"""
import json
import re
from typing import List, Dict, Any, Optional
from app.config import settings

# ── Groq client (primary — always available) ──────────────────────────────────
_groq = None
try:
    from groq import Groq
    if settings.GROQ_API_KEY:
        _groq = Groq(api_key=settings.GROQ_API_KEY)
except Exception as e:
    print(f"[ANALYSIS] Groq init failed: {e}")

# ── Gemini client — new google-genai SDK ────────────────────────────────────
_gemini = None
GEMINI_MODEL = "gemini-2.5-flash-lite"
try:
    from google import genai as _genai_sdk
    if settings.GEMINI_API_KEY:
        _gemini = _genai_sdk.Client(api_key=settings.GEMINI_API_KEY)
        print(f"[ANALYSIS] Gemini client ready ({GEMINI_MODEL})")
except Exception as e:
    print(f"[ANALYSIS] Gemini init failed: {e}")

# Keep old name for compat
_model = None  # legacy, unused


# ── Extraction via Groq ───────────────────────────────────────────────────────
EXTRACTION_SYSTEM = """You are a forensic data extraction specialist.
Extract crime scene information from the conversation transcript below into JSON.
Return ONLY valid JSON, no markdown, no explanation.

Schema:
{
  "crime_type": "specific crime type (e.g. homicide, robbery)",
  "time_of_incident": "time string",
  "location": {
    "description": "brief location description",
    "type": "indoor or outdoor",
    "room_type": "specific room (kitchen, bedroom, alley, etc.)",
    "environment": "urban/suburban/rural"
  },
  "victims": [{"name": "name or Unknown", "position": "where found", "condition": "condition"}],
  "suspects": [{"description": "appearance/description", "behavior": "behavior noted"}],
  "witnesses": [{"description": "who", "observation": "what they saw"}],
  "evidence": [{"item": "specific evidence item name", "location_in_scene": "where", "significance": "why important"}],
  "entry_exit": {"entry": "how entered", "exit": "how exited"},
  "environment": {"lighting": "lighting description", "conditions": "other conditions"},
  "security": {"cameras": false, "alarms": false, "details": "security details"},
  "summary": "2-sentence scene summary"
}

Rules:
- If info is not mentioned, use reasonable forensic defaults (not "See transcript" or "Unknown")
- For room_type: if apartment/house mentioned but no specific room, use "apartment"
- For evidence: extract specific items like "knife", "blood stain", "broken glass" from text
- For crime_type: extract from context (murder/homicide/robbery/assault)
"""

CORRELATION_SYSTEM = """You are a forensic analyst building a crime scene relationship matrix.
Given the scene data, return ONLY valid JSON with entities and their correlations.

Schema:
{
  "entities": [
    {"id": "e1", "name": "entity name", "type": "suspect|victim|evidence|location|witness|timeline", "details": "brief detail"}
  ],
  "correlations": [
    {"from": "e1", "to": "e2", "label": "relationship", "strength": 0.8}
  ],
  "timeline": [
    {"time": "time string", "event": "what happened", "entities_involved": ["e1"]}
  ],
  "risk_factors": ["risk 1", "risk 2"],
  "scene_summary": "2-sentence summary"
}

Create at least 5 entities and 6 correlations. Be specific and forensically accurate.
"""


def _call_gemini_text(system: str, user: str) -> Optional[str]:
    """Calls gemini-2.5-flash-lite and returns raw text."""
    if not _gemini:
        return None
    try:
        prompt = f"{system}\n\n{user}"
        r = _gemini.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return r.text.strip()
    except Exception as e:
        print(f"[ANALYSIS] Gemini call failed: {e.__class__.__name__}: {str(e)[:80]}")
        return None


def _call_gemini_json(system: str, user: str) -> Optional[Dict]:
    """Calls Gemini and parses JSON from the response."""
    text = _call_gemini_text(system, user)
    if not text:
        return None
    try:
        clean = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
        return json.loads(clean)
    except json.JSONDecodeError:
        return None


def _call_groq_json(system: str, user_content: str) -> Optional[Dict]:
    """Calls Groq (LLaMA 70b) and parses JSON response. Fallback after Gemini."""
    if not _groq:
        return None
    try:
        resp = _groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user_content},
            ],
            max_tokens=1500,
            temperature=0.1,
        )
        text = resp.choices[0].message.content.strip()
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[ANALYSIS] Groq JSON parse error: {e}")
        return None
    except Exception as e:
        print(f"[ANALYSIS] Groq call error: {e}")
        return None


def extract_scene_data(message_history: List[Dict]) -> Dict:
    """
    Extracts structured scene data from conversation history.
    Priority: Gemini 2.5 Flash-Lite → Groq LLaMA 70b → keyword fallback
    """
    transcript = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in message_history
    )
    user_prompt = f"TRANSCRIPT:\n{transcript}"

    # Try Gemini first (best quality)
    result = _call_gemini_json(EXTRACTION_SYSTEM, user_prompt)
    if result:
        print("[ANALYSIS] Gemini extraction OK")
        return result

    # Groq fallback
    result = _call_groq_json(EXTRACTION_SYSTEM, user_prompt)
    if result:
        print("[ANALYSIS] Groq extraction OK (Gemini fallback)")
        return result

    # Rule-based fallback
    print("[ANALYSIS] Using keyword fallback")
    return _keyword_extract(transcript)


def build_correlation_data(scene_data: Dict) -> Dict:
    """Builds correlation matrix. Priority: Gemini → Groq → rule-based."""
    scene_json = json.dumps(scene_data, indent=2)
    user_prompt = f"SCENE DATA:\n{scene_json}"

    result = _call_gemini_json(CORRELATION_SYSTEM, user_prompt)
    if result:
        print("[ANALYSIS] Gemini correlation OK")
        return result

    result = _call_groq_json(CORRELATION_SYSTEM, user_prompt)
    if result:
        print("[ANALYSIS] Groq correlation OK (Gemini fallback)")
        return result

    return _build_fallback_correlation(scene_data)


# ── Improved keyword fallback — NO "See transcript" values ────────────────────
def _keyword_extract(transcript: str) -> Dict:
    """Keyword-based extraction that always returns clean, usable values."""
    t = transcript.lower()

    crime_type = _find_keyword(t,
        ["murder", "homicide", "stabbing", "shooting", "robbery", "assault", "burglary", "theft", "rape"],
        "homicide"  # Safe forensic default
    )

    room_type = _find_keyword(t,
        ["kitchen", "bedroom", "living room", "bathroom", "office", "garage",
         "alley", "park", "street", "hallway", "stairwell", "basement"],
        "apartment"
    )

    loc_type = "indoor" if any(w in t for w in
        ["room", "apartment", "flat", "house", "building", "inside", "indoor", "floor", "kitchen", "bedroom"]
    ) else "outdoor"

    time_str = _find_pattern(transcript, r"\b\d{1,2}:\d{2}\s*(?:am|pm)?\b|\b\d{1,2}\s*(?:am|pm)\b", "late night")

    # Extract specific evidence items from text
    evidence_keywords = [
        "knife", "gun", "pistol", "blood", "stain", "fingerprint", "footprint",
        "phone", "wallet", "rope", "glass", "bottle", "bag", "shell casing",
        "hair", "fiber", "tool", "wire", "tape"
    ]
    found_evidence = [w for w in evidence_keywords if w in t][:4]
    if not found_evidence:
        found_evidence = ["blood stain", "trace evidence"]

    return {
        "crime_type": crime_type,
        "time_of_incident": time_str,
        "location": {
            "description": f"{room_type} crime scene",
            "type": loc_type,
            "room_type": room_type,
            "environment": "urban residential",
        },
        "victims": [{"name": "Unknown", "position": f"found in {room_type}", "condition": "deceased"}],
        "suspects": [{"description": "Unknown suspect", "behavior": "fled scene"}],
        "witnesses": [],
        "evidence": [{"item": item, "location_in_scene": room_type, "significance": "key evidence"} for item in found_evidence],
        "entry_exit": {"entry": "main entrance", "exit": "unknown"},
        "environment": {"lighting": "artificial lighting", "conditions": "indoor"},
        "security": {"cameras": False, "alarms": False, "details": "none confirmed"},
        "summary": f"{crime_type.capitalize()} scene in {room_type}. Investigation ongoing.",
    }


def _find_keyword(text: str, keywords: List[str], default: str) -> str:
    for kw in keywords:
        if kw in text:
            return kw
    return default


def _find_pattern(text: str, pattern: str, default: str) -> str:
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(0) if m else default


# ── Rule-based correlation fallback ──────────────────────────────────────────
def _build_fallback_correlation(scene_data: Dict) -> Dict:
    entities, correlations, eid = [], [], 0

    def add(name, typ, details=""):
        nonlocal eid
        eid += 1
        _id = f"{typ[0]}{eid}"
        entities.append({"id": _id, "name": name, "type": typ, "details": details})
        return _id

    room = scene_data.get("location", {}).get("room_type", "scene")
    loc_id   = add(f"{room} crime scene", "location", room)
    crime_id = add(scene_data.get("crime_type", "Incident"), "timeline",
                   scene_data.get("time_of_incident", "unknown time"))

    victim_ids = []
    for v in (scene_data.get("victims") or [{"name": "Victim", "position": "", "condition": ""}]):
        vid = add(v.get("name", "Victim"), "victim", v.get("condition", ""))
        victim_ids.append(vid)
        correlations.append({"from": vid, "to": loc_id, "label": "Found at", "strength": 1.0})
        correlations.append({"from": crime_id, "to": vid, "label": "Target of", "strength": 0.9})

    suspect_ids = []
    for s in (scene_data.get("suspects") or [{"description": "Unknown suspect", "behavior": ""}]):
        sid = add(s.get("description", "Suspect")[:28], "suspect", s.get("behavior", ""))
        suspect_ids.append(sid)
        correlations.append({"from": sid, "to": loc_id, "label": "Present at", "strength": 0.8})
        for vid in victim_ids:
            correlations.append({"from": sid, "to": vid, "label": "Attacked", "strength": 0.85})

    for ev in (scene_data.get("evidence") or [{"item": "Evidence", "location_in_scene": "", "significance": ""}])[:4]:
        item = ev.get("item", "Evidence")
        if item in ("See transcript", "", "Unknown"):
            item = "Physical evidence"
        evid = add(item, "evidence", ev.get("significance", ""))
        correlations.append({"from": evid, "to": loc_id, "label": "Found at", "strength": 0.9})
        for sid in suspect_ids:
            correlations.append({"from": evid, "to": sid, "label": "Links to", "strength": 0.75})

    return {
        "entities": entities,
        "correlations": correlations,
        "timeline": [
            {"time": scene_data.get("time_of_incident", "Unknown"), "event": "Incident occurred", "entities_involved": [crime_id]},
            {"time": "After incident", "event": "Scene secured", "entities_involved": [loc_id]},
        ],
        "risk_factors": ["Evidence contamination risk", "Witness safety concern", "Suspect still at large"],
        "scene_summary": scene_data.get("summary", "Crime scene under forensic investigation."),
    }


# ── Scene image prompt — short and clean ─────────────────────────────────────
def build_scene_image_prompt(scene_data: Dict) -> str:
    """Builds a short, clean Pollinations prompt. Always under 200 chars."""
    loc       = scene_data.get("location", {})
    crime     = scene_data.get("crime_type", "homicide")
    room      = loc.get("room_type", "apartment")
    loc_type  = loc.get("type", "indoor")

    # Get first real evidence item (skip garbage values)
    ev_item = ""
    for ev in (scene_data.get("evidence") or []):
        item = ev.get("item", "")
        if item and item not in ("See transcript", "Unknown", "Evidence", "Physical evidence"):
            ev_item = item
            break

    if loc_type == "indoor":
        parts = [
            f"crime scene investigation photo, {room} interior",
            ev_item if ev_item else "",
            "yellow evidence placards on floor, police tape, no people, photorealistic, dramatic forensic lighting"
        ]
    else:
        outdoor = loc.get("environment", "urban street")
        parts = [
            f"crime scene investigation photo, outdoor {outdoor}",
            "yellow evidence placards, police tape perimeter, no people, photorealistic"
        ]

    prompt = ", ".join(p for p in parts if p)
    return prompt[:200]  # Hard cap
