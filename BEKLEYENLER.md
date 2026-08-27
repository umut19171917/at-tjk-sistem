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

### 2. ✅ ÖLÇÜLDÜ ve KAPANDI (2026-08-18, K108) — 4'lü/5'li REDDEDİLDİ, mekanizma yok
**Eklendi:** 2026-07-24 · **KAPANDI:** 2026-08-18 (K108) · **İlgili:** K5, K46, K74, K75, K84, K94, K107, K108

> ## 🔒 KAPANIŞ ÖZETİ (K108, 18 Ağu 2026)
>
> **Ölçüldü, reddedildi.** Araç: `kod/nli_backtest.py`. Tasarım: 4'lü/5'li/6'lı TJK'da aynı
> koşuda biter ve ayakları iç içedir (4.931 üçlünün %100'ü) → **990 eşleşmiş olayda**, aynı
> gün/pist/saha, **aynı parayla** (TL eşitlendi, birim fiyatlar farklı: 1,75/1,50/1,25) kıyas.
>
> - **S1 (mekanizma):** 16 testin **1'i** geçti; şansa beklenen 0,8. Geçen hücre ne fiyat-güvenli
>   alt kümede ne öteki dağıtıcıda tekrarlıyor. **Fark neyse kesintinin ucuzluğuyla açıklanıyor.**
> - **S2 (oynanabilirlik):** 24 hücrenin **sıfırında** ROI ≥ 0. En iyi hücre **−%38,5** (4'lü).
> - **S3 (tavan):** Ayak azalınca isabet **4-8 kat** artıyor, ortalama ödeme **0,15-0,54 katına**
>   düşüyor, çarpım ~**1,0**. K98-h tavanı kısa üründe de aynen geçerli — tavan bir kupon-şekli
>   özelliği değil, **piyasa özelliği**.
>
> **K84'ün devir gözlemi açıklandı:** devir günü 5-ayak medyanının 201 kat sıçraması gerçekti
> ama zorluğun göstergesiydi, açıklığın değil (6/6'yı kimsenin bilemediği gün 5'li de zordur).
>
> **YENİDEN AÇILMASI İÇİN:** yeni bir mekanizma iddiası **ve** yeni veri gerekir.
> "Bir daha bakalım" gerekçe değildir. (Kural 6 / K33 overfit yasağı.)

**Aşağıdaki metin KAPANMADAN ÖNCEKİ hâliyle durur — gerekçe zinciri görünsün diye silinmedi.**
**TETİK: KULLANICI hatırlatacak** (2026-07-31'de öyle dedi) — kendiliğinden başlama.

**K84 EKLEDİ — en güçlü gerekçe (31 Tem 2026):** arşivde 6.747 Altılı'nın **24'ünde (%0,36)**
6/6'yı kimse bilemiyor. O günlerde değer az-ayak bahislerine akıyor:

| | devir günü medyan | normal gün medyan | oran |
|---|---|---|---|
| **5 ayak** | **198.489 TL** | 988 TL | **201 KAT** |
| 4 ayak | 18.768 TL | 270 TL | 70 kat |
| 3 ayak | 3.840 TL | 76 TL | 51 kat |

Yani Altılı'nın **en şişkin kuyruğu tam olarak 5-ayak bahsinde** toplanıyor; 6 ayak oynayan
o günlerde eli boş kalıyor. Bu, "4'lü/5'li kuralım mı"yı meraktan çıkarıp ölçülebilir bir
hipoteze çevirdi: *6-ayak ürününde harcadığımız aynı bütçe, 5-ayakta kuyruğu yakalar mı?*

**İşe başlarken İLK doğrulanacak şey:** mekanizma kural kitabından teyit edilmedi — ölçülen
şey güçlü bir birliktelik (n=24). "6/6 sahipsiz kalınca havuz az-ayak bahislerine mi dağıtılıyor,
yoksa bu sadece o günlerin zorluğunun yansıması mı?" Bu ayrım yapılmadan strateji kurulmaz.

**Neden artık ciddi bir aday:** K74, Altılı havuzunda **gerçek ve büyük** bir yanlılık ölçtü —
AGF payı %2'nin altındaki atlar havuzun dediğinin **2,73 katı** kazanıyor; ganyanın AGF'den çok
daha şanslı gördüğü atlarda oran **3,40**. K75 bunu Altılı kuponuna çevirmeyi denedi ve
**başarısız oldu** — ama başarısızlığın sebebi yanlılığın sahte olması değil, **çarpımın uzunluğu**:
- Yanlılık **ayak başına** gerçek (2,73 kat)
- Altılı **6 ayağın çarpımı** → 6 ayağı birden ucuz attan seçmek isabeti sıfırlıyor (λ=1'de
  1318 koşuda **sıfır** isabet), üstelik temettü havuzla sınırlı olduğu için teorik kazanç
  (2,73⁶ = 419 kat) hiçbir zaman gerçekleşemiyor.

**Hipotez:** Aynı ayak-başı kenar, **daha kısa çarpımda daha az yıkıcı** birleşir. 4'lü = 4 çarpım,
5'li = 5, Altılı = 6. İsabet çöküşü üstel olduğu için ayak sayısını azaltmak dengeyi ciddi
biçimde değiştirebilir. Bu, 12 negatif Altılı testinden sonra kalan **tek yapısal fikir**.

**~~ÖN KOŞUL — veri yok~~ → KARŞILANDI (K107, 18 Ağu 2026).** Eski not `veri/altili_tam.csv`'ye
bakıyordu (orada gerçekten yalnız 6'lı t6/t5/t4/t3 var) ama **veri K94'ten beri elimizdeydi:**
`veri/nli_ganyan.csv`, K94'ün kesinti ölçümünün yan ürünü olarak üretilmiş ve fark edilmemiş.

| ürün | olay | temettü dolu | ayak race_kod'ları dolu | medyan temettü |
|---|---|---|---|---|
| 3'lü | 8.060 | ✅ | ✅ | 73 TL |
| **4'lü** | **5.691** | ✅ | ✅ | **249 TL** |
| **5'li** | **6.519** | ✅ | ✅ | **1.006 TL** |
| 6'lı | 6.813 | ✅ | ✅ | 5.774 TL |
| 7'li | 359 | ✅ | ✅ | 170.016 TL |

Temettü **ve** ayak kodları birlikte duruyor → backtest için gereken her şey var.
**Eski 1-3. maddeler düşer** (tara / kazıya ekle / olay tablosu üret). Doğrudan 4. maddeden
başlanır:

4. Backtest: aynı `bot2/AGF^λ` ailesi, 4 ve 5 ayakta. Bütçe Altılı ile **eşitlenerek**
   (aynı para, farklı ayak sayısı) — yoksa kıyas anlamsız olur.

**ÖLÇÜT ÖNCEDEN BAĞLANACAK** (K33/K52): kol açılmadan önce "hangi sonuç fikri öldürür"
yazılır. K75'in λ taraması (ROI λ=0,25'ten itibaren kötüleşiyor) ilgili önsel; kesinti farkı
da zayıf (4'lü %45,6 · 5'li %46,8 · 6'lı %48,6 → **yalnız 2-3 puan**).

**Beklenti (önceden yazılıyor):** düşük. 12 test negatif, kesinti ~%49 ve muhtemelen bu
bahislerde de benzer. Ama ilk kez körlemesine değil, **ölçülmüş bir mekanizmayı takip ederek**
bakıyor olacağız — o yüzden yapmaya değer.

### 11. İSTANBUL AYKIRISI — post-hoc desen, ÖN-KAYITLI ölçütle sınanacak (K122)
**Eklendi:** 2026-08-26 (K122) · **TETİK: SAYISAL** — ≥400 yeni İstanbul ayağı

**Gözlenen (26 Ağu, 2.850 ayak):** aynı ayakta aynı genişlikte kamuyla kıyasta İstanbul
**−3,2 puan**, diğer dört pist **+2,7 puan**. Olay-bootstrap farkı **−6,0 [−10,2, −1,7]**,
sıfırı dışlıyor. Saha kovası içinde de İstanbul üç kovanın üçünde negatif → **saha etkisi
değil**. bot1 de yalnız İstanbul'da bot2'yi geçemiyor (−1,8).

**AMA POST-HOC.** Desen görüldükten sonra kurulan kıyas; K33/K52 gereği bu haliyle hüküm
kurmaz. Bu karardan SONRA biriken veriyle sınanacak.

**ÖN-KAYITLI ÖLÇÜT (sonuç görülmeden yazıldı):**
- **H:** İstanbul'da kamu-fark'ımız diğer pistlerdekinden düşüktür.
- **Ölçüm:** ≥400 YENİ İstanbul ayağı biriktiğinde `kod/pist_analiz.py` + olay-bootstrap ile
  (İstanbul farkı − diğer farkı) hesaplanır.
- **DOĞRULANDI** sayılır ancak %95 GA **tamamen sıfırın altındaysa**.
- **DÜŞER** ve kol KAPANIR: GA sıfırı içeriyorsa.
- **Karar sınırı:** doğrulansa BİLE "İstanbul oynamayalım" demek değildir — kâğıt deneyinde
  pist elemek örneklemi daraltır ve öğrenmeyi yavaşlatır. Doğrulanırsa yapılacak iş
  MEKANİZMAYI ölçmektir (hipotez: havuz derinliği ↑ → piyasa verimliliği ↑ → K112).

**Mevcut hız:** İstanbul'da ~792 ayak / 5 hafta → ~400 yeni ayak ≈ **2,5-3 hafta** (Ekim ortası).

### 15. ✅ AÇILDI ve AYNI GÜN KAPANDI (2026-08-27, K125 → K126 → K127) — ÇİFTE REDDEDİLDİ

> ## 🔒 KAPANIŞ ÖZETİ (K127, 27 Ağu 2026)
>
> **Üç kapıdan ikisi geçildi, üçüncüsü düştü.** Araçlar: `kod/kesinti_kalibre.py`,
> `kod/cifte_h1.py`, `kod/cifte_h2.py` — hepsi salt-okunur, ölçütleri önceden mühürlü.
>
> | kapı | soru | sonuç |
> |---|---|---|
> | **kesinti** (K125) | vergi ödenebilir mi? | **GEÇTİ** — %27,2; projedeki en ucuz çok-ayaklı |
> | **H1** (K126) | havuz kalibresiz mi? | **GEÇTİ** ama zayıf: favori havuz ortalamasını +3,9 puan yeniyor (Altılı'da +31,6) |
> | **H2** (K127) | model kalabalığı yeniyor mu? | **DÜŞTÜ** — +0,98 puan, %90 GA [−5,07..+7,05] sıfırı içeriyor |
>
> **Güç sorunu YOKTU:** 319 uyumsuz çift (asgari 6). Ölçüm yapılabildi, cevap "hayır" çıktı.
> Model ve kalabalık olayların **%85,2'sinde aynı çifti** seçiyor; ayrıştığı yerde de fark yok.
>
> **Yapısal ders:** ÇİFTE, projenin aradığı boşluğun tam adresiydi (ucuz vergi + çok ayak).
> Boşluk gerçekten oradaydı; **içinde bizim kenarımız yoktu.** Vergiyi %48,6'dan %27,2'ye
> indirmek işe yaramadı çünkü kenar sıfır — **sıfırın vergisi de sıfırdır.**
>
> **YENİDEN AÇILMASI İÇİN:** yeni bir mekanizma iddiası **ve** yeni veri gerekir
> (Kural 6 / K33). "Bir daha bakalım" gerekçe değildir.

**Aşağıdaki metin KAPANMADAN ÖNCEKİ hâliyle durur — gerekçe zinciri görünsün diye silinmedi.**

### 15-özgün. ÇİFTE KOLU — **AÇILDI** (K125). Kesinti kapısı geçildi, KENAR kapısı bekliyor
**Eklendi:** 2026-08-27 (K125) · **TETİK: SIRASI GELİNCE** · **İlgili:** K13, K73, K74, K123, K124, K125

**Neden açıldı:** ÇİFTE'nin kesintisi **%27,2 [26,4..28,0]** — projede ölçülen en düşük
çok-ayaklı kesinti. İki bağımsız yöntem aynı bandı gösterdi (kalibre ölçer %27,2; modelden
bağımsız temettü-oranı sınavı %22,6). Zincir bahislerin geri kalanı %43-57 bandında.

**AÇILMASININ KESİNLİKLE ANLAMI OLMAYAN ŞEY:** kârlılık. K13 zaten **%25,5'lik ganyan
duvarına çarpıp geri dönmüştü.** ÇİFTE'nin %27'si aynı duvar.

**Kolu açan TEK yapısal gerekçe:** K73/K74 Altılı havuzunun kötü kalibre olduğunu ölçtü
(seçimimiz havuz ortalamasını ~30 puan yeniyor) ama %48,6 vergi onu yutuyordu. ÇİFTE,
projede karşılaşılan **tek** bahis ki *çok-ayaklı havuz verimsizliği* ile *ganyan seviyesinde
vergi* aynı üründe buluşuyor.

**ÖN-KAYITLI ÖLÇÜT (sonuç görülmeden yazıldı — ölçüme başlamadan ÖNCE bu blok mühürlenecek):**
- **H1 (havuz kalibrasyonu):** ÇİFTE havuzu Altılı havuzu kadar kötü kalibre mi? Ölçüm:
  K74'ün yanlılık haritası ÇİFTE'ye uygulanır (kazanan çiftlerin ima edilen payı vs gerçek
  isabet). **Yanlılık yoksa kol KAPANIR** — model kurmaya girilmez.
- **H2 (kenar):** Bot2'nin ÇİFTE olasılıkları, aynı olaylarda kamunun (ganyan-türevli çarpım)
  olasılıklarını **log-loss'ta** yeniyor mu? Eşleşmiş olay, olay-bootstrap %95 GA.
  **Yenmiyorsa kol KAPANIR.**
- **H3 (para):** ancak H1 ve H2 geçilirse. Kupon/ROI ölçümü; eşik **ROI ≥ 0'ın %90 GA alt
  sınırı > −%5**. Aksi halde KAPANIR.
- **Güç eşiği:** K107, ≥6 uyumsuz çift. Kapsama eşiği: K106, %90.
- **Fiyat kaynağı:** K110 kuralı — resmî kapanış (`defter.ganyan_kapanis`), `oran_log` DEĞİL.

**KIRILMA NOKTASI — önce bu doğrulanmalı:** hükmün tamamı **ÇİFTE biriminin 1,00 TL** olmasına
dayanıyor. Birim 1,25 olsaydı kesinti %40,7 çıkar ve **kol kapanırdı.** Dayanak arşivden
çıkarım (asgari temettü 6 yıl boyunca enflasyonla sürüklenmiyor: 1,40·1,25·1,30·1,35·1,35·1,00),
**TJK'nın resmî tarifesinden okunmuş değil.** K86 resmî tarifeyi bulamamıştı; ÇİFTE için
tekrar aranmalı. Resmî değer 1,00 değilse **bu kol derhal kapanır.**

### 18. ÇİFTE'de bot1 deseni — POST-HOC, ön-kayıtlı ölçütle sınanacak (K127)
**Eklendi:** 2026-08-27 (K127) · **TETİK: SAYISAL** — ≥1.000 yeni ÇİFTE fırsatı

**Gözlenen (2.155 olay, 2026):** K127'nin ön-kayıtında **"yalnız bağlam"** diye işaretlenen
`bot1` kolu (oran-kör), kalabalığın favorisini **+16,19 puan** geçti (ROI −%9,5 vs −%25,6).
bot1 oran-kör olduğu için seçimi bahis kapanmadan bellidir — yani **sızıntısız**.

**AMA HÜKÜM DEĞİL, üç sebeple:**
1. **GA sıfırı içeriyor:** %90 GA [−2,36 .. +35,49], %95 GA [−5,54 .. +39,43].
2. **Birkaç uç ödemeye dayanıyor:** en büyük TEK ödeme çıkarılınca ROI −%9,5 → −%13,6;
   en büyük ÜÇ çıkarılınca **−%21,1** = kalabalığın seviyesi. (K57/K72'nin aynı tuzağı.)
3. **Ön-kayıtta hükme dahil değildi.** Sonucu görüp ölçüt değiştirmek K33/K52 yasağıdır.

**ÖN-KAYITLI ÖLÇÜT (sonuç görülmeden yazıldı):**
- **H:** ÇİFTE'de bot1'in seçimi kalabalığın favorisini ROI'de geçer.
- **Ölçüm:** ≥1.000 YENİ ÇİFTE fırsatı biriktikten sonra `kod/cifte_h2.py` yeniden koşulur;
  bot1−kamu farkı olay-bootstrap ile.
- **DOĞRULANDI** sayılır ancak (a) %95 GA tamamen sıfırın **üstünde** VE (b) **en büyük üç
  ödeme çıkarıldığında da** fark pozitif kalırsa. İkisi birden gerekir.
- **DÜŞER ve kol KAPANIR:** ikisinden biri tutmuyorsa.
- **Karar sınırı:** doğrulansa BİLE bu "çifte oynayalım" demek değildir — −%9,5 hâlâ kayıptır.
  Doğrulanırsa yapılacak iş, bot1'in oran-kör seçiminin nerede değer bulduğunu ölçmektir
  (K122'nin bot1×pist deseniyle bağlantılı olabilir).

**Mevcut hız:** 2026'da ~3.058 fırsat / ~8 ay → 1.000 yeni fırsat ≈ **2,5-3 ay** (Kasım sonu).

### 19. ✅ ÖLÇÜLDÜ ve KAPANDI (2026-08-27, K133) — birleşim kapıyı GEÇTİ, kupona GEÇMEDİ

> ## 🔒 KAPANIŞ ÖZETİ (K133, 27 Ağu 2026)
>
> **19-A (birleştirme): kalibrasyon kapısı GEÇİLDİ.** B1 ∪ B2 — alpha 0,190→0,196,
> Bot2 OOS 1,6987→1,6976, fark −0,0011 %95 GA [−0,0021, −0,0001]. Üç şartın üçü de tuttu.
> Bu, oturumun model tarafında ön-kayıtlı kapıyı geçen ilk varyantı.
>
> **BEKLENTİM YANLIŞTI:** "eşdoğrusaldır" demiştim; toplanabilirlik **0,99** çıktı — B1 ve B2
> **bağımsız** (biri değişkenler ARASI, öteki değişken İÇİ eğrilik yakalıyor).
>
> **AMA PARA KAPISI GEÇİLMEDİ — zaten ölçülmüştü.** `bot1_kupon.py`'nin "bot1+" varyantı
> tam olarak bu birleşimdir; K132 kuponda **−0,019 ayak** ölçtü (GA sıfırı içeriyor).
> **Canlıya alınması için gerekçe YOK.**
>
> **BÜYÜkLÜK — abartılmasın:** Bot2'nin piyasa üzerindeki toplam katkısı 0,0066; AB bunu
> ~%17 büyütüyor. Kıyas: AGF (K129) bunun **19 katını** verdi ve kuponu yine oynatmadı.
>
> **19-B ("bot1'i farklı kılmak"): SORULAMADI, kol kapanıyor.** n=5 betimleyici tablo, iki
> korelasyon birbirine çok yakın (0,871 vs 0,826) ve deseni tek nokta (C1) taşıyor.
> Cevaplanması için doğruluğu SABİT tutup uzaklığı kasten değiştiren varyantlar gerekir —
> ayrı ve pahalı bir iş, ve kol zaten kâr vaadi değildi.
>
> **YENİDEN AÇILMASI İÇİN:** yeni MEKANİZMA gerekir (Kural 6 / K33).

**Aşağıdaki metin KAPANMADAN ÖNCEKİ hâliyle durur.**

### 19-özgün. BİRLEŞTİRME + "bot1'i FARKLI kılmak" — K128'in açtığı kol
**Eklendi:** 2026-08-27 (K128) · **TETİK: SIRASI GELİNCE** · **İlgili:** K33, K110, K112, K128

**K128 ne buldu:** doğrusal-olmayan biçim (B1 etkileşimler, B2 spline) bot1'i **−0,0046 /
−0,0048** log-loss iyileştirdi — K33'ün son özellik denemesinin **46 katı**. Ama Bot2'ye
yalnız **%10-13'ü** geçti, çünkü α=0,19. Hiçbir varyant Bonferroni kapısını geçemedi.

**İKİ AYRI İŞ — karıştırılmasın:**

**19-A. Birleştirme (ucuz, dar).** B1+B2 birlikte denenmedi (K128 madde 6: 2^9 kombinasyonda
arama overfit kapısıdır). Denenecekse **tek bir** birleşim, önceden bağlanmış:
`B1 ∪ B2` (5 etkileşim + 13 spline tabanı), başka hiçbir kombinasyon taranmadan.
- **Ölçüt:** K128'in aynısı — α↑ **ve** Bot2 OOS log-loss↓ **ve** GA sıfırın altında.
  Tek varyant olduğu için Bonferroni gerekmez, %95 GA yeter.
- **Beklenti (önceden yazılıyor):** düşük. B1 ve B2 aynı şeyi (doğrusal-olmayanlık) iki farklı
  yoldan yakalıyor, bot1 iyileşmeleri neredeyse eşit (−0,0046 / −0,0048) → büyük olasılıkla
  **eşdoğrusal**, toplamları toplamları kadar olmaz. Yine de bot1 −0,008'e inse bile Bot2'ye
  ~0,001 geçer; **kâra dönüşmez.** Bu iş "kapatmak için" yapılır, umut için değil.

**19-B. Asıl soru: bot1'in sesi neden kısık?** α bir tercih değil, 2024'te fit edilen cevap:
*fiyat verildiğinde bot1'in kattığı BAĞIMSIZ bilgi kadar.* K128 gösterdi ki bot1'i daha
**doğru** kılmak α'yı kıpırdatmıyor (B1/B2: α 0,190→0,194/0,191). Ama C1 (sıra-patlatmalı
eğitim) bot1'i **kötüleştirdiği hâlde** α'yı **0,220**'ye çıkardı — yani daha kötü ama piyasayla
daha az örtüşük.

- **H:** α'yı yükselten şey doğruluk değil, piyasadan FARKLILIK'tır.
- **Ölçüm:** bot1'i kasten piyasadan uzaklaştıran varyantlar (ör. piyasayla en örtüşük
  özellikleri budamak; ya da bot1'i piyasa-artığı üzerine eğitmek) → α ve Bot2 OOS log-loss.
- **GEÇER:** yalnızca Bot2 OOS log-loss'u %95 GA ile düşüren bir varyant çıkarsa.
- **DÜŞER:** α yükselip Bot2 düzelmiyorsa — ki K128'in deseni bunu bekletiyor.
- **KARAR SINIRI:** bu kol **kâr vaadi değildir.** Bot2'nin piyasa üzerindeki toplam katkısı
  0,0066; kesintiyi aşmak için gereken mertebe bunun kat kat üstünde. Kol, "nereye
  bakmayacağımızı" kesinleştirmek için açık.

**KAPALI TUTULACAK:** yeni ÖZELLİK ekleme (K33). K128 o kapıya dokunmadı, bu kol da dokunmaz.

### 20. `ganyan_muhtemel` KUSURU — ne yapacağımıza karar verilecek (K130)
**Eklendi:** 2026-08-27 (K130) · **TETİK: KULLANICI** · **İlgili:** K1, K3, K97, K109, K111, K129

**Bulgu:** `katilim.csv`'de `ganyan_muhtemel` == `ganyan_kapanis`, 6 yılın %100'ünde
(342.986 at-satırı, ort. mutlak fark 0,0007). Sebep: arşivdeki **program** sayfaları koşudan
SONRA çekilmiş, `GANYAN` alanı kapanış oranını taşıyor. K1'de *"ganyan muhtemel mi kapanış mı
teyit"* diye bir yapılacak vardı, hiç yapılmamış.

**CANLI AKIŞ ETKİLENMİYOR** — `altili_canli.py`/`gunluk.py` oranları `oran_log`'tan gerçek
zamanlı okuyor. Etkilenen yalnız BACKTEST'in piyasa terimi (`model.py`, `altili_olasilik.py`).

**ÜÇ SEÇENEK — karar KULLANICININ:**
1. **Hiçbir şey yapma, yalnız BELİRT.** `model.py`/`altili_olasilik.py`'nin başına uyarı yaz,
   Kİ satırlarına atıf koy. Maliyet ~0. Gerekçe: geçmiş backtest'ler geriye dönük
   temizlenemez (arşivde gerçek erken oran YOK; `oran_log` yalnız Tem 2026'dan beri var).
2. **İleri-yönlü temiz kol.** Bugünden itibaren `oran_log`'un **kupon anı** oranını ayrı bir
   sütuna biriktir; yeterli veri olunca (≈400 olay) "temiz zemin" backtest'i kur ve mevcut
   iyimser zeminle KIYASLA. Böylece iyimserliğin BÜYÜKLÜĞÜ ölçülür.
3. **Sütunu sil/yeniden adlandır.** `ganyan_muhtemel` → `ganyan_resmi` yap, ikinci kopyayı
   kaldır. **RİSKLİ:** üretim hattının çok yerinde geçiyor; kullanıcı "kuponlara dokunma"
   dedi. Bu seçenek ancak açık izinle ve ayrı bir oturumda yapılır.

**ÖNERİM: 1 + 2.** Uyarıyı hemen yaz (bedava), temiz kolu ileri-yönlü aç (risksiz).
3'e dokunma.

**ÖNEMLİ — geçmiş kararlar geçersiz DEĞİL:** negatif sonuçlar **iyimser** bir zeminde
alınmıştı; gerçek zemin daha kötüyse negatifler **daha da güçlenir.** Risk yalnız backtest'te
ARTI görünen hücrelerde — ve onların hiçbiri zaten sıfırdan ayrılamıyordu.

### 21. AGF — kupon kolu kapandı, ama kalibrasyon bulgusu duruyor (K129)
**Eklendi:** 2026-08-27 (K129) · **TETİK: KULLANICI**

**Kapanan:** AGF'li üçlü olasılığı kupona vermek. Ön-kayıtlı para kapısı düştü
(ROI farkı −58,6 puan, %95 GA [−131,2..−5,5]; ayak isabeti +0,020, GA sıfırı içeriyor).

**Kapanmayan — ve ilginç olan:** AGF, **ganyan kapanışından daha iyi kalibre**
(OOS log-loss 1,7817 vs 1,8047) ve üçlü harmanda δ=+0,586 ile Bot2'yi **−0,0214** iyileştiriyor
— K128'in en iyisinin **36 katı**. Ayrıca AGF 3,5 saat önceden bellidir ve değişmez
(ρ=0,9999) — ganyan oranının aksine.

**AÇIK KALAN SORU:** kupon dışında AGF'nin işe yarayacağı bir yer var mı? Somut aday:
**raporlarda ikinci bir görüş sütunu.** Kupon seçimini DEĞİŞTİRMEDEN, günlük raporda her
ayağın AGF sırası gösterilirse, sistemin ve kalabalığın ayrıştığı yerler GÖRÜNÜR olur.
Bu bir strateji değişikliği değil, **gözlem** eklemesidir — kuponlara dokunmaz.
- **Karar KULLANICININ.** Yapılacaksa `rapor_ortak.py` düzeyinde, kupon üretimine
  dokunmadan. Yapılmayacaksa bu madde kapanır.
- **UYARI:** görünce oynamak isteme eğilimi gerçektir. K129 ölçtü ki AGF'yi kupona katmak
  **para kazandırmıyor.** Sütun eklenirse "bilgi" olarak kalır, karar kuralı olmaz.

### 16. ✅ KAPANDI (2026-08-27, K134) — ÖLÇÜLEMEZ: bu bahisler küçük sahada hiç oynatılmıyor

> 🔒 **KAPANIŞ (K134):** birim fiyatı arşivden okumanın tek yolu tabanın dövülmesidir.
> TABELA, TABELA SIRASIZ ve SIRALI 5'Lİ **saha ≤6 koşularda HİÇ oynatılmıyor** (0 olay)
> → temettü hiçbir zaman tabana inmiyor → birim okunamaz. **Yapısal, geçici değil.**
> **Açılma şartı:** TJK'nın resmî 2026 tarifesi bulunursa derhal ölçülebilir.
> **Yan bulgu:** ÜÇLÜ BAHİS'in 2021-22 birimi **1,25 TL** okundu (asgari 1,31 = 1,25×1,05;
> 8 ve 7 olaylık yığılma) — K124'ün bağımsız "birim ≥ 1,25" alt sınırıyla birebir tutuyor.

### 16-özgün. TABELA BAHİS ve SIRALI 5'Lİ — **BELİRSİZ**, birim fiyat bulunursa karara bağlanır
**Eklendi:** 2026-08-27 (K125) · **TETİK: KULLANICI / birim fiyat kaynağı bulunursa**

K125 bu ikisi için yalnız **alt sınır** verebildi (birim ≥ 1,00 varsayımıyla): TABELA
**≥%28,5** [24,1..32,0], SIRALI 5'Lİ **≥%33,0** [28,8..36,7]. Ne %40 eşiğini geçiyorlar
(kapanmıyorlar) ne %30'un altında kalıyorlar (açılmıyorlar).

**Neden nokta hüküm verilemedi — iki ayrı sebep:**
1. **Birim tanımlanamıyor.** Asgari temettüleri 6 yıl boyunca enflasyonla sürükleniyor
   (TABELA 6,29→3,37 dalgalı, SIRALI 5'Lİ 13,0→325,6) → taban hiç dövülmüyor → arşivden
   okunamıyor. K86'da olduğu gibi TJK yayımlamıyor.
2. **Ailede çapa yok.** Derin sıralı bahislerde (ilk 4 / ilk 5, sırayla) Harville yanlılığı
   derinlikle birikir ve bu ailede değeri bağımsız yöntemle bilinen tek bir bahis bile yok.
   ÜÇLÜ BAHİS de aynı sebeple ölçülemedi (yalnız birim ≥ 1,25 TL olduğu çıkarıldı).

**Beklenti (önceden yazılıyor):** düşük. Birim 2,00 TL olsaydı ikisi de %64-67'ye çıkar ve
kapanırdı; Harville yanlılığı da kesintiyi olduğundan DÜŞÜK gösteriyor. **İkisinin de gerçek
kesintisinin egzotik bantta olması muhtemel** — ama bu bir tahmin, ölçüm değil.

**Açılış şartı:** ya TJK'nın resmî tarifesi bulunmalı, ya da bu ailede kesintisi bağımsız
yöntemle bilinen bir çapa üretilmeli.

### 17. ✅ KAPANDI (2026-08-27, K134) — teşhis ilerledi (%26 → %51,4) ama kalite kapısı geçilemedi

> 🔒 **KAPANIŞ (K134):** K125'in varsayımı yanlışmış — ayaklar **plase değil, İLK 2**'dir;
> buna **çıkanlar (kosmaz)** ve **ekürie ortakları** eklenir. Doğrulama %26 → **%51,4**.
> **Pencere DOĞRUYMUŞ:** kartın bütün 7'li dilimleri taranınca eşleşenlerin %100'ü
> varsayılan pencerede çıktı (K94 kuralı). Benim "pencere yanlış olabilir" tahminim YANLIŞTI.
> Kalan **%48,6** çözülemedi (muhtemelen beraberlik + yayımlanmayan ödeme kuralları)
> → kalite kapısı (%90) geçilemiyor → kesinti ölçülemez.
> **Açılma şartı:** TJK'nın ödeme kuralı belgelenirse.

### 17-özgün. 7'Lİ PLASE — **ÖLÇÜLEMEDİ**, ayak eşleme teşhisi gerekiyor
**Eklendi:** 2026-08-27 (K125) · **TETİK: SIRASI GELİNCE**

K125'te 447 olayın yalnız **118'i (%26)** kalite kapısını geçti ve kesinti değeri saçma çıktı
(−%50.000 mertebesinde). Diğer bütün bahislerde doğrulama oranı %90-100 olduğuna göre kusur
verinin değil, **ayak eşlemesinin**: bahsin 7 ayağının "bittiği koşuda biten 7 ardışık koşu"
olduğu varsayımı (K94 kuralı) bu bahiste tutmuyor olabilir — 7'Lİ PLASE muhtemelen günün
SABİT 7 koşusunda oynanıyor, kayan pencerede değil.

**Yapılacak:** kombinasyondaki at sayıları (ör. `2,4/2,9/1,7/2,6/3,6/2,4/7,12`) ile o günün
koşularının plase kümeleri karşılaştırılıp doğru ayak penceresi bulunacak. Bulunmadan bu
bahis hakkında **hiçbir şey söylenemez** — ne kapanır ne açılır.

**Not:** 7'Lİ PLASE'nin temettüleri şaşırtıcı derecede DÜŞÜK (2026 medyanı 287 TL; aynı yılın
7'Lİ GANYAN'ı 70.802 TL). Bu, bahsin çok daha sık tutturulduğunu gösteriyor — kesintisi
ölçülmeye değer bir aday yapıyor onu. Ama ölçüm ancak eşleme düzeldikten sonra.

### 3. defter.html'i K55 görsel diline çevirme
**Eklendi:** 2026-07-24 (teklif edildi, istenmedi) · **İlgili:** K55
altili.html / paper.html K55 zengin formatına geçti (tahminler + sistem sırası + kazanan +
kamu sırası + oran + bedel + ödül + toplam). defter.html hâlâ eski düzende. İstenirse aynı
`rapor_ortak.py` yapıtaşlarıyla çevrilebilir; sistemin veri akışına dokunmaz.

### 4. Kupon zamanı — 30 vs 15 dk · **CANLI KOL AÇIK (K105)** · **GERİYE DÖNÜK ÖLÇÜLDÜ (K111)**

> **K111 SONUCU (19 Ağu 2026) — beklentiyi DÜŞÜRÜYOR, kolu kapatmıyor.**
> Ayak düzeyinde eşleşmiş ölçüm (1.548 ayak, 78 Altılı, ölçüt önceden bağlandı):
> - **Bilgi GERÇEK:** kupon anı → 5 dk kala ayak isabeti %56,8 → **%60,3**
>   (+3,5 puan, %95 GA [+0,8, +5,9], McNemar **p=0,0003**).
> - **Ama PARA KÖTÜLEŞİYOR:** ganyan ROI (resmî kapanışla) **−%22,9 → −%25,3**.
>   54 fazla kazanan tutuluyor, toplam getiri düşüyor → geç cetvel **daha ucuz** atları tutuyor.
>   Bu, **K98-h "tavan"ının zaman eksenindeki hâli**: kalabalığa yaklaşmak isabeti artırır,
>   kazancı artırmaz.
> - **Aksiyona dönük versiyonda (yalnız 1. ayak = kuponu 25 dk geç kurmak): İŞARET YOK**
>   (+2,3 puan, GA sıfırı içeriyor, p=0,38).
> - İç kontrol geçti: `bot1` (orana kör) config'lerinde uyumsuz çift **sıfır**.
> - Kapsam %78 → ön-kayıtlı %90 eşiği tutmadı, **config düzeyinde hüküm verilmedi**.
>
> ⚠️ **"5 dk kala kupon" YAPISAL OLARAK ÖLÇÜLEMEZ:** kupon 1. ayak başlamadan kurulur;
> 6. ayağın `defter` kaydı 1. ayaktan ~2,5 saat sonra alınmıştır → kullanmak K97 sızıntısı
> olur. `oran_log` da 1. ayağa en yakın 10,4 dk kala geçiyor. Kolun sorusu ancak **canlı
> kolla** veya Z1'in örneklemi büyüyerek cevaplanır.
>
> **KARAR KULLANICININ:** bu ölçüm kolun beklentisini düşürüyor ama kol farklı bir şeyi test
> ediyor (tüm kupon 30 vs 15 dk) ve kâğıt üzerinde Altılı başına 120 TL. K106 ilkesi:
> veri toplamaya başlamış bir kol teoriyle kapatılmaz.

> **K110 EKLEDİ (19 Ağu 2026):** *"5 dk kala kursak ne olurdu"* sorusu için veri toplamaya
> **gerek yok — zaten elimizde.** `defter.csv` her koşuyu postaya **medyan 0 dk kala**
> kaydediyor (%100'ü ≤6 dk) ve satırda bot1/bot2/kamu/oran **hepsi dolu**; Altılı ayak
> koşularının %88'ini kapsıyor. Yani 5 dk'lık kupon simülasyonu offline kurulabilir,
> canlı sisteme hiç dokunmadan.
> ⚠️ Bunu yaparken `altili_oran_log.csv` KULLANILMAZ: o dosya kapanışı hiç görmüyor
> (medyan 14,9 dk kala durur; K110/§14). Fiyat için `defter.ganyan_kapanis`.

**DURUM DEĞİŞTİ.** "Ekim'i bekle" tetiği 31 Tem'de, oran_log kupon anının tam fotoğrafını
çekmezken kondu; K76 bunu düzeltti ve o gün bugündür doğru veri birikiyor. Kullanıcı 15 Ağu'da
"neden bekliyoruz" diye sordu, haklıydı — takvim notu tekrarlanmış, tetikteki SAYI kontrol
edilmemişti. **Ders: tetik bir tarihse değil bir SAYIYSA, sayıya bakılır.**

**Simülasyon güncel (15 Ağu, 18 tam Altılı, 108 ayak, orta):** ikisi de tuttu 41 · yalnız-30 10 ·
yalnız-15 **15** · ikisi de kaçırdı 42 → net **+5 ayak, p=0,424** (anlamsız, yön "geç kur" lehine).
İç kontrol: bot1_900 ve bot1_1800 farkı **tam +0** — bot1 orana bakmaz, teorinin dediği bu →
simülasyonun kendisi doğrulandı.

**CANLI: `orta_15` + `acgozlu900_15` eklendi** (K105). Her biri 30 dk'lık ikiziyle kural
olarak BİREBİR aynı, tek fark kurulma anı. **İki genişlik seçildi bilerek:** dar (96 kombo) ve
geniş (900 kombo) — zamanlamanın etkisi genişliğe göre değişebilir (simülasyon işareti düz değil:
dar +0, orta +5, geniş900 +4). **bot1'e ikiz açılmadı** (orana bakmaz → fark yapısal olarak +0).
**acgozlu_v2'ye ikiz açılmadı** (en yeni deney; ikinci değişken tek-değişken ilkesini bozar,
v2'nin kontrolü 30 dk'lık acgozlu900 olarak kalır). 15 dk grubu tavanı ~1.245 TL/Altılı.
Altyapı: KONFIG'e `dk` alanı, kupon grup grup kurulur, kupon-anı kaydı `dk_grup` ile anahtarlı.

**TETİK (K106'da düzeltildi):** `orta_15` **~60 kupona** ulaşınca → eşleşmiş ayak kıyası
(aynı Altılı, iki zaman) + simülasyonla karşılaştır. **Canlı zamanlama o güne kadar 30 dk KALIR.**

> **25 EYLÜL BU KOLU KAPSAMAZ (K106).** Tetik ~60 kupon; 17 Ağu itibarıyla `orta_15` 7,
> `acgozlu900_15` 6 kupon. 25 Eyl'e ~40 yarış günü var → tetik o tarihte **dolmayacak**.
> Kural 6 gereği tarihe değil sayıya bakılır: 25 Eylül'de verilecek karar **sistem modu**
> kararıdır (K42/K48), zamanlama kolu ayrı ve kendi sayısal tetiğiyle (~Kasım) değerlendirilir.
> İki tarih birbirine BAĞLANMAZ.

**10 dk hâlâ YOK:** takip 15 dk'da bir çalışıyor, o pencereye sistematik geçiş düşmüyor →
örneklem yanlı kesilir. Çözümü görev sıklığını artırmak; sistemin çalışma düzenine dokunduğu
için AYRI karar konusu, yapılmadı.

<sub>--- özgün madde (arşiv) ---</sub>
### 4-eski. Kupon zamanı analizi — 30 vs 15 dk (ARAÇ KURULDU, VERİ BEKLENİYOR)
**Eklendi:** 2026-07-24 · **Güncellendi:** 2026-07-31 (K76) · **İlgili:** K59, K76
**DURUM:** Test aracı kuruldu ve koştu → `kod/altili_zaman_test.py`. Ama **oran_log'da yapısal bir
eksik bulundu:** her ayak KENDİ postasına 45 dk kala loglanıyordu; oysa kupon tek anda, 1. ayağa
30 dk kala kuruluyor — o anda 2-6. ayaklar kendi postalarına 1-3 saat uzak olduğu için **hiç kayda
girmiyordu**. 17 Altılıdan yalnızca 3'ü iki zaman diliminde de tam çıktı.
**K76'da düzeltildi (ileri-yönlü):** artık pencerenin herhangi bir ayağı 45 dk içindeyse, o an
başlamamış TÜM ayaklar loglanıyor → kupon-kurma anının tam fotoğrafı.
**YENİ TETİK: ~40-50 tam Altılı birikince (≈2-3 ay, yani Ekim 2026 civarı)** → aracı tekrar koştur.
İlerlemeyi görmek için: aracın başındaki "iki zaman diliminde de TAM olan Altılı" sayısına bak.
**Şimdilik ne diyor (KARAR DEĞİL):** 3 Altılı/18 ayakta yalnız-30 tuttu 2, yalnız-15 tuttu 4;
net +2 ayak, işaret testi **p=0,688** → anlamsız. Yön hafifçe "geç kur" lehine.
**10 dk bandı düştü:** takip 15 dk'da bir çalışıyor, o pencereye geçiş düşmüyor — test edilemez.
**Kullanıcı kararı (2026-07-25, geçerli): canlı zamanlama 30 dk KALSIN.**
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

### 5. ✅ ÖLÇÜLDÜ ve KAPANDI (2026-08-27, K135) — etkisi SIFIR, canlı koda dokunulmadı

> 🔒 **KAPANIŞ (K135):** kural 4.090 kâğıt ayağında **6 ayağı** kurtarırdı (%0,147).
> Ama **altısında da diğer ayaklar tutmamıştı** → en iyi ihtimalle 5/6, Altılı'da 5/6
> ödemez → **para sonucuna etkisi TAM OLARAK SIFIR.**
> **Canlı puanlayıcı (`sonucla_altili`) DEĞİŞTİRİLMEDİ** — sıfır faydası ölçülmüş bir
> değişiklik için çalışan sisteme dokunmak kötü takas. Kuralın yokluğu zaten
> **muhafazakâr**: sicili olduğundan kötü gösterir, asla yanlış-pozitif üretmez.
> **Yerine ARAÇ yazıldı:** `kod/devir_kurali.py` (salt-okunur, istendiğinde koşulur).
> **YENİDEN AÇMA TETİĞİ:** araç "*** 6/6 OLURDU ***" satırı üretirse #5 yeniden açılır.
> **Etkisi büyüklüğü:** kupon başına 0,009 ayak — K122/K131/K132'nin ayak isabeti
> kıyasları bu kusurdan etkilenmiyor.

### 5-özgün. Altılı sonuçlamada favori-devri kuralı — BİLİNEN MODELLEME BOŞLUĞU
**Eklendi:** 2026-07-24 · **İlgili:** K59 · **TETİK:** doğruluk kritikleşirse / kullanıcı isterse
Kupona yazdığımız bir at kupon kurulduktan (30 dk) SONRA çıkarsa (KOSMAZ), TJK'da o ayaktaki pay
**posta-favorisine devreder**. Kâğıt sistemimiz bunu uygulamıyor — çıkan seçim ölü seçim sayılıyor
(`sonucla_altili` sadece kazananı okuyup "bizim seçimimizde mi" diye bakar). **Etkisi nadir ve
muhafazakâr:** ancak (seçtiğimiz at çıkar) VE (o ayağı posta-favorisi kazanır) VE (favoriyi zaten
yazmadıysak) devreye girer; yönü sonucu **daha kötü** gösterir, asla yanlış-pozitif üretmez → "Altılı
−EV" bulgusunu bozmaz. Bu yüzden ertelendi. **Not:** kâğıt sonucu birebir TJK muhasebesi sanılmamalı.
Yapılırsa: `sonucla_altili`'de çıkan-seçim tespiti + o ayağın posta-favorisini kazanan yerine koyma.

### 6. Model AĞIRLIKLARINI genişletilmiş pencereyle yeniden fit etme (walk-forward'ı ileri kaydır)

**ERKEN CEVAP (K96, 7 Ağu 2026): yeniden fit GEREKSİZ görünüyor.** Yürüyen-ileri test — ağırlıklar 2025'te yeniden fit edilip 2026'da (2.513 koşu) mevcutlarla kıyaslandı: yeni α=0,200 γ=0,960 (bot1 payı %17) vs mevcut 0,208/0,950 (%18); 2026 log-olabilirlik farkı +0,00014, **%95 GA sıfırı içeriyor**. Ağırlıklar yıllar arası kararlı. Madde KAPATILMADI (tetik tarih bazlı, 25 Eyl) ama sürpriz beklenmiyor; o gün aynı ölçüm tekrarlanıp K96'daki sayılarla kıyaslanmalı, sıfırdan hesaplanmamalı.
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

### 7. ✅ ÖLÇÜLDÜ (2026-07-31, K68) — ayrışma dağıtımı BULGU VERMEDİ, canlıya alınmadı
**Sonuç:** `kod/altili_ayrisma_test.py` (1455 OOS, w=0/0,5/1/2/4, bütçe 96/288/900). Önceden
yazılan üç ölçütün üçü de düştü: (a) monotonluk 900'de yok, (b) 12 eşli farkın 12'sinde GA sıfırı
içeriyor, (c) en iyi w bütçeler arası tutarsız. Üstelik mevcut canlı kapsam mantığı hepsini yeniyor
(−%19,4/−%31,7/−%41,2 vs en iyi ayrışma −%48,2/−%40,2/−%54,9). Tek olumlu iz: w büyüdükçe ort.
temettü artıyor (798→1.078 @96) — K67'nin mekanizması görünüyor ama kârlılığa yetmiyor.
Özgün madde aşağıda arşiv olarak duruyor.

<sub>--- özgün madde (arşiv) ---</sub>
**Eklendi:** 2026-07-26 · **İlgili:** K65, K1 · **TETİK:** kullanıcı isterse (beklenti DÜŞÜK)
K65 "isabet-maksimize" (açgözlü) dağıtımı çürüttü: şekil istenen hale geldi (tek atlı ayak %5,9→%98,7)
ve 6/6 sayısı arttı (185→225), **ama para kötüleşti** (ROI(6) −41,2→−55,0) çünkü açgözlü güvendiği
ayağa tek at = kamu favorisi = kalabalık havuz → ort. temettü yarıya düşüyor (1.656→798 TL), büyük
ödemeler (47.383→22.374) sistematik kaçıyor. **Test EDİLMEYEN üçüncü aile:** bütçeyi *bot2 ile kamu
AGF'sinin en çok ayrıştığı* ayağa ver (kenar kalabalıkla anlaşmaktan değil, ondan ayrılmaktan gelir).
Aynı koşum (`kod/altili_dagitim_test.py`) üstünde yeni bir dağıtıcı olarak eklenebilir; ölçüt yine
ROI(6) + eşli bootstrap GA. **Uyarı:** K1 etkin-pazar duvarı + K19-K33/K44/K46/K52'de 9 kenar testi
zaten negatif çıktı; bu da büyük ihtimalle negatif çıkar. Ucuz olduğu için açık bırakıldı, umut değil.

### 8. Kesinti oranları — ÖLÇÜLDÜ (K94). KAPANDI.
**Eklendi:** 2026-07-31 · **İlgili:** K72, K73 · **TETİK:** resmî kaynağa erişilince
K72'de saf favori oynamak −%17,4 getirdi; "bu kesintiden iyi mi?" sorusu için Altılı havuzunun
kesinti oranı lazımdı ve hiç kaynaklanmamıştı. **K73'te AGF verisinden tahmin edildi: ~%45-50**
(1283 olay, medyan %48,6). Ama bu bir TAHMİN — bağımsızlık varsayımına dayanıyor ve çeyrekler
%26-%74 arasında geniş. **Yapılacak:** TJK'nın yayımladığı resmî 6'lı Ganyan yasal kesinti oranını
kaynakla (mevzuat/TJK sitesi) ve K73 tahminiyle karşılaştır. Doğrulanırsa K73'ün sonucu
("favori oynamak havuz ortalamasını ~30 puan yeniyor") sağlamlaşır. Ganyan tarafı zaten
kaynaklıydı (%25,5 İngiliz / %30,6 Arap, K46).

**>>> KAPANDI — 7 Ağu 2026 (K94): ölçümle çıkarıldı. <<<**
2026, standart pistler, 2.526 olay, üstel kalibrasyon (k=0,978, 6'lı çapası):
**3'lü %45,4 · 4'lü %45,6 · 5'li %46,8 · 6'lı %48,6 · 7'li %57,6.**
Altyapı: `veri/nli_ganyan.csv` (27.442 olay, %99+ doğrulanmış). Ayrıntı K94'te.
**Sonuç: hiçbir üründe yapısal açıklık yok; ürün kolu kapandı.**

**GÜNCELLEME 2026-08-02 (K86) — ARANDI, RESMÎ ORAN YAYIMLANMIYOR.**
- `At Yarışları Müşterek Bahisler Yönetmeliği` oran vermiyor, **5602 sayılı Kanun**'a atıf yapıyor.
- **5602 sayılı Kanun** ürün bazında oran koymuyor; yalnızca yıllık ikramiye toplamının hasılatın
  **%40'ından az %93'ünden fazla olamayacağını** şart koşuyor (md. 4/2). Ürün bazında oranı
  **TJK kendi belirliyor ve yayımlamıyor.** At yarışlarında şans oyunları vergisi **%7** (md. 6/4).
- TJK'nın "Bahisler" sayfası yalnızca **birim fiyatları** veriyor: 3'lü 2,00 · **4'lü 1,75** ·
  **5'li 1,50** · **6'lı 1,25** · **7'li 2,00** · Sıralı 5'li 1,25 TL. (Asgari iştirak 20 TL,
  azami 12.000 TL.)
- **Devir kuralı resmen doğrulandı:** devreden tutar **aynı oyunun bir sonraki yerli yarış
  gününe** aktarılır — [[K84]]/[[K85]]'teki devir mantığı geçerli.
- **SONUÇ: bu madde web aramasıyla KAPANMAZ.** Kalan tek yol ölçüm.

**ÖNERİLEN YÖNTEM (yapılmadı, onay bekliyor):** K73'ün kimliği genelleştirilir —
`1 − kesinti = temettü × P(kazanan kombinasyon) / birim`. Altılı'da `P` AGF'den geliyordu;
diğer ürünlerde AGF **yok** (feed'de yalnız `AGF1` var, Altılı'ya özel). Yerine ganyan
oranlarından de-vig edilmiş kazanma olasılıklarının çarpımı kullanılır.
**Yanlılık ve düzeltmesi:** ganyan havuzunun favori-sürpriz eğilimi egzotik havuzunkinden
farklıdır. Aynı hesap ÖNCE Altılı için ganyan-türevli `P` ile yapılıp K73'ün AGF-türevli
%48,6'sıyla karşılaştırılır → çıkan fark **düzeltme katsayısı** olur, 4'lü/5'li/7'li'ye o
katsayıyla uygulanır. Mutlak kesinti tahmini kaba kalır ama **ürünler arası SIRALAMA** —
asıl soru budur — güvenilir olur.
**Ön koşul:** ham arşivden (4.219 kart, `BAHISLER_TR`) her ürünün temettüsü + kazanan
kombinasyonu çıkarılıp koşulara eşlenmeli. **Önce fizibilite denemesi yapılmalı.**

### 10. ✅ ÖLÇÜLDÜ ve KAPANDI (2026-08-09, K98) — tamamlayıcı kupon DEĞER KATMIYOR

**Sonuç:** Aynı gün içinde ölçüldü (kullanıcı "orta'yı çoğaltmak mantıklı mı?" diye sorunca).
Önceden bağlanan ölçüt **GEÇİLEMEDİ** — üç ayrı bölme kuralının üçü de parayı bozdu:
- 1→2→3→4 × orta@96: isabet %4,6→6,7→8,4→9,6 ama ROI −35,5→−51,6→−58,3→−59,8.
  Aynı parayı **tek kupona genişleterek** vermek her seviyede daha iyi (@192: 90 isabet, −34,0%).
- **"Tek ayakta bölmek = o ayağı genişletmek."** İki farklı bölme kuralı ("A ilk atlar/B sonraki"
  ve "A tek sıralı/B çift sıralı") **birebir aynı** sonucu verdi (96 isabet, −51,6%), çünkü diğer
  beş ayak ortakken iki kuponun BİRLEŞİMİ aynı kombinasyon kümesidir. Yeni bir şey değil.
- **Banker rotasyonu** (maddenin asıl fikri; A: 1-3 dar/4-6 geniş, B: tersi): temettüyü **ikiye
  katlıyor** (1.656→3.222 — de-chalking gerçekten çalışıyor) ama isabet 66→52 düşüyor.
  Net −41,5%, şans arındırılınca −59,7%.
- **YAPISAL SEBEP (K98-h, "tavan"):** kupon zorunlu olarak bir DİKDÖRTGENDİR. Kısıt olmadan
  "en olası N kombinasyon" seçilebilseydi %32-64 daha çok tutturur ama **temettü yarıya iner**
  ve ROI ~21 puan kötüleşir. En olası kombinasyonlar herkesin oynadığıdır → kapsamı büyütmek
  kalabalığa katılmaktır. **Dikdörtgen kısıtı handikap değil, kazara işleyen bir
  kalabalıktan-kaçınma mekanizmasıdır.** Bu, [[K65]]'i de yeni bir açıdan açıklar.
**Bu kol kapandı; yeniden açmak için yeni bir MEKANİZMA gerekir, yeni bir bölme kuralı değil.**

<sub>--- özgün madde (arşiv) ---</sub>
### 10-B. ✅ ÖLÇÜLDÜ ve KAPANDI (2026-08-10, K101) — banker takası ÇARE DEĞİL

Kullanıcının 10 Ağu'daki tarifi ölçüldü (güven 1. ayak tek / 2. ayak geniş ↔ tersi; artı şekli).
Önceden bağlanan ölçüt **dört hücrenin dördünde de düştü**: çift, aynı paradaki tek dikdörtgeni
ne ROI(−1)'de ne temettüde geçebildi.
**Teşhis DOĞRUYDU, çare işe yaramadı:** A banker ayağını olayların %50-61'inde kaçırıyor (kuponun
gerçek katili orası) ama B o ölümlerin ancak **%2-4'ünü** kurtarıyor — kurtarabilmesi için A'nın
diğer beş ayağı tutturmuş olması gerekiyor, üstelik B 2. ayağı tek ata indirerek yeni bir kırılma
noktası yaratıyor ve ortak dört ayak iki kez satın alınıyor.
Araç: `kod/altili_banker_takasi_test.py`. **Kupon şekli kolundaki 5. ret** (K68/K90/K98-f/K98-g/K101)
→ bu kol kapandı; yeniden açmak için yeni MEKANİZMA gerekir, yeni şekil varyantı değil.

<sub>--- özgün madde (arşiv) ---</sub>
### 10. TAMAMLAYICI KUPON (banker rotasyonu) — ölçülmedi, ölçüt önceden bağlandı
**Eklendi:** 2026-08-09 · **İlgili:** K89, K90, K96, K97
**TETİK: KULLANICI söyleyince** — kendiliğinden başlama.

**Soru (kullanıcının):** "Deneyimli oyuncular birbirine alternatif kupon kurar — farklı
ayaklarda banker yaparak, at sayılarını artırıp eksilterek. Bizde buna yönelik ne var?"

**BUGÜNKÜ DURUM ÖLÇÜLDÜ (2026-08-09, 64 Altılı / 194 sonuçlanmış ayak) — hiçbir şey yok:**
- 8 kuponun farkı yalnız **bütçe** ve **dağıtım kuralı**; hiçbiri "diğerinin kaçırdığını
  yakalayayım" diye kurulmuyor. Çeşitlilik tasarlanmadı, **artakaldı**.
- Örtüşme (Jaccard): açgözlü900 ↔ ayrışma900 **%92** (ayakların **%77'sinde birebir aynı**),
  orta ↔ geniş %88 (%64 birebir). bot2 ailesi pratikte tek kuponun yedi kostümü.
- **Banker'lar dağılmıyor, yığılıyor:** ≥2 kuponun banker yaptığı 47 Altılıda, banker yapan
  kuponların ortalama **%70'i AYNI ayağı** bankerliyor. Deneyimli oyuncunun yaptığının tersi.
- Gerçekten alternatif olan **tek kupon bot1_900**: 194 ayağın **30'unu tek başına** tutturdu
  (genis900 2, ayrışma 2, açgözlü 1, dar/orta/geniş **0**); örtüşmesi de en düşük (%37–46).
  [[K89]]'u daha büyük örneklemde doğrular.
- Portföyün faturası: 62 Altılıda 8 kupon birlikte 5 kez 6/6; Altılı başına **2.453
  kombinasyon** (≈3.066 TL). Tek açgözlü900: 866 kombinasyon, 44 Altılıda 2 kez.

**DÜRÜST ÇERÇEVE (önden yazılıyor ki sonuç görülünce esnetilmesin):** tamamlayıcı kupon
beklenen değeri **değiştirmez**, varyansı değiştirir. "En az biri tutar" olasılığı yükselir,
tutan kuponun getirisinden kaybeden kuponların bedeli düşülür. %48,6 kesinti duvarı
([[K94]]) yerinde kalır. Bu bir kenar arayışı değil, **sürdürülebilirlik = varyans** sorusudur.

**TASARIM (önceden sabit):** sabit toplam bütçe — tek 900 kombinasyonluk açgözlü **vs**
tamamlayıcı iki 450'lik kupon (A: tek sayılı ayaklarda dar/çift sayılı ayaklarda geniş,
B: tersi). Ayak rotasyonu **sonuca bakılmadan** belirlenir, taranmaz ([[K33]]/[[K52]]
hindsight yasağı). Backtest EDİLEBİLİR: gün-içi oran gerekmez, yalnız dağıtım kuralıdır.
K90'ın reddedilen "birleşim" fikrinden farkı: orada iki **model** birleştirildi, burada
aynı modelden **ayrışan** kuponlar kurulur.

**KARAR ÖLÇÜTÜ (önceden bağlanır, sonra değiştirilmez):** tamamlayıcı çift canlıya alınır
⟺ OOS'ta **hem 6/6 sayısı hem ayak isabeti**, aynı parayı tek kupona veren kontrolden
düşük DEĞİLSE. Düşükse "ayrıştırma değer katmıyor" yazılır ve kapanır.

---

## ZAMANLI — takvime bağlı

### 4. Paper test karar noktası — 25 Eylül 2026
**İlgili:** K42, K48
K42 kâğıt testi 25 Eylül 2026'ya kadar koşuyor. O tarihte sistem modu kararı: günlük devam /
talep-üzerine / arşivle. Karar için sicil o güne kadar birikecek.

**CANLI OYNAMA PLANI — 2026-08-09'da konuşuldu, ölçüldü, ERTELENDİ (K98).**
Kullanıcının önerisi "bot1 + ona alternatif bir kupon" idi. Ölçüm sonucu:
- **bot1 canlı portföye KONMAMALI.** ROI'si −18,3% görünüyor ama **getirisinin %43'ü tek bir
  kupondan** (539.029 TL). O olay çıkınca −53,2%. Kenar değil, piyango biçimi.
- **Birleştirme (f) ve çoğaltma (g) elendi** — bkz. #10.
- **Canlıya çıkılacaksa tek savunulabilir kupon: `orta`** (kapsam 0,75 / 96 kombinasyon),
  Altılı başına **118 TL**, ortalama **−42 TL/Altılı**. Şansa en az bağımlı olan o
  (ROI(−1) −44,4%, getirisinin yalnız %5'i en büyük kupondan). Zaten canlıda var olan config;
  **yeni config gerekmez.**
- **AMA "canlı, kâğıt gibi mi davranıyor?" sorusunun cevabı ZATEN VAR** (K93): ganyanda kâğıt
  −%25,4 / teorik kesinti %25,5; Altılı'da −%33,3 / backtest −%32. İki bağımsız üründe kâğıt
  gerçeği birebir tutturdu. **Canlı para koymanın ölçüme ekleyeceği bilgi yok.**
- **Karar 25 Eylül'e bağlandı.** O tarihe kadar `acgozlu_v2`'nin ileri ölçümü birikiyor (#9).
  Kod/config DEĞİŞMEDİ.

### 5. ✅ YAPILDI (kullanıcı beyanı 2026-07-27: "attım birkaç gün önce") — dış yedek yüklendi
**İlgili:** yedekleme
Yedek zip buluta/USB'ye yüklendi. **Bu iş artık TEKRARLANAN bir görev** — aşağıdaki #6'ya bak.

### 6. ✅ ÇÖZÜLDÜ (2026-08-10) — git artık PRIVATE uzak depoya bağlı

`umut19171917/at-tjk-sistem` (**private**) oluşturuldu, 80 commit'in tamamı itildi, `origin/main`
ile yerel HEAD aynı hash'te. Tek-disk riski bitti: bundan sonra her commit makine dışına gider.
Takip edilen içerik 52 MB (`.git` 17,6 MB) — ağır ve yeniden üretilebilir kısım (`veri/ham` 1,1 GB,
`katilim.csv`, `ozellikli.csv`) zaten .gitignore'da, yedeğe girmiyor.
**Kalan tek iş:** `veri/ham` arşivi hâlâ yalnız bu diskte. TJK arşivi kapanırsa `kazi.py` ile
yeniden inemez → ara sıra harici disk/bulut kopyası almak yine de mantıklı (TETİK: 3 ayda bir).

<sub>--- özgün madde (arşiv) ---</sub>
### 6-eski. Dış yedek TAZELEME — çünkü git UZAK DEPOYA bağlı DEĞİL (2026-07-27 bulgusu)
**Eklendi:** 2026-07-27 · **İlgili:** K50, #5 · **TETİK:** ayda bir (veya sistem modu değişince)
**DÜZELTME — eski notta yanlış varsayım vardı:** "haftalık git commit (K50) kod+veriyi korur"
deniyordu. `git remote -v` **BOŞ** → depo yalnızca yerel. Git yanlış silme/bozma'ya karşı korur ama
**disk arızasına karşı KORUMAZ** (geçmiş de aynı diskte). Yani **buluttaki zip TEK makine-dışı kopya.**
**Sonuç:** son yüklemeden bu yana biriken her şey (defter, altili_kupon, oran_log, temettü) yalnızca
bu diskte duruyor. Zip'i periyodik tazelemek gerçekten gerekli.
**İki seçenek (kullanıcı kararı bekliyor):**
(a) Periyodik zip yükle — basit, ama elle ve her seferinde ~150 MB.
(b) **Önerilen:** git'i bir ÖZEL (private) uzak depoya bağla → haftalık commit otomatik makine-dışına
gider; zip yalnızca ara sıra gerekir (ham JSON önbelleği zaten yeniden üretilebilir, yedeğe girmiyor).
Not: depo kişisel bahis defteri içerir → **mutlaka private**. `kod/telegram_config.json` zaten gitignore'da.

---

### 9 — ✅ KAPANDI (2026-08-24, K116) — dört adayın dördü de sonuçlandı

**>>> BU MADDE KAPALI. Dört aday da ölçüldü; yalnız biri canlıya girdi. <<<**

| aday | sonuç |
|---|---|
| 1. "en az 2 at" kaba kuralı | kullanıcı REDDETTİ (31 Tem) — semptomu bastırır, marifeti öldürür |
| 2. λ kalibrasyonu (uzak ayak) | ÖLÇÜLDÜ, GEÇTİ → **`acgozlu_v2` canlıda** (K92) |
| 3. `acgozlu_v3` "banker hak edilsin" | ÖLÇÜLDÜ, KRİTER KALDI (K115) — @900 anlamlı kötü |
| 4. `saha900` saha-orantılı genişlik | ÖLÇÜLDÜ, ANLAMLI KÖTÜ (K116) — kapsamdan −11,8 puan |

**ÜST DÜZEY DERS (K90 birleşim · K115 v3 · K116 saha — üç ardışık ret):** aynı bütçeyi yeniden
dağıtmak kazandırmıyor. Üçünde de mekanizma amaçladığını yaptı, üçünde de sonuç nötr ya da kötü.
Olasılık modeli elindeki bilgiyi zaten çıkarıyor; onu **yeniden düzenlemek** yeni bilgi üretmiyor.
**Dağıtıcı kolu tükendi.** Kalan adresler dağıtımda değil BİLGİDE/ÜRÜNDE: 7'li ganyan (K85, yeni
ürün) ve devir anları (K84/K85). İkisi de henüz ölçülmedi.

**AÇIK KALAN TEK İŞ:** `acgozlu_v2`'nin İLERİ-YÖNLÜ ölçümü (canlıda birikiyor, 25 Eyl'e bağlı).

<details><summary>Maddenin özgün metni (arşiv — tetikler artık geçersiz)</summary>

### 9-eski — Açgözlü uzak ayakta bankeri hak ediyor mu? (K79/K80)

**Sorun:** ACGOZLU900 olasılık vektörünün *sivriliğine* göre genişlik dağıtıyor. 6. ayak kupon
anında ~180 dk uzakta; o yarışın havuzu neredeyse boş → çarpık oran → sahte favori. Açgözlü
bunu "eminim" diye okuyup en az atı oraya yazıyor. 12 bankerinin 6'sı 6. ayakta, 6. ayak
isabeti %33 (1-5. ayak %75, p=0,014). Kapsam dağıtıcısı sahaya göre ölçtüğü için etkilenmiyor
(kontrol: p=0,84) → sorun ayağın zorluğu değil, açgözlünün genişlik kararı.

**"En az 2 at" kuralı REDDEDİLDİ** (kullanıcı, 31 Tem): semptomu bastırır ve açgözlünün asıl
marifetini — gerçekten güvendiği ayakta daralabilmesini — öldürür. Banker yasaklanmayacak,
**hak edilmesi** sağlanacak.

**Denenip ELENEN fikir:** "bot1 de o atı ilk-2'de görüyorsa bankere izin ver". Test edildi:
bot1 ilk-2'de görüyorsa 2/5, görmüyorsa 3/7 tuttu — **p=1,00, sinyal yok** (n=12, gücü de yok).
Kanıt diye sunulamaz, bırakıldı.

**ARAÇ HAZIR:** `kod/altili_suruklenme.py` (offline, salt-okunur). Her mesafe kovası için
sıcaklık katsayısı lambda'yı ölçer: `p_kalibre = normalize(p^lambda)`, lambda<1 = vektör fazla
sivri. Kazananın log-olabilirliğini enbüyüterek kestirir, koşu-bazlı bootstrap ile %90 GA verir.
Katsayı **tahmin edilmez, ölçülür**.

**Baz çizgisi ölçüldü (31 Tem):** 1. ayak (~30 dk) bot2 lambda = **0,944, GA [0,79 – 1,10]**
→ 1'i içeriyor, yani yakın ayakta olasılık **iyi kalibre**, sorun yok. bot1 lambda = 1,020.
Karşılaştırma noktası hazır; geriye 2-6. ayakları doldurmak kaldı.

**TETİK — iki koşul birden:**
1. `python kod/altili_suruklenme.py` çalıştır; B tablosunda **6. ayak satırının n'i ≥ 15**
   olmalı (araç "yetersiz" yazmayı bıraktığında hazırdır).
2. Aynı anda `acgozlu900` ile `bot1_900` ayak-sırasına göre kıyaslanabilir olmalı
   **İLK OKUMA YAPILDI (K87, 2 Ağu 2026): 66 eşleşmiş ayakta üçlü AYIRT EDİLEMİYOR**
   (acgozlu 37 / ayrisma 39 / bot1 35; tüm p≥0,50). Taban çizgisi K87'de; tekrar bakıldığında
   oradaki sayılarla kıyasla, sıfırdan hesaplama.
   (bot1_900 30 Tem'de canlıya girdi; ~25+ kupon gerekir).
Günde ~3 Altılı geliyor → tahmini **~2-3 hafta (Ağustos ortası 2026)**.
**Haftada bir çalıştır** — `n` sütunu ilerleme çubuğudur.

**İLK ÇALIŞTIRMANIN ASIL AMACI (yarın):** K76 düzeltmesi 31 Tem'de girdi ve o ana kadar
**tek satır uzak-ayak verisi üretmemişti**. Araç her açılışta "uzak ayak kaydı geliyor mu"
diye bakıp açıkça söylüyor. Yarın çalıştır: 60/90/120/150/180 dk satırları görünmüyorsa
düzeltme işlememiş demektir → 3 hafta değil 1 gün kaybederiz. (BEKLEYENLER #4 tam bu yüzden
haftalarca cevapsız kalmıştı.)

**K98 NOTU (2026-08-09) — v2 backtest'te BAĞIMSIZ DESTEK aldı, ama bütçeye özgü:**
Arşivde (OOS 2025-26, 1.433 olay) λ=0,65'i geç ayaklara uygulamak açgözlüyü **−64,0% → −47,2%**
iyileştirdi, temettüyü %41 artırdı. Kontrol: λ'yı **tüm** ayaklara uygulamak hiçbir şey yapmıyor
(−65,2%), **erken** ayaklara uygulamak da (−64,5%) → etki "düzleştirme" değil, **geç ayaklara
genişlik**. Yani açgözlünün kusuru sürüklenmeden bağımsız olarak arşivde de var.
**AMA:** üstünlük yalnız @900'de. @288 ve @96'da genis (kapsam) v2'yi açık ara geçiyor
(@96: −37,1% vs −64,4%). v2 "daha iyi mekanizma" değil, **900'e özgü düzeltme**.
λ DEĞİŞTİRİLMEDİ (tarama 0,50'yi iyi gösteriyor ama backtest'ten λ seçmek overfit — K33/K52).
Bu, ileri-yönlü ölçümün yerine GEÇMEZ; aşağıdaki tetik aynen geçerli.

**ÜÇÜNCÜ ADAY — "banker hak edilsin" (yeni parametre GEREKTİRMEZ).**
Sistemde bu test **zaten var**, sadece açgözlü ondan muaf. `kupon_kur` (kapsam ailesi,
altili_backtest.py:39): bir ayak ancak tepedeki atın bot2 olasılığı `BANKER_ESIK = 0.70`'i
**tek başına** geçerse tek ata iner. Açgözlü/ayrışmada böyle bir sınav yok — orada tek at
bütçe aritmetiğinin artığıdır ("emindim" değil, "başka yere harcamak daha kârlıydı").

Fiili durum (31 Tem, kurulmuş tüm kuponlar):
| config | kupon | tek-at ayak | oranı | kaçı GERÇEK banker |
|---|---|---|---|---|
| dar | 30 | 60 | %33 | **6** |
| orta | 30 | 6 | %3 | **6** |
| geniş | 17 | 3 | %3 | **3** |
| geniş900 | 17 | 3 | %3 | **3** |
| açgözlü900 | 12 | 12 | %17 | **1** |

orta/geniş/geniş900'de tek-at ayaklarının **tamamı** %70 sınavını geçmiş. Açgözlünün 12
tek-at ayağından **yalnızca 1'i** geçiyor. — Ayrı bulgu: dar'ın 60 tek-at ayağının **54'ü
banker değil, bütçe kıtlığı**; 24 kombo altı ayağa bölününce budayıcı zorla daraltıyor
(ayak başına ort. 1,7 at). Dar'ın "bankerleri" büyük ölçüde açlık.

**>>> ÜÇÜNCÜ ADAY KAPANDI — 24 Ağu 2026 (K115): ÖLÇÜLDÜ, KRİTER GEÇİLEMEDİ. <<<**
Önceden bağlanan kriter (@900'de hem ayak isabeti hem 6/6 açgözlüden düşük olmayacak) **KALDI**:
ayak %73,1 vs %74,2 · 6/6 227 vs 235 · eşli p=0,0000 (v3 anlamlı KÖTÜ). Canlıya ALINMADI.
Mekanizma çalıştı (hak edilmemiş tek-at 1254→0, gerçek banker 87→88 dokunulmadı) — sorun
uygulama değil, fikrin kendisi @900'de değer katmıyor.
**Post-hoc bulgu (hipotez, kriter değil):** @96'da ROI farkı +26,4 puan [+9,8 , +45,2] ANLAMLI;
kazanç isabetten değil temettüden (831→1.373, +%65) — açgözlünün tek attığı ayak kamu favorisi
olduğu için havuz kalabalık (K65). AMA @96'da doğru kıyas kapsam'dır (canlıda `orta` orada
koşuyor): kapsam −39,4% vs v3 −41,5% → **v3 kapsamı geçmiyor.** Yeni zemin yok.
Araç: `kod/altili_v3_test.py` (offline). `kupon_kur_acgozlu_v3` kodda, canlıda ÇAĞRILMIYOR.

**Aday `acgozlu_v3`:** aynı açgözlü dağıtım, tek fark — bir ayak ancak `p_tepe >= BANKER_ESIK`
ise 1 atta bitebilir; geçemezse taban 2. Banker yasak değil, **hak edilmesi** gerekiyor
(kullanıcının 31 Tem'deki şartı). Yeni sabit yok, sistemin kendi eşiği kullanılıyor.

**Dürüst uyarı:** bu kural mevcut 12 tek-attan 11'ini iptal ederdi → açgözlüyü epeyce
değiştirir ve **işe yarayacağı ÖLÇÜLMÜŞ DEĞİL**. Aynı oturumda "bot1 de ilk-2'de görüyorsa
bankere izin ver" fikri de kulağa böyle mantıklı geliyordu, test edilince p=1,00 çıktı.
v3 uydurma değil ama kanıtlı da değil; λ ölçümünün yerini TUTMAZ.

**v2 ile v3 ARASINDA SEÇİM KURALI (şimdiden bağlanıyor):** λ bulgusu düzeltmeyi haklı
çıkarırsa ikisi de AYRI config olarak canlıya alınır ve **ileri veriyle** yargılanır.
Geçmiş kuponlar üzerinde ikisini deneyip "daha iyi sonuç vereni" seçmek YASAK — 12 kuponluk
geçmişte kazanan seçmek, ölçüm değil kendini kandırmadır.

**YAPISAL TESPİT — açgözlünün tek-atı bir GÜVEN BEYANI DEĞİL, bütçe artığıdır.**
(Kod önerisi değil; λ geldiğinde yanlış yorumlamamak için not.) Sentetik sınama, 31 Tem:
3 ayağa tepesi 0,80 olan girdi, 3 ayağa dağınık girdi verilip iki dağıtıcı koşuldu.

| kaç ayakta 0,80'lik at var | KAPSAM (0.75/96) | tek-at | AÇGÖZLÜ (900) | tek-at |
|---|---|---|---|---|
| 1 | 1×2×2×2×3×3 (72) | 1 | 1×5×5×4×3×3 (900) | 1 |
| 2 | 1×1×3×3×3×3 (81) | 2 | 1×1×5×5×5×5 (625) | 2 |
| 3 | 1×1×1×4×4×4 (64) | **3** | 3×2×1×5×5×5 (750) | **1** |
| 4 | 1×1×1×1×4×4 (16) | **4** | 4×2×2×2×5×5 (800) | **0** |
| 6 | 1×1×1×1×1×1 (1) | **6** | 4×4×4×3×2×2 (768) | **0** |

- **Kapsam ailesi:** banker testi ayak ayak bağımsız; sayaç/tavan YOK. Altısında birden banker
  bulursa tek kombinasyonluk kupon yazar. Banker arttıkça kombo düşer, artan bütçe diğer
  ayakları genişletir — istenen davranış.
- **Açgözlü TERS çalışıyor:** ne kadar çok ayaktan eminse o kadar AZ tek at yazıyor. Altı ayağın
  altısı da 0,80'lik favoriliyken HİÇ banker yazmıyor. Sebep: açgözlü güven ifade etmiyor,
  **900 bütçesini harcamak zorunda**. Dağınık ayaklar doyunca artan bütçe geri dönüp güvenilen
  ayağa 2., 3., 4. atı satın alıyor.
- Ek artık: 1-2-3. ayakların girdisi **birebir aynıyken** 3/2/1 at almışlar — sıralı tarama +
  tamsayı bütçe kısıtının yan ürünü. Ayak düzeyindeki çıktı bir yargı değil, aritmetik.
- **Fiiliyat:** 106 kuponun 87'sinde 0, 19'unda 1 gerçek banker; **aynı kuponda 2 gerçek banker
  hiç olmamış** (%70 yüksek eşik). Yani çoklu-banker durumu henüz gerçekleşmedi.
- **v3 bunu ÇÖZMEZ** — v3 yalnızca hak edilmemiş tek atı engeller (taban 2). Buradaki kusur
  tersi: açgözlü gerçekten emin olduğunda bile daralamıyor.
- **Muhtemel DÖRDÜNCÜ aday (yazıldı, önerilmedi):** açgözlü bütçeyi harcamak ZORUNDA olmasın —
  marjinal kazanç/bedel oranı bir eşiğin altına düşünce dursun (kupon 900 yerine 300'de biter).
  Ama bu YENİ bir eşik = yine ölçülmesi gereken bir sayı. λ ölçümünden önce dokunulmaz.

**DÖRDÜNCÜ ADAY — saha büyüklüğüne göre genişlik dağıt (K88).**
Ölçüm: kapsam ailesinin genişliği **bütçenin 6. kökü** (`24^(1/6)=1,70` · `96^(1/6)=2,15` ·
`288^(1/6)=2,58` · `900^(1/6)=3,11`, gözlenenle birebir) — kapsam/banker eşikleri pratikte hiç
bağlamıyor. Saha 4-7'den 12+'ya çıkarken seçilen at sayısı **sabit kalıyor** (korelasyon
−0,15..+0,17). Oysa isabet %65,4 → %36,4 düşüyor.

| saha | ort.at | isabet | rastgele | kazanç |
|---|---|---|---|---|
| 4-7 | 2,2 | %65,4 | %35,1 | 1,86 |
| 8-9 | 2,1 | %51,9 | %24,0 | 2,16 |
| 10-11 | 2,1 | %43,9 | %20,5 | 2,14 |
| 12+ | 2,3 | %36,4 | %16,5 | 2,21 |

Kazanç sütunu düşmediği için sorun modelin kalabalık sahada bozulması DEĞİL; sorun aynı
bütçeyi zaten %65'te olduğumuz ayakla %36'da olduğumuz ayağa **eşit** dağıtmak. Altılı zincirin
en zayıf halkasıyla belirlendiğinden, küçük sahadaki 3. at neredeyse hiçbir şey satın almıyor.

**Aday `saha900`:** genişlik saha büyüklüğüyle ölçeklenir (küçük sahadan kıs, kalabalığa ver).
Açgözlü bunu zaten KISMEN yapıyor (küçük saha 2,5 at → büyük saha ~4,0), kapsam ailesi hiç yapmıyor.

**Neden diğer adaylardan farklı:** saha büyüklüğü **kupon kurulmadan önce kesin olarak
biliniyor** — tahmin, kalibrasyon ya da uydurma parametre gerektirmiyor. λ'yı beklemesi gerekmez.
**Ama yine de ölçülmeden canlıya alınmaz** — K79'da "bot1 teyidi" fikri de böyle mantıklı
görünüp p=1,00 çıkmıştı.

**AÇGÖZLÜ EMEKLİLİK KRİTERİ (K90, önceden bağlandı — 3 Ağu 2026):** kullanıcı açgözlüyü
iptal etmek istedi; n=13'le kazanan seçmemek ve ayrışmanın KONTROL GRUBUNU korumak için
ertelendi. Kriter: **40 eşleşmiş kupon** dolduğunda (şu an 13) açgözlünün benzersiz ayak
katkısı hâlâ **0** ise VE açgözlü-ayrışma eşli skoru hâlâ tek yönlüyse (bugün 0-3) →
acgozlu900 kapatılır, ayrışma tek başına devam eder. Sayılar K89/K90'da; karar günü gelince
aynı ölçüm tekrarlanır, kriter DEĞİŞTİRİLMEZ.

**>>> BU KRİTER ARTIK UYGULANAMAZ — 10 Ağu 2026, K100. Karşılandığı için değil, ÖNKOŞULU
ortadan kalktığı için. <<<** Kriterin "o zaman" kısmı *"ayrışma tek başına devam eder"*
diyordu; K100'de **ayrışma900 emekli edildi**, açgözlü900 kaldı. Tersi tercih edilmedi çünkü
seçim sicile değil ROLE göre yapıldı: açgözlü900, `acgozlu_v2`'nin kontrol grubudur (bu madde).
Ayrışma kaldırılsaydı v2 ölçümü ayakta kalır, açgözlü kaldırılsaydı kalmazdı.
**Kriterin altındaki soru ("açgözlü portföye bir şey katıyor mu?") zaten cevaplandı:**
benzersiz ayak katkısı canlıda 1/216, backtest'te 1/194 (K98-b, K100-b). Cevap: neredeyse hiç.
Ama açgözlü900 canlıda **ölçüm aracı** olarak duruyor, kupon değeri için değil.
**Bu satır silinmedi** — önceden bağlanmış bir kuralın ne olduğu ve neden uygulanmadığı
kayıtta kalsın diye (kriteri sessizce düşürmek, kriteri sonuca göre değiştirmekle aynı hatadır).

**BİRLEŞİM DENEMESİ SONUÇLANDI (K90): RED.** max(bot1,bot2) birleşimi 1433 OOS olayda
bot2-kontrolünden anlamlı kötü (p=0,0002) → canlıya alınmadı. Tamamlayıcılık gerçek ama
max-birleşim yanlış araç. İleride farklı birleştirme fikri gelirse `kupon_kur_birlesim`
zemini hazır; yeni deneme için önce YENİ bir önceden-bağlanmış kriter yazılır.

**K100 NOTU (10 Ağu 2026) — bu maddenin ölçüm zemini korundu ve bir tuzak eklendi.**
Kalabalık budanırken (dar/geniş/geniş900/ayrışma900 emekli) **açgözlü900 bilerek bırakıldı**:
v2'nin kontrolü odur, kaldırılsaydı bu madde ölçülemez hale gelirdi.
Ayrıca `bot1_1800` eklendi — **v2 kıyasını etkilemez** (farklı aile, farklı cetvel), ama
kıyas yapılırken şu akılda tutulacak: **bot1_1800, bot1_900'ün üst kümesi DEĞİL.** Açgözlü
dağıtıcı bütçe artınca genişliği yeniden dağıtıyor (ölçüldü: 10.08 BURSA 1. Altılı'da 900'ün
22 atının 21'i 1800'de var; 1. ayak 6→5 atarken 2. ayak 3→7 çıkıyor). Aynı şey **acgozlu900 ↔
acgozlu_v2** için de geçerlidir — v2 "açgözlü + biraz genişlik" değil, farklı bir dağıtımdır.

**>>> TETİK ATEŞLENDİ — 7 Ağu 2026 (K92). Bu maddenin λ kolu KAPANDI. <<<**
Eşleşmiş ölçüm n=87: uzak λ=0,650 [0,465..0,875] (1'i içermiyor), yakın λ=0,980 [0,765..1,220],
FARK −0,330 [−0,545..−0,135] **anlamlı**. `acgozlu_v2` canlıya alındı (8. config, λ_uzak=0,65,
eşik 75 dk). Tam λ(T) eğrisi kurulMADI (n=24, monoton değil, farklar anlamsız → overfit riski).
Ayrıntı ve iç-örneklem sağlaması K92'de.
**AÇIK KALAN:** ileri-yönlü ölçüm — acgozlu_v2 ile acgozlu900 ayak-ayak kıyaslanacak (tek fark
uzak-ayak düzeltmesi). K87 taban çizgisi ve K89 yöntemi kullanılır. **v3 (banker hak edilsin)
ve v4 (saha genişliği) BEKLETİLDİ** — tek seferde tek değişken.

**KARAR KURALI — şimdiden bağlanıyor (hindsight yasağı):**
- 6. ayak lambda'sının %90 GA'sı **1'i içeriyorsa** → eskime hikâyesi doğrulanmadı,
  **açgözlü ellenmez**, K79 "ölçüldü, çıkmadı" diye kapanır.
- GA'sı **tamamen 1'in altındaysa** → `acgozlu_v2` YENİ config olarak eklenir (K69 kalıbı;
  çalışan akış ortasında değiştirilmez). Her ayağın olasılığı kendi kovasının ölçülmüş
  lambda'sıyla düzleştirilir, sonra aynı açgözlü dağıtım koşar. Banker serbest kalır ama
  ancak gerçekten sivri bir dağılımda ortaya çıkar.
- Lambda değeri **koşturulan ölçümden** alınır; birden çok aday arasından "en iyi sonucu
  vereni" seçmek YASAK.

---

### 11. ✅ ÖLÇÜLDÜ ve KAPANDI (2026-08-24/25, K117 · K120) — 7'Lİ ve 4'LÜ/5'Lİ "EK OYUN"
**Eklendi ve kapandı:** 2026-08-24/25 · **İlgili:** K85, K86, K108, K117, K120
- **7'li ganyan (K117):** 2026'da çıkmış yeni ürün; olay tablosu ham arşivden üretildi
  (`veri/yedili_tam.csv`, 395 olay, ayak eşlemesi **%100 çapraz doğrulandı**).
  Eşit parada, aynı kartların Altılısına karşı: 32 isabet / −%24,5 vs **12 isabet / −%65,8**.
  Kriter geçilemedi. **K117 EK kesin kapattı:** tutturduklarımız tipik olayın %5'ini ödüyor
  (Altılı %7) → 7. ayak daha büyük ödüle erişim VERMİYOR, sadece daha çok olaydan ELİYOR.
- **4'lü/5'li EK oynamak (K120):** K108 ikameyi reddetmişti; bu ek oynamayı ölçtü.
  5'li −93.927 · 4'lü −366 · 3'lü −6.604 TL. Genel: Altılı tek başına −297.179 →
  üçü birlikte −391.472. **ROI 2,6 puan "iyileşiyor" ama net 94.293 TL kötüleşiyor** (seyreltme).
  4'lünün −%0,9'u tuzak: ödülün %35'i tek olaydan; o çıkınca −%36,0.
- **DEVİR (K117):** avantaj GERÇEK (devir sonrası temettü medyanı +%37) ama ulaşılamıyor —
  darboğaz ödül değil **isabet**.
- **YENİDEN AÇMA ŞARTI (önceden yazıldı):** 7'liyi tekrar açmak için **bizim tuttuğumuz
  olayların** temettüsünün Altılı'dakinden anlamlı yüksek çıkması gerekir. Bugün %5 vs %7 —
  yön 7'li aleyhine. Altyapı (`yedili_tam.csv` + iki betik) duruyor, sıfırdan başlanmaz.

### 12. ✅ KAPANDI (2026-08-24, K118) — `bot1_1800` emeklilik önerisi · K90 kriteri ÖLÜ
- **`bot1_1800`:** 44 eşleşmiş Altılı'da `bot1_900` ile **birebir aynı getiri** (33.451 TL),
  **iki katı bedel** (95.200 vs 47.591). Tutturduğu tek Altılı'yı (18.08 ANKARA-1) bot1_900 da
  **1.080 TL eksiğine** tutturmuştu. 1800'ün başladığı 11 Ağu'dan beri 900'ün yakalamadığı
  hiçbir Altılı'yı yakalamadı; 14 fazladan ayak yakaladı (p=0,0010) ama hiçbiri 6/6'ya dönüşmedi.
  **Emeklilik önerildi → KULLANICI "şimdilik devam etsin" DEDİ → EMEKLİ EDİLMEDİ.**
  Karar ileride yeniden açılabilir; ölçüm K118'de duruyor.
- **K90'ın açgözlü emeklilik kriteri ÖLÜ:** eşi olan `ayrisma900` 10 Ağu'da durdu →
  "40 eşleşmiş kupon" eşiği **hiçbir zaman dolmayacak** (36'da dondu). Kriter yine de
  çalıştırıldı, üç şartın üçü de tutmuyor → cevap zaten "açgözlü kalır".
  **Açgözlünün rolü artık ayrışmanın kontrolü DEĞİL, `acgozlu_v2`'nin kontrolüdür**
  ve o rol 25 Eylül'e kadar açıktır. Bu maddede "kriter bekliyor" sanılmasın diye yazıldı.

---

## KAPALI / KARARA BAĞLANMIŞ — tekrar açma, gerekçesi var

- **Gerçek bahis çerçevesi** — ❌ askıya alındı (K48): kullanıcı gerçek para oynamıyor.
  Sistem ölçüm/öğrenme deneyi olarak sürüyor.
- **"Tüm TJK bahis türlerine genişlet"** — ❌ veriyle reddedildi (K46): pazar etkin +
  %25-31 kesinti; Arap pazarı da negatif çıktı.
- **Plase modeli (Plackett-Luce)** — ❌ backtest'te başarısız (K44): −%12,5 OOS.
- **9 bağımsız edge testi** (ganyan/exacta/Altılı/chalk-exotic/özellik batch'leri) — ❌ hepsi
  negatif; yapısal engel etkin pazar + kesinti (K19-K33, K44, K46, K52).

</details>
