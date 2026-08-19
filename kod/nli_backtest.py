# -*- coding: utf-8 -*-
"""
nli_backtest.py — BEKLEYENLER #2: 4'LU / 5'LI KUPON KOLU (K108).
Salt offline. Canliya / paper'a / defter'e DOKUNMAZ, hicbir dosyaya YAZMAZ.

SORU (K84/K74/K75'ten devralinan hipotez):
  Ayak basina olculmus kenar (K74: AGF payi <%2 olan atlar havuzun dediginin 2,73 kati
  kazaniyor) Altili'da 6 ayagin CARPIMINDA yok oluyordu (K75: lambda=1'de 1318 kosuda SIFIR
  isabet). Hipotez: AYNI kenar DAHA KISA CARPIMDA daha az yikici birlesir.
  4'lu = 4 carpim · 5'li = 5 · Altili = 6.

TASARIM — ESLESMIS UCLU (bu kolun asil kazanimi):
  TJK'da 4'lu/5'li/6'li AYNI KOSUDA biter ve ayaklari IC ICEDIR: 6'linin son 5 ayagi = 5'li,
  son 4 ayagi = 4'lu. Arsivde bu 4.931 uclunun %100'unde dogrulandi.
  -> Ayni gun, ayni pist, ayni saha, ayni son kosu. Gun/pist/zorluk etkisi TAMAMEN elenir.
  Tek degisken: KAC AYAK tutturman gerektigi. Bu, hipotezin izole edilmis halidir.

AYNI PARA (kombo degil!):
  Resmi 2026 birim fiyatlari ESIT DEGIL (K86): 4'lu 1,75 · 5'li 1,50 · 6'li 1,25 TL.
  Kombo sayisini esitlemek 4'luye %40 fazla para harcatirdi. Bu yuzden BUTCE TL cinsinden
  esitlenir; her urunun kombo tavani butce/birim ile bulunur.
  Referans: Altili 900 kombo x 1,25 = 1.125 TL  ->  4'lu 642 kombo · 5'li 750 kombo.
  Ikinci butce: Altili 96 kombo x 1,25 = 120 TL  ->  4'lu 68 · 5'li 80.

ODEME: yalniz TAM isabet oder (4/4, 5/5, 6/6). Teselli YOK — 4'lu ve 5'li TJK'da AYRI
  bahislerdir, Altili'nin tesellisi degildir. Altili tarafi da kademeli=False ile alinir
  ki uc urun ayni kuralla yarissin.

============================================================================================
ON-KAYITLI OLCUTLER — BU BLOK SONUC GORULMEDEN YAZILDI (K33/K52 overfit yasagi)
============================================================================================
BEKLENTI (onceden yaziliyor): DUSUK. K94 kesintiyi olctu: 4'lu %45,6 · 5'li %46,8 ·
  6'li %48,6. Yani hicbir sey olmasa bile kisa urun 2-3 PUAN daha iyi cikacak — SIRF
  KESINTI UCUZ OLDUGU ICIN. Bu bir mekanizma bulgusu DEGILDIR ve kol acmaz.
  Ayrica K98-h ("tavan"): ayni parayla ayak genisletmek isabeti artirir ama temettuyu
  YARIYA dusurur (kalabaliga katilmak). Kisa urunde ayni para daha genis ayak alir
  (642^(1/4)=5,03 at/ayak vs 900^(1/6)=3,11) -> tavanin AYNISI beklenir.

S1 — MEKANIZMA VAR MI?  Birincil olcut.
  Olculen: eslesmis ROI farki  D4 = ROI(4'lu) - ROI(6'li)  ve  D5 = ROI(5'li) - ROI(6'li),
  ayni olayda, ayni parayla, ayni dagitici. Olay duzeyinde %95 bootstrap GA (birim = OLAY,
  ayak degil; ayni olayin ayaklari bagimsiz degildir).
  KESINTI TABANI: D4_taban = +3,0 puan · D5_taban = +1,8 puan (K94 farklari).
  >> MEKANIZMA VAR denir ANCAK VE ANCAK: GA'nin ALT SINIRI kesinti tabanindan BUYUKSE.
  >> Alt sinir tabanin altindaysa (veya GA tabani iceriyorsa): fark kesintiyle aciklanir,
     MEKANIZMA YOK, hipotez CURUR, BEKLEYENLER #2 KAPANIR.

S2 — OYNANABILIR MI?  Ikincil olcut; S1 gecse bile ayrica sorulur.
  >> OYNANABILIR denir ANCAK VE ANCAK: mutlak ROI >= 0 VE %95 GA alt siniri > -%5.
  >> Aksi halde: negatif ROI'li bir urun, digerinden iyi olsa da OYNANMAZ. Kullanicinin
     cercevesi "surdurulebilir yol" (K48); -%40, -%48'den iyi olmasi onu oynanabilir yapmaz.

S3 — TAVAN (K98-h) KISA URUNDE DE GECERLI MI?  Betimleyici, karar vermez.
  Isabet orani ve ortalama temettu ayri ayri basilir. Beklenen ornek: isabet ARTAR,
  temettu DUSER, net ~sifir. Ters cikarsa K98-h'nin sinirini gosterir -> yeni soru.

DOGRULAMA (calistirmadan once gecmeli):
  (a) N-ayak dagiticilar N=6'da altili_backtest.py'nin CIKTISINI BIREBIR uretmeli.
      Uretmezse mantik sessizce degismis demektir -> olcum GECERSIZ.
  (b) Boru hattinin kendisi K94'un bilinen cevabini vermeli: 2026 6'li ima edilen kesinti
      ~%48,6 civari cikmali. Cikmazsa temettu/birim okumasi yanlistir.
============================================================================================
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}

# K86'da TJK'dan alinan resmi 2026 birim fiyatlari (TL)
BIRIM = {3: 2.00, 4: 1.75, 5: 1.50, 6: 1.25, 7: 2.00}
# K94'te olculen kesintiler (%) — S1'in on-kayitli tabani bunlarin farkidir
KESINTI = {3: 45.4, 4: 45.6, 5: 46.8, 6: 48.6}
TABAN = {4: KESINTI[6] - KESINTI[4], 5: KESINTI[6] - KESINTI[5]}   # +3,0 · +1,8 puan

BANKER_ESIK = 0.70


# --------------------------------------------------------------------------------------
# N-AYAK DAGITICILAR — altili_backtest.py'nin 6-ayak mantiginin ayak sayisindan
# bagimsiz hali. Dogrulama (a): N=6'da orijinalle BIREBIR ayni cikti vermeli.
# --------------------------------------------------------------------------------------
def kupon_kur_n(ayak_atlari, kapsam_esik, max_kombo, banker_esik):
    """altili_backtest.kupon_kur'un N-ayak hali (K52 kapsam dagitici)."""
    n = len(ayak_atlari)
    sec = []
    for atlar in ayak_atlari:
        if not atlar:
            sec.append(set())
            continue
        atlar = sorted(atlar, key=lambda x: -x[1])
        if atlar[0][1] >= banker_esik:
            sec.append({atlar[0][0]})
            continue
        kum, secilen = 0.0, []
        for no, p in atlar:
            secilen.append(no)
            kum += p
            if kum >= kapsam_esik:
                break
        sec.append(set(secilen))
    while np.prod([len(s) for s in sec]) > max_kombo:
        i = max(range(n), key=lambda j: len(sec[j]))
        if len(sec[i]) <= 1:
            break
        atlar = sorted(ayak_atlari[i], key=lambda x: -x[1])
        for no, _ in reversed(atlar):
            if no in sec[i]:
                sec[i].discard(no)
                break
    return sec


