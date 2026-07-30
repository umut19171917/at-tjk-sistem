"""
altili_ayak_korelasyon_test.py — "ALTILI AYAKLARI BIRBIRIYLE ILISKILI MI?" (K70 adayi).
OFFLINE, SALT-OKUNUR: hicbir dosyaya yazmaz, canliya dokunmaz.

SORUYU DOGURAN FIKIR (kullanici, 2026-07-31): "Iyi Altili oyunculari birbirine ALTERNATIF
kuponlar yapar." Olcum: bizim kuponlarimiz alternatif degil, TAM IC ICE (dar C orta C genis
C genis900, 12/12 Altilida) -- satin alinan kombinasyonlarin %24,7'si tekrar.

AMA asil mesele su: tek kupon matematiksel olarak bir CARPIM'dir (ayak1 x ayak2 x ... x ayak6).
Carpimla ifade EDILEMEYEN sey KOSULLU yapidir: "1. ayagi favori kazanirsa 3. ayakta dar git,
surpriz kazanirsa 3. ayakta genis git". Bunu ancak BIRDEN COK kuponla yazarsin.
  -> Ve bu ancak AYAKLAR BIRBIRIYLE ILISKILIYSE bir sey kazandirir.
Modelimiz su an ayaklari BAGIMSIZ variyor (ayak olasiliklarini carpiyoruz). Eger surprizler
kumeleniyorsa (pist bozulmasi, hava, o gun formda olmayan favoriler) bu varsayim YANLIS'tir
ve kosullu kupon gercek bilgi tasir. Kumelenme yoksa alternatif kupon yalnizca OYNAKLIK
duzenlemesidir -- para getirmez.

YONTEM (iki tanim, ayni sonuca bakiyoruz):
  (a) IKILI surpriz  : kazanan, KAMU FAVORISI degil mi?
  (b) SUREKLI surpriz: -ln(kazananin kamu olasiligi)  ("bilgi kurami" anlaminda saskinlik)
  NULL (bagimsizlik): ayaklar Altililara RASTGELE yeniden dagitilir (marjinaller korunur,
  yalnizca "ayni Altiliya ait olma" bagi kirilir). Gozlenen kumelenme null dagilimin disinda
  mi? -> permutasyon testi, 20.000 tur.
  Ek olarak: P(sonraki ayakta surpriz | 1. ayakta surpriz) vs kosulsuz oran.

NOT: Ayni Altilinin 6 ayagi AYNI GUN ve AYNI PISTTE kosulur. Bulunacak herhangi bir kumelenme
zaten "gun/pist etkisi"dir -- aradigimiz sey de tam olarak budur (pist/hava ortak faktoru).
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
EXCL_SEHIR = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
RNG = np.random.default_rng(20260731)
NPERM = 20000


def veri_yukle(sadece_oos=False):
    p = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    olay = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    olay["dt"] = pd.to_datetime(olay["tarih"], format="%d/%m/%Y", errors="coerce")
    olay = olay[~olay["sehir"].isin(EXCL_SEHIR)]
    if sadece_oos:
        olay = olay[olay.dt.dt.year >= 2025]

    # her kosu icin: kazanan kamu-favorisi mi + kazananin kamu olasiligi
    bilgi = {}
    for rk, g in p.groupby("race_kod"):
        km = pd.to_numeric(g["kamu"], errors="coerce")
        kz = pd.to_numeric(g["kazandi"], errors="coerce")
        if km.notna().sum() < 2 or (kz == 1).sum() != 1:
            continue
        i = kz.idxmax()
        pk = float(km.get(i, np.nan))
        if not np.isfinite(pk) or pk <= 0:
            continue
        fav_i = km.idxmax()
        bilgi[int(rk)] = {"surpriz": int(i != fav_i),
                          "p_fav": float(km.max()),
                          "saskinlik": float(-np.log(pk))}

    ikili, surekli, meta = [], [], []
    for o in olay.to_dict("records"):
        legs = [int(o[f"leg{i+1}"]) for i in range(6)]
        if any(l not in bilgi for l in legs):
            continue
        ikili.append([bilgi[l]["surpriz"] for l in legs])
        surekli.append([bilgi[l]["saskinlik"] for l in legs])
        meta.append((o["tarih"], o["sehir"]))
    return np.array(ikili), np.array(surekli), meta


def permutasyon(mat, olcu):
    """mat: (olay x 6). Ayaklari olaylar arasinda RASTGELE yeniden dagit -> null dagilim."""
    duz = mat.reshape(-1)
    n = mat.shape[0]
    gozlem = olcu(mat)
    null = np.empty(NPERM)
    for t in range(NPERM):
        k = RNG.permutation(duz)[: n * 6].reshape(n, 6)
        null[t] = olcu(k)
    p_sag = (null >= gozlem).mean()
    return gozlem, null.mean(), np.percentile(null, [2.5, 97.5]), p_sag


def main():
    for etiket, oos in (("TUM ARSIV", False), ("SADECE OOS (2025-26)", True)):
        ik, su, meta = veri_yukle(oos)
        if len(ik) < 30:
            print(f"\n{etiket}: yeterli olay yok ({len(ik)})")
            continue
        print("\n" + "=" * 96)
        print(f"{etiket} — {len(ik)} Altili olayi ({len(ik)*6} ayak)")
        print("=" * 96)

        sayim = ik.sum(axis=1)
        print(f"Ayak basina surpriz orani (kazanan kamu favorisi DEGIL): "
              f"%{100*ik.mean():.1f}")
        print(f"Altili basina surpriz sayisi: ort {sayim.mean():.2f}, "
              f"VARYANS {sayim.var():.3f}")
        print("  dagilim (0..6 surpriz):",
              " ".join(f"{k}:{(sayim == k).sum()}" for k in range(7)))

        # (a) IKILI — kumelenme = sayim varyansinin sismesi
        g, nm, ga, ps = permutasyon(ik, lambda m: m.sum(axis=1).var())
        print(f"\n(a) IKILI surpriz — Altili ici KUMELENME testi (varyans)")
        print(f"    gozlenen varyans = {g:.4f}")
        print(f"    bagimsizlik null = {nm:.4f}   %95 arali [{ga[0]:.4f}, {ga[1]:.4f}]")
        print(f"    p (tek yonlu, kumelenme lehine) = {ps:.4f}"
              f"   -> {'KUMELENME VAR' if ps < 0.05 else 'kumelenme YOK (bagimsizlikla uyumlu)'}")

        # (b) SUREKLI — ayni olay icindeki ortalama ikili korelasyon
        def ort_ikili_kor(m):
            mm = m - m.mean()
            # olay ici capraz carpim ortalamasi / genel varyans  ~ sinif ici korelasyon
            n_, k_ = mm.shape
            top = (mm.sum(axis=1) ** 2 - (mm ** 2).sum(axis=1)).sum()
            return top / (n_ * k_ * (k_ - 1) * mm.var())

        g2, nm2, ga2, ps2 = permutasyon(su, ort_ikili_kor)
        print(f"\n(b) SUREKLI saskinlik — Altili ici ortalama ikili KORELASYON")
        print(f"    gozlenen r = {g2:+.4f}")
        print(f"    bagimsizlik null = {nm2:+.4f}   %95 arali [{ga2[0]:+.4f}, {ga2[1]:+.4f}]")
        print(f"    p = {ps2:.4f}"
              f"   -> {'ILISKI VAR' if ps2 < 0.05 else 'iliski YOK'}")

        # (c) kosullu oran: 1. ayak surprizse sonrakiler?
        m1 = ik[:, 0] == 1
        if m1.sum() > 10:
            son_k = ik[m1, 1:].mean()
            son_y = ik[~m1, 1:].mean()
            print(f"\n(c) 1. ayakta SURPRIZ olduysa sonraki 5 ayagin surpriz orani: %{100*son_k:.1f}")
            print(f"    1. ayakta surpriz OLMADIYSA                              : %{100*son_y:.1f}")
            print(f"    fark: {100*(son_k-son_y):+.1f} puan")

    print("\n" + "=" * 96)
    print("YORUM: Kumelenme YOKSA -> ayaklar bagimsiz; kosullu/alternatif kupon EK BILGI tasimaz,")
    print("yalnizca oynaklik duzenler (ayni -EV). Kumelenme VARSA -> carpim varsayimi eksik ve")
    print("kosullu kupon yapisi gercek bir kazanim olabilir; ayrica backtest ile sinanmali.")
    print("=" * 96)


if __name__ == "__main__":
    main()
