"""
altili_emekli_rapor.py — EMEKLI kupon turlerinin AYRI arsiv sayfasi (9 Eyl 2026).

NEDEN AYRI SAYFA: raporlar/altili.html emeklileri de yan yana basiyordu; her emekli
tur bir sutun daha demek ve tablo okunamaz hale geliyordu. Emekli turlerin sicili
SILINMEZ (K100 kurali) ama canli sayfayi tikamamalari icin buraya tasindi.
Bu dosya raporlar/altili_emekli.html uretir ve altili.html'e HIC DOKUNMAZ.

KAPSAM: KONFIG'de aktif=False olan her config (altili_canli.emekli_konfig()).
Liste burada ELLE tutulmaz -- bir config emekli edildiginde sayfa kendiliginden onu alir.

GORSEL DIL: beyaz zemin, vurgular siyah zemin/beyaz harf, hucrelerde altili.html ile ayni
anlamda K/Y/B/P etiketleri (K161'de kaldirilan altili_sabit3_rapor.py'nin temasi). Yardimci
fonksiyonlar altili_canli'dan yalnizca _kupon_ozet/_sira_etiketleri olarak alinir; gerisi
burada kopyadir -- bu arsiv sayfasi bozulsa bile ana sayfa etkilenmez (ve tersi).

SALT-OKUNUR: veri/altili_kupon.csv, veri/altili_kupon_ani.csv, veri/defter.csv ve
temettu onbellegi okunur; HICBIRINE YAZILMAZ.
Elle: python kod/altili_emekli_rapor.py [--ac]
"""
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
import rapor_ortak as ro                                        # noqa: E402
from altili_canli import KONFIG, _kupon_ozet, _sira_etiketleri  # noqa: E402

HTML = KOK / "raporlar" / "altili_emekli.html"
CSV = KOK / "veri" / "altili_kupon.csv"

# Emeklilik tarihi + tek cumlelik gerekce (karar numarasiyla). Sayfayi okuyan
# "bu neden durdu" sorusunu KARARLAR.md'yi acmadan cevaplayabilsin diye burada.
EMEKLI_NOT = {
    "dar":        ("10.08.2026", "K100 — 216 ayakta 0 benzersiz katki; 60 tek-at ayaginin 54'u "
                                 "banker degil butce kitligiydi"),
    "genis":      ("10.08.2026", "K100 — 0 benzersiz katki, komsulariyla %88/%83 ortusme; "
                                 "merdiven sorusu backtest'te kapandi (K88/K98)"),
    "genis900":   ("10.08.2026", "K100 — tek isi K65'in kontroluydu, o kol kapandi (K83/K93/K98)"),
    "ayrisma900": ("10.08.2026", "K100 — acgozlu900'un ikizi: ayaklarin %78'inde birebir ayni "
                                 "kupon, Jaccard %92, McNemar p=0,80"),
    "orta":       ("09.09.2026", "K161 — kagit karinin tamami tek olaydan (23.07 ANKARA-2, "
                                 "17.934 TL / 90 TL kupon); o olay disinda −15.904 TL"),
    "orta_15":    ("09.09.2026", "K161 — K153: 30 dk ile fark +5 ayak/408, p=0,576 (anlamsiz); "
                                 "esli pencerede ROI −%75,4 vs −%75,1"),
    "bot1_1800":  ("09.09.2026", "K161 — K118: bot1_900 ile ayni getiri, IKI KATI bedel; "
                                 "91 esli Altilida net −154.006 vs −63.542"),
}

