"""
ozellik.py — Bot 1 cekirdek ozellik seti (NOKTA-ANINDA, look-ahead YOK; saha-goreli).
Girdi: veri/katilim.csv (tum veri). Cikti: veri/ozellikli.csv (Ingiliz + izinli pist).

ILKE: her per-at / baglanti ozelligi yalnizca o kosudan ONCEKI veriden hesaplanir.
  - shift(1) ile mevcut kosu daima haric.
  - jokey/antrenor: son 365 gun penceresi, mevcut kosu cikarilarak.
  - kulvar sapmasi ve par-zamani: track-fizik sabiti -> egitim yillarindan (<=2024) tablo.
Piyasa (ganyan/AGF) ozellik DEGIL -> sadece Bot 2'ye tasinir.

YAPI: load_katilim() -> build_features() -> select_scope() fonksiyonlarina ayrildi ki
  gunluk.py AYNI nokta-aninda mantigi yeniden kullanabilsin (tek kaynak; sizinti/ayrisma yok).
  main() ciktisi (ozellikli.csv) refaktor oncesiyle BIT-AYNI kalir.
"""
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA"}
K = 4  # form penceresi (son K kosu)

FEAT = ["hiz_son_ort_z", "hiz_en_iyi_z", "form_pos_z", "form_fark_z", "kilo_z",
        "handikap_z", "kariyer_galip_oran_z", "zemin_galip_oran_z", "jokey_isabet_z",
        "antrenor_isabet_z", "kulvar_skor_z", "son_yarisdan_gun_z", "yas_z", "disi", "ilk_kosu",
        "jokey_degisim", "taki_ilk"]  # Batch 1: jokey/techizat degisim (z'siz ikili).
# Test edilip EKLENMEYENLER (gurultu/esdogrusal; ozellik muhendisligi K33'te kapatildi):
#   - taki_kalkan (K32): kosullu katki ~0, kats. ham yone ters.
#   - going_uygunluk / mesafe_uygunluk (K33, Batch 2): going zemin_galip_oran ile esdogrusal,
#     mesafe kats ~0; ikisi de Bot1'i ~0 / Bot2'yi 0 oynatti.
ZCOLS = ["hiz_son_ort", "hiz_en_iyi", "form_pos", "form_fark", "kilo", "handikap",
         "kariyer_galip_oran", "zemin_galip_oran", "jokey_isabet", "antrenor_isabet",
         "kulvar_skor", "son_yarisdan_gun", "yas"]


def zscore_race(df, col):
    """Yaris ici z-skor (conditional logit icin saha-goreli)."""
    g = df.groupby("race_kod")[col]
    m, s = g.transform("mean"), g.transform("std")
    z = (df[col] - m) / s
    return z.fillna(0.0)  # tek-atli/std=0 -> notr


