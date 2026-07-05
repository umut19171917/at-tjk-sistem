# TJK At Yarışı Bahis Tahmin Sistemi

Bu klasör (`projeler/at/`) bu projenin **tek ve kalıcı çalışma alanıdır**. Kripto klasörüyle
ve onun hafızasıyla ilişkisi yoktur; oraya dokunulmaz. Bu projede **otomatik hafıza
kullanılmaz** — tüm kayıt bu klasördeki dosyalardadır.

## Amaç
TJK müşterek bahislerinde **sürdürülebilir, pozitif beklenen değerli (EV>0)** bir bahis sistemi.
Jackpot avı değil. Yaklaşım Benter-*ilhamlı* (kopya değil): fundamental olasılık modeli +
kamuoyu oranını harman + disiplinli bahis boyutu.

## Temel gerçek
Pari-mutuel + ganyan kesintisi **~%25,7** (veriden ölçüldü) → negatif toplamlı oyun. Kâr için
"kazananı bilmek" değil, **havuzun yanlış fiyatladığı atları kesintiyi aşacak biçimde** bulmak.

## Kapsam (Faz 1)
- **İçeride:** TR **İngiliz atı düz koşuları**, **Ganyan + Plase**.
- **Dışarıda (şimdilik):** Altılı/çok-koşulu, egzotikler, yabancı, Arap atı, 4 şüpheli pist
  (Elazığ, Diyarbakır, Urfa/Şanlıurfa, Adana).

## Durum (2026-06-30)
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
- **OTOMATİK BAŞLATMA (K43, 2026-07-05):** Görev Zamanlayıcı **"TJK Takip"** her gün 10:30'da
  takibi kendisi başlatır (PC açık/uyanık olmalı; uykudaysa uyandırır, saati kaçırdıysa fırsat
  bulunca başlar). Elle çift-tık artık gerekmez ama zararsızdır (tek-instans kilidi var).
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
