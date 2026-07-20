"""
devir_ayikla.py — CARRYOVER (devir) olaylarini cikarir (K51, arastirma amacli — sistemin
tahmin/paper hattina baglanti YOK). BAHISLER_TR'de kazanan cikmayan cok-ayakli havuzlar:
  "<TUR>(<kombo>): Bilen cikmamistir, <TUTAR> TL devretmistir."
Tum turleri yakalar (6'LI GANYAN=Altili oncelikli ilgi; SIRALI 5 Lİ BAHIS, TABELA BAHIS vb. de
cikar — ayni maliyetle). Elimizdeki resolved-Altili (altili.csv, egzotik6_ayikla.py) ile
BIRLIKTE tam Altili evrenini verir: resolved + devreden.
Cikti: veri/devir.csv  (tarih, sehir, tur, seq, kombo, devir_tl)
YEREL, TOKEN=0 (ham JSON zaten indirilmis; ag/LLM cagrisi yok). Kazima bitince: python kod/devir_ayikla.py
"""
import json
import re
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "veri" / "ham" / "sonuclar"
# Turkce karakterlerin bozuk gelebildigi (mojibake) dosyalar da yakalansin diye tur adi gevsek:
# harf+rakam+bosluk+kesme, parantez-ici kombo, "Bilen ...mistir/mamistir, TUTAR TL dev...tir."
PAT = re.compile(
    r"(?:(\d+)\.\s*)?([A-ZÇĞİÖŞÜ0-9'’\s]{3,30}?)\(([\d/,]+)\):\s*Bilen\s*\S*\s*,\s*"
    r"([\d.,]+)\s*TL\s*dev\S*\.",
    re.IGNORECASE,
)


def vfloat(s):
    s = s.strip()
    s = s.replace(".", "").replace(",", ".") if ("," in s and "." in s) else s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def main():
    rows = []
    nfile = 0
    for f in sorted(HAM.glob("*.json")):
        try:
            o = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        nfile += 1
        sehir = f.stem.split("_")[-1]
        for k in o.get("kosular", []):
            s = k.get("BAHISLER_TR") or ""
            if "dev" not in s.lower():
                continue
            for seq, tur, combo, tutar in PAT.findall(s):
                # K51 DUZELTME: ad grubu rakam+harf+bosluk kabul ettigi icin bir ONCEKI
                # tutarin virgul-sonrasi kuyrugu ("60TL","90TL"...) sizabiliyordu (virgul
                # yasak oldugundan en erken eslesme tam sizinti noktasinda basliyordu).
                # Sizinti HER ZAMAN '<rakamlar>TL ' + gercek ad seklinde -> temizle.
                tur = re.sub(r"^\d+TL\s*", "", tur.strip())
                rows.append({
                    "tarih": k.get("TARIH"), "sehir": sehir,
                    "tur": tur, "seq": int(seq) if seq else 1,
                    "kombo": combo, "devir_tl": vfloat(tutar),
                })

    df = pd.DataFrame(rows).drop_duplicates(["tarih", "sehir", "tur", "seq", "kombo"])
    df.to_csv(KOK / "veri" / "devir.csv", index=False, encoding="utf-8")

    print(f"dosya: {nfile} | devir olayi (tum turler): {len(df)}")
    print("\ntur bazinda:")
    print(df.groupby("tur").agg(n=("devir_tl", "size"), medyan_tl=("devir_tl", "median"),
                                 max_tl=("devir_tl", "max")).sort_values("n", ascending=False).to_string())

    # TAM esleseme (K51 duzeltmesi sonrasi da temkinli): "6'LI GANYAN" ile baslamali,
    # sadece "6" icermek yetmez (7'Lİ/5'Lİ GANYAN'daki kirli kalintilarla karisirdi).
    alt = df[df["tur"].str.upper().str.startswith("6'LI GANYAN")
             | df["tur"].str.upper().str.startswith("6'Lİ GANYAN")]
    print(f"\n--- ALTILI (6'LI GANYAN) devir olaylari: {len(alt)} ---")
    if len(alt):
        alt = alt.copy()
        alt["yil"] = pd.to_datetime(alt["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
        print("yil bazinda:")
        print(alt.groupby("yil").agg(n=("devir_tl", "size"), medyan_tl=("devir_tl", "median"),
                                      max_tl=("devir_tl", "max")).to_string())
        # resolved Altili (egzotik6_ayikla.py ciktisi) varsa -> devir sikligi = devir / (devir+resolved)
        altf = KOK / "veri" / "altili.csv"
        if altf.exists():
            res = pd.read_csv(altf)
            toplam = len(res) + len(alt)
            print(f"\nresolved (kazanan cikti): {len(res)}  |  devreden: {len(alt)}  |  "
                  f"toplam cekilis: {toplam}  |  devir sikligi: %{100*len(alt)/toplam:.1f}")
        print("\nen buyuk 5 devir:")
        print(alt.nlargest(5, "devir_tl")[["tarih", "sehir", "devir_tl"]].to_string(index=False))
        # K4: proje 4 supheli pisti (sike soylentisi) egitim/tahminden disliyor -> devir'in
        # bu pistlerde ne kadar yogunlastigi ayri raporlanir (izinli-kapsam icin asil sayi).
        EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
        supheli = alt[alt["sehir"].isin(EXCL)]
        temiz = alt[~alt["sehir"].isin(EXCL)]
        print(f"\npist kirilimi: K4-supheli pistte {len(supheli)}/{len(alt)} (%"
              f"{100*len(supheli)/len(alt):.0f}) | izinli (proje kapsami) pistte {len(temiz)}")
        print("izinli-pist devir olaylari:")
        print(temiz[["tarih", "sehir", "devir_tl"]].to_string(index=False))
    print(f"\nyazildi: devir.csv")


if __name__ == "__main__":
    main()
