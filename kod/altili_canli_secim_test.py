"""
altili_canli_secim_test.py — K98'in TUM olcumlerini yeniden ureten tek betik.
OFFLINE, SALT-OKUNUR: canliya/paper'a/deftere DOKUNMAZ, hicbir dosyaya yazmaz.

NEDEN VAR: 9 Agu 2026'da kullanici "canliya iki kuponla cikmak istiyorum, bot1 + bir
alternatif; hangisi olurdu, secmeyeceksek nasil birlestiririz" diye sordu. Cikan sonuclar
K98'e yazildi. Sayilar yeniden uretilebilir olmasa karar denetlenemez -> bu betik odur.

BOLUMLER
  1  ADAYLAR       : bot1 disi 900'lukler tek basina (+ bot1 kiyas)
  2  ESLESMIS      : McNemar, ayak duzeyinde (ayrisma == acgozlu mu?)
  3  LAMBDA KONTROL: v2'nin arsivdeki kazanci NEREDEN geliyor? (gec / hepsi / erken)
  4  BUTCE         : 96 / 288 / 900 merdiveni, dort mekanizma
  5  PORTFOY       : bot1_900 + X (iki kupon ayri oynanir) + ayni parayi tek kupona verme kontrolu
  6  YOGUNLASMA    : en buyuk kuponlar cikarilinca ROI ne olur (bot1'in -18,3'u kac olaya dayaniyor)
  7  BIRLESTIRME   : uc bot2 kuponunu tek kupona indirmenin uc yolu
  8  COGALTMA      : N x orta@96 vs tek kupon; uc farkli bolme kurali (banker rotasyonu dahil)
  9  TAVAN         : dikdortgen KISITI OLMADAN en olasi N kombinasyon -- ust sinir

DURUST ZEMIN: yalniz 6/6 oder (K57/K65), teselli yok. Birim 1,25 TL. OOS = 2025-26,
izinli pistler (EXCL disarida). Guven araliklari OLAY duzeyinde bootstrap (n=3000).

ROI(-1) SUTUNU: getiriden EN BUYUK tek kupon cikarilinca kalan ROI. Canli oyuncu 1433 Altili
oynamaz; tek bir dev temettuye dayanan ROI onun yasayacagi sey degildir. Siralamayi bu sutun belirler.

UYARI — OVERFIT: buradaki lambda ve butce taramalari MEKANIZMA TESHISI icindir, parametre
secmek icin DEGIL. Backtest'e bakip lambda ya da butce secmek K33/K52'nin yasakladigi
hindsight'tir. K98'de taramanin en iyisi cikan lambda=0,50 ve @192 bilerek ALINMAMISTIR.

Elle: python altili_canli_secim_test.py            (hepsi)
      python altili_canli_secim_test.py --bolum 9  (tek bolum)
"""
import argparse
import heapq
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_backtest import (kupon_kur, kupon_kur_acgozlu,  # noqa: E402
                             kupon_kur_ayrisma, kupon_kur_kalibre, ayrisma_skoru)

EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
BIRIM = 1.25
NBOOT = 3000
RNG = np.random.default_rng(20260809)
KAPSAM, BANKER = 0.75, 0.70          # canlidaki dar/orta/genis ailesinin ayarlari
KAPSAM95 = 0.95                      # genis900'un ayari
# Altili yapisi: ilk ayaga ~30 dk kala kurulur, ayaklar ~30 dk arayla (v2'nin mesafe girdisi)
AYAK_DK = [30.0, 60.0, 90.0, 120.0, 150.0, 180.0]


