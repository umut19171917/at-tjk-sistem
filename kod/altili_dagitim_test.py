"""
altili_dagitim_test.py — "BUTCEYI AYAKLARA NASIL DAGITMALI?" backtesti (K65 adayi).
OFFLINE, SALT-OKUNUR: canli sisteme / takip / paper / altili_canli'ya DOKUNMAZ.
Sadece arsiv verisini (altili_olasilik.csv + altili_tam.csv) okur, konsola rapor basar.

SORU (kullanici gozlemi, 2026-07-26): Altili kuponlari normalde "en guvendigin ayakta TEK at,
guvenmedigin ayakta GENIS" mantigiyla kurulur. Bizim kuponlarimizda her ayakta asagi yukari
ayni sayida at cikiyor (canli olcum: orta'da ayaklarin %74'u tam 2 at; genis900'de HIC 2 atli
ayak yok). Oysa gercek talep cok degisken: %75 kapsam icin gereken at sayisi 1 ile 9 arasi
(ort 4,2). Yani duzlestirmeyi BIZ yapiyoruz. Sebep uc katmanli:
  (1) banker esigi 0.70 pratikte ulasilamaz (78 ayagin sadece 3'u gecti),
  (2) kapsam esigi her ayakta AYNI (%75/%95) -> esit kapsam = esitleyici,
  (3) budayici HER ZAMAN en kalabalik ayaktan keser -> aktif duzlestirici (asil suclu).

UC DAGITICI AYNI VERIDE KIYASLANIYOR:
  v1       : MEVCUT CANLI davranis. Duz kapsam esigi + butce asilinca en kalabalik ayaktan kes.
  v2       : K56/K57'de test edilip REDDEDILEN. Favorisi belirgin ayaktan kes, sikisigi koru.
             (Kayit icin duruyor; sadece budamayi degistirir, dagitimi degil.)
  acgozlu  : YENI. Duz kapsam esigi YOK, budayici YOK. Her ayakta 1 atla basla; sonra
             "eklendiginde 6/6 olasiligini en cok, maliyeti en az artiran" ati tekrar tekrar
             ekle, butce dolana dek. Matematigi: max PI(P_i) s.t. PI(n_i)<=C  ->  loglarda
             acgozlu sirt cantasi; kazanc=log(1+p_yeni/P_i), bedel=log((k+1)/k), oran=kazanc/bedel.
             Bu KENDILIGINDEN kaos ayagina cok at, net ayaga tek at koyar (kural yazmadan).

NEDEN "6/6 SAYISI" DEGIL "TL" OLCUYORUZ (kritik):
  En guvendigin ayaga tek at koymak = genelde kamu favorisine tek at = EN KALABALIK havuz.
  Isabet artar ama temettu duser. Buyuk odemeler kalabaligin yanildigi ayaklardan gelir.
  Yani isabet ve kazanc TERS ceker. O yuzden asil karar olcutu ROI(6) = durust zemin (TL).

SEKIL TESHISI de basiliyor (ort ayak genisligi, en dar/en genis, tek-atli ayak orani):
  acgozlu gercekten tekduzeligi kiriyor mu, once ONU dogrulamak icin.

ODAK: OOS 2025-26 (gercek sinav donemi). Butceler = canli konfiglerimiz (24/96/288/900).
"""
import math
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
KAPSAM, BANKER = 0.75, 0.70          # uretim ayari (v1/v2 icin; acgozlu bunlari KULLANMAZ)
BUTCELER = [(24, "dar"), (96, "orta"), (288, "genis"), (900, "genis900")]
RNG = np.random.default_rng(20260726)
NBOOT = 4000


# ---------------------------------------------------------------- dagiticilar
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


def kur_v1v2(ayak_atlari, max_kombo, budama="v1"):
    """MEVCUT aile: duz kapsam esigi + butce budamasi. budama='v1' en kalabalik ayaktan,
    'v2' favorisi en belirgin ayaktan keser."""
    sec = _sec_baz(ayak_atlari, KAPSAM, BANKER)
    bot2 = [dict(a) for a in ayak_atlari]
    while np.prod([len(s) for s in sec]) > max_kombo:
        adaylar = [j for j in range(6) if len(sec[j]) > 1]
        if not adaylar:
            break
        if budama == "v1":
            i = max(adaylar, key=lambda j: len(sec[j]))
        else:
            def belirginlik(j):
                sr = sorted(sec[j], key=lambda no: -bot2[j].get(no, 0.0))
                p1 = bot2[j].get(sr[0], 0.0)
                p2 = bot2[j].get(sr[1], 0.0) if len(sr) > 1 else 0.0
                return p1 - p2
            i = max(adaylar, key=belirginlik)
        dus = min(sec[i], key=lambda no: bot2[i].get(no, 0.0))
        sec[i].discard(dus)
    return sec


