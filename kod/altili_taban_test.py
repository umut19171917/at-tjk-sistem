"""
altili_taban_test.py — "SECIMIMIZ GERCEKTEN BIR SEY KATIYOR MU?" (K72 adayi).
OFFLINE, SALT-OKUNUR: hicbir dosyaya yazmaz, canliya dokunmaz.

SORU (kullanici, 2026-07-31): orta (96 kombo) durust zeminde -%19,4 getiriyor. Bu kesintiden
(%25-31) iyi gorunuyor. Peki bu MODELIN MARIFETI mi, yoksa "favorilere yaslanan her kupon boyle
cikar" mi? K67'de olctuk: Bot2 favorisi = kamu favorisi %89,9. Yani kuponumuz kalabaligin
kuponuna cok yakin olabilir.

YONTEM — ADIL KIYAS: her olayda once GERCEK orta kuponu kurulur, onun AYAK GENISLIKLERI
(or. [2,2,2,2,2,3]) alinir; sonra AYNI genislikle alternatif secimler kurulur. Boylece
MALIYET BIREBIR AYNI olur (ayni kombo sayisi) -> getiriler dogrudan kiyaslanabilir.

DORT SECICI:
  A) bot2   : GERCEK sistemimiz (harman)                -> olculen sey
  B) rastgele: her ayakta sahadan rastgele k at         -> "sans" taban cizgisi
  C) kamu   : her ayakta en dusuk oranli (favori) k at  -> "sadece kalabaligi kopyala"
  D) bot1   : oran-kor temel model                      -> "harman olmasa"
KIYASLAR: A-B (siralama bir sey katiyor mu?), A-C (kalabaligi yeniyor muyuz?), A-D (harman
gerekli mi?). Rastgele R kez tekrarlanir; esli bootstrap ile fark GA'lari verilir.

NOT: Bu test ROI'yi "sifirdan" olcmez; MALIYETI SABITLEYIP secicileri kiyaslar. Amac
"karli mi" degil, "secimimiz katma deger uretiyor mu".
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_backtest import kupon_kur  # noqa: E402

EXCL_SEHIR = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
KAPSAM, BANKER, KOMBO = 0.75, 0.70, 96
RASTGELE_TEKRAR = 25
RNG = np.random.default_rng(20260731)
NBOOT = 4000


def main():
    p = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    o = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    o["yil"] = pd.to_datetime(o["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    o = o[~o["sehir"].isin(EXCL_SEHIR)]

    saha = {}
    for rk, g in p.groupby("race_kod"):
        g = g.dropna(subset=["bot2", "kamu", "bot1"])
        if len(g) < 4:
            continue
        w = g.loc[g["kazandi"] == 1, "no"]
        if len(w) != 1:
            continue
        saha[int(rk)] = {"no": g["no"].astype(int).values,
                         "bot2": g["bot2"].values, "bot1": g["bot1"].values,
                         "kamu": g["kamu"].values, "kaz": int(w.iloc[0])}

    olaylar = []
    for r in o[o.yil >= 2025].to_dict("records"):
        legs = [int(r[f"leg{i+1}"]) for i in range(6)]
        if any(l not in saha for l in legs):
            continue
        aa = [list(zip(saha[l]["no"], saha[l]["bot2"])) for l in legs]
        sec = kupon_kur(aa, KAPSAM, KOMBO, BANKER)
        if any(len(s) == 0 for s in sec):
            continue
        div = float(r["t6_div"]) if pd.notna(r.get("t6_div")) else 0.0
        olaylar.append({"legs": legs, "sekil": [len(s) for s in sec],
                        "bot2_sec": sec, "div": div})
    n = len(olaylar)
    print("=" * 92)
    print("ALTILI TABAN CIZGISI — 'secimimiz bir sey katiyor mu?'  (OFFLINE)")
    print(f"OOS olay: {n} | butce {KOMBO} kombo | MALIYET tum seciciler icin BIREBIR AYNI")
    print("=" * 92)

    def topk(rk, alan, k):
        s = saha[rk]
        idx = np.argsort(-s[alan])[:k]
        return set(s["no"][idx].tolist())

    def calis(secici, tohum=None):
        rng = np.random.default_rng(tohum) if tohum is not None else None
        mal = np.zeros(n); od = np.zeros(n); hit = 0
        ayni = 0
        for i, e in enumerate(olaylar):
            secim = []
            for j, rk in enumerate(e["legs"]):
                k = e["sekil"][j]
                if secici == "bot2":
                    secim.append(e["bot2_sec"][j])
                elif secici == "rastgele":
                    nos = saha[rk]["no"]
                    secim.append(set(rng.choice(nos, size=min(k, len(nos)),
                                                replace=False).tolist()))
                else:
                    secim.append(topk(rk, secici, k))
            mal[i] = float(np.prod([len(s) for s in secim]))
            if all(saha[rk]["kaz"] in secim[j] for j, rk in enumerate(e["legs"])):
                od[i] = e["div"]; hit += 1
            if secici != "bot2" and all(secim[j] == e["bot2_sec"][j] for j in range(6)):
                ayni += 1
        return mal, od, hit, ayni

    sonuc = {}
    print(f"\n{'secici':10s} {'maliyet':>10} {'6/6':>4} {'isabet%':>7} {'ROI(6)':>9} "
          f"{'ort.temettu':>11}  {'bot2 ile AYNI kupon':>20}")
    for s, ad in (("bot2", "bot2 (BIZ)"), ("kamu", "kamu (favori)"), ("bot1", "bot1 (oran-kor)")):
        mal, od, hit, ayni = calis(s)
        sonuc[s] = (mal, od)
        roi = (od.sum() - mal.sum()) / mal.sum() * 100
        ort = od[od > 0].mean() if hit else 0
        ay = "-" if s == "bot2" else f"%{100*ayni/n:.1f}"
        print(f"{ad:10s} {mal.sum():>10,.0f} {hit:>4} {100*hit/n:>7.2f} {roi:>+8.1f}% "
              f"{ort:>11,.0f}  {ay:>20}")

    # rastgele: R tekrar
    rois, hits, aynilar = [], [], []
    r_mal = r_od = None
    for t in range(RASTGELE_TEKRAR):
        mal, od, hit, ayni = calis("rastgele", tohum=1000 + t)
        rois.append((od.sum() - mal.sum()) / mal.sum() * 100)
        hits.append(hit); aynilar.append(100 * ayni / n)
        if t == 0:
            r_mal, r_od = mal, od
    rois = np.array(rois)
    print(f"{'rastgele':10s} {r_mal.sum():>10,.0f} {np.mean(hits):>4.0f} "
          f"{100*np.mean(hits)/n:>7.2f} {rois.mean():>+8.1f}% {'':>11}  {f'%{np.mean(aynilar):.1f}':>20}")
    print(f"           (rastgele {RASTGELE_TEKRAR} tekrar: ROI %5-%95 arali "
          f"[{np.percentile(rois,5):+.1f}, {np.percentile(rois,95):+.1f}]; "
          f"isabet {min(hits)}-{max(hits)})")
    sonuc["rastgele"] = (r_mal, r_od)

    # ---- esli bootstrap farklari ----
    print("\nESLI FARKLAR (ayni olaylar, 4000 bootstrap) — bot2 EKSI digeri:")
    idx = RNG.integers(0, n, size=(NBOOT, n))
    m0, o0 = sonuc["bot2"]
    for s, ad in (("kamu", "kamu (favori)"), ("bot1", "bot1"), ("rastgele", "rastgele")):
        m1, o1 = sonuc[s]
        r0 = (o0[idx].sum(1) - m0[idx].sum(1)) / m0[idx].sum(1) * 100
        r1 = (o1[idx].sum(1) - m1[idx].sum(1)) / m1[idx].sum(1) * 100
        d = r0 - r1
        lo, hi = np.percentile(d, 2.5), np.percentile(d, 97.5)
        sifir = lo <= 0 <= hi
        print(f"   bot2 - {ad:16s}: {np.median(d):+7.1f} puan  GA [{lo:+7.1f}, {hi:+7.1f}]  "
              f"{'SIFIRI ICERIR -> fark yok' if sifir else 'sifir DISINDA -> gercek fark'}")

    print("\n" + "=" * 92)
    print("OKUMA: bot2 ile kamu arasindaki fark sifiri iceriyorsa -> kuponumuz fiilen")
    print("KALABALIGIN kuponu, model katma deger uretmiyor. bot2-rastgele farki sifiri")
    print("iceriyorsa -> siralamamiz sanstan ayirt edilemiyor (cok daha agir bir sonuc).")
    print("=" * 92)


if __name__ == "__main__":
    main()
