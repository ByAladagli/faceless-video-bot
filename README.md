# Yüzsüz (Faceless) YouTube Shorts & TikTok Üretici Botu 🤖

Bu proje, tamamen otomatik (otonom) bir şekilde çalışarak "Yüzsüz" (Faceless) kısa videolar üreten ve bunları TikTok / YouTube Shorts'a yüklemeye hazır hale getiren bir yapay zeka botudur.

## 🌟 Özellikler

- **Tam Otomatik İçerik Bulucu:** Reddit'in popüler başlıklarından (`r/Showerthoughts` vb.) İngilizce metinleri otomatik çeker.
- **Akıllı Çeviri & Filtreleme:** İngilizce içerikleri yapay zeka ile Türkçe'ye çevirir. Küfür ve yasaklı kelime filtresinden geçirerek temiz bir içerik oluşturur.
- **Gerçekçi Yapay Zeka Ses (TTS):** Microsoft Edge'in yüksek kaliteli *Aria* sinirsel sesiyle metni seslendirir.
- **Dinamik Altyazılar:** Senkronize, TikTok tarzı kalın sarı fontlu ve siyah gölgeli, kelime-kelime/cümle-cümle altyazılar (SRT) üretir.
- **FFmpeg ile Otomatik Montaj:** Videoyu dikey formata (9:16) uygun olarak kırpar, arkaplan videosu üzerine sesi ve altyazıları kusursuz şekilde yerleştirir.
- **Otomatik Yükleme Altyapısı:** İşlem bitiminde videoyu TikTok API veya çerezler üzerinden yükleyebilecek temel yapıya sahiptir.

## ⚙️ Kurulum (Nasıl Çalıştırılır?)

Bu botu kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları sırasıyla izleyin.

### 1. Gereksinimler
- **Python 3.9+** (Sisteminizde yüklü olmalıdır)
- **FFmpeg** (Video montajı için gereklidir, sistem PATH'inize ekli olmalıdır)

### 2. İndirme ve Bağımlılıkların Yüklenmesi
Projeyi indirdikten sonra, terminali (veya komut satırını) açın ve projenin bulunduğu klasöre gidin:

```bash
cd faceless-video-bot
pip install -r requirements.txt
```

### 3. Arkaplan Videosu Ayarlama (Opsiyonel)
Bot, videonun arka planına koymak için `assets/background.mp4` adlı bir dosyaya ihtiyaç duyar. 
Projede standart bir arka plan bulunur. Ancak kendi "parkur", "Minecraft", "GTA" veya "tatmin edici (satisfying)" videolarınızı bu klasöre `background.mp4` adıyla atarak videoları özelleştirebilirsiniz.

### 4. Botu Çalıştırma
Tüm hazırlıklar tamamlandığında botu çalıştırmak çok basittir:

```bash
python main.py
```

Sistem otomatik olarak:
1. Hikayeyi çekecek ve Türkçeye çevirecek.
2. Sesi ve altyazıyı oluşturacak.
3. Videoyu renderlayıp `assets/final_video.mp4` olarak çıktı verecektir!

## ⚠️ Uyarılar ve Sınırlamalar
- **TikTok Yüklemesi İçin:** Otomatik yükleme özelliğinin çalışması için TikTok hesabınıza giriş yaptığınız tarayıcı çerezlerinizi bir `cookies.txt` dosyası olarak ana dizine eklemeniz gerekebilir. Eğer bu dosya yoksa bot videoyu üretir ancak yükleme adımını atlar.

---
*Geliştirici: Bu sistem tamamen otonom çalışması amacıyla otomatik içerik üreticileri için tasarlanmıştır.*
