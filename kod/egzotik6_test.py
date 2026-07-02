"""
egzotik6_test.py — ALTILI backtest (top-k spread).
Strateji: her ayakta sirala (model varsa model, yoksa piyasa), top-k at al.
  Tutar (hit) <=> 6 ayagin HEPSINDE kazanan top-k icinde.
  Maliyet = Π min(k, saha)  (satir sayisi) ;  odeme = gercek Altili temettusu (1 kazanan satir).
Model-sirasi vs Piyasa-sirasi, OUT-OF-SAMPLE (2025-26).
UYARI: Altili variance devasa; ROI birkac dev temettuye baglidir -> dusuk istatistiksel guc.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import minimize

KOK = Path(__file__).resolve().parent.parent
FEAT = ["hiz_son_ort_z", "hiz_en_iyi_z", "form_pos_z", "form_fark_z", "kilo_z",
        "handikap_z", "kariyer_galip_oran_z", "zemin_galip_oran_z", "jokey_isabet_z",
        "antrenor_isabet_z", "kulvar_skor_z", "son_yarisdan_gun_z", "yas_z", "disi", "ilk_kosu"]


def rstruct(df):
    rc = df["race_kod"].values
    st = np.r_[0, np.where(rc[1:] != rc[:-1])[0] + 1]
    return st, np.diff(np.r_[st, len(rc)]), (df["kazandi"].values == 1)


def softmax(s, st, sz):
    e = np.exp(s - np.repeat(np.maximum.reduceat(s, st), sz))
    return e / np.repeat(np.add.reduceat(e, st), sz)


def fit(X, st, sz, win):
    def f(b):
        p = softmax(X @ b, st, sz)
        return -np.log(p[win] + 1e-12).sum(), -(X[win].sum(0) - (X * p[:, None]).sum(0))
    return minimize(f, np.zeros(X.shape[1]), jac=True, method="L-BFGS-B").x


def devig(o, st, sz):
    inv = 1.0 / o
    return inv / np.repeat(np.add.reduceat(inv, st), sz)


def main():
    # ---- MODEL: Bot1+Bot2 -> pc per (race_kod,no) (Ingiliz+izinli) ----
    d = pd.read_csv(KOK / "veri" / "ozellikli.csv", low_memory=False)
    d["yil"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    for c in FEAT:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0.0)
    d["no"] = pd.to_numeric(d["no"], errors="coerce")
    tr = d[d.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
    beta = fit(tr[FEAT].values, *rstruct(tr))

    def prep(x):
        x = x.dropna(subset=["ganyan_muhtemel"]).copy()
        x = x[x.ganyan_muhtemel > 1].sort_values("race_kod")
        sz = x.groupby("race_kod")["race_kod"].transform("size")
        return x[sz >= 2].sort_values("race_kod").reset_index(drop=True)
    va = prep(d[d.yil == 2024])
    st, sz, _ = rstruct(va)
    pfv = softmax(va[FEAT].values @ beta, st, sz)
    pmv = devig(va.ganyan_muhtemel.values, st, sz)
    a, g = fit(np.c_[np.log(pfv + 1e-12), np.log(pmv + 1e-12)], st, sz, va.kazandi.values == 1)

    allp = prep(d)
    st, sz, _ = rstruct(allp)
    pf = softmax(allp[FEAT].values @ beta, st, sz)
    pm = devig(allp.ganyan_muhtemel.values, st, sz)
    allp["pc"] = softmax(a * np.log(pf + 1e-12) + g * np.log(pm + 1e-12), st, sz)
    allp["model_rank"] = allp.groupby("race_kod")["pc"].rank(ascending=False, method="first")
    model_rank = {(r, int(n)): int(rk) for r, n, rk in
                  zip(allp.race_kod, allp.no, allp.model_rank)}

    # ---- PIYASA: tum kosular (katilim) -> winner rank + saha ----
    kt = pd.read_csv(KOK / "veri" / "katilim.csv", low_memory=False)
    kt["ganyan_muhtemel"] = pd.to_numeric(kt["ganyan_muhtemel"], errors="coerce")
    kt["sonuc"] = pd.to_numeric(kt["sonuc"], errors="coerce")
    kt["no"] = pd.to_numeric(kt["no"], errors="coerce")
    kt = kt.dropna(subset=["ganyan_muhtemel"])
    kt = kt[kt.ganyan_muhtemel > 1]
    kt["mrank"] = kt.groupby("race_kod")["ganyan_muhtemel"].rank(method="first")
    saha = kt.groupby("race_kod").size().to_dict()
    # kazananlarin market & model rank'i (beraberlikte min)
    legtab = {}
    for rk, gg in kt.groupby("race_kod"):
        wins = gg[gg.sonuc == 1]
        if len(wins) == 0:
            continue
        mr = wins.mrank.min()
        mor = min((model_rank.get((rk, int(n)), gg.mrank.loc[idx])
                   for idx, n in zip(wins.index, wins.no)), default=mr)
        legtab[rk] = (int(mr), int(mor), int(saha.get(rk, len(gg))))

    # ---- ALTILI olaylari ----
    ev = pd.read_csv(KOK / "veri" / "altili.csv", low_memory=False)
    ev["yil"] = pd.to_datetime(ev.gun, format="%d/%m/%Y", errors="coerce").dt.year
    legcols = [f"leg{i}" for i in range(1, 7)]

    def backtest(sub, ranksel):
        out = {}
        for k in [1, 2, 3, 4]:
            cost = pay = hit = nev = 0
            for _, e in sub.iterrows():
                legs = [legtab.get(e[c]) for c in legcols]
                if any(l is None for l in legs):
                    continue
                nev += 1
                c = 1
                for (mr, mor, fld) in legs:
                    c *= min(k, fld)
                cost += c
                ok = all((mor if ranksel == "model" else mr) <= k for (mr, mor, fld) in legs)
                if ok:
                    pay += e.temettu
                    hit += 1
            roi = (pay - cost) / cost * 100 if cost else float("nan")
            out[k] = (nev, hit, cost, roi)
        return out

    for yad, sub in [("TEST 2025-26", ev[ev.yil >= 2025]), ("ref egitim<=2024", ev[ev.yil <= 2024])]:
        print(f"\n=== {yad} (olay: {len(sub)}) ===")
        for ranksel in ["piyasa", "model"]:
            r = backtest(sub, ranksel)
            print(f"  [{ranksel}] {'k':>2s} {'olay':>5s} {'tuttu':>6s} {'maliyet':>9s} {'ROI%':>9s}")
            for k, (nev, hit, cost, roi) in r.items():
                print(f"        {k:>2d} {nev:>5d} {hit:>6d} {cost:>9d} {roi:>+9.1f}")


if __name__ == "__main__":
    main()
