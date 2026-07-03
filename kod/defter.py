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
from gunluk import hesapla, getjson, BASE, canli_seri  # noqa: E402
from duzlestir import vir_float  # noqa: E402  (K39: GANYAN parse tek kaynak)

DEFTER = KOK / "veri" / "defter.csv"
KOL = ["kayit_ts", "tarih", "pist", "race_kod", "kosu_no", "saat", "irk",
       "at_kod", "no", "at_ad", "bot1", "bot2", "kamu", "oran", "agf1",
       "canli", "model_rank", "secim", "sonuc", "kazandi", "ganyan_kapanis", "sonuclandi"]

# --- GERCEK BAHIS DEFTERI (K37): kagit-defterden AYRI dosya; fiilen oynanan kuponlar.
# Amac: "senin yargın kesintiyi asiyor mu" sorusunu OLCMEK. getiri = kuponun toplam odemesi
# (TL; 0 = kaybetti, NaN = sonuclanmadi). Ganyan tek-at kuponu sonucla'da otomatik sonuclanir;
# diger turler (plase/ikili/altili...) elle: defter.py bahis-sonuc --id N --getiri X
BAHIS = KOK / "veri" / "bahisler.csv"
KOLB = ["id", "kayit_ts", "tarih", "pist", "kosu_no", "tur", "secim",
        "miktar", "getiri", "aciklama"]


def _bahis_oku():
    if BAHIS.exists():
        return pd.read_csv(BAHIS, low_memory=False)
    return pd.DataFrame(columns=KOLB)


def _bahis_yaz(df):
    df.to_csv(BAHIS, index=False, encoding="utf-8", columns=KOLB)


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
    canli = canli_seri(tg).astype(int)   # tek kaynak: gunluk.canli_seri (K39)

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


# ----------------------------- gercek bahisler (K37) -----------------------------
def bahis_ekle(tarih, pist, kosu, tur, secim, miktar, aciklama=None):
    """Fiilen oynanan kuponu kaydeder. Kupon basina BIR satir (ayni kosuda 2 ganyan
    bileti = 2 satir). Altili gibi cok-kosulu kuponda kosu = ILK ayak, secim serbest metin."""
    b = _bahis_oku()
    yeni_id = int(pd.to_numeric(b["id"], errors="coerce").max() + 1) if len(b) else 1
    satir = {"id": yeni_id, "kayit_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
             "tarih": tarih, "pist": str(pist).upper(), "kosu_no": kosu,
             "tur": str(tur).strip().lower(), "secim": str(secim).strip(),
             "miktar": float(miktar), "getiri": np.nan,
             "aciklama": aciklama or ""}
    b = pd.concat([b, pd.DataFrame([satir])], ignore_index=True)
    _bahis_yaz(b)
    print(f"bahis kaydedildi: id={yeni_id}  {tarih} {satir['pist']} kosu {kosu}  "
          f"{satir['tur']} '{satir['secim']}'  {miktar} TL")
    # --- K41 TAVAN UYUMU (kullanici tavani 2026-07-03: kupon/kosu <=100 TL, gun <=300 TL).
    # Sistem OLCER/UYARIR, engellemez (talimatname m.7: karar kullanicinin).
    gun_b = b[b["tarih"].astype(str) == str(tarih)]
    mikt = pd.to_numeric(gun_b["miktar"], errors="coerce").fillna(0.0)
    kosu_top = float(mikt[(gun_b["pist"].astype(str).str.upper() == str(pist).upper())
                          & (pd.to_numeric(gun_b["kosu_no"], errors="coerce")
                             == pd.to_numeric(kosu, errors="coerce"))].sum())
    gun_top = float(mikt.sum())
    if float(miktar) > 100:
        print(f"  UYARI (K41): kupon {float(miktar):.0f} TL > 100 TL tavani.")
    if kosu_top > 100:
        print(f"  UYARI (K41): bu kosuya bugun toplam {kosu_top:.0f} TL > 100 TL tavani.")
    if gun_top > 300:
        print(f"  UYARI (K41): bugunku toplam {gun_top:.0f} TL > 300 TL gun tavani.")
    if satir["tur"] != "ganyan":
        print("  NOT: bu tur otomatik sonuclanmaz -> sonucu ogrenince: "
              f"python kod/defter.py bahis-sonuc --id {yeni_id} --getiri <odeme; kaybettiyse 0>")
    return yeni_id


def bahis_sonuc(bid, getiri):
    """Kuponun gercek odemesini isler (kaybetti -> 0)."""
    b = _bahis_oku()
    m = pd.to_numeric(b["id"], errors="coerce") == bid
    if not m.any():
        print(f"id={bid} bulunamadi.")
        return
    b.loc[m, "getiri"] = float(getiri)
    _bahis_yaz(b)
    r = b[m].iloc[0]
    print(f"islendi: id={bid}  {r['tarih']} {r['pist']} kosu {r['kosu_no']}  {r['tur']}  "
          f"miktar {r['miktar']} -> getiri {float(getiri)} (net {float(getiri)-float(r['miktar']):+.2f})")


