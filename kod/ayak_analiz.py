# -*- coding: utf-8 -*-
"""
ayak_analiz.py — AKTIF CONFIG'LERIN AYAK (KOSU) DUZEYINDE DETAYLI SICILI (K109).
Salt-okunur; hicbir dosyaya yazmaz, canliya dokunmaz.

SORU (kullanici): "Altili tutmasi onemli degil — KOSU BAZINDA en basarili kuponlar
hangileri ve NEDEN? Istatistigini istiyorum."

NEDEN AYAK DUZEYI: kupon duzeyinde elde 4 adet 6/6 var, hicbir sey ayirt edilemez.
Ayak duzeyinde ~3.100 gozlem var. Ama HAM AYAK ISABETI YANILTICIDIR: genis kupon
her zaman daha cok tutar. O yuzden burada UC AYRI adil olcu kullanilir:

  1. HAM   : isabet / ayak            -> genisligi odullendirir, TEK BASINA OKUNMAZ
  2. ADIL  : ayni genislikte KAMU cetveli ne tuttururdu? (fark = SECIM becerisi)
  3. VERIM : bir isabet kac at yazmaya mal oldu? (at-basi isabet)

"NEDEN" tarafi icin kazananin kupon ANINDAKI kimligi cozulur (altili_kupon_ani.csv,
K97 — yaris ani verisiyle yargilamak sizinti olurdu):
  - kazanan, config'in KENDI siralamasinda kacinci atti?  -> genislik ise yariyor mu
  - kazanan, KAMU siralamasinda kacinciydi?               -> favori mi surpriz mi
  - kazananin orani hangi kovada?                         -> nerede para var
  - ayak pozisyonu (1-6) / saha buyuklugu                 -> zorluk yapisi

KAPSAM UYARISI: kupon-ani kaydi K97'de kuruldu; ondan onceki config'lerde eksik.
Her "neden" tablosunun basinda kapsam yuzdesi basilir; %90 altindaysa okuma serbest
ama karar baglanmaz (A0'in on-kayitli esigi).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_canli import aktif_konfig, KONFIG          # noqa: E402

KUPON = KOK / "veri" / "altili_kupon.csv"
ANI = KOK / "veri" / "altili_kupon_ani.csv"
KAPSAM_ESIGI = 0.90


def yukle():
    k = pd.read_csv(KUPON, low_memory=False)
    k = k[k["sonuclandi"].notna() & k["kazanan"].notna() & k["tuttu"].notna()]
    k = k[k["config"].isin(aktif_konfig())]
    k["nat"] = pd.to_numeric(k["nat"], errors="coerce")
    k["tuttu"] = pd.to_numeric(k["tuttu"], errors="coerce")
    k["kazanan"] = pd.to_numeric(k["kazanan"], errors="coerce")
    k = k[k["nat"].notna() & k["nat"].gt(0)]
    k["dk"] = k["config"].map(lambda c: KONFIG[c].get("dk", 30))

    a = pd.read_csv(ANI, low_memory=False)
    if "dk_grup" not in a.columns:
        a["dk_grup"] = 30
    a["dk_grup"] = pd.to_numeric(a["dk_grup"], errors="coerce").fillna(30)
    for s in ("bot1", "bot2", "kamu", "oran", "no"):
        a[s] = pd.to_numeric(a[s], errors="coerce")
    return k, a


def ani_indeks(a):
    """(tarih,pist,seq,dk_grup,race_kod) -> o kosunun kupon-anindaki tam tablosu."""
    ix = {}
    for anahtar, g in a.groupby(["tarih", "pist", "seq", "dk_grup", "race_kod"]):
        ix[anahtar] = g
    return ix


def satir_zenginlestir(k, ix):
    """Her ayak kaydina kupon-anindan turetilmis alanlari ekle."""
    kaz_kendi, kaz_kamu, kaz_oran, saha, pu = [], [], [], [], []
    for r in k.itertuples():
        skor = "bot1" if KONFIG[r.config].get("puan", "bot2") == "bot1" else "bot2"
        g = ix.get((r.tarih, r.pist, int(r.seq), float(r.dk), r.race_kod))
        if g is None or g[skor].isna().all():
            kaz_kendi.append(np.nan); kaz_kamu.append(np.nan)
            kaz_oran.append(np.nan); saha.append(np.nan); pu.append(skor)
            continue
        g = g.dropna(subset=[skor])
        s_kendi = g.sort_values(skor, ascending=False)["no"].tolist()
        s_kamu = g.sort_values("kamu", ascending=False)["no"].tolist()
        kz = r.kazanan
        kaz_kendi.append(s_kendi.index(kz) + 1 if kz in s_kendi else np.nan)
        kaz_kamu.append(s_kamu.index(kz) + 1 if kz in s_kamu else np.nan)
        o = g.loc[g["no"] == kz, "oran"]
        kaz_oran.append(float(o.iloc[0]) if len(o) and pd.notna(o.iloc[0]) else np.nan)
        saha.append(len(g))
        pu.append(skor)
    k = k.copy()
    k["kaz_kendi_sira"] = kaz_kendi      # kazanan, BIZIM siralamamizda kacinci
    k["kaz_kamu_sira"] = kaz_kamu        # kazanan, KAMU siralamasinda kacinci
    k["kaz_oran"] = kaz_oran
    k["saha"] = saha
    k["puan_kaynak"] = pu
    return k


def kamu_ayni_genislikte(k, ix):
    """ADIL KIYAS: ayni ayakta, ayni sayida at, ama KAMU cetvelinin ilk k'si tutar miydi?"""
    sonuc = []
    for r in k.itertuples():
        g = ix.get((r.tarih, r.pist, int(r.seq), float(r.dk), r.race_kod))
        if g is None or g["kamu"].isna().all():
            sonuc.append(np.nan)
            continue
        g = g.dropna(subset=["kamu"])
        ilk = g.sort_values("kamu", ascending=False)["no"].head(int(r.nat)).tolist()
        sonuc.append(1.0 if r.kazanan in ilk else 0.0)
    k = k.copy()
    k["kamu_tuttu"] = sonuc
    return k


