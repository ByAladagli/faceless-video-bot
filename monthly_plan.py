"""30-day Turkish publishing calendar and persistent SQLite job state."""
from __future__ import annotations
import hashlib, json, os, sqlite3
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DB_PATH = Path(os.getenv("BOT_DB_PATH", str(DATA_DIR / "publishing.sqlite3"))).resolve()
PLAN_PATH = Path(os.getenv("BOT_PLAN_PATH", str(DATA_DIR / "monthly_plan.json"))).resolve()
TZ = ZoneInfo(os.getenv("BOT_TIMEZONE", "Europe/Istanbul"))
PUBLISH_TIME = os.getenv("PUBLISH_TIME", "19:00")

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""CREATE TABLE IF NOT EXISTS publications (
      id TEXT PRIMARY KEY, scheduled_at TEXT NOT NULL, content_id TEXT NOT NULL,
      video_path TEXT, title TEXT NOT NULL, description TEXT NOT NULL,
      platform TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'planned',
      attempts INTEGER NOT NULL DEFAULT 0, result_json TEXT, last_error TEXT,
      updated_at TEXT NOT NULL)""")
    db.commit()
    return db

def _hash(*parts):
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:32]

def metadata(item):
    title = " ".join(str(item.get("title") or item.get("original_text") or "Günün kısa bilgisi").split())[:95]
    body = " ".join(str(item.get("turkish_text") or item.get("summary") or title).split())
    link = str(item.get("link") or item.get("source_url") or "")
    desc = f"{body}\n\nKaynak ve ek bilgiler: {link}\n\n#Türkçe #Bilgi #Teknoloji"
    return title, desc[:4900]

def create_month_plan(items: list[dict], start_date: date | None = None, days: int = 30):
    if not items:
        raise RuntimeError("Plan oluşturmak için kaynak içerik bulunamadı.")
    start = start_date or datetime.now(TZ).date()
    hour, minute = map(int, PUBLISH_TIME.split(":"))
    result = []
    for i in range(days):
        item = items[i % len(items)]
        cid = str(item.get("id") or _hash(str(item)))
        title, description = metadata(item)
        scheduled = datetime.combine(start + timedelta(days=i), time(hour, minute), TZ)
        result.append({
          "id": _hash(cid, scheduled.isoformat()), "scheduled_at": scheduled.isoformat(),
          "content_id": cid, "source": item.get("source", "unknown"),
          "source_url": item.get("link", item.get("source_url", "")),
          "title": title, "description": description,
          "content": item.get("turkish_text") or item.get("summary") or title,
          "video_path": item.get("video_path", ""),
          "content_mode": item.get("content_mode", "original_narration"),
          "license_note": item.get("license_note", ""),
          "platforms": ["youtube", "tiktok", "instagram"]
        })
    return result

def save_plan(slots):
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = PLAN_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(slots, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(PLAN_PATH)
    with connect() as db:
        for slot in slots:
            for platform in slot["platforms"]:
                db.execute("""INSERT OR IGNORE INTO publications
                (id,scheduled_at,content_id,video_path,title,description,platform,status,updated_at)
                VALUES (?,?,?,?,?,?,?,'planned',?)""",
                (_hash(slot["id"], platform), slot["scheduled_at"], slot["content_id"],
                 slot.get("video_path") or None, slot["title"], slot["description"],
                 platform, datetime.now(TZ).isoformat()))
        db.commit()

def load_plan():
    if not PLAN_PATH.is_file(): return []
    data = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []

def due_publications(now=None):
    current = (now or datetime.now(TZ)).astimezone(TZ).isoformat()
    with connect() as db:
        rows = db.execute("""SELECT * FROM publications WHERE scheduled_at <= ?
        AND status IN ('planned','retry') ORDER BY scheduled_at,platform""", (current,)).fetchall()
    return [dict(r) for r in rows]

def update_publication(job_id, status, result=None, error=None, video_path=None):
    with connect() as db:
        db.execute("""UPDATE publications SET status=?, attempts=attempts+1,
        result_json=?,last_error=?,video_path=COALESCE(?,video_path),updated_at=? WHERE id=?""",
        (status, json.dumps(result, ensure_ascii=False) if result else None, error,
         video_path, datetime.now(TZ).isoformat(), job_id))
        db.commit()
