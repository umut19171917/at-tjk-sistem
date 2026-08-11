"""
altili_banker_takasi_test.py — K101: "ALTERNATIF KUPON" (banker takasi) olcumu.
OFFLINE, SALT-OKUNUR: canliya/CSV'lere/config'e DOKUNMAZ, hicbir dosyaya yazmaz.

NEREDEN GELDI: kullanici 10 Agu 2026'da tarif etti — "alternatif altili kuponlari, oyuncunun
guvenip tek attigi ayagin yikilmasi olasiligi uzerine kurulur; ikinci kuponda ilk kuponun
banker ayagi daha cok atla yazilir, varsa diger favori ayak tek atilir."

BANKER TANIMI (kullanicinin duzeltmesi, 10 Agu): banker KESINLIK degil GORECE guvendir --
"bu ayakta bu ata guveniyorum, digerlerini guclu tutayim". Bu tanim onemliydi: ben once
BANKER_ESIK=0,70'i arayip "bizde banker yok" demistim (bot1_900'un 33 tek-at ayaginin
SIFIRI esigi geciyor, ort. tepe olasilik 0,40). Kullanicinin tanimiyla banker her Altilida
tanimli: tepe atin olasiliginin en yuksek oldugu ayak.

KURAL:
  guven siralamasi: i = 1. (en guvenilen ayak), j = 2.
    A: i = 1 at (banker),  j >= 2 at
    B: j = 1 at (banker),  i >= 2 at   <- A'nin tek kirilma noktasini sigortalar
  Kalan dort ayak iki kuponda da acgozlu dagiticidan. Butce asilirsa i/j DISINDAKI en genis
  ayaktan kisilir. Serbest parametre YOK (asgari genislik 2).

NEDEN YENI BIR SEY: A u B, (i,j) duzleminde ARTI seklidir; hicbir TEK kupon bu sekli kuramaz
  (kupon zorunlu olarak kartezyen carpim = dikdortgen, K98-h). K98-g'deki "rotasyon" testi
  AYAK SIRASINA goreydi (1-3 dar / 4-6 genis), modelin guveniyle ilgisi yoktu ve kupon basina
  UC banker koyuyordu -> bu fikri KARSILAMIYORDU.

KARAR OLCUTU (SONUC GORULMEDEN BAGLANDI): cift, AYNI TOPLAM PARADAKI tek dikdortgeni
  (a) ROI(-1)  [en buyuk tek kupon cikarilinca kalan ROI, K98-e olcutu]  VE
  (b) ort. temettu  [mekanizmanin iddia ettigi kanal]
  IKISINDE DE gecmeli. Birinde bile gecemezse RED. Ham ROI/isabet BILGI amaclidir.

SONUC (K101): dort hucrenin dordunde de RED. Ayrica UYGULAMA DERSI: ilk turda B'de banker
  ayagini yalnizca "serbest biraktim"; acgozlu en guvenilen ayaga zaten az at verdigi icin
  o ayak olaylarin %45-59'unda YINE tek atta kaldi -> sigorta hic olusmadi. Zorlanmis
  (>=2 at) surumde sigorta %100 olustu ve sonuc yine RED. Bu betik ZORLANMIS surumdur;
  --gevsek ile ilk tur da uretilebilir.

ZEMIN: yalniz 6/6 oder (K57/K65). Birim 1,25 TL. OOS 2025-26, izinli pistler. Kazanan
kombinasyon iki kuponda da varsa IKI KEZ oder (ayri kuponlar).
Elle: python altili_banker_takasi_test.py [--gevsek]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_backtest import kupon_kur_acgozlu  # noqa: E402

EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
BIRIM = 1.25
NBOOT = 3000
RNG = np.random.default_rng(20260810)


def veri():
    p = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    p2, p1, w = {}, {}, {}
    for rk, g in p.groupby("race_kod"):
        p2[rk] = sorted([(int(n), float(v)) for n, v in zip(g["no"], g["bot2"])
                         if pd.notna(v) and v > 0], key=lambda x: -x[1])
        p1[rk] = sorted([(int(n), float(v)) for n, v in zip(g["no"], g["bot1"])
                         if pd.notna(v) and v > 0], key=lambda x: -x[1])
        k = g.loc[g["kazandi"] == 1, "no"]
        if len(k):
            w[rk] = int(k.iloc[0])
    o = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    o["yil"] = pd.to_datetime(o["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    o = o[~o["sehir"].isin(EXCL)]
    return p2, p1, w, list(o[o.yil >= 2025].to_dict("records"))


def kur_arti(ayak, tek_leg, genis_leg, maxk, zorla=True):
    """tek_leg = 1 at (banker); zorla ise genis_leg >= 2 at (sigorta); kalan acgozlu."""
    y = [(a[:1] if z == tek_leg else a) for z, a in enumerate(ayak)]
    S = [set(x) for x in kupon_kur_acgozlu(y, maxk)]
    if zorla and len(S[genis_leg]) < 2 and len(ayak[genis_leg]) >= 2:
        S[genis_leg] = {no for no, _ in ayak[genis_leg][:2]}
        while int(np.prod([len(x) for x in S])) > maxk:
            aday = [z for z in range(6) if z not in (tek_leg, genis_leg) and len(S[z]) > 1]
            if not aday:
                break
            z = max(aday, key=lambda q: len(S[q]))
            pm = dict(ayak[z])
            S[z].discard(min(S[z], key=lambda n: pm.get(n, 0.0)))
    return S


def calis(olay, P, W, mod, her=None, tek=None, zorla=True):
    rs = []
    for oi, oo in enumerate(olay):
        ayak, kaz, ok = [], [], True
        for z in range(6):
            rk = int(oo[f"leg{z+1}"])
            if rk not in P or rk not in W or len(P[rk]) < 2:
                ok = False
                break
            ayak.append(P[rk]); kaz.append(W[rk])
        if not ok:
            continue
        div = float(oo["t6_div"]) if pd.notna(oo.get("t6_div")) else 0.0
        if mod == "cift":
            guven = [a[0][1] for a in ayak]
            i, j = sorted(range(6), key=lambda z: -guven[z])[:2]
            A = kur_arti(ayak, i, j, her, zorla)
            B = kur_arti(ayak, j, i, her, zorla)
            if any(len(x) == 0 for x in A) or any(len(x) == 0 for x in B):
                continue
            rs.append({"kombo": int(np.prod([len(x) for x in A]))
                                + int(np.prod([len(x) for x in B])),
                       "isabet": int(all(kaz[z] in A[z] for z in range(6)))
                                 + int(all(kaz[z] in B[z] for z in range(6))),
                       "div": div, "sig": len(B[i]),
                       "oldu_i": int(kaz[i] not in A[i]),
                       "kurtardi": int(kaz[i] not in A[i]
                                       and all(kaz[z] in B[z] for z in range(6)))})
        else:
            S = kupon_kur_acgozlu(ayak, tek)
            if any(len(x) == 0 for x in S):
                continue
            rs.append({"kombo": int(np.prod([len(x) for x in S])),
                       "isabet": int(all(kaz[z] in S[z] for z in range(6))),
                       "div": div, "sig": np.nan, "oldu_i": np.nan, "kurtardi": np.nan})
    return rs


def ozet(rs, ad):
    mal = np.array([r["kombo"] * BIRIM for r in rs])
    get = np.array([r["div"] * r["isabet"] for r in rs])
    tut = np.array([int(r["isabet"] > 0) for r in rs])
    idx = RNG.integers(0, len(mal), size=(NBOOT, len(mal)))
    roi = (get[idx].sum(1) - mal[idx].sum(1)) / mal[idx].sum(1) * 100
    g1 = get.copy(); g1[np.argsort(-get)[:1]] = 0
    return {"ad": ad, "n": len(rs), "kombo": mal.mean() / BIRIM, "bedel": mal.mean(),
            "tut": int(tut.sum()),
            "roi": (get.sum() - mal.sum()) / mal.sum() * 100,
            "roi1": (g1.sum() - mal.sum()) / mal.sum() * 100,
            "lo": np.percentile(roi, 2.5), "hi": np.percentile(roi, 97.5),
            "div": get[get > 0].mean() if (get > 0).any() else 0.0, "rs": rs}


def yaz(s):
    print(f"{s['ad']:>26} {s['kombo']:>6.0f} {s['bedel']:>7,.0f} TL {s['tut']:>5} "
          f"%{100*s['tut']/s['n']:>6.1f} {s['roi']:>+7.1f} {s['roi1']:>+9.1f} "
          f"[{s['lo']:>+6.1f},{s['hi']:>+6.1f}] {s['div']:>11,.0f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gevsek", action="store_true",
                    help="B'de banker ayagini ZORLAMA (1. turdaki kusurlu surum)")
    args = ap.parse_args()
    zorla = not args.gevsek
    p2, p1, W, olay = veri()
    print(f"OOS olay (2025-26, izinli pistler): {len(olay)}")
    print(f"sigorta {'ZORLANIYOR (>=2 at)' if zorla else 'ZORLANMIYOR (kusurlu surum)'}")
    print("OLCUT: cift, ayni paradaki tek dikdortgeni hem ROI(-1)'de HEM temettude gecmeli.\n")
    sonuc = {}
    for etiket, P in (("bot2", p2), ("bot1", p1)):
        print("=" * 118)
        print(f"{etiket.upper()} — banker takasi cifti vs ayni paradaki TEK kupon")
        print("=" * 118)
        print(f"{'kupon':>26} {'kombo':>6} {'bedel':>10} {'6/6':>5} {'siklik':>7} "
              f"{'ROI%':>7} {'ROI(-1)%':>9} {'%95 GA':>17} {'ort.temettu':>11}")
        for her in (450, 900):
            c = ozet(calis(olay, P, W, "cift", her=her, zorla=zorla), f"CIFT {etiket} 2x{her}")
            t = ozet(calis(olay, P, W, "tek", tek=2 * her), f"tek {etiket} @{2*her}")
            yaz(c); yaz(t)
            sonuc[(etiket, her)] = (c, t)
            sig = np.array([r["sig"] for r in c["rs"]])
            old = np.array([r["oldu_i"] for r in c["rs"]])
            kur = np.array([r["kurtardi"] for r in c["rs"]])
            print(f"      A banker ayaginda OLDU: %{100*old.mean():.0f}  |  "
                  f"bunlarin B tarafindan KURTARILANI: {int(kur.sum())} olay "
                  f"(%{100*kur.mean():.1f})  |  B'de banker ayagi ort. {sig.mean():.2f} at")
            print("  " + "-" * 114)
    print("=" * 118)
    print("KARAR — onceden baglanan olcut")
    print("=" * 118)
    hepsi_red = True
    for (etiket, her), (c, t) in sonuc.items():
        a, b = c["roi1"] > t["roi1"], c["div"] > t["div"]
        hepsi_red = hepsi_red and not (a and b)
        print(f"  {etiket} 2x{her} vs tek@{2*her}: "
              f"ROI(-1) {c['roi1']:+.1f} vs {t['roi1']:+.1f} [{'GECTI' if a else 'KALDI'}]   "
              f"temettu {c['div']:,.0f} vs {t['div']:,.0f} [{'GECTI' if b else 'KALDI'}]   "
              f"=> {'GECTI' if (a and b) else 'RED'}")
    print(f"\n  SONUC: {'FIKIR OLCUMLE REDDEDILDI (K101)' if hepsi_red else 'en az bir hucre gecti'}")
    print("\n  NEDEN (K101): A banker ayagini olaylarin yarisindan fazlasinda kaciriyor —")
    print("  teshis DOGRU. Ama B o olumlerin ancak ~%3'unu kurtariyor: B'nin kurtarabilmesi")
    print("  icin A'nin DIGER BES ayagi tutturmus olmasi gerekir. Ustelik B, 2. ayagi tek ata")
    print("  indirdigi icin YENI bir kirilma noktasi yaratir. Sigorta bir delik kapatip")
    print("  baska delik aciyor; iki kuponun ORTAK dort ayagi da iki kez satin aliniyor.")


if __name__ == "__main__":
    main()
