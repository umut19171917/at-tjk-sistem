"""BAHISLER_TR / parasal netice formatini incele (egzotik parser tasarimi icin)."""
import json
from pathlib import Path

HAM = Path(__file__).resolve().parent.parent / "veri" / "ham" / "sonuclar"
f = sorted(HAM.glob("2025*ISTANBUL*.json"))[:1] or sorted(HAM.glob("2025*.json"))[:1]
o = json.loads(f[0].read_text(encoding="utf-8"))
print("dosya:", f[0].name)
for k in o.get("kosular", [])[:5]:
    print("=" * 70)
    print("kosu NO:", k.get("NO"), "KOD:", k.get("KOD"))
    print("BAHISLER_TR:", repr(k.get("BAHISLER_TR")))
    # ilk 3 atin NO/SONUC (bitis sirasi dogrulamak icin)
    atl = sorted(k.get("atlar", []), key=lambda a: int(a.get("SONUC") or 99))[:4]
    print("ilk 4:", [(a.get("NO"), "s=" + str(a.get("SONUC"))) for a in atl])
