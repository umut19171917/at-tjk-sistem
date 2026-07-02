"""
gunluk.py — GUNLUK TAHMIN + KAGIT-TICARET araci (KAR DEGIL; bkz. KARARLAR K26).
6 bagimsiz test +EV cikmadi; bu arac = calisan sistem + ogrenme + kalibre "matematik gorusu"nu
kullanici yargisiyla birlestiren analiz araci. Sistem KAR garantisi VERMEZ.

Ne yapar:
  - O gunun canli programini ebayi.tjk.org'dan ceker (GANYAN=canli muhtemel, KOSMAZ=cikan,
    JOKEY=guncel) -> gecmis katilim.csv'ye ekler -> EGITIMLE AYNI nokta-aninda ozellikleri uretir
    (ozellik.build_features) -> Bot1 (oran-kor) + Bot2 (piyasayla harman) uygular.
  - Cikti: her kosu icin sahin Bot1% (kendi AGF'si), Bot2% (harman), kamu% (de-vig oran),
    AGF%, canli oran ve "canli-non-favori" isareti (Bot1% kamu%'den COK yuksek).

KAPSAM: model yalnizca TR Ingiliz duz kosulari icin egitildi/dogrulandi. Arap / 2yas-maiden /
  kucuk-saha kosular "model kapsam disi" gosterilir (sadece kamu AGF/oran). 4 supheli pist haric.

CANLI != SIZINTI: tahmin aninda gelecek yok; ozellikler gecmisten. Canli aslinda daha AZ bilgi.

Kullanim:
    python gunluk.py --pist ANKARA                 # bugun, tam kart (sabah)
    python gunluk.py --pist ANKARA --tarih 2026-06-30
    python gunluk.py --pist ANKARA --kosu 5         # tek kosuyu guncel kadro/oranla yeniden
    python gunluk.py                                # bugunku yerli pistleri listele
"""
import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from ozellik import load_katilim, build_features, select_scope, FEAT, EXCL  # noqa: E402
from duzlestir import vir_float, zaman_sn, parse_yas, irk_of, going_of, SEHIR_MAP  # noqa: E402
from model import race_struct, seg_softmax, fit_clogit, devig  # noqa: E402

BASE = "https://ebayi.tjk.org/s/d"
HEAD = {"User-Agent": "Mozilla/5.0 (gunluk.py kisisel arastirma)"}


# ----------------------------- canli veri -----------------------------
def getjson(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=HEAD), timeout=25) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return {"_hata": f"HTTP {e.code}"}
    except Exception as e:
        return {"_hata": f"{type(e).__name__}"}


def yerli_pistler(ymd):
    """O gunun yerli (TR) pist KEY listesi.
    KAYNAK = PROGRAM index (sonuclar degil): sonuclar/yarislar.json yaris GUNU BOSTUR (results
    aksam dolar) -> sabah takip baslatinca [] donerdi (K34 hatasi). Program index sabah da dolu;
    TR pistlerde GUN sayisal, yabanci pistlerde GUN=None -> asagidaki GUN filtresi TR/yabanci ayirir."""
    j = getjson(f"{BASE}/program/{ymd}/yarislar.json")
    venues = []
    if isinstance(j, list):
        venues = [v for v in j if isinstance(v, dict)]
    elif isinstance(j, dict):
        for v in j.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                venues = v
                break
    out = []
    for v in venues:
        key = str(v.get("KEY", "")).strip().upper()
        gun = v.get("GUN")
        if (key and key != "KARMA" and gun is not None
                and str(gun).strip() not in ("", "0", "null", "None")
                and str(v.get("SIRA", "")).strip() != "99"):
            out.append((SEHIR_MAP.get(key, key), v.get("AD", "")))
    return out


def as_int(x):
    """Program JSON'da KOD/JOKEYKODU vb. STRING gelir; gecmis katilim.csv int64.
    Join'in (groupby at_kod/jokey/antrenor) kirilmamasi icin int'e cevir."""
    try:
        return int(str(x).strip())
    except (ValueError, TypeError):
        return None


