# -*- coding: utf-8 -*-
"""Iki git surumu arasinda FONKSIYON DUZEYINDE davranis degisikligi arar.

Yorum/bosluk/docstring farklarini gormezden gelir; yalnizca calisan kodun AST'sine bakar.
Boylece "yorum ekledim" ile "mantik degistirdim" ayrilir.
"""
import ast
import subprocess
import sys

ESKI = sys.argv[1]
YENI = sys.argv[2]
DOSYALAR = sys.argv[3:]


def govde(src, ad):
    """dosyadaki her fonksiyon/metot icin AST parmak izi (docstring HARIC)."""
    try:
        t = ast.parse(src)
    except SyntaxError as e:
        return {"__PARSE_HATASI__": str(e)}
    out = {}
    for n in ast.walk(t):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            g = list(n.body)
            if (g and isinstance(g[0], ast.Expr)
                    and isinstance(getattr(g[0], "value", None), ast.Constant)
                    and isinstance(g[0].value.value, str)):
                g = g[1:]                      # docstring at
            out[n.name] = ast.dump(ast.Module(body=g, type_ignores=[]))
    # modul duzeyi (fonksiyon disi) kod: sabitler, KONFIG, esikler...
    modg = [x for x in t.body
            if not isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                                  ast.Import, ast.ImportFrom))]
    if modg and isinstance(modg[0], ast.Expr) and isinstance(
            getattr(modg[0], "value", None), ast.Constant) and isinstance(
            modg[0].value.value, str):
        modg = modg[1:]
    out["<MODUL DUZEYI (sabitler/esikler/KONFIG)>"] = ast.dump(
        ast.Module(body=modg, type_ignores=[]))
    return out


def oku(rev, yol):
    try:
        return subprocess.run(["git", "show", f"{rev}:{yol}"], capture_output=True,
                              text=True, encoding="utf-8", check=True).stdout
    except subprocess.CalledProcessError:
        return None


print("=" * 96)
print(f"FONKSIYON DUZEYI DAVRANIS KARSILASTIRMASI   {ESKI}  ->  {YENI}")
print("(yorum/docstring/bosluk farklari GORMEZDEN gelinir; yalniz calisan kod)")
print("=" * 96)
toplam_degisen = 0
for yol in DOSYALAR:
    a, b = oku(ESKI, yol), oku(YENI, yol)
    if a is None:
        print(f"\n### {yol}: eski surumde YOK (yeni dosya)")
        continue
    if b is None:
        print(f"\n### {yol}: yeni surumde YOK (SILINMIS!)")
        toplam_degisen += 1
        continue
    A, B = govde(a, yol), govde(b, yol)
    degisen = [k for k in set(A) | set(B) if A.get(k) != B.get(k)]
    if not degisen:
        print(f"\n### {yol}: {len(B)} fonksiyon/blok — HEPSI AYNI  ✓  (davranis degismedi)")
    else:
        toplam_degisen += len(degisen)
        print(f"\n### {yol}: {len(degisen)} BLOK DEGISTI  ⚠")
        for k in sorted(degisen):
            durum = ("YENI" if k not in A else "SILINDI" if k not in B else "DEGISTI")
            print(f"      {durum:>8}: {k}")
print("\n" + "=" * 96)
print(f"SONUC: davranisi degisen blok sayisi = {toplam_degisen}")
print("=" * 96)
