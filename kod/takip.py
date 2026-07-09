"""
takip.py — GUNLUK OTOMATIK TAKIP (sabah baslat, gun boyu kossun). KAR DEGIL; kagit-ticaret.
Sabah bir kez calistir; gun boyu kendi dongusunde:
  - gunun yerli pistlerini + (Ingiliz + Arap, K46) kosu saatlerini cikarir,
  - her kosuyu SAAT'ine ~5 dk kala CANLI oranla analiz eder (tum atlari kendi AGF'siyle
    siralar) -> ekrana + rapor dosyasina yazar + deftere isler,
  - tum kosular bitince defter.sonucla calistirir.
PC yaris saatlerinde ACIK/uyanik olmali (yerel script; uyurken tetiklenmez).

Kullanim:
    python takip.py                      # bugun, tum yerli pistler, canli dongu
    python takip.py --pist ANKARA        # sadece bu pist
    python takip.py --once               # su an vakti gelmis kosulari bir kez isle ve cik (test/zamanlayici)
    python takip.py --dk 6 --bekle 60    # kac dk kala / dongu bekleme sn
"""
import argparse
import sys
import time
from datetime import date, datetime
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from gunluk import hesapla, kosu_rapor, yerli_pistler, getjson, BASE, EXCL  # noqa: E402
from duzlestir import irk_of  # noqa: E402
import defter  # noqa: E402

RAPOR = KOK / "raporlar" / "gunluk"
_KILIT = None


def tek_instans():
    """Ikinci takip ornegini engelle (K43: zamanlanmis gorev + elle baslatma cakisirsa iki kopya
    ayni CSV'lere yazardi). Kilit dosyasi surec boyunca ACIK tutulur; surec olunce OS kilidi
    kendiliginden birakir -> bayat kilit sorunu yok."""
    global _KILIT
    import msvcrt
    _KILIT = open(KOK / "veri" / "takip.kilit", "w")
    try:
        msvcrt.locking(_KILIT.fileno(), msvcrt.LK_NBLCK, 1)
        return True
    except OSError:
        return False


def program_kosulari(pist, ymd, tarih):
    """pist programindan Ingiliz + Arap kosularinin (no, saat, post_dt) listesi (K46:
    Arap modeli eklendi; 'diger' irk haric)."""
    o = getjson(f"{BASE}/program/{ymd}/full/{pist}.json")
    if o.get("_hata"):
        print(f"  {pist}: program yok ({o['_hata']})")
        return []
    out = []
    for k in o.get("kosular", []):
        if irk_of(k.get("GRUP_TR"), k.get("GRUPKISA")) not in ("Ingiliz", "Arap"):
            continue
        no = k.get("RACENO") or k.get("NO")
        saat = str(k.get("SAAT", "")).strip()
        try:
            post = datetime.strptime(f"{tarih} {saat}", "%Y-%m-%d %H:%M")
            no = int(no)
        except (ValueError, TypeError):
            continue
        out.append({"pist": pist, "no": no, "saat": saat, "post": post, "durum": "bekliyor"})
    return out


