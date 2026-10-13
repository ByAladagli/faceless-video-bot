# Faceless Video Bot

Türkçe teknoloji/bilim haber başlıklarından dikey video üreten bir Python prototipi. İki çalışma yolu vardır:

- **Web arayüzü/API:** Kullanıcının girdiği metni Edge TTS ile seslendirir, altyazı oluşturur ve FFmpeg ile MP4 üretir.
- **CLI botu:** Google News RSS'den içerik seçer, video üretir ve yalnızca yerel `cookies.txt` varsa TikTok yüklemesini dener.

## Gereksinimler
- Python 3.10+
- Node.js 20+
- FFmpeg ve FFprobe PATH üzerinde

## Kurulum
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Arka plan videosu `assets/background.mp4` veya `backend/background.mp4` konumunda bulunmalıdır.

## Web arayüzünü çalıştırma
Terminal 1:
```powershell
python api.py
```
API: http://127.0.0.1:8001/api/health

Terminal 2:
```powershell
cd frontend
npm ci
npm run dev
```
Arayüz varsayılan olarak http://localhost:5173 adresinde açılır. API adresini değiştirmek için frontend ortamında `VITE_API_BASE_URL` tanımlayın.

## CLI botunu çalıştırma
```powershell
python main.py
```
Video `assets/final_video.mp4` olarak üretilir. TikTok yüklemesi yalnızca `cookies.txt` bulunduğunda denenir. Başarısız/atlanmış yükleme geçmişe yazılmaz.

## Davranış ve sınırlamalar
- İçerik kaynağı Google News RSS'dir; Reddit kullanılmaz.
- RSS erişilemezse sahte/yedek hikâye üretmek yerine işlem durur.
- Web arayüzü girilen metni doğrudan seslendirir; LLM senaryo üretimi henüz entegre değildir.
- Otomatik sosyal paylaşım, yayın planlayıcı, görev kuyruğu, içerik onay ekranı ve kalıcı üretim geçmişi henüz tamamlanmamıştır.
- `cookies.txt`, API anahtarları ve üretilen medya Git'e eklenmemelidir.
- Web API varsayılan olarak yalnızca localhost'ta dinler. İnternete açmadan önce kimlik doğrulama, oran sınırlaması, iş kuyruğu ve çıktı saklama politikası ekleyin.
