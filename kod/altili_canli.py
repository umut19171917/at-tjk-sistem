"""
altili_canli.py — CANLI ALTILI kupon uretimi + takibi (K53). GERCEK BAHIS DEGIL (K48; +EV yok,
K52 backtest OOS -%32). Amac: izleme/ogrenme — kuponu ilk kosu baslamadan kur, kosular ilerledikce
ayak sonuclarini + nihai Altili isabetini isle, basari oranini ACIK dille/gorselle goster.

AYRI dosya/sayfa: veri/altili_kupon.csv + raporlar/altili.html. defter/paper'a DOKUNMAZ.

Kupon mantigi (K52 backtest'iyle AYNI cekirdek: altili_backtest.kupon_kur):
  banker (Bot2 guveni >= esik -> tek at) + spread (kumulatif kapsam) + butce tavani.
  IKI config (kullanici K53): 'dar' (<=24 kombo) ve 'orta' (<=96 kombo), ayri takip.
Pencere: program BAHISLER_TR'de "N. 6'LI GANYAN bu kosudan baslar" -> o kosudan 6 ardisik kosu.
  Gunde 1-2 Altili olabilir (K46 kesfi); hepsi ayri islenir.
Odeme yapisi (K52): 5/4/3'lu AYRI bahisler, teselli DEGIL -> yalniz 6/6 "tam isabet" kazanc sayilir;
  yine de 5/4/3 sondan-ayak isabetini BILGI olarak gosteririz (ogrenme; para degeri yok).

Kullanim:
    python altili_canli.py --pist ISTANBUL [--tarih YYYY-MM-DD]   # kupon hazirla + HTML
    python altili_canli.py --sonucla                              # bekleyen ayaklari sonucla + HTML
    python altili_canli.py --html                                 # sadece HTML'i tazele + ac
"""
import argparse
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from gunluk import hesapla, getjson, BASE, EXCL  # noqa: E402
from altili_backtest import kupon_kur  # noqa: E402
from duzlestir import vir_float  # noqa: E402

KUPON = KOK / "veri" / "altili_kupon.csv"
HTMLA = KOK / "raporlar" / "altili.html"
KONFIG = {"dar": 24, "orta": 96}      # K53: kullanici ikisini de istedi
KAPSAM_ESIK, BANKER_ESIK = 0.75, 0.70  # K52 backtest'te en iyi OOS profili
KOL = ["kayit_ts", "tarih", "pist", "seq", "ilk_saat", "config", "ayak",
       "kosu_no", "race_kod", "saat", "secim", "banker", "nat",
       "kazanan", "tuttu", "sonuclandi"]


def _oku():
    if KUPON.exists():
        return pd.read_csv(KUPON, low_memory=False)
    return pd.DataFrame(columns=KOL)


def _yaz(df):
    df.to_csv(KUPON, index=False, encoding="utf-8", columns=KOL)


# ----------------------------- pencere tespiti -----------------------------
def altili_pencereleri(o):
    """Program JSON'dan Altili pencereleri: [(seq, [6 kosu-dict], ilk_saat)].
    Kaynak: her kosunun BAHISLER_TR'sinde '<seq>. 6'LI GANYAN bu kosudan baslar' isareti."""
    kos = sorted(o.get("kosular", []),
                 key=lambda k: int(k.get("RACENO") or k.get("NO") or 0))
    pat = re.compile(r"(\d+)\.\s*6'LI GANYAN\s+bu\s+ko", re.IGNORECASE)
    out = []
    for i, k in enumerate(kos):
        m = pat.search(k.get("BAHISLER_TR") or "")
        if not m:
            continue
        pencere = kos[i:i + 6]
        if len(pencere) < 6:                 # eksik pencere (program kesik) -> atla
            continue
        out.append((int(m.group(1)), pencere, str(k.get("SAAT", "")).strip()))
    return out


def _as_int(x):
    try:
        return int(str(x).strip())
    except (ValueError, TypeError):
        return None


