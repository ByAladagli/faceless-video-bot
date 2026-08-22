import feedparser
from deep_translator import GoogleTranslator
import re

# Ayarlar
REDDIT_RSS_URL = "https://www.reddit.com/r/Showerthoughts/top/.rss?t=day"
BANNED_WORDS = ["ölüm", "intihar", "seks", "porno", "kan", "tecavüz", "suikast", "kill", "die", "suicide", "murder"]

def clean_text(text):
    # HTML etiketlerini ve linkleri temizle
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'http\S+', '', text)
    # Gereksiz boşlukları temizle
    text = " ".join(text.split())
    return text

def check_banned_words(text):
    text_lower = text.lower()
    for word in BANNED_WORDS:
        if word in text_lower:
            return True
    return False

def get_content():
    """Reddit'ten günün en iyi gönderilerini çeker ve Türkçe olarak döndürür."""
    feed = feedparser.parse(REDDIT_RSS_URL)
    
    entries = []
    
    for entry in feed.entries:
        title = clean_text(entry.title)
        
        # Filtreye takılanları atla
        if check_banned_words(title):
            continue
            
        # Çok kısa (15 karakterden az) veya çok uzun (300 karakterden fazla) ise atla
        if len(title) < 15 or len(title) > 300:
            continue
            
        try:
            # Türkçeye çevir
            translated_title = GoogleTranslator(source='en', target='tr').translate(title)
            
            # Çeviride sorunlu kelime var mı diye tekrar kontrol et
            if check_banned_words(translated_title):
                continue
                
            entries.append({
                "id": entry.id,
                "original_text": title,
                "turkish_text": translated_title,
                "link": entry.link
            })
            
        except Exception as e:
            print(f"Çeviri hatası: {e}")
            continue

    if not entries:
        # Eğer RSS'den veri çekilemezse (Örn: Rate limit) yedek bir hikaye kullan
        entries.append({
            "id": "fallback_test_001",
            "original_text": "This is a fallback test story because Reddit blocked the request.",
            "turkish_text": "Dünyadaki en ilginç şeylerden biri, her insanın hayatında en az bir kez tamamen yabancı birinin arka plan karakteri olmasıdır.",
            "link": ""
        })
        
    return entries

if __name__ == "__main__":
    # Test amaçlı
    icerikler = get_content()
    for i, icerik in enumerate(icerikler[:3]):
        print(f"{i+1}. Orijinal: {icerik['original_text']}")
        print(f"{i+1}. Türkçe: {icerik['turkish_text']}\n")
