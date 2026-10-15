"""Daily 19:00 workflow: render once and publish to all three platforms."""
import logging, os
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from monthly_plan import TZ, create_month_plan, due_publications, load_plan, save_plan, update_publication
from scraper import get_content
from selenium_publisher import PublishError, publish
from tts_engine import create_tts
from video_maker import make_video

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_DIR / "scheduler.log", encoding="utf-8")])
log = logging.getLogger("faceless-scheduler")

def ensure_month_plan():
    plan = load_plan()
    if plan: return plan
    items = get_content()
    if not items: raise RuntimeError("İçerik kaynağı boş; sahte plan oluşturulmadı.")
    plan = create_month_plan(items, days=30)
    save_plan(plan)
    log.info("30 günlük plan kaydedildi: %s", ROOT / "data" / "monthly_plan.json")
    return plan

def render_slot(slot):
    supplied = Path(slot.get("video_path") or "")
    if supplied.is_file() and supplied.stat().st_size:
        return supplied
    ASSETS.mkdir(parents=True, exist_ok=True)
    stem = slot["content_id"]
    audio, subtitles, output = ASSETS / f"{stem}.mp3", ASSETS / f"{stem}.srt", ASSETS / f"{stem}.mp4"
    if not output.is_file() or not output.stat().st_size:
        audio_path, subtitle_path = create_tts(slot["content"], str(audio), str(subtitles))
        make_video(audio_path, subtitle_path, output)
    if not output.is_file() or not output.stat().st_size:
        raise RuntimeError("Video çıktısı yok veya boş.")
    return output

def run_due_once():
    plan = ensure_month_plan()
    today = datetime.now(TZ).date()
    # Do not dump missed days in a burst if the host was offline.
    pending = [job for job in due_publications() if datetime.fromisoformat(job["scheduled_at"]).astimezone(TZ).date() == today]
    if not pending:
        log.info("Bugün için yayın saati gelmiş bekleyen görev yok.")
        return
    slot_by_content = {slot["content_id"]: slot for slot in plan}
    rendered = {}
    for job in pending:
        cid, jid = job["content_id"], job["id"]
        slot = slot_by_content.get(cid)
        if not slot:
            update_publication(jid, "failed", error="Plan dosyasında içerik bulunamadı.")
            continue
        try:
            if cid not in rendered: rendered[cid] = render_slot(slot)
            result = publish(job["platform"], rendered[cid], job["title"], job["description"])
            update_publication(jid, "published", result=result, video_path=str(rendered[cid]))
            log.info("Gönderim sonucu doğrulandı: %s", job["platform"])
        except PublishError as exc:
            update_publication(jid, "retry", error=str(exc), video_path=str(rendered.get(cid, "")) or None)
            log.exception("Platform yüklemesi başarısız: %s", job["platform"])
        except Exception as exc:
            update_publication(jid, "retry", error=f"{type(exc).__name__}: {exc}")
            log.exception("Görev başarısız: %s", jid)

def main():
    ensure_month_plan()
    hour, minute = map(int, os.getenv("PUBLISH_TIME", "19:00").split(":"))
    scheduler = BlockingScheduler(timezone=TZ)
    scheduler.add_job(run_due_once, "cron", hour=hour, minute=minute, id="daily-publish", max_instances=1, coalesce=True)
    log.info("Zamanlayıcı başladı: her gün %02d:%02d (%s).", hour, minute, TZ)
    scheduler.start()

if __name__ == "__main__": main()
