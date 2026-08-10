"""
kayip_raporu.py — K82: "PC kapaliyken NE KAYBETTIK?" gunluk hasar raporu.
OFFLINE, SALT-OKUNUR: canliya DOKUNMAZ, hicbir dosyaya YAZMAZ, kupon kurmaz.

NEDEN VAR: kullanici bazi gunler ~15:30 civari yarim saat PC'yi kapatmak zorunda. Takip
15 dk'da bir gectigi icin kesinti UC ayri hasar yapabilir ve ucu de SESSIZ:

  1) KURULMAYAN ALTILI (en pahali). Kupon yalnizca 1. kosuya <=30 dk kala kurulur
     (altili_canli.kupon_zamani_kur). O 30 dk'lik pencereye iki gecis duser; ikisi de
     kacarsa o Altili HIC kurulmaz -> AKTIF config sayisi kadar kupon birden ve o Altili
     deneyden duser (sayi KONFIG'den okunur, elle yazilmaz -- K100).
     Olcum: 15:00 gunun en yogun kupon anidir (12 gunun 9'unda), 15:30/15:45'te hic
     kupon kurulmamistir -> kesintiyi 15:30'da baslatmak bu hasari sifirlar.

  2) GEC KURULAN KUPON (en sinsi). Kesinti pencereye KISMEN denk gelirse kupon kaybolmaz,
     GEC kurulur (or. 30 dk yerine 5 dk kala). Kupon var gorunur ama aslinda FARKLI bir
     deneydir; BEKLEYENLER #4 tam olarak "30 dk mi 15 dk mi" sorusudur -> kirlenmis
     zamanlamalar o olcumu bozar. kayit_ts kayitli oldugu icin tespit edilebilir.

  3) DUSEN DEFTER KAYDI (en ucuz). Bir kosu deftere ancak takip [posta-5dk, posta+3dk]
     araliginda gecerse yazilir; kacarsa "gecmis" diye muhurlenir ve BIR DAHA DENENMEZ.
     Kupon/isabet/kar-zarar bozulmaz (sonuclandirma sonuc feed'inden gelir) ama o ayagin
     siralamasi sayfada gorunmez VE o kosu lambda olcumunden duser (altili_suruklenme
     bot1'i ve posta oranini defter'den alir).

KAYNAKLAR (hepsi salt-okunur): altili_temettu.csv (hangi Altili GERCEKTEN kostu),
altili_kupon.csv (hangisine kupon kurduk + kayit_ts), defter.csv (kosu saati + kayit).

Elle:  python kayip_raporu.py [--gun 14]
"""
import sys
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))

# K100: "kac kupon kaybederiz" sayisi ELLE YAZILMAZ -- config sayisi degistikce bayatlar
# (K78 dersi). Tek kaynak altili_canli.KONFIG'in aktif bayragidir. Import edilemezse
# rapor yine calisir, yalniz sayi yerine "tum" yazar.
try:
    from altili_canli import aktif_konfig
    AKTIF_SAYI = len(aktif_konfig())
except Exception:                                            # noqa: BLE001
    AKTIF_SAYI = None
KUPON_ADET = f"{AKTIF_SAYI} kupon" if AKTIF_SAYI else "tum kuponlar"

KUPON_DK = 30    # altili_canli.kupon_zamani_kur varsayilani
GECIS_DK = 15    # takip gecis araligi -> normal kurulum farki [15, 30] dk arasi olmali
ASGARI_FARK = GECIS_DK   # bundan kucukse en az bir gecis kacmis demektir


def _oku(ad, **kw):
    p = KOK / "veri" / ad
    return pd.read_csv(p, **kw) if p.exists() else pd.DataFrame()


