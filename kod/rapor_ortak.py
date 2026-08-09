"""
rapor_ortak.py — K55: RAPOR ZENGINLESTIRME (salt-okunur; sistemin veri toplama akisina DOKUNMAZ).
Kullanici istegi: her kuponda "bizim tahminimiz + sectigimiz atlarin SISTEM SIRASI + kazanan at +
kazananin SISTEM SIRASI + KAMU SIRASI + ganyan orani + kupon bedeli + odul" ve altta TOPLAM.

TASARIM: altili_kupon.csv / paper_kupon.csv / defter.csv DEGISMEZ. Zenginlestirme HTML uretim
aninda defter.csv'den JOIN ile yapilir (defter zaten her kosunun TUM atlarini bot1/bot2/kamu/oran/
model_rank ile tutuyor). Boylece takip/paper/altili otomasyonu bugunku haliyle calisir.

Eksik veri durusu: 21 Tem'de kaybedilen kosular (K54 oncesi) ve 20 Tem elle kurulan kuponlar
defter'de YOK -> o ayaklarda sistem sirasi "-" gosterilir (UYDURULMAZ); kazanan bilgisi yine de
sonuc feed'inden alinabilir.

BIRIM FIYAT (2026 tarifesi, 5 Ocak 2026'dan itibaren; kaynak: TJK/Yaris Dergisi):
  Istanbul, Ankara, Izmir, Adana, Bursa, Kocaeli, Antalya -> 1,25 TL
  Elazig, Sanliurfa, Diyarbakir (+yurtdisi)               -> 1,00 TL
  Asgari kupon bedeli: 20 TL (bilgi; dar kupon 16 kombo x 1,25 = 20 TL tam sinirda)
"""
import json
import re
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
DEFTER = KOK / "veri" / "defter.csv"
TEMETTU_CACHE = KOK / "veri" / "altili_temettu.csv"
BASE = "https://ebayi.tjk.org/s/d"
HEAD = {"User-Agent": "Mozilla/5.0 (rapor_ortak.py kisisel arastirma)"}

BIRIM_1TL = {"ELAZIG", "SANLIURFA", "DIYARBAKIR", "DBAKIR"}


def birim_fiyat(pist):
    """Altili birim bahis tutari (TL) — 2026 tarifesi."""
    return 1.00 if str(pist).strip().upper() in BIRIM_1TL else 1.25


# ----------------------------- defter zenginlestirme -----------------------------
_defter_cache = None


def defter_yukle():
    """defter.csv -> race_kod bazli indeks. Salt-okunur."""
    global _defter_cache
    if _defter_cache is not None:
        return _defter_cache
    if not DEFTER.exists():
        _defter_cache = pd.DataFrame()
        return _defter_cache
    d = pd.read_csv(DEFTER, low_memory=False)
    for c in ["race_kod", "no", "bot1", "bot2", "kamu", "oran", "model_rank",
              "sonuc", "kazandi", "ganyan_kapanis"]:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    # kamu sirasi: kosu icinde kamu% azalan (1 = kamu favorisi)
    d["kamu_sira"] = d.groupby("race_kod")["kamu"].rank(ascending=False, method="min")
    _defter_cache = d
    return d


def kosu_atlari(race_kod):
    """Bir kosunun defter kaydi (tum atlar). Yoksa bos DataFrame."""
    d = defter_yukle()
    if d.empty:
        return d
    return d[d["race_kod"] == race_kod]


def at_bilgi(race_kod, at_no):
    """(at_ad, sistem_sirasi, kamu_sirasi, oran, sonuc) — defter'de yoksa None'lar."""
    g = kosu_atlari(race_kod)
    if len(g) == 0:
        return {"ad": None, "sis": None, "kamu": None, "oran": None, "sonuc": None}
    r = g[g["no"] == at_no]
    if len(r) == 0:
        return {"ad": None, "sis": None, "kamu": None, "oran": None, "sonuc": None}
    r = r.iloc[0]
    return {"ad": r.get("at_ad"), "sis": r.get("model_rank"), "kamu": r.get("kamu_sira"),
            "oran": r.get("ganyan_kapanis") if pd.notna(r.get("ganyan_kapanis")) else r.get("oran"),
            "sonuc": r.get("sonuc")}


def kazanan_bilgi(race_kod):
    """Kosunun kazanani (defter'den): no, ad, sistem sirasi, kamu sirasi, kapanis orani."""
    g = kosu_atlari(race_kod)
    if len(g) == 0:
        return None
    w = g[g["sonuc"] == 1]
    if len(w) == 0:
        return None
    r = w.iloc[0]
    return {"no": int(r["no"]) if pd.notna(r["no"]) else None, "ad": r.get("at_ad"),
            "sis": r.get("model_rank"), "kamu": r.get("kamu_sira"),
            "oran": r.get("ganyan_kapanis") if pd.notna(r.get("ganyan_kapanis")) else r.get("oran")}


