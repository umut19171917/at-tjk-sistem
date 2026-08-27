# -*- coding: utf-8 -*-
"""
model_deney.py — K128: BOT1'İN BİÇİMİ, PENCERESİ VE HEDEFİ. SALT-OKUNUR / OFFLINE.

NEDEN: K33'te özellik mühendisliği ön-taahhütle KAPATILDI — 8 test, hiçbiri Bot2'yi
oynatmadı. O karar geçerli ve bu betik ONA DOKUNMUYOR: **tek bir yeni özellik eklenmiyor.**

Fark ettiğim şey şu: o 8 testin sekizi de MALZEMEYİ değiştirdi, hiçbiri TARİFİ değiştirmedi.
Bot1 hâlâ üç sınanmamış varsayımın üstünde duruyor:
    (1) model DOĞRUSAL (17 z-skorun düz toplamı)
    (2) eğitim hedefi YALNIZ KAZANAN
    (3) eğitim penceresi SABİT 2021-2023 (test 2025-26 -> 2 yıl bayat)
K33 "bu malzemelerde daha fazla sinyal yok" dedi; "bu malzemelerdeki sinyali doğrusal bir
modelle tam çıkardık" DEMEDİ. Bu betik o üç varsayımı sınar.

=====================================================================================
ÖN-KAYITLI ÖLÇÜT — SONUÇLAR GÖRÜLMEDEN YAZILDI VE GİT'E MÜHÜRLENDİ (K33/K52)
=====================================================================================
0) MUTLAK SINIR — CANLI SİSTEM: bu betik HİÇBİR dosyaya yazmaz. `model.py`, `ozellik.py`,
   `altili_olasilik.py`, `gunluk.py`, config'ler, kuponlar — HİÇBİRİ değişmez.
   `veri/ozellikli.csv` YALNIZCA OKUNUR, asla yeniden üretilmez. Bir varyant kazansa bile
   bu betik onu canlıya ALMAZ; alma kararı ayrı ve KULLANICININDIR.

1) ÇAPA (kill-first): "T" (taban) varyantı, `model.py`'nin bugünkü çıktısını üretmeli:
       alpha = +0,190 · gamma = +0,975 · Bot1 OOS 1,8594 · Bot2 OOS 1,6987
   Tolerans: log-loss +/-0,0005 · alpha +/-0,002.
   TUTMAZSA: ölçüm GÜVENİLMEZ ilan edilir, HİÇBİR VARYANT HÜKÜM ALMAZ.

2) YENİ ÖZELLİK YASAK. FEAT listesi (17) aynen kalır. Değişebilecek üç şey:
   pencere/ağırlık · fonksiyon biçimi · eğitim hedefi. Bir varyant yeni bir ham sütun
   getiriyorsa ölçüt ihlalidir ve o varyant atılır.

3) BİRİNCİL HÜKÜM — bir varyant "GEÇTİ" sayılır ancak ÜÇÜ BİRDEN tutarsa:
   (a) alpha > taban alpha (bot1 fiyata ek bilgi katıyor)
   (b) Bot2 OOS log-loss (2025-26) < taban Bot2 OOS log-loss
   (c) (b)'deki farkın KOŞU-DÜZEYİ eşleşmiş bootstrap GA'sı tamamen sıfırın altında,
       Bonferroni düzeltmeli: 9 varyant -> iki yanlı %99,44 GA (0,05/9).
   Üçünden biri tutmazsa DÜŞTÜ.

4) BOOTSTRAP: koşu düzeyinde (at düzeyinde DEĞİL), eşleşmiş, 4.000 tekrar. Aynı test
   koşuları her varyantta aynı — kıyas eşleşmiş.

5) VARYANTLAR (9 adet, sonuçlara bakılmadan sabitlendi):
   A. PENCERE/TAZELİK  (eğitim ağırlığı; FEAT aynı)
      A1 üstel zaman ağırlığı, yarı-ömür 1 yıl
      A2 üstel zaman ağırlığı, yarı-ömür 2 yıl
      A3 üstel zaman ağırlığı, yarı-ömür 3 yıl
      A4 kayan pencere: yalnız 2022-2023
      A5 kayan pencere: yalnız 2023
   B. BİÇİM  (aynı 17 özellik, farklı fonksiyon)
      B1 + 5 ÖNCEDEN BAĞLANMIŞ etkileşim terimi (aşağıda listeli; sonuca bakılmadan seçildi)
      B2 parçalı-doğrusal (spline) genişletme: 13 sürekli z-skorun her biri 3 düğümle
      B3 gradient boosting (yarış-içi softmax hedefi), derinlik 3, lr 0,05, **M=300 SABİT**
         -- erken durdurma YOK, M seçimi YOK (seçim serbestliği = overfit kapısı)
   C. HEDEF
      C1 sıra-patlatmalı (Plackett-Luce) eğitim, derinlik 3 -- kazanan + 2. + 3.

   B1'in etkileşimleri (alan bilgisiyle, sonuçtan bağımsız seçildi):
      kilo_z x mesafe_n · form_pos_z x son_yarisdan_gun_z · jokey_isabet_z x alan_n
      hiz_son_ort_z x going_n · kariyer_galip_oran_z x yas_z

6) BİRLEŞTİRME YASAK: birden fazla varyant geçse bile bu koşuda birleştirilmez.
   Birleştirme ayrı bir ön-kayıt ister (aksi halde 2^9 kombinasyonda arama = overfit).

7) alpha YÜKSELİR AMA log-loss DÜŞMEZSE: bu "DÜŞTÜ"dür ve öyle raporlanır. alpha
   mekanizma göstergesidir, hüküm değil. (Kullanıcıya "alpha termometredir" dedim;
   doğrusu: alpha termometre, log-loss karar. İkisi birden isteniyor -- madde 3.)
=====================================================================================
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from ozellik import FEAT                                            # noqa: E402
from model import race_struct, seg_softmax, devig, logloss, prep    # noqa: E402

from scipy.optimize import minimize                                 # noqa: E402

BOOT = 4000
N_VARYANT = 9
BONF = 0.05 / N_VARYANT                    # iki yanli %99,44
RNG = np.random.default_rng(20260827)

CAPA = {"alpha": 0.190, "gamma": 0.975, "ll1": 1.8594, "ll2": 1.6987}
TOL_LL, TOL_A = 0.0005, 0.002

SUREKLI = ["hiz_son_ort_z", "hiz_en_iyi_z", "form_pos_z", "form_fark_z", "kilo_z",
           "handikap_z", "kariyer_galip_oran_z", "zemin_galip_oran_z", "jokey_isabet_z",
           "antrenor_isabet_z", "kulvar_skor_z", "son_yarisdan_gun_z", "yas_z"]

ETKILESIM = [("kilo_z", "mesafe_n"), ("form_pos_z", "son_yarisdan_gun_z"),
             ("jokey_isabet_z", "alan_n"), ("hiz_son_ort_z", "going_n"),
             ("kariyer_galip_oran_z", "yas_z")]


# --------------------------- agirlikli conditional logit -------------------------
def fit_clogit_w(X, start, sizes, win, w=None):
    """model.fit_clogit'in agirlikli hali. w = KOSU basina agirlik (None -> hepsi 1)."""
    if w is None:
        wr = np.ones(len(start))
    else:
        wr = np.asarray(w, float)
    wrow = np.repeat(wr, sizes)

    def negll(b):
        p = seg_softmax(X @ b, start, sizes)
        ll = (np.log(p[win] + 1e-12) * wr).sum()
        grad = (X[win] * wr[:, None]).sum(0) - (X * (p * wrow)[:, None]).sum(0)
        return -ll, -grad
    r = minimize(negll, np.zeros(X.shape[1]), jac=True, method="L-BFGS-B")
    return r.x


