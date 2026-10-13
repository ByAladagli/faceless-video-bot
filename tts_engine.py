import asyncio
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"
VOICE = "tr-TR-AhmetNeural"


async def generate_audio_and_subs(text: str, output_audio=None, output_subs=None):
    """Generate TTS audio and word-boundary subtitles at stable project paths."""
    if not text or not text.strip():
        raise ValueError("TTS metni boş olamaz.")

    audio_path = Path(output_audio) if output_audio else ASSETS_DIR / "audio.mp3"
    subs_path = Path(output_subs) if output_subs else ASSETS_DIR / "subs.srt"
    audio_path = audio_path.resolve()
    subs_path = subs_path.resolve()
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    subs_path.parent.mkdir(parents=True, exist_ok=True)
    audio_tmp = audio_path.with_suffix(audio_path.suffix + ".tmp")
    subs_tmp = subs_path.with_suffix(subs_path.suffix + ".tmp")

    communicate = edge_tts.Communicate(text.strip(), VOICE)
    submaker = edge_tts.SubMaker()
    try:
        with audio_tmp.open("wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk.get("type") == "audio":
                    audio_file.write(chunk["data"])
                elif chunk.get("type") in ("WordBoundary", "SentenceBoundary"):
                    submaker.feed(chunk)

        subtitles = submaker.get_srt()
        if not audio_tmp.is_file() or audio_tmp.stat().st_size == 0:
            raise RuntimeError("TTS ses çıktısı boş.")
        if not subtitles.strip():
            raise RuntimeError("TTS altyazı çıktısı boş; sağlayıcı kelime sınırlarını döndürmemiş olabilir.")

        subs_tmp.write_text(subtitles, encoding="utf-8")
        audio_tmp.replace(audio_path)
        subs_tmp.replace(subs_path)
    except Exception:
        audio_tmp.unlink(missing_ok=True)
        subs_tmp.unlink(missing_ok=True)
        raise

    return str(audio_path), str(subs_path)


def create_tts(text: str, audio_path=None, subs_path=None):
    """Synchronous wrapper for the command-line pipeline."""
    return asyncio.run(generate_audio_and_subs(text, audio_path, subs_path))


if __name__ == "__main__":
    audio, subtitles = create_tts(
        "Merhaba, bu otomatik olarak üretilen bir videodur.",
    )
    print(f"Ses: {audio}\nAltyazı: {subtitles}")
