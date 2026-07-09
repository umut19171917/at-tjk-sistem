"""
bekci.py — K47: takip BUGUN calisti mi? (K43/K45 vakalari: gorev sessizce calismayinca
gun kayboluyordu ve kimse fark etmiyordu.) Zamanlanmis gorev 13:30'da bunu calistirir:
  - takip o gun basladiysa (veri/takip_son.txt kalp atisi bugunun tarihiyle) -> sessizce biter.
  - baslamadiysa -> EKRANDA GORUNUR uyari penceresi: "baslat_takip.bat'a cift tikla".
Yaris olmayan gunler sorun degil: takip 10:30'da yine acilir, kalp atisini yazar,
"pist yok" deyip kapanir -> bekci sessiz kalir.
"""
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
HB = KOK / "veri" / "takip_son.txt"


def main():
    bugun = date.today().isoformat()
    if HB.exists() and HB.read_text(encoding="utf-8").strip().startswith(bugun):
        print(f"bekci: takip bugun ({bugun}) calismis, sorun yok.")
        return
    import tkinter as tk
    from tkinter import messagebox
    kok = tk.Tk()
    kok.withdraw()
    kok.attributes("-topmost", True)
    messagebox.showwarning(
        "TJK TAKIP BUGUN CALISMADI!",
        f"Bugun ({bugun}) takip baslamamis gorunuyor.\n\n"
        "Yaris varsa kayip buyumeden:\n"
        "  Masaustu > projeler > at > baslat_takip.bat  (cift tik)\n\n"
        "(Detay: KARARLAR.md K47)")
    kok.destroy()


if __name__ == "__main__":
    main()
