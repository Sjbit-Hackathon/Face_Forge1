"""
Multi-Agent Council for Crime Scene Reconstruction
Three specialist AI agents — all powered by Groq's ultra-fast inference:

  🔵 GEMINI-PERSONA  — Scene Coordinator   (LLaMA 4 Scout 17b via Groq)
  🟢 GROQ            — Evidence Analyst    (LLaMA 3.3 70b via Groq)
  🟣 GROK-PERSONA    — Behavioral Profiler (LLaMA 3.1 8b-instant via Groq)

Gemini API is kept as an optional upgrade when daily quota resets.
"""

import json
from typing import List, Dict, Optional
from app.config import settings

# ── Agent definitions ─────────────────────────────────────────────────────────
AGENTS = {
    "gemini": {
        "name": "Det. Gemini",
        "role": "Scene Coordinator",
        "color": "#4285f4",
        "icon": "🔵",
        "specialty": "crime scene coordination and investigation strategy",
    },
    "groq": {
        "name": "Analyst Groq",
        "role": "Evidence Specialist",
        "color": "#22c55e",
        "icon": "🟢",
        "specialty": "physical evidence, forensic science, and crime scene trace analysis",
    },
    "grok": {
        "name": "Profiler Grok",
        "role": "Behavioral Profiler",
        "color": "#a855f7",
        "icon": "🟣",
        "specialty": "suspect psychology, behavioral patterns, and criminal profiling",
    },
}

# ── System prompts per agent ──────────────────────────────────────────────────
SYSTEM_PROMPTS = {
    "gemini": """You are Det. Gemini, Scene Coordinator in a forensic council.

CRITICAL RULES:
- First, briefly ACKNOWLEDGE what the person just said (show you understood it)
- Then give ONE key insight or observation about what it means for the investigation
- Finally ask exactly ONE short follow-up question (under 10 words)
- Total response: MAX 3 short sentences
- Do NOT list multiple questions
- Do NOT use bullet points
- Sound like a real detective having a conversation, not running an interrogation

When you have enough info (crime type, location, victim, evidence mentioned, time), write SCENE_COMPLETE on its own line then a closing statement.""",

    "groq": """You are Analyst Groq, Evidence Specialist in a forensic council.

CRITICAL RULES:
- Read what the witness just said carefully
- Make ONE forensic observation about the evidence implications of what they described
- Ask ONE short specific evidence question (under 8 words)
- Total response: MAX 2 short sentences
- No bullet points, no lists
- Sound like a forensic scientist, not a questionnaire""",

    "grok": """You are Profiler Grok, Behavioral Profiler in a forensic council.

CRITICAL RULES:
- Read what the witness just said and make ONE behavioral/psychological observation about it
- Ask ONE short profiling question (under 8 words)
- Total response: MAX 2 short sentences
- No bullet points, no lists
- Sound like a criminal psychologist, not an interviewer""",
}

# ── Gemini client (new SDK) ─────────────────────────────────────────────────────
_gemini_client = None
GEMINI_COUNCIL_MODEL = "gemini-2.5-flash-lite"  # new key, fresh quota
try:
    from google import genai as _genai_sdk
    if settings.GEMINI_API_KEY:
        _gemini_client = _genai_sdk.Client(api_key=settings.GEMINI_API_KEY)
        print(f"[COUNCIL] Gemini client ready ({GEMINI_COUNCIL_MODEL})")
except Exception as e:
    print(f"[COUNCIL] Gemini init failed: {e}")

# Legacy model ref (unused but kept to avoid NameError in any old callers)
_gemini_model = None

# ── Groq clients (all 3 agents) ─────────────────────────────────────────────────
_groq_client = None   # Evidence analyst  — LLaMA 3.3 70b
_gemini_groq = None   # Scene coordinator — LLaMA 4 Scout 17b
_grok_client = None   # Behavioral profiler — LLaMA 3.1 8b-instant
try:
    from groq import Groq
    if settings.GROQ_API_KEY:
        _groq_client  = Groq(api_key=settings.GROQ_API_KEY)
        _gemini_groq  = Groq(api_key=settings.GROQ_API_KEY)  # same key, different model
        _grok_client  = Groq(api_key=settings.GROQ_API_KEY)  # same key, different model
except Exception as e:
    print(f"[COUNCIL] Groq init failed: {e}")


# ── Fallback questions ────────────────────────────────────────────────────────
_FALLBACK_COORD = [
    "What type of crime occurred, and where exactly did it take place?",
    "When did the incident happen — date and estimated time window?",
    "Describe the layout: indoor or outdoor? What type of space and approximate size?",
    "How many victims were involved? Describe their positions.",
    "Were there any witnesses? What did they observe?",
    "How did the perpetrator enter and exit the scene?",
    "Describe environmental conditions: lighting and ambient sounds.",
    "Were there security cameras or alarm systems present?",
    "Any vehicles, digital evidence, or unusual circumstances observed?",
]

_FALLBACK_EVIDENCE = [
    "What physical objects were disturbed or moved at the scene?",
    "Were biological traces found — blood, hair, fingerprints, or DNA?",
    "Was a weapon found? Describe its type, location, and condition.",
    "Any transfer material — fibres, soil, or foreign substances?",
    "Were any latent prints lifted from surfaces?",
]

