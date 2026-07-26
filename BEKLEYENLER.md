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

### 4. Kupon zamanı analizi — 30 vs 15 vs 10 dk (oran_log verisiyle, OFFLINE)
**Eklendi:** 2026-07-24 · **Güncellendi:** 2026-07-25 · **İlgili:** K59 · **TETİK:** ~2-3 hafta
oran_log verisi (yeterli Altılı günü) biriktiğinde. **Kullanıcı kararı (2026-07-25): canlı zamanlama
30 dk KALSIN; bu soru canlıyı değiştirmeden, simülasyonla cevaplanacak.**
`oran_log.py` (K59) her ayağın oranını farklı anlarda (30 / 15 / ~5 dk kala) biriktiriyor.
**Yöntem:** her Altılı için, 15-dk ve 10-dk snapshot oranlarından bot2'yi YENİDEN hesapla
(bot1 sabit, sadece piyasa bileşeni değişir) → `kupon_kur`'u tekrar koştur → 30 vs 15 vs 10 dk
kuponların isabetini **maliyet-sonrası** kıyasla. Canlı build hiç değişmez (güvenli + kayıt tutarlı).
**Operasyonel taban:** görev 15 dk'da bir çalışıyor → 30 dk penceresi ~2 geçiş, 15 dk ~1 geçiş,
**10 dk'ya hiç geçiş düşmeyebilir** (o gün kupon kurulamaz) → 10 dk pratik taban değil, sadece simüle et.
**Uyarılar:** (a) tek örnek 23.07 Ankara-2'de kayma LEHİMİZE çalıştı (6/6 tuttuk); 25.07 İzmir 1.
ayakta ise ALEYHİMİZE (K59'un ilk canlı drift örneği: #4'ü 4. sıradayken aldık, posta anında 5.'ye
düştü). İki yön birden var → karar veriyle. (b) 15/10 dk bile final oran değil (en sert para son ~5 dk).
(c) Etkin-pazar tezi (K1): geç kur = kalabalığı daha çok taklit = kesintiye yaslanmak → "az kayma"
otomatik "daha çok kâr" değil.

### 5. Altılı sonuçlamada favori-devri kuralı — BİLİNEN MODELLEME BOŞLUĞU
**Eklendi:** 2026-07-24 · **İlgili:** K59 · **TETİK:** doğruluk kritikleşirse / kullanıcı isterse
Kupona yazdığımız bir at kupon kurulduktan (30 dk) SONRA çıkarsa (KOSMAZ), TJK'da o ayaktaki pay
**posta-favorisine devreder**. Kâğıt sistemimiz bunu uygulamıyor — çıkan seçim ölü seçim sayılıyor
(`sonucla_altili` sadece kazananı okuyup "bizim seçimimizde mi" diye bakar). **Etkisi nadir ve
muhafazakâr:** ancak (seçtiğimiz at çıkar) VE (o ayağı posta-favorisi kazanır) VE (favoriyi zaten
yazmadıysak) devreye girer; yönü sonucu **daha kötü** gösterir, asla yanlış-pozitif üretmez → "Altılı
−EV" bulgusunu bozmaz. Bu yüzden ertelendi. **Not:** kâğıt sonucu birebir TJK muhasebesi sanılmamalı.
Yapılırsa: `sonucla_altili`'de çıkan-seçim tespiti + o ayağın posta-favorisini kazanan yerine koyma.

### 6. Model AĞIRLIKLARINI genişletilmiş pencereyle yeniden fit etme (walk-forward'ı ileri kaydır)
**Eklendi:** 2026-07-25 · **İlgili:** K38, K48 · **TETİK:** mevcut sınav dönemi kapanınca (K42/K48
kararı, 25 Eylül 2026 veya sistem modu netleşince)
**Durum bugün:** Özellikler (at formu/kariyeri, jokey 365-gün isabeti) güncel arşivden (2026 dahil)
her tahminde üretiliyor → sistem atları/jokeyleri **tanıyor**. AMA model AĞIRLIKLARI donuk:
Bot1 katsayıları ≤2024, Bot2 harman (α,γ) 2025 ile fit; **2026 koşuları ağırlıkları değiştirmiyor.**
Bilerek: 2025-26 temiz walk-forward **sınav** dönemi; şimdi yeniden eğitmek "modelin kenarı var mı"
ölçümünü kirletir. **Seçenek:** sınav bitince ağırlıkları genişletilmiş pencerede (≤2025 veya ≤2026)
yeniden fit et → "kural kitabı" da yeni veriden öğrensin. **Ödünç:** bunu yapınca o test dönemi
eğitime dönüşür, temiz OOS biter → yeni bir sınav dönemi tanımlamak gerekir. Sadece katsayı meselesi;
özellikler zaten güncel. **Not:** track/kulvar/par özellikleri ≤2024 sabit (K38) — o da bu turda gözden geçirilebilir.

### 7. EV-maksimize dağıtım — kamu ile AYRIŞTIĞIMIZ ayağa genişlik ver
**Eklendi:** 2026-07-26 · **İlgili:** K65, K1 · **TETİK:** kullanıcı isterse (beklenti DÜŞÜK)
K65 "isabet-maksimize" (açgözlü) dağıtımı çürüttü: şekil istenen hale geldi (tek atlı ayak %5,9→%98,7)
ve 6/6 sayısı arttı (185→225), **ama para kötüleşti** (ROI(6) −41,2→−55,0) çünkü açgözlü güvendiği
ayağa tek at = kamu favorisi = kalabalık havuz → ort. temettü yarıya düşüyor (1.656→798 TL), büyük
ödemeler (47.383→22.374) sistematik kaçıyor. **Test EDİLMEYEN üçüncü aile:** bütçeyi *bot2 ile kamu
AGF'sinin en çok ayrıştığı* ayağa ver (kenar kalabalıkla anlaşmaktan değil, ondan ayrılmaktan gelir).
Aynı koşum (`kod/altili_dagitim_test.py`) üstünde yeni bir dağıtıcı olarak eklenebilir; ölçüt yine
ROI(6) + eşli bootstrap GA. **Uyarı:** K1 etkin-pazar duvarı + K19-K33/K44/K46/K52'de 9 kenar testi
zaten negatif çıktı; bu da büyük ihtimalle negatif çıkar. Ucuz olduğu için açık bırakıldı, umut değil.

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
