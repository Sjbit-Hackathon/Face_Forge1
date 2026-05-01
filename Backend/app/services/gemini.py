import random
from typing import Dict, Any
from app.config import settings

try:
    import google.generativeai as genai
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
    else:
        model = None
except Exception as e:
    print(f"Warning: Could not load google.generativeai: {e}")
    model = None

# ── Facial feature translation map ──────────────────────────────────────────
# Maps UI pill labels → photorealistic prompt phrases for each facial region
FEATURE_PHRASES = {
    "Eyes": {
        "Size":    {"Small": "small eyes", "Medium": "medium-sized eyes", "Large": "large eyes", "Wider": "wide-set eyes"},
        "Shape":   {"Round": "round eyes", "Almond": "almond-shaped eyes", "Narrow": "narrow eyes"},
        "Spacing": {"Close": "close-set eyes", "Normal": "normally spaced eyes", "Wide": "wide-set eyes"},
        "Depth":   {"Deep": "deep-set eyes", "Normal": "normally set eyes", "Protruding": "protruding eyes"},
    },
    "Nose": {
        "Width":  {"Narrow": "narrow nose", "Medium": "medium-width nose", "Broad": "broad nose"},
        "Bridge": {"Straight": "straight nasal bridge", "Flat": "flat nasal bridge", "Curved": "curved nasal bridge"},
        "Tip":    {"Pointed": "pointed nose tip", "Rounded": "rounded nose tip"},
        "Length": {"Short": "short nose", "Medium": "medium-length nose", "Long": "long nose"},
    },
    "Mouth": {
        "Lip Size": {"Thin": "thin lips", "Medium": "medium lips", "Full": "full lips"},
        "Shape":    {"Straight": "straight mouth", "Curved": "naturally curved mouth", "Downturned": "downturned mouth corners"},
        "Width":    {"Narrow": "narrow mouth", "Medium": "medium-width mouth", "Wide": "wide mouth"},
    },
    "Jaw": {
        "Width":   {"Narrow": "narrow jaw", "Medium": "medium jaw width", "Wide": "wide jaw"},
        "Jawline": {"Soft": "soft rounded jawline", "Defined": "defined angular jawline", "Square": "square jawline"},
        "Chin":    {"Round": "round chin", "Pointed": "pointed chin", "Square": "square chin"},
    },
}


def _build_feature_description(feature_locks: Dict[str, Any]) -> str:
    """Converts UI pill selections into specific anatomical prompt phrases."""
    if not feature_locks:
        return ""
    parts = []
    for group, attrs in feature_locks.items():
        if not isinstance(attrs, dict):
            continue
        for attr, val in attrs.items():
            if not val:
                continue
            phrase = (
                FEATURE_PHRASES.get(group, {})
                               .get(attr, {})
                               .get(val)
            )
            if phrase:
                parts.append(phrase)
            else:
                parts.append(f"{val.lower()} {attr.lower()}")
    return ", ".join(parts)


