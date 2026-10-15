# Çok kullanıcılı VDS kurulumu

## Mevcut durum: doğrudan herkese açmayın

Mevcut repo bir prototiptir: React formu metin alır, FastAPI video üretir; yayın otomasyonu için ayrıca zamanlayıcı ve Selenium kodu vardır. Henüz kullanıcı kaydı/girişi, kullanıcıya göre veri izolasyonu, yönetilen platform bağlantıları veya çoklu işçi kilitlemesi yoktur. `monthly_plan.py` mevcut durumda tek ortak SQLite veritabanı ve ortak plan kullanır. Bu yüzden birden fazla kişinin aynı kurulumda güvenli biçimde kullanmasına hazır değildir.

## Önerilen yapı

- **VDS:** Ubuntu LTS, SSH anahtarıyla erişim; parola ile root SSH kapalı.
- **Web:** React/Vite derlemesi, Nginx veya Caddy üzerinden HTTPS.
- **API:** FastAPI, kullanıcı kimliğiyle korunan endpoint'ler.
- **Veritabanı:** PostgreSQL. Her içerik, takvim, görev, çıktı ve platform profili için `user_id` / tenant sınırı.
- **Kuyruk:** Redis + RQ/Celery gibi iş kuyruğu. Uzun video render ve Selenium işlemlerini HTTP isteğinde çalıştırma.
- **Scheduler:** Tek merkezi zamanlayıcı; günlük görevleri kullanıcı ve platform bazında idempotent şekilde kuyruğa koyar.
- **Browser worker:** Kullanıcı/platform başına ayrı kalıcı Chrome profili. Aynı profil üzerinde eşzamanlı iki tarayıcı açılmaz.
- **Depolama:** Medya dosyaları Git'e yazılmaz; sunucuda kullanıcıya özel dizin veya S3 uyumlu nesne depolama kullanılır.
- **Gözlem:** Görev geçmişi, hata logları, yeniden deneme ve sistem sağlık endpoint'i.

## Çok kullanıcılı kullanım kuralları

1. Kullanıcı A'nın içerikleri, videoları, planı, logları veya hesap oturumları kullanıcı B'ye gösterilmemeli.
2. Tüm DB sorguları yetkili kullanıcının tenant kimliğiyle filtrelenmeli; sadece arayüzde gizlemek yeterli değildir.
3. Her yayın işi için benzersiz idempotency anahtarı kullanılmalı: kullanıcı + tarih + platform + içerik.
4. Görev önce `queued/running` durumuna atomik şekilde alınmalı; birden fazla worker aynı işi alamamalı.
5. Başarılı platform yayınları tekrar edilmemeli. Bir platform başarısız olursa sadece o platform yeniden denenmeli.
6. Tarayıcı profilleri, cookie'ler ve şifreler asla Git'e veya uygulama loglarına yazılmamalı. Kullanıcı hesabı ilk kez görünür tarayıcıda kendisi bağlamalı.
7. Kullanıcıların birbirlerinin oturum çerezlerine erişimi olmamalı; her worker düşük izinle çalışmalı.
8. CAPTCHA veya iki faktörlü doğrulama atlatılmamalı. Selenium arayüzü değişebileceğinden yayın sonucu belirsizse iş 'başarılı' işaretlenmemeli.
9. Kaynak videolar için yeniden kullanım izni/telif durumu tutulmalı. İzin belirsizse indirmek yerine kaynak metinden özgün anlatım oluşturulmalı.

## VDS'ye kurulum sırası

### 1. Sunucuyu hazırla

Ubuntu LTS kullan; SSH anahtarıyla bağlan, güvenlik güncellemelerini kur, firewall'da yalnızca SSH, HTTP ve HTTPS aç. PostgreSQL ve Redis portlarını internete açma.

### 2. Uygulamayı ayrı servisler olarak çalıştır

- `web`: React statik dosyaları ve HTTPS proxy.
- `api`: FastAPI, loopback/özel Docker ağı üzerinde.
- `postgres`: yalnızca özel ağ, kalıcı volume ve düzenli yedek.
- `redis`: yalnızca özel ağ.
- `scheduler`: tek kopya.
- `render-worker`: video üretimi için sınırlanmış kaynak.
- `browser-worker`: izole tarayıcı profili ve kullanıcı başına tek iş.

### 3. İlk dağıtımda yalnızca test kullanıcısı

Önce bir test hesabı, bir platform ve özel/gizli yayınla doğrula. Başlık, Türkçe açıklama, doğru video, platformdaki görünür sonuç ve yeniden denemeyi test et. Üç platform kararlı olmadan tüm kullanıcılar için otomatik yayını açma.

## Neden SSH ile hemen kurmuyoruz?

VDS'ye SSH ile bağlanmak mümkün; ancak uzaktaki sunucuya bu sohbetten erişimim yok ve senin SSH özel anahtarını/şifreni istememeliyim. Bu repo için uygulanacak komutları ve deployment dosyalarını hazırlayabilirim; sunucuya komutları sen çalıştırırsın. Ayrıca mevcut kodun çok kullanıcılı güvenlik katmanı tamamlanmadan internete açılması, kullanıcıların içerik ve oturumlarının karışması riskini taşır.
