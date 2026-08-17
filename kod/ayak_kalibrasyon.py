"""
ayak_kalibrasyon.py — K106 / ÖLÇÜM A0: "config'ler birbirinden AYIRT EDILEBILIYOR MU?"
OFFLINE, SALT-OKUNUR: canliya/CSV'lere/config'e DOKUNMAZ, hicbir dosyaya yazmaz.

NEREDEN GELDI (dis analiz, 17 Agu 2026): canli sicilde 6 adet 6/6 var. Altili yalniz 6/6
odedigi icin kupon-duzeyinde bir config'i digerinden ayirmak bu orneklemle IMKANSIZ; 25 Eyl'de
de imkansiz olacak. Ama ayak duzeyinde ~2.850 gozlem duruyor ve kullanilmiyor.

ASIL SORU: "Bizim cetvelimiz, AYNI PARAYLA, kalabaligin cetvelinden daha iyi mi seciyor?"

--------------------------------------------------------------------------------------
BIRINCIL OLCUT — ESLESMIS ISABET (dis analizin onerdiginden FARKLI; gerekce asagida)
--------------------------------------------------------------------------------------
Her ayakta config k at yaziyor. AYNI ayakta, AYNI k ile, KAMU cetvelinin ilk k'si alinir.
Iki secim de kazanani tutuyor mu diye bakilir -> eslesmis (McNemar) kiyas.

  yalniz-sistem tuttu = a        yalniz-kamu tuttu = b
  tam binom isaret testi, iki yonlu, alpha=0,05

NEDEN KALIBRASYON ORANI DEGIL: dis analiz, ham kalibrasyon oraninin (gerceklesen/beklenen)
GURULTU-SECIM YANLILIGI tasidigini sentetik testle gosterdi -- gurultulu bir skorun tepesinden
secim yapinca secilen kumede o skor iyimser olur (kazananin laneti), R duser; dibinden secince
yukselir. Kasten en kotu ati secen kol R=1,30 ile "en umut verici" gorunuyordu. Onlarin cozumu
R'yi kamu-R'sine BOLMEKTI. Bu yanliligi azaltir ama tam gidermez (iki cetvelin gurultu yapisi
ayni degil) ve bot2 ile kamu %89,9 ortustugu icin GUCU dusuktur.
ESLESMIS ISABET bu sorunun TAMAMINDAN bagisiktir: olasilik degeri hic kullanilmaz, yalnizca
"kazanan secimin icinde miydi" sorulur. Kalibrasyon orani BETIMLEYICI olarak yine basilir
ama KARARA GIRMEZ.

--------------------------------------------------------------------------------------
METODOLOJI
--------------------------------------------------------------------------------------
* Olasiliklar `altili_kupon_ani.csv`'den (KUPON ANI, K97) -- `defter.csv`'den DEGIL.
  K97: iki siralama yalniz %30 ayni. Karar anini yaris ani verisiyle yargilamak, K97'de
  duzeltilen sizintinin aynisi olurdu.
* Her config KENDI dk grubunun fotografini kullanir (K105): orta_15 -> 15 dk, orta -> 30 dk.
* bot1 tabanli config'ler icin sistem cetveli bot1'dir (K99); kontrol yine KAMU'dur.
  Soru "bot1 kalabaliktan iyi mi", "bot1 bot2'den iyi mi" degil.
* Bootstrap birimi AYAK DEGIL ALTILI OLAYIDIR: ayni Altili'nin alti ayagi bagimsiz degildir
  (ayni gun/pist/zemin). Ayaklari tek tek orneklemek GA'yi yapay olarak daraltir.
* Beraberlik (ayni k'da hem sistem hem kamu ayni kumeyi seciyorsa) McNemar'da zaten
  sayilmaz -- bilgi tasimayan ayak karara girmez.

--------------------------------------------------------------------------------------
KARAR ESIKLERI (SONUC GORULMEDEN BAGLANDI)
--------------------------------------------------------------------------------------
  McNemar p < 0,05 ve yalniz-kamu > yalniz-sistem  -> config EMEKLI adayi
  McNemar p < 0,05 ve yalniz-sistem > yalniz-kamu  -> TEK ADAY, derinlestir
  p >= 0,05                                        -> "kenar kaniti yok" etiketi, sicilde kalir

GECERSIZLIK: bir config icin kupon-ani kaydi bulunan ayak orani %90'in altindaysa o config
icin olcum GECERSIZ sayilir (once veri butunlugu onarilir).

UYARI: ORAN veya isabet farkinin sistem lehine cikmasi POZITIF BEKLENEN DEGER DEMEK DEGILDIR.
Kesinti (%48,6) odeme asamasinda ayrica uygulanir. Bu olcum yalnizca SECIM KATMANINI test eder.

Elle: python ayak_kalibrasyon.py
"""
import sys
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_canli import KONFIG  # noqa: E402

