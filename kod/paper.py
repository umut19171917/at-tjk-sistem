"""
paper.py — 12 HAFTALIK ON-KAYITLI PAPER TEST (K42). Gercek para DEGIL; bahisler.csv'den
ve kagit-defterden (defter.csv) TAMAMEN AYRI: kendi dosyasi (veri/paper_kupon.csv) +
kendi sayfasi (raporlar/paper.html). Canli takip/defter arayuzune dokunmaz.

ON-KAYIT (degistirilemez; K42): baslangic 2026-07-04, bitis 2026-09-25 (12 hafta).
Kupon 15 TL flat; hafta (ISO) butcesi 3000 TL — asilacaksa yeni kupon ACILMAZ (sira S1..S5).
(15 TL: plase_test olcumuyle boyutlandi — CANLI kosularin ~%80'inde var -> ~3.9 kupon/kosu;
 25 TL'de hafta ~4.400 TL olur, butce kurali hafta sonlarini sistematik keserdi = orneklem yanlisi.)
Stratejiler (kosu basina en fazla 1'er kupon; kayit ani = takip tetigi, yaristan ~5 dk once):
  S1 model top-pick (Bot2 max) GANYAN      S2 ayni atin PLASE'si (yalniz saha>=7)
  S3 kamu favorisi (kamu% max) GANYAN      S4 ayni atin PLASE'si (yalniz saha>=7)
  S5 CANLI (canli_seri; birden coksa Bot1 max) GANYAN — yoksa kupon yok
(saha>=7 sarti veriden: plase havuzu 2025-26 testinde YALNIZ 7+ atli kosularda bulundu.)
Odeme: ganyan = kapanis ganyan; plase = BAHISLER_TR temettusu. At kosmadi / plase havuzu
yok -> kupon IPTAL (iade: getiri = miktar). GECMIS-VERI BEKLENTILERI (plase_test.py, test
2025-26): S1 -28.0% / S3 -28.7% / S5 -33.6% / S2 -12.5% / S4 -14.0% — hepsi NEGATIF;
amac kar degil: canli hatti dogrulamak + plase'nin ilk canli olcumu.

Kullanim: takip.py kayit/sonuclamayi otomatik yapar. Elle:
    python kod/paper.py ozet | html | sonucla
Cift-tik: paper_goster.bat
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from gunluk import getjson, BASE, canli_seri  # noqa: E402
from duzlestir import vir_float  # noqa: E402
from temettu import gan_plase  # noqa: E402

PAPER = KOK / "veri" / "paper_kupon.csv"
HTMLP = KOK / "raporlar" / "paper.html"
KUPON_TL = 15.0            # boyutlandirma gerekce: docstring (25'te butce orneklemi keserdi)
HAFTA_BUTCE = 3000.0
BAS, BIT = "2026-07-04", "2026-09-25"
KOLP = ["id", "kayit_ts", "tarih", "hafta", "pist", "kosu_no", "race_kod", "strateji",
        "tur", "at_no", "at_ad", "miktar", "oran_kayit", "getiri", "durum"]
BEKLENTI = {"S1": "top-pick ganyan", "S2": "top-pick plase", "S3": "favori ganyan",
            "S4": "favori plase", "S5": "CANLI ganyan"}


def _oku():
    if PAPER.exists():
        return pd.read_csv(PAPER, low_memory=False)
    return pd.DataFrame(columns=KOLP)


def _yaz(df):
    df.to_csv(PAPER, index=False, encoding="utf-8", columns=KOLP)


def _hafta(tarih):
    t = pd.Timestamp(str(tarih))
    return f"{t.isocalendar().year}-W{t.isocalendar().week:02d}"


# ----------------------------- kupon uretimi -----------------------------
def kupon_uret(kosu_tg, tarih, pist):
    """Tek kosunun puanli (tg) satirlarindan S1-S5 kuponlarini yazar (takip tetiginde).
    Pencere disi / mukerrer / butce-asimi -> sessizce uretmez. Doner: yazilan kupon sayisi."""
    if kosu_tg is None or len(kosu_tg) == 0 or not (BAS <= str(tarih) <= BIT):
        return 0
    k = kosu_tg.copy()
    for c in ["bot1", "bot2", "kamu", "ganyan_muhtemel"]:
        k[c] = pd.to_numeric(k[c], errors="coerce")
    if k["bot2"].isna().all() or k["kamu"].isna().all():
        return 0                                            # puanlanamamis kosu
    rk = int(k["race_kod"].iloc[0])
    saha = len(k)
    top = k.loc[k["bot2"].idxmax()]
    fav = k.loc[k["kamu"].idxmax()]
    cm = canli_seri(k)
    canli = k[cm].loc[k[cm]["bot1"].idxmax()] if cm.any() else None

    adaylar = [("S1", "ganyan", top)]
    if saha >= 7:                       # plase havuzu yalniz 7+ sahada (plase_test olcumu)
        adaylar.append(("S2", "plase", top))
    adaylar.append(("S3", "ganyan", fav))
    if saha >= 7:
        adaylar.append(("S4", "plase", fav))
    if canli is not None:
        adaylar.append(("S5", "ganyan", canli))

    b = _oku()
    hafta = _hafta(tarih)
    harcanan = float(pd.to_numeric(b.loc[b["hafta"] == hafta, "miktar"], errors="coerce").sum())
    var = set(zip(b["race_kod"], b["strateji"])) if len(b) else set()
    nid = int(pd.to_numeric(b["id"], errors="coerce").max() + 1) if len(b) else 1
    yeni = []
    for st, tur, at in adaylar:
        if (rk, st) in var:
            continue                                        # ayni kosu+strateji bir kez
        if harcanan + KUPON_TL > HAFTA_BUTCE:
            print(f"  paper: {hafta} butcesi doldu ({harcanan:.0f} TL) -> {st} acilmadi")
            continue
        yeni.append({"id": nid, "kayit_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                     "tarih": tarih, "hafta": hafta, "pist": pist,
                     "kosu_no": at["kosu_no"], "race_kod": rk, "strateji": st, "tur": tur,
                     "at_no": int(at["no"]), "at_ad": at["at_ad"], "miktar": KUPON_TL,
                     "oran_kayit": at["ganyan_muhtemel"], "getiri": np.nan, "durum": "acik"})
        nid += 1
        harcanan += KUPON_TL
    if yeni:
        _yaz(pd.concat([b, pd.DataFrame(yeni)], ignore_index=True))
    return len(yeni)


# ----------------------------- sonuclama -----------------------------
def sonucla_paper():
    """Acik kuponlari sonuclar feed'iyle kapatir. Doner: kapatilan kupon sayisi."""
    b = _oku()
    if b.empty:
        return 0
    acik = b[b["durum"] == "acik"]
    if acik.empty:
        return 0
    kapanan = 0
    for (tarih, pist), grp in acik.groupby(["tarih", "pist"]):
        ymd = pd.Timestamp(str(tarih)).strftime("%Y%m%d")
        o = getjson(f"{BASE}/sonuclar/{ymd}/full/{pist}.json")
        if o.get("_hata"):
            continue
        for k in o.get("kosular", []):
            try:
                rk = int(k.get("KOD"))
            except (TypeError, ValueError):
                continue
            idx = grp.index[grp["race_kod"] == rk]
            if len(idx) == 0:
                continue
            _, plase = gan_plase(k.get("BAHISLER_TR"))
            atlar = {}
            for a in k.get("atlar", []):
                try:
                    no = int(a.get("NO"))
                except (TypeError, ValueError):
                    continue
                atlar[no] = (pd.to_numeric(a.get("SONUC"), errors="coerce"),
                             vir_float(a.get("GANYAN")),
                             str(a.get("KOSMAZ", "")).lower() in ("true", "1"))
            if not atlar or all(pd.isna(v[0]) and not v[2] for v in atlar.values()):
                continue                                    # kosu henuz sonuclanmamis
            for i in idx:
                no = int(b.at[i, "at_no"])
                mik = float(b.at[i, "miktar"])
                son, gan, kosmaz = atlar.get(no, (np.nan, None, False))
                if kosmaz or no not in atlar:
                    b.at[i, "getiri"], b.at[i, "durum"] = mik, "iptal"      # iade
                elif b.at[i, "tur"] == "ganyan":
                    kaz = pd.notna(son) and son == 1
                    b.at[i, "getiri"] = round(mik * gan, 2) if (kaz and gan) else 0.0
                    b.at[i, "durum"] = "kazandi" if kaz else "kaybetti"
                else:                                       # plase
                    if not plase:
                        b.at[i, "getiri"], b.at[i, "durum"] = mik, "iptal"  # havuz yok -> iade
                    elif no in plase:
                        b.at[i, "getiri"], b.at[i, "durum"] = round(mik * plase[no], 2), "kazandi"
                    else:
                        b.at[i, "getiri"], b.at[i, "durum"] = 0.0, "kaybetti"
                kapanan += 1
    if kapanan:
        _yaz(b)
        html_yaz(b)
    return kapanan