# ------------------------------- histogram GBM ----------------------------------
def _hist_split(Bsub, gsub, nbin, min_n):
    """En iyi (ozellik, esik) bolunmesi. Kriter: L2 kazanci = sum(g)^2/n toplami."""
    n = len(gsub)
    if n < 2 * min_n:
        return None
    G, N = gsub.sum(), float(n)
    en_iyi, skor0 = None, G * G / N
    for j in range(Bsub.shape[1]):
        b = Bsub[:, j]
        gs = np.bincount(b, weights=gsub, minlength=nbin)
        ns = np.bincount(b, minlength=nbin).astype(float)
        gl, nl = np.cumsum(gs)[:-1], np.cumsum(ns)[:-1]
        gr, nr = G - gl, N - nl
        ok = (nl >= min_n) & (nr >= min_n)
        if not ok.any():
            continue
        kaz = np.where(ok, gl * gl / np.maximum(nl, 1) + gr * gr / np.maximum(nr, 1), -np.inf)
        k = int(np.argmax(kaz))
        if kaz[k] > skor0 and (en_iyi is None or kaz[k] > en_iyi[2]):
            en_iyi = (j, k, float(kaz[k]))
    return en_iyi


def _agac(Bin, g, idx, derinlik, nbin, min_n):
    Bsub, gsub = Bin[idx], g[idx]
    d = _hist_split(Bsub, gsub, nbin, min_n) if derinlik > 0 else None
    if d is None:
        return ("yaprak", float(gsub.mean()) if len(idx) else 0.0)
    j, k, _ = d
    m = Bsub[:, j] <= k
    sol, sag = idx[m], idx[~m]
    if len(sol) == 0 or len(sag) == 0:
        return ("yaprak", float(gsub.mean()))
    return ("dal", j, k, _agac(Bin, g, sol, derinlik - 1, nbin, min_n),
            _agac(Bin, g, sag, derinlik - 1, nbin, min_n))


