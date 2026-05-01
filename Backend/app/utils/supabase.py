import uuid
from typing import Optional
from supabase import create_client, Client
from app.config import settings

# Initialize Supabase client
try:
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    else:
        supabase = None
except Exception as e:
    print(f"Failed to initialize Supabase client: {e}")
    supabase = None

def upload_image(image_bytes: bytes, file_name: str, bucket_name: str = "forensic_images") -> Optional[str]:
    """Uploads an image to Supabase Storage and returns the public URL."""
    if not supabase:
        print("Supabase client not initialized.")
        return None
        
    try:
        supabase.storage.from_(bucket_name).upload(file_name, image_bytes, {"content-type": "image/png"})
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        return public_url
    except Exception as e:
        print(f"Error uploading image to Supabase: {e}")
        return None

def create_audit_record(case_id: str, witness_input: str, prompt_generated: str, image_hash: str, image_url: str, iteration_number: int):
    """Creates a record in the face_forge_audit table."""
    if not supabase:
        print("Supabase client not initialized.")
        return None
        
    try:
        data = {
            "case_id": case_id,
            "witness_input": witness_input,
            "prompt_generated": prompt_generated,
            "image_hash_sha256": image_hash,
            "image_url": image_url,
            "iteration_number": iteration_number
        }
        
        response = supabase.table("face_forge_audit").insert(data).execute()
        return response.data
    except Exception as e:
        print(f"Error inserting audit record: {e}")
        return None

def create_session(title: str):
    """Creates a new session in the database."""
    if not supabase:
        # Return a mock session if DB is not connected
        return [{"id": str(uuid.uuid4()), "title": title, "created_at": "now"}]
        
    try:
        data = {"title": title}
        # Assuming a 'sessions' table exists
        response = supabase.table("sessions").insert(data).execute()
        return response.data
    except Exception as e:
        print(f"Error inserting session record: {e}")
        # Fallback for hackathon
        return [{"id": str(uuid.uuid4()), "title": title, "created_at": "now"}]
        
def get_session(session_id: str):
    if not supabase:
        return [{"id": session_id, "title": "Mock Session", "created_at": "now"}]
    try:
        response = supabase.table("sessions").select("*").eq("id", session_id).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching session: {e}")
        return [{"id": session_id, "title": "Mock Session", "created_at": "now"}]
