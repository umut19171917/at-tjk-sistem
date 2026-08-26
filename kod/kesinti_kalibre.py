# -*- coding: utf-8 -*-
"""
kesinti_kalibre.py — K125: K124'ün ölçerini KALİBRE ET ve BİRİNİ-DIŞARIDA-BIRAK ile SINA.
SALT-OKUNUR / OFFLINE. Hiçbir dosyaya yazmaz.

NEDEN VAR: K124 iki kez koştu, iki kez ÇAPA KAPISI DÜŞTÜ, iki kez de hiçbir kol
kapanmadı/açılmadı (ön-kayıtlı kural aynen uygulandı). Ama ikinci koşuda kapının NEDEN
düştüğü göründü: ölçerin yanlılığı RASTGELE DEĞİL, ayak sayısıyla düzgün büyüyor.

  ayak · bahis          · bilinen · ölçülen · fark
   1   · GANYAN         · %28,3   · %33,0   · +4,7
   1   · SIRALI İKİLİ   · %26,0   · %31,1   · +5,1
   3   · 3'LÜ GANYAN    · %45,4   · %49,8   · +4,4
   4   · 4'LÜ GANYAN    · %45,6   · %54,5   · +8,9
   5   · 5'Lİ GANYAN    · %46,8   · %55,2   · +8,4
   6   · 6'LI GANYAN    · %48,6   · %57,3   · +8,7
   7   · 7'Lİ GANYAN    · %57,6   · %66,9   · +9,3

K124'ün kapısı MUTLAK DOĞRULUĞU sınıyordu (±6 puan ham değerde) ve düşmesi doğruydu.
Bu betik farklı bir soruyu sorar: yanlılık MODELLENEBİLİR mi? Bir termometrenin 5 derece
şaştığını bilmek onu kullanılamaz yapmaz — şaşmasının ÖNGÖRÜLEBİLİR olması gerekir.

=====================================================================================
ÖN-KAYITLI ÖLÇÜT — SONUÇLAR GÖRÜLMEDEN YAZILDI VE GİT'E MÜHÜRLENDİ (K33/K52)
=====================================================================================
A) MODEL: ganyan ailesinde  yanlilik(N) = a + b·N   (N = ayak sayısı), en küçük kareler.
   Yukarıdaki 7 bilinen nokta üzerinde fit edilir. BAŞKA HİÇBİR SERBESTLİK YOK —
   ikinci dereceden terim, ağırlık, aykırı-atma YOK. (Serbestlik eklemek, ölçütü
   sonuca uydurmak olurdu.)

B) SINAV — BİRİNİ-DIŞARIDA-BIRAK (LOO). Bu ölçütün TEK kapısıdır ve DÜŞEBİLİR:
   7 bilinen noktanın her biri için model O NOKTA OLMADAN yeniden fit edilir ve o
   bahsin kesintisi kestirilir.
   **7 LOO artığının HEPSİ ±6,0 puan içinde değilse: KALİBRE ÖLÇER DÜŞER,
     HİÇBİR KOL KAPANMAZ, HİÇBİR KOL AÇILMAZ.** (K124'ün tolerans değeri aynen
     korundu — eşik sonuca bakılarak gevşetilmedi.)

C) GEÇERSE HÜKÜM: kalibre kesinti = ham − yanlilik(N). Eşikler K124'ten AYNEN:
       >= %40 KAPANIR · < %30 AÇILIR · arası BELİRSİZ · %90 GA'nın TAMAMI geçmeli.
   Yalnız birimi BİLİNEN bahisler için nokta hüküm verilir.

D) BİRİM DUYARLILIĞI (zorunlu): ÇİFTE'nin hükmü birim=1,00 TL varsayımına dayanır
   (K124-EK E1: asgari temettü 6 yıl boyunca 1,40·1,25·1,30·1,35·1,35·1,00 — enflasyonla
   SÜRÜKLENMİYOR, yani taban dövülüyor). Her satır birim 1,00/1,25/1,50 için tekrarlanır.
   Birim 1,25'te hüküm değişiyorsa bu RAPORDA AÇIKÇA YAZILIR.

E) PLASE AİLESİ: tek çapa var (PLASE) -> LOO YAPILAMAZ -> nokta hüküm YASAK.
   Yalnız YÖN ve ALT SINIR: ölçer plase kesintisini %10,1 DÜŞÜK ölçüyor. Harville
   yanlılığı seçim sayısıyla birikir -> iki atlı PLASE İKİLİ'de düzeltme +10,1'den
   BÜYÜK olmalı -> gerçek kesinti >= ham + 10,1 bir ALT SINIRDIR.
   Alt sınır bile >= %40 ise KOL KAPANIR (asimetri K124 madde 6'da önceden yazılıydı).

F) DERİN SIRALI AİLE (ÜÇLÜ, TABELA ±sırasız, SIRALI 5'Lİ): birim TANIMLANAMAZ ve
   ailede ÇAPA YOK -> nokta hüküm YASAK. Yalnız K124-EK E2(c) alt sınırı geçerlidir
   (birim >= 1,00 -> t >= 1 - M). Alt sınır bile >= %40 ise KOL KAPANIR.

G) 7'Lİ PLASE: K124'te 447 olayın yalnız 118'i (=%26) kalite kapısını geçti ve değer
   saçma çıktı -> ÖLÇÜLEMEDİ ilan edilir. Ayrı bir ayak-eşleme teşhisi gerekir;
   bu betik onun için hüküm ÜRETMEZ.
=====================================================================================
"""
import sys
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))