def flatten_program(o, sehir, ymd):
    """Canli program JSON -> katilim-sema satirlari (SONUC YOK; bugun=1)."""
    hava = o.get("hava", {}) or {}
    rows = []
    for k in o.get("kosular", []):
        rk = k.get("KOD")
        ac = k.get("ActiveClass")
        going, going_ag = going_of(hava, ac)
        irk = irk_of(k.get("GRUP_TR"), k.get("GRUPKISA"))
        rmeta = {
            "race_kod": as_int(rk), "tarih": k.get("TARIH"), "sehir": SEHIR_MAP.get(sehir, sehir),
            "kosu_no": as_int(k.get("RACENO") or k.get("NO")), "saat": k.get("SAAT"),
            "mesafe": k.get("MESAFE"), "zemin": ac, "grup": k.get("GRUP_TR"),
            "grupkisa": k.get("GRUPKISA"), "irk": irk, "sinif": k.get("CINSDETAY_TR"),
            "cinsiyet": k.get("CINSIYET"), "going": going, "going_agirlik": going_ag,
            "hava": hava.get("HAVA_TR"), "sicaklik": hava.get("SICAKLIK"),
            "nem": hava.get("NEM"), "gece": hava.get("GECE"),
        }
        for a in k.get("atlar", []):
            yas, renk, cins = parse_yas(a.get("YAS"))
            rows.append({
                **rmeta,
                "at_kod": as_int(a.get("KOD")), "at_ad": a.get("AD"), "no": as_int(a.get("NO")),
                "start": a.get("START"), "yas": yas, "renk": renk, "cins": cins,
                "kilo": vir_float(a.get("KILO")), "fazla_kilo": vir_float(a.get("FAZLAKILO")),
                "apranti_ind": vir_float(a.get("APRANTIKILOINDIRIMI")),
                "handikap": a.get("HANDIKAP"),
                "jokey_kod": as_int(a.get("JOKEYKODU")), "jokey_ad": a.get("JOKEYADI"),
                "antrenor_kod": as_int(a.get("ANTRENORKODU")), "sahip_kod": as_int(a.get("SAHIPKODU")),
                "baba_kod": as_int(a.get("BABAKODU")), "anne_kod": as_int(a.get("ANNEKODU")),
                "taki": a.get("TAKI"), "son6": a.get("SON6"),
                "kosmaz": a.get("KOSMAZ"), "ekuri": a.get("EKURI"),
                "at_eniyi": zaman_sn(a.get("ENIYIDERECE")),
                "agf1": vir_float(a.get("AGF1")), "agfsira1": a.get("AGFSIRA1"),
                "ganyan_kapanis": None,                       # kapanis YOK (kosu olmadi)
                "ganyan_muhtemel": vir_float(a.get("GANYAN")),  # canli muhtemel
                "sonuc": np.nan, "fark": None, "zaman_sn": None,
                "kazandi": 0, "bugun": 1,
            })
    return rows


# ----------------------------- model -----------------------------
def egit_ve_uygula(feat):
    """feat = select_scope ciktisi (bugun dahil). Bot1 (<=2024) + Bot2 (2025) egit, bugune uygula.
    feat'e bot1/bot2/kamu yuzdeleri eklenmis kopya + (alpha,gamma,spanlar) doner."""
    feat = feat.copy()
    feat["yil"] = feat["dt"].dt.year
    for c in FEAT:
        feat[c] = pd.to_numeric(feat[c], errors="coerce").fillna(0.0)

    # --- Bot1: oran-kor conditional logit, gecmis tamamlanmis kosular <= 2024 ---
    tr = feat[(feat["bugun"] == 0) & (feat["yil"] <= 2024)].sort_values("race_kod").reset_index(drop=True)
    beta = fit_clogit(tr[FEAT].values, *race_struct(tr))

    # --- Bot2: harman agirligi, holdout 2025 (cross-fit sizinti yok) ---
    va = feat[(feat["bugun"] == 0) & (feat["yil"] == 2025)].copy()
    va = va[va["ganyan_muhtemel"] > 1]
    gw = va.groupby("race_kod")["kazandi"].transform("sum")
    sz = va.groupby("race_kod")["race_kod"].transform("size")
    va = va[(gw == 1) & (sz >= 4)].sort_values("race_kod").reset_index(drop=True)
    stv, szv, winv = race_struct(va)
    pfv = seg_softmax(va[FEAT].values @ beta, stv, szv)
    pmv = devig(va["ganyan_muhtemel"].values, stv, szv)
    alpha, gamma = fit_clogit(np.c_[np.log(pfv + 1e-12), np.log(pmv + 1e-12)], stv, szv, winv)

    # --- bugune uygula ---
    tg = feat[feat["bugun"] == 1].sort_values(["race_kod", "no"]).reset_index(drop=True)
    out = []
    for rk, g in tg.groupby("race_kod", sort=False):
        g = g.copy()
        st = np.array([0]); szc = np.array([len(g)])
        pf = seg_softmax(g[FEAT].values @ beta, st, szc)
        g["bot1"] = pf
        if (g["ganyan_muhtemel"] > 1).all():
            pm = devig(g["ganyan_muhtemel"].values, st, szc)
            g["kamu"] = pm
            g["bot2"] = seg_softmax(alpha * np.log(pf + 1e-12) + gamma * np.log(pm + 1e-12), st, szc)
        else:
            g["kamu"] = np.nan
            g["bot2"] = np.nan
        out.append(g)
    tg = pd.concat(out, ignore_index=True) if out else tg
    spanlar = (f"Bot1<=2024 ({tr.race_kod.nunique()} kosu), Bot2=2025 ({va.race_kod.nunique()} kosu)",
               float(alpha), float(gamma))
    return tg, spanlar


