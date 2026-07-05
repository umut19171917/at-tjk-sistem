"""
plase_model.py — BENTER SON DOSYA (K44): sira-bilgili model (Plackett-Luce / exploded logit)
-> plase olasiliklari -> plase havuzunda overlay var mi? OFFLINE analiz; canli sisteme dokunmaz.

Tasarim (ON-TAAHHUTLU, kill-first):
  1) Egit <=2023: conditional logit'i sira-patlatmali fit et (k=1 kazanan; k=2 +ikinci; k=3 +ucuncu).
     Derinlik secimi 2024 holdout PLASE log-loss'una gore (bahis ROI'sine gore DEGIL — overfit yasak).
  2) KILL TESTI (test 2025-26, saha>=7): plase-top3 uyelik log-loss —
        p_model  (oran-kor PL)  vs  p_piyasa (devig ganyan -> Harville top-3)  vs  p_harman.
     Harman piyasayi anlamli gecmiyorsa -> DUR, dosya kapanir (ekonomi hesabina girilmez).
  3) IYIMSER TAVAN ekonomisi (yalniz kill gecilirse): temettu kestirimi log(D)~log(kapanis)+log(saha)
     (egitim yillari, plase alanlar) -> harman p x D_kestirim > esik -> GERCEK temettuyle ROI.
     Kapanis orani kullanilir = iyimser ust sinir (model.py konvansiyonu).

Veri: ozellikli.csv (mevcut uretim) + ham sonuclar BAHISLER_TR plase temettuleri (temettu.py).
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


# ----------------------------- sira-patlatma (exploded logit) -----------------------------
def patlat(df, k):
    """Kosulari k asamali pseudo-kosulara acar: asama s'de, s'den iyi bitirenler cikar,
    'kazanan' = s. bitiren. Ayni beta tum asamalarda (Plackett-Luce). DNF (sonuc NaN)
    atlar asamada kaybeden olarak kalir (yaristilar, o siraya giremediler)."""
    parcalar = []
    for s in range(1, k + 1):
        d = df[~(df["sonuc"] < s)].copy()          # sonuc<s cikar (NaN kalir)
        d["kazandi"] = (d["sonuc"] == s).astype(int)
        gw = d.groupby("race_kod")["kazandi"].transform("sum")
        sz = d.groupby("race_kod")["race_kod"].transform("size")
        d = d[(gw == 1) & (sz >= 2)]
        d["race_kod"] = d["race_kod"] * 10 + s      # pseudo-kosu kimligi
        parcalar.append(d)
    return pd.concat(parcalar, ignore_index=True).sort_values("race_kod").reset_index(drop=True)


def pl_top3(w):
    """Plackett-Luce guclerinden (w=exp(skor)) P(at ilk-3'te). O(n^2) vektorlu, kesin."""
    n = len(w)
    if n <= 3:
        return np.ones(n)
    W = w.sum()
    p1 = w / W
    P2 = np.outer(p1, w) / (W - w)[:, None]         # P2[a,b] = P(a birinci, b ikinci)
    np.fill_diagonal(P2, 0.0)
    ptop = P2.sum(1) + P2.sum(0)                    # i ilk-2'de
    Rem = W - w[:, None] - w[None, :]
    coef = P2 / Rem
    s_all, rowc, colc = coef.sum(), coef.sum(1), coef.sum(0)
    ptop += w * (s_all - rowc - colc)               # i ucuncu (i'li ciftler dislanir; kosegen=0)
    return ptop


def top3_probs(df, skor_col):
    """Kosu bazinda pl_top3; df sirali (race_kod). Doner: df ile hizali np.array."""
    out = np.empty(len(df))
    i = 0
    for _, g in df.groupby("race_kod", sort=False):
        w = np.exp(g[skor_col].values - g[skor_col].values.max())
        out[i:i + len(g)] = pl_top3(w)
        i += len(g)
    return out


def harville_top3(df, p_col):
    """Piyasa win-olasiligindan Harville top-3 (ayni PL formulu, w=p)."""
    out = np.empty(len(df))
    i = 0
    for _, g in df.groupby("race_kod", sort=False):
        out[i:i + len(g)] = pl_top3(g[p_col].values + 1e-12)
        i += len(g)
    return out


def bin_logloss(y, p):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())


