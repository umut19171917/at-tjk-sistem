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

## 2026-07-31 — K75: Deger secimi (bot2/AGF^λ) — kenar GERCEK ama Altili'da HASAT EDILEMIYOR

**K75 — K74'un bulduğu yanlilik kupona cevrilemedi. λ arttikca ort. temettu YUKSELIYOR (mekanizma
calisiyor) ama isabet CÖKÜYOR; λ=1'de kupon 1318 olayda SIFIR kez tuttu. Canliya hicbir sey
eklenmedi. `kod/altili_deger_test.py` (OFFLINE).**
- **Mantik:** pari-mutuel'de EV ∝ Π(bot2_i / agf_i). Yani her ayakta "deger orani" en yuksek
  atlari almak EV'yi maksimize etmeli. Tek parametreli aile tarandi: **skor = bot2 / AGF^λ**
  (λ=0 mevcut sistem, λ=1 saf deger). Maliyet her λ'da BIREBIR AYNI (ayni ayak genislikleri),
  getiri GERCEK t6 temettusu, 1318 OOS olay (AGF'si tam olanlar).
- **SONUC (butce 96 / kapsam sekli):**
  | λ | 6/6 | isabet% | ROI(6) | ort.temettu |
  |---|---|---|---|---|
  | **0,00 (mevcut)** | **64** | %4,86 | **−%14,1** | 1.674 |
  | 0,25 | 48 | %3,64 | −%33,9 | 1.718 |
  | 0,50 | 40 | %3,03 | −%26,1 | 2.305 |
  | 0,75 | 15 | %1,14 | −%49,1 | **4.236** |
  | 1,00 | **0** | %0,00 | **−%100** | — |
  Butce 900'de ayni sekil: λ=0 → 215 isabet/−%53,3; λ=0,75 → 60 isabet/−%83,6; λ=1 → 3 isabet.
  Esli fark: λ≥0,75'te GA **sifir DISINDA ve NEGATIF** (kesin kotu); λ≤0,5'te sifiri iceriyor
  (fark yok). **Hicbir λ'da iyilesme YOK.**
- **MEKANIZMA DOGRU CALISIYOR AMA:** ort. temettu λ ile duzenli yukseliyor (1.674 → 4.236),
  yani secim gercekten "havuzun ucuz biraktigi" atlara kayiyor — K74 dogru. Ama isabet
  bundan daha hizli cokuyor.
- **KOK NEDEN — kenar neden hasat edilemiyor:** K74'teki 2,73 kat TEK AYAK ifadesidir. Altili
  ALTI ayagin CARPIMIDIR:
  (a) 6 ayagi birden ucuz atlardan secmek isabeti 0'a indirir (λ=1'de birebir bu oldu),
  (b) **temettu HAVUZLA SINIRLIDIR** — teorik EV 2,73^6 = 419 kat der, ama kimsenin yazmadigi
      kombinasyon havuzdan fazlasini odeyemez,
  (c) q'yu ayak paylarinin carpimi saymak tam da bu uc kombinasyonlarda kirilir.
  **Yani yanlilik GERCEK ama 6-ayakli carpim bahsinde yapisal olarak hasat edilemez.**
- **KAPANIS:** Bu, K74'un acik biraktigi tek kapiydi ve kapandi. Altili tarafinda denenmedik
  yontem kalmadi: kap boyutu (K57), budama (K57), dagitim (K65), bot1 (K67), bot1-kamu ayrismasi
  (K68), ayak korelasyonu (K70), katman getirisi (K71), taban cizgisi (K72), kesinti (K73),
  havuz yanliligi (K74), deger secimi (K75). **12 test, hepsi negatif.**
- **MANTIKLI SONRAKI HALKA (yapilmadi, veri gerekir):** yanlilik ayak basina gercek oldugu icin
  DAHA AZ AYAKLI bahislerde daha az yikici birlesir (4'lu = 4 carpim, 6'li = 6). BEKLEYENLER #2
  (4'lu/5'li kupon turleri) bu yuzden artik SOMUT bir gerekce kazandi. Onkosul: 4'lu/5'li
  temettu verisi arsivde YOK -> once veri toplanmali.

## 2026-07-31 — K76: Kupon zamani testi (BEKLEYENLER #4) kosuldu — ARAC EKSIGI BULUNDU ve duzeltildi

**K76 — 30-vs-15 dk testi kuruldu ve kosuldu; ama oran_log'un YAPISAL bir eksigi ortaya cikti:
kupon kurulma aninda 2-6. ayaklar hic kaydedilmiyordu. `oran_log.py` duzeltildi (ileri-yonlu).
Canli zamanlama 30 dk KALDI. `kod/altili_zaman_test.py` (OFFLINE) kalici arac olarak duruyor.**
- **Once bir dogrulama:** harman katsayilari defter.csv'den GERI CIKARILDI — ayni kosuda log-oran
  regresyonu: `ln(bot2_i/bot2_j) = α·ln(bot1_i/bot1_j) + γ·ln(kamu_i/kamu_j)`.
  **α=0,2095  γ=0,9495  R²=0,999606** (325 kosu, 2.775 gozlem). Model formu birebir dogrulandi.
  **Yan bulgu:** γ/α ≈ 4,5 -> Bot2 ezici agirlikla piyasayi takip ediyor. Bu, K67'deki
  "Bot2 favorisi = kamu favorisi %89,9" bulgusunun BAGIMSIZ dogrulamasi (ayri yontem, ayni sonuc).
- **ARAC EKSIGI (asil bulgu):** `oran_log` (K59) her ayagi KENDI postasina 45 dk kala logluyordu.
  Ama kupon TEK ANDA, 1. ayaga 30 dk kala kuruluyor — o anda 2-6. ayaklar kendi postalarina
  1-3 SAAT uzak, yani **hic kayda girmiyorlardi**. Kanit (29.07 ISTANBUL 1. Altili):
  `14:00 -> yalniz ayak1 (44,9 dk)`, `14:15 -> ayak1 (14,9) + ayak2 (44,9)`. Yani "kuponu 15 dk
  kala kursak ne olurdu" sorusu bu veriyle **CEVAPLANAMAZ** — 17 Altilidan yalnizca 3'u
  iki zaman diliminde de tam cikti.
- **DUZELTME (ileri-yonlu, K76):** yeni kural — pencerenin HERHANGI bir ayagi 45 dk icindeyse,
  o an henuz BASLAMAMIS TUM ayaklar loglanir. Dogrulama (kuru): 29.07 ISTANBUL'da 1. ayaga
  30 dk kala artik `ayaklar=[1..6], dk_kala=[30,60,90,120,150,180]`; 15 dk kala `[15,45,...,165]`.
  Yani kupon-kurma aninin TAM fotografi cikiyor. Gecmis veri degismez; birikim ileriye donuk.
  Yan etki: log hacmi ~3-4 kat artar (kabul edilebilir; haftalik commit'te zaten tasiniyor).
- **MEVCUT VERININ SOYLEDIGI (sinirli, karar DEGIL):** elde 3 tam Altili / 18 ayak. Eslesmis ayak
  kiyasi (orta config): ikisi de tuttu 9, **yalniz 30 dk 2**, **yalniz 15 dk 4**, ikisi de kacirdi 3.
  Net **+2 ayak**, isaret testi **p=0,688** -> istatistiksel olarak ANLAMSIZ. Yon hafifce "gec kur"
  lehine; bu, etkin-pazar beklentisiyle (son oran daha isabetli) ve K74 ile (ganyan iyi kalibre)
  tutarli — ama K70'te de gorduğumuz gibi ayak kazanmak kupon kazanmak demek degil.
- **KARAR:** canli zamanlama **30 dk KALIYOR**. Yeterli veri (hedef: ~40-50 tam Altili, ~2-3 ay)
  birikince `altili_zaman_test.py` tekrar kosulacak. BEKLEYENLER #4 acik kaliyor, tetigi degisti.

## 2026-07-31 — K77: Sayfadaki sıralama NE ZAMAN alınıyor (tekrar eden soruya kalıcı cevap)

**K77 — `altili.html`'deki "sistem sırası", kuponun kurulduğu andaki sıralama DEĞİLDİR.
Ölçüldü ve kayda geçti; kullanıcı bunu iki kez sordu, üçüncüde yeniden hesaplanmasın.**
- **Defter ne zaman yazılıyor:** 324 koşuda ölçüm — defter kaydı, o koşuya **medyan 4 dk kala**
  yazılıyor (çeyrekler 0 / 4 / 5 dk; **hepsi 0-5 dk aralığında**). Yani sayfadaki sıralama
  pratikte "posta anı" fotoğrafıdır.
- **Kupon ne zaman kuruluyor:** TEK ANDA, yalnızca **1. ayağa 30 dk kala** (`kupon_zamani_kur`,
  `dk_kala=30`). Altı ayağın seçimi de o tek anın oranlarıyla yapılır.
- **ARADAKİ FARK (ölçüldü, ayak bazında):**
  | ayak | kupon → sayfa farkı | sayfada "boşluklu" görünme oranı |
  |---|---|---|
  | 1 | 30 dk | %42,9 |
  | 2 | 60 dk | %53,9 |
  | 3 | 90 dk | %62,1 |
  | 4 | 120 dk | %41,5 |
  | 5 | 150 dk | %75,3 |
  | 6 | **180 dk** | **%82,4** |
  **Genel medyan fark: 90 dk.** İki sütun neredeyse birebir aynı yönde artıyor (4. ayak sapması
  açıklanamadı, muhtemelen gürültü) → "boşluk" olgusunun sebebi KESİN olarak zaman farkıdır.
- **SONUÇ:** Sistem sıralamada ASLA atlama yapmaz — beş dağıtıcının beşi de listeyi tepeden
  KESİNTİSİZ okur (`_sec_baz` kümülatif ekler, budayıcı en alttakini atar, `kupon_kur_acgozlu`
  ve `kupon_kur_ayrisma` `sr[j][:k]` alır). Kullanıcının gördüğü "1.-2. yazmış 3.'yü atlamış"
  görüntüsü, aldığımız atların SONRADAN sıra kaybetmesidir.
- **İstenirse çözüm (yapılmadı):** kupon kurulurken her atın o anki sırası `altili_kupon.csv`'ye
  yazılabilir (yeni sütun) → sayfa "kupon anındaki sıra / posta anındaki sıra" ikisini birden
  gösterir. İleri-yönlü, mevcut veriyi bozmaz. Kullanıcı "gerek yok" demişti (2026-07-25).

**K78 — Sayfa "biz tutturamadık" diyordu ama tutturmuştuk (HATA DÜZELTMESİ).**
Kullanıcı 29.07 İSTANBUL 1. Altılı kartında çelişki gördü: başlık `net +10.536,93 TL` yazarken
hemen altında *"bu Altılı'yı bilenlerin aldığı; biz tutturamadık"* diyordu. ACGOZLU900 6/6
tutturmuştu.
- **Sebep:** `_resmi_satir(k)` TEK kupon alıyordu ve çağrısı `_resmi_satir(kk[cfgler[0]])` idi →
  her zaman `KONFIG`'in ilk elemanı, yani **DAR**. Oysa o satır kartın başlığında, yani
  Altılı'nın TAMAMINI özetleyen yerde duruyor. DAR tutmayınca "tutturamadık" yazıyordu.
  K69'da kart başına tek tablo + yan yana sütun düzenine geçilirken bu satır tek-kupon
  varsayımıyla kalmış; kapsam değişti, satır değişmedi.
- **Düzeltme:** `_resmi_satir(kupolar)` artık o Altılı'nın TÜM türlerini alır, `kademe == 6`
  olanları toplar ve adıyla yazar: *"tutturan kuponumuz: ACGOZLU900 (1/5 tür)"*. Hiçbiri
  tutmadıysa kaç türün tutmadığını sayıyla söyler. `bitti` kontrolü de `all(...)` oldu.
- **Doğrulama:** sayfa yeniden üretildi, 30 kartın 3'ünde isabet görünüyor —
  30.07 ANKARA-1 `GENIS900, ACGOZLU900 (2/5)`, 29.07 İSTANBUL-1 `ACGOZLU900 (1/5)`,
  23.07 ANKARA-2 `ORTA (1/2)`. Ödül toplamı 13.442,86 + 12.983,18 + 17.934,50 =
  **44.360,54 TL** = kümülatif tablodaki Altılı ödülü (birebir tutuyor).
- **Yalnızca gösterim hatasıydı:** `_kupon_ozet` ödülü zaten config bazında doğru hesaplıyordu;
  ROI, kümülatif tablo, Telegram ve `altili_kupon.csv` etkilenmedi. Telegram mesajı zaten her
  türü ayrı satırda ✅/tutmadı diye yazıyor, orada yanlış iddia yoktu.
- **Aynı sayfada ikinci bayatlık:** giriş metni elle yazılmış *"Kupon dört boyda kurulur"* deyip
  4 tür sayıyordu; 7 tür var. Metin artık `_tur_ozeti()` ile **KONFIG'den üretiliyor**
  (aile başlıkları + kombo + dağıtıcı) → aynı şekilde bir daha bayatlayamaz.
- **Ders (tekrar eden kalıp):** K69'da olduğu gibi bir bileşenin kapsamı genişleyince (tek kupon
  → kupon ailesi), o kapsamı özetleyen metinler ayrıca gözden geçirilmeli. Elle yazılmış
  özet metin = bayatlamaya açık; üretilebiliyorsa üretilmeli.

**K79 — Açgözlü bankeri YANLIŞ ayağa koyuyor (ölçüm; kod değişmedi).**
Kullanıcı 28.07 KOCAELİ 2. Altılı'da fark etti: ACGOZLU900 son ayakta sistemin (yarış anı)
**8. sıradaki** atını TEK yazmış, 5/6'da kalmış. Kupon şekli `2×9×2×5×5×1 = 900`.
- **O vakada ne oldu:** kupon anındaki sıra diğer kuponlardan geri çıkarılabiliyor
  (dar=ilk2={7,9}, orta=ilk3={4,7,9}) → kupon anında sıra **9 > 7 > 4** idi. Oran seyri
  (`altili_oran_log.csv`, race_kod 226449): #9 → 4,35 (44 dk) → 8,05 (15 dk) → **13,65** (posta);
  #7 → 8,25 → 4,75 → **3,40**. Yani #9 kupon anında favoriydi, posta anında 8. sıraya düştü.
- **Sistematik mi? (n=27 Altılı, 12'sinde açgözlü var):**
  | ölçüm | 1. ayak | 6. ayak | p |
  |---|---|---|---|
  | seçimimiz = yarış-anı ilk-k (SONUÇTAN BAĞIMSIZ) | 15/27 | **4/27** | **0,0038** |
  | ACGOZLU isabet (6. ayak vs 1-5) | 45/60 | **4/12** | **0,0138** |
  | ACGOZLU isabet (tek-at ayak vs çok-at) | 44/60 | **5/12** | 0,0443 |
  | **ORTA** isabet (6. ayak vs 1-5) — KONTROL | 78/150 | **15/30** | **0,8446** |
- **Kontrol belirleyici:** 6. ayak zor DEĞİL — kapsam kuponu orada hiç kaybetmiyor (p=0,84).
  Sorun ayağın kendisi değil, açgözlünün o ayaktaki **genişlik kararı**.
- **Mekanizma:** kapsam dağıtıcısı sahanın kapsanmasına göre ölçer; 6. ayak en kalabalık saha
  (ort. 12,8 at vs 8-10) olduğu için oraya *daha çok* at verir (orta 2,8) ve korunur.
  Açgözlü ise olasılık vektörünün **sivriliğine** göre ölçer. 6. ayağın kupon anındaki oranları
  ~3 saat uzaktaki ince/durgun havuzdan gelir → sahte bir favori üretir → açgözlü "burada
  eminim" deyip *en az* at verir (2,2, tüm ayakların en azı). 12 bankerinin **6'sı** 6. ayakta.
- **İroni:** kullanıcının 25 Tem'de istediği "bir ayakta banker, gerisi geniş" şeklini üreten tek
  dağıtıcı açgözlü — ama bankeri en az bildiği ayağa koyuyor.
- **Karar: ŞİMDİLİK KOD DEĞİŞMİYOR.** Açgözlü n=12 Altılı; p=0,014 ipucu, kanıt değil.
  Ayrıca düzeltme için gereken "geç ayak ne kadar güvenilmez" katsayısı şu an **tahmin** olurdu.
  K76 düzeltmesinden sonra `oran_log` artık kupon anında TÜM ayakları kaydediyor → birkaç hafta
  içinde bu katsayı ölçülerek çıkarılabilir. O zamana kadar gözlem.
- **Uygulanabilir seçenekler (yapılmadı, konuşulacak):** (a) açgözlüye "ayak başına en az 2 at"
  kuralı; (b) geç ayaklarda olasılığı düzgüne doğru büzen güvenilirlik katsayısı; (c) ikisi de
  mevcut akışı bozmadan YENİ config olarak eklenir (K69 kalıbı) — çalışan ölçüm akışı
  ortasında değiştirilmez.

**K81 — İlk uzak-ayak ölçümü: K76 doğrulandı, bot1 kontrolü beni yanlış sonuçtan kurtardı.**

**(a) Sayfadaki "defter kaydı yok" uyarısı.** Kullanıcı 31 Tem 21:55'te üretilen `altili.html`'de
bugünün 24 ayağının HEPSİNDE bu uyarıyı gördü. İnceleme: bugünün verisi **eksiksiz** (24/24 ayak,
`model_rank` dolu). Sayfa 22:19'da yeniden üretilince uyarı **sıfıra düştü** (toplam 62 → 38).
Kalan 38 uyarı gerçek ve tarihsel: 20-30 Tem'de 15 koşunun defter kaydı hiç oluşmamış (PC o
anlarda kapalı) — kalıcı boşluk, düzeltilemez.
**21:55'teki üretimin neden başarısız olduğu BELİRLENEMEDİ.** defter.csv'nin bugünkü satırları
13:30–21:30 damgalı, yani o an dosyadaydılar; `defter.sonucla()` satır eklemez (yalnız sonuç
alanlarını doldurur). Uydurma sebep yazılmadı.
**Yapılan:** `_tum_siralama_html`'in iki dalı aynı cümleyi basıyordu → artık hangi dalın yandığı
ve hangi `race_kod` olduğu yazılıyor ("race_kod'u yok" / "defter'de 226499 kaydı bulunamadı").
Tekrarlarsa teşhis anlık olacak. **Pratik kural:** sayfayı takip'in gün-sonu geçişinden
(≈22:30) sonra tazele.

**(b) K76 DOĞRULANDI.** `oran_log`'da 31 Tem: **1144 uzak-ayak satırı, 16 koşu, en uzak 210 dk**.
Dün sıfırdı. BEKLEYENLER #9'un beklediği veri akıyor.

**(c) İlk λ ölçümü ve KRİTİK KONTROL.** Kovalara göre bot2 λ'sı çöküyor gibi göründü
(0,854 → 0,482 → 0,400 → 0,328 → 0,338). Hikâye doğrulanmış gibiydi. **Ama bot1 λ'sı da aynı
şekilde çöktü** (0,936 → 0,514 → 0,442 → 0,460 → 0,428). bot1 orana bakmaz, gün içinde
değişmez → eskime doğru olsaydı bot1 SABİT kalmalıydı.
**Sonuç:** düşüş eskimeden değil, **kova seçiminden** geliyor. Uzak ayaklar günün geç koşuları;
sahaları kalabalık (6. ayak ort. 12,8 at vs 8-10) → intrinsik olarak zor → iki model de orada
fazla iddialı görünüyor. A/B tabloları FARKLI koşuları kıyaslıyor = kusurlu tasarım.
Kontrolü araca baştan koymuş olmam bu yanlış sonucu engelledi.

