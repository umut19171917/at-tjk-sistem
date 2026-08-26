# -*- coding: utf-8 -*-
"""
kesinti_tara.py — BAKILMAMIŞ BEŞ BAHSİN KESİNTİSİ (K124). SALT-OKUNUR / OFFLINE.

K123 envanteri gösterdi ki TJK'nın oynattığı beş bahse (ÇİFTE, PLASE İKİLİ, TABELA ±sırasız,
SIRALI 5'Lİ, 7'Lİ PLASE) 123 karar boyunca hiç bakılmadı ve HEPSİNİN 6 yıllık verisi var.
Bu betik onları model kurmadan önce ELEMEK için yazıldı ("kill-first", K44 konvansiyonu):
kesinti duvarı %45-58 bandındaysa (K94) model kurmanın anlamı yok — projede ölçülmüş en
büyük kenar 3-4 puan.

=====================================================================================
ÖN-KAYITLI ÖLÇÜT — BU BLOK SONUÇLAR GÖRÜLMEDEN YAZILDI VE GİT'E MÜHÜRLENDİ (K33/K52)
=====================================================================================
1) KAPSAM: yalnız 2026. Gerekçe K94: tarihsel temettüyü bugünün birim fiyatıyla bölmek
   kesintiyi sahte biçimde yıllara yayar (enflasyon tuzağı, K73'te de düşülmüştü).

2) TAHMİNCİ (K73 pari-mutuel kimliği):
       temettü = birim x (1 - kesinti) / q     ->     iade = temettü x q / birim
   q = kazanan seçime gelen havuz payı; kapanış ganyanı devig edilip Harville ile
   ilgili bahse çevrilir.

3) BİRİM FİYAT: TJK asgari temettüyü birim fiyatın altına düşürmez -> birim, o bahsin
   2026'daki EN DÜŞÜK temettüsünden okunur (0,25'e yuvarlanır).
   DOĞRULAMA: bu çıkarım GANYAN için 1,00 ve 6'LI için 1,25 (K86 resmî) vermelidir.
   Vermezse birim çıkarımı GÜVENİLMEZ ilan edilir.
   DUYARLILIK: her satır birim x0,8 ve x1,25 ile tekrar edilir.

4) ÇAPA TESTİ (asıl kill-first kapısı): aynı makine, değeri BAĞIMSIZ yöntemle bilinen
   iki bahiste çalıştırılır:
       GANYAN  = %28,3  (K10/K13, overround'dan — bu makineden bağımsız)
       6'LI    = %48,6  (K73, AGF'den — bu makineden bağımsız)
   MAKİNE BU İKİSİNİ ±6 PUAN İÇİNDE ÜRETEMEZSE: ölçüm GÜVENİLMEZ ilan edilir,
   HİÇBİR KOL KAPANMAZ, sonuç yalnız "yöntem tutmadı" olarak kaydedilir.

5) KARAR KURALI (yalnız çapa geçerse uygulanır) — %90 GA'nın TAMAMI eşiği geçmeli:
       kesinti >= %40  -> KOL KAPANIR   (model kurulmaz)
       kesinti <  %30  -> KOL AÇILIR    (ön-kayıtlı ölçütle model kolu kurulur)
       %30 - %40       -> BELİRSİZ      (ne açılır ne kapanır; BEKLEYENLER'e yazılır)
   GA: olay-bootstrap, 2.000 tekrar, medyan iade üzerinden.

6) ASİMETRİ UYARISI (önceden yazıldı): Harville plase olasılıklarını favoriler lehine
   ŞİŞİRİR -> q şişer -> ölçülen kesinti OLDUĞUNDAN DÜŞÜK çıkar. Dolayısıyla plase
   ailesinde (PLASE, PLASE İKİLİ, 7'Lİ PLASE) "KAPANIR" hükmü MUHAFAZAKÂRDIR
   (gerçek kesinti daha yüksek), "AÇILIR" hükmü ŞÜPHEYLE karşılanmalıdır.

7) KALİTE KAPISI: her olayda, temettü satırındaki kombinasyon gerçek sonuçlarla
   doğrulanır (kazananlar / plase alanlar). Doğrulamayan olay ATILIR ve sayısı raporlanır.
   K94'te bu oran %99,1-100'dü; belirgin düşük çıkarsa ayrıştırıcıdan şüphelenilir.
=====================================================================================

DOKUNULMAYANLAR: hiçbir dosyaya yazmaz. Config, dağıtıcı, ağırlık, canlı akış — hiçbiri.
KAYNAK: veri/ham/sonuclar/*.json (temettü) + veri/katilim.csv (kapanış oranı, sonuç).
"""
import json
import re
from collections import defaultdict
from itertools import permutations
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
SONUC = KOK / "veri" / "ham" / "sonuclar"

