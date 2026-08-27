"""
duzlestir.py — ham full JSON'lari TEK zengin tabloya acar: veri/katilim.csv
Her satir = bir at-kosu. SONUC tabanli (kosan/biten koSular), PROGRAM'dan muhtemel oran +
AGF + handikap zenginlestirme. Stabil ID'ler sayesinde join sorunu YOK.

YEREL, token=0. Kazima bitince calistir:  python duzlestir.py
"""
import ast
import json
import re
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "veri" / "ham"
CIK = KOK / "veri" / "katilim.csv"

# Ayni pistin zaman icinde degisen KEY'lerini birlestir (full kazimada kazi_ozet'ten guncellenir)
SEHIR_MAP = {"DBAKIR": "DIYARBAKIR"}


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
def vir_float(s):
    """ '18,50' -> 18.5 ; '1.00' -> 1.0 ; '' -> None """
    if s is None:
        return None
    s = str(s).strip()
    if not s or s.lower() in ("false", "none"):
        return None
    s = s.replace(".", "").replace(",", ".") if ("," in s and "." in s) else s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def fark_boy(s):
    """ '2,5 Boy' -> 2.5 ; 'Burun'/'Kafa'/'Boyun' -> kucuk degerler ; '' -> None """
    if not s:
        return None
    s = str(s).strip()
    kucuk = {"Burun": 0.05, "Kafa": 0.2, "Boyun": 0.3, "Bas": 0.2, "Başaltı": 0.4}
    for k, v in kucuk.items():
        if s.startswith(k):
            return v
    m = re.match(r"([\d.,]+)", s)
    return vir_float(m.group(1)) if m else None


def zaman_sn(s):
    if not s:
        return None
    p = str(s).strip().split(".")
    try:
        if len(p) == 3:
            return int(p[0]) * 60 + int(p[1]) + int(p[2]) / 100.0
        if len(p) == 2:
            return int(p[0]) + int(p[1]) / 100.0
    except ValueError:
        return None
    return None


def parse_yas(s):
    if not isinstance(s, str):
        return (None, None, None)
    m = re.match(r"\s*(\d+)\s*y\s+(\S+)\s+(\S+)", s)
    if m:
        return (int(m.group(1)), m.group(2), m.group(3))
    a = re.match(r"\s*(\d+)\s*y", s or "")
    return (int(a.group(1)) if a else None, None, None)


def irk_of(grup_tr, grupkisa):
    g = (grup_tr or "") + " " + (grupkisa or "")
    if "rap" in g or g.strip().endswith("A"):
        return "Arap"
    if "ngiliz" in g or "I" in (grupkisa or ""):
        return "Ingiliz"
    return "diger"


def going_of(hava, active_class):
    if active_class == "sand" or "kum" in (active_class or ""):
        return (hava.get("KUM_TR", ""), hava.get("KUMPISTAGIRLIGI", ""))
    return (hava.get("CIM_TR", ""), hava.get("CIMPISTAGIRLIGI", ""))


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def program_index():
    """(race_kod, at_kod) -> pre-race alanlar (muhtemel oran, agf, handikap)."""
    idx = {}
    for f in (HAM / "program").glob("*.json"):
        o = load(f)
        if not o:
            continue
        for k in o.get("kosular", []):
            rk = k.get("KOD")
            for a in k.get("atlar", []):
                idx[(rk, a.get("KOD"))] = {
                    "ganyan_muhtemel": vir_float(a.get("GANYAN")),
                    "agf1_prog": vir_float(a.get("AGF1")),
                    "agfsira1_prog": a.get("AGFSIRA1"),
                    "handikap_prog": a.get("HANDIKAP"),
                }
    return idx


