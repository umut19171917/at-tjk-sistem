"""
altili_canli.py — CANLI ALTILI kupon uretimi + takibi (K53). GERCEK BAHIS DEGIL (K48; +EV yok,
K52 backtest OOS -%32). Amac: izleme/ogrenme — kuponu ilk kosu baslamadan kur, kosular ilerledikce
ayak sonuclarini + nihai Altili isabetini isle, basari oranini ACIK dille/gorselle goster.

AYRI dosya/sayfa: veri/altili_kupon.csv + raporlar/altili.html. defter/paper'a DOKUNMAZ.

Kupon mantigi (K52 backtest'iyle AYNI cekirdek: altili_backtest.kupon_kur):
  banker (Bot2 guveni >= esik -> tek at) + spread (kumulatif kapsam) + butce tavani.
  Hangi config'lerin kuruldugu TEK KAYNAKTAN okunur: asagidaki KONFIG sozlugu ve onun
  "aktif" bayragi (aktif_konfig()/emekli_konfig()). Bu docstring sayi vermez -- K78'de
  ogrenildi: elle yazilan liste bayatliyor. Sayfa girisi de KONFIG'den uretilir.
  EMEKLI config (aktif=False): yeni kupon KURULMAZ, gecmis sicil raporda AYNEN kalir.
Pencere: program BAHISLER_TR'de "N. 6'LI GANYAN bu kosudan baslar" -> o kosudan 6 ardisik kosu.
  Gunde 1-2 Altili olabilir (K46 kesfi); hepsi ayri islenir.
Odeme yapisi (K52): 5/4/3'lu AYRI bahisler, teselli DEGIL -> yalniz 6/6 "tam isabet" kazanc sayilir;
  yine de 5/4/3 sondan-ayak isabetini BILGI olarak gosteririz (ogrenme; para degeri yok).

Kullanim:
    python altili_canli.py --pist ISTANBUL [--tarih YYYY-MM-DD]   # kupon hazirla + HTML
    python altili_canli.py --sonucla                              # bekleyen ayaklari sonucla + HTML
    python altili_canli.py --html                                 # sadece HTML'i tazele + ac
"""
import argparse
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from gunluk import hesapla, getjson, BASE, EXCL  # noqa: E402
from altili_backtest import (kupon_kur, kupon_kur_acgozlu,  # noqa: E402
                             kupon_kur_ayrisma, ayrisma_skoru,
                             kupon_kur_kalibre, UZAK_ESIK_DK, LAM_UZAK)
from duzlestir import vir_float  # noqa: E402
import rapor_ortak as ro  # noqa: E402

KUPON = KOK / "veri" / "altili_kupon.csv"
HTMLA = KOK / "raporlar" / "altili.html"
# K97: kupon KURULURKEN kullanilan olasilik vektoru. Defter'deki model_rank posta-5dk'nin
# siralamasidir; kupon ise ilk ayaktan ~30 dk once TEK seferde kurulur, yani son ayagin karari
# 2-3 saat onceden verilir. Iki siralama farklidir ve karari yargilarken dogrusu BUDUR.
# 09.08 Istanbul 2. Altili: kosu 8'in kazanani sayfada "sistem 10.", kupon aninda 2. sirdaydi.
KUPON_ANI = KOK / "veri" / "altili_kupon_ani.csv"
# K105: dk_grup = bu anlik goruntu HANGI kupon-kurma anina ait (30 / 15). Iki zaman dilimi
# paralel kuruldugu icin anahtara girmek ZORUNDA -- yoksa 15 dk gecisi 30 dk'nin fotografini
# ezer ve K97'nin tum "karar anindaki vektor" kaydi bozulur.
KOL_ANI = ["kayit_ts", "tarih", "pist", "seq", "dk_grup", "ayak", "kosu_no", "race_kod",
           "saat", "dk_kala", "no", "at_ad", "bot1", "bot2", "kamu", "oran", "kaynak"]
# config -> ayarlar. Alanlar:
#   kapsam  : kumulatif kapsam esigi (SADECE dagitim="kapsam" kullanir)
#   kombo   : butce tavani (kombinasyon)
#   dagitim : "kapsam"  = K52 mantigi (kapsam esigi + butce asilinca en kalabalik ayaktan buda)
#             "acgozlu" = K65 isabet-maksimize (log-uzayinda sirt cantasi; kapsam alani KULLANILMAZ)
#             "ayrisma" = K68 acgozlu'nun ayrisma-agirlikli hali
#   puan    : secim hangi olasilikla yapilir -- "bot2" (harman) veya "bot1" (oran-kor)
#   aile    : rapor/Telegram gruplamasi
#   aktif   : K100 -- False ise YENI kupon KURULMAZ ama gecmis sicil AYNEN durur.
#             Config'i sozlukten SILMEK yasak: silinirse raporda o config'in sutunu ve
#             TOPLAM DURUM'daki bedeli/odulu sessizce kaybolur, isleyen bakiye bozulur
#             (kumulatif blok kuponlari CSV'den okur, toplam blok KONFIG'den gezer ->
#             ikisi ayrisir). Emeklilik = bayrak, silme DEGIL.
#
# GECMIS (hepsi kagit; hicbiri "iyilestirme" degil, GOZLEM akisi):
#   K52/K57 : dar/orta/genis  -- asil kupon ailemiz, kapsam mantigi
#   K62     : genis900 yuksek kapsam (0.95) ki derin (5./6. sira) kazananlara ulassin
#   K65     : acgozlu900 -- genis900 ile AYNI butce = kontrollu A/B, tek fark dagitim
#   K67     : bot1_900 -- Bot2 pratikte kamunun kendisi (favori ortakligi %89,9). Bot1 oran-kor,
#             kalabaliktan ayri; buyuk temettu bolgesine eriyor (bot2 225 isabette 50bin ustu
#             SIFIR, bot1 123 isabette 100bin ustu UC kez) ama isabeti dusuk (%29,1 vs %35,7).
#             8 hucreden TEK sinyal veren ve izlenebilir siklikta tutan hucre: acgozlu@900.
#   K68     : ayrisma900 -- "genisligi bot1 ile kamunun ayristigi ayaga ver". Backtest'te
#             onceden yazilan UC OLCUT DE DUSTU (bulgu yok); kullanici karariyla yine de
#             GOZLEM olarak eklendi ("aklimizda soru kalmasin", 2026-07-31).
#             w=1.0 SABIT ve TARANMADI: backtest'te en iyi cikan w'yi secmek overfit olurdu
#             (K33/K52 hindsight yasagi) -> tarafsiz deger.
#   K100 (2026-08-10): kalabalik budandi. dar/genis/genis900/ayrisma900 EMEKLI edildi --
#             216 sonuclanmis ayakta benzersiz katkilari 0/0/2/2 idi ve hicbiri acik bir
#             soruya cevap vermiyordu. ayrisma900 ayrica acgozlu900'un ikizi (canlida
#             ayaklarin %78'inde BIREBIR ayni kupon; backtest McNemar p=0,80).
#             acgozlu900 KALDI cunku acgozlu_v2'nin kontrol grubudur (BEKLEYENLER #9).
#   K100    : bot1_1800 -- kullanici istegi. Backtest'te 900'un getirisi TEK olaya asili
#             (ROI -18,3 ama en buyuk kupon cikinca -53,2); 1800'de -29,2/-46,6 yani
#             GORUNEN ROI kotulesiyor, SANSTAN ARINDIRILMIS ROI iyilesiyor. Amac "buyuk
#             odulleri yakalamak" DEGIL (olculdu: yuksek odullu 5/6'larin donusumu %10,
#             dusuk odullulerin %17 -- butce buyukleri KURTARMIYOR), bot1'i piyangoluktan
#             cikarmak. Olcum degeri dusuk (25 Eyl'e ~35 kupon), GOZLEM akisi olarak eklendi.
#   dk      : K105 -- kupon ILK ayaga kac dk kala kurulur (30 varsayilan). Ayni gun iki
#             farkli anda kupon kurulabilir; her dk grubu KENDI gecisinde kurulur ve
#             birbirinin satirlarina DOKUNMAZ.
#   K105    : orta_15 -- `orta` ile TEK farki kurulma ani (30 -> 15 dk). BEKLEYENLER #4'un
#             canli kolu. Simulasyon (altili_zaman_test) 18 Altilida orta icin +5 ayak
#             gosterdi ama p=0,42 (anlamsiz) ve simulasyonun kendi varsayimlari var
#             (oran_log anlik goruntusu + bot2'nin geri hesaplanmasi). Bu config o
#             varsayimlari ORTADAN KALDIRIR: gercek kupon, gercek kayit.
#             bot1 config'lerine 15 dk ikizi ACILMADI: bot1 orana bakmaz, zamanla
#             DEGISMEZ -> simulasyonda da farki tam olarak +0 cikti (ic kontrol).
AYRISMA_W = 1.0
KONFIG = {
    "dar":        {"kapsam": 0.75, "kombo": 24,  "dagitim": "kapsam",  "puan": "bot2", "aile": "kamu",    "aktif": False, "dk": 30},
    "orta":       {"kapsam": 0.75, "kombo": 96,  "dagitim": "kapsam",  "puan": "bot2", "aile": "kamu",    "aktif": True,  "dk": 30},
    "orta_15":    {"kapsam": 0.75, "kombo": 96,  "dagitim": "kapsam",  "puan": "bot2", "aile": "zaman",   "aktif": True,  "dk": 15},
    "genis":      {"kapsam": 0.75, "kombo": 288, "dagitim": "kapsam",  "puan": "bot2", "aile": "kamu",    "aktif": False, "dk": 30},
    "genis900":   {"kapsam": 0.95, "kombo": 900, "dagitim": "kapsam",  "puan": "bot2", "aile": "kamu",    "aktif": False, "dk": 30},
    "acgozlu900": {"kapsam": 0.95, "kombo": 900, "dagitim": "acgozlu", "puan": "bot2", "aile": "kamu",    "aktif": True,  "dk": 30},
    "bot1_900":   {"kapsam": 0.95, "kombo": 900, "dagitim": "acgozlu", "puan": "bot1", "aile": "temel",   "aktif": True,  "dk": 30},
    "bot1_1800":  {"kapsam": 0.95, "kombo": 1800, "dagitim": "acgozlu", "puan": "bot1", "aile": "temel",  "aktif": True,  "dk": 30},
    "ayrisma900": {"kapsam": 0.95, "kombo": 900, "dagitim": "ayrisma", "puan": "bot2", "aile": "ayrisma", "aktif": False, "dk": 30},
    # K92: uzak ayagin olasiligi OLCULMUS lambda ile duzlestirilir (bkz. kupon_kur_kalibre).
    # acgozlu900 ile TEK farki budur -> aradaki her fark uzak-ayak duzeltmesine atfedilebilir.
    "acgozlu_v2": {"kapsam": 0.95, "kombo": 900, "dagitim": "kalibre", "puan": "bot2", "aile": "kalibre", "aktif": True,  "dk": 30},
}


