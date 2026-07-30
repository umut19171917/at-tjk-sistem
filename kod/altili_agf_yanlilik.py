"""
altili_agf_yanlilik.py — "ALTILI HAVUZUNDAKI FAVORI YANLILIGININ HARITASI" (K74 adayi).
OFFLINE, SALT-OKUNUR: hicbir dosyaya yazmaz, canliya dokunmaz.

NEREDEN GELDI: K72 -> secimimiz kalabaligi yenmiyor ama rastgeleyi eziyor. K73 -> Altili kesintisi
~%49; buna ragmen favori-agirlikli oynamak havuz ortalamasini ~30 PUAN yeniyor. Yani Altili
havuzunda GUCLU bir favori-longshot yanliligi var ve sistemimiz ondan KAZARA faydalaniyor
(bot2 zaten kamuya yakin oldugu icin). Hic sorulmamis soru: **yanlilik tam olarak NEREDE?**

VERI — AGF (Agirlikli Ganyan Favorisi): ham sonuc feed'indeki `agf` blogu, her Altili ayaginda
her ata ALTILI HAVUZUNUN yuzde kacinin geldigini verir. Bu, kalabaligin o ayak icin bicaigi
olasiliktir. Yaninda gercek kazanani da biliyoruz -> DOGRUDAN kalibrasyon yapilabilir.

OLCUM:
  1) AGF payi kovalarina gore GERCEK kazanma orani. Etkin havuzda ikisi ESIT olmali.
     Oran = gercek/AGF  ->  >1 ise o kova UCUZ (az para gelmis), <1 ise PAHALI (fazla para).
  2) Ayni atlar icin GANYAN havuzunun olasiligi (kamu, de-vig) ile kiyas: hangi havuz daha iyi
     kalibre? Altili havuzu ganyandan DAHA yanliysa, "ganyan bilgisiyle Altili oynamak" bir
     kenar demektir -- bizim 30 puanimizin kaynagi bu olabilir.
  3) Yanliligin en guclu oldugu yer: saha buyuklugu, ayak sirasi, favori sirasi kirilimlari.

UYARI: Bulunan yanlilik KESINTIDEN sonra karliliga cevrilmek zorunda degil. K73'e gore ~%49
kesinti var; bir kovada oran 1,20 bile olsa net getiri 1,20 x 0,51 = %61 -> hala kayip.
Karli olmasi icin oran > ~1,96 gerekir. Bu esik raporda ACIKCA gosterilir.
"""
import glob
import json
import re
import sys
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))

GERI_DONUS = 0.514      # K73: Altili havuzunun ima edilen geri donusu (1 - kesinti), medyan
BASABAS_ORAN = 1.0 / GERI_DONUS


def _f(x):
    try:
        return float(str(x).replace(".", "").replace(",", "."))
    except Exception:
        return np.nan


def agf_topla():
    """Ham sonuc feed'inden (race_kod, at_no, agf_pay, kazandi, ayak_sira, saha) tablosu."""
    sat = []
    for f in sorted(glob.glob(str(KOK / "veri" / "ham" / "sonuclar" / "*.json"))):
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        no2kod, kazanan = {}, {}
        for k in j.get("kosular", []):
            no2kod[str(k.get("NO"))] = k.get("KOD")
            for a in k.get("atlar", []):
                if str(a.get("SONUC", "")).strip() == "1":
                    kazanan[str(k.get("NO"))] = str(a.get("NO"))
        for blok in j.get("agf", []):
            for ai, ay in enumerate(blok.get("kosular", [])):
                no = str(ay.get("NO"))
                rk, kn = no2kod.get(no), kazanan.get(no)
                atlar = ay.get("atlar", [])
                if rk is None or kn is None or len(atlar) < 4:
                    continue
                pay = np.array([_f(a.get("AGFORAN")) for a in atlar], float)
                if not np.isfinite(pay).all() or pay.sum() <= 0:
                    continue
                pay = pay / pay.sum()
                sira = np.argsort(-pay)
                rank = np.empty(len(pay), int)
                rank[sira] = np.arange(1, len(pay) + 1)
                for i, a in enumerate(atlar):
                    sat.append({"race_kod": int(rk), "no": int(a.get("NO")),
                                "agf": float(pay[i]), "agf_sira": int(rank[i]),
                                "kazandi": int(str(a.get("NO")) == kn),
                                "ayak": ai + 1, "saha": len(atlar)})
    return pd.DataFrame(sat)


