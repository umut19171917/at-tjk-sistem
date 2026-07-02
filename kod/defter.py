"""
defter.py — KAGIT-TICARET DEFTERI (gercek bahis YOK; bkz. KARARLAR K27/K28).
Amac: gunluk.py tahminlerini kaydet -> ertesi gun sonucla otomatik esle -> KOSAN bakiye + kalibrasyon.
"+EV yok"u soyut bilmek yerine biriken bir tabloda gor (kapanis maddesi).

Kapsam: yalnizca model-puanli (TR Ingiliz) kosular kaydedilir; ROI=GANYAN bazli (model win-olasiligi
uretir). Plase: para-getirisi DEGIL ama varis pozisyonu zaten kayitli -> ozet'te model top-pick'in
win/ilk-2/ilk-3 ISABET orani gosterilir (plase modeli/temettusu olmadan, bedava).

Komutlar:
    python defter.py kaydet --pist ANKARA [--tarih YYYY-MM-DD] [--kosu N --secim "2,5"]
    python defter.py sonucla                 # sonucu gelmemis kayitlari doldur
    python defter.py ozet                    # biriken kalibrasyon + ROI tablosu
"""
import argparse
import sys
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from gunluk import hesapla, getjson, BASE  # noqa: E402

DEFTER = KOK / "veri" / "defter.csv"
KOL = ["kayit_ts", "tarih", "pist", "race_kod", "kosu_no", "saat", "irk",
       "at_kod", "no", "at_ad", "bot1", "bot2", "kamu", "oran", "agf1",
       "canli", "model_rank", "secim", "sonuc", "kazandi", "ganyan_kapanis", "sonuclandi"]


def _oku():
    if DEFTER.exists():
        return pd.read_csv(DEFTER, low_memory=False)
    return pd.DataFrame(columns=KOL)


def _yaz(df):
    df.to_csv(DEFTER, index=False, encoding="utf-8", columns=KOL)


