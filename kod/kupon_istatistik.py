# -*- coding: utf-8 -*-
"""
kupon_istatistik.py — K140: TÜM AKTİF KUPON TÜRLERİNİN tam istatistiği + son 2 hafta kıyası.
SALT-OKUNUR / OFFLINE. Kullanıcı isteği (2 Eylül 2026): "şu an aktif olan tüm kupon
türlerini, yapılmış tüm kuponları üzerinden dikkatle incele ve ayak bazında, kupon tutma
bazında istatistiğini ver; son iki haftayı öncekilerle kıyasla, başarı oranında düşüş var mı".

KAPSAM: veri/altili_kupon.csv — kâğıt sistemin (paper) TÜM sonuçlanmış Altılı ayakları.
Aktif config'ler `altili_canli.KONFIG`'den (aktif=True) OKUNUR, elle kopyalanmaz.

TANIM:
  ayak isabeti  = bir ayakta (6'dan biri) seçtiğimiz atlardan biri kazandı mı (tuttu=1)
  kupon tutma   = bir kuponun (tarih,pist,seq,config) 6 ayağından KAÇINI tuttu (0-6)
  tam 6/6       = Altılı'nın PARA ÖDEYEN tek eşiği (K52; 5/4/3 teselli VARSAYIM, kesin değil)

İSTATİSTİKSEL YÖNTEM: ayak-düzeyi ve kupon-düzeyi karşılaştırmalar OLAY-BOOTSTRAP (4.000
tekrar) ile %95 GA. Kupon sayısı azsa (n<15) GA çok geniş çıkar -> "gürültü" etiketiyle
işaretlenir (K138'in dersi: birkaç kupona bakıp yön okumak sinyal-gürültü karışıklığıdır).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
import altili_canli as AC                                            # noqa: E402

BOOT = 4000
RNG = np.random.default_rng(20260902)
SON_GUN = 14


def yukle():
    d = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    d = d[d["tuttu"].notna()].copy()
    d["tuttu"] = d["tuttu"].astype(int)
    d["tarih_dt"] = pd.to_datetime(d["tarih"], format="%Y-%m-%d", errors="coerce")
    return d


def boot_fark(a, b, n=BOOT):
    """iki bagimsiz orneklemin ORTALAMA farki icin %95 GA (olay-bootstrap)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2:
        return float("nan"), float("nan"), float("nan")
    ba = a[RNG.integers(0, len(a), size=(n, len(a)))].mean(1)
    bb = b[RNG.integers(0, len(b), size=(n, len(b)))].mean(1)
    d = bb - ba
    return float(d.mean()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def main():
    aktif = [c for c, a in AC.KONFIG.items() if a.get("aktif")]
    print("=" * 108)
    print("K140 — TÜM AKTİF KUPON TÜRLERİ: ayak + kupon istatistiği, son 14 gün vs öncesi")
    print(f"Aktif config (altili_canli.KONFIG'den okundu): {', '.join(aktif)}")
    print("=" * 108)

    d = yukle()
    son_tarih = d["tarih_dt"].max()
    esik = son_tarih - pd.Timedelta(days=SON_GUN - 1)
    print(f"veri aralığı: {d['tarih'].min()} .. {d['tarih'].max()}  ·  "
          f"'son {SON_GUN} gün' eşiği: {esik.date()} ve sonrası\n")

    d = d[d["config"].isin(aktif)].copy()
    d["donem"] = np.where(d["tarih_dt"] >= esik, "son14", "öncesi")

    # ---------------------------- (A) AYAK DÜZEYİ — genel sicil -----------------------
    print("-" * 108)
    print("(A) AYAK İSABETİ — TÜM SİCİL (config bazında, KONFIG sırasıyla)")
    print("-" * 108)
    print(f"  {'config':>15} {'aile':>8} {'ayak(n)':>8} {'isabet':>8} {'oran':>8}   "
          f"{'öncesi n/oran':>16}   {'son14 n/oran':>16}   {'fark (pp)':>12}   {'%95 GA':>20}")
    ozet_ayak = {}
    for c in aktif:
        g = d[d["config"] == c]
        n, hit = len(g), int(g["tuttu"].sum())
        oran = hit / n if n else float("nan")
        ozet_ayak[c] = (n, hit, oran)
        onc = g[g["donem"] == "öncesi"]["tuttu"].to_numpy()
        son = g[g["donem"] == "son14"]["tuttu"].to_numpy()
        fo = onc.mean() * 100 if len(onc) else float("nan")
        fs = son.mean() * 100 if len(son) else float("nan")
        m, lo, hi = boot_fark(onc, son)
        gurultu = " (az veri)" if min(len(onc), len(son)) < 60 else ""
        ga = f"[{100*lo:+.1f},{100*hi:+.1f}]pp{gurultu}" if not np.isnan(m) else "—"
        print(f"  {c:>15} {AC.KONFIG[c]['aile']:>8} {n:>8,} {hit:>8,} {100*oran:>7.1f}%   "
              f"{len(onc):>4}/{fo:>6.1f}%      {len(son):>4}/{fs:>6.1f}%      "
              f"{100*m:>+9.1f}pp   {ga:>20}")

    # ---------------------------- (B) KUPON DÜZEYİ — genel sicil -----------------------
    print("\n" + "-" * 108)
    print("(B) KUPON TUTMA — kupon başına 6 ayaktan kaçı tuttu (kupon = tarih·pist·seq·config)")
    print("-" * 108)
    kup = (d.groupby(["tarih", "pist", "seq", "config", "donem"], as_index=False)
            .agg(ayak_n=("tuttu", "size"), ayak_tut=("tuttu", "sum")))
    kup["tam6"] = ((kup["ayak_n"] == 6) & (kup["ayak_tut"] == 6)).astype(int)
    print(f"  {'config':>15} {'kupon':>7} {'ort.ayak/kupon':>15} {'6/6 sayı':>9} {'6/6 oran':>9}  "
          f"{'dağılım (0..6 ayak tutan kupon sayısı)':>50}")
    for c in aktif:
        g = kup[kup["config"] == c]
        n = len(g)
        dagilim = g["ayak_tut"].value_counts().reindex(range(7), fill_value=0)
        dstr = " ".join(f"{i}:{int(dagilim[i])}" for i in range(7))
        print(f"  {c:>15} {n:>7,} {g['ayak_tut'].mean():>15.3f} {int(g['tam6'].sum()):>9} "
              f"{100*g['tam6'].mean():>8.1f}%  {dstr}")

    # ---------------------------- (C) KUPON DÜZEYİ — son14 vs öncesi -------------------
    print("\n" + "-" * 108)
    print("(C) KUPON TUTMA — son 14 gün vs öncesi (birincil kıyas ölçütü, ROI DEĞİL — K122 dersi)")
    print("-" * 108)
    print(f"  {'config':>15} {'öncesi n/ort.ayak':>19} {'son14 n/ort.ayak':>18} "
          f"{'fark (ayak/kupon)':>18} {'%95 GA':>22}   hüküm")
    for c in aktif:
        g = kup[kup["config"] == c]
        onc = g[g["donem"] == "öncesi"]["ayak_tut"].to_numpy()
        son = g[g["donem"] == "son14"]["ayak_tut"].to_numpy()
        m, lo, hi = boot_fark(onc, son)
        gurultu = min(len(onc), len(son)) < 15
        if np.isnan(m):
            hkm = "veri yok"
        elif hi < 0:
            hkm = "DÜŞÜŞ (GA sıfırın altında)" + (" — ama az kupon, temkinli" if gurultu else "")
        elif lo > 0:
            hkm = "ARTIŞ (GA sıfırın üstünde)" + (" — ama az kupon, temkinli" if gurultu else "")
        else:
            hkm = "fark yok (GA sıfırı içeriyor)"
        oo = onc.mean() if len(onc) else float("nan")
        so = son.mean() if len(son) else float("nan")
        print(f"  {c:>15} {f'{len(onc)}/{oo:.2f}':>19} {f'{len(son)}/{so:.2f}':>18} "
              f"{m:>+18.3f} [{lo:>+7.3f},{hi:>+7.3f}]   {hkm}")

    # ---------------------------- (D) HAVUZ — tüm aktif configler birleşik -------------
    print("\n" + "-" * 108)
    print("(D) TÜM AKTİF CONFIGLER BİRLEŞİK (ağırlıksız havuz) — son14 vs öncesi")
    print("-" * 108)
    onc_ayak = d[d["donem"] == "öncesi"]["tuttu"].to_numpy()
    son_ayak = d[d["donem"] == "son14"]["tuttu"].to_numpy()
    m, lo, hi = boot_fark(onc_ayak, son_ayak)
    print(f"  AYAK isabeti   : öncesi {onc_ayak.mean()*100:.1f}% (n={len(onc_ayak):,}) -> "
          f"son14 {son_ayak.mean()*100:.1f}% (n={len(son_ayak):,})   "
          f"fark {100*m:+.1f}pp  GA [{100*lo:+.1f},{100*hi:+.1f}]pp")
    onc_kup = kup[kup["donem"] == "öncesi"]["ayak_tut"].to_numpy()
    son_kup = kup[kup["donem"] == "son14"]["ayak_tut"].to_numpy()
    m2, lo2, hi2 = boot_fark(onc_kup, son_kup)
    print(f"  KUPON ort.ayak : öncesi {onc_kup.mean():.3f} (n={len(onc_kup):,}) -> "
          f"son14 {son_kup.mean():.3f} (n={len(son_kup):,})   "
          f"fark {m2:+.3f}  GA [{lo2:+.3f},{hi2:+.3f}]")
    print(f"  6/6 oranı      : öncesi {100*(onc_kup==6).mean():.1f}% -> "
          f"son14 {100*(son_kup==6).mean():.1f}%")

    print("\n" + "=" * 108)
    print("HİÇBİR DOSYAYA YAZILMADI. Bu bir teşhis raporudur, hüküm ROI'den değil AYAK/KUPON")
    print("isabetinden çıkarılmıştır (K122: ham ROI 6/6 varyansıyla savrulur, kıyasa elverişsiz).")
    print("=" * 108)


if __name__ == "__main__":
    main()
