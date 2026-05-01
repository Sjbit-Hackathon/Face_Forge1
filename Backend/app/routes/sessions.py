from fastapi import APIRouter, HTTPException
from app.models.schemas import SessionCreate, SessionResponse
from app.utils.supabase import create_session, get_session

router = APIRouter()

@router.post("/", response_model=SessionResponse)
def create_new_session(request: SessionCreate):
    """Creates a new session for a user."""
    result = create_session(request.title)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create session")
        
    session_data = result[0]
    return SessionResponse(
        id=str(session_data.get("id")),
        title=session_data.get("title", request.title),
        created_at=str(session_data.get("created_at"))
    )

@router.get("/{session_id}", response_model=SessionResponse)
def get_session_by_id(session_id: str):
    """Retrieves an existing session."""
    result = get_session(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session_data = result[0]
    return SessionResponse(
        id=str(session_data.get("id")),
        title=session_data.get("title"),
        created_at=str(session_data.get("created_at"))
    )