# ----------------------------- cikti -----------------------------
def yuzde(x):
    return "  -  " if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x*100:4.1f}"


def kosu_rapor(raw_kosu, scored):
    """Bir kosunun rapor metnini SATIR LISTESI olarak dondurur (gunluk + takip ortak kullanir).
    'Bot2%' = sistemin kendi AGF'si (harman win-olasiligi); tum atlar siralanir."""
    r0 = raw_kosu.iloc[0]
    saha = (raw_kosu["kosmaz"].astype(str).str.lower().isin(["true", "1"]) == False).sum()
    L = [f"\nKOSU {int(r0['kosu_no']):>2}  {r0['saat']}  {r0['mesafe']}m  "
         f"{str(r0['grup'])[:26]}  ({saha} at)"]
    if scored is None or len(scored) == 0:
        L.append("   [model KAPSAM DISI: " + ("Arap/diger irk" if r0["irk"] != "Ingiliz"
                 else "kucuk saha / veri yok") + " -> yalnizca kamu]")
        kk = raw_kosu.copy()
        kk["g"] = pd.to_numeric(kk["ganyan_muhtemel"], errors="coerce")
        kk = kk[~kk["kosmaz"].astype(str).str.lower().isin(["true", "1"])].sort_values("g")
        L.append(f"   {'no':>2} {'at':22s} {'AGF%':>6} {'oran':>6}")
        for _, a in kk.iterrows():
            L.append(f"   {str(a['no']):>2} {str(a['at_ad'])[:22]:22s} "
                     f"{yuzde((a['agf1'] or 0)/100 if pd.notna(a['agf1']) else None):>6} "
                     f"{('%.2f' % a['g']) if pd.notna(a['g']) else '  -':>6}")
        return L
    s = scored.sort_values("bot2", ascending=False)   # sistemin kendi AGF'sine gore sirala
    genc = float(s["ilk_kosu"].mean()) if "ilk_kosu" in s else 0.0
    ortk = float(pd.to_numeric(s.get("kariyer_kosu", pd.Series([np.nan])), errors="coerce").mean())
    if genc >= 0.34 or (not np.isnan(ortk) and ortk < 3):
        L.append(f"   [DUSUK GUVEN: ilk-kosu pay {genc*100:.0f}%, ort.gecmis {ortk:.1f} kosu "
                 f"-> Bot1 zayif, kamuya yaslan]")
    L.append(f"   {'no':>2} {'at':22s} {'Bot1%':>6} {'AGF%(sis)':>9} {'kamu%':>6} {'AGF%':>6} {'oran':>6}  iz")
    for _, a in s.iterrows():
        canli = (pd.notna(a["kamu"]) and a["kamu"] > 0 and a["bot1"] >= 1.5 * a["kamu"]
                 and a["bot1"] >= 0.10 and a["kamu"] < a["bot1"])
        favmi = pd.notna(a["kamu"]) and a["kamu"] == s["kamu"].max()
        iz = ">>CANLI" if (canli and not favmi) else ("F" if favmi else "")
        oran = a["ganyan_muhtemel"]
        L.append(f"   {str(a['no']):>2} {str(a['at_ad'])[:22]:22s} "
                 f"{yuzde(a['bot1']):>6} {yuzde(a['bot2']):>9} {yuzde(a['kamu']):>6} "
                 f"{yuzde((a['agf1'] or 0)/100 if pd.notna(a['agf1']) else None):>6} "
                 f"{('%.2f' % oran) if pd.notna(oran) else '  -':>6}  {iz}")
    return L


