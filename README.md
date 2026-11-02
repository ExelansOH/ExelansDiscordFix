# ⚡ Exelans Discord Fixer

<p align="center">
  <img src="discord_fix.png" alt="Exelans Discord Fixer Logo" width="128"/>
</p>

<p align="center">
  <b>Türkiye İnternet Servis Sağlayıcıları İçin Yalnızca Discord Hedefli DPI & DNS Aşma Aracı</b><br>
  <i>Oyunlar, bankacılık ve genel internet trafiği etkilenmez • Ping artışı ve hız kaybı yaşanmaz</i>
</p>

<p align="center">
  <a href="https://www.exelansmacro.com"><img src="https://img.shields.io/badge/Resmi_Site-exelansmacro.com-5865F2?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Website"></a>
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011%20(64--bit)-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/Lisans-MIT-green?style=for-the-badge" alt="License">
</p>

---

## 🎯 Projenin Amacı

> **Bu proje;** Türkiye'deki internet servis sağlayıcılarının (İSS) Discord üzerinde uyguladığı DNS engellerini ve Derin Paket İnceleme (DPI) kısıtlamalarını harici bir VPN kullanmadan, internet hızında ve oyun içi gecikmelerde (ping) herhangi bir kayıp yaşamadan **yalnızca Discord trafiğini izole ederek** aşmayı amaçlamaktadır.

---

## 💡 Neden Bu Proje? (Klasik Yöntemlerden Farkı)

Geleneksel DPI atlatıcılar (`GoodbyeDPI` varsayılan komutları) veya genel VPN servisleri tüm bilgisayarın ağ trafiğine müdahale eder. Bu durum:
- ❌ Online oyunlarda (Valorant, CS2, Knight Online, LoL vb.) ping artışına ve ani takılmalara,
- ❌ Yerel bankacılık, kamu (e-Devlet) sitelerinde güvenlik bloklarına,
- ❌ Genel indirme hızında dalgalanmalara yol açar.

**Exelans Discord Fixer**, GoodbyeDPI motorunu `--blacklist` parametresiyle sınırlar.
* **Giden trafik Discord'a aitse** (ses bağlantıları, gateway, medya, güncellemeler) DPI parçalama ve DNS korumasını uygular.
* **Diğer tüm siteler, uygulamalar ve oyunlar** doğrudan orijinal internet rotasından ve maksimum hızında akmaya devam eder.

---

## 🚀 Öne Çıkan Özellikler

- **🎯 İzole Hedefleme:** Yalnızca Discord alan adlarını (`discord.com`, `discord.gg`, `*.discord.media`, `updates.discord.com` vb.) dinler.
- **🌐 Özel İSS Profilleri:**
  - *Türk Telekom / TurkNet / Kablonet (Önerilen - Mod -5, TTL 5 + DNS)*
  - *Superonline / Vodafone (TTL 3 Modu)*
  - *Superonline Alternatif (Ağır DPI - Mod -9)*
  - *Sadece DPI Bypass (DNS Değiştirmeden)*
- **🛠 İki Farklı Çalışma Yöntemi:**
  1. **Kalıcı Windows Hizmeti (Service):** Tek tıkla sisteme kurulur. Bilgisayar her açıldığında hiçbir pencere açmanıza gerek kalmadan siz kaldırana kadar 7/24 arkada çalışır.
  2. **Anlık Masaüstü Modu:** İhtiyaç duyulduğunda açılır, çarpıya basıldığında saatin yanına (sistem tepsisine) küçülür.
- **🔄 Discord Onarım Aracı (Anti-Update Loop):** Discord'un güncelleme döngüsünde ("Update failed") takılmasını önleyen otomatik DNS ve önbellek sıfırlama mekanizması.
- **📝 Doğrudan Alan Adı Düzenleme:** Arayüz üzerinden tek tıkla hedef alan adı listesini görüntüleyebilir ve yeni adresler ekleyebilirsiniz.

---

## 📂 Proje Yapısı

