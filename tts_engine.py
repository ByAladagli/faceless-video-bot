import edge_tts
import asyncio
import os

VOICE = "tr-TR-AhmetNeural" # Alternatif: tr-TR-EmelNeural

async def generate_audio_and_subs(text, output_audio="assets/audio.mp3", output_subs="assets/subs.srt"):
    """Metni sese dönüştürür ve kelime kelime altyazı (SRT) üretir."""
    
    # Hedef klasörü oluştur
    os.makedirs(os.path.dirname(output_audio), exist_ok=True)
    
    communicate = edge_tts.Communicate(text, VOICE)
    submaker = edge_tts.SubMaker()
    
    with open(output_audio, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                # Altyazı için kelime/cümle sınırlarını kaydet
                submaker.feed(chunk)

    srt_content = submaker.get_srt()
    
    with open(output_subs, "w", encoding="utf-8") as file:
        file.write(srt_content)
        
    return output_audio, output_subs

def create_tts(text, audio_path="assets/audio.mp3", subs_path="assets/subs.srt"):
    """Asenkron fonksiyonu senkron olarak çağırmak için sarıcı."""
    asyncio.run(generate_audio_and_subs(text, audio_path, subs_path))
    return audio_path, subs_path

if __name__ == "__main__":
    # Test amaçlı
    test_metni = "Merhaba, bu otomatik olarak üretilen yüzsüz bir videodur. Sadece kod ile yapılmıştır."
    create_tts(test_metni)
    print("Test ses ve altyazı dosyaları assets/ klasörüne kaydedildi.")