# acgozlu dagitici TEK KAYNAK: altili_backtest.kupon_kur_acgozlu (K65'te canliya da baglandi;
# burada kopyasi TUTULMAZ ki test ile canli birbirinden KAYMASIN).
from altili_backtest import kupon_kur_acgozlu as kur_acgozlu  # noqa: E402


DAGITICI = {
    "v1":      lambda aa, mk: kur_v1v2(aa, mk, "v1"),
    "v2":      lambda aa, mk: kur_v1v2(aa, mk, "v2"),
    "acgozlu": kur_acgozlu,
}


# ---------------------------------------------------------------- degerlendirme
def olay_sonuc(o, puan_map, puan_map_full, max_kombo, dagitici, birim=1.0):
    """Tek olay -> (maliyet, getiri_teselli, getiri_6uz, alti, genislikler). None: veri eksik."""
    legs = [int(o[f"leg{i+1}"]) for i in range(6)]
    ayak_atlari, kaz = [], []
    for rk in legs:
        atlar = puan_map.get(rk)
        if not atlar:
            return None
        ayak_atlari.append(atlar)
        w = [no for no, p, kz in puan_map_full.get(rk, []) if kz == 1]
        kaz.append(w[0] if w else None)
    if any(kz is None for kz in kaz):
        return None
    sec = DAGITICI[dagitici](ayak_atlari, max_kombo)
    gen = [len(s) for s in sec]
    nk = int(np.prod(gen))
    if nk == 0:
        return None
    maliyet = nk * birim
    tut = [kaz[i] in sec[i] for i in range(6)]
    g_tes = g_6 = 0.0
    alti = 0
    for n in (6, 5, 4, 3):                        # teselli ACIK (iyimser zemin)
        if all(tut[6 - n:]):
            div = o.get(f"t{n}_div")
            if pd.notna(div):
                onceki = int(np.prod([len(sec[j]) for j in range(6 - n)])) if n < 6 else 1
                g_tes += onceki * birim * div
                if n == 6:
                    alti = 1
                break
    if all(tut):                                  # teselli KAPALI (durust zemin): sadece 6/6
        div = o.get("t6_div")
        if pd.notna(div):
            g_6 = birim * div
    return maliyet, g_tes, g_6, alti, gen


def calis(kayitlar, puan_map, puan_map_full, max_kombo, dagitici):
    mal, gt, g6, a6, sekil = [], [], [], 0, []
    for o in kayitlar:
        r = olay_sonuc(o, puan_map, puan_map_full, max_kombo, dagitici)
        if r is None:
            continue
        m, t, s, al, gen = r
        mal.append(m); gt.append(t); g6.append(s); a6 += al; sekil.append(gen)
    return np.array(mal), np.array(gt), np.array(g6), a6, np.array(sekil)


def boot_roi(mal, get):
    n = len(mal)
    if n == 0:
        return (float("nan"), float("nan"))
    idx = RNG.integers(0, n, size=(NBOOT, n))
    roi = (get[idx].sum(1) - mal[idx].sum(1)) / mal[idx].sum(1) * 100
    return (np.percentile(roi, 2.5), np.percentile(roi, 97.5))


def fark_ga(mal0, get0, mal1, get1, ad0, ad1):
    """Iki dagiticinin ROI farkinin %95 GA'si (AYNI olaylar, esli yeniden ornekleme)."""
    n = min(len(mal0), len(mal1))
    if n == 0:
        return
    idx = RNG.integers(0, n, size=(NBOOT, n))
    r0 = (get0[idx].sum(1) - mal0[idx].sum(1)) / mal0[idx].sum(1) * 100
    r1 = (get1[idx].sum(1) - mal1[idx].sum(1)) / mal1[idx].sum(1) * 100
    d = r1 - r0
    lo, hi = np.percentile(d, 2.5), np.percentile(d, 97.5)
    yorum = "SIFIRI ICERIR -> fark sans" if lo <= 0 <= hi else "sifir DISINDA -> gercek fark"
    print(f"      {ad1} eksi {ad0}: {np.median(d):+.1f} puan, %95 GA [{lo:+.1f}, {hi:+.1f}]  ({yorum})")


