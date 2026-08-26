# TJK At Yarışı Bahis Tahmin Sistemi

Bu klasör (`projeler/at/`) bu projenin **tek ve kalıcı çalışma alanıdır**. Kripto klasörüyle
ve onun hafızasıyla ilişkisi yoktur; oraya dokunulmaz. Bu projede **otomatik hafıza
kullanılmaz** — tüm kayıt bu klasördeki dosyalardadır.

## Amaç
Kuruluş sorusu: TJK müşterek bahislerinde **sürdürülebilir EV>0** mümkün mü? Benter-*ilhamlı*
yaklaşımla (fundamental model + kamu oranı harmanı) soruldu ve **12+ bağımsız testte cevaplandı:
HAYIR** (verimli piyasa + %25-31 ganyan / ~%49 Altılı kesintisi; K13-K46, K52-K75). **Güncel amaç (K48, 2026-07-17):** paper
testi 25 Eylül'e kadar tamamlamak + izleme/öğrenme. Kullanıcı gerçek bahis OYNAMIYOR;
K37/K41 çerçevesi askıda (ilk gerçek kuponla kendiliğinden yeniden aktif). Mod kararı: 25 Eylül.

## Temel gerçek
Pari-mutuel + ganyan kesintisi **~%25,7** (veriden ölçüldü) → negatif toplamlı oyun. Kâr için
"kazananı bilmek" değil, **havuzun yanlış fiyatladığı atları kesintiyi aşacak biçimde** bulmak.