def _tahmin(agac, Bin, out=None, idx=None):
    n = Bin.shape[0]
    if out is None:
        out, idx = np.zeros(n), np.arange(n)
    if agac[0] == "yaprak":
        out[idx] = agac[1]
        return out
    _, j, k, sol, sag = agac
    m = Bin[idx, j] <= k
    _tahmin(sol, Bin, out, idx[m])
    _tahmin(sag, Bin, out, idx[~m])
    return out


def gbm_fit(Xtr, start, sizes, win, kenar, M=300, lr=0.05, derinlik=3, nbin=32, min_n=200):
    """Yaris-ici softmax hedefiyle gradient boosting. kenar = bin kenarlari (egitimden)."""
    Bin = np.stack([np.clip(np.searchsorted(kenar[j], Xtr[:, j], side="right") - 1, 0, nbin - 1)
                    for j in range(Xtr.shape[1])], axis=1).astype(np.int32)
    s = np.zeros(len(Xtr))
    agaclar = []
    tum = np.arange(len(Xtr))
    for _ in range(M):
        p = seg_softmax(s, start, sizes)
        g = win.astype(float) - p
        a = _agac(Bin, g, tum, derinlik, nbin, min_n)
        agaclar.append(a)
        s += lr * _tahmin(a, Bin)
    return agaclar, lr, nbin


def gbm_skor(agaclar, lr, nbin, kenar, X):
    Bin = np.stack([np.clip(np.searchsorted(kenar[j], X[:, j], side="right") - 1, 0, nbin - 1)
                    for j in range(X.shape[1])], axis=1).astype(np.int32)
    s = np.zeros(len(X))
    for a in agaclar:
        s += lr * _tahmin(a, Bin)
    return s


# ------------------------------ sira-patlatma (C1) -------------------------------
def patlat(df, k, feats):
    """Kosulari k asamali pseudo-kosulara acar (Plackett-Luce). plase_model.py deseni."""
    parcalar = []
    for s in range(1, k + 1):
        d = df[~(df["sonuc"] < s)].copy()
        d["kazandi"] = (d["sonuc"] == s).astype(int)
        gw = d.groupby("race_kod")["kazandi"].transform("sum")
        sz = d.groupby("race_kod")["race_kod"].transform("size")
        d = d[(gw == 1) & (sz >= 2)]
        d = d.copy()
        d["race_kod"] = d["race_kod"] * 10 + s
        parcalar.append(d[["race_kod", "kazandi"] + feats])
    return pd.concat(parcalar, ignore_index=True).sort_values("race_kod").reset_index(drop=True)


