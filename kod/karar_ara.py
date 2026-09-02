# -*- coding: utf-8 -*-
"""
karar_ara.py — K148 / BEKLEYENLER 22-F: KARAR GÜNLÜĞÜ ARAMA ARACI. SALT-OKUNUR.

SORUN: KARARLAR.md 376 KB / 146 karar. "bot1'in kârına dair hangi kararlar var?" sorusu
elle grep'le dakikalar sürüyor ve bağlam kaybediliyor.

KULLANIM
  python kod/karar_ara.py K129              -> tek kararı tam metniyle göster
  python kod/karar_ara.py bot1 kâr          -> geçen TÜM kararları özetle listele
  python kod/karar_ara.py --liste           -> bütün kararların tek satırlık dizini
  python kod/karar_ara.py --liste kesinti   -> dizini filtreleyerek
  python kod/karar_ara.py --tam bot1        -> eşleşen kararların TAM metni

Arama Türkçe'ye duyarsızdır (İ/ı/ş/ğ/ü/ö/ç normalize edilir) ve birden çok kelime
verilirse hepsini birden içeren kararlar döner (VE mantığı).
"""
import re
import sys
import unicodedata
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
KAYNAK = KOK / "KARARLAR.md"
BASLIK = re.compile(r"^\*\*(K\d+[A-Za-z\-]*)\s*[—-]\s*(.*)$", re.MULTILINE)


def nrm(s: str) -> str:
    """Türkçe-duyarsız arama anahtarı."""
    s = s.replace("İ", "i").replace("I", "i").replace("ı", "i")
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def kararlar():
    """KARARLAR.md -> [(kod, baslik, tam_metin, satir_no)] — belge sırasıyla."""
    metin = KAYNAK.read_text(encoding="utf-8")
    satir_basi = [0]
    for m in re.finditer(r"\n", metin):
        satir_basi.append(m.end())
    bulunan = list(BASLIK.finditer(metin))
    out = []
    for i, m in enumerate(bulunan):
        son = bulunan[i + 1].start() if i + 1 < len(bulunan) else len(metin)
        satir = metin.count("\n", 0, m.start()) + 1
        out.append((m.group(1), m.group(2).strip(), metin[m.start():son].rstrip(), satir))
    return out


def kisalt(s, n=96):
    s = re.sub(r"\*\*|\*|`", "", s).replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def main(argv):
    if not argv:
        print(__doc__)
        return 0
    tam = "--tam" in argv
    liste = "--liste" in argv
    kelimeler = [a for a in argv if not a.startswith("--")]
    K = kararlar()

    # tek karar kodu mu verildi? (K129, K124-EK…)
    if len(kelimeler) == 1 and re.fullmatch(r"[Kk]\d+[A-Za-z\-]*", kelimeler[0]):
        hedef = kelimeler[0].upper()
        for kod, bas, metin, satir in K:
            if kod.upper() == hedef:
                print(f"{'='*96}\n{kod} (KARARLAR.md:{satir})\n{'='*96}\n{metin}")
                return 0
        yakin = [k for k, *_ in K if k.upper().startswith(hedef[:4])]
        print(f"{hedef} bulunamadı. Yakın: {', '.join(yakin[:8])}")
        return 1

    anahtar = [nrm(k) for k in kelimeler]
    eslesen = []
    for kod, bas, metin, satir in K:
        govde = nrm(metin)
        if all(a in govde for a in anahtar) or not anahtar:
            eslesen.append((kod, bas, metin, satir))

    if not eslesen:
        print(f"'{' '.join(kelimeler)}' için karar bulunamadı.")
        return 1

    baslik = ("TÜM KARARLAR" if not anahtar
              else f"'{' '.join(kelimeler)}' geçen kararlar")
    print(f"{'='*96}\n{baslik} — {len(eslesen)}/{len(K)} karar\n{'='*96}")

    if tam:
        for kod, bas, metin, satir in eslesen:
            print(f"\n{'-'*96}\n{kod} (satır {satir})\n{'-'*96}\n{metin}")
        return 0

    for kod, bas, metin, satir in eslesen:
        print(f"  {kod:>9} · s{satir:<5} {kisalt(bas)}")
        if anahtar and not liste:
            # ilk eslesmenin gectigi satiri baglamla goster
            for sat in metin.split("\n"):
                if all(a in nrm(sat) for a in anahtar) and len(sat.strip()) > 20:
                    print(f"            └─ {kisalt(sat.strip(), 88)}")
                    break
    print(f"\n  ipucu: tam metin için  python kod/karar_ara.py --tam {' '.join(kelimeler)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
