# -*- coding: utf-8 -*-
"""
deney_durum.py — K144 / BEKLEYENLER 22-I: AÇIK DENEYLERİN TETİK DOLULUK TABLOSU.
SALT-OKUNUR / OFFLINE.

SORUN: BEKLEYENLER'de sayısal tetikli maddeler var ("≥400 yeni İstanbul ayağı", "~60 kupon")
ama tetiğin ne kadar dolduğunu görmenin tek yolu elle saymaktı. Sonuç: **#11'in kendi notu
'Ekim ortası' diyordu, gerçek doluş ~8-16 Eylül'dü** — yani madde, sırası geldiği hâlde
kenarda bekliyordu. Bu sayfa o hatayı imkânsız kılar.

KAYIT (elle tutulur, bilerek): tetikler aşağıdaki TETIKLER tablosunda açıkça yazılı.
BEKLEYENLER.md ayrıştırılmıyor — çünkü serbest metin ayrıştırmak kırılgan ve sessizce
yanlış cevap verir. Bir tetik değişirse BURASI da güncellenir; tablo, BEKLEYENLER'in
sayısal özeti olarak okunur.

ÇIKTI: terminal + raporlar/deney_durum.html (YENİ dosya; mevcut hiçbir rapora dokunmaz)
"""
import sys
from datetime import date, datetime
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_canli import KONFIG                                     # noqa: E402

CIKTI = KOK / "raporlar" / "deney_durum.html"
AKTIF = [c for c, a in KONFIG.items() if a.get("aktif")]


# ------------------------------------------------------------------ ölçerler
def _kupon():
    k = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    return k[k["tuttu"].notna() & k["config"].isin(AKTIF)].copy()


def olc_istanbul(baslangic):
    """#11: K122'den (26 Ağu) sonra biriken İSTANBUL ayağı. pist_analiz ile AYNI birim:
    aktif config'lerin sonuçlanmış kupon ayağı satırı."""
    k = _kupon()
    return int(len(k[(k["pist"] == "ISTANBUL") & (k["tarih"] > baslangic)]))


def olc_zamanlama():
    """#4: zaman kolu config'lerinin sonuçlanmış KUPON sayısı (ayak değil)."""
    k = _kupon()
    out = {}
    for c in ("orta_15", "acgozlu900_15"):
        g = k[k["config"] == c]
        out[c] = int(len(g.groupby(["tarih", "pist", "seq"])))
    return out


def olc_cifte(baslangic):
    """#18: K127'den (27 Ağu) sonraki ÇİFTE fırsatı — ÜST SINIR tahmini.
    Bir kartta n koşu varsa ardışık çift sayısı n-1'dir; gerçek fırsat kalite kapısından
    sonra bunun ~%75'i (K126: 3.058/4.018). Tahmin olduğu AÇIKÇA raporlanır."""
    k = pd.read_csv(KOK / "veri" / "katilim.csv",
                    usecols=["race_kod", "tarih", "sehir", "kosmaz"], low_memory=False)
    k = k[~k["kosmaz"].fillna(False).astype(bool)]
    k["dt"] = pd.to_datetime(k["tarih"], format="%d/%m/%Y", errors="coerce")
    k = k[k["dt"] > pd.Timestamp(baslangic)]
    if k.empty:
        return 0
    kart = k.groupby(["tarih", "sehir"])["race_kod"].nunique()
    return int(((kart - 1).clip(lower=0)).sum() * 0.75)