def isle_kosu(pist, ymd, tarih, no, saat, dosya):
    """Tek kosuyu canli cek -> rapor (ekran+dosya) + deftere isle."""
    try:
        raw, tg, (span, alpha, gamma) = hesapla(pist, ymd)
    except RuntimeError as e:
        print(f"  HATA {pist} kosu {no}: {e}")
        return False
    rk = raw[pd.to_numeric(raw["kosu_no"], errors="coerce") == no]
    if rk.empty:
        print(f"  {pist} kosu {no}: programda yok (cikmis olabilir)")
        return False
    scored = None
    if tg is not None and len(tg):
        s = tg[pd.to_numeric(tg["kosu_no"], errors="coerce") == no]
        scored = s if len(s) else None

    bas = (f"\n[{datetime.now():%H:%M} tetik]  {pist}  KOSU {no} (yaris {saat})  "
           f"[{span}]")
    blok = bas + "\n" + "\n".join(kosu_rapor(rk, scored))
    print(blok)
    with open(dosya, "a", encoding="utf-8") as f:
        f.write(blok + "\n")
    try:
        nk, n = defter.yaz_tg(tg, tarih, pist, only_kosu=no)
        if n:
            defter.html_yaz()   # tarayici tablosunu tazele
        print(f"  -> deftere islendi ({n} at)" if n else "  -> (deftere yazilmadi: kapsam disi/gecmis)")
    except Exception as e:
        # defter.csv kilitli (or. Excel'de acik) vb. -> GUNUN TAKIBI COKMESIN (K39);
        # rapor dosyasi/ekran zaten yazildi, sadece defter kaydi bu kosuda dusmus olur.
        print(f"  -> DEFTER YAZILAMADI ({type(e).__name__}: {e}) -> dosyayi kapat; takip devam ediyor")
    try:
        # K42 paper test: ayri dosya/sayfa; hata takibi ASLA bozmasin
        import paper
        if scored is not None and len(scored):
            npk = paper.kupon_uret(scored, tarih, pist)
            if npk:
                paper.html_yaz()
                print(f"  -> paper: {npk} kupon acildi (K42; raporlar/paper.html)")
    except Exception as e:
        print(f"  -> paper kupon uretilemedi ({type(e).__name__}) - takip devam ediyor")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pist", default=None, help="tek pist (bos -> gunun tum yerli pistleri)")
    ap.add_argument("--tarih", default=date.today().isoformat())
    ap.add_argument("--dk", type=int, default=5, help="kosuya kac dk kala tetikle")
    ap.add_argument("--bekle", type=int, default=60, help="dongu bekleme (sn)")
    ap.add_argument("--once", action="store_true", help="vakti gelmisleri bir kez isle ve cik")
    args = ap.parse_args()
    ymd = datetime.strptime(args.tarih, "%Y-%m-%d").strftime("%Y%m%d")

    if not tek_instans():
        print("takip ZATEN calisiyor (baska pencere/zamanlanmis gorev) -> bu kopya kapaniyor (K43).")
        return

    pistler = [args.pist.strip().upper()] if args.pist else [p for p, _ in yerli_pistler(ymd)]
    # K4: 4 supheli pist (sike soylentisi) hem tahmin hem takip DISI
    atilan = [p for p in pistler if p in EXCL]
    pistler = [p for p in pistler if p not in EXCL]
    if atilan:
        print(f"K4: {', '.join(atilan)} (sike supheli) -> takip DISI.")
    if not pistler:
        print(f"{args.tarih}: takip edilecek (izinli) yerli pist yok.")
        return

    sched = []
    for p in pistler:
        sched += program_kosulari(p, ymd, args.tarih)
    sched.sort(key=lambda r: r["post"])
    if not sched:
        print(f"{args.tarih}: Ingiliz/Arap kosusu yok ({', '.join(pistler)}).")
        return

    RAPOR.mkdir(parents=True, exist_ok=True)
    dosya = RAPOR / f"{args.tarih}_{'_'.join(pistler)}.txt"
    print("=" * 70)
    print(f"TAKIP basladi  {args.tarih}  pist: {', '.join(pistler)}  "
          f"Ingiliz+Arap kosu: {len(sched)}  (yaris-{args.dk}dk kala)")
    print("KAR DEGIL — kagit-ticaret. AGF%(sis)=sistemin kendi AGF'si. Rapor: " + str(dosya.name))
    for r in sched:
        print(f"   {r['pist']:10s} kosu {r['no']:>2}  yaris {r['saat']}  tetik ~{(r['post'] - pd.Timedelta(minutes=args.dk)):%H:%M}")
    print("=" * 70)

    while True:
        now = datetime.now()
        # posta saati GECMIS kosu islenmez (K36): yaris-sonrasi oranla "tahmin" kaydi deneyi bozar.
        # (takip'i oglen baslatinca sabahki kosular buraya duser; ekrana da analiz basilmaz.)
        for r in sched:
            if r["durum"] == "bekliyor" and now > r["post"] + pd.Timedelta(minutes=3):
                r["durum"] = "gecmis"
                print(f"  {r['pist']} kosu {r['no']} (yaris {r['saat']}): posta saati gecti "
                      f"-> islenmedi (defter korumasi)")
        bekleyen = [r for r in sched if r["durum"] == "bekliyor"]
        vakti = [r for r in bekleyen if args.once or now >= r["post"] - pd.Timedelta(minutes=args.dk)]
        for r in vakti:
            ok = isle_kosu(r["pist"], ymd, args.tarih, r["no"], r["saat"], dosya)
            # gecici hata (ag vb.) kosuyu YAKMASIN (K39): posta saatine kadar dongude yeniden dene;
            # post gecerse yukaridaki suzgec "gecmis" yapar. --once'ta tek deneme.
            if ok:
                r["durum"] = "bitti"
            elif args.once or datetime.now() > r["post"]:
                r["durum"] = "atlandi"

        kalan = [r for r in sched if r["durum"] == "bekliyor"]
        if not kalan or args.once:
            print(f"\n{datetime.now():%H:%M}  isleme bitti "
                  f"({sum(r['durum']=='bitti' for r in sched)}/{len(sched)} kosu).")
            if not args.once:
                # sonuclar feed'i yarislardan ~dakikalar sonra dolar; son kosudan hemen once
                # sonucla cagirmak bos donerdi (K39) -> son post + 40 dk beklenir.
                hedef = max(r["post"] for r in sched) + pd.Timedelta(minutes=40)
                if datetime.now() < hedef:
                    print(f"sonuclarin dolmasi icin ~{hedef:%H:%M} bekleniyor (pencere acik kalsin)...")
                    while datetime.now() < hedef:
                        time.sleep(min(60.0, max(1.0, (hedef - datetime.now()).total_seconds())))
            print("sonucla...")
            defter.sonucla()
            break
        nxt = min(r["post"] for r in kalan) - pd.Timedelta(minutes=args.dk)
        print(f"{now:%H:%M}  bekleyen {len(kalan)} kosu; sonraki tetik ~{nxt:%H:%M}. "
              f"({args.bekle}sn uyku)", flush=True)
        time.sleep(args.bekle)


if __name__ == "__main__":
    main()
