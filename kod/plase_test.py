"""
plase_test.py — PLASE ilk kez olculuyor (K42 on-analiz): paper testin 5 stratejisinin
GECMIS-VERI beklentisi. model.py ile AYNI walk-forward (egit<=2023, harman 2024, TEST 2025-26).

Stratejiler (paper testle birebir ayni tanim):
  S1 model top-pick (Bot2 max) GANYAN     S2 ayni atin PLASE'si
  S3 kamu favorisi (kapanis min) GANYAN   S4 ayni atin PLASE'si
  S5 CANLI (canli_seri; birden coksa Bot1 max) GANYAN
Odeme: ganyan = kapanis ganyan; plase = BAHISLER_TR temettusu (at plase alamadiysa 0,
plase havuzu olmayan kosuda kupon IPTAL=iade). TOKEN=0, yerel.
"""
import json
import sys
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from ozellik import FEAT  # noqa: E402
from model import race_struct, seg_softmax, fit_clogit, devig, prep  # noqa: E402
from temettu import gan_plase  # noqa: E402

HAM = KOK / "veri" / "ham" / "sonuclar"


def plase_tablosu():
    """ham sonuclar -> {race_kod: {at_no: plase_temettu}} (bos dict = havuz yok/bulunamadi)."""
    tab = {}
    for f in sorted(HAM.glob("*.json")):
        try:
            o = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for k in o.get("kosular", []):
            rk = k.get("KOD")
            try:
                rk = int(rk)
            except (TypeError, ValueError):
                continue
            _, pl = gan_plase(k.get("BAHISLER_TR"))
            tab[rk] = pl
    return tab


def roi_ganyan(rows):
    ret = rows["ganyan_kapanis"].values * (rows["kazandi"].values == 1) - 1
    return ret.mean() * 100, (rows["kazandi"] == 1).mean() * 100, len(rows)


def roi_plase(rows, ptab):
    """kupon basina getiri-1; plase havuzu olmayan kosu IPTAL (hesaba girmez)."""
    rets, hit, n_iptal = [], 0, 0
    for _, r in rows.iterrows():
        pl = ptab.get(int(r["race_kod"]))
        if not pl:
            n_iptal += 1
            continue
        g = pl.get(int(r["no"]), 0.0)
        rets.append(g - 1.0)
        hit += g > 0
    n = len(rets)
    return ((np.mean(rets) * 100) if n else float("nan"),
            (hit / n * 100) if n else float("nan"), n, n_iptal)


def main():
    print("plase temettu tablosu cikariliyor (tum ham)...")
    ptab = plase_tablosu()
    dolu = sum(1 for v in ptab.values() if v)
    print(f"  kosu: {len(ptab)} | plase havuzu bulunan: {dolu} (%{dolu/len(ptab)*100:.1f})")

    d = pd.read_csv(KOK / "veri" / "ozellikli.csv", low_memory=False)
    d["yil"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    for c in FEAT:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0.0)

    tr = d[d.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
    va = prep(d[d.yil == 2024])
    te = prep(d[d.yil >= 2025])
    print(f"egitim: {tr.race_kod.nunique()} | val: {va.race_kod.nunique()} | TEST 2025-26: {te.race_kod.nunique()} kosu")

    beta = fit_clogit(tr[FEAT].values, *race_struct(tr))
    stv, szv, winv = race_struct(va)
    pfv = seg_softmax(va[FEAT].values @ beta, stv, szv)
    pmv = devig(va.ganyan_muhtemel.values, stv, szv)
    alpha, gamma = fit_clogit(np.c_[np.log(pfv + 1e-12), np.log(pmv + 1e-12)], stv, szv, winv)
    print(f"ALPHA={alpha:+.3f} GAMMA={gamma:+.3f}")

    stt, szt, _ = race_struct(te)
    pf = seg_softmax(te[FEAT].values @ beta, stt, szt)
    pm = devig(te.ganyan_muhtemel.values, stt, szt)
    te = te.copy()
    te["bot1"], te["kamu"] = pf, pm
    te["bot2"] = seg_softmax(alpha * np.log(pf + 1e-12) + gamma * np.log(pm + 1e-12), stt, szt)

    g = te.groupby("race_kod")
    top = te.loc[g["bot2"].idxmax()]                       # S1/S2
    fav = te.loc[g["ganyan_kapanis"].idxmin()]             # S3/S4
    favmax = g["kamu"].transform("max")
    canli_m = ((te["kamu"] > 0) & (te["bot1"] >= 1.5 * te["kamu"]) & (te["bot1"] >= 0.10)
               & (te["kamu"] < te["bot1"]) & (te["kamu"] < favmax))
    canli = te[canli_m]
    canli = canli.loc[canli.groupby("race_kod")["bot1"].idxmax()]   # kosu basina 1 (Bot1 max)

    print("\nTEST 2025-26 — paper stratejilerinin gecmis beklentisi (kupon=1 birim):")
    print(f"  {'strateji':34s} {'n':>5s} {'isabet%':>8s} {'ROI%':>8s}")
    for ad, rows in [("S1 top-pick GANYAN", top), ("S3 favori GANYAN", fav),
                     ("S5 CANLI GANYAN", canli)]:
        roi, hit, n = roi_ganyan(rows)
        print(f"  {ad:34s} {n:>5d} {hit:>7.1f}% {roi:>+7.1f}%")
    for ad, rows in [("S2 top-pick PLASE", top), ("S4 favori PLASE", fav)]:
        roi, hit, n, nip = roi_plase(rows, ptab)
        print(f"  {ad:34s} {n:>5d} {hit:>7.1f}% {roi:>+7.1f}%   (iptal/havuzsuz: {nip})")

    # saha boyu kirilimi (plase 4-6 atta ilk-2, 7+ atta ilk-3 oder -> yapi farkli)
    alan = te.groupby("race_kod")["race_kod"].transform("size")
    te["alan_k"] = np.where(alan >= 7, "7+", "4-6")
    print("\n  plase saha-boyu kirilimi (top-pick):")
    for ak, grp in top.merge(te[["race_kod", "alan_k"]].drop_duplicates(), on="race_kod").groupby("alan_k"):
        roi, hit, n, nip = roi_plase(grp, ptab)
        print(f"    saha {ak:3s}: n={n:<5d} isabet {hit:5.1f}%  ROI {roi:+6.1f}%")


if __name__ == "__main__":
    main()
