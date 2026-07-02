"""
baz_cizgi.py — Faz 1a PIYASA BAZ CIZGISI (model YOK).
Soru: Izinli-pist ganyan havuzu ne kadar verimli? Kalabalik nerede hata yapiyor?
Yalnizca katilimlar gerekiyor: ganyan_orani + kazanan_mi + race_id.

Metrikler:
  1. Kesinti (overround'dan)
  2. Favori kazanma orani vs implied
  3. Kalibrasyon (implied olasilik kovalarinda tahmin vs gercek)
  4. Favori-uzunsansli sapma (oran bantlarinda ROI) -- favori mi, uzunsansli mi over/under bahis

UYARI: ROI 'kapanis oranina' gore = IYIMSER UST SINIR. Gercekte (a) bahsi daha erken koyarsin
(muhtemel != kapanis), (b) kendi bahsin havuzu kaydirir. Yani gercek ROI bundan KOTU olur.
"""
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
VERI = KOK / "veri"
RAP = KOK / "raporlar"
EXCL = {"Adana", "Elazığ", "Diyarbakır", "Şanlıurfa"}


def main():
    df = pd.read_csv(VERI / "temiz_katilim.csv", encoding="utf-8")
    df = df[~df["sehir"].isin(EXCL)].copy()
    df = df[df["ganyan"].notna() & (df["ganyan"] > 1.0)].copy()

    # race basina overround + de-vig olasilik
    df["imp_raw"] = 1.0 / df["ganyan"]
    over = df.groupby("race_id")["imp_raw"].transform("sum")
    df["overround"] = over
    df["p_norm"] = df["imp_raw"] / over
    df["n_runner"] = df.groupby("race_id")["race_id"].transform("size")

    # tam bir galipli ve >=4 atli kosular (temiz analiz)
    win_per_race = df.groupby("race_id")["kazandi"].transform("sum")
    df = df[(win_per_race == 1) & (df["n_runner"] >= 4)].copy()
    n_race = df["race_id"].nunique()
    n_row = len(df)

    rlines = []
    def pr(s=""):
        print(s); rlines.append(s) if False else rlines.append(s)
    rlines = []
    def emit(s=""):
        print(s); rlines.append(s)

    emit("# Faz 1a — Piyasa Baz Cizgisi (izinli pistler, 2024-10..12)")
    emit("")
    emit(f"Kosu: {n_race} | Kosan at-satiri: {n_row} | Ort. at/kosu: {n_row/n_race:.1f}")
    emit("")

    # 1) KESINTI
    ov = df.groupby("race_id")["overround"].first()
    take = 1 - 1/ov
    emit("## 1. Kesinti (takeout)")
    emit(f"- Overround medyan: {ov.median():.3f}  => kesinti medyan ~%{take.median()*100:.1f}")
    emit(f"- Overround ort.: {ov.mean():.3f}  | P25/P75: {ov.quantile(.25):.3f} / {ov.quantile(.75):.3f}")
    emit("")

    # 2) FAVORI
    idx_fav = df.groupby("race_id")["ganyan"].idxmin()
    fav = df.loc[idx_fav]
    fav_wr = fav["kazandi"].mean()
    fav_imp = fav["p_norm"].mean()
    fav_roi = (fav["ganyan"] * fav["kazandi"]).mean() - 1
    emit("## 2. Favori (en dusuk oran)")
    emit(f"- Favori kazanma orani: %{fav_wr*100:.1f}  (implied beklenti: %{fav_imp*100:.1f})")
    emit(f"- 'Her kosuda favoriyi oyna' ROI (kapanis, iyimser): %{fav_roi*100:+.1f}")
    emit(f"- Favori ort. oran: {fav['ganyan'].mean():.2f} | medyan: {fav['ganyan'].median():.2f}")
    emit("")

    # 3) KALIBRASYON (implied kovalar)
    emit("## 3. Kalibrasyon (de-vig implied olasilik kovalari)")
    emit("| kova p_norm | n | tahmin% | gercek% | fark |")
    emit("|---|---|---|---|---|")
    bins = [0, .05, .10, .15, .20, .30, .50, 1.0]
    df["kova"] = pd.cut(df["p_norm"], bins)
    for k, g in df.groupby("kova", observed=True):
        if len(g) == 0:
            continue
        emit(f"| {k} | {len(g)} | {g['p_norm'].mean()*100:.1f} | {g['kazandi'].mean()*100:.1f} | "
             f"{(g['kazandi'].mean()-g['p_norm'].mean())*100:+.1f} |")
    emit("")

    # 4) FAVORI-UZUNSANSLI SAPMA (oran bantlari + ROI)
    emit("## 4. Favori-uzunsansli sapma (oran bantlari)")
    emit("ROI = bu banttaki TUM atlari kapanis oraniyla oyna (iyimser ust sinir).")
    emit("| oran bandi | n | gercek kazanma% | ort.implied% | ROI(kapanis)% |")
    emit("|---|---|---|---|---|")
    obins = [1, 2, 3, 5, 8, 15, 30, 10000]
    olbl = ["1-2", "2-3", "3-5", "5-8", "8-15", "15-30", "30+"]
    df["oband"] = pd.cut(df["ganyan"], obins, labels=olbl)
    for k, g in df.groupby("oband", observed=True):
        if len(g) == 0:
            continue
        roi = (g["ganyan"] * g["kazandi"]).mean() - 1
        emit(f"| {k} | {len(g)} | {g['kazandi'].mean()*100:.1f} | {g['p_norm'].mean()*100:.1f} | "
             f"{roi*100:+.1f} |")
    emit("")
    emit("_Not: ROI kapanis oranina gore ve iyimser; gercek (erken bahis + price impact) daha kotu._")

    RAP.mkdir(exist_ok=True)
    (RAP / "faz1a-piyasa-baz-cizgisi.md").write_text("\n".join(rlines), encoding="utf-8")
    print("\n[yazildi] raporlar/faz1a-piyasa-baz-cizgisi.md")


if __name__ == "__main__":
    main()
