"""Faz 1 kapsam olcumu: Ingiliz + izinli pist, yil bazinda."""
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA"}

d = pd.read_csv(KOK / "veri" / "katilim.csv", low_memory=False)
f = d[(d.irk == "Ingiliz") & (~d.sehir.isin(EXCL))].copy()
f["yil"] = pd.to_datetime(f.tarih, format="%d/%m/%Y", errors="coerce").dt.year

print("Ingiliz + izinli pist (Faz 1 kapsami):")
print("  kosu:", f.race_kod.nunique(), "| at-satiri:", len(f))
print("  ort at/kosu:", round(len(f) / f.race_kod.nunique(), 1))
print("  ganyan_kapanis dolu: %.1f%%" % (f.ganyan_kapanis.notna().mean() * 100))
print("  benzersiz at:", f.at_kod.nunique(),
      "| jokey:", f.jokey_kod.nunique(), "| antrenor:", f.antrenor_kod.nunique())
print("yil bazinda kosu sayisi:")
print(f.groupby("yil").race_kod.nunique().to_string())
print("pist bazinda kosu (izinli):")
print(f.groupby("sehir").race_kod.nunique().sort_values(ascending=False).to_string())
