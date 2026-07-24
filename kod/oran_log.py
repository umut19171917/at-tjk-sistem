"""
oran_log.py — K59: gun-ici ORAN gecmisi kaydi (ILERI-YONLU; fiyat-kaymasi olcumu icin).

SISTEME DOKUNMAZ: kupon KURMAZ, model CALISTIRMAZ, mevcut HICBIR dosyaya yazmaz. Yalnizca
veri/altili_oran_log.csv'ye, her takip gecisinde, postaya <=45 dk kalan (ve baslamamis) her
Altili ayaginin canli oranlarini (GANYAN + AGF1) zaman damgasiyla EKLER. Cikan (KOSMAZ) atlar da
`kosmaz` bayragiyla loglanir (cikma bir piyasa olayi; oran None olabilir).

NEDEN: asil kuponlar 30 dk kala kuruluyor (degismiyor); ama oranlar posta anina kadar kayiyor
(23.07 Ankara-2'de 6 kazanandan 3'u kaymisti). "30 yerine 15/5 dk kala kursaydik secim/isabet
degisir miydi" sorusu backtest'le OLCULEMEZ cunku arsiv gun-ici oran serisi tutmuyor. Bu modul
o seriyi ILERIYE donuk biriktirir; birkac ay sonra offline analizle karar GERCEK veriyle verilir.

Takip.py her geciste try-korumali cagirir -> hatasi takibi ASLA bozmaz (paper/altili hook'u gibi).
Elle:  python oran_log.py [--pist ISTANBUL ...] [--tarih YYYY-MM-DD]
"""
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_canli import altili_pencereleri, _as_int  # noqa: E402
from gunluk import getjson, BASE  # noqa: E402
from duzlestir import vir_float  # noqa: E402

LOG = KOK / "veri" / "altili_oran_log.csv"
KOL = ["kayit_ts", "tarih", "pist", "seq", "ayak", "kosu_no", "race_kod",
       "saat", "dk_kala", "no", "at_ad", "ganyan", "agf1", "kosmaz"]
PENCERE_DK = 45   # sadece postaya <=45 dk kalan ayaklari logla (dosya sismesin; drift penceresi)


def oran_kaydet(pistler, ymd, tarih):
    """Postaya <=45 dk kalan her Altili ayaginin canli oranlarini bir snapshot olarak log'a ekle.
    Doner: eklenen satir sayisi. HATA FIRLATMAZ (takip guvenligi)."""
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M")
    yeni = []
    for pist in pistler:
        try:
            o = getjson(f"{BASE}/program/{ymd}/full/{pist}.json")
            if o.get("_hata"):
                continue
            for seq, pencere, _ilk in altili_pencereleri(o):
                for ai, k in enumerate(pencere):
                    saat = str(k.get("SAAT", "")).strip()
                    try:
                        post = datetime.strptime(f"{tarih} {saat}", "%Y-%m-%d %H:%M")
                    except ValueError:
                        continue
                    dk = (post - now).total_seconds() / 60.0
                    if not (0 <= dk <= PENCERE_DK):        # baslamamis + son 45 dk
                        continue
                    rk = _as_int(k.get("KOD"))
                    kno = _as_int(k.get("RACENO") or k.get("NO"))
                    for a in k.get("atlar", []):
                        # K59+: cikan (KOSMAZ) at da bir PIYASA OLAYI (havuz dagilir, oranlar ziplar)
                        # -> atmiyoruz; bayrakla logluyoruz. Cikan atin orani None olabilir (normal).
                        kosmaz = 1 if str(a.get("KOSMAZ", "")).strip().lower() in ("true", "1") else 0
                        yeni.append({
                            "kayit_ts": ts, "tarih": tarih, "pist": pist, "seq": seq,
                            "ayak": ai + 1, "kosu_no": kno, "race_kod": rk, "saat": saat,
                            "dk_kala": round(dk, 1), "no": _as_int(a.get("NO")),
                            "at_ad": a.get("AD"),
                            "ganyan": vir_float(a.get("GANYAN")),
                            "agf1": vir_float(a.get("AGF1")),
                            "kosmaz": kosmaz,
                        })
        except Exception as e:
            print(f"  oran_log ({pist}): {type(e).__name__} - devam")
    if not yeni:
        return 0
    df = pd.DataFrame(yeni, columns=KOL)
    if LOG.exists():
        df = pd.concat([pd.read_csv(LOG), df], ignore_index=True)
    # ayni (race_kod,no,kayit_ts) tekrarini sil (bir gecis iki kez calisirsa)
    df = df.drop_duplicates(["race_kod", "no", "kayit_ts"], keep="last")
    LOG.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(LOG, index=False, encoding="utf-8", columns=KOL)
    return len(yeni)


if __name__ == "__main__":
    import argparse
    from datetime import date
    ap = argparse.ArgumentParser()
    ap.add_argument("--pist", nargs="*")
    ap.add_argument("--tarih", default=date.today().isoformat())
    a = ap.parse_args()
    ymd = a.tarih.replace("-", "")
    pistler = a.pist
    if not pistler:
        from gunluk import yerli_pistler
        pistler, _ = yerli_pistler(ymd, hata_bildir=True)
    n = oran_kaydet(pistler, ymd, a.tarih)
    print(f"oran_log: {n} satir eklendi -> {LOG}")