CSS = """<style>
:root{
  --bg:#fff; --kart-bg:#fff; --kart-border:#ddd; --kart-shadow:rgba(0,0,0,.06);
  --text:#1a1a1a; --k:#555; --mini:#777; --baslik-border:#eee;
  --th-bg:#f2f2f2; --td-border:#e4e4e4;
  --tut-bg:#eef0f2; --siralama-bg:#f7f9fc;
  --poz:#0a7d0a; --neg:#c62828; --toplam-border:#000; --hr:#ddd;
}
body{font-family:"Segoe UI",Arial,sans-serif;margin:18px;color:var(--text);background:var(--bg);}
h2{margin:0 0 4px;font-size:19px;} h3{margin:18px 0 6px;font-size:15px;}
.alt{font-weight:normal;font-size:14px;color:var(--k);}
a{color:#1a1a1a;}
.nav{margin:-2px 0 14px;font-size:12px;color:var(--k);}
.kart{background:var(--kart-bg);border:1px solid var(--kart-border);border-radius:8px;
  padding:10px 14px;margin:12px 0;box-shadow:0 1px 3px var(--kart-shadow);}
.baslik{font-weight:bold;font-size:14px;margin-bottom:8px;padding-bottom:6px;
  border-bottom:2px solid var(--baslik-border);}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;}
td,th{border:1px solid var(--td-border);padding:5px 8px;font-size:13px;text-align:center;}
th{background:var(--th-bg);font-weight:600;}
td.l,th.l{text-align:left;}
.vurgu{background:#000;color:#fff;padding:1px 6px;border-radius:3px;font-weight:bold;}
.toplam{background:var(--kart-bg);border:3px solid var(--toplam-border);border-radius:8px;
  padding:14px 18px;margin:16px 0;font-size:14px;}
.toplam .buyuk{font-size:20px;font-weight:bold;}
.poz{color:var(--poz);} .neg{color:var(--neg);}
.k{font-size:12px;color:var(--k);} .mini{font-size:11px;color:var(--mini);}
.rozet{display:inline-block;padding:2px 10px;border-radius:12px;font-weight:bold;font-size:12px;}
.r6{background:#000;color:#fff;} .rb{background:#ddd;color:#555;}
.r0{background:#f2f2f2;color:#555;} .rk{background:#e4e4e4;color:#333;}
.wrap{overflow-x:auto;}
</style>"""


def emekli_configler():
    """KONFIG sirasini korur (rapor sirasi degil, kaydin kendi sirasi)."""
    return [c for c, a in KONFIG.items() if not a.get("aktif", True)]


def _oku():
    if not CSV.exists():
        return pd.DataFrame()
    d = pd.read_csv(CSV, low_memory=False)
    d = d[d["config"].isin(emekli_configler())].copy()
    for c in ("seq", "ayak", "kosu_no", "race_kod", "banker", "nat", "kazanan", "tuttu"):
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    return d


def _siralama_satiri(tarih, pist, seq, ayak, kosu_no, secset, kzno, dk_grup, etiket, bot1_ad):
    """Bir ayagin KUPON ANI siralamasi, istenen dk_grup fotografiyla."""
    a = ro.kupon_ani_atlari(tarih, pist, seq, ayak, dk_grup=dk_grup)
    if len(a) == 0:
        return f"<span class=mini><b>kosu {kosu_no}</b> &middot; {etiket}: <b>kayit yok</b></span>"
    r0 = a.iloc[0]
    dk = pd.to_numeric(r0.get("dk_kala"), errors="coerce")
    dkstr = ("%.0f" % dk) if pd.notna(dk) else "?"
    sirali = [(int(r["sis_sira"]), int(r["no"])) for _, r in a.iterrows()]
    out = [f"<span class=mini><b>kosu {kosu_no}</b> &middot; <b>{etiket}</b> "
           f"({str(r0.get('kayit_ts'))[11:16]}, {dkstr} dk kala): </span>"
           + _sira_etiketleri(sirali, secset, kzno)]
    if bot1_ad and "bot1_sira" in a.columns and pd.notna(a["bot1_sira"]).any():
        b = a.dropna(subset=["bot1_sira"]).sort_values("bot1_sira")
        b_sirali = [(int(r["bot1_sira"]), int(r["no"])) for _, r in b.iterrows()]
        out.append(f"<span class=mini><b>kosu {kosu_no}</b> &middot; <b>BOT1 CETVELI</b> "
                   f"(orana bakmaz &mdash; <i>{bot1_ad}</i> secimini bununla yapar): </span>"
                   + _sira_etiketleri(b_sirali, secset, kzno))
    return "<br>".join(out)