# ------------------------------------------------------------------ tetik tablosu
def tetikler():
    bugun = date.today()
    T = []

    ist = olc_istanbul("2026-08-26")
    T.append(dict(no="#11", ad="İSTANBUL aykırısı (post-hoc desen)", tur="sayısal",
                  simdi=ist, hedef=400, birim="ayak", kaynak="K122",
                  baslangic=date(2026, 8, 26),
                  not_="pist_analiz.py + olay-bootstrap ile sınanır"))

    z = olc_zamanlama()
    for c in ("orta_15", "acgozlu900_15"):
        T.append(dict(no="#4", ad=f"zamanlama kolu — {c}", tur="sayısal",
                      simdi=z[c], hedef=60, birim="kupon", kaynak="K105/K111",
                      baslangic=date(2026, 8, 15),
                      not_="30 dk vs 15 dk eşli kıyas"))

    cf = olc_cifte("2026-08-27")
    T.append(dict(no="#18", ad="ÇİFTE'de bot1 deseni (post-hoc)", tur="sayısal",
                  simdi=cf, hedef=1000, birim="fırsat (tahmini)", kaynak="K127",
                  baslangic=date(2026, 8, 27),
                  not_="TAHMİN: kart başına (n−1)×0,75. Gerçek sayım cifte_h1.py ile"))

    for no, ad, hedef, kaynak, nt in (
        ("ZAMANLI-4", "Kâğıt test karar noktası", date(2026, 9, 25), "K42/K142",
         "ÖLÇÜT YAZILDI (K142): S1 kenar → S2 tetik → S3 arşiv modu"),
        ("#6", "Model ağırlıklarını yeniden fit", date(2026, 9, 25), "K96",
         "K96: sıfırdan hesaplama, K96 sayılarıyla KIYASLA"),
        ("ZAMANLI-6", "veri/ham dış yedek tazeleme", date(2026, 10, 27), "K35",
         "son yükleme ~27 Tem; 3 aylık tetik"),
    ):
        T.append(dict(no=no, ad=ad, tur="tarih", simdi=(hedef - bugun).days,
                      hedef=hedef, birim="gün kaldı", kaynak=kaynak, not_=nt))
    return T


def yuzde(t):
    if t["tur"] != "sayısal":
        return None
    return min(100.0, 100.0 * t["simdi"] / t["hedef"])


def tahmin_gun(t, kupon=None):
    """Sayısal tetik: tetiğin KENDİ başlangıcından bu yana geçen hızla kaç gün sonra dolar.

    K144 DÜZELTME: önce hız, kupon dosyasının TAMAMININ tarih aralığından hesaplanıyordu;
    her tetiğin başlangıcı farklı olduğu için #18 için 216 gün gibi yanlış bir tahmin
    üretiyordu. Artık her tetik kendi `baslangic`ından ölçülüyor."""
    if t["tur"] != "sayısal" or t["simdi"] >= t["hedef"]:
        return None
    gecen = max((date.today() - t["baslangic"]).days, 1)
    hiz = t["simdi"] / gecen
    if hiz <= 0:
        return None
    return int(np.ceil((t["hedef"] - t["simdi"]) / hiz))


