"""
model.py — KARAR DENEYI: Bot1 (oran-kor conditional logit) + Bot2 (piyasayla harman) + ALPHA.
Walk-forward: egit 2021-2023, harman(Bot2) 2024, TEST 2025-2026 (cross-fit sizinti yok).

Cikti (asil sorular):
  - alpha: Bot2'nin fundamentale verdigi agirlik. ~0 => fundamental bir sey eklemiyor => DUR.
  - test log-loss: harman, piyasayi yeniyor mu?
  - test ROI (kapanis, IYIMSER): %25,5 kesintiyi asip pozitif mi?
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import minimize

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from ozellik import FEAT  # noqa: E402  tek kaynak (kopya drift olmasin)


# =============================================================================
# UYARI (K130, 27 Agu 2026) — `ganyan_muhtemel` BIR "MUHTEMEL ORAN" DEGILDIR
# -----------------------------------------------------------------------------
# Olculdu: katilim.csv'de ganyan_muhtemel == ganyan_kapanis, 6 yilin %100'unde
# (342.986 at-satiri, ort. mutlak fark 0,0007). Sebep: arsivdeki PROGRAM sayfalari
# kosudan SONRA cekilmis; duzlestir.py'nin program'dan okudugu GANYAN alani da
# kapanis oranini tasiyor. Ayni gun kontrolu: program GANYAN == sonuc GANYAN %99,1.
#
# BUNUN ANLAMI:
#   * CANLI AKIS ETKILENMIYOR — altili_canli.py / gunluk.py oranlari oran_log'tan
#     GERCEK ZAMANLI okur (dk_kala damgali). Canli kupon dogru fiyatla kurulur.
#   * BACKTEST'IN PIYASA TERIMI IYIMSER — kupon ayak 1'den once kurulur ama bu
#     sutun ayak 2-6'nin KAPANIS fiyatini tasir; o bilgi kupon aninda YOKTUR.
#   * alpha = 0,19'un anlami degisir: "bot1, KAPANIS fiyatinin ustune %19 katiyor".
#     Erken bir oranin ustune katmaktan cok daha zor bir sinav.
#
# GECMIS KARARLARI GECERSIZ KILMAZ: negatif sonuclar IYIMSER bir zeminde alinmisti;
# gercek zemin daha kotuyse negatifler DAHA DA guclenir. Risk yalnizca backtest'te
# ARTI gorunen hucrelerdedir — ve hicbiri zaten sifirdan ayrilamiyordu.
#
# Ayrinti: KARARLAR.md K130 · Secenekler: BEKLEYENLER.md #20
# =============================================================================
def race_struct(df):
    rc = df["race_kod"].values
    start = np.r_[0, np.where(rc[1:] != rc[:-1])[0] + 1]
    sizes = np.diff(np.r_[start, len(rc)])
    win = (df["kazandi"].values == 1)
    return start, sizes, win


def seg_softmax(s, start, sizes):
    smax = np.maximum.reduceat(s, start)
    e = np.exp(s - np.repeat(smax, sizes))
    den = np.add.reduceat(e, start)
    return e / np.repeat(den, sizes)


def fit_clogit(X, start, sizes, win):
    def negll(b):
        p = seg_softmax(X @ b, start, sizes)
        ll = np.log(p[win] + 1e-12).sum()
        grad = X[win].sum(0) - (X * p[:, None]).sum(0)
        return -ll, -grad
    r = minimize(negll, np.zeros(X.shape[1]), jac=True, method="L-BFGS-B")
    return r.x


def logloss(p, start, sizes, win):
    return float(-np.log(p[win] + 1e-12).mean())   # kosu basina ort. -log p(galip)


def devig(odds, start, sizes):
    inv = 1.0 / odds
    den = np.add.reduceat(inv, start)
    return inv / np.repeat(den, sizes)


def prep(df):
    """Tam-kapsamli (tum kosanlarda muhtemel+kapanis var) kosulara indir, sirala."""
    df = df.dropna(subset=["ganyan_muhtemel", "ganyan_kapanis"]).copy()
    df = df[(df.ganyan_muhtemel > 1) & (df.ganyan_kapanis > 1)]
    df = df.sort_values("race_kod")
    # tek galipli + >=4 atli kosular
    gw = df.groupby("race_kod")["kazandi"].transform("sum")
    sz = df.groupby("race_kod")["race_kod"].transform("size")
    df = df[(gw == 1) & (sz >= 4)].sort_values("race_kod").reset_index(drop=True)
    return df


def main():
    d = pd.read_csv(KOK / "veri" / "ozellikli.csv", low_memory=False)
    d["yil"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    for c in FEAT:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0.0)

    tr = d[d.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
    va = prep(d[d.yil == 2024])
    te = prep(d[d.yil >= 2025])
    print(f"egitim kosu: {tr.race_kod.nunique()} | val(2024): {va.race_kod.nunique()} | "
          f"test(2025-26): {te.race_kod.nunique()}")

    # ----- BOT 1: oran-kor conditional logit (egitim) -----
    s_tr = race_struct(tr)
    beta = fit_clogit(tr[FEAT].values, *s_tr)
    print("\nBot1 katsayilari (buyukluk = onem):")
    for f, b in sorted(zip(FEAT, beta), key=lambda x: -abs(x[1])):
        print(f"  {f:22s} {b:+.3f}")

    def pfund(df):
        st, sz, _ = race_struct(df)
        return seg_softmax(df[FEAT].values @ beta, st, sz), (st, sz)

    # ----- BOT 2: harman (val 2024 uzerinde) -----
    pf_va, (stv, szv) = pfund(va)
    pm_va = devig(va.ganyan_muhtemel.values, stv, szv)
    X2 = np.c_[np.log(pf_va + 1e-12), np.log(pm_va + 1e-12)]
    a_g = fit_clogit(X2, stv, szv, va.kazandi.values == 1)
    alpha, gamma = a_g
    print(f"\n>>> ALPHA (fundamental agirligi) = {alpha:+.3f}   GAMMA (piyasa) = {gamma:+.3f}")

    # ----- TEST (2025-26): log-loss + ROI -----
    pf_te, (stt, szt) = pfund(te)
    pm_te = devig(te.ganyan_muhtemel.values, stt, szt)
    win_te = te.kazandi.values == 1
    s_comb = alpha * np.log(pf_te + 1e-12) + gamma * np.log(pm_te + 1e-12)
    pc_te = seg_softmax(s_comb, stt, szt)

    print("\nTEST log-loss (kosu basina -log p(galip), DUSUK iyi):")
    print(f"  piyasa(muhtemel) : {logloss(pm_te, stt, szt, win_te):.4f}")
    print(f"  Bot1 (fund)      : {logloss(pf_te, stt, szt, win_te):.4f}")
    print(f"  harman (Bot2)    : {logloss(pc_te, stt, szt, win_te):.4f}")
    print(f"  (referans: tek-favori sabit ~ {np.log(te.groupby('race_kod').size().mean()):.4f})")

    # ----- ROI: deger bahsi (kapanis oraniyla, IYIMSER ust sinir) -----
    odds = te.ganyan_kapanis.values
    ev = pc_te * odds
    print("\nTEST ROI (combined p x kapanis oran; IYIMSER, gercek daha kotu):")
    print(f"  {'esik EV>':8s} {'bahis':>7s} {'isabet%':>8s} {'ROI%':>8s}")
    for thr in [1.00, 1.05, 1.10, 1.20]:
        sel = ev > thr
        n = int(sel.sum())
        if n == 0:
            print(f"  {thr:8.2f} {0:>7d}")
            continue
        roi = (odds[sel] * win_te[sel] - 1).mean()
        hit = win_te[sel].mean()
        print(f"  {thr:8.2f} {n:>7d} {hit*100:>7.1f}% {roi*100:>+7.1f}%")
    # piyasa-favori referans ROI (her kosuda en dusuk oran)
    fav = te.loc[te.groupby("race_kod")["ganyan_kapanis"].idxmin()]
    print(f"  [referans] her kosuda favori oyna ROI: "
          f"{((fav.ganyan_kapanis*(fav.kazandi==1)-1).mean()*100):+.1f}%  (n={len(fav)})")


if __name__ == "__main__":
    main()
