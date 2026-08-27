"""
altili_olasilik.py — Altili backtest'i icin TUM kosularin (Ingiliz + Arap) walk-forward Bot2
olasiligini uretir (K52). Cikti: veri/altili_olasilik.csv (race_kod, no, at_kod, bot2, kamu, kazandi).

WALK-FORWARD (sizinti yok): her irk icin ayri model.
  Bot1 (oran-kor conditional logit) egit <=2023; Bot2 harman agirligi (alpha,gamma) 2024;
  TEST kosulari (>=2025) bu sabit modelle puanlanir. 2021-2024 kosulari da (backtest tarihsel
  butunlugu icin) ayni <=2023-egitimli modelle puanlanir -- ama backtest ANALIZI 2025-26'ya
  odaklanacak (gercek OOS). Uretim modeliyle (gunluk.py alpha=+0.24/+0.18) tutarli.

ozellik.build_features K46'dan beri irk-farkindalikli kulvar uretir -> Ingiliz + Arap tek gecis.
Kapsam: Ingiliz + Arap, izinli pist (EXCL haric). Diger irk puanlanmaz (Altili'da ~%0, olcum).
YEREL, TOKEN=0.
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from ozellik import load_katilim, build_features, select_scope, FEAT, EXCL  # noqa: E402
from model import race_struct, seg_softmax, fit_clogit, devig  # noqa: E402


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
def irk_model(f):
    """f = tek irkin select_scope ciktisi (yil sutunlu). Doner: race_kod->(no,at_kod,bot2,kamu,kazandi)."""
    for c in FEAT:
        f[c] = pd.to_numeric(f[c], errors="coerce").fillna(0.0)
    f = f[f["ganyan_muhtemel"] > 1].copy()

    tr = f[f.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
    beta = fit_clogit(tr[FEAT].values, *race_struct(tr))

    va = f[f.yil == 2024].copy()
    gw = va.groupby("race_kod")["kazandi"].transform("sum")
    sz = va.groupby("race_kod")["race_kod"].transform("size")
    va = va[(gw == 1) & (sz >= 4)].sort_values("race_kod").reset_index(drop=True)
    stv, szv, winv = race_struct(va)
    pfv = seg_softmax(va[FEAT].values @ beta, stv, szv)
    pmv = devig(va.ganyan_muhtemel.values, stv, szv)
    alpha, gamma = fit_clogit(np.c_[np.log(pfv + 1e-12), np.log(pmv + 1e-12)], stv, szv, winv)

    # TUM kosulari puanla (kosu-ici; her yaris ayri softmax)
    out = []
    for rk, g in f.groupby("race_kod", sort=False):
        g = g.sort_values("no")
        st = np.array([0]); szc = np.array([len(g)])
        pf = seg_softmax(g[FEAT].values @ beta, st, szc)
        pm = devig(g["ganyan_muhtemel"].values, st, szc)
        b2 = seg_softmax(alpha * np.log(pf + 1e-12) + gamma * np.log(pm + 1e-12), st, szc)
        out.append(pd.DataFrame({"race_kod": rk, "no": g["no"].values, "at_kod": g["at_kod"].values,
                                 "bot2": b2, "kamu": pm, "kazandi": g["kazandi"].values}))
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame(), (alpha, gamma)


def main():
    d = load_katilim()
    d = build_features(d)
    d["yil"] = d["dt"].dt.year

    parcalar = []
    for irk in ("Ingiliz", "Arap"):
        f = select_scope(d, irk=irk)
        f["yil"] = pd.to_datetime(f["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
        res, (a, g) = irk_model(f)
        res["irk"] = irk
        parcalar.append(res)
        print(f"{irk}: {res['race_kod'].nunique()} kosu puanlandi | alpha={a:+.3f} gamma={g:+.3f}")

    allp = pd.concat(parcalar, ignore_index=True)
    allp.to_csv(KOK / "veri" / "altili_olasilik.csv", index=False, encoding="utf-8")
    print(f"\ntoplam: {allp['race_kod'].nunique()} kosu / {len(allp)} at-satiri -> altili_olasilik.csv")


if __name__ == "__main__":
    main()