# ----------------------------- ozet + html -----------------------------
def _tablolar(b):
    b = b.copy()
    for c in ["miktar", "getiri"]:
        b[c] = pd.to_numeric(b[c], errors="coerce")
    s = b[b["durum"].isin(["kazandi", "kaybetti"])]         # iptal = iade, ROI'ye girmez
    st_rows, hf_rows = [], []
    for st in ["S1", "S2", "S3", "S4", "S5"]:
        g = s[s["strateji"] == st]
        if len(g) == 0:
            st_rows.append((st, BEKLENTI[st], 0, np.nan, np.nan, np.nan))
            continue
        yat, don = g["miktar"].sum(), g["getiri"].sum()
        st_rows.append((st, BEKLENTI[st], len(g), (g["durum"] == "kazandi").mean() * 100,
                        don - yat, (don - yat) / yat * 100))
    kum = 0.0
    for hf, g in b.groupby("hafta"):
        gs = g[g["durum"].isin(["kazandi", "kaybetti"])]
        yat = float(g["miktar"].sum())                       # butce kullanimi (iptal dahil yatti)
        net = float(gs["getiri"].sum() - gs["miktar"].sum())
        kum += net
        hf_rows.append((hf, len(g), yat, net, kum, int((g["durum"] == "acik").sum())))
    return st_rows, hf_rows, s


