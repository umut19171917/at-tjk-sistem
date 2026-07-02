"""
favori_test.py — "SAHTE FAVORI" / canli non-favori nisi (arkadasin yontemi).
Hipotez: kalabaligin tek favoriye yigildigi (yuksek implied) koSularda favori asiri oynanmis
olabilir -> 2./3. tercih veya modelin canli non-favorisi DEGER tasiyabilir.
Favori-gucu segmentlerinde, kapanis-orani ROI'leri (out-of-sample 2025-26).
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


def prep(df):
    df = df.dropna(subset=["ganyan_muhtemel", "ganyan_kapanis"]).copy()
    df = df[(df.ganyan_muhtemel > 1) & (df.ganyan_kapanis > 1)]
    gw = df.groupby("race_kod")["kazandi"].transform("sum")
    sz = df.groupby("race_kod")["race_kod"].transform("size")
    return df[(gw == 1) & (sz >= 5)].sort_values("race_kod").reset_index(drop=True)


def main():
    d = pd.read_csv(KOK / "veri" / "ozellikli.csv", low_memory=False)
    d["yil"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    for c in FEAT:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0.0)
    tr = d[d.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
    beta = fit(tr[FEAT].values, *rstruct(tr))
    va = prep(d[d.yil == 2024])
    st, sz, _ = rstruct(va)
    pfv, pmv = softmax(va[FEAT].values @ beta, st, sz), devig(va.ganyan_muhtemel.values, st, sz)
    a, g = fit(np.c_[np.log(pfv + 1e-12), np.log(pmv + 1e-12)], st, sz, va.kazandi.values == 1)

    te = prep(d[d.yil >= 2025])
    st, sz, _ = rstruct(te)
    te["pm"] = devig(te.ganyan_muhtemel.values, st, sz)
    pf = softmax(te[FEAT].values @ beta, st, sz)
    te["pc"] = softmax(a * np.log(pf + 1e-12) + g * np.log(te.pm.values + 1e-12), st, sz)
    te["mrank"] = te.groupby("race_kod")["pm"].rank(ascending=False, method="first")
    te["ev"] = te.pc * te.ganyan_kapanis
    # yaris favori gucu = favori implied (max pm)
    te["fav_imp"] = te.groupby("race_kod")["pm"].transform("max")

    def roi(sub):
        return (sub.ganyan_kapanis * (sub.kazandi == 1) - 1).mean() * 100 if len(sub) else float("nan")

    te["seg"] = pd.cut(te.fav_imp, [0, .35, .45, .55, .70, 1.0],
                       labels=["<35", "35-45", "45-55", "55-70", "70+"])
    print("Favori-gucu segmentleri (TEST 2025-26). ROI%% kapanis oraniyla.")
    print(f"{'segment':8s} {'kosu':>5s} {'favWR%':>7s} {'favIMP%':>8s} "
          f"{'favROI':>7s} {'2.terc':>7s} {'3.terc':>7s} {'modelNonFav':>12s} {'modelEV>1nf':>12s}")
    for s, gg in te.groupby("seg", observed=True):
        nrace = gg.race_kod.nunique()
        fav = gg[gg.mrank == 1]
        c2 = gg[gg.mrank == 2]
        c3 = gg[gg.mrank == 3]
        nonfav = gg[gg.mrank >= 2]
        # modelin canli non-favorisi: her kosuda non-favoriler arasinda max pc
        idx = nonfav.groupby("race_kod")["pc"].idxmax()
        mnf = nonfav.loc[idx]
        # modelin +EV non-favori bahisleri
        evnf = nonfav[nonfav.ev > 1.0]
        print(f"{str(s):8s} {nrace:>5d} {fav.kazandi.mean()*100:>6.1f}% {fav.pm.mean()*100:>7.1f}% "
              f"{roi(fav):>+6.0f} {roi(c2):>+6.0f} {roi(c3):>+6.0f} "
              f"{roi(mnf):>+11.0f} {roi(evnf):>+8.0f}(n={len(evnf)})")

    print("\nNOT: favWR=favori kazanma orani, favIMP=favori implied (de-vig). "
          "favWR<favIMP => sahte-favori (asiri oynanmis).")


if __name__ == "__main__":
    main()
