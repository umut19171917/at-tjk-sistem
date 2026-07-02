"""
segment.py — Edge nis analizi. model.py hattini tekrar kurar, TEST setinde edge'in
nerede yogunlastigini arar:
  1) EV-desil kalibrasyonu (asil mercek): yuksek-EV bahisler gercekten kar ediyor mu?
  2) Saha boyu / sinif / pist kirilimi: model-top-pick ROI
  3) Kontrarian: model favoriden ayrildiginda (saf fundamental bahis) ROI
Hepsi kapanis oraniyla (IYIMSER ust sinir).
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import minimize

KOK = Path(__file__).resolve().parent.parent
FEAT = ["hiz_son_ort_z", "hiz_en_iyi_z", "form_pos_z", "form_fark_z", "kilo_z",
        "handikap_z", "kariyer_galip_oran_z", "zemin_galip_oran_z", "jokey_isabet_z",
        "antrenor_isabet_z", "kulvar_skor_z", "son_yarisdan_gun_z", "yas_z", "disi", "ilk_kosu"]


def race_struct(df):
    rc = df["race_kod"].values
    start = np.r_[0, np.where(rc[1:] != rc[:-1])[0] + 1]
    sizes = np.diff(np.r_[start, len(rc)])
    return start, sizes, (df["kazandi"].values == 1)


def seg_softmax(s, start, sizes):
    e = np.exp(s - np.repeat(np.maximum.reduceat(s, start), sizes))
    return e / np.repeat(np.add.reduceat(e, start), sizes)


def fit_clogit(X, start, sizes, win):
    def negll(b):
        p = seg_softmax(X @ b, start, sizes)
        return -np.log(p[win] + 1e-12).sum(), -(X[win].sum(0) - (X * p[:, None]).sum(0))
    return minimize(negll, np.zeros(X.shape[1]), jac=True, method="L-BFGS-B").x


def devig(odds, start, sizes):
    inv = 1.0 / odds
    return inv / np.repeat(np.add.reduceat(inv, start), sizes)


def prep(df):
    df = df.dropna(subset=["ganyan_muhtemel", "ganyan_kapanis"]).copy()
    df = df[(df.ganyan_muhtemel > 1) & (df.ganyan_kapanis > 1)].sort_values("race_kod")
    gw = df.groupby("race_kod")["kazandi"].transform("sum")
    sz = df.groupby("race_kod")["race_kod"].transform("size")
    return df[(gw == 1) & (sz >= 4)].sort_values("race_kod").reset_index(drop=True)


def sinif_bucket(s):
    s = str(s)
    for k in ["Maiden", "Handikap", "Şartlı", "Satış", "KV"]:
        if k.lower() in s.lower():
            return k
    return "diger"


def roi(odds, win):
    return (odds * win - 1).mean() if len(odds) else np.nan


def main():
    d = pd.read_csv(KOK / "veri" / "ozellikli.csv", low_memory=False)
    d["yil"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    for c in FEAT:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0.0)

    tr = d[d.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
    va, te = prep(d[d.yil == 2024]), prep(d[d.yil >= 2025])
    beta = fit_clogit(tr[FEAT].values, *race_struct(tr))

    def pf(df):
        st, sz, _ = race_struct(df)
        return seg_softmax(df[FEAT].values @ beta, st, sz), st, sz

    pfv, stv, szv = pf(va)
    pmv = devig(va.ganyan_muhtemel.values, stv, szv)
    a, g = fit_clogit(np.c_[np.log(pfv + 1e-12), np.log(pmv + 1e-12)], stv, szv, va.kazandi.values == 1)

    pft, stt, szt = pf(te)
    pmt = devig(te.ganyan_muhtemel.values, stt, szt)
    pct = seg_softmax(a * np.log(pft + 1e-12) + g * np.log(pmt + 1e-12), stt, szt)
    te = te.copy()
    te["pc"], te["odds"], te["win"] = pct, te.ganyan_kapanis.values, (te.kazandi.values == 1)
    te["ev"] = te.pc * te.odds

    print(f"test kosu: {te.race_kod.nunique()} | at-satiri: {len(te)}  (alpha={a:+.3f})")

    # 1) EV-DESIL KALIBRASYONU
    print("\n[1] EV-desil (pc x kapanis): yuksek EV gercekten kar mi?")
    te["evd"] = pd.qcut(te.ev, 10, labels=False, duplicates="drop")
    print(f"  {'desil':>5s} {'n':>6s} {'ort.EV':>7s} {'isabet%':>8s} {'ROI%':>8s}")
    for q, gg in te.groupby("evd"):
        print(f"  {int(q):>5d} {len(gg):>6d} {gg.ev.mean():>7.2f} "
              f"{gg.win.mean()*100:>7.1f}% {roi(gg.odds.values, gg.win.values)*100:>+7.1f}%")

    # 2) MODEL TOP-PICK (her kosuda max pc) ROI, kirilimli
    top = te.loc[te.groupby("race_kod")["pc"].idxmax()].copy()
    fav = te.loc[te.groupby("race_kod")["odds"].idxmin()]
    print(f"\n[2] Her kosuda MODEL top-pick oyna ROI: {roi(top.odds.values, top.win.values)*100:+.1f}%"
          f"  (favori referans: {roi(fav.odds.values, fav.win.values)*100:+.1f}%)")
    top["alan_k"] = pd.cut(top.alan, [0, 8, 12, 99], labels=["<=8", "9-12", "13+"])
    top["sinif_k"] = top.sinif.map(sinif_bucket)
    top["oran_k"] = pd.cut(top.odds, [0, 2, 4, 8, 999], labels=["1-2", "2-4", "4-8", "8+"])
    for kol in ["alan_k", "sinif_k", "sehir", "oran_k"]:
        print(f"\n  top-pick ROI -> {kol}:")
        for k, gg in top.groupby(kol, observed=True):
            print(f"    {str(k):10s} n={len(gg):>4d} isabet={gg.win.mean()*100:>5.1f}% "
                  f"ROI={roi(gg.odds.values, gg.win.values)*100:>+6.1f}%")

    # 3) KONTRARIAN: model top-pick != favori (saf fundamental bahis)
    top["fav_odds"] = fav.set_index("race_kod").reindex(top.race_kod).odds.values
    kar = top[top.odds > top.fav_odds + 1e-9]   # model favoriden farkli (daha uzun oranli) at sectiyse
    print(f"\n[3] Kontrarian (model top-pick != favori): n={len(kar)} "
          f"isabet={kar.win.mean()*100:.1f}% ROI={roi(kar.odds.values, kar.win.values)*100:+.1f}%")


if __name__ == "__main__":
    main()
