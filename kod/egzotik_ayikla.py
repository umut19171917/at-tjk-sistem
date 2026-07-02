"""
egzotik_ayikla.py — ham sonuc JSON'larindan egzotik temettuleri cikarir.
BAHISLER_TR ornegi: 'GANYAN(9): 6,75TL İKİLİ(9/10): 23,80TL SIRALI İKİLİ(9/10): 53,50TL
                     ÜÇLÜ BAHİS(9/11/2): 79,90TL ...'
Cikti: veri/egzotik.csv  (race_kod basina: ganyan/ikili/exacta/trifecta combo + temettu)
TOKEN=0, yerel.
"""
import json
import re
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "veri" / "ham" / "sonuclar"
PAT = re.compile(r"([^()]*?)\(([\d/]+)\):\s*([\d.,]+)\s*TL")


def fold(s):
    return (s.upper().replace("İ", "I").replace("Ş", "S").replace("Ü", "U")
            .replace("Ç", "C").replace("Ö", "O").replace("Ğ", "G"))


def vfloat(s):
    s = s.strip()
    s = s.replace(".", "").replace(",", ".") if ("," in s and "." in s) else s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def siniflandir(name):
    n = fold(name)
    if "TABELA" in n:
        return "tabela"
    if "5 L" in n or ("SIRALI" in n and "5" in n):
        return "sirali5"
    if "UCLU" in n:
        return "trifecta"        # SIRALI UCLU / UCLU BAHIS = sirali uclu
    if "PLASE" in n and "IKILI" in n:
        return "plase_ikili"
    if "PLASE" in n:
        return "plase"
    if "SIRALI" in n and "IKILI" in n:
        return "exacta"          # sirali ikili
    if "IKILI" in n:
        return "quinella"        # ikili (sirasiz)
    if "CIFTE" in n:
        return "cifte"
    if "GANYAN" in n:
        return "ganyan"
    return None


def parse_bahis(s):
    out = {}
    if not isinstance(s, str):
        return out
    for name, combo, val in PAT.findall(s):
        tip = siniflandir(name)
        if tip and tip not in out:        # ilk gorulen (ana) -> cifte vb. tekrarlari atla
            out[tip] = (combo, vfloat(val))
    return out


def main():
    rows = []
    for f in sorted(HAM.glob("*.json")):
        try:
            o = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for k in o.get("kosular", []):
            b = parse_bahis(k.get("BAHISLER_TR"))
            r = {"race_kod": k.get("KOD")}
            for tip in ["ganyan", "quinella", "exacta", "trifecta"]:
                if tip in b:
                    r[tip + "_combo"] = b[tip][0]
                    r[tip + "_div"] = b[tip][1]
            rows.append(r)
    df = pd.DataFrame(rows).drop_duplicates("race_kod")
    df.to_csv(KOK / "veri" / "egzotik.csv", index=False, encoding="utf-8")

    print(f"kosu: {len(df)}")
    for tip in ["ganyan", "quinella", "exacta", "trifecta"]:
        c = df[tip + "_div"].notna().mean() * 100 if tip + "_div" in df else 0
        med = df[tip + "_div"].median() if tip + "_div" in df else float("nan")
        print(f"  {tip:9s} dolu %{c:5.1f}  medyan temettu: {med}")
    print("ornek:")
    print(df.head(3).to_string())


if __name__ == "__main__":
    main()