def main():
    prog = program_index()
    rows = []
    nfile = 0
    for f in sorted((HAM / "sonuclar").glob("*.json")):
        o = load(f)
        if not o:
            continue
        nfile += 1
        sehir = o.get("KEY", f.stem.split("_")[-1])
        sehir = SEHIR_MAP.get(sehir, sehir)
        hava = o.get("hava", {}) or {}
        for k in o.get("kosular", []):
            rk = k.get("KOD")
            ac = k.get("ActiveClass")
            going, going_ag = going_of(hava, ac)
            irk = irk_of(k.get("GRUP_TR"), k.get("GRUPKISA"))
            rmeta = {
                "race_kod": rk, "tarih": k.get("TARIH"), "sehir": sehir,
                "kosu_no": k.get("RACENO") or k.get("NO"), "saat": k.get("SAAT"),
                "mesafe": k.get("MESAFE"), "zemin": ac, "grup": k.get("GRUP_TR"),
                "grupkisa": k.get("GRUPKISA"), "irk": irk, "sinif": k.get("CINSDETAY_TR"),
                "cinsiyet": k.get("CINSIYET"), "going": going, "going_agirlik": going_ag,
                "hava": hava.get("HAVA_TR"), "sicaklik": hava.get("SICAKLIK"),
                "nem": hava.get("NEM"), "gece": hava.get("GECE"),
            }
            for a in k.get("atlar", []):
                yas, renk, cins = parse_yas(a.get("YAS"))
                pr = prog.get((rk, a.get("KOD")), {})
                rows.append({
                    **rmeta,
                    "at_kod": a.get("KOD"), "at_ad": a.get("AD"), "no": a.get("NO"),
                    "start": a.get("START"), "yas": yas, "renk": renk, "cins": cins,
                    "kilo": vir_float(a.get("KILO")), "fazla_kilo": vir_float(a.get("FAZLAKILO")),
                    "apranti_ind": vir_float(a.get("APRANTIKILOINDIRIMI")),
                    "handikap": a.get("HANDIKAP") or pr.get("handikap_prog"),
                    "jokey_kod": a.get("JOKEYKODU"), "jokey_ad": a.get("JOKEYADI"),
                    "antrenor_kod": a.get("ANTRENORKODU"), "sahip_kod": a.get("SAHIPKODU"),
                    "baba_kod": a.get("BABAKODU"), "anne_kod": a.get("ANNEKODU"),
                    "taki": a.get("TAKI"), "son6": a.get("SON6"),
                    "kosmaz": a.get("KOSMAZ"), "ekuri": a.get("EKURI"),
                    "at_eniyi": zaman_sn(a.get("ENIYIDERECE")),
                    # piyasa
                    "agf1": vir_float(a.get("AGF1")), "agfsira1": a.get("AGFSIRA1"),
                    "ganyan_kapanis": vir_float(a.get("GANYAN")),
                    "ganyan_muhtemel": pr.get("ganyan_muhtemel"),
                    # sonuc
                    "sonuc": pd.to_numeric(a.get("SONUC"), errors="coerce"),
                    "fark": fark_boy(a.get("FARK")), "zaman_sn": zaman_sn(a.get("DERECE")),
                })

    df = pd.DataFrame(rows)
    df["kazandi"] = (df["sonuc"] == 1).astype(int)
    df.to_csv(CIK, index=False, encoding="utf-8")

    # teshis
    print("=" * 60)
    print(f"sonuc dosyasi islenen: {nfile}")
    print(f"satir (at-kosu): {len(df)}  | kosu: {df['race_kod'].nunique()}")
    if len(df):
        td = pd.to_datetime(df["tarih"], format="%d/%m/%Y", errors="coerce")
        print(f"tarih araligi: {td.min():%Y-%m-%d} .. {td.max():%Y-%m-%d}")
        print(f"ganyan_kapanis dolu: {df['ganyan_kapanis'].notna().mean()*100:.1f}%  "
              f"ganyan_muhtemel dolu: {df['ganyan_muhtemel'].notna().mean()*100:.1f}%")
        print(f"handikap dolu: {df['handikap'].replace('', pd.NA).notna().mean()*100:.1f}%  "
              f"going dolu: {df['going'].replace('', pd.NA).notna().mean()*100:.1f}%")
        print("irk dagilimi:")
        print(df["irk"].value_counts(dropna=False).to_string())
        print(f"sehirler: {df['sehir'].nunique()} -> "
              + ", ".join(sorted(df['sehir'].unique())[:20]))
    print(f"yazildi: {CIK.name}")


if __name__ == "__main__":
    main()