# ----------------------------- kaydet -----------------------------
def yaz_tg(tg, tarih, pist, only_kosu=None, kosu=None, secim=None):
    """Hazir puanli tg'yi deftere upsert eder. only_kosu -> sadece o kosuyu yaz (takip icin).
    Doner: (kosu_sayisi, satir_sayisi)."""
    if tg is None or len(tg) == 0:
        return 0, 0
    tg = tg.copy()
    if only_kosu is not None:
        tg = tg[pd.to_numeric(tg["kosu_no"], errors="coerce") == only_kosu]
        if len(tg) == 0:
            return 0, 0
    # --- ILERIYE-DONUKLUK KORUMASI (K36): posta saati gecmis kosu deftere yazilamaz.
    # Deferin deney degeri kayitlarin YARIS ONCESI olmasi; takip'i oglen baslatmak veya gecmis
    # --tarih ile kaydet, yaris-sonrasi (final'e yakin) oranla sahte "tahmin" uretirdi.
    # 3 dk tolerans: takip zaten post-5dk'da yazar. Saat parse edilemezse satir tutulur.
    post = pd.to_datetime(str(tarih) + " " + tg["saat"].astype(str),
                          format="%Y-%m-%d %H:%M", errors="coerce")
    gecmis = post.notna() & (post + pd.Timedelta(minutes=3) < datetime.now())
    if gecmis.any():
        atilan = sorted(set(pd.to_numeric(tg.loc[gecmis, "kosu_no"], errors="coerce")
                            .dropna().astype(int)))
        print(f"UYARI (defter korumasi): posta saati gecmis kosu(lar) YAZILMADI: {atilan} "
              f"(yaris-sonrasi kayit deneyi bozar)")
        tg = tg[~gecmis]
        if len(tg) == 0:
            return 0, 0
    tg["model_rank"] = tg.groupby("race_kod")["bot2"].rank(ascending=False, method="first")
    favimp = tg.groupby("race_kod")["kamu"].transform("max")
    canli = ((tg["kamu"] > 0) & (tg["bot1"] >= 1.5 * tg["kamu"]) & (tg["bot1"] >= 0.10)
             & (tg["kamu"] < tg["bot1"]) & (tg["kamu"] < favimp)).astype(int)

    yeni = pd.DataFrame({
        "kayit_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tarih": tarih, "pist": pist,
        "race_kod": tg["race_kod"].values, "kosu_no": tg["kosu_no"].values,
        "saat": tg["saat"].values, "irk": tg["irk"].values,
        "at_kod": tg["at_kod"].values, "no": tg["no"].values, "at_ad": tg["at_ad"].values,
        "bot1": tg["bot1"].round(4).values, "bot2": tg["bot2"].round(4).values,
        "kamu": tg["kamu"].round(4).values, "oran": tg["ganyan_muhtemel"].values,
        "agf1": tg["agf1"].values, "canli": canli.values,
        "model_rank": tg["model_rank"].astype("Int64").values, "secim": 0,
        "sonuc": np.nan, "kazandi": np.nan, "ganyan_kapanis": np.nan, "sonuclandi": np.nan,
    })

    old = _oku()
    # eski secim'leri koru (anahtar: race_kod+at_kod)
    if len(old):
        smap = {(r, a): s for r, a, s in zip(old["race_kod"], old["at_kod"], old["secim"])}
        yeni["secim"] = [int(smap.get((r, a), 0) or 0)
                         for r, a in zip(yeni["race_kod"], yeni["at_kod"])]

    # bu turda secim isareti
    if secim:
        if kosu is None:
            print("UYARI: --secim icin --kosu N gerekli; secim atlandi.")
        else:
            nos = {int(x) for x in str(secim).replace(" ", "").split(",") if x}
            m = (yeni["kosu_no"].astype("Int64") == kosu) & (yeni["no"].astype("Int64").isin(nos))
            yeni.loc[m, "secim"] = 1
            print(f"secim isaretlendi: kosu {kosu} -> no {sorted(nos)} ({int(m.sum())} at)")

    # upsert: eski COZULMEMIS ayni-anahtar satirlari at, cozulmusleri koru
    if len(old):
        anahtar_yeni = set(zip(yeni["race_kod"], yeni["at_kod"]))
        cozulmus = old["sonuclandi"].notna()
        ayni = [(r, a) in anahtar_yeni for r, a in zip(old["race_kod"], old["at_kod"])]
        old_keep = old[cozulmus | ~pd.Series(ayni, index=old.index)]
        out = pd.concat([old_keep, yeni], ignore_index=True)
    else:
        out = yeni
    _yaz(out)
    return yeni["race_kod"].nunique(), len(yeni)


def kaydet(pist, ymd, tarih, kosu=None, secim=None):
    raw, tg, _ = hesapla(pist, ymd)
    nk, n = yaz_tg(tg, tarih, pist, only_kosu=None, kosu=kosu, secim=secim)
    if n == 0:
        print(f"{pist} {tarih}: model-puanli (Ingiliz) kosu yok -> kaydedilmedi.")
        return
    out = _oku()
    print(f"kaydedildi: {pist} {tarih} -> {nk} kosu, {n} at  (defter: {len(out)} satir)")


