# -*- coding: utf-8 -*-
"""
ast_diff.py — K149 / BEKLEYENLER 22-H: DAVRANIŞ DEĞİŞTİ Mİ? (fonksiyon düzeyi AST kıyası)

Yorum/docstring/boşluk farklarını GÖRMEZDEN gelir; yalnız çalışan kodun AST'sine bakar.
Böylece "yorum ekledim" ile "mantık değiştirdim" kesin olarak ayrılır.

NEDEN VAR: K136'da dört dosyaya uyarı yorumu eklendi, K139'da telegram yolu değişti — her
seferinde "canlı sistemin davranışı değişmedi" iddiasının KANITLANMASI gerekti. K138'de bu
araç ilk kez yazıldı ve üç kararda kullanıldı; 22-H ile kalıcı hâle getirildi.

KULLANIM
  python kod/ast_diff.py                      -> ÇEKİRDEK dosyalar: HEAD ile çalışma ağacı
  python kod/ast_diff.py --hepsi              -> kod/*.py tamamı
  python kod/ast_diff.py HEAD~5               -> çekirdek: HEAD~5 ile çalışma ağacı
  python kod/ast_diff.py 207eb99 HEAD         -> iki commit arası
  python kod/ast_diff.py HEAD -- kod/model.py -> belirli dosyalar

ÇIKIŞ KODU: 0 = hiçbir davranış değişmedi · 1 = değişen blok var (betikte kullanılabilir)

ÇEKİRDEK = canlı yolun puanlama/karar veren dosyaları. Rapor/görüntü dosyaları bilerek
dışarıda: onların değişmesi beklenen bir şey, gürültü yapar.
"""
import ast
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent

CEKIRDEK = ["kod/model.py", "kod/ozellik.py", "kod/altili_olasilik.py", "kod/duzlestir.py",
            "kod/takip.py", "kod/gunluk.py", "kod/altili_canli.py", "kod/altili_backtest.py",
            "kod/defter.py", "kod/paper.py", "kod/rapor_ortak.py", "kod/oran_log.py"]


def parmak_izi(src):
    """Her fonksiyon + modül düzeyi için AST parmak izi (docstring HARİÇ)."""
    try:
        t = ast.parse(src)
    except SyntaxError as e:
        return {"__SÖZDİZİMİ_HATASI__": str(e)}

    def govdesiz(govde):
        g = list(govde)
        if (g and isinstance(g[0], ast.Expr) and isinstance(getattr(g[0], "value", None),
                                                            ast.Constant)
                and isinstance(g[0].value.value, str)):
            g = g[1:]                                   # docstring at
        return ast.dump(ast.Module(body=g, type_ignores=[]))

    out = {}
    for n in ast.walk(t):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[f"{n.name}()"] = govdesiz(n.body)
        elif isinstance(n, ast.ClassDef):
            out[f"class {n.name}"] = govdesiz(n.body)
    modul = [x for x in t.body if not isinstance(
        x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))]
    out["<MODÜL DÜZEYİ: sabitler/eşikler/KONFIG>"] = govdesiz(modul)
    return out


def oku_git(rev, yol):
    r = subprocess.run(["git", "show", f"{rev}:{yol}"], capture_output=True,
                       text=True, encoding="utf-8", cwd=KOK)
    return r.stdout if r.returncode == 0 else None


def oku_disk(yol):
    p = KOK / yol
    return p.read_text(encoding="utf-8") if p.exists() else None


def main(argv):
    hepsi = "--hepsi" in argv
    argv = [a for a in argv if a != "--hepsi"]
    if "--" in argv:
        i = argv.index("--")
        revler, dosyalar = argv[:i], argv[i + 1:]
    else:
        revler, dosyalar = argv, []

    eski = revler[0] if revler else "HEAD"
    yeni = revler[1] if len(revler) > 1 else None       # None = çalışma ağacı

    if not dosyalar:
        if hepsi:
            dosyalar = sorted(f"kod/{p.name}" for p in (KOK / "kod").glob("*.py"))
        else:
            dosyalar = [d for d in CEKIRDEK if (KOK / d).exists()]

    print("=" * 98)
    print(f"AST KIYASI   {eski}  ->  {yeni or 'çalışma ağacı'}")
    print("yorum/docstring/boşluk GÖRMEZDEN gelinir; yalnız çalışan kod")
    print(f"kapsam: {len(dosyalar)} dosya ({'tamamı' if hepsi else 'çekirdek'})")
    print("=" * 98)

    toplam, bozuk = 0, 0
    for yol in dosyalar:
        a = oku_git(eski, yol)
        b = oku_git(yeni, yol) if yeni else oku_disk(yol)
        if a is None:
            print(f"\n### {yol}: eski sürümde YOK (yeni dosya)")
            continue
        if b is None:
            print(f"\n### {yol}: yeni sürümde YOK — *** SİLİNMİŞ ***")
            toplam += 1
            continue
        A, B = parmak_izi(a), parmak_izi(b)
        if "__SÖZDİZİMİ_HATASI__" in B:
            print(f"\n### {yol}: *** SÖZDİZİMİ HATASI *** {B['__SÖZDİZİMİ_HATASI__']}")
            bozuk += 1
            toplam += 1
            continue
        degisen = sorted(k for k in set(A) | set(B) if A.get(k) != B.get(k))
        if not degisen:
            print(f"  [✓] {yol:<28} {len(B):>3} blok — hepsi AYNI")
        else:
            toplam += len(degisen)
            print(f"  [!] {yol:<28} {len(degisen):>3} BLOK DEĞİŞTİ")
            for k in degisen:
                durum = "YENİ" if k not in A else ("SİLİNDİ" if k not in B else "değişti")
                print(f"        {durum:>8}: {k}")

    print("\n" + "=" * 98)
    if bozuk:
        print(f"*** {bozuk} DOSYADA SÖZDİZİMİ HATASI — ÖNCE ONU DÜZELT ***")
    if toplam == 0:
        print("SONUÇ: hiçbir davranış değişmedi. (Yorum/biçim değişiklikleri bu kıyası geçer.)")
    else:
        print(f"SONUÇ: davranışı değişen blok sayısı = {toplam}")
        print("Beklenen bir değişiklikse sorun yok; beklenmiyorsa İNCELE.")
    print("=" * 98)
    return 1 if toplam else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