def dk_gruplari():
    """K105: aktif config'lerin kullandigi kupon-kurma anlari (buyukten kucuge)."""
    return sorted({a.get("dk", 30) for a in aktif_konfig().values()}, reverse=True)


def grup_konfig(dk):
    return {c: a for c, a in aktif_konfig().items() if a.get("dk", 30) == dk}


def aktif_konfig():
    """K100: YENI kupon kurulacak config'ler. Emekliler KONFIG'de kalir (gecmis sicil icin)."""
    return {c: a for c, a in KONFIG.items() if a.get("aktif", True)}


def emekli_konfig():
    return [c for c, a in KONFIG.items() if not a.get("aktif", True)]
AILE_AD = {"kamu":    "KAMU BOTU (bot2 — piyasayı dinler)",
           "zaman":   "ZAMANLAMA KOLU (orta ile aynı kural, 15 dk kala kurulur)",
           "temel":   "TEMEL BOT (bot1 — orana hiç bakmaz)",
           "ayrisma": "AYRIŞMA (bot2 seçer, genişlik ayrışmaya gider)",
           "kalibre": "MESAFE KALİBRELİ (bot2, uzak ayak λ=%.2f ile düzeltilir)" % LAM_UZAK}
BANKER_ESIK = 0.70                     # tek-at banker esigi (tum config ortak)
KOL = ["kayit_ts", "tarih", "pist", "seq", "ilk_saat", "config", "ayak",
       "kosu_no", "race_kod", "saat", "secim", "banker", "nat",
       "kazanan", "tuttu", "sonuclandi"]


def _oku():
    if KUPON.exists():
        return pd.read_csv(KUPON, low_memory=False)
    return pd.DataFrame(columns=KOL)


def _yaz(df):
    df.to_csv(KUPON, index=False, encoding="utf-8", columns=KOL)


def _kupon_ani_yaz(satirlar):
    """K97: kupon anindaki olasilik tablosunu upsert eder.
    K105: anahtar (tarih,pist,seq,DK_GRUP) — dk_grup olmadan 15 dk gecisi 30 dk'nin
    fotografini ezerdi. Eski satirlarda sutun yoksa 30 sayilir (geriye uyum).
    Kupon yeniden kurulursa anlik goruntu de yenilenir ki ikisi hep AYNI ani anlatsin.
    Geri kurulmus (kaynak='geri_kurulan') satirlar da ayni anahtarla ezilir: canli kayit
    her zaman geri kurulana ustundur."""
    if not satirlar:
        return 0
    yeni = pd.DataFrame(satirlar)
    if KUPON_ANI.exists():
        old = pd.read_csv(KUPON_ANI, low_memory=False)
        if "dk_grup" not in old.columns:
            old["dk_grup"] = 30
        old["dk_grup"] = pd.to_numeric(old["dk_grup"], errors="coerce").fillna(30)
        anahtar = set(zip(yeni["tarih"], yeni["pist"], yeni["seq"].astype(int),
                          yeni["dk_grup"].astype(float)))
        tut = [(t, p, int(s), float(dg)) not in anahtar for t, p, s, dg in
               zip(old["tarih"], old["pist"],
                   pd.to_numeric(old["seq"], errors="coerce").fillna(-1), old["dk_grup"])]
        yeni = pd.concat([old[pd.Series(tut, index=old.index)], yeni], ignore_index=True)
    KUPON_ANI.parent.mkdir(parents=True, exist_ok=True)
    yeni.reindex(columns=KOL_ANI).to_csv(KUPON_ANI, index=False, encoding="utf-8")
    return len(satirlar)


# ----------------------------- pencere tespiti -----------------------------
def altili_pencereleri(o):
    """Program JSON'dan Altili pencereleri: [(seq, [6 kosu-dict], ilk_saat)].
    Altili baslangici = BAHISLER_TR'de "6'LI GANYAN" GECEN kosu (bu ifade YALNIZ baslangic
    kosusunda gecer -- 24 Tem cok-Altili ve 25 Tem tek-Altili gunlerinde dogrulandi).
    Iki format: (a) "N. 6'LI GANYAN bu kosudan baslar" -> seq=N (cok-Altili gunu);
    (b) sadece "6'LI GANYAN" listelenir, "baslar" baska bahse bagli (tek-Altili gunu) -> seq sirayla.
    K63: eskiden yalniz (a) yakalaniyordu -> (b) formatindaki gunlerde HIC kupon kurulmuyordu (sessiz kayip)."""
    kos = sorted(o.get("kosular", []),
                 key=lambda k: int(k.get("RACENO") or k.get("NO") or 0))
    pat_ord = re.compile(r"(\d+)\.\s*6'LI GANYAN", re.IGNORECASE)   # acik sira no'su (varsa)
    out, sira = [], 0
    for i, k in enumerate(kos):
        b = k.get("BAHISLER_TR") or ""
        if "6'LI GANYAN" not in b.upper():
            continue
        pencere = kos[i:i + 6]
        if len(pencere) < 6:                 # eksik pencere (program kesik) -> atla
            continue
        sira += 1
        m = pat_ord.search(b)
        seq = int(m.group(1)) if m else sira
        out.append((seq, pencere, str(k.get("SAAT", "")).strip()))
    return out


def _as_int(x):
    try:
        return int(str(x).strip())
    except (ValueError, TypeError):
        return None


