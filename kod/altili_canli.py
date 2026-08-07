"""
altili_canli.py — CANLI ALTILI kupon uretimi + takibi (K53). GERCEK BAHIS DEGIL (K48; +EV yok,
K52 backtest OOS -%32). Amac: izleme/ogrenme — kuponu ilk kosu baslamadan kur, kosular ilerledikce
ayak sonuclarini + nihai Altili isabetini isle, basari oranini ACIK dille/gorselle goster.

AYRI dosya/sayfa: veri/altili_kupon.csv + raporlar/altili.html. defter/paper'a DOKUNMAZ.

Kupon mantigi (K52 backtest'iyle AYNI cekirdek: altili_backtest.kupon_kur):
  banker (Bot2 guveni >= esik -> tek at) + spread (kumulatif kapsam) + butce tavani.
  DORT config: 'dar' (<=24), 'orta' (<=96, K53), 'genis' (<=288, K57) ve 'genis900'
  (kapsam 0.95, <=900 kombo; K62 gozlem akisi -- derin kazananlari da kapsar, ~900-1125 TL).
  K57: orta genisletilmedi (backtest: kazanc yok, dar zemin -%19'dan kotu); genis AYRI stream
  olarak eklendi (kullanici istegi, iyilestirme iddiasi degil; -EV oldugu backtest'te olculu).
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
# config -> ayarlar. Alanlar:
#   kapsam  : kumulatif kapsam esigi (SADECE dagitim="kapsam" kullanir)
#   kombo   : butce tavani (kombinasyon)
#   dagitim : "kapsam"  = K52 mantigi (kapsam esigi + butce asilinca en kalabalik ayaktan buda)
#             "acgozlu" = K65 isabet-maksimize (log-uzayinda sirt cantasi; kapsam alani KULLANILMAZ)
#             "ayrisma" = K68 acgozlu'nun ayrisma-agirlikli hali
#   puan    : secim hangi olasilikla yapilir -- "bot2" (harman) veya "bot1" (oran-kor)
#   aile    : rapor/Telegram gruplamasi
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
AYRISMA_W = 1.0
KONFIG = {
    "dar":        {"kapsam": 0.75, "kombo": 24,  "dagitim": "kapsam",  "puan": "bot2", "aile": "kamu"},
    "orta":       {"kapsam": 0.75, "kombo": 96,  "dagitim": "kapsam",  "puan": "bot2", "aile": "kamu"},
    "genis":      {"kapsam": 0.75, "kombo": 288, "dagitim": "kapsam",  "puan": "bot2", "aile": "kamu"},
    "genis900":   {"kapsam": 0.95, "kombo": 900, "dagitim": "kapsam",  "puan": "bot2", "aile": "kamu"},
    "acgozlu900": {"kapsam": 0.95, "kombo": 900, "dagitim": "acgozlu", "puan": "bot2", "aile": "kamu"},
    "bot1_900":   {"kapsam": 0.95, "kombo": 900, "dagitim": "acgozlu", "puan": "bot1", "aile": "temel"},
    "ayrisma900": {"kapsam": 0.95, "kombo": 900, "dagitim": "ayrisma", "puan": "bot2", "aile": "ayrisma"},
    # K92: uzak ayagin olasiligi OLCULMUS lambda ile duzlestirilir (bkz. kupon_kur_kalibre).
    # acgozlu900 ile TEK farki budur -> aradaki her fark uzak-ayak duzeltmesine atfedilebilir.
    "acgozlu_v2": {"kapsam": 0.95, "kombo": 900, "dagitim": "kalibre", "puan": "bot2", "aile": "kalibre"},
}
AILE_AD = {"kamu":    "KAMU BOTU (bot2 — piyasayı dinler)",
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
def kupon_hazirla(pist, ymd, tarih, sadece_seq=None):
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

    yeni_satirlar = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    for seq, pencere, ilk_saat in pencereler:
        # her ayagin (no, bot2) VE (no, bot1) listesi + ayrisma skoru
        # -- Bot2'si olmayan ayak varsa pencere ATLANIR (eskisi gibi)
        ayak_atlari, ayak_bot1, ayak_ayr, ayak_meta, eksik = [], [], [], [], False
        for k in pencere:
            kno = _as_int(k.get("RACENO") or k.get("NO"))
            g = tg[tg["kosu_no_i"] == kno]
            g = g[pd.to_numeric(g["bot2"], errors="coerce").notna()]
            if len(g) < 4:                    # <4 atli / puansiz ayak -> Altili kurulamaz
                eksik = True
                break
            atlar = [(int(r["no"]), float(r["bot2"])) for _, r in g.iterrows()]
            ayak_atlari.append(atlar)
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

        for cfg, ay in KONFIG.items():
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
    print(f"{pist} {tarih}: {n} kupon kuruldu ({len(pencereler)} Altili x {len(KONFIG)} config).")
    return n


# ----------------------------- Telegram bildirimi (K60) -----------------------------
def _at_ad_map(o):
    """program JSON -> {race_kod: {at_no: at_ad}} (kupon atlarini isimle yazmak icin)."""
    m = {}
    for k in o.get("kosular", []):
        m[_as_int(k.get("KOD"))] = {_as_int(a.get("NO")): a.get("AD") for a in k.get("atlar", [])}
    return m


def bildir_kupon(pist, tarih, seq, o):
    """Kurulan (pist,seq) Altili kuponunu Telegram'dan NUMARA + ISIMLE bildir (uc config).
    telegram_at config'i yoksa sessizce gecer (bot kurulmadan da guvenli). try-korumali cagirilir."""
    import telegram_at
    df = _oku()
    g = df[(df["tarih"] == tarih) & (df["pist"] == pist)
           & (pd.to_numeric(df["seq"], errors="coerce") == seq)]
    if g.empty:
        return
    admap = _at_ad_map(o)
    tarih_tr = pd.Timestamp(str(tarih)).strftime("%d.%m.%Y")
    ilk_saat = str(g["ilk_saat"].iloc[0])
    sat = ["🎫 <b>ALTILI KUPONU KURULDU</b>",
           f"📍 {pist} — {tarih_tr}, {int(seq)}. Altılı",
           f"🕐 İlk koşu {ilk_saat} (30 dk kala)", ""]
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
    ref = g_all[g_all["config"] == next(iter(KONFIG))].sort_values("ayak")
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
def kupon_zamani_kur(pistler, ymd, tarih, dk_kala=30):
    """takip.py her turda cagirir. Her Altili penceresi icin: ilk kosusuna <=dk_kala kaldiysa
    VE ilk kosu HENUZ baslamadiysa VE bugun bu (pist,seq) icin kupon YOKSA -> kur.
    Idempotent (kurulmus olani atlar). Doner: kurulan kupon sayisi. Hata firlatmaz (takip guvenligi)."""
    kurulan = 0
    df = _oku()
    now = datetime.now()
    for pist in pistler:
        try:
            o = getjson(f"{BASE}/program/{ymd}/full/{pist}.json")
            if o.get("_hata"):
                continue
            for seq, pencere, ilk_saat in altili_pencereleri(o):
                if len(df) and ((df["tarih"] == tarih) & (df["pist"] == pist)
                                & (df["seq"] == seq)).any():
                    continue                       # zaten kurulmus
                try:
                    ilk_post = datetime.strptime(f"{tarih} {ilk_saat}", "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
                if ilk_post - timedelta(minutes=dk_kala) <= now < ilk_post:
                    n = kupon_hazirla(pist, ymd, tarih, sadece_seq=seq)
                    kurulan += n
                    df = _oku()
                    if n:                              # K60: yeni kupon -> Telegram bildirimi
                        try:
                            bildir_kupon(pist, tarih, seq, o)
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
    ('dort boyda kurulur') ve 7 ture cikinca bayatladi -> artik bayatlayamaz."""
    sat = []
    for aile, ad in AILE_AD.items():
        cs = [c for c, ay in KONFIG.items() if ay["aile"] == aile]
        if not cs:
            continue
        sat.append(f"&nbsp;&nbsp;<b>{ad}</b> &rarr; " + ", ".join(
            f"{c.upper()} <span class=mini>(~{KONFIG[c]['kombo']} kombo, "
            f"{KONFIG[c]['dagitim']})</span>" for c in cs))
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


def _tum_siralama_html(rk, secimler):
    """K58: o kosudaki TUM atlar SISTEM sirasina gore (ayri satirda). Bizim sectigimiz KALIN,
    kazanan YESIL kutu + tik. defter'den (salt-okunur). Kayit yoksa acikca soyler."""
    # K81: eskiden iki dal da AYNI cumleyi basiyordu -> 31 Tem'de bugunun 24 ayaginin
    # hepsinde uyari cikti, sayfa yeniden uretilince sifira dustu ve SEBEP ANLASILAMADI.
    # Artik hangi dalin yandigi ve hangi race_kod oldugu yaziliyor; tekrarlarsa teshis anlik.
    if not rk:
        return ("<span class=mini>sistemin siralamasi: bu ayagin <b>race_kod'u yok</b> "
                "(kupon kaydinda bos)</span>")
    g = ro.kosu_atlari(rk)
    if g is None or len(g) == 0:
        return (f"<span class=mini>sistemin siralamasi: <b>defter'de {rk} kaydi bulunamadi</b> "
                f"&mdash; gun sonu 'sonucla' gecisinden once bakildiysa normaldir, "
                f"sayfayi 22:30'dan sonra tazele</span>")
    g = g.copy()
    g["mr"] = pd.to_numeric(g["model_rank"], errors="coerce")
    g = g.sort_values("mr", na_position="last")
    secset = {int(x) for x in secimler}
    parcalar = []
    for _, r in g.iterrows():
        if pd.isna(r.get("no")):
            continue
        no = int(r["no"])
        etiket = f"{ro.sira_str(r['mr'])}<b>#{no}</b>" if no in secset else f"{ro.sira_str(r['mr'])}#{no}"
        if pd.notna(r.get("sonuc")) and int(r["sonuc"]) == 1:
            etiket = (f"<span style='background:#d9f7d9;padding:0 4px;border-radius:3px'>"
                      f"{etiket}&nbsp;&#10003;</span>")
        parcalar.append(etiket)
    return ("<span class=mini>Sistemin tum siralamasi "
            "(<b>kalin</b>=bizim sectigimiz, yesil &#10003;=kazanan): </span>"
            + " &nbsp; ".join(parcalar))


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
         f"Su an <b>{len(KONFIG)} kupon turu</b> paralel izleniyor "
         "(K78: metin KONFIG'den uretilir, elle guncellenmez):<br>" + _tur_ozeti() +
         "<br>Birim fiyat 2026 tarifesi: Ist/Ank/Izm/Ada/Bur/Koc/Ant 1,25 TL, "
         "Elazig/Urfa/Diyarbakir 1,00 TL.<br>"
         "<b>Odul yalniz 6/6 tam isabette</b> odenir; 5/4/3 ayak TJK'da AYRI bahistir "
         "(teselli degil) &mdash; tabloda yalnizca bilgi amacli gosterilir.</div>"]

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
            H2.append(f"<div style='margin:6px 0'><b>{cfg.upper()}</b> "
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
        H.append("<div style='overflow-x:auto'><table>")
        H.append("<tr><th>ayak</th><th class=l>KAZANAN AT</th><th>kazananin<br>sistem / kamu</th>"
                 "<th>ganyan<br>orani</th>"
                 + "".join(f"<th class=l>{c.upper()}<br><span class=mini>{KONFIG[c]['aile']}</span></th>"
                           for c in cfgler) + "</tr>")
        for _, r in ref.iterrows():
            ai = int(r["ayak"])
            rk = int(r["race_kod"]) if pd.notna(r["race_kod"]) else None
            kz = ro.kazanan_bilgi(rk) if rk else None
            if kz:
                kz_html = f"<b>{kz['no']}</b> {str(kz['ad'])[:20]}"
                kz_sk = f"{ro.sira_str(kz['sis'])} / {ro.sira_str(kz['kamu'])}"
                kz_oran = ro.oran_str(kz["oran"])
                kzno = _as_int(kz["no"])
            elif pd.notna(r["kazanan"]):
                kz_html = f"<b>{int(r['kazanan'])}</b> <span class=mini>(defter kaydi yok)</span>"
                kz_sk = kz_oran = "-"
                kzno = int(r["kazanan"])
            else:
                kz_html, kz_sk, kz_oran, kzno = "<span class=bek>bekleniyor</span>", "-", "-", None
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
                hucre = []
                for no in secimler:
                    bi = ro.at_bilgi(rk, no) if rk else {}
                    et = (f"<b style='color:#137333'>{no}</b>" if no == kzno else f"{no}")
                    hucre.append(f"{et} <span class=mini>{ro.sira_str(bi.get('sis'))}/"
                                 f"{ro.sira_str(bi.get('kamu'))}</span>")
                bk = " <span class=mini>[banker]</span>" if int(sr["banker"]) == 1 else ""
                tuttu = kzno is not None and kzno in secimler
                stil = " style='background:#e8f7ec'" if tuttu else ""
                H.append(f"<td class=l{stil}>" + "<br>".join(hucre) + bk + "</td>")
            H.append("</tr>")
            # o kosunun TUM sistem siralamasi (K58) -- tum turler icin ORTAK, tek satir
            H.append(f"<tr><td></td><td colspan={3+len(cfgler)} class=l "
                     "style='background:#f7f9fc;border-top:none'>"
                     f"{_tum_siralama_html(rk, tum_sec)}</td></tr>")

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