def son_oran_ekle(k):
    """Kazananin ODENEN fiyati. K110 DUZELTMESI — kaynak sirasi degisti.

    K109'da bu fonksiyon altili_oran_log.csv'nin SON gozlemini "kapanisa en yakin" diye
    kullaniyordu. OLCULDU, YANLISMIS: takip 15 dk'da bir kostugu ve kosular :00/:30'a
    dustugu icin oran_log'un son fotografi SISTEMATIK olarak ~15 dk erken duruyor
    (374 kosu: medyan 14,9 dk kala, HICBIRI <=10 dk degil). O nokta ile gercek kapanis
    arasindaki fark kucuk degil: medyan +%12,7, atlarin %85'i >%10, %60'i >%25 oynuyor
    (5-95 persentil -%51 .. +%151).

    GERCEK KAPANIS ZATEN ELIMIZDE: defter.csv.ganyan_kapanis, sonuc feed'inden gelir ve
    %99 dolu. Musterek bahiste odenen fiyat BUDUR. Artik birincil kaynak o; defter'de
    olmayan (at,kosu) ciftlerinde oran_log'un son gozlemi YEDEK olarak kullanilir ve
    satir 'oran_log' diye isaretlenir ki karisim gorunur olsun."""
    k = k.copy()
    # 1) BIRINCIL: resmi kapanis (defter.csv)
    d = pd.read_csv(KOK / "veri" / "defter.csv", low_memory=False)
    for s in ("ganyan_kapanis", "no", "race_kod"):
        d[s] = pd.to_numeric(d[s], errors="coerce")
    d = d[d["ganyan_kapanis"].notna() & d["ganyan_kapanis"].gt(0)]
    kap = {(int(r.race_kod), int(r.no)): float(r.ganyan_kapanis)
           for r in d.itertuples() if pd.notna(r.race_kod) and pd.notna(r.no)}
    # 2) YEDEK: oran_log son gozlemi (kapanis DEGIL, ~15 dk erken)
    ol = pd.read_csv(KOK / "veri" / "altili_oran_log.csv", low_memory=False)
    for s in ("ganyan", "no", "dk_kala"):
        ol[s] = pd.to_numeric(ol[s], errors="coerce")
    ol = ol[ol["ganyan"].notna() & ol["ganyan"].gt(0) & ol["dk_kala"].notna()]
    son = ol.sort_values("dk_kala").groupby(["race_kod", "no"]).first()[["ganyan", "dk_kala"]]
    yed = {(rk, no): (g, dk) for (rk, no), (g, dk) in son.iterrows()}

    oran, dk_kala, kaynak = [], [], []
    for r in k.itertuples():
        rk, no = r.race_kod, r.kazanan
        if pd.isna(rk) or pd.isna(no):
            oran.append(np.nan); dk_kala.append(np.nan); kaynak.append("yok"); continue
        v = kap.get((int(rk), int(no)))
        if v is not None:
            oran.append(v); dk_kala.append(0.0); kaynak.append("kapanis")
            continue
        g, dkk = yed.get((rk, no), (np.nan, np.nan))
        oran.append(g); dk_kala.append(dkk)
        kaynak.append("oran_log" if pd.notna(g) else "yok")
    k["son_oran"] = oran
    k["son_dk"] = dk_kala
    k["oran_kaynak"] = kaynak
    return k


