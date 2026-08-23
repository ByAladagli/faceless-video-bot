from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
from video_generator import generate_video

app = FastAPI(title="Faceless Video Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    topic: str

@app.post("/api/generate")
async def api_generate_video(req: VideoRequest):
    try:
        # Her video için benzersiz bir isim oluştur
        video_id = str(uuid.uuid4())[:8]
        output_filename = f"out_{video_id}.mp4"
        
        result = await generate_video(req.topic, output_filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_video(filename: str):
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filename, media_type="video/mp4", filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
