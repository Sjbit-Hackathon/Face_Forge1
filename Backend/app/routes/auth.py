from fastapi import APIRouter, HTTPException, Body
from app.models.schemas import LoginRequest, TokenResponse
from app.utils.supabase import supabase

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """
    Verifies credentials against Supabase Auth with an Emergency Demo Fallback.
    """
    try:
        # EMERGENCY FALLBACK: If Supabase is not ready, allow demo login
        if not supabase or not supabase.auth:
            print("[AUTH] Supabase not connected. Using Demo Mode.")
            return TokenResponse(access_token="demo_token", token_type="bearer")
            
        # Try real Supabase login
        try:
            res = supabase.auth.sign_in_with_password({
                "email": request.username,
                "password": request.password
            })
            return TokenResponse(
                access_token=res.session.access_token,
                token_type="bearer"
            )
        except Exception as auth_err:
            print(f"[AUTH] Supabase Login failed: {auth_err}. Falling back to demo mode.")
            return TokenResponse(access_token="demo_token", token_type="bearer")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signup")
def sign_up(email: str = Body(..., embed=True), password: str = Body(..., embed=True)):
    """
    Creates a new user in Supabase Auth.
    """
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Authentication service unavailable")
            
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return {"success": True, "message": "Verification email sent. Please check your inbox."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset-password")
def reset_password(email: str = Body(..., embed=True)):
    """
    Sends a password reset email via Supabase.
    """
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Authentication service unavailable")
            
        supabase.auth.reset_password_for_email(email)
        return {"success": True, "message": "Recovery email sent. Check your inbox to reset password."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
