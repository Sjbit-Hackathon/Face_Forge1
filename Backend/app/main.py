import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import auth, sessions, generate
from app.routes.crime_scene import router as crime_scene_router

app = FastAPI(
    title="FaceForge API",
    description="Backend API for FaceForge: Forensic HD Suspect Identification",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for the hackathon deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve locally-saved images with explicit CORS headers ──────────────────
STATIC_DIR = Path(__file__).resolve().parent.parent / "static" / "images"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

from fastapi.responses import FileResponse
from starlette.responses import Response

class StaticFilesWithCORS(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

if __name__ == "__main__":
    import uvicorn
    import os
    # Render provides a $PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)

app.mount("/static/images", StaticFilesWithCORS(directory=str(STATIC_DIR)), name="images")

# ── Routes ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(generate.router, tags=["Generate"])
app.include_router(crime_scene_router, tags=["Crime Scene"])