def kalibrasyon(d, alan, kovalar, baslik):
    print(f"\n### {baslik} ###")
    print(f"{'kova':>14} {'at':>7} {'ort. ' + alan:>10} {'GERCEK':>8} {'oran':>7} "
          f"{'net getiri':>11}  durum")
    d = d.copy()
    d["kova"] = pd.cut(d[alan], kovalar)
    for kv, g in d.groupby("kova", observed=True):
        if len(g) < 60:
            continue
        bek, ger = g[alan].mean(), g["kazandi"].mean()
        oran = ger / bek if bek > 0 else np.nan
        net = oran * GERI_DONUS
        durum = "KARLI" if net > 1 else ("ucuz" if oran > 1.03 else
                                         ("pahali" if oran < 0.97 else "adil"))
        print(f"{str(kv):>14} {len(g):>7,} {bek:>10.4f} {ger:>8.4f} {oran:>7.2f} "
              f"{net:>10.2f}x  {durum}")


def main():
    print("AGF verisi toplaniyor (ham feed)...")
    d = agf_topla()
    if d.empty:
        print("AGF bulunamadi."); return
    print(f"  {len(d):,} at-satiri | {d.race_kod.nunique():,} kosu")

    # ganyan (de-vig) olasiligini ekle -> iki havuzu kiyasla
    p = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    d = d.merge(p[["race_kod", "no", "kamu", "bot1", "bot2"]], on=["race_kod", "no"], how="left")
    ok = d.dropna(subset=["kamu"])
    print(f"  ganyan olasiligi eslesen: {len(ok):,}")

    print("\n" + "=" * 96)
    print("ALTILI HAVUZU FAVORI YANLILIGI HARITASI")
    print(f"K73: Altili geri donusu ~%{100*GERI_DONUS:.0f} -> bir kovanin KARLI olmasi icin")
    print(f"     oran (gercek/AGF) > {BASABAS_ORAN:.2f} olmali. 'net getiri' = oran x {GERI_DONUS:.3f}")
    print("=" * 96)

    kv = [0, .02, .05, .10, .15, .20, .30, .45, 1.0]
    kalibrasyon(d, "agf", kv, "1) ALTILI havuzu — AGF payina gore kalibrasyon")
    kalibrasyon(ok, "kamu", kv, "2) GANYAN havuzu — ayni atlar, de-vig oran olasiligi")

    # 3) favori sirasina gore
    print("\n### 3) AGF sirasina gore (havuzun favori sirasi) ###")
    print(f"{'sira':>5} {'at':>8} {'ort.AGF':>9} {'GERCEK':>8} {'oran':>7} {'net':>7}")
    for s, g in d[d.agf_sira <= 8].groupby("agf_sira"):
        bek, ger = g.agf.mean(), g.kazandi.mean()
        print(f"{s:>5} {len(g):>8,} {bek:>9.4f} {ger:>8.4f} {ger/bek:>7.2f} {ger/bek*GERI_DONUS:>6.2f}x")

    # 4) iki havuz dogrudan kiyas: hangisi daha iyi kestiriyor?
    print("\n### 4) HANGI HAVUZ DAHA IYI KESTIRIYOR? (dusuk = iyi) ###")
    for ad, alan in (("Altili (AGF)", "agf"), ("Ganyan (kamu)", "kamu"), ("Bot2", "bot2")):
        if alan not in ok:
            continue
        v = ok[alan].values
        y = ok["kazandi"].values
        brier = np.mean((v - y) ** 2)
        ll = -np.mean(y * np.log(np.clip(v, 1e-9, 1)) + (1 - y) * np.log(np.clip(1 - v, 1e-9, 1)))
        print(f"  {ad:16s} Brier={brier:.5f}   log-kayip={ll:.5f}")

    # 5) AGF ile ganyan AYRISTIGINDA ne oluyor? (asil kenar adayi)
    print("\n### 5) AGF ile GANYAN ayristiginda (Altili havuzu ganyandan farkli fiyatliyorsa) ###")
    ok = ok.copy()
    ok["fark"] = ok["kamu"] - ok["agf"]        # + : ganyan daha cok sansliyor
    kvf = [-1, -.10, -.05, -.02, .02, .05, .10, 1]
    print(f"{'kamu-AGF':>14} {'at':>8} {'ort.AGF':>9} {'ort.kamu':>9} {'GERCEK':>8} "
          f"{'AGF orani':>10} {'net':>7}")
    ok["kv"] = pd.cut(ok["fark"], kvf)
    for kv2, g in ok.groupby("kv", observed=True):
        if len(g) < 60:
            continue
        ger = g.kazandi.mean()
        oran = ger / g.agf.mean() if g.agf.mean() > 0 else np.nan
        print(f"{str(kv2):>14} {len(g):>8,} {g.agf.mean():>9.4f} {g.kamu.mean():>9.4f} "
              f"{ger:>8.4f} {oran:>10.2f} {oran*GERI_DONUS:>6.2f}x")

    print("\n" + "=" * 96)
    print(f"OKUMA: 'net' sutunu 1,00'in USTUNDE olan kova = kesinti sonrasi KARLI (esik oran "
          f"{BASABAS_ORAN:.2f}).")
    print("Hicbiri gecmiyorsa yanlilik GERCEK ama kesintiyi asmaya YETMIYOR demektir.")
    print("=" * 96)


if __name__ == "__main__":
    main()
