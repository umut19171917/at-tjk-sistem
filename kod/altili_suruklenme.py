"""
altili_suruklenme.py — K80: "UZAK AYAGIN OLASILIGI NE KADAR GUVENILMEZ?" (olcum araci).
OFFLINE, SALT-OKUNUR: canliya DOKUNMAZ, hicbir dosyaya YAZMAZ. Kupon kurmaz, model calistirmaz.

NEDEN VAR (K79):
  Altili kuponu 1. ayaga 30 dk kala kurulur; 6. ayak o an ~180 dk uzaktadir. O yarisin havuzu
  neredeyse bostur -> oranlar carpiktir -> sahte bir favori uretir. ACGOZLU dagitici olasilik
  vektorunun SIVRILIGINE gore genislik dagittigi icin bu sahte favoriye kanar ve en az ati
  oraya yazar (12 bankerinin 6'si 6. ayakta; 6. ayak isabeti %33 vs %75).
  Kapsam dagitici sahaya gore olctugu icin bu tuzaga dusmez (kontrol: p=0,84).

BU ARACIN URETTIGI SAYI (acgozlu_v2 icin gereken tek parametre):
  Her mesafe kovasi icin SICAKLIK KATSAYISI lambda:
        p_kalibre = normalize( p ^ lambda )
  lambda = 1  -> vektor oldugu gibi dogru, budama gerekmez
  lambda < 1  -> vektor FAZLA SIVRI (kendine gereginden cok guveniyor) -> duzlestirilmeli
  lambda, gercek kazananin log-olabilirligini enbuyulterek kestirilir; guven araligi
  KOSU-BAZLI bootstrap ile. Yani katsayi TAHMIN EDILMEZ, OLCULUR.

VERI KAYNAGI: veri/altili_oran_log.csv (kupon anindaki canli oranlar) + veri/defter.csv
  (posta anindaki oran + bot1 + gercek kazanan). bot1 ORAN-KOR oldugu icin gun icinde eskimez,
  defter'den alinir. bot2(t) = softmax(alpha*ln bot1 + gamma*ln p_piyasa(t)), katsayilar
  defter'den geri cikarilir (altili_zaman_test.katsayi_cikar; olculdu a=0,2095 g=0,9495).

ONEMLI — VERI DURUMU BOLUMU:
  oran_log 30 Tem'e kadar her ayagi YALNIZ kendi postasina 45 dk kala kaydediyordu; yani uzak
  ayak kaydi HIC YOKTU (BEKLEYENLER #4 bu yuzden haftalarca cevapsiz kaldi). K76 bunu duzeltti.
  Arac her calisinda ONCE "uzak ayak verisi geliyor mu" diye bakar ve acikca soyler. Ilk
  calistirma AMACI budur: duzeltmenin isledigini 3 hafta sonra degil ERTESI GUN dogrulamak.

Elle:  python altili_suruklenme.py [--bootstrap 2000]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_zaman_test import katsayi_cikar  # noqa: E402

LOG = KOK / "veri" / "altili_oran_log.csv"
DEFTER = KOK / "veri" / "defter.csv"

# Kupon 1. ayaga 30 dk kala kurulur -> ayaklar kabaca 30/60/90/120/150/180 dk uzakta.
# Kovalar bu ayaklara birebir oturur.
KOVA = [(0, 45, "1. ayak (~30 dk)"), (45, 75, "2. ayak (~60 dk)"),
        (75, 105, "3. ayak (~90 dk)"), (105, 135, "4. ayak (~120 dk)"),
        (135, 165, "5. ayak (~150 dk)"), (165, 10 ** 6, "6. ayak (~180 dk+)")]
ASGARI = 15          # bir kovada lambda kestirmek icin en az bu kadar kosu
LAM_IZGARA = np.concatenate([np.arange(0.05, 1.0, 0.01), np.arange(1.0, 2.51, 0.02)])


def devig(oranlar):
    """Ganyan orani -> olasilik (bahisci marji cikarilmis)."""
    inv = 1.0 / np.asarray(oranlar, dtype=float)
    return inv / inv.sum()


def _logol(P, lam):
    """sum ln( normalize(p^lam)[kazanan] ) — P: [(olasilik dizisi, kazanan indeksi), ...]"""
    t = 0.0
    for p, w in P:
        q = np.power(p, lam)
        t += np.log(q[w] / q.sum())
    return t


def lambda_kestir(P):
    """Kazananin log-olabilirligini enbuyuten lambda (izgara + yerel incelme)."""
    if not P:
        return np.nan
    skor = [_logol(P, l) for l in LAM_IZGARA]
    en = LAM_IZGARA[int(np.argmax(skor))]
    ince = np.arange(max(en - 0.02, 0.01), en + 0.021, 0.002)
    return float(ince[int(np.argmax([_logol(P, l) for l in ince]))])


def lambda_ga(P, n=1500, tohum=0):
    """Kosu-bazli bootstrap ile %90 guven araligi."""
    if len(P) < ASGARI:
        return (np.nan, np.nan)
    rng = np.random.default_rng(tohum)
    v = []
    for _ in range(n):
        idx = rng.integers(0, len(P), len(P))
        l = lambda_kestir([P[i] for i in idx])
        if np.isfinite(l):
            v.append(l)
    if not v:
        return (np.nan, np.nan)
    return (float(np.percentile(v, 5)), float(np.percentile(v, 95)))


def veri_durumu(log):
    """K76 dogrulamasi: uzak ayak kaydi geliyor mu? Haftalik ilerleme cubugu."""
    print("=" * 92)
    print("VERI DURUMU — 'uzak ayak' kaydi geliyor mu? (K76 duzeltmesinin dogrulamasi)")
    print("=" * 92)
    if log.empty:
        print("  oran_log BOS.")
        return False
    print(f"  toplam {len(log):,} satir | {log.race_kod.nunique()} kosu | "
          f"tarihler {log.tarih.min()} .. {log.tarih.max()}")
    print(f"  dk_kala araligi: {log.dk_kala.min():.0f} .. {log.dk_kala.max():.0f} dk")
    uzak = log[log.dk_kala > 60]
    if uzak.empty:
        print("\n  >>> UZAK AYAK (>60 dk) KAYDI YOK. <<<")
        print("      K76 oncesi davranis buydu: her ayak yalniz KENDI postasina 45 dk kala")
        print("      kaydediliyordu. Duzeltme 31 Tem'de girdi; ilk kosulardan sonra burada")
        print("      60/90/120/150/180 dk satirlari GORUNMELI. Gorunmuyorsa oran_log'a bak.")
        return False
    print("\n  UZAK AYAK KAYDI VAR — K76 calisiyor. Gune gore:")
    t = uzak.groupby("tarih").agg(kosu=("race_kod", "nunique"), en_uzak=("dk_kala", "max"))
    for tar, r in t.iterrows():
        print(f"    {tar}: {int(r.kosu):3d} kosu, en uzak {r.en_uzak:.0f} dk")
    return True


def main(bootstrap=1500):
    if not LOG.exists():
        print("altili_oran_log.csv yok."); return
    log = pd.read_csv(LOG)
    for c in ("ganyan", "dk_kala", "race_kod", "no"):
        log[c] = pd.to_numeric(log[c], errors="coerce")
    log = log[(log.kosmaz == 0) & log.ganyan.notna() & (log.ganyan > 1) & log.dk_kala.notna()]

    uzak_var = veri_durumu(log)

    d = pd.read_csv(DEFTER, low_memory=False).drop_duplicates(["race_kod", "no"], keep="last")
    for c in ("race_kod", "no", "bot1", "bot2", "kamu", "oran", "sonuc"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    dd = d.dropna(subset=["bot1", "bot2", "kamu"])
    dd = dd[(dd.bot1 > 0) & (dd.bot2 > 0) & (dd.kamu > 0)]
    alpha, gamma, r2 = katsayi_cikar(dd)
    print(f"\nharman katsayilari (defter'den geri cikarildi): "
          f"alpha={alpha:.4f} gamma={gamma:.4f} R2={r2:.6f}")
    print(f"  -> bot2'nin agirliginin ~%{100*gamma/(alpha+gamma):.0f}'i PIYASADAN geliyor; "
          f"piyasa eskiyince bot2 de eskir. bot1 orana bakmaz, eskimez.")

    # ---- her kova icin gozlemleri topla ----
    kutu = {ad: {"pz": [], "p1": [], "fav": [], "tvd": [], "ust3": []} for _, _, ad in KOVA}
    for rk, g in log.groupby("race_kod"):
        dg = d[d.race_kod == rk].dropna(subset=["oran", "bot1"])
        dg = dg[dg.oran > 1]
        if len(dg) < 4:
            continue
        w = dg[dg.sonuc == 1]
        if len(w) == 0:
            continue
        kaz_no = int(w.iloc[0]["no"])
        son_o = {int(n): float(o) for n, o in zip(dg.no, dg.oran)}
        b1m = {int(n): float(b) for n, b in zip(dg.no, dg.bot1)}
        for ts, s in g.groupby("kayit_ts"):
            no = sorted({int(x) for x in s.no} & set(son_o))
            if len(no) < 4 or kaz_no not in no:
                continue
            dk = float(s.dk_kala.iloc[0])
            ad = next((a for lo, hi, a in KOVA if lo <= dk < hi), None)
            if ad is None:
                continue
            w_idx = no.index(kaz_no)
            pm = devig([float(s[s.no == n].ganyan.iloc[0]) for n in no])   # kupon ani piyasa
            ps = devig([son_o[n] for n in no])                             # posta ani piyasa
            b1 = np.array([b1m[n] for n in no], dtype=float)
            b1 = b1 / b1.sum()
            z = alpha * np.log(b1) + gamma * np.log(pm)
            pz = np.exp(z - z.max()); pz = pz / pz.sum()                   # kupon ani bot2
            kutu[ad]["pz"].append((pz, w_idx))
            kutu[ad]["p1"].append((b1, w_idx))
            kutu[ad]["fav"].append(no[int(np.argmax(pm))] == no[int(np.argmax(ps))])
            kutu[ad]["tvd"].append(0.5 * np.abs(pm - ps).sum())
            a3 = set(np.array(no)[np.argsort(-pm)][:3]); b3 = set(np.array(no)[np.argsort(-ps)][:3])
            kutu[ad]["ust3"].append(len(a3 & b3) / 3.0)

    print("\n" + "=" * 92)
    print("A) BETIMSEL — kupon anindaki piyasa, posta anina gore ne kadar kaymis?")
    print("=" * 92)
    print(f"  {'kova':22s}{'n':>5s}{'favori ayni':>14s}{'ilk-3 ortusme':>16s}{'vektor kaymasi':>17s}")
    for _, _, ad in KOVA:
        k = kutu[ad]
        if not k["fav"]:
            print(f"  {ad:22s}{0:>5d}{'-':>14s}{'-':>16s}{'-':>17s}"); continue
        print(f"  {ad:22s}{len(k['fav']):>5d}"
              f"{'%' + format(100*np.mean(k['fav']), '.1f'):>14s}"
              f"{'%' + format(100*np.mean(k['ust3']), '.1f'):>16s}"
              f"{'%' + format(100*np.mean(k['tvd']), '.1f'):>17s}")

    print("\n" + "=" * 92)
    print("B) SICAKLIK KATSAYISI lambda — acgozlu_v2'nin ihtiyaci olan sayi")
    print("   p_kalibre = normalize(p^lambda);  lambda<1 => vektor fazla sivri, DUZLESTIR")
    print("=" * 92)
    print(f"  {'kova':22s}{'n':>5s}{'bot2 lambda':>16s}{'%90 GA':>18s}{'bot1 lambda':>16s}")
    for _, _, ad in KOVA:
        k = kutu[ad]
        n = len(k["pz"])
        if n < ASGARI:
            print(f"  {ad:22s}{n:>5d}{'yetersiz':>16s}{'(en az ' + str(ASGARI) + ')':>18s}{'-':>16s}")
            continue
        lz = lambda_kestir(k["pz"]); lo, hi = lambda_ga(k["pz"], bootstrap)
        l1 = lambda_kestir(k["p1"])
        print(f"  {ad:22s}{n:>5d}{lz:>16.3f}{f'[{lo:.2f} .. {hi:.2f}]':>18s}{l1:>16.3f}")

    # ---- C) ESLESMIS: AYNI KOSU, UZAKTAN vs YAKINDAN (K81) ----
    # A/B tablolari FARKLI kosulari kiyasliyor -> uzak kovalar gunun GEC kosulari (saha daha
    # kalabalik, intrinsik olarak zor). Nitekim bot1'in lambda'si da kovalarla dusuyor; oysa
    # bot1 orana bakmaz, eskiyemez -> dusus eskime DEGIL, kosu secimi. Tek durust kiyas:
    # ayni kosunun uzak fotografi ile yakin fotografi. bot1 vektoru ikisinde de AYNI oldugu
    # icin fark tamamen PIYASA bileseninden gelir.
    uzakp, yakinp, b1p = [], [], []
    for rk, g in log.groupby("race_kod"):
        dg = d[d.race_kod == rk].dropna(subset=["oran", "bot1"])
        dg = dg[dg.oran > 1]
        if len(dg) < 4:
            continue
        w = dg[dg.sonuc == 1]
        if len(w) == 0:
            continue
        kaz_no = int(w.iloc[0]["no"])
        b1m = {int(n): float(b) for n, b in zip(dg.no, dg.bot1)}
        gu = g[g.dk_kala > 60]
        gy = g[g.dk_kala <= 45]
        if gu.empty or gy.empty:
            continue
        cift = []
        for gg, en_uzak in ((gu, True), (gy, False)):
            ts = gg.loc[gg.dk_kala.idxmax() if en_uzak else gg.dk_kala.idxmin(), "kayit_ts"]
            s = gg[gg.kayit_ts == ts]
            no = sorted({int(x) for x in s.no} & set(b1m))
            if len(no) < 4 or kaz_no not in no:
                cift = None; break
            pm = devig([float(s[s.no == n].ganyan.iloc[0]) for n in no])
            b1 = np.array([b1m[n] for n in no]); b1 = b1 / b1.sum()
            z = alpha * np.log(b1) + gamma * np.log(pm)
            pz = np.exp(z - z.max())
            cift.append((pz / pz.sum(), b1, no.index(kaz_no), float(s.dk_kala.iloc[0])))
        if not cift or len(cift) != 2:
            continue
        uzakp.append((cift[0][0], cift[0][2]))
        yakinp.append((cift[1][0], cift[1][2]))
        b1p.append((cift[0][1], cift[0][2]))

    print("\n" + "=" * 92)
    print("C) ESLESMIS KIYAS — AYNI kosu, uzaktan (>60 dk) vs yakindan (<=45 dk)   [ASIL OLCUT]")
    print("=" * 92)
    if len(uzakp) < ASGARI:
        print(f"  n={len(uzakp)} — yetersiz (en az {ASGARI}). Ayni kosunun hem uzak hem yakin")
        print("  fotografi gerekiyor; K76 sonrasi birikiyor.")
    else:
        lu = lambda_kestir(uzakp); lo_u, hi_u = lambda_ga(uzakp, bootstrap)
        ly = lambda_kestir(yakinp); lo_y, hi_y = lambda_ga(yakinp, bootstrap)
        lb = lambda_kestir(b1p)
        print(f"  ayni {len(uzakp)} kosu, iki farkli anda olculdu:")
        print(f"    UZAKTAN  bot2 lambda = {lu:.3f}   %90 GA [{lo_u:.2f} .. {hi_u:.2f}]")
        print(f"    YAKINDAN bot2 lambda = {ly:.3f}   %90 GA [{lo_y:.2f} .. {hi_y:.2f}]")
        print(f"    (ayni kosularda bot1 lambda = {lb:.3f} — iki anda da AYNI vektor,")
        print(f"     zorluk taban cizgisi; uzak/yakin farki tamamen PIYASADAN gelir)")
        rng = np.random.default_rng(7)
        fark = []
        for _ in range(bootstrap):
            i = rng.integers(0, len(uzakp), len(uzakp))
            a_ = lambda_kestir([uzakp[j] for j in i]); b_ = lambda_kestir([yakinp[j] for j in i])
            if np.isfinite(a_) and np.isfinite(b_):
                fark.append(a_ - b_)
        if fark:
            f5, f95 = np.percentile(fark, 5), np.percentile(fark, 95)
            print(f"\n    FARK (uzak - yakin) = {lu-ly:+.3f}   %90 GA [{f5:+.2f} .. {f95:+.2f}]")
            print("    GA sifiri iceriyorsa: uzaklik BASLI BASINA bozmuyor -> acgozlu ELLENMEZ.")

    print("\n" + "=" * 92)
    print("NASIL OKUNUR")
    print("=" * 92)
    print("  * ASIL OLCUT (C) — A/B tablolari farkli kosulari kiyasladigi icin gunun geç")
    print("    kosulari (kalabalik saha) yanlisligi tasir; bot1 sutunu bunun kanitidir.")
    print("  * 6. ayagin lambda'si 1'e yakinsa -> uzak ayak sanildigi kadar guvenilmez DEGIL,")
    print("    K79'daki 4/12 tesadufmus demektir; acgozlu ELLENMEZ.")
    print("  * 6. ayagin lambda'si belirgin kucukse (GA'si 1'i icermiyorsa) -> vektor sahiden")
    print("    fazla sivri. O zaman acgozlu_v2, dagitim yaparken her ayagin olasiligini o")
    print("    ayagin lambda'siyla duzlestirir; banker YASAKLANMAZ, sadece hak edilmesi gerekir.")
    print("  * bot1 lambda'si karsilastirma icin: bot1 orana bakmaz, mesafeyle BOZULMAMALI.")
    print("    Kovalar arasi sabit cikiyorsa eskime hikayesi dogrulanir.")
    if not uzak_var:
        print("\n  !! Su an uzak ayak verisi YOK -> B tablosunun 2-6. satirlari doldugunda")
        print("     karar verilebilir. Bu araci HAFTADA BIR calistir; n sutunu ilerleme cubugudur.")
    print("\n  Bu arac hicbir seye yazmaz; karar KARARLAR.md'ye elle islenir.")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--bootstrap", type=int, default=1500)
    main(ap.parse_args().bootstrap)
