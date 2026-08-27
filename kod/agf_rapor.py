# -*- coding: utf-8 -*-
"""
agf_rapor.py — K137 / BEKLEYENLER #21: AGF "İKİNCİ GÖRÜŞ" raporu.

NE YAPAR: sistemin seçimiyle **AGF'nin** (Altılı havuzunun kendi parasının) nerede ayrıştığını
gösterir. Kupon seçimini DEĞİŞTİRMEZ; yalnız gösterir.

NEDEN AYRI DOSYA — ve neden `altili_canli.py`'ye dokunulmadı:
  Kullanıcı #21'de "raporlarda ikinci bir görüş sütunu" istemişti. Sütunu mevcut rapora
  eklemek `altili_canli.py`'yi (65 KB, sistemin en kritik dosyası, günlük kupon üreticisi)
  ya da `rapor_ortak.py`'yi (üç raporun ortak temeli) değiştirmek demekti. Kullanıcı
  "sistemde asla hasar olmasın" dedi. **Aynı bilgi, sıfır riskle:** bu betik hiçbir mevcut
  dosyayı okumaz-yazmaz, yalnız `raporlar/agf_gozlem.html` üretir.

NİYE İLGİNÇ (K129/K131):
  * AGF, devig edilmiş ganyan KAPANIŞINDAN daha iyi kalibre (OOS log-loss 1,7817 vs 1,8047).
  * AGF **3,5 saat öncesinden bellidir ve değişmez** (ρ=0,9999) — ganyan oranı ise aynı
    pencerede medyan %27,7 kayar, atların %79'u >%10 oynar.
  * Yani AGF, kupon anında sahip OLMADIĞIMIZ kapanış fiyatının, kupon anında sahip
    OLDUĞUMUZ vekilidir.

UYARI — BU BİR KARAR KURALI DEĞİLDİR:
  K129 ölçtü: AGF'yi kupona katmak parayı DEĞİŞTİRMİYOR (ayak isabeti +0,020, GA sıfırı
  içeriyor). Bu sayfa "bilgi" olarak durur. Görünce oynamak isteme eğilimi gerçektir;
  ölçüm o eğilimin karşılığı olmadığını söylüyor.

KAYNAK (hepsi salt-okunur): veri/altili_oran_log.csv · veri/altili_kupon.csv · veri/katilim.csv
ÇIKTI: raporlar/agf_gozlem.html  (YENİ dosya; mevcut hiçbir raporun üstüne yazmaz)
"""
import sys
from html import escape
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent
CIKTI = KOK / "raporlar" / "agf_gozlem.html"
SON_GUN = 14


def veri():
    o = pd.read_csv(KOK / "veri" / "altili_oran_log.csv", low_memory=False)
    for c in ("agf1", "no", "ayak", "dk_kala", "ganyan"):
        o[c] = pd.to_numeric(o[c], errors="coerce")
    o = o[o["agf1"].notna() & (~o["kosmaz"].fillna(False).astype(bool))]
    # her (Altili, ayak, at) icin KUPON ANINA en yakin (en buyuk dk_kala) kayit
    o = o.sort_values("dk_kala", ascending=False)
    o = o.groupby(["tarih", "pist", "seq", "ayak", "no"], as_index=False).first()

    kp = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    k = pd.read_csv(KOK / "veri" / "katilim.csv",
                    usecols=["race_kod", "no", "sonuc", "kosmaz"], low_memory=False)
    for c in ("no", "sonuc"):
        k[c] = pd.to_numeric(k[c], errors="coerce")
    k = k[~k["kosmaz"].fillna(False).astype(bool)]
    KAZ = {}
    for rk, g in k.groupby("race_kod"):
        w = g["no"][g["sonuc"] == 1]
        KAZ[int(rk)] = int(w.iloc[0]) if len(w) == 1 else None
    return o, kp, KAZ


