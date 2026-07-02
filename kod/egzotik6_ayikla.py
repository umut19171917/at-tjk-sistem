"""
egzotik6_ayikla.py — Altili (6'li Ganyan) olaylarini cikar.
Son ayak BAHISLER_TR'sinde: "6'LI GANYAN(l1/l2/.../l6): TEMETTU" (9 kosuluk gun: "2. 6'LI ...").
6 ayagi, kombinasyondaki kazananlari ardisik koSularin GERCEK kazananlariyla esleyerek bulur.
Cikti: veri/altili.csv  (event: gun, sehir, seq, temettu, 6 ayagin race_kod'u)
"""
import json
import re
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "veri" / "ham" / "sonuclar"
PAT = re.compile(r"(?:(\d+)\.\s*)?6'LI GANYAN\(([^)]+)\):\s*([\d.,]+)\s*TL")


def vfloat(s):
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


def main():
    rows = []
    nfile = es = bul = kayip = 0
    for f in sorted(HAM.glob("*.json")):
        try:
            o = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        nfile += 1
        kos = o.get("kosular", [])
        if len(kos) < 6:
            continue
        sehir = f.stem.split("_")[-1]          # KEY top-level'da yok; dosya adindan
        winners = [race_winners(k) for k in kos]
        kods = [k.get("KOD") for k in kos]
        last = kos[-1].get("BAHISLER_TR") or ""
        for seq, combo, val in PAT.findall(last):
            es += 1
            legs = [set(int(x) for x in part.split(",")) for part in combo.split("/")]
            if len(legs) != 6:
                continue
            # 6 ardisik kosu penceresi: her ayakta kombinasyon-set ile gercek-kazanan kesisiyor mu
            found = None
            for off in range(0, len(kos) - 5):
                ok = all(winners[off + i] & legs[i] for i in range(6))
                if ok:
                    found = off
                    break
            if found is None:
                kayip += 1
                continue
            bul += 1
            rows.append({
                "gun": kos[-1].get("TARIH"), "sehir": sehir,
                "seq": int(seq) if seq else 1, "temettu": vfloat(val),
                **{f"leg{i+1}": kods[found + i] for i in range(6)},
            })

    df = pd.DataFrame(rows).drop_duplicates(["gun", "sehir", "seq"])
    df.to_csv(KOK / "veri" / "altili.csv", index=False, encoding="utf-8")
    print(f"dosya: {nfile} | bulunan 6'li ifadesi: {es} | ayak eslesen: {bul} | eslesemeyen: {kayip}")
    print(f"benzersiz Altili olayi: {len(df)}")
    print(f"temettu medyan: {df.temettu.median():.0f} | min: {df.temettu.min():.0f} | "
          f"max: {df.temettu.max():.0f}")
    print("yil bazinda olay:")
    df["yil"] = pd.to_datetime(df.gun, format="%d/%m/%Y", errors="coerce").dt.year
    print(df.groupby("yil").size().to_string())
    print("ornek:")
    print(df.head(3).to_string())


if __name__ == "__main__":
    main()
