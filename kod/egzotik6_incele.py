"""Altili (6'li Ganyan) temettusu ve ayak yapisini ham JSON'da BUL (varsayim yok)."""
import json
import re
from pathlib import Path

HAM = Path(__file__).resolve().parent.parent / "veri" / "ham" / "sonuclar"


def fold(s):
    return (s.upper().replace("İ", "I").replace("Ş", "S").replace("Ü", "U")
            .replace("Ç", "C").replace("Ö", "O").replace("Ğ", "G"))


def walk(o, path=""):
    """6'li / altili gecen string degerleri yol ile dondur."""
    hits = []
    if isinstance(o, dict):
        for k, v in o.items():
            hits += walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o[:3]):     # liste basindan ornek
            hits += walk(v, f"{path}[{i}]")
    elif isinstance(o, str):
        f = fold(o)
        if any(t in f for t in ["6'LI", "6 LI", "6LI GANYAN", "ALTILI", "PICK 6", "PICK6"]):
            hits.append((path, o[:160]))
    return hits


# Altili olan buyuk bir gun: Istanbul (hafta sonu)
files = sorted(HAM.glob("2025*ISTANBUL*.json"))
for f in files[:4]:
    o = json.loads(f.read_text(encoding="utf-8"))
    h = walk(o)
    print("=" * 70)
    print(f.name, "| top-level keys:", list(o.keys()))
    kos = o.get("kosular", [])
    print(f"kosu sayisi: {len(kos)}")
    # son kosunun BAHISLER ve parasal netice (Altili genelde son ayakta duyurulur)
    if kos:
        son = kos[-1]
        print("SON kosu BAHISLER_TR:", repr(son.get("BAHISLER_TR"))[:300])
        print("SON kosu emiParasalNeticeler_tr:", repr(son.get("emiParasalNeticeler_tr"))[:300])
    print(f"--- '6'li/altili' gecen alanlar ({len(h)}): ---")
    for p, v in h[:15]:
        print(f"  {p}: {v}")