def main():
    o, kp, KAZ = veri()
    gunler = sorted(o["tarih"].unique())[-SON_GUN:]
    o = o[o["tarih"].isin(gunler)]

    sat = []
    ozet = {"ayak": 0, "agf_tuttu": 0, "biz_tuttu": 0, "ayrisma": 0,
            "ayrismada_agf": 0, "ayrismada_biz": 0}
    for (tar, pist, seq), g in o.groupby(["tarih", "pist", "seq"]):
        satirlar = []
        for ayak, ga in g.groupby("ayak"):
            ga = ga.sort_values("agf1", ascending=False)
            rk = int(ga["race_kod"].iloc[0])
            kaz = KAZ.get(rk)
            agf_sira = [(int(r["no"]), float(r["agf1"])) for _, r in ga.head(4).iterrows()]
            agf_top = agf_sira[0][0] if agf_sira else None
            # bizim secimimiz: uretimin 'orta' config'i (canli baş kol)
            s = kp[(kp["tarih"] == tar) & (kp["pist"] == pist) & (kp["seq"] == seq)
                   & (kp["config"] == "orta") & (kp["ayak"] == ayak)]
            bizim = set()
            if len(s):
                bizim = {int(x) for x in str(s["secim"].iloc[0]).split(",") if x.strip().isdigit()}
            if kaz is None:
                continue
            ozet["ayak"] += 1
            at = agf_top == kaz
            bt = kaz in bizim
            ozet["agf_tuttu"] += at
            ozet["biz_tuttu"] += bt
            ayr = bool(bizim) and agf_top is not None and agf_top not in bizim
            if ayr:
                ozet["ayrisma"] += 1
                ozet["ayrismada_agf"] += at
                ozet["ayrismada_biz"] += bt
            satirlar.append((ayak, agf_sira, sorted(bizim), kaz, at, bt, ayr))
        if satirlar:
            sat.append((tar, pist, seq, satirlar))

    H = ["<title>AGF Gözlem</title>", """<style>
body{font:14px/1.5 system-ui,Segoe UI,Arial;margin:24px;background:#fafafa;color:#222}
h1{font-size:20px;margin:0 0 4px} h2{font-size:15px;margin:22px 0 6px;color:#444}
.not{background:#fff8e1;border-left:4px solid #f0b429;padding:10px 14px;margin:14px 0;
border-radius:4px;font-size:13px}
table{border-collapse:collapse;width:100%;background:#fff;font-size:13px;margin-bottom:8px}
th,td{border:1px solid #e3e3e3;padding:5px 8px;text-align:left}
th{background:#f2f2f2;font-weight:600}
.ay{background:#fff3cd} .tut{color:#0a7d28;font-weight:600} .yok{color:#b00020}
.k{font-family:ui-monospace,Consolas,monospace}
.ozet td{font-size:14px} .ozet th{width:44%}
</style>"""]
    H.append("<h1>AGF Gözlem — ikinci görüş</h1>")
    H.append("<p style='color:#666;font-size:13px'>Sistemin seçimi ile <b>AGF</b> "
             "(Altılı havuzunun kendi parası) nerede ayrışıyor? Son "
             f"{len(gunler)} yarış günü. Kıyas kolu: üretimin <span class=k>orta</span> "
             "config'i.</p>")
    H.append("<div class=not><b>Bu bir karar kuralı değildir.</b> K129 ölçtü: AGF'yi kupona "
             "katmak parayı değiştirmiyor (ayak isabeti +0,020, güven aralığı sıfırı içeriyor). "
             "Bu sayfa yalnız <b>gözlem</b>. AGF'nin ilginç yanı doğruluğu değil, "
             "<b>kupon anında zaten belli olması</b>: 3,5 saat öncesinden sabit (ρ=0,9999), "
             "oysa ganyan oranı aynı pencerede medyan %27,7 kayıyor.</div>")

    t = ozet["ayak"] or 1
    H.append("<h2>Özet</h2><table class=ozet>")
    H.append(f"<tr><th>değerlendirilen ayak</th><td>{ozet['ayak']}</td></tr>")
    H.append(f"<tr><th>AGF'nin 1. atı kazandı</th><td>{ozet['agf_tuttu']} "
             f"(%{100*ozet['agf_tuttu']/t:.1f})</td></tr>")
    H.append(f"<tr><th>bizim seçimimiz tuttu</th><td>{ozet['biz_tuttu']} "
             f"(%{100*ozet['biz_tuttu']/t:.1f})</td></tr>")
    a = ozet["ayrisma"] or 1
    H.append(f"<tr><th>AYRIŞMA (AGF'nin 1.'si bizde yok)</th><td>{ozet['ayrisma']} "
             f"(%{100*ozet['ayrisma']/t:.1f})</td></tr>")
    H.append(f"<tr><th>&nbsp;&nbsp;ayrışmada AGF haklı çıktı</th><td>{ozet['ayrismada_agf']} "
             f"(%{100*ozet['ayrismada_agf']/a:.1f})</td></tr>")
    H.append(f"<tr><th>&nbsp;&nbsp;ayrışmada BİZ haklı çıktık</th><td>{ozet['ayrismada_biz']} "
             f"(%{100*ozet['ayrismada_biz']/a:.1f})</td></tr>")
    H.append("</table>")

    for tar, pist, seq, satirlar in sorted(sat, reverse=True):
        H.append(f"<h2>{escape(str(tar))} · {escape(str(pist))} · {seq}. Altılı</h2>")
        H.append("<table><tr><th>ayak</th><th>AGF sırası (pay %)</th>"
                 "<th>bizim seçim (orta)</th><th>kazanan</th><th>AGF</th><th>biz</th></tr>")
        for ayak, agf_sira, bizim, kaz, at, bt, ayr in satirlar:
            ag = " · ".join(f"<b>{n}</b>({v:.1f})" if i == 0 else f"{n}({v:.1f})"
                            for i, (n, v) in enumerate(agf_sira))
            cls = " class=ay" if ayr else ""
            H.append(f"<tr{cls}><td>{ayak}</td><td class=k>{ag}</td>"
                     f"<td class=k>{','.join(map(str, bizim)) or '—'}</td>"
                     f"<td class=k><b>{kaz}</b></td>"
                     f"<td class={'tut' if at else 'yok'}>{'✓' if at else '✗'}</td>"
                     f"<td class={'tut' if bt else 'yok'}>{'✓' if bt else '✗'}</td></tr>")
        H.append("</table>")
    H.append("<p style='color:#888;font-size:12px'>Sarı satır = ayrışma "
             "(AGF'nin favorisi bizim seçimimizde yok). Üretilen: "
             f"{pd.Timestamp.now():%Y-%m-%d %H:%M} · <span class=k>kod/agf_rapor.py</span> "
             "(salt-okunur; hiçbir mevcut dosyaya dokunmaz)</p>")

    CIKTI.parent.mkdir(exist_ok=True)
    CIKTI.write_text("\n".join(H), encoding="utf-8")
    print(f"yazildi: {CIKTI}  ({ozet['ayak']} ayak, {len(sat)} Altili, {len(gunler)} gun)")
    print(f"  AGF 1.'si kazandi: %{100*ozet['agf_tuttu']/t:.1f} · "
          f"bizim secim tuttu: %{100*ozet['biz_tuttu']/t:.1f}")
    print(f"  ayrisma {ozet['ayrisma']} ayak -> AGF hakli {ozet['ayrismada_agf']} · "
          f"biz hakli {ozet['ayrismada_biz']}")


if __name__ == "__main__":
    main()
