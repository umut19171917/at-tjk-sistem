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
import math
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


def kupon_kur_acgozlu(ayak_atlari, max_kombo):
    """K65: ACGOZLU (isabet-maksimize) dagitici. Kapsam esigi ve budama YOKTUR.
    Her ayakta 1 atla basla; butce dolana dek "kazanc/bedel orani" en yuksek ati ekle.
    Matematik: max PI(P_i) s.t. PI(n_i) <= C  ->  loglarda acgozlu sirt cantasi;
      kazanc = log(1 + p_yeni / P_i)   (o ayakta kapsanan olasiligin oransal artisi)
      bedel  = log((k+1)/k)            (kombo sayisinin oransal artisi)
    Kural yazmadan kaos ayagina cok at, net ayaga TEK at koyar (banker kendiliginden olusur).

    UYARI (K65 backtest, 1455 OOS olay): bu dagitici 6/6 SAYISINI artirir (185->225 @900)
    ama PARAYI kotulestirir (ROI(6) -41,2% -> -55,0%), cunku guvenilen ayaga tek at koymak =
    kamu favorisine tek at = kalabalik havuz -> ort. temettu yariya duser (1.656->798 TL @96)
    ve buyuk odemeler sistematik kacar. CANLIDA yalnizca GOZLEM akisi olarak kullanilir
    (config "acgozlu", bkz. altili_canli.KONFIG); asil kupon mantigi kupon_kur'dur.

    ayak_atlari: 6 elemanli liste; her eleman [(no, bot2), ...]. Doner: 6 elemanli set listesi."""
    sr = [sorted([(no, p) for no, p in a if pd.notna(p) and p > 0], key=lambda x: -x[1])
          for a in ayak_atlari]
    if len(sr) != 6 or any(len(s) == 0 for s in sr):
        return [set() for _ in range(6)]
    k = [1] * 6                                   # her ayakta secili at sayisi
    P = [s[0][1] for s in sr]                     # o ayakta kapsanan olasilik
    while True:
        kombo = int(np.prod(k))
        en_iyi, en_oran = None, 0.0
        for j in range(6):
            if k[j] >= len(sr[j]):
                continue
            if kombo // k[j] * (k[j] + 1) > max_kombo:      # bu at butceyi tasirir
                continue
            p = sr[j][k[j]][1]
            bedel = math.log((k[j] + 1) / k[j])
            oran = (math.log1p(p / P[j]) / bedel) if (P[j] > 0 and bedel > 0) else 0.0
            if oran > en_oran:
                en_oran, en_iyi = oran, j
        if en_iyi is None:
            break
        j = en_iyi
        P[j] += sr[j][k[j]][1]
        k[j] += 1
    return [set(no for no, _ in sr[j][:k[j]]) for j in range(6)]


def ayrisma_skoru(bot1_p, kamu_p):
    """K68: bir ayakta Bot1 (oran-kor) ile KAMU ne kadar ayri dusuyor?
    Toplam degisim uzakligi: 0.5*sum|p1-pk|, [0,1]. 0 = ayni fikirdeler, 1 = tamamen ayri.
    Bos/gecersiz girdi -> 0.0 (yani "ayrisma yok" -> tarafsiz)."""
    a = np.asarray(list(bot1_p), dtype=float)
    b = np.asarray(list(kamu_p), dtype=float)
    if len(a) == 0 or len(a) != len(b):
        return 0.0
    a = np.nan_to_num(a); b = np.nan_to_num(b)
    sa, sb = a.sum(), b.sum()
    if sa <= 0 or sb <= 0:
        return 0.0
    return float(0.5 * np.abs(a / sa - b / sb).sum())


def kupon_kur_ayrisma(ayak_atlari, agirlik, max_kombo, w=1.0):
    """K68: acgozlu'nun AYRISMA-AGIRLIKLI hali. Secim sirasi HEP verilen puan (canlida Bot2)
    -> isabet korunur; degisen sadece hangi ayaga GENISLIK verildigi.
      kazanc = log(1 + p_yeni/P_i) * (1 + w*D_i)   (D_i = o ayagin ayrisma skoru)
      bedel  = log((k+1)/k)
    w=0 ise saf acgozlu'ya doner.

    UYARI (K68 backtest, 1455 OOS): onceden yazilan uc olcut de DUSTU -- (a) w-monotonlugu
    900'de yok, (b) 12 esli farkin 12'sinde GA sifiri iceriyor, (c) en iyi w butceler arasi
    tutarsiz. Ustelik mevcut kapsam mantigi tum ayrisma varyantlarindan iyi. Gorunen tek iz:
    w buyudukce ort. temettu artiyor (798->1.078 @96). CANLIDA yalnizca GOZLEM akisi.

    ayak_atlari: 6 x [(no, p)]; agirlik: 6 elemanli D listesi. Doner: 6 set."""
    sr = [sorted([(no, p) for no, p in a if pd.notna(p) and p > 0], key=lambda x: -x[1])
          for a in ayak_atlari]
    if len(sr) != 6 or any(len(s) == 0 for s in sr):
        return [set() for _ in range(6)]
    ag = list(agirlik) + [0.0] * 6
    k = [1] * 6
    P = [s[0][1] for s in sr]
    while True:
        kombo = int(np.prod(k))
        en_iyi, en_oran = None, 0.0
        for j in range(6):
            if k[j] >= len(sr[j]):
                continue
            if kombo // k[j] * (k[j] + 1) > max_kombo:
                continue
            p = sr[j][k[j]][1]
            bedel = math.log((k[j] + 1) / k[j])
            kazanc = math.log1p(p / P[j]) * (1.0 + w * float(ag[j]))
            oran = kazanc / bedel if (P[j] > 0 and bedel > 0) else 0.0
            if oran > en_oran:
                en_oran, en_iyi = oran, j
        if en_iyi is None:
            break
        j = en_iyi
        P[j] += sr[j][k[j]][1]
        k[j] += 1
    return [set(no for no, _ in sr[j][:k[j]]) for j in range(6)]


