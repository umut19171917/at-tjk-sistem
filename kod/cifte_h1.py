# -*- coding: utf-8 -*-
"""
cifte_h1.py — K126: ÇİFTE kolunun BİRİNCİ KAPISI (H1). SALT-OKUNUR / OFFLINE.

K125 ÇİFTE'nin kesintisini %27,2 ölçtü ve kolu açtı. Ama ucuz kesinti GEREKLİ şart,
YETERLİ şart değil: K13 zaten %25,5'lik ganyan duvarına çarpıp geri dönmüştü.

Kolu açan tek yapısal gerekçe şuydu: K73/K74 Altılı havuzunun KÖTÜ KALİBRE olduğunu
ölçtü (favori-uzunşanslı yanlılığı güçlü) ama %48,6 vergi kenarı yutuyordu. ÇİFTE,
çok-ayaklı havuz verimsizliğiyle ganyan seviyesinde verginin buluştuğu TEK bahis.

H1 tam olarak şunu sorar: **ÇİFTE havuzu da Altılı havuzu gibi kötü kalibre mi?**
Değilse kol burada kapanır ve model kurulmaz.

=====================================================================================
ÖN-KAYITLI ÖLÇÜT — SONUÇLAR GÖRÜLMEDEN YAZILDI VE GİT'E MÜHÜRLENDİ (K33/K52)
=====================================================================================
1) KAPSAM: yalnız 2026 (K125'te ÇİFTE biriminin 1,00 TL olduğu YALNIZ bu yıl için
   dayanaklandırıldı; başka yılın birimi bilinmiyor).

2) OLAY: ard arda iki koşu; ikincisinde ÇİFTE temettüsü yayımlanmışsa bir fırsattır.
   Bedel her fırsatta 1,00 TL (tek kombinasyon). Ödül: seçim kazanan çiftse temettü, yoksa 0.

3) ÜÇ STRATEJİ — ve aralarındaki SIZINTI FARKI açıkça ayrılır (K97/K111 tuzağı):
   Ç1 "kapanış favorisi x kapanış favorisi"  -> **SIZINTILI ÜST SINIR.** Kupon ayak 1'den
       ÖNCE alınır; ayak 2'nin kapanış oranı o an HENÜZ YOKTUR. Oynanamaz, yalnız tavan.
   Ç2 "ayak1 kapanış favorisi + ayak2 MUHTEMEL favorisi" -> **UYGULANABİLİR.** Muhtemel oran
       (morning line) bahis kapanmadan önce bellidir. Asıl ölçüm budur.
   Ç3 "her ayakta rastgele at" -> **HAVUZ ORTALAMASI** (K72'nin Altılı'da kullandığı zemin).
       2.000 tekrar, olay başına yeni çekiliş.

4) KARŞILAŞTIRMA ZEMİNİ — K72'nin Altılı ölçümü (aynı mantık, farklı ürün):
       rastgele kombinasyon %40,4  ·  saf favori %82,6  ->  **FARK +42,2 puan**
   Altılı havuzunun kötü kalibre olduğunun kanıtı buydu.

5) HÜKÜM (eşik sonuç görülmeden sabitlendi):
   ÖLÇÜT = Ç2 iadesi − Ç3 iadesi (puan). Olay-bootstrap %90 GA, 2.000 tekrar.
     - fark >= +15 puan VE %90 GA'nın tamamı sıfırın üstünde
           -> **H1 GEÇTİ**, havuz sömürülebilir biçimde kalibresiz; kol H2'ye ilerler.
     - aksi halde -> **H1 DÜŞTÜ, ÇİFTE KOLU KAPANIR.** Model kurulmaz.
   +15 puan neden: kesinti %27,2. Kenar umudu için yanlılığın verginin en az yarısını
   kapatması gerekir. Keyfî bir sayı ama SONUÇ GÖRÜLMEDEN bağlandı.

6) İKİNCİ, BAĞIMSIZ OKUMA (hüküm ÜRETMEZ, yalnız bağlam): Ç2'nin HAM ROI'si. Bu sayı
   "çifte oynasaydık ne olurdu"nun doğrudan cevabıdır ve kesintiyle kıyaslanabilir:
   ROI ~ −%27 ise havuz verimli · ROI belirgin daha iyiyse yanlılık var.

7) KALİTE KAPISI: iki ayağın da tek kazananı olmalı (beraberlik dışarıda), iki ayakta da
   kapanış VE muhtemel oran dolu olmalı, temettü kombinasyonu gerçek kazananlarla
   doğrulanmalı. Atılan olay sayısı raporlanır.

8) DOKUNULMAYANLAR: hiçbir dosyaya yazılmaz. Config, dağıtıcı, ağırlık, canlı akış — hiçbiri.
=====================================================================================
"""
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
SONUC = KOK / "veri" / "ham" / "sonuclar"
YIL = "2026"
BOOT = 2000
ESIK_PUAN = 15.0
RNG = np.random.default_rng(20260827)

