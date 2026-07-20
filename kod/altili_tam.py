"""
altili_tam.py — Altili'nin TAM odeme merdiveni (K52): 6'LI/5'Lİ/4'LÜ/3'LÜ GANYAN, hem
normal odeme hem devir (carryover) hali, GUNDE 1 VEYA 2 PENCERE (K46 sonrasi kesif: 9 kosulu
gunde iki ORTUSEN pencere olabilir: 1-6. kosular ve 4-9. kosular).

METIN GERCEKLERI (ham veriden dogrulandi, tahmin degil):
  - Alt-kademe (5/4/3) metinleri her zaman kombo olarak ANA 6-ayak komboNUN SONDAN kesilmis
    alt-kumesidir (6'LI(a/b/c/d/e/f) -> 5'Lİ(b/c/d/e/f) -> 4'LÜ(c/d/e/f) -> 3'LÜ(d/e/f)).
    Bu yuzden pencere<->alt-kademe eslemesi METIN ONEKINE ("1."/"2.") DEGIL, KOMBO ALT-KUME
    ESLESMESINE dayanir -- onek tutarsiz (bazen 4'LÜ'de hic yok, gozlemlendi).
  - Cift-pencereli gunde 2. pencere HER ZAMAN tam merdiveni tasir (n=2610, %100); 1. pencere
    bazen sadece 6+5 (4/3 o gun o pencere icin hic YAYIMLANMAMIS -- urun kurali, veri hatasi
    degil). Tek-pencereli gunlerde odeme cikan gunlerde de merdiven tam.
  - Ayni olay BAZEN birden fazla kosunun BAHISLER_TR'sinde YANKILANIR (kumulatif metin) ->
    (tarih,sehir,kombo) ile dedup sart.

Pencere (6 ardisik kosu) tespiti: egzotik6_ayikla.py'nin offset-arama teknigi (komboyu
GERCEK kazananlarla esleyerek) aynen kullanilir -- kanitlanmis, degistirilmedi.

Cikti: veri/altili_tam.csv (tarih, sehir, seq, leg1..leg6=race_kod, kombo,
  t6_div, t6_devir, t5_div, t5_devir, t4_div, t4_devir, t3_div, t3_devir)
  NaN = o kademe o pencere icin YOK (urun kurali; "kaybetti" degil "mevcut degil").
YEREL, TOKEN=0.
"""
import json
import re
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "veri" / "ham" / "sonuclar"

TIER_ISIM = {6: "6'LI GANYAN", 5: "5'Lİ GANYAN", 4: "4'LÜ GANYAN", 3: "3'LÜ GANYAN"}
PAT = {n: re.compile(
    re.escape(isim) + r"\(([\d/,]+)\):\s*"
    r"(?:Bilen\s*\S*\s*,\s*([\d.,]+)\s*TL\s*dev\S*\.|([\d.,]+)\s*TL)"
) for n, isim in TIER_ISIM.items()}


def vfloat(s):
    s = s.strip()
    s = s.replace(".", "").replace(",", ".") if ("," in s and "." in s) else s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def race_winners(k):
    ws = set()
    for a in k.get("atlar", []):
        try:
            if int(a.get("SONUC")) == 1:
                ws.add(int(a.get("NO")))
        except (TypeError, ValueError):
            pass
    return ws


def pencere_bul(kombo, winners, kods):
    """egzotik6_ayikla.py ile AYNI teknik: komboyu gercek kazananlarla esleyerek 6-ardisik
    kosu ofsetini bulur. Bulunamazsa None."""
    legs = [set(int(x) for x in part.split(",")) for part in kombo.split("/")]
    if len(legs) != 6:
        return None
    for off in range(0, len(kods) - 5):
        if all(winners[off + i] & legs[i] for i in range(6)):
            return off
    return None


