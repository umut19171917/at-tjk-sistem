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
from altili_backtest import kupon_kur  # noqa: E402
from duzlestir import vir_float  # noqa: E402
import rapor_ortak as ro  # noqa: E402

KUPON = KOK / "veri" / "altili_kupon.csv"
HTMLA = KOK / "raporlar" / "altili.html"
# K62: config -> (kapsam_esik, max_kombo). genis900 YUKSEK kapsam (0.95) ki derin (5./6. sira)
# kazananlara ulassin (0.75 onlara varmadan doluyor). Hepsi -EV gozlem akisi; backtest K52/K57/K62.
KONFIG = {"dar": (0.75, 24), "orta": (0.75, 96), "genis": (0.75, 288), "genis900": (0.95, 900)}
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
        # her ayagin (no, bot2) listesi -- puani olmayan ayak varsa pencere ATLANIR
        ayak_atlari, ayak_meta, eksik = [], [], False
        for k in pencere:
            kno = _as_int(k.get("RACENO") or k.get("NO"))
            g = tg[tg["kosu_no_i"] == kno]
            g = g[pd.to_numeric(g["bot2"], errors="coerce").notna()]
            if len(g) < 4:                    # <4 atli / puansiz ayak -> Altili kurulamaz
                eksik = True
                break
            atlar = [(int(r["no"]), float(r["bot2"])) for _, r in g.iterrows()]
            ayak_atlari.append(atlar)
            ayak_meta.append({"kosu_no": kno, "race_kod": _as_int(k.get("KOD")),
                              "saat": str(k.get("SAAT", "")).strip()})
        if eksik:
            print(f"  {seq}. Altili (kosu {pencere[0].get('RACENO')}): bir ayak kapsam disi -> atlandi")
            continue

        for cfg, (kaps, maxk) in KONFIG.items():
            sec = kupon_kur(ayak_atlari, kaps, maxk, BANKER_ESIK)
            for ai in range(6):
                atlar_sirali = sorted(ayak_atlari[ai], key=lambda x: -x[1])
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
    for cfg in KONFIG:                                 # dar, orta, genis
        gc = g[g["config"] == cfg].sort_values("ayak")
        if gc.empty:
            continue
        kombo = int(np.prod([int(x) for x in gc["nat"]]))
        bedel = kombo * ro.birim_fiyat(pist)
        sat.append(f"<b>{cfg.upper()}</b> — {kombo} kombo / {ro.para(bedel)}")
        for _, r in gc.iterrows():
            adm = admap.get(_as_int(r["race_kod"]), {})
            secim = [int(x) for x in str(r["secim"]).split(",") if x != ""]
            atlar = ", ".join(f"{no} {adm.get(no, '?')}" for no in secim)
            bank = " (banker)" if int(r["banker"]) == 1 else ""
            sat.append(f"  {int(r['ayak'])}. ayak (koşu {int(r['kosu_no'])}): {atlar}{bank}")
        sat.append("")
    sat.append("Detay/takip: raporlar/altili.html")
    telegram_at.gonder("\n".join(sat))


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
    for cfg in KONFIG:
        gc = g_all[g_all["config"] == cfg].sort_values("ayak")
        if gc.empty:
            continue
        oz = _kupon_ozet(gc, tarih, pist, seq, cfg)
        kad = oz["kademe"]
        durum = "✅ 6/6 TUTTU" if kad == 6 else (f"son {kad} ayak (bilgi)" if kad else "tutmadı")
        sat.append(f"<b>{cfg.upper()}</b>: {durum} — bedel {ro.para(oz['bedel'])}, "
                   f"ödül {ro.para(oz['odul'])}, net {ro.para(oz['net'], isaret=True)}")
    res = ro.altili_odeme(tarih, pist, int(seq), cek=False)
    if res.get("temettu"):
        sat.append(f"\n💰 Resmi temettü (1 birim): {ro.para(res['temettu'])}")
    elif res.get("devir"):
        sat.append(f"\n↪️ Kimse bilemedi — {ro.para(res['devir'])} devretti")
    sat.append("\nDetay: raporlar/altili.html")
    telegram_at.gonder("\n".join(sat))


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


def _resmi_satir(k):
    """O Altili'nin RESMI odemesi — kupon tutmasa da gosterilir (kacirilan odul)."""
    r = k.get("resmi") or {}
    if r.get("temettu"):
        t = ro.para(r["temettu"])
        if k["kademe"] == 6:
            return f"<b>resmi temettu (1 birim): {t}</b> &mdash; bu kuponla tutturuldu"
        return (f"resmi temettu (1 birim): <b>{t}</b> "
                f"<span class=mini>&mdash; bu Altili'yi bilenlerin aldigi; biz tutturamadik</span>")
    if r.get("devir"):
        return (f"<b>KIMSE BILEMEDI</b> &mdash; {ro.para(r['devir'])} "
                f"<span class=mini>sonraki cekilise devretti (bu Altili'da odeme yapilmadi)</span>")
    if not k["bitti"]:
        return "<span class=mini>resmi temettu: kosular bitince belli olacak</span>"
    return "<span class=mini>resmi temettu: bilinmiyor (feed'den alinamadi)</span>"


