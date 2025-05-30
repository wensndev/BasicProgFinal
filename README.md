# 🎮 Sims 1960: MS-DOS Edition

**Nostaljik terminal yaşam simülasyonu oyunu**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-lightgrey.svg)](README.md)

---

## 📖 Proje Hakkında

**Sims 1960: MS-DOS Edition**, klasik The Sims oyunlarından ilham alınarak geliştirilmiş, terminal tabanlı bir hayat simülasyonu oyunudur. 1960'lı yılların retro MS-DOS estetiğini modern Python teknolojisiyle birleştiren bu proje, kullanıcılara nostaljik ama aynı zamanda zengin bir oyun deneyimi sunar.

### 🎯 Proje Vizyonu
- Retro terminal estetiği ile modern oyun mekanikleri
- Gerçekçi yaşam simülasyonu deneyimi
- Hem tek oyunculu hem multiplayer oyun modu
- Extensible ve modüler kod yapısı

---

## 👥 Geliştirici Ekibi

**🏢 Saumur Games**

- **👨‍💻 Melih Ulukoz**
- **👨‍💻 Egehan Yavuz**
- **👨‍💻 Erdinç Yıldırım**

---

## ✨ Özellikler

### 🎭 Karakter Sistemi
- **4 Farklı Karakter Tipi**: Ambitious, Social, Creative, Balanced
- Detaylı karakter özelleştirme (isim, cinsiyet, yaş, meslek)
- Karakter tipine göre özel yetenekler ve bonuslar

### 💼 Gelişmiş Meslek Sistemi
- **5 Farklı Meslek Dalı**: Yazılımcı, Öğretmen, Doktor, Sanatçı, Mühendis
- Meslek seviyesi ve deneyim sistemi
- Her meslek için özel mekanikler:
  - 🏥 **Doktor**: Acil durum bonusları
  - 🎨 **Sanatçı**: Değişken gelir sistemi
  - 💻 **Yazılımcı**: Yüksek maaş potansiyeli

### 🎲 Eğlence Sistemleri
- **Kumarhane**: Bahis oyunları ve slot makineleri
- **Sosyalleşme**: İlişki kurma ve geliştirme
- **Random Olaylar**: Beklenmedik durumlar ve fırsatlar

### 🌐 Multiplayer Desteği
- Real-time çok oyunculu mod
- Chat sistemi
- Oyuncu durumu senkronizasyonu
- Sunucu-istemci mimarisi

### 💾 Veri Yönetimi
- Kapsamlı kayıt/yükleme sistemi
- JSON tabanlı veri saklama
- Ölüm istatistikleri kayıtları

### 🛠️ Developer Araçları
- **Developer Mode**: Hızlı test ve geliştirme
- Command line argümanları
- Detaylı logging sistemi

---


## 🎮 Oyun Rehberi

### 🏁 Başlangıç
1. **Oyun Modu Seçimi**: Tek oyunculu, Sunucu başlat, veya Sunucuya bağlan
2. **Karakter Oluşturma**: İsim, cinsiyet, yaş ve karakter tipi belirleyin
3. **Meslek Seçimi**: Başlangıç mesleğinizi seçin

### 🕹️ Temel Kontroller

#### 🏠 Ana Aktiviteler
- **🍽️ Ye** (3 saat) - Açlığınızı giderin
- **😴 Uyu** (6-8 saat) - Enerji toplayın
- **🚿 Banyo Yap** (2 saat) - Temizliğinizi artırın

#### 💼 İş Hayatı
- **İşe Git** (4-8 saat) - Para kazanın ve deneyim edinin
- **İş Ara** (2 saat) - Yeni meslek bulun
- **İstifa Et** (1 saat) - Mevcut işinizden ayrılın

#### 👥 Sosyal Hayat
- **Arkadaşlarla Buluş** (3 saat) - Sosyal ihtiyaçlarınızı karşılayın
- **Flört Et** (2 saat) - Romantik ilişkiler geliştirin
- **Partiye Git** (4 saat) - Eğlenin ama maliyetli!

#### 🎲 Eğlence
- **Bahis Oyunları** (1 saat) - Şansınızı deneyin
- **Slot Makineleri** (1 saat) - Jackpot peşinde koşun

### 📊 Karakter İstatistikleri
- **💪 Enerji** (0-100): Günlük aktiviteler için gerekli
- **🍔 Açlık** (0-100): Düzenli beslenme zorunlu
- **🧼 Hijyen** (0-100): Temizlik ve sağlık
- **👥 Sosyal** (0-100): İnsan ilişkileri
- **😊 Ruh Hali** (0-100): Genel mutluluk seviyesi
- **💰 Para**: Yaşam için gerekli kaynak