_FALLBACK_PROFILER = [
    "Did the crime appear planned or opportunistic?",
    "What is the known relationship between suspect and victim?",
    "Were there signs of rage, control, or calculation in the attack?",
    "Does the MO suggest familiarity with the victim or the location?",
    "Any post-offense behavior — staging, cleaning, or contact attempts?",
]


def _call_gemini(system: str, messages: List[Dict]) -> str:
    """Scene Coordinator: tries Gemini 2.5 Flash-Lite first, falls back to LLaMA 4 Scout."""
    # Try new Gemini client
    if _gemini_client:
        try:
            history_text = "\n".join(
                f"{m['role'].upper()}: {m['content']}" for m in messages
            )
            prompt = f"{system}\n\nCONVERSATION:\n{history_text}"
            r = _gemini_client.models.generate_content(
                model=GEMINI_COUNCIL_MODEL, contents=prompt
            )
            return r.text.strip()
        except Exception as e:
            print(f"[COUNCIL] Gemini call failed ({e.__class__.__name__}), switching to LLaMA 4 Scout")

    # Fallback: LLaMA 4 Scout 17b as Scene Coordinator (Groq)
    if not _gemini_groq:
        return None
    try:
        msgs = [{"role": "system", "content": system}]
        for m in messages:
            msgs.append({"role": m["role"], "content": m["content"]})
        resp = _gemini_groq.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=msgs,
            max_tokens=250,
            temperature=0.6,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[COUNCIL] LLaMA 4 Scout error: {e}")
        return None


def _call_groq(system: str, messages: List[Dict]) -> str:
    if not _groq_client:
        return None
    try:
        msgs = [{"role": "system", "content": system}]
        for m in messages:
            msgs.append({"role": m["role"], "content": m["content"]})
        resp = _groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=msgs,
            max_tokens=200,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[COUNCIL] Groq call error: {e}")
        return None


def _call_grok(system: str, messages: List[Dict]) -> str:
    """Uses Mixtral-8x7b via Groq for the behavioral profiler persona."""
    if not _grok_client:
        return None
    try:
        msgs = [{"role": "system", "content": system}]
        for m in messages:
            msgs.append({"role": m["role"], "content": m["content"]})
        resp = _grok_client.chat.completions.create(
            model="llama-3.1-8b-instant",   # Fast, distinct from 70b coordinator
            messages=msgs,
            max_tokens=200,
            temperature=0.8,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[COUNCIL] Grok-persona call error: {e}")
        return None


def get_council_greeting() -> List[Dict]:
    """Returns opening messages from all three agents."""
    return [
        {
            "agent": "gemini",
            "content": (
                "Council assembled. I'm Det. Gemini, your Scene Coordinator. "
                "My colleagues Analyst Groq (Evidence) and Profiler Grok (Behavioral) "
                "will contribute their expertise alongside me.\n\n"
                "**Let's begin. What type of crime are we investigating, and where did it take place?**"
            ),
            **AGENTS["gemini"],
        }
    ]


def run_council_turn(history: List[Dict], user_message: str) -> Dict:
    """
    Runs one turn of the council — all three agents respond.
    Returns: { responses: [...], is_complete: bool }
    """
    full_history = history + [{"role": "user", "content": user_message}]
    turn = sum(1 for m in full_history if m["role"] == "user")

    responses = []
    is_complete = False

    # ── GEMINI — Scene Coordinator (always leads) ─────────────────────────────
    gemini_text = _call_gemini(SYSTEM_PROMPTS["gemini"], full_history)
    if not gemini_text:
        idx = min(turn - 1, len(_FALLBACK_COORD) - 1)
        gemini_text = _FALLBACK_COORD[idx]
        is_complete = turn >= len(_FALLBACK_COORD)
        if is_complete:
            gemini_text = (
                "Excellent — the council has gathered sufficient information. "
                "Proceeding to correlation analysis and scene visualization.\n\nSCENE_COMPLETE"
            )

    if "SCENE_COMPLETE" in gemini_text:
        is_complete = True
        gemini_text = gemini_text.replace("SCENE_COMPLETE", "").strip()

    responses.append({
        "agent": "gemini",
        "content": gemini_text,
        **AGENTS["gemini"],
    })

    # ── GROQ — Evidence Specialist ────────────────────────────────────────────
    if turn <= 3 or turn % 2 == 0:  # Groq speaks every other turn + first 3
        groq_text = _call_groq(SYSTEM_PROMPTS["groq"], full_history)
        if not groq_text:
            idx = min((turn - 1) % len(_FALLBACK_EVIDENCE), len(_FALLBACK_EVIDENCE) - 1)
            groq_text = f"From an evidence standpoint — {_FALLBACK_EVIDENCE[idx]}"
        responses.append({
            "agent": "groq",
            "content": groq_text,
            **AGENTS["groq"],
        })

    # ── GROK — Behavioral Profiler ────────────────────────────────────────────
    if turn <= 3 or turn % 2 == 1:  # Grok speaks alternate turns + first 3
        grok_text = _call_grok(SYSTEM_PROMPTS["grok"], full_history)
        if not grok_text:
            idx = min((turn - 1) % len(_FALLBACK_PROFILER), len(_FALLBACK_PROFILER) - 1)
            grok_text = f"Behaviorally speaking — {_FALLBACK_PROFILER[idx]}"
        responses.append({
            "agent": "grok",
            "content": grok_text,
            **AGENTS["grok"],
        })

    return {"responses": responses, "is_complete": is_complete}