import kesinti_tara as KT                                            # noqa: E402

LOO_TOLERANS = 6.0

# K124'un genisletilmis capasi (ayak sayisi, bilinen kesinti)
CAPA_GANYAN = {
    "GANYAN": (1, 28.3), "SIRALI İKİLİ": (1, 26.0), "3'LÜ GANYAN": (3, 45.4),
    "4'LÜ GANYAN": (4, 45.6), "5'Lİ GANYAN": (5, 46.8), "6'LI GANYAN": (6, 48.6),
    "7'Lİ GANYAN": (7, 57.6),
}
AYAK = {"GANYAN": 1, "PLASE": 1, "İKİLİ": 1, "SIRALI İKİLİ": 1, "ÜÇLÜ BAHİS": 1,
        "PLASE İKİLİ": 1, "TABELA BAHİS": 1, "TABELA BAHİS SIRASIZ": 1,
        "SIRALI 5 Lİ BAHİS": 1, "ÇİFTE": 2, "3'LÜ GANYAN": 3, "4'LÜ GANYAN": 4,
        "5'Lİ GANYAN": 5, "6'LI GANYAN": 6, "7'Lİ GANYAN": 7, "7'Lİ PLASE": 7}


def dogru_fit(N, y):
    """y = a + b*N, en kucuk kareler. Baska serbestlik yok (olcut A)."""
    N = np.asarray(N, float)
    y = np.asarray(y, float)
    b = ((N - N.mean()) * (y - y.mean())).sum() / ((N - N.mean()) ** 2).sum()
    return y.mean() - b * N.mean(), b


def ham_olc():
    """K124'un ham cikisini yeniden uretir (ayni kod, ayni birimler)."""
    T = KT.kosu_tablosu()
    KART = KT.kart_sirasi(T)
    kayit, tem, sayac = KT.topla(T, KART)
    ham = {}
    for ad, v in kayit.items():
        v = np.array(v, float)
        if v.size < 20:
            continue
        b, kaynak = KT.birim_al(ad)
        iade = v / b
        lo, hi = KT.boot_ga(iade)
        ham[ad] = {"kes": 100 * (1 - float(np.median(iade))),
                   "lo": 100 * (1 - hi), "hi": 100 * (1 - lo),
                   "b": b, "kaynak": kaynak, "M": float(np.median(v)),
                   "n": sayac[ad][2], "gor": sayac[ad][0], "dog": sayac[ad][1]}
    return ham