# ----------------------------- ana akis -----------------------------
def main():
    d = pd.read_csv(KOK / "veri" / "ozellikli.csv", low_memory=False)
    d["yil"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    for c in FEAT:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0.0)
    print(f"veri: {d['race_kod'].nunique()} kosu, yillar {int(d.yil.min())}-{int(d.yil.max())}")

    tr = d[d.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
    va = prep(d[d.yil == 2024])
    te = prep(d[d.yil >= 2025])
    # plase kapsami: saha>=7 (havuz yalniz orada; plase_test olcumu)
    for isim, df in [("va", va), ("te", te)]:
        sz = df.groupby("race_kod")["race_kod"].transform("size")
        df["saha7"] = sz >= 7

    # ---- 1) derinlik secimi: k=1/2/3 fit (<=2023), 2024 plase log-loss ----
    betalar = {}
    print("\nDERINLIK SECIMI (egit<=2023, olcut 2024 plase-top3 log-loss, saha>=7):")
    va7 = va[va["saha7"]].sort_values("race_kod").reset_index(drop=True)
    y_va = (va7["sonuc"] <= 3).astype(int).values
    for k in (1, 2, 3):
        trk = patlat(tr, k)
        betalar[k] = fit_clogit(trk[FEAT].values, *race_struct(trk))
        va7[f"s{k}"] = va7[FEAT].values @ betalar[k]
        ll = bin_logloss(y_va, top3_probs(va7, f"s{k}"))
        print(f"  k={k}: plase log-loss {ll:.5f}")
        va7[f"ll{k}"] = ll
    k_sec = min((1, 2, 3), key=lambda k: bin_logloss(y_va, top3_probs(va7, f"s{k}")))
    beta = betalar[k_sec]
    print(f"  -> secilen derinlik: k={k_sec}")

    # ---- harman agirligi (2024, KAZANAN uzerinden — model.py ile ayni yontem) ----
    stv, szv, winv = race_struct(va)
    sv = va[FEAT].values @ beta
    pfv = seg_softmax(sv, stv, szv)
    pmv = devig(va.ganyan_muhtemel.values, stv, szv)
    alpha, gamma = fit_clogit(np.c_[np.log(pfv + 1e-12), np.log(pmv + 1e-12)], stv, szv, winv)
    print(f"  harman: ALPHA={alpha:+.3f} GAMMA={gamma:+.3f}")

    # ---- 2) KILL TESTI: test 2025-26 plase log-loss (saha>=7) ----
    te = te.sort_values("race_kod").reset_index(drop=True)
    stt, szt, _ = race_struct(te)
    s_mod = te[FEAT].values @ beta
    p_win_m = seg_softmax(s_mod, stt, szt)
    p_win_p = devig(te.ganyan_muhtemel.values, stt, szt)
    s_harman = alpha * np.log(p_win_m + 1e-12) + gamma * np.log(p_win_p + 1e-12)
    te["s_mod"], te["p_piy"], te["s_har"] = s_mod, p_win_p, s_harman

    t7 = te[te["saha7"]].sort_values("race_kod").reset_index(drop=True)
    y = (t7["sonuc"] <= 3).astype(int).values
    p_model = top3_probs(t7, "s_mod")
    p_piyasa = harville_top3(t7, "p_piy")
    p_harman = top3_probs(t7, "s_har")
    llm, llp, llh = bin_logloss(y, p_model), bin_logloss(y, p_piyasa), bin_logloss(y, p_harman)
    print(f"\nKILL TESTI — test 2025-26 plase-top3 log-loss ({t7['race_kod'].nunique()} kosu, saha>=7):")
    print(f"  piyasa(Harville) : {llp:.5f}")
    print(f"  model (oran-kor) : {llm:.5f}")
    print(f"  harman           : {llh:.5f}   (fark piyasaya gore {llh-llp:+.5f})")
    if llh >= llp - 1e-4:
        print("\n>>> VERDICT: harman plase'de piyasayi GECMIYOR -> DUR. Ekonomi hesabina girilmedi.")
        print(">>> Benter dosyasi kapandi: sira-bilgili model plase havuzuna da katki vermiyor.")
        return

    # ---- 3) IYIMSER TAVAN ekonomisi ----
    print("\nkill gecildi -> temettu tablosu + tavan ekonomisi...")
    ptab = {}
    for f in sorted(HAM.glob("*.json")):
        try:
            o = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for kk in o.get("kosular", []):
            try:
                ptab[int(kk.get("KOD"))] = gan_plase(kk.get("BAHISLER_TR"))[1]
            except (TypeError, ValueError):
                continue
    # temettu kestirimi (egitim yillari + 2024; plase ALAN atlar): log D ~ log kapanis + log saha
    eg = pd.concat([tr, va], ignore_index=True)
    sz = eg.groupby("race_kod")["race_kod"].transform("size")
    eg = eg[(sz >= 7) & eg["ganyan_kapanis"].notna()]
    X, yv = [], []
    for _, r in eg.iterrows():
        dv = ptab.get(int(r["race_kod"]), {}).get(int(r["no"]))
        if dv and dv > 1.0:
            X.append([1.0, np.log(r["ganyan_kapanis"]), np.log(r.get("alan", 8) if pd.notna(r.get("alan")) else 8)])
            yv.append(np.log(dv))
    X, yv = np.array(X), np.array(yv)
    coef, *_ = np.linalg.lstsq(X, yv, rcond=None)
    print(f"  D-kestirim katsayilari: {coef.round(3)}  (n={len(yv)})")

    t7 = t7.copy()
    t7["p_har3"] = p_harman
    alan7 = t7.groupby("race_kod")["race_kod"].transform("size")
    t7["d_hat"] = np.exp(coef[0] + coef[1] * np.log(t7["ganyan_kapanis"].clip(lower=1.01))
                         + coef[2] * np.log(alan7))
    t7["ev"] = t7["p_har3"] * t7["d_hat"]
    print(f"\nTAVAN EKONOMISI (kapanis oranli D-kestirimi, GERCEK temettuyle odeme; IYIMSER):")
    print(f"  {'esik EV>':>9s} {'bahis':>7s} {'isabet%':>8s} {'ROI%':>8s}")
    for thr in [1.00, 1.05, 1.10, 1.20]:
        sel = t7[t7["ev"] > thr]
        if len(sel) == 0:
            print(f"  {thr:>9.2f} {0:>7d}")
            continue
        rets, hit = [], 0
        for _, r in sel.iterrows():
            pl = ptab.get(int(r["race_kod"]), {})
            if not pl:
                continue                       # havuz yok -> iade, hesaba girmez
            g = pl.get(int(r["no"]), 0.0)
            rets.append(g - 1.0)
            hit += g > 0
        if rets:
            print(f"  {thr:>9.2f} {len(rets):>7d} {hit/len(rets)*100:>7.1f}% {np.mean(rets)*100:>+7.1f}%")


if __name__ == "__main__":
    main()