# ----------------------------- kupon hazirla -----------------------------
def kupon_hazirla(pist, ymd, tarih, sadece_seq=None, sadece_cfg=None, dk_grup=30):
    """Pistin canli kartini puanla (Ingiliz+Arap), Altili pencereleri icin dar+orta kupon kur,
    deftere upsert. sadece_seq verilirse yalniz o Altili penceresini kurar (takip: her Altili
    kendi ilk kosusundan ~30dk once). Doner: kurulan (pencere x config) sayisi."""
    o = getjson(f"{BASE}/program/{ymd}/full/{pist}.json")
    if o.get("_hata"):
        print(f"{pist} {tarih}: program yok ({o['_hata']})")
        return 0
    pencereler = altili_pencereleri(o)
    if sadece_seq is not None:
        pencereler = [p for p in pencereler if p[0] == sadece_seq]
    if not pencereler:
        print(f"{pist} {tarih}: Altili penceresi bulunamadi (program bahis bilgisi yok/kesik).")
        return 0

    raw, tg, _ = hesapla(pist, ymd)          # tg = puanli satirlar (Ingiliz+Arap); bot2 dolu
    if tg is None or len(tg) == 0:
        print(f"{pist} {tarih}: hicbir kosu puanlanamadi (kapsam disi).")
        return 0
    tg = tg.copy()
    tg["kosu_no_i"] = pd.to_numeric(tg["kosu_no"], errors="coerce")

    yeni_satirlar, ani_satirlar = [], []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    for seq, pencere, ilk_saat in pencereler:
        # her ayagin (no, bot2) VE (no, bot1) listesi + ayrisma skoru
        # -- Bot2'si olmayan ayak varsa pencere ATLANIR (eskisi gibi)
        ayak_atlari, ayak_bot1, ayak_ayr, ayak_meta, eksik = [], [], [], [], False
        ayak_tablo = []                       # K97: ayagin kupon anindaki TAM tablosu
        for k in pencere:
            kno = _as_int(k.get("RACENO") or k.get("NO"))
            g = tg[tg["kosu_no_i"] == kno]
            g = g[pd.to_numeric(g["bot2"], errors="coerce").notna()]
            if len(g) < 4:                    # <4 atli / puansiz ayak -> Altili kurulamaz
                eksik = True
                break
            atlar = [(int(r["no"]), float(r["bot2"])) for _, r in g.iterrows()]
            ayak_atlari.append(atlar)
            ayak_tablo.append(g)
            # K67/K68: bot1 ve kamu ayni satirlarda; biri eksikse o config sessizce atlanir
            b1 = pd.to_numeric(g["bot1"], errors="coerce")
            km = pd.to_numeric(g["kamu"], errors="coerce")
            ayak_bot1.append([(int(r["no"]), float(v)) for (_, r), v in zip(g.iterrows(), b1)
                              if pd.notna(v) and v > 0])
            ayak_ayr.append(ayrisma_skoru(b1.fillna(0.0).values, km.fillna(0.0).values)
                            if km.notna().any() and b1.notna().any() else 0.0)
            ayak_meta.append({"kosu_no": kno, "race_kod": _as_int(k.get("KOD")),
                              "saat": str(k.get("SAAT", "")).strip()})
        # K92: her ayagin KUPON ANINDAKI posta-uzakligi (dk). Kalibreli dagitici bunu kullanir.
        # Saat cozulemezse None -> o ayak "yakin" sayilir (muhafazakar: duzeltme uygulanmaz).
        _simdi = datetime.now()
        ayak_dk = []
        for _meta in ayak_meta:
            try:
                _post = datetime.strptime(f"{tarih} {_meta['saat']}", "%Y-%m-%d %H:%M")
                ayak_dk.append((_post - _simdi).total_seconds() / 60.0)
            except ValueError:
                ayak_dk.append(None)
        if eksik:
            print(f"  {seq}. Altili (kosu {pencere[0].get('RACENO')}): bir ayak kapsam disi -> atlandi")
            continue

        # K97: karar anindaki vektoru AYNEN kaydet (geri kurulmasin, varsayim girmesin).
        # Yardimci kayit -> hatasi kupon kurmayi engellemez (asagidaki yazma da korumali).
        try:
            for ai, gtab in enumerate(ayak_tablo):
                for _, r in gtab.iterrows():
                    ani_satirlar.append({
                        "kayit_ts": ts, "tarih": tarih, "pist": pist, "seq": seq,
                        "dk_grup": dk_grup, "ayak": ai + 1,
                        "kosu_no": ayak_meta[ai]["kosu_no"], "race_kod": ayak_meta[ai]["race_kod"],
                        "saat": ayak_meta[ai]["saat"],
                        "dk_kala": (round(ayak_dk[ai], 1) if ayak_dk[ai] is not None else np.nan),
                        "no": _as_int(r.get("no")), "at_ad": r.get("at_ad"),
                        "bot1": r.get("bot1"), "bot2": r.get("bot2"), "kamu": r.get("kamu"),
                        "oran": r.get("ganyan_muhtemel"), "kaynak": "canli",
                    })
        except Exception as e:                                   # noqa: BLE001
            print(f"  UYARI: {seq}. Altili kupon ani vektoru toplanamadi "
                  f"({type(e).__name__}: {e}) -- kupon kurma etkilenmedi.")

        # K100: emekliler kupon KURMAZ. K105: yalniz bu gecise ait config'ler kurulur --
        # 15 dk gecisi 30 dk'nin satirlarina DOKUNMAMALI (deney kirlenmesin).
        _hedef = (aktif_konfig() if sadece_cfg is None
                  else {c: a for c, a in KONFIG.items() if c in sadece_cfg})
        for cfg, ay in _hedef.items():
            maxk, dagitim = ay["kombo"], ay["dagitim"]
            puanlar = ayak_bot1 if ay["puan"] == "bot1" else ayak_atlari
            if any(len(p) < 1 for p in puanlar):   # bot1 yoksa O CONFIG atlanir (digerleri kurulur)
                print(f"  {seq}. Altili / {cfg}: {ay['puan']} puani eksik -> bu config atlandi")
                continue
            if dagitim == "acgozlu":               # K65: kapsam esigi/budama yok
                sec = kupon_kur_acgozlu(puanlar, maxk)
            elif dagitim == "ayrisma":             # K68: acgozlu + ayrisma agirligi
                sec = kupon_kur_ayrisma(puanlar, ayak_ayr, maxk, AYRISMA_W)
            elif dagitim == "kalibre":             # K92: uzak ayak lambda ile duzlestirilir
                sec = kupon_kur_kalibre(puanlar, ayak_dk, maxk)
            else:
                sec = kupon_kur(puanlar, ay["kapsam"], maxk, BANKER_ESIK)
            if any(len(s) == 0 for s in sec):      # dagitici bos donduyse yazma (bozuk satir olmasin)
                print(f"  {seq}. Altili / {cfg}: secim uretilemedi -> atlandi")
                continue
            for ai in range(6):
                atlar_sirali = sorted(puanlar[ai], key=lambda x: -x[1])
                secili = sec[ai]
                banker = 1 if len(secili) == 1 and atlar_sirali[0][1] >= BANKER_ESIK else 0
                yeni_satirlar.append({
                    "kayit_ts": ts, "tarih": tarih, "pist": pist, "seq": seq,
                    "ilk_saat": ilk_saat, "config": cfg, "ayak": ai + 1,
                    "kosu_no": ayak_meta[ai]["kosu_no"], "race_kod": ayak_meta[ai]["race_kod"],
                    "saat": ayak_meta[ai]["saat"],
                    "secim": ",".join(str(n) for n in sorted(secili)),
                    "banker": banker, "nat": len(secili),
                    "kazanan": np.nan, "tuttu": np.nan, "sonuclandi": np.nan,
                })

    # K97: anlik goruntu YARDIMCI kayittir; hatasi ASLA kupon kurmayi engellememeli.
    # (Kupon kurulmazsa o Altili deneyden duser -- kayip_raporu.py'nin "KURULMAYAN ALTILI"
    #  kalemi, en pahali hasar. Yeni bir dosyaya yazmak icin bu riski almayiz.)
    try:
        _kupon_ani_yaz(ani_satirlar)
    except Exception as e:                                       # noqa: BLE001
        print(f"  UYARI: kupon ani kaydi yazilamadi ({type(e).__name__}: {e}) "
              f"-- kupon kurma etkilenmedi, geri kurma betigi bosluğu doldurur.")
    if not yeni_satirlar:
        return 0
    yeni = pd.DataFrame(yeni_satirlar)
    old = _oku()
    if len(old):
        # upsert: ayni (tarih,pist,seq,config) COZULMEMIS satirlarini degistir, cozulmusleri koru
        anahtar = set(zip(yeni["tarih"], yeni["pist"], yeni["seq"], yeni["config"]))
        coz = old["sonuclandi"].notna()
        ayni = [(t, p, s, c) in anahtar for t, p, s, c in
                zip(old["tarih"], old["pist"], old["seq"], old["config"])]
        old = old[coz | ~pd.Series(ayni, index=old.index)]
        out = pd.concat([old, yeni], ignore_index=True)
    else:
        out = yeni
    _yaz(out)
    n = yeni.groupby(["seq", "config"]).ngroups
    print(f"{pist} {tarih}: {n} kupon kuruldu ({len(pencereler)} Altili x "
          f"{yeni['config'].nunique()} config, {dk_grup} dk grubu"
          + (f"; emekli: {', '.join(emekli_konfig())}" if emekli_konfig() else "") + ").")
    return n


# ----------------------------- Telegram bildirimi (K60) -----------------------------
def _at_ad_map(o):
    """program JSON -> {race_kod: {at_no: at_ad}} (kupon atlarini isimle yazmak icin)."""
    m = {}
    for k in o.get("kosular", []):
        m[_as_int(k.get("KOD"))] = {_as_int(a.get("NO")): a.get("AD") for a in k.get("atlar", [])}
    return m


def bildir_kupon(pist, tarih, seq, o, sadece_cfg=None, dk_grup=30):
    """Kurulan (pist,seq) Altili kuponunu Telegram'dan NUMARA + ISIMLE bildir.
    K105: sadece_cfg verilirse YALNIZ o gecise ait config'ler bildirilir (iki zamanli
    kurulumda mesaj karismasin; 30 dk mesaji 15 dk kuponunu icermez, tersi de).
    telegram_at config'i yoksa sessizce gecer (bot kurulmadan da guvenli). try-korumali cagirilir."""
    import telegram_at
    df = _oku()
    g = df[(df["tarih"] == tarih) & (df["pist"] == pist)
           & (pd.to_numeric(df["seq"], errors="coerce") == seq)]
    if sadece_cfg is not None:
        g = g[g["config"].isin(sadece_cfg)]
    if g.empty:
        return
    admap = _at_ad_map(o)
    tarih_tr = pd.Timestamp(str(tarih)).strftime("%d.%m.%Y")
    ilk_saat = str(g["ilk_saat"].iloc[0])
    sat = ["🎫 <b>ALTILI KUPONU KURULDU</b>",
           f"📍 {pist} — {tarih_tr}, {int(seq)}. Altılı",
           f"🕐 İlk koşu {ilk_saat} ({dk_grup} dk kala)", ""]
    toplam_bedel = 0.0
    son_aile = None
    for cfg, ay in KONFIG.items():                     # KONFIG sirasi = aile sirasi
        gc = g[g["config"] == cfg].sort_values("ayak")
        if gc.empty:
            continue
        if ay["aile"] != son_aile:                     # K69: aile basligi
            sat.append(f"━━━ <b>{AILE_AD[ay['aile']]}</b> ━━━")
            son_aile = ay["aile"]
        kombo = int(np.prod([int(x) for x in gc["nat"]]))
        bedel = kombo * ro.birim_fiyat(pist)
        toplam_bedel += bedel
        sat.append(f"▸ <b>{cfg.upper()}</b> — {kombo} kombo / {ro.para(bedel)}")
        for _, r in gc.iterrows():
            adm = admap.get(_as_int(r["race_kod"]), {})
            secim = [int(x) for x in str(r["secim"]).split(",") if x != ""]
            atlar = ", ".join(f"{no} {adm.get(no, '?')}" for no in secim)
            bank = " (banker)" if int(r["banker"]) == 1 else ""
            sat.append(f"   {int(r['ayak'])}. ayak (koşu {int(r['kosu_no'])}): {atlar}{bank}")
        sat.append("")
    sat.append(f"💰 Toplam kâğıt bedel: {ro.para(toplam_bedel)}")
    sat.append("Detay/takip: raporlar/altili.html")
    for parca in _telegram_bol("\n".join(sat)):
        telegram_at.gonder(parca)


