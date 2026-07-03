"""
temettu.py — sonuc JSON'u BAHISLER_TR metninden GANYAN + PLASE temettuleri (K42 ortak parser).
Ornek metin: 'GANYAN(4): 3,60TL ... PLASE(13): 9,90TL PLASE(4): 2,30TL PLASE IKILI(4/10): 3,40TL'
  - PLASE her plase alan at icin AYRI yazilir -> {at_no: temettu} sozlugu doner
    (egzotik_ayikla.parse_bahis 'ilk goruleni' alir; plase icin o YETMEZ, bu yuzden ayri fonksiyon).
  - 'PLASE IKILI' plase DEGIL -> isim folding ile dislanir.
Temettuler TJK'da 1 TL birim bahis basina TL odemedir.
"""
import re

PAT = re.compile(r"([^()]*?)\(([\d/]+)\):\s*([\d.,]+)\s*TL")


def _fold(s):
    return (s.upper().replace("İ", "I").replace("Ş", "S").replace("Ü", "U")
            .replace("Ç", "C").replace("Ö", "O").replace("Ğ", "G"))


def _vfloat(s):
    s = s.strip()
    s = s.replace(".", "").replace(",", ".") if ("," in s and "." in s) else s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def gan_plase(bahisler_tr):
    """-> (ganyan_temettu | None, {at_no: plase_temettu}). at_no int."""
    gan, plase = None, {}
    if not isinstance(bahisler_tr, str):
        return gan, plase
    for name, combo, val in PAT.findall(bahisler_tr):
        n = _fold(name)
        v = _vfloat(val)
        if v is None or "/" in combo:
            continue                      # kombinasyon bahisleri (ikili vb.) burada isimizi gormez
        try:
            no = int(combo)
        except ValueError:
            continue
        if "PLASE" in n and "IKILI" not in n:
            plase[no] = v
        elif "GANYAN" in n and gan is None:
            gan = v
    return gan, plase
