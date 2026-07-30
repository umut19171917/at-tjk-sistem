"""
altili_ayrisma_test.py — "GENISLIGI, BOT1 ile KAMUNUN AYRISTIGI AYAGA VER" backtesti (K68 adayi).
OFFLINE, SALT-OKUNUR: canliya / takip'e / hicbir veri dosyasina DOKUNMAZ. Sadece okur, rapor basar.

FIKIR NEREDEN GELDI (BEKLEYENLER #7, K65+K67 zincirinin sonucu):
  K65: acgozlu (isabet-maksimize) dagitim SEKLI duzeltti ama parayi kotulestirdi -- cunku
       guvenilen ayaga tek at koymak = kamu favorisine tek at = kalabalik havuz.
  K67: Bot2 pratikte kamunun kendisi (favori ortakligi %89,9). Bot1 (oran-kor) kalabaliktan
       ayri ve BUYUK temettu bolgesine erisiyor (bot2 225 isabette 50bin ustu SIFIR;
       bot1 123 isabette 100bin ustu UC kez). Ama bot1'i tek basina kullanmak isabetten
       cok goturuyor (favori tutturma %29,1 vs %35,7).
  BURADAKI SENTEZ: bot2 ile SEC (isabeti koru), ama GENISLIGI bot1 ile kamunun en cok
  AYRISTIGI ayaga ver. Boylece kalabaliktan ayriligi, en ucuz oldugu yerden satin al.

DAGITICI (acgozlu'nun agirlikli hali):
  Her ayakta 1 atla basla; butce dolana dek "kazanc/bedel" orani en yuksek ati ekle.
    kazanc = log(1 + p_yeni/P_i) * (1 + w * D_i)      <-- D_i = o ayagin AYRISMA skoru
    bedel  = log((k+1)/k)
  D_i = 0.5 * sum |bot1_p - kamu_p|  (toplam degisim uzakligi; 0 = ayni fikirde, 1 = tamamen ayri)
  w = 0 -> saf acgozlu (K65). w buyudukce ayrisan ayaga daha cok at.
  SECIM SIRASI HEP bot2 (isabet korunur); degisen sadece hangi ayaga genislik verildigi.

DURUSTLUK NOTU: w icin birden fazla deger taranir (0/0.5/1/2/4). Bu bir COKLU KIYAS'tir --
en iyi cikan w'yi "bulgu" saymak overfit olur. Karar icin: (a) egilim monoton mu, (b) esli
fark GA'si sifiri disliyor mu, (c) en iyi w bir sonraki butcede de ayni mi.
"""
import math
import sys
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_backtest import kupon_kur, kupon_kur_acgozlu  # noqa: E402

BOT1CSV = KOK / "veri" / "altili_olasilik_bot1.csv"
EXCL_SEHIR = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
KAPSAM, BANKER = 0.75, 0.70
WLER = [0.0, 0.5, 1.0, 2.0, 4.0]
BUTCELER = [96, 288, 900]
RNG = np.random.default_rng(20260731)
NBOOT = 4000


def ayrisma_skoru(b1, km):
    """b1, km: ayni ayaktaki at olasiliklari (dizi). Toplam degisim uzakligi [0,1]."""
    a = np.asarray(b1, float); b = np.asarray(km, float)
    sa, sb = a.sum(), b.sum()
    if sa <= 0 or sb <= 0:
        return 0.0
    return float(0.5 * np.abs(a / sa - b / sb).sum())


def kupon_kur_ayrisma(ayak_atlari, agirlik, max_kombo, w):
    """acgozlu + ayrisma agirligi. ayak_atlari: bot2 (no,p) listeleri. agirlik: 6 elemanli D_i."""
    sr = [sorted([(n, p) for n, p in a if pd.notna(p) and p > 0], key=lambda x: -x[1])
          for a in ayak_atlari]
    if len(sr) != 6 or any(len(s) == 0 for s in sr):
        return [set() for _ in range(6)]
    kk = [1] * 6
    P = [s[0][1] for s in sr]
    while True:
        kombo = int(np.prod(kk))
        en, eno = None, 0.0
        for j in range(6):
            if kk[j] >= len(sr[j]):
                continue
            if kombo // kk[j] * (kk[j] + 1) > max_kombo:
                continue
            p = sr[j][kk[j]][1]
            bedel = math.log((kk[j] + 1) / kk[j])
            kazanc = math.log1p(p / P[j]) * (1.0 + w * agirlik[j])
            o = kazanc / bedel if bedel > 0 else 0.0
            if o > eno:
                eno, en = o, j
        if en is None:
            break
        P[en] += sr[en][kk[en]][1]
        kk[en] += 1
    return [set(n for n, _ in sr[j][:kk[j]]) for j in range(6)]