def kupon_kur_acgozlu_n(ayak_atlari, max_kombo):
    """altili_backtest.kupon_kur_acgozlu'nun N-ayak hali (K65 log-uzayi sirt cantasi)."""
    n = len(ayak_atlari)
    sr = [sorted([(no, p) for no, p in a if pd.notna(p) and p > 0], key=lambda x: -x[1])
          for a in ayak_atlari]
    if any(len(s) == 0 for s in sr):
        return [set() for _ in range(n)]
    k = [1] * n
    P = [s[0][1] for s in sr]
    while True:
        kombo = int(np.prod(k))
        en_iyi, en_oran = None, 0.0
        for j in range(n):
            if k[j] >= len(sr[j]):
                continue
            if kombo // k[j] * (k[j] + 1) > max_kombo:
                continue
            p = sr[j][k[j]][1]
            bedel = math.log((k[j] + 1) / k[j])
            oran = (math.log1p(p / P[j]) / bedel) if (P[j] > 0 and bedel > 0) else 0.0
            if oran > en_oran:
                en_oran, en_iyi = oran, j
        if en_iyi is None:
            break
        j = en_iyi
        P[j] += sr[j][k[j]][1]
        k[j] += 1
    return [set(no for no, _ in sr[j][:k[j]]) for j in range(n)]