NBOOT = 5000
RNG = np.random.default_rng(20260817)
KAPSAM_ESIGI = 0.90


def veri():
    k = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    k["sec"] = k.secim.apply(lambda s: frozenset(int(x) for x in str(s).split(",") if x.strip()))
    k = k[k.kazanan.notna()].copy()
    k["kazanan"] = k.kazanan.astype(int)
    a = pd.read_csv(KOK / "veri" / "altili_kupon_ani.csv", low_memory=False)
    if "dk_grup" not in a.columns:
        a["dk_grup"] = 30
    for c in ["seq", "ayak", "no", "bot1", "bot2", "kamu", "dk_grup"]:
        a[c] = pd.to_numeric(a[c], errors="coerce")
    a["dk_grup"] = a["dk_grup"].fillna(30)
    ani = {}
    for key, g in a.groupby(["tarih", "pist", "seq", "dk_grup", "ayak"]):
        ani[(str(key[0]), key[1], int(key[2]), float(key[3]), int(key[4]))] = g
    return k, ani


def topk(g, sutun, kk):
    """Verilen cetvele gore ilk k atin NO kumesi. Eksik/gecersiz -> None."""
    v = g.dropna(subset=[sutun])
    if len(v) < kk:
        return None
    return set(v.sort_values(sutun, ascending=False).head(kk).no.astype(int))