# ----------------------------- KUPON ANI siralamasi (K97) -----------------------------
# Defter'deki model_rank KOSU ANININ (posta-5dk) siralamasidir. Kupon ise Altili'nin ILK
# ayagindan ~30 dk once, TEK seferde kurulur -> son ayak icin karar 2-3 SAAT onceden verilir.
# O anki siralama baska bir siralamadir ve KARARI YARGILARKEN dogru cetvel odur.
# Ornek (09.08 Istanbul 2. Altili, kupon 15:14):
#   kosu 6 kazanani #1 -> sayfada "sistem 2." ama kupon aninda 7 atin 6.'siydi
#   kosu 8 kazanani #5 -> sayfada "sistem 10." ama kupon aninda 2. sirdaydi
# Bu yuzden kupon ani vektoru artik AYRI dosyaya yazilir (altili_kupon_ani.csv).
KUPON_ANI = KOK / "veri" / "altili_kupon_ani.csv"
_ani_cache = None


def kupon_ani_yukle():
    """altili_kupon_ani.csv -> (tarih,pist,seq,ayak) bazli indeks. Salt-okunur, cache'li."""
    global _ani_cache
    if _ani_cache is not None:
        return _ani_cache
    if not KUPON_ANI.exists():
        _ani_cache = pd.DataFrame()
        return _ani_cache
    a = pd.read_csv(KUPON_ANI, low_memory=False)
    for c in ["seq", "ayak", "kosu_no", "race_kod", "no", "bot1", "bot2", "kamu",
              "oran", "dk_kala"]:
        if c in a.columns:
            a[c] = pd.to_numeric(a[c], errors="coerce")
    # kupon anindaki siralamalar: sistem (bot2 azalan) ve piyasa (kamu azalan)
    grup = ["tarih", "pist", "seq", "ayak"]
    a["sis_sira"] = a.groupby(grup)["bot2"].rank(ascending=False, method="min")
    a["bot1_sira"] = a.groupby(grup)["bot1"].rank(ascending=False, method="min")
    a["kamu_sira"] = a.groupby(grup)["kamu"].rank(ascending=False, method="min")
    _ani_cache = a
    return _ani_cache


def kupon_ani_atlari(tarih, pist, seq, ayak):
    """Bir ayagin KUPON ANINDAKI tablosu (bot2 azalan sirali). Kayit yoksa bos DataFrame.
    NOT: ayni kosu iki Altili'da yer alabilir ve kupon anlari FARKLIDIR -> anahtar seq'i icerir."""
    a = kupon_ani_yukle()
    if a.empty:
        return a
    g = a[(a["tarih"].astype(str) == str(tarih)) & (a["pist"] == pist)
          & (a["seq"] == int(seq)) & (a["ayak"] == int(ayak))]
    return g.sort_values("sis_sira")


def kupon_ani_bilgi(tarih, pist, seq, ayak, at_no):
    """Tek atin kupon anindaki sirasi/olasiligi. Kayit yoksa None'lar."""
    bos = {"sis": None, "bot1_sira": None, "kamu": None, "oran": None,
           "bot2": None, "dk": None, "ts": None, "kaynak": None}
    g = kupon_ani_atlari(tarih, pist, seq, ayak)
    if len(g) == 0:
        return bos
    r = g[g["no"] == at_no]
    if len(r) == 0:
        return bos
    r = r.iloc[0]
    return {"sis": r.get("sis_sira"), "bot1_sira": r.get("bot1_sira"),
            "kamu": r.get("kamu_sira"), "oran": r.get("oran"), "bot2": r.get("bot2"),
            "dk": r.get("dk_kala"), "ts": r.get("kayit_ts"), "kaynak": r.get("kaynak")}


# ----------------------------- Altili temettu (cache'li) -----------------------------
PAT_ALTILI = re.compile(r"(?:(\d+)\.\s*)?6'LI GANYAN\(([\d/,]+)\):\s*([\d.,]+)\s*TL")


def _vfloat(s):
    s = str(s).strip()
    s = s.replace(".", "").replace(",", ".") if ("," in s and "." in s) else s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


PAT_ALTILI_DEVIR = re.compile(
    r"(?:(\d+)\.\s*)?6'LI GANYAN\(([\d/,]+)\):\s*Bilen\s*\S*\s*,\s*([\d.,]+)\s*TL\s*dev")
KOLT = ["tarih", "pist", "seq", "temettu", "devir", "kazanan_kombo"]


def _temettu_oku():
    if TEMETTU_CACHE.exists():
        c = pd.read_csv(TEMETTU_CACHE)
        for k in KOLT:                       # eski cache'te 'devir' yoksa ekle (geriye uyum)
            if k not in c.columns:
                c[k] = np.nan
        return c
    return pd.DataFrame(columns=KOLT)