def dogrula_esdegerlik():
    """DOGRULAMA (a): N-ayak dagiticilar N=6'da orijinali birebir uretiyor mu?"""
    import altili_backtest as ab
    rng = np.random.default_rng(20260818)
    fark_kapsam = fark_acgozlu = 0
    for _ in range(4000):
        ayak = []
        for _ in range(6):
            m = int(rng.integers(4, 15))
            p = rng.dirichlet(np.ones(m) * float(rng.uniform(0.4, 3.0)))
            ayak.append(list(zip(range(1, m + 1), p)))
        for ke in (0.60, 0.75, 0.90):
            for mk in (24, 96, 900):
                if ab.kupon_kur(ayak, ke, mk, BANKER_ESIK) != kupon_kur_n(ayak, ke, mk, BANKER_ESIK):
                    fark_kapsam += 1
        for mk in (24, 96, 900):
            if ab.kupon_kur_acgozlu(ayak, mk) != kupon_kur_acgozlu_n(ayak, mk):
                fark_acgozlu += 1
    print(f"  kapsam  : 4000 rastgele kart x 9 ayar -> fark {fark_kapsam}")
    print(f"  acgozlu : 4000 rastgele kart x 3 ayar -> fark {fark_acgozlu}")
    ok = (fark_kapsam == 0 and fark_acgozlu == 0)
    print("  SONUC   :", "GECTI - N-ayak mantigi 6'da orijinalle AYNI" if ok
          else "!!! KALDI - mantik degismis, olcum GECERSIZ")
    return ok


# --------------------------------------------------------------------------------------
def veri_yukle():
    n = pd.read_csv(KOK / "veri" / "nli_ganyan.csv", low_memory=False)
    n["yil"] = pd.to_datetime(n.tarih, errors="coerce").dt.year
    n["ayaklar"] = n.race_kodlar.astype(str).str.split("/")
    n["son"] = n.ayaklar.str[-1]
    n["tl"] = pd.to_numeric(n.tl, errors="coerce")
    n = n[(~n.sehir.isin(EXCL)) & (n.tip == "odendi") & n.tl.notna() & (n.tl > 0)]

    p = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    p["race_kod"] = p.race_kod.astype(str)
    puan, kazanan = {}, {}
    for rk, g in p.groupby("race_kod"):
        puan[rk] = {
            "bot2": list(zip(g["no"], g["bot2"])),
            "bot1": list(zip(g["no"], g["bot1"])),
            "kamu": list(zip(g["no"], g["kamu"])),
        }
        w = g.loc[g.kazandi == 1, "no"].tolist()
        kazanan[rk] = w[0] if len(w) == 1 else None
    return n, puan, kazanan


def uclu_kur(n, puan, kazanan, yillar):
    """Eslesmis uclu listesi: her olay = {urun: (ayaklar, temettu)} + kazananlar."""
    a = n[n.urun.isin([4, 5, 6]) & n.yil.isin(yillar)]
    olaylar = []
    for _, gg in a.groupby(["tarih", "sehir", "son"]):
        if set(gg.urun) != {4, 5, 6}:
            continue
        d = {int(r.urun): (r.ayaklar, float(r.tl)) for r in gg.itertuples()}
        if d[6][0][-5:] != d[5][0] or d[6][0][-4:] != d[4][0]:
            continue
        ayak6 = d[6][0]
        if not all(rk in puan and kazanan.get(rk) is not None for rk in ayak6):
            continue
        olaylar.append({"tarih": gg.tarih.iloc[0], "sehir": gg.sehir.iloc[0],
                        "urun": d, "kaz": {rk: kazanan[rk] for rk in ayak6}})
    return olaylar