def main():
    k = _kupon()
    T = tetikler()
    bugun = date.today()

    print("=" * 96)
    print(f"K144 / 22-I — AÇIK DENEYLERİN TETİK DURUMU   ({bugun:%d %b %Y})")
    print("=" * 96)
    print(f"  {'madde':>10} {'tetik':>9} {'durum':>16} {'doluluk':>9} {'tahmini doluş':>16}  kaynak")
    print("-" * 96)
    for t in T:
        if t["tur"] == "sayısal":
            y = yuzde(t)
            d = tahmin_gun(t, k)
            dur = f"{t['simdi']:,}/{t['hedef']:,} {t['birim'][:12]}"
            tah = (f"~{d} gün (~{(pd.Timestamp(bugun)+pd.Timedelta(days=d)):%d %b})"
                   if d else ("DOLDU" if t["simdi"] >= t["hedef"] else "—"))
            print(f"  {t['no']:>10} {'sayısal':>9} {dur:>16} {y:>8.0f}% {tah:>16}  {t['kaynak']}")
        else:
            kaldi = t["simdi"]
            dur = f"{t['hedef']:%d %b %Y}"
            tah = f"{kaldi} gün kaldı" if kaldi >= 0 else f"{-kaldi} gün GEÇTİ"
            print(f"  {t['no']:>10} {'tarih':>9} {dur:>16} {'—':>9} {tah:>16}  {t['kaynak']}")

    yakin = [t for t in T if t["tur"] == "tarih" and 0 <= t["simdi"] <= 30]
    dolan = [t for t in T if t["tur"] == "sayısal" and (tahmin_gun(t, k) or 999) <= 23]
    print("\n" + "-" * 96)
    print(f"  25 EYLÜL'E {(date(2026,9,25)-bugun).days} GÜN — o tarihe kadar:")
    for t in dolan:
        print(f"    · {t['no']} {t['ad']} tetiği dolacak (~{tahmin_gun(t,k)} gün)")
    for t in yakin:
        print(f"    · {t['no']} {t['ad']} ({t['simdi']} gün)")
    if not dolan and not yakin:
        print("    · yakın tetik yok")

    # ------------------------------------------------------------------ HTML
    H = ["<title>Deney Durumu</title>", """<style>
body{font:15px/1.6 system-ui,Segoe UI,Arial;margin:0;background:#f7f8fa;color:#151b23}
.w{max-width:1000px;margin:0 auto;padding:32px 24px 64px}
h1{font-size:23px;margin:0 0 4px} .alt{color:#5a6673;font-size:13.5px;margin:0 0 26px}
table{border-collapse:collapse;width:100%;background:#fff;border:1px solid #dde2e8;
border-radius:4px;overflow:hidden;font-size:14px}
th,td{padding:11px 14px;text-align:left;border-bottom:1px solid #e8ecf1}
th{background:#eef1f4;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#6b7683}
tr:last-child td{border-bottom:0}
td.n{text-align:right;font-variant-numeric:tabular-nums;font-family:ui-monospace,Consolas,monospace}
.bar{height:7px;background:#e3e8ee;border-radius:4px;overflow:hidden;min-width:90px}
.bar i{display:block;height:100%;background:#0b6b62}
.bar i.yak{background:#b8860b} .bar i.dol{background:#a63a2b}
.rz{display:inline-block;padding:2px 9px;border-radius:11px;font-size:11.5px;font-weight:600}
.rz.s{background:#e4f0ee;color:#0b6b62} .rz.t{background:#f2eee0;color:#7a5c10}
.not{color:#6b7683;font-size:12.5px}
.uyari{background:#fff8e1;border-left:3px solid #d9a520;padding:14px 18px;border-radius:0 3px 3px 0;margin:22px 0;font-size:14px}
</style>"""]
    H.append('<div class=w>')
    H.append("<h1>Açık deneylerin tetik durumu</h1>")
    H.append(f"<p class=alt>{bugun:%d %B %Y} · 25 Eylül karar noktasına "
             f"<b>{(date(2026,9,25)-bugun).days} gün</b> · aktif config: {len(AKTIF)}</p>")
    if dolan:
        H.append("<div class=uyari><b>25 Eylül'den önce dolacak:</b> "
                 + " · ".join(f"{escape(t['no'])} {escape(t['ad'])} (~{tahmin_gun(t,k)} gün)"
                              for t in dolan) + "</div>")
    H.append("<table><tr><th>madde</th><th>deney</th><th>tetik</th><th>durum</th>"
             "<th>doluluk</th><th>tahmini doluş</th><th>kaynak</th></tr>")
    for t in T:
        if t["tur"] == "sayısal":
            y = yuzde(t)
            d = tahmin_gun(t, k)
            cls = "dol" if y >= 90 else ("yak" if y >= 60 else "")
            tah = (f"~{d} gün · {(pd.Timestamp(bugun)+pd.Timedelta(days=d)):%d %b}"
                   if d else "DOLDU")
            H.append(f"<tr><td><b>{escape(t['no'])}</b></td><td>{escape(t['ad'])}"
                     f"<div class=not>{escape(t['not_'])}</div></td>"
                     f"<td><span class='rz s'>sayısal</span></td>"
                     f"<td class=n>{t['simdi']:,} / {t['hedef']:,}<div class=not>"
                     f"{escape(t['birim'])}</div></td>"
                     f"<td><div class=bar><i class='{cls}' style='width:{y:.0f}%'></i></div>"
                     f"<div class=not>%{y:.0f}</div></td>"
                     f"<td class=n>{tah}</td><td class=not>{escape(t['kaynak'])}</td></tr>")
        else:
            kaldi = t["simdi"]
            H.append(f"<tr><td><b>{escape(t['no'])}</b></td><td>{escape(t['ad'])}"
                     f"<div class=not>{escape(t['not_'])}</div></td>"
                     f"<td><span class='rz t'>tarih</span></td>"
                     f"<td class=n>{t['hedef']:%d.%m.%Y}</td><td>—</td>"
                     f"<td class=n>{kaldi} gün</td><td class=not>{escape(t['kaynak'])}</td></tr>")
    H.append("</table>")
    H.append(f"<p class=not style='margin-top:22px'>Üretildi: {datetime.now():%d.%m.%Y %H:%M} · "
             "<code>kod/deney_durum.py</code> — salt-okunur, hiçbir mevcut dosyaya dokunmaz. "
             "Tetikler betiğin <code>tetikler()</code> tablosunda elle tutulur; BEKLEYENLER.md "
             "değişirse burası da güncellenmeli.</p>")
    H.append("</div>")
    CIKTI.parent.mkdir(exist_ok=True)
    CIKTI.write_text("\n".join(H), encoding="utf-8")
    print(f"\n  yazıldı: {CIKTI}")


if __name__ == "__main__":
    main()