YIL = "2026"
CAPA = {"GANYAN": 28.3, "6'LI GANYAN": 48.6}      # bagimsiz yontemle bilinen degerler
CAPA_TOLERANS = 6.0                                # puan
KAPAT_ESIK = 40.0
AC_ESIK = 30.0
BOOT = 2000
RNG = np.random.default_rng(20260826)

DESEN = re.compile(r"([^()]+?)\(([^)]*)\):\s*([\d.,]+)\s*TL", re.UNICODE)


def ad_normalle(ad):
    a = re.sub(r"^\s*\d+\.\s*", "", ad).strip()
    return " ".join(a.split())


def tl(s):
    try:
        return float(s.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def ayak_coz(kombo):
    """'9,10/9/10/2,5' -> [[9,10],[9],[10],[2,5]] (beraberlik = ayni ayakta cok at)."""
    out = []
    for p in kombo.split("/"):
        try:
            out.append([int(x) for x in p.split(",") if x.strip()])
        except ValueError:
            return None
    return out if out and all(out) else None


# ------------------------------- Harville ---------------------------------------
def harville_sirali(p, idx):
    """P(idx[0] birinci, idx[1] ikinci, ...) — Harville zinciri."""
    kalan = 1.0
    q = 1.0
    for i in idx:
        if kalan <= 1e-12:
            return 0.0
        q *= p[i] / kalan
        kalan -= p[i]
    return q


def harville_sirasiz(p, idx):
    """P(ilk-len(idx) tam olarak bu kume; sira farketmez)."""
    return sum(harville_sirali(p, list(o)) for o in permutations(idx))


def top_m(p, m):
    """P(her at ilk-m'de) — Harville. m<=3, n<=22 -> ucuz."""
    n = len(p)
    if n <= m:
        return np.ones(n)
    out = np.zeros(n)
    for i in range(n):
        if m == 1:
            out[i] = p[i]
            continue
        t = p[i]
        for j in range(n):
            if j == i:
                continue
            t += harville_sirali(p, [j, i])
            if m >= 3:
                for k in range(n):
                    if k in (i, j):
                        continue
                    t += harville_sirali(p, [j, k, i])
        out[i] = t
    return np.clip(out, 1e-9, 1.0)


def ikili_top_m(p, a, b, m):
    """P(a ve b'nin IKISI de ilk-m'de)."""
    n = len(p)
    if n <= m:
        return 1.0
    if m == 2:
        return harville_sirasiz(p, [a, b])
    t = 0.0
    for c in range(n):
        if c in (a, b):
            continue
        t += harville_sirasiz(p, [a, b, c])
    return t


# ------------------------------- veri -------------------------------------------
def kosu_tablosu():
    """race_kod -> {no dizisi, devig p, kazananlar, plase alanlar, saha, m}."""
    d = pd.read_csv(KOK / "veri" / "katilim.csv",
                    usecols=["race_kod", "tarih", "sehir", "kosu_no", "no",
                             "ganyan_kapanis", "sonuc", "kosmaz"], low_memory=False)
    d["yil"] = d["tarih"].astype(str).str[-4:]
    d = d[d["yil"] == YIL].copy()
    d = d[~d["kosmaz"].fillna(False).astype(bool)]
    for c in ("ganyan_kapanis", "sonuc", "no"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=["no"])

    T = {}
    for rk, g in d.groupby("race_kod"):
        o = g["ganyan_kapanis"].to_numpy(float)
        if (~np.isfinite(o)).any() or (o <= 1.0).any() or len(o) < 4:
            continue
        inv = 1.0 / o
        p = inv / inv.sum()
        nos = g["no"].to_numpy(int)
        s = g["sonuc"].to_numpy(float)
        saha = len(nos)
        m = 3 if saha >= 8 else 2
        T[int(rk)] = {
            "p": p, "saha": saha, "m": m,
            "idx": {int(x): i for i, x in enumerate(nos)},
            "kazanan": set(nos[s == 1].tolist()),
            "plase": set(nos[(s >= 1) & (s <= m)].tolist()),
            "sehir": g["sehir"].iloc[0], "kosu_no": int(g["kosu_no"].iloc[0]),
            "tarih": g["tarih"].iloc[0],
        }
    return T


def kart_sirasi(T):
    """(tarih,sehir) -> kosu_no'ya gore sirali race_kod listesi (zincir bahisler icin)."""
    kart = defaultdict(list)
    for rk, v in T.items():
        kart[(v["tarih"], v["sehir"])].append((v["kosu_no"], rk))
    return {k: [r for _, r in sorted(v)] for k, v in kart.items()}


# ------------------------------- q hesabi ---------------------------------------
# Her bahis icin: (aile, ayak_sayisi, q_fonksiyonu, dogrulama_fonksiyonu)
# aile: "tek"  = tek kosu   ·  "zincir" = N ardisik kosu
TEK_KOSU = {
    "GANYAN": 1, "PLASE": 1, "İKİLİ": 1, "SIRALI İKİLİ": 1, "ÜÇLÜ BAHİS": 1,
    "PLASE İKİLİ": 1, "TABELA BAHİS": 1, "TABELA BAHİS SIRASIZ": 1,
    "SIRALI 5 Lİ BAHİS": 1,
}
ZINCIR = {
    "ÇİFTE": 2, "3'LÜ GANYAN": 3, "4'LÜ GANYAN": 4, "5'Lİ GANYAN": 5,
    "6'LI GANYAN": 6, "7'Lİ GANYAN": 7, "7'Lİ PLASE": 7,
}
PLASE_AILE = {"PLASE", "PLASE İKİLİ", "7'Lİ PLASE"}


def q_tek(ad, R, ayaklar):
    """Tek kosuluk bahsin q'su. ayaklar = [[at],[at],...] (sirali gorunum)."""
    p, m, ix = R["p"], R["m"], R["idx"]
    duz = [h for a in ayaklar for h in a]
    if any(h not in ix for h in duz):
        return None
    I = [ix[h] for h in duz]
    if len(set(I)) != len(I):
        return None
    if ad == "GANYAN":
        return float(p[I[0]])
    if ad == "PLASE":
        return float(top_m(p, m)[I[0]])
    if ad == "SIRALI İKİLİ":
        return harville_sirali(p, I[:2])
    if ad == "İKİLİ":
        return harville_sirasiz(p, I[:2])
    if ad == "ÜÇLÜ BAHİS":
        return harville_sirali(p, I[:3])
    if ad == "PLASE İKİLİ":
        return ikili_top_m(p, I[0], I[1], m)
    if ad == "TABELA BAHİS":
        return harville_sirali(p, I[:4])
    if ad == "TABELA BAHİS SIRASIZ":
        return harville_sirasiz(p, I[:4])
    if ad == "SIRALI 5 Lİ BAHİS":
        return harville_sirali(p, I[:5])
    return None


def dogrula_tek(ad, R, ayaklar):
    duz = [h for a in ayaklar for h in a]
    if ad == "GANYAN":
        return set(duz[:1]) <= R["kazanan"]
    if ad in ("PLASE", "PLASE İKİLİ"):
        return set(duz) <= R["plase"]
    # sirali/sirasiz bitis bahisleri: ilk eleman kazanan olmali, hepsi farkli
    return duz[0] in R["kazanan"] and len(set(duz)) == len(duz)


def q_zincir(ad, Rs, ayaklar):
    """Zincir bahsin q'su = ayaklarin paylarinin CARPIMI (K73 bagimsizlik varsayimi)."""
    if len(Rs) != len(ayaklar):
        return None
    q = 1.0
    plase = ad == "7'Lİ PLASE"
    for R, atlar in zip(Rs, ayaklar):
        ix = R["idx"]
        if any(h not in ix for h in atlar):
            return None
        I = [ix[h] for h in atlar]
        pr = top_m(R["p"], R["m"]) if plase else R["p"]
        q *= float(sum(pr[i] for i in I))
    return q


def dogrula_zincir(ad, Rs, ayaklar):
    hedef = "plase" if ad == "7'Lİ PLASE" else "kazanan"
    return all(set(a) <= R[hedef] for R, a in zip(Rs, ayaklar))


# ------------------------------- tarama -----------------------------------------
def topla(T, KART):
    """Her bahis icin (iade_ham, temettu) listesi + kalite sayaclari."""
    kayit = defaultdict(list)
    tem = defaultdict(list)
    sayac = defaultdict(lambda: [0, 0, 0])   # gorulen, dogrulandi, q_hesaplandi
    yer = {}                                  # race_kod -> (kart anahtari, sira)
    for k, dizi in KART.items():
        for i, rk in enumerate(dizi):
            yer[rk] = (k, i)

    dosyalar = sorted(SONUC.glob(f"{YIL}*.json"))
    for f in dosyalar:
        try:
            o = json.loads(f.read_text(encoding="utf-8"))
        except Exception:                                        # noqa: BLE001
            continue
        for kosu in (o.get("kosular") or []):
            try:
                rk = int(kosu.get("KOD"))
            except (TypeError, ValueError):
                continue
            R = T.get(rk)
            if R is None:
                continue
            metin = kosu.get("emiParasalNeticeler_tr") or ""
            if not isinstance(metin, str):
                continue
            for ad_ham, kombo, para in DESEN.findall(metin):
                ad = ad_normalle(ad_ham)
                if ad not in TEK_KOSU and ad not in ZINCIR:
                    continue
                d = tl(para)
                ayaklar = ayak_coz(kombo)
                if d is None or ayaklar is None:
                    continue
                sayac[ad][0] += 1
                tem[ad].append(d)
                if ad in TEK_KOSU:
                    if not dogrula_tek(ad, R, ayaklar):
                        continue
                    sayac[ad][1] += 1
                    q = q_tek(ad, R, ayaklar)
                else:
                    n = ZINCIR[ad]
                    kk, i = yer[rk]
                    if i - n + 1 < 0:
                        continue
                    kodlar = KART[kk][i - n + 1:i + 1]
                    Rs = [T.get(x) for x in kodlar]
                    if any(x is None for x in Rs) or len(ayaklar) != n:
                        continue
                    if not dogrula_zincir(ad, Rs, ayaklar):
                        continue
                    sayac[ad][1] += 1
                    q = q_zincir(ad, Rs, ayaklar)
                if q is None or not np.isfinite(q) or q <= 0:
                    continue
                sayac[ad][2] += 1
                kayit[ad].append(d * q)          # birim'e BOLUNMEDI (sonra bolunur)
    return kayit, tem, sayac


def birim_cikar(temettuler):
    """TJK asgari temettu ~ birim -> en dusuk temettuden oku, 0,25'e yuvarla."""
    v = np.array([x for x in temettuler if x and x > 0])
    if v.size < 30:
        return np.nan
    return max(0.25, round(float(v.min()) * 4) / 4)


def boot_ga(x):
    if len(x) < 20:
        return (np.nan, np.nan)
    a = np.asarray(x, float)
    idx = RNG.integers(0, len(a), size=(BOOT, len(a)))
    med = np.median(a[idx], axis=1)
    return float(np.percentile(med, 5)), float(np.percentile(med, 95))


def main():
    print("=" * 108)
    print(f"K124 — BAHİS BAZINDA KESİNTİ ({YIL}, salt-okunur). Ölçüt betiğin başında ÖN-KAYITLI.")
    print("=" * 108)
    T = kosu_tablosu()
    KART = kart_sirasi(T)
    print(f"  {YIL} koşu (devig edilebilen): {len(T):,} · kart: {len(KART):,}")
    kayit, tem, sayac = topla(T, KART)

    sira = sorted(kayit, key=lambda a: -sayac[a][2])
    print("\n" + "-" * 108)
    print(f"  {'bahis':>22} {'görülen':>8} {'doğru':>7} {'kul.':>7} {'birim':>7} "
          f"{'KESİNTİ':>9} {'%90 GA':>17} {'x0,8':>7} {'x1,25':>7}")
    print("-" * 108)
    sonuc = {}
    for ad in sira:
        gor, dog, kul = sayac[ad]
        b = birim_cikar(tem[ad])
        v = np.array(kayit[ad], float)
        if not np.isfinite(b) or v.size < 20:
            print(f"  {ad[:22]:>22} {gor:>8,} {dog:>7,} {kul:>7,} {'—':>7} {'YETERSİZ':>9}")
            continue
        iade = v / b
        kes = 100 * (1 - float(np.median(iade)))
        lo, hi = boot_ga(iade)
        ga = f"[{100*(1-hi):>5.1f} .. {100*(1-lo):>5.1f}]"
        k08 = 100 * (1 - float(np.median(v / (b * 0.8))))
        k125 = 100 * (1 - float(np.median(v / (b * 1.25))))
        sonuc[ad] = (kes, 100 * (1 - hi), 100 * (1 - lo), b, kul, gor, dog)
        print(f"  {ad[:22]:>22} {gor:>8,} {dog:>7,} {kul:>7,} {b:>7.2f} "
              f"{kes:>8.1f}% {ga:>17} {k08:>6.1f}% {k125:>6.1f}%")

    # ---------------- CAPA TESTI ----------------
    print("\n" + "=" * 108)
    print("ÇAPA TESTİ — makine, değeri bağımsız yöntemle bilinen iki bahsi üretebiliyor mu?")
    print("=" * 108)
    gecti = True
    for ad, bilinen in CAPA.items():
        if ad not in sonuc:
            print(f"  {ad:>14}: ölçülemedi -> ÇAPA DÜŞTÜ")
            gecti = False
            continue
        olculen = sonuc[ad][0]
        fark = abs(olculen - bilinen)
        ok = fark <= CAPA_TOLERANS
        gecti &= ok
        print(f"  {ad:>14}: bilinen %{bilinen:.1f} · ölçülen %{olculen:.1f} · "
              f"fark {fark:.1f} puan -> {'GEÇTİ' if ok else 'DÜŞTÜ'}")
    print(f"\n  BİRİM ÇIKARIMI DOĞRULAMASI (beklenen GANYAN 1,00 · 6'LI 1,25):")
    for ad, bek in (("GANYAN", 1.00), ("6'LI GANYAN", 1.25)):
        if ad in sonuc:
            b = sonuc[ad][3]
            print(f"     {ad:>14}: çıkarılan {b:.2f} · beklenen {bek:.2f} -> "
                  f"{'TUTTU' if abs(b - bek) < 0.13 else 'TUTMADI'}")

    print("\n" + "=" * 108)
    if not gecti:
        print("HÜKÜM: ÇAPA DÜŞTÜ -> ÖLÇÜM GÜVENİLMEZ. HİÇBİR KOL KAPANMAZ, HİÇBİR KOL AÇILMAZ.")
        print("Yukarıdaki sayılar yalnız 'yöntem tutmadı' kaydı olarak durur (ön-kayıtlı madde 4).")
        print("=" * 108)
        return
    print("HÜKÜM (ön-kayıtlı madde 5 — %90 GA'nın TAMAMI eşiği geçmeli)")
    print("=" * 108)
    BAKILMAMIS = {"ÇİFTE", "PLASE İKİLİ", "TABELA BAHİS", "TABELA BAHİS SIRASIZ",
                  "SIRALI 5 Lİ BAHİS", "7'Lİ PLASE"}
    for ad in sira:
        if ad not in sonuc:
            continue
        kes, lo, hi, b, kul, _, _ = sonuc[ad]
        if lo >= KAPAT_ESIK:
            h = "KAPANIR"
        elif hi < AC_ESIK:
            h = "AÇILIR"
        else:
            h = "BELİRSİZ"
        etiket = "  <-- BAKILMAMIŞ" if ad in BAKILMAMIS else ""
        uyari = ""
        if ad in PLASE_AILE:
            uyari = ("   [Harville yanlı: gerçek kesinti DAHA YÜKSEK -> 'KAPANIR' muhafazakâr, "
                     "'AÇILIR' şüpheli]")
        print(f"  {ad[:22]:>22} n={kul:>6,}  %{kes:>5.1f} GA[{lo:>5.1f}..{hi:>5.1f}]"
              f"  -> {h:<9}{etiket}{uyari}")


if __name__ == "__main__":
    main()