def _bahis_sonucla(defter_df):
    """sonucla icinden cagrilir: GANYAN tek-at kuponlarini cozulmus defter satirlariyla
    otomatik sonuclar (kazandi -> miktar x kapanis-ganyan, kaybetti -> 0). Diger turler elle."""
    b = _bahis_oku()
    if b.empty:
        return
    acik = b["getiri"].isna()
    d = defter_df[defter_df["sonuclandi"].notna()].copy()
    if not acik.any() or d.empty:
        return
    for c in ["kosu_no", "no", "kazandi", "ganyan_kapanis"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    dolan = 0
    for i in b.index[acik]:
        if str(b.at[i, "tur"]).strip().lower() != "ganyan":
            continue
        try:
            at_no = int(str(b.at[i, "secim"]).strip())      # tek at degilse (or. "3,5") elle
        except ValueError:
            continue
        m = ((d["tarih"].astype(str) == str(b.at[i, "tarih"]))
             & (d["pist"].astype(str).str.upper() == str(b.at[i, "pist"]).upper())
             & (d["kosu_no"] == pd.to_numeric(b.at[i, "kosu_no"], errors="coerce"))
             & (d["no"] == at_no))
        if not m.any():
            continue
        r = d[m].iloc[0]
        if pd.isna(r["kazandi"]) or pd.isna(r["ganyan_kapanis"]):
            continue
        b.at[i, "getiri"] = round(float(b.at[i, "miktar"]) * float(r["ganyan_kapanis"]), 2) \
            if r["kazandi"] == 1 else 0.0
        dolan += 1
    if dolan:
        _bahis_yaz(b)
        print(f"gercek bahis: {dolan} ganyan kuponu otomatik sonuclandi.")


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
                # K39: vir_float (duzlestir ile ayni parser) — feed'de GANYAN virgul-ondalik
                # ('9,95') ama AGF1 nokta-ondalik ('9.27'); eski elle-parse nokta gelirse bozardi.
                kap = vir_float(a.get("GANYAN"))
                res[(rk, ak)] = (s, np.nan if kap is None else kap)
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
    _bahis_sonucla(df)   # gercek ganyan kuponlarini otomatik sonucla (K37)
    html_yaz(df)   # HTML tabloyu tazele
    try:
        # K42 paper kuponlari da ayni aksam akisinda kapansin (ayri dosya/sayfa; hata bozmasin)
        import paper
        n = paper.sonucla_paper()
        if n:
            print(f"paper: {n} kupon kapatildi (raporlar/paper.html).")
    except Exception as e:
        print(f"paper sonuclama atlandi ({type(e).__name__}).")
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

    # --- GERCEK BAHISLER (K37): fiili kuponlarin P&L'i — asil olculen sey BU ---
    b = _bahis_oku()
    if len(b):
        b["miktar"] = pd.to_numeric(b["miktar"], errors="coerce")
        b["getiri"] = pd.to_numeric(b["getiri"], errors="coerce")
        s = b[b["getiri"].notna()]
        print("\n" + "=" * 66)
        print(f"GERCEK BAHISLER — {len(b)} kupon ({len(s)} sonuclandi, {len(b)-len(s)} acik)")
        if len(s):
            yat, don = s["miktar"].sum(), s["getiri"].sum()
            print(f"  TOPLAM: yatirilan {yat:.2f} TL  donen {don:.2f} TL  "
                  f"net {don-yat:+.2f} TL  ROI {100*(don-yat)/yat:+.1f}%")
            for tur, g in s.groupby(s["tur"].astype(str).str.lower()):
                yt, dn = g["miktar"].sum(), g["getiri"].sum()
                print(f"    {tur:10s} n={len(g):<4d} yatirilan {yt:8.2f}  net {dn-yt:+8.2f}  "
                      f"ROI {100*(dn-yt)/yt:+6.1f}%")
            if len(s) < 30:
                print(f"  UYARI: n={len(s)} kucuk — ROI guven araligi cok genis; "
                      f"K37 degerlendirme esigine (n>=100) kadar sonuc cikarma.")
        # --- K41 tavan uyumu (TUM kuponlar; oynanan para oynandi, sonuclanmasi gerekmez):
        # kupon<=100, kosu-toplami<=100, gun-toplami<=300 TL ---
        kup_asim = int((b["miktar"] > 100).sum())
        kosu_asim = int((b.groupby(["tarih", "pist", "kosu_no"])["miktar"].sum() > 100).sum())
        gun_asim = int((b.groupby("tarih")["miktar"].sum() > 300).sum())
        print(f"  K41 tavan uyumu: kupon>100TL: {kup_asim} | kosu-toplami>100TL: {kosu_asim} "
              f"| gun>300TL: {gun_asim}")
        # --- K37 ON-TAAHHUTLU KURAL (ONAYLANDI 2026-07-03, K40): esik = n>=100 SONUCLANMIS
        # kupon VE >=90 gun. Dolunca bootstrap %95 GA; ust sinir < 0 (kayip istatistiksel net)
        # -> GERCEK PARA DURUR, kagit devam. Kural veri birikmeden taahhut edildi (hindsight yok).
        gun_gecti = 0
        if len(s):
            gun_gecti = (pd.Timestamp.today()
                         - pd.to_datetime(s["tarih"], errors="coerce").min()).days
        if len(s) >= 100 and gun_gecti >= 90:
            rng = np.random.default_rng(42)
            mv = s["miktar"].to_numpy(dtype=float)
            gv = s["getiri"].to_numpy(dtype=float)
            idx = rng.integers(0, len(s), size=(10000, len(s)))
            rois = (gv[idx].sum(1) - mv[idx].sum(1)) / mv[idx].sum(1)
            lo, hi = np.percentile(rois, [2.5, 97.5])
            print(f"  K37 DEGERLENDIRME (esik doldu): ROI %95 GA "
                  f"[{lo*100:+.1f}%, {hi*100:+.1f}%]  (bootstrap 10k, n={len(s)})")
            if hi < 0:
                print("  >>> K37 TETIKLENDI: kayip istatistiksel olarak net -> "
                      "GERCEK PARA DUR, kagit-ticaret devam.")
            else:
                print("  K37: tetiklenmedi (GA ust siniri >= 0) -> izlemeye devam.")
        else:
            print(f"  K37 esigine ilerleme: kupon {len(s)}/100, gun {max(gun_gecti, 0)}/90.")


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
    # --- gercek bahisler ozeti (K37) ---
    b = _bahis_oku()
    if len(b):
        b["miktar"] = pd.to_numeric(b["miktar"], errors="coerce")
        b["getiri"] = pd.to_numeric(b["getiri"], errors="coerce")
        s = b[b["getiri"].notna()]
        H.append("<h3>Gercek bahisler</h3>")
        if len(s):
            yat, don = s["miktar"].sum(), s["getiri"].sum()
            H.append(f"<div class=not><b>{len(b)}</b> kupon ({len(s)} sonuclandi) &mdash; "
                     f"yatirilan <b>{yat:.2f}</b> TL, net <b>{don-yat:+.2f}</b> TL, "
                     f"ROI <b>{100*(don-yat)/yat:+.1f}%</b>"
                     + (f" &mdash; UYARI: n kucuk, sonuc cikarma (K37 esik n&ge;100)" if len(s) < 30 else "")
                     + "</div>")
        H.append("<table><tr><th>id</th><th>tarih</th><th class=l>pist</th><th>kosu</th>"
                 "<th class=l>tur</th><th class=l>secim</th><th>miktar</th><th>getiri</th><th>net</th></tr>")
        for _, r in b.sort_values("id", ascending=False).head(30).iterrows():
            net = (r["getiri"] - r["miktar"]) if pd.notna(r["getiri"]) else None
            H.append(f"<tr><td>{int(r['id'])}</td><td>{r['tarih']}</td><td class=l>{r['pist']}</td>"
                     f"<td>{r['kosu_no']}</td><td class=l>{r['tur']}</td><td class=l>{r['secim']}</td>"
                     f"<td>{r['miktar']:.2f}</td>"
                     f"<td>{('%.2f' % r['getiri']) if pd.notna(r['getiri']) else 'acik'}</td>"
                     f"<td>{('%+.2f' % net) if net is not None else '-'}</td></tr>")
        H.append("</table>")
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
    b = sub.add_parser("bahis", help="GERCEK kupon kaydet (K37; kupon basina bir satir)")
    b.add_argument("--pist", required=True)
    b.add_argument("--kosu", required=True, help="kosu no (altili vb. icin ILK ayak)")
    b.add_argument("--tur", required=True, help="ganyan/plase/ikili/uclu/altili/...")
    b.add_argument("--secim", required=True, help='at no; kombine ise serbest metin (or. "3-7" / "2,5/1/4...")')
    b.add_argument("--miktar", required=True, type=float, help="kupon tutari TL")
    b.add_argument("--tarih", default=date.today().isoformat())
    b.add_argument("--aciklama", default=None)
    bs = sub.add_parser("bahis-sonuc", help="kuponun gercek odemesini isle (kaybetti -> 0)")
    bs.add_argument("--id", required=True, type=int)
    bs.add_argument("--getiri", required=True, type=float, help="toplam odeme TL (0=kaybetti)")
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
    elif args.komut == "bahis":
        bahis_ekle(args.tarih, args.pist, args.kosu, args.tur, args.secim,
                   args.miktar, args.aciklama)
    elif args.komut == "bahis-sonuc":
        bahis_sonuc(args.id, args.getiri)


if __name__ == "__main__":
    main()