def ozet():
    b = _oku()
    print("=" * 66)
    print(f"PAPER TEST (K42) — {BAS} .. {BIT}  kupon {KUPON_TL:.0f} TL, hafta {HAFTA_BUTCE:.0f} TL")
    print("KAR AMACI YOK: gecmis-veri beklentileri negatif; olculen sey canli hat + plase.")
    print("=" * 66)
    if b.empty:
        print("henuz kupon yok (ilk yaris gununde takip otomatik uretir).")
        return
    st_rows, hf_rows, s = _tablolar(b)
    print(f"kupon: {len(b)} (acik {int((b['durum']=='acik').sum())}, "
          f"iptal {int((b['durum']=='iptal').sum())})")
    print(f"\n{'':4s}{'strateji':18s} {'n':>5s} {'isabet%':>8s} {'net TL':>9s} {'ROI%':>8s}")
    for st, ad, n, hit, net, roi in st_rows:
        if n:
            print(f"  {st:2s} {ad:18s} {n:>5d} {hit:>7.1f}% {net:>+9.2f} {roi:>+7.1f}%")
        else:
            print(f"  {st:2s} {ad:18s} {0:>5d}      -         -       -")
    print(f"\n{'hafta':10s} {'kupon':>6s} {'yatan':>8s} {'net':>9s} {'kumulatif':>10s} {'acik':>5s}")
    for hf, n, yat, net, kum, ac in hf_rows:
        print(f"{hf:10s} {n:>6d} {yat:>8.0f} {net:>+9.2f} {kum:>+10.2f} {ac:>5d}")