def hesapla(pist, ymd):
    """pist+ymd -> (raw=tum kart flatten, tg=Ingiliz puanli satirlar, (span,alpha,gamma)).
    gunluk.main ve defter.py AYNI cekirdegi kullanir (tek kaynak). Hata -> RuntimeError."""
    o = getjson(f"{BASE}/program/{ymd}/full/{pist}.json")
    if o.get("_hata"):
        raise RuntimeError(f"program cekilemedi ({pist} {ymd}): {o['_hata']}")
    raw = pd.DataFrame(flatten_program(o, pist, ymd))
    if raw.empty:
        raise RuntimeError("program bos.")
    # gecmis + bugun -> ozellikler (egitimle AYNI nokta-aninda mantik)
    hist = pd.read_csv(KOK / "veri" / "katilim.csv", low_memory=False)
    hist["bugun"] = 0
    # --- NOKTA-ANINDA KORUMASI (K36): arsivden, tahmin gununden ITIBAREN tum satirlari dusur.
    # Iki sizintiyi birden keser: (a) ayni kosu arsivde de varsa (gecmis --tarih / gun-ici veri
    # tazeleme) shift(1) mekanigi kosunun SONUCUNU bugunku ozelliklere tasirdi; (b) gecmis tarihli
    # calistirmada o gunden SONRAKI kosular ozelliklere girerdi. Normal kullanimda (arsiv < bugun)
    # hicbir satir dusmez -> davranis birebir ayni.
    hd = pd.to_datetime(hist["tarih"], format="%d/%m/%Y", errors="coerce")
    gun = pd.Timestamp(datetime.strptime(ymd, "%Y%m%d").date())
    cakisan = hd >= gun
    if cakisan.any():
        print(f"UYARI (sizinti korumasi): arsivde {gun:%Y-%m-%d} ve sonrasina ait "
              f"{int(cakisan.sum())} satir var -> ozellik hesabindan dusuldu (nokta-aninda).")
        hist = hist[~cakisan]
        hd = hd[~cakisan]
    # --- BAYATLIK UYARISI (K36): atlarin son kosulari arsivde yoksa form/kariyer sessizce eskir.
    arsiv_son = hd.max()
    print(f"arsiv son gunu: {arsiv_son:%Y-%m-%d}" if pd.notna(arsiv_son) else "arsiv BOS!")
    if pd.notna(arsiv_son) and (gun - arsiv_son).days > 3:
        print(f"UYARI: arsiv {(gun - arsiv_son).days} gun eski -> form/kariyer ozellikleri bayat. "
              f"Guncelle: python kod/guncelle.py (veya baslat_takip.bat zaten calistirir).")
    allrows = pd.concat([hist, raw], ignore_index=True)
    d = load_katilim(df=allrows)
    d = build_features(d)
    feat = select_scope(d)
    tg, span = egit_ve_uygula(feat)
    return raw, tg, span


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pist", help="pist KEY (or. ANKARA). bos -> bugunku yerli pistleri listeler")
    ap.add_argument("--tarih", default=date.today().isoformat(), help="YYYY-MM-DD")
    ap.add_argument("--kosu", type=int, default=None, help="sadece bu kosu no")
    args = ap.parse_args()
    ymd = datetime.strptime(args.tarih, "%Y-%m-%d").strftime("%Y%m%d")

    if not args.pist:
        print(f"{args.tarih} yerli pistler:")
        for key, ad in yerli_pistler(ymd):
            print(f"  {key:12s} {ad}")
        print("\n-> python gunluk.py --pist <KEY>")
        return

    pist = args.pist.strip().upper()
    if pist in EXCL:
        print(f"UYARI: {pist} 4 supheli pistten (sike soylentisi) -> egitim/tahmin KAPSAM DISI (K4).")
    try:
        raw, tg, (span, alpha, gamma) = hesapla(pist, ymd)
    except RuntimeError as e:
        print(e)
        return

    print("=" * 74)
    print(f"GUNLUK TAHMIN  {pist}  {args.tarih}   (cekim {datetime.now():%H:%M})")
    print(f"model: {span} | ALPHA(fund)={alpha:+.2f} GAMMA(piyasa)={gamma:+.2f}")
    print("UYARI: sistem +EV degil (6 test). Tahminler analiz/karsilastirma icin; KAR garantisi yok.")
    print("AGF%(sis)=sistemin kendi AGF'si (Bot2 harman win-olas.) | Bot1=oran-kor | tum atlar sirali")
    print("iz: F=kamu favorisi | >>CANLI=Bot1 kamuyu COK asiyor (non-favori). DIKKAT: bunlar")
    print("    backtest'te kontrarian= -%35 (K20) -> BAHIS sinyali DEGIL, 'kendi yarginla bak' isareti.")
    print("=" * 74)

    # bugunun puanlari -> race_kod -> df
    skor = {rk: g for rk, g in tg.groupby("race_kod")} if len(tg) else {}
    raw["kosu_no_i"] = pd.to_numeric(raw["kosu_no"], errors="coerce")
    for rk, gkosu in sorted(raw.groupby("race_kod"), key=lambda x: x[1]["kosu_no_i"].iloc[0]):
        if args.kosu is not None and int(gkosu["kosu_no_i"].iloc[0]) != args.kosu:
            continue
        print("\n".join(kosu_rapor(gkosu, skor.get(rk))))


if __name__ == "__main__":
    main()
