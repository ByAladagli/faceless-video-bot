import asyncio
import subprocess
import os

async def generate_video(topic: str, output_path: str = "output.mp4"):
    # 1. Metin (Mock-AI)
    # Normalde burada OpenAI ile konu hakkında bir metin üretilir.
    script = f"Biliyor muydunuz? {topic} hakkında ilginç bir bilgi vermek istiyorum. Bu konu dünya genelinde giderek popülerleşiyor ve teknoloji dünyasında büyük yankı uyandırıyor. Daha fazlası için videoyu beğenmeyi unutmayın!"
    
    # 2. TTS (Metinden Sese)
    audio_path = "temp_audio.mp3"
    print(f"[1/3] Ses üretiliyor: {audio_path}")
    
    # edge-tts CLI ile ses üret
    # Türkçe ses örneği: tr-TR-AhmetNeural (Erkek) veya tr-TR-EmelNeural (Kadın)
    tts_cmd = [
        "edge-tts",
        "--text", script,
        "--voice", "tr-TR-AhmetNeural",
        "--write-media", audio_path
    ]
    subprocess.run(tts_cmd, check=True)
    
    # 3. Video ve Sesi Birleştir (FFmpeg)
    print(f"[2/3] Ses ve Video birleştiriliyor...")
    bg_video = "background.mp4"
    
    # FFmpeg komutu:
    # -stream_loop -1 : Videoyu ses bitene kadar döngüye sok (eğer video kısa ise)
    # -i bg_video : Görüntü dosyası
    # -i audio_path : Ses dosyası
    # -c:v copy : Görüntüyü yeniden kodlamadan kopyala (Çok hızlıdır)
    # -c:a aac : Sesi AAC formatına çevir (standart)
    # -shortest : En kısa olan dosya bittiğinde (yani ses bittiğinde) kes.
    
    ffmpeg_cmd = [
        "ffmpeg",
        "-y", # Üzerine yaz
        "-stream_loop", "-1",
        "-i", bg_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_path
    ]
    
    subprocess.run(ffmpeg_cmd, check=True)
    print(f"[3/3] Video başarıyla üretildi: {output_path}")
    
    # Geçici dosyayı temizle
    if os.path.exists(audio_path):
        os.remove(audio_path)
        
    return {"script": script, "video_url": f"/download/{output_path}"}

if __name__ == "__main__":
    # Test
    asyncio.run(generate_video("Yapay Zeka ve Gelecek", "test_out.mp4"))