```
ExelansDiscordFix/
├── bin/
│   ├── goodbyedpi.exe          # x86_64 DPI manipülasyon çekirdeği
│   ├── WinDivert.dll           # WinDivert kullanıcı modu kütüphanesi
│   └── WinDivert64.sys         # 64-bit Windows ağ filtre sürücüsü
├── scripts/
│   ├── service_install_discord_only.cmd              # Standart İSS kalıcı servis kurulumu
│   ├── service_install_discord_only_superonline.cmd  # Superonline için TTL 3 kurulumu
│   └── service_remove.cmd                            # Servisi sistemden kaldırma
├── discord_domains.txt         # Filtrelenen Discord domain listesi
├── discord_fix.ico             # Uygulama ikonu
├── gui.py                      # Modern CustomTkinter masaüstü arayüzü
├── build.bat                   # PyInstaller tek tıkla derleme scripti
├── requirements.txt            # Python bağımlılıkları
├── LICENSE                     # MIT Lisansı
└── README.md
```

---

## 🛠 Kurulum ve Kullanım

### Yöntem 1: Hazır `.exe` İle Kullanım (En Kolayı)
1. [Releases](https://github.com/ExelansOH/ExelansDiscordFix/releases) sayfasından en son `ExelansDiscordFix.exe` dosyasını indirin (veya projeyi klonlayıp `build.bat` ile kendiniz derleyin).
2. Dosyayı çalıştırın (Otomatik yönetici izni isteyecektir).
3. İSS profilinizi seçin (Çoğu kullanıcı için varsayılan Türk Telekom / TurkNet modu uygundur).
4. **"🚀 Windows Hizmeti Olarak Kur (Kalıcı)"** butonuna tıklayın.
5. Discord'unuzu açın veya **"🔄 Discord'u Yeniden Başlat"** butonuna basın.

### Yöntem 2: Arayüzsüz Doğrudan `.cmd` İle Kalıcı Servis Kurulumu
1. `scripts\service_install_discord_only.cmd` dosyasına sağ tıklayın.
2. **Yönetici Olarak Çalıştır**'ı seçin.
3. Servis kurulup arka planda otomatik başlayacaktır (Superonline kullanıcıları `scripts\service_install_discord_only_superonline.cmd` çalıştırabilir).

---

## 💻 Kaynaktan Çalıştırma ve Derleme (Geliştiriciler İçin)

Projeyi doğrudan Python kaynak kodundan çalıştırmak veya kendi `.exe` dosyanızı oluşturmak isterseniz:

```bash
# 1. Repoyu klonlayın
git clone https://github.com/ExelansOH/ExelansDiscordFix.git
cd ExelansDiscordFix

# 2. Gerekli Python kütüphanelerini yükleyin
pip install -r requirements.txt

# 3. Arayüzü doğrudan Python ile başlatın
python gui.py

# 4. İsterseniz tek parça bağımsız .exe haline derleyin
build.bat
```

---

## ⚠️ Dikkat Edilmesi Gerekenler
* **Yönetici Hakları:** Yazılım, paketleri filtrelemek için Windows `WinDivert` sürücüsünü kullandığından Yönetici Hakları (UAC) gerektirir.
* **Antivirüs:** Bazı agresif antivirüs programları (özellikle Kaspersky), ağ sürücülerine (`WinDivert64.sys`) müdahaleyi şüpheli görebilir. Gerekirse dışlama listesine ekleyiniz.

---

## 📜 Lisans & Teşekkür
Bu proje [MIT Lisansı](LICENSE) kapsamında sunulmaktadır.
* Çekirdek paket filtreleme motoru: [GoodbyeDPI](https://github.com/ValdikSS/GoodbyeDPI) & [GoodbyeDPI-Turkey](https://github.com/cagritaskn/GoodbyeDPI-Turkey)
* Sürücü Katmanı: [WinDivert](https://reqrypt.org/windivert.html)
* Arayüz ve Entegrasyon: **Exelans Macro Ekibi** ([www.exelansmacro.com](https://www.exelansmacro.com))
