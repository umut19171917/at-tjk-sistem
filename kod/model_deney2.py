# -*- coding: utf-8 -*-
"""
model_deney2.py — K133: BEKLEYENLER #19'un iki işi. SALT-OKUNUR / OFFLINE.

#19-A BİRLEŞTİRME: K128'de B1 (5 etkileşim) ve B2 (13 sürekli x 3 spline düğümü) ayrı ayrı
       bot1'i iyileştirmişti (−0,0046 / −0,0048) ama ikisi BİRLİKTE denenmemişti (K128 madde 6:
       2^9 kombinasyonda arama overfit kapısıdır). #19-A **tek bir** birleşimi, önceden
       bağlanmış hâlde denemeyi şart koşmuştu: B1 ∪ B2, başka hiçbir kombinasyon taranmadan.

#19-B "bot1'i FARKLI kılmak": K128'in deseni şunu ima etti — alpha'yı yükselten şey bot1'in
       DOĞRULUĞU değil, piyasadan FARKLILIĞI olabilir. Kanıt: B1/B2 bot1'i iyileştirdi ama
       alpha kıpırdamadı (0,190 → 0,194/0,191); C1 (sıra-patlatmalı) bot1'i KÖTÜLEŞTİRDİĞİ
       hâlde alpha'yı 0,220'ye çıkardı.

=====================================================================================
ÖN-KAYITLI ÖLÇÜT — SONUÇLAR GÖRÜLMEDEN YAZILDI VE GİT'E MÜHÜRLENDİ (K33/K52)
=====================================================================================
0) MUTLAK SINIR: hiçbir dosyaya YAZILMAZ. Canlı yol, config, kuponlar, `ozellikli.csv` —
   hiçbiri değişmez. **Canlı kart şu anda akıyor;** bu betik yalnız okur.

1) ÇAPA: taban varyantı K128'in değerlerini üretmeli —
   alpha +0,190 · gamma +0,975 · Bot1 OOS 1,8594 · Bot2 OOS 1,6987 (tolerans ±0,0005/±0,002).
   Tutmazsa ölçüm güvenilmez, hüküm yok.

2) YENİ ÖZELLİK YASAK (K33 kapalı). Yalnız fonksiyon biçimi değişir.

3) #19-A HÜKÜM (tek varyant -> Bonferroni GEREKMEZ, %95 GA yeter):
   AB = B1 ∪ B2 "GEÇTİ" sayılır ancak ÜÇÜ birden tutarsa:
     (a) alpha > taban alpha
     (b) Bot2 OOS log-loss < taban
     (c) (b) farkının koşu-düzeyi eşleşmiş %95 GA'sı tamamen sıfırın altında
   Üçünden biri tutmazsa DÜŞTÜ ve **#19-A KAPANIR.**

4) #19-A EK SORU (hüküm üretmez, mekanizma): B1 ve B2 EŞDOĞRUSAL mı?
   Ölçü: bot1 iyileşmelerinin TOPLANABİLİRLİĞİ.
     toplanabilirlik = (ll1_taban − ll1_AB) / [(ll1_taban − ll1_B1) + (ll1_taban − ll1_B2)]
   ~1,0 -> bağımsız · ~0,5 -> yarı örtüşük · ~0 -> tamamen aynı şey.
   Beklenti ÖNCEDEN yazılıyor: **düşük (~0,5 veya altı)**; ikisi de "doğrusal-olmayanlık"
   yakalıyor, farklı yollardan.

5) #19-B HÜKÜM: "farklılık" hipotezi. Bot1'in piyasadan UZAKLIĞI ölçülür:
     uzaklik = koşu başına 0,5*sum|p_bot1 − p_kamu|  (toplam değişim uzaklığı, [0,1])
   Beş varyantın (taban, B1, B2, AB, C1) her biri için (uzaklik, ll1, alpha) üçlüsü basılır.
     H: alpha, DOĞRULUKTAN çok UZAKLIK ile açıklanıyor.
     ÖLÇÜT: 5 nokta üzerinde alpha'nın uzaklik ile korelasyonu, ll1 ile korelasyonundan
     BÜYÜK olmalı VE işareti pozitif olmalı.
     **n=5 ile bu bir HİPOTEZ SINAMASI DEĞİLDİR** — betimleyicidir ve öyle raporlanır.
     Hüküm üretmez; yalnız BEKLEYENLER'e yön verir.

6) #19-B'nin karar sınırı (K128'den aynen): bu kol KÂR VAADİ DEĞİLDİR. Bot2'nin piyasa
   üzerindeki toplam katkısı 0,0066; kesintiyi aşmak için gereken mertebe bunun kat kat
   üstünde. Kol "nereye bakmayacağımızı" kesinleştirmek için açık.
=====================================================================================
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from ozellik import FEAT                                            # noqa: E402
from model import race_struct, seg_softmax, devig, logloss, prep    # noqa: E402
import model_deney as MD                                            # noqa: E402

BOOT = 4000
RNG = np.random.default_rng(20260827)
EPS = 1e-12


def main():
    print("=" * 106)
    print("K133 — BEKLEYENLER #19: (A) B1∪B2 birleşimi · (B) 'bot1'i farklı kılmak' hipotezi")
    print("SALT-OKUNUR. Canlı kart akıyor; bu betik hiçbir dosyaya yazmaz.")
    print("=" * 106)

    d = MD.yukle()
    tr = d[d.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
    va = prep(d[d.yil == 2024])
    te = prep(d[d.yil >= 2025])
    st0, sz0, win0 = race_struct(tr)
    Xtr, Xva, Xte = tr[FEAT].values, va[FEAT].values, te[FEAT].values
    print(f"  eğitim {tr.race_kod.nunique():,} · val {va.race_kod.nunique():,} "
          f"· test {te.race_kod.nunique():,}")

    def etk(f):
        return np.column_stack([f[a].to_numpy(float) * f[b].to_numpy(float)
                                for a, b in MD.ETKILESIM])

    Str, Sva, _ = MD.spline_genislet(tr, va, MD.SUREKLI)
    _, Ste, _ = MD.spline_genislet(tr, te, MD.SUREKLI)
    ikili = [c for c in FEAT if c not in MD.SUREKLI]

    # spline blogu = sadece ek tabanlar (ham z-skor FEAT'te zaten var)
    ek_tr = Str[:, [i for i in range(Str.shape[1])
                    if i % 4 != 0]]              # her ozellik icin [x, s0, s1, s2] -> x'i at
    ek_va = Sva[:, [i for i in range(Sva.shape[1]) if i % 4 != 0]]
    ek_te = Ste[:, [i for i in range(Ste.shape[1]) if i % 4 != 0]]

    tasarimlar = {
        "T   taban": (Xtr, Xva, Xte),
        "B1  etkileşim": (np.c_[Xtr, etk(tr)], np.c_[Xva, etk(va)], np.c_[Xte, etk(te)]),
        "B2  spline": (np.c_[Str, tr[ikili].values], np.c_[Sva, va[ikili].values],
                       np.c_[Ste, te[ikili].values]),
        "AB  B1 ∪ B2 (#19-A)": (np.c_[Xtr, etk(tr), ek_tr], np.c_[Xva, etk(va), ek_va],
                                np.c_[Xte, etk(te), ek_te]),
    }

    sonuc = {}
    for ad, (A, B, C) in tasarimlar.items():
        beta = MD.fit_clogit_w(A, st0, sz0, win0)
        sonuc[ad] = MD.degerlendir(ad, None, B @ beta, C @ beta, va, te)
        sonuc[ad]["skor_te"] = C @ beta
    # C1: sira-patlatmali (K128'deki ile ayni)
    pl = MD.patlat(tr, 3, FEAT)
    sp, zp, wp = race_struct(pl)
    b_pl = MD.fit_clogit_w(pl[FEAT].values, sp, zp, wp)
    sonuc["C1  sıra-patlatmalı"] = MD.degerlendir("C1  sıra-patlatmalı", None,
                                                  Xva @ b_pl, Xte @ b_pl, va, te)
    sonuc["C1  sıra-patlatmalı"]["skor_te"] = Xte @ b_pl

    T = sonuc["T   taban"]
    print("\n" + "=" * 106)
    print("ÇAPA (madde 1)")
    print("=" * 106)
    kont = [("alpha", T["alpha"], 0.190, 0.002), ("gamma", T["gamma"], 0.975, 0.002),
            ("Bot1 OOS", T["ll1"], 1.8594, 0.0005), ("Bot2 OOS", T["ll2"], 1.6987, 0.0005)]
    ok = True
    for a, o, b, tol in kont:
        g = abs(o - b) <= tol
        ok &= g
        print(f"  {a:>10}: beklenen {b:+.4f} · ölçülen {o:+.4f} -> {'TUTTU' if g else 'TUTMADI'}")
    if not ok:
        print("\n  ÇAPA DÜŞTÜ -> hüküm yok.")
        return

    # ------------------------------- #19-A ---------------------------------------
    print("\n" + "=" * 106)
    print("#19-A — B1 ∪ B2 BİRLEŞİMİ (tek varyant, %95 GA)")
    print("=" * 106)
    print(f"  {'varyant':>22} {'alpha':>8} {'Bot1 OOS':>10} {'Bot2 OOS':>10} {'Δ Bot2':>9} "
          f"{'%95 GA':>21}  hüküm")
    kt = T["kayip"]
    idx = RNG.integers(0, len(kt), size=(BOOT, len(kt)))
    for ad in ("B1  etkileşim", "B2  spline", "AB  B1 ∪ B2 (#19-A)", "C1  sıra-patlatmalı"):
        r = sonuc[ad]
        f = r["kayip"] - kt
        bb = f[idx].mean(1)
        lo, hi = np.percentile(bb, 2.5), np.percentile(bb, 97.5)
        a_ok, l_ok, c_ok = r["alpha"] > T["alpha"], r["ll2"] < T["ll2"], hi < 0
        h = "GEÇTİ" if (a_ok and l_ok and c_ok) else "düştü"
        yildiz = "  <-- #19-A" if ad.startswith("AB") else ""
        print(f"  {ad:>22} {r['alpha']:>+8.3f} {r['ll1']:>10.4f} {r['ll2']:>10.4f} "
              f"{f.mean():>+9.4f} [{lo:>+9.4f},{hi:>+9.4f}]  {h}{yildiz}")

    # ---------------------------- #19-A ek soru ----------------------------------
    k1 = T["ll1"] - sonuc["B1  etkileşim"]["ll1"]
    k2 = T["ll1"] - sonuc["B2  spline"]["ll1"]
    kab = T["ll1"] - sonuc["AB  B1 ∪ B2 (#19-A)"]["ll1"]
    topl = kab / (k1 + k2) if (k1 + k2) != 0 else float("nan")
    print(f"\n  TOPLANABİLİRLİK (madde 4): B1 {k1:+.4f} · B2 {k2:+.4f} · "
          f"birlikte {kab:+.4f}")
    print(f"     oran = {topl:.2f}  ->  " +
          ("BAĞIMSIZ" if topl > 0.85 else "YARI ÖRTÜŞÜK" if topl > 0.4 else "AYNI ŞEY"))

    # ------------------------------- #19-B ---------------------------------------
    print("\n" + "=" * 106)
    print("#19-B — 'bot1'i FARKLI kılmak' (BETİMLEYİCİ, n=5; HÜKÜM ÜRETMEZ — madde 5)")
    print("=" * 106)
    stt, szt, wint = race_struct(te)
    pmt = devig(te.ganyan_muhtemel.values, stt, szt)
    print(f"  {'varyant':>22} {'Bot1 OOS':>10} {'piyasadan uzaklık':>18} {'alpha':>8}")
    U, L, A = [], [], []
    for ad in ("T   taban", "B1  etkileşim", "B2  spline", "AB  B1 ∪ B2 (#19-A)",
               "C1  sıra-patlatmalı"):
        r = sonuc[ad]
        p1 = seg_softmax(r["skor_te"], stt, szt)
        # kosu basina toplam degisim uzakligi
        d_ = np.abs(p1 - pmt)
        uz = 0.5 * np.add.reduceat(d_, stt)
        print(f"  {ad:>22} {r['ll1']:>10.4f} {uz.mean():>18.4f} {r['alpha']:>+8.3f}")
        U.append(uz.mean()); L.append(r["ll1"]); A.append(r["alpha"])
    U, L, A = np.array(U), np.array(L), np.array(A)
    r_uz = float(np.corrcoef(U, A)[0, 1])
    r_ll = float(np.corrcoef(L, A)[0, 1])
    print(f"\n  alpha ~ UZAKLIK korelasyonu : {r_uz:+.3f}")
    print(f"  alpha ~ Bot1 log-loss koral.: {r_ll:+.3f}  (log-loss DÜŞÜK=iyi, "
          f"pozitif korelasyon 'kötü bot1 -> yüksek alpha' demek)")
    if r_uz > 0 and abs(r_uz) > abs(r_ll):
        print("  -> DESEN, 'farklılık' hipotezini destekliyor (ama n=5, HÜKÜM DEĞİL).")
    else:
        print("  -> DESEN, 'farklılık' hipotezini DESTEKLEMİYOR (n=5, HÜKÜM DEĞİL).")
    print("\n  HATIRLATMA (madde 6): bu kol kâr vaadi değildir. Bot2'nin piyasa üzerindeki")
    print("  toplam katkısı 0,0066; kesinti duvarı bunun kat kat üstünde.")
    print("\n  HİÇBİR DOSYAYA YAZILMADI.")


if __name__ == "__main__":
    main()