def b(baslik):
    print("\n" + "=" * 118)
    print(baslik)
    print("=" * 118)


def main():
    k, a = yukle()
    ix = ani_indeks(a)
    k = satir_zenginlestir(k, ix)
    k = kamu_ayni_genislikte(k, ix)
    kapsam = k["kaz_kendi_sira"].notna()

    print("=" * 118)
    print("K109 — AKTIF CONFIG'LERIN AYAK DUZEYINDE SICILI. Salt-okunur.")
    print(f"  sonuclanmis ayak: {len(k):,} | aktif config: {len(aktif_konfig())} | "
          f"kupon-ani kapsami: %{100*kapsam.mean():.0f}")
    print(f"  tarih: {k.tarih.min()} .. {k.tarih.max()}")
    print("=" * 118)

    # ---------------------------------------------------------------- 1
    b("1) UC OLCU YAN YANA — ham isabet yaniltir, adil ve verim ile birlikte okunur")
    print(f"  {'config':>15} {'ayak':>6} {'ort.genislik':>13} {'HAM isabet':>11} "
          f"{'ADIL: kamu ayni k':>18} {'FARK':>7} {'VERIM (at/isabet)':>18}")
    ozet = []
    for c, g in k.groupby("config"):
        gk = g[g["kamu_tuttu"].notna()]
        ham = g["tuttu"].mean()
        adil = gk["kamu_tuttu"].mean() if len(gk) else np.nan
        biz_ayni = gk["tuttu"].mean() if len(gk) else np.nan
        verim = g["nat"].sum() / max(g["tuttu"].sum(), 1)
        ozet.append((c, len(g), g["nat"].mean(), ham, adil, biz_ayni, verim, len(gk)))
    for c, n, gen, ham, adil, biz, ver, nk in sorted(ozet, key=lambda x: -x[3]):
        fark = (biz - adil) * 100 if pd.notna(adil) else np.nan
        fs = f"{fark:+6.1f}" if pd.notna(fark) else "     -"
        asr = f"%{100*adil:.1f} (n={nk})" if pd.notna(adil) else "-"
        print(f"  {c:>15} {n:>6} {gen:>13.2f} {'%'+f'{100*ham:.1f}':>11} {asr:>18} "
              f"{fs:>7} {ver:>18.2f}")
    print("\n  OKUMA: HAM isabeti genislik belirler -> tek basina KIYAS ARACI DEGILDIR.")
    print("  FARK = ayni ayakta ayni sayida atla bizim isabetimiz eksi kamunun isabeti.")
    print("  Bu, kupon seklinden ve butceden arinmis SECIM becerisidir (bkz. OLCUM A0/K106).")
    print("  VERIM = bir isabet icin kac at yazildi. Dusuk = ucuz isabet.")

    # ---------------------------------------------------------------- 2
    b("2) KAZANAN, BIZIM SIRALAMAMIZDA KACINCI ATTI? — genislik hak ediyor mu?")
    kk = k[kapsam]
    print(f"  (kapsam %{100*len(kk)/len(k):.0f}; yalniz kupon-ani kaydi olan ayaklar)")
    print(f"  {'config':>15} {'ayak':>6} " + " ".join(f"{f'{i}.':>6}" for i in range(1, 8))
          + f" {'8+':>6} {'>gen':>7}")
    for c, g in kk.groupby("config"):
        d = g["kaz_kendi_sira"]
        sat = []
        for i in range(1, 8):
            sat.append(f"{100*(d == i).mean():>5.1f}%")
        sat.append(f"{100*(d >= 8).mean():>5.1f}%")
        # kazanan yazdigimiz at sayisindan DAHA GERIDE miydi (yani kacirdik mi)
        kacir = (d > g["nat"]).mean()
        print(f"  {c:>15} {len(g):>6} " + " ".join(sat) + f" {100*kacir:>6.1f}%")
    print("\n  OKUMA: soldaki sutunlar 'kazanan bizim 1., 2., 3... tercihimizdi'. Saga kaydikca")
    print("  ayagi genis tutmak ISE YARAMIS demektir. '>gen' = kazanan yazdigimiz at sayisinin")
    print("  otesindeydi -> o ayagi KACIRDIK.")

    # ---------------------------------------------------------------- 3
    b("3) MARJINAL KATKI — n. ati eklemek ne kazandirdi, neye mal oldu?")
    print("  Butun aktif config'lerin ayaklari birlikte (kazanan sirasi dagilimindan).")
    d = kk["kaz_kendi_sira"].dropna()
    kum = 0.0
    print(f"  {'n. at':>7} {'bu at kazandirdi':>18} {'kumulatif isabet':>18} "
          f"{'kombo carpani':>15} {'marjinal verim':>16}")
    for i in range(1, 11):
        pay = (d == i).mean()
        onceki = kum
        kum += pay
        carpan = i / (i - 1) if i > 1 else 1.0
        # marjinal verim: isabet artis orani / maliyet artis orani
        mv = (kum / onceki) / carpan if onceki > 0 and i > 1 else np.nan
        mvs = f"{mv:>15.2f}" if pd.notna(mv) else "              -"
        print(f"  {i:>7} {100*pay:>17.1f}% {100*kum:>17.1f}% {carpan:>15.2f} {mvs}")
    print("\n  OKUMA: marjinal verim > 1 -> o ati eklemek isabeti maliyetinden HIZLI artirdi.")
    print("  < 1 -> o at parasini cikarmadi. (Tek ayak icin; kupon 6 ayagin carpimi oldugu")
    print("  icin gercek maliyet daha da agirdir.)")

    # ---------------------------------------------------------------- 4
    b("4) NE TUTTURUYORUZ, NE KACIRIYORUZ? — kazananin KAMU sirasina gore")
    print(f"  {'config':>15} " + " ".join(f"{'kamu ' + str(i) + '.':>11}" for i in range(1, 5))
          + f" {'kamu 5+':>11}")
    for c, g in kk.groupby("config"):
        sat = []
        for i in list(range(1, 5)) + ["5+"]:
            m = (g["kaz_kamu_sira"] >= 5) if i == "5+" else (g["kaz_kamu_sira"] == i)
            sub = g[m]
            sat.append(f"{100*sub['tuttu'].mean():>5.1f}% ({len(sub):>3})" if len(sub) else "     -     ")
        print(f"  {c:>15} " + " ".join(f"{s:>11}" for s in sat))
    print("\n  OKUMA: 'kamu 1.' = favori kazandi. Herkes tutar, temettu kucuk olur.")
    print("  'kamu 5+' = surpriz kazandi. Tutturmak zor ama temettu ORADA. Bir config'in")
    print("  degeri sag sutunlarda ayrisir; sol sutunda herkes iyidir.")

    # ---------------------------------------------------------------- 5
    b("5) AYAK POZISYONU — hangi kosu daha zor?")
    print(f"  {'config':>15} " + " ".join(f"{str(i)+'. ayak':>11}" for i in range(1, 7)))
    for c, g in k.groupby("config"):
        sat = [f"%{100*g[g.ayak == i]['tuttu'].mean():>4.1f}" if len(g[g.ayak == i]) else "   -"
               for i in range(1, 7)]
        print(f"  {c:>15} " + " ".join(f"{s:>11}" for s in sat))
    tum = k.groupby("ayak").agg(isabet=("tuttu", "mean"), gen=("nat", "mean"), n=("tuttu", "size"))
    print("\n  TUM CONFIG'LER BIRLIKTE:")
    print(f"  {'ayak':>7} {'isabet':>9} {'ort.genislik':>13} {'n':>6}")
    for i, r in tum.iterrows():
        print(f"  {int(i):>7} {'%'+f'{100*r.isabet:.1f}':>9} {r.gen:>13.2f} {int(r.n):>6}")

    # ---------------------------------------------------------------- 6
    b("6) BANKER SICILI — tek at yazdigimiz ayaklar")
    print(f"  {'config':>15} {'banker ayak':>12} {'isabet':>9} {'kamu ayni (1 at)':>18} {'FARK':>8}")
    for c, g in k.groupby("config"):
        bg = g[g["nat"] == 1]
        if not len(bg):
            print(f"  {c:>15} {0:>12} {'-':>9} {'-':>18} {'-':>8}")
            continue
        bk = bg[bg["kamu_tuttu"].notna()]
        kt = bk["kamu_tuttu"].mean() if len(bk) else np.nan
        bt = bk["tuttu"].mean() if len(bk) else np.nan
        f = (bt - kt) * 100 if pd.notna(kt) else np.nan
        print(f"  {c:>15} {len(bg):>12} {'%'+f'{100*bg.tuttu.mean():.1f}':>9} "
              + (f"{'%'+f'{100*kt:.1f}':>18} {f:>+8.1f}" if pd.notna(kt) else f"{'-':>18} {'-':>8}"))
    print("\n  OKUMA: banker = kuponun en pahali karari. Tutmazsa kupon o anda biter.")
    print("  Kamu ile FARK burada en anlamlidir: tek atta secim becerisi ciplak olcumlenir.")

    # ---------------------------------------------------------------- 7
    b("7) KAZANANIN ORAN KOVASI — parayi nerede kaciriyoruz?")
    kov = [(0, 2), (2, 4), (4, 8), (8, 16), (16, 1e9)]
    ad = ["<2", "2-4", "4-8", "8-16", "16+"]
    print(f"  {'config':>15} " + " ".join(f"{x:>13}" for x in ad))
    for c, g in kk.groupby("config"):
        sat = []
        for (lo, hi) in kov:
            sub = g[(g["kaz_oran"] >= lo) & (g["kaz_oran"] < hi)]
            sat.append(f"%{100*sub['tuttu'].mean():>4.1f} ({len(sub):>3})" if len(sub) else "      -      ")
        print(f"  {c:>15} " + " ".join(f"{s:>13}" for s in sat))
    print("\n  TUM CONFIG'LER: kazanan oranina gore ayak isabeti ve o ayaklarin payi")
    print(f"  {'kova':>8} {'ayak':>7} {'pay':>7} {'isabet':>9}")
    for adx, (lo, hi) in zip(ad, kov):
        sub = kk[(kk["kaz_oran"] >= lo) & (kk["kaz_oran"] < hi)]
        if len(sub):
            print(f"  {adx:>8} {len(sub):>7} {'%'+f'{100*len(sub)/len(kk):.0f}':>7} "
                  f"{'%'+f'{100*sub.tuttu.mean():.1f}':>9}")

    # ---------------------------------------------------------------- 8
    b("8) ORAN SURUKLENMESI — kupon anindaki fiyat KAPANISTA tutmuyor (K109 TUZAGI)")
    print("  Bu bolum bir olcumden once bir UYARIDIR. Kupon anindaki MUHTEMEL oranla")
    print("  deger hesaplamak SISTEMATIK olarak yanlistir ve yanlisligi TARAFLIDIR.")
    kg = k[k["kaz_oran"].notna()].copy()
    kg = son_oran_ekle(kg)
    e = kg[kg["son_oran"].notna() & (kg["tuttu"] == 1)]
    if len(e):
        print(f"\n  Kazanan atlarin orani, kupon anindan RESMI KAPANISA ({len(e)} ayak; "
              f"{int((e.oran_kaynak=='kapanis').sum())}'i resmi kapanis):")
        print(f"  {'kupon-ani orani':>17} {'n':>6} {'ortalama degisim':>18}")
        for lo, hi, ad in [(0, 4, "<4"), (4, 8, "4-8"), (8, 16, "8-16"), (16, 1e9, "16+")]:
            s = e[(e.kaz_oran >= lo) & (e.kaz_oran < hi)]
            if len(s):
                print(f"  {ad:>17} {len(s):>6} {100*(s.son_oran/s.kaz_oran-1).mean():>+17.1f}%")
        print("\n  >>> DUSUK oranlilar ACILIYOR, YUKSEK oranlilar COKUYOR. Bu, erken muhtemel")
        print("  oranin gurultusunun ortalamaya donmesidir. Sonuc: kupon aninda 'surpriz'")
        print("  gorunen at, kapanista o kadar surpriz DEGILDIR.")

    b("8b) AYAK-GANYAN ROI — secimleri paraya cevir. IKI FIYATLA, farki gormek icin.")
    print("  Dusunce deneyi: yazdigin HER ATA, HER AYAKTA 1 TL ganyan oynasaydin?")
    print("  SOL sutun kupon-ani (muhtemel) fiyati -> YANILTICI, yalniz tuzagi gostermek icin.")
    print("  SAG sutun RESMI KAPANIS (defter.ganyan_kapanis) -> ODENEN FIYAT BUDUR.")
    print("  Muserek bahiste oynadigin fiyat degil KAPANIS fiyati oder; muhtemel oranla")
    print("  hesaplanan kazanc TAHSIL EDILEMEZ.")
    print("  REFERANS: olculmus ganyan kesintisi %28,3 (K104).")
    ke = kg[kg["son_oran"].notna()]
    print(f"\n  {'config':>15} {'yazilan at':>11} {'tutan':>7} {'ROI (muhtemel)':>16} "
          f"{'ROI (KAPANIS)':>19} {'yanilsama':>11}")
    for c, g in sorted(ke.groupby("config"), key=lambda x: x[0]):
        yaz = g["nat"].sum()
        t = g[g["tuttu"] == 1]
        r_m = (t.kaz_oran.sum() - yaz) / yaz * 100
        r_k = (t.son_oran.sum() - yaz) / yaz * 100
        print(f"  {c:>15} {int(yaz):>11,} {len(t):>7} {r_m:>+15.1f}% {r_k:>+18.1f}% "
              f"{r_m-r_k:>+11.1f}")

    print("\n  OLAY DUZEYINDE BOOTSTRAP (%95 GA; birim = ALTILI, ayak degil) — RESMI KAPANIS fiyatiyla:")
    print(f"  {'config':>15} {'Altili':>7} {'ROI':>9} {'%95 GA':>22} {'hüküm':>22}")
    rng = np.random.default_rng(11)
    for c, g in sorted(ke.groupby("config"), key=lambda x: x[0]):
        olaylar = [gg for _, gg in g.groupby(["tarih", "pist", "seq"])]
        m = len(olaylar)
        if m < 10:
            print(f"  {c:>15} {m:>7} {'-':>9} {'-':>22} {'olay<10, bakilamaz':>22}")
            continue
        yz = np.array([x["nat"].sum() for x in olaylar], dtype=float)
        gt = np.array([x.loc[x.tuttu == 1, "son_oran"].sum() for x in olaylar], dtype=float)
        goz = (gt.sum() - yz.sum()) / yz.sum() * 100
        orn = np.empty(4000)
        for i in range(4000):
            j = rng.integers(0, m, m)
            orn[i] = (gt[j].sum() - yz[j].sum()) / yz[j].sum() * 100
        lo, hi = np.percentile(orn, 2.5), np.percentile(orn, 97.5)
        h = "POZITIF (incele!)" if lo > 0 else ("negatif, kesin" if hi < 0 else "ayirt edilemiyor")
        print(f"  {c:>15} {m:>7} {goz:>+8.1f}% [{lo:>+7.1f}, {hi:>+7.1f}] {h:>22}")
    print("\n  K110: sayilar artik RESMI KAPANIS fiyatiyla (defter.csv.ganyan_kapanis).")
    print("  K109'un 'bunlar hala iyimser' uyarisi DUSTU -- o uyari oran_log'un yaklasik")
    print("  15 dk erken durmasindan kaynakliydi (olculdu: 374 kosu, medyan 14,9 dk kala,")
    print("  hicbiri <=10 dk degil; kapanisla farki medyan +%12,7, atlarin %60'i >%25 oynuyor).")
    print(f"  fiyat kaynagi: {kg['oran_kaynak'].value_counts().to_dict()}")
    print("  REFERANS: olculmus ganyan kesintisi %28,3 (K104). ROI'ler oraya oturuyorsa")
    print("  secim katmani ne kazandiriyor ne kaybettiriyor -- yalnizca kesinti odeniyor.")

    # ---------------------------------------------------------------- 9
    b("9) VERI KALITESI — bu sayfadaki sayilari okurken bilinmesi gerekenler (K110)")
    # C3: 'dk_grup' NIYETI kaydeder, GERCEGI degil. takip 15 dk'da bir kostugu icin
    # 30 dk grubu bazen 14-15 dk kala kurulabiliyor -> dk_grup'a gore gruplayan her
    # analizde (bu dosya ve ayak_kalibrasyon dahil) etiket-gercek ayrimi vardir.
    try:
        a2 = a[a["ayak"] == 1].drop_duplicates(["tarih", "pist", "seq", "dk_grup"]).copy()
        a2["dk_kala"] = pd.to_numeric(a2["dk_kala"], errors="coerce")
        a2 = a2[a2["dk_kala"].notna()]
        sap = (a2["dk_kala"] - a2["dk_grup"]).abs()
        print(f"  C3 ETIKET vs GERCEK kurulma ani: {len(a2)} kupon-ani | "
              f"medyan sapma {sap.median():.1f} dk | >5 dk sapan {int((sap > 5).sum())} "
              f"(%{100*(sap > 5).mean():.0f})")
        kotu = a2[sap > 5]
        if len(kotu):
            print("     sapanlar (etiket 'dk_grup' ama gercek 'dk_kala'):")
            for r in kotu.itertuples():
                print(f"       {r.tarih} {r.pist} {int(r.seq)}. -> etiket {int(r.dk_grup)} dk, "
                      f"gercek {r.dk_kala:.1f} dk")
        print("     ANLAMI: bu kuponlar dk_grup'una gore gruplanirken ETIKETIYLE sayilir;")
        print("     zamanlama kolu (K105) kiyasi yalniz ETIKET=GERCEK olanlarda temizdir.")
    except Exception as e:                                       # noqa: BLE001
        print(f"  C3 kontrolu atlandi ({type(e).__name__})")

    # C4: BASABAS'ta 'kazanan' sutunu BIZIM tuttugumuz ati yazar (altili_canli.sonucla_altili:
    # kazanan = min(tuttugumuz kazanan) if tuttuysak else min(tum kazananlar)). Yani yukaridaki
    # "kazanan bizim kacinci tercihimizdi" tablolari (2/4/7) o olaylarda KENDIMIZE dogru yanlidir.
    try:
        dd = pd.read_csv(KOK / "veri" / "defter.csv", low_memory=False)
        dd["sonuc"] = pd.to_numeric(dd["sonuc"], errors="coerce")
        kz = dd[dd["sonuc"].notna()].groupby("race_kod")["sonuc"].apply(lambda s: int((s == 1).sum()))
        if len(kz):
            print(f"\n  C4 BASABAS (dead heat): {len(kz):,} sonuclanmis kosunun "
                  f"{int((kz > 1).sum())}'inde birden cok kazanan (%{100*(kz > 1).mean():.2f})")
            print("     ANLAMI: o olaylarda 'kazanan' sutunu BIZIM tuttugumuz attir -> bolum 2/4/7")
            print("     kendimize dogru hafif yanli. Sikliga bakilirsa etki ihmal edilebilir.")
    except Exception as e:                                       # noqa: BLE001
        print(f"  C4 kontrolu atlandi ({type(e).__name__})")


if __name__ == "__main__":
    main()
