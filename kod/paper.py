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
import rapor_ortak as ro  # noqa: E402

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
    # ON-KAYIT KORUMASI (K42/K46): test YALNIZ Ingiliz kosularinda on-kaydedildi. K46 ile
    # canli sisteme Arap modeli eklendi ama 12 haftalik test ortasinda kapsam DEGISTIRILEMEZ —
    # Arap kosusu paper kuponu uretemez (kural degisikligi = deney gecersiz).
    if "irk" in kosu_tg.columns and str(kosu_tg["irk"].iloc[0]) != "Ingiliz":
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
    """K55: Altili sayfasiyla AYNI duzen — bizim atimiz + SISTEM SIRASI, kazanan at +
    sistem/kamu sirasi + ganyan orani, kupon bedeli + odul, altta TOPLAM.
    Zenginlestirme defter.csv'den (salt-okunur); paper_kupon.csv DEGISMEZ."""
    if b is None:
        b = _oku()
    for c in ["kosu_no", "race_kod", "at_no", "miktar", "getiri", "oran_kayit"]:
        if c in b.columns:
            b[c] = pd.to_numeric(b[c], errors="coerce")

    H = ["<meta charset='utf-8'><title>Paper Test</title>", ro.ORTAK_CSS,
         "<h2>PAPER TEST (K42) &mdash; ganyan &amp; plase kuponlari</h2>",
         f"<div class=not>guncelleme {datetime.now():%d.%m.%Y %H:%M} &mdash; "
         "<b>GERCEK BAHIS DEGIL</b>, kagit uzerinde on-kayitli deney (K42/K48). "
         f"Pencere {BAS} .. {BIT}, kupon {KUPON_TL:.0f} TL, hafta butcesi {HAFTA_BUTCE:.0f} TL.<br>"
         "Stratejiler: <b>S1</b> model top-pick GANYAN &middot; <b>S2</b> top-pick PLASE &middot; "
         "<b>S3</b> kamu favorisi GANYAN &middot; <b>S4</b> favori PLASE &middot; "
         "<b>S5</b> CANLI isaretli at GANYAN.<br>"
         "Gecmis-veri beklentileri NEGATIF (S1 &minus;%28 / S3 &minus;%29 / S5 &minus;%34 / "
         "S2 &minus;%12,5 / S4 &minus;%14); olculen sey canli hat + plase.</div>"]

    if b.empty:
        H.append("<p>Henuz kupon yok.</p>")
        HTMLP.parent.mkdir(parents=True, exist_ok=True)
        HTMLP.write_text("\n".join(H), encoding="utf-8")
        return HTMLP

    s = b[b["durum"].isin(["kazandi", "kaybetti"])]      # iptal = iade, ROI'ye girmez

    def toplam_blok(baslik):
        H2 = ["<div class=toplam>", f"<b>{baslik}</b><br>"]
        H2.append("<table style='margin-top:6px'><tr><th>strateji</th><th class=l>tanim</th>"
                  "<th>kupon</th><th>isabet</th><th>bedel</th><th>odul</th><th>net</th>"
                  "<th>ROI</th></tr>")
        gen_b = gen_o = 0.0
        for st in ["S1", "S2", "S3", "S4", "S5"]:
            g = s[s["strateji"] == st]
            if len(g) == 0:
                H2.append(f"<tr><td>{st}</td><td class=l>{BEKLENTI[st]}</td>"
                          "<td>0</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>")
                continue
            bed, od = g["miktar"].sum(), g["getiri"].sum()
            gen_b += bed
            gen_o += od
            net = od - bed
            isb = (g["durum"] == "kazandi").mean() * 100
            cls = "poz" if net >= 0 else "neg"
            H2.append(f"<tr><td><b>{st}</b></td><td class=l>{BEKLENTI[st]}</td>"
                      f"<td>{len(g)}</td><td>%{isb:.1f}</td><td>{ro.para(bed)}</td>"
                      f"<td>{ro.para(od)}</td><td class={cls}>{ro.para(net, isaret=True)}</td>"
                      f"<td class={cls}>%{100*net/bed:+.1f}</td></tr>")
        H2.append("</table>")
        gnet = gen_o - gen_b
        cls = "poz" if gnet >= 0 else "neg"
        H2.append(f"<hr style='border:none;border-top:1px solid #ddd;margin:8px 0'>"
                  f"<b>GENEL TOPLAM</b> &nbsp; {len(s)} sonuclanan kupon &nbsp; "
                  f"bedel {ro.para(gen_b)} &nbsp; odul {ro.para(gen_o)} &nbsp; net "
                  f"<span class='{cls} buyuk'>{ro.para(gnet, isaret=True)}</span>"
                  + (f" &nbsp;<span class=k>(ROI %{100*gnet/gen_b:+.1f})</span>" if gen_b else ""))
        H2.append("</div>")
        return H2

    H += toplam_blok("TOPLAM DURUM")

    # ---- haftalik ozet ----
    H.append("<h3>Haftalik</h3><div class=kart><table>"
             "<tr><th class=l>hafta</th><th>kupon</th><th>bedel</th><th>odul</th>"
             "<th>net</th><th>kumulatif</th></tr>")
    kum = 0.0
    for hf, g in b.groupby("hafta"):
        gs = g[g["durum"].isin(["kazandi", "kaybetti"])]
        bed = float(gs["miktar"].sum())
        od = float(gs["getiri"].sum())
        net = od - bed
        kum += net
        cls = "poz" if kum >= 0 else "neg"
        H.append(f"<tr><td class=l>{hf}</td><td>{len(g)}</td><td>{ro.para(bed)}</td>"
                 f"<td>{ro.para(od)}</td><td>{ro.para(net, isaret=True)}</td>"
                 f"<td class={cls}><b>{ro.para(kum, isaret=True)}</b></td></tr>")
    H.append("</table></div>")

    # ---- TUM kuponlar (yeni ustte) ----
    H.append(f"<h3>Tum kuponlar ({len(b)} kayit, yeni ustte)</h3>")
    H.append("<div class=kart><table><tr><th class=l>tarih</th><th class=l>sehir</th>"
             "<th>kosu</th><th>str</th><th class=l>tur</th>"
             "<th class=l>BIZIM ATIMIZ <span class=mini>(no / sistem sirasi)</span></th>"
             "<th class=l>KAZANAN AT</th><th>kaz.<br>sistem</th><th>kaz.<br>kamu</th>"
             "<th>ganyan<br>orani</th><th>bedel</th><th>odul</th><th class=l>sonuc</th></tr>")
    for _, r in b.sort_values("id", ascending=False).iterrows():
        rk = int(r["race_kod"]) if pd.notna(r["race_kod"]) else None
        no = int(r["at_no"]) if pd.notna(r["at_no"]) else None
        bi = ro.at_bilgi(rk, no) if (rk and no) else {"sis": None, "ad": None}
        bizim = f"<b>{no}</b> {str(r['at_ad'])[:18]} <span class=mini>({ro.sira_str(bi['sis'])})</span>"
        kz = ro.kazanan_bilgi(rk) if rk else None
        if kz:
            kz_html = f"<b>{kz['no']}</b> {str(kz['ad'])[:18]}"
            kz_sis, kz_kamu, kz_oran = (ro.sira_str(kz["sis"]), ro.sira_str(kz["kamu"]),
                                        ro.oran_str(kz["oran"]))
        else:
            kz_html, kz_sis, kz_kamu, kz_oran = "<span class=bek>-</span>", "-", "-", "-"
        d = str(r["durum"])
        if d == "kazandi":
            scls, stxt = "tut", "KAZANDI"
        elif d == "kaybetti":
            scls, stxt = "kac", "kaybetti"
        elif d == "iptal":
            scls, stxt = "bek", "iptal (iade)"
        else:
            scls, stxt = "bek", "bekliyor"
        tarih_tr = pd.Timestamp(str(r["tarih"])).strftime("%d.%m.%Y")
        H.append(f"<tr><td class=l>{tarih_tr}</td><td class=l>{r['pist']}</td>"
                 f"<td>{int(r['kosu_no']) if pd.notna(r['kosu_no']) else '-'}</td>"
                 f"<td><b>{r['strateji']}</b></td><td class=l>{r['tur']}</td>"
                 f"<td class=l>{bizim}</td><td class=l>{kz_html}</td>"
                 f"<td>{kz_sis}</td><td>{kz_kamu}</td><td>{kz_oran}</td>"
                 f"<td>{ro.para(r['miktar'])}</td>"
                 f"<td>{ro.para(r['getiri']) if pd.notna(r['getiri']) else '-'}</td>"
                 f"<td class={scls}>{stxt}</td></tr>")
    H.append("</table></div>")

    H += toplam_blok("TOPLAM DURUM (liste sonu)")

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
