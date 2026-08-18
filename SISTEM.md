# TJK AT YARIŞI ÖLÇÜM SİSTEMİ — TAM DURUM

> **Bu dosya bir devir belgesidir.** Yeni bir Claude oturumuna sistemin tamamını
> anlatmak için hazırlandı. Üretim tarihi: **16 Ağustos 2026** ·
> **güncellendi 18 Ağustos 2026 (K107 sessiz gün kaybı · K108 4'lü/5'li KAPANDI · K109 ayak sicili + ORAN SÜRÜKLENMESİ tuzağı).**
> Otorite sırası: `KARARLAR.md` (numaralı karar günlüğü, K1–K109) > `BEKLEYENLER.md`
> (ertelenmiş işler + tetikleri) > bu dosya. Çelişki olursa KARARLAR kazanır.

---

## 1. BU NEDİR, NE DEĞİLDİR

**Bir ölçüm deneyidir, para kazanma aracı değildir.** Kullanıcı bugüne kadar **tek bir
canlı bahis yatırmadı** (K48). Tüm bahisler kâğıt üzerindedir; `veri/bahis.csv` diye bir
dosya yoktur.

Kullanıcının kendi çerçevesi — yorumlarda gözetilmesi gereken cümleler:

> *"benim amacımın buradan vurgun vurmak değil sürdürülebilir bir yol bulmak olduğunu bil
> ve ona göre yorumla"*
>
> *"evet bu bir kumar ama ben bunu bir kumarbaz gibi körlemesine oynamak istemiyorum, o
> yüzden bu sistemle uğraşıyorum ve henüz hiç canlı kupon yatırmadım"*

Sistemin bulduğu ana sonuç: **kenar yoktur.** Kâğıt ROI'si teorik kesintiye yakınsamıştır.
Bu bir başarısızlık değil, ölçüm aygıtının doğrulanmasıdır.

**Konum:** `C:\Users\KURTİ\Desktop\projeler\at`
**Uzak depo:** `github.com/umut19171917/at-tjk-sistem` (**private**), 84 commit
**Dil:** kod ve belgeler Türkçe; kod içi yorumlar ASCII (Türkçe karakter yok, konsol
kodlaması yüzünden).

---

## 2. VERİ AKIŞI — UÇTAN UCA

```
ebayi.tjk.org (JSON feed)
   │  kazi.py            → veri/ham/*.json        (1,1 GB, gitignore, YENİDEN İNDİRİLEBİLİR)
   ▼
duzlestir.py             → veri/katilim.csv       (349.911 satır, 94 MB, gitignore)
   ▼
ozellik.py               → veri/ozellikli.csv     (118.800 satır, 85 MB, gitignore)
   │   17 nokta-anında özellik + yarış-içi z-skor
   ▼
model.py                 → Bot1 (koşul logit) + Bot2 (harman) + α, γ
   ▼
gunluk.py hesapla()      → canlı puanlama (her koşu için bot1/bot2/kamu)
   ▼
takip.py (15 dk'da bir)  → defter.csv · altili_kupon.csv · paper_kupon.csv · oran_log
   ▼
raporlar/*.html
```