# ----------------------------- kupon hazirla -----------------------------
def kupon_hazirla(pist, ymd, tarih, sadece_seq=None):
    """Pistin canli kartini puanla (Ingiliz+Arap), Altili pencereleri icin dar+orta kupon kur,
    deftere upsert. sadece_seq verilirse yalniz o Altili penceresini kurar (takip: her Altili
    kendi ilk kosusundan ~30dk once). Doner: kurulan (pencere x config) sayisi."""
    o = getjson(f"{BASE}/program/{ymd}/full/{pist}.json")
    if o.get("_hata"):
        print(f"{pist} {tarih}: program yok ({o['_hata']})")
        return 0
    pencereler = altili_pencereleri(o)
    if sadece_seq is not None:
        pencereler = [p for p in pencereler if p[0] == sadece_seq]
    if not pencereler:
        print(f"{pist} {tarih}: Altili penceresi bulunamadi (program bahis bilgisi yok/kesik).")
        return 0

    raw, tg, _ = hesapla(pist, ymd)          # tg = puanli satirlar (Ingiliz+Arap); bot2 dolu
    if tg is None or len(tg) == 0:
        print(f"{pist} {tarih}: hicbir kosu puanlanamadi (kapsam disi).")
        return 0
    tg = tg.copy()
    tg["kosu_no_i"] = pd.to_numeric(tg["kosu_no"], errors="coerce")

    yeni_satirlar = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    for seq, pencere, ilk_saat in pencereler:
        # her ayagin (no, bot2) listesi -- puani olmayan ayak varsa pencere ATLANIR
        ayak_atlari, ayak_meta, eksik = [], [], False
        for k in pencere:
            kno = _as_int(k.get("RACENO") or k.get("NO"))
            g = tg[tg["kosu_no_i"] == kno]
            g = g[pd.to_numeric(g["bot2"], errors="coerce").notna()]
            if len(g) < 4:                    # <4 atli / puansiz ayak -> Altili kurulamaz
                eksik = True
                break
            atlar = [(int(r["no"]), float(r["bot2"])) for _, r in g.iterrows()]
            ayak_atlari.append(atlar)
            ayak_meta.append({"kosu_no": kno, "race_kod": _as_int(k.get("KOD")),
                              "saat": str(k.get("SAAT", "")).strip()})
        if eksik:
            print(f"  {seq}. Altili (kosu {pencere[0].get('RACENO')}): bir ayak kapsam disi -> atlandi")
            continue

        for cfg, maxk in KONFIG.items():
            sec = kupon_kur(ayak_atlari, KAPSAM_ESIK, maxk, BANKER_ESIK)
            for ai in range(6):
                atlar_sirali = sorted(ayak_atlari[ai], key=lambda x: -x[1])
                secili = sec[ai]
                banker = 1 if len(secili) == 1 and atlar_sirali[0][1] >= BANKER_ESIK else 0
                yeni_satirlar.append({
                    "kayit_ts": ts, "tarih": tarih, "pist": pist, "seq": seq,
                    "ilk_saat": ilk_saat, "config": cfg, "ayak": ai + 1,
                    "kosu_no": ayak_meta[ai]["kosu_no"], "race_kod": ayak_meta[ai]["race_kod"],
                    "saat": ayak_meta[ai]["saat"],
                    "secim": ",".join(str(n) for n in sorted(secili)),
                    "banker": banker, "nat": len(secili),
                    "kazanan": np.nan, "tuttu": np.nan, "sonuclandi": np.nan,
                })

    if not yeni_satirlar:
        return 0
    yeni = pd.DataFrame(yeni_satirlar)
    old = _oku()
    if len(old):
        # upsert: ayni (tarih,pist,seq,config) COZULMEMIS satirlarini degistir, cozulmusleri koru
        anahtar = set(zip(yeni["tarih"], yeni["pist"], yeni["seq"], yeni["config"]))
        coz = old["sonuclandi"].notna()
        ayni = [(t, p, s, c) in anahtar for t, p, s, c in
                zip(old["tarih"], old["pist"], old["seq"], old["config"])]
        old = old[coz | ~pd.Series(ayni, index=old.index)]
        out = pd.concat([old, yeni], ignore_index=True)
    else:
        out = yeni
    _yaz(out)
    n = yeni.groupby(["seq", "config"]).ngroups
    print(f"{pist} {tarih}: {n} kupon kuruldu ({len(pencereler)} Altili x {len(KONFIG)} config).")
    return n