# --------------------------------- yardimci --------------------------------------
def yukle():
    d = pd.read_csv(KOK / "veri" / "ozellikli.csv", low_memory=False)
    d["yil"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    for c in FEAT:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0.0)
    d["sonuc"] = pd.to_numeric(d["sonuc"], errors="coerce")
    # etkilesimler icin normalize edilmis KOSU-DUZEYI degiskenler (yeni OZELLIK degil:
    # zaten modelde olan z-skorlarin etkilesim ortagi; tek baslarina modele GIRMEZ)
    d["mesafe_n"] = (pd.to_numeric(d["mesafe"], errors="coerce").fillna(1600) - 1600) / 800.0
    d["alan_n"] = (pd.to_numeric(d["alan"], errors="coerce").fillna(9) - 9) / 3.0
    d["going_n"] = pd.to_numeric(d["going_agirlik"], errors="coerce").fillna(0.0)
    return d


def spline_genislet(tr, ot, kolonlar):
    """Her surekli z-skoru [x, max(x-k,0) x3] tabanina acar. Dugumler EGITIMDEN."""
    yeni_tr, yeni_ot, ad = [], [], []
    for c in kolonlar:
        x = tr[c].to_numpy(float)
        knots = np.quantile(x, [0.25, 0.50, 0.75])
        yeni_tr.append(x)
        yeni_ot.append(ot[c].to_numpy(float))
        ad.append(c)
        for i, k in enumerate(knots):
            yeni_tr.append(np.maximum(x - k, 0.0))
            yeni_ot.append(np.maximum(ot[c].to_numpy(float) - k, 0.0))
            ad.append(f"{c}_s{i}")
    return np.column_stack(yeni_tr), np.column_stack(yeni_ot), ad


def kosu_loss(p, start, sizes, win):
    """Her KOSU icin -log p(galip) (bootstrap birimi kosu)."""
    return -np.log(p[win] + 1e-12)


def degerlendir(ad, beta_skor_tr, beta_skor_va, beta_skor_te, va, te):
    """Ortak son adim: alpha/gamma'yi 2024'te fit et, 2025-26'da Bot2 log-loss."""
    stv, szv, winv = race_struct(va)
    pfv = seg_softmax(beta_skor_va, stv, szv)
    pmv = devig(va.ganyan_muhtemel.values, stv, szv)
    alpha, gamma = fit_clogit_w(np.c_[np.log(pfv + 1e-12), np.log(pmv + 1e-12)],
                                stv, szv, winv)
    stt, szt, wint = race_struct(te)
    pft = seg_softmax(beta_skor_te, stt, szt)
    pmt = devig(te.ganyan_muhtemel.values, stt, szt)
    pct = seg_softmax(alpha * np.log(pft + 1e-12) + gamma * np.log(pmt + 1e-12), stt, szt)
    return {
        "ad": ad, "alpha": float(alpha), "gamma": float(gamma),
        "ll1": logloss(pft, stt, szt, wint), "ll2": logloss(pct, stt, szt, wint),
        "kayip": kosu_loss(pct, stt, szt, wint),
    }