def sekil_ozet(sekil):
    """Kupon SEKLI: tekduze mi, degil mi."""
    if len(sekil) == 0:
        return "-"
    ort = sekil.mean()
    dar = sekil.min(axis=1).mean()
    gen = sekil.max(axis=1).mean()
    tek = 100.0 * (sekil.min(axis=1) == 1).mean()      # tek-atli ayagi olan kupon %
    return f"{ort:>5.2f} {dar:>5.2f} {gen:>5.2f} {gen - dar:>6.2f} {tek:>7.1f}"


# ---------------------------------------------------------------- ana
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

    print("=" * 104)
    print("ALTILI DAGITIM TESTI — 'butceyi ayaklara nasil dagitmali?'  (OFFLINE; canliya DOKUNMAZ)")
    print(f"OOS olay (2025-26, izinli pist): {len(oos)} | v1/v2 ayari: kapsam={KAPSAM} banker={BANKER}")
    print("ROI(tes)=teselli acik/iyimser · ROI(6)=SADECE 6/6 oder = DURUST ZEMIN (asil olcut)")
    print("=" * 104)

    for mk, ad in BUTCELER:
        print(f"\n### BUTCE {mk} kombo  ({ad}) ###")
        print(f"{'dagitici':>9} {'olay':>5} {'ort.kombo':>9} {'ROI(tes)%':>9} {'ROI(tes)GA':>16} "
              f"{'ROI(6)%':>8} {'6/6':>4} {'isabet%':>7} | {'ayak':>5} {'endar':>5} {'engen':>5} "
              f"{'yayil':>6} {'tekat%':>7}")
        sakla = {}
        for dg in ("v1", "v2", "acgozlu"):
            mal, gt, g6, a6, sekil = calis(oos, puan_map, puan_map_full, mk, dg)
            if len(mal) == 0:
                continue
            roi_t = (gt.sum() - mal.sum()) / mal.sum() * 100
            roi_6 = (g6.sum() - mal.sum()) / mal.sum() * 100
            ga = boot_roi(mal, gt)
            ok = 100 * a6 / len(mal)
            print(f"{dg:>9} {len(mal):>5} {mal.sum()/len(mal):>9.1f} {roi_t:>+9.1f} "
                  f"[{ga[0]:>+6.1f},{ga[1]:>+6.1f}] {roi_6:>+8.1f} {a6:>4} {ok:>7.2f} | "
                  f"{sekil_ozet(sekil)}")
            sakla[dg] = (mal, gt, g6)
        if "v1" in sakla and "acgozlu" in sakla:
            print("   esli fark (teselli acik):")
            fark_ga(sakla["v1"][0], sakla["v1"][1], sakla["acgozlu"][0], sakla["acgozlu"][1],
                    "v1", "acgozlu")
            print("   esli fark (DURUST zemin, sadece 6/6):")
            fark_ga(sakla["v1"][0], sakla["v1"][2], sakla["acgozlu"][0], sakla["acgozlu"][2],
                    "v1", "acgozlu")

    print("\n" + "=" * 104)
    print("OKUMA KILAVUZU:")
    print(" · 'yayil' (en genis ayak - en dar ayak) ve 'tekat%' acgozlu'de v1'den YUKSEKSE,")
    print("   kullanicinin istedigi sekil (tek atli banker + genis kaos ayagi) GERCEKTEN olusmus demektir.")
    print(" · Sekil duzeldi ama ROI(6) duzelmediyse: dagitim degil, KESINTI (%25-31) baglayici kisit.")
    print(" · Esli fark GA'si sifiri iceriyorsa fark sanstir -> canliyi DEGISTIRME.")
    print(" · Isabet(6/6) artip ROI dustuyse: kalabalik havuza tek at koyma tuzagi dogrulanmis olur.")
    print("=" * 104)


if __name__ == "__main__":
    main()
