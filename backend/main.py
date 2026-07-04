import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Annotated

from firebase_admin_setup import verify_token
from services.caption_pipeline import run_pipeline, preload_models
from services.firestore_service import save_caption, get_captions, delete_caption

app = FastAPI(
    title="MICG API",
    description="Mood-Based Multilingual Image Caption Generator",
    version="1.0.0",
)

# ── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{path:path}")
async def options_handler(path: str):
    return {"message": "Success"}


@app.on_event("startup")
async def startup_event():
    preload_models()

# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/")
def health():
    return {"status": "MICG backend running"}


# ── POST /generate-captions ───────────────────────────────────────────────────
@app.post("/generate-captions")
async def generate_captions(
    file: Annotated[UploadFile, File(description="Image file (jpg/png/webp)")],
    mood: Annotated[str, Form()] = "calm",
    language: Annotated[str, Form()] = "English",
    style: Annotated[str, Form()] = "casual",
    user: dict = Depends(verify_token),
):
    """
    Accepts an uploaded image + user preferences.
    Returns 8–10 diverse, mood-aware, optionally translated captions.
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload jpg, png or webp.")

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="Image too large. Max size is 10 MB.")

    result = run_pipeline(image_bytes, mood, language, style)
    
    return {
        "insight": result["insight"],
        "captions": result["captions"],
        "count": len(result["captions"]),
    }


# ── POST /captions/save ───────────────────────────────────────────────────────
class SaveRequest(BaseModel):
    text: str
    mood: str
    language: str
    style: str = "casual"


@app.post("/captions/save")
def save_user_caption(
    payload: SaveRequest,
    user: dict = Depends(verify_token),
):
    """Persist a favourite caption to Firestore for the authenticated user."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required to save captions.")
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Caption text cannot be empty.")
    doc_id = save_caption(
        user_id=user["uid"],
        text=payload.text,
        mood=payload.mood,
        language=payload.language,
        style=payload.style,
    )
    return {"message": "Caption saved successfully.", "id": doc_id}


# ── DELETE /captions/{caption_id} ────────────────────────────────────────────
@app.delete("/captions/{caption_id}")
def delete_user_caption(
    caption_id: str,
    user: dict = Depends(verify_token),
):
    """Delete a saved caption by ID for the authenticated user."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required.")
    deleted = delete_caption(user_id=user["uid"], caption_id=caption_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Caption not found or not yours.")
    return {"message": "Caption deleted successfully."}


# ── GET /captions ─────────────────────────────────────────────────────────────
@app.get("/captions")
def get_user_captions(user: dict = Depends(verify_token)):
    """Retrieve all saved captions for the authenticated user, newest first."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required to view saved captions.")
    captions = get_captions(user["uid"])
    return {"captions": captions, "count": len(captions)}