## Kapsam
- **İçeride:** TR **İngiliz + Arap** düz koşuları (K46: iki ayrı model; Arap analiz katmanı,
  kesintisi ~%30,6 → ekonomisi İngiliz'den de sert). Ganyan + Plase ölçümü.
- **İçeride (K53'ten beri): ALTILI GANYAN** — kâğıt gözlem akışı, 7 aktif + 4 emekli config (aşağıda).
  *(Bu satır 2026-07-31'de düzeltildi: eski README Altılı'yı "dışarıda" gösteriyordu, artık
  sistemin ana faaliyeti odur.)*
- **Dışarıda:** 4'lü/5'li (K108 ikame · K120 ek — ikisi de ÖLÇÜLDÜ, reddedildi), 7'li (K117),
  diğer egzotikler, yabancı,
  4 şüpheli pist (Elazığ, Diyarbakır, Urfa/Şanlıurfa, Adana — Arap'ta da hariç).
  Paper test (K42) İngiliz-kilitli.

## ALTILI SİSTEMİ (güncel ana faaliyet — 2026-08-26)
Kupon **tek anda** kurulur: 30 dk grubu 1. ayağa 30 dk kala, 15 dk grubu 15 dk kala
(`altili_canli.kupon_zamani_kur`). Telegram'a kurulum + sonuç bildirimi gider;
sayfa: `raporlar/altili.html` (`altili_goster.bat`).

**7 aktif + 4 emekli config.** Emekliler kupon KURMAZ, geçmiş sicilleri raporda AYNEN durur.

| config | bütçe | dağıtım | puan | dk | durum / rolü |
|---|---|---|---|---|---|
| `orta` | 96 | kapsam | bot2 | 30 | aktif — temel kupon, zamanlama kolunun kontrolü |
| `orta_15` | 96 | kapsam | bot2 | **15** | aktif — zamanlama kolu (K105), tetik ~60 kupon |
| `acgozlu900` | 900 | açgözlü | bot2 | 30 | aktif — `acgozlu_v2`'nin kontrolü |
| `acgozlu900_15` | 900 | açgözlü | bot2 | **15** | aktif — zamanlama kolu, geniş bütçe |
| `acgozlu_v2` | 900 | **kalibre** (λ=0,65 uzak ayak) | bot2 | 30 | aktif — en yeni deney (K92), 25 Eyl'e bağlı |
| **`bot1_900`** | 900 | açgözlü | **bot1** | 30 | aktif — portföyün tek gerçek çeşitlendiricisi |
| `bot1_1800` | 1800 | açgözlü | **bot1** | 30 | aktif — bütçe kolu (K118'de emeklilik önerildi, kullanıcı "devam etsin" dedi) |
| `dar` · `genis` · `genis900` · `ayrisma900` | 24/288/900/900 | — | bot2 | 30 | **EMEKLİ** (10.08.2026, K100) |

**Hepsi −EV gözlem akışıdır, iyileştirme değil.** Gerekçeler: K62 · K65 · K67 · K68 · K69 ·
K92 · K100 · K105.

### Altılı'da ne öğrenildi — bütün kenar hipotezleri ölçüldü, hepsi kapandı
**Merkez bulgu (K72):** model **şansı eziyor** (+79 puan) ama **kalabalığı yenmiyor**
(−1,2 puan, GA sıfırı içeriyor). Seçimimiz kuponların %41,4'ünde saf-favori seçimiyle aynı.
**Ekonomi (K73/K94):** Altılı kesintisi **~%49**. Favori oynamak havuz ortalamasını ~30 puan
yeniyor → *"sistem havuzu yeniyor ama vergiyi yenemiyor."*

| aranan kenar | sonuç |
|---|---|
| model / ağırlıklar (bot1, harman, kamu ağırlığı) | K67 · K96 · K112 — kenar yok |
| dağıtıcı (birleşim · v3 · saha · λ) | K90 · K115 · K116 — yalnız λ geçti, o da 900'e özgü (K98) |
| bütçe (900↔1800, derinlik taraması) | K91 · K113 — hiçbir derinlik kârlı değil |
| zamanlama (30 vs 15 dk) | K111 — daha çok tutturuyor, daha az ödüyor |
| başka ürün: 4'lü/5'li (ikame) · 7'li | K108 · K117 — ikisi de reddedildi |
| 4'lü/5'li **ek** oynamak | K120 — 94.293 TL DAHA kaybettirirdi |
| yapısal fırsat: devir | K117 — gerçek (temettü +%37) ama ulaşılamıyor |

**Neden hiçbiri tutmuyor — tek cümlelik mekanizma (K65 · K117 EK · K120):**
hangi ürünü, hangi genişlikte oynarsak oynayalım **yalnız ucuz kuyruğa erişiyoruz.**
Tutturduğumuz olaylar tipik olayın %5-7'sini ödüyor (Altılı %7 · 7'li %5 · 5'li %26).
Büyük temettüler, tam da tutturamadığımız olaylarda yaşıyor.

**Diğer sağlam bulgular:**
- **K88:** kupon genişliği modelin güveninden değil, **bütçenin 6. kökünden** geliyor
  (`24^(1/6)=1,70` … `900^(1/6)=3,11`); kapsam/banker eşikleri pratikte hiç bağlamıyor.
- **K114:** banker bayrağı gerçek bilgi taşıyor — bayraklı tek-at ayakları **%52,1**,
  bütçe artığı tek-atlar **%30,4** (taban %33; p=0,0001).
- **K113:** 5/6 bir "az kaldı" sinyali DEĞİL. 10 tane 6/6'ya karşılık 112 tane 5/6;
  kaçan ayakta kazananın sırası medyan 5. Aynı sonucu önceden almak 9 kat pahalı.
- **K70/K71:** ayaklar bağımsız → koşullu kupon ek bilgi taşımıyor; 96 kombodan sonraki
  her katman kanıtlı zararlı.
- **K97/K77:** sayfadaki iki sıralama farklıdır — **K** kupon anı (karar bu cetvelle verildi),
  **Y** yarış anı. "Sistem sıra atladı" görüntüsünün sebebi budur; atlama YOK.
- **K121:** `getjson` artık bir kez yeniden dener — 15 dk kolu yapısal tek nokta arızasıydı
  (Altılı 1. ayak postaları %100 tam çeyrek saatte; 15 dk penceresine tek geçiş düşer).

## Durum (temel altyapı — 2026-06-30; güncel durum için KARARLAR.md son 10 karar)
- Faz 0 — Veri fizibilitesi: **TAMAM** (`raporlar/faz0-veri-fizibilite.md`).
- Kapı #2 — Eldeki verinin incelenmesi: **TAMAM** (`raporlar/kapi2-veri-inceleme.md`).
  - Eldeki veri = **3 ay** (2024-10 … 2024-12), ~1.041 izinli-pist koşu. Başka veri yok.
  - Yapı doğru (ganyan_orani + sonuç + özellik var) ama **miktar yetersiz** (overfit riski) ve
    **temizlik/join işi** gerek.
- **Veri hattı + Bot1/Bot2 TAMAM, walk-forward test edildi:** 5,5 yıl (2021-2026), Faz 1 kapsamı
  13.597 koşu; α=+0,18, piyasayı log-loss'ta kıl payı yeniyor ama **+EV yok.**
- **NİHAİ ARAŞTIRMA SONUCU (6 bağımsız test, K13-K25):** ganyan/exacta/Altılı/chalk — hiçbir
  sistematik strateji +EV değil. Engel yapısal (verimli piyasa + ~%25-40 kesinti). Arkadaş-vakası
  edge'i veri-türevli değil (tacit/yargı).
- **`gunluk.py` KURULDU (K27):** canlı program (`.../program/{Ymd}/full/{KEY}.json`) → eğitimle
  aynı nokta-anında özellikler → Bot1+Bot2 → tam kart (Bot1%/Bot2%/kamu%/AGF/oran/CANLI işareti).
  Sızıntı yok (kontaminasyon testi geçti). KÂR DEĞİL — analiz/kâğıt-ticaret aracı; +EV yok.
  Kullanım: `python kod/gunluk.py --pist ANKARA` | `--kosu N` | `--tarih YYYY-MM-DD`.
- **`defter.py` KURULDU (K28):** kâğıt-ticaret defteri. `kaydet` (model tahminlerini + opsiyonel
  kendi seçimini deftere yaz) → `sonucla` (ertesi gün sonuçla otomatik eşle) → `ozet` (kalibrasyon +
  log-loss + hipotetik ROI: model/kamu/CANLI/senin-seçimlerin + isabet) → `goster` (gün/koşu/at bazlı
  tahmin+sonuç okunur tablo, K30). Tam döngü gerçek veriyle doğrulandı. ROI=ganyan; plase = top-pick
  win/ilk-2/ilk-3 isabet oranı (bedava).
- **`takip.py` OTOMATİK TAKIP kuruldu (K29):** yarış günü sabahı `python kod/takip.py` (terminal açık
  kalsın, PC uyumasın). Gün boyu her İngiliz koşusunu yarıştan ~5 dk kala canlı oranla analiz eder
  (tüm atları kendi AGF%'siyle sıralar), `raporlar/gunluk/`'a yazar + deftere işler, gün sonu sonuçlar.
  `--once`/`--pist X`/`--dk`/`--bekle` ayarlanır.
- **PowerShell'siz erişim (K31):** kök klasörde **`baslat_takip.bat`** (arşivi günceller + gün boyu
  takip) + **`sonuclari_goster.bat`** (çift-tık → sonuçları çek + tarayıcıda aç)
  + **`bahis_gir.bat`** (gerçek kupon kaydı, K37). Okunur tablo: **`raporlar/defter.html`**
  (gün/koşu/at: tahmin+sonuç, kazanan yeşil + gerçek-bahis P&L); otomatik güncellenir.
- **TAM OTOMATİK — DURUMSUZ GEÇİŞ (K49, 2026-07-18; K43'ü değiştirdi):** "TJK Takip" görevi
  **her 15 dk'da bir** durumsuz geçiş çalıştırır (vadesi gelen koşuları işle → `takip_gecis.txt`
  mühürle → çık). Süreç ölümü/uyku/pencere sorunu kalmadı; çöken geçişin yerini 15 dk sonra
  yenisi alır. Bekçi 2 saatte bir "son 45 dk nabız var mı" bakar, yoksa ekrana uyarı basar.
  `baslat_takip.bat` = elle tek geçiş (sadece kurtarma için; rutinde hiçbir tıklama gerekmez).
- **Revizyon paketi (2026-07-02 gece, K35-K39):** dış kod incelemesi sonrası: **git deposu** (baseline
  + paket paket commit), `requirements.txt`, **nokta-anında dt-guard** (mükerrer-koşu/geçmiş-tarih
  sızıntısı kapandı), **arşiv bayatlık uyarısı + `kod/guncelle.py`** tazeleme protokolü, **defter
  ileriye-dönüklük koruması** (posta saati geçmiş koşu kaydedilmez), **gerçek-bahis defteri**
  (`veri/bahisler.csv`; "senin yargın kesintiyi aşıyor mu" ölçümü), `par` look-ahead düzeltmesi
  (A/B: Bot2 değişmedi → K19-K33 verdiktleri geçerli), takip dayanıklılığı.
- **K37 kuralı ONAYLANDI + koda bağlandı (K40, 2026-07-03):** n≥100 kupon VE ≥90 gün dolunca
  `ozet` gerçek-ROI %95 GA hesaplar; üst sınır < 0 → "GERÇEK PARA DUR" verdikti otomatik basılır.
- **K41 (2026-07-03):** kapsam = İngiliz GANYAN; tavan **kupon/koşu ≤100 TL, gün ≤300 TL** —
  `bahis` kayıt anında uyarır, `ozet` uyum sayar (ölçer, engellemez). Harici yedek arşivi üretildi:
  `Desktop/at-yedek-2026-07-03.zip` (196 MB; ham+kod+git+defter).
- **K42 PAPER TEST (2026-07-04 → 2026-09-25):** 5 ön-kayıtlı strateji (S1-S5), kupon 15 TL,
  hafta 3000 TL; takip otomatik üretir/kapatır. **Ayrı arayüz:** `raporlar/paper.html` +
  çift-tık `paper_goster.bat` (defter arayüzüne dokunmaz). Plase ilk kez ölçüldü (backtest:
  top-pick plase −%12,5); tüm beklentiler negatif — amaç kalibrasyon + plase'nin canlı ölçümü.
- **K44 Benter dosyası kapandı:** Plackett-Luce plase modeli kill testinde elendi (harman piyasa-
  Harville'i geçemedi). **K46 Arap modeli eklendi:** α=+0,22, log-loss piyasayı geçiyor ama
  kesinti ~%30,6 → analiz katmanı; takip/defter artık iki ırkı da izler, paper test İngiliz-kilitli
  (kod korumalı). "Tüm bahis türleri" genişletmesi veriyle reddedildi (KARARLAR K46).
- **AÇIK GÖREV (kullanıcı, tek adım):** `at-yedek-2026-07-03.zip`'i Google Drive'a yükle
  (drive.google.com → sürükle-bırak) veya USB'ye kopyala. Tazeleme: ~ayda bir yeni zip.
- **Sıradaki adım (açık):** (1) gerçek kartlarda kâğıt-izleme + gerçek-bahis birikimi; (2) Arap modeli
  (Altılı, *veri gösterirse*); (3) hız/param cache (çalışma süresi). Detay: `KARARLAR.md` K31-K39.

## Veri
- Eldeki ham set: `veri/` (kullanıcının 3 aylık 5 tablosu — gelince buraya konacak).
- Genişletme kaynağı: `ebayi.tjk.org/s/d/{program|sonuclar}/{Ymd}/full/{KEY}.json` (arşiv ≥2021).

## Klasör yapısı
```
at/
├── README.md     → tek bakışta durum
├── KARARLAR.md   → tarihli karar günlüğü + gerekçe
├── raporlar/     → analizler
└── veri/         → ham veri
```

## Çalışma kuralları
- Veri-öncelikli; "bilmiyorum" geçerli. Adım adım; onaysız ileri yok.
- **Seçenek sunulan her iletinin sonunda asistan kendi tavsiyesini gerekçesiyle verir** (K11).
- Tüm kayıt `at/` altında; kripto'ya/otomatik-hafızaya dokunulmaz.
