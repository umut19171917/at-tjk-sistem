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
ÖN-KAYITLI ÖLÇÜT — EK / DEĞİŞİKLİK (K124-EK). YİNE SONUÇLAR GÖRÜLMEDEN YAZILDI.
İLK KOŞU YAPILDI VE ÇAPA DÜŞTÜ (6'LI: ölçülen %99,6 / bilinen %48,6). ARIZA TEŞHİS EDİLDİ:
tek kusurlu bileşen BİRİM FİYAT çıkarımıydı. Aşağıdaki değişiklik YALNIZ birim kaynağına
dokunur; çapa testi, tolerans ve karar eşikleri (40/30) AYNEN durur ve YİNE DÜŞEBİLİR.
-------------------------------------------------------------------------------------
E1) NEDEN DÜŞTÜ: "asgari temettü = birim" varsayımı yalnız TABANI DÖVÜLEN bahislerde
    geçerli. 6'LI'nın en ucuz olayı bile 141 TL ödüyor; taban hiç dövülmüyor.
    AYIRT EDİCİ İŞARET (6 yıl, 2021-2026): taban dövülüyorsa asgari temettü ENFLASYONLA
    SÜRÜKLENMEZ, sabit kalır. Ölçülen:
       GANYAN      1,05 · 1,05 · 1,05 · 1,05 · 1,05 · 1,05   (SABİT -> taban)
       PLASE       1,05 x6 yıl, yılda 515-1638 olay          (SABİT -> taban)
       PLASE İKİLİ 2,10 x6 yıl, yılda 9-59 olay              (SABİT -> taban, birim 2,00)
       İKİLİ       1,15·1,15·1,10·1,20·1,20·1,05             (SABİT -> taban)
       SIRALI İKİLİ 1,45·1,45·1,25·1,30·1,05·1,25            (SABİT -> taban)
       ÇİFTE       1,40·1,25·1,30·1,35·1,35·1,00             (SABİT -> taban)
       6'LI        20,5 · 14,9 · 21,1 · 78,1 · 89,9 · 141,2  (SÜRÜKLENİYOR -> taban yok)
       3'LÜ/TABELA/SIRALI 5'Lİ/7'Lİ PLASE/ÜÇLÜ: hepsi sürükleniyor -> taban yok.

E2) BİRİM KAYNAĞI (öncelik sırasıyla, sonuçlara BAKILMADAN sabitlendi):
    (a) ARŞİV TABANI (sabit asgari / 1,05): GANYAN 1,00 · PLASE 1,00 · İKİLİ 1,00 ·
        SIRALI İKİLİ 1,00 · ÇİFTE 1,00 · PLASE İKİLİ 2,00
    (b) K86 RESMÎ 2026 TARİFESİ: 3'lü 2,00 · 4'lü 1,75 · 5'li 1,50 · 6'lı 1,25 · 7'li 2,00
    (c) TANIMLANAMAZ (ÜÇLÜ BAHİS, TABELA BAHİS, TABELA BAHİS SIRASIZ, SIRALI 5 Lİ,
        7'Lİ PLASE): kesinti HESAPLANMAZ. Yalnız ALT SINIR verilir: TJK'da tanımlanmış
        her birim >= 1,00 TL ve kesinti birimle ARTAR -> t >= 1 - M (M = medyan temettü x q).
        Alt sınır bile >= %40 ise KOL KAPANIR; değilse BELİRSİZ, hüküm yok.

E3) KALİBRASYON (çapa geçerse): makinenin yanlılığı çapadan okunur ve karara o değerden
    bakılır. İki AİLE, iki ayrı çapa:
      - ganyan ailesi (kazanan zinciri): düzeltme = ham(GANYAN) - 28,3
      - plase ailesi (PLASE, PLASE İKİLİ, 7'Lİ PLASE): düzeltme = ham(PLASE) - 14,0
        [bilinen plase kesintisi %10-14 bandının ÜST ucu alınır = en muhafazakâr]
    Ganyan ailesinde yanlılığın ayak sayısıyla BÜYÜDÜĞÜ bu koşuda görülecektir; 1-ayaklık
    düzeltmeyi çok-ayaklı bahse uygulamak kesintiyi OLDUĞUNDAN YÜKSEK bırakır = muhafazakâr.

E4) GENİŞLETİLMİŞ ÇAPA (tolerans kapısına DAHİL DEĞİL, yalnız desen görünsün diye):
    3'lü %45,4 · 4'lü %45,6 · 5'li %46,8 · 7'li %57,6 (K94) · SIRALI İKİLİ ~%26 (K21)