**(d) Araç düzeltildi — C bölümü (eşleşmiş kıyas) eklendi.** Artık AYNI koşunun uzak (>60 dk)
ve yakın (≤45 dk) fotoğrafı kıyaslanıyor. bot1 vektörü iki anda da aynı olduğundan fark
tamamen piyasa bileşeninden gelir. İlk sonuç (16 koşu, tek gün):
| | λ | %90 GA |
|---|---|---|
| UZAKTAN | 0,454 | [0,07 – 0,95] |
| YAKINDAN | 0,638 | [0,27 – 1,00] |
| **FARK (uzak−yakın)** | **−0,184** | **[−0,57 – +0,20]** |
Aynı koşularda bot1 λ = 0,514 (zorluk taban çizgisi).
**Yön beklenen tarafta ama GA sıfırı içeriyor → SONUÇSUZ.** n=16 ve hepsi tek günden (aynı
pistler, aynı koşullar → gerçek belirsizlik GA'nın gösterdiğinden büyük).

**KARAR: açgözlü ELLENMEZ, veri birikmeye devam.** BEKLEYENLER #9'un tetiği artık C bölümüdür:
FARK'ın %90 GA'sı sıfırdan ayrılana kadar hiçbir şey değişmez. Bugünkü tablo bir ipucu değil,
sadece aracın çalıştığının kanıtıdır.

**K82 — Günlük hasar raporu: kesintinin sessiz maliyetini görünür kıldı.**
Kullanıcı bazı günler **~15:00-16:00 arası yarım saat** PC'yi kapatmak zorunda. Takip 15 dk'da
bir geçtiği için kesinti üç ayrı hasar yapabiliyor ve **üçü de sessizdi**.
- **Ölçüm — kupon kurma anları (12 gün, 34 Altılı):** 12:30(1) 13:00(3) 13:30(2) 14:00(4)
  14:45(1) **15:00(9)** 16:15(2) 16:45(1) 17:15(2) 17:30(1) 18:30(2) 18:31(4).
  **15:00 günün en yoğun anı — 12 günün 9'unda.** 15:30 ve 15:45'te bugüne kadar
  **hiç kupon kurulmamış.**
- **Üç hasar türü, artan maliyetle:**
  1. `DEFTER KAYDI YOK` (ucuz) — koşu deftere ancak takip [posta−5, posta+3] aralığında
     geçerse yazılır; kaçarsa "geçmiş" mühürlenir, **bir daha denenmez**. Kupon/isabet/
     kâr-zarar bozulmaz (sonuçlandırma sonuç feed'inden), ama sıralama görünmez ve o koşu
     **λ ölçümünden düşer** (altili_suruklenme bot1'i ve posta oranını defter'den alır).
  2. `GEC KURULDU` (sinsi) — kesinti pencereye kısmen denk gelirse kupon kaybolmaz, geç
     kurulur (30 dk yerine 5 dk kala). Kupon var görünür ama **farklı bir deneydir**;
     BEKLEYENLER #4 tam olarak bu soruyu ölçüyor → kirlenmiş zamanlama onu bozar.
  3. `KURULMAYAN ALTILI` (pahalı) — 30 dk'lık pencereye iki geçiş düşer; ikisi de kaçarsa
     o Altılı **hiç kurulmaz**: 7 kupon + o Altılı deneyden düşer.
- **Mevcut hasar (12 gün):** 6 gün temiz. 1 kurulmayan Altılı (21 Tem ANKARA-2),
  0 geç kurulan, 15 düşen defter kaydı. Ayrıca 2 "yarış sonrası kayıt" (20 Tem elle
  girilen kuponlar) — bu kesinti hasarı DEĞİL, ayrı sayılıyor ki istatistiği kirletmesin.
- **KULLANICIYA VERİLEN KURAL:** zorunlu kesinti **15:30'da başlasın, 15:00'te değil.**
  15:00'te kesmek günlerin çoğunda bütün bir Altılı'yı öldürür; 15:30'da kesmek 1-2 koşunun
  defter kaydına mal olur. 10:30 öncesi / 22:30 sonrası ise maliyet **sıfır**.
- **Araç:** `kod/kayip_raporu.py` + `kayip_bak.bat` (offline, salt-okunur, çift-tık).
  `altili_temettu.csv`'yi "hangi Altılı gerçekten koştu" kaynağı olarak kullanır →
  kurulmayan Altılı sayısı bir **alt sınırdır** (o dosyada eksik olan burada da görünmez).
- Not: `TJK Takip` görevinde `StartWhenAvailable=True` — PC dönünce kaçan geçişi telafi
  etmeye çalışır, yani 15:30 kesintisinde kayıp 2 koşu yerine 1 olabilir. `WakeToRun`
  kullanıcı isteğiyle kapalı (PC çantada), dokunulmadı.

**K83 — "Bugünkü Bursa'yı tutturmak için nasıl kupon gerekirdi?" (gerçek temettülerle ölçüm).**
31 Tem BURSA: 1. Altılı **244.060 TL**, 2. Altılı **1.302.968 TL** ödedi. Bizim en iyimiz 3/6 ve 2/6.
- **Kazananların bizim sıralamamızdaki yeri (KUPON ANINDA — bugün uzak-ayak verisi olduğu için
  ilk kez hesaplanabildi):** BURSA-1 → 3,1,6,4,3,8 | BURSA-2 → **7,8,4,4,3,8**.
  BURSA-2'de altı ayağın hiçbirinde kazanan ilk 3'te değil; 1,3 milyonun sebebi bu.
- **En küçük "ilk-N" kuponu:** BURSA-1 1.728 kombo (2.160 TL), BURSA-2 21.504 kombo (26.880 TL)
  — ama bu, hangi ayakta kaç at gerektiğini ÖNCEDEN bilmeyi varsayar. Gerçekçi tekdüze kupon
  (her ayakta ilk 7) her iki Altılı'yı da tutardı: **126.052 TL/Altılı**. Tek başına ikisi de kârlı.
- **AMA aynı genişliği her gün oynasak (22 Altılı, RESMİ temettülerle):**
  | ilk N | tutan | ort.kombo | bedel | ödül | ROI |
  |---|---|---|---|---|---|
  | 4 | 5/22 | 4.096 | 112.640 | 135.463 | +%20,3 |
  | 5 | 12/22 | 15.341 | 421.875 | 223.856 | −%46,9 |
  | 7 | 20/22 | 96.804 | 2.662.109 | 2.077.842 | −%21,9 |
  | 9 | **22/22** | 305.477 | 8.400.611 | 2.171.089 | **−%74,2** |
  | 12 | 22/22 | 767.443 | 21.104.670 | 2.171.089 | −%89,7 |
- **Ana bulgu: TUTTURMAK ZOR DEĞİL, BEDELİNİ ÇIKARMAK ZOR.** N=9'da 22 Altılı'nın 22'sini birden
  tutturuyorsun ve %74 kaybediyorsun. Genişlik 6. kuvvetle büyür, ödül büyümez — hatta küçülür,
  çünkü aynı kombinasyonu başkaları da bulur ve havuz bölünür.
- **N=4'ün +%20,3'ü TUZAK:** 135.463 TL ödülün 102.131'i (%75) TEK bir Altılı'dan (30 Tem KOC-1).
  O olay çıkarılınca ROI **−%70,4**. Temettü dağılımı zaten bunu söylüyor: medyan 17.262 TL,
  **en büyük 3 Altılı toplam ödülün %77'si**.
- **Tablo İYİMSER (dürüstlük notu):** yarış-anı sıralaması kullanıldı; kupon 30 dk önce kuruluyor.
  BURSA-2 kupon anında 21.504, yarış anında 6.720 kombo gerektiriyordu → gerçekte **3,2 kat**
  pahalı. Ayrıca n=22. Arşiv backtesti (K52, 1455 olay) da aynı yönde: −%32.

**K84 — Devir (kimse bilemedi) parası nereye gidiyor? Beklediğimiz yere DEĞİL.**
Kullanıcı sordu: "Bursa'yı bilen çıkmamışsa sonraki Altılı bizim için avantajlı olmaz mı?"
**Olgu düzeltmesi:** Bursa'da bilen ÇIKTI (temettü ödendi, devir yok). Ama fikir doğru olduğu
için arşiv tarandı — devir, Altılı'daki tek yapısal avantaj durumudur (devreden para kesintisini
zaten ödemiştir).
- **Devir NADİR:** 6.747 Altılı'da **24 devir = %0,36 → 281 Altılı'da bir.** Son yıllarda
  hızlanmış (2025: 7, 2026: şimdiden 4). Tutar büyük: medyan 6,16 M TL, en büyük 24,86 M
  (01/11/2025 ANKARA).
- **"Sonraki Altılı avantajlı" DOĞRULANMADI.** Aynı pistteki bir sonraki Altılı medyanda
  78.839 TL ödemiş (normal medyan 5.589 → 14,1 kat) — ilk bakışta doğrular gibi. Ama devrin
  görünen geri dönüşü **0,017×**: devreden 6 milyonun sonraki Altılı'da karşılığı ~%2.
  Para oraya gitmiyor; 14 kat büyük ihtimalle pist/zorluk etkisi.
- **Para AYNI GÜN, AZ-AYAK bahislerinde:**
  | | devir günü medyan | normal gün medyan | oran |
  |---|---|---|---|
  | t5 (5 ayak) | **198.489 TL** | 988 TL | **201 kat** |
  | t4 | 18.768 TL | 270 TL | 70 kat |
  | t3 | 3.840 TL | 76 TL | 51 kat |
  *Mekanizma kural kitabından doğrulanmadı; ölçülen şey güçlü bir birliktelik. Ama yön açık:
  6/6 sahipsiz kalınca değer az-ayak bahislerinde toplanıyor.*
- **Devirlerin %71'i bizim OYNAMADIĞIMIZ pistlerde:** ŞANLIURFA(8), DİYARBAKIR(5), ELAZIĞ(2),
  ADANA(1), DBAKIR(1) = 17/24 — hepsi `EXCL` listesinde. Kalan 7: BURSA(4), İSTANBUL, İZMİR, ANKARA.
- **SONUÇ:** devir sonrasını beklemek işe yaramaz. Asıl bulgu BEKLEYENLER #2'yi (4'lü/5'li)
  güçlendiriyor: Altılı'nın kayıp kuyruğu 5-ayak bahsinde toplanıyor.

**K85 — K84'ÜN MEKANİZMASI YANLIŞTI (düzeltme) + TJK bahis ürünlerinin haritası.**
K84'te "6/6 sahipsiz kalınca değer az-ayak bahislerine akıyor" yazmıştım ve mekanizmanın
doğrulanmadığını not düşmüştüm. Doğrulandı: **yanlıştı.**
- **Kanıt 1 (ham metin, 15/07/2026 ELAZIG):** Altılı devir kombinasyonu `12/8,10/8/6/4/12`;
  aynı kartta `SIRALI 5 Lİ BAHİS(6/13/1/2/11): 1.587.498,75TL`, `4'LÜ GANYAN(8/6/4/12):
  75.602,45TL`, `3'LÜ GANYAN(6/4/12): 7.105,90TL` — **bambaşka koşular/kombinasyonlar.**
- **Kanıt 2 (kesin):** SIRALI 5 Lİ'nin **kendi 1201 devri** var. Altılı'nın teselli katmanı
  olsaydı kendi başına devredemezdi. → `altili_tam.csv`'deki `t5_div/t4_div/t3_div` sütunları
  Altılı katmanı DEĞİL, **aynı kartta koşan ayrı ürünlerin** ödemeleridir.
- **DOĞRU AÇIKLAMA:** devir günlerindeki 201 kat, para akışı değil **ortak sürpriz**.
  Altılı'yı kimsenin bilemediği gün, aynı kartın koşuları sürpriz üretmiştir; o koşuları
  paylaşan diğer çok-ayaklı bahisler de büyük öder. Korelasyon var, nedensellik yok.
- **K84'ün geçerli kalan kısmı:** devir sayıları, sıklıklar, "sonraki Altılı avantajlı
  DEĞİL" bulgusu (0,017× geri dönüş) ve devirlerin %71'inin EXCL pistlerinde olması.

**ÜRÜN HARİTASI (arşiv taraması, 4.219 kart / 2021-2026):**
| ürün | devir | kart başına | medyan devir | hangi yıllarda var |
|---|---|---|---|---|
| SIRALI 5 Lİ BAHİS | 1201 | **%28,5** | 32.291 TL | 2021-2026 (kartların ~%80'i) |
| **7'Lİ GANYAN** | **91** | %2,2 | **508.874 TL** | **YALNIZ 2026** (kartların %75'i) |
| 6'LI GANYAN (Altılı) | 24 | %0,6 | 6.160.747 TL | 2021-2026 (%100) |
| 7'Lİ PLASE | 14 | %0,3 | 631.682 TL | 2021-2026 |
| 5'Lİ GANYAN | 3 | %0,1 | 6.086.044 TL | 2021-2026 (%100) |
- **EN ÖNEMLİ BULGU: 7'Lİ GANYAN 2026'da çıkmış YENİ bir üründür.** 2021-2025 kartlarının
  **%0'ında**, 2026 kartlarının **%75'inde** görünüyor (yılda 40 kart örneklemesi). 91 devrinin
  tamamı 2026'da. Yeni ürün = kalabalık henüz kalibre olmamış + devir sık.
  Bu, projede bugüne kadar bulunan **tek yapısal açıklık adayıdır.**
- **3'lü/4'lü/5'li/6'lı GANYAN** = ardışık N koşunun kazananları. **SIRALI 5 Lİ BAHİS** ise
  TEK koşuda ilk 5'i sırasıyla bilmek — o yüzden %28,5 devrediyor (zorluğu farklı sınıftan).
- **KOD/VERİ DURUMU:** bu ürünlerin olay tabloları YOK (`altili_tam.csv` sadece Altılı için).
  Backtest öncesi arşivden olay tablosu üretmek gerekir — ham veri mevcut, iş yapılabilir.

**K86 — Ürün bazında kesinti oranı ARANDI: TJK yayımlamıyor (BEKLEYENLER #8 kapanmadı).**
K85'te 7'li ganyanın yeni ürün olduğu bulununca "hangi ürünün kesintisi düşük" sorusu kritik
hale geldi. Kullanıcı aratma dedi; arandı.
- **Yönetmelik** (At Yarışları Müşterek Bahisler Yönetmeliği) oran vermiyor → 5602 sayılı Kanun'a
  atıf yapıyor. **5602 sayılı Kanun** ürün bazında oran koymuyor: yıllık ikramiye toplamı
  hasılatın **%40-93** aralığında olmak zorunda (md. 4/2), ürün bazındaki oranı **TJK belirliyor
  ve yayımlamıyor**. At yarışlarında şans oyunları vergisi **%7** (md. 6/4).
- **Elde edilen resmî veriler:** birim fiyatlar — 3'lü 2,00 · 4'lü 1,75 · 5'li 1,50 · 6'lı 1,25 ·
  **7'li 2,00** · Sıralı 5'li 1,25 TL. Asgari iştirak 20 TL, azami 12.000 TL.
  → **7'li, Altılı'nın 1,6 KATI birim maliyetli**; genişlik 7. kuvvetle büyürken bu da biniyor.
- **Devir kuralı resmen doğrulandı:** devreden tutar aynı oyunun **bir sonraki yerli yarış
  gününe** aktarılır. K84/K85'teki devir okuması geçerli.
- **SONUÇ: BEKLEYENLER #8 web aramasıyla kapanmaz.** Yöntem önerisi (ganyan-türevli P + Altılı
  üzerinden kalibre edilmiş düzeltme katsayısı) BEKLEYENLER #8'e yazıldı; **fizibilite denemesi
  yapılmadı, onay bekliyor.**

**K87 — Kupon türlerinin ayak-ayak kıyası: beceri sıralaması genişliğin TERSİ; 900'lü üçlü
ise henüz AYIRT EDİLEMİYOR.** (Ara okuma — karar değil, taban çizgisi.)
- **Yöntem notu:** config'lerin kupon sayıları ve genişlikleri farklı → ham isabet kıyası geniş
  kuponu haksız kazandırır. İki düzeltme: (1) **eşleşmiş küme** — yedi config'in de bulunduğu
  11 Altılı / 66 ayak; (2) **KAZANÇ = isabet / rastgele**, burada rastgele = ort(seçilen at /
  saha). Aynı genişlikte rastgele seçseydik ne olurdu; 1,00 = beceri yok, sadece genişlik.
- **Eşleşmiş 66 ayak:**
  | config | isabet | rastgele | KAZANÇ | ort.at |
  |---|---|---|---|---|
  | **dar** | %30,3 | %17,4 | **1,74** | 1,7 |
  | orta | %36,4 | %22,3 | 1,63 | 2,2 |
  | genis | %42,4 | %26,2 | 1,62 | 2,5 |
  | genis900 | %51,5 | %31,8 | 1,62 | 3,1 |
  | ayrisma900 | %59,1 | %39,9 | 1,48 | 3,9 |
  | bot1_900 | %53,0 | %36,2 | 1,47 | 3,6 |
  | acgozlu900 | %56,1 | %40,8 | 1,37 | 4,0 |
- **BULGU 1:** ham isabet sıralaması = genişlik sıralaması (beceri ölçmez). KAZANÇ'a göre
  sıralama **tersine döner**: modelin kenarı TEPEDE yoğun, genişledikçe seyreliyor.
  Tüm geçmişte fark daha keskin: dar 2,21 → ayrisma900 1,48.
- **BULGU 2 (BEKLEYENLER #9 için önemli):** 900 bütçeli üçlü eşleşmiş McNemar ile
  **AYIRT EDİLEMİYOR** — acgozlu 37 vs ayrisma 39 (p=0,500), acgozlu 37 vs bot1 35 (p=0,851),
  ayrisma 39 vs bot1 35 (p=0,572). n=66 ayak. **Nominal sıralamayı sonuç sanma.**
  - İzlenecek iki nominal işaret (İDDİA DEĞİL): (a) ayrışma, açgözlünün tuttuğu hiçbir ayağı
    kaçırmamış (yalnız-açgözlü 0, yalnız-ayrışma 2) ve biraz daha az atla; (b) **bot1_900
    piyasaya HİÇ bakmadan başa baş gidiyor** (3,6 atla 35 vs 4,0 atla 37) — bot2'nin
    ağırlığının %82'si piyasadanken dikkat çekici. bot1_900 zaten bunu ölçmek için kuruldu.
- **BULGU 3:** kapsam merdiveninde tek anlamlı adım genis→genis900 (p=0,031, +6 isabet).
  Eklenen her at ~0,12-0,17 ayak isabet satın alıyor, merdiven boyunca sabit.
- **PARA:** eşleşmiş 11 Altılı'da hiçbiri 6/6 yapmadı → yedisi de −%100. Tüm geçmişte yalnız
  orta (1 isabet) ve acgozlu900 (2 isabet) gelir üretti; 1-2 olaydan hüküm çıkmaz.
- **ÖZET GERİLİM:** dar en iyi seçiyor ama 41 kuponda bir kez bile 6/6 yapamadı (sıfır gelir);
  geniş olanlar ara sıra tamamlıyor ama bedelini çıkaramıyor. **İyi seçmek ile kazanmak farklı
  şeyler ve biz birincisinde iyiyiz.** K52/K72'nin bulgusuyla tutarlı.

**K88 — Kupon genişliği modelin güveninden DEĞİL, bütçenin 6. kökünden geliyor. Saha
büyüklüğü hiç fiyatlanmıyor.** (Kullanıcı sordu: "sistem ayaklardaki at sayısını dikkate
alıyor mu?")
- **Kodda hiçbir dağıtıcı saha büyüklüğünü AÇIKÇA kullanmıyor.** `kupon_kur` kümülatif kapsama
  bakar, açgözlü/ayrışma olasılık şekline; saha yalnızca üst sınır olarak geçer
  (`k[j] >= len(sr[j])`).
- **Kapsam ailesi saha büyüklüğünü fiiliyatta da GÖRMEZDEN geliyor.** Saha 4-7'den 12+'ya
  (üç kat) çıkarken seçilen at sayısı sabit:
  | config | saha 4-7 | 8-9 | 10-11 | 12+ | korelasyon |
  |---|---|---|---|---|---|
  | dar | 1,8 | 1,6 | 1,6 | 1,7 | −0,04 |
  | orta | 2,2 | 2,1 | 2,1 | 2,3 | +0,17 |
  | genis | 2,4 | 2,5 | 2,6 | 2,5 | +0,02 |
  | genis900 | 3,1 | 3,0 | 3,1 | 3,0 | −0,15 |
- **SEBEP (asıl bulgu): genişlik = bütçenin 6. dereceden kökü.**
  `24^(1/6)=1,70` · `96^(1/6)=2,15` · `288^(1/6)=2,58` · `900^(1/6)=3,11` — gözlenen
  ortalamalarla birebir. Yani **kapsam eşiği (0,75) ve banker eşiği (0,70) pratikte neredeyse
  hiç bağlayıcı olmuyor**; her seferinde kombinasyon tavanı bağlıyor ve kuponu altı ayağa
  eşit bölüyor.
  → **Kullanıcının 25 Tem'deki "her ayakta aşağı yukarı aynı sayıda at var" gözleminin
  gerçek sebebi budur** (K65'te budayıcıya bağlanmıştı; kök neden bütçe aritmetiğidir,
  model kararsızlığı değil).
- **Açgözlü/ayrışma tepki VERİYOR:** küçük sahada 2,5 at, büyük sahalarda ~4,0-4,4
  (korelasyon +0,13). Kalabalık sahada olasılık yayvanlaşır → eklenen at daha çok olasılık
  satın alır → açgözlü kendiliğinden oraya kayar. Saha büyüklüğünü dolaylı fiyatlıyor.
- **SAHA ÖNEMLİ Mİ? EVET (orta ile ölçüldü):**
  | saha | ort.at | isabet | rastgele | kazanç |
  |---|---|---|---|---|
  | 4-7 | 2,2 | **%65,4** | %35,1 | 1,86 |
  | 8-9 | 2,1 | %51,9 | %24,0 | 2,16 |
  | 10-11 | 2,1 | %43,9 | %20,5 | 2,14 |
  | 12+ | 2,3 | **%36,4** | %16,5 | 2,21 |
  İsabet %65→%36 düşerken at sayısı sabit. **Kazanç sütunu DÜŞMÜYOR** (hatta hafif artıyor)
  → model kalabalık sahada kötüleşmiyor; 14 attan 2 seçmek 6 attan 2 seçmekten doğası gereği zor.
- **SONUÇ:** Altılı altı ayağı birden ister → zincirin en zayıf halkası belirler. 5 atlık ayakta
  zaten %65'teyiz, 14 atlık ayakta %36'dayız; ikisine eşit at yazmak israf. **Kullanılmayan
  bir kaldıraç var: genişliği küçük sahalardan büyük sahalara kaydırmak.** Kod DEĞİŞMEDİ;
  BEKLEYENLER #9'a dördüncü aday olarak yazıldı.

**K89 — Dört 900'lük config'in eşleşmiş karşılaştırması (13 Altılı / 78 ayak, çift doğrulama).**
Tüm sayılar iki bağımsız yolla doğrulandı: canlı sonuçlar defter'den satır satır yeniden
hesaplandı (312 satır, 0 uyumsuzluk); bot1'in 6/6'sı resmî kombo ile ayrıca teyit edildi.
- **bot1_900 6/6 yaptı (03.08 BURSA-1, 19.283,18 TL)** → eşleşmiş kümede tek para kazanan
  (ROI +%39,3 — TEK olaydan, K83 tuzağı hatırda). Kritik an 2. ayak: kazanan #4 (6,90) —
  bot1 yazdı, ÜÇ kamu config'i birden kaçırdı. Kupon dağılımı: bot1 1×6/6 + 4×5/6 (13'te 5
  tepe); diğer üçünün toplamı 2×5/6.
- **Karakterler:** bot1 = sürpriz avcısı (13 benzersiz ayak; kazanan 15+ oranlıysa %42 vs
  diğerleri %25; ama favoriyi kaçırıyor — 5/6'larının 2'sinde yatan ayakta piyasa favorisi
  vardı, biri 1,50'lik). acgozlu900 = **0 benzersiz ayak**, KAZANÇ en düşük (1,31), hiç 5/6'sı
  yok, orta banda sıkışık. ayrisma900 ≈ açgözlünün üstkümesi (%71 birebir aynı kupon, Jaccard
  0,89; farklılaştığında 3-0 ayrışma lehine — K87'deki 2-0 büyüdü, yön dönmedi, p=0,25).
  genis900 = 8-15 oran bandında 0/7 (eşit bölme aritmetiği orta-pahalı sürprizi hiç almıyor).
- McNemar'da hiçbir çift anlamlı değil (en düşük p=0,25) — nominal sıralama hüküm değil.
- K79 notu: açgözlünün 6. ayak zaafı bu kümede görünmüyor (%62) — erken dönem verisiydi;
  λ ölçümü yine de sürüyor (BEKLEYENLER #9).

**K90 — Birleşim kuponu backtest edildi: KRİTER GEÇİLEMEDİ, canlıya ALINMADI.
Açgözlü iptal EDİLMEDİ (kontrol grubu); emeklilik kriteri önceden bağlandı.**
Kullanıcı önerdi (3 Ağu): bot1 kalsın, açgözlü iptal, K89 sentezinden yeni kupon (bütçe 2x'e
kadar). Konuşuldu; şu plan onaylandı:
- **Açgözlü iptal edilmedi.** İki gerekçe: (a) n=13 kuponla kazanan seçmek K87'nin kendi
  uyarısını çiğner; (b) acgozlu900, ayrisma900'ün **kontrol grubu** — silinirse "ayrışma
  ağırlığı işe yarıyor mu" sorusu (şu an 3-0, p=0,25) sonsuza dek ölçülemez kalır.
  **EMEKLİLİK KRİTERİ (önceden bağlandı):** 40 eşleşmiş kupon dolduğunda açgözlünün benzersiz
  ayak katkısı hâlâ 0 ise VE yalnız-X skoru hâlâ tek yönlüyse açgözlü kapatılır. BEKLEYENLER #9'da.
- **Birleşim tasarımı ÖNCEDEN sabitlendi:** her ayakta skor = max(bot1_norm, bot2_norm),
  normalize → aynı açgözlü dağıtım (`kupon_kur_birlesim`, altili_backtest.py — tek kaynak).
  Bütçe 1800. Başka varyant taranmadı (tek değişken ilkesi). **Karar kriteri sonuç görülmeden
  koda yazıldı:** birlesim1800, 1800'lük iki tek-bot kontrolünün İKİSİNDEN de hem ayak
  isabetinde hem 6/6'da düşük olmamalı.
- **Backtest (1433 OOS olay, sadece 6/6 öder, birim 1,25):**
  | config | ayak isabet | 6/6 | 5/6 | ROI | ort.temettü |
  |---|---|---|---|---|---|
  | acgozlu1800_bot2 | **%77,9** | **300** | 575 | −61,1 | 4.027 |
  | birlesim1800 | %76,7 | 259 | 590 | −60,1 | 4.778 |
  | acgozlu1800_bot1 | %72,1 | 188 | 474 | −29,2 [GA −61..+17] | 11.694 |
  - vs bot2-kontrol: ayak KALDI, 6/6 KALDI; eşli fark **anlamlı** (yalnız-birleşim 319,
    yalnız-kontrol 420, p=0,0002). vs bot1-kontrol: geçti — ama kriter İKİSİNİ de istiyordu.
  - **SONUÇ: RED — birlesim1800 canlıya alınmadı.** Aynı sonuç 900 bütçede de (189 vs 225,
    p=0,0001) → mekanizma sorunu, bütçe sorunu değil.
- **Başarısızlığın mekanizması (ÖLÇÜLDÜ, K85 dersi):** birleşimin kaybettiği 420 ayakta kazanan
  medyan **bot2-sırası 4** (dağılım 2-5'te yoğun); kazandığı 319 ayakta medyan **bot1-sırası 3**.
  Yani max-birleşim, bot2'nin orta sıralarını (piyasa bilgisi taşıyan bant) feda edip bot1'in
  tepesini alıyor; takas net −101 ayak. **K89'daki tamamlayıcılık gerçek ama max-birleşim onu
  kupona çevirmenin doğru yolu değil** — bot1'in benzersiz yakalayışları, bot2'nin orta
  bandından daha seyrek.
- ROI tarafında birleşim ile bot2-kontrol başa baş (−60 vs −61; birleşimin temettüsü daha
  yüksek) — ama karar İSABET kriteriyle bağlıydı ve sonuca bakıp kriter değiştirilmez.
- **NET DURUM: canlı sistem DEĞİŞMEDİ.** 7 config aynen; bot1 olduğu gibi; açgözlü emeklilik
  kriteriyle izlemede. `kupon_kur_birlesim` kodda duruyor (ileride farklı birleştirme
  denenirse zemin hazır), canlıda KULLANILMIYOR.

**K91 — "Bütçeyi 1800 yapsak 5/6'lar 6/6 olur muydu?" — ÖLÇÜLDÜ: %15-16 dönüşüyor,
YÜKSEK ÖDÜLLÜLER DÖNÜŞMÜYOR (77'de 3).** Kullanıcı sordu (3 Ağu); 1433 OOS olayda dört
config'in arşiv karşılığı 900 ve 1800 bütçeyle koşuldu, geçişler sayıldı.
| config | P(6/6) 900→1800 | 5/6@900 | dönüşen | marjinal ROI (ikinci 900) |
|---|---|---|---|---|
| genis | %12,1→%17,2 | 404 | 65 (%16) | −%59,8 |
| acgozlu | %15,7→%20,9 | 527 | 80 (%15) | −%58,2 |
| **bot1** | %8,6→%13,1 | 405 | 63 (%16) | **−%40,0** |
| ayrisma | %15,0→%21,1 | 533 | 87 (%16) | −%56,7 |
- **P(6/6) her config'de ~+5 puan artıyor AMA ikinci 900'ün marjinal ROI'si ilkiyle aynı
  sızıntıda** (~−%57-60; bot1 −%40). Kesinti duvarı artan her liraya aynı oranda uygulanır;
  bütçe büyütmek sızıntı ORANINI değiştirmez.
- **ASIL BULGU:** 100bin+ ödeyen 77 büyük-ödüllü 5/6'dan 1800 ile yalnız **3'ü** dönüştü.
  Anatomi: dönüşen 5/6'larda kaçan kazanan kendi sıralamada medyan **4.** (ucuz — medyan
  temettü 3-4bin); büyük ödüllülerde medyan **9.** Matematik: 2x bütçe = ayak başına 2^(1/6)
  ≈ **1,12x** genişlik (2-3 ayağa birer at) → 4.'yü yakalar, 9.'yu yakalamaz. 9.'ya inmek
  ~5-10x ister, o noktada bedel ödülü aşar (K83).
- **YORUM (kullanıcının sürdürülebilirlik çerçevesi):** "5'te kaldım, az kaldı" hissi bu
  ölçümle çürüdü — **5/6 bir yaklaşma sinyali DEĞİL.** Yüksek ödüllü 5/6'da kaçan at 9.
  sıradaysa "az kalmadı, beş ayak şans güldü" doğru okumadır. 1800'ün satın aldığı 6/6'lar
  tam da ucuz olanlar (kaçan yakınsa herkes yakındır → temettü düşük). Sürdürülebilir yol
  bütçe kolundan geçmiyor; aday adresler: yeni ürün (7'li, K85) ve devir anları (K84/K85).
- Canlı sistem DEĞİŞMEDİ; bütçeler 900 kaldı.

**K92 — BEKLEYENLER #9 TETİĞİ ATEŞLENDİ: uzak ayak gerçekten bozuyor. `acgozlu_v2` canlıya
alındı (8. config).** 31 Tem'de kuralı sonuç görmeden bağlamıştık: *"FARK'ın %90 GA'sı sıfırdan
ayrılana kadar hiçbir şey değişmez."* 7 Ağu'da ayrıldı.
- **Eşleşmiş ölçüm (aynı koşunun uzak ve yakın fotoğrafı), n=87 koşu:**
  | | λ | %90 GA |
  |---|---|---|
  | UZAK (>75 dk, ayak 3-6) | **0,650** | [0,465 .. 0,875] → **1'i İÇERMİYOR** |
  | YAKIN (≤75 dk, ayak 1-2) | 0,980 | [0,765 .. 1,220] → 1'i içeriyor |
  | **FARK** | **−0,330** | **[−0,545 .. −0,135] ANLAMLI** |
  60 dk eşiğiyle de aynı (n=97, fark −0,320 [−0,505..−0,135]). 31 Tem'de n=16 ve GA sıfırı
  içeriyordu; veri 5 katına çıkınca ayrıldı.
- **TAM λ(T) EĞRİSİ KURULAMADI — ve kurulmadı.** 7 mesafenin hepsinde fotoğrafı olan koşu
  yalnız 24; ölçülen eğri monoton bile değil (30dk 0,820 · 120dk 0,690 · **150dk 0,865** ·
  180dk 0,750) ve mesafe farklarının **hiçbiri** anlamlı değil. Bu bir eğri değil gürültü;
  6 parametreli λ tablosu kurmak doğrudan overfit olurdu (K33/K52 yasağı) → **REDDEDİLDİ.**
  Yerine iki seviyeli tasarım: tek ölçülmüş parametre λ_uzak = 0,65.
- **λ_yakın = 1,0 seçildi** (ölçülen 0,98, GA null'u içeriyor). Gerekçe: (a) GA 1'i içeriyor,
  (b) böylece acgozlu_v2 ile acgozlu900 arasındaki **her fark yalnızca uzak-ayak
  düzeltmesine** atfedilebilir — temiz atıf.
- **BACKTEST EDİLEMEZ** (K90'dan farkı bu): arşivde gün-içi oran serisi yok, `oran_log` zaten
  bu yüzden var. Yapılabilen tek kontrol geriye dönük **iç-örneklem** sağlamasıydı.
- **Geriye dönük kontrol (17 Altılı, 31 Tem'den beri, kupon-anı fotoğraflarıyla):**
  ayak isabeti v1 63/102 (%61,8) → v2 65/102 (%63,7); eşleşmiş yalnız-v1 3 / yalnız-v2 5,
  **p=0,727 (anlamlı DEĞİL)**. 5/6: 3→4. Ort. kombo 869→860 (bütçe korunuyor).
  **Tasarım niyeti DOĞRULANDI:** yakın ayak 4,41→2,97 at (daraldı), uzak ayak 4,00→**4,74** at
  (genişledi). Sentetik testte de altı ayak birebir aynı girdiyken 3-3-3-3-3-3 → 3-1-4-4-4-4.
  *Bu iç-örneklem sağlamasıdır, doğrulama değil — λ aynı dönemden ölçüldü. Amacı "tasarlandığı
  işi yapıyor mu + bariz zarar var mı" idi; ikisi de cevaplandı.*
- **CANLIYA ALINDI:** `acgozlu_v2` (kombo 900, dağıtım "kalibre", puan bot2, aile "kalibre").
  Mevcut 7 config'e DOKUNULMADI. Ölçüm ileri-yönlü: acgozlu900 ile ayak-ayak kıyaslanacak
  (tek fark uzak-ayak düzeltmesi).
- **BEKLENTİ (önceden yazıldı):** ROI'yi kurtarmayacak (K93). Değeri para değil cevap:
  "eskimeyi düzeltmek ayak isabetini artırıyor mu?" v3 (banker hak edilsin) ve v4 (saha
  genişliği) BEKLETİLDİ — tek seferde tek değişken.

**K93 — Kâğıt ROI backtest'e yakınsadı: +%18,8 → −%33,3. Ölçüm aygıtı çalışıyor.**
31 Tem'de kullanıcı "+%18,8, kardayız" demişti; o gün 106 kuponun 4'ünün gelirin %100'ünü
ürettiğini, P(≥+%18,8)=%9,2 olduğunu ve gerçekte −%19,4 olan bir stratejinin bile 5 ay sonra
%25,7 ihtimalle pozitif görüneceğini hesaplamıştık. **Bir hafta içinde gerçekleşti.**
| tarih | kümülatif Altılı ROI |
|---|---|
| 23 Tem | +%1394 (ilk 6/6) |
| 30 Tem | **+%18,8** |
| 2 Ağu | −%49,4 |
| 6 Ağu | **−%33,3** |
- **Yakınsama iki üründe birden:** Altılı −%33,3 vs backtest −%32 (K52). Ganyan (955 kâğıt
  kupon) **−%25,4** vs ganyan kesintisi %25,5 (K46). İki bağımsız üründe teori ne diyorsa o.
- **YORUM (kullanıcının sürdürülebilirlik çerçevesi):** bu başarısızlık değil, **ölçüm aygıtının
  doğrulanması**. Sistem kenarı olmayan bir oyunda tam kesinti kadar kaybediyor. "Kupon şeklini
  iyileştirerek kâra geçme" yolu bu tabloyla kapandı — K83'te de ölçülmüştü (hiçbir genişlik
  kârlı değil, N=9'da 22/22 tutturup −%74).
- **Yön:** kalan iki açık adres ürün tarafında — **7'li ganyan** (2026'da çıkmış YENİ ürün,
  kalabalık kalibre olmamış, 91 devir; K85) ve **4'lü ganyan** (kısa zincir; BEKLEYENLER #2).
  İkisi de arşivden çıkarılabilir → **backtest EDİLEBİLİR**, acgozlu_v2'nin aksine.

**K94 — Ürün bazında kesinti ÖLÇÜLDÜ: 4'lü/5'li Altılı'dan sadece 2-3 puan iyi, 7'li EN KÖTÜ
(%57,6). "Yeni ürün fırsatı" hipotezi ÇÜRÜDÜ.** K86'da TJK'nın oranı yayımlamadığını bulmuştuk;
ölçümle çıkarıldı.
- **VERİ ALTYAPISI KURULDU:** `veri/nli_ganyan.csv` — ham arşivin 4.232 kartından çıkarılan
  **27.442 olay** (3/4/5/6/7'li ganyan; tarih, pist, ayak race_kod'ları, kazanan kombo, temettü,
  devir). Yapı çözüldü: **temettü bahsin BİTTİĞİ koşuya ilişir, ayaklar o koşuda biten N ardışık
  koşudur.** Fizibilite: çıkarılan olayların **%99,1-100'ünde** ayaklar gerçek kazananlarla
  doğrulandı. Mevcut hiçbir dosya değiştirilmedi.
- **DEVİR ORANLARI (asıl sürpriz):**
  | ürün | ödendi | devir | devir oranı |
  |---|---|---|---|
  | 3'lü | 8.060 | 0 | %0 |
  | 4'lü | 5.691 | 0 | %0 |
  | 5'li | 6.516 | 3 | %0,05 |
  | 6'lı | 6.789 | 24 | %0,35 |
  | **7'li** | 255 | **104** | **%29,0** |
- **İKİ ARTIFAKT YAKALANDI VE DÜZELTİLDİ (ilk tablo yanıltıcıydı):**
  1. **Enflasyon:** tarihsel temettüleri bugünün birim fiyatıyla bölmek kesintiyi 2021'de %57,
     2026'da %15 gösteriyordu. Kesinti böyle davranmaz — birim fiyatlar da o yıllarda düşüktü.
     K73'te aynı tuzağa düşülmüştü. **Çözüm: yalnız 2026.** (7'li zaten sadece 2026'da var →
     adil kıyas ancak böyle olur; ham tablo 7'li'yi *en ucuz* gösteriyordu, tam ters.)
  2. **Kalibrasyon üstel olmalı:** ganyan-türevli P'nin ayak başına yanlılığı k ise N ayaklı
     üründe k^N birikir → sabit fark düzeltmesi YANLIŞ. `log(1−kesinti_est) =
     log(1−kesinti_true) + N·log k`; k, 6'lı üzerinden çözüldü (**k=0,978**, ayak başına
     P'yi %2,2 şişiriyor).
- **SONUÇ (2026, standart tarifeli pistler, 2.526 olay):**
  | ürün | n | KALİBRE KESİNTİ | %90 GA |
  |---|---|---|---|
  | 3'lü | 712 | %45,4 | [43,1 .. 46,8] |
  | 4'lü | 402 | %45,6 | [41,0 .. 47,8] |
  | 5'li | 518 | %46,8 | [43,8 .. 49,0] |
  | 6'lı | 662 | %48,6 | *(kalibrasyon çapası — doğrulama değil)* |
  | **7'li** | 232 | **%57,6** | **[51,8 .. 62,7]** |
- **KARARLAR:**
  - **7'li REDDEDİLDİ.** "Yeni ürün, kalabalık kalibre olmamış" hipotezi (K85) çürüdü:
    kesintisi en yüksek (%57,6, GA 6'lı'nın üstünde), birim fiyatı en pahalı (2,00 TL =
    Altılı'nın 1,6 katı) ve genişlik 7. kuvvetle büyüyor. %29 devir oranı ürünün *zorluğunun*
    göstergesi, fırsatın değil — devreden para yeni çekilişte yine %57,6 kesintiyle karşılaşıyor.
  - **4'lü/5'li: heyecan yok.** Altılı'dan 2-3 puan iyi, güven aralıkları örtüşüyor. Bizim
    ölçülmüş kenarımız SIFIR (K52/K93) → 45 ile 49 arasındaki fark −%45 ile −%49 kayıp demek.
    Kupon sistemi kurmaya değmez.
  - **Ürün kolu KAPANDI.** Kesinti duvarı 3'lüden 7'liye kadar %45-58 bandında; hiçbir ürün
    "sürdürülebilir kazanç" için yapısal açıklık sunmuyor.
- **DÜRÜSTLÜK NOTU:** 6'lı satırı tanım gereği %48,6 çıkar (çapa). Diğerlerinin değeri
  "ayak başına yanlılık ürünler arası aynı" varsayımına dayanır. Ama SIRALAMA bu varsayımdan
  görece bağımsız ve 7'li'nin kötülüğü çok belirgin (ham iade 0,363 vs 6'lı 0,449).

**K95 — Ayrışma mekanizması kuponu ancak %24 kıpırdatıyor: ayrisma900 bir BULGU değil,
GÜÇSÜZ BİR TEST.** Kullanıcı fark etti (7 Ağu): "açgözlü ve ayrışma neredeyse tıpatıp kupon
yapıyor". Ölçüldü, doğru — ve sebebi bulundu.
- **Örtüşme (156 ortak ayak / 26 Altılı, w=1,0):** birebir aynı ayak **118/156 = %75,6**
  (K89'da %71'di, veri büyüdükçe arttı) · ortalama Jaccard **0,916** · ayak genişliği farkı
  ortalama −0,08 at · **Altılıların %50'sinde altı ayağın altısı da birebir aynı.**
- **SEBEP (mekanizma teşhisi):** ağırlık çarpanı `1 + w·D`. Ölçüm: D ortalaması 0,239,
  **bir Altılı içindeki ayaklar arası std yalnız 0,070**; Altılı-içi en yüksek/en düşük çarpan
  oranı medyan **1,166**. Yani altı ayağın ağırlıkları birbirinden ancak %17 farklı.
  Açgözlünün kazanç/bedel oranları arasındaki farklar çoğu zaman bundan büyük → sıralama
  değişmiyor. **w=1,0 mekanizmayı fiilen etkisiz bırakıyor.**
- **Sonuç okuması:** ayrıştığı 38 ayakta skor yalnız-açgözlü 2 / yalnız-ayrışma 4 (p=0,688).
  Yön K87'den beri hep ayrışma lehine (0-2 → 0-3 → 2-4) ama hiç anlamlı olmadı — çünkü test
  edilen ayak sayısı 38. **Bu bir tasarım kusuru, bulgu değil.** 500 ayakta bile ~120 ayrışma
  olur; bu dozla soru muhtemelen KALICI OLARAK cevapsız kalır.
- **w=1,0 K68'de BİLEREK sabitlenmişti** (en iyi w'yi seçmek overfit olurdu). Şimdi w'yi
  yükseltmek meşru olabilir AMA yalnızca **sonuçtan bağımsız** bir ölçütle (ör. "ayakların
  ~yarısı farklılaşsın"), isabete bakarak DEĞİL. Karar kullanıcıya bırakıldı; **kod
  DEĞİŞMEDİ.**

**K96 — Harman ağırlıkları (α/γ) DEĞİŞMEMELİ: yürüyen-ileri testle doğrulandı. bot1'in katkısı
gerçek ama çok küçük.** Kullanıcı sordu: "kupon bazında verilere bakınca bu oranlarda değişiklik
gerekli mi?"
- **YÖNTEM NOTU:** kupon bazında cevaplanamaz — bot1_900'ün +%105 ROI'si 2 olaydan geliyor
  (K93 dersi). Doğru alet **ayak seviyesi**: 2026'da 2.513 koşu. Dürüst kurulum: mevcut
  ağırlıklar 2024'te fit edilmişti → **2025'te yeniden fit edildi, ikisi de 2026'da test edildi.**
- **Ağırlıklar yıllar arası KARARLI:**
  | | α | γ | bot1 payı |
  |---|---|---|---|
  | mevcut (2024 fit, canlıda) | 0,208 | 0,950 | %18 |
  | 2025'te yeniden fit (havuz) | 0,200 | 0,960 | %17 |
  | İngiliz ayrı | 0,240 | 0,940 | %20 |
  | Arap ayrı | 0,180 | 0,960 | %16 |
- **2026 TESTİ (koşu başına ort. log-olabilirlik):** yeniden-fit ağırlıklar mevcut olanlardan
  **hiç iyi değil** — fark +0,00014 (havuz), −0,00037 (İngiliz), −0,00051 (Arap);
  **%95 GA'ların hepsi sıfırı içeriyor.** → **DEĞİŞİKLİK GEREKSİZ.**
- **ASIL BULGU — bot1'in katkısının büyüklüğü:**
  | | log-olabilirlik / koşu |
  |---|---|
  | harman (0,21/0,95) | **−1,7674** |
  | yalnız kamu | −1,7749 (harman +0,0075 iyi) |
  | yalnız bot1 | −1,9300 (harman +0,163 iyi) |
  bot1, kamuya göre kazanan atın tahmin olasılığını ortalama **%0,75** artırıyor. Gerçek ama
  minik. bot1 tek başına belirgin KÖTÜ.
- **bot1_900 HAKKINDAKİ YANILGI DÜZELTİLDİ:** 25 benzersiz ayak "bot1 daha iyi" demek değil,
  **"bot1 FARKLI"** demek. Farklı ≠ iyi. Tahmin gücü zayıf; ama kalabalıktan koptuğu için
  tuttuğunda az kişiyle bölüşüyor (iki 6/6'sının temettüleri bunu gösteriyor) — K67'nin öngörüsü.
- **bot1 ağırlığını artırmanın mantığı isabet değil FİYAT olurdu** (bilerek isabetten feragat
  edip ayrışma satın almak). O kol K75'te test edildi: `skor = bot2/AGF^λ`, λ=1'de 1318 olayda
  **sıfır** isabet. **Kapalı.**
- **BEKLEYENLER #6 (25 Eyl'de ağırlıkları yeniden fit et) için erken cevap:** yeniden fit
  gereksiz görünüyor. Madde kapatılMADI (tetiği tarih bazlı) ama bu ölçüm oraya not düşüldü.

**K97 — Sayfadaki "sistem sırası" YARIŞ ANININ sırasıydı; KARAR ANININ sırası artık ayrı
gösteriliyor.** Kullanıcı 9 Ağu'da sordu: "bu liste kupon kurma anındaki sıralama mı, yoksa
koşudan hemen önceki münferit sıralama mı?" Cevap: **koşu anınınki** — ve bu, tek tek vaka
yorumlarını sistematik olarak yanıltıyordu.
- **MEKANİZMA:** `_tum_siralama_html` sıralamayı defter.csv'deki `model_rank`'ten alıyordu;
  defter satırı **postaya 5 dk kala** yazılır (takip.py, `--dk 5`). Kupon ise Altılı'nın **ilk**
  ayağından ~30 dk önce, **tek seferde** kurulur → 6. ayağın kararı **2-3 saat** önceden verilir.
  Hücrelerdeki `sis/kamu` notasyonu da (`ro.at_bilgi`) aynı kaynaktan geliyordu.
- **KANIT (09.08 İstanbul 2. Altılı, kupon 15:14):** kupon anı ile posta anı arasında piyasa
  sırası değişimi ayak ayak — 15 dk kala 6/11 · 45 dk 9/10 · 75 dk 7/9 · 105 dk 5/7 ·
  135 dk 0/5 · **165 dk 13/13**.
- **YORUMU TERSİNE ÇEVİREN İKİ VAKA (aynı günden):**
  | koşu | kazanan | sayfada (yarış anı) | kupon anında |
  |---|---|---|---|
  | 6 | #1 JAZZ RUNNER | sistem **2.** | 7 atın **6.**'sı (oran 10,80 → 2,85) |
  | 8 | #5 ARNAVUT KIZ | sistem **10.**/13 | **2.** (oran 4,45 → 16,20) |
  Yani "kendi 2. atını yazmamış" görüntüsü yanlıştı (karar anında sondan ikinciydi), "10. atı
  yazmış" görüntüsü de yanlıştı (karar anında 2. sıradaydı). **Kararı yargılarken doğru cetvel
  kupon anıdır; sonucu okurken doğru cetvel yarış anıdır.**
- **YAPILAN:**
  1. `veri/altili_kupon_ani.csv` — kupon kurulurken kullanılan vektör (bot1/bot2/kamu/oran +
     dk_kala) **aynen** kaydedilir (`kaynak='canli'`). Geri kurulmuyor, varsayım girmiyor.
  2. `kod/kupon_ani_geri_kur.py` — geçmiş için: oran_log'un kupon anına en yakın anlık
     görüntüsü + defter'deki bot1 (zamandan bağımsız) + o günün **rapor başlığındaki** α/γ ile
     `bot2 = softmax(α·ln bot1 + γ·ln p_kamu)`. Yeniden fit YOK. 64 Altılının **51'i** geri
     kuruldu; 20-24 Tem'in 13'ünde oran günlüğü olmadığı için **geri kurulMADI — uydurulmadı**,
     sayfada açıkça öyle yazıyor. Geri kurulanlar `[geri kurulan]` etiketiyle gösterilir.
  3. Sayfada her ayak için **İKİ ayrı sıralama satırı**, ikisi de **koşu numarasıyla** başlar.
  4. Hücrelerde `K<sıra> Y<sıra>`; ikisi 3+ sıra ayrılırsa **turuncu** (piyasa kupondan sonra
     ciddi kaymış demektir — K76/K80/K92 sürükleme).
- **YAN DÜZELTME:** ayak satırındaki "(defter kaydı yok)" metni **yanlıştı** — kayıt vardı,
  yalnız `defter.sonucla()` gün sonunda (son posta +40 dk, takip.py) bir kez çalıştığı için
  henüz sonuçlanmamıştı. "(sistem sırası gün sonu işlenecek)" oldu. Ayrıca kazanan ✓ işareti
  artık Altılı tarafındaki `kazanan`'dan da çizilebiliyor → gün içinde de görünüyor.
- **BU HATANIN GEÇMİŞE ETKİSİ (dürüstlük notu):** sayfaya bakarak yapılan ayak-ayak yorumlar
  bu yanlılığı taşır — **K79'un "son ayakta sistemin 8. atını tek yazmış"** tespiti dahil.
  K92'nin λ ölçümü oran_log'dan eşleşmiş yapıldığı için **o bulgu ayakta**; etkilenen, tek tek
  vaka anlatılarıdır. Bundan sonra vaka incelemesi K sütunundan okunacak.
- **KAPSAM ve İKİ CETVELİN AYRIŞMASI (ölçüldü, 2026-08-09):** 384 ayağın **258'inde** kupon
  anı kaydı var (126'sında yok: 78'i 20-24 Tem'de oran günlüğü henüz yokken, 48'i günün ilk
  Altılısının uzak ayakları — oran günlüğü o ayakları kupon anında henüz loglamamıştı; bunlar
  ileriye dönük canlı kayıtla kapanır). Eşleşen 2.508 at kaydında **K ile Y sırası yalnız
  %30 aynı**, %48'i 1-2 sıra oynamış, **%22'si 3+ sıra** (turuncu eşiği). Postaya kalan süreye
  göre 3+ kayma oranı: <30 dk **%15** · 30-60 %18 · 60-90 %21 · 90-120 %19 · **120+ dk %32**
  (ortalama mutlak kayma 1,17 → 2,00 sıra). Yani iki cetvelin ayrışması **mesafeyle büyüyor** —
  K76/K80/K92 sürükleme bulgusunun bağımsız bir teyidi.
- **BEKLEYENLER #9 (acgozlu_v2 ileri ölçümü) bu sütun olmadan doğru okunamazdı** — v2'nin tek
  farkı zaten uzak ayak düzeltmesi; kıyas cetveli yarış anı olursa düzeltmenin etkisi görünmez.

**K98 — CANLIYA CIKIS ANALIZI: "bot1 + bir alternatif" plani ÖLÇÜMLE DÜŞTÜ; kalan tek
savunulabilir canlı kupon `orta` (96 kombinasyon).** Kullanıcı 9 Ağu'da sordu: "canlı oynamak
için bot1 ve ona alternatif bir kupon gerekiyor, mevcut kupon sayımız canlıya çıkamayacak kadar
çok ve maliyetli — bot1 dışında 900'lüklerden hangisi? Seçmeyeceksek nasıl birleştiririz?"
Beş turluk backtest (OOS 2025-26, 1.433 olay, yalnız 6/6 öder, birim 1,25 TL).

**(a) DÖRT ADAY, TEK BAŞINA @900**
| kupon | ort.kombo | ayak | KAZANÇ | 6/6 | ROI | ort.temettü |
|---|---|---|---|---|---|---|
| genis900 | 732 | %70,0 | **2,04** | 173 | −55,2% | 3.393 |
| acgozlu900 | 862 | %74,3 | 1,89 | 225 | −64,0% | 2.469 |
| ayrisma900 | 862 | %74,3 | 1,88 | 215 | −64,0% | 2.589 |
| acgozlu_v2 | 862 | %74,6 | 1,86 | **234** | **−47,2%** | **3.483** |
| bot1_900 | 862 | %68,0 | 1,70 | 123 | −18,3% | 10.248 |
- **ayrisma900 elendi:** açgözlü ile eşleşmiş McNemar yalnız-ayrışma 119 / yalnız-açgözlü 124,
  **p=0,80** (8.598 ayak). K95'in canlı bulgusu backtest'te de doğrulandı: ayrı kupon değil, kopya.
- **acgozlu900 elendi:** v2 onu her para ölçüsünde geçiyor.

**(b) v2'nin SÜRPRİZİ ve KONTROLÜ — asıl mekanizma teşhis edildi.** v2'nin arşivde iyi çıkması
BEKLENMİYORDU: arşiv olasılıkları kapanış oranlarından gelir, düzeltilecek sürüklenme yoktur.
İki hipotez ayırt edildi (λ=0,65 @900):
| λ nereye | ROI | temettü |
|---|---|---|
| yok (açgözlü) | −64,0% | 2.469 |
| **geç ayaklara (3-6)** | **−47,2%** | **3.483** |
| tüm ayaklara | −65,2% | 2.452 |
| erken ayaklara (1-2) | −64,5% | 2.460 |
**Tekdüze düzleştirme hiçbir şey yapmıyor.** Etki tamamen *geç ayaklara genişlik vermekten*
geliyor → açgözlünün gerçek kusuru "sivri vektöre kanmak" değil, **son ayaklara sistematik
olarak az at yazmak**; bu kusur sürüklenmeden bağımsız olarak arşivde de var. λ=0,65 canlı
sürüklenme verisinden ölçülmüştü ([[K92]]), backtest'ten seçilmedi → bağımsız teyit.
**λ DEĞİŞTİRİLMEDİ:** tarama 0,50'yi daha iyi gösteriyor (−26,6%) ama backtest'e bakıp λ seçmek
K33/K52'nin yasakladığı overfit'tir. Tarama buraya teşhis için kondu, parametre seçmek için değil.

**(c) v2'nin ÜSTÜNLÜĞÜ BÜTÇEYE ÖZGÜ — küçükte tersine dönüyor.** (Bu ölçüm ilk cevabı düzeltti.)
| bütçe | genis (kapsam) | acgozlu_v2 |
|---|---|---|
| @96 | **−37,1%** | −64,4% |
| @288 | **−46,4%** | −65,0% |
| @900 | −55,2% | **−47,2%** |
v2 "daha iyi mekanizma" değil, **900'e özgü bir düzeltme**.

**(d) PORTFÖY (bot1_900 + X, iki kupon ayrı oynanır)**
| portföy | Altılı başına | en az bir 6/6 | ROI | ROI (en büyük 1 çıkınca) |
|---|---|---|---|---|
| + genis900 | 1.991 TL | 248 (%17,3) | −35,3% | −54,1% |
| + acgozlu900 | 2.154 TL | 277 (%19,3) | −41,2% | −58,6% |
| **+ acgozlu_v2** | 2.154 TL | **293 (%20,4)** | **−32,8%** | −50,2% |
| *kontrol: bot1_1800 tek* | 2.168 TL | 188 (%13,1) | −29,2% | −46,6% |
Önceden bağlanan iki ölçütü de v2 kazandı → **planın literal cevabı bot1_900 + acgozlu_v2.**

**(e) AMA bot1'in SAYISI YANILTICI — bu bugünün en önemli bulgusu.** En büyük kuponlar teker
teker çıkarılıp ROI yeniden hesaplandı:
| kupon | ROI | −en büyük 1 | −en büyük 3 | −en büyük 5 |
|---|---|---|---|---|
| **bot1_900** | −18,3% | **−53,2%** | −70,1% | −72,9% |
| bot1_1800 | −29,2% | −46,6% | −57,3% | −64,4% |
| v2_900 | −47,2% | −50,3% | −54,1% | −56,9% |
| genis900 | −55,2% | −57,5% | −61,4% | −64,8% |
bot1_900'ün 1.433 Altılıdaki **tüm getirisinin %43'ü TEK bir kupondan** (539.029 TL'lik temettü),
%63'ü ilk üçten. Medyan temettüsü 2.056 TL, Altılı başına bedeli 1.078 TL. Karşılaştır: genis900'de
en büyük kuponun payı %5, v2'de %3. **bot1 bir kenar değil, piyango biçimidir.** K67'nin "tuttuğunda
az kişiyle bölüşür" öngörüsü doğru ama bedeli getirinin tek olaya bağlanması. Canlı oyuncu birkaç
yüz Altılı oynar; o tek olayı görme olasılığı düşüktür → **bot1 canlı portföye KONMAMALI.**

**(f) BİRLEŞTİRME İŞE YARAMIYOR.** Üç bot2 kuponunu tek kupona indirmenin üç yolu (@900):
birleşim+buda 173 / −55,2% · çoğunluk(≥2/3) 214 / −62,8% · ortalama vektör 202 / −64,1% ·
en iyi tek (genis900) 173 / −55,2%. **"Birleşim+buda" genis900 ile 1.433 olayın 1.432'sinde
KELİMESİ KELİMESİNE aynı kupon (%99,9)** — birleşimi bütçeye budarken en düşük olasılıklı atları
atmak, tam olarak kapsam kuralının yaptığı şey. Diğer ikisi en iyi teklinden kötü.
K90'ın (bot1+bot2 birleşimi) reddiyle aynı yöne bakıyor.

**(g) ÇOĞALTMA DA İŞE YARAMIYOR — ve NEDENİ yapısal.** ("orta'yı birbirine alternatif çoğaltmak
mantıklı mı?")
| | kombo | bedel | 6/6 | ROI | ROI(−1) |
|---|---|---|---|---|---|
| **1 × orta@96** | 95 | 118 TL | 66 (%4,6) | **−35,5%** | **−44,4%** |
| 2 × orta@96 | 189 | 236 TL | 96 (%6,7) | −51,6% | −56,0% |
| 3 × orta@96 | 284 | 355 TL | 121 (%8,4) | −58,3% | −61,3% |
| 4 × orta@96 | 378 | 473 TL | 138 (%9,6) | −59,8% | −62,0% |
Aynı parayı tek kupona genişleterek vermek her seviyede daha iyi (@192: 90 isabet, −34,0%, 181 TL).
- **Bölme kuralı kontrolü:** üç kural denendi. "A ilk atlar / B sonraki atlar" ile "A tek sıralı /
  B çift sıralı" **birebir aynı sonucu verdi** (96 isabet, −51,6%) — çünkü diğer beş ayak ortakken
  iki kuponun BİRLEŞİMİ aynı kombinasyon kümesidir. **Tek ayakta bölmek = o ayağı genişletmek.**
  Aynı zamanda kodun doğruluk kontrolü.
- **Banker rotasyonu** (kullanıcının tarif ettiği şey; A: 1-3 dar/4-6 geniş, B: tersi):
  temettüyü **İKİYE KATLIYOR** (1.656 → 3.222, de-chalking gerçekten çalışıyor) ama isabet
  66 → 52 düşüyor. Net −41,5%, şans arındırılınca −59,7%. Fikir doğru yöne bakıyor, bedeli büyük.

**(h) TAVAN — sistemin neden kenar bulamadığının en temiz açıklaması.** Kupon zorunlu olarak bir
DİKDÖRTGENDİR (seçim kümelerinin kartezyen çarpımı). Kısıt olmadan "en olası N kombinasyon"
seçilebilseydi ne olurdu (heap ile k-en-iyi kombinasyon):
| | 6/6 | sıklık | ROI | ort.temettü |
|---|---|---|---|---|
| orta@96 (dikdörtgen) | 66 | %4,6 | **−35,5%** | **1.656** |
| tavan, 96 kombinasyon | **87** | **%6,1** | −56,3% | 864 |
| tavan, 192 kombinasyon | 133 | %9,3 | −54,5% | 1.178 |
| tavan, 288 kombinasyon | 164 | %11,4 | −57,6% | 1.335 |
Tavan %32-64 daha fazla tutturuyor ama **temettüsü yarısı** ve ROI'si ~21 puan kötü.
**En olası kombinasyonlar, herkesin oynadığı kombinasyonlardır; kapsamı büyütmek kalabalığa
katılmaktır.** Bunun tersi de doğru: **kuponun dikdörtgen olma zorunluluğu bir handikap değil,
kazara işleyen bir kalabalıktan-kaçınma mekanizmasıdır** — ikinci tercihlerin çapraz çarpımlarını
almaya zorlar, ödeyen kombinasyonlar da onlardır.
Bu, K65'i yeni bir açıdan açıklar: açgözlü isabeti maksimize ederek TAVANA doğru yürür, bu yüzden
daha çok tutturur ve daha az kazanır (185→225 isabet, ROI −41→−55) — ölçülen tam olarak budur.
**Kapsam ile fiyat bu havuzda BİRBİRİNE TERS çalışır ve hiçbir noktada sıfırın üstüne çıkmaz.**

**(i) KARAR / TAVSİYE**
- **Canlıya çıkılacaksa: tek kupon, `orta` (kapsam 0,75 / 96 kombinasyon), Altılı başına 118 TL.**
  Şansa en az bağımlı olan o (ROI(−1) −44,4% ile birinci; getirisinin yalnız %5'i en büyük
  kupondan). KAZANÇ'ı en yüksek olanlardan (2,42). 22 Altılıda bir 6/6, tutunca bedelin ~14 katı.
  Ortalama 42 TL/Altılı kaybettirir.
- **bot1 canlı portföye konmaz** (e maddesi). **Çoğaltma yapılmaz** (g). **Birleştirme yapılmaz** (f).
- Kapsam eşiği kontrolü: 0,75 ile 0,95 arasında fark yok (bütçe zaten bağlıyor) → öneri
  **canlıda hâlihazırda var olan `orta` config'idir**, yeni config gerekmez.
- **DÜRÜSTLÜK NOTU:** tabloda @192'nin @96'dan iyi görünmesi (−34,0 vs −35,5) BULGU DEĞİLDİR —
  dört değerlik taramanın en iyisi ve GA'lar iç içe ([−53,2,−12,9] vs [−58,1,−7,6]). λ için
  söylenenin aynısı: taramadan bütçe seçmek overfit. Doğru okuma: **96-192 bandı aynı, 288'den
  itibaren bozuluyor.**
- **HİÇBİR KOD/CONFIG DEĞİŞMEDİ.** Bu karar bir ölçüm kaydıdır; canlıya çıkma kararı 25 Eyl'e
  bağlı ([[K42]]/[[K48]]).

**(j) YENİDEN ÜRETİLEBİLİRLİK:** yukarıdaki dokuz tablonun tamamını `kod/altili_canli_secim_test.py`
üretir (offline, salt-okunur; `--bolum N` ile tek bölüm). Sayı denetlenemiyorsa karar da
denetlenemez — bu yüzden geçici betikler değil kalıcı araç yazıldı.
**Araçta yakalanan tuzak (not düşülüyor, tekrar etmesin):** `ayrisma_skoru` bot1 ile kamu'yu
**eleman eleman** kıyaslar; p1/p2 olasılığa göre SIRALI tutulduğu için onlardan hesaplanamaz —
hiza kayar ve skor bozulur (ilk yazımda bozulmuştu: p=0,50 çıktı, doğrusu p=0,80). Skor artık
veri yüklenirken, DataFrame satırları hizalıyken bir kez hesaplanıyor.

**(k) YAN İŞ — K97'nin kayıt yolu korumalı hale getirildi.** `kupon_hazirla` içindeki kupon-anı
anlık görüntüsü **yardımcı** kayıttır; hatası kupon kurmayı ASLA engellememeli. İki yer de
try/except'e alındı ve uyarı basıyor. Gerekçe: kupon kurulmazsa o Altılı deneyden düşer —
`kayip_raporu.py`'nin "KURULMAYAN ALTILI" kalemi, ölçtüğümüz en pahalı hasar. Yeni bir dosyaya
yazmak için o riski almayız; boşluğu zaten `kupon_ani_geri_kur.py` doldurur.

**K99 — RAPOR HATASI: bot1 sütunu YANLIŞ CETVELLE etiketleniyordu; `B` sırası eklendi.**
Kullanıcı 9 Ağu İZMİR 1. Altılı'ya bakarken sordu: *"5. ayakta ROSİLDA kupon anında 5. sırada
ama bot1 kuponunda 5 atın arasında yok"* ve netleştirdi: *"bot1 o ayakta 5 at yazmış ama kupon
anında 5. olan atı değil 8. atı yazmış."* **Öncül doğruydu ve şikâyet haklıydı — ama sebep
bot1'in seçimi değil, RAPORUN ETİKETİYDİ.**

**(a) TEŞHİS.** `bot1_900` config'i `"puan": "bot1"` ile çalışır (K67) — seçimini **bot1'in
kendi cetveliyle** yapar, harmanla değil. Ama HTML rapor hücrelerinde her config için AYNI
etiket basılıyordu: `K` = harman kupon-anı sırası, `Y` = harman yarış-anı sırası. Sonuç: bot1
sütununda `K1. K2. K3. K4. K8.` görünüyor ve **5, 6, 7 atlanmış gibi** duruyor. Oysa bot1
kendi cetvelinde ilk 5'ini KESİNTİSİZ almıştı. O "K8" bot1'in **3. atıydı**.

**(b) VAKANIN GERÇEĞİ (İZMİR, seq 1, 5. ayak, kupon anı 17:30 / 149 dk kala).**
| bot1 sırası | at | bot1 p | harman sırası | oran |
|---|---|---|---|---|
| 1 | #3 DREAM FOR VICTORY | 0,1833 | 3. | 6,35 |
| 2 | #8 SONANDA | 0,1665 | 2. | 4,90 |
| 3 | **#4 MAMMA LUNA** | 0,1641 | **8.** | **24,65** |
| 4 | #2 STORM BELLE | 0,1580 | 1. | 3,15 |
| 5 | #6 FREYDIS | 0,0872 | 4. | 7,25 |
| **6** | **#1 ROSİLDA (KAZANAN)** | **0,0704** | **5.** | 8,65 |

bot1 kazananı **kesimin bir sıra altında** bıraktı. Harmanın 8. sıradaki atını (oran 24,65 —
piyasaya göre uzak ihtimal) kendi 3. sırası olduğu için aldı. **Bu hata değil, ayrışmanın
tanımı** — bot1 orana hiç bakmaz.

**(c) DÜZELTME (`kod/altili_canli.py`).** (1) `puan == "bot1"` olan config'lerin hücrelerinde
`B<sıra>` ÖNCE yazılır: `4 B3. K8. Y5.` → "bot1'in 3. atı, harman 8. sayıyordu, yarış anında
5. oldu". (2) Ayak altına **BOT1 CETVELİ** satırı eklendi (KUPON ANI / YARIŞ ANI satırlarının
yanına) — bot1'in tam sıralaması, seçilenler kalın, kazanan yeşil tik. (3) Tablo üstüne lejant.
Doğrulama: rapor yeniden üretildi, 1.086 B-etiketi ve 263 BOT1 CETVELİ satırı basıldı; söz
konusu hücre artık `2 B4. · 3 B1. · 4 B3. · 6 B5. · 8 B2.` = kesintisiz 1-5, cetvel satırı
`1.#3 2.#8 3.#4 4.#2 5.#6 6.#1✓` ile kazananın neden dışarıda kaldığı tek bakışta görünüyor.

**(d) NEDEN ÖNEMLİ.** K97'nin tekrarı: **yanlış cetvelle bakınca vaka yorumu yanılır.** K97'de
kupon anı / yarış anı ayrımı yoktu ve tek tek vakalar yanlış okunuyordu; burada da bot1'in
kararı harmanın cetveliyle yargılanıyordu. Kullanıcının "bu bir hata mı?" diye takılması
raporun kusuru, botun değil. **Ölçüme etkisi YOK** (yalnız görselleştirme; seçim/backtest
kodu değişmedi), ama vaka incelemesinin güvenilirliğine etkisi büyük.

**(e) SINIR.** Tek vakadan "bot1 kötü sıralıyor" çıkarılmaz (hindsight yasağı). Toplu ölçüm
zaten kayıtlı: bot1 isabeti %29,1 vs harman %35,7 (K67), ve K98-e uyarınca **bot1 canlı
portföye konmaz** (getirisinin %43'ü tek kupondan). Bu karar o hükümleri DEĞİŞTİRMEZ.

**K100 — KALABALIK BUDANDI: dört config EMEKLİ, `bot1_1800` eklendi. Config silinmez,
EMEKLİ edilir.** Kullanıcı 10 Ağu'da istedi: "canlı oynamıyorum, para kaybetmiyorum, aklıma
gelen her şeyi deneyimlemek istiyorum — iptal edilecekleri iptal et, bot1_1800'ü kur, sisteme
hiçbir zarar gelmesin." Önce önerinin her maddesi ölçüldü, sonra uygulandı.

**(a) KULLANICININ VERDİĞİ SAYILAR DOĞRULANDI** (canlı sicil, sonuçlanmış kuponlar):
| config | kupon | 6/6 | ayak isabeti | net | Altılı başına |
|---|---|---|---|---|---|
| dar | 66 | 0 | %39,4 | −1.320 | 20 TL |
| orta | 66 | 1 | %45,7 | **+10.314** | 115 TL |
| geniş | 53 | 0 | %48,4 | −14.602 | 276 TL |
| geniş900 | 53 | 1 | %56,0 | −41.916 | 918 TL |
| açgözlü900 | 48 | 2 | %60,8 | −32.274 | 1.083 TL |
| bot1_900 | 36 | 2 | **%63,4** | **+11.957** | 1.075 TL |
| ayrışma900 | 36 | 0 | %59,3 | −39.189 | 1.089 TL |
| açgözlü_v2 | 10 | 0 | %60,0 | −10.735 | 1.074 TL |
**UYARI — net TL karar dayanağı DEĞİL:** açgözlünün −32.274'ü 2 isabete, geniş900'ün −41.916'sı
1 isabete dayanıyor; artıdaki ikisi de tek/çift isabetin eseri. 36-66 kuponluk sicilde net TL
tek olayın gürültüsüdür ([[K98]]-e'nin aynı dersi). Karar iki sütuna dayandırıldı:
**benzersiz katkı** ve **açık bir soruya cevap veriyor mu**.

**(b) BENZERSİZ KATKI** (216 sonuçlanmış ayak; o ayağı SADECE o config tutturdu):
dar **0** · orta **0** · geniş **0** · geniş900 2 · açgözlü900 1 · ayrışma900 2 · **bot1_900 32**.
bot1 dışındaki hiçbir config portföye ayak kazandırmıyor — K98'in backtest bulgusunun
(194 ayakta bot1 30, diğerleri 0-2) canlı karşılığı.

**(c) EMEKLİ EDİLENLER ve gerekçeleri**
- **ayrışma900** — açgözlü900'ün ikizi: canlıda ayakların **%78'inde birebir aynı kupon**,
  Jaccard %92; backtest McNemar p=0,80 (8.598 ayak). [[K95]]'in açık bıraktığı "w kararı"
  böylece (c) şıkkıyla kapandı.
- **dar** — 0 benzersiz katkı. "Bu bedelle tutturmak imkânsız" iddiası neredeyse doğru:
  backtest'te 1.433 Altılıda 19 isabet (%1,3), ~75 Altılıda bir. 66 kuponda 0 isabet
  beklenenin içinde, bulgu değil.
- **geniş** — 0 benzersiz katkı, komşularıyla %88/%83 örtüşme. Merdiven sorusu backtest'te
  1.433 olayla kapandı ([[K88]]/[[K98]]).
- **geniş900** — tek işi K65'in kontrolüydü (aynı bütçe, tek fark dağıtım); o kol
  [[K83]]/[[K93]]/[[K98]]'de kapandı. Kapsam ailesi `orta` ile temsil ediliyor.
**açgözlü900 KALDI** — ikizinden hangisinin kalacağı sicile göre değil ROLE göre seçildi:
açgözlü900, `acgozlu_v2`'nin kontrol grubudur (BEKLEYENLER #9). Kaldırılsaydı tek açık
deneyimiz dayanaksız kalırdı.

**(d) `bot1_1800` EKLENDİ — ama kullanıcının gerekçesiyle DEĞİL.** İddia: "bot1 özellikle
yüksek ödüllü yarışlarda 5'te kalıyor; kaçırdığı ayakta 1 at daha yazsa tutturacak."
İki parçası da ayrı sınandı:
- **"1 at daha yazsa" HINDSIGHT.** 5/6 kalınan olaylarda kazananın, config'in KENDİ cetvelinde
  kesimin kaç sıra altında olduğu: bot1@900 **%31**, açgözlü@900 **%31**, geniş900 **%29**,
  orta@96 **%33** (medyan derinlik hepsinde 2). Dördü aynı → bu bot1'e özgü bir yakınlık değil;
  açgözlü dağıtıcı tanımı gereği kesim çizgisinde durur, kıl payı kaçırma her kuponda böyle
  görünür. Hangi ayağı kaçıracağın önceden bilinmiyor.
- **"Yüksek ödüllüleri yakalarız" YANLIŞ — tersi ölçüldü.** bot1@900 → bot1@1800: 405 near-miss'in
  63'ü (%15,6) 6/6'ya dönüyor. **Yüksek ödüllülerin dönüşümü %10, düşük ödüllülerin %17.**
  Dönenlerin medyan temettüsü 2.966 TL, dönmeyenlerin 6.276 TL; dönmeyenlerin en büyüğü
  2.347.571 TL. Büyük ödül = sürpriz at = cetvelin DERİNİ, kesimin bir altı değil.
  [[K91]]'in bot2 için bulduğunun bot1'deki karşılığı.
- **GERÇEK gerekçe (farklı):** bot1@900'ün getirisi tek olaya asılı (ROI −18,3% ama en büyük
  kupon çıkınca **−53,2%**). Bütçe merdiveni: 900 → 1350 → 1800 → 2700 → 3600 için görünen ROI
  −18,3/−22,3/−29,2/−39,5/−42,5, **şanstan arındırılmış ROI −53,2/−45,7/−46,6/−51,2/−51,2**.
  Yani 900 belirgin şekilde kötü, 1350-1800 bandı iyi. (Banttan tek değer SEÇİLMEDİ; beş
  değerlik taramanın en iyisini almak λ ve @192'de reddedilen overfit'in aynısı olurdu —
  1800 kullanıcının istediği değer olduğu için alındı, taramanın kazananı olduğu için değil.)
- **ÖLÇÜM DEĞERİ ~SIFIR, açıkça söylendi:** 25 Eyl'e kadar ~35 kupon birikir; [[K87]]/[[K89]]'da
  bu örneklemde hiçbir şeyin ayırt edilemediği görüldü. Bütçe sorusu backtest'te 1.433 olayla
  zaten cevaplandı. Kullanıcı bunu bilerek istedi ("deneyimlemek istiyorum") → [[K68]] gibi
  **GÖZLEM AKIŞI** olarak eklendi, bulgu iddiası yok.

**(e) NASIL UYGULANDI — "sisteme zarar gelmesin" şartının karşılığı.**
**Config SİLİNMEDİ, `aktif: False` bayrağı eklendi.** Silinseydi sessiz bozulma olurdu:
`toplam_blok` KONFIG'i gezer, `_kumulatif_blok` kuponları CSV'den okur → silinen config
CSV'de kalır ama toplamdan düşer, **işleyen bakiye ile TOPLAM DURUM birbirinden ayrışırdı.**
Ayrıca o config'in sütunu geçmiş Altılı kartlarından da kaybolurdu. Emeklilik = bayrak.
Uygulama sırasında bulunan ve kapatılan **üç ayrı kırılma noktası**:
1. `_telegram_sonuc` referans satırı `next(iter(KONFIG))` = **"dar"** idi. Dar emekli olunca
   yeni Altılılarda o satır boş dönüp **"Kazananlar" satırı sessizce kaybolacaktı**.
   Artık o Altılı'da gerçekten kupon kurulmuş ilk config'ten okunuyor.
2. `kayip_raporu.py` üç yerde **"7 kupon"** yazıyordu (elle). Artık `aktif_konfig()`'ten
   üretiliyor — K78'in dersi: elle yazılan sayı bayatlar.
3. Modül docstring'i hâlâ "DÖRT config: dar/orta/geniş/geniş900" diyordu. Sayı verme alışkanlığı
   kaldırıldı; tek kaynak KONFIG.
`_tur_ozeti` emeklileri ayrı satırda açıkça yazıyor; TOPLAM DURUM'da ve tablo başlıklarında
**[EMEKLİ]** etiketi var — sicil görünür kalıyor, "kupon nerede?" diye aranmıyor.

**(f) DOĞRULAMA (uygulama sonrası, üç bağımsız kontrol)**
1. **Geçmiş sicil bozulmadı:** CSV'den KONFIG'e hiç bakmadan hesaplanan toplam bedel
   **212.791,25 TL**; sayfanın GENEL TOPLAM'ı **212.791,25 TL**. Birebir. Emekli dört config
   her iki TOPLAM DURUM bloğunda da duruyor.
2. **Kuru çalışma (canlıya dokunmadan):** 10.08 BURSA'nın GERÇEK kupon-anı vektörleriyle
   config döngüsü çalıştırıldı. 5 aktif config geçerli kupon kurdu (boş ayak yok, bütçe aşımı
   yok), 4 emekli atlandı. bot1_1800: 1.680 ve 1.764 kombo (tavan 1800) = 2.100 / 2.205 TL.
3. **BEKLENMEDİK BULGU:** `bot1_1800`, `bot1_900`'ün üst kümesi DEĞİL. 1. Altılı'da 900'ün
   22 atının 21'i 1800'de var — açgözlü dağıtıcı bütçe artınca genişliği YENİDEN dağıtıyor
   (1. ayak 6→5 atarken 2. ayak 3→7 çıkıyor). Yani ikisi "dar/geniş aynı kupon" değil,
   **farklı kuponlar**. İleride kıyaslanırken bu akılda tutulmalı.

**(g) SONUÇ.** Aktif: `orta` (115 TL) · `acgozlu900` (1.083) · `bot1_900` (1.075) ·
`bot1_1800` (~2.150) · `acgozlu_v2` (1.074). Emekli: `dar`, `genis`, `genis900`, `ayrisma900`.
Altılı başına kâğıt bedel ~5.649 → ~5.497 TL (bedel amaç değildi; amaç kalabalığın azalmasıydı:
8 config → 5, ve kalan beşin her biri açık bir soruya bağlı).
Ölçüm koduna, dağıtıcılara, backtest'e, `orta`nın ayarlarına DOKUNULMADI.

**K101 — "ALTERNATİF KUPON" (banker takası) ÖLÇÜLDÜ → REDDEDİLDİ. Teşhis doğruydu, çare işe
yaramıyor.** Kullanıcının tarifi (10 Ağu): *"alternatif altılı kuponları, oyuncunun güvenip tek
attığı ayağın yıkılması olasılığı üzerine kurulur; ikinci kuponda ilk kuponun banker ayağı daha
çok atla yazılır, varsa diğer favori ayak tek atılır."*

**(a) BANKER TANIMI — kullanıcının düzeltmesi ve benim yanılgım.** Ben `BANKER_ESIK=0,70`'i arayıp
"bizim kuponlarımızda banker yok" demiştim (ölçüm: bot1_900'ün 33 tek-at ayağının **sıfırı** eşiği
geçiyor, tepe atın ort. olasılığı 0,40; acgozlu900'de 64'ün 5'i; yalnız `orta`da 10/10 geçiyor).
Kullanıcı düzeltti: **banker kesinlik değil görece güvendir** — "bu ayakta bu ata güveniyorum,
diğerlerini güçlü tutayım". Bu tanımla banker her Altılıda tanımlıdır (tepe olasılığı en yüksek
ayak) ve benim "bizde banker yok" itirazım geçersizdir. Fikri gömen bir engel yokmuş.

**(b) KURAL (serbest parametre YOK).** Güven sıralaması: i = 1., j = 2. ayak.
`A: i=1 at, j>=2 at` · `B: j=1 at, i>=2 at` · kalan dört ayak açgözlüden; bütçe aşılırsa i/j
DIŞINDAKİ en geniş ayaktan kısılır. A∪B, (i,j) düzleminde **artı** şeklidir — hiçbir tek kupon bu
şekli kuramaz (kupon zorunlu olarak dikdörtgen, K98-h). **K98-g'deki "rotasyon" testi bunu
KARŞILAMIYORDU**: o ayak sırasına göreydi (1-3 dar / 4-6 geniş), modelin güveniyle ilgisizdi ve
kupon başına üç banker koyuyordu.

**(c) UYGULAMA DERSİ — ilk tur mekanizmayı hiç çalıştırmamış.** B'de banker ayağını yalnızca
*serbest bıraktım*; açgözlü en güvenilen ayağa zaten az at verdiği için o ayak olayların
**%45-59'unda yine tek atta kaldı** → B, A ile aynı → sigorta hiç oluşmadı. Yani fikir olayların
yarısında test EDİLMEMİŞTİ. Zorlanmış sürümde (i>=2) sigorta %100 oluştu. **Ölçüt değiştirilmedi**
— düzeltilen şey ölçüt değil mekanizmanın uygulanışıydı.

**(d) SONUÇ (OOS 2025-26, 1.433 olay, yalnız 6/6 öder, birim 1,25 TL).** Ölçüt önceden bağlanmıştı:
*çift, aynı toplam paradaki tek dikdörtgeni hem ROI(−1)'de hem ort. temettüde geçmeli.*
| | 6/6 | ROI | ROI(−1) | ort. temettü |
|---|---|---|---|---|
| çift bot2 2×450 | 197 | −68,3% | −69,5% | 2.387 |
| **tek bot2 @900** | **225** | −64,0% | **−65,5%** | **2.469** |
| çift bot2 2×900 | 295 | −65,5% | −66,5% | 3.581 |
| **tek bot2 @1800** | **300** | −61,1% | **−64,1%** | **4.027** |
| çift bot1 2×450 | 106 | −33,2% | **−42,9%** | 9.401 |
| **tek bot1 @900** | **123** | −18,3% | −53,2% | **10.248** |
| çift bot1 2×900 | 159 | −49,0% | −53,7% | 9.840 |
| **tek bot1 @1800** | **188** | −29,2% | **−46,6%** | **11.694** |
**Dört hücrenin dördünde de RED.** (bot1 2×450 ROI(−1)'de geçti ama temettüde kaldı → ölçüt
gereği red; tek kriterle kurtarmak hindsight olurdu.)

**(e) TAHMİNİMİN İKİ KANADI DA YANLIŞ ÇIKTI.** "Daha çok tutturur, daha ucuz temettü verir" VEYA
"daha az tutturur, daha pahalı temettü verir" diye iki zıt kuvvet öngörmüştüm ve yönünü
bilmediğimi yazmıştım. Ölçüm **ikisini de** yalanladı: çift hem daha az tutturdu **hem** daha ucuz
temettü verdi. Öngörülmeyen sonuç.

**(f) NEDENİ — asıl bulgu.** Kullanıcının teşhisi DOĞRU: A, banker ayağını olayların
**%50 (bot2) / %61 (bot1)**'inde kaçırıyor; kuponun tek kırılma noktası gerçekten orası. Ama B o
ölümlerin ancak **%2-4'ünü** kurtarabiliyor. Üç sebep:
1. B'nin kurtarabilmesi için A'nın **diğer beş ayağı** tutturmuş olması gerekir — zaten düşük olasılık.
2. B, 2. ayağı tek ata indirdiği için **yeni bir kırılma noktası** yaratır (sigorta bir delik
   kapatıp başka delik açıyor).
3. İki kuponun **ortak dört ayağı iki kez satın alınıyor**; aynı para tek kupona verilse altı ayağa
   birden genişlik olurdu.

**(g) BAĞLAM.** Bu, kupon ŞEKLİNİ akıllandırma kolundaki **beşinci** ret: K68 ayrışma · K90 birleşim ·
K98-f birleştirme · K98-g çoğaltma · K101 banker takası. Hepsi K98-h'nin "tavan" bulgusuyla aynı
yere çıkıyor: bu havuzda kupon şekliyle kenar üretilemiyor, dikdörtgen kısıtı zaten kazara işe
yarıyor. **Kupon şekli kolu kapanmıştır**; yeniden açmak için yeni bir MEKANİZMA gerekir, yeni bir
şekil varyantı değil.

**(h) ARAÇ:** `kod/altili_banker_takasi_test.py` (offline, salt-okunur; `--gevsek` ile kusurlu ilk
tur da üretilir). **HİÇBİR KOD/CONFIG DEĞİŞMEDİ** — canlı 5 config K100'deki gibi.

**K102 — ATA ÖZEL KULVAR TERCİHİ test edildi → EKLENMEDİ. Eşdoğrusal DEĞİLmiş (tahminim yanlıştı)
ama yardımı da yok.** Kullanıcı 10 Ağu'da sordu: *"sistem analizinde jokey, atın kulvarı, hava ve
pist durumu, atın son antrenmanları değerlendiriliyor mu?"*

**(a) MEVCUT DURUMUN ENVANTERİ** (soruya cevap): **VAR** → jokey (365 gün isabet oranı + jokey
değişimi ikili sinyali), antrenör (aynı desen), kulvar **ama pist seviyesinde**
(`kulvar_skor` = şehir × mesafe kovası × start kovası tarihsel galip oranı, ≤2024'ten, ırk ayrı),
zemin (atın kum/çim galip oranı), pist hızı (hız figüründeki `gun_ofset`), takı değişimi,
dinlenme süresi, kilo, handikap, yaş, cins, kariyer, form. **YOK** → hava/sıcaklık/nem/gece
(veri %99,9 toplanıyor, özellik değil), going (K33'te test edilip ELENDİ), **antrenman/idman
verisi feed'de hiç yok**. Denenmemiş tek şey: **ata özel kulvar tercihi**.

**(b) TEST.** `kulvar_uygunluk` = atın BU start kovasındaki (1-3/4-6/7-9/10-12/13+) önceki galip
oranı — `zemin_galip_oran` deseniyle birebir aynı, nokta-anında, yarış-içi z-skorlu. Doluluk %76,9.
Walk-forward K38 ile aynı: eğit ≤2023 (7.259 koşu), harman 2024 (2.592), TEST 2025-26 (4.044).
Ölçüt sonuç görülmeden bağlandı: **(a)** Bot2 test log-loss iyileşmesi ≥ 0,0010 (K33'te ölçülen
"sıfır"ın 25 katı, Batch 1'in iki katı) **VE (b)** yeni katsayı, eşdoğrusal adaylardaki katsayı
düşüşünün toplamından büyük olmalı.

**(c) SONUÇ.**
| | Bot1 | Bot2 (üretim) | α | γ |
|---|---|---|---|---|
| 17 özellik | 1,85969 | **1,69945** | +0,190 | +0,975 |
| 18 özellik | 1,86002 | 1,69949 | +0,192 | +0,974 |
İyileşme: Bot1 **−0,00033**, Bot2 **−0,00004** — ikisi de **kötüleşti**. Ölçüt (a) KALDI → EKLENMEZ.

**(d) TAHMİNİM YANLIŞ ÇIKTI — kayda geçsin.** "going_uygunluk nasıl zemin ile eşdoğrusal çıktıysa,
ata-özel kulvarın da kariyer_galip_oran ile aynı kaderi paylaşması muhtemel" demiştim. **Öyle
olmadı:** ölçüt (b) **GEÇTİ** — eşdoğrusal adayların katsayıları neredeyse hiç kıpırdamadı
(kulvar_skor_z +0,0827→+0,0832; zemin_galip_oran_z +0,1369→+0,1377; kariyer_galip_oran_z
−0,0409→−0,0339, toplam düşüş 0,0070) ve yeni özellik kendi başına −0,0181 katsayı aldı. Yani
**bağımsız bilgi taşıyor, ama işe yaramayan bir bilgi.** K33'ün "eşdoğrusallık" hikâyesi burada
geçerli değil; bu sefer sebep başka: sinyal var ama gürültüden ibaret.
Katsayının **negatif** olması da dikkat çekici — atın bir kulvar kovasındaki yüksek geçmiş galip
oranı, her şey sabitken kazanmayla ters ilişkili. Muhtemel sebep: yüksek oran çoğunlukla küçük
paydadan geliyor (o kovada az koşmuş at) → gürültü; gerçek sinyali `kariyer_galip_oran` zaten almış.

**(e) K33'ÜN KAPANIŞI YERİNDE KALIR.** Bu, K19-K33 dizisinden sonraki ilk özellik testiydi ve
sonuç değişmedi: **hiçbir kamuya açık veri özelliği Bot2'yi oynatmıyor.** Sebep K96'da ölçülü —
Bot2'nin ağırlığının %82'si piyasadan geliyor; piyasa jokeyi, kulvarı, havayı zaten fiyatlamış.
Kenar veri mühendisliğinde değil.

**(f) ARAÇ:** `kod/kulvar_tercih_test.py` (offline, salt-okunur; `ozellikli.csv`'yi EZMEZ).
Canlı model 17 özellikle çalışmaya devam ediyor, hiçbir kod/config değişmedi.

**K103 — KAMU SIRASI GERİ GELDİ. K97'de sessizce düşmüştü: sütun EKLENECEKKEN DEĞİŞTİRİLMİŞ.**
Kullanıcı 11 Ağu'da sordu: *"altılı takipte atların kamu sıralaması da görülmüyor muydu daha
önce?"* — doğruydu, ben düşürmüşüm.

**(a) NE OLDU.** K97 öncesi hücre `no sis./kamu.` basıyordu (sistem sırası + kamu sırası), başlık
da "kazananın sistem / kamu" idi. K97'de "kupon anı (K) / yarış anı (Y)" ayrımını eklerken kamu
sütununu **eklemek yerine DEĞİŞTİRDİM**: hücre `K1. Y1.` oldu, kamu kayboldu. Kimse fark etmedi;
kullanıcı iki hafta sonra hatırladı.

**(b) NEDEN ÖNEMLİ.** Kaybedilen şey bu projenin merkezindeki karşılaştırma: **sistem kalabalıkla
aynı mı, ayrı mı düştü.** bot1'in tüm gerekçesi (K67: "Bot2 pratikte kamunun kendisi, favori
ortaklığı %89,9"), ayrışma dağıtıcısı (K68), tavan bulgusu (K98-h: kapsamı büyütmek kalabalığa
katılmaktır) — hepsi kamu sırasıyla kıyasa dayanır. O sütun olmadan sayfada "biz kalabalıktan
ayrıldık mı" sorusu **cevaplanamıyordu**.

**(c) DÜZELTME.** Hücreler dört etiket taşıyor: **K** kupon anı harman sırası · **Y** yarış anı
harman sırası · **B** bot1'in kendi sırası (yalnız bot1 config'lerinde, K99) · **P** kamu sırası.
Örnek: `3 K2. Y3. P2.` ve bot1 sütununda `9 B1. K1. Y1. P1.`
İki renk uyarısı: **turuncu** = K ile Y 3+ sıra kaymış (sürüklenme, K97) · **mor** = sistem kamudan
3+ sıra ayrı (ayrışma). Üretilen sayfada 5.776 P etiketi, 218 mor işaret, 299 kazanan satırı.
Kazanan sütunu: `7. → 8. / kamu 7.`
**Kamu sırası KUPON ANINDAN alınır**, yarış anından değil — K ile aynı ana denk gelsin ki
"karar verirken kalabalık ne diyordu" sorusu doğru cevaplansın. Veri zaten
`veri/altili_kupon_ani.csv`'de duruyordu (K97'de toplanmaya başlamıştı), yeni veri gerekmedi.

**(d) DERS — kayda geçsin.** *Bir sütun eklerken mevcut sütunu değiştirme.* K97'de yer darlığı
yüzünden kamu'yu K ile "takas ettim" ve bunu ne karar notuna yazdım ne de kullanıcıya söyledim.
Sayfa üretim kodunda bir alan silmek, o alanı besleyen ölçümü de görünmez kılıyor. Bundan sonra
rapor alanı çıkarılacaksa **açıkça karara yazılır**; sığmıyorsa satır/renk ile çözülür, silinerek
değil. (K78'in "elle yazılan liste bayatlar" dersinin kardeşi.)

**(e) KAPSAM.** Yalnız görselleştirme; seçim, dağıtıcı, config, backtest **değişmedi**.
Canlı 5 config K100'deki gibi.

**K104 — ALTILI DIŞI KOL İLK KEZ ÖLÇÜLDÜ: gerçek ganyan kesintisi %28,3 (varsaydığımız %25,5
değil), PLASE kesintisi %10-14 ile ölçtüğümüz EN UCUZ ürün. Seçim zararı YOK.** Kullanıcı 15
Ağu'da sordu: *"altılı dışındaki bahislerde ne durumdayız?"* — K93'ten beri bu kola hiç
bakılmamıştı.

**(a) NE OYNUYORUZ.** Tek kol: K42 kâğıt testi, 4 Tem – 25 Eyl, **yalnız İngiliz** koşularında
(K46 ile canlıya Arap eklendi ama deney ortasında kapsam değiştirilemez; veriyle doğrulandı:
1.042 kuponun 1.042'si İngiliz). Kupon 15 TL sabit, hafta bütçesi 3.000 TL.
S1 model top-pick ganyan · S2 aynı atın plasesi · S3 kamu favorisi ganyan · S4 aynı atın plasesi ·
S5 CANLI (bot1'in kamudan çok yüksek gördüğü non-favori) ganyan. Plase yalnız saha≥7'de.
**PLASE'nin ne ödediği kendi verimizden türetildi:** kazanan plase kuponlarında at ya 1. (88) ya
2. (42); 3. ve sonrası 85 kuponun tamamı kayıp → **ilk 2'ye ödüyor**, saha büyüklüğünden bağımsız.

**(b) YÖNTEM — ROI'yi ikiye ayır.** Mükemmel kalibre bir havuzda hangi atı oynarsan oyna beklenen
ROI = −kesinti (kanıt: p_devig·O = 1/Σ(1/O) = 1−t, her at için aynı). Demek ki −t'den sapma
YALNIZCA seçimin piyasadan kötü olmasından gelir. İki parça ayrı ölçüldü: (A) gerçek kesinti
her koşuda kapanış oranlarından, (B) kalibrasyon = gerçek galibiyet / piyasanın dediği.

**(c) GANYAN — seçim zararı YOK, sorun kesintinin kendisi.**
| | kupon | galip | piyasanın dediği | kalibrasyon | %95 GA |
|---|---|---|---|---|---|
| tüm ganyan | 802 | 227 | 232,4 | **0,977** | [0,88 – 1,08] |
| S1 (model) | 285 | 101 | 102,8 | 0,983 | [0,84 – 1,13] |
| S3 (favori) | 285 | 100 | 102,8 | 0,972 | [0,83 – 1,11] |
| S5 (canlı) | 232 | 26 | 26,7 | 0,972 | [0,64 – 1,32] |
Kalibrasyon 1,00'i rahatça içeriyor → seçtiğimiz atlar piyasanın öngördüğü kadar kazanıyor.
**Açık kesintiden geliyor:** İngiliz koşularında kapanıştan ölçülen gerçek kesinti **ortalama
%28,3** (medyan %25,6 — teorik %25,5 ile birebir — ama %10-%90 aralığı **%25,3 – %37,0**, kuyruk
ağır). Kalibrasyon 0,977 ve t=%28,2 ile hesaplanan ROI −%29,8; gerçekleşen −%34,2 [−43,1, −24,5].
Model tahmini aralığın içinde → **açıklanamayan artık yok.**
**K93 DÜZELTMESİ:** "ganyan −%25,4, kesinti %25,5, birebir tuttu" demiştim; o eşleşme kısmen
tesadüfmüş. Doğru referans %25,5 değil, oynadığımız koşuların gerçek ortalaması **%28,3**.

**(d) PLASE — kesinti %10-14, ölçtüğümüz en ucuz ürün.** İlk-2 olasılığı Harville ile.
Kalibrasyon 0,960 [0,85–1,06] → burada da seçim zararı yok. Kesinti kestirimi: kalibrasyon 1,00
kabul edilirse **%14,0**; ölçülen kalibrasyonla **%10,4**. Harville favorinin plase olasılığını
şişirdiği için ikinci sayı kesintiyi olduğundan büyük gösterir → **gerçek değer %10-14 arası.**
Ürün sıralaması (K94 + bu ölçüm): **plase %10-14** · ganyan %28,3 · 3'lü %45,4 · 4'lü %45,6 ·
5'li %46,8 · 6'lı %48,6 · 7'li %57,6. **Plase açık ara en ucuz ürün.**
Yine de −%14 negatif ve GA [−26,7, −1,5] sıfırı içermiyor: ucuz ≠ kârlı.

**(e) BAĞIMSIZ DOĞRULAMA — 14 Ağu İstanbul 2. Altılı (2.780.891 TL).** Altılı temettüsü / aynı
altı atı üst üste ganyan oynamanın getirisi = **3,74**. Teorik beklenti (Altılı kesintiyi BİR kez,
altı ganyan ALTI kez alır): (1−0,486)/(1−0,283)⁶ = **3,78**. Tek olaydan, hiçbir model varsayımı
olmadan, iki kesinti ölçümümüz (ganyan %28,3 · Altılı %48,6) aynı anda doğrulandı.

**(f) YAYVANLIK KOLU AÇILDI ve KAPANDI — "ne zaman oynamalı" ilk kez soruldu.** 14 Ağu'da
İstanbul yüksek ödedi ama kazananların kupon anı sıraları 2,8,2,1,3,2 idi — **sürpriz değil**.
Yüksek ödül ayakların YAYVAN olmasından geldi (ayak başına ort. favori olasılığı %29; Bursa'da
%32-34, temettü 9-11 bin). Yayvanlık kupon kurulmadan ÖNCE bilinir → kullanılabilir mi?
**Çerçeve:** havuz etkinse bu boyut ROI'yi DEĞİŞTİREMEZ. Fark çıkarsa gözlemlenebilir etkinsizlik.
Ölçüt önceden bağlandı: medyandan bölme (eşik taraması YASAK), fark GA'sı sıfırı içermeyecek ve
üç config'in en az ikisinde aynı yönde olacak.
**SONUÇ: BULGU YOK.** orta@96 +9,9 [−36,8,+64,5] · acgozlu@900 −7,7 [−21,4,+6,9] ·
bot1@900 −43,0 [−208,6,+67,2] — üçünde de GA sıfırı içeriyor, **yönler bile tutarsız**.
**Mekanizma doğrulandı ama net etkisi sıfır:** yayvanlık temettüyü öngörüyor (225 isabette
log(temettü) ile korelasyon **−0,316**; yayvan yarıda temettü 2.832 vs sivri 1.108, 2,6 katı) ama
isabeti aynı oranda düşürüyor (21 vs 45 tutturma). İkisi birbirini götürüyor.
Kuintil tablosunda 4. kova parlıyor (bot1'de +%113,8) ama monoton değil ve tek dev temettüden —
oradan eşik seçmek K33/K52 overfit'i olurdu, ölçüt tam bunun için önceden bağlanmıştı.
**Zamanlama kolunun ilk ölçümü negatif.**

**(g) ARAÇLAR:** ölçümler scratchpad'de yapıldı; kalıcı araç YAZILMADI (tek seferlik teşhis).
Tekrar gerekirse yöntem bu maddede tam olarak tarif edilidir. Hiçbir kod/config değişmedi.


**K105 — ZAMANLAMA KOLU CANLIYA: `orta_15` eklendi; kupon artık İKİ ayrı anda kurulabiliyor.**
Kullanıcı 15 Ağu'da sordu: *"neden 15 hatta 10 dk kala aynı kuponların versiyonlarını şimdi
kurmuyoruz, Ekim'i neden bekliyoruz?"* — itiraz haklıydı.

**(a) EKİM TETİĞİ BAYATTI.** BEKLEYENLER #4'ün "Ekim" tahmini 31 Tem'de, `oran_log` kupon anının
tam fotoğrafını çekmezken kondu (17 Altılıdan yalnız 3'ü iki zaman diliminde tamdı). K76 bunu
düzeltti ve 15 gündür doğru veri birikiyor; ben tetikteki **sayıyı** kontrol etmek yerine
takvimdeki "Ekim" notunu tekrarladım. Araç bugün koşturuldu: **18 tam Altılı** (3'ten yükselmiş).

**(b) SİMÜLASYON GÜNCEL SONUCU (18 Altılı, 108 ayak, `orta`):** ikisi de tuttu 41 · yalnız 30 dk
10 · yalnız 15 dk 15 · ikisi de kaçırdı 42 → **net +5 ayak, p=0,424** (anlamsız). Yön "geç kur"
lehine ama kanıt yok. Config bazında ayak farkı: orta +5 · ayrışma +5 · genis900 +4 · v2 +4 ·
genis +3 · açgözlü +3 · **bot1_900 +0 · bot1_1800 +0 · dar +0**.
**bot1'in tam SIFIR çıkması iç kontroldür:** bot1 orana bakmaz, zamanla değişmez → teorinin
öngördüğü tam olarak budur. Simülasyonun kendisi doğrulanmış oldu.

**(c) CANLI KOL AÇILDI: `orta_15`.** `orta` ile TEK farkı kurulma anı (30 → 15 dk). Gerekçe:
simülasyonun kendi varsayımları var (oran_log anlık görüntüsü, bot2'nin geri hesaplanması,
±8 dk tolerans); gerçek kupon bunları ortadan kaldırır. **bot1 config'lerine 15 dk ikizi
AÇILMADI** — bot1 orana bakmaz, simülasyonda farkı tam +0 çıktı; ikiz açmak boş harcama olurdu.
Yalnız `orta` ikizlendi: canlıya çıkılacaksa aday o (K98-i) ve en güçlü işaret onda.
Maliyet: ~96 kombo ≈ 120 TL/Altılı.

**(d) ALTYAPI — KONFIG'e `dk` alanı, kupon artık grup grup kurulur.** İki tehlike vardı ve ikisi
de kapatıldı:
1. `kupon_zamani_kur`'un "kurulmuş mu" kontrolü **(tarih,pist,seq)** düzeyindeydi → 30 dk geçişi
   kupon kurunca pencere "bitti" sayılıyordu; 15 dk grubu **hiç kurulmazdı**. Artık kontrol
   **config** düzeyinde ve `kupon_hazirla`'ya `sadece_cfg` geçiliyor → gruplar birbirinin
   satırına DOKUNMUYOR.
2. `altili_kupon_ani.csv` upsert'i **(tarih,pist,seq)** anahtarlıydı → 15 dk geçişi 30 dk'nın
   fotoğrafını **ezerdi** ve K97'nin tüm "karar anındaki vektör" kaydı bozulurdu. Anahtara
   **`dk_grup`** eklendi; sıralamalar da grup İÇİNDE hesaplanıyor. Eski satırlar (sütunsuz) 30
   sayılır — geriye uyumlu. Raporda her config KENDİ anının fotoğrafıyla etiketleniyor.
Telegram bildirimi de gruba özel (30 dk mesajı 15 dk kuponunu içermez).

**(e) GÜVENLİK TESTİ — canlı dosyalara DOKUNMADAN.** Geçici dizinde dört sınama: (1) 15 dk yazınca
30 dk fotoğrafı duruyor mu → EVET (18+18 satır); (2) aynı grup tekrar yazılınca çoğaltıyor mu →
HAYIR; (3) iki grubun sıralamaları birbirini bozuyor mu → HAYIR, her grup kendi içinde 1-2-3;
(4) `dk_grup` sütunu olmayan eski dosya → 30 sayılıyor. **Hepsi geçti.**
Rapor yeniden üretildi, GENEL TOPLAM bağımsız CSV hesabıyla birebir (289.463,75 TL) → geçmiş
sicil bozulmadı.

**(f) 10 DK NEDEN YOK.** Takip görevi 15 dakikada bir çalışıyor; 10 dk penceresine sistematik
olarak geçiş düşmüyor → bazı günler kupon kurulamaz, örneklem yanlı kesilir. Çözümü var (görev
sıklığını artırmak) ama sistemin çalışma düzenine dokunur; **yapılmadı**, ayrı karar konusu.

**(g-EK, aynı gün) — `acgozlu900_15` de eklendi.** İlk kurulumda yalnız `orta` ikizlenmişti;
kullanıcı "sadece orta için mi?" diye sorunca gerekçe yeniden tartıldı ve **zayıf bulundu**.
Sebep: **zamanlamanın etkisi kupon GENİŞLİĞİNE göre değişebilir.** `orta` 96 kombo (dar) — bir
sıra kayması seçimi hemen bozar; `acgozlu900` 900 kombo (geniş) — çok daha toleranslı. Simülasyon
işareti de düz değil: dar +0 · orta +5 · geniş +3 · genis900 +4 · açgözlü +3. Tek config ile
"geç kurmak iyi mi" sorusu yalnızca DAR kupon için cevaplanmış olurdu.
**`acgozlu_v2`'ye ikiz AÇILMADI:** v2 zaten en yeni deney (24 kupon); üzerine ikinci bir değişken
bindirmek TEK DEĞİŞKEN ilkesini bozar. v2'nin kontrolü 30 dk'lık `acgozlu900` olarak KALIR →
BEKLEYENLER #9 bozulmadı.
Eşleşmiş çiftler doğrulandı: `orta`↔`orta_15` ve `acgozlu900`↔`acgozlu900_15` — kapsam, kombo,
dağıtım ve puan alanları birebir aynı, **tek fark `dk`**. 15 dk grubunun tavanı ~1.245 TL/Altılı.

**(g) BEKLENTİ.** 25 Eyl'e ~40 gün, günde ~2 Altılı → `orta_15` için ~80 kupon birikir. Eşleşmiş
ayak kıyası (aynı Altılı, iki zaman) yapılacak; simülasyondaki +5/p=0,42 ile kıyaslanacak.
Canlı zamanlama kararı 25 Eyl'e kadar **30 dk KALIR** — `orta_15` gözlem akışıdır, değişiklik değil.

**K106 — DIŞ ANALİZ CEVABI: K104'te YÖN HATASI bulundu, `orta`'nın siciline tek-bilet uyarısı
kondu, config kapsama alarmı eklendi, ÖLÇÜM A0 kuruldu ve **hiçbir config kalabalığı
yenemiyor**.** 17 Ağu 2026'da kullanıcı, `SISTEM.md`'yi dışarıdan analiz eden bir belge getirdi
(veriye/koda/KARARLAR'a erişimi yok, yalnız SISTEM.md metni). Belgenin doğrulanabilir her iddiası
veriyle sınandı.

**(a) BENİM HATAM — K104'ün plase pasajı iki yönden yanlış.**
1. **Yön hatası.** K104'te *"Harville favorinin plase olasılığını şişirdiği için ikinci sayı
   kesintiyi olduğundan büyük gösterir"* yazmışım. **Ters.** `t = 1 − (1+ROI)/kalibrasyon`;
   ROI=−0,140 iken kal=0,96 → t=%10,4 · kal=1,00 → t=%14,0 · kal=1,05 → t=%18,1.
   Kalibrasyon **yükseldikçe** kesinti tahmini **yükselir**. Harville favorinin ilk-2
   olasılığını şişirir → beklenen isabet fazla → ölçülen kalibrasyon **olduğundan DÜŞÜK** →
   gerçek kesinti %10,4'ten **YÜKSEK**. Doğrusu: **%10,4 bir TABANDIR**, tavan değil.
2. **Bağımsız ölçüm değil.** %14,0 doğrudan −ROI; %10,4 ise ROI'nin kalibrasyonla düzeltilmiş
   hâli. **İkisi de kâğıt sonucundan türetilmiş.** Dolayısıyla *"plase kaybının tamamı
   kesintiden geliyor"* cümlesi **döngüseldir** — kaybı kaybın kendisiyle açıklıyor.
   Dış analiz bunu 4.9'da yakaladı ve haklı.
**DÜZELTİLMİŞ İFADE:** plase kesintisi **bağımsız olarak ÖLÇÜLMEDİ**; mevcut veriyle
ölçülemez (plase havuzunun para dağılımı gerekir). Elde olan: kesinti **en az %14**, muhtemelen
daha yüksek. Ganyanın %28,3'ünden ve Altılı'nın %48,6'sından hâlâ ucuz görünüyor ama
"%10-14 bandı" ifadesi **geçersizdir**. Kalibrasyon bulgusu (0,960 → seçim zararı yok)
bundan ETKİLENMEZ; o bağımsız ölçümdür.

**(b) ÖLÇÜM A0 KURULDU — `kod/ayak_kalibrasyon.py`.** Sorun doğru teşhis edilmişti: canlı sicilde
6 adet 6/6 var, kupon düzeyinde hiçbir config ayırt edilemez ve 25 Eyl'de de edilemeyecek. Ama
**ayak düzeyinde ~2.850 gözlem** duruyordu ve kullanılmıyordu.
**Sorulan:** *"Bizim cetvelimiz, AYNI PARAYLA, kalabalığın cetvelinden daha iyi mi seçiyor?"*
Her ayakta config k at yazıyor; aynı ayakta, aynı k ile KAMU cetvelinin ilk k'si alınıp
eşleşmiş (McNemar) kıyas yapılıyor.

**TASARIM DEĞİŞİKLİĞİ — dış analizin önerisinden saptım, gerekçesiyle.** Onlar birincil ölçüt
olarak kalibrasyon oranını (R_sistem/R_kamu) önerdi ve ham R'nin **gürültü-seçim yanlılığı**
taşıdığını sentetik testle gösterdi (kasten en kötü atı seçen kol R=1,30 ile "en umut verici"
görünüyordu — kazananın laneti). Tespit **doğru**. Ama çözümleri yanlılığı azaltır, gidermez
(iki cetvelin gürültü yapısı aynı değil) ve bot2 ile kamu **%89,9 örtüştüğü** için gücü düşüktür.
**Eşleşmiş isabet bu sorunun tamamından bağışıktır:** olasılık değeri hiç kullanılmaz, yalnızca
"kazanan seçimin içinde miydi" sorulur. Kalibrasyon oranı **betimleyici** olarak basılıyor,
karara girmiyor.
Metodoloji: olasılıklar `altili_kupon_ani.csv`'den (KUPON ANI, K97 — yarış anı verisiyle
yargılamak K97'de düzeltilen sızıntının aynısı olurdu); her config **kendi dk grubunun**
fotoğrafını kullanıyor (K105); bootstrap birimi **ayak değil ALTILI olayı** (aynı Altılı'nın
altı ayağı bağımsız değil).

**(c) SONUÇ — HİÇBİR CONFIG KALABALIĞI YENMİYOR.**
| config | ayak | kapsam | yalnız-sistem | yalnız-kamu | McNemar p | karar |
|---|---|---|---|---|---|---|
| acgozlu900 | 391 | %92 | 8 | 3 | 0,227 | kenar kanıtı yok |
| bot1_900 | 342 | %97 | 55 | 49 | 0,624 | kenar kanıtı yok |
| acgozlu_v2 | 195 | %98 | 4 | 0 | 0,125 | kenar kanıtı yok |
| ayrisma900 | 204 | %94 | 3 | 1 | 0,625 | kenar kanıtı yok |
| bot1_1800 | 138 | %100 | 18 | 21 | 0,749 | kenar kanıtı yok |
| orta_15 | 42 | %100 | 3 | 1 | 0,625 | kenar kanıtı yok |
| acgozlu900_15 | 36 | %100 | 0 | 0 | 1,000 | kenar kanıtı yok |
| *dar/orta/genis/genis900* | | %69-86 | | | | **GEÇERSİZ (kapsam<%90)** |
**Hiçbirinde p<0,05.** ~2.850 ayakta, aynı parayla, bizim cetvelimiz kalabalığın cetvelinden
**ölçülebilir biçimde farklı değil.** Bu, projenin bugüne kadar ürettiği **en temiz "kenar yok"
ifadesidir** — çünkü ilk kez kupon şekli, bütçe ve kesinti değişkenlerinden arınmış olarak
yalnızca SEÇİM KATMANI test edildi.
`acgozlu_v2`'nin olay-bootstrap aralığı sıfırı içermiyor (+2,1 puan [+0,5, +4,1]) ama bu
**yalnız 4 uyumsuz ayaktan** geliyor; McNemar p=0,125. Bu sayıda uyumsuzlukta bootstrap
anti-muhafazakârdır → **aşırı okunmamalı**, ölçüt McNemar'dır.
**KAPSAM SORUNU (yeni iş):** `orta` %77 kapsamla GEÇERSİZ çıktı — `altili_kupon_ani.csv`
20-24 Tem'i hiç, 26-30 Tem'i kısmen kapsıyor (K97 geri kurma sınırı). En çok ilgilendiğimiz
config için ölçüm henüz yapılamıyor. Kapsam arttıkça tekrar koşulmalı.

**(d) `orta`'nın siciline TEK-BİLET uyarısı kondu.** Dış analiz 4.1a: `bot1_900` için
"getirinin %43'ü tek kupondan" uyarısı vardı ama `orta` için yoktu. Ölçtüm: **`orta`'nın
17.934 TL ödülünün %100'ü TEK biletten** (23.07 Ankara 2.). +8.424'lük net **bir olaydır**;
o olay çıkarsa ROI −%100. Artık raporda 1-2 isabetli her config'in yanında ödülün en büyük
bilete düşen payı yazıyor. (Aynı uyarı `acgozlu900_15` %100 ve `genis900` %100 için de çıkıyor.)
Ayrıca **GENEL TOPLAM'a kapsam notu** eklendi: o sayı bir portföy tavsiyesi değil, paralel
yürüyen deneylerin ortak faturasıdır (harcamanın çoğu 900-1800'lük gözlem akışlarından gelir;
K98-i'nin tavsiyesi yalnız `orta`).

**(e) CONFIG KAPSAMA ALARMI — `bekci.py` genişletildi.** Disiplin kuralı 8 "kupon kurulmazsa
o Altılı deneyden düşer, ölçülen en pahalı hasar budur" diyordu ama buna karşı **hiçbir alarm
yoktu**; bekçi yalnız takip nabzına bakıyordu. Nabız atmaya devam ederken bir config sessizce
kupon kurmayı bırakabilir — ve K103'ün dersi (kamu sırası K97'de sessizce düştü, **iki hafta**
fark edilmedi) bunun tekrar edeceğini söylüyor.
Yeni kural: bugün kupon kurulmuş her Altılı'da, o pencerenin dk grubuna ait TÜM aktif
config'ler bulunmalı; eksikse ekranda uyarı. Yanlış alarm koruması: config'in sicildeki ilk
gününden önceki Altılılar sayılmaz, ve yalnız **ilk koşusu başlamış** Altılılar denetlenir
(15 dk grubu henüz kurulmamışken eksik görünmesin). Salt-okunur; kupon kurmaz.
İlk çalıştırma: *"bekci: nabiz var (9 dk once), sorun yok. bekci: config kapsamasi tam."*

**(f) DIŞ ANALİZİN VERİYLE ÇÜRÜYEN İDDİALARI — üç tane.**
1. **"AGF aktif hatta hiç yok" (5.2) — YANLIŞ.** `agf1` beş yıldır toplanıyor:
   `defter.csv` (**%66 dolu**, 5.481 satır), `altili_oran_log.csv`, `katilim.csv`
   (+`agfsira1`). Doğru olan: AGF bir **özellik/rekabet ölçüsü olarak kullanılmıyor**.
   "kazi.py'ye alan eklensin" (D2) önerisi gereksiz.
2. **Devir "en güçlü aday" (5.1) — aritmetiği doğru, fırsatı yok denecek kadar seyrek.**
   Başabaş eşiği D=0,486·Y hesabı doğru. Ama (i) **payda elimizde yok** — hiçbir dosyada
   hasılat/havuz toplamı (Y) yok; (ii) daha önemlisi **Altılı'da devir neredeyse hiç olmuyor**:
   `altili_tam.csv` 6.747 olayın **24'ünde** t6_devir dolu (%0,36), `devir.csv`'de de 24
   "6'LI GANYAN" kaydı var (1.201'i SIRALI 5'Lİ — ayrı ürün, K85). İki bağımsız dosya aynı
   sayıyı veriyor. Altılı'nın %99,6'sında kazanan çıkıyor.
3. **"Kesinti dağılımı saha büyüklüğünden" (5.4) — ÖLÇTÜM, DÜŞTÜ.** 566 koşu:
   saha 4-6 %28,7 · 7-8 %26,8 · 9-10 %28,7 · 11-12 %28,2 · 13+ %29,7.
   **Saha ile kesinti korelasyonu +0,075** (sıfır), monoton değil. Irk de açıklamıyor
   (Arap %28,5 · İngiliz %28,2). Medyan her bantta %25,5-25,8 → **tarife sabit**, ortalamayı
   şişiren kuyruğun kaynağı saha değil. "Düşük kesintili koşuları seç" önerisinin dayanağı yok.

**(g) DIŞ ANALİZİN DOĞRU ÇIKAN DİĞER TESPİTLERİ.** 4.1b (TOPLAM tavsiyeyi temsil etmiyor) →
düzeltildi. 4.2 (25 Eyl / #4 çelişkisi) → doğru, bkz. (h). 4.4 (belirsizlik aralıkları
SISTEM.md'de yok) → doğru; ama endişelerinin cevabı KARARLAR'da: **λ_uzak=0,650 GA
[0,465–0,875], 1'i İÇERMİYOR** → `acgozlu_v2` gürültüye ayarlı değil. 4.6 (feed tavanı
projenin birincil kısıtıdır) → doğru ve SISTEM.md'de öne çıkarıldı. 4.7 (kapsama alarmı) →
(e)'de yapıldı; `acgozlu900_15=0` vakası masumdu (15 Ağu'da pencere kapandıktan sonra eklendi).

**(h) 25 EYLÜL ÇELİŞKİSİ ÇÖZÜLDÜ.** BEKLEYENLER #4'ün tetiği ~60 kupon; elde 7 (`orta_15`) ve
6 (`acgozlu900_15`) var, 25 Eyl'e ~40 yarış günü kaldı → tetik o tarihte **dolmayacak**.
Kural 6 ("tetik tarih değil sayıysa sayıya bakılır") gereği: **25 Eylül kararı zamanlama
kolunu KAPSAMAZ.** O tarihte verilecek karar sistem modu kararıdır (K42/K48); zamanlama kolu
kendi sayısal tetiğiyle, muhtemelen Kasım'da değerlendirilir. İki tarih birbirine bağlanmaz.

**(i) KATILMADIĞIM ÖNERİ.** Dış analiz 15 dk ikizlerinin (C2) **yapısal gerekçeyle**
kapatılmasını önerdi: 30→15 geçişinde en çok bilgi kazanan ayak, sürüklenmesi en az olan
1. ayaktır. Argüman kısmen doğru ama kol **iki gün önce açıldı**, Altılı başına 120 TL ve
elde simülasyondan +5 ayaklık bir işaret var. Veri toplamaya başlamış bir kolu iki gün sonra
teoriyle kapatmak, projenin "ölçmeden konuşma" ilkesine ters. **Kol açık kalır.**
`bot1_1800` için önerileri (C1) yerinde — 900→1800 ayak genişliğini yalnız %12 artırıyor
(3,107→3,487) ve K98-e bot1'i zaten portföyden dışlamıştı — ama config kullanıcının açık
isteğiyle eklendi; **karar kullanıcınındır**, tek taraflı emekli edilmedi.

**(j) ARAÇ:** `kod/ayak_kalibrasyon.py` (offline, salt-okunur). Ölçütler dosya başında,
sonuç görülmeden bağlandı. `bekci.py` genişletildi (nabız + kapsama, ikisi de salt-okunur).
Canlı seçim/dağıtım/config koduna **dokunulmadı**.

---

**K107 — SESSİZ BİR GÜN KAYBI BULUNDU (16 Ağu: defter+paper SIFIR), A0'ın GÜCÜ ölçüldü ve
ifadesi düzeltildi, ikinci dış denetim raporu değerlendirildi.** 18 Ağu 2026.

## (a) 16 AĞUSTOS 2026 — TAKİP DÖNDÜ, DEFTER YAZILMADI. Sicildeki TEK böyle gün.

Hasar taraması sırasında `defter.csv`'de 16 Ağu'nun **tamamen boş** olduğu görüldü. Kontrol
edildi, tesadüf değil — o gün sistemin diğer her parçası çalışmıştı:

| kayıt | 15 Ağu | **16 Ağu** | 17 Ağu |
|---|---|---|---|
| `takip_gecis.txt` "bitti" mührü | 16 koşu | **17 koşu** | 10 koşu |
| `altili_oran_log.csv` | 1.349 | **1.430** | 847 |
| `altili_kupon.csv` | 96 | **168** (7 config × 4 Altılı) | 84 |
| `altili_kupon_ani.csv` | 225 | **442** (sicildeki en yüksek) | 252 |
| **`defter.csv`** | 148 | **0** | 102 |
| **`paper_kupon.csv`** | 18 | **0** | 14 |

Yani: takip her 15 dk'da geçiş yaptı, 17 koşuyu işleyip "bitti" mührünü bastı, oran kaydetti,
dört Altılı'ya yedi config kupon kurdu — **ama kâğıt defterine ve paper testine tek satır
girmedi.** 32 yarış gününün taraması yapıldı: **bu tek gün.** Diğer 31 günün hepsinde
"bitti" mührü sayısı ile deftere yazılan koşu sayısı **birebir eşit**.

**KAYIP:** o günün kalibrasyon kaydı, ganyan ROI'si, top-pick isabeti ve paper kuponları.
Geri kurulamaz — `defter.py kaydet` yarış-öncesi anlık kayıttır; şimdi geriye dönük yazmak
K36'nın açıkça yasakladığı şeydir (kapanış oranıyla sahte "tahmin" üretmek). **Kayıp kalıcıdır
ve öyle kalacaktır.**

**KÖK NEDEN BULUNAMADI — ve bu, bulgunun kendisidir.** Elenenler: `hesapla()` bugün 16 Ağu
verisiyle yeniden çağrıldı, ISTANBUL 93 / IZMIR 67 puanlı satır döndürdü → **model çalışıyordu**;
zaten `altili_canli.py` de aynı `hesapla`'yı kullanır ve o gün kupon kurdu. Yazma izni de
sorunsuzdu (aynı klasöre `oran_log` ve `altili_kupon` yazıldı). Geriye iki aday kalıyor —
`defter.yaz_tg`'nin istisna fırlatması (K39'un adını koyduğu "dosya Excel'de açık" durumu) ya da
n=0 dalına düşmesi. **Hangisi olduğu bilinemiyor**, çünkü:

> `isle_kosu` içindeki üç tanı mesajı da (`DEFTER YAZILAMADI`, `deftere yazılmadı: kapsam dışı`,
> `paper kupon üretilemedi`) `print`'e gidiyordu. Görev **pythonw** ile sessiz koştuğu için
> stdout hiçbir yere düşmüyor. `_log`'a bağlı olan tek şey geçiş özetiydi ve o özet o gün
> **"işlenen 1, bekleyen 16"** diye tıkır tıkır yazmaya devam etti.

Bu, K103'ün (kamu sırası iki hafta sessizce düştü) aynısıdır: **sistem çalışıyor gibi
görünürken bir kolu ölmüştü.** Fark şu ki K103 iki haftada, bu iki günde yakalandı — çünkü
K106'da hasar taraması alışkanlık hâline gelmişti.

**İKİ DÜZELTME YAPILDI:**

1. **`takip.py` — sessizlik kapatıldı.** Üç mesaj da artık `_log`'a düşüyor
   (`veri/takip_log.txt`). Yeni `_gorunur_log()` sarmalayıcısı tam korumalı: `_log`'un kendisi
   patlarsa `isle_kosu` **çökmemeli** (çökerse koşu "bitti" mührünü alamaz ve sonraki geçiş
   aynı koşuyu yeniden dener). Davranış değişikliği yok — yalnızca kayıt eklendi.
2. **`bekci.py` — üçüncü denetim: DEFTER KAPSAMA.** Kural: bugün "bitti" mührü almış koşu
   sayısı ile `defter.csv`'de bugüne yazılmış ayrı koşu sayısı karşılaştırılır. Defter yazımı
   mühürden **önce** olduğu için gecikme yanılması yok. Eşik: **≥3 koşu işlenmişken ≥2 koşu
   eksikse** uyarır (tek koşunun tg'den düşmesi normaldir).
   **GERİYE DÖNÜK SINANDI: 32 gün, 1 alarm, o da 16 Ağu (17 işlendi / 0 yazıldı). Sıfır yanlış
   alarm.** Salt-okunur.

**DERS (disiplin kuralı 8'e ek):** *bir kolun sessizce ölmesi, o kolun hata vermesinden daha
pahalıdır.* Hata veren kol fark edilir; sessiz kol veri kaybettirmeye devam eder. Bundan sonra
`except` bloğuna düşen her mesaj **log'a da** yazılacak; `print` tek başına kayıt sayılmaz.

## (b) ÖLÇÜM A0'IN GÜCÜ — K106'daki İFADEM FAZLA GÜÇLÜYDÜ, DÜZELTİLDİ

K106'da *"hiçbir config kalabalığı yenmiyor"* yazdım. Dört config için bu **söylenemezdi**.
Tam binom testinde iki yönlü α=0,05'e ulaşmak için **en az 6 uyumsuz çift** gerekir:

| uyumsuz çift n | hepsi tek yanlı olsa p |
|---|---|
| 3 | 0,250 |
| 4 | 0,125 |
| 5 | 0,0625 |
| **6** | **0,031** ← ilk yeterli |

Yani n=4 olan bir config'te sonuç **4-0** çıksa bile p=0,125'tir; test **hiçbir sonuçla**
anlamlılık üretemezdi. Böyle bir config için "kenar kanıtı yok" demek, ölçüm yapılmadığı hâlde
ölçüm yapılmış gibi konuşmaktır. `kod/ayak_kalibrasyon.py`'ye `ASGARI_UYUMSUZ = 6` eşiği ve
**BAKILAMAZ** hükmü eklendi; karar akışı artık: kapsam → **güç** → p.

**DÜZELTİLMİŞ A0 TABLOSU (18 Ağu):**

| config | ayak | kapsam | yalnız-sis | yalnız-kamu | p | karar |
|---|---|---|---|---|---|---|
| `acgozlu900` | 402 | %92 | 9 | 3 | 0,146 | **kenar kanıtı yok** |
| `bot1_900` | 353 | %97 | 57 | 49 | 0,497 | **kenar kanıtı yok** |
| `bot1_1800` | 149 | %100 | 20 | 21 | 1,000 | **kenar kanıtı yok** |
| `acgozlu_v2` | 206 | %99 | 4 | 0 | 0,125 | BAKILAMAZ (4<6) |
| `ayrisma900` | 204 | %94 | 3 | 1 | 0,625 | BAKILAMAZ (4<6) |
| `orta_15` | 53 | %100 | 3 | 1 | 0,625 | BAKILAMAZ (4<6) |
| `acgozlu900_15` | 47 | %100 | 0 | 0 | 1,000 | BAKILAMAZ (0<6) |
| `dar` `orta` `genis` `genis900` | 275-424 | %69-86 | — | — | — | GEÇERSİZ (kapsam<%90) |

**GEÇERLİ HÜKÜM:** `acgozlu900`, `bot1_900` ve `bot1_1800` için — ~900 ayakta, aynı parayla —
bizim cetvelimiz kalabalığınkinden **ölçülebilir biçimde farklı değil.** Diğerleri için
**henüz veri yok**; hüküm yok.

**ÇOKLU TEST NOTU (dış raporun haklı olduğu nokta).** A0'da 11 config × 2 test (McNemar +
olay-bootstrap) bakılıyor. Olay-bootstrap'te `acgozlu_v2` (+1,9 puan [+0,5, +3,9]) ve
`acgozlu900` (+1,5 [+0,0, +3,0]) güven aralıkları sıfırı dışlıyor — **ama bu bir kenar bulgusu
değildir.** Üç sebep: (1) `acgozlu_v2`'de McNemar aynı veride BAKILAMAZ diyor, yani sonucu 4
uyumsuz çift taşıyor; (2) 11 config'te %95 GA'lardan birinin şansa sıfırı dışlaması ~0,55 kez
beklenir; (3) yüzdelik bootstrap, bu kadar seyrek ayrık veride anti-muhafazakârdır.
**Ön-kayıtlı birincil ölçüt McNemar'dır** (K106'da sonuç görülmeden bağlandı); bootstrap
betimleyicidir. Kayda geçiyor ki ileride biri bu sayıyı bulup "kenar vardı" demesin.
Bugüne kadar hiçbir düzeltme sonuç değiştirmedi çünkü **sicilimiz baştan sona boş** — FDR
düzeltmesinin pratikte düzeltecek bir pozitifi yok.

## (c) İKİNCİ DIŞ DENETİM RAPORU — 2 iddia çürüdü, 3 sayı/okuma hatası, 1 gerçek katkı

Kullanıcı `at_dis_denetim_raporu.md` başlıklı ikinci bir dış analiz getirdi (yine yalnız
`SISTEM.md` metnine bakıyor; veri/kod/KARARLAR erişimi yok).

**ÇÜRÜYENLER:**
- **"ACİL: `plase_test.py` sonucu hiçbir yere girmemiş"** — YANLIŞ ve iddianın en yüksek
  önceliklisiydi. Araç kesinti değil **ROI** ölçer; sonucu (−%12,5 / −%14,0) **K42'de zaten
  kayıtlı.** KARARLAR.md'de tek arama yapılsaydı çürürdü; rapor "K1–K106 okundu" diyor.
- **"`bot1_900` aktif ama K98-e portföye konmamalı diyor → tutarsızlık"** — YANLIŞ. K98-e
  *"canlı portföye"* der; `bot1_900` **kâğıt akışıdır**, canlı portföy değildir. Çelişki yok.

**SAYI/OKUMA HATALARI:**
- **"`orta` sicilinde 552 kupon"** — hayır, **93 kupon**. 552 `altili_kupon.csv`'deki *satır*
  sayısına yakın (kupon = 6 ayak = 6 satır). **6 kat şişirilmiş** bir taban.
- R² etiketi zaten K106'da düzeltilmişti (katsayı geri-kazanımı, öngörü gücü değil); rapor
  düzeltilmemiş gibi yazıyor.
- `defter.csv` sayıları dolu-satır ayrımı yapılmadan alınmış.

**GERÇEK KATKI (tek):** post-hoc güç analizi istemesi. (b) maddesi bunun ürünüdür ve **benim
hatamı düzeltti.** Bir dış gözün en çok işe yaradığı yer, veriye erişmeden de sorulabilen
metodoloji sorusu oldu — sayı iddialarında ise erişimsizlik onu sürekli yanılttı.

**İLKE (K106'daki gözlemin pekişmesi):** dış analiz, *yöntem* sorularında değerli; *sayı*
iddialarında ise SISTEM.md'den okuduğunu veriyle karıştırıyor. Bundan sonraki dış raporlarda
sıra: önce yöntem eleştirisi sınanır, sayı iddiaları doğrudan veriye vurulur.

## (d) BEKLEYENLER #2'NİN ÖN KOŞULU MEĞER KARŞILANMIŞ — 4'lü/5'li kolu AÇILABİLİR

BEKLEYENLER #2 *"ÖN KOŞUL — veri yok: 4'lü ve 5'li bahislerin kendi temettü serileri arşivde
YOK"* diyordu ve yapılacaklar listesinin 1. maddesi "ham feed'de var mı, tara" idi. **Tarandı:
veri K94'ten beri elimizde.** `veri/nli_ganyan.csv` (K94'ün yan ürünü, kimse fark etmemiş):

| ürün | olay | temettü dolu | ayak kodları dolu | medyan temettü |
|---|---|---|---|---|
| 3'lü | 8.060 | ✅ | ✅ | 73 TL |
| **4'lü** | **5.691** | ✅ | ✅ | **249 TL** |
| **5'li** | **6.519** | ✅ | ✅ | **1.006 TL** |
| 6'lı | 6.813 | ✅ | ✅ | 5.774 TL |
| 7'li | 359 | ✅ | ✅ | 170.016 TL |

Temettü **ve** ayak race_kod'ları birlikte duruyor → backtest kurulabilir. BEKLEYENLER #2'nin
1-3. maddeleri **düşer**, doğrudan 4. maddeden (backtest) başlanır.
**Önceki beklenti değişmiyor, düşük:** K75 aynı mekanizmayı 6 ayakta ölçtü ve λ=0,25'ten
itibaren ROI kötüleşti. Yeni olan tek şey, hipotezin **daha kısa çarpımda** hiç sınanmamış
olması. Ölçüt yine sonuç görülmeden bağlanacak.

## (e) HASAR ORANI ÖLÇÜLDÜ (son 14 gün)

`kod/kayip_raporu.py`: **14 günün 4'ü tamamen temiz.** 2 kurulmayan Altılı (7 kupon/Altılı →
14 kupon deneyden düştü) · **0 geç kurulan kupon** (en sinsi tür hiç görülmedi) · 0 yarış
sonrası kayıt · 35 düşen defter koşusu — buna 16 Ağu'nun 17 koşusu dâhil, yani **düşen defter
kayıtlarının yarısı tek bir günden.** Araç kendi sayısının **alt sınır** olduğunu söylüyor
(`altili_temettu.csv`'de eksik olan Altılı burada da görünmez).

## (f) `prep()` DAĞILIM KAYMASI — backtest sayıları canlıya DOĞRUDAN taşınmaz

`altili_backtest.py`'nin `prep()`'i yalnızca **muhtemel + kapanış oranı olan ve tek kazananı
bulunan** koşuları alır. Canlı taraf ise kartta ne varsa puanlar. Bu, backtest evrenini canlı
evrenden **sistematik olarak** ayırır (eksik oranlı/çoklu kazananlı koşular temizlenmiş bir
örneklem). K96 ve benzeri backtest sayıları bu yüzden canlı beklentiye **birebir çevrilemez**;
yön göstergesidir, seviye göstergesi değil. SISTEM.md'ye not düşüldü.

**Dokunulan dosyalar:** `kod/bekci.py` (üçüncü denetim), `kod/takip.py` (yalnız log ekleme,
davranış değişikliği yok), `kod/ayak_kalibrasyon.py` (güç eşiği), `SISTEM.md`, `BEKLEYENLER.md`.
**Canlı seçim/dağıtım/config koduna DOKUNULMADI.**

---

**K108 — 4'LÜ / 5'Lİ KOLU ÖLÇÜLDÜ → REDDEDİLDİ. BEKLEYENLER #2 KAPANDI. "Daha kısa çarpım
kenarı korur" hipotezi çürüdü; K98-h tavanı kısa üründe de birebir geçerli.** 18 Ağu 2026.
Araç: `kod/nli_backtest.py` (salt offline, hiçbir dosyaya yazmaz).

## (a) TASARIM — eşleşmiş üçlü, kolun asıl kazanımı

TJK'da 4'lü/5'li/6'lı **aynı koşuda biter ve ayakları iç içedir**: 6'lının son 5 ayağı = 5'li,
son 4 ayağı = 4'lü. Arşivdeki **4.931 üçlünün %100'ünde** doğrulandı. Bu, hipotezi izole eden
bir tasarım verdi: aynı gün, aynı pist, aynı saha, aynı son koşu, aynı para — **tek değişken
kaç ayak tutturman gerektiği.** Gün/pist/zorluk etkisi tamamen elenir.

**AYNI PARA, AYNI KOMBO DEĞİL.** Resmî 2026 birim fiyatları eşit değil (K86): 4'lü 1,75 ·
5'li 1,50 · 6'lı 1,25 TL. Kombo eşitlemek 4'lüye %40 fazla para harcatırdı. Bütçe **TL
cinsinden** eşitlendi: Altılı 900 kombo × 1,25 = **1.125 TL** → 4'lü 642 · 5'li 750 kombo.
İkinci bütçe 120 TL. Ödeme yalnız tam isabet (4/4, 5/5, 6/6); Altılı tarafı da `kademeli=False`
alındı ki üç ürün aynı kuralla yarışsın.

**Örneklem:** OOS 2025-26 **990** eşleşmiş üçlü (birincil) · 2026 **330** (fiyat-güvenli
alt küme). Puanlar `altili_olasilik_bot1.csv` (walk-forward, eğit ≤2023 · harman 2024).

## (b) İKİ DOĞRULAMA — ölçütle birlikte, sonuç görülmeden bağlanmıştı

**(a) Dağıtıcı eşdeğerliği: GEÇTİ.** N-ayak dağıtıcıları `altili_backtest.py`'nin 6-ayak
mantığının genellemesidir; mantık sessizce değişmesin diye 4.000 rastgele kart × 12 ayarda
orijinalle karşılaştırıldı: **fark 0.** N=6'da birebir aynı kuponu üretiyorlar.

**(b) Boru hattı kontrolü: GEÇTİ ama K94'ten sapıyor.** İma edilen iade
= medyan[(temettü/birim) × P_kamu(kazanan kombo)]:

| ürün | 2026 ima edilen kesinti | K94 (kalibre) | OOS 2025-26 |
|---|---|---|---|
| 3'lü | %51,9 | %45,4 | %52,9 |
| 4'lü | %54,0 | %45,6 | %59,9 |
| 5'li | %57,1 | %46,8 | %65,6 |
| 6'lı | %60,8 | %48,6 | %66,8 |

**Sıralama aynı** (ayak arttıkça kesinti artıyor) ama benim sayılarım 6-12 puan yüksek.
Sebep bilinen: K94 ayak başına yanlılığı `k=0,978` çözerek üstel düzeltme uyguladı ve 6'lıyı
**%48,6'ya çapaladı**; benimki **ham/kalibresiz**, yani üst tahmindir. Karar için önemli olan
sıralamadır ve o birebir tutuyor.
**Asıl doğrulama başka yerden geldi:** ölçülen kupon ROI'leri, bağımsız hesaplanan kesintinin
tam üstüne oturdu — 6'lı ROI −%63,4 vs kesinti %66,8 · 4'lü −%58,7 vs %59,9. **Kupon ne
kazandırıyor ne kaybettiriyor; sadece kesintiyi ödüyor.** Projenin merkezi bulgusunun
üçüncü bir üründen bağımsız teyidi.

## (c) S1 — MEKANİZMA YOK. Hipotez çürüdü.

Ölçüt önceden şuydu: eşleşmiş ROI farkının %95 GA **alt sınırı**, K94'ün kesinti farkından
(D4 taban +3,0 · D5 taban +1,8 puan) **büyük olmalı**. 16 test (2 pencere × 2 bütçe ×
2 dağıtıcı × 2 ürün):

| pencere · bütçe · dağıtıcı | D4 (4'lü − 6'lı) | D5 (5'li − 6'lı) |
|---|---|---|
| OOS · 1.125 TL · açgözlü | +4,7 [−6,5, +15,1] | +6,5 [−4,3, +17,3] |
| OOS · 1.125 TL · kapsam | −1,5 [−18,2, +13,2] | −1,7 [−18,4, +14,7] |
| OOS · 120 TL · açgözlü | **+21,3 [+7,9, +33,8]** ← tek geçen | +11,6 [−0,3, +23,6] |
| OOS · 120 TL · kapsam | +8,4 [−12,2, +27,4] | −1,7 [−18,9, +14,7] |
| 2026 · 1.125 TL · açgözlü | +3,8 [−20,8, +26,2] | +9,9 [−13,3, +32,7] |
| 2026 · 1.125 TL · kapsam | −18,9 [−48,5, +4,8] | −8,8 [−34,5, +12,1] |
| 2026 · 120 TL · açgözlü | +22,6 [−7,4, +50,0] | +17,5 [−8,6, +42,9] |
| 2026 · 120 TL · kapsam | +13,8 [−22,3, +45,7] | +3,4 [−28,2, +31,9] |

**16 testin 1'i geçti.** α=0,05'te şansa beklenen yanlış pozitif **0,8** — yani gözlenen tam
olarak boş hipotezin öngördüğü kadar. Üstelik geçen hücre **fiyat-güvenli alt kümede
tekrarlamıyor** (aynı hücre 2026'da +22,6 [−7,4, +50,0] → geçmiyor) ve **öteki dağıtıcıda
tekrarlamıyor**. K107'de FDR notunu yazarken tarif ettiğim desenin ta kendisi.
**HÜKÜM: mekanizma yok. Ne kadar fark varsa kesintinin ucuzluğuyla açıklanıyor.**

*Not (ölçütü sertleştiren yönde):* eğer taban olarak K94'ün kalibre farkları yerine (b)'deki
kendi ham farklarım kullanılsaydı taban +6,8/+3,7'ye çıkardı ve tek geçen hücre de düşerdi.
Ölçüt sonradan değiştirilmedi; kayda geçiyor ki hüküm bu yönde daha da güçlü.

## (d) S2 — OYNANAMAZ. 24 hücrenin sıfırında ROI ≥ 0.

| ürün | en iyi hücre | en kötü hücre |
|---|---|---|
| 4'lü | **−%38,5** | −%69,0 |
| 5'li | −%43,6 | −%60,4 |
| 6'lı | −%50,1 | −%70,8 |

Ön-kayıtlı S2 eşiği "mutlak ROI ≥ 0 **ve** GA alt sınırı > −%5" idi. En iyi hücre bile
−%38,5. Kullanıcının çerçevesi *"sürdürülebilir yol"* (K48): **−%38, −%50'den iyi olduğu için
oynanabilir olmaz.** 4'lü Altılı'dan ucuz bir kayıptır, kâr değil.

## (e) S3 — K98-h TAVANI KISA ÜRÜNDE DE GEÇERLİ. Kolun en öğretici sonucu.

Ayak sayısı azaldıkça aynı para çok daha geniş ayak alıyor (642^(1/4)=**4,97 at/ayak** vs
900^(1/6)=**3,08**) ve isabet patlıyor. Ama ödeme tam o oranda düşüyor:

| bütçe · dağıtıcı | ürün | isabet | isabet katı | ort. ödeme | ödeme katı | **çarpım** |
|---|---|---|---|---|---|---|
| 1.125 TL · açgözlü | 4'lü | %63,0 | 4,26× | 696 TL | 0,26× | **1,12** |
| | 5'li | %32,1 | 2,17× | 1.418 TL | 0,53× | **1,16** |
| | 6'lı | %14,8 | 1,00× | 2.655 TL | 1,00× | 1,00 |
| 120 TL · açgözlü | 4'lü | %25,7 | 6,27× | 211 TL | 0,25× | **1,59** |
| | 6'lı | %4,1 | 1,00× | 831 TL | 1,00× | 1,00 |

Sekiz hücrenin hepsinde çarpım **0,73 – 1,59** bandında, medyanı ~1,09. Yani:
**isabeti 4-8 kat artırıyorsun, ödemen 0,15-0,54 katına düşüyor, net elinde hemen hemen
hiçbir şey kalmıyor.** K98-h Altılı'da "kapsamı genişletmek = kalabalığa katılmak" demişti;
burada aynı şey **ayak sayısını azaltarak** yapıldı ve **aynı duvara** çarpıldı. Tavan bir
kupon-şekli özelliği değil, **piyasa özelliği** — kolay tutan bahsi herkes tutuyor.

## (f) KARARLAR

1. **BEKLEYENLER #2 KAPANDI.** 4'lü/5'li kolu **reddedildi**. Yeniden açılması için yeni
   bir mekanizma iddiası **ve** yeni veri gerekir; "bir daha bakalım" gerekçe değildir.
2. **K84'ün devir gözlemi açıklandı.** Devir günlerinde 5 ayak medyanının 201 kat sıçraması
   gerçekti ama **fırsat değildi**: o günler 6/6'nın kimsenin bilemediği günlerdir, yani
   5'li de zordur. Zorluğun göstergesi, açıklığın değil (K94'ün 7'li için söylediğinin aynısı).
3. **K75 farklı bir açıdan doğrulandı.** K75 "kısa çarpımda bakılmadı" boşluğuyla kapanmıştı;
   o boşluk artık kapalı. Ayak başına kenar (K74) **hiçbir çarpım uzunluğunda** paraya
   dönüşmüyor.
4. **12 negatif Altılı testinden sonra kalan tek yapısal fikir de öldü.** Ürün kolu
   (K94'te kesinti tarafından, K108'de kupon tarafından) tamamen kapandı.

## (g) DOKUNULMAYANLAR

`kod/nli_backtest.py` yeni ve salt-okunur; hiçbir dosyaya yazmaz. Canlı seçim/dağıtım/config
koduna, `altili_backtest.py`'ye, defter/paper akışına **dokunulmadı**. `altili_backtest.py`'nin
6-ayak fonksiyonları kopyalanmadı, genelleştirildi ve eşdeğerliği sınandı (bkz. (b)-a).

---

**K109 — AYAK DÜZEYİ SİCİLİ ÇIKARILDI: bot1 ailesi gerçekten SÜRPRİZ yakalıyor (yapısal, gerçek),
ama "+%19,4 ganyan ROI" bir YANILSAMA çıktı — ORAN SÜRÜKLENMESİ TUZAĞI bulundu ve kayda geçti.**
18 Ağu 2026. Araç: `kod/ayak_analiz.py` (salt-okunur). Kullanıcının sorusu: *"Altılı tutması
önemli değil — koşu bazında en başarılı kuponlar hangileri ve NEDEN?"*

**Kapsam:** 20 Tem – 18 Ağu, **1.896 sonuçlanmış ayak**, 7 aktif config, kupon-anı kapsamı %91.
Kupon anındaki kimlikler `altili_kupon_ani.csv`'den okundu (K97 — yarış anı verisiyle
yargılamak sızıntı olurdu).

## (a) ⚠️ ORAN SÜRÜKLENMESİ TUZAĞI — bu maddenin kendisi bir bulgudur

İlk ölçümde `bot1_900` için **ayak-ganyan ROI +%19,4** çıktı (kamu aynı genişlikte −%24,2;
fark **+43,5 puan**). Bu projede bu büyüklükte pozitif bir sayı hiç görülmemişti, o yüzden
yayımlanmadan önce kırılmaya çalışıldı. **Kırıldı.**

**Kupon anındaki MUHTEMEL oran, kapanışa doğru sistematik olarak kayıyor** (1.002 kazanan ayak,
son kayıt ort. 16 dk kala):

| kupon-anı oranı | n | ortalama değişim |
|---|---|---|
| <4 | 519 | **+%61,1** ← açılıyor |
| 4-8 | 322 | +%1,5 |
| 8-16 | 125 | −%23,9 |
| 16+ | 36 | **−%61,4** ← çöküyor |

Erken muhtemel oran gürültülüdür ve para geldikçe ortalamaya döner. **Sonuç: kupon anında
"sürpriz" görünen at, kapanışta o kadar sürpriz değildir.** Ve bu yanlışlık **taraflıdır** —
tam olarak orana kör config'leri kayırır, çünkü onlar sürekli "yüksek oranlı görünen" atı seçer.

| config | ROI (muhtemel) | ROI (son görülen) | **yanılsama** |
|---|---|---|---|
| **bot1_900** | **+%19,4** | **−%17,9** | **+37,3 puan** |
| **bot1_1800** | **+%4,2** | **−%21,3** | **+25,5 puan** |
| acgozlu900 | −%27,1 | −%22,4 | −4,7 |
| acgozlu_v2 | −%23,4 | −%20,6 | −2,7 |
| orta | −%32,1 | −%15,0 | −17,1 |

Ayrıca dayanıksızdı: 223 isabetin **en büyük 10'u çıkarılınca +%19,4 → −%5,3.**

**KURAL (kayda geçiyor):** *müşterek bahiste ödenen fiyat kapanış fiyatıdır; kupon anındaki
muhtemel oranla hesaplanan hiçbir kazanç **tahsil edilemez**. Muhtemel oran değer hesabında
KULLANILAMAZ.* Mevcut ölçümler bu hatayı taşımıyor (defter `ganyan_kapanis` kullanır; A0 orana
hiç bakmaz; K104 kapanışla ölçtü) — tuzak bugün ilk kez bu yeni ölçüde kuruldu ve yakalandı.

**DÜZELTİLMİŞ HÜKÜM (son görülen fiyatla, olay-bootstrap %95 GA):**

| config | Altılı | ROI | %95 GA | hüküm |
|---|---|---|---|---|
| acgozlu900 | 75 | −%22,4 | [−29,7, −14,7] | negatif, kesin |
| bot1_1800 | 27 | −%21,3 | [−33,2, −7,1] | negatif, kesin |
| acgozlu_v2 | 37 | −%20,6 | [−29,7, −11,1] | negatif, kesin |
| bot1_900 | 63 | −%17,9 | [−27,5, −7,1] | negatif, kesin |
| orta | 80 | −%15,0 | [−26,7, −3,1] | negatif, kesin |
| acgozlu900_15 | 10 | −%6,6 | [−21,7, +10,1] | ayırt edilemiyor |
| orta_15 | 11 | +%12,6 | [−22,8, +43,9] | ayırt edilemiyor |

**Hiçbir config'te pozitif kanıt yok.** Üstelik "son görülen" de kapanış değil (~16 dk kala);
sürüklenme oradan sonra da sürer ve kazananın fiyatını genelde daha da düşürür → **bu ROI'ler
hâlâ iyimser taraftadır.**

## (b) GERÇEK VE YAPISAL BULGU — iki config ailesi birbirinden ciddi biçimde farklı

Ayak isabeti, **kazananın kamu sırasına** göre ayrıştırılınca aileler net ayrılıyor:

| config | kamu 1. (favori) | kamu 5+ (sürpriz) |
|---|---|---|
| acgozlu900 | **%98,3** (118) | %27,9 (147) |
| acgozlu_v2 | **%100,0** (60) | %31,7 (82) |
| orta | %97,5 (122) | **%1,3** (154) |
| **bot1_900** | %77,7 (103) | **%46,0** (137) |
| **bot1_1800** | %71,1 (45) | **%48,3** (58) |

Kazananın oran kovasında aynı yapı:

| config | oran <2 | oran 16+ |
|---|---|---|
| orta | %100,0 | **%0,0** |
| acgozlu900 | %100,0 | %7,4 |
| **bot1_900** | %91,4 | **%44,9** |

**Bu, orana körlüğün ders kitabı davranışıdır ve gerçektir:** bot1 favoride ~20-27 puan
bırakıyor, sürprizde ~18-20 puan kazanıyor. Yani bot1 "daha iyi" değil, **farklı** — ve
temettünün büyük olduğu yerde daha çok bulunuyor. **Ama (a)'da görüldüğü gibi bu, paraya
dönüşmüyor**; çünkü kupon anında sürpriz görünen at kapanışta sürpriz değil.
`orta`'nın %1,3'ü ise ayrı bir uyarıdır: 154 sürpriz ayağın 2'sini tutmuş — **`orta`
neredeyse tanım gereği kalabalığın kendisidir.**

## (c) MARJİNAL KATKI — eklenen HİÇBİR at parasını çıkarmıyor

Kazananın bizim kendi sıralamamızdaki yerinden türetildi (1.726 ayak):

| n. at | bu at kazandırdı | kümülatif isabet | kombo çarpanı | **marjinal verim** |
|---|---|---|---|---|
| 1 | %27,2 | %27,2 | 1,00 | — |
| 2 | %17,3 | %44,5 | 2,00 | **0,82** |
| 3 | %14,4 | %58,9 | 1,50 | **0,88** |
| 5 | %9,3 | %77,9 | 1,25 | **0,91** |
| 8 | %3,9 | %95,2 | 1,14 | **0,91** |
| 10 | %1,3 | %98,3 | 1,11 | **0,91** |

**Hiçbiri 1'i geçmiyor** ve 3. attan sonra **0,87-0,92'de düz gidiyor** — yani "tatlı nokta"
diye bir şey yok, genişletmek her yerde eşit derecede biraz zararlı. Bu, K98-h tavanının ve
K108'in ayak düzeyindeki üçüncü ifadesidir. Üstelik burada maliyet **tek ayak** üzerinden
hesaplandı; kupon 6 ayağın çarpımı olduğu için gerçek maliyet çok daha ağırdır.

## (d) BANKER SİCİLİ — banker yazmak, kalabalığa katılmaktır

| config | banker ayak | isabet | kamu aynı (1 at) | FARK |
|---|---|---|---|---|
| acgozlu900 | 96 | %36,5 | %35,9 | **−1,1** |
| acgozlu_v2 | 53 | %35,8 | %35,8 | **+0,0** |
| bot1_900 | 54 | %31,5 | %28,8 | +3,8 |
| bot1_1800 | 22 | %18,2 | %18,2 | **+0,0** |
| orta | 20 | %55,0 | %52,9 | **+0,0** |
| acgozlu900_15 | 15 | %26,7 | %26,7 | **+0,0** |
| orta_15 | 3 | %33,3 | %33,3 | **+0,0** |

**Yedi config'in beşinde fark tam olarak +0,0** — yani tek at yazdığımızda **kamunun favorisini
yazıyoruz.** Banker, kuponun en pahalı kararıdır (tutmazsa kupon o anda biter) ve orada
sistemin kalabalıktan hiçbir ayrımı yok. K101'in banker takası reddine ek bir gerekçe.

## (e) ADİL KIYAS ÖZETİ (aynı ayak, aynı sayıda at, kamu cetveli)

| config | ayak | ort. genişlik | HAM isabet | FARK (kamuya göre) | VERİM (at/isabet) |
|---|---|---|---|---|---|
| acgozlu900_15 | 60 | 4,13 | %73,3 | +0,0 | 5,64 |
| bot1_1800 | 162 | 4,16 | %63,6 | +0,6 | 6,54 |
| acgozlu_v2 | 222 | 4,05 | %63,5 | +2,3 | 6,38 |
| acgozlu900 | 450 | 4,04 | %63,3 | +1,7 | 6,38 |
| bot1_900 | 378 | 3,70 | %61,1 | +2,5 | 6,06 |
| orta_15 | 66 | 2,20 | %56,1 | +4,5 | **3,92** |
| orta | 558 | 2,17 | %45,9 | **−0,9** | 4,73 |

**HAM isabeti genişlik belirler; tek başına kıyas aracı değildir** (K87'nin uyarısı).
FARK sütunu A0'ın (K106) aynı ölçüsüdür ve orada hiçbiri anlamlı çıkmamıştı — burada da
işaretler küçük ve tutarsız. `orta` ayrıca kupon-anı kapsamı %78 olduğu için ön-kayıtlı %90
eşiğinin altında; sayısı okunur, karara bağlanmaz.
**En ucuz isabet `orta_15`'te** (3,92 at/isabet) ama n=66.

## (f) ZAMANLAMA KOLUNA ÖN-KAYITLI TAHMİN (yeni; K105/BEKLEYENLER #4)

(a)'daki sürüklenme, zamanlama kolu için **bir mekanizma** veriyor: kamu fiyatı geç saatte
daha bilgili. bot2 = softmax(α·ln bot1 + γ·ln p_kamu) ve p_kamu kupon anındaki orandan
türetiliyor → **30 dk'daki p_kamu, 15 dk'dakinden daha gürültülü olmalı.**

> **TAHMİN, ŞİMDİ YAZILIYOR:** 15 dk config'leri, 30 dk ikizlerini ayak isabetinde
> **geçmelidir.** Şu anki durum bu yönde ama örneklem hükümsüz: `acgozlu900_15` %73,3 vs
> `acgozlu900` %63,3 (n=60 vs 450) · `orta_15` %56,1 vs `orta` %45,9 (n=66 vs 558).
> **Tetik BEKLEYENLER #4'ün kendi sayısal eşiğidir; bu tahmin o eşik dolmadan
> DEĞERLENDİRİLMEYECEK.** Erken bakmak tam olarak K33'ün yasakladığı şeydir.

## (g) SON İKİ GÜNÜN TAM İSABETLERİ (kullanıcının sorusunun çıkış noktası)

17 Ağu BURSA 1: `acgozlu900` ve `acgozlu900_15` **6/6**. 18 Ağu ANKARA 1: `bot1_900` ve
`bot1_1800` **6/6**. Dört tam isabet iki günde. **Bu bir sinyal değildir** — 42 kupon
kuruldu, dördü tuttu; K98-h'nin ve A0'ın gösterdiği gibi tam isabet sayısı config ayırt
etmez. Bu yüzden kullanıcının sorusu (ayak düzeyi) doğru sorudur ve bu karar onun cevabıdır.

**Dokunulmayanlar:** `kod/ayak_analiz.py` yeni ve salt-okunur. Canlı seçim/dağıtım/config
koduna, defter/paper akışına **dokunulmadı**.

---

**K110 — TAM KOD İNCELEMESİ: üç ölçüm-etkileyen hata bulundu ve düzeltildi. Backtest ROI'leri
21 PUANA kadar iyimsermiş; oran kaydı kapanışı HİÇ görmüyormuş; offline yığın 3-6 hafta
bayatmış. Hepsi kapatıldı, canlı yola dokunulmadı.** 19 Ağu 2026.

Kullanıcı *"tüm sistemin kodunu çok dikkatle kontrol et"* dedi, sonra *"yapalım dediğin her şeyi
çok dikkatle yap, sisteme asla zarar gelmesin"*. Önce emniyet kaydı atıldı (`824e41e`, salt veri,
mükerrer kontrolünden geçirilerek), sonra düzeltmeler yapıldı.

## (a) BACKTEST KUPON BEDELİNİ 1,00 TL SAYIYORMUŞ — gerçek fiyat 1,25 TL

`altili_backtest.degerlendir` iki yerde yanlıştı ve **iki hata birbirini gizliyordu**:

| satır | eski | sorun |
|---|---|---|
| `maliyet = nkombo * birim` | `birim=1.0` varsayılan, `main()` hiç geçersiz kılmıyor | maliyet %20 eksik |
| `getiri += onceki * birim * div` | temettü de `birim` ile çarpılıyor | **birim değiştirmek ROI'yi hiç değiştirmiyordu** |

Temettü, kazanan bir birim kupon başına **mutlak TL**'dir — `birim` ile çarpılmaz. Doğrulandı:
`altili_tam.t6_div` ile `nli_ganyan.tl` **6.723 olayın %99,7'sinde birebir aynı değer**.
Canlı taraf zaten doğru yapıyordu (`bedel = kombo * ro.birim_fiyat(pist)`, ödül = temettü) —
yani **backtest ile canlı sicil hiçbir zaman aynı ölçekte değildi.**

**ÜÇ AŞAMALI DÜZELTMENİN ETKİSİ** (OOS senaryo B, `orta` ayarı 0,75/0,55/96):

| aşama | ROI |
|---|---|
| eskiden basılan (birim=1,00 · Temmuz verisi) | **−%15,4** |
| birim düzeltildi (Temmuz verisi) | −%32,3 |
| birim düzeltildi + **taze veri** | **−%36,5** |

Toplam **21 puan**. Bütün hücrelerde etki 10-17 puan. Kapsamdaki her pist 1,25 TL'dir
(1,00 TL'li pistler tam olarak K4'te dışlananlar), yani istisna yok.

**KAYITTAKİ NE DEĞİŞİYOR:** K52'nin *"backtest OOS −%32"*'si ve K93'ün *"kâğıt −%33,3 vs
backtest −%32, yakınsadı"* cümlesi **iki farklı ölçekten sayı kıyaslamış**. Doğru kıyas
şimdi kuruldu ve **sonucu güçlendiriyor**:

| ölçü (hepsi gerçek tarifeyle) | değer |
|---|---|
| canlı kâğıt Altılı sicili (538 kupon, 10 tam isabet) | **−%50,8** |
| ölçülmüş Altılı kesintisi (K94) | **−%48,6** |
| düzeltilmiş backtest, 18 hücrenin **en iyisi** | −%36,5 |
| düzeltilmiş backtest, tipik hücre | ~−%50 |

**Canlı kâğıt ROI'si kesintinin tam üstüne oturuyor.** Ayrıca görüldü ki *"backtest −%32"*
başlığı **18 hücrenin en iyisiydi** — tipik hücre değil. Kazananın laneti, kendi kaydımızda.

## (b) ORAN KAYDI KAPANIŞ FİYATINI HİÇ GÖRMÜYORMUŞ — ve gerçeği zaten elimizdeymiş

`altili_oran_log.csv`, 374 koşuda son gözlemini **medyan 14,9 dk kala** yapıyor ve
**hiçbir koşuda ≤10 dk'ya inmiyor** (min 10,4). Sebep yapısal: takip 15 dk'da bir koşuyor,
geçişler :01/:16/:31/:46'ya, koşular :00/:30'a düşüyor → son fotoğraf **sistematik olarak
~15 dk erken**. Bu bir hata değil, tasarımın kaçınılmaz sonucu — ama fark edilmemişti.

**Ne kadar fark ediyor** (son gözlem vs resmî kapanış, 3.205 at-koşu):

| ölçü | değer |
|---|---|
| medyan sapma | **+%12,7** |
| %10'dan fazla oynayan | **%85** |
| %25'ten fazla oynayan | **%60** |
| 5–95 persentil | −%51 … **+%151** |

**GERÇEK KAPANIŞ ZATEN VARDI:** `defter.csv.ganyan_kapanis`, sonuç feed'inden gelir, **%99
dolu**. Müşterek bahiste ödenen fiyat budur. `ayak_analiz.son_oran_ekle` artık birincil
kaynak olarak onu kullanıyor; defter'de bulunmayan ayaklarda oran_log yedeğe düşüyor ve
satır işaretleniyor (şu an 1.548 kapanış / 262 yedek).

**K109'UN SAYISI DÜZELTİLDİ.** Dün *"bot1'in +%19,4'ü yanılsamaymış, gerçeği −%18"* yazmıştım.
Yönü doğruydu ama **büyüklüğü hâlâ yanlış fiyatla** hesaplanmıştı. Gerçek kapanışla:

| config | kupon-anı (muhtemel) | **RESMİ KAPANIŞ** | %95 GA | hüküm |
|---|---|---|---|---|
| `bot1_900` | +%18,7 | **−%24,8** | [−34,1 · −15,3] | negatif, kesin |
| `bot1_1800` | +%3,8 | **−%29,6** | [−39,3 · −18,8] | negatif, kesin |
| `acgozlu900` | −%26,6 | −%26,4 | [−34,5 · −17,7] | negatif, kesin |
| `orta` | −%31,0 | −%20,2 | [−31,5 · −8,4] | negatif, kesin |

Ölçülmüş ganyan kesintisi **%28,3** (K104). ROI'ler oraya oturuyor — seçim katmanı ne
kazandırıyor ne kaybettiriyor, yalnızca kesinti ödeniyor. **5 config'te GA tamamen sıfırın
altında**; K109'da fiyat proxy'si yüzünden bu kadar net değildi.

**YAN SONUÇ:** BEKLEYENLER #4'ün *"5 dk kala kursak ne olurdu"* sorusu için veri **zaten var** —
`defter.csv` postaya **medyan 0 dk kala** kaydediyor (%100'ü ≤6 dk) ve içinde bot1/bot2/kamu/oran
dolu. Yeni veri toplamaya, takip sıklığını artırmaya **gerek yok**. Kol ölçülebilir durumda.

## (c) OFFLINE YIĞIN SESSİZCE BAYATLAMIŞ — tazelendi + uyarı kuruldu

| dosya | önce | şimdi |
|---|---|---|
| `ozellikli.csv` | 8 Tem (**41 gün**) | 18 Ağu · 118.800 → **121.810** satır |
| `altili_tam.csv` | 19 Tem (30 gün) | 18 Ağu · 6.747 → **6.867** olay |
| `altili_olasilik.csv` | 20 Tem | 230.820 → **235.006** satır |
| `altili_olasilik_bot1.csv` | 30 Tem (20 gün) | **235.006** satır |
| `nli_ganyan.csv` | 5 Ağu | 27.442 → **27.958** olay |

**Somut zarar:** Ağustos'ta oynanan **272 ayak koşusunun SIFIRI** olasılık dosyalarındaydı →
o gün çalıştırılan her backtest Temmuz dünyasında koşuyordu ve bunu söyleyen hiçbir şey yoktu.
`gunluk.hesapla` K36'dan beri `katilim.csv` için bayatlık uyarıyor; **türetilmiş dosyalar için
aynı koruma yoktu.**

Kök nedenlerden biri: `altili_bot1_test.py` dosyayı **yalnız `--yenile` bayrağıyla** yeniden
üretiyor, aksi halde eskisini okuyup devam ediyordu — sessiz önbellek.

**`kod/tazelik.py` yazıldı.** Türetilmiş dosyanın yaşını basar, 7 günden eskiyse görünür uyarı
verir ve **üretici komutu gösterir**. `altili_backtest` ve `nli_backtest`'in `main()`'lerine
bağlandı. **Import `main()` İÇİNDE** — canlı yol bu modülü asla yüklemez, buradaki bir hata
kupon kurmayı engelleyemez.

Yeniden fit edilen harman katsayıları: İngiliz **α=+0,191 γ=+0,975** · Arap α=+0,217 γ=+0,909
(önce 0,21/0,95 kayıtlıydı). Hikâye değişmiyor: γ baskın, bot2 pratikte kamu.

## (d) K108 TAZE VERİYLE YENİDEN SINANDI — HÜKÜM AYAKTA

4'lü/5'li reddi bayat veriyle verilmişti; taze veriyle tekrarlandı. Eşleşmiş üçlü 990 → **1.033**.
Sonuç **birebir aynı desen**: 16 S1 testinin **1'i** geçiyor (α=0,05'te şansa beklenen 0,8),
geçen hücre yine fiyat-güvenli 2026 alt kümesinde **tekrarlamıyor**. S2: 24 hücrenin hepsi
negatif, en iyisi −%39,2. **BEKLEYENLER #2 kapalı kalıyor.**

## (e) `nli_ganyan.csv`'NİN KAYIP ÜRETİCİSİ YAZILDI — K108 artık doğrulanabilir

Dosyayı K94 üretmiş ama **üretici betik kaydedilmemiş** (geçici betikle üretilip atılmış).
Okuyan vardı, yazan yoktu → ne tazelenebiliyor ne yeniden üretilebiliyordu. K108'in tamamı
buna dayandığı için karar **doğrulanamaz durumdaydı**.

**`kod/nli_ayikla.py` yazıldı ve K94'ün çıktısına karşı doğrulandı:**

| ölçü | sonuç |
|---|---|
| ortak olay | **27.442** |
| yalnız eski dosyada olan | **0** ← hepsi yeniden üretildi |
| temettü aynı | 27.439 / 27.442 |
| **4/5/6'lı üründe temettü farkı** | **0** |
| 4/5/6'lı üründe ayak kodu farkı | 7 / 19.023 (%0,04) |

Kalan farkların hepsi **3'lü**de — en kısa üründe kombo birden fazla pencereye uyabiliyor,
iki sürüm de belirsizliği keyfî çözüyor. **K108'in kullandığı ürünlere etkisi sıfır.**

## (f) VERİ BÜTÜNLÜĞÜ

**32 mükerrer satır** bulundu `defter.csv`'de — 1 Tem 2026, iki koşu, 15:0x'te ve 18:31'de iki
kez yazılmış. O iki koşu kalibrasyon/ROI özetinde **çift sayılıyordu**. 16 geç satır atıldı
(5.676 → 5.660); **en erken kayıt tutuldu** çünkü yarış-öncesi tahmin odur.
`defter._yaz`'a **tekillik koruması** eklendi — upsert deseni ("çözülmüşleri koru" + concat)
yapısal olarak buna açık; artık son savunma hattı var. Test edildi.

**Günlük rapor dosyası her çok-pistli günde ikiye bölünüyormuş.** `takip.py` dosya adını
`'_'.join(pistler)` ile kuruyor, sıra feed'den geliyor ve sabit değil → `2026-08-18_ANKARA_
KOCAELI.txt` **ve** `2026-08-18_KOCAELI_ANKARA.txt`. **20+ günde olmuş**, hiçbir dosyada günün
tamamı yok. `sorted()` eklendi — **yalnız dosya adında**; `pistler` listesinin kendi sırası
değiştirilmedi ki koşu işleme/kupon kurma sırası aynen kalsın. CSV'ler etkilenmemişti.

## (g) KÜÇÜK SERTLEŞTİRMELER

- **Emekli config koruması fonksiyonun içine alındı.** `kupon_hazirla`, `sadece_cfg` verilince
  `KONFIG`'den seçiyordu (`aktif_konfig()`'den değil) → emekli bir ad geçse kupon kurardı.
  Çağıran zaten filtreliyordu, pratik risk yoktu; ama K100'ün kuralı **fonksiyonun kendisine**
  ait olmalı. Artık emekli istenirse uyarıp atlıyor.
- **`ayak_analiz.py`'ye "9) VERİ KALİTESİ" bölümü** eklendi, iki şeyi her çalıştırmada basıyor:
  - **C3:** `dk_grup` *niyeti* kaydeder, *gerçeği* değil. 88 kupon-anının 4'ü (%5) etiketinden
    >5 dk sapmış (hepsi "30 dk" etiketli ama 14-15 dk'da kurulmuş). **Dördü de 15 dk kolu
    açılmadan önce** (≤9 Ağu) → K105'in eşleşmiş verisi temiz (13 Altılı'da fark hep 14,4-15,5 dk),
    ama etiket-gerçek ayrımı `dk_grup`'a göre gruplayan her analizde latent risk.
  - **C4:** berabere durumunda `kazanan` sütunu **bizim tuttuğumuz atı** yazar → "kazanan bizim
    kaçıncı tercihimizdi" tabloları o olaylarda kendine doğru yanlı. Ölçüldü: **586 koşunun
    2'si (%0,34)** → etki ihmal edilebilir, ama artık görünür.

## (h) SAĞLAM ÇIKANLAR (kontrol edildi, sorun yok)

Çıplak `except:` yok · mutable default arg yok · `altili_kupon`/`kupon_ani`/`temettu` 0 mükerrer ·
kamu+bot1+bot2 olasılıkları **527 koşunun hepsinde toplam 1,0000** (sıfır sapma) · berabere
işleme (K64) doğru · sızıntı koruması (K36) çalışıyor · kupon hiç geç kurulmamış · üç zamanlanmış
görev de Ready · A0 canlı veriyle çalışıyor, bayatlıktan etkilenmedi.

## (i) CANLI SİSTEME ZARAR GELMEDİ — doğrulandı

Her düzeltmeden sonra ve en sonda tam kontrol koşuldu:
- **11 canlı modül** (gunluk, defter, paper, altili_canli, takip, bekci, oran_log…) hatasız import
- **KONFIG bozulmamış**: 7 aktif, 4 emekli, dk grupları [30, 15]
- **Dağıtıcılar bit-bit aynı**: 6.000 rastgele kartta kupon imzası `11a80724e9dccd9a`
  (kupon_kur / açgözlü / kalibre) — *kupon mantığı hiç değişmedi*
- **9 veri dosyasında 0 mükerrer**
- **Bekçinin üç denetimi de çalışıyor** (nabız / config kapsaması / defter kapsaması)

`altili_backtest.py`'ye eklenen `rapor_ortak` importu **korumalı** (try/except + yerel yedek
tarife) çünkü canlı yol o modülü `kupon_kur` için import ediyor — orada bir import hatası
**kupon kurulmamasına** yol açardı, ölçülen en pahalı hasar.

---

**K111 — ZAMANLAMA ÖLÇÜLDÜ (BEKLEYENLER #4): geç kurmak DAHA ÇOK TUTTURUYOR ama DAHA AZ
KAZANDIRIYOR. K98-h'nin "tavan"ı zaman ekseninde de geçerli. Aksiyona dönük versiyonda
(1. ayak) hiçbir işaret yok.** 19 Ağu 2026. Araç: `kod/zamanlama_test.py` (salt offline).

Kullanıcı 19 Ağu ISTANBUL 2. Altılı'nın ekran görüntüsünü getirip *"kazanan atın kamusu son
dakikalarda yükseldi, 5 dk kala kursaydık ne olurdu"* diye sordu. Önce **o tek koşu**, sonra
**tüm sicil** ölçüldü.

## (a) TEK KOŞU — okuma tersmiş, ve bu önemli

Kullanıcı görselden *"at son sıralardan yükseldi"* okumuştu. Veri **tam tersini** söylüyor:

| yarışa kala | oran | kamu sırası |
|---|---|---|
| 105 dk | **5,40** | **1. (favori)** |
| 29 dk (kupon anı) | 8,70 | 2. |
| 14 dk | 12,05 | 7. |
| ~0 dk (kapanış) | **25,40** | **10.** |

Görseldeki *"kamu 2."* etiketi **kupon anındaki** sıradır, yarış anındaki değil. At kupon
kurulurken kamunun 2. tercihiydi ve oradan **10.'luğa çöktü** — oranı ~5 katına çıktı.
Para bu attan **çekildi**, ona akmadı. Sistemin sırasının 8.→11. düşmesi de bunun sonucu
(bot2'nin %82'si kamudan gelir).

**Karşı-olgusal (aynı dağıtıcı, aynı bütçe, 5 dk verisi):**

| config | gerçek | 5 dk kala | at 11 |
|---|---|---|---|
| `acgozlu900` · `acgozlu900_15` | **5/6** | 4/6 ↓ | hayır |
| `acgozlu_v2` | 5/6 | 5/6 | hayır |
| diğer dördü | 3-4/6 | değişmedi | hayır |

**Yedi config'in hiçbiri at 11'i yazmıyor; ikisi kötüleşiyor, hiçbiri iyileşmiyor.**
5 dk kala at kamuda 10./12, sistemde 11./12'ydi. Temettü 272.186,93 TL'ydi ama at 25,40'a
kapandı — yani **kalabalık da bilmedi**; ödülün büyüklüğünün sebebi zaten bu.

## (b) BİR TUZAK: "5 dk kala kupon" ÖLÇÜLEMEZ — ve neden

Altılı kuponu 1. ayak başlamadan kurulmak zorundadır. "5 dk kala kursaydık" demek,
**1. ayağa 5 dk kala altı ayağın da o andaki fotoğrafını** kullanmak demektir.
- `defter.csv` her koşuyu **kendi** postasına ~0 dk kala kaydeder → 6. ayağın kaydı
  1. ayaktan **~2,5 saat sonra** alınmıştır. Onu kupon senaryosuna sokmak **K97'de
  düzeltilen sızıntının aynısıdır.** Yapılmadı.
- `oran_log` 1. ayağa en yakın 10,4 dk (medyan 14,9) kala geçiyor; **82 Altılı'nın
  sıfırında** ≤6 dk fotoğraf var (K110).

Bu yüzden soru **ikiye ayrıldı** ve ayrı ayrı okundu.

## (c) YÖNTEM — A0'ın iskeleti, değişen tek şey CETVEL değil ZAMAN

Her (config, ayak) için: **k = o ayakta gerçekten yazdığımız at sayısı** (genişlik sabit).
İki cetvel: kupon anı (`altili_kupon_ani`, config'in kendi dk grubundan) vs 5 dk kala
(`defter`, o koşunun kendi postasına ~0 dk kala). Eşleşmiş McNemar + olay-bootstrap.

**İÇ KONTROL — geçti.** `bot1` orana kördür, zamanla değişmemeli. `bot1_900` ve `bot1_1800`'de
uyumsuz çift **tam sıfır** çıktı. Yöntem doğrulandı.

## (d) SONUÇ

**Z1 — AKSİYONA DÖNÜK (yalnız 1. ayak; "kuponu 25 dk geç kur" demek):**
isabet **%55,9 → %58,2**, fark +2,3 puan, %95 GA **[−2,6, +7,4]**, McNemar **p=0,38**.
Para: −%20,6 → −%20,9. **İŞARET YOK.**

**Z2 — BİLGİ SORUSU (tüm ayaklar; kupon olarak kurulamaz, mekanizmayı ölçer):**

| | kupon anı | 5 dk kala |
|---|---|---|
| ayak isabeti | %56,8 | **%60,3** |
| tutan kazanan | 879 | **933** (+54) |
| **ganyan ROI (resmî kapanış)** | **−%22,9** | **−%25,3** |

Fark **+3,5 puan [+0,8, +5,9]**, McNemar **p=0,0003** — **gerçek bir sinyal.**
Son ~30 dakikanın oran hareketi **gerçekten bilgi taşıyor.**

**AMA PARA İYİLEŞMİYOR, KÖTÜLEŞİYOR.** 54 fazla kazanan tutuluyor ve toplam getiri
**düşüyor** — geç cetvel **daha ucuz atları** tutuyor.

> **Bu, K98-h "tavan"ının ZAMAN eksenindeki hâlidir.** K98-h'de kapsamı genişletmek isabeti
> artırıyor ama temettüyü yarıya düşürüyordu ("kalabalığa katılmak"). Burada aynı şey
> **beklemekle** yapıldı ve **aynı duvara** çarpıldı. Tavan bir kupon-şekli özelliği değil,
> **piyasa özelliği**: kalabalığa yaklaşmanın bedeli, yaklaşma biçiminden bağımsız.

## (e) KAPSAM — ön-kayıtlı eşik TUTMADI, dürüstçe kaydediliyor

İki fotoğrafta da bulunan ayak oranı **%78** (ön-kayıt %90 istiyordu) → **hiçbir config'e
tek tek hüküm verilmedi.** Ölçüt sonuca bakılıp değiştirilmedi.

Kapsamı sıfır olan 6 gün: 20-24 Tem (`kupon_ani` henüz yoktu, K97) ve **16 Ağu** (sessiz gün
kaybı, K107). Yani en büyük boşluklar **tarihsel/yapısal**, koşuya özgü değil.

**Eşleşmiş tasarım eksiklikten etkilenir mi? Hayır** — karşılaştırma aynı ayağın içinde;
bir ayak eksikse **her iki koldan birden** düşüyor. Eksiklik **farkı yanlılaştırmaz**,
yalnızca hangi ayaklar hakkında konuştuğumuzu daraltır (genellenebilirlik, iç geçerlilik değil).

Kayda geçen asimetri: ölçülebilen ayaklarda gerçek isabetimiz %56,4, **ölçülemeyenlerde %63,4**
(+7 puan). Yani ölçemediklerimiz **daha kolay** ayaklar — zamanlamanın etkisinin zaten küçük
olacağı yerler. Hüküm **ortalama zorluktaki** ayaklar için geçerlidir.

## (f) BEKLEYENLER #4 İÇİN NE DEMEK

1. **"Daha geç kur" fikrinin para tarafı ölçüldü ve olumsuz.** Bilgi geliyor (Z2 kesin),
   ama o bilgi **fiyata çoktan girmiş** durumda — tuttuğun at ucuzlamış oluyor.
2. **Aksiyona dönük versiyonda (Z1) hiçbir işaret yok.** Kuponu 25 dk geç kurmanın ölçülebilir
   faydası görülmedi; ne isabette ne parada.
3. **Canlı 15 dk kolu (K105) hakkında karar KULLANICININ.** Bu ölçüm kolun *beklentisini*
   düşürüyor ama kol farklı bir şeyi test ediyor (tüm kupon 30 vs 15 dk, ayak-ayak değil) ve
   kâğıt üzerinde Altılı başına 120 TL. K106'daki ilkeyi koruyorum: veri toplamaya başlamış
   bir kolu teoriyle kapatmam; **karar kullanıcınındır.**
4. **BEKLEYENLER #4'ün "5 dk verisi yok" ön koşulu ARTIK GEÇERSİZ ama "5 dk kupon" da
   ölçülemez** — (b)'deki yapısal sebep. Kolun sorusu ancak canlı kolla veya Z1'in
   büyümesiyle cevaplanır.

## (g) DOKUNULMAYANLAR

`kod/zamanlama_test.py` yeni ve salt-okunur; hiçbir dosyaya yazmaz. Canlı seçim/dağıtım/config
koduna dokunulmadı. Fiyat kaynağı K110 kuralına uyuyor: **resmî kapanış** (`defter.ganyan_kapanis`),
`oran_log` **kullanılmadı**.

---

**K112 — "KAMUYA DAHA ÇOK AĞIRLIK VERELİM Mİ?" ÖLÇÜLDÜ → HAYIR. Ayrıca uzak ayakta "kamu"nun
ne kadar HAM olduğu ilk kez sayıldı ve K92'nin λ'sı gerekçesine kavuştu.** 19 Ağu 2026.
Araç: `kod/kamu_test.py` (salt offline, hiçbir dosyaya yazmaz).

## (a) ÇIKIŞ NOKTASI — kullanıcının somut sorusu

19 Ağu ISTANBUL 2. Altılı'nın 1. ayağında kazanan AFRİKA ATEŞİ, kupon anında **kamuda 2.**
sıradaydı; bot2 onu **8.**'ye koydu, `orta` (2 at yazar) yazmadı, at kazandı, temettü
**272.186,93 TL**. Kullanıcı sordu: *"sistem kamuya yeterince ağırlık vermiyor olabilir mi?"*

**Mekanizma çözüldü.** O koşuda kamu bir tek atı ayırıyordu (#2, oran 2,45); **2.'den 8.'ye
kadar yedi at 8,70–10,80 bandında sıkışıktı** — yani kamu onları birbirinden neredeyse hiç
ayırmıyordu. bot1 ise net konuşuyordu: #8 sahanın **en iyisi** (1.), #11 sahanın **en kötüsü**
(12/12). Kamu ikisi arasında %24 fark görürken bot1 **7 kat** fark görüyordu.
**Kural:** bot1, kamunun kararlı olduğu yerde hiçbir şeyi oynatamaz (#2'ye dokunamadı);
kamunun kararsız olduğu yerde sıralamayı yeniden yazar. O koşuda tam bunu yaptı.

## (b) ÖLÇÜM A — UZAK AYAKTA "KAMU" GERÇEK AMA HAM

TJK, kupon anında uzak ayak için **gerçek bir piyasa** veriyor: para var, oranlar hareket
ediyor (`oran_log` 6. ayağı 195 dk kaladan itibaren izliyor). Dondurulmuş da değil, koşu-anı
verisi de değil. **Ama o piyasa ÖDEYEN piyasa değil.** Kupon anı sıralaması ile **resmî
kapanış** sıralaması (407 ayak):

| ayak | ort. uzaklık | Spearman ρ | **favori AYNI kaldı mı** |
|---|---|---|---|
| 1. | 28 dk | 0,758 | **%56** |
| 2. | 56 dk | 0,647 | %51 |
| 3. | 83 dk | 0,553 | %49 |
| 4. | 109 dk | 0,612 | %58 |
| 5. | 139 dk | 0,543 | %53 |
| **6.** | **163 dk** | **0,575** | **%40** |

**İki sonuç.** (1) 6. ayakta kupon anındaki favori, 10 koşunun 6'sında kapanışta favori
değil. (2) **1. ayakta bile** — postaya sadece 28 dk varken — favori **%44 ihtimalle
değişiyor.** Canlı örnek aynı Altılı'nın 6. ayağı: #2 ÖNDER kupon anında 5,70 ile favoriydi,
**>57'ye çöktü**; kapanışın favorisi #8 KRAKEN (2,95) o an **7. sıradaydı**.

> **K92 GEREKÇESİNE KAVUŞTU.** Uzak ayağın olasılığını λ=0,65 ile düzleştirmemiz gerektiğini
> K92'de **ölçmüştük ama nedenini bilmiyorduk**. Cevap bu: uzak ayakta kamu olasılıkları
> fazla kendinden emin, çünkü arkalarındaki piyasa henüz oluşmamış. λ o aşırı güveni kırıyor.
> Ölçülmüş bir düzeltmenin altında artık **ölçülmüş bir mekanizma** var.

## (c) ÖLÇÜM B — AĞIRLIĞI DEĞİŞTİRSEK NE OLURDU?

`bot2 ~ bot1^α · kamu^γ`. Ölçülen (**K110**, taze veriyle, **elle seçilmedi**): İngiliz
α=**0,19** γ=**0,98**. (K96 0,21/0,95 demişti; K110'da güncel veriyle yeniden ölçüldü.)
α=0 saf kamu demek. 1.495 (config × ayak) çiftinde **genişlik sabit**, değişen tek şey cetvel:

| α | | ayak isabeti | ganyan ROI | ort. kazanan oranı |
|---|---|---|---|---|
| 0,00 | **SAF KAMU** | %56,5 | −%29,9 | **4,90** |
| **0,19** | **BUGÜNKÜ** | **%57,9** | **−%28,9** | 4,84 |
| 0,35 | | %58,4 | −%30,1 | 4,72 |
| 0,50 | | %58,7 | −%31,6 | 4,60 |
| 1,00 | | %58,8 | −%33,6 | 4,46 |
| ∞ | SAF BOT1 | %57,1 | −%33,3 | 4,59 |

**ÖN-KAYITLI KARAR KIYASI (tarama değil — iki nokta):** saf kamu vs bugünkü.
- **İSABET:** yalnız-bugünkü **44**, yalnız-saf-kamu **22**, uyumsuz çift 66,
  McNemar **p=0,0092** → **FARK VAR, bugünkü daha iyi.**
- **PARA:** −%28,9 vs −%29,9, fark **+1,01 puan**, %95 GA **[−0,86, +2,95]** →
  **PARA FARKI KANITI YOK** (GA sıfırı içeriyor).

**HÜKÜM: kamuya daha fazla ağırlık VERİLMEZ.** Ön-kayıt "hem isabette hem parada anlamlı iyi
olmalı" diyordu; saf kamu **ikisinde de** iyi değil, isabette anlamlı **kötü**.

## (d) İKİ YENİ BULGU

**1. bot1'in katkısı ayak düzeyinde GERÇEK.** A0 (K106) "seçim katmanımız kalabalıktan
ölçülebilir biçimde farklı değil" demişti. Bu ölçüm daha temiz bir izolasyon yapıyor (aynı
ayak, aynı genişlik, **yalnız α değişiyor**) ve bot1'in isabete katkısını **p=0,022** ile
yakalıyor (**p=0,0092**). A0 ile çelişmiyor — A0 config'in kendi dağıtıcısı ve genişliğiyle bakıyordu, bu
ise cetveli tek başına izole ediyor.

**2. Ama katkı PARAYA DÖNMÜYOR.** bot1'in sesi arttıkça isabet yükseliyor, **kazanan atların
ortalama oranı düşüyor** (4,90 → 4,46). Daha çok tutturup daha ucuz tutturuyorsun.

> **TAVAN DÖRDÜNCÜ KEZ ÇIKTI.** K98-h: kapsam genişletmek. K108: ayak sayısını azaltmak.
> K111: daha geç kurmak. K112: bot1'in sesini kısmak. **Dördü de aynı sonucu veriyor** —
> isabet artar, ödeme düşer, net değişmez. Tavan bir kupon-şekli özelliği değil, **piyasa
> özelliğidir**: kalabalığa yaklaşmanın bedeli, ona nasıl yaklaştığından bağımsız.

## (e) DİSİPLİN NOTU — neden "en iyi α"yı seçmiyoruz

Taramada α=1,00 en yüksek isabeti (%58,8), α=0,19 en iyi ROI'yi (−%28,9) veriyor. **Hiçbiri
seçilmedi.** 10 değer denendiğinde birinin en iyi çıkması kaçınılmazdır; onu almak
K33/K52'nin yasakladığı hindsight'tır. Karar yalnızca **önceden belirlenmiş iki noktadan**
verildi. Ayrıca α=0,19 zaten **ölçülmüş** bir değer (K110); taramanın ROI optimumunun ona
denk düşmesi ayarın sağlamlığının küçük bir teyidi — **gerekçesi değil.**

**Tek olay hükmü kurmaz da kayda geçer:** AFRİKA ATEŞİ vakası, bot1'in yanıldığı **22
olaydan biriydi**; 44 olayda bot1 sayesinde tutturmuşuz. Tek olaydan gidilseydi sistem
yanlış yöne çevrilecekti. Bu, "ölçmeden konuşma" ilkesinin somut faydasıdır.

## (f) DOKUNULMAYANLAR

`kod/kamu_test.py` yeni ve salt-okunur. **Hiçbir ağırlık, config, dağıtıcı DEĞİŞTİRİLMEDİ.**
Kullanıcı zaten "sadece analiz, işlem yapma" demişti. Fiyat kaynağı K110 kuralına uyuyor:
resmî kapanış (`defter.ganyan_kapanis`), `oran_log` kullanılmadı.

**K113 — 5/6'DA KALAN 112 KUPON TARANDI: "kurtarma bedeli" medyan 2.205 TL, ama aynı sonucu
ÖNCEDEN almak 19.479 TL (9 kat). Hiçbir derinlik kârlı değil.**
Kullanıcı sordu (24 Ağu): 24.08 Bursa 2. Altılı yüksek ödüllüydü ve `acgozlu900_15` 5'te kaldı;
tüm kuponlar taransın, 5'te kalanların Altılı'yı tutturması için bedel ne olmalıydı.
- **KAPSAM:** 11 aktif config, **643 tamamlanmış kupon, 110 Altılı**. İsabet dağılımı
  {0:3, 1:36, 2:114, 3:188, 4:180, 5:112, 6:10} → **10 tane 6/6'ya karşılık 112 tane 5/6**
  (5'te kalmak tutturmaktan 11 kat sık).
- **SORULAN VAKA (24.08 BURSA-2, temettü 365.633 TL):** `acgozlu900_15` 3. ayakta yattı, o ayağa
  **tek at** yazmıştı (banker bayrağı YOK — bütçe artığı). Kazanan #4, kupon anı cetvelinde
  **4. sırada**, saha 10. Olan 900 kombo = 1.125 TL → gereken 3.600 kombo = **4.500 TL**.
- **112 VAKANIN TAMAMI (kupon anı cetveliyle, `altili_kupon_ani.csv`):**
  kaçan ayakta kazananın sırası → medyan **5.**, ortalama 5,3; dağılım
  {1:2, 2:17, 3:14, 4:13, 5:15, 6:17, 7:13, 8:10, 9:4, 10:2, 12:5}. O ayaklara yazdığımız
  medyan **2 at** → tipik olarak **2x derinlik** gerekiyordu.

  | | medyan | ortalama | min | max |
  |---|---|---|---|---|
  | olan bedel | 1.080 TL | 1.026 TL | 20 TL | 2.250 TL |
  | **gereken bedel** | **2.205 TL** | **3.005 TL** | 80 TL | 12.600 TL |

  Yüzdelikler: %25→1.328 · %50→2.205 · %75→3.679 · %90→6.648 · %95→8.784 TL.
  Config medyanları: `orta` 212 · `genis` 456 · `genis900` 1.519 · `bot1_900` 2.250 ·
  `acgozlu900` 2.430 · `acgozlu_v2` 3.370 · `bot1_1800` 4.865 TL.
- **ALDATICI SAYI (kayda geçsin ki bir daha yanlış okunmasın):** 112 vakanın **%84'ünde**
  gereken bedel temettüden düşüktü; hepsi kurtarılsa 336.521 TL verip 4.201.252 TL alınırdı
  (**+3,86 M**). **BU ULAŞILAMAZ** — kaçan ayak ancak yarıştan SONRA bilinir; o kuponlarda
  diğer beş ayak zaten tutmuştu ve o tutma satın alınamaz.
- **İLERİYE BAKAN GERÇEK HESAP** (75 Altılı, kupon anı cetveli tam kurulabilen; tüm ayaklar
  eşit derinlik):

  | derinlik | tutan | ort.kombo | bedel | ödül | ROI |
  |---|---|---|---|---|---|
  | 3 | 2/75 | 729 | 68.344 | 99.372 | +%45,4 |
  | 4 | 5/75 | 4.096 | 384.000 | 123.332 | −%67,9 |
  | **5** | 15/75 | 15.583 | 1.460.938 | 750.687 | **−%48,6** |
  | 6 | 22/75 | 44.531 | 4.174.740 | 2.513.340 | −%39,8 |
  | 8 | 55/75 | 194.292 | 18.214.880 | 11.634.824 | −%36,1 |
  | 10 | 70/75 | 447.181 | 41.923.235 | 13.462.479 | −%67,9 |

  Medyan gereken derinlik 5'ti; onu **önceden** almak Altılı başına **19.479 TL** =
  geriye dönük 2.205 TL'nin **9 KATI**, ve 75 Altılı boyunca −%48,6.
  D=3'teki +%45,4 **2/75'ten** geliyor → K83'teki tuzağın aynısı, sonuç değil gürültü.
- **YAPISAL ENGEL:** gereken sıra dağılımı kuyruklu (medyan 5, kuyruk 12). "Derinlik N alırsam
  kapatırım" diyebileceğin N yok; maliyet 6. kuvvetle, kapsama doğrusala yakın artıyor.
- **SÜRDÜRÜLEBİLİRLİK OKUMASI (kullanıcının çerçevesi):** 5/6 bir "az kaldı" sinyali DEĞİL,
  "beş ayakta şans güldü" demek. K91 aynı sonuca başka yoldan varmıştı (100bin+ ödeyen 77 büyük
  5/6'dan çift bütçeyle yalnız 3'ü dönüşmüştü); bu tarama onu 112 vakada doğruluyor.
- Canlı sistem DEĞİŞMEDİ.

**K114 — 5/6'LARIN ANATOMİSİ: yakan şey BANKER DEĞİL, "banker olmadığı halde tek kalan"
ayaklar. Banker bayrağı %52,1 tutturuyor, bütçe artığı tek-at %30,4.
AYRICA: 31 Tem öncesi geri kurulmuş kupon-anı kayıtları GÜVENİLMEZ.**
Kullanıcı sordu: 5/6'ların kaçı banker ayaktan yattı, kaçında yarış anında 2. seçilen at kazandı.
- **YATAN AYAĞIN TİPİ (112 kupon):**

  | tip | kupon | **farklı yarış** |
  |---|---|---|
  | tek at yazılmış | 45 (%40) | **29** |
  | — gerçek banker (bot2 ≥ BANKER_ESIK) | 7 | **3** |
  | — bütçe artığı (bayrak yok) | 38 | **26** |
  | 2+ at yazılmış | 67 (%60) | — |

  **7 "banker yatışı" aslında 3 ayrı yarıştır** (08.07 İST-2 ayak4 · 18.08 ANK-1 ayak3 ·
  18.08 ANK-2 ayak1); aynı yarışı birden çok config oynadığı için tabloda çoğalıyor.
  → "Banker bizi yakıyor" tezi bu veriyle KURULAMAZ.
- **KAZANAN YARIŞ ANINDA 2. Mİ? — taban oranla birlikte okunmalı.** Defter'de 663 koşuda
  kazananın sistem sırası: 1.:%33 · **2.:%20** · 3.:%14 · 4.:%11 · 5.:%9 · 6.:%6.
  - tek-at ayakları (TEKRARSIZ, 24 yarış): **7 = %29** vs taban %20 → **Fisher p=0,299**,
    şanstan ayırt EDİLEMİYOR. Dağılım {1:1, 2:7, 3:6, 4:4, 5:1, 6:2, 7:2, 11:1}.
  - gerçek banker: **2/3** — n=3, HÜKÜM ÇIKMAZ (açıkça yazılıyor çünkü tablo ikna edici
    görünüyor ve değil).
  - kupon anı cetveliyle (31 Tem sonrası güvenilir 25 vaka): 6 = %24, yine tabana yakın.
- **ASIL BULGU — tek-at ayakların TAM sicili (yatan+tutan, 546 ayak-kupon):**

  | | ayak-kupon | farklı yarış | isabet |
  |---|---|---|---|
  | gerçek banker (bayrak=1) | 96 | 24 | **%52,1** |
  | bütçe artığı (bayrak=0) | 450 | 272 | **%30,4** |
  | çok-atlı ayak | 3312 | 651 | %59,8 |

  Fisher p=0,0001. **Banker bayrağı gerçek bilgi taşıyor** (taban %33 iken tek atla %52,1);
  bütçe artığı tek-atlar tabanın bile ALTINDA. Sorun mekanizma değil, K88'in sonucu:
  genişlik bütçenin 6. kökünden geliyor, model güveninden değil → açgözlü parası yetmediği
  için bir ayağı tek bırakıyor ve o ayak %30 tutuyor.
- **VERİ KALİTESİ BULGUSU (tesadüfen değil, çelişki kovalanarak bulundu):**
  `altili_kupon_ani.csv`'nin geri kurulmuş kayıtları **31 Tem 2026 ÖNCESİNDE GÜVENİLMEZ**:
  beklenen dk_kala'ya göre medyan sapma **45 dk**, %41'i **>60 dk**. 31 Tem SONRASI sapma
  **1 dk** (canlı kayıtlar da 1 dk). Sebep K76: o tarihten önce `oran_log` uzak ayakları hiç
  kaydetmiyordu → "kupon anına en yakın anlık görüntü" saatler sonrasından geliyor.
  **KANIT:** 28.07 KOCAELİ 2. Altılı ayak6 — geri kurulan kayıt sırayı `4 > 9 > 12 > 7` diyor;
  oysa kuponların KENDİSİ `9 > 7 > 4` diyor (açgözlü tek #9, dar {7,9}, orta {4,7,9}).
  Kuponlar doğrudan kanıt, geri kurma tahmindir → o dönemin K sütunu YANLIŞ.
  **KURAL: K sütunu kullanan her analiz tarih >= 2026-07-31 filtresi uygulamalı.**
  Etiket ("geri kurulan") tek başına yetmiyor; tarih eşiği de gerekiyor.
  Bu, K79'un "son ayakta 8. atı tek yazmış" anlatısının neden yanıltıcı olduğunun da
  ikinci bağımsız teyidi (K97 zaten uyarmıştı).
