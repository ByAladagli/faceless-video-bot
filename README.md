# Faceless Video Bot

Türkçe teknoloji/bilim haber başlıklarından dikey video üreten bir Python prototipi. Google News RSS ile içerik bulur, Edge TTS ile ses/altyazı üretir, FFmpeg ile video montajlar. TikTok yüklemesi yalnızca yerel `cookies.txt` mevcutsa denenir.

## Gereksinimler
- Python 3.10+
- FFmpeg ve FFprobe PATH üzerinde
- TikTok yükleme için, yalnızca hesabınızın izin verdiği resmi/uyumlu bir kimlik doğrulama yöntemi

## Kurulum
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Arka plan videosu `assets/background.mp4` veya `backend/background.mp4` konumunda bulunmalıdır. Video üretimi için çıktı `assets/final_video.mp4` olur. FFmpeg/FFprobe özel bir bilgisayar yoluna sabitlenmemiştir; PATH üzerinden bulunur.

## Davranış ve sınırlamalar
- İçerik kaynağı Google News RSS'dir; Reddit kullanılmaz.
- RSS erişilemezse sahte/yedek hikâye üretmek yerine işlem durur.
- TikTok çerezi yoksa video yine üretilir, ancak içerik geçmişe eklenmez; yükleme daha sonra tekrar denenebilir.
- Başarısız yükleme geçmişe yazılmaz.
- Bu sürüm haber başlığı/özetinden kısa video üretir; tam senaryo yazımı, kaynak doğrulama, editoryal onay kuyruğu, güvenilir yayın API entegrasyonu ve zamanlanmış worker mimarisi henüz tamamlanmamıştır.
- `cookies.txt`, API anahtarları ve üretilen medya Git'e eklenmemelidir.

## Frontend
`frontend` klasörü ayrı bir Vite/React arayüzüdür. Python video üretim hattına bağlı bir backend API'si şu anda tamamlanmış değildir; arayüzü çalıştırmak tek başına otomatik üretim başlatmaz.