def load_katilim(path=None, df=None):
    """Ham katilim.csv -> tip donusumu + kosmayan ele + (dt,race_kod) sirali. alan eklenir.
    df verilirse CSV okumaz (gunluk.py: gecmis + bugunun canli satirlari birlesik gecirir)."""
    d = df.copy() if df is not None else pd.read_csv(path or (KOK / "veri" / "katilim.csv"), low_memory=False)
    d["dt"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce")
    for c in ["sonuc", "fark", "kilo", "handikap", "start", "yas", "zaman_sn",
              "ganyan_kapanis", "ganyan_muhtemel", "agf1", "mesafe"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["kosmaz_b"] = d["kosmaz"].astype(str).str.lower().isin(["true", "1"])
    d = d[~d["kosmaz_b"]].copy()                       # kosmayanlari at
    if "kazandi" not in d.columns:                     # canli/sonucsuz satirlar icin
        d["kazandi"] = (d["sonuc"] == 1).astype(int)
    d = d.sort_values(["dt", "race_kod"]).reset_index(drop=True)
    d["alan"] = d.groupby("race_kod")["at_kod"].transform("size")   # saha boyu
    return d


def build_features(d):
    """Ham nokta-aninda ozellikleri ekler (hiz, kariyer, form, jokey/antrenor, kulvar).
    Girdi sirasi: load_katilim ciktisi (dt,race_kod sirali). Ciktida ham ozellik sutunlari."""
    # ---------- HIZ FIGURU (par + gunluk varyant) ----------
    # par = track-fizik sabiti -> SADECE egitim yillari (<=2024); kulvar_skor ile ayni kural.
    # K38 DUZELTME: onceden TUM yillardan hesaplaniyordu (docstring ile celiski) -> 2025-26 test
    # doneminin galip zamanlari par'a, oradan hiz ozelliklerine siziyordu (olcum: 151 ortak
    # hucrede medyan |fark| 0.185 sn, p90 0.81 sn). gun_ofset per-gun kaliyor (o gun bitmis).
    win = d[(d["sonuc"] == 1) & (d["dt"].dt.year <= 2024)]
    par = win.groupby(["sehir", "zemin", "mesafe"])["zaman_sn"].median().rename("par")
    d = d.merge(par, on=["sehir", "zemin", "mesafe"], how="left")
    # gunluk track ofseti = o gun-pistteki galiplerin par'dan sapma ort.
    wd = d[d["sonuc"] == 1].copy()
    wd["sapma"] = wd["zaman_sn"] - wd["par"]
    ofset = wd.groupby(["dt", "sehir"])["sapma"].mean().rename("gun_ofset")
    d = d.merge(ofset, on=["dt", "sehir"], how="left")
    d["gun_ofset"] = d["gun_ofset"].fillna(0.0)
    # beklenen zaman = par + ofset ; hiz = beklenen - gercek (poz=hizli)
    d["hiz"] = (d["par"] + d["gun_ofset"]) - d["zaman_sn"]

    # ---------- PER-AT NOKTA-ANINDA (sirali: at_kod, dt) ----------
    d = d.sort_values(["at_kod", "dt", "race_kod"]).reset_index(drop=True)
    g = d.groupby("at_kod", sort=False)
    d["son_yarisdan_gun"] = (d["dt"] - g["dt"].shift(1)).dt.days
    d["kariyer_kosu"] = g.cumcount()                                   # onceki kosu sayisi
    d["kariyer_galip"] = g["kazandi"].cumsum() - d["kazandi"]          # onceki galibiyetler
    d["kariyer_galip_oran"] = d["kariyer_galip"] / d["kariyer_kosu"].replace(0, np.nan)
    # form: son K kosu (mevcut haric) ort. pozisyon ve fark
    d["form_pos"] = g["sonuc"].transform(lambda s: s.shift(1).rolling(K, min_periods=1).mean())
    d["form_fark"] = g["fark"].transform(lambda s: s.shift(1).rolling(K, min_periods=1).mean())
    # hiz: onceki kosulardan son-ort ve en-iyi
    d["hiz_son_ort"] = g["hiz"].transform(lambda s: s.shift(1).rolling(K, min_periods=1).mean())
    d["hiz_en_iyi"] = g["hiz"].transform(lambda s: s.shift(1).cummax())

    # ---------- DEGISIM SINYALLERI (onceki kosuya gore; ikili 0/1, nokta-aninda) ----------
    # jokey degisimi: bu kosudaki jokey atin onceki kosusundakinden farkli mi (ilk kosu -> 0)
    prev_jok = g["jokey_kod"].shift(1)
    d["jokey_degisim"] = ((d["jokey_kod"] != prev_jok) & prev_jok.notna()).astype(int)
    # taki (techizat) degisimi: bosluk-ayrilmis kod kumesi. Kod semantigini VARSAYMADAN:
    #   ilk-kez eklenen kod var mi (taki_ilk) / kaldirilan kod var mi (taki_kalkan).
    prev_taki = g["taki"].shift(1)

    def _kume(x):
        return set(str(x).split()) if pd.notna(x) and str(x).strip().lower() not in ("", "nan") else set()

    cur_s = d["taki"].map(_kume)
    prev_s = prev_taki.map(_kume)
    hp = prev_taki.notna().to_numpy()   # onceki kosu (ve taki kaydi) var mi -> yoksa degisim=0
    d["taki_ilk"] = [1 if h and (c - p) else 0 for c, p, h in zip(cur_s, prev_s, hp)]
    d["taki_kalkan"] = [1 if h and (p - c) else 0 for c, p, h in zip(cur_s, prev_s, hp)]

    # zemin uygunlugu: bu zeminde onceki galip orani
    gz = d.groupby(["at_kod", "zemin"], sort=False)
    d["zemin_kosu"] = gz.cumcount()
    d["zemin_galip"] = gz["kazandi"].cumsum() - d["kazandi"]
    d["zemin_galip_oran"] = d["zemin_galip"] / d["zemin_kosu"].replace(0, np.nan)

    # mes_kova: kulvar_skor'da kullanilir (per-at sirali iken burada hesaplanir; tek kaynak)
    d["mes_kova"] = pd.cut(d["mesafe"], [0, 1200, 1400, 1700, 2000, 9000],
                           labels=["<=1200", "1300-1400", "1500-1700", "1800-2000", "2000+"])
    # NOT (K33): Batch 2 = going/mesafe UYGUNLUK test edildi -> going_uygunluk zemin_galip_oran ile
    #   esdogrusal (agirligini boluyor, +0.073), mesafe_uygunluk kats ~0; ikisi de Bot1'i ~0,
    #   Bot2'yi 0 oynatti -> ozellik muhendisligi kapatildi, EKLENMEDI.

    # ---------- BAGLANTI: jokey/antrenor son 365 gun (mevcut haric) ----------
    def trailing_rate(df, kod):
        # orijinal index korunur; [kod,dt] sirali -> rolling ciktisi pozisyonel hizalanir
        s = df[[kod, "dt", "kazandi"]].copy()
        s = s[s[kod].notna()].sort_values([kod, "dt"], kind="mergesort")
        r = s.set_index("dt").groupby(kod)["kazandi"].rolling("365D")
        s["w"] = r.sum().to_numpy() - s["kazandi"].to_numpy()   # mevcut kosu haric
        s["c"] = r.count().to_numpy() - 1
        rate = s["w"] / s["c"].replace(0, np.nan)
        return rate.reindex(df.index)

    d["jokey_isabet"] = trailing_rate(d, "jokey_kod")
    d["antrenor_isabet"] = trailing_rate(d, "antrenor_kod")

    # ---------- KULVAR SAPMASI (egitim yillari <=2024'ten tablo) ----------
    # mes_kova yukarida (kosul uygunlugu blogunda) hesaplandi -> tek kaynak, burada tekrar yok
    # K46: tablo IRK-farkindalikli — her irkin kendi egitim kosularindan. Ingiliz satirlari
    # BIT-AYNI kalir (ayni egit kumesi, md5 ile dogrulandi); Arap kendi tablosunu alir
    # (start/mesafe yanliligi irka gore farkli); diger irk NaN -> z-skorda notr.
    d["st_kova"] = pd.cut(d["start"].fillna(0), [0, 3, 6, 9, 12, 99],
                          labels=["1-3", "4-6", "7-9", "10-12", "13+"])
    tablolar = []
    for irk in ("Ingiliz", "Arap"):
        egit = d[(d["dt"].dt.year <= 2024) & (d["irk"] == irk) & (~d["sehir"].isin(EXCL))]
        kt = egit.groupby(["sehir", "mes_kova", "st_kova"], observed=True)["kazandi"] \
                 .mean().rename("kulvar_skor").reset_index()
        kt["irk"] = irk
        tablolar.append(kt)
    d = d.merge(pd.concat(tablolar, ignore_index=True),
                on=["irk", "sehir", "mes_kova", "st_kova"], how="left")
    return d


def select_scope(d, irk="Ingiliz"):
    """Hedef kapsama (irk + izinli pist) indir + saha-goreli z-skor + ilk_kosu.
    d'de 'bugun'==1 sutunu varsa, O kosular tek-galip sarti ARANMADAN tutulur (canli/sonucsuz).
    K46: irk parametreli — varsayilan Ingiliz (eski davranis birebir); canli yol Arap'i ayri cagirir."""
    # ---------- HEDEF KAPSAM: irk + izinli pist, tek galipli kosu ----------
    m = (d["irk"] == irk) & (~d["sehir"].isin(EXCL))
    f = d[m].copy()
    gw = f.groupby("race_kod")["kazandi"].transform("sum")
    keep = (gw == 1) & (f["alan"] >= 4)
    if "bugun" in f.columns:                            # canli: sonuc yok -> tek-galip arama
        keep = keep | ((f["bugun"] == 1) & (f["alan"] >= 4))
    f = f[keep].copy()

    # ---------- SAHA-GORELI z-skorlar ----------
    f["disi"] = (f["cins"].astype(str).str.lower().str.startswith("k")).astype(int)  # kisrak
    for c in ZCOLS:
        f[c + "_z"] = zscore_race(f, c)
    f["ilk_kosu"] = (f["kariyer_kosu"] == 0).astype(int)
    return f


def main():
    d = load_katilim()
    d = build_features(d)
    f = select_scope(d)

    cik = KOK / "veri" / "ozellikli.csv"
    f.to_csv(cik, index=False, encoding="utf-8")

    # ---------- TESHIS ----------
    print("=" * 60)
    print(f"kapsam: {len(f)} at-satiri | {f['race_kod'].nunique()} kosu")
    print("ham ozellik dolu orani (%):")
    for c in ZCOLS:
        print(f"  {c:22s} {f[c].notna().mean()*100:5.1f}")
    print("-" * 60)
    print("SIZINTI/yon denetimi: ozellik z-skoru ile kazanma (galip vs kaybeden ort. z):")
    for c in ["hiz_son_ort_z", "hiz_en_iyi_z", "form_pos_z", "kariyer_galip_oran_z",
              "jokey_isabet_z", "antrenor_isabet_z", "kulvar_skor_z", "handikap_z"]:
        gz = f.loc[f["kazandi"] == 1, c].mean()
        kz = f.loc[f["kazandi"] == 0, c].mean()
        print(f"  {c:24s} galip={gz:+.3f}  kaybeden={kz:+.3f}  fark={gz-kz:+.3f}")
    print(f"yazildi: {cik.name}")


if __name__ == "__main__":
    main()
