# -*- coding: utf-8 -*-
"""
coklu_test.py — K143 / BEKLEYENLER 22-A: PROJE SEVİYESİNDE ÇOKLULUK DÜZELTMESİ.
SALT-OKUNUR / OFFLINE.

SORUN (2 Eylül değerlendirmesinde tespit edildi): proje Bonferroni'yi bir test YIĞINI
içinde titizlikle uyguluyor (K128'de 9 varyant için %99,44 GA) ama **proje ölçeğinde hiç
uygulamadı**. 146 karar boyunca onlarca hipotez sınandıysa ailesel yanlış-pozitif oranı
yüksek olabilir.

YÖNTEM — körlemesine düzeltme YAPILMAZ, önce SINIFLANDIRMA:
  AİLE 1 "KENAR İDDİASI"  — "şu varyant tabanı yeniyor mu?" testleri. Çokluluk asıl burada
                            tehlikeli: her biri ayrı ayrı %5 ile sınandıysa, 20 testte
                            beklenen sahte-pozitif ~1.
  AİLE 2 "ÇAPA/KONTROL"   — anlamSIZ çıkması ISTENEN testler (ör. "6. ayak zor değil,
                            p=0,84"). Burada çokluluk düzeltmesi ANLAMSIZDIR; düzeltme
                            null'u korumayı kolaylaştırır, yani testi zayıflatmaz.
  AİLE 3 "MEKANİZMA/VERİ"  — kenar iddiası değil, olgu tespiti (ör. banker bayrağı bilgi
                            taşıyor, p=0,0001). Ayrı aile, ayrı değerlendirilir.
  AİLE 4 "EŞİK/İLLUSTRASYON" — sonuç değil, önceden konmuş eşik ya da güç örneği.
                            Teste dahil EDİLMEZ.

Yalnız AİLE 1'e Benjamini-Hochberg (FDR) ve Bonferroni uygulanır.

ÖNEMLİ AYRIM (rapor bunu ayrı gösterir): AİLE 1'in "anlamlı" çıkanlarının bir kısmı
**bir şeyin DAHA KÖTÜ olduğunu** bulmuştur (ör. v3 anlamlı kötü). Bunlar sahte-pozitif
riski taşımaz — proje onlara dayanarak bir şey BENİMSEMEDİ, tersine kol KAPATTI.
Çokluluk endişesi asıl **"iyileşme bulduk"** iddialarında geçerlidir.

KAYNAK: KARARLAR.md'de açıkça raporlanmış p-değerleri (elle sınıflandırıldı, satır no ile).
"""
import numpy as np

# (p, satir, kisa_ad, yon)  yon: "iyilesme" | "kotulesme" | "fark_yok"
AILE1 = [
    (0.688, 1318, "zamanlama işaret testi (geç kur)",            "fark_yok"),
    (0.014, 1401, "açgözlü ipucu (n=12 Altılı)",                 "iyilesme"),
    (0.500, 1602, "açgözlü vs ayrışma",                          "fark_yok"),
    (0.851, 1602, "açgözlü vs bot1",                             "fark_yok"),
    (0.572, 1603, "ayrışma vs bot1",                             "fark_yok"),
    (0.031, 1608, "kapsam merdiveni geniş→geniş900",             "iyilesme"),
    (0.250, 1666, "ayrışma McNemar (3-0)",                       "fark_yok"),
    (0.727, 1755, "banker hak edilsin varyantı",                 "fark_yok"),
    (0.688, 1845, "açgözlü vs ayrışma (38 ayak)",                "fark_yok"),
    (0.800, 1951, "ayrışma = açgözlünün kopyası (backtest)",     "fark_yok"),
    (0.424, 2433, "15 dk simülasyonu (+5 ayak)",                 "fark_yok"),
    (0.125, 2544, "şehir kıyası McNemar (4 uyumsuz)",            "fark_yok"),
    (0.380, 3326, "zamanlama, ayak isabeti +2,3 puan",           "fark_yok"),
    (0.0003, 3337, "K111: geç kurmak DAHA ÇOK tutturuyor",       "iyilesme"),
    (0.0092, 3446, "α kıyası: bugünkü ağırlık daha iyi",         "iyilesme"),
    (0.022, 3457, "bot1'in isabete katkısı",                     "iyilesme"),
    (0.00005, 3608, "açgözlü_v3 anlamlı KÖTÜ",                   "kotulesme"),
    (0.0002, 3659, "saha-orantılı genişlik anlamlı KÖTÜ",        "kotulesme"),
    (0.0010, 3809, "bot1_1800 daha çok ayak yakalıyor",          "iyilesme"),
    (0.038, 4041, "Ankara kenarı (+2,9 puan)",                   "iyilesme"),
    (0.0002, 1693, "kap genişletme: yalnız-kontrol farkı",       "kotulesme"),
    (0.0001, 1695, "mekanizma sorunu, bütçe değil",              "kotulesme"),
]

AILE2 = [(0.840, 1392, "KONTROL: 6. ayak zor DEĞİL (anlamsızlık İSTENİYOR)")]
AILE3 = [(0.0001, 3567, "banker bayrağı gerçek bilgi taşıyor"),
         (0.299, 3554, "tek-at ayakları %29 vs taban %20")]