DESEN = re.compile(r"([^()]+?)\(([^)]*)\):\s*([\d.,]+)\s*TL", re.UNICODE)


def nrm(a):
    return " ".join(re.sub(r"^\s*\d+\.\s*", "", a).strip().split())


def tl(s):
    try:
        return float(s.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def kosular():
    d = pd.read_csv(KOK / "veri" / "katilim.csv",
                    usecols=["race_kod", "tarih", "sehir", "kosu_no", "no",
                             "ganyan_kapanis", "ganyan_muhtemel", "sonuc", "kosmaz"],
                    low_memory=False)
    d = d[d["tarih"].astype(str).str[-4:] == YIL].copy()
    d = d[~d["kosmaz"].fillna(False).astype(bool)]
    for c in ("no", "sonuc", "ganyan_kapanis", "ganyan_muhtemel"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=["no"])

    T, kart = {}, defaultdict(list)
    for rk, g in d.groupby("race_kod"):
        w = g[g["sonuc"] == 1]
        kap, muh = g["ganyan_kapanis"].to_numpy(float), g["ganyan_muhtemel"].to_numpy(float)
        nos = g["no"].to_numpy(int)
        T[int(rk)] = {
            "no": nos,
            "kazanan": int(w["no"].iloc[0]) if len(w) == 1 else None,
            "fav_kap": int(nos[np.nanargmin(kap)]) if np.isfinite(kap).any() else None,
            "fav_muh": int(nos[np.nanargmin(muh)]) if np.isfinite(muh).any() else None,
            "saha": len(nos),
        }
        kart[(g["tarih"].iloc[0], g["sehir"].iloc[0])].append((int(g["kosu_no"].iloc[0]), int(rk)))
    kart = {k: [r for _, r in sorted(v)] for k, v in kart.items()}
    return T, kart


def firsatlar(T, kart):
    """(ayak1, ayak2, temettu) listesi — kalite kapısından geçenler."""
    yer = {}
    for k, dizi in kart.items():
        for i, rk in enumerate(dizi):
            yer[rk] = (k, i)
    out, atilan = [], defaultdict(int)
    for f in sorted(SONUC.glob(f"{YIL}*.json")):
        try:
            o = json.loads(f.read_text(encoding="utf-8"))
        except Exception:                                        # noqa: BLE001
            continue
        for kosu in (o.get("kosular") or []):
            try:
                rk = int(kosu.get("KOD"))
            except (TypeError, ValueError):
                continue
            if rk not in yer or rk not in T:
                continue
            k, i = yer[rk]
            if i < 1:
                continue
            p = kart[k][i - 1]
            if p not in T:
                continue
            A, B = T[p], T[rk]
            for ad, kombo, para in DESEN.findall(kosu.get("emiParasalNeticeler_tr") or ""):
                if nrm(ad) != "ÇİFTE":
                    continue
                d = tl(para)
                pc = kombo.split("/")
                if d is None or len(pc) != 2:
                    atilan["biçim"] += 1
                    continue
                try:
                    a1 = [int(x) for x in pc[0].split(",")]
                    a2 = [int(x) for x in pc[1].split(",")]
                except ValueError:
                    atilan["biçim"] += 1
                    continue
                if len(a1) != 1 or len(a2) != 1:
                    atilan["beraberlik"] += 1
                    continue
                if A["kazanan"] is None or B["kazanan"] is None:
                    atilan["kazanan yok"] += 1
                    continue
                if a1[0] != A["kazanan"] or a2[0] != B["kazanan"]:
                    atilan["kombo tutmadı"] += 1
                    continue
                if None in (A["fav_kap"], A["fav_muh"], B["fav_kap"], B["fav_muh"]):
                    atilan["oran eksik"] += 1
                    continue
                out.append((A, B, d))
    return out, atilan


def boot(x):
    a = np.asarray(x, float)
    idx = RNG.integers(0, len(a), size=(BOOT, len(a)))
    return a[idx].mean(axis=1)


def main():
    print("=" * 100)
    print(f"K126 — ÇİFTE H1 KAPISI: havuz kötü kalibre mi? ({YIL}, salt-okunur)")
    print("Ölçüt betiğin başında ÖN-KAYITLI. Eşik: Ç2 − Ç3 >= +15 puan, GA sıfırın üstünde.")
    print("=" * 100)
    T, kart = kosular()
    F, atilan = firsatlar(T, kart)
    print(f"  {YIL} koşu: {len(T):,} · kart: {len(kart):,} · KULLANILAN ÇİFTE fırsatı: {len(F):,}")
    print("  atılan: " + " · ".join(f"{k} {v:,}" for k, v in sorted(atilan.items())))
    if len(F) < 200:
        print("  YETERSİZ ÖRNEKLEM -> hüküm yok.")
        return

    c1 = np.array([d if (A["fav_kap"] == A["kazanan"] and B["fav_kap"] == B["kazanan"]) else 0.0
                   for A, B, d in F])
    c2 = np.array([d if (A["fav_kap"] == A["kazanan"] and B["fav_muh"] == B["kazanan"]) else 0.0
                   for A, B, d in F])
    # C3: rastgele at, olay basina yeni cekilis, BOOT tekrar
    pA = np.array([1.0 / A["saha"] for A, B, d in F])
    pB = np.array([1.0 / B["saha"] for A, B, d in F])
    dv = np.array([d for A, B, d in F])
    c3_bek = dv * pA * pB                       # rastgele stratejinin OLAY BASINA beklentisi

    print("\n" + "-" * 100)
    print(f"  {'strateji':>52} {'isabet':>8} {'İADE':>9} {'%90 GA':>17}")
    print("-" * 100)
    satir = [
        ("Ç1  kapanış fav x kapanış fav   [SIZINTILI ÜST SINIR]", c1),
        ("Ç2  ayak1 kapanış fav + ayak2 MUHTEMEL fav  [UYGULANABİLİR]", c2),
        ("Ç3  her ayakta rastgele at   [HAVUZ ORTALAMASI]", c3_bek),
    ]
    iade = {}
    for ad, v in satir:
        b = boot(v)
        iade[ad[:2]] = (100 * v.mean(), 100 * np.percentile(b, 5), 100 * np.percentile(b, 95))
        isabet = int((v > 0).sum()) if ad.startswith(("Ç1", "Ç2")) else -1
        i_s = f"{isabet:,}" if isabet >= 0 else "—"
        print(f"  {ad:>52} {i_s:>8} {100*v.mean():>8.1f}% "
              f"[{100*np.percentile(b,5):>6.1f} ..{100*np.percentile(b,95):>6.1f}]")

    fark = c2 - c3_bek
    fb = boot(fark)
    fo, flo, fhi = 100 * fark.mean(), 100 * np.percentile(fb, 5), 100 * np.percentile(fb, 95)
    print("\n" + "=" * 100)
    print("HÜKÜM (ön-kayıtlı madde 5)")
    print("=" * 100)
    print(f"  ÖLÇÜT = Ç2 − Ç3 = {fo:+.1f} puan   %90 GA [{flo:+.1f} .. {fhi:+.1f}]")
    print(f"  Zemin: K72'nin Altılı'daki aynı farkı **+42,2 puan**tı (havuz kötü kalibre).")
    gecti = (fo >= ESIK_PUAN) and (flo > 0)
    if gecti:
        print(f"\n  -> H1 GEÇTİ (fark >= +{ESIK_PUAN:.0f} puan ve GA sıfırın üstünde).")
        print("     ÇİFTE havuzu sömürülebilir biçimde kalibresiz. Kol H2'ye (kenar) ilerler.")
    else:
        neden = ("fark eşiğin altında" if fo < ESIK_PUAN else "GA sıfırı içeriyor")
        print(f"\n  -> H1 DÜŞTÜ ({neden}). **ÇİFTE KOLU KAPANIR.** Model kurulmaz.")

    print("\n" + "-" * 100)
    print("  İKİNCİ OKUMA (madde 6 — hüküm üretmez, bağlam):")
    for ad in ("Ç1", "Ç2", "Ç3"):
        o, lo, hi = iade[ad]
        print(f"     {ad} ham ROI = {o-100:+.1f}%   (K125 ölçtüğü kesinti: −%27,2)")


if __name__ == "__main__":
    main()
