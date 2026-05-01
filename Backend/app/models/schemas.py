from pydantic import BaseModel
from typing import Optional, Dict, Any

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class SessionCreate(BaseModel):
    title: Optional[str] = "New Session"

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str

class GenerateRequest(BaseModel):
    case_id: str
    witness_input: str
    iteration_number: int
    feature_locks: Optional[Dict[str, Any]] = None

class GenerateResponse(BaseModel):
    success: bool
    image_url: Optional[str] = None
    audit_id: Optional[str] = None
    message: Optional[str] = None
    follow_up_question: Optional[str] = None

class RefineRequest(BaseModel):
    case_id: str
    previous_image_url: str
    original_witness_input: str
    refinement_input: str
    iteration_number: int
    feature_locks: Optional[Dict[str, Any]] = None

class RefineResponse(BaseModel):
    success: bool
    image_url: Optional[str] = None
    audit_id: Optional[str] = None
    message: Optional[str] = None
    follow_up_question: Optional[str] = None

class UploadReferenceResponse(BaseModel):
    success: bool
    image_url: Optional[str] = None
    description: Optional[str] = None
    audit_id: Optional[str] = None
    message: Optional[str] = None
