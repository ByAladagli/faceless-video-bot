import math
import os
import random
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"
BACKGROUND_CANDIDATES = [
    ASSETS_DIR / "background.mp4",
    ROOT / "backend" / "background.mp4",
]
DEFAULT_OUTPUT = ASSETS_DIR / "final_video.mp4"


def _binary(name: str) -> str:
    """Resolve FFmpeg tools from PATH; never depend on a developer's machine path."""
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"{name} bulunamadı. FFmpeg'i kurup PATH'e ekleyin.")
    return path


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def get_video_duration(video_path: str | Path) -> float:
    result = _run([
        _binary("ffprobe"), "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(video_path),
    ])
    try:
        duration = float(result.stdout.strip())
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Video süresi okunamadı: {video_path}") from exc
    if not math.isfinite(duration) or duration <= 0:
        raise RuntimeError(f"Geçersiz video süresi: {video_path}")
    return duration


def _find_background() -> Path:
    for candidate in BACKGROUND_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "Arka plan videosu bulunamadı. assets/background.mp4 veya "
        "backend/background.mp4 dosyasını ekleyin."
    )


def make_video(audio_path: str, srt_path: str, output_path: str | Path = DEFAULT_OUTPUT) -> str:
    audio = Path(audio_path).resolve()
    subtitles = Path(srt_path).resolve()
    background = _find_background()
    output = Path(output_path).resolve()

    for required in (audio, subtitles, background):
        if not required.is_file():
            raise FileNotFoundError(f"Gerekli dosya bulunamadı: {required}")
    output.parent.mkdir(parents=True, exist_ok=True)

    audio_duration = get_video_duration(audio)
    background_duration = get_video_duration(background)
    start_time = random.uniform(0, max(0, background_duration - audio_duration))

    # FFmpeg filter paths need escaping on Windows (drive colon and backslashes).
    subtitle_filter_path = str(subtitles).replace("\\", "/").replace(":", r"\:")
    vf_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        f"subtitles='{subtitle_filter_path}':"
        "force_style='Fontname=Arial,Fontsize=24,PrimaryColour=&H0000FFFF,"
        "OutlineColour=&H000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=40'"
    )
    command = [
        _binary("ffmpeg"), "-y", "-ss", f"{start_time:.3f}", "-i", str(background),
        "-i", str(audio), "-t", f"{math.ceil(audio_duration)}",
        "-map", "0:v:0", "-map", "1:a:0", "-vf", vf_filter,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
        str(output),
    ]
    try:
        _run(command)
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or "").strip()
        raise RuntimeError(f"FFmpeg video oluşturamadı: {details[-2000:]}") from exc
    return str(output)


if __name__ == "__main__":
    audio_file = ASSETS_DIR / "audio.mp3"
    subtitle_file = ASSETS_DIR / "subs.srt"
    print(make_video(str(audio_file), str(subtitle_file)))
