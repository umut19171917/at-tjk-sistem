"""
altili_kap_test.py — "ORTA'YI GENISLETMELI MIYIZ?" backtesti (K57 adayi).
OFFLINE, SALT-OKUNUR: canli sisteme / takip / paper / altili_canli / K52'ye DOKUNMAZ.
Sadece arsiv verisini (altili_olasilik.csv + altili_tam.csv) okur, konsola rapor basar.

IKI SORUYU AYNI VERIDE OLCER:
  (1) KAP BOYUTU: orta (96) ile daha genis kaplari (144/192/240/288/384) kiyasla.
      Uretim ayari sabit: kapsam=0.75, banker=0.70 (K52'nin en iyi OOS profili).
  (2) BUDAMA MANTIGI (K56): v1 = butce asilinca EN COK ATLI (sikisik) ayaktan kis (mevcut);
      v2 = FAVORISI EN BELIRGIN ayaktan kis, sikisik ayagi KORU. YURIBOYKA vakasinin hedefi.

SANSI AYIKLAMAK: Altili ROI'si tek bir 6/6'ya asiri bagli. O yuzden her satirda:
  - ROI (teselli ACIK = iyimser, ve teselli KAPALI = sadece 6/6 oder = durust zemin)
  - 6/6 sayisi, isabet orani
  - BOOTSTRAP %95 GA (olaylari yeniden ornekleyerek): GA sifiri iceriyorsa "fark sans olabilir".
  Iki kap arasindaki farkin GA'si sifiri iceriyorsa -> "genisletmek olculebilir kazanc VERMIYOR".

ODAK: OOS 2025-26 (gercek sinav donemi). Cikti yorumu en altta.
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
KAPSAM, BANKER = 0.75, 0.70          # uretim ayari (K52 en iyi OOS)
KAPLAR = [96, 144, 192, 240, 288, 384]
RNG = np.random.default_rng(20260724)
NBOOT = 4000


def _sec_baz(ayak_atlari, kapsam_esik, banker_esik):
    """Butce ONCESI secim: banker veya kumulatif kapsam. Doner sec (6 set)."""
    sec = []
    for atlar in ayak_atlari:
        if not atlar:
            sec.append(set()); continue
        a = sorted(atlar, key=lambda x: -x[1])
        if a[0][1] >= banker_esik:
            sec.append({a[0][0]}); continue
        kum, secilen = 0.0, []
        for no, p in a:
            secilen.append(no); kum += p
            if kum >= kapsam_esik:
                break
        sec.append(set(secilen))
    return sec


def kupon_kur(ayak_atlari, kapsam_esik, max_kombo, banker_esik, budama="v1"):
    """budama='v1': butce asilinca EN COK ATLI ayaktan en dusuk Bot2'yi at (MEVCUT davranis).
    budama='v2' : FAVORISI EN BELIRGIN (secili kumede top1-top2 farki en buyuk) ayaktan at;
                  sikisik (fark kucuk) ayagi korur. Tek atli/banker ayaga dokunmaz."""
    sec = _sec_baz(ayak_atlari, kapsam_esik, banker_esik)
    bot2 = [dict(a) for a in ayak_atlari]        # no -> bot2 (ayak bazli)
    while np.prod([len(s) for s in sec]) > max_kombo:
        adaylar = [j for j in range(6) if len(sec[j]) > 1]
        if not adaylar:
            break
        if budama == "v1":
            i = max(adaylar, key=lambda j: len(sec[j]))
        else:                                    # v2: en belirgin favorili ayak
            def belirginlik(j):
                sirali = sorted(sec[j], key=lambda no: -bot2[j].get(no, 0.0))
                p1 = bot2[j].get(sirali[0], 0.0)
                p2 = bot2[j].get(sirali[1], 0.0) if len(sirali) > 1 else 0.0
                return p1 - p2                    # buyukse = bir at one cikmis = budamaya guvenli
            i = max(adaylar, key=belirginlik)
        # o ayakta en dusuk Bot2'li secili ati at
        dus = min(sec[i], key=lambda no: bot2[i].get(no, 0.0))
        sec[i].discard(dus)
    return sec


def olay_sonuc(o, puan_map, puan_map_full, max_kombo, budama, birim=1.0):
    """Tek olay -> (maliyet, getiri_teselli, getiri_6uz, alti). None: puan/kazanan eksik."""
    legs = [int(o[f"leg{i+1}"]) for i in range(6)]
    ayak_atlari, kaz = [], []
    for rk in legs:
        atlar = puan_map.get(rk)
        if not atlar:
            return None
        ayak_atlari.append(atlar)
        w = [no for no, p, k in puan_map_full.get(rk, []) if k == 1]
        kaz.append(w[0] if w else None)
    if any(k is None for k in kaz):
        return None
    sec = kupon_kur(ayak_atlari, KAPSAM, max_kombo, BANKER, budama)
    nk = int(np.prod([len(s) for s in sec]))
    if nk == 0:
        return None
    maliyet = nk * birim
    tut = [kaz[i] in sec[i] for i in range(6)]
    g_tes = g_6 = 0.0
    alti = 0
    for n in (6, 5, 4, 3):                        # teselli ACIK
        if all(tut[6 - n:]):
            div = o.get(f"t{n}_div")
            if pd.notna(div):
                onceki = int(np.prod([len(sec[j]) for j in range(6 - n)])) if n < 6 else 1
                g_tes += onceki * birim * div
                if n == 6:
                    alti = 1
                break
    if all(tut):                                 # teselli KAPALI: sadece 6/6
        div = o.get("t6_div")
        if pd.notna(div):
            g_6 = birim * div
    return maliyet, g_tes, g_6, alti


def calis(kayitlar, puan_map, puan_map_full, max_kombo, budama):
    """Olay basina (maliyet, net_teselli, net_6uz) dizileri + ozet. Bootstrap icin olay-bazli."""
    mal, gt, g6, a6 = [], [], [], 0
    for o in kayitlar:
        r = olay_sonuc(o, puan_map, puan_map_full, max_kombo, budama)
        if r is None:
            continue
        m, t, s, al = r
        mal.append(m); gt.append(t); g6.append(s); a6 += al
    mal = np.array(mal); gt = np.array(gt); g6 = np.array(g6)
    return mal, gt, g6, a6


def boot_roi(mal, get):
    """Olaylari yeniden ornekleyip ROI dagilimindan %95 GA. ROI=(sum get-sum mal)/sum mal."""
    n = len(mal)
    if n == 0:
        return (float("nan"), float("nan"))
    idx = RNG.integers(0, n, size=(NBOOT, n))
    sm = mal[idx].sum(axis=1)
    sg = get[idx].sum(axis=1)
    roi = (sg - sm) / sm * 100
    return (np.percentile(roi, 2.5), np.percentile(roi, 97.5))


def main():
    puan = pd.read_csv(KOK / "veri" / "altili_olasilik.csv", low_memory=False)
    olay = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    olay["yil"] = pd.to_datetime(olay["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    olay = olay[~olay["sehir"].isin(EXCL)]
    puan_map, puan_map_full = {}, {}
    for rk, g in puan.groupby("race_kod"):
        puan_map[rk] = list(zip(g["no"], g["bot2"]))
        puan_map_full[rk] = list(zip(g["no"], g["bot2"], g["kazandi"]))
    oos = list(olay[olay.yil >= 2025].to_dict("records"))

    print("=" * 92)
    print("ALTILI KAP TESTI — 'orta'yi genisletmeli miyiz?'  (OFFLINE; canliya DOKUNMAZ)")
    print(f"OOS olay (2025-26, izinli pist): {len(oos)} | ayar: kapsam={KAPSAM} banker={BANKER}")
    print("ROI(tes)=teselli acik/iyimser · ROI(6)=sadece 6/6 oder/durust zemin · GA=bootstrap %95")
    print("=" * 92)

    for budama in ("v1", "v2"):
        etiket = "v1 (MEVCUT: sikisik ayaktan buda)" if budama == "v1" else "v2 (K56: favorili ayaktan buda, sikisigi KORU)"
        print(f"\n### BUDAMA {etiket} ###")
        print(f"{'kap':>5} {'olay':>5} {'ort.kombo':>9} {'maliyet':>9} "
              f"{'ROI(tes)%':>9} {'ROI(tes)GA':>16} {'ROI(6)%':>8} {'6/6':>4} {'isabet%':>7}")
        baz = None
        for mk in KAPLAR:
            mal, gt, g6, a6 = calis(oos, puan_map, puan_map_full, mk, budama)
            roi_t = (gt.sum() - mal.sum()) / mal.sum() * 100
            roi_6 = (g6.sum() - mal.sum()) / mal.sum() * 100
            ga = boot_roi(mal, gt)
            ok = 100 * a6 / len(mal) if len(mal) else 0
            ad = "orta" if mk == 96 else "genis"
            print(f"{mk:>5} {len(mal):>5} {mal.sum()/len(mal):>9.1f} {mal.sum():>9.0f} "
                  f"{roi_t:>+9.1f} [{ga[0]:>+6.1f},{ga[1]:>+6.1f}] {roi_6:>+8.1f} {a6:>4} {ok:>7.2f}  {ad}")
            if mk == 96:
                baz = (mal, gt)
        # orta(96) vs en genis(384): fark GA'si sifiri iceriyor mu? (esli bootstrap)
        malw, gtw, _, _ = calis(oos, puan_map, puan_map_full, 384, budama)
        _fark_ga(baz[0], baz[1], malw, gtw)

    print("\n" + "=" * 92)
    print("YORUM: fark-GA sifiri iceriyorsa 'genisletmek olculebilir kazanc vermiyor' demektir.")
    print("ROI(6) (durust zemin) tum kaplarda negatifse, artan kap sadece kaybi buyutur.")
    print("=" * 92)


def _fark_ga(mal0, get0, mal1, get1):
    """orta(96) ve genis(384) ROI farkinin %95 GA'si (ayni olaylar, esli yeniden ornekleme)."""
    n = min(len(mal0), len(mal1))
    if n == 0:
        return
    idx = RNG.integers(0, n, size=(NBOOT, n))
    r0 = (get0[idx].sum(1) - mal0[idx].sum(1)) / mal0[idx].sum(1) * 100
    r1 = (get1[idx].sum(1) - mal1[idx].sum(1)) / mal1[idx].sum(1) * 100
    d = r1 - r0
    lo, hi = np.percentile(d, 2.5), np.percentile(d, 97.5)
    icerir = "SIFIRI ICERIR -> fark sans" if lo <= 0 <= hi else "sifir DISINDA -> gercek fark"
    print(f"   -> genis(384) eksi orta(96) ROI farki: {np.median(d):+.1f} puan, "
          f"%95 GA [{lo:+.1f}, {hi:+.1f}]  ({icerir})")


if __name__ == "__main__":
    main()
