import time
import random
import requests
import urllib.parse
from app.config import settings

HF_API_BASE = "https://api-inference.huggingface.co/models"
TIMEOUT     = 90   # seconds per request
MAX_RETRIES = 2    # retries on timeout/429

# ─── Face sketch prompt prefix ────────────────────────────────────────────────
FACE_PREFIX = (
    "RAW photo DSLR, photorealistic human face portrait, forensic mugshot, "
    "front-facing, neutral gray background, ultra-realistic skin texture, "
    "no cartoon, no illustration, "
)

def build_face_prompt(raw_prompt: str) -> str:
    """Prepends photorealism guard for face/suspect sketch images."""
    return FACE_PREFIX + raw_prompt


# ─── Crime scene prompt builder ───────────────────────────────────────────────
_BAD_VALUES = {"unknown", "see transcript", "none", "n/a", "", "unknown crime"}

def _clean(val: str, default: str) -> str:
    """Returns val if it's a real value, else default."""
    if not val or val.strip().lower() in _BAD_VALUES or "transcript" in val.lower():
        return default
    return val.strip()


def build_scene_prompt(scene_data: dict) -> str:
    """
    Builds a high-quality Pollinations crime scene prompt.
    Uses the 'police crime scene photo' style which consistently produces
    realistic forensic imagery. Hard-capped at 190 chars.
    """
    loc      = scene_data.get("location", {})
    crime    = _clean(scene_data.get("crime_type", ""), "homicide")
    room     = _clean(loc.get("room_type", ""), "apartment interior")
    loc_type = loc.get("type", "indoor")

    # Pick first real evidence item
    ev = ""
    for e in (scene_data.get("evidence") or []):
        item = _clean(e.get("item", ""), "")
        if item:
            ev = item
            break

    crime_detail = f"{ev}, " if ev else ("blood on floor, " if crime == "homicide" else "")

    if loc_type == "indoor":
        prompt = (
            f"police crime scene photo, empty {room}, "
            f"numbered yellow forensic placards on floor, "
            f"{crime_detail}"
            f"crime scene tape, no people, forensic overhead lighting, photorealistic, canon 5d"
        )
    else:
        env = _clean(loc.get("environment", ""), "road")
        prompt = (
            f"police crime scene photo, empty outdoor {env}, "
            f"numbered yellow forensic placards on ground, "
            f"{crime_detail}"
            f"police tape perimeter, no people, night forensic lighting, photorealistic"
        )

    return prompt[:190]


# ─── Core generation functions ────────────────────────────────────────────────

def generate_image(prompt: str) -> bytes:
    """For face/suspect sketch images — HuggingFace primary, Pollinations fallback."""
    return _try_hf_then_pollinations(prompt)


def generate_scene_image(scene_data: dict) -> bytes:
    """
    For crime scene images — uses the validated 'police crime scene photo' template.
    Retries up to MAX_RETRIES times on timeout/rate-limit.
    """
    prompt = build_scene_prompt(scene_data)
    print(f"[SCENE-IMAGE] Prompt ({len(prompt)} chars): {prompt}")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = _pollinations(prompt, model="flux")
            return result
        except Exception as e:
            err = str(e)
            if attempt < MAX_RETRIES and ("timed out" in err or "429" in err or "failed" in err.lower()):
                wait = attempt * 4
                print(f"[SCENE-IMAGE] Attempt {attempt} failed ({err[:60]}), retrying in {wait}s…")
                time.sleep(wait)
            else:
                raise

    raise Exception("Crime scene image generation failed after all retries.")


# ─── HuggingFace + Pollinations ───────────────────────────────────────────────

def _try_hf_then_pollinations(prompt: str) -> bytes:
    """Tries HuggingFace inference API, falls back to Pollinations."""
    if settings.HUGGINGFACE_API_TOKEN:
        url     = f"{HF_API_BASE}/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}
        payload = {
            "inputs": prompt,
            "parameters": {"num_inference_steps": 8, "guidance_scale": 3.5,
                           "width": 1024, "height": 1024},
        }
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
            if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
                print(f"[IMAGE] HF FLUX OK ({len(r.content)} bytes)")
                return r.content
            print(f"[IMAGE] HF FLUX: HTTP {r.status_code} — using Pollinations")
        except Exception as e:
            print(f"[IMAGE] HF error: {e}")

    return _pollinations(prompt, "flux-realism")


def _pollinations(prompt: str, model: str = "flux") -> bytes:
    """
    Pollinations.ai via GET.
    - model=flux is faster and more reliable than flux-realism for scenes
    - enhance=false prevents Pollinations from rewriting the prompt
    - Raises on all errors so callers can retry
    """
    seed    = random.randint(1, 999999)
    encoded = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1024&height=768&nologo=true"
        f"&model={model}&seed={seed}&enhance=false&safe=false"
    )
    print(f"[IMAGE] Pollinations {model} URL={len(url)} chars")

    try:
        r = requests.get(url, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        raise Exception(f"Pollinations {model} timed out after {TIMEOUT}s")
    except Exception as e:
        raise Exception(f"Pollinations {model} network error: {e}")

    if r.status_code == 429:
        raise Exception(f"Pollinations 429 rate-limit")
    if r.status_code != 200:
        raise Exception(f"Pollinations HTTP {r.status_code}")
    if len(r.content) < 5000:
        raise Exception(f"Pollinations returned tiny response ({len(r.content)} bytes)")

    print(f"[IMAGE] Pollinations {model} OK ({len(r.content)} bytes)")
    return r.content
