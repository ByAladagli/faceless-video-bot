import json
from pathlib import Path

from scraper import get_content
from tts_engine import create_tts
from video_maker import make_video

ROOT = Path(__file__).resolve().parent
HISTORY_FILE = ROOT / "history.json"
COOKIES_FILE = ROOT / "cookies.txt"
ASSETS_DIR = ROOT / "assets"


def load_history() -> set[str]:
    if not HISTORY_FILE.exists():
        return set()
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return set(data) if isinstance(data, list) else set()
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(f"Geçmiş dosyası okunamadı: {HISTORY_FILE}") from exc


def save_history(history: set[str]) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = HISTORY_FILE.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(sorted(history), ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(HISTORY_FILE)


def run_bot() -> None:
    print("Bot başlatılıyor...")
    entries = get_content()
    if not entries:
        print("İçerik kaynağından kullanılabilir içerik alınamadı; sahte içerik üretilmedi.")
        return

    history = load_history()
    selected = next((entry for entry in entries if entry.get("id") and entry["id"] not in history), None)
    if selected is None:
        print("Yeni içerik bulunamadı.")
        return

    text = (selected.get("turkish_text") or "").strip()
    if not text:
        print("Seçilen içerik boş; işlem durduruldu.")
        return

    print(f"Seçilen içerik: {text}")
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    audio_path, subtitles_path = create_tts(
        text, str(ASSETS_DIR / "audio.mp3"), str(ASSETS_DIR / "subs.srt")
    )
    video_path = make_video(audio_path, subtitles_path, ASSETS_DIR / "final_video.mp4")
    output = Path(video_path)
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("Video üretimi tamamlandı olarak bildirildi ancak çıktı dosyası yok/boş.")

    if not COOKIES_FILE.is_file():
        print(f"Video üretildi: {video_path}")
        print("TikTok yüklemesi atlandı: cookies.txt yok. İçerik geçmişe yazılmadı; daha sonra tekrar denenebilir.")
        return

    try:
        from tiktok_uploader.upload import upload_video
        description = f"{text}\n\n#teknoloji #bilim #fyp #keşfet"
        upload_video(filename=str(output), description=description, cookies=str(COOKIES_FILE))
    except Exception as exc:
        print(f"TikTok yükleme hatası: {type(exc).__name__}: {exc}")
        return

    history.add(str(selected["id"]))
    save_history(history)
    print(f"Video üretildi ve yükleme çağrısı tamamlandı: {video_path}")


if __name__ == "__main__":
    run_bot()
