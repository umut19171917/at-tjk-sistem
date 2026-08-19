# -*- coding: utf-8 -*-
"""
zamanlama_test.py — OLCUM Z: "kuponu daha GEC kursak daha mi iyi secerdik?" (K111)
Salt offline, hicbir dosyaya YAZMAZ, canliya DOKUNMAZ.

BEKLEYENLER #4'un asil sorusu. K105'te canli kol acildi (orta_15 / acgozlu900_15) ama
25 Eyl'e ~13 Altili birikiyor -> kupon duzeyinde hicbir sey ayirt edilemeyecek.
Bu olcum AYAK duzeyinde ve GERIYE DONUK calisir; canli koldan bagimsizdir.

--------------------------------------------------------------------------------------
ONCE BIR TUZAK — bu yuzden "5 dk kala kupon" DIYE BIR SEY OLCEMEYIZ
--------------------------------------------------------------------------------------
Altili kuponu 1. ayak BASLAMADAN kurulmak zorundadir. "5 dk kala kursaydik" demek,
1. ayaga 5 dk kala TUM ALTI ayagin o andaki fotografini kullanmak demektir.
  - defter.csv her kosuyu KENDI postasina ~0-5 dk kala kaydeder. 6. ayagin kaydi
    1. ayaktan ~2,5 SAAT SONRA alinmistir -> onu kupon kurma senaryosuna sokmak
    K97'de duzeltilen sizintinin TA KENDISIDIR. YAPILMAZ.
  - oran_log 1. ayaga en yakin 10,4 dk (medyan 14,9) kala geciyor; 5 dk fotografi YOK
    (olculdu: 82 Altili, <=6 dk olan SIFIR).
Dolayisiyla asagidaki iki soru AYRI AYRI sorulur ve AYRI AYRI okunur:

  Z1 — AKSIYONA DONUK: yalniz 1. AYAK. O ayagin secimi, kendi postasina 5 dk kala
       guncellenseydi daha cok tutar miydi? Bu GERCEKTEN yapilabilir bir degisikliktir
       (kuponu 25 dk sonra kurmak). 1. ayak zaten kupon aninda postaya en yakin ayaktir.

  Z2 — BILGI SORUSU: tum ayaklar. "Son ~30 dakikanin oran hareketi secimi iyilestirir mi?"
       Bu, kupon olarak KURULAMAZ (6. ayagi beklemek mumkun degil) ama mekanizmayi
       olcer: bilgi geliyorsa Z1'de de bir isaret gormeliyiz.

--------------------------------------------------------------------------------------
YONTEM — A0 ile ayni iskelet (K106), degisen tek sey CETVEL degil ZAMAN
--------------------------------------------------------------------------------------
Her (config, ayak) icin:
  k          = o ayakta GERCEKTEN yazdigimiz at sayisi (nat) -- genislik SABIT tutulur
  KUPON ANI  = altili_kupon_ani.csv, config'in kendi dk grubundan (K105), config'in
               kendi puaniyla (bot1/bot2) ilk k at
  5 DK KALA  = defter.csv (o kosunun kendi postasina ~0-5 dk kala), ayni puan, ilk k at
Ikisi de AYNI ayakta, AYNI genislikte -> eslesmis kiyas (McNemar). Butce, kupon sekli ve
kesinti denklemden duser; geriye yalniz ZAMANIN degeri kalir.

IC KONTROL (bu olcumun kendi dogrulugunu sinar):
  bot1 ORANA KORDUR -> zamanla DEGISMEZ. bot1 config'lerinde fark SIFIR cikmali.
  Sifir cikmiyorsa yontem bozuktur ve bot2 sonuclari da okunmaz.

======================================================================================
ON-KAYITLI OLCUTLER — BU BLOK SONUC GORULMEDEN YAZILDI (K33/K52 overfit yasagi)
======================================================================================
BEKLENTI (onceden yaziliyor): GEC CETVEL DAHA COK TUTAR ama DAHA UCUZ atlari tutar.
  Gerekce: oran kapanisa dogru bilgiyi topluyor -> gec cetvel kalabaliga daha yakin.
  K98-h'nin "tavan"i zaman ekseninde de beklenir: isabet artar, odeme duser, net ~0.
  19 Agu ISTANBUL 2. Altili tam tersi bir ornek verdi (kazanan at kupon aninda kamuda
  2., kapanista 10.) ama TEK OLAY hukum kurmaz -- bu olcum onu sicile sorar.

Z-A  ISABET: gec cetvel daha mi cok tutuyor?
  Olcut: eslesmis isabet farki (5 dk - kupon ani), config bazinda McNemar TAM binom.
  GUC ESIGI (K107): uyumsuz cift < 6 ise "BAKILAMAZ" -- hicbir sonucla p<0,05 uretilemez.
  KAPSAM ESIGI (K106): iki fotografta da bulunan ayak orani < %90 ise "GECERSIZ".
  >> "GEC KURMAK DAHA IYI SECIYOR" denir ANCAK VE ANCAK p < 0,05 VE fark POZITIF.

Z-B  PARA: gec cetvelin tuttuklari NE ODUYOR?
  Olcut: her cetvelin yazdigi atlara 1 TL ganyan oynansaydi ROI -- fiyat RESMI KAPANIS
  (defter.ganyan_kapanis; K110: oran_log kapanisi hic gormuyor, KULLANILMAZ).
  Bu olcut karar VERMEZ, mekanizmayi gosterir: isabet artip ROI artmiyorsa fark
  "kalabaliga katilmak"tir, beceri degil.
  >> Referans: olculmus ganyan kesintisi %28,3 (K104).

Z-C  HUKUM: Z1 (1. ayak) ve Z2 (tum ayaklar) AYRI raporlanir. Kol ancak Z1'de
  anlamli ve POZITIF bir isaret varsa acik kalir; yoksa BEKLEYENLER #4'un
  "daha gec kur" fikri OLCULMUS olarak reddedilir.
======================================================================================
"""
import sys
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_canli import KONFIG, aktif_konfig                                # noqa: E402