# ----------------------------- sonucla -----------------------------
def sonucla():
    df = _oku()
    if df.empty:
        print("defter bos.")
        return
    acik = df[df["sonuclandi"].isna()]
    if acik.empty:
        print("sonuclanmamis kayit yok.")
        return
    df["sonuclandi"] = df["sonuclandi"].astype("object")   # tarih str tutabilsin (float64 degil)
    bugun = date.today().isoformat()
    dolan = 0
    for (tarih, pist), grp in acik.groupby(["tarih", "pist"]):
        ymd = datetime.strptime(str(tarih), "%Y-%m-%d").strftime("%Y%m%d")
        o = getjson(f"{BASE}/sonuclar/{ymd}/full/{pist}.json")
        if o.get("_hata"):
            print(f"  {tarih} {pist}: sonuc yok ({o['_hata']}) -> atlandi")
            continue
        res = {}
        for k in o.get("kosular", []):
            rk = k.get("KOD")
            try:
                rk = int(rk)
            except (ValueError, TypeError):
                pass
            for a in k.get("atlar", []):
                ak = a.get("KOD")
                try:
                    ak = int(ak)
                except (ValueError, TypeError):
                    pass
                s = pd.to_numeric(a.get("SONUC"), errors="coerce")
                kap = str(a.get("GANYAN", "")).replace(".", "").replace(",", ".")
                try:
                    kap = float(kap)
                except ValueError:
                    kap = np.nan
                res[(rk, ak)] = (s, kap)
        idx = df.index[(df["tarih"] == tarih) & (df["pist"] == pist) & df["sonuclandi"].isna()]
        for i in idx:
            key = (int(df.at[i, "race_kod"]), int(df.at[i, "at_kod"]))
            if key in res:
                s, kap = res[key]
                df.at[i, "sonuc"] = s
                df.at[i, "kazandi"] = int(s == 1) if pd.notna(s) else np.nan
                df.at[i, "ganyan_kapanis"] = kap
                df.at[i, "sonuclandi"] = bugun
                dolan += 1
    _yaz(df)
    html_yaz(df)   # HTML tabloyu tazele
    print(f"sonuclandi: {dolan} satir dolduruldu. (toplam {len(df)}, acik {int(df['sonuclandi'].isna().sum())})")


# ----------------------------- ozet -----------------------------
def _roi(sub, oran_col="ganyan_kapanis"):
    """flat 1 birim; getiri = oran*kazandi - 1. ROI% ve n."""
    sub = sub.dropna(subset=[oran_col, "kazandi"])
    if not len(sub):
        return float("nan"), 0
    ret = sub[oran_col].values * (sub["kazandi"].values == 1) - 1
    return float(ret.mean() * 100), len(sub)


def ozet():
    df = _oku()
    r = df[df["sonuclandi"].notna()].copy()
    if r.empty:
        print("sonuclanmis kayit yok (once 'sonucla').")
        return
    for c in ["bot1", "bot2", "kamu", "oran", "ganyan_kapanis", "kazandi", "sonuc", "model_rank"]:
        r[c] = pd.to_numeric(r[c], errors="coerce")
    nrace = r["race_kod"].nunique()
    print("=" * 66)
    print(f"DEFTER OZETI — {len(r)} at-satiri, {nrace} kosu, "
          f"{r['tarih'].min()}..{r['tarih'].max()}")
    print("UYARI: kagit-ticaret; +EV yok (6 test). Bu tablo 'ne olurdu'yu olcer, tavsiye degil.")
    print("=" * 66)

    # tam-cozulmus, tek-galipli kosular
    tam = r.groupby("race_kod").filter(
        lambda g: g["kazandi"].notna().all() and (g["kazandi"] == 1).sum() == 1)
    print(f"tam-cozulmus tek-galipli kosu: {tam['race_kod'].nunique()}")

    # --- kalibrasyon (bot2) ---
    print("\nKALIBRASYON (Bot2 dedigi % vs gercek kazanma):")
    kov = pd.cut(tam["bot2"], [0, .05, .10, .20, .35, 1.0],
                 labels=["0-5", "5-10", "10-20", "20-35", "35+"])
    for s, g in tam.groupby(kov, observed=True):
        print(f"  Bot2 %{str(s):6s}: tahmin~{g['bot2'].mean()*100:4.1f}%  "
              f"gercek {g['kazandi'].mean()*100:4.1f}%  (n={len(g)})")

    # --- log-loss model vs kamu (kosu basina -log p[galip]) ---
    def logloss(col):
        tot, n = 0.0, 0
        for _, g in tam.groupby("race_kod"):
            p = g[col].values
            p = p / p.sum() if p.sum() > 0 else p     # kosu-ici normalize
            w = g["kazandi"].values == 1
            if w.any():
                tot += -np.log(p[w][0] + 1e-12)
                n += 1
        return tot / n if n else float("nan")
    print(f"\nLOG-LOSS (dusuk iyi): Bot2={logloss('bot2'):.4f}  kamu={logloss('kamu'):.4f}")

    # --- ROI tablolari (kapanis ganyan, flat 1 birim) ---
    print("\nHIPOTETIK ROI (kapanis ganyan, flat 1 birim):")
    top = tam.loc[tam.groupby("race_kod")["bot2"].idxmax()]
    fav = tam.loc[tam.groupby("race_kod")["kamu"].idxmax()]
    canli = r[r["canli"] == 1]
    sec = r[r["secim"] == 1]
    for ad, sub in [("model top-pick (Bot2)", top), ("kamu favorisi (baz)", fav),
                    (">>CANLI atlari", canli), ("senin secimlerin", sec)]:
        roi, n = _roi(sub)
        print(f"  {ad:24s} ROI {roi:+6.1f}%  (n={n})" if n else f"  {ad:24s} (kayit yok)")

    # --- isabet orani: model top-pick varis (plase sezgisi, bedava) ---
    tp = top.dropna(subset=["sonuc"])
    if len(tp):
        print(f"\nMODEL TOP-PICK ISABET: win {(tp.sonuc==1).mean()*100:4.1f}%  "
              f"ilk-2 {(tp.sonuc<=2).mean()*100:4.1f}%  ilk-3 {(tp.sonuc<=3).mean()*100:4.1f}%  "
              f"(n={len(tp)})")


