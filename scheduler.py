"""Daily 19:00 workflow: choose content, render once, publish to all 3 platforms."""
from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

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
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_DIR / "scheduler.log", encoding="utf-8")],
)
log = logging.getLogger("faceless-scheduler")
PLATFORMS = ("youtube", "tiktok", "instagram")


def ensure_month_plan(force: bool = False) -> list[dict]:
    plan = [] if force else load_plan()
    if plan:
        return plan
    items = get_content()
    if not items:
        raise RuntimeError("İçerik kaynağından içerik alınamadı; boş/sahte plan oluşturulmadı.")
    # Build a month plan from unique available stories. If fewer than 30 exist,
    # the planner will rotate them; see README note on editorial quality.
    plan = create_month_plan(items, days=30)
    save_plan(plan)
    log.info("30 günlük plan oluşturuldu: %s", ROOT / "data" / "monthly_plan.json")
    return plan


def _render_slot(slot: dict) -> Path:
    existing = Path(slot.get("video_path") or "")
    if existing.is_file() and existing.stat().st_size > 0:
        return existing
    ASSETS.mkdir(parents=True, exist_ok=True)
    stem = slot["content_id"]
    audio = ASSETS / f"{stem}.mp3"
    subtitles = ASSETS / f"{stem}.srt"
    output = ASSETS / f"{stem}.mp4"
    if not output.is_file() or output.stat().st_size == 0:
        audio_path, subtitle_path = create_tts(slot["content"], str(audio), str(subtitles))
        make_video(audio_path, subtitle_path, output)
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("Video oluşturma başarısız: çıktı dosyası yok veya boş.")
    return output


def _slot_for_content(content_id: str, plan: list[dict]) -> dict | None:
    return next((slot for slot in plan if slot.get("content_id") == content_id), None)


def run_due_once() -> None:
    plan = ensure_month_plan()
    pending = due_publications()
    if not pending:
        log.info("Yayın saati gelmiş bekleyen görev yok.")
        return
    rendered: dict[str, Path] = {}
    for job in pending:
        job_id = job["id"]
        content_id = job["content_id"]
        slot = _slot_for_content(content_id, plan)
        if not slot:
            update_publication(job_id, "failed", error="Plan dosyasında içerik bulunamadı.")
            continue
        try:
            # Reuse one rendered file for the three platforms on the same date.
            if content_id not in rendered:
                rendered[content_id] = _render_slot(slot)
            result = publish(job["platform"], rendered[content_id], job["title"], job["description"])
            update_publication(job_id, "published", result=result, video_path=str(rendered[content_id]))
            log.info("Yayın gönderildi/doğrulandı: platform=%s content=%s", job["platform"], content_id)
        except PublishError as exc:
            update_publication(job_id, "retry", error=str(exc), video_path=str(rendered.get(content_id, "")) or None)
            log.exception("Platform yüklemesi başarısız: %s", job["platform"])
        except Exception as exc:
            update_publication(job_id, "retry", error=f"{type(exc).__name__}: {exc}")
            log.exception("Görev başarısız: %s", job_id)


def main() -> None:
    ensure_month_plan()
    hour, minute = map(int, os.getenv("PUBLISH_TIME", "19:00").split(":"))
    scheduler = BlockingScheduler(timezone=TZ)
    scheduler.add_job(run_due_once, "cron", hour=hour, minute=minute, id="daily-publish", max_instances=1, coalesce=True)
    log.info("Zamanlayıcı başladı; her gün %02d:%02d (%s).", hour, minute, TZ)
    # Run overdue work after startup as well, useful after machine downtime.
    run_due_once()
    scheduler.start()


if __name__ == "__main__":
    main()
