"""
altili_bot1_test.py — "KAMU BOTU (Bot2) HIC OLMASAYDI NE OLURDU?" backtesti (K67 adayi).
OFFLINE, SALT-OKUNUR: canliya / takip'e / mevcut veri dosyalarina DOKUNMAZ.
Kendi cikti dosyasini yazar: veri/altili_olasilik_bot1.csv (yeni; mevcut altili_olasilik.csv
AYNEN KALIR).

SORU (kullanici, 2026-07-30): Tum kuponlarimiz Bot2 ile kuruldu. Bot2 = Bot1 (oran-kor temel
model) ile piyasanin (kamu oranlari) HARMANI. Peki harman hic olmasaydi -- yani kalabaligin
fikrini hic sormasaydik, sadece kendi temel modelimizle kupon kursaydik -- ne olurdu?

NEDEN ONEMLI (olcum, 24.822 kosu): Bot2 pratikte KAMUNUN KENDISI.
  - Bot2 favorisi = kamu favorisi olan kosu: %89,9
  - Bot2 ile kamu sirasi korelasyonu: 0,977
  - kamu favorisi kazanma orani %35,6  vs  Bot2 favorisi %35,7  (fark ~0,1 puan)
Yani bugune kadarki her kupon, ozunde KALABALIGIN kuponu. Bot1 ise oranlara HIC bakmaz =
kalabaliktan maksimum ayrilan surumumuz. Pari-mutuel'de odeme, kac kisinin ayni kuponu
yazdigina bagli oldugu icin bu soru dogrudan "ayri dusmek oduyor mu"yu sinar.

BEKLENTI (onceden yazildi, sonuca gore degistirilmeyecek): Bot1 tek basina DAHA AZ tutturur
(kamu ciddi bilgi tasiyor, atmak isabetten olur) ama tutturdugunda DAHA COK oder (kimse o
kuponu yazmamistir). Toplamda hangisi agir basar: BILINMIYOR -- test bunun icin.

YONTEM (K52/K65 ile ayni zemin):
  - Bot1 = altili_olasilik.py'nin ICINDE zaten hesaplanan `pf` (satir 49); orada kaydedilmiyordu.
    Burada AYNI walk-forward kurulumu (Bot1 egitim <=2023, harman 2024) birebir tekrarlanir ve
    pf de saklanir. Uretilen bot2 sutunu mevcut dosyayla KARSILASTIRILARAK dogrulanir.
  - Ayni 1455 OOS olay (2025-26), ayni butceler, ayni dagiticilar (kapsam-v1 ve acgozlu).
  - DURUST ZEMIN: sadece 6/6 oder (teselli yok) -- K57/K65'teki olcut.
  - Bootstrap %95 GA + esli fark (ayni olaylar) -> "fark sans mi?" sorusu cevaplanir.
Elle: python altili_bot1_test.py [--yenile]   (--yenile: bot1 dosyasini bastan uret, yavas)
"""
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
BUTCELER = [(24, "dar"), (96, "orta"), (288, "genis"), (900, "genis900")]
RNG = np.random.default_rng(20260730)
NBOOT = 4000