def _ozet_tablo(kupolar, cfgler):
    """Her emekli turun tam sicili + NE ZAMAN, NEDEN durduruldugu."""
    H = ["<h3>Emekli turler &mdash; tam sicil</h3><div class=kart><div class=wrap><table>",
         "<tr><th class=l>tur</th><th>donem</th><th>kupon</th><th>6/6</th><th>bedel</th>"
         "<th>odul</th><th>net</th><th>ROI</th><th class=l>durdurma tarihi ve gerekce</th></tr>"]
    tb = to = 0.0
    for cfg in cfgler:
        kk = [k for k in kupolar if k["cfg"] == cfg and k["bitti"]]
        if not kk:
            continue
        bedel = sum(k["bedel"] for k in kk)
        odul = sum(k["odul"] for k in kk)
        net = odul - bedel
        tb += bedel
        to += odul
        tam = sum(1 for k in kk if k["kademe"] == 6)
        cls = "poz" if net >= 0 else "neg"
        t0 = min(str(k["tarih"]) for k in kk)
        t1 = max(str(k["tarih"]) for k in kk)
        don = (f"{pd.Timestamp(t0).strftime('%d.%m')} &ndash; "
               f"{pd.Timestamp(t1).strftime('%d.%m.%Y')}")
        tar, ger = EMEKLI_NOT.get(cfg, ("&mdash;", "&mdash;"))
        a = KONFIG[cfg]
        H.append(f"<tr><td class=l><b>{cfg.upper()}</b><br><span class=mini>"
                 f"{a.get('kombo')} kombo &middot; {a.get('dk', 30)}dk &middot; "
                 f"{a.get('dagitim')} &middot; {a.get('puan')}</span></td>"
                 f"<td><span class=mini>{don}</span></td><td>{len(kk)}</td>"
                 f"<td>{tam or '&mdash;'}</td><td>{ro.para(bedel)}</td><td>{ro.para(odul)}</td>"
                 f"<td class={cls}><b>{ro.para(net, isaret=True)}</b></td>"
                 f"<td class={cls}>{('%%%+.1f' % (100*net/bedel)) if bedel else '-'}</td>"
                 f"<td class=l><span class=mini><b>{tar}</b> &middot; {ger}</span></td></tr>")
    net = to - tb
    cls = "poz" if net >= 0 else "neg"
    H.append(f"<tr><td class=l><b>TOPLAM</b></td><td></td><td></td><td></td>"
             f"<td><b>{ro.para(tb)}</b></td><td><b>{ro.para(to)}</b></td>"
             f"<td class={cls}><b>{ro.para(net, isaret=True)}</b></td>"
             f"<td class={cls}>{('%%%+.1f' % (100*net/tb)) if tb else '-'}</td><td></td></tr>")
    H.append("</table></div></div>")
    return H


def _gun_gun(kupolar):
    bitmis = [k for k in kupolar if k["bitti"]]
    if not bitmis:
        return []
    gun = {}
    for k in bitmis:
        g = gun.setdefault(str(k["tarih"]), {"bedel": 0.0, "odul": 0.0, "kupon": 0, "tam": 0})
        g["bedel"] += k["bedel"]; g["odul"] += k["odul"]
        g["kupon"] += 1; g["tam"] += (k["kademe"] == 6)
    H = ["<h3>Gun gun kar/zarar ve isleyen bakiye <span class=alt>(yalniz emekli turler)</span>"
         "</h3><div class=kart>",
         "<div class=wrap><table><tr><th class=l>tarih</th><th>kupon</th><th>6/6</th>"
         "<th>bedel</th><th>odul</th><th>gun neti</th><th>ISLEYEN BAKIYE</th></tr>"]
    kum = 0.0
    for t in sorted(gun):
        g = gun[t]
        net = g["odul"] - g["bedel"]
        kum += net
        H.append(f"<tr><td class=l>{pd.Timestamp(t).strftime('%d.%m.%Y')}</td>"
                 f"<td>{g['kupon']}</td><td>{g['tam'] or '&mdash;'}</td>"
                 f"<td>{ro.para(g['bedel'])}</td><td>{ro.para(g['odul'])}</td>"
                 f"<td class='{'poz' if net >= 0 else 'neg'}'>{ro.para(net, isaret=True)}</td>"
                 f"<td class='{'poz' if kum >= 0 else 'neg'}'><b>{ro.para(kum, isaret=True)}</b>"
                 f"</td></tr>")
    H.append("</table></div></div>")
    return H


