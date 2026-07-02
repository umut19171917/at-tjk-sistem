"""
yapisal.py — Kalabaligin egzotik YAPISAL sapmasi (model-free).
Her yaris: atlari kamu oranina (muhtemel) gore sirala (1=favori). Kazanan exacta'nin
yapisi = (1.'nin favori-sirasi r1, 2.'nin favori-sirasi r2). Gercek temettuyle:
  IZGARA ROI[i,j] = "her yaris (i 1., j 2.) exacta'sini oyna" stratejisinin gercek ROI'si.
  -> negatif = kalabalik o yapiyi asiri oynamis; ~0/pozitif = eksik oynamis (sömürülebilir).
Detection <=2024; secilen +EV yapiyi 2025-26'da OUT-OF-SAMPLE test.
"""
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA"}  # zaten ozellikli'de haric
RMAX = 7


def main():
    d = pd.read_csv(KOK / "veri" / "ozellikli.csv", low_memory=False)
    eg = pd.read_csv(KOK / "veri" / "egzotik.csv", low_memory=False)
    d["yil"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    for c in ["ganyan_muhtemel", "sonuc", "alan"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=["ganyan_muhtemel", "sonuc"])
    d = d[d.ganyan_muhtemel > 1]
    d["rank"] = d.groupby("race_kod")["ganyan_muhtemel"].rank(method="first")

    w1 = d[d.sonuc == 1][["race_kod", "rank", "yil", "alan"]].rename(columns={"rank": "r1"})
    w2 = d[d.sonuc == 2][["race_kod", "rank"]].rename(columns={"rank": "r2"})
    r = w1.merge(w2, on="race_kod").merge(eg[["race_kod", "exacta_div"]], on="race_kod")
    r = r.dropna(subset=["exacta_div", "r1", "r2", "alan"])
    r[["r1", "r2", "alan"]] = r[["r1", "r2", "alan"]].astype(int)
    tr = r[r.yil <= 2024]
    te = r[r.yil >= 2025]
    print(f"yaris: toplam {len(r)} | egitim(<=2024) {len(tr)} | test(>=2025) {len(te)}")

    def grid_roi(sub):
        G = np.full((RMAX + 1, RMAX + 1), np.nan)
        N = np.zeros((RMAX + 1, RMAX + 1), int)
        for i in range(1, RMAX + 1):
            for j in range(1, RMAX + 1):
                if i == j:
                    continue
                elig = sub[sub.alan >= max(i, j)]
                n = len(elig)
                if n < 20:
                    continue
                pay = elig.loc[(elig.r1 == i) & (elig.r2 == j), "exacta_div"].sum()
                G[i, j] = (pay - n) / n * 100
                N[i, j] = n
        return G, N

    G, N = grid_roi(tr)
    print("\nIZGARA ROI% (satir=1.'nin favori sirasi, sutun=2.'nin) — EGITIM <=2024")
    print("      " + "".join(f"j={j:<6d}" for j in range(1, RMAX + 1)))
    for i in range(1, RMAX + 1):
        cells = "".join((f"{G[i,j]:>+6.0f} " if np.isfinite(G[i, j]) else "   .   ")
                        for j in range(1, RMAX + 1))
        print(f"i={i}  {cells}")

    # egitimde +EV (ya da ~breakeven) hucreler: ROI>-5 ve yeterli ornek
    sec = [(i, j) for i in range(1, RMAX + 1) for j in range(1, RMAX + 1)
           if np.isfinite(G[i, j]) and G[i, j] > -5 and N[i, j] >= 50]
    print(f"\negitimde ROI>-5% hucreler (n>=50): {sec}")

    # ---- OUT-OF-SAMPLE test (2025-26): secilen hucreleri oyna ----
    def strat_roi(sub, cells):
        n_cost = pay = 0
        for (i, j) in cells:
            elig = sub[sub.alan >= max(i, j)]
            n_cost += len(elig)
            pay += elig.loc[(elig.r1 == i) & (elig.r2 == j), "exacta_div"].sum()
        return n_cost, ((pay - n_cost) / n_cost * 100 if n_cost else float("nan"))

    if sec:
        nc, roi = strat_roi(te, sec)
        print(f"\nOUT-OF-SAMPLE (2025-26) secilen yapiyi oyna: maliyet={nc}  ROI={roi:+.1f}%")

    # ---- kanonik stratejiler (hucre-kume, dogru maliyet) — TEST 2025-26 ----
    print("\nKanonik stratejiler — TEST 2025-26 (maliyet=kombinasyon sayisi):")
    R = range(1, RMAX + 1)
    kanon = {
        "favori/saha (1/*)": [(1, j) for j in R if j != 1],
        "saha/favori (*/1)": [(i, 1) for i in R if i != 1],
        "top2 box (1-2)": [(1, 2), (2, 1)],
        "top3 box": [(i, j) for i in range(1, 4) for j in range(1, 4) if i != j],
        "uzunsansli 1. (r1>=4)": [(i, j) for i in range(4, RMAX + 1) for j in R if i != j],
    }
    for ad, cells in kanon.items():
        nc, roi = strat_roi(te, cells)
        print(f"  {ad:24s} maliyet={nc:>6d}  ROI={roi:>+7.1f}%")


if __name__ == "__main__":
    main()
