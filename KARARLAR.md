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
