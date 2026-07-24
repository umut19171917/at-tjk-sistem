# Bekleyen İşler — "Sonra Yapalım / Deneyelim" Defteri

**Amaç:** Konuşma içinde "şimdilik bırakalım, sonrası için not edelim" denen işler
KARARLAR.md'nin tarihli satırlarına dağılıp unutuluyordu. Bu dosya TEK bakış noktasıdır.

**Kural:** Bir iş ertelendiğinde BURAYA yazılır; yapıldığında/düştüğünde buradan
işaretlenir (silinmez, "✅ yapıldı" / "❌ düştü" olarak damgalanır). Gerekçe kısa; ayrıntı
ilgili K kararında. İlk kurulum: 2026-07-24.

---

## AÇIK — sırası gelince

### 1. ✅ ÇÖZÜLDÜ (2026-07-24, K57) — kap genişletme + v2 budama backtest'te ölçüldü
**Sonuç:** `kod/altili_kap_test.py` (1455 OOS olay). (a) Orta'yı genişletmek **kazanç vermiyor**
— dürüst zeminde orta −%19, 288 −%32, 384 −%44; 384-vs-96 fark GA'sı sıfırı içeriyor → orta
**aynen kaldı**. (b) v2 budama (sıkışığı koru) **daha kötü** (orta ROI +%44,7→+%10,9, 6/6: 66→47)
→ **reddedildi**, YURİBOYKA hindsight tuzağıydı. (c) Kullanıcı isteğiyle ayrı **geniş (288)
gözlem akışı** eklendi (iyileştirme değil, −EV; ileri-yönlü). Aşağıdaki özgün analiz kayıt için durur.

<sub>--- özgün madde (arşiv) ---</sub>
**Eklendi:** 2026-07-24 · **İlgili:** K52, K53
Mevcut budama (`altili_backtest.kupon_kur`) bütçe aşılınca **en çok atlı = en sıkışık**
ayaktan atıyor. Bu mantık ters: atlar birbirine yakınken (belirsiz ayak) rastgele eleme
yapıyor, bir at öne çıkınca (net ayak) gereksiz kapsam bırakıyor. Doğrusu: sıkışık ayağı
KORU, baskın ayaktan buda. Somut vaka: 23.07.2026 Ankara 1. Altılı 2. ayakta kamu favorisi
YURİBOYKA budandı → 5/6'da kalındı, ~19.167 TL kaçtı.

**Nasıl sınanacak (ÖNEMLİ):** K52-tarzı **backtest**, arşivde v1-budama vs v2-budama eşleşmeli
(aynı koşular). Canlı paralel sistem KURMA — Altılı 6/6 varyansı o kadar uç ki canlı akış
ölçülemez. Kanıt: 13 olayda (24 sonuçlanan kupon, 5 gün) net **+16.344 TL / +%1028 ROI**
ama **tamamı tek bir 6/6'dan** (23.07 Ankara 2., 90 TL → 17.934 TL). O tek kupon olmasa
−1.590 TL / −%100. n=1 isabetle canlı kıyas istatistiksel gürültü; ayırt edilemez.
**Şart:** Kuralı tek YURİBOYKA vakasına göre kurgulama (hindsight/overfit — K33/K52 yasağı);
genel ilke olarak sabitle, backtest robust üstünlük gösterirse konuş.

### 2. 4'lü / 5'li / 7'li kupon türleri
**Eklendi:** 2026-07-24 (kullanıcı "sonra" dedi) · **İlgili:** K5, K46
TJK'nın diğer çok-koşulu bahisleri. Altılı (K53) deney olarak kuruldu; diğerleri henüz yok.
K46'da "tüm bahis türleri" veriyle reddedilmişti — bunlar açılırsa yine deney amaçlı
(gerçek bahis değil), önce backtest ile efektiflik sınanarak açılmalı.

### 3. defter.html'i K55 görsel diline çevirme
**Eklendi:** 2026-07-24 (teklif edildi, istenmedi) · **İlgili:** K55
altili.html / paper.html K55 zengin formatına geçti (tahminler + sistem sırası + kazanan +
kamu sırası + oran + bedel + ödül + toplam). defter.html hâlâ eski düzende. İstenirse aynı
`rapor_ortak.py` yapıtaşlarıyla çevrilebilir; sistemin veri akışına dokunmaz.

---

## ZAMANLI — takvime bağlı

### 4. Paper test karar noktası — 25 Eylül 2026
**İlgili:** K42, K48
K42 kâğıt testi 25 Eylül 2026'ya kadar koşuyor. O tarihte sistem modu kararı: günlük devam /
talep-üzerine / arşivle. Karar için sicil o güne kadar birikecek.

### 5. Dış yedek yükleme (KULLANICI görevi)
**İlgili:** yedekleme
`at-yedek-2026-07-03.zip` (196 MB) Google Drive'a veya USB'ye yüklenecek. Diskte tek kopya
= tek arıza noktası. Haftalık git commit (K50) kod+veriyi korur ama tam arşiv değil.
**Durum:** doğrulanmadı.

---

## KAPALI / KARARA BAĞLANMIŞ — tekrar açma, gerekçesi var

- **Gerçek bahis çerçevesi** — ❌ askıya alındı (K48): kullanıcı gerçek para oynamıyor.
  Sistem ölçüm/öğrenme deneyi olarak sürüyor.
- **"Tüm TJK bahis türlerine genişlet"** — ❌ veriyle reddedildi (K46): pazar etkin +
  %25-31 kesinti; Arap pazarı da negatif çıktı.
- **Plase modeli (Plackett-Luce)** — ❌ backtest'te başarısız (K44): −%12,5 OOS.
- **9 bağımsız edge testi** (ganyan/exacta/Altılı/chalk-exotic/özellik batch'leri) — ❌ hepsi
  negatif; yapısal engel etkin pazar + kesinti (K19-K33, K44, K46, K52).