def altili_odeme(tarih, pist, seq, cek=True):
    """(tarih,pist,seq) Altili RESMI odemesi — kupon tutsun tutmasin.
    Doner: {"temettu": float|None, "devir": float|None, "kombo": str|None}
      temettu dolu  -> o Altili X TL odedi (1 birim bahis basina)
      devir dolu    -> kimse bilemedi, X TL sonraki cekilise devretti
      ikisi de None -> henuz sonuclanmamis / bulunamadi"""
    c = _temettu_oku()
    m = ((c["tarih"].astype(str) == str(tarih)) & (c["pist"].astype(str) == str(pist))
         & (pd.to_numeric(c["seq"], errors="coerce") == seq))
    if m.any():
        r = c[m].iloc[0]
        t = pd.to_numeric(pd.Series([r.get("temettu")]), errors="coerce").iloc[0]
        d = pd.to_numeric(pd.Series([r.get("devir")]), errors="coerce").iloc[0]
        if pd.notna(t) or pd.notna(d):
            return {"temettu": None if pd.isna(t) else float(t),
                    "devir": None if pd.isna(d) else float(d),
                    "kombo": r.get("kazanan_kombo")}
    if not cek:
        return {"temettu": None, "devir": None, "kombo": None}
    ymd = pd.Timestamp(str(tarih)).strftime("%Y%m%d")
    try:
        req = urllib.request.Request(f"{BASE}/sonuclar/{ymd}/full/{pist}.json", headers=HEAD)
        with urllib.request.urlopen(req, timeout=25) as r:
            o = json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return {"temettu": None, "devir": None, "kombo": None}
    tam = " ".join(k.get("BAHISLER_TR") or "" for k in o.get("kosular", []))
    bulunan = {}
    for s, kombo, tut in PAT_ALTILI.findall(tam):
        bulunan[int(s) if s else 1] = {"temettu": _vfloat(tut), "devir": None, "kombo": kombo}
    for s, kombo, dv in PAT_ALTILI_DEVIR.findall(tam):
        bulunan[int(s) if s else 1] = {"temettu": None, "devir": _vfloat(dv), "kombo": kombo}
    if bulunan:
        yeni = [{"tarih": tarih, "pist": pist, "seq": s, "temettu": v["temettu"],
                 "devir": v["devir"], "kazanan_kombo": v["kombo"]} for s, v in bulunan.items()]
        c = pd.concat([c, pd.DataFrame(yeni)], ignore_index=True).drop_duplicates(
            ["tarih", "pist", "seq"], keep="last")
        TEMETTU_CACHE.parent.mkdir(parents=True, exist_ok=True)
        c.to_csv(TEMETTU_CACHE, index=False, encoding="utf-8", columns=KOLT)
    return bulunan.get(seq, {"temettu": None, "devir": None, "kombo": None})


def temettu_getir(tarih, pist, seq, cek=True):
    """Geriye uyumluluk: yalniz temettu (float|None)."""
    return altili_odeme(tarih, pist, seq, cek=cek)["temettu"]


# ----------------------------- ortak HTML parcalari -----------------------------
ORTAK_CSS = """<style>
body{font-family:Segoe UI,Arial,sans-serif;margin:18px;color:#1a1a1a;background:#fafafa;}
h2{margin:0 0 4px;} h3{margin:16px 0 6px;font-size:15px;}
.not{color:#666;font-size:12px;margin:2px 0 12px;line-height:1.5;}
.kart{background:#fff;border:1px solid #ddd;border-radius:8px;padding:10px 14px;margin:12px 0;
  box-shadow:0 1px 3px rgba(0,0,0,.06);}
.baslik{font-weight:bold;font-size:14px;margin-bottom:8px;padding-bottom:6px;
  border-bottom:2px solid #eee;}
table{border-collapse:collapse;width:100%;} td,th{border:1px solid #e4e4e4;padding:5px 8px;
  font-size:13px;text-align:center;} th{background:#f2f2f2;font-weight:600;}
td.l,th.l{text-align:left;}
.tut{background:#d9f7d9;} .kac{background:#fdeaea;} .bek{color:#999;background:#f7f7f7;}
.ban{background:#fff3cd;font-weight:bold;}
.rozet{display:inline-block;padding:2px 10px;border-radius:12px;font-weight:bold;font-size:12px;}
.r6{background:#0a7d0a;color:#fff;} .r5{background:#2a9d8f;color:#fff;}
.r4{background:#7cb342;color:#fff;} .r3{background:#c9a227;color:#fff;}
.r0{background:#c62828;color:#fff;} .rb{background:#ddd;color:#555;}
.toplam{background:#fff;border:3px solid #222;border-radius:8px;padding:14px 18px;margin:16px 0;
  font-size:14px;}
.toplam .buyuk{font-size:20px;font-weight:bold;}
.poz{color:#0a7d0a;} .neg{color:#c62828;}
.k{font-size:12px;color:#555;} .mini{font-size:11px;color:#777;}
</style>"""


def para(x, isaret=False):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "-"
    s = f"{abs(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if isaret:
        return ("+" if x >= 0 else "-") + s + " TL"
    return s + " TL"


def sira_str(x):
    """1.0 -> '1.' ; None -> '-'"""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "-"
    return f"{int(x)}."


def oran_str(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "-"
    return f"{x:.2f}".replace(".", ",")