def calis(olaylar, pm2, pmD, wmap, max_kombo, mod, w=0.0):
    """mod: 'ayrisma' | 'acgozlu' | 'kapsam'. Doner (maliyet, getiri6, isabet, temettuler, sekil)."""
    mal, g6, a6, div, sek = [], [], 0, [], []
    for o in olaylar:
        legs = [int(o[f"leg{i+1}"]) for i in range(6)]
        aa, kz, ag, ok = [], [], [], True
        for rk in legs:
            a = pm2.get(rk); dd = pmD.get(rk); wn = wmap.get(rk)
            if not a or dd is None or wn is None:
                ok = False; break
            aa.append(a); ag.append(dd); kz.append(wn)
        if not ok:
            continue
        if mod == "ayrisma":
            sec = kupon_kur_ayrisma(aa, ag, max_kombo, w)
        elif mod == "acgozlu":
            sec = kupon_kur_acgozlu(aa, max_kombo)
        else:
            sec = kupon_kur(aa, KAPSAM, max_kombo, BANKER)
        gen = [len(s) for s in sec]
        nk = int(np.prod(gen))
        if nk == 0:
            continue
        mal.append(nk); sek.append(gen)
        if all(kz[i] in sec[i] for i in range(6)):
            t = o.get("t6_div")
            v = float(t) if pd.notna(t) else 0.0
            g6.append(v); a6 += 1; div.append(v)
        else:
            g6.append(0.0)
    return np.array(mal, float), np.array(g6), a6, np.array(div), np.array(sek)


def boot(mal, get):
    idx = RNG.integers(0, len(mal), size=(NBOOT, len(mal)))
    r = (get[idx].sum(1) - mal[idx].sum(1)) / mal[idx].sum(1) * 100
    return np.percentile(r, 2.5), np.percentile(r, 97.5)


def fark(m0, g0, m1, g1):
    n = min(len(m0), len(m1))
    idx = RNG.integers(0, n, size=(NBOOT, n))
    r0 = (g0[idx].sum(1) - m0[idx].sum(1)) / m0[idx].sum(1) * 100
    r1 = (g1[idx].sum(1) - m1[idx].sum(1)) / m1[idx].sum(1) * 100
    d = r1 - r0
    lo, hi = np.percentile(d, 2.5), np.percentile(d, 97.5)
    return np.median(d), lo, hi, (lo <= 0 <= hi)


def main():
    p = pd.read_csv(BOT1CSV, low_memory=False)
    olay = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    olay["yil"] = pd.to_datetime(olay["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    olay = olay[~olay["sehir"].isin(EXCL_SEHIR)]
    oos = list(olay[olay.yil >= 2025].to_dict("records"))

    pm2, pmD, wmap = {}, {}, {}
    for rk, g in p.groupby("race_kod"):
        pm2[rk] = list(zip(g["no"], g["bot2"]))
        pmD[rk] = ayrisma_skoru(g["bot1"].values, g["kamu"].values)
        w = g.loc[g["kazandi"] == 1, "no"]
        if len(w):
            wmap[rk] = int(w.iloc[0])

    ds = np.array(list(pmD.values()))
    print("=" * 100)
    print("ALTILI AYRISMA TESTI — 'genisligi bot1 ile kamunun ayristigi ayaga ver' (OFFLINE)")
    print(f"OOS olay: {len(oos)} | ayrisma skoru D: ort={ds.mean():.3f} medyan={np.median(ds):.3f} "
          f"min={ds.min():.3f} max={ds.max():.3f}")
    print("ROI(6) = SADECE 6/6 oder (durust zemin). w=0 saf acgozlu (K65) = KIYAS TABANI.")
    print("=" * 100)

    for mk in BUTCELER:
        print(f"\n### BUTCE {mk} ###")
        print(f"{'w':>5} {'olay':>5} {'ort.kombo':>9} {'ROI(6)%':>9} {'ROI(6) GA':>18} "
              f"{'6/6':>4} {'isabet%':>7} {'ort.temettu':>11} {'medyan':>9}")
        taban = None
        for w in WLER:
            mal, g6, a6, div, sek = calis(oos, pm2, pmD, wmap, mk, "ayrisma", w)
            roi = (g6.sum() - mal.sum()) / mal.sum() * 100
            lo, hi = boot(mal, g6)
            print(f"{w:>5.1f} {len(mal):>5} {mal.mean():>9.1f} {roi:>+9.1f} [{lo:>+7.1f},{hi:>+7.1f}] "
                  f"{a6:>4} {100*a6/len(mal):>7.2f} {(div.mean() if len(div) else 0):>11,.0f} "
                  f"{(np.median(div) if len(div) else 0):>9,.0f}")
            if w == 0.0:
                taban = (mal, g6)
            elif taban is not None:
                md, lo2, hi2, sifir = fark(taban[0], taban[1], mal, g6)
                print(f"       -> w={w} eksi w=0: {md:+.1f} puan, GA [{lo2:+.1f},{hi2:+.1f}]"
                      f"  ({'SIFIRI ICERIR -> sans' if sifir else 'sifir DISINDA'})")
        # referans: mevcut canli genis900 mantigi (kapsam)
        mal, g6, a6, div, _ = calis(oos, pm2, pmD, wmap, mk, "kapsam")
        print(f"{'kapsam':>5} {len(mal):>5} {mal.mean():>9.1f} "
              f"{(g6.sum()-mal.sum())/mal.sum()*100:>+9.1f} {'(mevcut canli mantik)':>18} "
              f"{a6:>4} {100*a6/len(mal):>7.2f} {(div.mean() if len(div) else 0):>11,.0f}")

    print("\n" + "=" * 100)
    print("KARAR OLCUTU: (a) w buyudukce ROI monoton iyilesiyor mu, (b) esli fark GA'si sifiri")
    print("disliyor mu, (c) ayni w farkli butcelerde de en iyi mi. Ucu birden saglanmazsa")
    print("bulgu YOK demektir (w taramasi coklu kiyas -- en iyisini secmek overfit olur).")
    print("=" * 100)


if __name__ == "__main__":
    main()
