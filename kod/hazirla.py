"""
hazirla.py — Faz 1a veri hazirlama.
Eldeki 3 aylik (2024-10..12) katilimlar tablosunu temizler, parse eder, race_id uretir,
izinli/yasakli pist isaretler ve IRK bilgisini atlar tablosundan (isim join) ekler.
Cikti: veri/temiz_katilim.csv  + konsola teshis.

JOIN NOTU: katilimlar<->yarislar pozisyon-join GUVENILMEZ (meeting kosu-sayisi eslesmesi
~%20). Bu yuzden mesafe/zemin yarislar'dan ALINMAZ. Irk, ata-ozgu sabit oldugu icin
atlar_real'dan isim eslesmesiyle alinir (saglam). Race-level meta (mesafe/zemin) modelleme
fazinda ebayi.tjk.org temiz JSON'undan gelecek.

Baz cizgi cekirdegi (kalibrasyon, favori-uzunsansli sapma, kesinti) yalnizca katilimlar'dan
(ganyan_orani + kazanan_mi) hesaplanir; irk sadece kirilim icin.
"""
import re
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
VERI = KOK / "veri"
EXCL = {"Adana", "Elazığ", "Diyarbakır", "Şanlıurfa"}


def parse_at_id(s):
    if not isinstance(s, str):
        return (None, None)
    m = re.search(r"\((\d+)\)", s)
    if m:
        return (s[:m.start()].strip(), int(m.group(1)))
    return (s.strip(), None)


def parse_kilo(s):
    if not isinstance(s, str):
        return (None, None, None)
    b = re.match(r"\s*([\d.]+)", s)
    base = float(b.group(1)) if b else None
    e = re.search(r"\+([\d.]+)", s)
    extra = float(e.group(1)) if e else 0.0
    total = (base + extra) if base is not None else None
    return (base, extra, total)


def parse_yas(s):
    if not isinstance(s, str):
        return (None, None, None)
    m = re.match(r"\s*(\d+)\s*y\s+(\S+)\s+(\S+)", s)
    if m:
        return (int(m.group(1)), m.group(2), m.group(3))
    a = re.match(r"\s*(\d+)\s*y", s)
    return (int(a.group(1)) if a else None, None, None)


def parse_derece(s):
    if not isinstance(s, str) or not s.strip():
        return None
    p = s.strip().split(".")
    try:
        if len(p) == 3:
            return int(p[0]) * 60 + int(p[1]) + int(p[2]) / 100.0
        if len(p) == 2:
            return int(p[0]) + int(p[1]) / 100.0
    except ValueError:
        return None
    return None


def main():
    kat = pd.read_csv(VERI / "katilimlar_real_2024.csv", dtype=str, encoding="utf-8")
    n0 = len(kat)

    kat["ganyan"] = pd.to_numeric(kat["ganyan_orani"], errors="coerce")
    kat["bitis"] = pd.to_numeric(kat["kosu_sira"], errors="coerce")
    kat["kazandi"] = pd.to_numeric(kat["kazanan_mi"], errors="coerce").fillna(0).astype(int)
    kat[["at_isim", "start_no"]] = kat["at_id"].apply(lambda s: pd.Series(parse_at_id(s)))
    kat[["kilo_baz", "kilo_fazla", "kilo_top"]] = kat["kilo"].apply(lambda s: pd.Series(parse_kilo(s)))
    kat[["yas", "renk", "cins"]] = kat["at_yas"].apply(lambda s: pd.Series(parse_yas(s)))
    kat["zaman_sn"] = kat["derece"].apply(parse_derece)

    kat["tarih_dt"] = pd.to_datetime(kat["tarih"], format="%d/%m/%Y", errors="coerce")
    kat["tarih_iso"] = kat["tarih_dt"].dt.strftime("%Y-%m-%d")
    kat["race_id"] = kat["tarih_iso"] + "|" + kat["sehir"] + "|" + kat["kosu_no"].astype(str)
    kat["izinli"] = ~kat["sehir"].isin(EXCL)

    # --- IRK: atlar tablosundan isim eslesmesi (saglam) ---
    atl = pd.read_csv(VERI / "atlar_real.csv", dtype=str, encoding="utf-8")
    atl["isim_norm"] = atl["AtIsmi"].str.strip().str.upper()
    irk_map = (atl.dropna(subset=["IrkAdi"])
                  .drop_duplicates("isim_norm")
                  .set_index("isim_norm")["IrkAdi"])
    kat["isim_norm"] = kat["at_isim"].str.strip().str.upper()
    ham = kat["isim_norm"].map(irk_map)
    kat["irk"] = ham.apply(lambda g: "Ingiliz" if isinstance(g, str) and "ngiliz" in g
                           else ("Arap" if isinstance(g, str) and "rap" in g else None))
    irk_match = kat["irk"].notna().mean()

    # --- yarislar pozisyon-join: SADECE teshis (guvenilmez oldugunu belgele) ---
    yar = pd.read_csv(VERI / "yarislar_real.csv", dtype=str, encoding="utf-8")
    yar["tarih_iso"] = pd.to_datetime(yar["tarih_dt"], errors="coerce").dt.strftime("%Y-%m-%d")
    yar["kosu_no_atanan"] = yar.groupby(["tarih_iso", "sehir"]).cumcount() + 1
    kk = kat.groupby(["tarih_iso", "sehir"])["kosu_no"].nunique()
    yy = yar.groupby(["tarih_iso", "sehir"])["kosu_no_atanan"].max()
    ortak = kk.index.intersection(yy.index)
    eslesme = (kk.loc[ortak] == yy.loc[ortak]).mean() if len(ortak) else 0.0

    # --- teshis ---
    print("=" * 60)
    print(f"katilimlar satir: {n0}")
    print(f"ganyan NaN: {kat['ganyan'].isna().sum()} ({kat['ganyan'].isna().mean()*100:.1f}%)  "
          f"start NaN: {kat['start_no'].isna().sum()}  kilo NaN: {kat['kilo_baz'].isna().sum()}  "
          f"yas NaN: {kat['yas'].isna().sum()}  zaman NaN: {kat['zaman_sn'].isna().sum()}")
    print("-" * 60)
    print(f"toplam kosu: {kat['race_id'].nunique()}")
    print(f"izinli pist katilim: {kat['izinli'].sum()} / {n0}   "
          f"izinli pist kosu: {kat.loc[kat['izinli'],'race_id'].nunique()}")
    print("-" * 60)
    print(f"IRK isim-eslesme orani (atlar): {irk_match*100:.1f}%")
    print("irk dagilimi:")
    print(kat["irk"].value_counts(dropna=False).to_string())
    print(f"izinli + Ingiliz kosu: {kat.loc[kat['izinli'] & (kat['irk']=='Ingiliz'),'race_id'].nunique()}")
    print(f"izinli + Arap kosu:    {kat.loc[kat['izinli'] & (kat['irk']=='Arap'),'race_id'].nunique()}")
    print("-" * 60)
    print(f"[teshis] yarislar pozisyon-join meeting eslesme: {eslesme*100:.1f}% "
          f"-> GUVENILMEZ, mesafe/zemin bu join'den ALINMADI")

    out = VERI / "temiz_katilim.csv"
    kat.to_csv(out, index=False, encoding="utf-8")
    print(f"yazildi: {out.name}  ({len(kat)} satir)")


if __name__ == "__main__":
    main()
