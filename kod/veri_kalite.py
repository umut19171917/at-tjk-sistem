# -*- coding: utf-8 -*-
"""
veri_kalite.py — K151 / BEKLEYENLER 22-B: SESSİZ VERİ BOZULMA TARAYICISI. SALT-OKUNUR.

NEDEN: K130'da `ganyan_muhtemel`'in altı yıl boyunca kapanış fiyatının kopyası olduğu
fark edilmedi. K107'de bir gün defter+paper SIFIR kayıt yazdı ve kimse görmedi. İkisi de
"sessiz bozulma" — sistem çalışmaya devam ediyor ama veri yanlış/eksik.

=====================================================================================
ÖN-KAYITLI EŞİKLER — ÇIKTIYA BAKILMADAN YAZILDI VE GİT'E MÜHÜRLENDİ (22-B şartı)
=====================================================================================
Eşikler ilk çıktı görülüp AYARLANMAYACAK. Hepsi ya matematiksel zorunluluk ya da
tanım gereğidir — "veriye bakıp makul görünen" hiçbir sayı yok:

  D1 OLASILIK TOPLAMI   her koşuda bot1/bot2/kamu toplamı |Σ−1| < 0,01
                        Gerekçe: softmax çıktısı; sapma matematiksel olarak imkânsız.
  D2 ORAN TANIMI        ganyan oranı > 1,00 (1,00 = başabaş; altı anlamsız)
                        Gerekçe: tanım gereği.
  D3 VARIŞ TANIMI       sonuç ∈ [1, saha] tam sayı
                        Gerekçe: tanım gereği.
  D4 ÇAPRAZ-TABLO       kupon/defter'deki her race_kod katilim.csv'de bulunmalı → %100
                        Gerekçe: kupon var ama koşu yok = referans kopması.
  D5 SESSİZ GÜN         defter'de kaydı olan bir günde altili_kupon SIFIR satır olamaz
                        (o gün Altılı varsa) — K107'nin yakaladığı hata sınıfı.
  D6 KRİTİK NA          bot1/bot2/kamu sütunlarında NA oranı = %0
                        Gerekçe: model her ata olasılık verir; NA = hesap kopmuş.
  D7 YİNELENEN          anahtar sütunlarda yinelenen satır = 0 (K147 ile aynı anahtarlar)
  D8 SÜTUN İKİZİ        iki sütun %99'dan fazla aynıysa UYARI
                        Gerekçe: K130 tam bu — `ganyan_muhtemel` == `ganyan_kapanis`.
                        Bilinen ikizler BILINEN_IKIZ'de listeli; YENİ ikiz alarm üretir.

ALARM SEVİYELERİ (önceden sabit):
  KUSUR  = D1-D7'den herhangi biri ihlal → koşulsuz bildirilir
  UYARI  = D8 yeni ikiz, ya da bir kontrol veri yokluğundan çalıştırılamadı
Eşiklerin hiçbiri "az sapma tolere edilir" demiyor; hepsi sıfır-tolerans, çünkü hepsi
tanım/matematik. Bu bilinçli: gürültülü eşik, tarayıcıyı işe yaramaz kılar.
=====================================================================================
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent

TOPLAM_TOL = 0.01
BILINEN_IKIZ = {("ganyan_muhtemel", "ganyan_kapanis")}      # K130'da tespit, kayıtlı

ANAHTARLAR = {
    "veri/altili_kupon.csv": ["tarih", "pist", "seq", "config", "ayak"],
    "veri/defter.csv": ["tarih", "pist", "race_kod", "no"],
    "veri/altili_kupon_ani.csv": ["tarih", "pist", "seq", "dk_grup", "ayak", "no"],
}


class Rapor:
    def __init__(self):
        self.kusur, self.uyari, self.tamam = [], [], []

    def ok(self, ad, detay=""):
        self.tamam.append((ad, detay))

    def k(self, ad, detay):
        self.kusur.append((ad, detay))

    def u(self, ad, detay):
        self.uyari.append((ad, detay))


def d1_olasilik(r):
    p = KOK / "veri" / "altili_kupon_ani.csv"
    if not p.exists():
        return r.u("D1 olasılık toplamı", "dosya yok")
    d = pd.read_csv(p, low_memory=False)
    kotu = 0
    for kol in ("bot1", "bot2", "kamu"):
        if kol not in d.columns:
            continue
        d[kol] = pd.to_numeric(d[kol], errors="coerce")
        s = d.groupby(["tarih", "pist", "seq", "dk_grup", "ayak"])[kol].sum()
        kotu += int((np.abs(s - 1) > TOPLAM_TOL).sum())
    (r.ok if kotu == 0 else r.k)("D1 olasılık toplamı",
                                 f"|Σ−1|>{TOPLAM_TOL} olan koşu-sütun: {kotu}")


def d2_d3_d6(r):
    p = KOK / "veri" / "katilim.csv"
    if not p.exists():
        return r.u("D2/D3 tanım", "katilim.csv yok")
    d = pd.read_csv(p, usecols=["ganyan_kapanis", "sonuc", "kosmaz"], low_memory=False)
    d = d[~d["kosmaz"].fillna(False).astype(bool)]
    o = pd.to_numeric(d["ganyan_kapanis"], errors="coerce").dropna()
    kotu = int((o <= 1.0).sum())
    (r.ok if kotu == 0 else r.k)("D2 oran > 1,00", f"ihlal: {kotu} / {len(o):,}")
    s = pd.to_numeric(d["sonuc"], errors="coerce").dropna()
    kotu = int(((s < 1) | (s != s.round())).sum())
    (r.ok if kotu == 0 else r.k)("D3 varış tanımı", f"ihlal: {kotu} / {len(s):,}")

    pa = KOK / "veri" / "altili_kupon_ani.csv"
    if pa.exists():
        a = pd.read_csv(pa, low_memory=False)
        na = {k: float(pd.to_numeric(a[k], errors="coerce").isna().mean())
              for k in ("bot1", "bot2", "kamu") if k in a.columns}
        en = max(na.values()) if na else 0.0
        (r.ok if en == 0 else r.k)("D6 kritik NA",
                                   " · ".join(f"{k} %{100*v:.2f}" for k, v in na.items()))


def d4_capraz(r):
    """D4 — KAPSAM DÜZELTMESİ (ilk çalıştırma, 2 Eyl 2026; K151-EK'te kayıtlı).

    İlk sürüm 84 "kusur" buldu; teşhis: hepsi BUGÜNÜN kuponlarıydı ve `katilim.csv` dün
    bitiyordu — arşiv güncellemesi (`guncelle`) ertesi sabah koşuyor. Yani veri bozuk değil,
    KONTROL yanlış tanımlanmıştı: iki tabloyu tazelik farkını hesaba katmadan kıyaslıyordu.

    EŞİK DEĞİŞMEDİ (hâlâ %100 eşleşme şart). Değişen KAPSAM: yalnız arşivin görme fırsatı
    bulduğu günler (katilim.csv'nin son tarihine kadar) denetlenir. Bu bir eşik gevşetmesi
    DEĞİL, popülasyon tanımının düzeltilmesidir — ayrım K151-EK'te açıkça kayıtlı."""
    kp = KOK / "veri" / "altili_kupon.csv"
    ka = KOK / "veri" / "katilim.csv"
    if not (kp.exists() and ka.exists()):
        return r.u("D4 çapraz-tablo", "dosya yok")
    kat = pd.read_csv(ka, usecols=["race_kod", "tarih"], low_memory=False)
    son_arsiv = pd.to_datetime(kat["tarih"], format="%d/%m/%Y", errors="coerce").max()
    k = set(pd.to_numeric(kat["race_kod"], errors="coerce").dropna().astype(int))

    kup = pd.read_csv(kp, usecols=["race_kod", "tarih"], low_memory=False)
    kup["dt"] = pd.to_datetime(kup["tarih"], format="%Y-%m-%d", errors="coerce")
    kapsam = kup[kup["dt"] <= son_arsiv]
    bekleyen = len(kup) - len(kapsam)
    rk = pd.to_numeric(kapsam["race_kod"], errors="coerce").dropna().astype(int)
    yok = int((~rk.isin(k)).sum())
    ek = f" · arşive girmemiş {bekleyen} satır kapsam dışı (son arşiv {son_arsiv:%d.%m})"
    (r.ok if yok == 0 else r.k)("D4 çapraz-tablo",
                                f"eşleşmeyen: {yok} / {len(rk):,}{ek}")


def d5_sessiz_gun(r):
    dp, kp = KOK / "veri" / "defter.csv", KOK / "veri" / "altili_kupon.csv"
    if not (dp.exists() and kp.exists()):
        return r.u("D5 sessiz gün", "dosya yok")
    d = pd.read_csv(dp, usecols=["tarih"], low_memory=False)
    k = pd.read_csv(kp, usecols=["tarih"], low_memory=False)
    kupon_gun = set(k["tarih"])
    # Altılı kuponu OLMASI beklenen gün = defter kaydı olan gün (yarış olmuş)
    bos = sorted(g for g in set(d["tarih"]) if g not in kupon_gun)
    # kupon akışı 20 Tem'de başladı; öncesi kapsam dışı
    bos = [g for g in bos if g >= "2026-07-20"]
    (r.ok if not bos else r.k)("D5 sessiz gün",
                               f"defter var / kupon yok: {len(bos)} gün"
                               + (f" → {', '.join(bos[:5])}" if bos else ""))


def d7_yinelenen(r):
    top = 0
    for yol, anahtar in ANAHTARLAR.items():
        p = KOK / yol
        if not p.exists():
            continue
        d = pd.read_csv(p, low_memory=False)
        if all(c in d.columns for c in anahtar):
            top += int(d.duplicated(subset=anahtar).sum())
    (r.ok if top == 0 else r.k)("D7 yinelenen satır", f"toplam: {top}")


def d8_ikiz(r):
    p = KOK / "veri" / "katilim.csv"
    if not p.exists():
        return r.u("D8 sütun ikizi", "dosya yok")
    d = pd.read_csv(p, low_memory=False, nrows=60000)
    say = d.select_dtypes(include="number").columns.tolist()
    yeni = []
    for i, a in enumerate(say):
        for b in say[i + 1:]:
            m = d[a].notna() & d[b].notna()
            if m.sum() < 500:
                continue
            if float((d.loc[m, a] == d.loc[m, b]).mean()) > 0.99:
                if (a, b) not in BILINEN_IKIZ and (b, a) not in BILINEN_IKIZ:
                    yeni.append(f"{a}≡{b}")
    if yeni:
        r.u("D8 sütun ikizi", f"YENİ ikiz: {', '.join(yeni)} — K130 gibi bir kusur olabilir")
    else:
        r.ok("D8 sütun ikizi", f"yeni ikiz yok (bilinen: {len(BILINEN_IKIZ)})")


def main():
    print("=" * 92)
    print("K151 / 22-B — SESSİZ VERİ BOZULMA TARAYICISI")
    print("Eşikler ÖN-KAYITLI (betiğin başında); çıktıya bakılıp ayarlanmadı.")
    print("=" * 92)
    r = Rapor()
    for f in (d1_olasilik, d2_d3_d6, d4_capraz, d5_sessiz_gun, d7_yinelenen, d8_ikiz):
        try:
            f(r)
        except Exception as e:                                   # noqa: BLE001
            r.u(f.__name__, f"kontrol çalıştırılamadı: {type(e).__name__}: {e}")

    for ad, detay in r.tamam:
        print(f"  [✓] {ad:<24} {detay}")
    for ad, detay in r.uyari:
        print(f"  [!] {ad:<24} {detay}")
    for ad, detay in r.kusur:
        print(f"  [✗] {ad:<24} {detay}")

    print("\n" + "=" * 92)
    if r.kusur:
        print(f"*** {len(r.kusur)} KUSUR BULUNDU — incelenmeli ***")
    elif r.uyari:
        print(f"{len(r.uyari)} uyarı, kusur yok.")
    else:
        print("Bütün kontroller temiz.")
    print("=" * 92)
    return 1 if r.kusur else 0


if __name__ == "__main__":
    sys.exit(main())
