"""
egzotik_test.py — EGZOTIK KARAR DENEYI (Sirali Ikili / exacta).
Bot olasiliklari -> Harville -> exacta olasiligi.
  - SECIM: kamu-oran-Harville'den beklenen temettu ile EV>esik kombinasyonlar (yaris oncesi bilgi).
  - ODEME: gercek sonuc + gercek exacta temettusu (egzotik.csv).
Walk-forward: egit<=2023, harman(Bot2)+takeout(t) 2024, TEST 2025-26.
Soru: out-of-sample pozitif ROI veren +EV exacta kombinasyonu var mi?
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


def prep(df, eg):
    df = df.dropna(subset=["ganyan_muhtemel", "ganyan_kapanis"]).copy()
    df = df[(df.ganyan_muhtemel > 1) & (df.ganyan_kapanis > 1)]
    gw = df.groupby("race_kod")["kazandi"].transform("sum")
    sz = df.groupby("race_kod")["race_kod"].transform("size")
    df = df[(gw == 1) & (sz >= 4)]
    df = df.merge(eg[["race_kod", "exacta_div"]], on="race_kod", how="left")
    return df.sort_values("race_kod").reset_index(drop=True)


def harville_pairs(p):
    """ordered pair olasilik matrisi M[i,j]=p_i*p_j/(1-p_i)."""
    p = np.clip(p, 1e-9, 1 - 1e-9)
    M = np.outer(p, p) / (1 - p)[:, None]
    np.fill_diagonal(M, 0.0)
    return M


def main():
    d = pd.read_csv(KOK / "veri" / "ozellikli.csv", low_memory=False)
    eg = pd.read_csv(KOK / "veri" / "egzotik.csv", low_memory=False)
    d["yil"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    for c in FEAT:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0.0)
    d["no"] = pd.to_numeric(d["no"], errors="coerce")
    d["sonuc"] = pd.to_numeric(d["sonuc"], errors="coerce")

    tr = d[d.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
    va = prep(d[d.yil == 2024], eg)
    te = prep(d[d.yil >= 2025], eg)
    beta = fit(tr[FEAT].values, *rstruct(tr))

    def probs(df):
        st, sz, _ = rstruct(df)
        pf = softmax(df[FEAT].values @ beta, st, sz)
        pm = devig(df.ganyan_muhtemel.values, st, sz)
        return pf, pm, st, sz

    pfv, pmv, stv, szv = probs(va)
    a, g = fit(np.c_[np.log(pfv + 1e-12), np.log(pmv + 1e-12)], stv, szv, va.kazandi.values == 1)
    print(f"alpha={a:+.3f} gamma={g:+.3f}")

    # --- exacta takeout (t): (1-t) ~ mean[ real_div * kalabalik_Harville(kazanan) ] (<=2024) ---
    def iter_races(df):
        st, sz, _ = rstruct(df)
        for i in range(len(st)):
            sl = slice(st[i], st[i] + sz[i])
            yield df.iloc[sl]

    def crowd_win_prob(sub):
        pm = devig(sub.ganyan_muhtemel.values, np.array([0]), np.array([len(sub)]))
        M = harville_pairs(pm)
        no = sub.no.values
        try:
            i = np.where(sub.sonuc.values == 1)[0][0]
            j = np.where(sub.sonuc.values == 2)[0][0]
        except IndexError:
            return None
        return M[i, j], sub.exacta_div.values[0]

    vals = []
    for sub in iter_races(va):
        r = crowd_win_prob(sub)
        if r and np.isfinite(r[1]):
            vals.append(r[0] * r[1])
    one_minus_t = np.median(vals)
    print(f"exacta efektif (1-t) medyan ~ {one_minus_t:.3f}  => takeout ~%{(1-one_minus_t)*100:.0f}")

    # --- TEST backtest ---
    pft, pmt, stt, szt = probs(te)
    te = te.copy()
    te["pf"], te["pm"] = pft, pmt
    sc = a * np.log(pft + 1e-12) + g * np.log(pmt + 1e-12)
    te["pc"] = softmax(sc, stt, szt)

    def backtest(thr):
        tot_cost = tot_pay = nbet = nwin = 0
        for sub in iter_races(te):
            div = sub.exacta_div.values[0]
            if not np.isfinite(div):
                continue
            pc = sub.pc.values
            pm = sub.pm.values
            Mmy = harville_pairs(pc)
            Mcr = harville_pairs(pm)
            estdiv = one_minus_t / np.clip(Mcr, 1e-9, None)
            EV = Mmy * estdiv
            sel = EV > thr
            n = int(sel.sum())
            if n == 0:
                continue
            tot_cost += n
            nbet += n
            i = np.where(sub.sonuc.values == 1)[0]
            j = np.where(sub.sonuc.values == 2)[0]
            if len(i) and len(j) and sel[i[0], j[0]]:
                tot_pay += div
                nwin += 1
        roi = (tot_pay - tot_cost) / tot_cost * 100 if tot_cost else float("nan")
        return nbet, nwin, roi

    print("\nTEST exacta backtest (secim=kamu-Harville EV, odeme=gercek temettu):")
    print(f"  {'EV>':6s} {'bahis':>8s} {'tutan':>7s} {'ROI%':>8s}")
    for thr in [1.0, 1.2, 1.5, 2.0, 3.0]:
        nb, nw, roi = backtest(thr)
        print(f"  {thr:6.1f} {nb:>8d} {nw:>7d} {roi:>+8.1f}")


if __name__ == "__main__":
    main()
