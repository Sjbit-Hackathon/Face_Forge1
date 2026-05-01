import time
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from app.models.schemas import (
    GenerateRequest, GenerateResponse,
    RefineRequest, RefineResponse,
    UploadReferenceResponse
)
from app.services.gemini import generate_prompt, analyze_face_from_image
from app.services.image import generate_image
from app.services.hash import get_image_hash
from app.utils.storage import save_image_locally
from app.utils.supabase import upload_image, create_audit_record

router = APIRouter()


def _store_image(image_bytes: bytes, file_name: str) -> str:
    """
    Try Supabase first; fall back to local static file serving.
    Always returns a usable URL.
    """
    # 1. Try Supabase (may fail if credentials are wrong / bucket missing)
    try:
        url = upload_image(image_bytes, file_name)
        if url:
            return url
    except Exception as e:
        print(f"Supabase upload failed ({e}), using local storage.")

    # 2. Fall back to local static serving
    return save_image_locally(image_bytes, file_name)


def _try_audit(case_id, witness_input, prompt, image_hash, image_url, iteration_number):
    """Best-effort audit record — never raises."""
    try:
        result = create_audit_record(
            case_id=case_id,
            witness_input=witness_input,
            prompt_generated=prompt,
            image_hash=image_hash,
            image_url=image_url,
            iteration_number=iteration_number,
        )
        return str(result[0]["id"]) if result else None
    except Exception as e:
        print(f"Audit record failed (non-critical): {e}")
        return None


# ── Generate ─────────────────────────────────────────────────────────────────
@router.post("/generate", response_model=GenerateResponse)
def generate_sketch(request: GenerateRequest):
    """
    Full pipeline:
      witness input → Gemini prompt → FLUX image → store → audit
    """
    try:
        prompt, question = generate_prompt(request.witness_input, request.feature_locks)
        print(f"[GENERATE] Prompt: {prompt[:120]}...")

        image_bytes = generate_image(prompt)
        print(f"[GENERATE] Image bytes received: {len(image_bytes)}")

        image_hash = get_image_hash(image_bytes)
        file_name = f"case_{request.case_id}_iter_{request.iteration_number}_{int(time.time())}.png"
        image_url = _store_image(image_bytes, file_name)

        audit_id = _try_audit(
            request.case_id, request.witness_input,
            prompt, image_hash, image_url, request.iteration_number
        )

        return GenerateResponse(
            success=True,
            image_url=image_url,
            audit_id=audit_id,
            message="Generated successfully.",
            follow_up_question=question
        )
    except Exception as e:
        print(f"[GENERATE ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Refine ───────────────────────────────────────────────────────────────────
@router.post("/refine", response_model=RefineResponse)
def refine_sketch(request: RefineRequest):
    """
    Refines an existing image based on new instructions while preserving the original context.
    """
    try:
        combined_input = (
            f"ORIGINAL SUSPECT BASE: {request.original_witness_input}\n"
            f"NEW REFINEMENT INSTRUCTIONS: {request.refinement_input}\n"
            "STRICT: Maintain the same gender, ethnicity, and age as the original base."
        )
        prompt, question = generate_prompt(combined_input, request.feature_locks)
        print(f"[REFINE] Prompt: {prompt[:120]}...")

        image_bytes = generate_image(prompt)
        print(f"[REFINE] Image bytes received: {len(image_bytes)}")

        image_hash = get_image_hash(image_bytes)
        file_name = f"case_{request.case_id}_iter_{request.iteration_number}_{int(time.time())}.png"
        image_url = _store_image(image_bytes, file_name)

        audit_id = _try_audit(
            request.case_id, request.refinement_input,
            prompt, image_hash, image_url, request.iteration_number
        )

        return RefineResponse(
            success=True,
            image_url=image_url,
            audit_id=audit_id,
            message="Refined successfully.",
            follow_up_question=question
        )
    except Exception as e:
        print(f"[REFINE ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Upload Reference Photo ────────────────────────────────────────────────────
@router.post("/upload-reference", response_model=UploadReferenceResponse)
async def upload_reference_photo(
    file: UploadFile = File(...),
    case_id: str = Form(...),
    iteration_number: int = Form(...),
):
    """
    Accepts a reference photo → Gemini Vision analyzes face →
    FLUX generates forensic HD version → store → audit.
    """
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")

        mime_type = file.content_type or "image/jpeg"
        if not mime_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are accepted.")

        print(f"[UPLOAD-REF] Analyzing {len(image_bytes)} bytes with Gemini Vision...")
        face_prompt = analyze_face_from_image(image_bytes, mime_type=mime_type)
        print(f"[UPLOAD-REF] Prompt: {face_prompt[:120]}...")

        output_bytes = generate_image(face_prompt)
        print(f"[UPLOAD-REF] Image bytes: {len(output_bytes)}")

        image_hash = get_image_hash(output_bytes)
        file_name = f"case_{case_id}_ref_iter_{iteration_number}_{int(time.time())}.png"
        image_url = _store_image(output_bytes, file_name)

        audit_id = _try_audit(
            case_id, "[Reference photo uploaded]",
            face_prompt, image_hash, image_url, iteration_number
        )

        return UploadReferenceResponse(
            success=True,
            image_url=image_url,
            description=face_prompt,
            audit_id=audit_id,
            message="Reference photo processed successfully.",
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[UPLOAD-REF ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/generate-360')
async def generate_360_profile(case_id: str = Body(..., embed=True), image_url: str = Body(..., embed=True), witness_input: str = Body(..., embed=True)):
    try:
        from app.services.gemini import get_forensic_description
        from app.services.image import generate_image
        import uuid
        analysis_prompt = f'ACT AS A FORENSIC ANATOMIST. Describe the side profile for this witness description: {witness_input}'
        side_description = await get_forensic_description(analysis_prompt)
        left_bytes = generate_image(f'Forensic side profile view, left side, 90 degrees, {side_description}')
        right_bytes = generate_image(f'Forensic side profile view, right side, 90 degrees, {side_description}')
        left_url = _store_image(left_bytes, f'{case_id}_left_{uuid.uuid4().hex[:6]}.png')
        right_url = _store_image(right_bytes, f'{case_id}_right_{uuid.uuid4().hex[:6]}.png')
        return {'success': True, 'front': image_url, 'left': left_url, 'right': right_url}
    except Exception as e:
        print(f'[360 ERROR] {e}')
        raise HTTPException(status_code=500, detail=str(e))
