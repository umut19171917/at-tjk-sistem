# Karar Günlüğü

Her karar: tarih, karar, gerekçe. Değişirse yeni satır eklenir (eski silinmez).

---

## 2026-06-29 — Başlangıç ve veri incelemesi

**K1 — Problem çerçevesi.** Pari-mutuel + kesinti → negatif toplamlı. Hedef: havuz
mispricing'ini bulmak, "kazanan tahmini" değil.
*Gerekçe:* Favori genelde doğru fiyatlanır; sadece kazananı bilmek kesinti kadar kaybettirir.

**K2 — Hedef: sürdürülebilir EV>0**, Benter-ilhamlı (kopya değil), jackpot avı yok.
*Gerekçe:* Kullanıcı açıkça gerçekçi/sürdürülebilir kazanç istedi.

**K3 — Faz 1 kapsamı: TR İngiliz atı düz koşuları, Ganyan + Plase.**
*Gerekçe:* Edge'i en hızlı ölçebileceğimiz, en derin/likit, bizim bahsimizin oranı en az
kaydırdığı havuzlar.

**K4 — 4 pist (Elazığ, Diyarbakır, Urfa/Şanlıurfa, Adana) hariç — hem tahmin hem EĞİTİM.**
*Gerekçe:* Şike söylentileri yaygın (kullanıcı); şikeli sonuç gerçek gücü yansıtmaz → modeli
kirletir. Ayrıca bu pistler ağırlıkla Arap atı, zaten kapsam dışı.

**K5 — Altılı/çok-koşulu + egzotik + yabancı koşular ertelendi.**
*Gerekçe:* Çok-koşulu = devasa varyans/örnek azlığı/vergi eşiği. Egzotik = sığ havuz + price
impact + kombinatorik. Yabancı = seyrek form + küçük havuz. Önce dar kapsamda edge kanıtla.

**K6 — Çalışma alanı `Desktop/projeler/at`; kripto klasörü/hafızası kapsam dışı; bu projede
otomatik hafıza KULLANILMAZ** (kayıt dosya tabanlı).
*Gerekçe:* Kullanıcı net talep etti; otomatik hafıza cwd üzerinden kripto'ya bağlı.

**K7 — Modelleme referansı: Benter çerçevesi** (fundamental conditional-logit + kamuoyu oranını
özellik olarak harman + yalnızca model>piyasa kesintiyi aşınca oyna + kesirli Kelly).
*Durum:* ⚠ Orijinal rapor (W. Benter, 1994) birincil kaynaktan henüz doğrulanmadı.

**K8 — Veri kaynağı: `ebayi.tjk.org` statik JSON.** Üç katman mevcut, arşiv ≥2021.
Detay: `raporlar/faz0-veri-fizibilite.md`.

