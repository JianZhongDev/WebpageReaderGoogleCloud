from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from services.tts import synthesize_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Web Reader API", version="1.0.0")

# CORS Configuration
# Allow requests from the frontend (localhost:3000 for dev)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173", # Vite default
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SynthesizeRequest(BaseModel):
    text: str
    voice_id: str = "en-US-Wavenet-D"

@app.get("/")
def read_root():
    return {"message": "Web Reader API is running"}

@app.post("/api/v1/synthesize")
async def synthesize_audio(request: SynthesizeRequest):
    logger.info(f"Synthesizing audio for text length: {len(request.text)}")
    try:
        result = await synthesize_text(request.text, request.voice_id)
        return result
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
