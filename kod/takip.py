"""
takip.py — DURUMSUZ GECIS takibi (K49). KAR DEGIL; kagit-ticaret.
K43-K47 dersi: "butun gun yasamak zorunda olan tek surec" laptop ortaminda kirilgan
(uyku/kapak/pencere/cokme -> 16-17 Tem kosu kayiplari). Yeni model: zamanlanmis gorev
HER 15 DAKIKADA BIR bunu calistirir; her cagri DURUMSUZ tek gecis yapar ve cikar:
  - gunun ilk gecisinde arsivi gunceller (guncelle.py; marker ile gunde 1 kez),
  - vadesi gelen (post-5dk) kosulari isler -> rapor + defter + paper (mevcut isle_kosu),
  - islenen/gecen kosulari veri/takip_gecis.txt'e isler (kalici durum; bellek yok),
  - tum kosular bitince + son post+40dk gecince defter.sonucla (gunde 1 kez, marker).
Surec olumu kavrami kalmadi: cagri coker/uyku girerse SONRAKI cagri kaldigi yerden surer.
Kalp atisi (veri/takip_son.txt) HER geciste tazelenir -> bekci "nabiz var mi" diye bakar.

Kullanim:
    python takip.py                      # tek gecis (gorev de ayni komutu calistirir)
    python takip.py --pist ANKARA        # sadece bu pist
    python takip.py --dk 6               # kosuya kac dk kala islensin
"""
import argparse
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from gunluk import hesapla, kosu_rapor, yerli_pistler, getjson, BASE, EXCL  # noqa: E402
from duzlestir import irk_of  # noqa: E402
import defter  # noqa: E402

RAPOR = KOK / "raporlar" / "gunluk"
GECIS = KOK / "veri" / "takip_gecis.txt"    # kalici gecis-durumu (append-only marker)
HB = KOK / "veri" / "takip_son.txt"         # kalp atisi (her gecis tazeler; bekci okur)
LOG = KOK / "veri" / "takip_log.txt"        # gecis ozetleri + hatalar (pythonw sessiz kosar)
_KILIT = None


def _log(msg):
    satir = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(satir)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(satir + "\n")
    except OSError:
        pass


def _durum_oku(tarih):
    """Bugunun marker seti: {'GUNCELLE', 'YOK', 'SONUCLA', 'ANKARA 3 bitti', ...}"""
    if not GECIS.exists():
        return set()
    out = set()
    for ln in GECIS.read_text(encoding="utf-8").splitlines():
        p = ln.split("\t", 1)
        if len(p) == 2 and p[0] == tarih:
            out.add(p[1])
    return out


def _isaretle(tarih, anahtar):
    with open(GECIS, "a", encoding="utf-8") as f:
        f.write(f"{tarih}\t{anahtar}\n")


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


def guncelle_bir_kez(tarih, done):
    """Gunun ilk gecisinde arsivi guncelle (marker'li; basarisizsa sonraki geciste yeniden,
    3 denemede vazgec -> gun bayat arsivle surer, hesapla zaten uyarir)."""
    if "GUNCELLE" in done:
        return
    deneme = sum(1 for d in done if d == "GUNCELLE-DENEME")
    if deneme >= 3:
        return
    _log("guncelle basliyor (gunun ilk gecisi)...")
    try:
        r = subprocess.run([sys.executable, str(KOK / "kod" / "guncelle.py")],
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                           timeout=1200)
        if r.returncode == 0:
            _isaretle(tarih, "GUNCELLE")
            _log("guncelle tamam.")
            return
    except (subprocess.TimeoutExpired, OSError) as e:
        _log(f"guncelle hata: {type(e).__name__}")
    _isaretle(tarih, "GUNCELLE-DENEME")
    _log(f"guncelle basarisiz (deneme {deneme + 1}/3) -> sonraki geciste yeniden.")