**K9 — Eldeki veri = SADECE 3 ay (2024-10-04 … 2024-12-31).** Kullanıcıda başka veri yok.
1.602 koşu; izinli pistlerde 1.041 koşu / 9.340 katılım. İngiliz+izinli ≈ ~600-700 koşu.
*Sonuç:* Prototip için yeter, edge kanıtı (Kapı #3) için YETERSİZ → ileride scraper ile
genişletme şart. Detay: `raporlar/kapi2-veri-inceleme.md`.

**K10 — Ganyan havuzu kesintisi ~%25,7** (verideki medyan overround 1,345).
*Gerekçe/anlam:* Benter'in başarılı olduğu Hong Kong'dan (~%17-19) yüksek → eşik sert, edge
marjı dar. İmkânsız değil ama zorlu.

**K11 — İletişim kuralı: Asistan, seçenek sunduğu her iletinin sonunda kendi tavsiyesini
gerekçesiyle verir.** Kullanıcı her seferinde "senin fikrin ne" diye sormak zorunda kalmaz.
*Gerekçe:* Kullanıcı açıkça istedi (2026-06-29).

**K12 — Sıradaki adım: Faz 1a — Veri hazırlama + Piyasa baz çizgisi** (eldeki 3 ay, MODEL YOK).
ONAYLANDI (2026-06-29). İçerik: (1) temizle+join (İngiliz+izinli pist, parse kilo/yaş/start),
(2) ganyan muhtemel mi kapanış mı teyit, (3) piyasa baz çizgisi: favori kazanma oranı,
kalibrasyon eğrisi, favori-uzunşanslı sapması, kesinti dağılımı, (4) git/no-git kararı.
Araç: Python + pandas. Yer: `at/kod/`.
*Gerekçe:* Baz çizgi MARKETİ karakterize eder (~1000 koşu bunu kaldırır; model-fit kaldırmaz),
overfit etmez, scraper'ı de-riske eder, ve erken git/no-git sinyali verir.

**K13 — Baz çizgi sonucu: piyasa VERİMLİ, kesinti ~%25,5.** Favori %34,6 kazanıyor (implied
%34,2 — neredeyse tam kalibre); hiçbir oran bandı pozitif ROI vermiyor (en iyisi −%23, kapanış/
iyimser). Tek desen: uç uzunşanslılar (30+) ağır şişirilmiş.
*Anlam:* Kolay/naif edge YOK. Kâr ancak fundamental modelin kova-içi mispricing bulmasıyla
mümkün — bu da bu veride (form yok) test edilemez. Önsel beklenti karamsar ama "kesin hayır"
için form'lu veri + α testi şart. Detay: `raporlar/faz1a-piyasa-baz-cizgisi.md`.

**K14 — Mimari: iki aşamalı (Benter-uyumlu). ONAYLANDI.**
- Bot 1 (oran KÖR): conditional logit → p_fund. Eğitilmiş şeffaf model, elle-formül DEĞİL.
- Bot 2 (oran AÇIK): p = combine(p_fund, p_piyasa; α,γ) → değer (p×oran−1>marj) → kesirli Kelly.
- **Yerleşik kill-criterion:** Bot 2'nin Bot 1'e verdiği α ağırlığı. α≈0 → dur; α anlamlı → devam.
- Tuzaklar: Bot1→Bot2 cross-fitting (sızıntı), ve form'lu veri zorunluluğu.

**K15 — Özellik kataloğu + şema doğrulaması.** T1: hız figürü+pist varyantı, form/fark, sınıf+HP,
mesafe/zemin uygunluğu, kulvar sapması (pist×mesafe×zemin×saha). T2: rolling jokey/antrenör+kombin,
DSLR/mola, ilk-kez ekipman, soyağacı. Çatı: nokta-anında (look-ahead yok) + saha-göreli + karmaşığı
modelin dışında türet. **Doğrulama (gerçek JSON):** going ✓ VAR (sonuçta CIM/KUM_TR), hava ✓ (HAVA),
ama **yarış-içi pozisyon ✗ YOK → koşu tarzı/tempo BLOKE** (handikabın güçlü silahı, elimizde değil);
at vücut ağırlığı ✗. Detay: `raporlar/faz0-veri-fizibilite.md`.

**K16 — Kazıma kapsamı: 2021-01-01 → bugün, sadece Türkiye pistleri. ONAYLANDI.**
Yerel (token=0): `kod/kazi.py` Windows'ta ham JSON indirir; ben özet okurum. 4 şüpheli pist
İNDİRİLİR (atın form geçmişi onları da içerebilir) ama eğitim/tahminde dışlanır.
Kaynaktan kazıma, eldeki CSV'nin join sorununu (Kapı #2 #4) native çözer + form/AGF/going ekler.

**K17 — Veri hattı kuruldu ve doğrulandı (kısmi veride test).**
- `kod/kazi.py`: yerli pist tespiti **GUN-dolu kuralıyla** (KEY tahmini YOK → DBAKIR vb. kısaltmalar
  otomatik yakalanır). Resumable, throttle'lı, stdlib-only.
- `kod/duzlestir.py`: ham full JSON → `veri/katilim.csv` (her satır = at-koşu). Sonuç tabanlı +
  programdan muhtemel/AGF/handikap merge. **Stabil ID'ler (at/jokey/antrenör KOD) → join sorunu yok.**
  Kapsama (kısmi test): ganyan_kapanış %98, muhtemel %97,5, going %99, handikap %86, irk native.
- **Bulgu:** Diyarbakır'ın KEY'i zamanla değişmiş (DBAKIR↔DIYARBAKIR) → `SEHIR_MAP` ile kanonikleştirildi.
  Full kazıma bitince `kazi_ozet.txt`'deki pist listesinden başka varyant var mı kontrol edilecek.

**K18 — Tam veri hazır (Kapı #2 AŞILDI).** Kazıma 2021-01-01..2026-06-29 tamam (1991 yarış günü,
8187 dosya, 0 hata). `duzlestir.py` → `veri/katilim.csv`: **341.244 at-koşu / 34.857 koşu.**
**Faz 1 kapsamı (İngiliz + izinli pist): 13.597 koşu, 122.018 at-koşu, 10.028 at, 457 jokey,
903 antrenör.** Yıllara dengeli (2021-2026) → walk-forward mümkün. ganyan %97,4 dolu.
Pist varyantı: sadece DBAKIR↔DIYARBAKIR (SEHIR_MAP ile çözüldü), başka yok.

**K19 — KARAR DENEYİ sonucu (Bot1+Bot2, walk-forward, test 2025-26).** `kod/model.py`.
- **α = +0,18** (fundamental ağırlığı; kill-criterion α≈0 TETİKLENMEDİ → fundamental gerçek sinyal ekliyor).
- Test log-loss: piyasa 1,7051 → **harman 1,6969** (harman piyasayı OOS yendi, kıl payı).
- **Değer bahsi (EV>1, kapanış/iyimser): 2 yılda 5 bahis, 0 isabet** → pozitif-EV neredeyse yok.
- **Verdict:** Yöntem geçerli (mimari çalışıyor) AMA edge %25,5 kesintiyi aşmaya yetmiyor (fersah fersah).
  Çekirdek özelliklerle ganyan piyasası dövülemiyor. Engel yapısal (verimli piyasa + yüksek kesinti).
- Açık: küçük edge bir nişte (saha boyu/sınıf/oran aralığı/maiden) yoğunlaşıyor olabilir → segment analizi.

**K20 — Segment analizi: NİŞ YOK. NİHAİ VERDICT: ganyan piyasası dövülemiyor.** `kod/segment.py`.
- EV-desil: en iyi desil −%20, en kötü −%70 (sinyal sıralı/gerçek) ama hiçbir bölge pozitif değil.
- Her segment (saha/sınıf/pist/oran) −%21…−%36. Beatable niş yok.
- Kontrarian (model≠favori): −%35,6 → fundamental fazla bilgi, piyasayı geçen overlay ÜRETMİYOR.
- **KARAR: Kâr amaçlı ganyan tahmini durduruldu.** Engel yapısal (verimli piyasa + ~%25 kesinti),
  yöntem/yürütme değil. Altyapı (5,5 yıl veri, kazi/duzlestir/ozellik/model hattı, leak-denetimli
  conditional-logit) sağlam ve yeniden kullanılabilir; sonuç dürüst bir TRUE NEGATIVE.

**K21 — PIVOT: egzotik (exacta) ilk testi. Yön doğru, kâr değil.** `kod/egzotik_ayikla.py` (temettü
çıkarma: exacta %99,4 dolu) + `kod/egzotik_test.py` (Harville + backtest). Exacta overlay ROI
**−%18,8** (ganyan −%28'den iyi → egzotik daha affedici, tez destekleniyor) ama hâlâ negatif.
Exacta efektif kesinti ~%26. **Kritik sınır:** bu test yalnızca BİZİM olasılık-overlay'imizi ölçer;
kalabalığın Harville'den YAPISAL SAPMASINI (profesyonel edge'in asıl kaynağı) ölçemez — TJK sadece
kazanan temettüyü yayınlıyor (will-pays yok). Sıradaki: kalabalığın kombinasyon-yapısal sapması
(model-free probe).

**K22 — Yapısal sapma probe'u: kalabalık egzotikte de VERİMLİ.** `kod/yapisal.py`. Favori-sıra
ızgarası (1.×2.): tüm hücreler −%18…−%56, hiçbiri +EV değil (ROI>−5% hücre: 0). Kanonik stratejiler
(test 2025-26): favori/saha −%26, saha/favori −%24, top2 box −%23, top3 box −%26, uzunşanslı −%31.
**Sonuç:** Exacta kalabalığı kombinasyonları kötü kurmuyor → sömürülebilir yapısal mispricing YOK.
Üç bağımsız negatif (ganyan/exacta-overlay/exacta-yapısal). **Tek test edilmemiş: Altılı (arkadaşın
asıl oyunu)** — 10^6 kombinasyonla yapısal verimsizliğin saklanabileceği TEK yer, ama doğrulaması
zor (variance/power). Exacta verimliliği Altılı için kötü işaret ama kesin değil.

**K23 — ALTILI testi: top-k spread derin negatif, model katkı YOK.** `kod/egzotik6_ayikla.py`
(4112 olay) + `kod/egzotik6_test.py`. Test 2025-26: en iyi top-k (k=2 piyasa) −%34, gerisi
−%47…−%90; eğitim −%79…−%96. **Model sırası piyasayı yenmiyor (k=2'de daha kötü)** → fundamental
model Altılı'ya da katkısız. Variance devasa (düşük güç) ama merkez açıkça ağır kayıp.
**NİHAİ VERDICT (5 bağımsız test): sistematik model-tabanlı yaklaşım hiçbir TJK havuzunu
dövemiyor.** Model istatistiksel olarak geçerli (α>0) ama hiçbir yerde kâra dönmüyor (verimli
piyasa + ~%25-40 kesinti). Arkadaşın edge'i fundamental-olasılık modeli DEĞİL → muhtemelen
Altılı kupon-kurma zanaati (banker/spread) + tacit/yerel bilgi + disiplin. Bu ayrı, sanat-ağırlıklı,
belirsiz bir proje; kurduğumuz şeyin devamı değil.

**K24 — "Sahte favori" yok AMA chalk-koşu canlı-non-favori sinyali GERÇEK (yön).** `kod/favori_test.py`.
Favoriler implied'ı tutturuyor/aşıyor (sahte-favori mekanizması yok). FAKAT favori çok güçlüyken
(implied %55-70) 2. tercih ROI −%12 (n=168) vs açık koşularda −%25…−%38 → kullanıcının/arkadaşın
"yüksek-AGF'de canlı alternatif" sezgisi veriyle DESTEKLENİYOR (yön doğru), ama hâlâ negatif (ganyan).
Model "2. favoriyi oyna"yı geçemiyor. Açık soru: bu chalk-non-favori sinyali EGZOTİK monetizasyonla
(favori kaybedince büyük temettü) +EV'ye dönüşür mü — hedefli Altılı testi (chalk ayakta non-favori
yay, açık ayakta banker).

**K25 — Chalk + favori-karşıtı egzotik: yine +EV YOK.** `kod/chalk_egzotik.py`. Güçlü-favori (implied
%55+, 662 koşu) koşularda favori-karşıtı exacta yapıları: hepsi negatif (tüm-veri), en iyi "2-3 box"
−%15,9; "favori yenildi" −%48,7 (favori çoğu kez kazandığı için ona karşı oynamak pahalı). Test-sütunu
+%111,9 = 27 koşuluk GÜRÜLTÜ (kullanılmadı). **SONUÇ: arkadaşın yöntemi (chalk + canlı non-favori +
egzotik) precise haliyle test edildi → sistematik/veri-türevli hiçbir versiyonu +EV vermiyor.** Edge,
veride OLMAYAN seçim/yargıda (tacit: hangi non-favori "canlı", durum seçimi). Model "2. favori"yi
geçemiyordu → live-non-favori'yi piyasadan iyi ayırt edemiyoruz. Tek veri-dürüst devam: arkadaşın
fiili karar kurallarını çıkarıp O kuralları test etmek (outcome'dan tersine türetilemez).

**K26 — Günlük araç (`gunluk.py`) inşası — ONAYLANDI.** Amaç: KÂR DEĞİL (6 test +EV yok; biliyoruz).
Amaç = çalışan sistem + öğrenme + firsthand kapanış + kalibre "matematik görüşü"nü analiz aracı olarak
kullanıcı yargısıyla birleştirmek. Tasarım iki kipli:
- `--sabah`: tam kart; her koşu **Bot1%** (oran-kör, kendi AGF'si) + **Bot2%** (harman) + kamu(AGF/oran)
  + **canlı-non-favori işareti** (Bot1% ≫ kamu%). Altılı planı 1. ayaktan ÖNCE bunun üstüne kurulur.
- `--kosu <no>`: o tek koşuyu güncel kadro/jokey/oranla **Bot1→Bot2 YENİDEN** koşar (çıkan at/jokey
  Bot1%'i de değiştirir: saha re-normalize + jokey feature; sadece Bot2 yetmez).
- **Canlı ≠ sızıntı:** tahmin anında gelecek yok; özellikler eğitimle AYNI nokta-anında mantıkla
  (`ozellik.py` fonksiyonları yeniden kullanılır). Canlı aslında daha AZ bilgi (ileri-ayak scratch'leri) →
  backtest'ten kötü olabilir, hile değil.
- İnşada İLK doğrulama: 5dk-kala canlı oran kaynağı (program JSON güncelleniyor mu yoksa
  `vhs.tjk.org/muhtemeller` feed mi) + scratch/jokey program'a yansıyor mu.

## 2026-06-30 — Günlük araç inşası

**K27 — `gunluk.py` KURULDU, canlı veriyle uçtan-uca doğrulandı.** `kod/gunluk.py`.
- **Canlı kaynak (K26 ilk doğrulama → TAMAM):** ayrı feed GEREKMİYOR. Tek endpoint
  `program/{Ymd}/full/{KEY}.json` her şeyi taşıyor: `GANYAN`=canlı muhtemel (koşulmamış koşuda
  bile dolu/güncel), `KOSMAZ`=çıkan at, `JOKEYKODU/ADI`=güncel jokey, `AGF1`+top-level `agf`
  bloğu `AGFMODTIME` ile (canlı). Bugün (2026-06-30) ANKARA'da test: 200, 8 koşu çekildi.
- **Mimari:** bugünün canlı program satırları geçmiş `katilim.csv`'ye eklenir → EĞİTİMLE AYNI
  `ozellik.build_features` (tek kaynak; `ozellik.py` `load_katilim`/`build_features`/`select_scope`
  fonksiyonlarına ayrıldı, çıktı **bit-aynı** = FEAT-md5 `7cddc980…` değişmedi) → Bot1 (oran-kör,
  eğitim ≤2024) + Bot2 (harman, holdout 2025). Bugüne uygulama: α=+0,24 γ=+0,94 (validated
  +0,18'e yakın). Tüm parsing/fit kodu mevcut modüllerden import (ayrışma yok).
- **KRİTİK HATA (bulundu+düzeltildi):** program JSON'da `KOD/JOKEYKODU/ANTRENORKODU` **string**;
  geçmiş int64. Düzeltmeden önce `groupby at_kod/jokey` join'i kırılıyordu → bugünün TÜM atları
  "geçmişsiz" → kariyer/form/hız/jokey özellikleri NÖTR (en güçlü sinyaller, fark +0,3…+0,5,
  ölüydü). `as_int()` ile çözüldü. Etki çarpıcı: STEEL ROCK Bot1 %31→%62, uzun-şanslı %16→%2.
- **SIZINTI/kontaminasyon testi GEÇTİ:** bugün eklenince geçmiş 118.171 satırın FEAT-md5'i
  referansla birebir aynı → bugün geçmişi bozmuyor, bugünün özellikleri yalnızca geçmişten
  (nokta-anında). "Canlı ≠ sızıntı" doğrulandı.
- **KAPSAM:** model yalnızca TR İngiliz; Arap/2yaş-maiden/küçük-saha "model kapsam dışı" (sadece
  kamu). 2yaş/az-geçmiş sahada "DÜŞÜK GÜVEN" satırı (Bot1 zayıf → kamuya yaslan).
- **DÜRÜSTLÜK (talimatname):** `>>CANLI` işareti (Bot1 ≫ kamu win-olasılığı) **bahis sinyali
  DEĞİL** — bunlar K20'de kontrarian= −%35 test edilen ayrışmalar; "kendi yargınla bak" işareti.
  Bot2 ≈ kamu (γ=0,94) → harman piyasayı çok az kaydırıyor (verimli-piyasa bulgusunun aynısı).
  Başlıkta "+EV değil, KÂR garantisi yok" uyarısı sabit.
- **Kullanım:** `python gunluk.py --pist ANKARA` (tam kart), `--kosu N` (tek koşu, güncel
  kadro/oranla yeniden çek), `--tarih YYYY-MM-DD`, argümansız → günün yerli pistleri.
- **Açık (sıradaki muhtemel adımlar):** (1) Arap modeli (Altılı ayaklarının yarısı Arap; şu an
  kapsam dışı) — ayrı eğitim/validasyon gerek; (2) `defter.py` kâğıt-ticaret defteri (tahminleri
  kaydet, ertesi gün sonuçla eşle, hipotetik P&L); (3) hız için param/feature cache (çalışma süresi
  ~15-20sn/koşu).

**K28 — `defter.py` KURULDU, tam döngü gerçek veriyle doğrulandı.** `kod/defter.py`.
- **Karar (kullanıcı "sen karar ver"):** ROI tally'leri **GANYAN** bazlı (model win-olasılığı
  üretir; plase modeli/temettüsü yok → plase-ROI eklemek = yeni model+veri = sistemi bozma riski).
  Plase sezgisi **bedava** karşılandı: varış pozisyonu zaten kayıtlı → özet model top-pick'in
  win/ilk-2/ilk-3 **isabet oranını** gösterir (plase modeli gerekmeden). Plase-ROI = ileride net
  kapsamlı adım (temettü çıkarımı + plase olasılık modeli).
- **Arkadaş-ekseni ÇIKARILDI** (kullanıcı: düzenli veri alamam). Kalan manuel girdi = *opsiyonel
  kendi seçimin* (`--secim`, düzensiz olabilir). Defter aksi halde tam otomatik.
- **Tasarım/komutlar:** `kaydet` (gunluk.hesapla'yı yeniden kullanır = tek kaynak; İngiliz-puanlı
  satırları upsert eder, çözülmüş satırları korur, eski secim'i korur), `sonucla` (sonuçlanmamışları
  `sonuclar/full` feed'inden eşler: varış + kapanış ganyan + kazandı), `ozet` (kalibrasyon + log-loss
  Bot2-vs-kamu + hipotetik ROI: model-top-pick / kamu-favorisi / >>CANLI / senin-seçimlerin +
  top-pick isabet). Defter: `veri/defter.csv`.
- **Gerçek-veri döngü testi (2026-06-30 ANKARA, koşular bitmişti):** kaydet 29 at → sonucla 29 →
  ozet çalıştı. İllüstrasyon (n=4 koşu, GÜRÜLTÜ): >>CANLI ROI −%39 (K20 kontrarian −%35 ile tutarlı),
  top-pick ilk-3 %100, log-loss Bot2 0,87 vs kamu 0,83. **Test defteri silindi (temiz başlangıç);
  gerçek kâğıt-ticaret yarıştan ÖNCE `kaydet` ile başlar.**
- **Hata (düzeltildi):** all-NaN `sonuclandi` sütunu float64 okunuyor → tarih str ataması pandas 3.0'da
  patlıyordu; `astype(object)` ile çözüldü.

**K29 — `takip.py` OTOMATİK TAKIP kuruldu (kullanıcı: "sabah başlat, gün boyu koşsun").** `kod/takip.py`.
- **Otomasyon düzeyi (kullanıcı seçti):** sabah-başlat, gün-boyu-koş (Windows Görev Zamanlayıcı şart
  değil). Sınır: PC yarış saatlerinde açık/uyanık olmalı (yerel script; uyurken tetiklenmez).
- **Kullanıcı gereksinimleri:** sadece İngiliz koşuları (Arap yok → Altılı tahmini yok); her koşuyu
  yarıştan ~5 dk kala CANLI oranla analiz; "kazanır dediği at" değil **tüm atları kendi AGF%'siyle
  sırala**. → `gunluk.kosu_yaz` `kosu_rapor`'a çevrildi (satır listesi döndürür, tek kaynak), sıralama
  **Bot2'ye** (=sistemin kendi AGF'si, "AGF%(sis)" sütunu) göre; tüm atlar + kamu oranı yan yana.
- **Akış:** sabah günün yerli pistleri + (yalnız İngiliz) koşu saatlerini çıkarır → her koşu SAAT−5dk'da
  canlı çekip raporlar (ekran + `raporlar/gunluk/{tarih}_{pist}.txt`) + `defter.yaz_tg(only_kosu=N)` ile
  deftere işler → tüm koşular bitince `defter.sonucla`. `--once` = vakti gelmişleri bir kez işle/çık
  (test + zamanlayıcı paterni). `--pist`/`--dk`/`--bekle` ayarlanır.
- **Doğrulama:** `--once` ANKARA 2026-06-30 → 5 İngiliz koşusu zamanlama planıyla listelendi, hepsi
  raporlandı (AGF%(sis) sıralı, kamu yan yana), deftere işlendi, sonucla çalıştı, rapor dosyası yazıldı.
  Test artıkları (defter.csv + rapor) silindi → temiz başlangıç.
- **Refaktor güvenli:** `kosu_rapor` değişikliği sonrası `gunluk.py` doğrulandı; `defter.kaydet`,
  `yaz_tg`+`kaydet` olarak ayrıldı (takip tek koşu yazabiliyor). Tüm araçlar tek `hesapla` çekirdeğini
  paylaşır (gunluk/defter/takip).
- **Hangi pistler:** `--pist`siz → o günün TÜM izinli yerli pistleri (yalnız İngiliz koşuları; bir
  günde 2-3 pist olabilir, hepsi saatlerine göre sıralı). **K4: 4 şüpheli pist (Elazığ/Diyarbakır/
  Urfa/Adana) takip'te de baştan dışlanır** (sonradan eklendi; önce planlanıp boşuna çekiliyordu).
- **Çalıştırma:** yarış günü sabahı `python kod/takip.py` (veya `--pist X`); terminal açık kalmalı.

**K30 — `defter.py goster` eklendi (kullanıcı: okunur, koşu-bazlı görünüm istedi).** `ozet` toplu-istatistik,
ham CSV 21-sütun → kullanıcı gün/koşu/at bazlı tahmin+sonuç istedi. `goster [--tarih] [--pist]`: her
koşuyu ayrı blok yazar — no, at, Bot1%, AGF%(sis)=Bot2, kamu%, oran, VARIS (gerçek varış), iz
(KAZANDI/F/CANLI) + "kazanan: X (model N., kamu M.)" satırı. Varış'a göre sıralı (kazanan üstte).
Doğrulama (2026-07-01 ISTANBUL, gerçek): 3 koşu okunur biçimde döküldü; canlı illüstrasyon — K2'de
favori (LIVE YOUR FREEDOM oran 1.30, F) 6. oldu, CANLI'lar hep geride, longshot DARK MONEY (15.75)
kazandı → CANLI/favori "bahis sinyali değil" bir kez daha somutlandı (n küçük, gürültü).

**K31 — HTML çıktı + çift-tık başlatıcılar (kullanıcı: PowerShell dışında erişim istedi).** `defter.html_yaz`
→ `raporlar/defter.html`: gün/koşu/at bazlı okunur tablo (kazanan satır yeşil, F/CANLI renkli, tarih
desc/koşu asc). `defter.py html` yazar+tarayıcıda açar; `sonucla` ve `takip` (her koşuda + gün sonu)
otomatik tazeler. İki `.bat` (kök klasörde, çift-tık, PowerShell'siz): **`baslat_takip.bat`** (gün boyu
takip) + **`sonuclari_goster.bat`** (sonucla + HTML aç). Kullanıcı sadece HTML'i çift-tıklar; oran/veri
`.venv` python ile arka planda. Gerçek veriyle üretildi/doğrulandı (2026-07-01 ISTANBUL, 3 koşu).

**K32 — Bot1 özellik genişletme, Batch 1: jokey/teçhizat değişim sinyalleri (kullanıcı: "gerekli
gördüğün her şeyi ekle, sen planla").** Önce veri denetimi (175k İngiliz satırı, 2021-2026):
- **Kritik ders (önce iddia edilen "veri hazır" YANLIŞ çıktı):** `at_eniyi` geçmişte **%0 dolu**
  (`ENIYIDERECE` sonuç JSON'unda yok, sadece programda) → ÖLÜ, kullanılamaz. Veri-denetimi olmadan
  eklenseydi sessizce boş/gürültü özellik olurdu.
- **Tasarım düzeltmesi:** Bot1 koşu-içi z-skor (conditional logit) → **koşu-sabiti alanlar** (going,
  sinif, mesafe, hava) doğrudan giremez (z=0). Ancak **atın kendi geçmişiyle etkileşim** olarak girer.
- **Eklenen (nokta-anında, shift(1), ikili 0/1, z'siz — disi/ilk_kosu deseni):** `jokey_degisim` (jokey
  önceki koşuya göre değişti mi), `taki_ilk` (ilk kez eklenen teçhizat kodu — kod semantiği
  varsayılmadan küme farkı). **`taki_kalkan` test edildi → ATILDI:** koşullu katsayı (+0.030) ham yönüne
  (−3.72pp) ters = bağımsız katkı ~0 (gürültü); 18. özellik Bot1'i +0.00004 kötüleştirdi.
- **Walk-forward holdout (eğit ≤2023, harman 2024, test 2025-26) log-loss:**
  Bot1 1.86119 → **1.85590** (−0.28%); jokey_degisim katsayı **−0.228** (6. en güçlü, jokey değişimi =
  daha az galibiyet; ham: %10.2 vs %13.8), taki_ilk −0.073. ALPHA +0.181 → +0.191.
- **DÜRÜST SONUÇ:** **Bot2 (harman = üretim çıktısı) delta = −0.00002 → SIFIR.** Piyasa bu sinyalleri
  zaten fiyatlıyor; +EV değişmedi (bir kez daha piyasa-verimliliği). Fayda yalnız **Bot1'in bağımsız
  (oran-kör) görüşünü** azıcık keskinleştirmek (→ CANLI karşılaştırması biraz daha anlamlı). Abartı yok.
- **Tek kaynak:** `model.py` kopya FEAT'i kaldırıldı → `from ozellik import FEAT`. Canlı yol
  (`gunluk.py`) yeni özelliklerle doğrulandı (ISTANBUL K6, çökme yok). FEAT 15 → **17**.
- **Sıradaki batch (açık):** Grup A (going/mesafe **uygunluk** = atın kendi geçmişi × koşul), Grup C
  (jokey×antrenör ikili oran). Aynı protokol: geçmezse atılır.

**K33 — Batch 2 (going/mesafe uygunluk) TEST EDİLDİ → EKLENMEDİ; özellik mühendisliği KAPATILDI
(ön-taahhütlü durma kuralı).** Kullanıcıyla anlaşma (K32 sonrası): Batch 2'yi **son** özellik testi
olarak çalıştır; Bot2 kıpırdamazsa (beklenen) yolu kapat, birikim moduna geç.
- **Eklenenler (nokta-anında, `zemin_galip_oran` deseni, z-skorlu):** `going_uygunluk` (atın going
  kovasındaki — going_agirlik 0=normal/>0=yumuşak — önceki galip oranı), `mesafe_uygunluk` (mesafe
  bandındaki önceki galip oranı). Doluluk %87.8 / %76.6.
- **Holdout (17 → 19):** Bot1 1.85590 → 1.85580 (−0.00010, Batch 1'in 50'de biri); **Bot2 1.69691 →
  1.69687 (−0.00004 → SIFIR)**; ALPHA/GAMMA değişmedi.
- **`mesafe_uygunluk_z`: katsayı −0.001 (~0)** — ham sinyal var (+0.196) ama kariyer/form ile
  eşdoğrusal → bağımsız katkı yok (taki_kalkan gibi).
- **`going_uygunluk_z`: kilitli modelde katsayı +0.073** ve **`zemin_galip_oran_z` +0.137 → +0.064'e
  düştü** (0.064+0.073=0.137). Yani going_uygunluk zemin'in ağırlığını böldü = **ayrı sinyal değil,
  aynı koşul-tercihinin daha ince partisyonu (eşdoğrusal).** (İzole 19-özellik testinde geçici +0.380
  görünmüştü — collinear kararsızlık; kilitli değer +0.073.)
- **KARAR:** ikisi de FEAT'e **eklenmedi**, model **17'de** (Batch 1 kilidi) kaldı. `build_features`'ta
  going/mesafe_uygunluk hesabı da kaldırıldı (yalnız `mes_kova` kalır, kulvar_skor için). `ozellikli.csv`
  yeniden üretildi, `model.py` 17-özellik teyit (Bot1 1.8559 / Bot2 1.6969), canlı yol (ISTANBUL K6) aynı.
- **SONUÇ (kapanış):** 6 önceki test + Batch 1 (bariz sinyaller) + Batch 2 (incelikli etkileşimler) —
  **hiçbir kamuya-açık-veri özelliği Bot2'yi (üretim çıktısı) oynatmıyor.** Kenar veri-mühendisliğinde
  değil. **Özellik mühendisliği kapatıldı.** Enerji → asıl darboğaz: **canlı kâğıt-ticaret geçmişi
  biriktirmek** (CANLI/ayrışma işaretlerinin gerçek değeri ancak haftalarca gerçek sonuçla ölçülür).

**K34 — HATA (bulundu+düzeltildi): `takip.py` sabah "izinli takip edilecek koşu yok" diyordu.**
Kullanıcı 2026-07-02 Ankara yarışları varken takip'i çalıştırdı, boş döndü. Kök neden: `yerli_pistler()`
günün pist listesini **sonuçlar** index'inden (`sonuclar/{ymd}/yarislar.json`) çekiyordu — ama o feed'de
yarış GÜNÜ (GUN) **akşam sonuçlar dolunca** yazılıyor; sabah GUN boş → `GUN` filtresi tüm pistleri eledi
→ `[]`. Yani tam "sabah başlat" senaryosunda (aracın asıl kullanımı) bozuktu.
- **Düzeltme:** kaynak **program** index'ine çevrildi (`program/{ymd}/yarislar.json`) — sabah da dolu.
  TR pistlerde `GUN` sayısal (ANKARA=32, KOCAELI=17), yabancı pistlerde (VAAL/LONGCHAMP/KEMPTON…) `GUN`=None
  → mevcut GUN filtresi TR/yabancıyı zaten doğru ayırıyordu; yalnız endpoint yanlıştı. Tek satır + docstring.
- **Doğrulama (salt-okunur, deftere yazmadan):** yerli_pistler → ANKARA + KOCAELI; takip programı **8
  İngiliz koşusu** (ANKARA 1/3/5/8 + KOCAELI 1/2/3/7) saatleriyle listelendi. `gunluk.py` argümansız
  liste de artık sabah çalışır (aynı fonksiyon). Regresyon yok: fonksiyon yalnız "bugünün pistleri"
  keşfinde kullanılıyor; geçmiş sonuçlama `sonuclar/full`'u ayrı kullanır.

## 2026-07-02 (gece) — Dış inceleme + revizyon paketi (gerçek-para bağlamı)

Bağlam: sistemin baştan sona kod incelemesi yapıldı; kullanıcı iki şeyi netledi: (1) defter/takip
hem öğrenme aracı hem **CANLI-işareti ölçüm deneyi**; (2) **gerçek parayla bahis VAR.** Bu ikisi
önceliği belirledi: deney bütünlüğü + gerçek P&L ölçümü. Tüm değişiklikler tek gecede, paket paket
commit'lendi; değişiklik ÖNCESİ hal `BASELINE` commit'inde.

**K35 — Sürüm kontrolü + yedek + bağımlılık pinleme.** `at/` git deposu oldu (önce değildi; tek disk,
tek kopya — KARARLAR.md dahil). `.gitignore`: `.venv`, `veri/ham` (1.1 GB), katilim/ozellikli.csv
(yeniden üretilebilir) dışarıda; kod+raporlar+defter+küçük CSV'ler içeride. `requirements.txt`
(pip freeze; Python 3.14.6, pandas 3.0.4, numpy 2.5.0, scipy 1.18.0).
*AÇIK GÖREV (kullanıcı):* `veri/ham`ın tek seferlik HARİCİ kopyası (USB/bulut) — kazıma tekrarı
~2 saat AMA arşivin açık kalacağının garantisi yok; git bunu KAPSAMIYOR.

**K36 — Deney bütünlüğü paketi.** İnceleme 3 sessiz bozulma yolu buldu; üçü de kapatıldı:
- **Nokta-anında dt-guard (`gunluk.hesapla`):** arşivden, tahmin gününden İTİBAREN tüm satırlar
  düşülür. Tek kural iki sızıntıyı keser: (a) aynı koşu arşivde de varsa (geçmiş `--tarih` /
  gün-içi tazeleme) `shift(1)` mekaniği koşunun SONUCUNU bugünkü özelliklere taşırdı;
  (b) geçmiş-tarihli çalıştırmada o günden sonraki koşular özelliklere girerdi. Normal kullanımda
  (arşiv < bugün) hiçbir satır düşmez → davranış birebir aynı (K27 kontaminasyon özelliği korunur).
- **Bayatlık uyarısı:** `hesapla` arşiv-son-gününü basar; >3 gün eskiyse açık uyarı. (İnceleme anında
  arşiv 2026-06-29'da donmuştu = son 3 günün koşuları form/kariyer özelliklerine girmiyordu, hiçbir
  araç uyarmıyordu.)
- **Veri tazeleme protokolü:** `kazi.py --guncelle` (arşivdeki son günden bugüne; sınır günü yeniden
  indirilir — gün-içi kısmi inmiş olabilir) + `kod/guncelle.py` (kazi + yeni dosya indiyse duzlestir;
  yoksa hızlı geçer). `baslat_takip.bat` artık önce guncelle sonra takip çalıştırır. DİKKAT: guncelle
  takip ÇALIŞIRKEN elle çalıştırılmaz (katilim.csv yazma/okuma çakışması).
- **Defter ileriye-dönüklük koruması (`defter.yaz_tg`):** posta saati geçmiş koşu deftere yazılamaz
  (3 dk tolerans). Önceden takip'i öğlen başlatmak sabahki koşuları yarış-SONRASI oranla "tahmin"
  diye kaydederdi → deney verisi kirlenirdi. `takip.py` de geçmiş koşuyu hiç işlemez.

**K37 — GERÇEK-BAHİS DEFTERİ (fiili kuponlar; kâğıt-defterden AYRI dosya `veri/bahisler.csv`).**
Gerekçe: 6 test "model kesintiyi aşamıyor" dedi; test edilmemiş tek şey KULLANICININ YARGISI.
Gerçek para oynandığına göre ölçülmesi gereken soru: "senin seçimlerin kesintiyi aşıyor mu?"
Hipotetik flat-1-birim tablosu bunu ölçemez (miktar/tür/kupon farkı).
- Komutlar: `defter.py bahis --pist X --kosu N --tur ganyan --secim 3 --miktar 50` (kupon başına bir
  satır; altılı vb. için koşu=ilk ayak, seçim serbest metin) + `bahis-sonuc --id N --getiri X`
  (0=kaybetti). Çift-tık: **`bahis_gir.bat`**.
- Ganyan tek-at kuponları `sonucla`da OTOMATİK sonuçlanır (kazandı → miktar × kapanış-ganyan).
  Diğer türler elle (TJK plase/egzotik temettü çıkarımı ayrı iş; şimdilik kapsam dışı).
- `ozet` + `defter.html`: gerçek P&L bölümü (toplam + tür bazlı ROI; n<30'da "sonuç çıkarma" uyarısı).
- **ÖN-TAAHHÜTLÜ DEĞERLENDİRME KURALI (TASLAK — sayılar kullanıcı onayı bekliyor):**
  (1) Aylık gerçek-bahis bütçe tavanı: ___ TL (kaybı taşınabilir "eğlence bütçesi" olarak kullanıcı
  belirler; sistem tavana uyumu ölçer, karar vermez). (2) Değerlendirme noktası: **n≥100 sonuçlanmış
  kupon VE ≥3 ay** birikince gerçek ROI + güven aralığı hesaplanır; %95 GA üst sınırı < 0 ise
  (kayıp istatistiksel olarak net) gerçek para DURUR, kâğıt devam eder. Kural sonuç biriktikten
  sonra yazılamaz (hindsight); bu yüzden ŞİMDİ, veri birikmeden taahhüt ediliyor.

**K38 — `par` tablosu look-ahead DÜZELTİLDİ + etkisi ölçüldü.** Docstring "par ≤2024 eğitim
yıllarından" diyordu; kod TÜM yıllardan hesaplıyordu → 2025-26 test döneminin galip zamanları par'a,
oradan hız özelliklerine sızıyordu. Ölçüm: 151 ortak hücrede medyan |fark| 0,185 sn, p90 0,81 sn,
%18,5 hücre >0,5 sn. Düzeltme öncesi baseline BİREBİR yeniden üretildi (Bot1 1,8559 / Bot2 1,6969 /
α=+0,191), sonra tek değişiklikle A/B:
- Bot1 1,8559 → **1,8566** (sızıntı Bot1'i hafifçe suni parlatıyormuş — yön beklenen).
- **Bot2 1,6969 → 1,6970 (değişim yok), α +0,191 → +0,190, γ +0,975.**
- **Sonuç: K19-K33 verdiktleri GEÇERLİ** (sızıntı ölçülebilir ama sonuçları değiştirmeyecek
  büyüklükte). Artık kod ile docstring tutarlı; test dönemi temiz. `ozellikli.csv` yeniden üretildi
  (eski FEAT-md5 referansları bilinçli olarak geçersiz). NOT: `kulvar_skor` ≤2024 tablosu 2024
  α-fit'inde hâlâ in-sample (bilinen, küçük, K38'de belgelendi; par ile aynı kurala getirildi).
- **Ölçüm verisi notu:** A/B, tazeleme ÖNCESİ arşivle (2021-01-01..2026-06-29) yapıldı — tek
  değişken par kuralı olsun diye. Aynı gece K36 tazelemesi arşivi 2026-07-02'ye getirdi;
  bundan sonraki `model.py` koşuları bu ÜÇÜNCÜ sebeple de (veri arttı) hafif farklı çıkar.

**K39 — Dayanıklılık (gün-boyu koşan süreç + parse tutarlılığı).**
- `takip.py`: defter yazımı try içinde (defter.csv Excel'de açıkken PermissionError GÜNÜ ÇÖKERTMESİN);
  geçici ağ hatasında koşu posta saatine kadar döngüde yeniden denenir (önceden ilk hata kalıcı
  "atlandi" idi); gün-sonu `sonucla` son post+40 dk'ya ertelendi (önceden son koşudan ~5 dk ÖNCE
  çalışıyordu → hep boş dönüyordu).
- `defter.sonucla` GANYAN parse → `duzlestir.vir_float` (tek kaynak). Feed'in KENDİ İÇİNDE format
  karışık (GANYAN='9,95' virgül, AGF1='9.27' nokta — 2026-06-29 BURSA'dan doğrulandı); eski elle
  parse nokta-ondalık gelirse 3.55→355 yapardı.
- `>>CANLI` bayrağı tek fonksiyona indi (`gunluk.canli_seri`; kosu_rapor + defter.yaz_tg kullanır) —
  önceden iki yerde ayrı kodluydu, eşik değişse sessizce ayrışırlardı.
- Doğrulama: 12 birim-test (scratch defter/bahis dosyalarıyla; gerçek deftere dokunulmadı) — hepsi
  geçti; canli_seri eski mantıkla birebir aynı çıktı verdi.

## 2026-07-03 — K37 kuralı onaylandı

**K40 — K37 ön-taahhütlü değerlendirme kuralı ONAYLANDI (kullanıcı, 2026-07-03) ve KODA BAĞLANDI.**
- Kesinleşen kural: **n≥100 sonuçlanmış kupon VE ≥90 gün** dolunca `defter.py ozet` gerçek-ROI
  %95 güven aralığını hesaplar (bootstrap 10k, kupon bazlı — değişken miktarlara dayanıklı);
  **GA üst sınırı < 0 ise "GERÇEK PARA DUR, kâğıt devam" verdikti basılır.** Eşik dolana kadar
  her özet ilerlemeyi gösterir ("kupon X/100, gün Y/90"). Kural kendini uygular; unutulamaz.
- Doğrulama: sentetik eşik-dolu kayıp profili (n=120, ROI −%32,5) → GA [−%55,0, −%10,0] →
  tetiklendi; küçük n → ilerleme satırı. İkisi de scratch dosyalarla test edildi.
- **AÇIK: aylık bütçe tavanı (TL) hâlâ kullanıcıda** — sayı gelince buraya yazılacak; sistem
  tavana uyumu ölçer, karar vermez (talimatname m.7). *(→ K41'de geldi, kapandı.)*

**K41 — Bütçe tavanı belirlendi (kullanıcı, 2026-07-03) + koda bağlandı; harici yedek alındı.**
- **Kapsam/tavan (kullanıcı):** ilk hedef İngiliz koşularında GANYAN. Tavan: **kupon/koşu başına
  ≤100 TL, gün başına ≤300 TL.** (Aylık tavan yerine kupon+gün tavanı — kullanıcının tercihi.)
- **Koda bağlandı (ölçer, ENGELLEMEZ):** `bahis` komutu kayıt anında üç kontrol yapar (kupon>100 /
  koşu-toplamı>100 / gün-toplamı>300 → UYARI basar); `ozet` kalıcı uyum satırı gösterir
  ("K41 tavan uyumu: kupon>100TL: X | kosu-toplami>100TL: Y | gun>300TL: Z"). K37 ilerleme/GA
  satırı artık sonuçlanmış kupon olmasa da görünür (girinti düzeltmesi).
- Doğrulama: 4 senaryoluk scratch testi — üç uyarı türü + uyum satırı + "kupon 0/100" ilerlemesi.
- **Harici yedek:** tüm proje (ham 1.1 GB + kod + git geçmişi + defter; .venv ve türetilmiş
  katilim/ozellikli.csv hariç) tek dosyaya arşivlendi: `Desktop/at-yedek-YYYY-AA-GG.zip`.
  İlk deneme GNU tar'ın .zip uzantısını sessizce yok sayıp DÜZ TAR üretmesiyle bozuktu (magic-byte
  kontrolüyle yakalandı) → Windows bsdtar ile gerçek zip. *Kullanıcı görevi: bu TEK dosyayı Google
  Drive'a (drive.google.com → sürükle-bırak; hesap: gmail) veya USB'ye kopyala. Öneri: Drive
  (ev dışı kopya > aynı masadaki USB). Tazeleme: büyük kazıma sonrası veya ~ayda bir yenisi.*

**K42 — 12 HAFTALIK ÖN-KAYITLI PAPER TEST (kullanıcı önerdi, tasarım revizyonla ONAYLANDI).**
Kullanıcının önerisi: haftalık 3000 TL kâğıt bütçe, İngiliz ganyan+plase, kayıt alınsın.
İki düzeltmeyle kabul: (1) "asistanın tavsiyesi" diye serbest bir bacak YOK — önerilebilecek her
kural model türevi ve 6 testte negatif; onun yerine stratejiler ÖN-KAYITLA sabitlendi (K33/K37
kültürü). (2) Amaç kâr değil (beklentiler negatif, aşağıda): canlı hattın kalibrasyonunu doğrulamak
+ PLASE'nin ilk ölçümü + kullanıcının gerçek kuponlarına (K37) mekanik benchmark.
- **Ön-analiz (`kod/plase_test.py`, `kod/temettu.py`):** PLASE temettüsü feed'de VAR
  (`BAHISLER_TR`), 5,5 yılda %57,5 koşuda havuz mevcut ve **yalnız 7+ atlı sahalarda**. İlk plase
  backtest'i (test 2025-26, model.py ile aynı walk-forward): **top-pick plase −%12,5, favori plase
  −%14,0** (isabet ~%53) — negatif ama ganyan'ın (−%28) yarısı; sürpriz yok, +EV yok.
- **ÖN-KAYIT (2026-07-04 → 2026-09-25, 12 hafta; kurallar test boyunca DEĞİŞMEZ):**
  kupon **15 TL** flat (25 değil: CANLI koşuların ~%80'inde var → 25 TL'de hafta ~4.400 TL olur,
  3000 bütçe kuralı hafta sonlarını sistematik keserdi = örneklem yanlılığı; 15 TL → ~2.600 TL/hafta).
  Hafta (ISO) bütçesi 3000 TL; dolarsa yeni kupon açılmaz (öncelik S1→S5). Koşu başına en fazla
  1'er kupon: **S1** top-pick ganyan / **S2** top-pick plase (yalnız saha≥7) / **S3** favori ganyan /
  **S4** favori plase (saha≥7) / **S5** CANLI ganyan (canli_seri; birden çoksa Bot1 max).
  Kayıt anı = takip tetiği (~5 dk kala, ileriye-dönük). Ödeme: ganyan=kapanış; plase=temettü;
  at koşmadı / havuz yok → İPTAL (iade). **Beklentiler (geçmiş-veri):** S1 −%28,0 / S3 −%28,7 /
  S5 −%33,6 / S2 −%12,5 / S4 −%14,0.
- **Ayrı arayüz (kullanıcı şartı):** `veri/paper_kupon.csv` + `raporlar/paper.html` +
  `paper_goster.bat` — defter.csv/bahisler.csv/defter.html'e DOKUNMAZ. takip/sonucla entegrasyonu
  try-korumalı (paper hatası canlı takibi asla bozamaz). 19 birim-test geçti (üretim/dedup/bütçe/
  saha<7/kazandı-plase-iptal sonuçlama/HTML).
- **12. hafta sonunda:** strateji bazlı ROI + GA raporu; canlı-vs-backtest kalibrasyon
  karşılaştırması; sonuç ne olursa olsun kural ortasında değişmez.

## 2026-07-05 — Otomatik başlatma (K29 revizyonu)

**K43 — Takip artık Görev Zamanlayıcı ile OTOMATİK başlar (günlük 10:30).** Vaka: 5 Temmuz'da
PC açık olmasına rağmen takip 18:38'e kadar başlatılmadı → günün İngiliz koşuları izlenmedi,
paper test o günü boş geçti (3-4 Temmuz normal çalışmıştı; sistem arızası değil, K29'un
"sabah elle çift-tık" tasarımı insan hafızasına dayanıyordu ve bir unutma tam gün kaybettirdi).
- **Çözüm:** Windows Görev Zamanlayıcı görevi **"TJK Takip"** — her gün 10:30'da
  `baslat_takip.bat` (StartWhenAvailable: saat kaçırıldıysa fırsat bulunca; WakeToRun: PC
  uykudaysa uyandır; 15 saat süre sınırı; oturum açıkken görünür pencere). Koşu olmayan gün
  "izinli pist yok" yazıp kapanır — pencere günün durumunu gösterir.
- **Tek-instans kilidi (`takip.tek_instans`, msvcrt):** zamanlanmış görev + elle başlatma
  çakışırsa ikinci kopya "zaten çalışıyor" deyip çıkar (iki kopya aynı CSV'lere yazamaz).
  Kilit dosyası süreç ölünce OS tarafından bırakılır — bayat kilit olmaz. `veri/takip.kilit`
  git dışı.
- Elle başlatma hâlâ mümkün (erken başlamak istersen çift-tık; kilit korur). Görevi kaldırmak:
  PowerShell `Unregister-ScheduledTask -TaskName 'TJK Takip'`; saatini değiştirmek: Görev
  Zamanlayıcı arayüzü veya bana söyle.
- **5 Temmuz bilançosu:** sabah/öğlen koşuları geri getirilemez (geçmiş-koşu koruması doğru
  şekilde reddeder — tasarım gereği); kullanıcının 18:38'de başlattığı kopya akşam İZMİR 7
  (21:00) ve İZMİR 8'i (21:30) normal izler. Paper testte 5 Temmuz eksik gün olarak kalır
  (veri kirliliği değil, eksik örneklem).

**K44 — BENTER SON DOSYA: sıra-bilgili model (Plackett-Luce) → plase overlay testi = NEGATİF;
Benter'den alınacak şey kalmadı.** `kod/plase_model.py` (offline; canlı sisteme dokunmadı).
Soru: 6 negatif testin kapsamadığı tek cep — "plase-olasılık modeli plase havuzunda (en az kötü
havuz, −%12,5 baz) overlay bulur mu?" Ön-taahhütlü kill-first tasarım: önce model-kalitesi,
geçerse ekonomi.
- **Benter'in tekniği kendi başına ÇALIŞIYOR:** sıra-patlatma (k=1→3, eğit ≤2023) 2024 holdout
  plase log-loss'unu düzenli iyileştirdi (0,55462 → 0,55019; k=3 seçildi). Yani "ilk sıraları da
  kullan" fikri modeli gerçekten keskinleştiriyor — yöntem doğrulandı.
- **AMA KILL TESTİ (test 2025-26, 2.898 koşu, saha≥7): harman plase'de piyasayı GEÇMİYOR.**
  Plase-top3 log-loss: piyasa(devig ganyan→Harville) 0,50647; oran-kör model 0,53321;
  harman 0,50765 (piyasadan +0,00118 KÖTÜ). Kalabalığın ganyan oranları, plase sıralamasını
  bizim sıra-bilgili modelimizin katabileceğinden daha iyi fiyatlıyor. Ön-taahhüt gereği
  ekonomi hesabına hiç girilmedi.
- **VERDICT: Benter dosyası veriyle KAPANDI.** Çekirdek (Bot1+Bot2) zaten Benter'dendi;
  egzotik çarpanı K21-K23'te, plase cebi K44'te negatif; yarış-içi veri TJK'da yok (K15/K44
  yeniden doğrulandı). Kalan tek şey birikimdi ve o zaten işliyor (K37 gerçek-bahis, K42 paper).
  7. bağımsız negatif — engel yöntem değil, yapı (verimli piyasa + ~%25 kesinti).

## 2026-07-06 — K43 hiç çalışmamış: pil kısıtı

**K45 — HATA (bulundu+düzeltildi): "TJK Takip" görevi kurulduğundan beri HİÇ çalışmamış;
6 Temmuz tamamen kayıp (kurtarılamaz — Bursa'nın tek İngiliz kartı 17:00'de bitti, kontrol
18:36'da yapıldı).** Kök neden: makine laptop; Windows zamanlanmış görevleri varsayılan olarak
**`DisallowStartIfOnBatteries=True`** ile oluşturulur. K43 kurulurken bu ayar fark edilmedi.
Makine şarjda değilken (dün ve bugün — `Win32_Battery` ile doğrulandı, BatteryStatus=discharging)
10:30 tetiği sessizce atlandı: `StartWhenAvailable`/`WakeToRun` yalnız "saat kaçtı" durumunu
kurtarır, "güç kaynağı uygun değil" koşulunu görmezden gelmez. `Get-ScheduledTaskInfo` bunu
`LastRunTime: 30.11.1999` (= hiç çalışmadı) ile açıkça gösteriyordu — K43'te bu doğrulanmamıştı.
- **Düzeltme:** `DisallowStartIfOnBatteries=False`, `StopIfGoingOnBatteries=False` (PowerShell
  `Set-ScheduledTask`). Artık pilde de şarjda da 10:30'da çalışır.
- **Ders (K43'e ek doğrulama eksikliği):** görev kurulduktan sonra ertesi gün fiilen çalıştığı
  TEYİT EDİLMEMİŞTİ — sadece `Register-ScheduledTask` başarılı döndü diye "kuruldu" varsayıldı.
  Bundan sonra otomasyon kurulumlarında ilk gerçek tetikten sonra `LastRunTime`/`LastTaskResult`
  kontrolü zorunlu adım.
- **Kayıp:** 6 Temmuz — kâğıt defter, paper test, gerçek-bahis (varsa) o gün için boş. Veri
  kirliliği değil, eksik örneklem (K36/K42 ile aynı sınıf). 7 Temmuz'dan itibaren beklenmeli.

**K46 — ARAP GENİŞLETMESİ: karar-deneyi + canlı entegrasyon (kullanıcı onayladı; "tüm bahis
türleri" önerisi REDDEDİLDİ).** Kullanıcı iki genişletme önerdi: (1) Arap atları, (2) TJK'nın
tüm bahis türleri. (2) veriye dayalı reddedildi: türlerin tümü ya doğrudan test edildi (ganyan/
plase/exacta/Altılı/chalk — 8 negatif) ya da aynı win-olasılıklarının kombinatorik türevi; havuzlar
daha sığ, kesintiler daha yüksek → "genişletme" değil, negatif sonucun 10 tür × makine maliyetiyle
çoğaltılması olur. İstisna (koşullu, açık): Arap modeli kalibre çıkarsa Altılı ayak-bazlı
olasılık GÖRÜNTÜLEMESİ (bahis önerisi değil) ileride düşünülebilir.
- **Karar-deneyi (`kod/arap_test.py`, K19 protokolünün aynısı; kapsam Arap + izinli pist):**
  11.073 koşu / 110.903 at-koşu (yıllara dengeli, ganyan %97,9). Kulvar tablosu Arap'a özgü kuruldu.
  Sonuç: **α = +0,217** (kill TETİKLENMEDİ; İngiliz +0,19'a paralel), test log-loss piyasa 1,8565 →
  harman **1,8504** (OOS geçiyor). İlk-koşu payı %6,0. Katsayı yapısı İngiliz'e benzer
  (ilk_kosu −0,98, handikap +0,45, disi −0,44 — disi Arap'ta 2× güçlü).
- **AMA ekonomi daha sert:** Arap ganyan overround medyan **1,441 → ~%30,6 kesinti** (İngiliz
  ~%25,5); favori-oyna −%29,8. EV>1,00 taramasındaki "+%100 ROI" **14 bahislik GÜRÜLTÜ** (K25'teki
  +%111,9 gibi — kullanılmaz). **Arap modeli ANALİZ katmanıdır; +EV iddiası yok (9. veri noktası:
  Arap havuzu da verimli + daha yüksek kesinti).**
- **Canlı entegrasyon (İngiliz yolu BİT-AYNI korunarak):**
  - `ozellik.py`: kulvar tablosu ırk-farkındalıklı (her ırk kendi eğitim koşularından; merge
    anahtarına irk eklendi). REGRESYON KANITI: eski kod + yeni kod ile üretilen `ozellikli.csv`
    **md5 birebir aynı** (02e144f3…). `select_scope(d, irk=...)` parametreli (varsayılan İngiliz).
  - `gunluk.hesapla`: iki ayrı model (İngiliz + Arap; ayrı Bot1/Bot2 eğitimi) — kartta o ırktan
    koşu yoksa fit atlanır. Başlık span iki modelin α/γ'sını gösterir. Çalışma süresi karma
    kartlarda ~2× (kabul edildi).
  - `takip.py`: program filtresi İngiliz+Arap; `defter.py`: her iki ırkı kaydeder, özette ırk
    kırılımı satırı.
  - **K42 ÖN-KAYIT KORUMASI:** `paper.kupon_uret` Arap koşusunu KOD SEVİYESİNDE reddeder
    (test edildi: Arap → 0 kupon, İngiliz → normal) — 12 haftalık test İngiliz-kilitli, kural
    ortası kapsam değişikliği imkânsız.

## 2026-07-18 — Durumsuz takip (K49)

**K49 — TAKİP DURUMSUZ GEÇİŞ MODELİNE GEÇTİ (kullanıcı onayladı).** Kök sorun: "bütün gün
yaşamak zorunda olan tek süreç" laptop ortamında yapısal kırılgandı — 13 günde 4 olay
(5-6 Tem pil, 16 Tem gündüz ölümü: 9 koşu, 17 Tem kısa ölüm). Bekçi "başladı mı"yı görüyordu,
"yaşıyor mu"yu göremiyordu.
- **Yeni model:** "TJK Takip" görevi **her 15 dk'da bir** (10:30 + 12 saat, pythonw, 30 dk
  limit) `takip.py`'yi çalıştırır; her çağrı DURUMSUZ tek geçiş: vadesi gelen koşuları işler,
  durumu **`veri/takip_gecis.txt`** marker dosyasına yazar (bitti/gecmis/atlandi/YOK/
  GUNCELLE/SONUCLA), çıkar. Süreç ölümü kavramı kalktı: geçiş çökse/uyku girse sonraki geçiş
  kaldığı yerden sürer. Günün ilk geçişi arşivi günceller (3 başarısız denemede vazgeç → gün
  bayat arşivle sürer, hesapla uyarır). Gün sonu sonucla: tüm koşular mühürlü + son post+40dk.
  K36/K39/K42 korumaları aynen (isle_kosu değişmedi). Log: `veri/takip_log.txt` (pythonw sessiz).
- **Bekçi yeniden tanımlandı:** kalp atışı HER geçişte tazelenir; bekçi (10:40'tan itibaren
  2 saatte bir) "son 45 dk nabız var mı" bakar — 16-Tem-tipi gündüz ölümü artık en geç 2 saatte
  görünür uyarıya döner. Pencere dışında (22:30-10:40) sessiz.
- **`baslat_takip.bat` = elle tek geçiş** (kurtarma aracı); rutinde gerek yok. Sistem artık
  K48'in gerektirdiği gibi sıfır-insan-müdahale ile 25 Eylül'e kadar birikebilir.
- **Doğrulama:** 10 marker-akış birim-testi (YOK kararlılığı, mühür/tekrar-işlememe, retry
  hakkı, atlandi, SONUCLA-bir-kez) — tümü geçti; görev tetikleri PT15M/PT12H doğrulandı;
  bekçi ok-yolu smoke. İlk gerçek gün (19 Tem) ayrıca kontrol edilecek (K45 dersi).
- Eski sürekli-döngü kodu kaldırıldı (`--once/--bekle` uyumluluk no-op'u kaldı). 18 Tem akşamı
  eski-stil süreç günü bitirdi; yeni model 19 Tem 10:30'da devraldı.

**K50 — Deney verisinin haftalık otomatik commit'i (kullanıcı onayladı).** defter.csv +
paper_kupon.csv (+ günlük raporlar/HTML'ler; bahisler.csv oluşursa o da) tek kopya diskteydi
(zip yedek manuel/seyrek). `kod/veri_commit.py` + **"TJK Veri Commit"** görevi (pazartesi 22:45):
değişiklik varsa "veri: deney kaydı <tarih> (otomatik, K50)" commit'i; yoksa sessiz (idempotent —
test edildi). İlk yetişme commit'i 18 Tem: 13 dosya, 2 haftalık birikim (02fcc8e). Bozulma artık
en fazla 1 haftalık veriyi riske atar.

## 2026-07-19 — Carryover (devir) kazıyıcısı — araştırma, sisteme bağlantısız

**K51 — `kod/devir_ayikla.py`: TJK'nın tüm çok-ayaklı havuzlarında carryover (devir) olaylarını
ham veriden çıkaran YEREL script (token=0; ham JSON zaten inik, ağ/LLM çağrısı yok).** Bağlam:
Altılı kupon teorisi tartışılırken (sistemden bağımsız soru) carryover'ın beceriden bağımsız
en güçlü +EV kaldıracı olduğu ortaya çıktı (Benter 2006) — TR'de ne sıklıkla oluştuğu hiç
ölçülmemişti. Kaynak metin kalıbı: `"<TÜR>(<kombo>): Bilen çıkmamıştır, <TUTAR> TL devretmiştir."`
- **Bulunan+düzeltilen hata:** ilk regex, bahis-türü adını rakam+harf+boşluk olarak gevşek
  yakalıyordu; bir önceki tutarın virgül-sonrası kuyruğu ("60TL","90TL"...) sonraki adın başına
  sızıyordu (virgül yasak olduğundan en erken eşleşme tam sızıntı noktasında başlıyordu).
  Sonuç: 33 "Altılı" olayının **9'u aslında 7'Lİ GANYAN** idi (gevşek "6 içeriyor mu" filtresi
  yakalamıştı). Düzeltme: sızıntı `^\d+TL\s*` kalıbıyla temizlendi + Altılı filtresi TAM
  önek eşleşmesine (`6'LI GANYAN` ile başlamalı) sıkılaştırıldı. Doğru sayı: **24 Altılı devir
  olayı** (2021-2026), kombo alanları elle doğrulandı (6 at, temiz).
- **Sonuç (izinli-pist kapsamı, projenin asıl ilgi alanı):** 4.136 toplam Altılı çekilişinde
  (4.112 kazanan çıktı + 24 devretti) devir sıklığı **%0,6** — nadir ama büyüklüğü çarpıcı
  (medyan 6,16M TL, en büyüğü 24,86M TL — 01/11/2025 ANKARA). **7 olay izinli (proje-kapsamı)
  pistte:** BURSA×4, İSTANBUL×1, İZMİR×1, ANKARA×1 (2021-2026). Geri kalan 17/24 (%71)
  **K4'ün 4 şüpheli pistinde** (SANLIURFA×8, DIYARBAKIR×5+1, ELAZIG×2) — ⚠ HİPOTEZ (nedensellik
  kurulmadı, pist-bazlı devir ORANI için payda/toplam-çekiliş-sayısı hesaplanmadı; sadece HAM
  SAYI çarpıcı bir korelasyon, K4'ün şike-şüphesi gerekçesiyle örtüşüyor ama kanıt değil).
- **Sisteme bağlantı YOK:** takip/gunluk/paper/defter hiçbiri bu script'i çağırmıyor, hiçbir
  canlı davranışı etkilemiyor. Saf araştırma çıktısı: `veri/devir.csv`.
- **Açık (yapılmadı, istenirse):** carryover gününün ERTESİ (havuzun çözüldüğü) çekilişle
  eşleştirip "büyümüş havuzda gerçek ROI ne olurdu" hesabı — mevcut script sadece devir
  olaylarının kendisini sayıyor, sonraki resolve'a bağlamıyor.

## 2026-07-24 — Raporlarda tam şeffaflık: seçim + sıra + kazanan + bedel/ödül + toplam

**K55 — `kod/rapor_ortak.py` + Altılı/paper sayfaları zengin formata geçirildi (kullanıcı isteği).**
İstek: "kupona yazdığımız atların sistem tahmin sırası, kazanan atlar, kazananın kamu sırası ve
ganyan oranı, kupon bedeli ve ödülü, şehir/tarih — düzgün ve anlaşılır; altta toplam bedel ve
kazanç. Aynı düzen tüm analizlerde." Kullanıcı kararları: **3 ayrı sayfa aynı formatta** +
**geçmişin tamamı listelensin** + **sistemin mevcut hali hiç bozulmasın**.
- **Tasarım (bozmama kısıtına uygun):** `altili_kupon.csv`, `paper_kupon.csv`, `defter.csv` ve
  veri toplama akışı DEĞİŞMEDİ. Zenginleştirme HTML üretim anında `defter.csv`'den JOIN ile
  yapılıyor (defter zaten her koşunun TÜM atlarını bot1/bot2/kamu/oran/`model_rank` ile tutuyor).
  Tek yeni dosya: `veri/altili_temettu.csv` (ödül cache'i; feed'den çekilip saklanır).
- **Yeni sütunlar:** bizim seçimlerimiz + her birinin **sistem sırası**; **kazanan at** (ad+no);
  kazananın **sistem sırası**; kazananın **kamu sırası**; **ganyan oranı**; kupon bedeli; ödül; net.
  Üstte ve altta **TOPLAM blokları** (dar/orta veya strateji bazında + genel toplam).
- **Kupon bedeli gerçek tarifeyle:** 2026 birim fiyatı — İst/Ank/İzm/Ada/Bur/Koc/Ant **1,25 TL**,
  Elazığ/Urfa/Diyarbakır 1,00 TL (kaynak: TJK/Yarış Dergisi). Dar kupon 16 kombo × 1,25 = 20 TL
  (TJK asgari kupon sınırı). Önceki "72 TL" hesabı 1 TL varsayımıydı, düzeltildi.
- **Ödül dürüstlüğü korundu:** yalnız 6/6 ödeme yazılır; 5/4/3 ayak rozeti "(bilgi)" etiketiyle
  gösterilir (K52: ayrı bahis, teselli değil).
- **Eksik veri uydurulmuyor:** 21 Tem kaybı (K54 öncesi) + 20 Tem elle kurulan kuponlar defter'de
  yok → o ayaklarda sistem sırası "-" görünür (7/61 ayak).
- **İlk çıktılar:** Altılı — 13 pencere × 2 config; genel toplam bedel 1.200 TL, ödül 17.934,50 TL,
  **net +16.734,50 TL** (tek 6/6 isabetten; ⚠ varyans, K52 backtest −%32). Paper — 454 sonuçlanan
  kupon, bedel 6.810 TL, ödül 4.988,25 TL, **net −1.821,75 TL (ROI −%26,8)**.
- **Teşhis gücü kanıtlandı:** 23 Tem 6/6 kuponunda kazananların sistem sıraları 4./1./5./3./1./8. —
  orta kupon 6. ayakta **8. sıradaki** atı (oran 11,70) kapsadığı için tuttu, dar kupon kaçırdı.
- **Doğrulama:** her iki sayfa üretildi; `sonucla_paper`/`sonucla_altili` akışı çalıştı (47 + 44
  kayıt); **gerçek takip geçişi koşuldu, regresyon yok.** K50 yedeğine temettü cache'i eklendi.

## 2026-07-22 — HATA: geçici feed hatası günü kalıcı mühürlüyordu (15 koşu kayıp)

**K54 — `takip.gecis()` "YOK" mührü koşullandırıldı.** Vaka (21 Tem): 14:30 geçişi "bekleyen 15"
derken 14:45 geçişi `"izinli Ingiliz/Arap kosusu yok -> gun kapandi"` yazıp günü kalıcı mühürledi;
kalan 15 koşu (ANKARA 3-9 + KOCAELI 1-8) hiç işlenmedi, sonraki geçişler mührü görüp sessizce çıktı.
- **Kök neden:** `yerli_pistler()` ve `program_kosulari()` ağ/HTTP hatasında BOŞ LİSTE dönüyordu;
  kod bunu "bugün yarış yok" sanıp `YOK` marker'ı yazıyordu. Yani **geçici hata → kalıcı gün kaybı.**
  (PC kapalı değildi — geçişler 14:45'e kadar düzenli akıyor; tasarım kusuru.)
- **Düzeltme (iki katmanlı):** (a) her iki fonksiyon artık hata bildiriyor
  (`yerli_pistler(ymd, hata_bildir=True) -> (liste, hata)`, `program_kosulari -> (liste, hata)`);
  feed hatası varsa mühür YAZILMAZ, sonraki geçiş yeniden dener. (b) Gün içinde daha önce herhangi
  bir marker varsa (koşu görülmüş/işlenmiş) boş liste gelse bile ASLA mühürlenmez.
- **Doğrulama:** 3 senaryo testi (scratch dosyalarla) — feed hatası→mühür yok; gerçek boş gün+feed
  OK→mühür var (optimizasyon korundu); **21 Tem'in tam senaryosu (marker var + boş liste)→mühür yok.**
  Ardından gerçek geçiş koşuldu, regresyon yok. `yerli_pistler` geriye uyumlu (gunluk.py:300 etkilenmedi).
- **Kayıp telafi edilemez** (21 Tem koşuları geçti); düzeltme ileriye dönük.

## 2026-07-20 — Altılı CANLI kupon takibi (izleme/öğrenme; gerçek bahis değil)

**K53 — `kod/altili_canli.py`: canlı Altılı kupon üretimi + ayak-ayak sonuç + isabet takibi.**
Kullanıcı: "Altılı'yı gerçek bahis için KULLANMAYACAĞIM, o yüzden mutlaka denemek istiyorum —
ilk koşulardan makul süre önce kupon hazırlansın/listelensin, sonra her koşu + nihai Altılı sonucu
eklensin, başarı oranını en açık dille/görselle görelim." K48 ile tam uyumlu (para yok); K52 ile
dürüst (backtest OOS −%32, +EV yok — sayfada sabit uyarı).
- **Kullanıcı kararları:** (1) kupon genişliği: DAR (≤24 kombo) VE ORTA (≤96 kombo) İKİSİ de,
  ayrı takip. (2) Kapsam: önce sadece Altılı; 4/5/7'li sonra (aynı altyapı, program zaten
  "N'Lİ GANYAN bu koşudan başlar" ile hepsini işaretliyor → eklemek kolay).
- **Pencere tespiti (kesin, tahmin yok):** program BAHISLER_TR'de "N. 6'LI GANYAN bu koşudan
  başlar" → o koşudan 6 ardışık koşu. Günde 1-2 örtüşen Altılı (K46 keşfi) doğru yakalanıyor
  (İstanbul 19 Tem: koşu 1-6 ve 5-10).
- **Fizibilite doğrulandı:** muhtemel oran ilk koşudan saatler önce dolu → kupon baştan kurulabilir.
- **Kupon mantığı:** K52 backtest'iyle AYNI çekirdek (`altili_backtest.kupon_kur`) — banker
  (Bot2≥0,70→tek at) + spread (kümülatif 0,75) + bütçe tavanı (kombo>max→en belirsiz ayaktan buda).
  Ayaklar hem İngiliz hem Arap (K46 sayesinde puanlanıyor); bir ayak kapsam dışıysa o pencere atlanır.
- **Ödeme dürüstlüğü (K52):** 5/4/3'lü AYRI bahisler (teselli değil) → yalnız 6/6 "tam isabet"
  kazanç; 5/4/3 sondan-ayak isabeti sadece BİLGİ olarak gösterilir (öğrenme, para değeri yok).
- **Otomasyon:** `takip.py`'ye iki try-korumalı hook (paper pattern'i — Altılı hatası takibi ASLA
  bozmaz): her geçişte `kupon_zamani_kur` (her Altılı ilk koşusuna ≤30dk kala, bir kez kurar) +
  gün sonu `sonucla_altili`. **Ayrı arayüz:** `veri/altili_kupon.csv` + `raporlar/altili.html`
  + çift-tık `altili_goster.bat`. defter/paper/K42'ye DOKUNMAZ.
- **Görsel (kullanıcı "en açık/net"):** üstte DAR/ORTA ayrı ÖZET (tamamlanan Altılı, tam-isabet %,
  sondan-ayak isabet dağılımı çubuğu); altında her Altılı kartı (6 ayak, seçilen atlar banker-vurgulu,
  koşu bitince yeşil TUTTU / kırmızı kaçtı / gri bekliyor, isabet rozeti).
- **Doğrulama:** çekirdek scratch'te uçtan uca test (kupon kur→sonucla→HTML, 24 ayak); hook güvenlik
  testi (geçmiş Altılı'ya kupon KURMAZ, 0 döner); takip regresyonsuz; K50 veri_commit Altılı'yı da
  yedekliyor. İlk gerçek kayıt 20 Tem BURSA (2 Altılı × 2 config; ikisi de isabetsiz — K52 beklentisi).

## 2026-07-19 — Altılı kupon backtest'i (kullanıcı isteği) — NEGATİF, teselli-tuzağı atlatıldı

**K52 — ALTILI "en efektif kupon" backtest'i: banker/spread + sondan-ağırlık + bütçe-optimize
ile bile +EV YOK. Kritik: pozitif GÖRÜNEN sonuç YANLIŞ ödeme varsayımından geliyordu, doğrulanıp
elendi.** Kullanıcı "her gün Altılı da test edelim, en efektifi kursun, geniş/pahalı yapmasın"
dedi. K23'ten farkı (yeni test, tekrar değil): (a) K46 Arap modeli → ayakların %46'sı artık
puanlanıyor (K23'te dışlanıyordu), (b) banker/spread + kademeli ödeme + günde-2-pencere (K23 sadece
top-k spread + tam-isabet). Backtest zinciri (hepsi offline, canlıya/paper'a/K42'ye DOKUNMAZ):
- `kod/altili_tam.py`: 4 ödeme kademesini (6/5/4/3, normal+devir) çıkarır. Pencere↔kademe eşlemesi
  metin önekine değil KOMBO ALT-KÜME eşleşmesine dayanır (önek tutarsız). Günde 2 örtüşen pencere
  (1-6 ve 4-9. koşu) doğrulandı. 6.747 olay.
- `kod/altili_olasilik.py`: TÜM ayakların (İngiliz+Arap) walk-forward Bot2'si (α İng +0,191 /
  Arap +0,217 — üretimle birebir). 24.822 koşu puanlandı; ayak kapsamı %54 İng + %46 Arap + %0 dışı.
- `kod/altili_backtest.py`: banker (güven≥eşik→tek at) + spread (kümülatif kapsam) + bütçe tavanı
  (kombo>max→en belirsiz ayaktan buda) + kademeli ödeme + bütçe/eşik taraması.
- **PARSER GÜVENLİĞİ:** ilk `devir_ayikla` (K51) regex'i tutar-kuyruğu sızıntısıyla 33 Altılı'nın
  9'unu 7'Lİ sanmıştı → yakalandı/düzeltildi (24 doğru). Pencere-dedup: aynı 6 koşu bazen 2 kombo
  metniyle → race_kod bazlı dedup.
- **TESELLİ TUZAĞI (talimatname m.2/m.4 — olağanüstü iddiaya olağanüstü kanıt):** ilk tablo OOS
  (2025-26) +%21…+%68 (hepsi pozitif!) verdi — 9 negatif testlik sistemde ALARM. İki senaryo A/B:
  - A (kademeli AÇIK = 6 tutmazsa 5/4/3 teselli sayılır): OOS +%45,4, bootstrap %95 GA
    [+21,7%, +72,1%] POZİTİF.
  - B (kademeli KAPALI = sadece 6 öder): OOS −%31,7, GA [−51,7%, −8,3%] NEGATİF.
  - **Tüm sonuç "TJK Altılı'da teselli var mı"ya bağlıydı.** Ham veriden KESİN çözüldü: 2.497
    vakanın 27'sinde 5'li kombosu 6'lının son-5'inden BAĞIMSIZ (farklı at/pencere) — teselli olsa
    5'li HER ZAMAN 6'lının son-5'i olurdu. + web: "5'li ganyan AYRI kupon". **SONUÇ: 5'li/4'lü/3'lü
    BAĞIMSIZ bahisler, 6'lının kademeli tesellisi DEĞİL → doğru senaryo B → NEGATİF.**
- **"6'sız ROI" tanığı:** her konfigürasyonda 6-tutturma jackpotları çıkarılınca ROI negatif
  (A'da bile −%7…−%37) → teselli/küçük ekonomisi sürekli kayıp; A'nın pozitifliği tümüyle
  yanlış-sayılan teselliden.
- **NİHAİ VERDICT: Altılı da dövülemiyor (10. bağımsız negatif).** Doğru ödeme yapısıyla OOS −%32,
  tüm dönem −%60…−%76. Banker/spread/bütçe-optimizasyonu kaybı yavaşlatır ama +EV üretmez. K23
  doğrulandı ve GÜÇLENDİRİLDİ (Arap kapsamı + doğru ödeme + kupon-kurma zanaatıyla). Engel yine
  yapısal: verimli piyasa + yüksek kesinti. Canlıya hiçbir şey bağlanmadı.
- **⚠ AÇIK TEYİT (kullanıcıdan):** teselli-yok sonucu ham-veri kanıtına dayanıyor (27/2497 bağımsız
  pencere) ama TJK kuralı birincil kaynaktan (site erişilemedi) teyit edilmedi. Kullanıcı TJK'yı
  biliyor → teselli GERÇEKTEN yoksa verdict kesin; VARSA senaryo A yeniden açılır (o zaman jackpot-
  varyansı + price-impact ayrıca test edilmeli). **Karar bu teyide kadar: Altılı +EV değil.**

## 2026-07-17 — Gerçek bahis yok: K37/K41 askıda, amaç daraltıldı

**K48 — Kullanıcı beyanı (2026-07-17): GERÇEK BAHİS OYNAMIYOR.** 14 günde 0 kayıtlı kupon
(`bahisler.csv` hiç oluşmadı) sorgulandı; cevap net: oynamıyor.
- **Değerlendirme (dürüst):** Bu, projenin ölçülebilir en iyi finansal çıktısı. Sistem oyunun
  beklenen maliyetini 9 testte kesinleştirdi (−%25,5 İng / −%30,6 Arap kesinti); oynamamak =
  o maliyeti realize etmemek. "Kazandırdı" değil, "bilerek kaybettirmedi".
- **K37/K41 ASKIDA (kaldırılmadı):** bahis/bahis-sonuc komutları, tavan uyarıları, ön-taahhütlü
  değerlendirme kuralı ve `bahis_gir.bat` yerinde duruyor. İlk gerçek kupon kaydıyla çerçeve
  kendiliğinden yeniden aktifleşir (n≥100/90-gün sayacı o günden başlar). Yeniden başlama
  koşulu hakkında dürüst not: 9 test "+EV yok" diyor — veri değişmeden gerçek paraya dönüş
  için sistemden gerekçe ÇIKMAYACAK.
- **Sistemin resmi amacı daraltıldı:** (1) K42 paper testini 25 Eylül'e kadar tamamlamak
  (kalibrasyon + plase + CANLI verdiktleri), (2) öğrenme/izleme — kullanıcının kişisel takibi.
  +EV arayışı kapalı.
- **KARAR NOKTASI TAKVİME BAĞLANDI: 25 Eylül 2026 (W12 sonu).** Paper final raporuyla birlikte
  "sistem hangi modda devam etsin" kararı: (a) günlük izleme sürsün / (b) istek-üzerine analiz
  moduna insin (günlük takip kapalı, araçlar duruyor) / (c) arşivlensin. Ön-taahhüt kültürü:
  karar tarihi şimdi sabitlendi, tartışma veri geldiğinde.

## 2026-07-09 — Otomasyon doğrulaması + bekçi

**K47 — K43/K45 düzeltmesi DOĞRULANDI + kendi kendini denetleyen bekçi kuruldu.**
- **Doğrulama (kullanıcı istedi):** "TJK Takip" görevi pil düzeltmesinden beri 3 gün üst üste
  tam 10:30'da çalıştı (LastRunTime 09.07 10:30:01; 7/8/9 Tem rapor dosyaları + paper kuponları:
  37/19/31). 6 Tem tek kayıp gün olarak kaldı.
- **Bekçi:** insan-fark-etmesine dayanan son halka da kaldırıldı — `kod/bekci.py` + "TJK Bekci"
  görevi (13:30, pil-kısıtsız): takip o gün başlamadıysa (kalp atışı `veri/takip_son.txt`,
  takip.main yazar) EKRANDA uyarı penceresi açar. Yarış olmayan gün sessiz (takip yine açılıp
  kalp atışı yazar). Kurulum-sonrası-doğrulama dersi (K45) gereği: bekçinin İLK gerçek tetiği
  (10 Tem 13:30) ayrıca kontrol edilecek.
- **Not:** 9 Tem koşuları tek-model (İngiliz) kodla izlendi — K46 aynı akşam 20:38'de
  commit'lendi; ilk çift-modelli gün 10 Tem.

## 2026-07-24 — K56: Bekleyen işler defteri + v2 Altılı kararı

**K56 — Ertelenen işler için ayrı sayfa (`BEKLEYENLER.md`) + v2 Altılı budaması BACKTEST'e ertelendi.**
- **Sayfa:** "sonra yapalım/deneyelim" denen işler KARARLAR'ın tarihli satırlarına dağılıp
  unutuluyordu → `BEKLEYENLER.md` tek bakış noktası (kural: iş ertelenince yazılır,
  yapılınca/düşünce damgalanır, silinmez). K6 gereği proje kaydı dosya tabanlı; bu da öyle.
- **v2 Altılı budama kararı:** Mevcut budama bütçe aşımında EN SIKIŞIK ayaktan atıyor; doğrusu
  tersi (sıkışık ayağı koru, baskın ayaktan buda). Somut: 23.07 Ankara 1. Altılı'da YURİBOYKA
  budandı → 5/6, ~19.167 TL kaçtı. **Karar: canlı paralel v2 sistemi KURULMAYACAK** —
  Altılı 6/6 varyansı canlı kıyası ölçülemez kılıyor. Kanıt: 13 olayda (24 sonuçlanan kupon)
  net +16.344 TL / +%1028 ROI **ama tamamı tek 6/6'dan** (23.07 Ankara 2.); o hit olmasa
  −1.590 TL / −%100 → n=1, istatistiksel güç yok. **Doğru sınama = K52-tarzı eşleşmeli
  backtest** (arşiv), robust üstünlük çıkarsa konuşulur. BEKLEYENLER.md #1'e kaydedildi.

## 2026-07-24 — K57: Orta genisletilmedi (backtest) + genis gozlem akisi eklendi

**K57 — "orta'yi genisletmeli miyiz?" backtest'le olculdu; orta AYNEN kaldi, v2 budama REDDEDILDI,
kullanici istegiyle AYRI 'genis' (288) gozlem akisi eklendi.**
- **Arac:** `kod/altili_kap_test.py` (yeni, OFFLINE/salt-okunur; canliya/takip/paper/K52'ye dokunmaz).
  1455 OOS Altili olayinda (2025-26) kap boyutu (96/144/192/240/288/384) + budama (v1/v2) taramasi,
  olay-bazli bootstrap %95 GA ile.
- **Bulgu 1 — genisletme kazanc VERMIYOR:** durust zeminde (sadece 6/6 oder) ROI orta(96) -%19,4;
  288 -%31,7; 384 -%44,0 -> kap buyudukce zarar buyuyor. Iyimser zeminde (teselli ACIK, DOGRULANMAMIS
  varsayim) 144 daha yuksek puan verir ama genis(384) eksi orta(96) fark GA'si [-49,7 , +11,0] =
  SIFIRI ICERIR -> istatistiksel fark yok. **Karar: orta 96 AYNEN kalir.**
- **Bulgu 2 — K56 v2 budama (sikisik ayagi koru) DAHA KOTU:** orta'da ROI +%44,7 -> +%10,9'a duser,
  6/6 sayisi 66 -> 47. YURIBOYKA vakasina bakip degistirmemek dogruymus (hindsight tuzagi). **v2 REDDEDILDI.**
  -> K56'daki acik "v2 budama backtest'e ertelendi" maddesi KAPANDI (negatif).
- **Kullanici karari:** genisletme kar getirmese de AYRI 'genis' kupon gozlem akisi istendi (sistem
  bahis degil, deney — mesru). `altili_canli.KONFIG` -> {dar:24, orta:96, genis:288}. Makine konfig-
  bagimsiz oldugu icin tek satir + iki metin degisti; **dar/orta bit-bit ayni, mevcut deney bozulmadi.**
  genis kendi config satirlarini yazar, HTML'de ucuncu blok. **Ileri-yonlu:** genis, bir sonraki
  kupon-penceresinden itibaren birikir (bugun kurulmus dar/orta kuponlarina geriye donuk eklenmez).
- **Etiket dururken:** genis bir IYILESTIRME DEGIL; -EV oldugu backtest'te olculu. Kod/HTML metinleri
  bunu acikca yaziyor ki ileride "genis kar ediyor" yanilgisina dusulmesin (bkz. +%1028 ROI tuzagi, K56).
- **Dogrulama:** KONFIG=3 config; html_yaz bos genis blogunu cokmeden basti (60727 char).

## 2026-07-24 — K58: Altili sayfasi gorunum zenginlestirmesi

**K58 — altili.html'e (a) secimde KAMU sirasi, (b) her ayagin altinda koşunun TUM sistem
siralamasi eklendi. Salt gorunum; veri akisina/altili_kupon.csv'ye DOKUNMAZ.**
- **(a) Secim hucresi:** "at no (sistem sirasi)" -> "at no (sistem sirasi / kamu sirasi)".
  Ornek: 1 (2. / 3.) = sistem 2., kamu 3. at_bilgi zaten kamu_sira donuyordu; tek satir.
- **(b) Tum siralama satiri:** her ayagin ana satirinin ALTINDA ayri satir; o kosudaki BUTUN
  atlar sistem sirasina gore. Bizim sectigimiz KALIN, kazanan YESIL kutu + tik. `_tum_siralama_html`
  defter.csv'den (kosu_atlari) uretir; defter kaydi yoksa (21 Tem kayip / 20 Tem elle) acikca soyler.
- **Kullanici gerekcesi:** "en kolay anlayabilecegim, yormayacak sekilde" -> iki gorsel ipucu ile
  sinirli (kalin + yesil), lejant satir icinde; ekstra sutun yerine alt-satir (genis sahada okunakli).
- **Genis (K57):** ayni sayfada otomatik ucuncu blok; ileri-yonlu (gecmise backfill YOK, hindsight).
- **Dogrulama:** html_yaz cokmeden uretti (124268 char); 278 secim hucresi sistem/kamu formatinda,
  146 ayakta tum-siralama satiri, kazanan yesil kutulari basildi.

## 2026-07-24 — K59: Oran gecmisi kaydi (ileri-yonlu; kayma olcumu icin)

**K59 — `kod/oran_log.py` (yeni): gun-ici canli oran gecmisini biriktirir. SISTEME DOKUNMAZ —
kupon kurmaz, model calistirmaz, mevcut hicbir dosyayi degistirmez; kupon zamanlamasi 30 dk AYNI.**
- **Neden:** Asil kuponlar 30 dk kala kuruluyor (degismedi). Oranlar posta anina kadar kayiyor
  (23.07 Ankara-2: 6 kazanandan 3'u kaymis, ama kayma o vakada LEHIMIZE calisti). "30 yerine
  15/5 dk kala kursaydik degisir miydi" backtest'le OLCULEMEZ (arsivde gun-ici oran serisi yok).
  Bu modul o seriyi ILERIYE donuk biriktirir -> karar birkac ay sonra GERCEK veriyle verilir.
- **Ne yapar:** takip her geciste (try-korumali) cagirir; postaya <=45 dk kalan + baslamamis her
  Altili ayagi icin her atin canli GANYAN + AGF1'ini zaman damgasi + dk_kala ile
  `veri/altili_oran_log.csv`'ye EKLER. (race_kod,no,kayit_ts) tekrari silinir.
  **Ayni-gun duzeltme (a):** cikan (KOSMAZ) atlar ATILMAZ -> `kosmaz` bayragiyla loglanir; cikma da
  bir piyasa olayi (havuz dagilir, oranlar ziplar) -> kayma calismasi icin yakalanmasi gerek. Bu
  ileri-yonlu veride "sonra geri alinamaz" oldugu icin simdi eklendi.
- **Neden guvenli:** yeni modul + kendi log dosyasi + takip'e try-korumali TEK cagri. Hata firlatmaz;
  altili/paper hook'lariyla ayni izolasyon. Mevcut kupon/model/defter akisi bit-bit ayni.
- **Dogrulama:** sentetik program testi (sahte getjson, scratch log) -> 45dk penceresi dogru
  (ayak1@20dk,ayak2@40dk loglandi; ayak3@70dk haric), KOSMAZ atlandi, GANYAN/AGF1 dogru parse.
  py_compile + ast.parse takip.py/oran_log.py OK. veri_commit.py'ye log eklendi (K50 yedegi).
- **ACIK IS (BEKLEYENLER):** birkac ay veri birikince offline "kupon zamani" analizi — 30 vs 15/5 dk
  secim/isabet farki. TETIK: yeterli oran_log verisi (>= birkac hafta Altili gunu).

## 2026-07-25 — K60: Altili kupon Telegram bildirimi (AT'ye ozel bot)

**K60 — Altili kuponu kurulunca (30 dk kala) Telegram'dan NUMARA + ISIMLE bildirim. AT'ye OZEL bot
(kripto'dan AYRI, kullanici istegi).**
- **Yeni:** `kod/telegram_at.py` — urllib ile sendMessage (yeni bagimlilik yok). Token+chat_id
  `kod/telegram_config.json`'da (GIT DISI; .gitignore). Config yoksa gonder() SESSIZCE no-op ->
  bot kurulmadan da kod guvenli, hicbir sey bozulmaz.
- **altili_canli:** `bildir_kupon(pist,tarih,seq,o)` uc config'i (dar/orta/genis) numara+isimle,
  ayak-ayak, banker isaretli, bedelle mesajlar; `kupon_zamani_kur` yeni kupon kurunca TRY-KORUMALI
  cagirir (bildirim hatasi kupon kurmayi/takibi ASLA bozmaz). Isimler program JSON'dan (atlar/AD).
- **Dogrulama:** gercek kupon (23.07 ANKARA 2.) ile mesaj kuru uretildi (gondermeden) -> dar+orta
  ayak-ayak numara+isim dogru, banker isaretli. py_compile OK. Token gelince --kur ile chat_id
  bulunup config yazilacak + test mesaji.
- **Kurulum (kullanici):** @BotFather -> /newbot -> token; bota mesaj yaz; `telegram_at.py --kur <token>`
  chat_id'yi bulur, config yazar, test atar.

## 2026-07-25 — K61: Altili SONUC Telegram bildirimi

**K61 — Bir Altili'nin 6 ayagi da tamamlaninca Telegram'dan SONUC bildirimi (bir kez).**
- **altili_canli.bildir_sonuc(tarih,pist,seq):** kazananlar (numara+isim) + her config'in isabeti
  (6/6 / son-N / tutmadi) + bedel/odul/net + RESMI temettu (veya devir). `telegram_at` config yoksa
  sessizce gecer.
- **Tetik:** `sonucla_altili` bir geciste acik ayagi olan gruplari (aday_gruplar) not eder; gecis
  sonunda 6 ayagi da tamamlanan gruplar icin bir kez `bildir_sonuc` cagirir. IDEMPOTENT (sonraki
  geciste o grubun acik ayagi yok -> tekrar bildirmez). TRY-KORUMALI -> bildirim hatasi sonuclama/
  takibi ASLA bozmaz.
- **Zarar yok:** kupon-kurulum bildirimiyle (K60) ayni izole desen; sonuclama/defter/temettu akisi
  bit-bit ayni. Config yoksa hicbir mesaj gitmez.
- **Dogrulama:** gercek veri (23.07 ANKARA 2., orta 6/6) ile mesaj kuru uretildi (gondermeden) ->
  kazananlar+isim, DAR "son 5 ayak", ORTA "6/6 TUTTU" net +17.844,50, resmi temettu 17.934,50 dogru.
  py_compile OK.

## 2026-07-25 — K62: 'genis900' config (kullanici istegi, gozlem akisi)

**K62 — Dorduncu Altili config 'genis900' (kapsam 0.95, <=900 kombo ~ 900-1125 TL). Kullanici
karari: -EV oldugunu bilerek, "aklimiza geleni test edelim, paper zarari yok" ilkesiyle.**
- **Onaylanmadan once OLCULDU (backtest):** 1455 OOS'ta 900-kombo dürüst zemin (sadece 6/6) ROI
  **-%41..-%44**, bootstrap GA [-57,-24] -> sifiri NET disliyor, kesin zarar. Iyimser (teselli)
  ölcüde bile genis kötü (288'de +%45 -> 900'de +%8). Test edilen EN KOTU olcek. Kullaniciya
  sunuldu; kullanici yine de gozlem akisi olarak istedi -> eklendi (talimatname: tekrar onaylandi).
- **Tasarim:** KONFIG artik config -> (kapsam_esik, max_kombo). genis900 YUKSEK kapsam (0.95) ki
  derin (5./6. sira) kazananlara ulasabilsin (0.75 onlara varmadan doluyor). dar/orta/genis 0.75'te
  BIT-BIT AYNI kaldi. Telegram (K60/K61) + sonuc listesi + HTML KONFIG'i gezdigi icin genis900'u
  OTOMATIK alir (ek kod yok).
- **ONEMLI BULGU:** genis900 BILE Bursa 24.07/2. Altili'yi (6/1/5/3/3/8, ~57k) tutturmuyor -> 729
  kombo/911 TL, 3/6. Cunku 0.95 kapsam her ayakta 5-7 at ister, carpim 900'u asar, butce budamasi
  onu 900'e kiskarken TAM DA derin kazananlari atar. "900 kombo yeterdi" rakami ayaklari kazananin
  yerine gore dagitan HINDSIGHT-optimal kupondu; kural-tabanli hicbir kupon 900 tavanda 6 derin
  kazanani ayni anda kapsayamaz (1x6x5x2x5x3=900 zaten tam sinir). "Daha cok kombo cozmez" tekrar dogrulandi.
- **Dogrulama:** KONFIG 4 config; kupon_kur genis900 ->729 kombo; HTML 4 config cokmeden basti
  (124767 char); bildir_kupon/bildir_sonuc KONFIG geziyor (genis900 otomatik). Ileri-yonlu.

## 2026-07-25 — K63: Altili pencere tespiti — tek-Altili formati (sessiz kayip fix)

**K63 — altili_pencereleri iki BAHISLER formatini da taniyor. ONCEDEN tek-Altili gunlerinde HIC
kupon kurulmuyordu (sessiz kayip).**
- **Kok neden:** tespit yalniz "N. 6'LI GANYAN bu kosudan baslar" desenini ariyordu (cok-Altili gunu).
  Tek-Altili gunlerinde TJK "6'LI GANYAN, 2. CIFTE bu kosudan baslar" yaziyor -> "baslar" CIFTE'ye bagli,
  Altili'ya degil -> desen eslesmiyor -> o gun dar/orta/genis/genis900 HICBIRI kurulmuyor. 25 Tem'de
  ANKARA(15:00) ve IZMIR(18:00) Altililari boyle kaciriliyordu.
- **Fix:** Altili baslangici = BAHISLER'de "6'LI GANYAN" GECEN kosu (bu ifade yalniz baslangic kosusunda
  gecer; 24 Tem cok + 25 Tem tek gunlerinde dogrulandi). seq: acik "N." varsa o, yoksa sirayla.
- **Regresyon KANITI:** 6 gecmis gun (20-24 Tem, kupon kurulmustu) eski==yeni BIREBIR ayni pencereler;
  25 Tem eski=[] iken yeni ANKARA(1,15:00)+IZMIR(1,18:00) yakaliyor. py_compile OK.
- **Etki:** ileri-yonlu. Bu duzeltme olmasa genis900 (ve tum config) bugun de kurulamazdi -> soru
  "900 bugun calisir mi" bu fix'e bagliydi.

## 2026-07-25 — K64: Basabas (dead heat) sonuclama fix

**K64 — sonucla_altili basabasi (ayni kosuda >1 at SONUC=1) DOGRU isliyor. Onceden tek kazanan
tutuyordu -> basabas ayaklar yanlis "kacti" sayiliyordu.**
- **Kok neden:** `kaz[rk] = NO` her SONUC=1 atinda ustune yaziyor -> yalniz SONUNCU kazanan kaliyordu;
  tuttu = (o tek at secimde mi). Basabasta (25 Tem IZMIR ayak5: #1 & #4 birlikte 1.) bizim tuttugumuz
  #1 saklanmadi, #4 saklandi, tuttu=0 yazildi -> IZMIR 5/6 iken 4/6 gorundu (Telegram/sayfa yanlis).
- **Fix:** `kazananlar_kumesi(o)` race_kod -> {kazanan NO'lari}; tuttu = (secim ∩ kazananlar bos degil)
  -> HERHANGI bir basabas kazanani yeter. kazanan sutunu tek int kalir (uyum): tuttuysak tuttugumuz,
  yoksa ilk kazanan. `yeniden_sonucla()` (+ CLI --duzelt): tum sonuclanmis ayaklari feed'den yeniden
  hesaplar (geriye duzeltme).
- **Etki:** --duzelt -> SADECE 4 satir degisti (25 Tem IZMIR ayak5, dort boy; tuttu 0->1). Gecmiste
  baska basabas yok (23.07 Ankara 6/6 dahil eski kayitlar ETKILENMEDI). IZMIR artik dogru: 5/6, kademe 5.
- **Dogrulama:** py_compile OK; duzeltme ciktisi 4 satir; Ankara 2/6 degismedi, IZMIR 5/6'ya duzeldi.
- **NOT:** IZMIR sonuc Telegram'i (K61) settle aninda YANLIS 4/6 gonderdi (kayit duzeldi ama o mesaj gecti).

## 2026-07-26 — K65: Butce DAGITIMI backtesti — "her ayakta esit at" gozlemi dogru, ama duzeltmek PAHALI

**K65 — Acgozlu (isabet-maksimize) dagitici kuponun SEKLINI istenen hale getiriyor ama PARAYI
kotulestiriyor. Canli dagitim (v1) AYNEN KALDI. `kod/altili_dagitim_test.py` (OFFLINE, salt-okunur).**
- **Kullanici gozlemi (dogrulandi):** "Altili normalde en guvendigin ayakta TEK at, guvenmedigin
  ayakta GENIS kurulur; bizde her ayakta ayni sayida at var." Canli olcum: `orta`da 108 ayagin 80'i
  tam 2 at (%74); `genis900`de HIC 2 atli ayak yok (20x3, 8x4). Tek-atli ayagi olan kupon: %5,9.
- **Koslar tekduze DEGIL, duzlestirmeyi BIZ yapiyoruz:** 78 gercek ayakta %75 kapsam talebi 1-9 at
  arasi (ort 4,21), bot2 favori gucu 0,156-0,768. Bu [1..9] talep kuponda [1,75..2,54]'e cokuyor.
  **Uc sebep:** (1) banker esigi 0.70 pratikte ulasilamaz (78 ayagin 3'u gecti), (2) kapsam esigi her
  ayakta AYNI -> esit kapsam esitleyicidir, (3) **budayici hep en kalabalik ayaktan keser = aktif
  duzlestirici (asil suclu).**
- **Test edilen (yeni):** `acgozlu` dagitici — kapsam esigi YOK, budama YOK; her ayakta 1 atla basla,
  butce dolana dek en iyi kazanc/bedel oranli ati ekle (max PI(P_i) s.t. PI(n_i)<=C; loglarda acgozlu
  sirt cantasi: kazanc=log(1+p/P_i), bedel=log((k+1)/k)). Kural yazmadan kaos ayagina cok, net ayaga
  tek at koyar. 1455 OOS olay (2025-26), butceler 24/96/288/900, bootstrap %95 GA, esli fark.
- **SEKIL: tam istenen hale geldi.** orta'da yayilim (en genis-en dar ayak) 1,06 -> 4,10; tek-atli
  ayagi olan kupon %5,9 -> %98,7. 288'de %91,2; 900'de %74,0. Yani mekanik CALISIYOR.
- **ISABET de arti:** 6/6 sayisi 24'te 19->34, 288'de 100->118, 900'de 185->225 (%+22). Acgozlu
  gercekten isabet olasiligini maksimize ediyor — matematik dogru calisiyor.
- **AMA PARA EKSI (asil bulgu):** ROI(6) (durust zemin) HER butcede kotulesti — 24: -24,4->-46,7;
  **96: -19,4->-60,4**; 288: -31,7->-54,9; 900: -41,2->-55,0. Esli fark GA'si 96 ve 288'de **sifir
  DISINDA** (gercek fark, sans degil).
- **KOK NEDEN — isabet ve kazanc TERS ceker (pari-mutuel):** acgozlu guvendigi ayaga tek at koyar =
  genelde KAMU FAVORISI = en kalabalik havuz. Tutturdugunda temettu kucuk. Ort. 6/6 temettusu 96
  butcesinde v1=1.656 TL vs acgozlu=798 TL (**yarisi**, ayni sayida isabetle: 66 vs 67). En buyuk
  yakalanan: v1=15.056 vs acgozlu=4.515; 900'de v1=47.383 vs acgozlu=22.374. **Acgozlu buyuk odemeleri
  sistematik olarak KACIRIYOR** cunku odeyen kombinasyonlar tam da onun "verimsiz" diye attigi surpriz
  atlari icerir.
- **KARAR:** canli dagitim (v1) DEGISMEDI. Kullanicinin teshisi DOGRUYDU (sekil gercekten tekduze,
  sebebi de bulundu), ama onerilen yon parayi kotulestiriyor. **v1'in "duzlugu" kazara koruyucu:**
  tek at atmayi reddederek her ayakta surpriz kapsamasini koruyor. (Kazara — tasarim degil; not.)
- **NOT (acik kapi):** Bu test isabet-maksimizasyonunu curuttu, "duz en iyisidir"i KANITLAMADI. Test
  EDILMEYEN aile: **EV-maksimize** dagitim (bizim bot2 ile kamu AGF'sinin AYRISTIGI ayaga genislik ver
  — kenar kalabalikla anlasmaktan degil ayrilmaktan gelir). K1 (etkin pazar) + 9 basarisiz kenar testi
  yuzunden beklenti DUSUK; BEKLEYENLER #7'ye yazildi.
- **Dogrulama:** py_compile OK; canli hicbir dosya degismedi (yalniz yeni test dosyasi + belge).

## 2026-07-26 — K66: acgozlu900 canliya GOZLEM akisi olarak eklendi (5. config)

**K66 — K65'te reddedilen acgozlu dagitici, kullanici karariyla 900 butcesinde CANLI gozlem akisi
olarak eklendi. Mevcut dort config AYNEN duruyor; hicbirinin mantigi degismedi.**
- **Kullanici gerekcesi (2026-07-26):** "benim icin en onemlisi en genis kupon; mevcut en genis de
  dursun, bunu da adinda belirterek kur." Bilinen -EV; K62'deki (genis900) ayni cerceve: iyilestirme
  degil, GOZLEM. Kagit sistemi, gercek para yok.
- **Neden 96 degil 900 (ilk oneri 96'ydi, kullanici 900 dedi — ve hakli):** K65 backtest'inde iki
  dagitim EN AZ 900'de ayristi. Durust zemin farki -13,4 puan ama %95 GA **[-32,2, +2,4] SIFIRI
  ICERIYOR** = 900'de soru istatistiksel olarak KAPANMADI (96'da [-76,8,-9,9] ile kapanmisti).
  Isabet farki da orada en buyuk (185 -> 225). Yani canli gozlemin bilgi degeri en yuksek oldugu
  butce 900. Ayrica genis900 ile AYNI butce -> kontrollu A/B (ayni gun/kosu/para, tek fark dagitim).
- **Yapilan (uc dosya):**
  1. `altili_backtest.py`: `kupon_kur_acgozlu(ayak_atlari, max_kombo)` eklendi (SALT EKLEME; mevcut
     `kupon_kur` ve K52 davranisi degismedi). Dagiticinin TEK KAYNAGI burasi.
  2. `altili_canli.py`: KONFIG degeri 2'li -> **3'lu** ((kapsam, max_kombo, **dagitim**)); yeni
     `"acgozlu900": (0.95, 900, "acgozlu")` (kapsam alani acgozlu'de KULLANILMAZ). `kupon_hazirla`
     dagitim'a gore secim yapiyor. **Diger tum tuketiciler (HTML toplam_blok, bildir_kupon,
     bildir_sonuc, sonucla_altili) yalnizca KONFIG ANAHTARLARINI geziyor -> hicbiri degismedi.**
  3. `altili_dagitim_test.py`: yerel kopya SILINDI, altili_backtest'ten import ediyor (test ile canli
     birbirinden KAYMASIN).
- **Dogrulama:** py_compile 3 dosya OK. Gercek arsiv verisiyle 900 butcesinde yan yana:
  genis900 = **[3,3,3,3,3,3] her seferinde** (kullanicinin sikayet ettigi tekduzelik birebir);
  acgozlu900 = [7,3,5,1,1,8] / [7,1,3,2,4,5] / [10,8,3,3,1,1] (banker + genis kaos ayagi).
  `--html` yeniden uretildi: 217.977 char, ACGOZLU900 blogu sayfada goruluyor (henuz 0 kupon).
- **ILERI-YONLU:** bugunku (26 Tem) kuponlar YENIDEN KURULMADI (kosular kostu -> hindsight olurdu).
  Ilk acgozlu900 kuponu bir sonraki kurulumda cikacak. Gecmis kayitlar ETKILENMEDI.
- **Beklenti (dururst kayit):** backtest'e gore bu akis genis900'den DAHA COK 6/6 tutturacak ama
  DAHA AZ para kazandiracak (ort. temettu 3.489 -> 2.469 TL; en buyuk yakalanan 47.383 -> 22.374).
  Canli n cok kucuk (~yilda 100 olay) -> canli akis backtest'i CURUTEMEZ, sadece gorunur kilar.
- **Yan etki:** kagit gideri Altili basina +1.125 TL/gun; altili.html GENEL TOPLAM eksisi hizlanir.

## 2026-07-30 — K67: "Kamu botu hic olmasaydi?" — Bot1-tek Altili backtesti

**K67 — Bot1 (oran-kor) tek basina Bot2'yi GECMIYOR; ama "kalabaliktan ayrilmak buyuk odemeleri
aciyor" tezi YAPISAL olarak DOGRULANDI. Canliya hicbir sey eklenmedi. `kod/altili_bot1_test.py`
(OFFLINE; yeni dosya veri/altili_olasilik_bot1.csv, mevcut altili_olasilik.csv AYNEN kaldi).**
- **Soruyu doguran olcum:** Bot2 pratikte KAMUNUN KENDISI — 24.822 kosuda Bot2 favorisi = kamu
  favorisi %89,9; sira korelasyonu 0,977; favori kazanma orani kamu %35,5 vs Bot2 %35,7 (fark
  ~0,2 puan). Yani bugune kadarki HER kupon ozunde kalabaligin kuponu.
- **Bot1 gercekten ayri:** Bot1 favorisi = kamu favorisi yalnizca %47,3. Bedeli var: Bot1 favorisi
  kazanma orani %29,1 (Bot2 %35,7) -> kamuyu atmak isabetten OLUYOR.
- **Onceden yazilan beklenti AYNEN cikti:** Bot1 daha AZ tutturur, daha COK oder. 900 butce/acgozlu:
  isabet 225 -> 123 (yariya), ort. temettu 2.469 -> 10.248 TL (4 kat).
- **8 hucre tarandi** (2 dagitim x 4 butce). Yedisi negatif. TEK pozitif: bot1+acgozlu+900 =
  **ROI +%2,1** — ama %95 GA **[-64,5, +105,8]**, esli fark GA'si **[-8,7, +167,8] SIFIRI ICERIYOR**.
  8 hucrede 1 pozitif = gurultuden beklenecek sayi (coklu kiyas uyarisi).
- **YOGUNLASMA TESTI (kritik):** o +%2,1'in kaynagi TEK isabet — 539.029 TL. Cikarinca **-%41,6**.
  Toplam getirinin %43'u tek isabetten, %63'u en buyuk uc isabetten. Medyan temettu ise sadece
  2.056 TL. Yani siradan isabetler masrafi KARSILAMIYOR; her sey kuyruga bagli.
- **AMA YAPISAL BULGU (sans degil):** 900/acgozlu'de **Bot2'nin 225 isabetinde en buyuk odeme
  22.374 TL; 50 binin ustu SIFIR.** Bot1 ise 123 isabette 100 binin ustune **UC KEZ** cikti
  (en buyuk 539.029). Bot2 buyuk temettu bolgesine hic girmiyor — cunku temettu tam da kalabalik
  YANILDIGINDA buyur ve Bot2 kalabaligin ta kendisi. **Kullanicinin "ayri dusmek oduyor" sezgisi
  mekanizma olarak DOGRU.**
- **KARAR:** canliya Bot1 akisi EKLENMEDI, hicbir config degismedi. Gerekce: tez kuyruk olaylarina
  dayaniyor (1455 olayda 3 adet 100bin+ = ~%0,2). Canlida ~gunde 2 Altili ile bir jackpot beklemek
  ~250 gun demek; canli gozlem bu soruyu OMURDE cozemez. Karlilik bu veriyle ne dogrulanabilir
  ne curutulebilir.
- **Dogrulama:** yeniden uretilen bot2, mevcut altili_olasilik.csv ile birebir ayni (max fark
  ~1e-16) -> walk-forward kurulumu dogru kopyalandi. py_compile OK.
- **Not:** Bu, K19-K33/K44/K46/K52/K57/K65 dizisindeki 10. kenar testi. Digerlerinden farki:
  ilk kez bir mekanizma DOGRULANDI (kuyruk erisimi), ama karliliga cevirilemedi.

## 2026-07-31 — K68: Ayrisma dagitici testi (BEKLEYENLER #7) — BULGU YOK

**K68 — "Genisligi bot1 ile kamunun ayristigi ayaga ver" fikri OLCULDU, ONCEDEN YAZILAN uc
olcutun UCU de dustu. `ayrisma900` canliya EKLENMEDI. `kod/altili_ayrisma_test.py` (OFFLINE).**
- **Fikir (K65+K67 sentezi):** bot2 ile SEC (isabeti koru), ama genisligi ayrisan ayaga ver ->
  kalabaliktan ayriligi en ucuz oldugu yerden satin al. Dagitici = acgozlu'nun agirlikli hali:
  kazanc = log(1+p/P_i) * (1 + w*D_i);  D_i = 0.5*sum|bot1_p - kamu_p| (toplam degisim uzakligi).
  w taramasi: 0 / 0.5 / 1 / 2 / 4 (w=0 = saf acgozlu = kiyas tabani). Butce 96 / 288 / 900.
  D dagilimi: ort 0,42 civari -- ayrisma gercekten var, olcu anlamli.
- **ONCEDEN yazilan karar olcutleri ve sonuclari:**
  (a) *w buyudukce ROI monoton iyilesmeli* -> 96 ve 288'de EVET (-60,4->-48,2 ve -54,9->-40,2),
      ama **900'de DUZ** (-55,0 / -57,7 / -54,9 / -56,1 / -55,9 -- egilim YOK). **DUSTU.**
  (b) *esli fark GA'si sifiri dislamali* -> **12 kiyasin 12'sinde de GA sifiri ICERIYOR.**
      En iyisi w=4@288: +13,7 puan ama GA [-4,7, +36,7]. **DUSTU.**
  (c) *ayni w farkli butcelerde de en iyi olmali* -> 96'da w=4, 288'de w=4, **900'de w=1
      (ve etki ~sifir)**. **DUSTU.**
- **DAHA ONEMLISI — mevcut canli mantik HEPSINI YENIYOR:** kapsam(v1) ROI(6): 96'da -%19,4,
  288'de -%31,7, 900'de -%41,2. En iyi ayrisma sirasiyla -%48,2 / -%40,2 / -%54,9. Yani
  ayrisma sadece "acgozlu'dan iyi degil" degil, tum acgozlu ailesi mevcut kapsam mantigindan
  KOTU (K65 bulgusuyla tutarli).
- **TEK OLUMLU IZ (mekanizma gorunuyor ama yetmiyor):** w buyudukce ort. temettu artiyor --
  96'da 798->1.078, 288'de 1.547->2.088 (isabet ~sabit kalarak). Yani ayrisma agirligi
  GERCEKTEN daha buyuk odemeli kombinasyonlara itiyor (K67'nin mekanizmasi burada da gorunur).
  Ama 900'de bu da kayboluyor: temettu 2.469->2.711 artarken isabet 225->201 dusup netlesiyor.
- **KARAR:** `ayrisma900` canliya alinmadi. Gerekce: kendi onceden yazdigimiz uc olcut de
  dustu; w taramasi coklu kiyas oldugu icin "en iyi w"yi secmek overfit olurdu (K33/K52 yasagi).
- **BEKLEYENLER #7 -> KAPANDI** (olculdu, negatif).
- **Dogrulama:** py_compile OK; canliya/veriye dokunulmadi (yalniz yeni test dosyasi + belge).

## 2026-07-31 — K69: bot1_900 + ayrisma900 canliya; sayfa yan-yana matrise, kumulatif eklendi

**K69 — Iki yeni GOZLEM akisi (7 config), Altili sayfasi kupon-turleri-yan-yana matrise cevrildi,
gun-gun ISLEYEN BAKIYE ve "Altili + ganyan birlesik" sicili eklendi. Mevcut bes config'in
mantigi BIT-BIT AYNI kaldi.**
- **Yeni config'ler (kullanici karari 2026-07-31, "aklimizda soru kalmasin"):**
  - `bot1_900` = Bot1 (oran-kor) + acgozlu + 900. K67'de 8 hucreden TEK sinyal veren ve
    izlenebilir siklikta tutan hucre (isabet %8,58; kapsam ailesi %0,42-%5,93 ile ekranda
    aylarca bos kalirdi). Kullanici "bot1 sadece acgozlude mi" diye sordu -> EVET, gerekcesi bu.
  - `ayrisma900` = Bot2 secer + genislik ayrisan ayaga (K68). **Backtest'te bulgu YOK** (uc olcut
    de dustu); kullanici bilerek gozlem olarak istedi. **w=1.0 SABIT/TARANMADI** -- en iyi puanlayan
    w'yi secmek overfit olurdu (K33/K52). Olcum: w=1'de kuponlarin **%45,4'u** acgozlu'den farkli
    cikiyor (ayaklarin %20'si) -> kopya degil, ama %55 ayni cikacak (30 Tem ANKARA'da oyle oldu).
- **KONFIG yapisi degisti:** tuple -> dict (`kapsam/kombo/dagitim/puan/aile`). `puan` alani YENI:
  secim Bot2 yerine Bot1 ile yapilabiliyor. `dagitim` artik uc degerli (kapsam/acgozlu/ayrisma).
  Diger tum tuketiciler KONFIG ANAHTARLARINI geziyordu -> dokunulmadi.
- **Dayaniklilik:** bir config'in puani eksikse (or. bot1 yok) SADECE O CONFIG atlanir, digerleri
  kurulur; dagitici bos secim dondururse satir YAZILMAZ (bozuk kayit olusmaz).
- **Telegram:** aile basliklariyla gruplandi (KAMU BOTU / TEMEL BOT / AYRISMA), toplam kagit bedel
  satiri eklendi, sonuc bildirimine "bu Altili toplami" eklendi. `_telegram_bol()`: 3900 karakteri
  asarsa SATIR sinirindan bolup parca parca gonderir (7 config'te olcum: 2.104 karakter, tek parca).
- **altili.html (kullanici tasarimi onayladi):** her Altili artik TEK tablo, kupon turleri YAN YANA
  sutun. Eski karttaki her bilgi korundu: secilen atin sistem/kamu sirasi, kazananin sistem/kamu
  sirasi + ganyan orani, banker etiketi, durum rozeti, resmi temettu satiri, ve o kosunun TAM sistem
  siralamasi (artik TUM turler icin ortak tek satir). Kazanan hucre yesil zemin, kazanan at yesil kalin.
- **KUMULATIF (kullanici: "tum kar zarar tablosunu gormem onemli"):** iki yeni blok --
  (1) `_kumulatif_blok`: gun gun bedel/odul/net + **ISLEYEN BAKIYE** (yalniz sonuclanmis kuponlar),
  (2) `_birlesik_blok`: **ALTILI + GANYAN tek tabloda** + GENEL TOPLAM. Bugun: Altili 106 kupon
  +7.008,04 TL (%+18,8), ganyan 655 kupon -2.839,50 TL (%-28,9), **birlesik +4.168,54 TL (%+8,8)**.
  NOT: Altili artisi hala tek 6/6'lara dayaniyor (23 Tem +17.934, 29 Tem +12.983, 30 Tem +6.721).
  *Duzeltme: ganyan sayfasinda kumulatif zaten VARDI (haftalik); eksik olan Altili sayfasindaydi.*
- **Dogrulama:** py_compile OK. KURU CALISMA (`_yaz` devre disi) bugunku ANKARA+KOCAELI kartinda
  2 Altili x 7 config = 14 kupon kurdu, hepsi butce icinde (16/24, 96/96, 216/288, 729/900,
  864/900, 900/900, 864/900). `veri/altili_kupon.csv` bayt-bayt DEGISMEDI (yedekle karsilastirildi).
  Telegram kuru gonderim: 1 parca, 2.104 karakter, aile basliklari dogru. HTML 235.151 karakter.
- **ILERI-YONLU:** gecmis kuponlar yeniden kurulmadi; iki yeni akis bir sonraki kurulumda baslar.

## 2026-07-31 — K70: Altili ayaklari BAGIMSIZ — "alternatif/kosullu kupon" ek bilgi tasimiyor

**K70 — Ayni Altilinin 6 ayagi arasinda surpriz KUMELENMESI YOK. Carpim (bagimsizlik) varsayimimiz
DOGRU. Kosullu kupon yapisi ek BILGI tasimaz; yalnizca oynaklik duzenler. Hicbir sey degistirilmedi.
`kod/altili_ayak_korelasyon_test.py` (OFFLINE, salt-okunur).**
- **Soruyu doguran fikir (kullanici):** "Iyi Altili oyunculari birbirine ALTERNATIF kuponlar yapar."
- **Once mevcut durumu olctuk:** kuponlarimiz alternatif DEGIL, TAM IC ICE -- dar ⊂ orta ⊂ genis
  ⊂ genis900 **12/12 Altilida (%100)**. Satin alinan 23.084 kombinasyonun %24,7'si TEKRAR.
  **AMA bu israf DEGIL:** pari-mutuel'de ayni kazanan kombinasyonu iki kuponda tutmak IKI KEZ oder
  (30 Tem ANKARA: genis900 ve acgozlu900 ayri ayri 6.721 TL aldi). Yani ic icelik fiilen KADEMELI
  BAHIS: dar'daki kombinasyon 4 birim, genis900'un kiyisindaki 1 birim. Kazara kurulmus ama tutarli.
- **Asil mesele:** tek kupon matematiksel olarak bir CARPIM'dir; carpimla YAZILAMAYAN sey KOSULLU
  yapidir ("1. ayagi favori alirsa 3. ayakta dar, surpriz alirsa genis"). Bu ancak AYAKLAR
  ILISKILIYSE bilgi tasir. Model su an ayaklari bagimsiz variyor -> varsayimi SINADIK.
- **Test:** iki surpriz tanimi -- (a) ikili: kazanan kamu favorisi degil, (b) surekli: -ln(kazananin
  kamu olasiligi). Null = ayaklari Altililar arasinda rastgele yeniden dagitma (marjinaller korunur,
  yalnizca "ayni Altiliya ait olma" bagi kirilir), 20.000 permutasyon.
- **SONUC — her iki veri kumesinde de kumelenme YOK:**
  | olcu | gozlenen | bagimsizlik null | p |
  |---|---|---|---|
  | surpriz sayisi varyansi (tum arsiv) | 1,3621 | 1,3597 [1,3104-1,4101] | 0,46 |
  | ayak ici ort. korelasyon (tum arsiv) | +0,0004 | -0,0000 [-0,0073,+0,0073] | 0,45 |
  | surpriz sayisi varyansi (OOS 1433) | 1,3551 | 1,3659 [1,2770-1,4570] | 0,59 |
  | ayak ici ort. korelasyon (OOS) | +0,0006 | -0,0001 [-0,0135,+0,0136] | 0,46 |
  Kosullu kontrol: 1. ayakta surpriz varsa sonraki 5 ayagin surpriz orani %65,0; yoksa %63,9
  -> fark **+1,2 puan** (gurultu). Yan bulgu: ayak basina surpriz orani **%64,9** (kamu favorisi
  yalnizca ~%35 kazaniyor -- K67'deki %35,5 ile tutarli, capraz dogrulama).
- **ANLAMI:** "Pist bozuldu, o gun surprizler kumelenir" sezgisi TJK verisinde YOK. Dolayisiyla
  alternatif/kosullu kupon **EV degistirmez**; sadece ayni -EV'yi farkli oynaklikla dagitir.
  Ic ice yapimiz bir HATA degil, bir tercih: az sayida kombinasyona agir yatirim (tuttugunda cok
  oder) yerine cok sayida kombinasyona hafif yatirim (daha sik tutar, az oder) secilebilirdi --
  sifir kenar oldugu icin BEKLENEN GETIRI IKISINDE DE AYNI.
- **KARAR:** hicbir degisiklik yapilmadi. Kullanici dusuk-oynaklik profili isterse "ic-ice-olmayan"
  kupon seti kurulabilir; ama bu bir kazanc degil risk tercihidir -- oyle sunulmali.
- **Not:** Bu, K19-K33/K44/K46/K52/K57/K65/K67/K68 dizisindeki 11. kenar testi. Digerlerinden farki:
  bu sefer MODELIN BIR VARSAYIMI sinandi ve varsayim DOGRULANDI (nadir bir olumlu sonuc).

## 2026-07-31 — K71: Kupon KATMANLARININ ayri ayri getirisi — "hangisini oynamazdin?"

**K71 — Ic icelik (K70) sayesinde her kupon "bir oncekinin uzerine eklenen KABUK" olarak
cozumlendi. Sonuc: 96 kombodan SONRAKI her katman ISTATISTIKSEL OLARAK KANITLI ZARARLI.
Canliya dokunulmadi (kagit deneyi aynen suruyor); bu bir TAVSIYE kaydidir.**
- **Yontem:** 1433 OOS olayda dar(24) ⊂ orta(96) ⊂ genis(288) ⊂ genis900(900) — **%99,8'inde
  ic ice dogrulandi**. Her katmanin KENDI maliyeti ve KENDI getirisi (ust eksi alt) hesaplandi,
  olay-bazli bootstrap %95 GA (4000 tur). Durust zemin: yalnizca 6/6 oder.
- **KATMAN GETIRILERI:**
  | katman | kombo/olay | ROI | %95 GA | hukum |
  |---|---|---|---|---|
  | cekirdek (dar 24) | 16 | −%24,4 | [−68,1, +33,1] | sifiri iceriyor |
  | dar → orta | 79 | **−%18,3** | [−51,1, +23,0] | sifiri iceriyor |
  | orta → genis | 124 | −%41,2 | [−67,1, **−6,3**] | **sifir DISINDA = kanitli zararli** |
  | genis → genis900 | 513 | **−%49,2** | [−66,7, **−29,9**] | **sifir DISINDA = kanitli zararli** |
- **OKUMA:** Marjinal kombinasyonlar ilerledikce KOTULESIYOR. Ilk 96 kombo icin "zarar ettigi
  ISPATLANAMIYOR" (GA sifiri iceriyor); 96'dan sonraki her sey icin **ispatlaniyor**. Ozellikle
  genis→genis900 kabugu tek basina olay basina 513 kombo (genis900 harcamasinin ~%70'i) ve
  −%49,2 -> yatirilan her 1.000 TL'den ~508 TL geri geliyor.
- **TAVSIYE (kullanici "canlida oynasaydim hangilerini yatirma derdin" diye sordu):**
  1. **Hicbiri** — hepsi negatif; kesinti %25-31 ve 11 kenar testi negatif. Dogru cevap bu.
  2. Zorunlu secim olsa: **yalnizca orta (96)**. Iki ic katmani da GA'si sifiri iceren tek katmanlar.
  3. **Kesinlikle yatirma:** genis, genis900, acgozlu900, bot1_900, ayrisma900. 900 ailesi
     backtest'te −%41…−%55 ve harcamanin ezici cogunlugu.
  4. **dar'i AYRI oynama:** orta zaten iceriyor; ayri oynamak cekirdegi CIFT paylandirir ve cekirdek
     (−%24,4) orta-kabugundan (−%18,3) daha kotu.
  5. Mevcut kagit gideri ~4.500 TL/Altili; bunun yalnizca 120 TL'si (orta) elemeyi geciyor -> **%97'si
     kanitli zararli katmanlara gidiyor.** (Kagit oldugu icin sorun degil; gercek para olsa olurdu.)
- **UYARI:** "zarar ettigi ispatlanamiyor" ≠ "karli". orta'nin GA'si genis; taban oran (kesinti +
  onceki 11 test) orta'nin da negatif oldugunu soyluyor, sadece n=1433 bunu ispata yetmiyor.
- **Canli sistemde DEGISIKLIK YOK:** 7 config gozlem amaciyla kosmaya devam ediyor (K62/K65/K67/K68);
  bu kayit "gercek para olsaydi" sorusunun cevabidir.

## 2026-07-31 — K72: Taban cizgisi — model SANSI yeniyor, KALABALIGI yenmiyor

**K72 — orta'nin -%19,4'u modelin marifeti DEGIL; "favorileri oyna" tabanının kendisi.
Model rastgeleyi ezici farkla yeniyor ama kamu favorilerini YENEMIYOR. Canliya dokunulmadi.
`kod/altili_taban_test.py` (OFFLINE, salt-okunur).**
- **Soru (kullanici):** "-%19,4 kesintiden iyi gorunuyor — bu modelin marifeti mi, yoksa
  favorilere yaslanan her kupon boyle mi cikar?"
- **Adil kiyas:** her olayda GERCEK orta kuponunun AYAK GENISLIKLERI alinir (or. [2,2,2,2,2,3]),
  ayni genislikle alternatif seciciler kurulur -> **maliyet birebir ayni** (135.561 kombo, dordu de).
  1433 OOS olay, esli bootstrap 4000.
- **SONUC:**
  | secici | 6/6 | isabet% | ROI(6) | ort.temettu | bot2 ile AYNI kupon |
  |---|---|---|---|---|---|
  | **bot2 (biz)** | 66 | %4,61 | **−%19,4** | 1.656 | — |
  | kamu (sadece favoriler) | 65 | %4,54 | **−%17,4** | 1.722 | **%41,4** |
  | bot1 (oran-kor) | 28 | %1,95 | −%22,2 | 3.769 | %0,2 |
  | rastgele (25 tekrar) | 0-2 | %0,03 | −%59,6 | — | %0,0 |
- **ESLI FARKLAR (bot2 eksi digeri):**
  - vs **rastgele**: **+79,3 puan**, GA [+51,7, +114,3] -> **sifir DISINDA = gercek fark.**
    Model sansi EZICI farkla yeniyor; siralama gercek bilgi tasiyor, gurultu degil.
  - vs **kamu**: **−1,2 puan**, GA [−29,9, +21,4] -> **fark YOK** (ve isaret bizim aleyhimize).
  - vs **bot1**: +5,4 puan, GA [−77,7, +64,1] -> fark yok.
- **ANLAMI (net):** Kuponumuz fiilen KALABALIGIN kuponu. Secimimiz %41,4 oranında saf-favori
  secimiyle **birebir ayni**; kalanlarda da olculebilir ustunluk uretmiyor. −%19,4 bizim
  basarimiz degil, "Altilida favori oynamanin" getirisi (saf favori −%17,4, yani bizden bir tik
  daha iyi). **K1 (etkin pazar) tezinin en temiz kaniti** — bilgi zaten fiyatta.
- **Ama kucumsenmemeli:** model rastgeleye gore +79 puan uretiyor. Yani ozellikler/model
  CALISIYOR; sadece piyasanin ZATEN bildigi seyi ogreniyor. "Bot2 = kamu" (K67: favori
  ortakligi %89,9) bulgusunun sonuc-tarafindaki karsiligi budur.
- **Yan bulgu:** bot1 yarisi kadar tutturup (28 vs 66) iki kattan fazla oduyor (3.769 vs 1.656)
  ve ROI farki istatistiksel DEGIL -> K67 ile tutarli: kalabaliktan ayrilmak isabeti dusurup
  odemeyi buyutuyor, toplamda basa bas.
- **TAVSIYEYE ETKISI (K71):** "gercek para olsa yalniz orta" tavsiyesi zayifladi — orta oynamak
  fiilen "favori oyna" demek ve o da negatif. Dogru cevap yine: **oynama.**
- **ACIK SORU:** Altili havuzunun gercek kesinti orani nedir? Saf favori −%17,4 getiriyorsa
  kesinti ~%17-20 civarindaysa favoriler ortalamayi yeniyor demektir; daha yuksekse daha da cok.
  TJK Altili kesintisi kaynaklanmadi -> BEKLEYENLER'e.

## 2026-07-31 — K73: Altili kesintisi AGF'den tahmin edildi (~%45-50) — favori oynamak havuzu YENIYOR

**K73 — Altili kesinti orani ~%48,6 (tahmin). Bu, K72'yi yeniden yorumluyor: saf favori oynamanin
−%17,4'u, havuz ortalamasindan (~−%49) yaklasik **30 PUAN IYI**. Yani secim gercekten deger
cikariyor; kesinti onu yutuyor. Canliya dokunulmadi.**
- **Basarisiz ilk deneme (kayit icin):** "tum kombinasyonlari oynasak ne donerdi" yontemi
  DENENDI ve GECERSIZ cikti. Medyan kombinasyon 582.120 -> tam kapsama maliyeti havuzdan buyuk;
  olculen sey kesinti degil "havuz/kapsama-maliyeti orani" oldu. Yillara gore %1,3 -> %27,5
  tirmanmasi da enflasyon (temettu nominal TL, kombo sayisi degil). **Yontem terk edildi.**
- **Calisan yontem — AGF:** ham sonuc feed'inde `agf` blogu her Altili ayaginda her ata havuzun
  YUZDE KACININ geldigini veriyor (AGFORAN). Pari-mutuel kimligi:
  `temettu = birim x (1 - kesinti) / q`  ->  `1 - kesinti = temettu x q / birim`
  q = kazanan kombinasyona gelen pay = 6 ayagin AGF paylarinin CARPIMI (bagimsizlik varsayimi).
- **SONUC (1283 olay, 2026):** ima edilen geri donus **medyan %51,4** (ceyrekler %26,4 / %51,4 /
  %73,5) -> **ima edilen kesinti medyan %48,6**. Kazanan kombinasyona gelen pay medyan %0,0027.
- **VARSAYIM UYARISI:** oyuncular ayaklari BAGIMSIZ oynamaz (herkes ayni favoriyi banker yapar),
  gercek q populer kombinasyonlarda carpimdan BUYUK. Bu yuzden tahmin gurultulu (ceyrek araligi
  genis) ve nokta degeri +/- birkac puan oynayabilir. Buyukluk mertebesi (~%45-50) saglam;
  kesin deger icin TJK'nin resmi orani kaynaklanmali -> BEKLEYENLER #8.
- **ASIL ONEMLI SONUC — K72 yeniden yorumlaniyor:** ayni zeminde uc getiri:
  | strateji | geri donus |
  |---|---|
  | havuz ortalamasi (= 1-kesinti) | ~%51 |
  | rastgele kombinasyon (K72) | %40,4 |
  | **bizim orta / saf favori (K72)** | **%80,6 / %82,6** |
  Yani favori-agirlikli oynamak havuz ortalamasini **~30 puan**, rastgeleyi **~42 puan** yeniyor.
  **Favori-longshot yanliligi Altili havuzunda COK guclu:** kalabalik surprizlere fazla, favorilere
  az para yatiriyor. Model/secim GERCEKTEN deger cikariyor — ama %49'luk kesinti onu yutuyor.
- **CERCEVE DEGISIMI:** "sistem ise yaramiyor" degil; **"sistem havuzu yeniyor ama vergiyi
  yenemiyor."** K1 (etkin pazar) tezi nuanslanmali: pazar ETKIN DEGIL (favori yanliligi var),
  ama kesinti o verimsizligi somurmeye yetmeyecek kadar buyuk. Bu, 11 negatif kenar testinin
  neden hepsinde "yaklastik ama yetmedi" cikti sorusunun cevabi olabilir.
- **PRATIK SONUC DEGISMEDI:** oynanacak bir sey yok; −%17 ile −%19 arasi kayip hala kayip.

## 2026-07-31 — K74: Altili havuzu YANLILIK HARITASI — yanlilik gercek, yeri de belli

**K74 — Altili havuzu ganyan havuzundan DAHA KOTU kalibre. En buyuk sapma: (a) AGF payi <%2 olan
atlar, (b) ganyanin AGF'den COK daha sansli gordugu atlar. Ikisi de kesinti sonrasi POZITIF
gorunuyor. Henuz kupon stratejisine cevrilmedi. `kod/altili_agf_yanlilik.py` (OFFLINE).**
- **Veri:** ham feed'in `agf` blogu = her Altili ayaginda her ata ALTILI HAVUZUNUN yuzde kaci
  geldigi. 448.897 at-satiri / 40.707 ayak. Yaninda gercek kazanan -> DOGRUDAN kalibrasyon.
  Karsilastirma: ayni atlarin ganyan (de-vig) olasiligi. Esik: K73'e gore geri donus %51,4 ->
  bir kovanin karli olmasi icin oran (gercek/AGF) > **1,95**.
- **(1) AGF kalibrasyonu — asil sapma en DIPTE:**
  | AGF payi | at | AGF | GERCEK | oran | net |
  |---|---|---|---|---|---|
  | **≤ %2** | 86.013 | %1,07 | **%2,93** | **2,73** | **1,41x KARLI** |
  | %2-5 | 87.786 | %3,36 | %4,10 | 1,22 | 0,63x |
  | %5-15 | 145.431 | ~%10 | ~%9,5 | ~0,96 | ~0,50x |
  | %15-30 | 67.520 | ~%20 | ~%21 | ~1,06 | ~0,55x |
  | > %45 | 7.162 | %55,9 | %52,1 | 0,93 | 0,48x |
  **Klasik favori-longshot yanliliginin TERSI:** Altili havuzunda kalabalik dip atlari
  neredeyse 3 KAT az fiyatliyor. Sebebi yapisal: kupon kuran oyuncu ayak basina 2-3 at
  yazabildigi icin sahanin altini TAMAMEN gormezden geliyor.
- **(2) Ganyan havuzu ayni atlarda cok daha duzgun:** dip kovada oran 0,72 (Altili 2,73),
  ust kovalarda 1,00-1,04. Yani ganyan pazari etkin, Altili pazari DEGIL.
- **(3) Kalibrasyon skorlari (dusuk=iyi):** Altili(AGF) Brier 0,08824 / log-kayip 0,31042;
  Ganyan(kamu) 0,08706 / 0,29657; **Bot2 0,08684 / 0,29570 (EN IYI)**. Bot2'nin ganyani da
  hafif gecmesi ilk kez olculdu.
- **(4) EN GUCLU SINYAL — iki havuzun AYRISMASI:** ganyan bir ati AGF'den ne kadar cok
  sansli goruyorsa, gercek kazanma o kadar yuksek:
  | kamu − AGF | at | AGF | kamu | GERCEK | AGF orani | net |
  |---|---|---|---|---|---|---|
  | > +0,10 | 11.414 | %5,96 | %24,45 | **%20,26** | **3,40** | **1,75x** |
  | +0,05..0,10 | 15.594 | %12,67 | %19,69 | %18,14 | 1,43 | 0,74x |
  | ~0 | 168.735 | %7,36 | %7,42 | %7,36 | 1,00 | 0,51x |
  | < −0,10 | 3.392 | %49,45 | %34,33 | %44,49 | 0,90 | 0,46x |
  Gercek oran ganyana degil ARAYA dusuyor -> her iki havuz da bilgi tasiyor ama Altili havuzu
  daha cok yaniliyor. **K72/K73 bulmacasinin cozumu bu:** bot2 (≈ganyan) ile oynamak Altili
  havuzunu 30 puan yeniyor cunku ganyan daha iyi kalibre.
- **KRITIK UYARI — bu henuz kar DEGIL:** yukaridaki oranlar TEK AYAK ifadeleridir. Altili 6
  ayagin CARPIMIDIR ve (a) 6 ayagi birden bu kovalardan secmek isabeti yerin dibine indirir,
  (b) temettu HAVUZLA SINIRLIDIR -- kimsenin yazmadigi kombinasyon teorik formulun dedigi kadar
  odeyemez, (c) q'yu ayak paylarinin carpimi saymak populer olmayan kombinasyonlarda en cok
  yanildigimiz yer. Yani "oran 2,73" gercek ama dogrudan kupona cevrilemez.
- **SIRADAKI SOMUT ADIM (henuz yapilmadi):** AGF canlida ZATEN VAR (defter.agf1, oran_log.agf1).
  Test edilecek strateji: kupon secimini bot2 yerine **(kamu − AGF) ayrismasi** ile agirliklandir
  -> gercek temettulerle 1455 OOS olayda backtest. Bu, K68'deki (bot1−kamu) ayrismasindan FARKLI
  ve daha guclu bir sinyal: orada carpan +%45 kupon degistiriyordu ama bulgu yoktu; burada
  olculen sapma 3,40 kat.