def main():
    print("=" * 112)
    print("K125 — KALİBRE EDİLMİŞ KESİNTİ ÖLÇER + BİRİNİ-DIŞARIDA-BIRAK SINAVI (salt-okunur)")
    print("=" * 112)
    ham = ham_olc()

    ad_l = [a for a in CAPA_GANYAN if a in ham]
    N = [CAPA_GANYAN[a][0] for a in ad_l]
    y = [ham[a]["kes"] - CAPA_GANYAN[a][1] for a in ad_l]
    a0, b0 = dogru_fit(N, y)
    print(f"\n  YANLILIK MODELİ (ganyan ailesi, {len(ad_l)} bilinen nokta):")
    print(f"     yanlilik(N) = {a0:+.2f} {b0:+.2f}·N   (N = ayak sayısı)")

    print("\n" + "-" * 112)
    print("  SINAV — BİRİNİ-DIŞARIDA-BIRAK (ölçüt B; tolerans ±6,0 puan, K124'ten aynen)")
    print("-" * 112)
    print(f"  {'bahis':>16} {'ayak':>4} {'bilinen':>9} {'LOO kestirim':>13} {'artık':>8}   sonuç")
    gecti = True
    for i, a in enumerate(ad_l):
        Nd = [N[j] for j in range(len(N)) if j != i]
        yd = [y[j] for j in range(len(y)) if j != i]
        ai, bi = dogru_fit(Nd, yd)
        kestirim = ham[a]["kes"] - (ai + bi * N[i])
        art = kestirim - CAPA_GANYAN[a][1]
        ok = abs(art) <= LOO_TOLERANS
        gecti &= ok
        print(f"  {a[:16]:>16} {N[i]:>4} {CAPA_GANYAN[a][1]:>8.1f}% {kestirim:>12.1f}% "
              f"{art:>+7.1f}   {'geçti' if ok else 'DÜŞTÜ'}")

    if not gecti:
        print("\n" + "=" * 112)
        print("HÜKÜM: LOO SINAVI DÜŞTÜ -> KALİBRE ÖLÇER GÜVENİLMEZ.")
        print("HİÇBİR KOL KAPANMAZ, HİÇBİR KOL AÇILMAZ (ön-kayıtlı ölçüt B).")
        print("=" * 112)
        return
    en_kotu = max(abs(ham[a]["kes"] - (lambda t: t[0] + t[1] * N[i])(
        dogru_fit([N[j] for j in range(len(N)) if j != i],
                  [y[j] for j in range(len(y)) if j != i]))) - CAPA_GANYAN[a][1]
        for i, a in enumerate(ad_l))
    print(f"\n  SINAV GEÇTİ. En kötü LOO artığı: {en_kotu:+.1f} puan (tolerans ±{LOO_TOLERANS:.1f}).")
    print("  -> Ölçerin şaşması ÖNGÖRÜLEBİLİR. Kalibre değerler üzerinden hüküm verilebilir.")

    # ------------------------------- HUKUM ---------------------------------------
    print("\n" + "=" * 112)
    print("HÜKÜM — kalibre kesinti · eşikler K124'ten aynen (>=%40 KAPANIR · <%30 AÇILIR)")
    print("=" * 112)
    duz_pla = ham["PLASE"]["kes"] - 14.0 if "PLASE" in ham else np.nan
    print(f"  {'bahis':>22} {'ayak':>4} {'n':>6} {'birim':>6} {'KALİBRE':>9} {'%90 GA':>16}  "
          f"{'HÜKÜM':<10} dayanak")
    print("-" * 112)
    BAK = KT.BAKILMAMIS

    def yazdir(ad):
        h = ham[ad]
        n = AYAK.get(ad, 1)
        if ad == "7'Lİ PLASE":
            print(f"  {ad[:22]:>22} {n:>4} {h['n']:>6,} {'—':>6} {'—':>9} {'—':>16}  "
                  f"{'ÖLÇÜLEMEDİ':<10} kalite kapısı %{100*h['dog']/max(h['gor'],1):.0f} (ölçüt G)")
            return
        if ad == "PLASE":
            print(f"  {ad[:22]:>22} {n:>4} {h['n']:>6,} {h['b']:>6.2f} {14.0:>8.1f}% "
                  f"{'—':>16}  {'ÇAPA':<10} plase ailesinin kalibrasyon dayanağı "
                  f"(ham %{h['kes']:.1f} -> yanlılık {duz_pla:+.1f}); DOĞRULAMA DEĞİL")
            return
        if ad in KT.PLASE_AILE:
            # yanlilik = olculen - gercek = duz_pla (negatif) -> gercek = olculen - yanlilik
            k, lo, hi = h["kes"] - duz_pla, h["lo"] - duz_pla, h["hi"] - duz_pla
            hkm = "KAPANIR" if lo >= KT.KAPAT_ESIK else "BELİRSİZ"
            day = "ALT SINIR (ölçüt E); Harville yanlılığı 2 seçimde birikir -> gerçek DAHA YÜKSEK"
        elif ad in KT.BIRIM_YOK:
            k, lo, hi = h["kes"], h["lo"], h["hi"]
            hkm = "KAPANIR" if lo >= KT.KAPAT_ESIK else "BELİRSİZ"
            day = (f"ALT SINIR (ölçüt F; M={h['M']:.3f} -> birim>={max(1.0, h['M']):.2f})"
                   if h["M"] > 1 else f"ALT SINIR (ölçüt F, birim>=1,00; M={h['M']:.3f})")
        else:
            d = a0 + b0 * n
            k, lo, hi = h["kes"] - d, h["lo"] - d, h["hi"] - d
            hkm = ("KAPANIR" if lo >= KT.KAPAT_ESIK
                   else "AÇILIR" if hi < KT.AC_ESIK else "BELİRSİZ")
            day = f"kalibre (yanlilik {d:+.1f} puan)"
        etiket = "  <<< BAKILMAMIŞ" if ad in BAK else ""
        print(f"  {ad[:22]:>22} {n:>4} {h['n']:>6,} {h['b']:>6.2f} {k:>8.1f}% "
              f"[{lo:>5.1f} ..{hi:>6.1f}]  {hkm:<10} {day}{etiket}")

    for ad in sorted(ham, key=lambda a: (a not in BAK, AYAK.get(a, 1), a)):
        yazdir(ad)

    # ------------------------- BIRIM DUYARLILIGI (olcut D) ------------------------
    print("\n" + "=" * 112)
    print("BİRİM DUYARLILIĞI (ölçüt D) — birimi arşiv TABANINDAN okunan bahisler")
    print("=" * 112)
    print(f"  {'bahis':>22} {'birim 1,00':>11} {'1,25':>9} {'1,50':>9} {'2,00':>9}   hüküm değişiyor mu?")
    for ad in ("ÇİFTE", "GANYAN", "SIRALI İKİLİ", "İKİLİ", "PLASE İKİLİ"):
        if ad not in ham:
            continue
        h = ham[ad]
        n = AYAK.get(ad, 1)
        d = duz_pla if ad in KT.PLASE_AILE else (a0 + b0 * n)
        satir, hkm = [], []
        for bb in (1.00, 1.25, 1.50, 2.00):
            k = 100 * (1 - (h["M"] / bb)) - d
            satir.append(f"{k:>9.1f}%")
            hkm.append("KAPANIR" if k >= KT.KAPAT_ESIK else
                       "AÇILIR" if k < KT.AC_ESIK else "BELİRSİZ")
        degisir = "EVET -> " + " / ".join(dict.fromkeys(hkm)) if len(set(hkm)) > 1 else "hayır"
        print(f"  {ad[:22]:>22} " + " ".join(satir) + f"   {degisir}")
    print("\n  ÇİFTE'nin birimi 1,00 kabul edildi çünkü asgari temettüsü 6 yıl boyunca")
    print("  1,40·1,25·1,30·1,35·1,35·1,00 — ENFLASYONLA SÜRÜKLENMİYOR (K124-EK E1).")
    print("  Kıyas: 6'lı'nın asgarisi aynı 6 yılda 20,5 -> 141,2 TL'ye çıktı (taban hiç dövülmüyor).")


if __name__ == "__main__":
    main()
