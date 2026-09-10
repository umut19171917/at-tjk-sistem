"""
genislik_taramasi.py — SABIT GENISLIKLI Altili kuponlarinin kar/zarar taramasi (K164).

SORU: "her ayaga sabit k at yazsaydik ne olurdu?" k = 3, 4, 5, 6.

YONTEM (canli veriye dayanir, arsiv backtestine DEGIL):
  - Secim: `veri/altili_kupon_ani.csv` — kuponun KURULDUGU andaki puan vektoru. Yani karar,
    o gun gercekten elimizde olan bilgiyle veriliyor; K130 sizintisi (arsivdeki ganyan_muhtemel
    == kapanis) bu dosyada YOKTUR.
  - Kazanan: `altili_canli.kazananlar_kumesi` — yani EKURI genisletmesi dahil, canli sistemin
    bugun kullandigi kuralin AYNISI (K162/K162-EK).
  - Odul: yalnizca 6/6'da, o Altili'nin RESMI temettusu (`rapor_ortak.altili_odeme`, onbellek).
  - Bedel: GERCEK kombinasyon x birim fiyat. k**6 DEGIL -- ayakta k'dan az at kosuyorsa
    sahadaki hepsi yazilir; o ayak hem ucuzlar hem kesin tutar. Olculdu: ayaklarin %0,8'inde
    5'ten, %5,6'sinda 6'dan az at var. Ikisi de min(k, sahadaki) ile hesaplanir ki maliyet
    ve isabet TUTARLI olsun.

DURUSTLUK KURALI — "BILINMEZ" OLAY ATILIR, TAHMIN EDILMEZ:
  Bir Altili ancak 6 ayaginin da (a) kupon-ani fotografi VE (b) bilinen kazanani varsa sayilir.
  Eksik olan pencere iyimser/kotumser bantla DOLDURULMAZ, tamamen disarida birakilir.

OLAY KUMESI ZEMINE GORE DEGISIR — kiyas yaparken dikkat:
  30 dk fotografi 25 Tem'de, 15 dk fotografi 15 Agu'da basladi. bot1@30 ve bot2@30 AYNI
  olaylari gorur (dogrudan kiyaslanabilir); bot2@15 daha KISA bir pencereyi gorur.

SALT-OKUNUR: hicbir dosyaya yazmaz (--detay disinda; o da yalniz raporlar/ altina HTML uretir).
Elle: python kod/genislik_taramasi.py [--k 3,4,5,6] [--detay]
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
import rapor_ortak as ro                                     # noqa: E402
from altili_canli import kazananlar_kumesi                   # noqa: E402

ANI = KOK / "veri" / "altili_kupon_ani.csv"
SONUC = KOK / "veri" / "ham" / "sonuclar"
HTML = KOK / "raporlar" / "genislik_detay.html"

# Hangi cetvel hangi ana bakar: (etiket, puan sutunu, dk grubu)
ZEMIN = [("bot1 @30dk", "bot1", 30),
         ("bot2 @30dk", "bot2", 30),
         ("bot2 @15dk", "bot2", 15)]


def _kazananlar():
    """race_kod -> {kazanan no'lari}. EKURI genisletmesi dahil (canli kuralin aynisi)."""
    kaz = {}
    for f in sorted(SONUC.glob("*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                kaz.update(kazananlar_kumesi(json.load(fh)))
        except Exception:                                    # noqa: BLE001 -- bozuk dosya atlanir
            continue
    return kaz


def olaylar(k_listesi=(3, 4, 5, 6)):
    """(zemin, k) -> her Altili icin tek tek kayit listesi. Ozetler bundan turetilir."""
    ani = pd.read_csv(ANI, low_memory=False)
    for c in ("seq", "dk_grup", "ayak", "race_kod", "no", "bot1", "bot2"):
        ani[c] = pd.to_numeric(ani[c], errors="coerce")
    kaz = _kazananlar()

    cikti = {}
    for etiket, sut, dkg in ZEMIN:
        g = ani[ani["dk_grup"] == dkg]
        for (tarih, pist, seq), pen in g.groupby(["tarih", "pist", "seq"]):
            ayaklar = sorted(pen["ayak"].dropna().unique())
            if len(ayaklar) != 6:
                continue                                     # eksik fotograf -> olay ATILIR
            siralar, ok = [], True
            for a in ayaklar:
                sr = pen[pen["ayak"] == a].dropna(subset=[sut]).sort_values(sut, ascending=False)
                rk = sr["race_kod"].dropna()
                if sr.empty or rk.empty or int(rk.iloc[0]) not in kaz:
                    ok = False                               # sonucu bilinmeyen ayak -> ATILIR
                    break
                siralar.append((sr, kaz[int(rk.iloc[0])]))
            if not ok:
                continue
            birim = ro.birim_fiyat(pist)
            res = ro.altili_odeme(tarih, pist, int(seq), cek=False)
            temettu = float(res["temettu"]) if res["temettu"] else 0.0
            devir = bool(res["devir"])
            for k in k_listesi:
                secimler = [{int(x) for x in sr.head(k)["no"]} for sr, _ in siralar]
                kombo = 1
                for s in secimler:
                    kombo *= len(s)
                tut = [bool(s & w) for s, (_, w) in zip(secimler, siralar)]
                bedel = kombo * birim
                tam = all(tut)
                cikti.setdefault((etiket, k), []).append({
                    "tarih": str(tarih), "pist": pist, "seq": int(seq), "kombo": kombo,
                    "birim": birim, "bedel": bedel, "tam": tam, "isabet": sum(tut),
                    "temettu": temettu, "devir": devir,
                    "odul": temettu if tam else 0.0})
    return cikti


def ozet(kayitlar):
    b = sum(o["bedel"] for o in kayitlar)
    d = sum(o["odul"] for o in kayitlar)
    tam = [o for o in kayitlar if o["tam"]]
    return {"kupon": len(kayitlar), "tam": len(tam), "bedel": b, "odul": d, "net": d - b,
            "roi": (100 * (d - b) / b) if b else 0.0,
            "ayak": sum(o["isabet"] for o in kayitlar),
            "karli": [o for o in tam if o["odul"] > o["bedel"]], "tamlar": tam}


# ----------------------------- konsol -----------------------------
def konsol(cikti, ks):
    bas = (f"{'zemin / genislik':<22} {'kupon':>5} {'6/6':>5} {'ayak':>7} {'kupon TL':>11} "
           f"{'bedel':>14} {'odul':>14} {'net':>15} {'ROI':>9}")
    print("\n" + "=" * len(bas))
    print("SABIT GENISLIKLI ALTILI — kupon-ani verisiyle, EKURI kurali dahil (K164)")
    print("=" * len(bas))
    print(bas)
    print("-" * len(bas))
    for etiket, _, _ in ZEMIN:
        for k in ks:
            r = cikti.get((etiket, k))
            if not r:
                continue
            o = ozet(r)
            ayak = f"{100 * o['ayak'] / (6 * o['kupon']):.1f}%"
            print(f"{etiket + '  sabit-' + str(k):<22} {o['kupon']:>5} {o['tam']:>5} {ayak:>7} "
                  f"{o['bedel'] / o['kupon']:>11,.0f} {o['bedel']:>14,.0f} {o['odul']:>14,.0f} "
                  f"{o['net']:>+15,.0f} {'%' + format(o['roi'], '+.1f'):>9}")
        print()
    print("=" * len(bas))


# ----------------------------- HTML -----------------------------
CSS = """<style>
:root{--bg:#fff;--kart:#fff;--bd:#ddd;--tx:#1a1a1a;--k:#555;--mini:#777;
 --th:#f2f2f2;--td:#e4e4e4;--poz:#0a7d0a;--neg:#c62828;}
body{font-family:"Segoe UI",Arial,sans-serif;margin:18px;color:var(--tx);background:var(--bg);}
h2{margin:0 0 4px;font-size:19px;} h3{margin:22px 0 6px;font-size:15px;}
.alt{font-weight:normal;font-size:14px;color:var(--k);}
.kart{background:var(--kart);border:1px solid var(--bd);border-radius:8px;padding:10px 14px;
 margin:12px 0;box-shadow:0 1px 3px rgba(0,0,0,.06);}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;}
td,th{border:1px solid var(--td);padding:4px 8px;font-size:12.5px;text-align:right;}
th{background:var(--th);font-weight:600;text-align:right;}
td.l,th.l{text-align:left;}
.poz{color:var(--poz);} .neg{color:var(--neg);}
.k{font-size:12px;color:var(--k);} .mini{font-size:11px;color:var(--mini);}
.vurgu{background:#000;color:#fff;padding:1px 6px;border-radius:3px;font-weight:bold;}
tr.top td{background:#f2f2f2;font-weight:bold;border-top:2px solid #000;}
tr.gt td{background:#000;color:#fff;font-weight:bold;}
tr.gt td.poz{color:#7ee787;} tr.gt td.neg{color:#ffa198;}
.wrap{overflow-x:auto;} .uyari{border-left:4px solid #000;padding:6px 12px;margin:8px 0;
 background:#f7f7f7;font-size:12.5px;}
</style>"""


def _p(x, isaret=False):
    s = f"{x:,.0f}".replace(",", ".")
    return ("+" if (isaret and x >= 0) else "") + s


def detay_html(cikti, ks):
    H = ["<meta charset='utf-8'><title>Genislik Taramasi</title>", CSS,
         "<h2>SABIT GENISLIKLI ALTILI &mdash; tam dokum <span class=alt>(k = "
         + ", ".join(str(k) for k in ks) + ")</span></h2>",
         f"<div class=mini style='margin:-2px 0 12px'>kupon-ani verisi &middot; EKURI kurali "
         f"dahil (K162) &middot; uretim {datetime.now():%d.%m.%Y %H:%M} &middot; "
         f"<code>kod/genislik_taramasi.py</code></div>"]

    # --- ozet matris ---
    H.append("<h3>Ozet &mdash; 12 hucre</h3><div class=kart><div class=wrap><table>")
    H.append("<tr><th class=l>zemin</th><th>genislik</th><th>kupon</th><th>6/6</th>"
             "<th>ayak isabeti</th><th>kupon bedeli</th><th>toplam bedel</th><th>odul</th>"
             "<th>NET</th><th>ROI</th></tr>")
    for etiket, _, _ in ZEMIN:
        for k in ks:
            r = cikti.get((etiket, k))
            if not r:
                continue
            o = ozet(r)
            cls = "poz" if o["net"] >= 0 else "neg"
            H.append(f"<tr><td class=l>{etiket}</td><td><b>sabit-{k}</b></td>"
                     f"<td>{o['kupon']}</td><td>{o['tam']}</td>"
                     f"<td>%{100*o['ayak']/(6*o['kupon']):.1f}</td>"
                     f"<td>{_p(o['bedel']/o['kupon'])} &#8378;</td>"
                     f"<td>{_p(o['bedel'])} &#8378;</td><td>{_p(o['odul'])} &#8378;</td>"
                     f"<td class={cls}><b>{_p(o['net'], True)} &#8378;</b></td>"
                     f"<td class={cls}>%{o['roi']:+.1f}</td></tr>")
    H.append("</table></div>")
    H.append("<div class=uyari><b>Olay kumesi zemine gore degisir.</b> 30 dk fotografi "
             "25 Tem'de, 15 dk fotografi 15 Agu'da basladi &rarr; <b>bot1@30 ve bot2@30 ayni "
             "olaylari gorur</b> (dogrudan kiyaslanabilir), <b>bot2@15 daha kisa bir pencereyi "
             "gorur</b> ve onun TL'leri digerleriyle dogrudan kiyaslanamaz.</div></div>")

    # --- her hucre icin tam dokum ---
    for etiket, _, _ in ZEMIN:
        for k in ks:
            r = cikti.get((etiket, k))
            if not r:
                continue
            o = ozet(r)
            H.append(f"<h3>{etiket} &middot; sabit-{k} "
                     f"<span class=alt>&mdash; {o['tam']}/{o['kupon']} Altili tutturuldu</span></h3>")
            H.append("<div class=kart><div class=wrap><table>")
            H.append("<tr><th>#</th><th class=l>tarih</th><th class=l>pist</th><th>sira</th>"
                     "<th>kombinasyon</th><th>bedel</th><th>temettu (odul)</th>"
                     "<th>kupon neti</th></tr>")
            for i, e in enumerate(sorted(o["tamlar"], key=lambda x: (x["tarih"], x["pist"],
                                                                    x["seq"])), 1):
                net = e["odul"] - e["bedel"]
                cls = "poz" if net >= 0 else "neg"
                tr = pd.Timestamp(e["tarih"]).strftime("%d.%m.%Y")
                H.append(f"<tr><td>{i}</td><td class=l>{tr}</td><td class=l>{e['pist']}</td>"
                         f"<td>{e['seq']}.</td><td>{_p(e['kombo'])}</td>"
                         f"<td>{_p(e['bedel'])} &#8378;</td><td>{_p(e['odul'])} &#8378;</td>"
                         f"<td class={cls}><b>{_p(net, True)} &#8378;</b></td></tr>")
            tb = sum(x["bedel"] for x in o["tamlar"])
            to = sum(x["odul"] for x in o["tamlar"])
            cls = "poz" if to - tb >= 0 else "neg"
            H.append(f"<tr class=top><td colspan=4 class=l>TUTTURULAN {o['tam']} KUPON</td>"
                     f"<td></td><td>{_p(tb)} &#8378;</td><td>{_p(to)} &#8378;</td>"
                     f"<td class={cls}>{_p(to - tb, True)} &#8378;</td></tr>")
            kb = o["bedel"] - tb
            H.append(f"<tr class=top><td colspan=4 class=l>TUTTURULAMAYAN "
                     f"{o['kupon'] - o['tam']} KUPON <span class=mini>(tamami zarar)</span></td>"
                     f"<td></td><td>{_p(kb)} &#8378;</td><td>0 &#8378;</td>"
                     f"<td class=neg>{_p(-kb, True)} &#8378;</td></tr>")
            cls = "poz" if o["net"] >= 0 else "neg"
            H.append(f"<tr class=gt><td colspan=4 class=l>GENEL TOPLAM "
                     f"&mdash; {o['kupon']} kupon</td><td></td>"
                     f"<td>{_p(o['bedel'])} &#8378;</td><td>{_p(o['odul'])} &#8378;</td>"
                     f"<td class={cls}>{_p(o['net'], True)} &#8378; (%{o['roi']:+.1f})</td></tr>")
            H.append("</table></div>")

            # tek-olay bagimliligi: bu hucrenin sonucu bir bilete mi dayaniyor?
            if o["tamlar"]:
                en = max(o["tamlar"], key=lambda x: x["odul"])
                pay = 100 * en["odul"] / o["odul"] if o["odul"] else 0
                kalan = o["odul"] - en["odul"] - o["bedel"]
                H.append(f"<div class=uyari>Tutturulan {o['tam']} kupondan <b>bedelini "
                         f"cikaran: {len(o['karli'])}</b> "
                         f"<span class=mini>(kalan {o['tam'] - len(o['karli'])} tanesi 6/6 "
                         f"yapti ve yine zarar etti)</span>.<br>En buyuk olay "
                         f"<b>{pd.Timestamp(en['tarih']).strftime('%d.%m.%Y')} {en['pist']} "
                         f"{en['seq']}. &rarr; {_p(en['odul'])} &#8378;</b> = toplam odulun "
                         f"<b>%{pay:.0f}</b>'i. <b>O olay cikarilirsa net "
                         f"{_p(kalan, True)} &#8378; "
                         f"(ROI %{100 * kalan / o['bedel']:+.1f})</b>.</div>")
            H.append("</div>")

    H.append("<div class=mini style='margin-top:16px'>Kagit hesabidir &mdash; bu kuponlar "
             "GERCEKTE KURULMADI, kupon-ani fotografindan geriye dogru simule edildi. "
             "Yalniz 6 ayaginin da fotografi ve bilinen kazanani olan Altililar sayildi; "
             "eksik olay iyimser/kotumser bantla doldurulmadi, atildi. Odul yalniz 6/6'da "
             "ve o Altili'nin resmi temettusudur (5/6 odemez, K52).</div>")

    HTML.parent.mkdir(parents=True, exist_ok=True)
    HTML.write_text("\n".join(H), encoding="utf-8")
    return HTML


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", default="3,4,5,6")
    ap.add_argument("--detay", action="store_true", help="raporlar/genislik_detay.html uret")
    args = ap.parse_args()
    ks = [int(x) for x in args.k.split(",")]

    cikti = olaylar(ks)
    konsol(cikti, ks)
    if args.detay:
        p = detay_html(cikti, ks)
        print(f"HTML: {p}")


if __name__ == "__main__":
    main()
