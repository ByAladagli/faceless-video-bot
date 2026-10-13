import logging
import os
import re
import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from tts_engine import create_tts
from video_maker import make_video

ROOT = Path(__file__).resolve().parent
JOBS_DIR = ROOT / "assets" / "jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger("faceless-api")
JOB_ID_RE = re.compile(r"^[0-9a-f]{32}$")

app = FastAPI(
    title="Faceless Video Bot API",
    version="1.0.0",
    description="Kullanıcının verdiği metni TTS ve FFmpeg ile videoya dönüştüren yerel prototip.",
)
origins = [
    item.strip()
    for item in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if item.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class GenerateRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=2000)


def _generate(job_id: str, topic: str) -> Path:
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=False)
    audio = job_dir / "audio.mp3"
    subtitles = job_dir / "subtitles.srt"
    video = job_dir / "video.mp4"
    audio_path, subtitles_path = create_tts(topic, str(audio), str(subtitles))
    output_path = Path(make_video(audio_path, subtitles_path, video))
    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError("Video dosyası oluşturulamadı.")
    return output_path


@app.get("/api/health")
async def health():
    return {"ok": True, "service": "faceless-video-bot-api", "version": app.version}


@app.post("/api/generate")
async def generate_video(request: GenerateRequest):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=422, detail="Video metni boş olamaz.")
    job_id = uuid.uuid4().hex
    try:
        await run_in_threadpool(_generate, job_id, topic)
    except FileNotFoundError as exc:
        shutil.rmtree(JOBS_DIR / job_id, ignore_errors=True)
        logger.warning("Video üretimi için eksik dosya/araç: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception:
        shutil.rmtree(JOBS_DIR / job_id, ignore_errors=True)
        logger.exception("Video üretimi başarısız (job=%s)", job_id)
        raise HTTPException(status_code=500, detail="Video üretilemedi. FFmpeg/FFprobe ve TTS bağlantısını kontrol edin.")
    return {
        "success": True,
        "script": topic,
        "mode": "user_supplied_text",
        "notice": "Bu prototip metni otomatik yazmaz; girilen metni seslendirir ve videoya dönüştürür.",
        "video_url": f"/api/videos/{job_id}",
    }


@app.get("/api/videos/{job_id}")
async def download_video(job_id: str):
    if not JOB_ID_RE.fullmatch(job_id):
        raise HTTPException(status_code=400, detail="Geçersiz video kimliği.")
    video_path = JOBS_DIR / job_id / "video.mp4"
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail="Video bulunamadı.")
    return FileResponse(video_path, media_type="video/mp4", filename=f"faceless-{job_id}.mp4")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8001")))
