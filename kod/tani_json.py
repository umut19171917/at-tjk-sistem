"""Ham full JSON'un yapi-iskeletini basar (parser tasarimi icin)."""
import json
from pathlib import Path

HAM = Path(__file__).resolve().parent.parent / "veri" / "ham"


def skel(o, d=0, maxd=4):
    ind = "  " * d
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)) and d < maxd:
                print(f"{ind}{k}: {type(v).__name__}"
                      + (f"(len={len(v)})" if isinstance(v, list) else ""))
                skel(v, d + 1, maxd)
            else:
                s = str(v).replace("\n", " ")[:45]
                print(f"{ind}{k} = {s!r}")
    elif isinstance(o, list):
        print(f"{ind}[liste len={len(o)}] -> ilk eleman:")
        if o and d < maxd:
            skel(o[0], d + 1, maxd)


for tur in ("sonuclar", "program"):
    files = sorted((HAM / tur).glob("2026*.json"))  # test (2026) dosyalari
    if not files:
        print(f"{tur}: dosya yok")
        continue
    f = files[-1]
    print("=" * 64)
    print(f"{tur}: {f.name}  ({f.stat().st_size//1024} KB)")
    print("=" * 64)
    o = json.loads(f.read_text(encoding="utf-8"))
    skel(o)
    print()
