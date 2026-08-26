# -*- coding: utf-8 -*-
"""
bahis_tara.py — TJK'NIN OYNATTIĞI TÜM BAHİSLER: HANGİSİNİN TEMETTÜSÜ ARŞİVDE VAR? (K123)
Salt-okunur ENVANTER taraması. Hiçbir dosyaya yazmaz, hiçbir şey ölçmez, karar üretmez.

NEDEN: Altılı dışı kollar tek tek kapandı (K42 ganyan/plase, K21-K25 exacta, K94 kesintiler,
K108 4'lü/5'li, K117 7'li) ama TJK'nın oynattığı bahislerin TAMAMINA hiç bakılmadı.
Kullanıcı sordu: "5'li ve 4'lü ganyanın testini yaptık ama kalan tüm bahislere bakmadık."

Bu betik yalnızca ŞU soruyu cevaplar: hangi bahsin temettüsü ham arşivde YAYIMLANIYOR?
Veri yoksa o kol kesin kapanır. Varsa, ölçüt önceden bağlanarak ayrı bir kol açılabilir.
(K108'in dersi: "veri yok" notu bayat olabilir -- nli_ganyan.csv meğer elimizdeymiş.)

KAYNAK: veri/ham/sonuclar/*.json -> kosular[].emiParasalNeticeler_tr
Format duz metin, ornek:
  GANYAN(3): 30,60TL  IKILI(2/3): 313,00TL  SIRALI IKILI(3/2): 422,45TL
  UCLU BAHIS(7/6/9): 1.122,10TL  PLASE(6): 3,00TL  1. CIFTE(3/7): 548,55TL
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
SONUC = KOK / "veri" / "ham" / "sonuclar"

# "AD(kombo): 1.234,56TL"  -- ad basinda "1. " gibi sira no'su olabilir
DESEN = re.compile(r"([^()]+?)\(([^)]*)\):\s*([\d.,]+)\s*TL", re.UNICODE)


def ad_normalle(ad):
    """'1. ÇİFTE' -> 'ÇİFTE' · bastaki sira no'sunu ve bosluklari at."""
    a = re.sub(r"^\s*\d+\.\s*", "", ad).strip()
    return " ".join(a.split())


def tl(s):
    """'1.122,10' -> 1122.10 (TR: nokta binlik, virgul ondalik)."""
    try:
        return float(s.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def main():
    if not SONUC.exists():
        print(f"HATA: {SONUC} yok.")
        return
    dosyalar = sorted(SONUC.glob("*.json"))
    print("=" * 100)
    print("K123 — BAHİS TÜRÜ ENVANTERİ (ham arşiv taraması, SALT-OKUNUR)")
    print(f"  taranan dosya: {len(dosyalar):,}")
    print("=" * 100)

    say = defaultdict(int)              # bahis adi -> kac olay
    tutar = defaultdict(list)           # bahis adi -> temettuler
    yil = defaultdict(set)              # bahis adi -> hangi yillar
    ornek = {}                          # bahis adi -> ornek satir
    kombo_uz = defaultdict(set)         # bahis adi -> kombo parca sayilari
    bozuk = 0

    for i, f in enumerate(dosyalar):
        if i % 500 == 0:
            print(f"  ... {i:,}/{len(dosyalar):,}", flush=True)
        try:
            o = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:                                        # noqa: BLE001
            bozuk += 1
            continue
        y = f.name[:4]
        for k in (o.get("kosular") or []):
            metin = k.get("emiParasalNeticeler_tr") or ""
            if not isinstance(metin, str) or not metin.strip():
                continue
            for ad, kombo, para in DESEN.findall(metin):
                a = ad_normalle(ad)
                if not a:
                    continue
                say[a] += 1
                yil[a].add(y)
                v = tl(para)
                if v is not None:
                    tutar[a].append(v)
                n = len([x for x in re.split(r"[/,]", kombo) if x.strip()])
                kombo_uz[a].add(n)
                if a not in ornek:
                    ornek[a] = f"{ad.strip()}({kombo}): {para}TL"

    print(f"\n  bozuk/okunamayan dosya: {bozuk}")
    print("\n" + "=" * 100)
    print("BULUNAN BAHİS TÜRLERİ (olay sayısına göre)")
    print("=" * 100)
    print(f"  {'bahis':>22} {'olay':>9} {'yıl':>6} {'kombo':>8} {'medyan TL':>12} "
          f"{'%90 TL':>12}  örnek")
    import statistics as st
    for a, n in sorted(say.items(), key=lambda x: -x[1]):
        v = sorted(tutar[a])
        med = st.median(v) if v else float("nan")
        p90 = v[int(0.9 * len(v))] if v else float("nan")
        ku = ",".join(str(x) for x in sorted(kombo_uz[a])[:4])
        print(f"  {a[:22]:>22} {n:>9,} {len(yil[a]):>6} {ku:>8} {med:>12,.2f} "
              f"{p90:>12,.2f}  {ornek[a][:44]}")

    print("\n" + "=" * 100)
    print("OKUMA")
    print("=" * 100)
    print("  'kombo' = temettü satırındaki seçim sayısı (2 = iki at, 3 = üç at ...).")
    print("  Bir bahsin burada GÖRÜNMESİ, o kol için backtest kurulabilir demektir:")
    print("  temettü + kazanan kombinasyon ikisi de kayıtlı.")
    print("  GÖRÜNMEYEN bir bahis TJK tarafından yayımlanmıyordur -> o kol KESİN KAPALI.")


if __name__ == "__main__":
    main()