TG_SINIR = 3900                                        # Telegram 4096; guvenlik payi


def _telegram_bol(mesaj):
    """K69: 7 config ile mesaj Telegram sinirini asabilir. Asarsa SATIR sinirindan boler
    (HTML etiketleri satir icinde kapaniyor -> bolme guvenli). Asmiyorsa tek parca."""
    if len(mesaj) <= TG_SINIR:
        return [mesaj]
    parcalar, cur = [], []
    n = 0
    for satir in mesaj.split("\n"):
        if n + len(satir) + 1 > TG_SINIR and cur:
            parcalar.append("\n".join(cur))
            cur, n = [], 0
        cur.append(satir)
        n += len(satir) + 1
    if cur:
        parcalar.append("\n".join(cur))
    return [f"{p}\n<i>({i+1}/{len(parcalar)})</i>" for i, p in enumerate(parcalar)]


def bildir_sonuc(tarih, pist, seq):
    """Tamamlanan (pist,seq) Altili SONUCUNU Telegram'dan bildir (K61): kazananlar (numara+isim) +
    her config'in isabeti/bedeli/odulu/neti + RESMI temettu. Config yoksa sessizce gecer."""
    import telegram_at
    df = _oku()
    g_all = df[(df["tarih"] == tarih) & (df["pist"] == pist)
               & (pd.to_numeric(df["seq"], errors="coerce") == seq)]
    if g_all.empty or g_all["sonuclandi"].isna().any():
        return
    tarih_tr = pd.Timestamp(str(tarih)).strftime("%d.%m.%Y")
    sat = ["🏁 <b>ALTILI SONUÇLANDI</b>",
           f"📍 {pist} — {tarih_tr}, {int(seq)}. Altılı", ""]
    # K100: referans config SABIT olamaz -- eskiden next(iter(KONFIG))="dar" idi, dar emekli
    # olunca yeni Altililarda o satir bos donup "Kazananlar" satiri sessizce kaybolurdu.
    # Artik o Altili'da GERCEKTEN kupon kurulmus ilk config'ten okunur.
    _ref_cfg = next((c for c in KONFIG if (g_all["config"] == c).any()), None)
    if _ref_cfg is None:
        return
    ref = g_all[g_all["config"] == _ref_cfg].sort_values("ayak")
    kaz_par = []
    for _, r in ref.iterrows():
        kz = ro.kazanan_bilgi(_as_int(r["race_kod"]))
        if kz and kz.get("no") is not None:
            kaz_par.append(f"{int(r['ayak'])}.#{kz['no']} {str(kz.get('ad') or '')[:20]}".rstrip())
        elif pd.notna(r["kazanan"]):
            kaz_par.append(f"{int(r['ayak'])}.#{int(r['kazanan'])}")
    if kaz_par:
        sat += ["🏇 Kazananlar: " + ", ".join(kaz_par), ""]
    son_aile = None
    t_bedel = t_odul = 0.0
    for cfg, ay in KONFIG.items():
        gc = g_all[g_all["config"] == cfg].sort_values("ayak")
        if gc.empty:
            continue
        if ay["aile"] != son_aile:
            sat.append(f"━━━ <b>{AILE_AD[ay['aile']]}</b> ━━━")
            son_aile = ay["aile"]
        oz = _kupon_ozet(gc, tarih, pist, seq, cfg)
        t_bedel += oz["bedel"]; t_odul += oz["odul"]
        kad = oz["kademe"]
        durum = "✅ 6/6 TUTTU" if kad == 6 else (f"son {kad} ayak (bilgi)" if kad else "tutmadı")
        sat.append(f"▸ <b>{cfg.upper()}</b>: {durum} — bedel {ro.para(oz['bedel'])}, "
                   f"ödül {ro.para(oz['odul'])}, net {ro.para(oz['net'], isaret=True)}")
    sat.append(f"\n<b>Bu Altılı toplamı</b> — bedel {ro.para(t_bedel)}, ödül {ro.para(t_odul)}, "
               f"net {ro.para(t_odul - t_bedel, isaret=True)}")
    res = ro.altili_odeme(tarih, pist, int(seq), cek=False)
    if res.get("temettu"):
        sat.append(f"\n💰 Resmi temettü (1 birim): {ro.para(res['temettu'])}")
    elif res.get("devir"):
        sat.append(f"\n↪️ Kimse bilemedi — {ro.para(res['devir'])} devretti")
    sat.append("\nDetay: raporlar/altili.html")
    for parca in _telegram_bol("\n".join(sat)):
        telegram_at.gonder(parca)


