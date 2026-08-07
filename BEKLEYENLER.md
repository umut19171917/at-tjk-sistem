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

### 2. 4'lü / 5'li kupon türleri — GEREKÇE GÜÇLENDİ (K74/K75/K84)
**Eklendi:** 2026-07-24 · **Güncellendi:** 2026-07-31 · **İlgili:** K5, K46, K74, K75
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

**ÖN KOŞUL — veri yok:** `veri/altili_tam.csv` yalnızca 6'lı temettülerini (t6/t5/t4/t3) tutuyor.
4'lü ve 5'li bahislerin **kendi temettü serileri arşivde YOK**. Yapılacak sıra:
1. Ham feed'de 4'lü/5'li temettüsü var mı, hangi uçta — `kod/tani_json.py` ile tara
2. Yoksa kazı tarafına ekle (`kazi.py`), ileri-yönlü biriktir + mümkünse geriye dönük çek
3. `altili_tam.py` muadili bir olay tablosu üret (hangi koşular, hangi temettü)
4. Ancak ondan sonra backtest: aynı `bot2/AGF^λ` ailesi, 4 ve 5 ayakta

**Beklenti (önceden yazılıyor):** düşük. 12 test negatif, kesinti ~%49 ve muhtemelen bu
bahislerde de benzer. Ama ilk kez körlemesine değil, **ölçülmüş bir mekanizmayı takip ederek**
bakıyor olacağız — o yüzden yapmaya değer.

### 3. defter.html'i K55 görsel diline çevirme
**Eklendi:** 2026-07-24 (teklif edildi, istenmedi) · **İlgili:** K55
altili.html / paper.html K55 zengin formatına geçti (tahminler + sistem sırası + kazanan +
kamu sırası + oran + bedel + ödül + toplam). defter.html hâlâ eski düzende. İstenirse aynı
`rapor_ortak.py` yapıtaşlarıyla çevrilebilir; sistemin veri akışına dokunmaz.

### 4. Kupon zamanı analizi — 30 vs 15 dk (ARAÇ KURULDU, VERİ BEKLENİYOR)
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

---

## ZAMANLI — takvime bağlı

### 4. Paper test karar noktası — 25 Eylül 2026
**İlgili:** K42, K48
K42 kâğıt testi 25 Eylül 2026'ya kadar koşuyor. O tarihte sistem modu kararı: günlük devam /
talep-üzerine / arşivle. Karar için sicil o güne kadar birikecek.

### 5. ✅ YAPILDI (kullanıcı beyanı 2026-07-27: "attım birkaç gün önce") — dış yedek yüklendi
**İlgili:** yedekleme
Yedek zip buluta/USB'ye yüklendi. **Bu iş artık TEKRARLANAN bir görev** — aşağıdaki #6'ya bak.

### 6. Dış yedek TAZELEME — çünkü git UZAK DEPOYA bağlı DEĞİL (2026-07-27 bulgusu)
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

### 9 — Açgözlü uzak ayakta bankeri hak ediyor mu? (K79/K80)

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

**BİRLEŞİM DENEMESİ SONUÇLANDI (K90): RED.** max(bot1,bot2) birleşimi 1433 OOS olayda
bot2-kontrolünden anlamlı kötü (p=0,0002) → canlıya alınmadı. Tamamlayıcılık gerçek ama
max-birleşim yanlış araç. İleride farklı birleştirme fikri gelirse `kupon_kur_birlesim`
zemini hazır; yeni deneme için önce YENİ bir önceden-bağlanmış kriter yazılır.

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

## KAPALI / KARARA BAĞLANMIŞ — tekrar açma, gerekçesi var

- **Gerçek bahis çerçevesi** — ❌ askıya alındı (K48): kullanıcı gerçek para oynamıyor.
  Sistem ölçüm/öğrenme deneyi olarak sürüyor.
- **"Tüm TJK bahis türlerine genişlet"** — ❌ veriyle reddedildi (K46): pazar etkin +
  %25-31 kesinti; Arap pazarı da negatif çıktı.
- **Plase modeli (Plackett-Luce)** — ❌ backtest'te başarısız (K44): −%12,5 OOS.
- **9 bağımsız edge testi** (ganyan/exacta/Altılı/chalk-exotic/özellik batch'leri) — ❌ hepsi
  negatif; yapısal engel etkin pazar + kesinti (K19-K33, K44, K46, K52).