# ----------------------------- takip tetigi (zaman-bazli) -----------------------------
def kupon_zamani_kur(pistler, ymd, tarih, dk_kala=30):
    """takip.py her turda cagirir. Her Altili penceresi icin: ilk kosusuna <=dk_kala kaldiysa
    VE ilk kosu HENUZ baslamadiysa VE bugun bu (pist,seq) icin kupon YOKSA -> kur.
    Idempotent (kurulmus olani atlar). Doner: kurulan kupon sayisi. Hata firlatmaz (takip guvenligi)."""
    kurulan = 0
    df = _oku()
    now = datetime.now()
    for pist in pistler:
        try:
            o = getjson(f"{BASE}/program/{ymd}/full/{pist}.json")
            if o.get("_hata"):
                continue
            for seq, pencere, ilk_saat in altili_pencereleri(o):
                if len(df) and ((df["tarih"] == tarih) & (df["pist"] == pist)
                                & (df["seq"] == seq)).any():
                    continue                       # zaten kurulmus
                try:
                    ilk_post = datetime.strptime(f"{tarih} {ilk_saat}", "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
                if ilk_post - timedelta(minutes=dk_kala) <= now < ilk_post:
                    kurulan += kupon_hazirla(pist, ymd, tarih, sadece_seq=seq)
                    df = _oku()
        except Exception as e:
            print(f"  altili kupon hatasi ({pist}): {type(e).__name__} - takip devam ediyor")
    if kurulan:
        html_yaz()
    return kurulan


# ----------------------------- sonucla -----------------------------
def sonucla_altili():
    df = _oku()
    if df.empty:
        print("altili defteri bos.")
        return 0
    acik = df[df["sonuclandi"].isna()]
    if acik.empty:
        print("sonuclanmamis ayak yok.")
        return 0
    df["sonuclandi"] = df["sonuclandi"].astype("object")
    bugun = date.today().isoformat()
    dolan = 0
    for (tarih, pist), grp in acik.groupby(["tarih", "pist"]):
        ymd = datetime.strptime(str(tarih), "%Y-%m-%d").strftime("%Y%m%d")
        o = getjson(f"{BASE}/sonuclar/{ymd}/full/{pist}.json")
        if o.get("_hata"):
            continue
        kaz = {}                              # race_kod -> kazanan no
        for k in o.get("kosular", []):
            rk = _as_int(k.get("KOD"))
            for a in k.get("atlar", []):
                s = pd.to_numeric(a.get("SONUC"), errors="coerce")
                if pd.notna(s) and int(s) == 1:
                    kaz[rk] = _as_int(a.get("NO"))
        idx = df.index[(df["tarih"] == tarih) & (df["pist"] == pist) & df["sonuclandi"].isna()]
        for i in idx:
            rk = _as_int(df.at[i, "race_kod"])
            if rk in kaz and kaz[rk] is not None:
                kz = kaz[rk]
                secilenler = {int(x) for x in str(df.at[i, "secim"]).split(",") if x != ""}
                df.at[i, "kazanan"] = kz
                df.at[i, "tuttu"] = int(kz in secilenler)
                df.at[i, "sonuclandi"] = bugun
                dolan += 1
    _yaz(df)
    html_yaz(df)
    print(f"altili: {dolan} ayak sonuclandi (acik {int(df['sonuclandi'].isna().sum())}).")
    return dolan


# ----------------------------- isabet hesabi -----------------------------
def _isabet_kademe(tuttu_listesi):
    """tuttu_listesi = ayak 1..6 icin 0/1/None. Sondan kesik en uzun ardisik tutan (6/5/4/3);
    hicbiri degilse 0. None (bekleyen) varsa None (henuz belli degil)."""
    if any(t is None for t in tuttu_listesi):
        return None
    t = [bool(x) for x in tuttu_listesi]
    for n in (6, 5, 4, 3):
        if all(t[6 - n:]):
            return n
    return 0


# ----------------------------- HTML (acik/net) -----------------------------
def html_yaz(df=None, ac=False):
    if df is None:
        df = _oku()
    for c in ["seq", "ayak", "kosu_no", "banker", "nat", "kazanan", "tuttu"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    css = """<meta charset='utf-8'><title>Altili Canli Takip</title><style>
body{font-family:Segoe UI,Arial,sans-serif;margin:18px;color:#1a1a1a;background:#fafafa;}
h2{margin:0 0 4px;} h3{margin:14px 0 4px;font-size:15px;}
.not{color:#666;font-size:12px;margin:2px 0 10px;}
.kart{background:#fff;border:1px solid #ddd;border-radius:8px;padding:10px 14px;margin:10px 0;
  box-shadow:0 1px 3px rgba(0,0,0,.05);}
.baslik{font-weight:bold;font-size:14px;margin-bottom:6px;}
table{border-collapse:collapse;width:100%;} td,th{border:1px solid #e2e2e2;padding:4px 8px;
  font-size:13px;text-align:center;} th{background:#f0f0f0;}
td.l{text-align:left;} .ban{background:#fff3cd;font-weight:bold;}
.tut{background:#d7f7d7;} .kac{background:#fde0e0;} .bek{color:#999;}
.rozet{display:inline-block;padding:2px 9px;border-radius:12px;font-weight:bold;font-size:12px;}
.r6{background:#0a7d0a;color:#fff;} .r5{background:#3a9;color:#fff;} .r4{background:#7a3;color:#fff;}
.r3{background:#ba3;color:#fff;} .r0{background:#c33;color:#fff;} .rb{background:#ddd;color:#555;}
.ozet{background:#fff;border:2px solid #333;border-radius:8px;padding:12px 16px;margin:10px 0;}
.bar{display:inline-block;height:16px;border-radius:3px;vertical-align:middle;}
.k{font-size:12px;color:#444;}
</style>"""

    H = [css, "<h2>Altili Canli Takip (K53)</h2>",
         f"<div class=not>guncelleme {datetime.now():%Y-%m-%d %H:%M} &mdash; "
         "GERCEK BAHIS DEGIL, izleme/ogrenme. Backtest OOS -%32, +EV yok (K52). "
         "5/4/3 ayak isabeti yalniz BILGI (TJK'da ayri bahis, teselli degil).</div>"]

    if df.empty:
        H.append("<p>Henuz kupon yok. Altili gununde ilk kosudan once otomatik kurulur.</p>")
        HTMLA.parent.mkdir(parents=True, exist_ok=True)
        HTMLA.write_text("\n".join(H), encoding="utf-8")
        return HTMLA

    # ---- pencere-config bazli isabet + GENEL OZET ----
    kayitlar = []
    for (tarih, pist, seq, cfg), g in df.groupby(["tarih", "pist", "seq", "config"]):
        g = g.sort_values("ayak")
        tut = [None if pd.isna(t) else int(t) for t in g["tuttu"]]
        kademe = _isabet_kademe(tut)
        nkombo = int(np.prod([int(x) for x in g["nat"]]))
        kayitlar.append({"tarih": tarih, "pist": pist, "seq": seq, "config": cfg,
                         "kademe": kademe, "nkombo": nkombo, "g": g,
                         "ilk_saat": g["ilk_saat"].iloc[0]})

    for cfg in KONFIG:
        alt = [k for k in kayitlar if k["config"] == cfg and k["kademe"] is not None]
        n = len(alt)
        dag = {kad: sum(1 for k in alt if k["kademe"] == kad) for kad in (6, 5, 4, 3, 0)}
        ort_kombo = np.mean([k["nkombo"] for k in kayitlar if k["config"] == cfg]) if kayitlar else 0
        H.append(f"<div class=ozet><b>OZET — {cfg.upper()} kupon</b> "
                 f"(<span class=k>ort. {ort_kombo:.0f} kombinasyon/kupon</span>)<br>")
        if n == 0:
            H.append("Henuz sonuclanmis Altili yok.</div>")
            continue
        H.append(f"Tamamlanan Altili: <b>{n}</b> &nbsp;|&nbsp; "
                 f"TAM ISABET (6/6): <b>{dag[6]}</b> "
                 f"(%{100*dag[6]/n:.1f})<br><span class=k>ayak isabet dagilimi (sondan): </span>")
        renk = {6: "#0a7d0a", 5: "#33aa99", 4: "#77aa33", 3: "#bbaa33", 0: "#cc3333"}
        etiket = {6: "6/6", 5: "5", 4: "4", 3: "3", 0: "<3"}
        for kad in (6, 5, 4, 3, 0):
            w = int(120 * dag[kad] / n)
            H.append(f"<div style='margin:2px 0'><span style='display:inline-block;width:34px' class=k>"
                     f"{etiket[kad]}</span>"
                     f"<span class=bar style='width:{max(w,2)}px;background:{renk[kad]}'></span> "
                     f"<span class=k>{dag[kad]}</span></div>")
        H.append("</div>")

    # ---- her Altili karti (yeni gun ustte, config yan yana) ----
    kayitlar.sort(key=lambda k: (str(k["tarih"]), k["pist"], int(k["seq"]), k["config"]), reverse=True)
    for k in kayitlar:
        g = k["g"]
        kad = k["kademe"]
        rozet = (f"<span class='rozet r{kad}'>{'TAM ISABET 6/6' if kad==6 else (str(kad)+' ayak (sondan)' if kad else 'isabetsiz')}</span>"
                 if kad is not None else "<span class='rozet rb'>bekleniyor</span>")
        H.append("<div class=kart>")
        H.append(f"<div class=baslik>{k['tarih']} &nbsp; {k['pist']} &nbsp; "
                 f"{k['seq']}. ALTILI &nbsp;(ilk kosu {g['kosu_no'].iloc[0]:.0f}, {k['ilk_saat']}) "
                 f"&nbsp; [{k['config'].upper()}, {k['nkombo']} kombinasyon] &nbsp; {rozet}</div>")
        H.append("<table><tr><th>ayak</th><th>kosu</th><th>saat</th><th class=l>secimimiz</th>"
                 "<th>kazanan</th><th>durum</th></tr>")
        for _, r in g.iterrows():
            tuttu = r["tuttu"]
            if pd.isna(tuttu):
                dcls, dtxt = "bek", "bekleniyor"
            elif int(tuttu) == 1:
                dcls, dtxt = "tut", "TUTTU"
            else:
                dcls, dtxt = "kac", "kactı"
            secim = str(r["secim"])
            scls = " class=ban" if int(r["banker"]) == 1 else " class=l"
            setxt = secim + (" (banker)" if int(r["banker"]) == 1 else "")
            kztxt = "-" if pd.isna(r["kazanan"]) else f"{int(r['kazanan'])}"
            H.append(f"<tr><td>{int(r['ayak'])}</td><td>{int(r['kosu_no'])}</td><td>{r['saat']}</td>"
                     f"<td{scls}>{setxt}</td><td>{kztxt}</td><td class={dcls}>{dtxt}</td></tr>")
        H.append("</table></div>")

    HTMLA.parent.mkdir(parents=True, exist_ok=True)
    HTMLA.write_text("\n".join(H), encoding="utf-8")
    if ac:
        import webbrowser
        try:
            webbrowser.open(HTMLA.as_uri())
        except Exception:
            pass
    return HTMLA


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pist")
    ap.add_argument("--tarih", default=date.today().isoformat())
    ap.add_argument("--sonucla", action="store_true")
    ap.add_argument("--html", action="store_true")
    args = ap.parse_args()

    if args.sonucla:
        sonucla_altili()
    elif args.html:
        p = html_yaz(ac=True)
        print(f"HTML: {p}")
    elif args.pist:
        ymd = datetime.strptime(args.tarih, "%Y-%m-%d").strftime("%Y%m%d")
        n = kupon_hazirla(args.pist.strip().upper(), ymd, args.tarih)
        if n:
            html_yaz()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
