"""
altili_zaman_test.py — "KUPONU 30 DK YERINE 15 DK KALA KURSAK NE OLURDU?" (BEKLEYENLER #4, K76 adayi).
OFFLINE, SALT-OKUNUR: canliya DOKUNMAZ, hicbir dosyaya yazmaz. Canli zamanlama 30 dk KALIR.

NEREDEN GELDI: 25 Tem'de kullanici "kuponu 15 dk kala kursak?" diye sordu. Kanit yoktu; canliyi
degistirmek yerine K59'da `oran_log.py` kuruldu -> her Altili ayaginin oranini postaya 45 dk
kalana kadar birden fazla anda kaydediyor. Simdi o veriyle SIMULASYON yapiliyor.

YONTEM:
 1) Harman katsayilari (alpha,gamma) defter.csv'den GERI CIKARILIR: ayni kosuda log-oranlar
    uzerinde  ln(bot2_i/bot2_j) = a*ln(bot1_i/bot1_j) + g*ln(kamu_i/kamu_j)  regresyonu.
    (Olculdu: alpha=0,2095 gamma=0,9495, R2=0,9996 -> model formu birebir dogrulandi.)
 2) Her anlik goruntude (snapshot) canli GANYAN oranindan piyasa olasiligi: p = de-vig(1/oran).
 3) Bot1 ORAN-KOR oldugu icin zamanla DEGISMEZ -> defter'den alinir.
    bot2(t) = softmax( alpha*ln bot1 + gamma*ln p_piyasa(t) )
 4) Ayni kupon kurallariyla (KONFIG) her zaman dilimi icin kupon kurulur, GERCEK kazananla
    sonuclanir. 30 dk ve 15 dk YAN YANA kiyaslanir.

ISTATISTIK NOTU: elde 17 Altili var -> KUPON seviyesinde (6/6) hicbir sey kanitlanamaz.
O yuzden ASIL olcut AYAK seviyesidir (~70-100 gozlem): "kazanan secimin icinde miydi?"
Eslesmis kiyas (ayni ayak, iki zaman) -> McNemar tarzi: 30 tutup 15 kacirdigi ayak sayisi
vs tersi. Kupon seviyesi bilgi olarak basilir ama karar icin KULLANILMAZ.

10 DK: takip 15 dk'da bir calistigi icin o bandda veri YOK (K59'da ongorulmustu) -> test edilemez.
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_canli import KONFIG, BANKER_ESIK, AYRISMA_W  # noqa: E402
from altili_backtest import (kupon_kur, kupon_kur_acgozlu,  # noqa: E402
                             kupon_kur_ayrisma, ayrisma_skoru)
import rapor_ortak as ro  # noqa: E402

HEDEFLER = [(30, "30 dk (CANLI)"), (15, "15 dk")]
TOLERANS = 8          # hedefe +/- bu kadar dakika icindeki en yakin snapshot


def katsayi_cikar(d):
    """defter'den (alpha, gamma) geri cikar. Doner (alpha, gamma, R2)."""
    X, Y = [], []
    for _, g in d.groupby("race_kod"):
        if len(g) < 3:
            continue
        b1, b2, km = g.bot1.values, g.bot2.values, g.kamu.values
        X.append(np.c_[np.log(b1 / b1[0]), np.log(km / km[0])][1:])
        Y.append(np.log(b2 / b2[0])[1:])
    X, Y = np.vstack(X), np.concatenate(Y)
    coef, *_ = np.linalg.lstsq(X, Y, rcond=None)
    r2 = 1 - ((Y - X @ coef) ** 2).sum() / ((Y - Y.mean()) ** 2).sum()
    return float(coef[0]), float(coef[1]), float(r2)


