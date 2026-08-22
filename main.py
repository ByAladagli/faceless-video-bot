import json
import os
import time
from scraper import get_content
from tts_engine import create_tts
from video_maker import make_video
from tiktok_uploader.upload import upload_video

HISTORY_FILE = "history.json"
TIKTOK_COOKIES = "cookies.txt"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

def run_bot():
    print("Bot başlatılıyor...")
    
    # 1. İçerikleri çek
    print("İçerikler Reddit'ten çekiliyor...")
    entries = get_content()
    
    if not entries:
        print("Uygun içerik bulunamadı veya tüm içerikler filtrelendi.")
        return
        
    history = load_history()
    selected_entry = None
    
    for entry in entries:
        if entry["id"] not in history:
            selected_entry = entry
            break
            
    if not selected_entry:
        print("Yeni bir hikaye bulunamadı. Hepsi zaten yüklenmiş.")
        return
        
    print(f"\nSeçilen Hikaye: {selected_entry['original_text']}")
    print(f"Türkçesi: {selected_entry['turkish_text']}\n")
    
    # 2. Ses ve Altyazı Üret
    print("Yapay Zeka Ses ve Altyazı üretiliyor...")
    audio_path, subs_path = create_tts(selected_entry["turkish_text"])
    
    # 3. Video Montajla
    final_video_path = make_video(audio_path, subs_path)
    
    # 4. TikTok'a Yükle
    if os.path.exists(TIKTOK_COOKIES) and os.path.exists(final_video_path):
        print("TikTok'a yükleniyor...")
        description = f"{selected_entry['turkish_text']} \n\n#ilginçbilgiler #hikaye #reddit #fyp #keşfet"
        
        try:
            # tiktok-uploader kütüphanesi
            upload_video(
                filename=final_video_path,
                description=description,
                cookies=TIKTOK_COOKIES
            )
            print("Video başarıyla TikTok'a yüklendi!")
            
            # Başarılı olursa geçmişe kaydet
            history.append(selected_entry["id"])
            save_history(history)
            
        except Exception as e:
            print(f"Yükleme hatası: {e}")
    else:
        print("TikTok çerezleri (cookies.txt) bulunamadığı için yükleme atlandı.")
        # Sadece video üretilmiş oldu, test için geçmişe de ekleyebiliriz
        history.append(selected_entry["id"])
        save_history(history)

if __name__ == "__main__":
    run_bot()