def html_yaz(df=None, ac=False):
    if df is None:
        df = _oku()
    cfgler_tum = emekli_configler()

    H = ["<meta charset='utf-8'><title>Altili Takip &mdash; Emekliler</title>", CSS,
         "<h2>ALTILI GANYAN &mdash; EMEKLI KUPON TURLERI <span class=alt>(arsiv)</span></h2>",
         "<div class=nav><a href='altili.html'>&larr; Altili Takip (aktif turler)</a>"
         f" &nbsp;&middot;&nbsp; guncelleme {datetime.now():%d.%m.%Y %H:%M}</div>"]

    if df is None or df.empty:
        H.append("<p>Emekli tur yok.</p>")
        HTML.parent.mkdir(parents=True, exist_ok=True)
        HTML.write_text("\n".join(H), encoding="utf-8")
        return HTML

    kupolar = []
    for (tarih, pist, seq, cfg), g in df.groupby(["tarih", "pist", "seq", "config"]):
        if len(g) != 6:
            continue
        kupolar.append({"tarih": tarih, "pist": pist, "seq": int(seq), "cfg": cfg,
                        **_kupon_ozet(g, tarih, pist, int(seq), cfg)})

    H += _ozet_tablo(kupolar, cfgler_tum)

    H.append("<h3>Kuponlar (yeni tarih ustte)</h3>")
    H.append("<div class=k style='margin:6px 0 4px'>Hucre etiketleri: "
             "<b>K</b> = kupon anindaki sistem sirasi &nbsp;&middot;&nbsp; "
             "<b>Y</b> = yaris anindaki sistem sirasi &nbsp;&middot;&nbsp; "
             "<b>B</b> = <i>bot1'in kendi sirasi</i> (yalniz bot1 sutununda) &nbsp;&middot;&nbsp; "
             "<b>P</b> = kamu (piyasa) sirasi &nbsp;&middot;&nbsp; "
             "<span style='color:#6d28d9'><b>mor</b></span> = sistem kamudan 3+ sira ayri "
             "&nbsp;&middot;&nbsp; <span style='color:#b45309'><b>turuncu</b></span> = "
             "kupon ani ile yaris ani 3+ sira kaymis</div>")

    gruplar = sorted({(k["tarih"], k["pist"], k["seq"]) for k in kupolar}, reverse=True)
    for tarih, pist, seq in gruplar:
        kk = {k["cfg"]: k for k in kupolar
              if (k["tarih"], k["pist"], k["seq"]) == (tarih, pist, seq)}
        cfgler = [c for c in cfgler_tum if c in kk]
        if not cfgler:
            continue
        ref = kk[cfgler[0]]["g"].sort_values("ayak")
        t_bedel = sum(kk[c]["bedel"] for c in cfgler)
        t_odul = sum(kk[c]["odul"] for c in cfgler)
        tn = t_odul - t_bedel
        tutanlar = [c.upper() for c in cfgler if kk[c]["kademe"] == 6]
        res = kk[cfgler[0]]["resmi"] or {}
        if res.get("temettu"):
            resmi = f"resmi temettu (1 birim): <b>{ro.para(res['temettu'])}</b>"
            if tutanlar:
                resmi += f" &mdash; <span class=poz><b>tutturan: {', '.join(tutanlar)}</b></span>"
        elif res.get("devir"):
            resmi = f"<b>KIMSE BILEMEDI</b> &mdash; {ro.para(res['devir'])} devretti"
        else:
            resmi = "<span class=mini>resmi temettu: bilinmiyor</span>"

        H.append("<div class=kart>")
        H.append(f"<div class=baslik>{pd.Timestamp(str(tarih)).strftime('%d.%m.%Y')} "
                 f"&nbsp;|&nbsp; <b>{pist}</b> &nbsp;|&nbsp; {seq}. ALTILI<br>"
                 f"<span class=k>{len(cfgler)} emekli tur &nbsp;&middot;&nbsp; toplam bedel "
                 f"<b>{ro.para(t_bedel)}</b> &nbsp;&rarr;&nbsp; odul <b>{ro.para(t_odul)}</b> "
                 f"&nbsp;&rarr;&nbsp; net <span class='{'poz' if tn >= 0 else 'neg'}'>"
                 f"<b>{ro.para(tn, isaret=True)}</b></span><br>{resmi}</span></div>")

        H.append("<div class=wrap><table>")
        H.append("<tr><th>ayak</th><th class=l>KAZANAN AT</th>"
                 "<th>sistem/kamu sirasi<br><span class=mini>kupon ani &rarr; yaris ani</span>"
                 "</th><th>ganyan<br>orani</th>"
                 + "".join(f"<th class=l>{c.upper()}<br><span class=mini>"
                           f"{KONFIG[c].get('kombo')} kombo &middot; {KONFIG[c].get('dk', 30)}dk "
                           f"&middot; {KONFIG[c]['aile']}</span></th>"
                           for c in cfgler) + "</tr>")

        for _, r in ref.iterrows():
            ai = int(r["ayak"])
            rk = int(r["race_kod"]) if pd.notna(r["race_kod"]) else None
            kosu_no = int(r["kosu_no"]) if pd.notna(r["kosu_no"]) else "?"
            kz = ro.kazanan_bilgi(rk) if rk else None
            if kz and kz.get("no") is not None:
                kzno = int(kz["no"])
                kz_html = f"<b>{kzno}</b> {str(kz['ad'])[:20]}"
                kz_oran = ro.oran_str(kz["oran"])
                y_sira, y_kamu = ro.sira_str(kz["sis"]), ro.sira_str(kz["kamu"])
            elif pd.notna(r["kazanan"]):
                kzno = int(r["kazanan"])
                kz_html = (f"<b>{kzno}</b> <span class=mini>(sistem sirasi gun sonu islenecek)"
                           f"</span>")
                kz_oran, y_sira, y_kamu = "-", "-", "-"
            else:
                kzno, kz_html, kz_oran, y_sira, y_kamu = None, \
                    "<span class=mini>bekleniyor</span>", "-", "-", "-"

            if kzno is not None:
                ka = ro.kupon_ani_bilgi(tarih, pist, seq, ai, kzno, dk_grup=30)
                kz_sk = (f"<span class=mini>sistem</span> <b>{ro.sira_str(ka['sis'])}</b> "
                         f"&rarr; {y_sira}<br><span class=mini>kamu</span> &nbsp;&nbsp;"
                         f"<b>{ro.sira_str(ka['kamu'])}</b> &rarr; {y_kamu}")
            else:
                kz_sk = "-"

            H.append(f"<tr><td><b>{ai}</b><br><span class=mini>kosu {kosu_no}</span></td>"
                     f"<td class=l>{kz_html}</td><td>{kz_sk}</td><td>{kz_oran}</td>")

            tum_sec = set()
            for c in cfgler:
                gc = kk[c]["g"]
                sr = gc[gc["ayak"] == ai]
                if sr.empty:
                    H.append("<td class=l><span class=mini>-</span></td>")
                    continue
                sr = sr.iloc[0]
                secimler = [int(x) for x in str(sr["secim"]).split(",") if x != ""]
                tum_sec |= set(secimler)
                dk_c = KONFIG[c].get("dk", 30)
                bot1_cfg = KONFIG[c].get("puan") == "bot1"
                hucre = []
                for no in secimler:
                    bi = ro.at_bilgi(rk, no) if rk else {}
                    ka = ro.kupon_ani_bilgi(tarih, pist, seq, ai, no, dk_grup=dk_c)
                    ks, ys = ro.sira_str(ka.get("sis")), ro.sira_str(bi.get("sis"))
                    ps = ro.sira_str(ka.get("kamu"))
                    ayri = (pd.notna(ka.get("sis")) and pd.notna(ka.get("kamu"))
                            and abs(float(ka["sis"]) - float(ka["kamu"])) >= 3)
                    pstl = " style='color:#6d28d9;font-weight:bold'" if ayri else ""
                    kayar = (pd.notna(ka.get("sis")) and pd.notna(bi.get("sis"))
                             and abs(float(ka["sis"]) - float(bi["sis"])) >= 3)
                    stl = " style='color:#b45309;font-weight:bold'" if kayar else ""
                    et = f"<span class=vurgu>{no}</span>" if no == kzno else f"{no}"
                    if bot1_cfg:
                        hucre.append(f"{et} <span class=mini><b>B{ro.sira_str(ka.get('bot1_sira'))}"
                                     f"</b></span> <span class=mini{stl}>K{ks} Y{ys}</span>"
                                     f" <span class=mini{pstl}>P{ps}</span>")
                    else:
                        hucre.append(f"{et} <span class=mini{stl}>K{ks} Y{ys}</span>"
                                     f" <span class=mini{pstl}>P{ps}</span>")
                bk = " <span class=mini>[banker]</span>" if int(sr["banker"]) == 1 else ""
                tuttu = kzno is not None and kzno in secimler
                stil = " style='background:var(--tut-bg)'" if tuttu else ""
                H.append(f"<td class=l{stil}>" + "<br>".join(hucre) + bk + "</td>")
            H.append("</tr>")

            # KUPON ANI siralamasi: bu Altilida hangi dk gruplari varsa onlar icin ayri satir.
            dk_gruplari = sorted({KONFIG[c].get("dk", 30) for c in cfgler}, reverse=True)
            satirlar = []
            for dkg in dk_gruplari:
                b1 = [c for c in cfgler if KONFIG[c].get("puan") == "bot1"
                      and KONFIG[c].get("dk", 30) == dkg]
                satirlar.append(_siralama_satiri(tarih, pist, seq, ai, kosu_no, tum_sec, kzno,
                                                 dkg, f"KUPON ANI {int(dkg)}dk",
                                                 b1[0] if b1 else None))
            H.append(f"<tr><td></td><td colspan={3+len(cfgler)} class=l "
                     "style='background:var(--siralama-bg);border-top:none'>"
                     + "<br>".join(satirlar) + "</td></tr>")

        def ozet_satir(baslik, fn):
            return (f"<tr><td colspan=4 class=l><b>{baslik}</b></td>"
                    + "".join(f"<td class=l>{fn(kk[c])}</td>" for c in cfgler) + "</tr>")

        H.append(ozet_satir("kombinasyon", lambda k: f"{k['kombo']}"))
        H.append(ozet_satir("kagit bedel", lambda k: ro.para(k["bedel"])))
        H.append(ozet_satir("durum", lambda k: (
            "<span class='rozet rb'>devam</span>" if not k["bitti"] else
            "<span class='rozet r6'>6/6 TUTTU</span>" if k["kademe"] == 6 else
            f"<span class='rozet rk'>son {k['kademe']} ayak</span>" if k["kademe"] else
            "<span class='rozet r0'>isabetsiz</span>")))
        H.append(ozet_satir("odul", lambda k: ro.para(k["odul"]) if k["odul"] else "&mdash;"))
        H.append(ozet_satir("net", lambda k:
                            f"<span class='{'poz' if k['net'] >= 0 else 'neg'}'>"
                            f"<b>{ro.para(k['net'], isaret=True)}</b></span>"))
        H.append("</table></div></div>")

    H += _gun_gun(kupolar)
    H.append("<div class=mini style='margin-top:14px'>Kagit (paper) sicilidir &mdash; gercek para "
             "yatirilmiyor. Emekli turler yeni kupon KURMAZ; buradaki sicil dondurulmustur ve "
             "silinmez (K100 kurali). Genel toplam ana sayfada bu turleri de icerir.</div>")

    HTML.parent.mkdir(parents=True, exist_ok=True)
    HTML.write_text("\n".join(H), encoding="utf-8")
    if ac:
        import webbrowser
        try:
            webbrowser.open(HTML.as_uri())
        except Exception:                                        # noqa: BLE001
            pass
    return HTML


if __name__ == "__main__":
    p = html_yaz(ac="--ac" in sys.argv)
    print(f"HTML: {p}")