# ------------------------------------------------------- Bot1 uretimi (bir kez)
def uret():
    """altili_olasilik.irk_model'in BIREBIR ayni walk-forward kurulumu; farki: pf (=Bot1) de saklanir.
    Mevcut veri/altili_olasilik.csv'ye DOKUNMAZ; ayri dosya yazar."""
    from ozellik import load_katilim, build_features, select_scope, FEAT  # noqa
    from model import race_struct, seg_softmax, fit_clogit, devig        # noqa
    d = load_katilim()
    d = build_features(d)
    d["yil"] = d["dt"].dt.year
    parcalar = []
    for irk in ("Ingiliz", "Arap"):
        f = select_scope(d, irk=irk)
        f["yil"] = pd.to_datetime(f["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
        for c in FEAT:
            f[c] = pd.to_numeric(f[c], errors="coerce").fillna(0.0)
        f = f[f["ganyan_muhtemel"] > 1].copy()

        tr = f[f.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
        beta = fit_clogit(tr[FEAT].values, *race_struct(tr))

        va = f[f.yil == 2024].copy()
        gw = va.groupby("race_kod")["kazandi"].transform("sum")
        sz = va.groupby("race_kod")["race_kod"].transform("size")
        va = va[(gw == 1) & (sz >= 4)].sort_values("race_kod").reset_index(drop=True)
        stv, szv, winv = race_struct(va)
        pfv = seg_softmax(va[FEAT].values @ beta, stv, szv)
        pmv = devig(va.ganyan_muhtemel.values, stv, szv)
        alpha, gamma = fit_clogit(np.c_[np.log(pfv + 1e-12), np.log(pmv + 1e-12)], stv, szv, winv)

        out = []
        for rk, g in f.groupby("race_kod", sort=False):
            g = g.sort_values("no")
            st = np.array([0]); szc = np.array([len(g)])
            pf = seg_softmax(g[FEAT].values @ beta, st, szc)          # <-- BOT1 (oran-kor)
            pm = devig(g["ganyan_muhtemel"].values, st, szc)
            b2 = seg_softmax(alpha * np.log(pf + 1e-12) + gamma * np.log(pm + 1e-12), st, szc)
            out.append(pd.DataFrame({"race_kod": rk, "no": g["no"].values,
                                     "at_kod": g["at_kod"].values, "bot1": pf, "bot2": b2,
                                     "kamu": pm, "kazandi": g["kazandi"].values}))
        res = pd.concat(out, ignore_index=True)
        res["irk"] = irk
        parcalar.append(res)
        print(f"  {irk}: {res['race_kod'].nunique()} kosu | alpha={alpha:+.3f} gamma={gamma:+.3f}")
    allp = pd.concat(parcalar, ignore_index=True)
    BOT1CSV.parent.mkdir(parents=True, exist_ok=True)
    allp.to_csv(BOT1CSV, index=False, encoding="utf-8")
    print(f"  -> {BOT1CSV.name}: {allp['race_kod'].nunique()} kosu / {len(allp)} satir")
    return allp


def dogrula(yeni):
    """Uretilen bot2, mevcut altili_olasilik.csv ile ayni mi? (yeniden uretimin ISPATI)"""
    eski = pd.read_csv(KOK / "veri" / "altili_olasilik.csv", low_memory=False)
    m = eski.merge(yeni, on=["race_kod", "no"], suffixes=("_e", "_y"))
    if m.empty:
        print("  DOGRULAMA: eslesen satir yok (!)"); return
    d = (m.bot2_e - m.bot2_y).abs()
    print(f"  DOGRULAMA: {len(m):,} ortak satirda bot2 farki  max={d.max():.2e}  ort={d.mean():.2e}"
          f"  -> {'AYNI (yeniden uretim dogru)' if d.max() < 1e-6 else 'FARKLI (!) dikkat'}")


# ------------------------------------------------------- degerlendirme
def olay_sonuc(o, pmap, wmap, max_kombo, dagitim, birim=1.0):
    """Tek olay -> (maliyet, getiri_6, alti, genislikler). None: veri eksik."""
    ayak_atlari, kaz = [], []
    for i in range(6):
        rk = int(o[f"leg{i+1}"])
        atlar = pmap.get(rk)
        if not atlar:
            return None
        ayak_atlari.append(atlar)
        w = wmap.get(rk)
        if w is None:
            return None
        kaz.append(w)
    sec = (kupon_kur_acgozlu(ayak_atlari, max_kombo) if dagitim == "acgozlu"
           else kupon_kur(ayak_atlari, KAPSAM, max_kombo, BANKER))
    gen = [len(s) for s in sec]
    nk = int(np.prod(gen))
    if nk == 0:
        return None
    g6 = 0.0
    alti = 0
    if all(kaz[i] in sec[i] for i in range(6)):
        div = o.get("t6_div")
        if pd.notna(div):
            g6 = birim * float(div)
        alti = 1
    return nk * birim, g6, alti, gen


def calis(olaylar, pmap, wmap, max_kombo, dagitim):
    mal, g6, a6, sek, div = [], [], 0, [], []
    for o in olaylar:
        r = olay_sonuc(o, pmap, wmap, max_kombo, dagitim)
        if r is None:
            continue
        m, g, al, gen = r
        mal.append(m); g6.append(g); a6 += al; sek.append(gen)
        if al:
            div.append(float(o["t6_div"]) if pd.notna(o.get("t6_div")) else 0.0)
    return np.array(mal), np.array(g6), a6, np.array(sek), np.array(div)


def boot(mal, get):
    if len(mal) == 0:
        return (float("nan"),) * 2
    idx = RNG.integers(0, len(mal), size=(NBOOT, len(mal)))
    r = (get[idx].sum(1) - mal[idx].sum(1)) / mal[idx].sum(1) * 100
    return np.percentile(r, 2.5), np.percentile(r, 97.5)


def fark_ga(m0, g0, m1, g1):
    n = min(len(m0), len(m1))
    idx = RNG.integers(0, n, size=(NBOOT, n))
    r0 = (g0[idx].sum(1) - m0[idx].sum(1)) / m0[idx].sum(1) * 100
    r1 = (g1[idx].sum(1) - m1[idx].sum(1)) / m1[idx].sum(1) * 100
    d = r1 - r0
    lo, hi = np.percentile(d, 2.5), np.percentile(d, 97.5)
    yorum = "SIFIRI ICERIR -> fark sans" if lo <= 0 <= hi else "sifir DISINDA -> gercek fark"
    print(f"      bot1 eksi bot2: {np.median(d):+.1f} puan, %95 GA [{lo:+.1f}, {hi:+.1f}]  ({yorum})")


def main():
    yenile = "--yenile" in sys.argv
    if yenile or not BOT1CSV.exists():
        print("Bot1 olasiliklari uretiliyor (walk-forward, birkac dakika surebilir)...")
        p = uret()
        dogrula(p)
    else:
        p = pd.read_csv(BOT1CSV, low_memory=False)
        print(f"{BOT1CSV.name} okundu: {p['race_kod'].nunique():,} kosu")

    olay = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    olay["yil"] = pd.to_datetime(olay["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    olay = olay[~olay["sehir"].isin(EXCL_SEHIR)]
    oos = list(olay[olay.yil >= 2025].to_dict("records"))

    pm1, pm2, wmap = {}, {}, {}
    for rk, g in p.groupby("race_kod"):
        pm1[rk] = list(zip(g["no"], g["bot1"]))
        pm2[rk] = list(zip(g["no"], g["bot2"]))
        w = g.loc[g["kazandi"] == 1, "no"]
        if len(w):
            wmap[rk] = int(w.iloc[0])

    # once: Bot1 tek basina NE KADAR ISABETLI (kupon oncesi teshis)
    print("\n" + "=" * 100)
    print("TESHIS — favori kazanma orani (tum arsiv):")
    for ad, col in (("bot1 (oran-kor)", "bot1"), ("bot2 (harman)", "bot2"), ("kamu (oranlar)", "kamu")):
        top = p.loc[p.groupby("race_kod")[col].idxmax()]
        print(f"   {ad:18s}: %{100*top.kazandi.mean():.1f}")
    ayni1 = sum(1 for rk, g in p.groupby("race_kod")
                if g.loc[g.bot1.idxmax(), "no"] == g.loc[g.kamu.idxmax(), "no"])
    print(f"   bot1 favorisi = kamu favorisi olan kosu: %{100*ayni1/p.race_kod.nunique():.1f}"
          "   (bot2'de %89,9 idi -> bot1 kalabaliktan COK daha ayri)")

    print("\n" + "=" * 100)
    print("ALTILI: BOT1 (kamu botu YOK) vs BOT2 (mevcut) — ayni olay, ayni butce, DURUST zemin")
    print(f"OOS olay: {len(oos)} | ROI(6): sadece 6/6 oder | GA: bootstrap %95")
    print("=" * 100)
    for dagitim in ("kapsam", "acgozlu"):
        print(f"\n### DAGITIM: {dagitim} ###")
        print(f"{'butce':>6} {'puan':>5} {'olay':>5} {'ort.kombo':>9} {'ROI(6)%':>9} {'ROI(6) GA':>17} "
              f"{'6/6':>4} {'isabet%':>7} {'ort.temettu':>11}")
        for mk, ad in BUTCELER:
            sakla = {}
            for etiket, pmap in (("bot2", pm2), ("bot1", pm1)):
                mal, g6, a6, sek, div = calis(oos, pmap, wmap, mk, dagitim)
                if len(mal) == 0:
                    continue
                roi = (g6.sum() - mal.sum()) / mal.sum() * 100
                lo, hi = boot(mal, g6)
                print(f"{mk:>6} {etiket:>5} {len(mal):>5} {mal.sum()/len(mal):>9.1f} {roi:>+9.1f} "
                      f"[{lo:>+6.1f},{hi:>+6.1f}] {a6:>4} {100*a6/len(mal):>7.2f} "
                      f"{(div.mean() if len(div) else 0):>11,.0f}")
                sakla[etiket] = (mal, g6)
            if len(sakla) == 2:
                fark_ga(*sakla["bot2"], *sakla["bot1"])
    print("\n" + "=" * 100)
    print("OKUMA: bot1'in isabeti DUSUK ama ort.temettusu YUKSEK cikmasi beklenir (kalabaliktan ayri).")
    print("Karar olcutu ROI(6). Esli fark GA'si sifiri iceriyorsa 'ayri dusmek olculebilir kazanc")
    print("vermiyor' demektir; NEGATIF ve sifir disindaysa kamuyu atmak PAHALIYA patliyor demektir.")
    print("=" * 100)


if __name__ == "__main__":
    main()
