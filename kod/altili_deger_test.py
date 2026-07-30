"""
altili_deger_test.py — "DEGER SECIMI: bot2 / AGF^λ" backtesti (K75 adayi).
OFFLINE, SALT-OKUNUR: hicbir dosyaya yazmaz, canliya dokunmaz.

NEREDEN GELDI (K74): Altili havuzu ganyandan kotu kalibre. En guclu sapma: ganyanin AGF'den
cok daha sansli gordugu atlar 3,40 kat fazla kazaniyor. Yani secimi "kazanma olasiligi"na gore
degil, "olasilik / havuzun o ata verdigi pay" oranina gore yapmak EV'yi artirmali.

MANTIK (pari-mutuel EV): bir kombinasyonun beklenen getirisi
    EV ∝ Π(olasilik_i) x temettu,   temettu ∝ 1 / Π(havuz_payi_i)
  => EV ∝ Π( bot2_i / agf_i )
Yani her ayakta "deger orani" v = bot2/agf en yuksek atlari almak EV'yi maksimize eder.
AMA saf deger pesinde kosmak isabeti yerin dibine indirir (hep dip atlar secilir) ve
temettu HAVUZLA SINIRLI oldugu icin teorik EV gerceklesmez.
  -> O yuzden TEK PARAMETRELI aile taranir:   skor = bot2 / agf^λ
     λ=0   : saf bot2 (MEVCUT sistem, kiyas tabani)
     λ=1   : saf deger orani (EV-maksimize)
     arasi : karma

ADIL KIYAS: her olayda once GERCEK kupon (bot2 + kapsam kurali) kurulur, AYAK GENISLIKLERI
alinir; sonra ayni genislikle skor-siralamasina gore secim yapilir -> MALIYET BIREBIR AYNI.
Getiri GERCEK t6 temettusuyle hesaplanir. Esli bootstrap ile λ=0'a gore fark GA'lari.

UYARI (durustluk): buradaki AGF, yarisin RESMI/son AGF'sidir. Canlida kupon 30 dk kala
kuruluyor ve o andaki AGF biraz farkli olur (oran kaymasinin AGF karsiligi). Yani bu test
en-iyi-durum tahminidir; canli sonuc bundan bir miktar KOTU olur.
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_backtest import kupon_kur, kupon_kur_acgozlu  # noqa: E402
from altili_agf_yanlilik import agf_topla                 # noqa: E402

EXCL_SEHIR = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
KAPSAM, BANKER = 0.75, 0.70
LAMBDALAR = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5]
BUTCELER = [96, 900]
RNG = np.random.default_rng(20260731)
NBOOT = 4000
AGF_TABAN = 0.002        # AGF sifira yakinsa skor patlamasin (yarim binde taban)


def main():
    print("AGF toplaniyor...")
    agf = agf_topla()
    agf = agf.groupby(["race_kod", "no"], as_index=False)["agf"].mean()
    p = pd.read_csv(KOK / "veri" / "altili_olasilik.csv", low_memory=False)
    p = p.merge(agf, on=["race_kod", "no"], how="inner")
    print(f"  AGF eslesen at-satiri: {len(p):,} / kosu {p.race_kod.nunique():,}")

    o = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    o["yil"] = pd.to_datetime(o["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    o = o[~o["sehir"].isin(EXCL_SEHIR)]

    saha, kaz = {}, {}
    for rk, g in p.groupby("race_kod"):
        g = g.dropna(subset=["bot2", "agf"])
        if len(g) < 4:
            continue
        w = g.loc[g["kazandi"] == 1, "no"]
        if len(w) != 1:
            continue
        saha[int(rk)] = (g["no"].astype(int).values,
                         g["bot2"].values.astype(float),
                         np.clip(g["agf"].values.astype(float), AGF_TABAN, None))
        kaz[int(rk)] = int(w.iloc[0])

    olaylar = []
    for r in o[o.yil >= 2025].to_dict("records"):
        legs = [int(r[f"leg{i+1}"]) for i in range(6)]
        if any(l not in saha for l in legs):
            continue
        div = float(r["t6_div"]) if pd.notna(r.get("t6_div")) else 0.0
        olaylar.append({"legs": legs, "div": div})
    n = len(olaylar)
    print(f"  AGF'si TAM olan OOS olay: {n} (K72'de 1433 idi)")

    print("\n" + "=" * 100)
    print("DEGER SECIMI TESTI —  skor = bot2 / AGF^λ   (λ=0 MEVCUT sistem)")
    print("Maliyet her λ icin BIREBIR AYNI (ayni ayak genislikleri). Getiri GERCEK temettu.")
    print("=" * 100)

    for butce in BUTCELER:
        # once taban kuponun sekli
        sekiller = []
        for e in olaylar:
            aa = [list(zip(saha[l][0], saha[l][1])) for l in e["legs"]]
            s = (kupon_kur_acgozlu(aa, butce) if butce == 900
                 else kupon_kur(aa, KAPSAM, butce, BANKER))
            sekiller.append([len(x) for x in s])

        print(f"\n### BUTCE {butce} ({'acgozlu' if butce == 900 else 'kapsam'} sekli) ###")
        print(f"{'λ':>5} {'maliyet':>12} {'6/6':>4} {'isabet%':>8} {'ROI(6)':>9} "
              f"{'ROI GA':>18} {'ort.temettu':>11} {'medyan':>9}")
        sakla = {}
        for lam in LAMBDALAR:
            mal = np.zeros(n); od = np.zeros(n); hit = 0; divs = []
            for i, e in enumerate(olaylar):
                sec = []
                for j, l in enumerate(e["legs"]):
                    no, b2, ag = saha[l]
                    skor = b2 / (ag ** lam) if lam else b2
                    k = sekiller[i][j]
                    sec.append(set(no[np.argsort(-skor)[:k]].tolist()))
                mal[i] = float(np.prod([len(x) for x in sec]))
                if all(kaz[l] in sec[j] for j, l in enumerate(e["legs"])):
                    od[i] = e["div"]; hit += 1; divs.append(e["div"])
            roi = (od.sum() - mal.sum()) / mal.sum() * 100
            idx = RNG.integers(0, n, size=(NBOOT, n))
            r = (od[idx].sum(1) - mal[idx].sum(1)) / mal[idx].sum(1) * 100
            lo, hi = np.percentile(r, 2.5), np.percentile(r, 97.5)
            dv = np.array(divs) if divs else np.array([0.0])
            print(f"{lam:>5.2f} {mal.sum():>12,.0f} {hit:>4} {100*hit/n:>8.2f} {roi:>+8.1f}% "
                  f"[{lo:>+7.1f},{hi:>+7.1f}] {dv.mean():>11,.0f} {np.median(dv):>9,.0f}")
            sakla[lam] = (mal, od)

        m0, o0 = sakla[0.0]
        print("   esli fark (λ eksi λ=0):")
        for lam in LAMBDALAR[1:]:
            m1, o1 = sakla[lam]
            idx = RNG.integers(0, n, size=(NBOOT, n))
            r0 = (o0[idx].sum(1) - m0[idx].sum(1)) / m0[idx].sum(1) * 100
            r1 = (o1[idx].sum(1) - m1[idx].sum(1)) / m1[idx].sum(1) * 100
            d = r1 - r0
            lo, hi = np.percentile(d, 2.5), np.percentile(d, 97.5)
            print(f"      λ={lam:<4} : {np.median(d):+8.1f} puan  GA [{lo:+8.1f},{hi:+8.1f}]  "
                  f"{'sifiri icerir' if lo <= 0 <= hi else 'SIFIR DISINDA'}")

    print("\n" + "=" * 100)
    print("KARAR: λ>0'da ROI hem YUKSELIYOR hem esli fark GA'si sifiri DISLIYORSA gercek kenar.")
    print("Sadece ort.temettu yukselip ROI degismiyorsa: deger yakalaniyor ama isabet kaybi")
    print("onu goturuyor (K65/K67'deki ayni gerilim).")
    print("=" * 100)


if __name__ == "__main__":
    main()
