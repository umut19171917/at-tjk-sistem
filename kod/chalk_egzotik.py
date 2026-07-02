"""
chalk_egzotik.py — "Canli non-favori + egzotik monetizasyon" hedefli testi.
Sadece GUCLU-FAVORI (chalk) koSularda, favori-rank yapilariyla exacta stratejileri,
GERCEK temettuyle. Soru: chalk'ta favoriyi yenen yapi egzotikle +EV mi?
Model-free (sadece kamu orani siralamasi). Segment = favori implied gucu.
"""
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
RMAX = 8


def main():
    d = pd.read_csv(KOK / "veri" / "ozellikli.csv", low_memory=False)
    eg = pd.read_csv(KOK / "veri" / "egzotik.csv", low_memory=False)
    d["yil"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    for c in ["ganyan_muhtemel", "sonuc", "alan"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=["ganyan_muhtemel", "sonuc"])
    d = d[d.ganyan_muhtemel > 1]
    d["inv"] = 1.0 / d.ganyan_muhtemel
    d["pimp"] = d.inv / d.groupby("race_kod")["inv"].transform("sum")
    d["fav_imp"] = d.groupby("race_kod")["pimp"].transform("max")
    d["rank"] = d.groupby("race_kod")["ganyan_muhtemel"].rank(method="first")

    w1 = d[d.sonuc == 1].groupby("race_kod").agg(r1=("rank", "min"), yil=("yil", "first"),
                                                 alan=("alan", "first"), fav_imp=("fav_imp", "first"))
    w2 = d[d.sonuc == 2].groupby("race_kod").agg(r2=("rank", "min"))
    r = w1.join(w2, how="inner").reset_index().merge(eg[["race_kod", "exacta_div"]], on="race_kod")
    r = r.dropna(subset=["exacta_div", "r1", "r2", "alan", "fav_imp"])
    r[["r1", "r2", "alan"]] = r[["r1", "r2", "alan"]].astype(int)

    def strat_roi(sub, cells):
        cost = pay = 0
        for (i, j) in cells:
            elig = sub[sub.alan >= max(i, j)]
            cost += len(elig)
            pay += elig.loc[(elig.r1 == i) & (elig.r2 == j), "exacta_div"].sum()
        return cost, ((pay - cost) / cost * 100 if cost else float("nan"))

    R = range(1, RMAX + 1)
    strat = {
        "favori 1. (1/*) [baz]": [(1, j) for j in R if j != 1],
        "2.tercih 1. (2/*)": [(2, j) for j in R if j != 2],
        "favori YENILDI (r1>=2 / *)": [(i, j) for i in range(2, RMAX + 1) for j in R if i != j],
        "favori 2.'de (*/1)": [(i, 1) for i in R if i != 1],
        "2-3 box": [(i, j) for i in (2, 3) for j in (2, 3) if i != j],
        "2-3-4 ust / saha (r1 in 2..4)": [(i, j) for i in (2, 3, 4) for j in R if i != j],
    }

    segs = [("acik <45", r.fav_imp < .45), ("orta 45-55", (r.fav_imp >= .45) & (r.fav_imp < .55)),
            ("CHALK 55-70", (r.fav_imp >= .55) & (r.fav_imp < .70)), ("CHALK 70+", r.fav_imp >= .70),
            ("TUM CHALK 55+", r.fav_imp >= .55)]

    for sad, smask in segs:
        sub = r[smask]
        ntest = sub[sub.yil >= 2025]
        print(f"\n=== {sad}  (toplam {len(sub)} kosu, test'25-26 {len(ntest)}) ===")
        print(f"  {'strateji':32s} {'maliyet':>8s} {'ROI%(tum)':>10s} {'ROI%(test)':>11s}")
        for ad, cells in strat.items():
            c_all, roi_all = strat_roi(sub, cells)
            c_te, roi_te = strat_roi(ntest, cells)
            print(f"  {ad:32s} {c_all:>8d} {roi_all:>+10.1f} {roi_te:>+11.1f}")


if __name__ == "__main__":
    main()