AILE4 = [(0.010, 3979, "önceden konmuş eşik (sonuç değil)"),
         (0.125, 2687, "güç örneği: n=4'te 4-0 bile p=0,125")]


def bh(ps, q=0.05):
    """Benjamini-Hochberg: FDR kontrollu esik ve hangi testler ayakta kalir."""
    n = len(ps)
    sira = np.argsort(ps)
    p_sirali = np.array(ps)[sira]
    esikler = (np.arange(1, n + 1) / n) * q
    gecen = p_sirali <= esikler
    k = np.where(gecen)[0].max() + 1 if gecen.any() else 0
    kritik = p_sirali[k - 1] if k else 0.0
    ayakta = set(sira[:k].tolist())
    return kritik, ayakta, k


def main():
    print("=" * 100)
    print("K143 / 22-A — PROJE SEVİYESİNDE ÇOKLULUK DÜZELTMESİ")
    print("KARARLAR.md'de raporlanmış p-değerleri, elle sınıflandırılmış.")
    print("=" * 100)
    print(f"  AİLE 1 kenar iddiası : {len(AILE1)} test  <- düzeltme BURAYA uygulanır")
    print(f"  AİLE 2 çapa/kontrol  : {len(AILE2)} test  (anlamsızlık isteniyor -> düzeltme anlamsız)")
    print(f"  AİLE 3 mekanizma/veri: {len(AILE3)} test  (kenar iddiası değil)")
    print(f"  AİLE 4 eşik/örnek    : {len(AILE4)} test  (sonuç değil, dışarıda)")

    ps = [x[0] for x in AILE1]
    n = len(ps)
    nominal = [x for x in AILE1 if x[0] < 0.05]
    print("\n" + "-" * 100)
    print(f"AİLE 1 — ham durum: {len(nominal)}/{n} test nominal olarak anlamlı (p<0,05)")
    print(f"  Beklenen sahte-pozitif (düzeltmesiz, {n} test × 0,05): {n*0.05:.1f}")
    print("-" * 100)

    bonf = 0.05 / n
    kritik, ayakta, k = bh(ps, q=0.05)
    print(f"  Bonferroni eşiği (0,05/{n})     : p < {bonf:.5f}")
    print(f"  Benjamini-Hochberg eşiği (q=0,05): p <= {kritik:.5f}  -> {k} test ayakta")

    print("\n" + "-" * 100)
    print(f"  {'p':>9} {'satır':>6} {'yön':>11}  {'nominal':>8} {'BH':>4} {'Bonf':>5}  test")
    print("-" * 100)
    for i, (p, sat, ad, yon) in enumerate(sorted(AILE1, key=lambda x: x[0])):
        idx = [j for j, x in enumerate(AILE1) if x[:2] == (p, sat)][0]
        nom = "✓" if p < 0.05 else "·"
        b_h = "✓" if idx in ayakta else "·"
        bon = "✓" if p < bonf else "·"
        print(f"  {p:>9.5f} {sat:>6} {yon:>11}  {nom:>8} {b_h:>4} {bon:>5}  {ad}")

    iyi = [x for x in AILE1 if x[3] == "iyilesme"]
    iyi_nom = [x for x in iyi if x[0] < 0.05]
    iyi_bh = [x for x in iyi if [j for j, y in enumerate(AILE1) if y[:2] == x[:2]][0] in ayakta]
    iyi_bonf = [x for x in iyi if x[0] < bonf]

    print("\n" + "=" * 100)
    print("ASIL SORU — 'İYİLEŞME BULDUK' İDDİALARI DÜZELTMEDEN SAĞ ÇIKIYOR MU?")
    print("=" * 100)
    print(f"  iyileşme iddiası taşıyan test : {len(iyi)}")
    print(f"    nominal anlamlı (p<0,05)    : {len(iyi_nom)}")
    print(f"    BH (FDR q=0,05) sonrası     : {len(iyi_bh)}")
    print(f"    Bonferroni sonrası          : {len(iyi_bonf)}")
    print()
    for x in iyi_nom:
        idx = [j for j, y in enumerate(AILE1) if y[:2] == x[:2]][0]
        durum = []
        if idx in ayakta:
            durum.append("BH ayakta")
        if x[0] < bonf:
            durum.append("Bonf ayakta")
        if not durum:
            durum = ["DÜŞTÜ"]
        print(f"    p={x[0]:<8.5f} {x[2]:<42} -> {' · '.join(durum)}")

    kotu = [x for x in AILE1 if x[3] == "kotulesme" and x[0] < 0.05]
    print(f"\n  KARŞILAŞTIRMA — 'daha kötü' bulan anlamlı test: {len(kotu)}")
    print("  Bunlar sahte-pozitif riski taşımaz: proje onlara dayanarak bir şey BENİMSEMEDİ,")
    print("  tersine kol KAPATTI. Yanlış kapatma maliyeti, yanlış benimseme maliyetinden düşük.")
    print("\n" + "=" * 100)
    print("HİÇBİR DOSYAYA YAZILMADI.")
    print("=" * 100)


if __name__ == "__main__":
    main()
