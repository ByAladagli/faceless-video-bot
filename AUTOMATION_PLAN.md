# Otomatik yayın planı

- Her gün 19:00 Europe/Istanbul saatinde bir video hazırlanır.
- Aynı video YouTube, TikTok ve Instagram hesaplarına ayrı ayrı yüklenir.
- Tarayıcı otomasyonu Selenium ile yürütülür; resmî API anahtarı gerekmez.
- İlk kurulumda her platformun hesabına kullanıcı tarafından normal şekilde giriş yapılır. CAPTCHA/2FA atlatılmaz.
- Kaynak videolar yalnızca açıkça yeniden kullanım izni bulunan veya kullanıcı tarafından sağlanan dosyalardan alınır. Aksi durumda haber metninden özgün anlatım videosu üretilir.
- Her platformun sonucu ayrı kaydedilir. Hata alan platform tekrar denenir; başarılı platform tekrar yüklenmez.
- GitHub kod deposudur; zamanlayıcı için açık kalan bilgisayar/sunucu gerekir.

Mevcut `main.py` prototipinden üretim otomasyonuna geçişte 30 günlük içerik planı, SQLite yayın geçmişi, günlük zamanlayıcı, kalıcı Chrome profilleri ve yükleme doğrulaması eklenmelidir.