E5) MADDE 6 GENİŞLETİLDİ: Harville yanlılığı yalnız plase bahislerinde değil, DERİN SIRALI
    bahislerde de (ÜÇLÜ, TABELA, SIRALI 5'Lİ) derinlikle birikir ve o ailede ÇAPA YOKTUR.
    O üçü için nokta hüküm verilemez; yalnız E2(c) alt sınırı geçerlidir.
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




# --------------------------- BIRIM FIYAT (E2, on-kayitli) ------------------------
# (a) ARSIV TABANI: 6 yil boyunca asgari temettu enflasyonla SURUKLENMIYOR -> taban dovuluyor
BIRIM_TABAN = {
    "GANYAN": 1.00, "PLASE": 1.00, "İKİLİ": 1.00, "SIRALI İKİLİ": 1.00,
    "ÇİFTE": 1.00, "PLASE İKİLİ": 2.00,
}
# (b) K86 RESMI 2026 TARIFESI
BIRIM_RESMI = {
    "3'LÜ GANYAN": 2.00, "4'LÜ GANYAN": 1.75, "5'Lİ GANYAN": 1.50,
    "6'LI GANYAN": 1.25, "7'Lİ GANYAN": 2.00,
}
# (c) TANIMLANAMAZ -> yalniz alt sinir
BIRIM_YOK = {"ÜÇLÜ BAHİS", "TABELA BAHİS", "TABELA BAHİS SIRASIZ",
             "SIRALI 5 Lİ BAHİS", "7'Lİ PLASE"}

# E4: genisletilmis capa (tolerans kapisina DAHIL DEGIL, desen gorunsun diye)
BILINEN = {"GANYAN": 28.3, "6'LI GANYAN": 48.6, "3'LÜ GANYAN": 45.4,
           "4'LÜ GANYAN": 45.6, "5'Lİ GANYAN": 46.8, "7'Lİ GANYAN": 57.6,
           "SIRALI İKİLİ": 26.0, "PLASE": 14.0}
BAKILMAMIS = {"ÇİFTE", "PLASE İKİLİ", "TABELA BAHİS", "TABELA BAHİS SIRASIZ",
              "SIRALI 5 Lİ BAHİS", "7'Lİ PLASE"}


def birim_al(ad):
    if ad in BIRIM_TABAN:
        return BIRIM_TABAN[ad], "taban"
    if ad in BIRIM_RESMI:
        return BIRIM_RESMI[ad], "K86"
    return 1.00, "ALT-SINIR"          # birim>=1 -> t>=1-M (E2c)


def boot_ga(x):
    if len(x) < 20:
        return (np.nan, np.nan)
    a = np.asarray(x, float)
    idx = RNG.integers(0, len(a), size=(BOOT, len(a)))
    med = np.median(a[idx], axis=1)
    return float(np.percentile(med, 5)), float(np.percentile(med, 95))


def main():
    print("=" * 112)
    print(f"K124 — BAHİS BAZINDA KESİNTİ ({YIL}). Ölçüt betiğin başında ÖN-KAYITLI (+EK). SALT-OKUNUR.")
    print("=" * 112)
    T = kosu_tablosu()
    KART = kart_sirasi(T)
    print(f"  {YIL} koşu (devig edilebilen): {len(T):,} · kart: {len(KART):,}")
    kayit, tem, sayac = topla(T, KART)

    ham = {}
    sira = sorted(kayit, key=lambda a: -sayac[a][2])
    print("\n" + "-" * 112)
    print(f"  {'bahis':>22} {'ayak':>4} {'görülen':>8} {'doğr.':>7} {'birim':>6} {'kayn.':>9} "
          f"{'HAM KESİNTİ':>12} {'%90 GA':>16}")
    print("-" * 112)
    for ad in sira:
        gor, dog, kul = sayac[ad]
        v = np.array(kayit[ad], float)
        if v.size < 20:
            print(f"  {ad[:22]:>22} {'':>4} {gor:>8,} {dog:>7,} {'—':>6} {'—':>9} {'YETERSİZ':>12}")
            continue
        b, kaynak = birim_al(ad)
        iade = v / b
        kes = 100 * (1 - float(np.median(iade)))
        lo, hi = boot_ga(iade)
        ham[ad] = {"kes": kes, "lo": 100 * (1 - hi), "hi": 100 * (1 - lo), "b": b,
                   "kaynak": kaynak, "n": kul, "gor": gor, "dog": dog,
                   "M": float(np.median(v))}
        ayak = ZINCIR.get(ad, 1)
        print(f"  {ad[:22]:>22} {ayak:>4} {gor:>8,} {dog:>7,} {b:>6.2f} {kaynak:>9} "
              f"{kes:>11.1f}% [{ham[ad]['lo']:>5.1f} ..{ham[ad]['hi']:>6.1f}]")

    # ------------------------------ CAPA TESTI (madde 4) --------------------------
    print("\n" + "=" * 112)
    print("ÇAPA TESTİ (madde 4) — makine, bağımsız yöntemle bilinen değerleri üretiyor mu?")
    print("=" * 112)
    print(f"  {'bahis':>16} {'ayak':>4} {'bilinen':>9} {'ölçülen':>9} {'fark':>8}   kapı")
    gecti = True
    for ad, bil in sorted(BILINEN.items(), key=lambda x: ZINCIR.get(x[0], 1)):
        if ad not in ham:
            continue
        o = ham[ad]["kes"]
        f = o - bil
        kapi = ad in CAPA
        ok = abs(f) <= CAPA_TOLERANS
        if kapi:
            gecti &= ok
        etiket = ("KAPI: " + ("GEÇTİ" if ok else "DÜŞTÜ")) if kapi else "(bilgi)"
        print(f"  {ad[:16]:>16} {ZINCIR.get(ad,1):>4} {bil:>8.1f}% {o:>8.1f}% {f:>+7.1f}   {etiket}")

    if not gecti:
        print("\n" + "=" * 112)
        print("HÜKÜM: ÇAPA DÜŞTÜ -> ÖLÇÜM GÜVENİLMEZ. HİÇBİR KOL KAPANMAZ, HİÇBİR KOL AÇILMAZ.")
        print("=" * 112)
        return

    # ------------------------------ KALIBRASYON (E3) ------------------------------
    duz_gan = ham["GANYAN"]["kes"] - 28.3 if "GANYAN" in ham else 0.0
    duz_pla = ham["PLASE"]["kes"] - 14.0 if "PLASE" in ham else 0.0
    print("\n" + "=" * 112)
    print("KALİBRASYON (E3) — makinenin yanlılığı çapadan okundu")
    print("=" * 112)
    print(f"  ganyan ailesi düzeltmesi = ham(GANYAN) - 28,3 = {duz_gan:+.1f} puan")
    print(f"  plase  ailesi düzeltmesi = ham(PLASE)  - 14,0 = {duz_pla:+.1f} puan")
    print("  UYARI: ganyan ailesinde yanlılık ayak sayısıyla büyür (yukarıdaki çapa tablosuna")
    print("  bak). 1-ayaklık düzeltmeyi çok-ayaklıya uygulamak kesintiyi OLDUĞUNDAN YÜKSEK")
    print("  bırakır -> 'KAPANIR' hükmü muhafazakâr, 'AÇILIR' hükmü şüpheli.")

    # ------------------------------ HUKUM (madde 5) -------------------------------
    print("\n" + "=" * 112)
    print("HÜKÜM — kesinti >= %40 KAPANIR · < %30 AÇILIR · arası BELİRSİZ (%90 GA'nın TAMAMI)")
    print("=" * 112)
    print(f"  {'bahis':>22} {'n':>6} {'KALİBRE KESİNTİ':>16} {'%90 GA':>16}  {'hüküm':<10} not")
    for ad in sira:
        if ad not in ham:
            continue
        h = ham[ad]
        aile_pl = ad in PLASE_AILE
        duz = duz_pla if aile_pl else duz_gan
        k, lo, hi = h["kes"] - duz, h["lo"] - duz, h["hi"] - duz
        if ad in BIRIM_YOK:
            hkm = "KAPANIR" if lo >= KAPAT_ESIK else "BELİRSİZ"
            not_ = f"ALT SINIR (birim bilinmiyor, M={h['M']:.3f}); nokta hüküm YOK"
        elif lo >= KAPAT_ESIK:
            hkm, not_ = "KAPANIR", ""
        elif hi < AC_ESIK:
            hkm, not_ = "AÇILIR", ""
        else:
            hkm, not_ = "BELİRSİZ", ""
        if aile_pl:
            not_ = ("Harville yanlı -> gerçek kesinti DAHA YÜKSEK; KAPANIR muhafazakâr. " + not_).strip()
        if ad in BAKILMAMIS:
            not_ = "<<< BAKILMAMIŞ BAHİS >>> " + not_
        print(f"  {ad[:22]:>22} {h['n']:>6,} {k:>15.1f}% [{lo:>5.1f} ..{hi:>6.1f}]  {hkm:<10} {not_}")

    print("\n" + "-" * 112)
    print("  DOĞRULAMA ORANI DÜŞÜK OLANLAR (kalite kapısı, madde 7):")
    for ad in sira:
        g, d, _ = sayac[ad]
        if g >= 50 and d / g < 0.90:
            print(f"     {ad[:22]:>22}: {d:,}/{g:,} = %{100*d/g:.0f} -> bu satır ŞÜPHELİ")


if __name__ == "__main__":
    main()