def main():
    d = pd.read_csv(KOK / "veri" / "defter.csv").drop_duplicates(["race_kod", "no"], keep="last")
    for c in ("bot1", "bot2", "kamu"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    dd = d.dropna(subset=["bot1", "bot2", "kamu"])
    dd = dd[(dd.bot1 > 0) & (dd.bot2 > 0) & (dd.kamu > 0)]
    alpha, gamma, r2 = katsayi_cikar(dd)
    print(f"harman katsayilari (defter'den): alpha={alpha:.4f} gamma={gamma:.4f}  R2={r2:.6f}")

    bot1 = {(int(r.race_kod), int(r.no)): float(r.bot1) for r in dd.itertuples()}

    log = pd.read_csv(KOK / "veri" / "altili_oran_log.csv")
    log["ganyan"] = pd.to_numeric(log["ganyan"], errors="coerce")
    log = log[(log.kosmaz == 0) & log.ganyan.notna() & (log.ganyan > 1)]
    print(f"oran_log: {len(log):,} kullanilabilir satir | "
          f"{log.groupby(['tarih','pist','seq']).ngroups} Altili | {log.race_kod.nunique()} ayak")

    def secim_kur(grup, hedef):
        """Bir Altilinin 6 ayagi icin hedef dakikaya en yakin snapshot'tan bot2 uret.
        Doner: (ayak_atlari_bot2, ayak_bot1, ayrisma, race_kodlar) veya None."""
        aa, ab1, ayr, rks = [], [], [], []
        for ayak in range(1, 7):
            g = grup[grup.ayak == ayak]
            if g.empty:
                return None
            g = g.assign(uz=(g.dk_kala - hedef).abs())
            en = g.uz.min()
            if en > TOLERANS:
                return None
            ts = g.loc[g.uz == en, "kayit_ts"].iloc[0]
            s = g[g.kayit_ts == ts]
            rk = int(s.race_kod.iloc[0])
            no = s.no.astype(int).values
            b1 = np.array([bot1.get((rk, int(x)), np.nan) for x in no])
            if np.isnan(b1).any() or len(no) < 4:
                return None
            inv = 1.0 / s.ganyan.values
            pm = inv / inv.sum()                       # de-vig
            z = alpha * np.log(b1) + gamma * np.log(pm)
            b2 = np.exp(z - z.max()); b2 = b2 / b2.sum()
            aa.append(list(zip(no.tolist(), b2.tolist())))
            ab1.append(list(zip(no.tolist(), (b1 / b1.sum()).tolist())))
            ayr.append(ayrisma_skoru(b1 / b1.sum(), pm))
            rks.append(rk)
        return aa, ab1, ayr, rks

    # ---- her Altili x her zaman dilimi ----
    kayit = []
    for (tarih, pist, seq), grup in log.groupby(["tarih", "pist", "seq"]):
        paket = {}
        for hedef, ad in HEDEFLER:
            r = secim_kur(grup, hedef)
            if r is None:
                paket = None
                break
            paket[hedef] = r
        if paket is None:
            continue
        rks = paket[HEDEFLER[0][0]][3]
        kaz = []
        for rk in rks:
            z = ro.kazanan_bilgi(rk)
            kaz.append(int(z["no"]) if z and z.get("no") is not None else None)
        if any(k is None for k in kaz):
            continue
        kayit.append({"tarih": tarih, "pist": pist, "seq": int(seq),
                      "paket": paket, "kaz": kaz})
    print(f"iki zaman diliminde de TAM olan + sonuclanmis Altili: {len(kayit)}\n")
    if not kayit:
        print("Yeterli veri yok."); return

    print("=" * 92)
    print("30 DK vs 15 DK — ayni Altili, ayni kurallar, tek fark KUPONUN KURULDUGU AN")
    print("=" * 92)

    for cfg, ay in KONFIG.items():          # K100: emekliler de taranir (gecmis kiyas anlamli)
        satir = {}
        for hedef, ad in HEDEFLER:
            ayak_tut = 0; ayak_top = 0; tam = 0; kombo_top = 0
            for k in kayit:
                aa, ab1, ayr, rks = k["paket"][hedef]
                puan = ab1 if ay["puan"] == "bot1" else aa
                if ay["dagitim"] == "acgozlu":
                    sec = kupon_kur_acgozlu(puan, ay["kombo"])
                elif ay["dagitim"] == "ayrisma":
                    sec = kupon_kur_ayrisma(puan, ayr, ay["kombo"], AYRISMA_W)
                else:
                    sec = kupon_kur(puan, ay["kapsam"], ay["kombo"], BANKER_ESIK)
                if any(len(s) == 0 for s in sec):
                    continue
                t = sum(1 for i in range(6) if k["kaz"][i] in sec[i])
                ayak_tut += t; ayak_top += 6; tam += (t == 6)
                kombo_top += int(np.prod([len(s) for s in sec]))
            satir[hedef] = (ayak_tut, ayak_top, tam, kombo_top)
        a30 = satir[30]; a15 = satir[15]
        print(f"{cfg:12s} ayak isabeti  30dk {a30[0]:>3}/{a30[1]:<3} (%{100*a30[0]/max(a30[1],1):4.1f})   "
              f"15dk {a15[0]:>3}/{a15[1]:<3} (%{100*a15[0]/max(a15[1],1):4.1f})   "
              f"fark {a15[0]-a30[0]:+3d}   |  6/6: {a30[2]} vs {a15[2]}   "
              f"ort.kombo {a30[3]//max(len(kayit),1)} vs {a15[3]//max(len(kayit),1)}")

    # ---- ESLESMIS AYAK KIYASI (asil olcut) ----
    print("\n" + "=" * 92)
    print("ESLESMIS AYAK KIYASI (asil olcut) — ayni ayak, iki zaman, orta config")
    print("=" * 92)
    ay = KONFIG["orta"]
    sadece30 = sadece15 = ikisi = hicbiri = 0
    for k in kayit:
        secs = {}
        for hedef, _ in HEDEFLER:
            aa, ab1, ayr, rks = k["paket"][hedef]
            secs[hedef] = kupon_kur(aa, ay["kapsam"], ay["kombo"], BANKER_ESIK)
        for i in range(6):
            a = k["kaz"][i] in secs[30][i]
            b = k["kaz"][i] in secs[15][i]
            if a and b: ikisi += 1
            elif a: sadece30 += 1
            elif b: sadece15 += 1
            else: hicbiri += 1
    n = ikisi + sadece30 + sadece15 + hicbiri
    print(f"  toplam ayak: {n}")
    print(f"  ikisi de tuttu     : {ikisi}")
    print(f"  SADECE 30 dk tuttu : {sadece30}   <- gec kursak KAYBEDECEGIMIZ")
    print(f"  SADECE 15 dk tuttu : {sadece15}   <- gec kursak KAZANACAGIMIZ")
    print(f"  ikisi de kacirdi   : {hicbiri}")
    fark = sadece15 - sadece30
    ayrisan = sadece30 + sadece15
    if ayrisan:
        from math import comb
        p = sum(comb(ayrisan, i) for i in range(min(sadece30, sadece15) + 1)) / 2 ** ayrisan * 2
        print(f"  NET: {fark:+d} ayak   (iki-yonlu isaret testi p={min(p,1):.3f})")
    else:
        print("  Hicbir ayakta fark yok -> iki zaman ayni kuponu uretiyor.")

    print("\n" + "=" * 92)
    print(f"UYARI: n={len(kayit)} Altili. Bu bir EGILIM okumasidir, KARAR DEGIL.")
    print("Canli zamanlama 30 dk KALIR; veri biriktikce bu test tekrar kosulmalidir.")
    print("=" * 92)


if __name__ == "__main__":
    main()
