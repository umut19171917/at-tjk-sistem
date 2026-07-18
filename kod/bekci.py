"""
bekci.py — K47/K49: takip NABZI kontrolu. Eski surum "bugun basladi mi" soruyordu ve
16 Tem'de yetersiz kaldi (10:32 basladi, ~15:00 oldu, bekci sustu, 9 kosu gitti).
K49'dan sonra takip her 15 dk'da bir durumsuz gecis yapar ve HER geciste kalp atisi yazar
(veri/takip_son.txt). Bekci kurali: yaris-saatleri penceresinde (10:40-22:30) kalp atisi
45 dakikadan eskiyse -> EKRANDA GORUNUR uyari. PC uykudaysa ikisi de calismaz; uyaninca
gorev StartWhenAvailable ile ikisini de tetikler -> yanlis alarm olmaz.
"""
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
HB = KOK / "veri" / "takip_son.txt"
ESIK_DK = 45


def main():
    now = datetime.now()
    if not (10 * 60 + 40 <= now.hour * 60 + now.minute <= 22 * 60 + 30):
        print("bekci: yaris-saatleri penceresi disinda, kontrol yok.")
        return
    yas_dk = None
    if HB.exists():
        try:
            hb = datetime.strptime(HB.read_text(encoding="utf-8").strip(), "%Y-%m-%d %H:%M")
            yas_dk = (now - hb).total_seconds() / 60
        except ValueError:
            pass
    if yas_dk is not None and yas_dk <= ESIK_DK:
        print(f"bekci: nabiz var ({yas_dk:.0f} dk once), sorun yok.")
        return
    import tkinter as tk
    from tkinter import messagebox
    kok = tk.Tk()
    kok.withdraw()
    kok.attributes("-topmost", True)
    messagebox.showwarning(
        "TJK TAKIP NABZI YOK!",
        (f"Son gecis {yas_dk:.0f} dk once" if yas_dk is not None else "Bugun hic gecis yok")
        + f" (esik {ESIK_DK} dk).\n\n"
        "Zamanlanmis gorev calismiyor olabilir. Kontrol:\n"
        "  1) Gorev Zamanlayici'da 'TJK Takip' etkin mi?\n"
        "  2) Elle bir gecis: at klasoru > baslat_takip.bat (cift tik)\n\n"
        "(Detay: KARARLAR.md K49)")
    kok.destroy()


if __name__ == "__main__":
    main()