def oyna(olay, urun, butce_tl, dagitici, puan, skor="bot2"):
    """Tek olayda tek urunu oyna. Doner (maliyet, getiri, tam_isabet, kombo)."""
    ayaklar, temettu = olay["urun"][urun]
    birim = BIRIM[urun]
    max_kombo = int(butce_tl // birim)
    if max_kombo < 1:
        return None
    ayak_atlari = [puan[rk][skor] for rk in ayaklar]
    if any(len(a) == 0 for a in ayak_atlari):
        return None
    if dagitici == "acgozlu":
        sec = kupon_kur_acgozlu_n(ayak_atlari, max_kombo)
    else:
        sec = kupon_kur_n(ayak_atlari, 0.95, max_kombo, BANKER_ESIK)
    nk = int(np.prod([len(s) for s in sec]))
    if nk == 0:
        return None
    maliyet = nk * birim
    tuttu = all(olay["kaz"][rk] in sec[i] for i, rk in enumerate(ayaklar))
    getiri = temettu if tuttu else 0.0        # temettu = 1 birim kupon basina TL
    return maliyet, getiri, int(tuttu), nk


def bootstrap_fark(kayit_a, kayit_b, yineleme=4000, tohum=7):
    """Olay duzeyinde eslesmis ROI farki (a - b), %95 GA. kayit = [(mal, get), ...]"""
    rng = np.random.default_rng(tohum)
    a = np.array(kayit_a, dtype=float)
    b = np.array(kayit_b, dtype=float)
    m = len(a)

    def roi(x):
        return (x[:, 1].sum() - x[:, 0].sum()) / x[:, 0].sum() * 100 if x[:, 0].sum() else np.nan

    gozlenen = roi(a) - roi(b)
    orn = np.empty(yineleme)
    for i in range(yineleme):
        idx = rng.integers(0, m, m)
        orn[i] = roi(a[idx]) - roi(b[idx])
    return gozlenen, float(np.percentile(orn, 2.5)), float(np.percentile(orn, 97.5))


def kesinti_kontrol(n, puan, kazanan, yillar):
    """DOGRULAMA (b): boru hatti K94'un BILINEN cevabini uretiyor mu?

    Iliski: havuz, yatirilan paranin (1-t) kadarini oder. Kazanan komboya yatirilan para
    orani f ise  (temettu/birim) * f = (1-t).  Kalabalik olasiliginca oynuyorsa f ~ P_kamu.
    -> ort[(temettu/birim) * P_kamu(kazanan kombo)] ~ (1 - t).
    K94'un olctugu 2026 kesintileri: 3'lu %45,4 · 4'lu %45,6 · 5'li %46,8 · 6'li %48,6.
    Buradan cikan iade ~0,51-0,55 bandinda olmali. CIKMAZSA temettu/birim okumasi yanlistir
    ve ROI sayilarinin tamami gecersizdir."""
    print(f"  {'urun':>6} {'n':>7} {'birim':>6} {'medyan temettu':>15} {'ima edilen iade':>16} "
          f"{'ima edilen kesinti':>19} {'K94':>7}")
    for u in (3, 4, 5, 6):
        g = n[(n.urun == u) & n.yil.isin(yillar)]
        iadeler = []
        for r in g.itertuples():
            if not all(rk in puan and kazanan.get(rk) is not None for rk in r.ayaklar):
                continue
            P = 1.0
            for rk in r.ayaklar:
                d = dict(puan[rk]["kamu"])
                p = d.get(kazanan[rk])
                if p is None or not (p > 0):
                    P = None
                    break
                P *= float(p)
            if P:
                iadeler.append(r.tl / BIRIM[u] * P)
        if not iadeler:
            continue
        iade = float(np.median(iadeler))          # medyan: temettu dagilimi asiri carpik
        print(f"  {u:>6} {len(iadeler):>7} {BIRIM[u]:>6.2f} {g.tl.median():>15,.2f} "
              f"{iade:>16.3f} {100*(1-iade):>18.1f}% {KESINTI[u]:>6.1f}%")
    print("  NOT: medyan kullanildi (temettu dagilimi asiri carpik; ortalama tek bir devasa")
    print("  odemeyle savrulur). K94 ile ayni bandda cikiyorsa okuma DOGRU.")


def main():
    # K110: turetilmis veri bayatsa SESSIZ KALMASIN (19 Agu dersi: yigin 20-41 gun
    # eskiydi, Agustos kosularinin sifiri olasilik dosyasindaydi ve hicbir uyari yoktu).
    # Import main() ICINDE: canli yol bu modulu asla yuklemesin.
    try:
        from tazelik import uyar
        uyar("nli_ganyan.csv", "altili_olasilik_bot1.csv")
    except Exception:                                            # noqa: BLE001
        pass
    print("=" * 108)
    print("K108 — 4'LU / 5'LI KUPON KOLU (BEKLEYENLER #2). Salt offline, hicbir dosyaya yazmaz.")
    print("=" * 108)

    print("\n[DOGRULAMA a] N-ayak dagiticilar N=6'da orijinali uretiyor mu?")
    if not dogrula_esdegerlik():
        print("\nOLCUM DURDURULDU: dagitici esdegerligi saglanmadi.")
        return

    n, puan, kazanan = veri_yukle()

    for etiket, yillar in [("OOS 2025-26 (birincil)", (2025, 2026)),
                           ("2026 (fiyat-guvenli alt kume)", (2026,))]:
        olaylar = uclu_kur(n, puan, kazanan, yillar)
        print("\n" + "#" * 108)
        print(f"# {etiket} — eslesmis uclu: {len(olaylar):,}")
        print("#" * 108)
        if len(olaylar) < 30:
            print("  orneklem cok kucuk, atlaniyor.")
            continue

        print("\n[DOGRULAMA b] temettu/birim tanima tablosu")
        kesinti_kontrol(n, puan, kazanan, yillar)

        for butce_kombo in (900, 96):
            butce_tl = butce_kombo * BIRIM[6]
            for dagitici in ("acgozlu", "kapsam"):
                print("\n" + "-" * 108)
                print(f"BUTCE {butce_tl:,.0f} TL (Altili {butce_kombo} kombo esdegeri) "
                      f"| dagitici: {dagitici} | puan: bot2 | yalniz TAM isabet oder")
                print("-" * 108)
                kayit = {4: [], 5: [], 6: []}
                ozet = {}
                for o in olaylar:
                    r = {u: oyna(o, u, butce_tl, dagitici, puan) for u in (4, 5, 6)}
                    if any(v is None for v in r.values()):
                        continue
                    for u in (4, 5, 6):
                        kayit[u].append((r[u][0], r[u][1]))
                    for u in (4, 5, 6):
                        d = ozet.setdefault(u, {"n": 0, "mal": 0.0, "get": 0.0,
                                                "tut": 0, "kombo": 0, "odeme": []})
                        d["n"] += 1; d["mal"] += r[u][0]; d["get"] += r[u][1]
                        d["tut"] += r[u][2]; d["kombo"] += r[u][3]
                        if r[u][2]:
                            d["odeme"].append(r[u][1])
                if not ozet or ozet[6]["n"] < 30:
                    print("  eslesmis olay yetersiz.")
                    continue
                print(f"  {'urun':>6} {'olay':>6} {'ort.kombo':>10} {'at/ayak':>8} {'maliyet':>11} "
                      f"{'getiri':>11} {'ROI%':>8} {'tam isabet':>11} {'ort.odeme':>11}")
                for u in (4, 5, 6):
                    d = ozet[u]
                    roi = (d["get"] - d["mal"]) / d["mal"] * 100
                    ok = d["kombo"] / d["n"]
                    print(f"  {u:>6} {d['n']:>6} {ok:>10.1f} {ok ** (1 / u):>8.2f} "
                          f"{d['mal']:>11,.0f} {d['get']:>11,.0f} {roi:>+8.1f} "
                          f"{d['tut']:>4} (%{100*d['tut']/d['n']:>4.1f}) "
                          f"{np.mean(d['odeme']) if d['odeme'] else 0:>11,.0f}")
                print()
                for u in (4, 5):
                    g, lo, hi = bootstrap_fark(kayit[u], kayit[6])
                    tb = TABAN[u]
                    if lo > tb:
                        karar = f"MEKANIZMA VAR (GA alt siniri {lo:+.1f} > taban {tb:+.1f})"
                    else:
                        karar = f"mekanizma yok (GA tabani {tb:+.1f} disliyor degil)"
                    print(f"  S1  D{u} = ROI({u}'li) - ROI(6'li) = {g:+.1f} puan  "
                          f"%95 GA [{lo:+.1f}, {hi:+.1f}]  | kesinti tabani {tb:+.1f}  -> {karar}")
                for u in (4, 5, 6):
                    d = ozet[u]
                    roi = (d["get"] - d["mal"]) / d["mal"] * 100
                    if roi >= 0:
                        print(f"  S2  {u}'li mutlak ROI {roi:+.1f}% >= 0 -> GA'ya bakilmali")
                print(f"  S2  mutlak ROI'ler: " + " · ".join(
                    f"{u}'li {(ozet[u]['get']-ozet[u]['mal'])/ozet[u]['mal']*100:+.1f}%"
                    for u in (4, 5, 6)) + "  -> hicbiri >= 0 ise OYNANAMAZ")


if __name__ == "__main__":
    main()