def main(gun=14):
    tem = _oku("altili_temettu.csv")
    kup = _oku("altili_kupon.csv")
    dft = _oku("defter.csv", low_memory=False)
    if kup.empty:
        print("altili_kupon.csv yok."); return

    kup = kup.sort_values("kayit_ts").drop_duplicates(
        ["tarih", "pist", "seq", "config", "ayak"], keep="last")
    for c in ("seq", "ayak", "race_kod"):
        kup[c] = pd.to_numeric(kup[c], errors="coerce")
    dft["race_kod"] = pd.to_numeric(dft["race_kod"], errors="coerce")

    # race_kod -> posta saati (defter birincil; oran_log yedek)
    saat = {}
    for r in dft.dropna(subset=["race_kod"]).itertuples():
        saat.setdefault(int(r.race_kod), str(getattr(r, "saat", "") or "").strip())
    ol = _oku("altili_oran_log.csv")
    if not ol.empty:
        ol["race_kod"] = pd.to_numeric(ol["race_kod"], errors="coerce")
        for r in ol.dropna(subset=["race_kod"]).itertuples():
            saat.setdefault(int(r.race_kod), str(getattr(r, "saat", "") or "").strip())
    defter_var = set(dft["race_kod"].dropna().astype(int))

    kuruldu = set(zip(kup.tarih, kup.pist, kup.seq.astype("Int64")))
    kostu = set()
    if not tem.empty:
        tem["seq"] = pd.to_numeric(tem["seq"], errors="coerce")
        kostu = set(zip(tem.tarih, tem.pist, tem.seq.astype("Int64")))

    gunler = sorted(set(kup.tarih) | {t for t, _, _ in kostu})[-gun:]

    print("=" * 94)
    print("GUNLUK HASAR RAPORU — 'PC kapaliyken ne kaybettik?'  (offline, salt-okunur)")
    print("=" * 94)

    t_kurulmayan = t_gec = t_defter = t_elle = 0
    temiz = 0
    for g in gunler:
        satir = []
        # 1) kurulmayan Altili
        eksik = sorted([(p, int(s)) for (t, p, s) in kostu
                        if t == g and (t, p, s) not in kuruldu])
        for p, s in eksik:
            satir.append(f"    !! KURULMAYAN ALTILI: {p} {s}. Altili — kupon penceresi kacmis "
                         f"({KUPON_ADET} + o Altili deneyden dustu)")
        t_kurulmayan += len(eksik)

        # 2) gec kurulan kupon (1. ayagin postasi ile kayit_ts farki)
        gk = kup[(kup.tarih == g) & (kup.ayak == 1)].drop_duplicates(["pist", "seq"])
        for r in gk.itertuples():
            rk = int(r.race_kod) if pd.notna(r.race_kod) else None
            sa = saat.get(rk, "")
            if not sa or ":" not in sa:
                continue
            try:
                post = pd.Timestamp(f"{g} {sa}")
                kurdu = pd.Timestamp(str(r.kayit_ts))
            except ValueError:
                continue
            fark = (post - kurdu).total_seconds() / 60.0
            if fark < 0:
                # Negatif = kupon 1. kosu BASLADIKTAN sonra kaydedilmis. Bu bir kesinti
                # hasari DEGIL; 20 Tem'de elle/geriye donuk girilen kuponlar boyle gorunur.
                # Ayri sayilir, yoksa kesinti istatistigini kirletir.
                t_elle += 1
                satir.append(f"    ~  YARIS SONRASI KAYIT: {r.pist} {int(r.seq)}. Altili — "
                             f"1. kosudan {-fark:.0f} dk SONRA kaydedilmis "
                             f"(elle/geriye donuk; canli deneyin parcasi degil)")
            elif fark < ASGARI_FARK:
                t_gec += 1
                satir.append(f"    !  GEC KURULDU: {r.pist} {int(r.seq)}. Altili — 1. kosuya "
                             f"{fark:.0f} dk kala kuruldu (normal 15-30 dk) "
                             f"-> ZAMANLAMA KIRLENMESI, BEKLEYENLER #4'u etkiler")

        # 3) defter kaydi dusen kosu
        gl = kup[kup.tarih == g].drop_duplicates(["pist", "seq", "ayak"])
        dus = sorted({int(r.race_kod) for r in gl.itertuples()
                      if pd.notna(r.race_kod) and int(r.race_kod) not in defter_var})
        if dus:
            t_defter += len(dus)
            satir.append(f"    .  DEFTER KAYDI YOK: {len(dus)} kosu {dus} "
                         f"-> siralama gorunmez + lambda olcumunden duser")

        if satir:
            print(f"\n  {g}")
            for s in satir:
                print(s)
        else:
            temiz += 1

    print("\n" + "=" * 94)
    print(f"OZET ({len(gunler)} gun): {temiz} gun TEMIZ")
    print(f"  kurulmayan Altili : {t_kurulmayan:>3d}   (en pahali — {KUPON_ADET}/Altili)")
    print(f"  gec kurulan kupon : {t_gec:>3d}   (en sinsi — zamanlama kirlenmesi)")
    print(f"  yaris sonrasi kayit: {t_elle:>2d}   (elle/geriye donuk — kesinti hasari DEGIL)")
    print(f"  defter kaydi dusen: {t_defter:>3d} kosu (en ucuz — yalniz siralama+lambda)")
    print("=" * 94)
    print("HATIRLATMA: kupon anlari 12:30-18:31 bandinda; 15:00 en yogun (12 gunun 9'unda).")
    print("15:30-15:45'te bugune kadar HIC kupon kurulmadi -> zorunlu kesinti icin en guvenli")
    print("saat 15:30. Kesinti 10:30 oncesi / 22:30 sonrasi ise maliyet SIFIR.")
    print("\nNot: 'kurulmayan Altili' altili_temettu.csv'ye gore bulunur; o dosyada eksik olan")
    print("bir Altili burada da gorunmez (yani bu sayi ALT SINIR'dir).")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--gun", type=int, default=14, help="son kac gun")
    main(ap.parse_args().gun)
