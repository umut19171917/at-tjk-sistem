"""
altili_backtest.py — ALTILI KUPON BACKTEST'i (K52): "en efektif kupon" mantigini tarihsel
veride olcer. CANLI SISTEME / paper'a / K42'ye DOKUNMAZ. Salt offline analiz.

KRITERLER (kullanicinin sorusu + web-dogrulanmis Pick-6 teorisi + ham-veri gercekleri):
  1. SONDAN-AGIRLIK: TJK odeme merdiveni sondan kesilir (6/5/4/3'lu = son N ayak).
     -> 4-5-6. ayaklar odeme icin ZORUNLU; erken ayaklarda (1-2-3) banker'a yatkin ol.
  2. BANKER/SPREAD: her ayakta model guveni yuksekse tek at (banker), dagilmissa genislet.
     Genisleme, atlari Bot2'ye gore kumulatif esik doldurana dek ekleyerek yapilir.
  3. BUTCE SINIRI: kombinasyon = ayak-secim-sayilarinin carpimi; belli bir tavani asamaz
     (asarsa en belirsiz ayaktan kisilir). "cok genis/yuksek tutarli yapma" kurali.
  4. KADEMELI ODEME: 6 tutmazsa son-5 / son-4 / son-3 konsolasyonlari da sayilir (altili_tam).

Puanlar: veri/altili_olasilik.csv (Ingiliz+Arap walk-forward Bot2). Olaylar: veri/altili_tam.csv.
ANALIZ ODAGI: 2025-26 (gercek OOS). Cikti: konsol raporu + bütçe/esik taramasi.
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from itertools import product

KOK = Path(__file__).resolve().parent.parent
EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}


def kupon_kur(ayak_atlari, kapsam_esik, max_kombo, banker_esik):
    """ayak_atlari: 6 elemanli liste; her eleman [(no, bot2), ...] Bot2-azalan sirali.
    Her ayakta: en olasi at banker_esik'i asiyorsa TEK at (banker); yoksa kumulatif kapsam
    esigi (or. 0.75) dolana dek at ekle. Sonra butce: kombo > max ise en belirsiz (en cok atli)
    ayaktan teker teker kis. Doner: 6 elemanli secilen-no listesi (setler)."""
    sec = []
    for atlar in ayak_atlari:
        if not atlar:
            sec.append(set())
            continue
        atlar = sorted(atlar, key=lambda x: -x[1])
        if atlar[0][1] >= banker_esik:
            sec.append({atlar[0][0]})          # banker
            continue
        kum, secilen = 0.0, []
        for no, p in atlar:
            secilen.append(no)
            kum += p
            if kum >= kapsam_esik:
                break
        sec.append(set(secilen))
    # butce: kombo carpimi max_kombo'yu asarsa en genis ayaktan kis (belirsizden buda)
    while np.prod([len(s) for s in sec]) > max_kombo:
        i = max(range(6), key=lambda j: len(sec[j]))
        if len(sec[i]) <= 1:
            break
        # o ayakta en dusuk Bot2'li ati at
        atlar = sorted(ayak_atlari[i], key=lambda x: -x[1])
        for no, _ in reversed(atlar):
            if no in sec[i]:
                sec[i].discard(no)
                break
    return sec


def degerlendir(olay, puan_map, puan_map_full, kapsam_esik, max_kombo, banker_esik,
                birim=1.0, kademeli=True):
    """Tek Altili olayi icin kupon kur, odemeyi hesapla. Doner (maliyet, getiri, alti_tuttu)
    veya None (ayak puani/kazanani eksikse).
    kademeli=True: 6 tutmazsa son-5/4/3 teselli de sayilir (VARSAYIM — TJK'da teselli var mi
      KESIN dogrulanmadi). kademeli=False: SADECE 6 tutturan oder (en-kotu/muhafazakar sinir)."""
    legs = [int(olay[f"leg{i+1}"]) for i in range(6)]
    ayak_atlari, kaz = [], []
    for rk in legs:
        atlar = puan_map.get(rk)
        if not atlar:
            return None                        # ayagin puani yok -> olay backtest disi
        ayak_atlari.append(atlar)
        w = [no for no, p, k in puan_map_full.get(rk, []) if k == 1]
        kaz.append(w[0] if w else None)
    if any(k is None for k in kaz):
        return None

    sec = kupon_kur(ayak_atlari, kapsam_esik, max_kombo, banker_esik)
    nkombo = int(np.prod([len(s) for s in sec]))
    if nkombo == 0:
        return None
    maliyet = nkombo * birim

    tut = [kaz[i] in sec[i] for i in range(6)]     # her ayagi tutturduk mu
    getiri, alti = 0.0, 0
    kademeler = (6, 5, 4, 3) if kademeli else (6,)
    # sondan kesik: 6'li hepsi, 5'li son5, 4'lu son4, 3'lu son3. En yuksek tutan kademe odenir.
    for n in kademeler:
        if all(tut[6 - n:]):                        # son n ayak tuttu
            div = olay.get(f"t{n}_div")
            if pd.notna(div):
                # tutan kombo sayisi = ilk (6-n) ayaktaki secim carpimi (o ayaklar "herhangi");
                # son n ayakta kazanani tutan tek yol. 6'li'da onceki=1.
                onceki = int(np.prod([len(sec[j]) for j in range(6 - n)])) if n < 6 else 1
                getiri += onceki * birim * div
                if n == 6:
                    alti = 1
                break                              # sondan en uzun tutan kademe -> dur
    return maliyet, getiri, alti


def main():
    puan = pd.read_csv(KOK / "veri" / "altili_olasilik.csv", low_memory=False)
    olay = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    olay["yil"] = pd.to_datetime(olay["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    olay = olay[~olay["sehir"].isin(EXCL)]         # izinli pist (proje kapsami)

    # race_kod -> [(no, bot2), ...]  ve  full: [(no, bot2, kazandi)]
    puan_map, puan_map_full = {}, {}
    for rk, g in puan.groupby("race_kod"):
        puan_map[rk] = list(zip(g["no"], g["bot2"]))
        puan_map_full[rk] = list(zip(g["no"], g["bot2"], g["kazandi"]))

    print("=" * 74)
    print("ALTILI BACKTEST (K52) — offline; canliya/paper'a DOKUNMAZ")
    print(f"olay (izinli pist): {len(olay)} | puanli kosu: {len(puan_map)}")
    print("ODAK: 2025-26 (gercek OOS). ROI = (toplam getiri - toplam maliyet)/maliyet")
    print("=" * 74)

    def tara(kayitlar, kademeli):
        print(f"{'kapsam':>7} {'banker':>7} {'maxK':>6} {'oynanan':>8} {'ort.kombo':>9} "
              f"{'maliyet':>9} {'getiri':>10} {'ROI%':>8} {'6tut':>5} {'6suz-ROI%':>9}")
        for kapsam_esik in (0.60, 0.75, 0.90):
            for banker_esik in (0.55, 0.70):
                for max_kombo in (24, 96, 288):
                    tmal = tget = tget_6suz = 0.0
                    noyn = alti = 0
                    for o in kayitlar:
                        r = degerlendir(o, puan_map, puan_map_full, kapsam_esik, max_kombo,
                                        banker_esik, kademeli=kademeli)
                        if r is None:
                            continue
                        mal, get, a6 = r
                        tmal += mal; tget += get; noyn += 1; alti += a6
                        if not a6:                     # 6 tutmayan olaylarin getirisi (jackpot haric)
                            tget_6suz += get
                    roi = (tget - tmal) / tmal * 100 if tmal else float("nan")
                    # jackpot'suz ROI: en buyuk kazanclarin (6 tutturma) varyansini disla
                    roi6suz = (tget_6suz - tmal) / tmal * 100 if tmal else float("nan")
                    ortk = tmal / noyn if noyn else 0
                    print(f"{kapsam_esik:>7.2f} {banker_esik:>7.2f} {max_kombo:>6} {noyn:>8} "
                          f"{ortk:>9.1f} {tmal:>9.0f} {tget:>10.0f} {roi:>+8.1f} {alti:>5} {roi6suz:>+9.1f}")

    oos = list(olay[olay.yil >= 2025].to_dict("records"))
    tum = list(olay.to_dict("records"))
    print("\n" + "#" * 74)
    print("# SENARYO A: KADEMELI ODEME ACIK (6 tutmazsa 5/4/3 teselli sayilir)")
    print("#   VARSAYIM — TJK'da teselli KESIN dogrulanmadi (web belirsiz). Iyimser sinir.")
    print("#" * 74)
    print("\n### OOS (2025-26) ###"); tara(oos, True)
    print("\n### TUM (2021-26) ###"); tara(tum, True)
    print("\n" + "#" * 74)
    print("# SENARYO B: KADEMELI KAPALI (SADECE 6 tutturan oder) — muhafazakar/en-kotu sinir")
    print("#" * 74)
    print("\n### OOS (2025-26) ###"); tara(oos, False)
    print("\n### TUM (2021-26) ###"); tara(tum, False)


if __name__ == "__main__":
    main()