def html_yaz(b=None, ac=False):
    """AYRI sayfa: raporlar/paper.html (defter.html'e dokunmaz)."""
    if b is None:
        b = _oku()
    css = ("<meta charset='utf-8'><title>Paper Test K42</title><style>"
           "body{font-family:Segoe UI,Arial,sans-serif;margin:20px;color:#222;}"
           "h2{margin:0 0 2px;} h3{margin:16px 0 3px;font-size:15px;}"
           "table{border-collapse:collapse;} td,th{border:1px solid #ccc;padding:3px 9px;"
           "text-align:right;font-size:13px;} th{background:#eee;} td.l,th.l{text-align:left;}"
           "tr.k{background:#d7f7d7;} tr.i{background:#f2f2f2;color:#777;}"
           ".not{color:#666;font-size:12px;margin:2px 0 12px;}.neg{color:#b30000;}.poz{color:#0a0;}"
           "</style>")
    H = [css, "<h2>Paper Test (K42) — 12 hafta, on-kayitli</h2>",
         f"<div class=not>{BAS} .. {BIT} &mdash; kupon {KUPON_TL:.0f} TL, hafta butcesi "
         f"{HAFTA_BUTCE:.0f} TL &mdash; guncelleme {datetime.now():%Y-%m-%d %H:%M}<br>"
         "KAR AMACI YOK: gecmis-veri beklentileri negatif (K42); olculen sey canli hattin "
         "kalibrasyonu + PLASE'nin ilk canli olcumu. Kurallar test boyunca DEGISMEZ.</div>"]
    if b.empty:
        H.append("<p>henuz kupon yok (ilk yaris gununde takip otomatik uretir).</p>")
    else:
        st_rows, hf_rows, s = _tablolar(b)
        H.append("<h3>Strateji durumu</h3><table><tr><th>st</th><th class=l>tanim</th>"
                 "<th>n</th><th>isabet%</th><th>net TL</th><th>ROI%</th></tr>")
        for st, ad, n, hit, net, roi in st_rows:
            if n:
                c = "poz" if net >= 0 else "neg"
                H.append(f"<tr><td>{st}</td><td class=l>{ad}</td><td>{n}</td>"
                         f"<td>{hit:.1f}</td><td class={c}>{net:+.2f}</td>"
                         f"<td class={c}>{roi:+.1f}</td></tr>")
            else:
                H.append(f"<tr><td>{st}</td><td class=l>{ad}</td><td>0</td>"
                         f"<td>-</td><td>-</td><td>-</td></tr>")
        H.append("</table><h3>Haftalik</h3><table><tr><th class=l>hafta</th><th>kupon</th>"
                 "<th>yatan</th><th>net</th><th>kumulatif</th><th>acik</th></tr>")
        for hf, n, yat, net, kum, ac in hf_rows:
            c = "poz" if kum >= 0 else "neg"
            H.append(f"<tr><td class=l>{hf}</td><td>{n}</td><td>{yat:.0f}</td>"
                     f"<td>{net:+.2f}</td><td class={c}>{kum:+.2f}</td><td>{ac}</td></tr>")
        H.append("</table><h3>Son kuponlar</h3><table><tr><th>id</th><th class=l>tarih</th>"
                 "<th class=l>pist</th><th>kosu</th><th>st</th><th class=l>tur</th><th>no</th>"
                 "<th class=l>at</th><th>miktar</th><th>getiri</th><th class=l>durum</th></tr>")
        for _, r in b.sort_values("id", ascending=False).head(40).iterrows():
            cls = " class=k" if r["durum"] == "kazandi" else (" class=i" if r["durum"] == "iptal" else "")
            get = f"{r['getiri']:.2f}" if pd.notna(pd.to_numeric(r["getiri"], errors="coerce")) else "-"
            H.append(f"<tr{cls}><td>{int(r['id'])}</td><td class=l>{r['tarih']}</td>"
                     f"<td class=l>{r['pist']}</td><td>{r['kosu_no']}</td><td>{r['strateji']}</td>"
                     f"<td class=l>{r['tur']}</td><td>{int(r['at_no'])}</td>"
                     f"<td class=l>{str(r['at_ad'])[:22]}</td><td>{float(r['miktar']):.0f}</td>"
                     f"<td>{get}</td><td class=l>{r['durum']}</td></tr>")
        H.append("</table>")
    HTMLP.parent.mkdir(parents=True, exist_ok=True)
    HTMLP.write_text("\n".join(H), encoding="utf-8")
    if ac:
        import webbrowser
        try:
            webbrowser.open(HTMLP.as_uri())
        except Exception:
            pass
    return HTMLP


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("komut", choices=["ozet", "html", "sonucla"])
    args = ap.parse_args()
    if args.komut == "ozet":
        ozet()
    elif args.komut == "html":
        p = html_yaz(ac=True)
        print(f"yazildi + acildi: {p}")
    elif args.komut == "sonucla":
        n = sonucla_paper()
        print(f"paper: {n} kupon kapatildi.")


if __name__ == "__main__":
    main()