### ⚠️ Hayatta Kalma
Karakterinizin ihtiyaçları kritik seviyelere düştüğünde ölüm riski artar:
- **Enerji < 15**: Kalp krizi riski (15 saniye)
- **Açlık < 20**: Açlıktan ölüm (30 saniye)
- **Hijyen < 20**: Hastalık riski (90 saniye)
- **Ruh Hali < 20**: Depresyon riski (45 saniye)
- **Sosyal < 20**: İzolasyon riski (120 saniye)

---

## 🌐 Multiplayer Modu

### 🖥️ Sunucu Başlatma
1. Ana menüden "Sunucu Başlat" seçin
2. Karakterinizi oluşturun
3. Diğer oyuncuların bağlanmasını bekleyin
4. En az 2 oyuncu olduğunda oyunu başlatın

### 📱 İstemci Olarak Bağlanma
1. Ana menüden "Sunucuya Bağlan" seçin
2. Sunucu IP adresini ve portu girin (varsayılan: localhost:5000)
3. Karakterinizi oluşturun
4. Lobby'de host'un oyunu başlatmasını bekleyin

### 💬 Multiplayer Özellikleri
- **Real-time Chat**: Diğer oyuncularla anlık mesajlaşma
- **Oyuncu Listesi**: Bağlı oyuncuları ve durumlarını görme
- **Durum Senkronizasyonu**: Otomatik oyuncu durumu güncellemesi
- **Ölüm Bildirimleri**: Oyuncu ölümlerinin canlı bildirilmesi

---

## 🔧 Teknik Detaylar

### 🏗️ Mimari Tasarım
- **MVC Pattern**: Model-View-Controller ayrımı
- **Factory Pattern**: Meslek ve karakter nesnesi oluşturma
- **Observer Pattern**: Oyuncu durumu güncellemeleri
- **Singleton Pattern**: Network bağlantı yönetimi

### 📦 Modül Yapısı
```
models/
├── game.py          # Ana oyun motoru
├── sim.py           # Karakter modeli
├── actions.py       # Oyuncu eylemleri
├── network.py       # Multiplayer sistem
├── ui.py            # Kullanıcı arayüzü
├── jobs.py          # Meslek sistemi
├── gambling.py      # Bahis oyunları
├── events.py        # Rastgele olaylar
├── character_types.py # Karakter tipleri
└── stats_display.py # İstatistik gösterimi
```

### 🛠️ Kullanılan Teknolojiler
- **Rich**: Terminal UI framework
- **Inquirer**: İnteraktif menü sistemi
- **PyFiglet**: ASCII sanat ve logolar
- **Socket**: Network programlama
- **Threading**: Çoklu iş parçacığı desteği
- **JSON**: Veri serileştirme

### 🔒 Network Güvenliği
- Client-server encryption desteği
- Bağlantı doğrulama
- DOS saldırı koruması
- Safe disconnect mekanizmaları

---

## 🎯 Developer Modu

Developer modu etkinleştirildiğinde:

### ⚡ Hızlandırılmış Deneyim
- Yükleme ekranları **10x hızlı**
- Aktivite süreleri **minimuma** indirilir
- Bildirim süreleri **kısaltılır**
- Progress bar'lar **hızlı** ilerler

### 🔧 Debug Özellikleri
- Detaylı log çıktıları
- Network trafiği görünürlüğü
- Performans metrikleri
- Hata yakalama geliştirilmiş

---

## 📋 Gereksinimler

### 🐍 Python Bağımlılıkları
```txt
rich>=13.0.0
inquirer>=3.1.0
pyfiglet>=0.8.0
```

### 💻 Sistem Gereksinimleri
- **İşletim Sistemi**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.7 veya üzeri
- **RAM**: Minimum 256 MB
- **Disk Alanı**: 50 MB boş alan
- **Network**: Multiplayer için internet bağlantısı

---

## 🐛 Bilinen Sorunlar

### 🔧 Aktif Sorunlar
- Windows terminal'de Unicode karakterlerin görüntülenme sorunu
- Çok oyunculu modda ağ kesintilerinde karakter kaybı
- Büyük kayıt dosyalarında yükleme gecikmesi
---


**🎮 İyi Oyunlar! - Saumur Games Ekibi**

*"1960'ların ruhunu modern teknoloji ile yaşatıyoruz."* 