# ----------------------------- goster (gun/kosu/at bazli) -----------------------------
def goster(tarih=None, pist=None):
    """Deftere GUN -> KOSU -> AT bazli bakis: Bot1/Bot2 tahmini + gercek varis, yan yana."""
    df = _oku()
    if df.empty:
        print("defter bos.")
        return
    if tarih:
        df = df[df["tarih"].astype(str) == tarih]
    if pist:
        df = df[df["pist"].astype(str).str.upper() == pist.upper()]
    if df.empty:
        print("kayit yok (filtre bos dondu).")
        return
    for c in ["bot1", "bot2", "kamu", "oran", "sonuc", "kazandi", "ganyan_kapanis",
              "kosu_no", "no", "canli"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    def p(x):
        return f"{x*100:5.1f}" if pd.notna(x) else "  -  "

    def f2(x):
        return f"{x:6.2f}" if pd.notna(x) else "   -  "

    keys = sorted({(t, pi, k) for t, pi, k in zip(df["tarih"], df["pist"], df["kosu_no"])},
                  key=lambda z: (str(z[0]), z[2] if pd.notna(z[2]) else 999))
    for (tr, pi, ko) in keys:
        g = df[(df["tarih"] == tr) & (df["pist"] == pi) & (df["kosu_no"] == ko)].copy()
        saat = str(g["saat"].iloc[0]) if "saat" in g.columns else ""
        cozuldu = g["sonuc"].notna().any()
        g["mr"] = g["bot2"].rank(ascending=False, method="first")
        g["kr"] = g["kamu"].rank(ascending=False, method="first")
        favmax = g["kamu"].max()
        g = g.sort_values("sonuc", na_position="last") if cozuldu else g.sort_values("bot2", ascending=False)

        print(f"\n=== {tr}  {pi}  KOSU {int(ko) if pd.notna(ko) else '?'}  ({saat}) "
              f"{'' if cozuldu else '[sonuc bekleniyor]'}===")
        print(f"   {'no':>2} {'at':22s} {'Bot1%':>6} {'AGF%(sis)':>9} {'kamu%':>6} "
              f"{'oran':>6} {'VARIS':>5}  iz")
        for _, a in g.iterrows():
            iz = []
            if pd.notna(a["sonuc"]) and a["sonuc"] == 1:
                iz.append("KAZANDI")
            if pd.notna(a["kamu"]) and a["kamu"] == favmax:
                iz.append("F")
            if a["canli"] == 1:
                iz.append("CANLI")
            varis = str(int(a["sonuc"])) if pd.notna(a["sonuc"]) else "-"
            no = int(a["no"]) if pd.notna(a["no"]) else 0
            print(f"   {no:>2} {str(a['at_ad'])[:22]:22s} {p(a['bot1']):>6} {p(a['bot2']):>9} "
                  f"{p(a['kamu']):>6} {f2(a['oran']):>6} {varis:>5}  {' '.join(iz)}")
        if cozuldu:
            w = g[g["sonuc"] == 1]
            if len(w):
                wr = w.iloc[0]
                print(f"   -> kazanan: {str(wr['at_ad'])[:22]} "
                      f"(model {int(wr['mr'])}., kamu {int(wr['kr'])}., kapanis {f2(wr['ganyan_kapanis']).strip()})")


# ----------------------------- HTML (PowerShell'siz: tarayicida ac) -----------------------------
HTML = KOK / "raporlar" / "defter.html"


def html_yaz(df=None, path=None, ac=False):
    """Deferi okunur HTML tabloya dokler (gun/kosu/at: tahmin + sonuc). Cift tikla tarayicida ac."""
    if df is None:
        df = _oku()
    path = path or HTML
    path.parent.mkdir(parents=True, exist_ok=True)
    css = ("<meta charset='utf-8'><title>TJK Defter</title><style>"
           "body{font-family:Segoe UI,Arial,sans-serif;margin:20px;color:#222;}"
           "h2{margin:0 0 2px;} h3{margin:18px 0 3px;font-size:15px;}"
           "table{border-collapse:collapse;margin-bottom:2px;}"
           "td,th{border:1px solid #ccc;padding:3px 9px;text-align:right;font-size:13px;}"
           "th{background:#eee;} td.l,th.l{text-align:left;}"
           "tr.win{background:#d7f7d7;font-weight:bold;}"
           ".canli{color:#b30000;font-weight:bold;}.fav{color:#0050c0;font-weight:bold;}"
           ".kz{color:#0a0;}.not{color:#666;font-size:12px;margin:2px 0 12px;}</style>")
    if df.empty:
        path.write_text(css + "<p>defter bos.</p>", encoding="utf-8")
        return path
    for c in ["bot1", "bot2", "kamu", "oran", "sonuc", "kazandi", "ganyan_kapanis",
              "kosu_no", "no", "canli"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    def pc(x):
        return f"{x*100:.1f}" if pd.notna(x) else "-"

    def fo(x):
        return f"{x:.2f}" if pd.notna(x) else "-"

    keys = list({(t, pi, k) for t, pi, k in zip(df["tarih"], df["pist"], df["kosu_no"])})
    keys.sort(key=lambda z: z[2] if pd.notna(z[2]) else 999)     # kosu artan
    keys.sort(key=lambda z: str(z[0]), reverse=True)             # yeni gun ustte
    H = [css, "<h2>TJK Kagit-Defter</h2>",
         f"<div class=not>guncelleme {datetime.now():%Y-%m-%d %H:%M} &mdash; KAR DEGIL, kagit-ticaret; "
         "+EV yok (6 test). AGF%(sis)=sistemin kendi AGF'si (Bot2 harman). "
         "iz: F=kamu favorisi, CANLI=Bot1 kamuyu cok asiyor -> BAHIS sinyali DEGIL, 'kendi yarginla bak'.</div>"]
    for (tr, pi, ko) in keys:
        g = df[(df["tarih"] == tr) & (df["pist"] == pi) & (df["kosu_no"] == ko)].copy()
        saat = str(g["saat"].iloc[0]) if "saat" in g.columns else ""
        cozuldu = g["sonuc"].notna().any()
        g["mr"] = g["bot2"].rank(ascending=False, method="first")
        g["kr"] = g["kamu"].rank(ascending=False, method="first")
        favmax = g["kamu"].max()
        g = g.sort_values("sonuc", na_position="last") if cozuldu else g.sort_values("bot2", ascending=False)
        durum = "" if cozuldu else " <span class=not>[sonuc bekleniyor]</span>"
        H.append(f"<h3>{tr} &nbsp; {pi} &nbsp; KOSU {int(ko) if pd.notna(ko) else '?'} &nbsp;({saat}){durum}</h3>")
        H.append("<table><tr><th>varis</th><th>no</th><th class=l>at</th><th>Bot1%</th>"
                 "<th>AGF%(sis)</th><th>kamu%</th><th>oran</th><th class=l>iz</th></tr>")
        for _, a in g.iterrows():
            iz = []
            kazandi = pd.notna(a["sonuc"]) and a["sonuc"] == 1
            if kazandi:
                iz.append("<span class=kz>KAZANDI</span>")
            if pd.notna(a["kamu"]) and a["kamu"] == favmax:
                iz.append("<span class=fav>F</span>")
            if a["canli"] == 1:
                iz.append("<span class=canli>CANLI</span>")
            varis = int(a["sonuc"]) if pd.notna(a["sonuc"]) else "-"
            no = int(a["no"]) if pd.notna(a["no"]) else "-"
            rc = " class=win" if kazandi else ""
            H.append(f"<tr{rc}><td>{varis}</td><td>{no}</td><td class=l>{str(a['at_ad'])[:26]}</td>"
                     f"<td>{pc(a['bot1'])}</td><td>{pc(a['bot2'])}</td><td>{pc(a['kamu'])}</td>"
                     f"<td>{fo(a['oran'])}</td><td class=l>{' '.join(iz)}</td></tr>")
        H.append("</table>")
        if cozuldu:
            w = g[g["sonuc"] == 1]
            if len(w):
                wr = w.iloc[0]
                H.append(f"<div class=not>kazanan: <b>{str(wr['at_ad'])[:26]}</b> "
                         f"(model {int(wr['mr'])}., kamu {int(wr['kr'])}., kapanis {fo(wr['ganyan_kapanis'])})</div>")
    path.write_text("\n".join(H), encoding="utf-8")
    if ac:
        import webbrowser
        try:
            webbrowser.open(path.as_uri())
        except Exception:
            pass
    return path


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="komut", required=True)
    k = sub.add_parser("kaydet")
    k.add_argument("--pist", required=True)
    k.add_argument("--tarih", default=date.today().isoformat())
    k.add_argument("--kosu", type=int, default=None)
    k.add_argument("--secim", default=None, help='or. "2,5" (--kosu ile)')
    sub.add_parser("sonucla")
    sub.add_parser("ozet")
    g = sub.add_parser("goster", help="gun/kosu/at bazli tahmin+sonuc (terminal)")
    g.add_argument("--tarih", default=None)
    g.add_argument("--pist", default=None)
    sub.add_parser("html", help="okunur HTML tablo yaz + tarayicida ac")
    args = ap.parse_args()

    if args.komut == "kaydet":
        ymd = datetime.strptime(args.tarih, "%Y-%m-%d").strftime("%Y%m%d")
        kaydet(args.pist.strip().upper(), ymd, args.tarih, args.kosu, args.secim)
    elif args.komut == "sonucla":
        sonucla()
    elif args.komut == "ozet":
        ozet()
    elif args.komut == "goster":
        goster(args.tarih, args.pist)
    elif args.komut == "html":
        p = html_yaz(ac=True)
        print(f"HTML yazildi ve acildi: {p}")


if __name__ == "__main__":
    main()
