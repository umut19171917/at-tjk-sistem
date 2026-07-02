"""
takip.py — GUNLUK OTOMATIK TAKIP (sabah baslat, gun boyu kossun). KAR DEGIL; kagit-ticaret.
Sabah bir kez calistir; gun boyu kendi dongusunde:
  - gunun yerli pistlerini + (yalniz Ingiliz) kosu saatlerini cikarir,
  - her Ingiliz kosusunu SAAT'ine ~5 dk kala CANLI oranla analiz eder (tum atlari kendi AGF'siyle
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


def program_kosulari(pist, ymd, tarih):
    """pist programindan SADECE Ingiliz kosularinin (no, saat, post_dt) listesi."""
    o = getjson(f"{BASE}/program/{ymd}/full/{pist}.json")
    if o.get("_hata"):
        print(f"  {pist}: program yok ({o['_hata']})")
        return []
    out = []
    for k in o.get("kosular", []):
        if irk_of(k.get("GRUP_TR"), k.get("GRUPKISA")) != "Ingiliz":
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
           f"model a={alpha:+.2f} g={gamma:+.2f}")
    blok = bas + "\n" + "\n".join(kosu_rapor(rk, scored))
    print(blok)
    with open(dosya, "a", encoding="utf-8") as f:
        f.write(blok + "\n")
    nk, n = defter.yaz_tg(tg, tarih, pist, only_kosu=no)
    if n:
        defter.html_yaz()   # tarayici tablosunu tazele
    print(f"  -> deftere islendi ({n} at)" if n else "  -> (model kapsam disi, deftere islenmedi)")
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
        print(f"{args.tarih}: Ingiliz kosusu yok ({', '.join(pistler)}).")
        return

    RAPOR.mkdir(parents=True, exist_ok=True)
    dosya = RAPOR / f"{args.tarih}_{'_'.join(pistler)}.txt"
    print("=" * 70)
    print(f"TAKIP basladi  {args.tarih}  pist: {', '.join(pistler)}  "
          f"Ingiliz kosu: {len(sched)}  (yaris-{args.dk}dk kala)")
    print("KAR DEGIL — kagit-ticaret. AGF%(sis)=sistemin kendi AGF'si. Rapor: " + str(dosya.name))
    for r in sched:
        print(f"   {r['pist']:10s} kosu {r['no']:>2}  yaris {r['saat']}  tetik ~{(r['post'] - pd.Timedelta(minutes=args.dk)):%H:%M}")
    print("=" * 70)

    while True:
        now = datetime.now()
        bekleyen = [r for r in sched if r["durum"] == "bekliyor"]
        vakti = [r for r in bekleyen if args.once or now >= r["post"] - pd.Timedelta(minutes=args.dk)]
        for r in vakti:
            ok = isle_kosu(r["pist"], ymd, args.tarih, r["no"], r["saat"], dosya)
            r["durum"] = "bitti" if ok else "atlandi"

        kalan = [r for r in sched if r["durum"] == "bekliyor"]
        if not kalan or args.once:
            print(f"\n{datetime.now():%H:%M}  isleme bitti "
                  f"({sum(r['durum']=='bitti' for r in sched)}/{len(sched)} kosu). sonucla...")
            defter.sonucla()
            break
        nxt = min(r["post"] for r in kalan) - pd.Timedelta(minutes=args.dk)
        print(f"{now:%H:%M}  bekleyen {len(kalan)} kosu; sonraki tetik ~{nxt:%H:%M}. "
              f"({args.bekle}sn uyku)", flush=True)
        time.sleep(args.bekle)


if __name__ == "__main__":
    main()