def gecis(args):
    """TEK durumsuz gecis: vadesi gelenleri isle, durumu dosyaya yaz, cik."""
    tarih = args.tarih
    ymd = datetime.strptime(tarih, "%Y-%m-%d").strftime("%Y%m%d")
    now = datetime.now()
    done = _durum_oku(tarih)

    guncelle_bir_kez(tarih, done)
    done = _durum_oku(tarih)

    if "YOK" in done:
        return                                        # bugun izinli kosu yok (kararli)
    pistler = [args.pist.strip().upper()] if args.pist else [p for p, _ in yerli_pistler(ymd)]
    atilan = [p for p in pistler if p in EXCL]        # K4: supheli pistler takip DISI
    pistler = [p for p in pistler if p not in EXCL]
    if atilan:
        print(f"K4: {', '.join(atilan)} (sike supheli) -> takip DISI.")
    sched = []
    for p in pistler:
        sched += program_kosulari(p, ymd, tarih)
    sched.sort(key=lambda r: r["post"])
    if not sched:
        _isaretle(tarih, "YOK")
        _log(f"{tarih}: izinli Ingiliz/Arap kosusu yok -> gun kapandi.")
        return

    RAPOR.mkdir(parents=True, exist_ok=True)
    dosya = RAPOR / f"{tarih}_{'_'.join(pistler)}.txt"
    islenen = 0
    for r in sched:
        key = f"{r['pist']} {r['no']}"
        if any(d.startswith(key + " ") for d in done):
            continue                                  # onceki geciste sonuclanmis
        if now > r["post"] + pd.Timedelta(minutes=3):
            # K36: yaris-sonrasi "tahmin" kaydi yok — gecmis olarak muhurle
            _isaretle(tarih, f"{key} gecmis")
            _log(f"{key} (yaris {r['saat']}): posta gecti -> islenmedi (defter korumasi)")
        elif now >= r["post"] - pd.Timedelta(minutes=args.dk):
            ok = isle_kosu(r["pist"], ymd, tarih, r["no"], r["saat"], dosya)
            if ok:
                _isaretle(tarih, f"{key} bitti")
                islenen += 1
            elif datetime.now() > r["post"]:
                _isaretle(tarih, f"{key} atlandi")
            # aksi halde MARKER YOK -> sonraki gecis yeniden dener (K39: gecici hata kosuyu yakmasin)

    # K53: ALTILI canli kupon — her Altili ilk kosusuna ~30dk kala kur (ayri dosya/sayfa;
    # try-korumali: Altili hatasi takibi ASLA bozmaz, paper hook'u gibi).
    try:
        import altili_canli
        nk = altili_canli.kupon_zamani_kur(pistler, ymd, tarih)
        if nk:
            _log(f"altili: {nk} kupon kuruldu (raporlar/altili.html)")
    except Exception as e:
        _log(f"altili kupon hatasi: {type(e).__name__}: {e}")

    done = _durum_oku(tarih)
    bekleyen = [r for r in sched
                if not any(d.startswith(f"{r['pist']} {r['no']} ") for d in done)]
    son_post = max(r["post"] for r in sched)
    if not bekleyen and "SONUCLA" not in done and datetime.now() > son_post + pd.Timedelta(minutes=40):
        _log("gun bitti -> sonucla...")
        try:
            defter.sonucla()
            try:
                import altili_canli          # K53: Altili ayak sonuclari + isabet (ayri; hata izole)
                altili_canli.sonucla_altili()
            except Exception as e:
                _log(f"altili sonucla hata: {type(e).__name__}: {e}")
            _isaretle(tarih, "SONUCLA")
        except Exception as e:
            _log(f"sonucla hata: {type(e).__name__}: {e}")   # marker yok -> sonraki gecis dener
    ozet = (f"gecis bitti: islenen {islenen}, bekleyen {len(bekleyen)}"
            + (f", sonraki ~{min(r['post'] for r in bekleyen) - pd.Timedelta(minutes=args.dk):%H:%M}"
               if bekleyen else ", gun tamam"))
    _log(ozet)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pist", default=None, help="tek pist (bos -> gunun tum yerli pistleri)")
    ap.add_argument("--tarih", default=date.today().isoformat())
    ap.add_argument("--dk", type=int, default=5, help="kosuya kac dk kala islensin")
    ap.add_argument("--once", action="store_true", help="(uyumluluk; artik her cagri tek gecis)")
    ap.add_argument("--bekle", type=int, default=0, help="(uyumluluk; kullanilmiyor)")
    args = ap.parse_args()

    # K47/K49 kalp atisi: kilit kontrolunden ONCE yazilir — nabiz "gecis denemesi yapildi"
    # demektir; kilidi baska kopya tutuyorsa da sistem canlidir (18 Tem: eski surec gunu
    # bitirirken gecisler kilide takildi, nabiz yazilmadi, bekci yanlis alarm verdi).
    HB.write_text(datetime.now().strftime("%Y-%m-%d %H:%M"), encoding="utf-8")
    if not tek_instans():
        _log("gecis: kilit baskasinda (elle gecis/eski surec calisiyor) -> cikiyorum.")
        return
    try:
        gecis(args)
    except Exception:
        import traceback
        _log("GECIS COKTU:\n" + traceback.format_exc())   # pythonw sessiz -> log'a yaz
        raise


if __name__ == "__main__":
    main()