def mcnemar(a, b):
    n = a + b
    if n == 0:
        return 1.0
    p = 2 * sum(comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n
    return min(p, 1.0)


def main():
    k, ani = veri()
    print("=" * 116)
    print("OLCUM A0 — ESLESMIS ISABET: bizim cetvel, AYNI PARAYLA kalabaligin cetvelinden iyi mi?")
    print("  kontrol: ayni ayak, ayni k, KAMU cetvelinin ilk k'si")
    print("=" * 116)
    print(f"{'config':>15} {'ayak':>6} {'kapsam':>7} {'sistem':>7} {'kamu':>6} "
          f"{'yalniz-sis':>11} {'yalniz-kamu':>12} {'fark':>6} {'McNemar p':>10} {'karar':>22}")

    ozet = []
    for cfg in KONFIG:
        g = k[k.config == cfg]
        if g.empty:
            continue
        # sistem secimi ZATEN CSV'de (config kendi cetveliyle yapti) -> burada olasilik gerekmez;
        # yalnizca "kazanan secimin icinde miydi" sorulur. Olasilik betimleyici blokta kullanilir.
        dk = float(KONFIG[cfg].get("dk", 30))
        top = bul = 0
        h_sis = h_kam = 0
        a_only = b_only = 0
        olay = {}
        for _, r in g.iterrows():
            top += 1
            key = (str(r.tarih), r.pist, int(r.seq), dk, int(r.ayak))
            t = ani.get(key)
            if t is None:
                continue
            kk = len(r.sec)
            S = set(r.sec)
            K = topk(t, "kamu", kk)
            if K is None or not S:
                continue
            bul += 1
            hs = int(r.kazanan in S)
            hk = int(r.kazanan in K)
            h_sis += hs; h_kam += hk
            a_only += (hs and not hk)
            b_only += (hk and not hs)
            oi = (str(r.tarih), r.pist, int(r.seq))
            olay.setdefault(oi, []).append((hs, hk))
        if bul == 0:
            continue
        kaps = bul / top
        p = mcnemar(a_only, b_only)
        if kaps < KAPSAM_ESIGI:
            karar = "GECERSIZ (kapsam<%90)"
        elif p >= 0.05:
            karar = "kenar kaniti yok"
        elif a_only > b_only:
            karar = "TEK ADAY — derinlestir"
        else:
            karar = "EMEKLI ADAYI"
        print(f"{cfg:>15} {bul:>6} %{100*kaps:>5.0f} {h_sis:>7} {h_kam:>6} "
              f"{a_only:>11} {b_only:>12} {a_only-b_only:>+6} {p:>10.4f} {karar:>22}")
        ozet.append((cfg, olay, a_only, b_only, bul))

    print("\n" + "=" * 116)
    print("OLAY-BOOTSTRAP — ayak isabet FARKI (sistem - kamu), %95 GA")
    print("  birim AYAK DEGIL ALTILI: ayni Altili'nin ayaklari bagimsiz degil")
    print("=" * 116)
    print(f"{'config':>15} {'Altili':>7} {'sistem isabet':>14} {'kamu isabet':>12} "
          f"{'fark (puan)':>12} {'%95 GA':>18}")
    for cfg, olay, _, _, _ in ozet:
        ol = list(olay.values())
        if len(ol) < 5:
            continue
        idx = RNG.integers(0, len(ol), size=(NBOOT, len(ol)))
        farklar = np.empty(NBOOT)
        for b in range(NBOOT):
            s = kk_ = n = 0
            for j in idx[b]:
                for hs, hk in ol[j]:
                    s += hs; kk_ += hk; n += 1
            farklar[b] = (s - kk_) / n * 100 if n else 0.0
        s = sum(hs for v in ol for hs, _ in v)
        kk_ = sum(hk for v in ol for _, hk in v)
        n = sum(len(v) for v in ol)
        print(f"{cfg:>15} {len(ol):>7} %{100*s/n:>12.1f} %{100*kk_/n:>10.1f} "
              f"{100*(s-kk_)/n:>+11.1f} [{np.percentile(farklar,2.5):>+6.1f},"
              f"{np.percentile(farklar,97.5):>+6.1f}]")

    print("\n" + "=" * 116)
    print("BETIMLEYICI — kalibrasyon (KARARA GIRMEZ; gurultu-secim yanliligi tasir)")
    print("  R = gerceklesen isabet / modelin o secime verdigi olasilik toplami")
    print("=" * 116)
    print(f"{'config':>15} {'R_sistem':>9} {'R_kamu':>8} {'ORAN':>7}")
    for cfg in KONFIG:
        g = k[k.config == cfg]
        if g.empty:
            continue
        dk = float(KONFIG[cfg].get("dk", 30))
        sut = "bot1" if KONFIG[cfg].get("puan") == "bot1" else "bot2"
        hs = qs = hk = qk = 0.0
        for _, r in g.iterrows():
            t = ani.get((str(r.tarih), r.pist, int(r.seq), dk, int(r.ayak)))
            if t is None:
                continue
            kk = len(r.sec)
            S = set(r.sec)
            K = topk(t, "kamu", kk)
            if K is None or not S:
                continue
            v = t.dropna(subset=[sut, "kamu"])
            ps = v[v.no.astype(int).isin(S)][sut].sum()
            pk = v[v.no.astype(int).isin(K)]["kamu"].sum()
            hs += int(r.kazanan in S); qs += ps
            hk += int(r.kazanan in K); qk += pk
        if qs > 0 and qk > 0:
            Rs, Rk = hs / qs, hk / qk
            print(f"{cfg:>15} {Rs:>9.3f} {Rk:>8.3f} {Rs/Rk:>7.3f}")

    print("\n  UYARI: isabet farkinin sistem lehine cikmasi POZITIF BEKLENEN DEGER DEMEK DEGILDIR.")
    print("  Kesinti (%48,6) odeme asamasinda ayrica uygulanir; bu olcum yalniz SECIM katmanini test eder.")


if __name__ == "__main__":
    main()
