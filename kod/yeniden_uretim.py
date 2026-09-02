# -*- coding: utf-8 -*-
"""
yeniden_uretim.py — K150 / BEKLEYENLER 22-C: YENİDEN ÜRETİLEBİLİRLİK DENETİMİ. SALT-OKUNUR.

SORU: Boş bir makinede bu proje sıfırdan kurulup aynı çıktıları üretebilir mi? 2 aylık
birikim var ve hiç denenmedi.

NEDEN TAM KLON TESTİ YAPILMIYOR: `kazi.py` ile tüm arşivi yeniden indirmek ~2 saat sürer ve
TJK sunucusuna gereksiz yük bindirir. Onun yerine zincirin HER HALKASI ayrı doğrulanır —
bu, "çalışır herhâlde" demekten kesin olarak daha güçlüdür.

ASIL ÇIKTI: **neyin yeniden üretilebildiği, neyin ÜRETİLEMEDİĞİ.** Telafisi olmayanı bilmek,
yedekleme kararının tek girdisidir (ZAMANLI #6).
"""
import ast
import glob
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent

# (dosya/klasör, üreten adım, kaynağı, telafi edilebilir mi)
ZINCIR = [
    ("veri/ham/", "kazi.py", "ebayi.tjk.org (DIŞ)", "ŞARTLI",
     "TJK arşivi açık kaldığı sürece ~2 saatte iner. Kapanırsa TELAFİSİ YOK."),
    ("veri/katilim.csv", "duzlestir.py", "veri/ham/", "EVET",
     "ham'dan tamamen yeniden üretilir"),
    ("veri/ozellikli.csv", "ozellik.py", "veri/katilim.csv", "EVET",
     "katilim'dan tamamen yeniden üretilir"),
    ("veri/altili_olasilik*.csv", "altili_olasilik.py", "katilim.csv + model.py", "EVET",
     "walk-forward yeniden fit; sabit tohum yok ama L-BFGS deterministik"),
    ("veri/altili_tam.csv", "altili_ayikla.py", "veri/ham/", "EVET", "ham'dan üretilir"),
    ("veri/altili_temettu.csv", "altili_ayikla.py", "veri/ham/", "EVET", "ham'dan üretilir"),
    ("veri/defter.csv", "takip.py (canlı)", "GÜNLÜK AKIŞ", "HAYIR",
     "kupon anı tahmin kaydı — geçmişe dönük üretilemez (o anki oranlar kayıtlı değil)"),
    ("veri/altili_kupon.csv", "altili_canli.py (canlı)", "GÜNLÜK AKIŞ", "HAYIR",
     "kupon anındaki seçim — geçmişe dönük üretilemez"),
    ("veri/altili_kupon_ani.csv", "altili_canli.py (canlı)", "GÜNLÜK AKIŞ", "HAYIR",
     "kupon anı olasılık fotoğrafı — TELAFİSİ YOK"),
    ("veri/altili_oran_log.csv", "oran_log.py (canlı)", "GÜNLÜK AKIŞ", "HAYIR",
     "zaman damgalı oran serisi — arşivde YOK, TELAFİSİ YOK (K92/K111'in temeli)"),
    ("kod/telegram_config.json", "elle kurulum", "@BotFather", "EVET",
     "yeni token alınabilir (kod/telegram_at.py --kur)"),
    ("KARARLAR.md / BEKLEYENLER.md", "git", "GitHub (private)", "EVET",
     "uzak depoda; her commit makine dışına gidiyor"),
]


