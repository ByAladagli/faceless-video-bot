import os
import random
import subprocess
import urllib.request
import math

# Varsayılan arka plan videosu (Telifsiz Minecraft Parkur vb. bir kaynak eklenebilir)
# Şimdilik örnek olarak küçük bir video indiriyoruz (İlk çalışmada)
BG_VIDEO_URL = "https://www.youtube.com/watch?v=n_Dv4JMiwK8" # Minecraft Parkour (Telifsiz uzun video)
BG_VIDEO_PATH = "assets/background.mp4"

FFMPEG_PATH = r"C:\Users\mehme\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
FFPROBE_PATH = r"C:\Users\mehme\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffprobe.exe"

def download_bg_video():
    if not os.path.exists(BG_VIDEO_PATH):
        print("Arka plan videosu YouTube'dan indiriliyor (Sadece ilk kurulumda çalışır)...")
        os.makedirs(os.path.dirname(BG_VIDEO_PATH), exist_ok=True)
        # Sadece video indir (sesi kapat, çünkü kendi sesimizi koyacağız), max 720p/1080p
        cmd = ["yt-dlp", "-f", "bestvideo[height<=1080][ext=mp4]", "-o", BG_VIDEO_PATH, BG_VIDEO_URL]
        try:
            subprocess.run(cmd, check=True)
            print("İndirme tamamlandı!")
        except Exception as e:
            print(f"Video indirilemedi ({e}). Test için yer tutucu video oluşturuluyor...")
            # Eğer indiremezse, FFmpeg ile 60 saniyelik siyah/mavi bir yer tutucu video oluştur
            fallback_cmd = [
                FFMPEG_PATH, "-y", "-f", "lavfi", 
                "-i", "color=c=blue:s=1080x1920:d=60", 
                "-c:v", "libx264", BG_VIDEO_PATH
            ]
            subprocess.run(fallback_cmd, check=True)
            print("Yer tutucu video başarıyla oluşturuldu. (Lütfen daha sonra assets/background.mp4 dosyasını kendi videonuzla değiştirin.)")

def get_video_duration(video_path):
    """FFprobe kullanarak video süresini saniye cinsinden döndürür."""
    cmd = [
        FFPROBE_PATH, "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", video_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    return float(result.stdout.strip())

def make_video(audio_path, srt_path, output_path="assets/final_video.mp4"):
    """FFmpeg kullanarak ses, arka plan ve altyazıyı birleştirir."""
    
    download_bg_video()
    
    bg_duration = get_video_duration(BG_VIDEO_PATH)
    audio_duration = get_video_duration(audio_path)
    
    # Arka plan videosunun neresinden başlanacağını rastgele seç
    # Ses süresi arka plandan uzun olmamalı
    if bg_duration > audio_duration:
        start_time = random.uniform(0, bg_duration - audio_duration)
    else:
        start_time = 0
        
    # FFmpeg Subtitle formatını düzeltmek için (Windows path slash sorunu)
    # ffmpeg'e Windows mutlak yolunu verirken \ işaretlerini \\ yapmalı ve : işaretini \: olarak kaçırmalıyız.
    safe_srt_path = os.path.abspath(srt_path).replace('\\', '\\\\').replace(':', '\\:')
        
    # FFmpeg komutu: 
    # 1. Başlangıç süresini (-ss) ayarla ve videoyu kes (-t)
    # 2. 9:16 oranında (Örn: 1080x1920) ortaya hizalayarak kırp (crop)
    # 3. Altyazıları göm (subtitles) - Kalın, Sarı renk, Siyah gölge (Shorts stili)
    
    vf_filter = (
        f"crop=ih*(9/16):ih,"
        f"scale=1080:1920,"
        f"subtitles='{safe_srt_path}':force_style='Fontname=Arial,Fontsize=24,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=40'"
    )
    
    cmd = [
        FFMPEG_PATH, "-y",
        "-ss", str(start_time),
        "-t", str(math.ceil(audio_duration)),
        "-i", BG_VIDEO_PATH,
        "-i", audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-vf", vf_filter,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]
    
    print("Video montajlanıyor... (Bu işlem işlemci hızına göre 1-3 dk sürebilir)")
    subprocess.run(cmd, check=True)
    print(f"Video başarıyla üretildi: {output_path}")
    return output_path

if __name__ == "__main__":
    # Test amaçlı
    # audio.mp3 ve subs.srt 'assets' klasöründe olmalı
    if os.path.exists("assets/audio.mp3") and os.path.exists("assets/subs.srt"):
        make_video("assets/audio.mp3", "assets/subs.srt")
    else:
        print("Lütfen önce tts_engine.py'yi çalıştırarak test sesini üretin.")