def main():
    olaylar = {}   # (tarih, sehir, kombo6) -> dict(t6..t3 div/devir)
    nfile = kayip = 0
    for f in sorted(HAM.glob("*.json")):
        try:
            o = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        nfile += 1
        sehir = f.stem.split("_")[-1]
        kos = o.get("kosular", [])
        if len(kos) < 3:
            continue
        tarih = kos[-1].get("TARIH")

        # gunun TUM kosularindaki BAHISLER_TR'yi tek metinde topla (yanki -> zaten dedup edilecek)
        tam_metin = " ".join(k.get("BAHISLER_TR") or "" for k in kos)

        bulunan = {n: [] for n in (6, 5, 4, 3)}   # n -> [(kombo, div, devir_tutar)]
        for n, pat in PAT.items():
            for kombo, devir_tutar, div in pat.findall(tam_metin):
                bulunan[n].append((kombo, vfloat(div) if div else None,
                                   vfloat(devir_tutar) if devir_tutar else None))
            # dedup: ayni kombo birden fazla yankida gorulebilir
            gorulen, tekil = set(), []
            for kombo, div, dv in bulunan[n]:
                if kombo in gorulen:
                    continue
                gorulen.add(kombo)
                tekil.append((kombo, div, dv))
            bulunan[n] = tekil

        # pencere (race_kod) tespiti -- bu dosyanin kendi kosu listesinde arar.
        # DIKKAT (K52 duzeltme): ayni pencere (ayni 6 race_kod) BAZEN iki FARKLI kombo
        # metniyle eslesiyor (~%1.4 gun-sehir; muhtemelen sonuc itirazi/duzeltmesi sonrasi
        # ham metinde iki surum kalmis -- ⚠ HIPOTEZ, kesinlesmedi). Bu yuzden anahtar KOMBO
        # METNI degil PENCERENIN KENDISI (leg1..leg6 race_kod); rakip surumler arasinda
        # once EN TAM merdiven (4/3 de dolu), sonra EN BUYUK t6_div secilir (deterministik).
        winners = [race_winners(k) for k in kos]
        kods = [k.get("KOD") for k in kos]
        for k6, d6, dv6 in bulunan[6]:
            off = pencere_bul(k6, winners, kods)
            if off is None:
                kayip += 1
                continue          # bu dosyada eslesen pencere yok -> atla (baska gunun yankisi olabilir)
            legs = tuple(kods[off + i] for i in range(6))
            key = (tarih, sehir) + legs
            legs6 = k6.split("/")
            aday = {"t6_div": d6, "t6_devir": dv6, "legs": list(legs)}
            for n in (5, 4, 3):
                alt_kombo = "/".join(legs6[6 - n:])
                eslesen = next(((div, dv) for kb, div, dv in bulunan[n] if kb == alt_kombo), None)
                aday[f"t{n}_div"], aday[f"t{n}_devir"] = eslesen if eslesen else (None, None)

            eski = olaylar.get(key)
            if eski is None:
                olaylar[key] = aday
            else:
                tamlik = lambda r: sum(r[f"t{n}_div"] is not None or r[f"t{n}_devir"] is not None
                                       for n in (5, 4, 3))
                if (tamlik(aday), aday["t6_div"] or 0) > (tamlik(eski), eski["t6_div"] or 0):
                    olaylar[key] = aday

    rows = []
    for key, rec in olaylar.items():
        tarih, sehir = key[0], key[1]
        rows.append({
            "tarih": tarih, "sehir": sehir,
            **{f"leg{i+1}": rec["legs"][i] for i in range(6)},
            "t6_div": rec["t6_div"], "t6_devir": rec["t6_devir"],
            "t5_div": rec["t5_div"], "t5_devir": rec["t5_devir"],
            "t4_div": rec["t4_div"], "t4_devir": rec["t4_devir"],
            "t3_div": rec["t3_div"], "t3_devir": rec["t3_devir"],
        })

    df = pd.DataFrame(rows).drop_duplicates(["tarih", "sehir", "leg1", "leg6"])
    df.to_csv(KOK / "veri" / "altili_tam.csv", index=False, encoding="utf-8")

    print(f"dosya: {nfile} | pencere bulunan olay: {len(df)} | eslesemeyen: {kayip}")
    for n in (6, 5, 4, 3):
        div_dolu = df[f"t{n}_div"].notna().mean() * 100
        devir_dolu = df[f"t{n}_devir"].notna().mean() * 100
        yok = 100 - div_dolu - devir_dolu
        print(f"  t{n}: odeme %{div_dolu:5.1f}  devir %{devir_dolu:5.1f}  "
              f"yayimlanmamis %{yok:5.1f}")
    print("\nyil bazinda olay sayisi:")
    df["yil"] = pd.to_datetime(df["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    print(df.groupby("yil").size().to_string())
    print(f"\nyazildi: altili_tam.csv")


if __name__ == "__main__":
    main()
