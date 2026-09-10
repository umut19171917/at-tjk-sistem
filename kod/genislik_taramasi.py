"""
genislik_taramasi.py — SABIT GENISLIKLI Altili kuponlarinin kar/zarar taramasi (K164).

SORU: "her ayaga sabit k at yazsaydik ne olurdu?" k = 3, 4, 5.

YONTEM (canli veriye dayanir, arsiv backtestine DEGIL):
  - Secim: `veri/altili_kupon_ani.csv` — kuponun KURULDUGU andaki puan vektoru. Yani karar,
    o gun gercekten elimizde olan bilgiyle veriliyor; K130 sizintisi (arsivdeki ganyan_muhtemel
    == kapanis) bu dosyada YOKTUR.
  - Kazanan: `altili_canli.kazananlar_kumesi` — yani EKURI genisletmesi dahil, canli sistemin
    bugun kullandigi kuralin AYNISI (K162/K162-EK).
  - Odul: yalnizca 6/6'da, o Altili'nin RESMI temettusu (`rapor_ortak.altili_odeme`, onbellek).
  - Bedel: k**6 x birim fiyat (pist'e gore 1,25 / 1,00 — `ro.birim_fiyat`).

DURUSTLUK KURALI — "BILINMEZ" OLAY ATILIR, TAHMIN EDILMEZ:
  Bir Altili ancak 6 ayaginin da (a) kupon-ani fotografi VE (b) bilinen kazanani varsa sayilir.
  Eksik olan pencere iyimser/kotumser bantla DOLDURULMAZ, tamamen disarida birakilir. Boylece
  tek bir sayi cikar; K155-EK'in "mantiksal sinir" bandina gerek kalmaz.

NEDEN AYRI BASE: kupon-ani kaydi 25 Tem'de (30 dk) ve 15 Agu'da (15 dk) basladi. Oncesi icin
fotograf YOK -> o donem hicbir k icin sayilmaz. Bu yuzden buradaki TL'ler gercek sicilin
tamamiyla degil, AYNI PENCEREdeki gercek kuponlarla kiyaslanmalidir (rapor bunu basar).

SALT-OKUNUR: hicbir dosyaya yazmaz.
Elle: python kod/genislik_taramasi.py [--k 3,4,5]
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
import rapor_ortak as ro                                     # noqa: E402
from altili_canli import KONFIG, kazananlar_kumesi           # noqa: E402

ANI = KOK / "veri" / "altili_kupon_ani.csv"
KUPON = KOK / "veri" / "altili_kupon.csv"
SONUC = KOK / "veri" / "ham" / "sonuclar"

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


def tara(k_listesi=(3, 4, 5)):
    ani = pd.read_csv(ANI, low_memory=False)
    for c in ("seq", "dk_grup", "ayak", "race_kod", "no", "bot1", "bot2"):
        ani[c] = pd.to_numeric(ani[c], errors="coerce")
    kaz = _kazananlar()

    # gercek kuponlarin bedeli/odulu — ayni pencerede kiyas zemini olsun diye
    kup = pd.read_csv(KUPON, low_memory=False)
    for c in ("seq", "ayak", "race_kod", "nat", "tuttu"):
        kup[c] = pd.to_numeric(kup[c], errors="coerce")

    sonuc = {}
    for etiket, sut, dkg in ZEMIN:
        g = ani[ani["dk_grup"] == dkg]
        for (tarih, pist, seq), pen in g.groupby(["tarih", "pist", "seq"]):
            ayaklar = sorted(pen["ayak"].dropna().unique())
            if len(ayaklar) != 6:
                continue                                     # eksik fotograf -> olay ATILIR
            atlar, kazanan_var = [], True
            for a in ayaklar:
                sr = pen[pen["ayak"] == a].dropna(subset=[sut])
                if sr.empty:
                    kazanan_var = False
                    break
                rk = sr["race_kod"].dropna()
                if rk.empty or int(rk.iloc[0]) not in kaz:
                    kazanan_var = False                      # sonucu bilinmeyen ayak -> ATILIR
                    break
                atlar.append((sr.sort_values(sut, ascending=False), kaz[int(rk.iloc[0])]))
            if not kazanan_var:
                continue
            birim = ro.birim_fiyat(pist)
            res = ro.altili_odeme(tarih, pist, int(seq), cek=False)
            temettu = float(res["temettu"]) if res["temettu"] else 0.0
            for k in k_listesi:
                # BEDEL k**6 DEGIL, GERCEK KOMBINASYONDUR. Ayakta k'dan az at kosuyorsa
                # sahadaki hepsi yazilir; o ayak hem UCUZLAR hem de kesin tutar. Olculdu:
                # ayaklarin %0,8'inde 5'ten, %5,6'sinda 6'dan az at var -> k=6'da k**6
                # varsaymak bedeli sisirir ve isabeti bedavaya verirdi. Ikisi de ayni
                # yerden, min(k, sahadaki) ile hesaplanir ki maliyet ve isabet TUTARLI olsun.
                secimler = [{int(x) for x in sr.head(k)["no"]} for sr, _ in atlar]
                kombo = 1
                for s in secimler:
                    kombo *= len(s)
                tut = [bool(s & w) for s, (_, w) in zip(secimler, atlar)]
                d = sonuc.setdefault((etiket, k), {"kupon": 0, "bedel": 0.0, "odul": 0.0,
                                                   "tam": 0, "ayak": 0, "kombo": 0})
                d["kupon"] += 1
                d["bedel"] += kombo * birim
                d["kombo"] += kombo
                d["ayak"] += sum(tut)
                if all(tut):
                    d["tam"] += 1
                    d["odul"] += temettu
    return sonuc, kup


def _satir(ad, d, ek=""):
    net = d["odul"] - d["bedel"]
    roi = f"%{100 * net / d['bedel']:+.1f}" if d["bedel"] else "-"
    kb = d["bedel"] / d["kupon"] if d.get("kupon") else 0
    ayak = f"{100 * d['ayak'] / (6 * d['kupon']):.1f}%" if d.get("ayak") else "  -  "
    return (f"{ad:<22} {d['kupon']:>5} {d['tam']:>5} {ayak:>7} {kb:>11,.0f} "
            f"{d['bedel']:>14,.0f} {d['odul']:>14,.0f} {net:>+15,.0f} {roi:>9}{ek}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", default="3,4,5,6")
    args = ap.parse_args()
    ks = [int(x) for x in args.k.split(",")]

    sonuc, kup = tara(ks)
    bas = (f"{'zemin / genislik':<22} {'kupon':>5} {'6/6':>5} {'ayak':>7} {'kupon TL':>11} "
           f"{'bedel':>14} {'odul':>14} {'net':>15} {'ROI':>9}")
    print("\n" + "=" * len(bas))
    print("SABIT GENISLIKLI ALTILI — kupon-ani verisiyle, EKURI kurali dahil (K164)")
    print("=" * len(bas))
    print(bas)
    print("-" * len(bas))
    for etiket, _, _ in ZEMIN:
        for k in ks:
            d = sonuc.get((etiket, k))
            if d:
                print(_satir(f"{etiket}  sabit-{k}", d))
        print()

    # iki kuponluk portfoy: bot1@30 + bot2@30 (K157'nin "hangi ikisi" cevabi)
    print("-" * len(bas))
    print("IKI KUPONLUK PORTFOY (bot1@30dk + bot2@30dk, ayni olaylarda)")
    for k in ks:
        a, b = sonuc.get(("bot1 @30dk", k)), sonuc.get(("bot2 @30dk", k))
        if a and b:
            d = {"kupon": a["kupon"] + b["kupon"], "tam": a["tam"] + b["tam"],
                 "bedel": a["bedel"] + b["bedel"], "odul": a["odul"] + b["odul"],
                 "ayak": a["ayak"] + b["ayak"], "kombo": a["kombo"] + b["kombo"]}
            print(_satir(f"  sabit-{k}", d))
    print("=" * len(bas))
    print("NOT 1: yalniz 6 ayaginin da kupon-ani fotografi VE bilinen kazanani olan Altililar")
    print("       sayildi; eksik olan olay iyimser/kotumser bantla DOLDURULMADI, atildi.")
    print("NOT 2: 'kupon TL' ortalamadir -- ayakta k'dan az at kosarsa sahadaki hepsi yazilir,")
    print("       o kupon k**6'dan UCUZ olur (ayaklarin %5,6'sinda 6'dan az at var).")


if __name__ == "__main__":
    main()