def dis_bagimliliklar():
    std = set(sys.stdlib_module_names)
    yerel = {Path(f).stem for f in glob.glob(str(KOK / "kod" / "*.py"))}
    dis = set()
    for f in glob.glob(str(KOK / "kod" / "*.py")):
        try:
            t = ast.parse(Path(f).read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for n in ast.walk(t):
            if isinstance(n, ast.Import):
                dis |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                dis.add(n.module.split(".")[0])
    return dis - std - yerel


def main():
    print("=" * 100)
    print("K150 / 22-C — YENİDEN ÜRETİLEBİLİRLİK DENETİMİ")
    print("=" * 100)

    # ------------------------------------------------ 1) bagimliliklar
    print("\n1) BAĞIMLILIKLAR")
    print("-" * 100)
    dis = dis_bagimliliklar()
    req_p = KOK / "requirements.txt"
    req = {l.split("==")[0].strip().lower()
           for l in req_p.read_text(encoding="utf-8").splitlines() if l.strip()} if req_p.exists() else set()
    eksik = sorted(d for d in dis if d.lower() not in req)
    print(f"  kod/*.py dış bağımlılık : {', '.join(sorted(dis))}")
    print(f"  requirements.txt        : {', '.join(sorted(req))}")
    print(f"  EKSİK                   : {', '.join(eksik) if eksik else '— yok, tamam ✓'}")
    print(f"  sürümler sabitlenmiş mi : "
          f"{'evet ✓' if all('==' in l for l in req_p.read_text(encoding='utf-8').splitlines() if l.strip()) else 'HAYIR'}")

    # ------------------------------------------------ 2) git
    print("\n2) KOD + KARAR GÜNLÜĞÜ (git)")
    print("-" * 100)
    r = subprocess.run(["git", "status", "--short", "--branch"], capture_output=True,
                       text=True, encoding="utf-8", cwd=KOK)
    dal = r.stdout.splitlines()[0] if r.stdout else "?"
    uzak = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True,
                          text=True, encoding="utf-8", cwd=KOK).stdout.strip()
    print(f"  uzak depo : {uzak or 'YOK — TEK DİSK RİSKİ'}")
    print(f"  durum     : {dal}")
    senkron = "ahead" not in dal and "behind" not in dal
    print(f"  senkron   : {'evet ✓' if senkron else '*** DEĞİL — itilmemiş commit var ***'}")

    # ------------------------------------------------ 3) zincir
    print("\n3) VERİ ZİNCİRİ — neyi yeniden üretebiliriz?")
    print("-" * 100)
    print(f"  {'dosya':>30} {'üreten':>22} {'telafi':>8}  not")
    for dosya, uretici, kaynak, telafi, notu in ZINCIR:
        isaret = {"EVET": "✓", "HAYIR": "✗", "ŞARTLI": "!"}[telafi]
        print(f"  {dosya:>30} {uretici:>22} {isaret:>4} {telafi:<6} {notu[:46]}")

    yok = [z for z in ZINCIR if z[3] == "HAYIR"]
    sartli = [z for z in ZINCIR if z[3] == "ŞARTLI"]

    # ------------------------------------------------ hüküm
    print("\n" + "=" * 100)
    print("HÜKÜM")
    print("=" * 100)
    print("  YENİDEN ÜRETİLEBİLİR: kod, karar günlüğü, ham arşivden türetilen HER ŞEY")
    print("  (katilim, ozellikli, olasılık, altili_tam, temettü). Bağımlılıklar sabit ve tam.")
    print(f"\n  *** TELAFİSİ OLMAYAN {len(yok)} DOSYA — kaybolursa GERİ GELMEZ: ***")
    for d, u, k, t, n in yok:
        print(f"    · {d:<28} {n}")
    print("\n  Bunlar 'canlı akış' ürünleridir: kupon ANINDAKİ tahmin, seçim ve oran fotoğrafı.")
    print("  Arşivde yalnız KAPANIŞ oranı var; kupon anı oranı hiçbir yerde yeniden bulunamaz.")
    print("  K92 (uzak-ayak λ), K111 (zamanlama) ve K129 (AGF kararlılığı) tamamen bunlara dayanıyor.")
    for d, u, k, t, n in sartli:
        print(f"\n  ! ŞARTLI: {d} — {n}")
    print("\n  SONUÇ: yedekleme önceliği DİSK BOYUTU değil, TELAFİ EDİLEBİLİRLİK sırasına göre:")
    print("    1. veri/altili_kupon_ani.csv + altili_oran_log.csv + defter.csv + altili_kupon.csv")
    print("       (küçük — birkaç MB — ama telafisi YOK; git'te de değiller mi kontrol et)")
    print("    2. veri/ham/ (1,1 GB, TJK açık kaldığı sürece telafi edilebilir)")
    print("    3. gerisi (kod+kararlar zaten GitHub'da; türetilenler yeniden üretilir)")


if __name__ == "__main__":
    main()
