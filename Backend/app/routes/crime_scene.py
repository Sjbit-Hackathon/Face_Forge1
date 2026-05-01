import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.services.scene_council import get_council_greeting, run_council_turn, AGENTS
from app.services.scene_analysis import (
    extract_scene_data,
    build_correlation_data,
)
from app.services.image import generate_scene_image
from app.utils.storage import save_image_locally

router = APIRouter()


class ChatMessage(BaseModel):
    role: str            # "user" | "assistant" | "council"
    content: str
    agent: Optional[str] = None


class CouncilChatRequest(BaseModel):
    case_id: str
    message: str
    history: List[ChatMessage] = []


class AnalyzeRequest(BaseModel):
    case_id: str
    history: List[ChatMessage]


class VisualizeRequest(BaseModel):
    case_id: str
    scene_data: Dict[str, Any]


# ── GET /crime-scene/greet ────────────────────────────────────────────────────
@router.get("/crime-scene/greet")
def greet():
    """Returns opening messages from the full council."""
    return {
        "council_messages": get_council_greeting(),
        "agents": AGENTS,
    }


# ── POST /crime-scene/chat ────────────────────────────────────────────────────
@router.post("/crime-scene/chat")
def crime_scene_chat(req: CouncilChatRequest):
    """
    Multi-agent council turn.
    Returns responses from all active agents + is_complete flag.
    """
    try:
        # Build a clean user-only history for context
        history = [{"role": m.role if m.role == "user" else "assistant",
                    "content": m.content}
                   for m in req.history]
        result = run_council_turn(history, req.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /crime-scene/analyze ─────────────────────────────────────────────────
@router.post("/crime-scene/analyze")
def crime_scene_analyze(req: AnalyzeRequest):
    """
    Extracts structured scene data and builds correlation matrix
    from conversation history.
    """
    try:
        # Flatten all messages into a user/assistant transcript
        history = []
        for m in req.history:
            role = "user" if m.role == "user" else "assistant"
            history.append({"role": role, "content": m.content})

        scene_data = extract_scene_data(history)
        correlation = build_correlation_data(scene_data)
        return {"scene_data": scene_data, "correlation": correlation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /crime-scene/visualize ───────────────────────────────────────────────
@router.post("/crime-scene/visualize")
def crime_scene_visualize(req: VisualizeRequest):
    """
    Generates a photorealistic crime scene image from extracted scene data.
    """
    try:
        print(f"[CRIME-SCENE] Generating image for case {req.case_id}...")
        image_bytes = generate_scene_image(req.scene_data)
        file_name   = f"crime_scene_{req.case_id}_{int(time.time())}.png"
        image_url   = save_image_locally(image_bytes, file_name)
        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