def _tum_siralama_html(rk, secimler):
    """K58: o kosudaki TUM atlar SISTEM sirasina gore (ayri satirda). Bizim sectigimiz KALIN,
    kazanan YESIL kutu + tik. defter'den (salt-okunur). Kayit yoksa acikca soyler."""
    if not rk:
        return "<span class=mini>sistemin siralamasi: bu kosunun defter kaydi yok</span>"
    g = ro.kosu_atlari(rk)
    if g is None or len(g) == 0:
        return "<span class=mini>sistemin siralamasi: bu kosunun defter kaydi yok</span>"
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
         "Kupon dort boyda kurulur: <b>DAR</b> (~16 kombo), <b>ORTA</b> (~72-96), "
         "<b>GENIS</b> (~288) ve <b>GENIS900</b> (kapsam 0.95, ~900 kombo/~1125 TL; K62 gozlem "
         "akisi -- backtest'te en cok kaybeden, sadece merak icin izleniyor). "
         "Birim fiyat 2026 tarifesi: Ist/Ank/Izm/Ada/Bur/Koc/Ant 1,25 TL, "
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

    kupolar.sort(key=lambda k: (str(k["tarih"]), k["pist"], k["seq"], k["cfg"]), reverse=True)
    H.append("<h3>Kuponlar (yeni tarih ustte)</h3>")
    for k in kupolar:
        g, tut = k["g"], k["tut"]
        kad = k["kademe"]
        if not k["bitti"]:
            rozet = "<span class='rozet rb'>kosular devam ediyor</span>"
        elif kad == 6:
            rozet = "<span class='rozet r6'>TAM ISABET 6/6</span>"
        elif kad:
            rozet = f"<span class='rozet r{kad}'>son {kad} ayak (bilgi)</span>"
        else:
            rozet = "<span class='rozet r0'>isabetsiz</span>"
        tarih_tr = pd.Timestamp(str(k["tarih"])).strftime("%d.%m.%Y")
        net_cls = "poz" if k["net"] >= 0 else "neg"
        H.append("<div class=kart>")
        H.append(f"<div class=baslik>{tarih_tr} &nbsp;|&nbsp; <b>{k['pist']}</b> &nbsp;|&nbsp; "
                 f"{k['seq']}. ALTILI &nbsp;|&nbsp; <b>{k['cfg'].upper()}</b> kupon "
                 f"({k['kombo']} kombinasyon) &nbsp; {rozet}<br>"
                 f"<span class=k>kupon bedeli <b>{ro.para(k['bedel'])}</b> &nbsp;&rarr;&nbsp; "
                 f"bizim odulumuz <b>{ro.para(k['odul'])}</b> &nbsp;&rarr;&nbsp; net "
                 f"<span class='{net_cls}'><b>{ro.para(k['net'], isaret=True)}</b></span>"
                 f"<br>{_resmi_satir(k)}</span></div>")
        H.append("<table><tr><th>ayak</th><th>kosu</th><th class=l>BIZIM SECIMIMIZ "
                 "<span class=mini>(at no &mdash; sistem sirasi / kamu sirasi)</span></th>"
                 "<th class=l>KAZANAN AT</th><th>kazananin<br>sistem sirasi</th>"
                 "<th>kazananin<br>kamu sirasi</th><th>ganyan<br>orani</th><th>sonuc</th></tr>")
        for _, r in g.iterrows():
            rk = int(r["race_kod"]) if pd.notna(r["race_kod"]) else None
            secimler = [int(x) for x in str(r["secim"]).split(",") if x != ""]
            parcalar = []
            for no in secimler:
                bi = ro.at_bilgi(rk, no) if rk else {"sis": None, "kamu": None}
                parcalar.append(f"<b>{no}</b> <span class=mini>({ro.sira_str(bi['sis'])}"
                                f" / {ro.sira_str(bi.get('kamu'))})</span>")
            sec_html = " &nbsp;&middot;&nbsp; ".join(parcalar)
            if int(r["banker"]) == 1:
                sec_html += " <span class=mini>[banker]</span>"
            kz = ro.kazanan_bilgi(rk) if rk else None
            if kz:
                kz_html = f"<b>{kz['no']}</b> {str(kz['ad'])[:22]}"
                kz_sis, kz_kamu, kz_oran = (ro.sira_str(kz["sis"]), ro.sira_str(kz["kamu"]),
                                            ro.oran_str(kz["oran"]))
            elif pd.notna(r["kazanan"]):
                kz_html = f"<b>{int(r['kazanan'])}</b> <span class=mini>(defter kaydi yok)</span>"
                kz_sis = kz_kamu = kz_oran = "-"
            else:
                kz_html, kz_sis, kz_kamu, kz_oran = "<span class=bek>bekleniyor</span>", "-", "-", "-"
            t = tut[int(r["ayak"]) - 1]
            if t is None:
                scls, stxt = "bek", "bekleniyor"
            elif t == 1:
                scls, stxt = "tut", "TUTTU"
            else:
                scls, stxt = "kac", "kacti"
            H.append(f"<tr><td>{int(r['ayak'])}</td><td>{int(r['kosu_no'])}</td>"
                     f"<td class=l>{sec_html}</td><td class=l>{kz_html}</td>"
                     f"<td>{kz_sis}</td><td>{kz_kamu}</td><td>{kz_oran}</td>"
                     f"<td class={scls}>{stxt}</td></tr>")
            # K58: o kosunun TUM sistem siralamasi -- ayaginin hemen altinda ayri satir
            H.append("<tr><td></td><td colspan=7 class=l "
                     "style='background:#f7f9fc;border-top:none'>"
                     f"{_tum_siralama_html(rk, secimler)}</td></tr>")
        H.append("</table></div>")

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