# ----------------------------- takip tetigi (zaman-bazli) -----------------------------
def kupon_zamani_kur(pistler, ymd, tarih, dk_kala=None):
    """takip.py her turda cagirir. K105: artik HER DK GRUBU icin ayri kontrol yapilir.
    Bir Altili penceresi icin, o grubun config'lerinden HENUZ kupon yoksa VE ilk kosuya
    <=grup_dk kaldiysa VE ilk kosu baslamadiysa -> YALNIZ o grubun config'leri kurulur.

    ONEMLI (deney guvenligi): eskiden 'kurulmus mu' kontrolu (tarih,pist,seq) duzeyindeydi;
    30 dk gecisi kupon kurunca pencere 'bitti' sayiliyordu. Iki zamanli kurulumda bu,
    15 dk grubunun HIC kurulmamasina yol acardi. Artik kontrol (tarih,pist,seq,CONFIG)
    duzeyinde ve kupon_hazirla'ya sadece_cfg gecilir -> gruplar birbirinin satirina DOKUNMAZ.

    Idempotent. Doner: kurulan kupon sayisi. Hata firlatmaz (takip guvenligi).
    dk_kala verilirse (elle cagri) yalnizca o grup kurulur."""
    kurulan = 0
    df = _oku()
    now = datetime.now()
    gruplar = [dk_kala] if dk_kala is not None else dk_gruplari()
    for pist in pistler:
        try:
            o = getjson(f"{BASE}/program/{ymd}/full/{pist}.json")
            if o.get("_hata"):
                continue
            for seq, pencere, ilk_saat in altili_pencereleri(o):
                try:
                    ilk_post = datetime.strptime(f"{tarih} {ilk_saat}", "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
                for gdk in gruplar:
                    cfgler = list(grup_konfig(gdk))
                    if not cfgler:
                        continue
                    if len(df):
                        var = df[(df["tarih"] == tarih) & (df["pist"] == pist)
                                 & (df["seq"] == seq)]["config"].unique()
                        if all(c in var for c in cfgler):
                            continue               # bu grup zaten kurulmus
                    if not (ilk_post - timedelta(minutes=gdk) <= now < ilk_post):
                        continue
                    n = kupon_hazirla(pist, ymd, tarih, sadece_seq=seq,
                                      sadece_cfg=cfgler, dk_grup=gdk)
                    kurulan += n
                    df = _oku()
                    if n:                          # K60: yeni kupon -> Telegram bildirimi
                        try:
                            bildir_kupon(pist, tarih, seq, o, sadece_cfg=cfgler, dk_grup=gdk)
                        except Exception as e:
                            print(f"  altili telegram bildirim hatasi: {type(e).__name__}")
        except Exception as e:
            print(f"  altili kupon hatasi ({pist}): {type(e).__name__} - takip devam ediyor")
    if kurulan:
        html_yaz()
    return kurulan


# ----------------------------- sonucla -----------------------------
def kazananlar_kumesi(o):
    """K64: Sonuc JSON'dan race_kod -> {kazanan NO'lari}. BASABAS (dead heat) -> birden cok NO
    (ayni kosuda >1 at SONUC=1). Bir ayak, bu kumeden HERHANGI biri secimimizde varsa tutar."""
    kaz = {}
    for k in o.get("kosular", []):
        rk = _as_int(k.get("KOD"))
        for a in k.get("atlar", []):
            s = pd.to_numeric(a.get("SONUC"), errors="coerce")
            if pd.notna(s) and int(s) == 1:
                no = _as_int(a.get("NO"))
                if no is not None:
                    kaz.setdefault(rk, set()).add(no)
    return kaz


def yeniden_sonucla():
    """K64: TUM sonuclanmis ayaklarin tuttu'sunu feed'den YENIDEN hesapla (basabas geriye duzeltme).
    Feed'i (tarih,pist) basina bir kez ceker. Doner: degisen satir sayisi."""
    df = _oku()
    if df.empty:
        print("altili defteri bos."); return 0
    son = df[df["sonuclandi"].notna()]
    degisen = 0
    for (tarih, pist), grp in son.groupby(["tarih", "pist"]):
        ymd = datetime.strptime(str(tarih), "%Y-%m-%d").strftime("%Y%m%d")
        o = getjson(f"{BASE}/sonuclar/{ymd}/full/{pist}.json")
        if o.get("_hata"):
            print(f"  {tarih} {pist}: feed yok, atlandi"); continue
        kaz = kazananlar_kumesi(o)
        for i in grp.index:
            rk = _as_int(df.at[i, "race_kod"])
            if not kaz.get(rk):
                continue
            secilenler = {int(x) for x in str(df.at[i, "secim"]).split(",") if x != ""}
            tut = secilenler & kaz[rk]
            yeni = int(bool(tut))
            eski = int(pd.to_numeric(df.at[i, "tuttu"], errors="coerce") or 0)
            if eski != yeni:
                print(f"  DUZELTME {tarih} {pist} {df.at[i,'config']} ayak{int(df.at[i,'ayak'])}: "
                      f"tuttu {eski} -> {yeni} (kazananlar {sorted(kaz[rk])})")
                degisen += 1
            df.at[i, "tuttu"] = yeni
            df.at[i, "kazanan"] = min(tut) if tut else min(kaz[rk])
    if degisen:
        _yaz(df)
        html_yaz(df)
    print(f"yeniden sonucla: {degisen} satir duzeltildi (basabas).")
    return degisen


def sonucla_altili():
    df = _oku()
    if df.empty:
        print("altili defteri bos.")
        return 0
    acik = df[df["sonuclandi"].isna()]
    if acik.empty:
        print("sonuclanmamis ayak yok.")
        return 0
    aday_gruplar = set()                          # K61: bu geciste acik ayagi olan Altili'lar
    for _, r in acik[["tarih", "pist", "seq"]].drop_duplicates().iterrows():
        s = pd.to_numeric(r["seq"], errors="coerce")
        if pd.notna(s):
            aday_gruplar.add((r["tarih"], r["pist"], int(s)))
    df["sonuclandi"] = df["sonuclandi"].astype("object")
    bugun = date.today().isoformat()
    dolan = 0
    for (tarih, pist), grp in acik.groupby(["tarih", "pist"]):
        ymd = datetime.strptime(str(tarih), "%Y-%m-%d").strftime("%Y%m%d")
        o = getjson(f"{BASE}/sonuclar/{ymd}/full/{pist}.json")
        if o.get("_hata"):
            continue
        kaz = kazananlar_kumesi(o)            # K64: race_kod -> {kazanan no'lari} (basabas -> >1)
        idx = df.index[(df["tarih"] == tarih) & (df["pist"] == pist) & df["sonuclandi"].isna()]
        for i in idx:
            rk = _as_int(df.at[i, "race_kod"])
            if kaz.get(rk):
                secilenler = {int(x) for x in str(df.at[i, "secim"]).split(",") if x != ""}
                tut = secilenler & kaz[rk]                # BASABAS: herhangi bir kazanan yeter
                # kazanan sutunu tek int (uyum): tuttuysak tuttugumuz kazanan, yoksa ilk kazanan
                df.at[i, "kazanan"] = min(tut) if tut else min(kaz[rk])
                df.at[i, "tuttu"] = int(bool(tut))
                df.at[i, "sonuclandi"] = bugun
                dolan += 1
    _yaz(df)
    # RESMI odemeleri (temettu / devir) cache'le: tutmayan kuponlarda da gosterilecek.
    # Yalniz TAMAMLANMIS pencereler icin cek (ag istegi bosa gitmesin).
    try:
        for (tarih, pist, seq), g in df.groupby(["tarih", "pist", "seq"]):
            if g["sonuclandi"].notna().all():
                ro.altili_odeme(tarih, pist, int(seq), cek=True)
    except Exception as e:
        print(f"  (temettu cache atlandi: {type(e).__name__})")
    # K61: bu geciste 6 ayagi da TAM tamamlanan Altili'lari Telegram'dan bildir (bir kez; try-korumali)
    for (t_, p_, s_) in aday_gruplar:
        g = df[(df["tarih"] == t_) & (df["pist"] == p_)
               & (pd.to_numeric(df["seq"], errors="coerce") == s_)]
        if len(g) and g["sonuclandi"].notna().all():
            try:
                bildir_sonuc(t_, p_, s_)
            except Exception as e:
                print(f"  altili sonuc telegram hatasi: {type(e).__name__}")
    html_yaz(df)
    print(f"altili: {dolan} ayak sonuclandi (acik {int(df['sonuclandi'].isna().sum())}).")
    return dolan


# ----------------------------- isabet hesabi -----------------------------
def _isabet_kademe(tuttu_listesi):
    """tuttu_listesi = ayak 1..6 icin 0/1/None. Sondan kesik en uzun ardisik tutan (6/5/4/3);
    hicbiri degilse 0. None (bekleyen) varsa None (henuz belli degil)."""
    if any(t is None for t in tuttu_listesi):
        return None
    t = [bool(x) for x in tuttu_listesi]
    for n in (6, 5, 4, 3):
        if all(t[6 - n:]):
            return n
    return 0


# ----------------------------- HTML (K55: zengin format) -----------------------------
def _kupon_ozet(g, tarih, pist, seq, cfg):
    """Bir (pencere x config) kuponunun ozeti: kombo, bedel, isabet, odul, net."""
    g = g.sort_values("ayak")
    tut = [int(t) if pd.notna(t) else None for t in g["tuttu"]]
    kombo = int(np.prod([int(x) for x in g["nat"]]))
    bedel = kombo * ro.birim_fiyat(pist)
    kademe = _isabet_kademe(tut)
    # RESMI odeme — kupon tutsun tutmasin (kullanici: "tutmayan kuponlarin da resmi odul
    # bilgisi olmali"): o Altili gercekte ne odedi / devretti mi.
    res = ro.altili_odeme(tarih, pist, int(seq), cek=False)
    odul = 0.0
    if kademe == 6:                      # SADECE 6/6 kazanir (K52: 5/4/3 ayri bahis, teselli degil)
        odul = float(res["temettu"]) if res["temettu"] else 0.0
    return {"g": g, "tut": tut, "kombo": kombo, "bedel": bedel,
            "kademe": kademe, "odul": odul, "net": odul - bedel,
            "resmi": res, "bitti": all(t is not None for t in tut)}


def _tur_ozeti():
    """K78: sayfa girisindeki kupon-turu listesi KONFIG'den uretilir. Eskiden elle yazilmisti
    ('dort boyda kurulur') ve 7 ture cikinca bayatladi -> artik bayatlayamaz.
    K100: emekliler ayri satirda -- gecmis sicilleri tabloda DURUYOR, yalniz yeni kupon
    kurulmuyor; sayfa bunu acikca soylesin ki 'kupon nerede?' diye aranmasin."""
    sat = []
    akt = aktif_konfig()
    for aile, ad in AILE_AD.items():
        cs = [c for c in akt if KONFIG[c]["aile"] == aile]
        if not cs:
            continue
        sat.append(f"&nbsp;&nbsp;<b>{ad}</b> &rarr; " + ", ".join(
            f"{c.upper()} <span class=mini>(~{KONFIG[c]['kombo']} kombo, "
            f"{KONFIG[c]['dagitim']})</span>" for c in cs))
    em = emekli_konfig()
    if em:
        sat.append("&nbsp;&nbsp;<span class=mini><b>EMEKLI</b> (10.08.2026, K100 &mdash; yeni "
                   "kupon kurulmuyor; gecmis sicilleri asagida AYNEN duruyor): "
                   + ", ".join(c.upper() for c in em) + "</span>")
    return "<br>".join(sat)


def _resmi_satir(kupolar):
    """O Altili'nin RESMI odemesi + hangi kupon TURLERIMIZ tutturdu (kacirilan odul).

    K78 DUZELTME: eskiden tek kupon alirdi ve cagri `kk[cfgler[0]]` idi -> her zaman KONFIG'in
    ilki (DAR). Baslik satiri ise Altili'nin TAMAMINI ozetliyor. Sonuc: 29.07 ISTANBUL 1.Altili'da
    ACGOZLU900 6/6 tuttugu (net +10.536,93 TL) halde baslikta "biz tutturamadik" yaziyordu.
    Artik TUM turlere bakilir; tutan varsa adiyla yazilir."""
    kupolar = list(kupolar)
    r = (kupolar[0].get("resmi") or {}) if kupolar else {}
    tutan = [k["cfg"] for k in kupolar if k["kademe"] == 6]
    if r.get("temettu"):
        t = ro.para(r["temettu"])
        if tutan:
            ad = ", ".join(c.upper() for c in tutan)
            return (f"<b>resmi temettu (1 birim): {t}</b> &mdash; "
                    f"<span class=poz><b>tutturan kuponumuz: {ad}</b></span> "
                    f"<span class=mini>({len(tutan)}/{len(kupolar)} tur)</span>")
        return (f"resmi temettu (1 birim): <b>{t}</b> "
                f"<span class=mini>&mdash; bu Altili'yi bilenlerin aldigi; "
                f"{len(kupolar)} kupon turumuzun hicbiri tutturamadi</span>")
    if r.get("devir"):
        return (f"<b>KIMSE BILEMEDI</b> &mdash; {ro.para(r['devir'])} "
                f"<span class=mini>sonraki cekilise devretti (bu Altili'da odeme yapilmadi)</span>")
    if not all(k["bitti"] for k in kupolar):
        return "<span class=mini>resmi temettu: kosular bitince belli olacak</span>"
    return "<span class=mini>resmi temettu: bilinmiyor (feed'den alinamadi)</span>"


def _sira_etiketleri(sirali, secset, kzno):
    """[(sira, no)] -> HTML. Bizim sectigimiz KALIN, kazanan YESIL kutu + tik."""
    parcalar = []
    for sira, no in sirali:
        et = f"{ro.sira_str(sira)}<b>#{no}</b>" if no in secset else f"{ro.sira_str(sira)}#{no}"
        if kzno is not None and no == kzno:
            et = (f"<span style='background:#d9f7d9;padding:0 4px;border-radius:3px'>"
                  f"{et}&nbsp;&#10003;</span>")
        parcalar.append(et)
    return " &nbsp; ".join(parcalar)


def _siralama_html(tarih, pist, seq, ayak, kosu_no, rk, secimler, kzno):
    """K97: ayni ayagin IKI siralamasi, AYRI satirlarda ve acikca etiketli:
      1) KUPON ANI -- kupon kurulurken elimizdeki vektor (altili_kupon_ani.csv).
         KARARI yargilarken dogru cetvel budur; son ayak icin karar 2-3 saat onceden verilir.
      2) YARIS ANI -- posta-5dk, defter'deki model_rank (K58'in eski davranisi).
         SONUCU okurken dogru cetvel budur.
    Ikisini karistirmak yaniltir: 09.08 Istanbul 2. Altili'da kosu 8'in kazanani yaris aninda
    sistemin 10. ati, kupon aninda 2. atiydi; kosu 6'nin kazanani yaris aninda 2., kupon
    aninda 6.'ydi. Her iki satirin basina KOSU NO yazilir -- satir kime ait, hic suphe kalmasin.
    K81 mirasi: kayit yoksa hangi dalin yandigi acikca yazilir, sessiz bosluk birakilmaz."""
    secset = {int(x) for x in secimler}
    H = []

    # --- 1) KUPON ANI ---------------------------------------------------------------
    a = ro.kupon_ani_atlari(tarih, pist, seq, ayak)
    if len(a) == 0:
        H.append(f"<span class=mini><b>kosu {kosu_no}</b> &middot; KUPON ANI siralamasi: "
                 f"<b>kayit yok</b> &mdash; 10 Agu oncesi kuponlar icin "
                 f"<code>kupon_ani_geri_kur.py</code> ile geri kurulur; oran gunlugu (K76) "
                 f"veya o gunun katsayilari eksikse geri kurulaMAZ, UYDURULMAZ</span>")
    else:
        r0 = a.iloc[0]
        dk = pd.to_numeric(r0.get("dk_kala"), errors="coerce")
        ek = ("" if str(r0.get("kaynak")) == "canli"
              else " <b title='oran gunlugu + bot1 + o gunun katsayilari ile geri kuruldu'>"
                   "[geri kurulan]</b>")
        sirali = [(int(r["sis_sira"]), int(r["no"])) for _, r in a.iterrows()]
        H.append(f"<span class=mini><b>kosu {kosu_no}</b> &middot; <b>KUPON ANI</b> siralamasi "
                 f"({str(r0.get('kayit_ts'))[11:16]}, "
                 f"{('%.0f' % dk) if pd.notna(dk) else '?'} dk kala){ek}: </span>"
                 + _sira_etiketleri(sirali, secset, kzno))
        # K99: BOT1 CETVELI ayri satir. bot1_900 secimini BU vektorle yapar; ustteki
        # harman satiriyla karsilastirilamaz. Ayrisma buradan okunur -- "bot1 neden
        # harmanin 5.'sini almadi" sorusunun cevabi bu satirdadir.
        if "bot1_sira" in a.columns and pd.notna(a["bot1_sira"]).any():
            b = a.dropna(subset=["bot1_sira"]).copy()
            b_sirali = [(int(r["bot1_sira"]), int(r["no"]))
                        for _, r in b.sort_values("bot1_sira").iterrows()]
            H.append("<span class=mini><b>kosu %s</b> &middot; <b>BOT1 CETVELI</b> "
                     "(orana bakmaz &mdash; <i>bot1_900</i> secimini bununla yapar): </span>"
                     % kosu_no + _sira_etiketleri(b_sirali, secset, kzno))

    # --- 2) YARIS ANI ---------------------------------------------------------------
    if not rk:
        H.append("<span class=mini><b>kosu %s</b> &middot; YARIS ANI siralamasi: bu ayagin "
                 "<b>race_kod'u yok</b> (kupon kaydinda bos)</span>" % kosu_no)
    else:
        g = ro.kosu_atlari(rk)
        if g is None or len(g) == 0:
            H.append(f"<span class=mini><b>kosu {kosu_no}</b> &middot; YARIS ANI siralamasi: "
                     f"<b>defter'de {rk} kaydi bulunamadi</b> &mdash; gun sonu 'sonucla' "
                     f"gecisinden once bakildiysa normaldir, sayfayi 22:30'dan sonra tazele</span>")
        else:
            g = g.copy()
            g["mr"] = pd.to_numeric(g["model_rank"], errors="coerce")
            g = g.sort_values("mr", na_position="last")
            sirali = [(r["mr"], int(r["no"])) for _, r in g.iterrows() if pd.notna(r.get("no"))]
            H.append(f"<span class=mini><b>kosu {kosu_no}</b> &middot; <b>YARIS ANI</b> "
                     f"siralamasi (postaya 5 dk kala): </span>"
                     + _sira_etiketleri(sirali, secset, kzno))

    return ("<div style='line-height:1.9'>" + "<br>".join(H) + "</div>")


def _kumulatif_blok(kupolar):
    """K69: GUNE gore kar/zarar + ISLEYEN BAKIYE (kullanici: 'tum kar zarar tablosunu gormem
    onemli'). Sadece SONUCLANMIS kuponlar sayilir; acik kuponlar bakiyeyi kirletmez."""
    bitmis = [k for k in kupolar if k["bitti"]]
    if not bitmis:
        return []
    gun = {}
    for k in bitmis:
        g = gun.setdefault(str(k["tarih"]), {"bedel": 0.0, "odul": 0.0, "kupon": 0, "tam": 0})
        g["bedel"] += k["bedel"]; g["odul"] += k["odul"]
        g["kupon"] += 1; g["tam"] += (k["kademe"] == 6)
    H = ["<h3>Gun gun kar/zarar ve isleyen bakiye</h3><div class=kart>",
         "<div style='overflow-x:auto'><table><tr><th class=l>tarih</th><th>kupon</th>"
         "<th>6/6</th><th>bedel</th><th>odul</th><th>gun neti</th>"
         "<th>ISLEYEN BAKIYE</th></tr>"]
    kum = 0.0
    for t in sorted(gun):
        g = gun[t]
        net = g["odul"] - g["bedel"]
        kum += net
        tr = pd.Timestamp(t).strftime("%d.%m.%Y")
        H.append(f"<tr><td class=l>{tr}</td><td>{g['kupon']}</td>"
                 f"<td>{g['tam'] or '&mdash;'}</td><td>{ro.para(g['bedel'])}</td>"
                 f"<td>{ro.para(g['odul'])}</td>"
                 f"<td class='{'poz' if net >= 0 else 'neg'}'>{ro.para(net, isaret=True)}</td>"
                 f"<td class='{'poz' if kum >= 0 else 'neg'}'><b>{ro.para(kum, isaret=True)}</b>"
                 f"</td></tr>")
    H.append("</table></div></div>")
    return H


def _ganyan_ozet():
    """paper_kupon.csv (ganyan kagit testi) toplami -- SALT-OKUNUR. Yoksa None."""
    p = KOK / "veri" / "paper_kupon.csv"
    if not p.exists():
        return None
    try:
        b = pd.read_csv(p, low_memory=False)
        s = b[b["durum"].isin(["kazandi", "kaybetti"])]     # iptal = iade
        if s.empty:
            return None
        bedel = float(pd.to_numeric(s["miktar"], errors="coerce").sum())
        odul = float(pd.to_numeric(s["getiri"], errors="coerce").sum())
        return {"kupon": len(s), "bedel": bedel, "odul": odul, "net": odul - bedel}
    except Exception:
        return None


def _birlesik_blok(kupolar):
    """K69: ALTILI + GANYAN tek tabloda -- 'tum kar zarar tablosu' tek bakista."""
    bitmis = [k for k in kupolar if k["bitti"]]
    a_bedel = sum(k["bedel"] for k in bitmis)
    a_odul = sum(k["odul"] for k in bitmis)
    gy = _ganyan_ozet()
    H = ["<div class=toplam><b>TUM KAGIT SICILI (Altili + ganyan birlikte)</b><br>",
         "<table style='margin-top:6px'><tr><th class=l>bahis</th><th>kupon</th>"
         "<th>bedel</th><th>odul</th><th>net</th><th>ROI</th></tr>"]

    def satir(ad, n, bedel, odul):
        net = odul - bedel
        cls = "poz" if net >= 0 else "neg"
        roi = f"%{100*net/bedel:+.1f}" if bedel else "-"
        return (f"<tr><td class=l><b>{ad}</b></td><td>{n}</td><td>{ro.para(bedel)}</td>"
                f"<td>{ro.para(odul)}</td><td class={cls}><b>{ro.para(net, isaret=True)}</b></td>"
                f"<td class={cls}>{roi}</td></tr>")

    H.append(satir("ALTILI", len(bitmis), a_bedel, a_odul))
    t_bedel, t_odul = a_bedel, a_odul
    if gy:
        H.append(satir("GANYAN (paper)", gy["kupon"], gy["bedel"], gy["odul"]))
        t_bedel += gy["bedel"]; t_odul += gy["odul"]
    else:
        H.append("<tr><td class=l>GANYAN (paper)</td><td colspan=5 class=l>"
                 "<span class=mini>paper_kupon.csv okunamadi</span></td></tr>")
    H.append("</table>")
    tnet = t_odul - t_bedel
    cls = "poz" if tnet >= 0 else "neg"
    H.append("<hr style='border:none;border-top:1px solid #ddd;margin:8px 0'>"
             f"<b>GENEL TOPLAM (her sey)</b> &nbsp; bedel {ro.para(t_bedel)} &nbsp; "
             f"odul {ro.para(t_odul)} &nbsp; net "
             f"<span class='{cls} buyuk'>{ro.para(tnet, isaret=True)}</span>"
             + (f" &nbsp;<span class=k>(ROI %{100*tnet/t_bedel:+.1f})</span>" if t_bedel else ""))
    H.append("<div class=mini style='margin-top:6px'>Kagit (paper) sicilidir &mdash; "
             "gercek para yatirilmiyor. Altili tarafi -EV gozlem akislari icerir (K62/K65/K67/K68).</div>")
    H.append("</div>")
    return H


def html_yaz(df=None, ac=False):
    """K55: secimlerimiz + SISTEM SIRASI, kazanan at + sistem/kamu sirasi + ganyan orani,
    kupon bedeli + odul, altta TOPLAM. Zenginlestirme defter.csv'den (salt-okunur);
    altili_kupon.csv DEGISMEZ (sistemin mevcut hali bozulmaz)."""
    if df is None:
        df = _oku()
    for c in ["seq", "ayak", "kosu_no", "race_kod", "banker", "nat", "kazanan", "tuttu"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    H = ["<meta charset='utf-8'><title>Altili Takip</title>", ro.ORTAK_CSS,
         "<h2>ALTILI GANYAN &mdash; kupon takibi</h2>",
         f"<div class=not>guncelleme {datetime.now():%d.%m.%Y %H:%M} &mdash; "
         "<b>GERCEK BAHIS DEGIL</b>, kagit uzerinde izleme/ogrenme (K48/K53). "
         "Backtest OOS &minus;%32, +EV yok (K52).<br>"
         f"Su an <b>{len(aktif_konfig())} kupon turu</b> paralel izleniyor "
         "(K78: metin KONFIG'den uretilir, elle guncellenmez):<br>" + _tur_ozeti() +
         "<br>Birim fiyat 2026 tarifesi: Ist/Ank/Izm/Ada/Bur/Koc/Ant 1,25 TL, "
         "Elazig/Urfa/Diyarbakir 1,00 TL.<br>"
         "<b>Odul yalniz 6/6 tam isabette</b> odenir; 5/4/3 ayak TJK'da AYRI bahistir "
         "(teselli degil) &mdash; tabloda yalnizca bilgi amacli gosterilir.<br>"
         "<b>K97 &mdash; IKI AYRI SIRALAMA:</b> her ayakta sistemin sirasi iki kez gosterilir. "
         "<b>K</b> = <b>kupon ani</b> sirasi (kupon Altili'nin ilk ayagindan ~30 dk once TEK "
         "seferde kurulur; son ayagin karari 2-3 SAAT onceden verilir, karari yargilarken "
         "dogru cetvel budur). <b>Y</b> = <b>yaris ani</b> sirasi (postaya 5 dk kala, defter; "
         "sonucu okurken dogru cetvel budur). Ikisi 3+ sira ayrilirsa "
         "<span style='color:#b45309;font-weight:bold'>turuncu</span> yazilir &mdash; o ayakta "
         "piyasa kupon kurulduktan sonra ciddi kaymis demektir (K76/K80/K92 surukleme).</div>"]

    if df.empty:
        H.append("<p>Henuz kupon yok.</p>")
        HTMLA.parent.mkdir(parents=True, exist_ok=True)
        HTMLA.write_text("\n".join(H), encoding="utf-8")
        return HTMLA

    kupolar = []
    for (tarih, pist, seq, cfg), g in df.groupby(["tarih", "pist", "seq", "config"]):
        kupolar.append({"tarih": tarih, "pist": pist, "seq": int(seq), "cfg": cfg,
                        **_kupon_ozet(g, tarih, pist, seq, cfg)})

    def toplam_blok(baslik):
        H2 = ["<div class=toplam>", f"<b>{baslik}</b><br>"]
        gen_bedel = gen_odul = 0.0
        for cfg in KONFIG:
            kk = [k for k in kupolar if k["cfg"] == cfg and k["bitti"]]
            bedel = sum(k["bedel"] for k in kk)
            odul = sum(k["odul"] for k in kk)
            gen_bedel += bedel
            gen_odul += odul
            net = odul - bedel
            tam = sum(1 for k in kk if k["kademe"] == 6)
            cls = "poz" if net >= 0 else "neg"
            # K100: emekli config'ler burada KALIR (sicil ve genel toplam bozulmasin), etiketlenir
            em = "" if KONFIG[cfg].get("aktif", True) else \
                 " <span class=mini style='color:#92400e'>[EMEKLI &mdash; K100]</span>"
            H2.append(f"<div style='margin:6px 0'><b>{cfg.upper()}</b>{em} "
                      f"<span class=k>({len(kk)} tamamlanan kupon, {tam} tam isabet)</span> &nbsp; "
                      f"bedel <b>{ro.para(bedel)}</b> &nbsp; odul <b>{ro.para(odul)}</b> &nbsp; "
                      f"net <span class='{cls}'><b>{ro.para(net, isaret=True)}</b></span></div>")
        gnet = gen_odul - gen_bedel
        cls = "poz" if gnet >= 0 else "neg"
        H2.append("<hr style='border:none;border-top:1px solid #ddd;margin:8px 0'>"
                  f"<b>GENEL TOPLAM</b> &nbsp; bedel {ro.para(gen_bedel)} &nbsp; "
                  f"odul {ro.para(gen_odul)} &nbsp; net "
                  f"<span class='{cls} buyuk'>{ro.para(gnet, isaret=True)}</span>")
        H2.append("</div>")
        return H2

    H += toplam_blok("TOPLAM DURUM")

    H += _kumulatif_blok(kupolar)
    H += _birlesik_blok(kupolar)

    # ---- K69: her Altili TEK tablo, kupon turleri YAN YANA ----
    gruplar = sorted({(k["tarih"], k["pist"], k["seq"]) for k in kupolar}, reverse=True)
    H.append("<h3>Kuponlar (yeni tarih ustte) &mdash; kupon turleri yan yana</h3>")
    for tarih, pist, seq in gruplar:
        kk = {k["cfg"]: k for k in kupolar if (k["tarih"], k["pist"], k["seq"]) == (tarih, pist, seq)}
        cfgler = [c for c in KONFIG if c in kk]
        if not cfgler:
            continue
        ref = kk[cfgler[0]]["g"].sort_values("ayak")
        tarih_tr = pd.Timestamp(str(tarih)).strftime("%d.%m.%Y")
        t_bedel = sum(kk[c]["bedel"] for c in cfgler)
        t_odul = sum(kk[c]["odul"] for c in cfgler)
        tn = t_odul - t_bedel
        H.append("<div class=kart>")
        H.append(f"<div class=baslik>{tarih_tr} &nbsp;|&nbsp; <b>{pist}</b> &nbsp;|&nbsp; "
                 f"{seq}. ALTILI<br><span class=k>{len(cfgler)} kupon turu &nbsp;&middot;&nbsp; "
                 f"toplam bedel <b>{ro.para(t_bedel)}</b> &nbsp;&rarr;&nbsp; odul "
                 f"<b>{ro.para(t_odul)}</b> &nbsp;&rarr;&nbsp; net "
                 f"<span class='{'poz' if tn >= 0 else 'neg'}'><b>{ro.para(tn, isaret=True)}</b>"
                 f"</span><br>{_resmi_satir([kk[c] for c in cfgler])}</span></div>")
        # K97: sistem sirasi artik IKI kolonlu okunur -> K=kupon ani, Y=yaris ani
        # K99: bot1 sutunlarinda ayrica B = bot1'in KENDI sirasi (secimi yapan cetvel)
        H.append("<div class=k style='margin:6px 0 10px'>Hucre etiketleri: "
                 "<b>K</b> = kupon anindaki harman sirasi &nbsp;&middot;&nbsp; "
                 "<b>Y</b> = yaris anindaki harman sirasi &nbsp;&middot;&nbsp; "
                 "<b>B</b> = <i>bot1'in kendi sirasi</i> (yalniz bot1 sutununda; "
                 "secimi yapan cetvel odur, K degil) &nbsp;&middot;&nbsp; "
                 "<b>P</b> = <i>kamu (piyasa) sirasi</i>, kupon aninda "
                 "<span style='color:#6d28d9'><b>mor</b></span> = sistem kamudan 3+ sira ayri "
                 "&nbsp;&middot;&nbsp; <span style='color:#b45309'><b>turuncu</b></span> = "
                 "kupon ani ile yaris ani 3+ sira kaymis</div>")
        H.append("<div style='overflow-x:auto'><table>")
        H.append("<tr><th>ayak</th><th class=l>KAZANAN AT</th>"
                 "<th>kazananin sirasi<br><span class=mini>sistem: kupon ani &rarr; yaris ani"
                 "<br>+ kamu sirasi</span></th>"
                 "<th>ganyan<br>orani</th>"
                 + "".join(
                     f"<th class=l>{c.upper()}"
                     + ("" if KONFIG[c].get("aktif", True)
                        else "<br><span class=mini style='color:#92400e'>EMEKLI</span>")
                     + f"<br><span class=mini>{KONFIG[c]['aile']}</span></th>"
                     for c in cfgler) + "</tr>")
        for _, r in ref.iterrows():
            ai = int(r["ayak"])
            rk = int(r["race_kod"]) if pd.notna(r["race_kod"]) else None
            kz = ro.kazanan_bilgi(rk) if rk else None
            if kz:
                kz_html = f"<b>{kz['no']}</b> {str(kz['ad'])[:20]}"
                kz_oran = ro.oran_str(kz["oran"])
                kzno = _as_int(kz["no"])
                y_sira = ro.sira_str(kz["sis"])
            elif pd.notna(r["kazanan"]):
                # K97: defter kaydi VAR ama gun sonu 'sonucla' gecisi henuz yapilmadi
                # (defter.sonucla gunde bir kez, son postadan 40 dk sonra calisir - takip.py).
                # Eski metin "defter kaydi yok" diyordu; yaniltiyordu.
                kz_html = (f"<b>{int(r['kazanan'])}</b> "
                           f"<span class=mini>(sistem sirasi gun sonu islenecek)</span>")
                kz_oran = "-"
                kzno = int(r["kazanan"])
                y_sira = "-"
            else:
                kz_html, kz_oran, kzno, y_sira = "<span class=bek>bekleniyor</span>", "-", None, "-"
            k_sira, p_sira = "-", "-"
            if kzno is not None:
                _ka = ro.kupon_ani_bilgi(tarih, pist, seq, ai, kzno)
                k_sira = ro.sira_str(_ka["sis"])
                p_sira = ro.sira_str(_ka["kamu"])          # K103: kamu sirasi geri geldi
            kz_sk = (f"<b>{k_sira}</b> &rarr; {y_sira}<br>"
                     f"<span class=mini>kamu {p_sira}</span>" if kzno is not None else "-")
            H.append(f"<tr><td><b>{ai}</b><br><span class=mini>kosu {int(r['kosu_no'])}</span></td>"
                     f"<td class=l>{kz_html}</td><td>{kz_sk}</td><td>{kz_oran}</td>")
            tum_sec = set()
            for c in cfgler:
                gc = kk[c]["g"]
                sr = gc[gc["ayak"] == ai]
                if sr.empty:
                    H.append("<td class=l><span class=mini>-</span></td>")
                    continue
                sr = sr.iloc[0]
                secimler = [int(x) for x in str(sr["secim"]).split(",") if x != ""]
                tum_sec |= set(secimler)
                # K99: config KENDI cetveliyle secim yapar. bot1 tabanli config'lerde
                # yalniz K (harman) gostermek YANILTIYORDU: bot1 sutununda "K1 K2 K3 K4 K8"
                # gorunup 5. atlanmis gibi duruyor, oysa bot1 KENDI ilk 5'ini kesintisiz
                # almis (o "K8" bot1'in 3. atidir). Bot1 config'lerinde B<sira> once yazilir.
                # (2026-08-09 vakasi: IZMIR 5. ayak, kazanan ROSILDA harman 5. / bot1 6. ->
                #  bot1 kesimin bir altinda kaldigi icin almadi; hata degil ayrisma.)
                bot1_cfg = KONFIG.get(c, {}).get("puan") == "bot1"
                hucre = []
                for no in secimler:
                    # K97: K = kupon anindaki sistem sirasi (KARAR bu vektorle verildi)
                    #      Y = yaris anindaki sistem sirasi (defter, posta-5dk)
                    # K103: P = KAMU (piyasa) sirasi, kupon aninda. K97'de bu sutun
                    # YANLISLIKLA DUSMUSTU: eskiden hucre "sis/kamu" basiyordu, K97 kamu'yu
                    # kaldirip yerine kupon-ani sistemini koydu (eklemek yerine DEGISTIRDI).
                    # Kamu sirasi bu projenin merkezinde: sistemin kalabalikla ayni mi ayri mi
                    # dustugu ondan okunur (K67 bot1'in tum gerekcesi, K68 ayrisma, K98-h tavan).
                    bi = ro.at_bilgi(rk, no) if rk else {}
                    # K105: her config KENDI kurulma anindaki fotografla etiketlenir
                    ka = ro.kupon_ani_bilgi(tarih, pist, seq, ai, no,
                                            dk_grup=KONFIG.get(c, {}).get("dk", 30))
                    ks, ys = ro.sira_str(ka.get("sis")), ro.sira_str(bi.get("sis"))
                    ps = ro.sira_str(ka.get("kamu"))
                    # sistem kamudan 3+ sira AYRI ise isaretle: ayrisma orada
                    ayri = (pd.notna(ka.get("sis")) and pd.notna(ka.get("kamu"))
                            and abs(float(ka["sis"]) - float(ka["kamu"])) >= 3)
                    pstl = " style='color:#6d28d9;font-weight:bold'" if ayri else ""
                    # ikisi 3+ sira ayrildiysa dikkat cek: o ayakta piyasa ciddi kaymis
                    kayar = (pd.notna(ka.get("sis")) and pd.notna(bi.get("sis"))
                             and abs(float(ka["sis"]) - float(bi["sis"])) >= 3)
                    stl = " style='color:#b45309;font-weight:bold'" if kayar else ""
                    et = (f"<b style='color:#137333'>{no}</b>" if no == kzno else f"{no}")
                    if bot1_cfg:
                        bs = ro.sira_str(ka.get("bot1_sira"))
                        # B = SECIMI YAPAN cetvel; K/Y karsilastirma icin
                        hucre.append(f"{et} <span class=mini><b>B{bs}</b></span>"
                                     f" <span class=mini{stl}>K{ks} Y{ys}</span>"
                                     f" <span class=mini{pstl}>P{ps}</span>")
                    else:
                        hucre.append(f"{et} <span class=mini{stl}>K{ks} Y{ys}</span>"
                                     f" <span class=mini{pstl}>P{ps}</span>")
                bk = " <span class=mini>[banker]</span>" if int(sr["banker"]) == 1 else ""
                tuttu = kzno is not None and kzno in secimler
                stil = " style='background:#e8f7ec'" if tuttu else ""
                H.append(f"<td class=l{stil}>" + "<br>".join(hucre) + bk + "</td>")
            H.append("</tr>")
            # o kosunun TUM siralamasi (K58) -- tum turler icin ORTAK.
            # K97: artik IKI satir (kupon ani / yaris ani) ve her ikisi de KOSU NO ile baslar;
            # bu satirin ustteki ayaga mi alttakine mi ait oldugu belirsizligi boylece biter.
            H.append(f"<tr><td></td><td colspan={3+len(cfgler)} class=l "
                     "style='background:#f7f9fc;border-top:none'>"
                     f"{_siralama_html(tarih, pist, seq, ai, int(r['kosu_no']), rk, tum_sec, kzno)}"
                     "</td></tr>")

        def ozet_satir(baslik, fn):
            return (f"<tr><td colspan=4 class=l><b>{baslik}</b></td>"
                    + "".join(f"<td class=l>{fn(kk[c])}</td>" for c in cfgler) + "</tr>")
        H.append(ozet_satir("kombinasyon", lambda k: f"{k['kombo']}"))
        H.append(ozet_satir("kagit bedel", lambda k: ro.para(k["bedel"])))
        H.append(ozet_satir("durum", lambda k: (
            "<span class='rozet rb'>devam</span>" if not k["bitti"] else
            "<span class='rozet r6'>6/6 TUTTU</span>" if k["kademe"] == 6 else
            f"<span class='rozet r{k['kademe']}'>son {k['kademe']} ayak</span>" if k["kademe"] else
            "<span class='rozet r0'>isabetsiz</span>")))
        H.append(ozet_satir("odul", lambda k: ro.para(k["odul"]) if k["odul"] else "&mdash;"))
        H.append(ozet_satir("net", lambda k:
                            f"<span class='{'poz' if k['net'] >= 0 else 'neg'}'>"
                            f"<b>{ro.para(k['net'], isaret=True)}</b></span>"))
        H.append("</table></div></div>")

    H += toplam_blok("TOPLAM DURUM (liste sonu)")

    HTMLA.parent.mkdir(parents=True, exist_ok=True)
    HTMLA.write_text("\n".join(H), encoding="utf-8")
    if ac:
        import webbrowser
        try:
            webbrowser.open(HTMLA.as_uri())
        except Exception:
            pass
    return HTMLA


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pist")
    ap.add_argument("--tarih", default=date.today().isoformat())
    ap.add_argument("--sonucla", action="store_true")
    ap.add_argument("--duzelt", action="store_true", help="K64: basabas geriye duzeltme (yeniden sonucla)")
    ap.add_argument("--html", action="store_true")
    args = ap.parse_args()

    if args.duzelt:
        yeniden_sonucla()
    elif args.sonucla:
        sonucla_altili()
    elif args.html:
        p = html_yaz(ac=True)
        print(f"HTML: {p}")
    elif args.pist:
        ymd = datetime.strptime(args.tarih, "%Y-%m-%d").strftime("%Y%m%d")
        n = kupon_hazirla(args.pist.strip().upper(), ymd, args.tarih)
        if n:
            html_yaz()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
