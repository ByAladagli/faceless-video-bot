# Faceless Video Bot

Türkçe dikey video üretimi ve tarayıcı tabanlı yayın otomasyonu. Mevcut prototipte Edge TTS + FFmpeg video üretimi, Google News RSS içerik toplama, 30 günlük takvim, SQLite yayın geçmişi ve Selenium tabanlı YouTube/TikTok/Instagram yayın akışı bulunur.

## Gereksinimler
- Python 3.10+
- Google Chrome
- FFmpeg ve FFprobe PATH üzerinde
- Kaynak arka plan videosu: `assets/background.mp4` veya `backend/background.mp4`

## Windows kurulumu
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

İlk olarak `assets/background.mp4` dosyasını yerleştirin veya mevcut `backend/background.mp4` dosyasını kullanın. Sonra:
```powershell
python scheduler.py
```
İlk açılışta 30 günlük plan `data/monthly_plan.json` dosyasına, yayın durumu `data/publishing.sqlite3` veritabanına kaydedilir. Zamanlayıcı her gün Türkiye saatiyle 19:00'da çalışır. Bilgisayarın/sunucunun açık ve internete bağlı olması gerekir.

## Tarayıcı oturumları
İlk çalıştırmada Selenium her platform için ayrı kalıcı Chrome profili oluşturur:
- `browser_profiles/youtube`
- `browser_profiles/tiktok`
- `browser_profiles/instagram`

Her platform hesabına tarayıcıda normal şekilde manuel giriş yapın; sonra otomasyonu yeniden çalıştırın. İki aşamalı doğrulama/CAPTCHA atlatılmaz. `SELENIUM_HEADLESS=1` yalnızca oturumlar hazırlandıktan sonra denenmelidir. Arayüz seçicileri platform güncellemeleriyle bozulabilir; her başarısız görev loglanır ve otomatik olarak başarılı sayılmaz.

## Ayarlar
- `PUBLISH_TIME=19:00`
- `BOT_TIMEZONE=Europe/Istanbul`
- `SELENIUM_PROFILE_DIR=browser_profiles`
- `SELENIUM_WAIT_SECONDS=25`
- `SELENIUM_HEADLESS=0`

## Çalışma davranışı
- Aynı günlük video dosyası üç platforma ayrı ayrı gönderilir.
- Başarılı platform görevi tekrar denenmez; başarısız görev `retry` durumunda kalır.
- Yayın geçmişi SQLite'a yazılır. Bilgisayar günlerce kapalı kalırsa geçmiş yayınlar bir anda topluca yüklenmez.
- Google News RSS erişilemezse sahte haber üretilmez.
- Plan oluşturma sırasında eldeki benzersiz haber sayısı 30'dan azsa plan aynı konuları döndürebilir; yayın öncesinde `data/monthly_plan.json` dosyasını kontrol edin.
- Şu an platformlardan otomatik video indirme/çekme özelliği tamamlanmış değildir. Kaynak video kullanımı için yalnızca kendi videonuzu veya yeniden kullanım izniniz olan dosyaları kullanın. Güncel akış haber metninden Türkçe anlatım videosu üretir.
- Selenium ile yükleme platformların resmî API'lerini kullanmaz; arayüz akışları kararsız olabilir. Yayın onayını kontrol edin.

## Web arayüzü
Mevcut metin-video API'si:
```powershell
python api.py
```
Ön yüz:
```powershell
cd frontend
npm ci
npm run dev
```

## Güvenlik
`browser_profiles/`, `.env`, SQLite veritabanı ve oluşturulan medya dosyalarını Git'e eklemeyin. Tarayıcı profilleri oturum çerezleri içerir. Bu otomasyonu yalnızca kendi hesaplarınızda ve platform kurallarına uygun biçimde kullanın.
