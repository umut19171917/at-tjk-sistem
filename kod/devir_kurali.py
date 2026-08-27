# -*- coding: utf-8 -*-
"""
devir_kurali.py — K135 / BEKLEYENLER #5: FAVORİ-DEVRİ kuralının sicilimize etkisi. SALT-OKUNUR.

KURAL: Kupona yazdığımız bir at, kupon kurulduktan SONRA çıkarsa (KOSMAZ), TJK'da o ayaktaki
pay **posta-favorisine devreder** — yani bilet o ayakta favoriyi yazmış sayılır. Kâğıt
sistemimiz bunu uygulamıyor; çıkan seçim "ölü seçim" sayılıyor (`sonucla_altili` yalnız
kazananı okuyup "bizim seçimimizde mi" diye bakar).

NEDEN CANLI KODA DOKUNULMUYOR (bilinçli karar, K135):
  Etkinin yönü ZATEN muhafazakâr — kuralın yokluğu sicili olduğundan KÖTÜ gösterir, asla
  yanlış-pozitif üretmez. Ölçüldü (K135): 4.090 ayakta kural 6 ayağı kurtarırdı ama
  **altısında da diğer ayaklar tutmamıştı** → en iyi ihtimalle 5/6, Altılı'da 5/6 ödemez.
  **Para sonucuna etkisi TAM OLARAK SIFIR.** Çalışan bir sisteme sıfır faydalı bir değişiklik
  için dokunmak kötü takas. Bunun yerine bu ARAÇ yazıldı: istendiği zaman koşulur, sicilin
  ne kadar karamsar olduğunu söyler, hiçbir şeye yazmaz.

NE ZAMAN YENİDEN BAKILMALI: bu betik "6/6 OLURDU" satırı üretirse. O gün kural gerçekten
para değiştirmiş demektir ve canlı puanlayıcıya eklenmesi tartışılır.

KAYNAK: veri/altili_kupon.csv (kâğıt kuponlar) + veri/katilim.csv (kosmaz, sonuç, kapanış).
"""
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent


def yukle():
    kp = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    kp = kp[kp["tuttu"].notna()].copy()
    k = pd.read_csv(KOK / "veri" / "katilim.csv",
                    usecols=["race_kod", "no", "sonuc", "kosmaz", "ganyan_kapanis"],
                    low_memory=False)
    for c in ("no", "sonuc", "ganyan_kapanis"):
        k[c] = pd.to_numeric(k[c], errors="coerce")
    k["ks"] = k["kosmaz"].fillna(False).astype(bool)
    R = {}
    for rk, g in k.groupby("race_kod"):
        r = g[~g["ks"]]
        w = r["no"][r["sonuc"] == 1]
        fav = None
        if r["ganyan_kapanis"].notna().any():
            fav = r["no"][r["ganyan_kapanis"].idxmin()]
        R[int(rk)] = {
            "ks": set(g["no"][g["ks"]].dropna().astype(int)),
            "kaz": int(w.iloc[0]) if len(w) == 1 else None,
            "fav": int(fav) if fav is not None and not pd.isna(fav) else None,
        }
    return kp, R


def main():
    kp, R = yukle()
    say = Counter()
    kurtulan = []
    for _, r in kp.iterrows():
        info = R.get(int(r["race_kod"]))
        if info is None or info["kaz"] is None:
            say["veri yok"] += 1
            continue
        sec = {int(x) for x in str(r["secim"]).split(",") if x.strip().isdigit()}
        if not sec:
            continue
        say["toplam ayak"] += 1
        cikan = sec & info["ks"]
        if not cikan:
            continue
        say["seçimde ÇIKAN at var"] += 1
        if info["kaz"] in sec:
            say["  zaten tutmuştu"] += 1
            continue
        if info["fav"] is None:
            say["  favori bilinmiyor"] += 1
            continue
        if info["fav"] == info["kaz"]:
            say["  >>> DEVİR KURALI AYAĞI KURTARIRDI"] += 1
            kurtulan.append((r["tarih"], r["pist"], r["seq"], r["config"], r["ayak"],
                             sorted(sec), sorted(cikan), info["fav"]))
        else:
            say["  favori kazanmadı -> fark yok"] += 1

    print("=" * 92)
    print("K135 — FAVORİ-DEVRİ KURALI: kâğıt sicilimizi ne kadar karamsar gösteriyor?")
    print("SALT-OKUNUR. Canlı puanlayıcı DEĞİŞTİRİLMEZ (gerekçe: betiğin başındaki not).")
    print("=" * 92)
    for a, c in say.most_common():
        print(f"  {a:>36}: {c:>7,}")
    t, d = say["toplam ayak"], say["  >>> DEVİR KURALI AYAĞI KURTARIRDI"]
    print(f"\n  oran: {d}/{t:,} ayak = %{100*d/max(t,1):.3f}")

    if not kurtulan:
        print("\n  Kuralın kurtaracağı hiçbir ayak yok -> sicil zaten doğru.")
        return

    print("\n" + "-" * 92)
    print("  ASIL SORU: kurtulan ayak, kuponun DİĞER BEŞ ayağı da tuttuysa para eder.")
    print("-" * 92)
    print(f"  {'tarih':>12} {'pist':>10} {'config':>15} {'ayak':>5} {'diğer 5':>8}  sonuç")
    kritik = 0
    for tar, pist, seq, cfg, ayak, sec, cik, fav in kurtulan:
        g = kp[(kp["tarih"] == tar) & (kp["pist"] == pist) & (kp["seq"] == seq)
               & (kp["config"] == cfg)]
        dig = g[g["ayak"] != ayak]
        tut, n = int(dig["tuttu"].sum()), len(dig)
        if tut == n == 5:
            son = "*** 6/6 OLURDU — CANLI KURALA EKLENMESİ TARTIŞILMALI ***"
            kritik += 1
        else:
            son = f"{tut+1}/6 olurdu (Altılı'da ödemez)"
        print(f"  {str(tar):>12} {str(pist):>10} {str(cfg):>15} {ayak:>5} "
              f"{f'{tut}/{n}':>8}  {son}")

    print("\n" + "=" * 92)
    if kritik == 0:
        print("HÜKÜM: kuralın PARA sonucuna etkisi SIFIR. Canlı koda dokunmak için gerekçe yok.")
        print("Sicil yalnızca 'ayak isabeti' sütununda hafifçe karamsar — yönü güvenli taraf.")
    else:
        print(f"DİKKAT: {kritik} olayda kural 6/6 üretirdi. Canlı puanlayıcıya eklenmesi")
        print("artık tartışılmalı (BEKLEYENLER #5'i yeniden aç).")
    print("=" * 92)


if __name__ == "__main__":
    main()
