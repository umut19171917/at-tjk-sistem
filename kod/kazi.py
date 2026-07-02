"""
kazi.py — TJK ham veri kaziyicisi (YEREL, token=0).
ebayi.tjk.org statik JSON'larini indirir: her gun, her YERLI (Turkiye) pisti icin program + sonuc.
Ham JSON'lar veri/ham/ altina AYNEN kaydedilir (parse YOK; o is duzlestir.py'de).

YERLI PIST TESPITI (KEY tahmin etmeden, kisaltmaya dayanikli):
  Index'te yerli fiziksel pistlerde GUN dolu + SIRA dusuk; yabanci + KARMA'da GUN=null, SIRA="99".
  -> yerli = (GUN dolu) ve (KEY != KARMA) ve (SIRA != "99").  Boylece DBAKIR vb. otomatik yakalanir.

Tasarim: sadece stdlib; resumable (var olani atlar); nazik (--bekle); loglu.

Calistirma:
    python kazi.py --test            # son 10 gun (ONCE bunu calistir)
    python kazi.py                   # 2021-01-01 -> bugun, tum Turkiye
    python kazi.py --baslangic 2023-01-01 --bekle 0.7
"""
import argparse
import json
import time
import urllib.request
import urllib.error
from datetime import date, datetime, timedelta
from pathlib import Path

BASE = "https://ebayi.tjk.org/s/d"
KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "veri" / "ham"
LOG = HAM / "kazi_log.txt"
ATLA = {"KARMA"}
HEADERS = {"User-Agent": "Mozilla/5.0 (kazi.py veri arsivleme; kisisel arastirma)"}


def logla(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}\n")


def getir(url, timeout=20, deneme=3):
    """(status, bytes). 404 -> (404,None). Kalici hata -> (kod,None). Gecici -> 3 deneme."""
    for i in range(deneme):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return (r.status, r.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return (404, None)
            if e.code < 500 and e.code != 429:
                logla(f"HTTP {e.code} {url}")
                return (e.code, None)
            time.sleep(1.5 * (i + 1))
        except Exception as e:
            time.sleep(1.5 * (i + 1))
            if i == deneme - 1:
                logla(f"HATA {type(e).__name__} {url}")
    return (None, None)


def index_venues(obj):
    """Index JSON -> pist dict listesi (yapiya dayanikli)."""
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        for v in obj.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v
    return []


def yerli(v):
    """Yerli fiziksel TR pisti mi? GUN dolu + KEY!=KARMA + SIRA!=99."""
    key = str(v.get("KEY", "")).strip().upper()
    if key in ATLA or not key:
        return False
    gun = v.get("GUN")
    if gun is None or str(gun).strip() in ("", "0", "null", "None"):
        return False
    if str(v.get("SIRA", "")).strip() == "99":
        return False
    return True


def gecerli_json(b):
    if not b or len(b) < 30:
        return False
    try:
        json.loads(b.decode("utf-8", "replace"))
        return True
    except Exception:
        return False


def indir_full(tur, ymd, key, bekle, sayac, force=False):
    hedef = HAM / tur / f"{ymd}_{key}.json"
    if not force and hedef.exists() and hedef.stat().st_size > 50:
        sayac["atla"] += 1
        return
    st, data = getir(f"{BASE}/{tur}/{ymd}/full/{key}.json")
    time.sleep(bekle)
    if st == 404:
        sayac["yok"] += 1
        return
    if data and gecerli_json(data):
        hedef.parent.mkdir(parents=True, exist_ok=True)
        hedef.write_bytes(data)
        sayac["indir"] += 1
    else:
        sayac["hata"] += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baslangic", default="2021-01-01")
    ap.add_argument("--bitis", default=date.today().isoformat())
    ap.add_argument("--bekle", type=float, default=0.5, help="istekler arasi saniye")
    ap.add_argument("--test", action="store_true", help="sadece son 10 gun")
    ap.add_argument("--guncelle", action="store_true",
                    help="arsivdeki son gunden bugune guncelle (K36; sinir gunu YENIDEN indirilir "
                         "cunku gun-ici kismi inmis olabilir)")
    args = ap.parse_args()

    bas = datetime.strptime(args.baslangic, "%Y-%m-%d").date()
    bit = datetime.strptime(args.bitis, "%Y-%m-%d").date()
    if args.test:
        bas, bit = date.today() - timedelta(days=10), date.today()
    force_ymd = None
    if args.guncelle:
        mevcut = sorted(p.stem.split("_")[0] for p in (HAM / "sonuclar").glob("*.json"))
        if mevcut:
            force_ymd = mevcut[-1]
            bas = datetime.strptime(force_ymd, "%Y%m%d").date()
        bit = date.today()
        print(f"guncelleme kipi: {bas} .. {bit} (ilk gun yeniden indirilir)")

    HAM.mkdir(parents=True, exist_ok=True)
    sayac = {"indir": 0, "atla": 0, "yok": 0, "hata": 0}
    yerli_keys = {}      # KEY -> AD (gorulen yerli pistler)
    yabanci_say = 0
    yaris_gun = 0
    t0 = time.time()
    toplam = (bit - bas).days + 1
    islenen = 0

    g = bas
    while g <= bit:
        ymd = g.strftime("%Y%m%d")
        st, data = getir(f"{BASE}/sonuclar/{ymd}/yarislar.json")
        time.sleep(args.bekle)
        if st != 404 and data and gecerli_json(data):
            venues = index_venues(json.loads(data.decode("utf-8", "replace")))
            yerliler = [v for v in venues if yerli(v)]
            yabanci_say += len(venues) - len(yerliler)
            if yerliler:
                yaris_gun += 1
                (HAM / "_index").mkdir(exist_ok=True)
                (HAM / "_index" / f"{ymd}_sonuclar.json").write_bytes(data)
                for v in yerliler:
                    key = str(v["KEY"]).strip().upper()
                    yerli_keys.setdefault(key, v.get("AD", ""))
                    frc = (ymd == force_ymd)
                    indir_full("sonuclar", ymd, key, args.bekle, sayac, force=frc)
                    indir_full("program", ymd, key, args.bekle, sayac, force=frc)

        islenen += 1
        if islenen % 60 == 0:
            print(f"  {ymd}  ({islenen}/{toplam} gun, {(time.time()-t0)/60:.1f}dk)  "
                  f"indir={sayac['indir']} atla={sayac['atla']} yarisGun={yaris_gun}", flush=True)
        g += timedelta(days=1)

    pist_satir = "\n".join(f"   {k:12s} {ad}" for k, ad in sorted(yerli_keys.items()))
    ozet = (
        "=" * 56 + "\n"
        f"KAZIMA BITTI  {bas} .. {bit}\n"
        f"yaris gunu (yerli): {yaris_gun}\n"
        f"indirilen dosya: {sayac['indir']}\n"
        f"atlanan (zaten var): {sayac['atla']}\n"
        f"pist/gun yok (404): {sayac['yok']}\n"
        f"hata: {sayac['hata']}  (detay: veri/ham/kazi_log.txt)\n"
        f"atlanan yabanci pist-gun: {yabanci_say}\n"
        f"gorulen YERLI pistler ({len(yerli_keys)}):\n{pist_satir}\n"
        f"sure: {(time.time()-t0)/60:.1f} dk\n"
        + "=" * 56
    )
    print(ozet)
    (HAM / "kazi_ozet.txt").write_text(ozet, encoding="utf-8")


if __name__ == "__main__":
    main()