# K92: uzak-ayak kalibrasyonu. Degerler OLCULDU (altili_suruklenme C bolumu, n=87 kosu,
# eslesmis: ayni kosunun uzak ve yakin fotografi):
#   uzak (>75 dk)  lambda = 0,65  %90 GA [0,47 .. 0,88]  -> 1'i ICERMIYOR, duzeltme GEREKLI
#   yakin (<=75 dk) lambda = 0,98  %90 GA [0,77 .. 1,22]  -> 1'i ICERIYOR, null kullanilir
# Yakinda 1,0 (=degisiklik yok) secildi: (a) GA null'u iceriyor, (b) boylece v2 ile v1
# arasindaki HER fark yalnizca uzak-ayak duzeltmesine atfedilebilir (temiz atif).
LAM_UZAK = 0.65
LAM_YAKIN = 1.0
UZAK_ESIK_DK = 75          # ayak 1-2 yakin (~30/60 dk), ayak 3-6 uzak (~90-180 dk)


def kupon_kur_kalibre(ayak_atlari, ayak_dk, max_kombo,
                      lam_uzak=LAM_UZAK, lam_yakin=LAM_YAKIN, esik=UZAK_ESIK_DK):
    """K92: her ayagin olasilik vektorunu KENDI mesafesinin olculmus lambda'siyla duzlestirip
    ayni acgozlu dagitima verir.  p_kalibre = normalize(p^lambda)

    NEDEN (K79 teshis + K92 olcum): kupon 1. ayaga 30 dk kala kurulur; 6. ayak o an ~180 dk
    uzaktadir ve havuzu neredeyse bostur -> carpik oran -> SAHTE bir favori. Acgozlu olasilik
    vektorunun SIVRILIGINE gore genislik dagittigi icin bu sahte favoriye kanip en az ati
    oraya yazar. lambda<1 ile duzlestirilince sahte sivrilik erir, gercek sivrilik kalir
    -> banker YASAKLANMAZ, hak edilmesi gerekir (kullanicinin 31 Tem sarti).

    ayak_dk: her ayagin kupon anindaki posta-uzakligi (dakika). None -> yakin sayilir.
    UYARI: lambda BACKTEST EDILEMEZ (arsivde gun-ici oran serisi yok; oran_log bu yuzden var).
    Ileri-yonlu olcum: acgozlu900 ile ayak-ayak kiyaslanir."""
    yeni = []
    for atlar, dk in zip(ayak_atlari, ayak_dk):
        lam = lam_uzak if (dk is not None and dk > esik) else lam_yakin
        v = [(no, float(p)) for no, p in atlar if pd.notna(p) and p > 0]
        if not v:
            yeni.append([])
            continue
        if lam == 1.0:
            yeni.append(v)
            continue
        q = [(no, p ** lam) for no, p in v]
        s = sum(x for _, x in q)
        yeni.append([(no, x / s) for no, x in q] if s > 0 else [])
    return kupon_kur_acgozlu(yeni, max_kombo)


def kupon_kur_birlesim(ayak_bot2, ayak_bot1, max_kombo):
    """K90: BIRLESIM dagitici — iki botun tamamlayiciligini kullanir.
    Her ayakta her atin skoru = max(bot1_norm, bot2_norm); vektor normalize edilip
    ayni acgozlu dagitima verilir. Dogal davranis: iki bot AYNI atlari seviyorsa
    dagilim sivri kalir -> kupon daralir (gercek guven); FARKLI atlari seviyorsa
    kutle yayilir -> kupon genisler (belirsizlik sinyali).
    GEREKCE (K89 olcumu, 78 eslesmis ayak): kamu botlari favoride %85, bot1 surprizde
    %42; bot1 13 benzersiz ayak yakaladi, acgozlu 0 -> iki kaynak TAMAMLAYICI.
    max (karisim degil) secildi cunku birlesim anlami 'IKI bottan biri oynardiysa
    kuponda olsun'dur; 0,5*karisim bir botun cok sevdigi ati yariya dusurur."""
    birles = []
    for a2, a1 in zip(ayak_bot2, ayak_bot1):
        d2 = {no: p for no, p in a2 if pd.notna(p) and p > 0}
        d1 = {no: p for no, p in a1 if pd.notna(p) and p > 0}
        s2, s1 = sum(d2.values()), sum(d1.values())
        birles.append([(no, max(d2.get(no, 0.0) / s2 if s2 else 0.0,
                                d1.get(no, 0.0) / s1 if s1 else 0.0))
                       for no in (set(d2) | set(d1))])
    return kupon_kur_acgozlu(birles, max_kombo)


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