# ---------------------------------- ana akis --------------------------------------
def main():
    print("=" * 108)
    print("K128 — BOT1'İN BİÇİMİ / PENCERESİ / HEDEFİ (salt-okunur). Ölçüt betiğin başında ÖN-KAYITLI.")
    print("YENİ ÖZELLİK YOK (K33 kapalı kalıyor). CANLI SİSTEME HİÇBİR DOKUNUŞ YOK.")
    print("=" * 108)

    d = yukle()
    tr0 = d[d.yil <= 2023].sort_values("race_kod").reset_index(drop=True)
    va = prep(d[d.yil == 2024])
    te = prep(d[d.yil >= 2025])
    print(f"  eğitim koşu: {tr0.race_kod.nunique():,} · val(2024): {va.race_kod.nunique():,} "
          f"· test(2025-26): {te.race_kod.nunique():,}")

    # egitim satirlarinin yasi (yil cinsinden, 2023 sonuna gore)
    dt = pd.to_datetime(tr0["tarih"], format="%d/%m/%Y", errors="coerce")
    yas_yil = (pd.Timestamp("2023-12-31") - dt).dt.days.to_numpy(float) / 365.25
    st0, sz0, win0 = race_struct(tr0)
    yas_kosu = yas_yil[st0]

    Xtr, Xva, Xte = tr0[FEAT].values, va[FEAT].values, te[FEAT].values
    sonuc = []

    def dogrusal(ad, X_tr, X_va, X_te, tr_df, w=None):
        s, z, wn = race_struct(tr_df)
        beta = fit_clogit_w(X_tr, s, z, wn, w)
        return degerlendir(ad, None, X_va @ beta, X_te @ beta, va, te)

    # ---- T: taban ----
    sonuc.append(dogrusal("T   taban (mevcut model)", Xtr, Xva, Xte, tr0))

    # ---- A1-A3: ustel zaman agirligi ----
    for ad, h in (("A1  üstel ağırlık, yarı-ömür 1 yıl", 1.0),
                  ("A2  üstel ağırlık, yarı-ömür 2 yıl", 2.0),
                  ("A3  üstel ağırlık, yarı-ömür 3 yıl", 3.0)):
        sonuc.append(dogrusal(ad, Xtr, Xva, Xte, tr0, w=0.5 ** (yas_kosu / h)))

    # ---- A4-A5: kayan pencere ----
    for ad, yillar in (("A4  kayan pencere: 2022-2023", (2022, 2023)),
                       ("A5  kayan pencere: yalnız 2023", (2023,))):
        sub = tr0[tr0.yil.isin(yillar)].sort_values("race_kod").reset_index(drop=True)
        sonuc.append(dogrusal(ad, sub[FEAT].values, Xva, Xte, sub))

    # ---- B1: onceden baglanmis etkilesimler ----
    def etk(df):
        return np.column_stack([df[a].to_numpy(float) * df[b].to_numpy(float)
                                for a, b in ETKILESIM])
    sonuc.append(dogrusal("B1  + 5 etkileşim terimi",
                          np.c_[Xtr, etk(tr0)], np.c_[Xva, etk(va)], np.c_[Xte, etk(te)], tr0))

    # ---- B2: parcali-dogrusal (spline) ----
    Str, Sva, _ = spline_genislet(tr0, va, SUREKLI)
    _, Ste, _ = spline_genislet(tr0, te, SUREKLI)
    ikili = [c for c in FEAT if c not in SUREKLI]
    sonuc.append(dogrusal("B2  spline (13 sürekli x 3 düğüm)",
                          np.c_[Str, tr0[ikili].values],
                          np.c_[Sva, va[ikili].values],
                          np.c_[Ste, te[ikili].values], tr0))

    # ---- B3: gradient boosting (yaris-ici softmax) ----
    print("\n  B3 (gradient boosting) eğitiliyor — M=300 SABİT, seçim yok...", flush=True)
    nbin = 32
    kenar = [np.unique(np.quantile(Xtr[:, j], np.linspace(0, 1, nbin + 1)[1:-1]))
             for j in range(Xtr.shape[1])]
    agaclar, lr, nb = gbm_fit(Xtr, st0, sz0, win0, kenar, M=300, lr=0.05,
                              derinlik=3, nbin=nbin, min_n=200)
    sonuc.append(degerlendir("B3  gradient boosting (derinlik 3, M=300)", None,
                             gbm_skor(agaclar, lr, nb, kenar, Xva),
                             gbm_skor(agaclar, lr, nb, kenar, Xte), va, te))

    # ---- C1: sira-patlatmali (Plackett-Luce) ----
    pl = patlat(tr0, 3, FEAT)
    sp, zp, wp = race_struct(pl)
    beta_pl = fit_clogit_w(pl[FEAT].values, sp, zp, wp)
    sonuc.append(degerlendir("C1  sıra-patlatmalı eğitim (derinlik 3)", None,
                             Xva @ beta_pl, Xte @ beta_pl, va, te))

    # ------------------------------- CAPA ----------------------------------------
    T = sonuc[0]
    print("\n" + "=" * 108)
    print("ÇAPA (madde 1) — taban, model.py'nin bugünkü çıktısını üretiyor mu?")
    print("=" * 108)
    kontrol = [("alpha", T["alpha"], CAPA["alpha"], TOL_A),
               ("gamma", T["gamma"], CAPA["gamma"], TOL_A),
               ("Bot1 OOS", T["ll1"], CAPA["ll1"], TOL_LL),
               ("Bot2 OOS", T["ll2"], CAPA["ll2"], TOL_LL)]
    gecti = True
    for ad, o, b, tol in kontrol:
        ok = abs(o - b) <= tol
        gecti &= ok
        print(f"  {ad:>10}: beklenen {b:+.4f} · ölçülen {o:+.4f} · fark {o-b:+.4f} "
              f"-> {'TUTTU' if ok else 'TUTMADI'}")
    if not gecti:
        print("\n  ÇAPA DÜŞTÜ -> ÖLÇÜM GÜVENİLMEZ. HİÇBİR VARYANT HÜKÜM ALMAZ.")
        return

    # ------------------------------- SONUC TABLOSU --------------------------------
    print("\n" + "=" * 108)
    print(f"SONUÇLAR — hüküm için ÜÇÜ BİRDEN gerekli: alpha↑ · Bot2 log-loss↓ · "
          f"Bonferroni GA (%{100*(1-BONF):.2f}) sıfırın altında")
    print("=" * 108)
    print(f"  {'varyant':>36} {'alpha':>8} {'gamma':>7} {'Bot1 OOS':>9} {'Bot2 OOS':>9} "
          f"{'Δ Bot2':>9} {'Bonferroni GA':>19}  hüküm")
    print("-" * 108)
    kt = T["kayip"]
    n = len(kt)
    lo_q, hi_q = 100 * BONF / 2, 100 * (1 - BONF / 2)
    idx = RNG.integers(0, n, size=(BOOT, n))
    for r in sonuc:
        if r["ad"].startswith("T "):
            print(f"  {r['ad']:>36} {r['alpha']:>+8.3f} {r['gamma']:>+7.3f} "
                  f"{r['ll1']:>9.4f} {r['ll2']:>9.4f} {'—':>9} {'(çapa)':>19}  —")
            continue
        fark = r["kayip"] - kt
        b = fark[idx].mean(axis=1)
        lo, hi = np.percentile(b, lo_q), np.percentile(b, hi_q)
        a_ok = r["alpha"] > T["alpha"]
        l_ok = r["ll2"] < T["ll2"]
        c_ok = hi < 0
        h = "GEÇTİ" if (a_ok and l_ok and c_ok) else "düştü"
        isaret = "".join(("a" if a_ok else "·", "l" if l_ok else "·", "c" if c_ok else "·"))
        print(f"  {r['ad']:>36} {r['alpha']:>+8.3f} {r['gamma']:>+7.3f} "
              f"{r['ll1']:>9.4f} {r['ll2']:>9.4f} {fark.mean():>+9.4f} "
              f"[{lo:>+8.4f},{hi:>+8.4f}]  {h} [{isaret}]")
    print("\n  işaret: a=alpha yükseldi · l=log-loss düştü · c=GA sıfırın altında (üçü de gerekli)")
    print("  Δ Bot2 negatifse varyant daha iyi. Bootstrap: koşu düzeyi, eşleşmiş, "
          f"{BOOT:,} tekrar.")

    gecen = [r for r in sonuc[1:]
             if r["alpha"] > T["alpha"] and r["ll2"] < T["ll2"]]
    print("\n" + "=" * 108)
    if not gecen:
        print("HÜKÜM: hiçbir varyant iki temel şartı (alpha↑ ve log-loss↓) birlikte sağlamadı.")
    else:
        print(f"HÜKÜM: {len(gecen)} varyant iki temel şartı sağladı — "
              "Bonferroni sütunu belirleyicidir (yukarıda).")
    print("BİRLEŞTİRME YAPILMADI (madde 6). CANLIYA HİÇBİR ŞEY ALINMADI (madde 0).")
    print("=" * 108)


if __name__ == "__main__":
    main()
