"""
kulvar_tercih_test.py — K102 adayi: "ATA OZEL KULVAR TERCIHI" ozelligi ise yariyor mu?
OFFLINE, SALT-OKUNUR: ozellikli.csv'yi EZMEZ, canliya/config'e DOKUNMAZ, hicbir dosyaya yazmaz.

NEREDEN GELDI: kullanici 10 Agu'da sordu — "sistem analizinde jokey, atin kulvari, hava ve pist
durumu, atin son antrenmanlari degerlendiriliyor mu?" Cevap: jokey VAR (365 gun isabet + jokey
degisimi), kulvar VAR ama **PIST SEVIYESINDE** (kulvar_skor = sehir x mesafe kovasi x start
kovasi tarihsel galip orani, <=2024 egitim yillarindan), antrenor VAR, zemin VAR, taki degisimi
VAR; hava/going YOK (going K33'te test edilip ELENDI), antrenman verisi feed'de YOK.

**Denenmemis tek sey:** ata OZEL kulvar tercihi — "bu at genis kulvardan iyi kosar". Mevcut
kulvar_skor pistin biasini olcer, atin tercihini DEGIL. K33 ozellik muhendisligini kapatmisti;
bu betik o kapiyi GEREKCEYLE aciyor ve tek bir ozellik test ediyor.

OZELLIK (mevcut zemin_galip_oran deseniyle BIREBIR ayni, nokta-aninda):
  kulvar_uygunluk = atin BU start kovasindaki (1-3 / 4-6 / 7-9 / 10-12 / 13+) ONCEKI galip orani
  shift/cumsum ile mevcut kosu daima haric; yaris-ici z-skor.

KARAR OLCUTU (SONUC GORULMEDEN BAGLANDI, sonuca gore DEGISTIRILMEYECEK) — ikisi de saglanmali:
  (a) Bot2 (URETIM CIKTISI) test log-loss iyilesmesi >= 0.0010.
      Gerekce: K33'te going_uygunluk Bot2'yi 0.00004 oynatmisti ve "SIFIR" sayilmisti; Batch 1
      (bariz sinyaller) Bot1'i 0.0005 oynatmisti. 0.0010 esigi, olculmus "sifir"in 25 kati ve
      Batch 1'in iki kati -> gecerse gercekten yeni bilgidir.
  (b) Yeni ozelligin kilitli modeldeki katsayisi, ESDOGRUSAL ADAYLARIN katsayilarindaki
      DUSUSUN TOPLAMINDAN buyuk olmali (kulvar_skor_z + kariyer_galip_oran_z + zemin_galip_oran_z).
      Gerekce: K33'te going_uygunluk +0.073 aldi ama zemin_galip_oran +0.137 -> +0.064'e dustu
      (0.064+0.073=0.137) -> yeni sinyal degil, ayni sinyalin bolunmesiydi. Bu tuzak tekrarlanmasin.
  Birinde bile kalirsa EKLENMEZ ve K33'un kapanisi yerinde kalir.

Walk-forward K38/model.py ile AYNI: egit <=2023, harman(alpha/gamma) 2024, TEST 2025-26.
Elle: python kulvar_tercih_test.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from ozellik import FEAT, load_katilim, build_features, select_scope, zscore_race  # noqa: E402
from model import race_struct, seg_softmax, fit_clogit, logloss, devig, prep  # noqa: E402

YENI = "kulvar_uygunluk_z"
ESDOGRUSAL = ["kulvar_skor_z", "kariyer_galip_oran_z", "zemin_galip_oran_z"]
ESIK_LOGLOSS = 0.0010


def kulvar_uygunluk_ekle(d):
    """Atin BU start kovasindaki onceki galip orani (nokta-aninda; mevcut kosu haric).
    zemin_galip_oran ile birebir ayni desen -> kiyaslanabilir."""
    d = d.sort_values(["at_kod", "dt", "race_kod"]).reset_index(drop=True)
    g = d.groupby(["at_kod", "st_kova"], sort=False, observed=True)
    d["kulvar_kosu"] = g.cumcount()
    d["kulvar_galip"] = g["kazandi"].cumsum() - d["kazandi"]
    d["kulvar_uygunluk"] = d["kulvar_galip"] / d["kulvar_kosu"].replace(0, np.nan)
    return d


def kur(f, feats):
    """Walk-forward: Bot1 (<=2023) + harman (2024) + TEST (2025-26). Doner olcum sozlugu."""
    f = f.copy()
    for c in feats:
        f[c] = pd.to_numeric(f[c], errors="coerce").fillna(0.0)
    f["yil"] = pd.to_datetime(f["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    tr = f[f.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
    va = prep(f[f.yil == 2024])
    te = prep(f[f.yil >= 2025])
    beta = fit_clogit(tr[feats].values, *race_struct(tr))

    def pf(df):
        st, sz, _ = race_struct(df)
        return seg_softmax(df[feats].values @ beta, st, sz), (st, sz)

    pf_va, (stv, szv) = pf(va)
    pm_va = devig(va.ganyan_muhtemel.values, stv, szv)
    a, g = fit_clogit(np.c_[np.log(pf_va + 1e-12), np.log(pm_va + 1e-12)],
                      stv, szv, va.kazandi.values == 1)
    pf_te, (stt, szt) = pf(te)
    pm_te = devig(te.ganyan_muhtemel.values, stt, szt)
    win = te.kazandi.values == 1
    pc = seg_softmax(a * np.log(pf_te + 1e-12) + g * np.log(pm_te + 1e-12), stt, szt)
    return {"beta": dict(zip(feats, beta)), "alpha": a, "gamma": g,
            "bot1": logloss(pf_te, stt, szt, win), "bot2": logloss(pc, stt, szt, win),
            "piyasa": logloss(pm_te, stt, szt, win),
            "kosu": {"egit": tr.race_kod.nunique(), "val": va.race_kod.nunique(),
                     "test": te.race_kod.nunique()}}


def main():
    print("OLCUT (onceden bagli): (a) Bot2 test log-loss iyilesmesi >= %.4f  VE" % ESIK_LOGLOSS)
    print("                       (b) yeni katsayi > esdogrusal adaylardaki dususun toplami")
    print("Ikisi de saglanmazsa EKLENMEZ; K33'un kapanisi yerinde kalir.\n")

    print("veri hazirlaniyor (katilim.csv -> ozellikler)...")
    d = load_katilim()
    d = build_features(d)
    d = kulvar_uygunluk_ekle(d)
    f = select_scope(d)                      # Ingiliz + izinli pist + yaris-ici z
    f[YENI] = zscore_race(f, "kulvar_uygunluk")
    dolu = f["kulvar_uygunluk"].notna().mean() * 100
    print(f"kapsam: {len(f):,} at-satiri | {f.race_kod.nunique():,} kosu | "
          f"yeni ozellik doluluk: %{dolu:.1f}")

    taban = kur(f, list(FEAT))
    yeni = kur(f, list(FEAT) + [YENI])
    print(f"kosu: egit {taban['kosu']['egit']:,} | val {taban['kosu']['val']:,} | "
          f"test {taban['kosu']['test']:,}\n")

    print("=" * 88)
    print("TEST (2025-26) LOG-LOSS  — dusuk iyi")
    print("=" * 88)
    print(f"{'':>10} {'piyasa':>10} {'Bot1':>10} {'Bot2 (URETIM)':>15} {'alpha':>8} {'gamma':>8}")
    for ad, r in (("17 ozellik", taban), ("18 ozellik", yeni)):
        print(f"{ad:>10} {r['piyasa']:>10.5f} {r['bot1']:>10.5f} {r['bot2']:>15.5f} "
              f"{r['alpha']:>+8.3f} {r['gamma']:>+8.3f}")
    d_bot1 = taban["bot1"] - yeni["bot1"]
    d_bot2 = taban["bot2"] - yeni["bot2"]
    print(f"\n  iyilesme: Bot1 {d_bot1:+.5f}   Bot2 {d_bot2:+.5f}   (pozitif = yeni model iyi)")

    print("\n" + "=" * 88)
    print("ESDOGRUSALLIK — yeni ozellik gercekten yeni bilgi mi, yoksa agirlik mi boluyor?")
    print("=" * 88)
    print(f"{'ozellik':>26} {'17li kats.':>11} {'18li kats.':>11} {'degisim':>10}")
    dus = 0.0
    for c in ESDOGRUSAL:
        a, b = taban["beta"][c], yeni["beta"][c]
        dus += max(0.0, abs(a) - abs(b))
        print(f"{c:>26} {a:>+11.4f} {b:>+11.4f} {b - a:>+10.4f}")
    ykats = yeni["beta"][YENI]
    print(f"{YENI:>26} {'-':>11} {ykats:>+11.4f}")
    print(f"\n  esdogrusal adaylardaki |katsayi| DUSUSUNUN toplami: {dus:.4f}")
    print(f"  yeni ozelligin |katsayisi|                        : {abs(ykats):.4f}")

    print("\n" + "=" * 88)
    print("KARAR")
    print("=" * 88)
    a_ok = d_bot2 >= ESIK_LOGLOSS
    b_ok = abs(ykats) > dus
    print(f"  (a) Bot2 iyilesmesi {d_bot2:+.5f} >= {ESIK_LOGLOSS:.4f} ? "
          f"[{'GECTI' if a_ok else 'KALDI'}]")
    print(f"  (b) yeni katsayi {abs(ykats):.4f} > dusus toplami {dus:.4f} ? "
          f"[{'GECTI' if b_ok else 'KALDI'}]")
    print(f"\n  SONUC: {'EKLENEBILIR — konusalim' if (a_ok and b_ok) else 'EKLENMEZ (K33 kapanisi yerinde)'}")
    print("\n  NOT: bu betik ozellikli.csv'yi EZMEDI; canli model 17 ozellikle calismaya devam ediyor.")


if __name__ == "__main__":
    main()
