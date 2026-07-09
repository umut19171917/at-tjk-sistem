"""
arap_test.py — ARAP KARAR-DENEYI (K46): K19 protokolunun birebir aynisi, kapsam = Arap + izinli pist.
Soru: Arap havuzu (farkli piyasa segmenti; 7 negatif testin hepsi Ingiliz'deydi) daha mi az verimli?

Yontem (model.py ile ayni): Bot1 (oran-kor conditional logit, egit <=2023) + Bot2 (harman, 2024)
-> TEST 2025-26: ALPHA kill-kriteri, log-loss piyasa-karsilastirmasi, EV esik taramasi.
Fark: kulvar_skor tablosu ARAP kosularindan yeniden kurulur (uretimdeki tablo Ingiliz-bazli;
start/mesafe yanliligi irka gore farkli olabilir). Uretim dosyalarina DOKUNMAZ (offline).
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from ozellik import load_katilim, build_features, zscore_race, FEAT, ZCOLS, EXCL  # noqa: E402
from model import race_struct, seg_softmax, fit_clogit, devig, prep  # noqa: E402


def main():
    d = load_katilim()
    d = build_features(d)

    # ---- kulvar tablosunu ARAP'a gore yeniden kur (uretim tablosu Ingiliz-bazli) ----
    d = d.drop(columns=["kulvar_skor"])
    egit = d[(d["dt"].dt.year <= 2024) & (d["irk"] == "Arap") & (~d["sehir"].isin(EXCL))]
    kt = egit.groupby(["sehir", "mes_kova", "st_kova"], observed=True)["kazandi"].mean().rename("kulvar_skor")
    d = d.merge(kt, on=["sehir", "mes_kova", "st_kova"], how="left")

    # ---- kapsam: Arap + izinli pist, tek galipli, alan>=4 (select_scope'un Arap esi) ----
    f = d[(d["irk"] == "Arap") & (~d["sehir"].isin(EXCL))].copy()
    gw = f.groupby("race_kod")["kazandi"].transform("sum")
    f = f[(gw == 1) & (f["alan"] >= 4)].copy()
    f["disi"] = (f["cins"].astype(str).str.lower().str.startswith("k")).astype(int)
    for c in ZCOLS:
        f[c + "_z"] = zscore_race(f, c)
    f["ilk_kosu"] = (f["kariyer_kosu"] == 0).astype(int)
    f["yil"] = f["dt"].dt.year
    for c in FEAT:
        f[c] = pd.to_numeric(f[c], errors="coerce").fillna(0.0)

    print(f"ARAP kapsam: {f['race_kod'].nunique()} kosu / {len(f)} at-kosu | "
          f"ilk-kosu pay: %{f['ilk_kosu'].mean()*100:.1f} (Ingiliz ~%10-12 referans)")

    tr = f[f.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
    va = prep(f[f.yil == 2024])
    te = prep(f[f.yil >= 2025])
    print(f"egitim: {tr.race_kod.nunique()} | val(2024): {va.race_kod.nunique()} | "
          f"TEST(2025-26): {te.race_kod.nunique()} kosu")

    # ---- Bot1 ----
    beta = fit_clogit(tr[FEAT].values, *race_struct(tr))
    print("\nBot1 katsayilari (buyukluk = onem):")
    for ad, b in sorted(zip(FEAT, beta), key=lambda x: -abs(x[1])):
        print(f"  {ad:22s} {b:+.3f}")

    # ---- Bot2 (2024) ----
    stv, szv, winv = race_struct(va)
    pfv = seg_softmax(va[FEAT].values @ beta, stv, szv)
    pmv = devig(va.ganyan_muhtemel.values, stv, szv)
    alpha, gamma = fit_clogit(np.c_[np.log(pfv + 1e-12), np.log(pmv + 1e-12)], stv, szv, winv)
    print(f"\n>>> ALPHA (fundamental) = {alpha:+.3f}   GAMMA (piyasa) = {gamma:+.3f}")
    print("    (kill-kriter: ALPHA~0 -> fundamental katkisiz -> DUR)")

    # ---- TEST ----
    stt, szt, wint = race_struct(te)
    pf = seg_softmax(te[FEAT].values @ beta, stt, szt)
    pm = devig(te.ganyan_muhtemel.values, stt, szt)
    pc = seg_softmax(alpha * np.log(pf + 1e-12) + gamma * np.log(pm + 1e-12), stt, szt)

    def logloss(p):
        return float(-np.log(p[wint] + 1e-12).mean())

    print(f"\nTEST log-loss (dusuk iyi):")
    print(f"  piyasa(muhtemel) : {logloss(pm):.4f}")
    print(f"  Bot1 (fund)      : {logloss(pf):.4f}")
    print(f"  harman (Bot2)    : {logloss(pc):.4f}   (piyasaya fark {logloss(pc)-logloss(pm):+.4f})")

    # ---- kesinti (Arap havuzu Ingiliz'den farkli mi?) ----
    inv = te.groupby("race_kod")["ganyan_kapanis"].apply(lambda s: (1 / s).sum())
    print(f"\nArap ganyan overround medyan: {inv.median():.3f} (Ingiliz ~1.34 / ~%25.5 kesinti)")

    # ---- EV taramasi (kapanis, IYIMSER) ----
    odds = te.ganyan_kapanis.values
    ev = pc * odds
    print(f"\nTEST ROI (harman p x kapanis; IYIMSER ust sinir):")
    print(f"  {'esik EV>':8s} {'bahis':>7s} {'isabet%':>8s} {'ROI%':>8s}")
    for thr in [1.00, 1.05, 1.10, 1.20]:
        sel = ev > thr
        n = int(sel.sum())
        if n == 0:
            print(f"  {thr:8.2f} {0:>7d}")
            continue
        roi = (odds[sel] * wint[sel] - 1).mean()
        print(f"  {thr:8.2f} {n:>7d} {wint[sel].mean()*100:>7.1f}% {roi*100:>+7.1f}%")
    fav = te.loc[te.groupby("race_kod")["ganyan_kapanis"].idxmin()]
    print(f"  [referans] her kosuda favori: ROI {((fav.ganyan_kapanis*(fav.kazandi==1)-1).mean()*100):+.1f}%  (n={len(fav)})")


if __name__ == "__main__":
    main()
