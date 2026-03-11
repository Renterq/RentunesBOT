# RentunesBOT
Discord sunucuları için rekabetçi müzik bilgi yarışması botu! Şarkıları bil, puan kazan, marketten ünvan al veya arkadaşlarınla bahisli kafes dövüşlerine gir (1v1, FFA, Takımlı). Otomatik özel ses odası yönetimi ve kusursuz ekonomi sistemiyle Discord'da yeni nesil eğlence altyapısı.
# 🎵 Rentunes - Discord E-Spor ve Müzik Arenası Botu

Rentunes, Discord sunucuları için geliştirilmiş sıradan bir müzik botu değildir. Müzik bilgisini, hızı ve şansı harmanlayan; içinde rekabet, ekonomi ve bahis (kumar) sistemleri barındıran tam teşekküllü bir **Oyun ve Eğlence Stüdyosudur.**

Kullanıcılar en sevdikleri sanatçıların rastgele çalınan şarkılarını saniyeler içinde tahmin etmeye çalışır, kazandıkları puanlarla marketten RPG tarzı ünvanlar satın alır veya tüm paralarını devasa kafes dövüşlerinde masaya sürebilirler!

## 🌟 Temel Özellikler

* **Mükemmel Senkronizasyon:** Sesin Discord'a iletilme süresi (buffer) hesaplanarak, müzik ve tahmin butonları ekrana %100 eşzamanlı düşer.
* **Gelişmiş Ekonomi Sistemi:** Kullanıcılar günlük ödüllerini toplayabilir, birbirlerine para transferi (`!pay`) yapabilir ve `!cuzdan` üzerinden bakiyelerini kontrol edebilirler.
* **RPG Market & Ünvanlar:** Oyuncular kazandıkları puanlarla "Acemi Dinleyici"den başlayıp "Müzik ve Gizem Efsanesi"ne kadar uzanan 30 farklı havalı ünvanı `!market` üzerinden satın alabilir.
* **Dostluk Modları:** Puan kaybetme korkusu olmadan, bulunduğunuz ses kanalında mikrofonlarınız açıkken arkadaşlarınızla şarkı söyleyip yarışabileceğiniz bedava oyun modları (`!oyna`, `!secili`).
* **Kanlı Rekabet & Bahis Modları:** Özel "Arena" odalarında mikrofonların kopya çekilmemesi için kilitlendiği, ortaya bahislerin konduğu ve kaybedenin puanından düşülen acımasız e-spor modları (`!vs`, `!ffa`, `!2vs2`, `!3vs3`).
* **Akıllı Temizlik Sistemi:** Chat kirliliğini önlemek için raund içi mesajlar butonlara tıklandığı an ve maç sonunda otomatik olarak temizlenir. Geriye sadece şık liderlik tablosu kalır.

## 🛠️ Kurulum (Nasıl Çalıştırılır?)

1. Bu depoyu bilgisayarınıza/sunucunuza klonlayın:
   `git clone https://github.com/KULLANICI_ADIN/rentunes.git`
2. Gerekli kütüphaneleri indirin:
   `pip install -r requirements.txt`
3. Proje dizininde `.env` adında bir dosya oluşturup Discord bot tokeninizi girin:
   `DISCORD_TOKEN=senin_bot_tokenin_buraya`
4. (Opsiyonel) Yaş kısıtlamalı videoları çekebilmek için tarayıcınızdan aldığınız YouTube çerezlerini `cookies.txt` adıyla ana dizine atın.
5. `cekici.py` dosyasını çalıştırarak istediğiniz şarkıcının YouTube Oynatma Listesi linkini girip veritabanınızı (JSON) oluşturun.
6. Botu başlatın:
   `python main.py`

## 🎮 Kısaca Nasıl Oynanır?
* **Tek Başına Antrenman:** `!oyna`
* **Arkadaşla Bedava Kapışma:** `!secili @kisi`
* **Bahisli Kumar Masası:** `!vs @kisi 100` (100 Puanlık Bahis)
* **Klan Savaşları:** `!3vs3 @takim1 @takim2 @rakip1 @rakip2 @rakip3`

## 🛡️ Güvenlik ve Yetkiler
Botun kusursuz çalışması (özel oda kurup silebilmesi, üyeleri odalara çekip fırlatabilmesi ve rekabetçi modlarda üyeleri susturabilmesi) için Discord üzerinden bota şu yetkilerin verilmesi zorunludur:
`Kanalları Yönet`, `Mesaj Gönder`, `Bağlantı Yerleştir`, `Üyeleri Taşı`, `Üyeleri Sustur`.