def generate_prompt(witness_input: str, feature_locks: Dict[str, Any] = None) -> tuple[str, str]:
    """
    Uses Gemini to transform witness input into:
    1. A photorealistic FLUX image generation prompt.
    2. A short forensic follow-up question about specific facial features.
    """
    feature_desc = _build_feature_description(feature_locks)

    PHOTO_PREFIX = (
        "RAW photograph, photorealistic, hyperrealistic, 8K UHD, DSLR photo, "
        "sharp focus, professional studio lighting, forensic mugshot portrait, "
        "front-facing, neutral light gray background, ultra-detailed skin texture, "
        "realistic facial pores, natural human face, no cartoon, no anime, no illustration, "
        "no painting, cinematic color grading"
    )

    if not model:
        base = f"{PHOTO_PREFIX}, {witness_input}"
        if feature_desc:
            base += f", {feature_desc}"
        return base, "Can you describe more about the suspect's facial structure?"

    feature_instruction = ""
    if feature_desc:
        feature_instruction = (
            f"\nCRITICAL — The following facial features MUST be precisely described: {feature_desc}."
        )

    system_instruction = f"""You are an elite forensic identification expert.
Your task: Convert the witness description into two parts:
1. PROMPT: A single-line, comma-separated prompt for FLUX.1 (photorealistic mugshot).
2. QUESTION: A single probing forensic question (max 12 words) to refine the suspect's face. 

STRICT RULES FOR THE QUESTION:
- Do NOT repeat the same question twice.
- If the witness was unsure about a feature, ask a clarifying question with 2-3 options (e.g., "Were the eyes more almond-shaped or round?").
- Focus on a specific feature that hasn't been detailed yet (e.g., ears, chin, forehead, eyebrows, or skin texture).
- Be professional and direct.

FORMAT:
PROMPT: [your prompt here]
QUESTION: [your question here]

{feature_instruction}

Witness Description: "{witness_input}"
"""

    try:
        response = model.generate_content(system_instruction)
        text = response.text.strip()
        
        prompt = ""
        question = "How would you describe the suspect's nose and jawline?" # Default
        
        for line in text.split('\n'):
            if line.upper().startswith('PROMPT:'):
                prompt = line.split(':', 1)[1].strip()
            elif line.upper().startswith('QUESTION:'):
                question = line.split(':', 1)[1].strip()

        if not prompt:
            prompt = text # Fallback

        if "photorealistic" not in prompt.lower():
            prompt = PHOTO_PREFIX + ", " + prompt
            
        return prompt, question
    except Exception as e:
        print(f"Gemini API error: {e}")
        base = f"{PHOTO_PREFIX}, {witness_input}"
        if feature_desc:
            base += f", {feature_desc}"
        return base, "Could you provide more details about the suspect's eyes or nose?"


def analyze_face_from_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """
    Uses Gemini Vision to analyze a face in an uploaded photo and returns
    a photorealistic FLUX prompt describing that face.
    Falls back to a generic forensic prompt if Gemini is unavailable.
    """
    PHOTO_PREFIX = (
        "RAW photograph, photorealistic, hyperrealistic, 8K UHD, DSLR photo, "
        "sharp focus, professional studio lighting, forensic mugshot portrait, "
        "front-facing, neutral light gray background, ultra-detailed skin texture, "
        "realistic facial pores, natural human face, no cartoon, no anime, no illustration, "
        "cinematic color grading"
    )

    if not model:
        return f"{PHOTO_PREFIX}, realistic human face, detailed facial features"

    try:
        import google.generativeai as genai

        vision_instruction = """You are a forensic identification expert.
Analyze the human face in this image and produce a single-line, highly detailed, comma-separated prompt for FLUX.1 image generation that will recreate this person's face as a photorealistic forensic mugshot.

Output ONLY the prompt text. No labels, no prefixes, no quotes.

Start with: "RAW photograph, photorealistic, hyperrealistic, 8K UHD, DSLR photo, sharp focus, professional studio lighting, forensic mugshot portrait, front-facing, neutral light gray background"

Then describe in precise anatomical detail:
- Estimated age and gender
- Skin tone and texture
- Hair color, texture, length, and style
- Eye color, shape, size, spacing
- Nose shape, width, bridge, and tip
- Lip shape, size, and mouth width
- Jaw shape and jawline definition
- Chin shape
- Any distinctive features (scars, moles, facial hair, etc.)

End with: "ultra-detailed skin texture, realistic facial pores, natural human skin, cinematic color grading, no cartoon, no anime, no illustration"
"""

        image_part = {"mime_type": mime_type, "data": image_bytes}
        response = model.generate_content([vision_instruction, image_part])
        prompt = response.text.strip()

        # Safety: ensure photorealism keywords present
        if "photorealistic" not in prompt.lower():
            prompt = PHOTO_PREFIX + ", " + prompt

        return prompt

    except Exception as e:
        print(f"Gemini Vision error: {e}")
        return f"{PHOTO_PREFIX}, realistic human face, detailed facial features, neutral expression"