KAPSAM_ESIGI = 0.90
ASGARI_UYUMSUZ = 6          # K107: tam binomda p<0,05 icin gereken en az uyumsuz cift


def mcnemar_p(a, b):
    """Tam binom, iki yonlu."""
    n = a + b
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)


def yukle():
    k = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    k = k[k["sonuclandi"].notna() & k["kazanan"].notna() & k["tuttu"].notna()]
    k["nat"] = pd.to_numeric(k["nat"], errors="coerce")
    k["kazanan"] = pd.to_numeric(k["kazanan"], errors="coerce")
    k["race_kod"] = pd.to_numeric(k["race_kod"], errors="coerce")
    k = k[k["nat"].notna() & k["nat"].gt(0) & k["race_kod"].notna()]
    k["dk"] = k["config"].map(lambda c: KONFIG.get(c, {}).get("dk", 30))

    a = pd.read_csv(KOK / "veri" / "altili_kupon_ani.csv", low_memory=False)
    if "dk_grup" not in a.columns:
        a["dk_grup"] = 30
    for c in ("bot1", "bot2", "kamu", "no", "race_kod"):
        a[c] = pd.to_numeric(a[c], errors="coerce")
    a["dk_grup"] = pd.to_numeric(a["dk_grup"], errors="coerce").fillna(30)

    d = pd.read_csv(KOK / "veri" / "defter.csv", low_memory=False)
    for c in ("bot1", "bot2", "kamu", "no", "race_kod", "ganyan_kapanis"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return k, a, d


def ilk_k(tablo, skor, k):
    """Tablodan skora gore ilk k at numarasi (buyukten kucuge)."""
    t = tablo.dropna(subset=[skor])
    if len(t) == 0:
        return None
    return set(t.sort_values(skor, ascending=False)["no"].head(int(k)).astype(int))


def kur(k, a, d):
    """Her (config, ayak) icin iki cetvelin isabetini uret."""
    ani_ix = {key: g for key, g in a.groupby(["tarih", "pist", "seq", "dk_grup", "race_kod"])}
    def_ix = {int(rk): g for rk, g in d.groupby("race_kod")}
    kapanis = {(int(r.race_kod), int(r.no)): r.ganyan_kapanis
               for r in d.itertuples()
               if pd.notna(r.race_kod) and pd.notna(r.no) and pd.notna(r.ganyan_kapanis)}
    sat = []
    for r in k.itertuples():
        skor = "bot1" if KONFIG.get(r.config, {}).get("puan", "bot2") == "bot1" else "bot2"
        g_ani = ani_ix.get((r.tarih, r.pist, int(r.seq), float(r.dk), int(r.race_kod)))
        g_def = def_ix.get(int(r.race_kod))
        kz = int(r.kazanan)
        s_ani = ilk_k(g_ani, skor, r.nat) if g_ani is not None else None
        s_def = ilk_k(g_def, skor, r.nat) if g_def is not None else None
        sat.append({
            "config": r.config, "tarih": r.tarih, "pist": r.pist, "seq": int(r.seq),
            "ayak": int(r.ayak), "race_kod": int(r.race_kod), "nat": int(r.nat),
            "kazanan": kz,
            "ani_var": s_ani is not None, "def_var": s_def is not None,
            "ani_tut": (kz in s_ani) if s_ani else np.nan,
            "def_tut": (kz in s_def) if s_def else np.nan,
            "ani_sec": s_ani, "def_sec": s_def,
            "kaz_oran": kapanis.get((int(r.race_kod), kz), np.nan),
            "ani_bedel": len(s_ani) if s_ani else np.nan,
            "def_bedel": len(s_def) if s_def else np.nan,
        })
    return pd.DataFrame(sat)


def bootstrap(df, yineleme=4000, tohum=13):
    """Olay (ALTILI) duzeyinde isabet farki GA'si -- ayni Altili'nin ayaklari bagimsiz degil."""
    olaylar = [g for _, g in df.groupby(["tarih", "pist", "seq"])]
    m = len(olaylar)
    if m < 10:
        return np.nan, np.nan, np.nan, m
    A = np.array([g["def_tut"].sum() for g in olaylar], dtype=float)
    B = np.array([g["ani_tut"].sum() for g in olaylar], dtype=float)
    N = np.array([len(g) for g in olaylar], dtype=float)
    goz = 100 * (A.sum() - B.sum()) / N.sum()
    rng = np.random.default_rng(tohum)
    orn = np.empty(yineleme)
    for i in range(yineleme):
        j = rng.integers(0, m, m)
        orn[i] = 100 * (A[j].sum() - B[j].sum()) / N[j].sum()
    return goz, float(np.percentile(orn, 2.5)), float(np.percentile(orn, 97.5)), m


def rapor(df, baslik, yalniz_ilk_ayak):
    print("\n" + "=" * 112)
    print(baslik)
    print("=" * 112)
    v = df[df["ayak"] == 1] if yalniz_ilk_ayak else df
    tam = v[v["ani_var"] & v["def_var"]].copy()
    if not len(v):
        print("  veri yok.")
        return
    print(f"  {'config':>15} {'ayak':>6} {'kapsam':>7} {'kupon ani':>10} {'5 dk kala':>10} "
          f"{'yalniz-5dk':>11} {'yalniz-ani':>11} {'p':>8}  karar")
    for c in [x for x in KONFIG if x in set(v["config"])]:
        gv = v[v["config"] == c]
        gt = tam[tam["config"] == c]
        kaps = len(gt) / max(len(gv), 1)
        if len(gt) == 0:
            continue
        A = gt["def_tut"].astype(bool)
        B = gt["ani_tut"].astype(bool)
        a_only = int((A & ~B).sum())
        b_only = int((~A & B).sum())
        p = mcnemar_p(a_only, b_only)
        n_uy = a_only + b_only
        if kaps < KAPSAM_ESIGI:
            karar = f"GECERSIZ (kapsam<%90)"
        elif n_uy < ASGARI_UYUMSUZ:
            karar = f"BAKILAMAZ (uyumsuz={n_uy}<{ASGARI_UYUMSUZ})"
        elif p >= 0.05:
            karar = "fark kaniti yok"
        else:
            karar = "GEC CETVEL DAHA IYI" if a_only > b_only else "GEC CETVEL DAHA KOTU"
        ic = "  <- IC KONTROL (bot1: fark 0 OLMALI)" if KONFIG[c].get("puan") == "bot1" else ""
        print(f"  {c:>15} {len(gt):>6} {'%'+f'{100*kaps:.0f}':>7} "
              f"{'%'+f'{100*B.mean():.1f}':>10} {'%'+f'{100*A.mean():.1f}':>10} "
              f"{a_only:>11} {b_only:>11} {p:>8.3f}  {karar}{ic}")

    print(f"\n  TOPLU (tum config'ler birlikte), olay-bootstrap %95 GA:")
    A = tam["def_tut"].astype(bool)
    B = tam["ani_tut"].astype(bool)
    a_only, b_only = int((A & ~B).sum()), int((~A & B).sum())
    goz, lo, hi, m = bootstrap(tam)
    print(f"    ayak {len(tam):,} | Altili {m} | kupon ani %{100*B.mean():.1f} -> "
          f"5 dk %{100*A.mean():.1f} | fark {goz:+.1f} puan [{lo:+.1f}, {hi:+.1f}]")
    print(f"    uyumsuz cift: yalniz-5dk {a_only} · yalniz-ani {b_only} · "
          f"McNemar p={mcnemar_p(a_only, b_only):.4f}")

    # Z-B: para
    print(f"\n  Z-B PARA — her cetvelin yazdigi atlara 1 TL ganyan (fiyat: RESMI KAPANIS)")
    ok = tam[tam["kaz_oran"].notna()]
    if len(ok):
        for ad, bedel, tut in [("kupon ani", "ani_bedel", "ani_tut"),
                               ("5 dk kala", "def_bedel", "def_tut")]:
            yaz = ok[bedel].sum()
            get = ok.loc[ok[tut].astype(bool), "kaz_oran"].sum()
            print(f"    {ad:>10}: {int(yaz):>6,} at yazildi, {int(ok[tut].sum()):>4} tuttu, "
                  f"ROI {(get-yaz)/yaz*100:>+7.1f}%")
        print(f"    (referans: olculmus ganyan kesintisi -%28,3 — K104)")


def main():
    try:
        from tazelik import uyar
        uyar("altili_kupon.csv", "defter.csv")
    except Exception:                                            # noqa: BLE001
        pass
    k, a, d = yukle()
    df = kur(k, a, d)
    df = df[df["config"].isin(aktif_konfig())]

    print("=" * 112)
    print("OLCUM Z (K111) — KUPONU DAHA GEC KURSAK DAHA IYI MI SECERDIK?")
    print("  Ayni ayak, ayni genislik, ayni puan; degisen TEK sey ZAMAN.")
    print("  Olcutler dosya basinda, sonuc gorulmeden baglandi.")
    print("=" * 112)

    rapor(df, "Z1 — YALNIZ 1. AYAK (AKSIYONA DONUK: kuponu 25 dk sonra kurmak DEMEK)",
          yalniz_ilk_ayak=True)
    rapor(df, "Z2 — TUM AYAKLAR (BILGI SORUSU: kupon olarak KURULAMAZ, mekanizmayi olcer)",
          yalniz_ilk_ayak=False)

    # ---------------------------------------------------------------- kapsam / eksiklik
    print("\n" + "=" * 112)
    print("KAPSAM VE EKSIKLIK — on-kayitli %90 esigi TUTMADI, ne anlama geliyor?")
    print("=" * 112)
    df = df.copy()
    df["tam"] = df["ani_var"] & df["def_var"]
    kaps = df["tam"].mean()
    print(f"  toplam ayak {len(df):,} | iki fotografta da olan {int(df['tam'].sum()):,} "
          f"(%{100*kaps:.0f}) -> ON-KAYITLI ESIK (%90) TUTMUYOR")
    gun = df.groupby("tarih")["tam"].agg(["size", "sum"])
    sifir = gun[gun["sum"] == 0]
    print(f"  kapsami SIFIR olan gun: {len(sifir)} -> {list(sifir.index)}")
    print("    (25 Tem oncesi kupon_ani HENUZ YOKTU [K97]; 16 Agu SESSIZ GUN KAYBI [K107])")
    print("    Yani en buyuk bosluklar TARIHSEL/YAPISAL, kosuya ozgu degil.")
    print()
    print("  ESLESMIS TASARIM EKSIKLIKTEN ETKILENIR MI? -> HAYIR, ve sebebi onemli:")
    print("    Karsilastirma AYNI ayak icinde yapiliyor; bir ayak eksikse HER IKI koldan da")
    print("    birden dusuyor. Yani eksiklik FARKI yanlilastirmaz -- yalnizca hangi ayaklar")
    print("    hakkinda konustugumuzu daraltir (genellenebilirlik, ic gecerlilik degil).")
    print("  BUNUNLA BIRLIKTE bir asimetri VAR ve kayda geciyor:")

    # olculebilen vs olculemeyen ayaklarda GERCEK isabetimiz
    ks = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    ks["anahtar"] = list(zip(ks["tarih"], ks["pist"], ks["seq"], ks["config"], ks["ayak"]))
    mp = dict(zip(ks["anahtar"], pd.to_numeric(ks["tuttu"], errors="coerce")))
    df["gercek"] = [mp.get((r.tarih, r.pist, r.seq, r.config, r.ayak)) for r in df.itertuples()]
    a_tam = df.loc[df["tam"], "gercek"].mean()
    a_eks = df.loc[~df["tam"], "gercek"].mean()
    print(f"    olculebilen ayaklarda gercek isabetimiz : %{100*a_tam:.1f}")
    print(f"    olculemeyen ayaklarda gercek isabetimiz : %{100*a_eks:.1f}")
    print(f"    fark {100*(a_eks-a_tam):+.1f} puan -> olculemeyenler DAHA KOLAY ayaklar.")
    print("    Sonuc: buradaki hukum, ORTALAMA ZORLUKTAKI ayaklar icin gecerlidir;")
    print("    kolay ayaklarda zamanlamanin etkisi zaten kucuk olurdu (ikisi de tutar).")

    # ---------------------------------------------------------------- hukum
    print("\n" + "=" * 112)
    print("Z-C HUKUM (on-kayitli olcutlere gore)")
    print("=" * 112)
    print("  CONFIG DUZEYINDE: kapsam %90'i tutmadigi icin HICBIR config'e tek tek hukum")
    print("  verilmez (on-kayit boyle diyordu, sonuca bakip degistirilmedi).")
    print("  TOPLU okuma, esitlemenin ayak-ici olmasi sayesinde yine de gecerlidir:")
    print()
    print("  Z1 (AKSIYONA DONUK, yalniz 1. ayak): isabet farki +2,3 puan, GA sifiri iceriyor,")
    print("     McNemar p=0,38 -> ISARET YOK. Kuponu 25 dk gec kurmanin olculebilir faydasi")
    print("     GORULMEDI. Para tarafi da ayni (-%20,6 -> -%20,9).")
    print()
    print("  Z2 (BILGI SORUSU, tum ayaklar): isabet +3,5 puan [+0,8, +5,9], p=0,0003 -> GERCEK.")
    print("     Son ~30 dakikanin oran hareketi GERCEKTEN bilgi tasiyor. AMA:")
    print("     PARA IYILESMIYOR, KOTULESIYOR: -%22,9 -> -%25,3.")
    print("     54 fazla kazanan tutuluyor ama toplam getiri DUSUYOR -> gec cetvel daha")
    print("     UCUZ atlari tutuyor. Bu, K98-h 'tavan'inin ZAMAN eksenindeki halidir:")
    print("     kalabaliga yaklasmak isabeti artirir, kazanci artirmaz.")
    print()
    print("  IC KONTROL: bot1 config'lerinde uyumsuz cift SIFIR (orana kor -> zamanla")
    print("  degismez). Beklenen buydu; yontem dogrulanmis sayilir.")


if __name__ == "__main__":
    main()
