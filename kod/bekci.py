"""
bekci.py — K47/K49: takip NABZI + K106: CONFIG KAPSAMA denetimi.

NABIZ (K47/K49): eski surum "bugun basladi mi" soruyordu ve 16 Tem'de yetersiz kaldi
(10:32 basladi, ~15:00 oldu, bekci sustu, 9 kosu gitti). K49'dan sonra takip her 15 dk'da bir
durumsuz gecis yapar ve HER geciste kalp atisi yazar (veri/takip_son.txt). Kural: yaris-saatleri
penceresinde (10:40-22:30) kalp atisi 45 dakikadan eskiyse -> EKRANDA GORUNUR uyari.
PC uykudaysa ikisi de calismaz; uyaninca gorev StartWhenAvailable ile ikisini de tetikler.

KAPSAMA (K106): nabiz ATMAYA DEVAM EDERKEN bir config sessizce kupon kurmayi birakabilir.
Disiplin kurali 8: "kupon kurulmazsa o Altili deneyden duser -- olculen en pahali hasar budur."
Buna karsi hicbir alarm yoktu; K103'un dersi (kamu sirasi K97'de sessizce dustu, IKI HAFTA
fark edilmedi) bunun tekrar edecegini soyluyor.
Kural: bugun kupon kurulmus her (pist,seq) Altili'sinda, o pencerenin dk grubuna ait TUM aktif
config'ler bulunmali. Eksik varsa uyari. SALT-OKUNUR -- hicbir dosyaya yazmaz, kupon kurmaz.

YANLIS ALARM KORUMASI: bir config'in ILK kuruldugu gunden onceki Altililar sayilmaz
(yeni eklenen config gecmisi yakalamaz); 15 dk grubu, 30 dk grubunun kuruldugu ama 15 dk
penceresinin henuz gelmedigi anlarda eksik gorunur -> yalniz ILK KOSUSU BASLAMIS Altililar denetlenir.
"""
import sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
HB = KOK / "veri" / "takip_son.txt"
KUPON = KOK / "veri" / "altili_kupon.csv"
ESIK_DK = 45


def _uyar(baslik, metin):
    """Ekranda gorunur uyari. Tkinter yoksa konsola duser (gorev pythonw ile kosar)."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        kok = tk.Tk()
        kok.withdraw()
        kok.attributes("-topmost", True)
        messagebox.showwarning(baslik, metin)
        kok.destroy()
    except Exception:                                            # noqa: BLE001
        print(f"[UYARI] {baslik}\n{metin}")


def nabiz_kontrol(now):
    """Doner: True = sorun yok / False = uyari verildi."""
    yas_dk = None
    if HB.exists():
        try:
            hb = datetime.strptime(HB.read_text(encoding="utf-8").strip(), "%Y-%m-%d %H:%M")
            yas_dk = (now - hb).total_seconds() / 60
        except ValueError:
            pass
    if yas_dk is not None and yas_dk <= ESIK_DK:
        print(f"bekci: nabiz var ({yas_dk:.0f} dk once), sorun yok.")
        return True
    _uyar("TJK TAKIP NABZI YOK!",
          (f"Son gecis {yas_dk:.0f} dk once" if yas_dk is not None else "Bugun hic gecis yok")
          + f" (esik {ESIK_DK} dk).\n\n"
          "Zamanlanmis gorev calismiyor olabilir. Kontrol:\n"
          "  1) Gorev Zamanlayici'da 'TJK Takip' etkin mi?\n"
          "  2) Elle bir gecis: at klasoru > baslat_takip.bat (cift tik)\n\n"
          "(Detay: KARARLAR.md K49)")
    return False


def kapsama_kontrol(now):
    """K106: bugunku Altililarda eksik config var mi? Doner: eksik listesi (bos = sorun yok)."""
    try:
        import pandas as pd
        sys.path.insert(0, str(KOK / "kod"))
        from altili_canli import aktif_konfig, KONFIG
    except Exception as e:                                       # noqa: BLE001
        print(f"bekci: kapsama denetimi atlandi ({type(e).__name__}) -- nabiz kontrolu etkilenmedi.")
        return []
    if not KUPON.exists():
        return []
    k = pd.read_csv(KUPON, low_memory=False)
    bugun = now.strftime("%Y-%m-%d")
    g = k[k["tarih"] == bugun]
    if g.empty:
        print("bekci: bugun henuz kupon yok, kapsama denetimi yapilmadi.")
        return []
    # her config'in SICILDEKI ilk gunu -> o gunden onceki Altililarda aranmaz
    ilk_gun = k.groupby("config")["tarih"].min().to_dict()
    eksik = []
    for (pist, seq), gg in g.groupby(["pist", "seq"]):
        ilk_saat = str(gg["ilk_saat"].iloc[0])
        try:
            post = datetime.strptime(f"{bugun} {ilk_saat}", "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if now < post:
            continue                       # ilk kosu baslamadi -> 15 dk grubu hakli olarak eksik olabilir
        var = set(gg["config"])
        for c in aktif_konfig():
            if ilk_gun.get(c, "9999-99-99") > bugun:
                continue                   # config bugun ilk kez ekleniyor -> gecmisi aranmaz
            if c not in var:
                eksik.append((pist, int(seq), c, KONFIG[c].get("dk", 30)))
    return eksik


def main():
    now = datetime.now()
    if not (10 * 60 + 40 <= now.hour * 60 + now.minute <= 22 * 60 + 30):
        print("bekci: yaris-saatleri penceresi disinda, kontrol yok.")
        return
    if not nabiz_kontrol(now):
        return                              # nabiz yoksa kapsama zaten anlamsiz
    eksik = kapsama_kontrol(now)
    if not eksik:
        print("bekci: config kapsamasi tam.")
        return
    sat = "\n".join(f"  {p} {s}. Altili -> {c} ({dk} dk grubu)" for p, s, c, dk in eksik[:12])
    print(f"[UYARI] eksik config: {len(eksik)}")
    _uyar("TJK: BIR CONFIG KUPON KURMADI!",
          f"Bugun {len(eksik)} yerde aktif config'in kuponu YOK:\n\n{sat}\n\n"
          "Bu, olculen EN PAHALI hasardir: o Altili o config icin deneyden duser.\n\n"
          "Kontrol:\n"
          "  1) veri/takip_log.txt -> 'altili kupon hatasi' satiri var mi?\n"
          "  2) Config yeni eklendiyse ve pencere kacirildiysa normaldir.\n\n"
          "(Detay: KARARLAR.md K106)")


if __name__ == "__main__":
    main()