# ----------------------------------------------------------------- veri
def veri():
    p = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    pm1, pm2, pmk, wmap, saha = {}, {}, {}, {}, {}
    for rk, g in p.groupby("race_kod"):
        pm2[rk] = sorted([(int(n), float(v)) for n, v in zip(g["no"], g["bot2"])
                          if pd.notna(v) and v > 0], key=lambda x: -x[1])
        pm1[rk] = sorted([(int(n), float(v)) for n, v in zip(g["no"], g["bot1"])
                          if pd.notna(v) and v > 0], key=lambda x: -x[1])
        # DIKKAT: ayrisma skoru bot1 ile kamu'yu ELEMAN ELEMAN kiyaslar; p1/p2 olasiliga gore
        # SIRALI tutuldugu icin onlardan hesaplanamaz (hiza kayar, skor bozulur). Bu yuzden
        # burada, DataFrame satirlari hizaliyken bir kez hesaplanip saklaniyor.
        pmk[rk] = ayrisma_skoru(pd.to_numeric(g["bot1"], errors="coerce").fillna(0.0).values,
                                pd.to_numeric(g["kamu"], errors="coerce").fillna(0.0).values)
        saha[rk] = len(g)
        w = g.loc[g["kazandi"] == 1, "no"]
        if len(w):
            wmap[rk] = int(w.iloc[0])
    o = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    o["yil"] = pd.to_datetime(o["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    o = o[~o["sehir"].isin(EXCL)]
    return {"p1": pm1, "p2": pm2, "ayr": pmk, "w": wmap, "saha": saha,
            "olay": list(o[o.yil >= 2025].to_dict("records"))}


def ayak_verisi(D, oo):
    """Bir olayin 6 ayagi. Doner (bot2, bot1, ayrisma_skorlari, kazananlar, saha) veya None."""
    a2, a1, ay, kaz, sh = [], [], [], [], []
    for i in range(6):
        rk = int(oo[f"leg{i+1}"])
        if rk not in D["p2"] or rk not in D["w"] or len(D["p2"][rk]) < 2:
            return None
        a2.append(D["p2"][rk]); a1.append(D["p1"][rk]); ay.append(D["ayr"][rk])
        kaz.append(D["w"][rk]); sh.append(D["saha"][rk])
    return a2, a1, ay, kaz, sh


# ----------------------------------------------------------------- dagiticilar
def duzlestir(atlar, lam):
    if lam == 1.0:
        return list(atlar)
    q = [(no, p ** lam) for no, p in atlar]
    s = sum(x for _, x in q)
    return [(no, x / s) for no, x in q] if s > 0 else []


def buda(sec, puanlar, maxk):
    """Butceyi asan secimi en dusuk olasilikli attan baslayarak kis (kupon_kur ile ayni mantik)."""
    sec = [set(s) for s in sec]
    pmap = [dict(a) for a in puanlar]
    while int(np.prod([len(s) for s in sec])) > maxk:
        j = max(range(6), key=lambda i: len(sec[i]))
        if len(sec[j]) <= 1:
            break
        sec[j].discard(min(sec[j], key=lambda n: pmap[j].get(n, 0.0)))
    return sec


def en_olasi_n(ayaklar, N):
    """Dikdortgen KISITI OLMADAN en olasi N kombinasyon (k-en-iyi, heap). TAVAN olcumu."""
    logp = [[math.log(v) for _, v in a] for a in ayaklar]
    bas = (0,) * 6
    yigin = [(-sum(l[0] for l in logp), bas)]
    gorulen, out = {bas}, []
    while yigin and len(out) < N:
        neg, ix = heapq.heappop(yigin)
        out.append(ix)
        for j in range(6):
            if ix[j] + 1 < len(logp[j]):
                y = list(ix); y[j] += 1; y = tuple(y)
                if y not in gorulen:
                    gorulen.add(y)
                    heapq.heappush(yigin, (-(-neg - logp[j][ix[j]] + logp[j][y[j]]), y))
    return {tuple(ayaklar[j][ix[j]][0] for j in range(6)) for ix in out}


def kuponlar(mod, a2, a1, ayr, maxk):
    """Doner: kupon listesi (her kupon 6 set). Cogu mod tek kupon dondurur.
    ayr = 6 elemanli ayrisma skoru listesi (veri() icinde hizali hesaplandi)."""
    if mod == "genis":                                   # kapsam 0,75 ailesi (dar/orta/genis)
        return [kupon_kur(a2, KAPSAM, maxk, BANKER)]
    if mod == "genis95":                                 # genis900'un ayari
        return [kupon_kur(a2, KAPSAM95, maxk, BANKER)]
    if mod == "acgozlu":
        return [kupon_kur_acgozlu(a2, maxk)]
    if mod == "bot1":
        return [kupon_kur_acgozlu(a1, maxk)]
    if mod == "ayrisma":
        return [kupon_kur_ayrisma(a2, ayr, maxk, 1.0)]
    if mod == "v2":
        return [kupon_kur_kalibre(a2, AYAK_DK, maxk)]
    if mod.startswith("lam_"):                           # lam_<gec|hepsi|erken>_<deger>
        _, nerede, dv = mod.split("_")
        lam = float(dv)
        hedef = {"hepsi": range(6), "gec": range(2, 6), "erken": range(0, 2)}[nerede]
        return [kupon_kur_acgozlu([duzlestir(a2[i], lam if i in hedef else 1.0)
                                   for i in range(6)], maxk)]
    if mod in ("birlesim_buda", "cogunluk"):
        parca = [kupon_kur(a2, KAPSAM95, maxk, BANKER), kupon_kur_acgozlu(a2, maxk),
                 kupon_kur_ayrisma(a2, ayr, maxk, 1.0)]
        if mod == "birlesim_buda":
            return [buda([set().union(*(p[i] for p in parca)) for i in range(6)], a2, maxk)]
        out = []
        for i in range(6):
            say = {}
            for p in parca:
                for n in p[i]:
                    say[n] = say.get(n, 0) + 1
            s = {n for n, c in say.items() if c >= 2}
            out.append(s if s else set().union(*(p[i] for p in parca)))
        return [buda(out, a2, maxk)]
    if mod == "ortalama":
        yeni = []
        for x2, x1 in zip(a2, a1):
            m1 = dict(x1)
            v = [(no, 0.5 * p + 0.5 * m1.get(no, 0.0)) for no, p in x2]
            s = sum(q for _, q in v)
            yeni.append([(no, q / s) for no, q in v] if s > 0 else [])
        return [kupon_kur_acgozlu(yeni, maxk)]
    if mod.startswith("coklu"):                          # coklu<N> : N x orta, "sonraki atlar"
        adet = int(mod[5:])
        A = [set(s) for s in kupon_kur(a2, KAPSAM, maxk, BANKER)]
        ks, kullanilan = [A], {j: set(A[j]) for j in range(6)}
        bos = sorted(((1.0 - sum(v for n, v in a2[j] if n in A[j]), j) for j in range(6)),
                     reverse=True)
        for k in range(1, adet):
            j = bos[(k - 1) % 6][1]
            kalan = [n for n, _ in a2[j] if n not in kullanilan[j]]
            if not kalan:
                break
            B = [set(s) for s in A]; B[j] = set(kalan[:len(A[j])])
            kullanilan[j] |= B[j]
            ks.append(B)
        return ks
    if mod == "serpistir":                               # esit kalite bolme kontrolu
        A = [set(s) for s in kupon_kur(a2, KAPSAM, maxk, BANKER)]
        j = max(range(6), key=lambda z: 1.0 - sum(v for n, v in a2[z] if n in A[z]))
        havuz = [n for n, _ in a2[j]]
        k = len(A[j])
        tek, cift = havuz[0::2][:k], havuz[1::2][:k]
        if not tek or not cift:
            return [A]
        A2 = [set(s) for s in A]; A2[j] = set(tek)
        B = [set(s) for s in A]; B[j] = set(cift)
        return [A2, B]
    if mod == "rotasyon":                                # kullanicinin tarif ettigi banker rotasyonu
        out = []
        for erken_dar in (True, False):
            dar = range(0, 3) if erken_dar else range(3, 6)
            s = [set() for _ in range(6)]
            for i in dar:
                s[i] = {a2[i][0][0]}
            pay = max(1, int(round(maxk ** (1 / 3))))
            for i in (z for z in range(6) if z not in dar):
                s[i] = {n for n, _ in a2[i][:min(pay, len(a2[i]))]}
            out.append(buda(s, a2, maxk))
        return out
    raise ValueError(mod)


# ----------------------------------------------------------------- kosum & ozet
def calis(D, mod, maxk):
    rs = []
    for oi, oo in enumerate(D["olay"]):
        v = ayak_verisi(D, oo)
        if v is None:
            continue
        a2, a1, ayr, kaz, sh = v
        div = float(oo["t6_div"]) if pd.notna(oo.get("t6_div")) else 0.0
        if mod == "tavan":
            kume = en_olasi_n(a2, maxk)
            n_kombo, isabet, gen = len(kume), int(tuple(kaz) in kume), None
        else:
            ks = kuponlar(mod, a2, a1, ayr, maxk)
            if any(any(len(x) == 0 for x in k) for k in ks):
                continue
            n_kombo = sum(int(np.prod([len(x) for x in k])) for k in ks)
            isabet = sum(1 for k in ks if all(kaz[i] in k[i] for i in range(6)))
            # ayak isabeti / KAZANC yalniz TEK kuponlu modlar icin anlamli; cok kuponluda
            # ilk kuponunkini basmak yanilticidir -> None birak, tabloda "-" cikar.
            gen = [len(x) for x in ks[0]] if len(ks) == 1 else None
        rs.append({"oi": oi, "kombo": n_kombo, "isabet": isabet, "div": div,
                   "gen": gen, "saha": sh,
                   "tut": [kaz[i] in ks[0][i] for i in range(6)] if gen is not None else None})
    return rs


def ozet(rs, ad):
    mal = np.array([r["kombo"] * BIRIM for r in rs])
    get = np.array([r["div"] * r["isabet"] for r in rs])
    tut = np.array([int(r["isabet"] > 0) for r in rs])
    idx = RNG.integers(0, len(mal), size=(NBOOT, len(mal)))
    roi = (get[idx].sum(1) - mal[idx].sum(1)) / mal[idx].sum(1) * 100
    g1 = get.copy(); g1[np.argsort(-get)[:1]] = 0
    o = {"ad": ad, "n": len(rs), "kombo": mal.mean() / BIRIM, "bedel": mal.mean(),
         "tut": int(tut.sum()), "roi": (get.sum() - mal.sum()) / mal.sum() * 100,
         "roi1": (g1.sum() - mal.sum()) / mal.sum() * 100,
         "lo": np.percentile(roi, 2.5), "hi": np.percentile(roi, 97.5),
         "div": get[get > 0].mean() if (get > 0).any() else 0.0, "get": get, "mal": mal}
    if rs and rs[0]["gen"] is not None:
        ayak = sum(sum(r["tut"]) for r in rs) / (6 * len(rs))
        pay = np.mean([np.mean([g / s for g, s in zip(r["gen"], r["saha"])]) for r in rs])
        o["ayak"], o["kazanc"] = 100 * ayak, ayak / pay
    else:
        o["ayak"], o["kazanc"] = float("nan"), float("nan")
    return o


def basSATIR():
    print(f"{'kupon':>26} {'kombo':>6} {'bedel':>10} {'ayak':>6} {'KAZANC':>7} {'6/6':>5} "
          f"{'siklik':>7} {'ROI%':>7} {'ROI(-1)%':>9} {'%95 GA':>17} {'temettu':>9}")


def satir(s):
    ay = f"%{s['ayak']:>5.1f}" if s['ayak'] == s['ayak'] else "     -"
    kz = f"{s['kazanc']:>7.2f}" if s['kazanc'] == s['kazanc'] else "      -"
    print(f"{s['ad']:>26} {s['kombo']:>6.0f} {s['bedel']:>7,.0f} TL {ay} {kz} {s['tut']:>5} "
          f"%{100*s['tut']/s['n']:>6.1f} {s['roi']:>+7.1f} {s['roi1']:>+9.1f} "
          f"[{s['lo']:>+6.1f},{s['hi']:>+6.1f}] {s['div']:>9,.0f}")


def mcnemar(A, B):
    ha = {(r["oi"], i): r["tut"][i] for r in A for i in range(6)}
    hb = {(r["oi"], i): r["tut"][i] for r in B for i in range(6)}
    ortak = set(ha) & set(hb)
    x = sum(1 for k in ortak if ha[k] and not hb[k])
    y = sum(1 for k in ortak if hb[k] and not ha[k])
    n = x + y
    p = 2 * sum(math.comb(n, i) for i in range(min(x, y) + 1)) / 2 ** n if n else 1.0
    return x, y, min(p, 1.0), len(ortak)


def portfoy(A, B, ad):
    da = {r["oi"]: r for r in A}; db = {r["oi"]: r for r in B}
    ort = sorted(set(da) & set(db))
    mal = np.array([(da[i]["kombo"] + db[i]["kombo"]) * BIRIM for i in ort])
    get = np.array([da[i]["div"] * (da[i]["isabet"] + db[i]["isabet"]) for i in ort])
    enaz1 = sum(1 for i in ort if da[i]["isabet"] or db[i]["isabet"])
    idx = RNG.integers(0, len(mal), size=(NBOOT, len(mal)))
    roi = (get[idx].sum(1) - mal[idx].sum(1)) / mal[idx].sum(1) * 100
    g1 = get.copy(); g1[np.argsort(-get)[:1]] = 0
    return {"ad": ad, "n": len(ort), "kombo": mal.mean() / BIRIM, "bedel": mal.mean(),
            "tut": enaz1, "roi": (get.sum() - mal.sum()) / mal.sum() * 100,
            "roi1": (g1.sum() - mal.sum()) / mal.sum() * 100,
            "lo": np.percentile(roi, 2.5), "hi": np.percentile(roi, 97.5),
            "div": get[get > 0].mean() if (get > 0).any() else 0.0,
            "ayak": float("nan"), "kazanc": float("nan")}


# ----------------------------------------------------------------- bolumler
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bolum", type=int, default=0, help="0 = hepsi")
    args = ap.parse_args()
    B = args.bolum
    D = veri()
    print(f"OOS olay (2025-26, izinli pistler): {len(D['olay'])}")
    print("ROI(-1) = getiriden EN BUYUK tek kupon cikarilinca kalan ROI (siralamayi bu belirler)\n")
    R = {}

    if B in (0, 1):
        print("=" * 128)
        print("1) ADAYLAR — bot1 disi 900'lukler tek basina")
        print("=" * 128)
        basSATIR()
        for mod, ad in [("genis95", "genis900"), ("acgozlu", "acgozlu900"),
                        ("ayrisma", "ayrisma900"), ("v2", "acgozlu_v2"), ("bot1", "bot1_900")]:
            R[ad] = calis(D, mod, 900)
            satir(ozet(R[ad], ad))

    if B in (0, 2):
        print("\n" + "=" * 128)
        print("2) ESLESMIS AYAK KIYASI (McNemar) — ayrisma gercekten ayri bir kupon mu?")
        print("=" * 128)
        for a in ("genis900", "acgozlu900", "ayrisma900", "acgozlu_v2"):
            R.setdefault(a, calis(D, {"genis900": "genis95", "acgozlu900": "acgozlu",
                                      "ayrisma900": "ayrisma", "acgozlu_v2": "v2"}[a], 900))
        cift = [("acgozlu900", "ayrisma900"), ("acgozlu900", "acgozlu_v2"),
                ("genis900", "acgozlu900"), ("genis900", "acgozlu_v2")]
        for a, b in cift:
            x, y, p, n = mcnemar(R[a], R[b])
            print(f"  {a:>12} vs {b:<12} yalniz-sol {x:>4}, yalniz-sag {y:>4}, p={p:.4f}  ({n} ayak)")
        print("  p>0,05 => AYIRT EDILEMEZ (ayrisma900 icin beklenen budur, K95).")

    if B in (0, 3):
        print("\n" + "=" * 128)
        print("3) LAMBDA KONTROLU — v2'nin arsivdeki kazanci nereden geliyor? (@900)")
        print("   A: 'gec ayaklara genislik'  B: 'duzlestirmenin kendisi'")
        print("   TARAMA TESHIS ICINDIR, PARAMETRE SECMEK ICIN DEGIL (K33/K52 overfit yasagi).")
        print("=" * 128)
        basSATIR()
        satir(ozet(calis(D, "acgozlu", 900), "acgozlu (lam=1)"))
        for nerede in ("gec", "hepsi", "erken"):
            for lam in (0.80, 0.65, 0.50):
                satir(ozet(calis(D, f"lam_{nerede}_{lam}", 900), f"lam {nerede} {lam:.2f}"))
            print("  " + "-" * 124)

    if B in (0, 4):
        print("\n" + "=" * 128)
        print("4) BUTCE MERDIVENI — v2'nin ustunlugu butceye ozgu mu?")
        print("=" * 128)
        basSATIR()
        for mk in (96, 288, 900):
            for mod, ad in [("genis", f"orta/genis@{mk}"), ("v2", f"v2@{mk}"),
                            ("acgozlu", f"acgozlu@{mk}"), ("bot1", f"bot1@{mk}")]:
                satir(ozet(calis(D, mod, mk), ad))
            print("  " + "-" * 124)

    if B in (0, 5):
        print("\n" + "=" * 128)
        print("5) PORTFOY — bot1_900 + X (iki kupon AYRI oynanir; kazanan ikisinde de varsa iki kez oder)")
        print("=" * 128)
        basSATIR()
        b1 = R.get("bot1_900") or calis(D, "bot1", 900)
        for mod, ad in [("genis95", "genis900"), ("acgozlu", "acgozlu900"),
                        ("ayrisma", "ayrisma900"), ("v2", "acgozlu_v2")]:
            satir(portfoy(b1, R.get(ad) or calis(D, mod, 900), f"bot1_900 + {ad}"))
        print("  ayni parayi TEK kupona vermek (kontrol):")
        for mod, ad in [("bot1", "bot1_1800"), ("acgozlu", "acgozlu1800"), ("genis95", "genis1800")]:
            satir(ozet(calis(D, mod, 1800), ad))

    if B in (0, 6):
        print("\n" + "=" * 128)
        print("6) YOGUNLASMA — getiri kac olaya dayaniyor? (surdurulebilirligin asil sorusu)")
        print("=" * 128)
        print(f"{'kupon':>16} {'6/6':>5} {'ROI':>8} {'-1':>8} {'-3':>8} {'-5':>8} "
              f"{'en buyuk temettu':>18} {'medyan':>10}")
        for mod, mk, ad in [("bot1", 900, "bot1_900"), ("bot1", 1800, "bot1_1800"),
                            ("v2", 900, "v2_900"), ("genis95", 900, "genis900"),
                            ("acgozlu", 900, "acgozlu900"), ("genis", 96, "orta@96")]:
            s = ozet(calis(D, mod, mk), ad)
            get, mal = s["get"], s["mal"]
            sira = np.argsort(-get)
            ler = []
            for k in (1, 3, 5):
                g = get.copy(); g[sira[:k]] = 0
                ler.append((g.sum() - mal.sum()) / mal.sum() * 100)
            d = get[get > 0]
            print(f"{ad:>16} {len(d):>5} {s['roi']:>+7.1f}% {ler[0]:>+7.1f}% {ler[1]:>+7.1f}% "
                  f"{ler[2]:>+7.1f}% {d.max():>17,.0f} {np.median(d):>10,.0f}")
        print("\n  'ROI' ile '-1' arasindaki ucurum = getirinin TEK OLAYA dayanmasi.")

    if B in (0, 7):
        print("\n" + "=" * 128)
        print("7) BIRLESTIRME — uc bot2 kuponunu tek kupona indirmek (@900)")
        print("=" * 128)
        basSATIR()
        for mod, ad in [("genis95", "genis900 (en iyi tek)"), ("acgozlu", "acgozlu900"),
                        ("birlesim_buda", "birlesim+buda"), ("cogunluk", "cogunluk(>=2/3)"),
                        ("ortalama", "ortalama vektor")]:
            satir(ozet(calis(D, mod, 900), ad))
        print("  NOT: birlesim+buda, genis900 ile olaylarin ~%99,9'unda BIREBIR ayni kupondur.")

    if B in (0, 8):
        print("\n" + "=" * 128)
        print("8) COGALTMA — orta'yi birbirine alternatif cogaltmak (@96)")
        print("=" * 128)
        basSATIR()
        for n in (1, 2, 3, 4):
            satir(ozet(calis(D, f"coklu{n}", 96), f"{n} x orta@96"))
        print("  " + "-" * 124)
        print("  BOLME KURALI KONTROLU (sonuc kurala mi bagli?):")
        satir(ozet(calis(D, "serpistir", 96), "2x serpistir (esit kalite)"))
        satir(ozet(calis(D, "rotasyon", 96), "2x banker rotasyonu"))
        print("  " + "-" * 124)
        print("  ayni parayi TEK kupona vermek:")
        for mk in (96, 192, 288, 384):
            satir(ozet(calis(D, "genis", mk), f"tek kupon @{mk}"))
        print("  NOT: 'sonraki atlar' ile 'serpistir' AYNI sonucu verir -> tek ayakta bolmek,")
        print("       o ayagi genisletmenin baska turlu yazilmasidir.")

    if B in (0, 9):
        print("\n" + "=" * 128)
        print("9) TAVAN — dikdortgen KISITI OLMADAN en olasi N kombinasyon (kupon olarak KURULAMAZ)")
        print("=" * 128)
        basSATIR()
        for mk in (96, 192, 288, 384):
            satir(ozet(calis(D, "tavan", mk), f"tavan {mk} kombinasyon"))
        print("  kiyas icin dikdortgen kupon:")
        for mk in (96, 192, 288):
            satir(ozet(calis(D, "genis", mk), f"orta/genis@{mk}"))
        print("\n  OKUMA: tavan daha COK tutturur ama temettusu YARIYA iner ve ROI'si kotudur.")
        print("  En olasi kombinasyonlar herkesin oynadigidir -> kapsami buyutmek kalabaliga")
        print("  katilmaktir. Kuponun dikdortgen olma zorunlulugu bir handikap degil, kazara")
        print("  isleyen bir kalabaliktan-kacinma mekanizmasidir. (K98-h)")


if __name__ == "__main__":
    main()