**Kritik:** `veri/ham`, `katilim.csv`, `ozellikli.csv` git'te **değil** (gitignore). İlki
`kazi.py` ile ~2 saatte yeniden inebilir ama TJK arşivinin açık kalacağı garanti değil →
**3 ayda bir harici kopya alınmalı** (BEKLEYENLER ZAMANLI #6).

---

## 3. MODELLER

### Bot1 — orana KÖR koşul logit (conditional logit)
Piyasayı hiç görmez. 17 özellik, hepsi **nokta-anında** (look-ahead yok; `shift(1)` ile
mevcut koşu daima hariç) ve **yarış-içi z-skorlu** (saha-göreli):

```
hiz_son_ort_z  hiz_en_iyi_z  form_pos_z  form_fark_z  kilo_z  handikap_z
kariyer_galip_oran_z  zemin_galip_oran_z  jokey_isabet_z  antrenor_isabet_z
kulvar_skor_z  son_yarisdan_gun_z  yas_z  disi  ilk_kosu  jokey_degisim  taki_ilk
```

- **Hız figürü:** `par + gün_ofseti − gerçek zaman`. `par` = (şehir × zemin × mesafe)
  medyanı, **yalnız ≤2024 eğitim yıllarından** (K38: eskiden tüm yıllardan alınıyordu,
  2025-26 test dönemi sızıyordu). `gün_ofseti` = o gün o pistteki galiplerin sapma
  ortalaması → pistin o günkü hızı düzeltilir.
- **Jokey/antrenör:** son **365 gün** isabet oranı, mevcut koşu çıkarılarak.
- **Kulvar:** `kulvar_skor` = (şehir × mesafe kovası × start kovası) tarihsel galip oranı,
  ≤2024'ten, **ırk ayrı** (K46). Bu **pistin biası**, atın tercihi DEĞİL.
- **Form penceresi K=4** (son 4 koşu).
- **Kapsam:** İngiliz + izinli pist. `EXCL = {ADANA, ELAZIG, DIYARBAKIR, SANLIURFA}`.
  Arap ayrı çağrılır (K46).

### Bot2 — piyasayla harman (üretim çıktısı)
```
bot2 = softmax( α · ln(bot1) + γ · ln(p_kamu) )
p_kamu = de-vig(1/oran)
```
**Ölçülen:** α ≈ **0,21**, γ ≈ **0,95** (defter'den geri çıkarma R²=0,9996). Walk-forward:
eğit ≤2023 · harman 2024 · **TEST 2025-26** (cross-fit, sızıntı yok).

**Bunun anlamı:** Bot2'nin ağırlığının **~%82'si piyasadan** gelir. Bot2 pratikte kamunun
kendisidir (favori ortaklığı %89,9). Bot1'in kazanan atın olasılığına net katkısı
ortalama **%0,75** — gerçek ama minik (K96).

---

## 4. KUPON MANTIĞI

Kupon zorunlu olarak bir **DİKDÖRTGENDİR**: her ayakta seçilen atların kartezyen çarpımı.
Bu kısıt sistemin merkezinde durur (bkz. §8 "tavan" bulgusu).

Dört dağıtıcı (`kod/altili_backtest.py` — tek kaynak, canlı ve backtest aynı kodu kullanır):

| dağıtıcı | mantık |
|---|---|
| `kapsam` | K52. Tepe at `BANKER_ESIK=0,70`'i geçerse tek at; yoksa kümülatif kapsam eşiği (0,75 veya 0,95) dolana dek at ekle. Bütçe aşılırsa en geniş ayaktan buda. |
| `acgozlu` | K65. Log-uzayında sırt çantası: her ayakta 1 atla başla, bütçe dolana dek `kazanç/bedel` oranı en yüksek atı ekle. `kazanç = log(1+p/P_i)`, `bedel = log((k+1)/k)`. Banker kendiliğinden oluşur (güvenden değil, bütçe artığından). |
| `ayrisma` | K68. Açgözlünün ayrışma-ağırlıklı hali: `kazanç × (1 + w·D_i)`, D = bot1 ile kamunun toplam değişim uzaklığı. `AYRISMA_W = 1,0` **sabit ve taranmadı** (overfit yasağı). |
| `kalibre` | K92. Uzak ayakların olasılık vektörünü ölçülmüş λ ile düzleştirir: `p^λ` normalize, sonra açgözlü. `LAM_UZAK=0,65`, `LAM_YAKIN=1,0`, `UZAK_ESIK_DK=75`. |

### Aktif config'ler (K100 + K105)

| config | kapsam | kombo | dağıtım | puan | aile | **dk** | durum |
|---|---|---|---|---|---|---|---|
| `orta` | 0,75 | 96 | kapsam | bot2 | kamu | 30 | aktif |
| `orta_15` | 0,75 | 96 | kapsam | bot2 | zaman | **15** | aktif |
| `acgozlu900` | 0,95 | 900 | acgozlu | bot2 | kamu | 30 | aktif |
| `acgozlu900_15` | 0,95 | 900 | acgozlu | bot2 | zaman | **15** | aktif |
| `bot1_900` | 0,95 | 900 | acgozlu | **bot1** | temel | 30 | aktif |
| `bot1_1800` | 0,95 | 1800 | acgozlu | **bot1** | temel | 30 | aktif |
| `acgozlu_v2` | 0,95 | 900 | **kalibre** | bot2 | kalibre | 30 | aktif |
| `dar` | 0,75 | 24 | kapsam | bot2 | kamu | 30 | **EMEKLİ** |
| `genis` | 0,75 | 288 | kapsam | bot2 | kamu | 30 | **EMEKLİ** |
| `genis900` | 0,95 | 900 | kapsam | bot2 | kamu | 30 | **EMEKLİ** |
| `ayrisma900` | 0,95 | 900 | ayrisma | bot2 | ayrisma | 30 | **EMEKLİ** |

> **CONFIG SİLİNMEZ, `aktif: False` ile emekli edilir.** Silinirse geçmiş sicili raporun
> TOPLAM DURUM bloğundan sessizce düşer ve işleyen bakiye ile ayrışır (kümülatif blok
> CSV'den okur, toplam blok KONFIG'den gezer). Emeklilik bir bayraktır, silme değil.

> **İKİ ZAMANLI KURULUM (K105).** `dk` alanı kuponun ilk ayağa kaç dk kala kurulacağını
> söyler. `kupon_zamani_kur` her dk grubu için AYRI kontrol yapar; "kurulmuş mu" kontrolü
> **config düzeyindedir** (pencere düzeyinde olsaydı 15 dk grubu hiç kurulmazdı) ve
> `kupon_hazirla`'ya `sadece_cfg` geçilir → gruplar birbirinin satırına dokunmaz.

**Birim fiyat:** İst/Ank/İzm/Ada/Bur/Koc/Ant **1,25 TL**; Elazığ/Urfa/Diyarbakır 1,00 TL.
**Ödeme:** yalnız **6/6** öder. 5/4/3 ayak TJK'da AYRI bahistir, teselli değildir — raporda
yalnız bilgi amaçlı gösterilir.

---

## 5. OTOMASYON

**Windows Zamanlanmış Görevler** (hepsi `pythonw.exe`, pencere açmaz):

| görev | sıklık | komut |
|---|---|---|
| **TJK Takip** | **15 dk**'da bir | `kod/takip.py` |
| **TJK Bekçi** | 2 saatte bir | `kod/bekci.py` — üç denetim: **nabız** (K49) + **config kapsaması** (K106) + **defter kapsaması** (K107). Hepsi salt-okunur. |
| **TJK Veri Commit** | haftalık (Pzt 22:45) | `kod/veri_commit.py` |

`takip.py` her geçişte: günün ilk geçişinde arşivi günceller → vadesi gelen koşuları işler
(posta−5 dk) → Altılı kuponlarını kurar (dk grubuna göre) → oran_log'a yazar → tüm koşular
bitip son postadan 40 dk geçince `defter.sonucla()` + `altili_canli.sonucla_altili()`
(günde bir kez, marker ile). **Durumsuzdur** (K49): çökerse sonraki geçiş kaldığı yerden sürer.

**Çift tıklama araçları:**

| .bat | ne zaman | ne yapar |
|---|---|---|
| `altili_goster.bat` | her gün 22:30 sonrası | ayakları sonuçla + kupon anı geri kur + HTML aç |
| `paper_goster.bat` | gerektikçe | paper kuponları sonuçla + sayfa |
| `sonuclari_goster.bat` | gerektikçe | defter sonuçla + sayfa |
| `kayip_bak.bat` | PC kapatılan günün ertesi | hasar raporu (14 gün) |
| `suruklenme_bak.bat` | haftada bir | uzak-ayak λ ölçümü |
| `baslat_takip.bat` | kurtarma | elle tek geçiş |
| `bahis_gir.bat` | (kullanılmadı) | gerçek bahis kaydı |

---

## 6. VERİ DOSYALARI (git'te olanlar)

| dosya | satır | ne |
|---|---|---|
| `altili_kupon.csv` | 2.850 | canlı Altılı kuponları (config × ayak) |
| `altili_kupon_ani.csv` | 4.134 | **kupon anındaki olasılık vektörü** — `dk_grup` ile anahtarlı (K97/K105) |
| `altili_oran_log.csv` | 24.867 | gün-içi oran geçmişi, ayak başına çok anlık görüntü (K59/K76) |
| `altili_temettu.csv` | 86 | resmî Altılı temettüleri + devir |
| `defter.csv` | 5.379 | her koşunun tüm atları: bot1/bot2/kamu/oran/model_rank/sonuç |
| `paper_kupon.csv` | 1.247 | ganyan/plase kâğıt testi (K42) |
| `altili_tam.csv` | 6.747 | tarihsel Altılı olayları + 6/5/4/3'lü temettü ve devir |
| `altili_olasilik_bot1.csv` | 232.100 | backtest için walk-forward bot1+bot2+kamu |
| `nli_ganyan.csv` | 27.442 | N'li ganyan olayları (K94 kesinti ölçümü) |
| `egzotik.csv` | 34.994 | ikili/üçlü temettüler |
| `devir.csv` | 1.337 | carryover olayları |

**Zaman damgası kuralı:** `defter.csv` koşuya **5 dk kala** yazılır (yarış anı).
`altili_kupon_ani.csv` **kupon kurulurken** yazılır (karar anı). İkisi farklı vektörlerdir.

---

## 7. ÖLÇÜLMÜŞ SABİTLER — SİSTEMİN "FİZİĞİ"

Bunların hepsi **ölçüldü**, varsayılmadı:

| büyüklük | değer | kaynak |
|---|---|---|
| harman α / γ | **0,21 / 0,95** | K96 — R²=0,9996 *(katsayıların geri çıkarılabilirliği; modelin öngörü gücü DEĞİL)* |
| Bot1'in net katkısı | **%0,75** | K96 |
| uzak ayak λ | **0,650**, %90 GA **[0,465 – 0,875]** → 1'i İÇERMİYOR | K92, eşleşmiş n=87 koşu |
| **ganyan kesintisi (İngiliz)** | **%28,3 ortalama**, medyan %25,6, %10-90: %25,3–%37,0 | **K104** |
| **plase kesintisi** | **≥%14** (bağımsız ölçülmedi — K106) | K104 → **K106 düzeltmesi** |
| 3'lü ganyan | %45,4 | K94 |
| 4'lü | %45,6 | K94 |
| 5'li | %46,8 | K94 |
| **6'lı (Altılı)** | **%48,6** | K94 |
| 7'li | **%57,6** (en pahalı ürün) | K94 |
| yabancı yarış kesintisi | medyan %25,6 (yerliyle **aynı**) | 16 Ağu, KARARLAR'a yazılmadı |
| kupon genişliği | bütçenin **6. kökü** (900^(1/6)=3,11) | K88 |

> **K93 DÜZELTMESİ (K104):** "ganyan −%25,4 = kesinti %25,5, birebir tuttu" ifadesi kısmen
> tesadüftü. Doğru referans %25,5 değil, oynadığımız koşuların gerçek ortalaması **%28,3**.

> ⚠️ **DAĞILIM KAYMASI — BACKTEST SAYILARI CANLIYA BİREBİR TAŞINMAZ (K107).**
> `altili_backtest.py`'nin `prep()`'i yalnızca **muhtemel + kapanış oranı bulunan ve tek
> kazananı olan** koşuları alır. Canlı taraf ise kartta ne varsa puanlar. Backtest evreni bu
> yüzden canlı evrenden sistematik olarak ayrılır (temizlenmiş bir örneklem). Yukarıdaki K96
> türevleri ve backtest ROI'leri **yön göstergesidir, seviye göstergesi değil.**

> **BAĞIMSIZ DOĞRULAMA:** 14 Ağu İstanbul 2. Altılı 2.780.891 TL ödedi. Temettü ÷ (aynı altı
> atın ganyan parlayı) = **3,74**. Teorik beklenti (Altılı kesintiyi bir kez, altı ganyan
> altı kez alır): (1−0,486)/(1−0,283)⁶ = **3,78**. İki kesinti ölçümü tek olayda doğrulandı.

---

## 8. KAPANMIŞ KOLLAR — ÖLÇÜMLE

### Kupon şekli kolu — **BEŞ RET, KAPALI**
| karar | ne denendi | sonuç |
|---|---|---|
| K68 | ayrışma dağıtımı | üç ölçüt de düştü; canlıda açgözlünün **ikizi** çıktı (ayakların %78'i birebir aynı, McNemar p=0,80) |
| K90 | bot1+bot2 birleşim kuponu | kriter geçilemedi |
| K98-f | üç bot2 kuponunu tek kupona indirme | "birleşim+buda" 1.433 olayın **1.432'sinde** `genis900`'ün kelimesi kelimesine aynısı |
| K98-g | `orta`yı çoğaltma (2×, 3×, 4×) | isabet %4,6→9,6 ama ROI −35,5→−59,8. Tek ayakta bölmek = o ayağı genişletmek (iki farklı bölme kuralı **birebir aynı** sonucu verdi) |
| K101 | banker takası (kullanıcının "alternatif kupon" fikri) | dört hücrede de RED. Teşhis doğru (A banker ayağını %50-61 kaçırıyor) ama B o ölümlerin **%2-4'ünü** kurtarıyor |

### **EN ÖNEMLİ YAPISAL BULGU — "TAVAN" (K98-h)**
Dikdörtgen kısıtı olmadan "en olası N kombinasyon" seçilebilseydi:

| | 6/6 | ROI | ort. temettü |
|---|---|---|---|
| orta@96 (dikdörtgen) | 66 | **−35,5%** | **1.656** |
| tavan, 96 kombinasyon | **87** | −56,3% | 864 |

Tavan %32-64 daha fazla tutturur ama **temettüsü yarısıdır** ve ROI'si ~21 puan kötüdür.
**En olası kombinasyonlar herkesin oynadığıdır → kapsamı büyütmek kalabalığa katılmaktır.**
Tersi de doğru: **kuponun dikdörtgen olma zorunluluğu bir handikap değil, kazara işleyen
bir kalabalıktan-kaçınma mekanizmasıdır.** Bu, K65'i (açgözlü daha çok tutturur, daha az
kazandırır) yeni bir açıdan açıklar.

### ⚠️ PROJENİN BİRİNCİL KISITI: FEED

Aşağıdaki kapalı kolların hepsi aynı duvara çarpıyor ve duvarın adı **veri erişimi**.
Benter'in Hong Kong'da ulaştığı sonuç modelleme zekâsından çok idman zamanları, veteriner
kayıtları ve sectional time'lardan geliyordu. **TJK feed'inde bunların hiçbiri yok.**

α=0,21'in küçüklüğü bir model zayıflığı değil, **mevcut veri kümesinin bilgi tavanıdır.**
K102 bunun kanıtı: ata-özel kulvar tercihi bağımsız bilgi taşıyor (katsayı −0,0181) ama yine
de faydasız — çünkü piyasa, bizim erişebildiğimiz her şeyi zaten fiyatlamış.

> **Feed genişlemeden model genişlemez.** Yeni bir oturum "belki şu özelliği eklesek" turuna
> girmeden önce bu satırı okumalı.

### Diğer kapalı kollar
- **Bütçe (K88/K91/K98):** genişletmek kenar satın almıyor, tutturma sıklığı satın alıyor.
  900→1800 P(6/6)'yı ~5 puan artırır, marjinal ROI aynı sızıntıda. Yüksek ödüllü
  near-miss'lerin dönüşümü %10, düşüklerin %17 — **bütçe büyükleri KURTARMIYOR**.
- **Ürün (K94):** 7'li "yeni ürün fırsatı" hipotezi çürüdü, en pahalı ürün.
- **Harman ağırlıkları (K96):** α/γ değişmemeli, yıllar arası kararlı.
- **Özellik mühendisliği (K33, K102 ile teyit):** ata-özel kulvar tercihi test edildi,
  Bot2'yi **0,00004 kötüleştirdi**. İlginç: eşdoğrusal ÇIKMADI (bağımsız bilgi taşıyor,
  katsayı −0,0181) ama faydasız. Sebep K96'da: piyasa jokeyi/kulvarı/havayı zaten fiyatlamış.
  **Hava/going toplanıyor ama özellik değil** (going K33'te elendi). **Antrenman verisi
  feed'de YOK.**
- **Zamanlama — yayvanlık (K104-f):** "sahaların açık olduğu günlerde ROI daha mı iyi?"
  → **BULGU YOK**. Yayvanlık temettüyü öngörüyor (korelasyon −0,316; temettü 2,6 katı) ama
  isabeti aynı oranda düşürüyor (21 vs 45). Havuz bu boyutta **etkin**.

### SEÇİM KATMANI TEK BAŞINA TEST EDİLDİ — hiçbir config kalabalığı yenmiyor (K106)

Bugüne kadarki bütün ölçümler kupon şekli, bütçe ve kesintiyi birlikte taşıyordu. **ÖLÇÜM A0**
(`kod/ayak_kalibrasyon.py`) ilk kez yalnız **seçim katmanını** test etti:

> *Her ayakta config k at yazıyor. Aynı ayakta, aynı k ile KAMU cetvelinin ilk k'si alınırsa,
> hangisi kazananı daha çok tutuyor?*

~2.850 ayakta, eşleşmiş McNemar ile: **hiçbir config'te p<0,05.**

| config | ayak | kapsam | yalnız-sis | yalnız-kamu | p | karar |
|---|---|---|---|---|---|---|
| acgozlu900 | 402 | %92 | 9 | 3 | 0,146 | **kenar kanıtı yok** |
| bot1_900 | 353 | %97 | 57 | 49 | 0,497 | **kenar kanıtı yok** |
| bot1_1800 | 149 | %100 | 20 | 21 | 1,000 | **kenar kanıtı yok** |
| acgozlu_v2 | 206 | %99 | 4 | 0 | 0,125 | BAKILAMAZ (4<6) |
| ayrisma900 | 204 | %94 | 3 | 1 | 0,625 | BAKILAMAZ (4<6) |
| orta_15 | 53 | %100 | 3 | 1 | 0,625 | BAKILAMAZ (4<6) |
| acgozlu900_15 | 47 | %100 | 0 | 0 | 1,000 | BAKILAMAZ (0<6) |
| dar · orta · genis · genis900 | 275-424 | %69-86 | — | — | — | GEÇERSİZ (kapsam<%90) |

**GEÇERLİ HÜKÜM — `acgozlu900`, `bot1_900`, `bot1_1800` için:** aynı parayla, bizim cetvelimiz
kalabalığın cetvelinden **ölçülebilir biçimde farklı değil.** Projenin ürettiği en temiz
"kenar yok" ifadesi — kupon şekli ve kesinti değişkenlerinden arınmış.

⚠️ **GÜÇ EŞİĞİ (K107 — K106'daki ifademin düzeltmesi).** Tam binom testi, iki yönlü α=0,05'e
ulaşmak için **en az 6 uyumsuz çift** ister (n=4 → hepsi tek yanlı olsa bile p=0,125).
Dört config bu eşiğin altında → onlar için **"kenar yok" DEĞİL, "bu örneklemle bakılamaz."**
Ölçüt `ayak_kalibrasyon.py`'de `ASGARI_UYUMSUZ = 6`; karar akışı kapsam → **güç** → p.

⚠️ **ÇOKLU TEST.** 11 config × 2 test bakılıyor. Olay-bootstrap'te `acgozlu_v2` (+1,9 puan
[+0,5, +3,9]) ve `acgozlu900` (+1,5 [+0,0, +3,0]) GA'ları sıfırı dışlıyor — **kenar bulgusu
değildir**: (1) `acgozlu_v2`'de McNemar aynı veride BAKILAMAZ diyor; (2) 11 config'te bir GA'nın
şansa sıfırı dışlaması ~0,55 kez beklenir; (3) yüzdelik bootstrap bu seyreklikte
anti-muhafazakârdır. **Ön-kayıtlı birincil ölçüt McNemar'dır**, bootstrap betimleyicidir.

*Kapsam notu:* `dar/orta/genis/genis900` kupon-anı kaydı %69-86 → ön-kayıtlı %90 eşiğiyle
**GEÇERSİZ**. Kapsam arttıkça tekrarlanmalı.

### ⚠️ ORAN SÜRÜKLENMESİ TUZAĞI — muhtemel oranla DEĞER hesaplanmaz (K109)
Kupon anındaki muhtemel oran, kapanışa doğru **sistematik ve taraflı** biçimde kayar
(1.002 kazanan ayak, son kayıt ~16 dk kala):

| kupon-anı oranı | ortalama değişim |
|---|---|
| <4 | **+%61,1** (açılıyor) |
| 4-8 | +%1,5 |
| 8-16 | −%23,9 |
| 16+ | **−%61,4** (çöküyor) |

Müşterek bahiste ödenen fiyat **kapanış** fiyatıdır; muhtemel oranla hesaplanan kazanç
**tahsil edilemez**. Yanlışlık orana kör config'leri kayırır: `bot1_900`'ün ayak-ganyan
ROI'si muhtemelle **+%19,4**, son görülen fiyatla **−%17,9** — **37 puanlık yanılsama.**
Mevcut ölçümler bu hatayı taşımıyor (defter `ganyan_kapanis` kullanır, A0 orana hiç bakmaz,
K104 kapanışla ölçtü). **Yeni bir değer ölçüsü kurarken ilk sorulacak soru budur.**

### Ayak düzeyi sicili — iki config ailesi gerçekten farklı, ama para etmiyor (K109)
1.896 ayakta ölçüldü. **bot1 ailesi orana kör olmanın ders kitabı davranışını gösteriyor:**
favoride ~20-27 puan bırakıyor (`bot1_1800` %71,1 vs `acgozlu900` %98,3 — kamu 1.'si kazanınca),
sürprizde ~18-20 puan kazanıyor (%46-48 vs %28-32 — kamu 5+'i kazanınca). `orta` ise 154
sürpriz ayağın **2'sini** tutmuş (%1,3) → **`orta` neredeyse tanım gereği kalabalığın kendisi.**
Bu fark **gerçek ama paraya dönüşmüyor** (yukarıdaki sürüklenme).

**Marjinal katkı:** eklenen n. atın verimi (isabet artışı / maliyet artışı) **hiçbir yerde
1'i geçmiyor**; 3. attan sonra 0,87-0,92'de düz. Tatlı nokta yok — genişletmek her yerde
eşit derecede biraz zararlı. K98-h/K108'in ayak düzeyindeki ifadesi.

**Banker:** yedi config'in **beşinde** kamuyla fark tam **+0,0** → tek at yazdığımızda
kamunun favorisini yazıyoruz. Kuponun en pahalı kararında sistemin kalabalıktan ayrımı yok.

### 4'lü / 5'li ürün kolu — ÖLÇÜLDÜ, REDDEDİLDİ (K108)
TJK'da 4'lü/5'li/6'lı **aynı koşuda biter, ayakları iç içedir** (4.931 üçlünün %100'ü) →
990 eşleşmiş olayda, aynı gün/pist/saha, **aynı parayla** kıyaslandı (birim fiyatlar farklı:
1,75 / 1,50 / 1,25 TL, o yüzden kombo değil TL eşitlendi).

- **Mekanizma yok:** 16 testin 1'i geçti (şansa beklenen 0,8), o da tekrarlamıyor.
- **Oynanamaz:** 24 hücrenin sıfırında ROI ≥ 0. En iyi hücre **−%38,5**.
- **TAVAN KISA ÜRÜNDE DE GEÇERLİ:** ayak azalınca isabet **4-8 kat** artıyor, ortalama ödeme
  **0,15-0,54 katına** düşüyor, çarpım ≈ **1,0**. → **Tavan bir kupon-şekli özelliği değil,
  PİYASA özelliğidir.** Kolay tutan bahsi herkes tutuyor; hangi yoldan kolaylaştırdığın
  fark etmiyor.
- **Yan teyit:** ölçülen ROI'ler bağımsız hesaplanan kesintinin üstüne oturdu (6'lı −%63,4 vs
  kesinti %66,8) → "kupon sadece kesintiyi ödüyor" üçüncü bir üründen doğrulandı.

Araç: `kod/nli_backtest.py` (salt offline). Ürün kolu böylece hem kesinti tarafından (K94)
hem kupon tarafından (K108) kapandı.

### Kâğıt ROI teoriye yakınsadı (K93)
Altılı −%33,3 (backtest −%32) · ganyan −%25,4 (o zamanki referans). **Kenar yok.**

---

## 9. CANLI SİCİL (16 Ağu 2026)

| config | durum | kupon | 6/6 | 5/6 | ayak | bedel | ödül | net |
|---|---|---|---|---|---|---|---|---|
| `orta` | aktif | 83 | 1 | 5 | %46 | 9.510 | 17.934 | **+8.424** |
| `orta_15` | aktif | 1 | 0 | 0 | %50 | 120 | 0 | −120 |
| `acgozlu900` | aktif | 65 | 2 | 12 | %62 | 70.034 | 19.705 | −50.329 |
| `acgozlu900_15` | aktif | 0 | — | — | — | 0 | 0 | 0 |
| `bot1_900` | aktif | 53 | 2 | 11 | %61 | 57.066 | 50.666 | **−6.400** |
| `bot1_1800` | aktif | 17 | 0 | 3 | %60 | 36.255 | 0 | −36.255 |
| `acgozlu_v2` | aktif | 27 | 0 | 4 | %62 | 29.018 | 0 | −29.018 |
| *emekliler* | — | 208 | 1 | 20 | — | 103.749 | 6.721 | −97.027 |
| **TOPLAM** | | | **6** | | | **305.751** | **95.026** | **−210.725** (ROI −%68,9) |

**Paper testi (ganyan/plase, K42):** 1.042 sonuçlanmış kupon, bedel 15.630, getiri 11.012,
net −4.618 (−%29,5). Ganyan −%34,2 · plase −%14,0. **Seçim zararı yok** (kalibrasyon 0,977
ve 0,960, ikisi de 1,00'i içeriyor).

> **UYARI 1 — TOPLAM satırı bir PORTFÖY TAVSİYESİ DEĞİLDİR.** Harcamanın çoğu 900-1800
> kombinasyonlu gözlem akışlarından gelir (`acgozlu900` ~1.077 TL/kupon, `orta` ~115 TL/kupon).
> K98-i'nin canlıya çıkış tavsiyesi **yalnız `orta`**. Bu toplam, paralel yürüyen deneylerin
> ortak faturasıdır.

> **UYARI 2 — `orta`'nın +8.424'ü TEK BİR OLAYDIR.** Altılı yalnız 6/6 öder; `orta`'nın 1
> isabeti var, dolayısıyla 17.934 TL ödülün **%100'ü tek biletten** (23.07 Ankara 2.). O olay
> çıkarsa `orta` −9.510, ROI −%100. Backtest'te "getirisinin yalnız %5'i en büyük kupondan"
> diyor; **canlıda %100.** İki sayı yan yana okunursa `orta` kanıtlanmış sanılır — değildir.
> (K106; rapor artık bu uyarıyı otomatik basıyor.)

> **UYARI 3 — `bot1_900` yanıltıcıdır.** Net −6.400 iyi görünüyor ama backtest'te bot1@900'ün
> tüm getirisinin **%43'ü tek bir kupondan** geliyordu (539.029 TL'lik temettü); o olay
> çıkınca ROI −%18,3'ten **−%53,2**'ye düşüyor. **Kenar değil, piyango biçimi.** Canlı
> portföye konmamalı (K98-e).

---

## 10. AÇIK DENEYLER

| deney | ne ölçüyor | veri | tetik |
|---|---|---|---|
| `acgozlu_v2` vs `acgozlu900` | uzak-ayak λ düzeltmesi işe yarıyor mu (K92) | 27 kupon | BEKLEYENLER #9; K87 taban çizgisi, K89 yöntemi |
| `bot1_1800` vs `bot1_900` | bot1'i piyangoluktan çıkarır mı | 17 kupon | 25 Eyl |
| `orta_15` vs `orta` | 15 dk kala kurmak daha mı iyi (dar kupon) | 1 kupon | BEKLEYENLER #4, ~60 kupon |
| `acgozlu900_15` vs `acgozlu900` | aynı soru **geniş** kuponda | 0 kupon | aynı |

**Zamanlama simülasyonu (15 Ağu, 18 tam Altılı, 108 ayak, `orta`):** yalnız-30 tuttu 10,
yalnız-15 tuttu 15, net **+5 ayak, p=0,424** (anlamsız). **İç kontrol:** `bot1_900` ve
`bot1_1800` farkı **tam +0** — bot1 orana bakmaz, teorinin dediği budur → simülasyonun
kendisi doğrulandı. Bu yüzden bot1'e 15 dk ikizi **açılmadı**.

**10 dk bandı YOK:** takip 15 dk'da bir çalışıyor, o pencereye sistematik geçiş düşmüyor →
örneklem yanlı kesilir. Çözümü görev sıklığını artırmak; **ayrı karar konusu**.

---

## 11. AÇIK SORULAR (BEKLEYENLER.md)

| # | konu | tetik |
|---|---|---|
| 2 | ~~4'lü / 5'li kupon türleri~~ | **KAPANDI (K108, 18 Ağu)** — 990 eşleşmiş olayda ölçüldü, mekanizma yok, en iyi ROI −%38,5. Bkz. §8 |
| 3 | `defter.html`'i K55 görsel diline çevirme | sıra gelince |
| 4 | 30 vs 15 dk | **canlı kol açıldı**, ~60 kupon sonra |
| 5 | Altılı sonuçlamada favori-devri kuralı | doğruluk kritikleşirse |
| 6 | ağırlıkları geniş pencereyle yeniden fit | sınav dönemi kapanınca (K96 erken "gerek yok" cevabı verdi) |
| 9 | açgözlü uzak ayakta bankeri hak ediyor mu | λ kolu K92'de kapandı, ileri ölçüm sürüyor |
| ZAMANLI 4 | **paper test karar noktası — 25 Eylül 2026** | takvim |
| ZAMANLI 6 | `veri/ham` harici kopya | 3 ayda bir |

**Ölçülüp KAPANANLAR:** #1 (K57) · #7 (K68) · #8 (K94) · #10 (K98) · #10-B (K101) ·
ZAMANLI #5, #6 (uzak depo bağlandı).

---

## 12. ÇALIŞMA DİSİPLİNİ — BU PROJEDE SIKI UYGULANIR

1. **Önce veri, sonra yorum.** Kullanıcının öncülünü doğrulamadan kabul etme; kendi
   öncülünü de doğrulamadan sunma.
2. **Hindsight/overfit YASAK.** Karar kuralları **sonuç görülmeden** yazılır ve sonuca göre
   değiştirilmez. Örnekler: K98'de λ=0,50 ve @192 taramanın en iyisiydi, **ikisi de
   alınmadı**; K101'de ölçüt düşünce gevşetilmedi.
3. **Kontrol koymadan sonuç sunma.** Bugüne kadar **yedi kez** yanlış sonuçtan dönüldü:
   enflasyon artifaktı (K73/K94) · kova karışması (K81) · çarpımsal kalibrasyon (K94) ·
   bot1 kontrol grubu (K81) · λ'nın nereye uygulandığı (K98) · bölme kuralı kontrolü (K98) ·
   ayrışma skorunun hizası (K98-j).
4. **Tek değişken.** İki şeyi aynı anda değiştirme; `acgozlu_v2`'nin `acgozlu900`'den TEK
   farkı λ'dır, bu yüzden aradaki her fark ona atfedilebilir.
5. **Her ölçüm KARARLAR.md'ye gerekçesiyle yazılır ve commit edilir.** Yazılmayan ölçüm
   altı ay sonra yeniden yapılır.
6. **Tetik bir tarih değil bir SAYI ise, sayıya bakılır** (K105 dersi — "Ekim'i bekle"
   notu 15 gün boyunca gereksiz tekrarlandı).
7. **Rapor alanı eklerken mevcut alanı DEĞİŞTİRME** (K103 dersi — kamu sırası K97'de
   sessizce düştü, iki hafta fark edilmedi).
8. **Yardımcı kayıtlar kupon kurmayı ASLA engellemez** (K97-k) — kupon kurulmazsa o Altılı
   deneyden düşer, ölçülen en pahalı hasar budur.

---

## 13. RAPORU OKUMA KILAVUZU

`raporlar/altili.html` her at için **dört etiket** basar:

| etiket | anlamı |
|---|---|
| **K** | kupon anındaki **harman** sırası — *kararı yargılarken doğru cetvel* |
| **Y** | yarış anındaki **harman** sırası (posta−5 dk, defter) — *sonucu okurken* |
| **B** | **bot1'in kendi sırası** — yalnız bot1 config'lerinde; **seçimi yapan cetvel odur** |
| **P** | **kamu (piyasa) sırası**, kupon anında |

Renkler: **turuncu** = K ile Y 3+ sıra kaymış (sürüklenme) · **mor** = sistem kamudan 3+
sıra ayrı (ayrışma).

> **Neden dört etiket var — üç ayrı yanılgının bedeli:**
> - **K97:** sayfa yalnız yarış anı sırasını gösteriyordu. Kupon ilk ayaktan 30 dk önce
>   kurulur, son ayağın kararı 2-3 SAAT öncedir. Ölçüm: iki sıra yalnız %30 aynı, %22'si
>   3+ sıra farklı, fark mesafeyle büyüyor (<30 dk %15 → 120+ dk %32).
> - **K99:** bot1 sütununda harman sırası gösteriliyordu, kupon delik delik görünüyordu.
>   Oysa bot1 kendi cetvelinde kesintisiz seçim yapıyordu.
> - **K103:** kamu sırası K97'de eklenmesi gerekirken **değiştirilmişti**; bu projenin
>   merkezindeki "kalabalıkla aynı mı ayrı mı" kıyası iki hafta görünmez kaldı.

---

## 14. BİLİNEN KIRILGANLIKLAR

- **`veri/ham` (1,1 GB) yalnız bu diskte.** Git'te değil. TJK arşivi kapanırsa `kazi.py`
  yeniden indiremez → 3 ayda bir harici kopya.
- **PC yarış saatlerinde kapalıysa veri kaybı olur.** Kupon anları 12:30–18:31 bandında,
  **15:00 en yoğun**. Zorunlu kesinti **15:30'da başlamalı** (K82). 10:30 öncesi / 22:30
  sonrası maliyet sıfır. Üç hasar türü: kurulmayan Altılı (en pahalı) · geç kurulan kupon
  (en sinsi, zamanlama ölçümünü kirletir) · düşen defter kaydı (en ucuz).
- **ÖLÇÜLEN HASAR ORANI (son 14 gün, `kod/kayip_raporu.py`):** 14 günün **4'ü tamamen temiz**;
  2 kurulmayan Altılı (= 14 kupon deneyden düştü) · **0 geç kurulan kupon** · 0 yarış sonrası
  kayıt · 35 düşen defter koşusu. Araç kendi sayısının **alt sınır** olduğunu söylüyor.
- ⚠️ **SESSİZ KOL ÖLÜMÜ — 16 Ağu 2026 vakası (K107).** Takip gün boyu döndü (17 koşu "bitti",
  oran_log dolu, 4 Altılı'ya 7 config kupon kurdu) ama `defter.csv` ve `paper_kupon.csv`'ye
  **tek satır yazılmadı**. Sicildeki tek böyle gün; 32 günün taramasında başka yok. O günün
  kalibrasyon/ROI/paper kaydı **kalıcı olarak kayıp** — geriye yazmak K36'nın yasakladığı şey.
  Kök neden bulunamadı çünkü tanı mesajları `print`'e gidiyordu ve görev **pythonw** ile sessiz
  koşuyor. İki düzeltme: `takip.py`'de o mesajlar artık `_log`'a düşüyor; `bekci.py`'ye üçüncü
  denetim (**defter kapsaması**) eklendi — "bitti" mührü sayısı vs deftere yazılan koşu sayısı,
  ≥2 fark → ekran uyarısı. Geriye dönük sınandı: **32 gün, 1 alarm, sıfır yanlış alarm.**
  **DERS:** bir kolun sessizce ölmesi, hata vermesinden pahalıdır. `except` bloğuna düşen her
  mesaj log'a da yazılır; `print` tek başına kayıt sayılmaz.
- **`kod/telegram_config.json` git'te değil** — bot yeniden kurulursa elle konmalı.
- **Yabancı yarışlar sistemin dışında.** `gunluk.yerli_pistler()` feed'deki `GUN` alanına
  bakar; TR pistlerinde sayısal, yabancıda `None` → elenirler. Arşivde tek bir yabancı
  koşu yok. Kesintileri ölçüldü (medyan %25,6, yerliyle aynı) → **avantaj yok**, kol
  bilinçli olarak kapalı.
- Oturum geçmişi workspace klasörüne bağlı; klasör değişirse eski sohbetler başka
  klasörde kalır.

---

## 15. TAKVİM

- **25 Eylül 2026** — K42 kâğıt testinin bitişi ve **sistem modu kararı** (K42/K48).
  O tarihe kadar açık deneyler (`acgozlu_v2`, `bot1_1800`, `orta_15`, `acgozlu900_15`)
  veri biriktirecek.
- **Canlıya çıkılacaksa** (K98-i tavsiyesi): **tek kupon, `orta`**, Altılı başına 118 TL,
  ortalama −42 TL/Altılı. Şansa en az bağımlı olan odur (ROI(−1) −%44,4; getirisinin yalnız
  %5'i en büyük kupondan). **bot1 portföye konmamalı.** Zaten var olan config, yenisi
  gerekmez.
- **Ama:** "canlı kâğıt gibi mi davranıyor?" sorusunun cevabı **zaten var** (K93) → canlı
  paranın ölçüme katkısı yoktur.

---

## 16. KOD DİZİNİ

**Canlı hat (dokunurken dikkat):**
`takip.py` (15 dk'lık geçiş, durumsuz) · `altili_canli.py` (kupon üretimi + HTML, 65 KB) ·
`gunluk.py` (canlı puanlama) · `defter.py` (kâğıt defter) · `paper.py` (K42 testi) ·
`oran_log.py` (gün-içi oran) · `rapor_ortak.py` (rapor zenginleştirme, salt-okunur) ·
`telegram_at.py` · `bekci.py` (**nabız + config kapsaması + defter kapsaması**, K106/K107) · `veri_commit.py`

**Boru hattı:** `kazi.py` → `duzlestir.py` → `ozellik.py` → `model.py` ·
`altili_tam.py` · `altili_olasilik.py` · `guncelle.py`

**Ölçüm araçları (offline, salt-okunur):**
`ayak_analiz.py` (**K109 — aktif config'lerin ayak düzeyi sicili + oran sürüklenmesi**) · `altili_backtest.py` (dağıtıcıların tek kaynağı) · `nli_backtest.py` (**K108 — 4'lü/5'li kolu; N-ayak dağıtıcıları N=6'da orijinalle eşdeğerliği sınanmış**) · `altili_canli_secim_test.py` (K98'in
dokuz tablosu) · `altili_banker_takasi_test.py` (K101) · `kulvar_tercih_test.py` (K102) ·
`altili_suruklenme.py` (K80 λ) · `altili_zaman_test.py` (30 vs 15 dk) ·
`kayip_raporu.py` (K82) · `kupon_ani_geri_kur.py` (K97 geri kurma) · **`ayak_kalibrasyon.py`** (K106 ÖLÇÜM A0 — seçim katmanı)

**Arşiv testler (kapanmış kollar):** `altili_bot1_test.py` · `altili_dagitim_test.py` ·
`altili_ayrisma_test.py` · `altili_birlesim_test.py` · `altili_kap_test.py` ·
`altili_deger_test.py` · `altili_taban_test.py` · `altili_agf_yanlilik.py` ·
`altili_ayak_korelasyon_test.py` · `plase_test.py` · `plase_model.py` · `arap_test.py` ·
`egzotik*.py` · `favori_test.py` · `chalk_egzotik.py` · `yapisal.py` · `segment.py`

---

## 17. YENİ OTURUMA BAŞLARKEN

1. `KARARLAR.md`'nin **son 10 kararını** oku (şu an K95–K105) → güncel duruma hâkim olursun.
2. `BEKLEYENLER.md`'yi tara → hangi işin tetiği geldi.
3. Bir şey ölçeceksen **ölçütü sonucu görmeden yaz**.
4. Bir şey değiştireceksen **önce geçmiş sicilin bozulmayacağını doğrula**
   (GENEL TOPLAM'ı bağımsız CSV hesabıyla karşılaştır — K100/K105'te böyle yapıldı).
5. Sonucu KARARLAR'a yaz, commit et, **push et** (uzak depo var artık).
