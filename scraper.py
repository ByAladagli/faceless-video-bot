import hashlib
import re
import urllib.request
from html import unescape

import feedparser
from deep_translator import GoogleTranslator

# No Reddit dependency: use public Google News RSS search results.
NEWS_RSS_URL = (
    "https://news.google.com/rss/search?q=(yapay+zeka+OR+teknoloji+OR+bilim)"
    "&hl=tr&gl=TR&ceid=TR:tr"
)
BANNED_WORDS = [
    "intihar", "tecavüz", "porno", "suikast", "bombalı saldırı",
    "self-harm", "suicide", "rape", "pornography",
]


def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", unescape(text or ""))
    text = re.sub(r"https?://\S+", "", text)
    return " ".join(text.split())


def check_banned_words(text: str) -> bool:
    normalized = f" {clean_text(text).casefold()} "
    return any(f" {word.casefold()} " in normalized for word in BANNED_WORDS)


def _fetch_feed():
    request = urllib.request.Request(
        NEWS_RSS_URL,
        headers={"User-Agent": "FacelessVideoBot/1.0 (RSS reader)"},
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        payload = response.read(2 * 1024 * 1024 + 1)
    if len(payload) > 2 * 1024 * 1024:
        raise ValueError("RSS yanıtı 2 MB sınırını aştı.")
    return feedparser.parse(payload)


def get_content():
    """Return recent technology/science headlines from Google News RSS.

    The bot does not fabricate fallback stories when a source is unavailable.
    """
    try:
        feed = _fetch_feed()
    except Exception as exc:
        print(f"Haber kaynağına ulaşılamadı: {type(exc).__name__}: {exc}")
        return []

    entries = []
    seen = set()
    translator = GoogleTranslator(source="auto", target="tr")
    for entry in feed.entries:
        title = clean_text(getattr(entry, "title", ""))
        summary = clean_text(getattr(entry, "summary", ""))
        link = str(getattr(entry, "link", "") or "")
        stable_key = link or title
        if not title or stable_key in seen or check_banned_words(title):
            continue
        if len(title) < 15 or len(title) > 300:
            continue
        seen.add(stable_key)

        # RSS titles are usually Turkish for this query; translate only when needed.
        try:
            translated_title = translator.translate(title) if not any(
                char in "çğıöşüÇĞİÖŞÜ" for char in title
            ) else title
        except Exception:
            translated_title = title

        text = clean_text(f"{translated_title}. {summary}" if summary else translated_title)
        if check_banned_words(text):
            continue
        item_id = hashlib.sha256(stable_key.encode("utf-8")).hexdigest()[:24]
        entries.append({
            "id": item_id,
            "original_text": title,
            "turkish_text": text,
            "link": link,
            "source": "Google News RSS",
        })
        if len(entries) >= 20:
            break
    return entries


if __name__ == "__main__":
    for index, item in enumerate(get_content()[:5], start=1):
        print(f"{index}. {item['turkish_text']}\n{item['link']}\n")
