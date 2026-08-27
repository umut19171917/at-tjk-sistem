# -*- coding: utf-8 -*-
"""
bot1_kupon.py — K131: İYİLEŞTİRİLMİŞ BOT1 ile KUPON. SALT-OKUNUR / OFFLINE.

KULLANICININ SORUSU (27 Ağu): *"testte isabet artışı getiren şeyleri sadece bot1'e yeni
parametrelerle yeni bir kupon türü için neden kullanmayalım?"*

Soru YERİNDE ve daha önce sorulmadı. Gerekçesi şu: K128'in bulduğu α darboğazı **yalnız
HARMANDA** vardır. Bot2 = softmax(α·ln bot1 + γ·ln kamu) ve α=0,19 olduğu için bot1'deki
iyileşmenin ancak ~%12'si çıktıya geçiyor. Ama **saf bot1 kuponunda harman yoktur** →
iyileşmenin %100'ü geçer. Sistemde zaten bot1 tabanlı canlı kollar var (`bot1_900`,
`bot1_1800`) ve ikisi de bot1'in ESKİ (doğrusal) hâlini kullanıyor.

KARŞI ARGÜMAN (önceden yazılıyor, sonuç görülmeden): K129'da AGF, B1/B2'nin **36 KATI**
kalibrasyon kazancı verdi ve kuponda +0,020 ayak/kupon çıktı (sıfırdan ayrılamadı). B1/B2'nin
dozu bunun 1/36'sı. Yani beklenti DÜŞÜK. Ama K129 harman-şekilli bir olasılıkla test edildi;
saf bot1 kuponu farklı ŞEKİLDE bir kupondur (kalabalıktan bilerek sapar) ve bu ayrım
ölçülmemiştir. Bu yüzden ölçmeye değer.

=====================================================================================
ÖN-KAYITLI ÖLÇÜT — SONUÇLAR GÖRÜLMEDEN YAZILDI VE GİT'E MÜHÜRLENDİ (K33/K52)
=====================================================================================
0) MUTLAK SINIR: hiçbir dosyaya YAZILMAZ. `altili_olasilik.py`, `altili_backtest.py`,
   `model.py`, `ozellik.py`, `altili_canli.py`, config'ler, KUPONLAR — hiçbiri değişmez.
   `ozellikli.csv` / `altili_olasilik*.csv` YENİDEN ÜRETİLMEZ. Kazanan çıksa bile canlıya
   ALINMAZ; alma kararı KULLANICININDIR. (Kullanıcı: "mevcut kuponlarımıza dokunmasın".)

1) ÇAPA: bu betiğin yeniden kurduğu bot1/bot2, üretimin `altili_olasilik_bot1.csv`
   değerleriyle örtüşmeli — ortak satırlarda ortalama mutlak fark < 0,001.
   TUTMAZSA ölçüm GÜVENİLMEZ, hiçbir varyant hüküm almaz.

2) DÖRT KUPON PUANI (aynı olay, aynı dağıtıcı, aynı bütçe, gerçek temettü):
     S0  bot2            — üretim tabanı (harman)
     S1  bot1            — mevcut doğrusal, oran-kör (= `bot1_900`'ün kullandığı)
     S2  bot1+           — B1 ∪ B2 BİRLEŞİMİ: 5 etkileşim + 13 sürekli×3 spline düğümü.
                           Bu birleşim BEKLEYENLER #19-A'da önceden bağlanmıştı; başka
                           hiçbir kombinasyon TARANMADI.
     S3  bot1+ ⊕ AGF     — oran-kör model + havuz şekli (ganyan fiyatı YOK). Harman
                           ağırlıkları 2024'te fit.
   YENİ ÖZELLİK YOK (K33 kapalı). Değişen yalnız fonksiyon biçimi ve AGF'nin eklenmesi.

3) ÜÇ ÖNCEDEN BELİRLENMİŞ KIYAS (Bonferroni 0,05/3 -> iki yanlı %98,33 GA):
     BİRİNCİL : S2 − S1   (bot1'i iyileştirmek bot1 kuponunu iyileştiriyor mu?)
                S3 − S1   (AGF eklemek iyileştiriyor mu?)
                S1 − S0   (bot1 kuponu bot2 kuponundan iyi mi? — bağlam)

4) HÜKÜM ÖLÇÜSÜ — **AYAK İSABETİ** birincildir, ROI değil.
   Gerekçe (K122): 6/6 nadirdir, ROI tek bir büyük temettüyle savrulur ve pistleri/varyantları
   kıyaslamaya elverişsizdir. Ayak isabeti düşük varyanslıdır.
     GEÇER : ayak isabeti farkının Bonferroni GA'sı TAMAMEN sıfırın üstünde.
     PARA İDDİASI ancak ek olarak ROI farkının GA'sı da sıfırın üstündeyse yapılır.
     Aksi halde DÜŞTÜ.

5) BÜTÇE EŞİTLİĞİ (K108 dersi): bot1'in olasılıkları bot2'den DAHA DÜZ olduğu için aynı
   kapsam eşiği farklı genişlik demektir. Bu yüzden kıyas **maxKombo tavanında** yapılır
   ve her hücrede ORTALAMA BEDEL basılır; eşit bedel doğrulanabilsin.
   Baş hücreler önceden seçildi: `orta` (kapsam 0,75 · K96) ve `bot1_900` (kapsam 0,75 · K900).

6) Kapsam: 2025-26 gerçek OOS, izinli pist (EXCL), 6 ayağı da puanlanabilen olaylar.
=====================================================================================
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from ozellik import load_katilim, build_features, select_scope, FEAT   # noqa: E402
from model import race_struct, seg_softmax, devig                      # noqa: E402
import altili_backtest as AB                                           # noqa: E402

EPS = 1e-12
BOOT = 4000
BONF = 0.05 / 3
RNG = np.random.default_rng(20260827)

SUREKLI = ["hiz_son_ort_z", "hiz_en_iyi_z", "form_pos_z", "form_fark_z", "kilo_z",
           "handikap_z", "kariyer_galip_oran_z", "zemin_galip_oran_z", "jokey_isabet_z",
           "antrenor_isabet_z", "kulvar_skor_z", "son_yarisdan_gun_z", "yas_z"]
ETKILESIM = [("kilo_z", "mesafe_n"), ("form_pos_z", "son_yarisdan_gun_z"),
             ("jokey_isabet_z", "alan_n"), ("hiz_son_ort_z", "going_n"),
             ("kariyer_galip_oran_z", "yas_z")]


def fit_clogit(X, st, sz, w):
    def f(b):
        p = seg_softmax(X @ b, st, sz)
        return -np.log(p[w] + EPS).sum(), -(X[w].sum(0) - (X * p[:, None]).sum(0))
    return minimize(f, np.zeros(X.shape[1]), jac=True, method="L-BFGS-B").x


def ek_kolonlar(f):
    f = f.copy()
    f["mesafe_n"] = (pd.to_numeric(f["mesafe"], errors="coerce").fillna(1600) - 1600) / 800.0
    f["alan_n"] = (pd.to_numeric(f["alan"], errors="coerce").fillna(9) - 9) / 3.0
    f["going_n"] = pd.to_numeric(f["going_agirlik"], errors="coerce").fillna(0.0)
    return f


def tasarim(f, knots=None):
    """S2'nin tasarim matrisi: 17 FEAT + 5 etkilesim + 13x3 spline tabani."""
    bloklar = [f[FEAT].to_numpy(float)]
    bloklar.append(np.column_stack([f[a].to_numpy(float) * f[b].to_numpy(float)
                                    for a, b in ETKILESIM]))
    if knots is None:
        knots = {c: np.quantile(f[c].to_numpy(float), [0.25, 0.50, 0.75]) for c in SUREKLI}
    sp = []
    for c in SUREKLI:
        x = f[c].to_numpy(float)
        for k in knots[c]:
            sp.append(np.maximum(x - k, 0.0))
    bloklar.append(np.column_stack(sp))
    return np.column_stack(bloklar), knots


def irk_puanla(f, agf):
    """Bir irk icin dort puani uretir. Doner race_kod -> {puan_adi: [(no,p)]} + kazandi."""
    for c in FEAT:
        f[c] = pd.to_numeric(f[c], errors="coerce").fillna(0.0)
    f = ek_kolonlar(f)
    f = f[f["ganyan_muhtemel"] > 1].copy()
    f["agf_p"] = f.set_index(["race_kod", "no"]).index.map(agf)
    tr = f[f.yil <= 2023].sort_values("race_kod").reset_index(drop=True)

    # --- S1: mevcut dogrusal bot1 ---
    beta1 = fit_clogit(tr[FEAT].to_numpy(float), *race_struct(tr))
    # --- S2: bot1+ (etkilesim + spline) ---
    Xtr2, knots = tasarim(tr)
    beta2 = fit_clogit(Xtr2, *race_struct(tr))

    # --- harman katsayilari 2024'te ---
    va = f[f.yil == 2024].copy()
    gw = va.groupby("race_kod")["kazandi"].transform("sum")
    sz = va.groupby("race_kod")["race_kod"].transform("size")
    va = va[(gw == 1) & (sz >= 4)].sort_values("race_kod").reset_index(drop=True)
    stv, szv, winv = race_struct(va)
    p1v = seg_softmax(va[FEAT].to_numpy(float) @ beta1, stv, szv)
    p2v = seg_softmax(tasarim(va, knots)[0] @ beta2, stv, szv)
    pmv = devig(va["ganyan_muhtemel"].to_numpy(float), stv, szv)
    ag, gam = fit_clogit(np.c_[np.log(p1v + EPS), np.log(pmv + EPS)], stv, szv, winv)
    vok = va["agf_p"].notna().to_numpy()
    if vok.sum() > 500:
        va3 = va[vok].copy()
        gw = va3.groupby("race_kod")["kazandi"].transform("sum")
        va3 = va3[gw == 1].sort_values("race_kod").reset_index(drop=True)
        st3, sz3, win3 = race_struct(va3)
        p2v3 = seg_softmax(tasarim(va3, knots)[0] @ beta2, st3, sz3)
        b3 = fit_clogit(np.c_[np.log(p2v3 + EPS),
                              np.log(va3["agf_p"].to_numpy(float) + EPS)], st3, sz3, win3)
    else:
        b3 = None
    print(f"     alpha={ag:+.3f} gamma={gam:+.3f}" +
          (f" | S3: w_bot1+={b3[0]:+.3f} w_AGF={b3[1]:+.3f}" if b3 is not None else " | S3 yok"))

    out = {}
    for rk, g in f.groupby("race_kod", sort=False):
        g = g.sort_values("no")
        st, sz = np.array([0]), np.array([len(g)])
        p1 = seg_softmax(g[FEAT].to_numpy(float) @ beta1, st, sz)
        p2 = seg_softmax(tasarim(g, knots)[0] @ beta2, st, sz)
        pm = devig(g["ganyan_muhtemel"].to_numpy(float), st, sz)
        s0 = seg_softmax(ag * np.log(p1 + EPS) + gam * np.log(pm + EPS), st, sz)
        a = g["agf_p"].to_numpy(float)
        if b3 is not None and np.isfinite(a).all() and a.sum() > 0:
            s3 = seg_softmax(b3[0] * np.log(p2 + EPS) + b3[1] * np.log(a + EPS), st, sz)
        else:
            s3 = None
        nos = g["no"].to_numpy()
        out[int(rk)] = {"no": nos, "S0": s0, "S1": p1, "S2": p2, "S3": s3,
                        "kazandi": g["kazandi"].to_numpy()}
    return out


def main():
    print("=" * 104)
    print("K131 — İYİLEŞTİRİLMİŞ BOT1 ile KUPON (kullanıcı sorusu). SALT-OKUNUR.")
    print("Ölçüt betiğin başında ÖN-KAYITLI. Canlıya/kuponlara DOKUNULMAZ.")
    print("=" * 104)

    ka = pd.read_csv(KOK / "veri" / "katilim.csv",
                     usecols=["race_kod", "no", "agf1", "kosmaz"], low_memory=False)
    ka["agf1"] = pd.to_numeric(ka["agf1"], errors="coerce")
    ka["no"] = pd.to_numeric(ka["no"], errors="coerce")
    ka = ka[~ka["kosmaz"].fillna(False).astype(bool)].dropna(subset=["no"])
    gg = ka.groupby("race_kod").agg(n=("no", "size"), nagf=("agf1", lambda s: s.notna().sum()),
                                    top=("agf1", "sum"))
    iyi = set(gg[(gg.nagf == gg.n) & (gg.top.between(99, 101))].index)
    k2 = ka[ka.race_kod.isin(iyi)].copy()
    k2["agf_p"] = k2["agf1"] / k2.groupby("race_kod")["agf1"].transform("sum")
    agf = dict(zip(zip(k2.race_kod.astype(int), k2.no.astype(int)), k2.agf_p))
    print(f"  AGF'si TAM koşu: {len(iyi):,}")

    print("  özellikler yeniden kuruluyor (üretim hattının aynısı)...", flush=True)
    d = build_features(load_katilim())
    d["yil"] = d["dt"].dt.year
    puan = {}
    for irk in ("Ingiliz", "Arap"):
        f = select_scope(d, irk=irk)
        f["yil"] = pd.to_datetime(f["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
        print(f"   {irk}: {f.race_kod.nunique():,} koşu", flush=True)
        puan.update(irk_puanla(f, agf))
    print(f"  puanlanan koşu: {len(puan):,}")

    # ------------------------------- CAPA -------------------------------------
    ref = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    ref["no"] = pd.to_numeric(ref["no"], errors="coerce")
    fark1, fark2 = [], []
    for rk, g in ref.groupby("race_kod"):
        p = puan.get(int(rk))
        if p is None:
            continue
        m = dict(zip(p["no"], zip(p["S1"], p["S0"])))
        for no, b1, b2 in zip(g["no"], g["bot1"], g["bot2"]):
            if no in m:
                fark1.append(abs(m[no][0] - b1)); fark2.append(abs(m[no][1] - b2))
    f1, f2 = float(np.mean(fark1)), float(np.mean(fark2))
    print(f"\n  ÇAPA — üretimle örtüşme: bot1 ort.|fark| {f1:.5f} · bot2 {f2:.5f} "
          f"(eşik 0,001) -> {'TUTTU' if max(f1, f2) < 0.001 else 'TUTMADI'}")
    if max(f1, f2) >= 0.001:
        print("  ÇAPA DÜŞTÜ -> ÖLÇÜM GÜVENİLMEZ, hiçbir varyant hüküm almaz.")
        return

    # ------------------------------- KUPON ------------------------------------
    olay = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    olay["yil"] = pd.to_datetime(olay["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    olay = olay[(~olay["sehir"].isin(AB.EXCL)) & (olay["yil"] >= 2025)]
    kayit = []
    for o in olay.to_dict("records"):
        legs = [int(o[f"leg{i+1}"]) for i in range(6)]
        if all(x in puan and puan[x]["S3"] is not None for x in legs):
            kayit.append((o, legs))
    print(f"  2025-26 olay (4 puanın 4'ü de hesaplanabilen): {len(kayit):,}")

    def kos(ad, kapsam, kombo):
        mal, get, ayak, alti = [], [], [], 0
        for o, legs in kayit:
            pm = {x: list(zip(puan[x]["no"], puan[x][ad])) for x in legs}
            pf = {x: list(zip(puan[x]["no"], puan[x][ad], puan[x]["kazandi"])) for x in legs}
            r = AB.degerlendir(o, pm, pf, kapsam, kombo, 0.70, kademeli=False)
            if r is None:
                continue
            m, g, a6 = r
            sec = AB.kupon_kur([pm[x] for x in legs], kapsam, kombo, 0.70)
            kaz = [[n for n, p, kz in pf[x] if kz == 1][0] for x in legs]
            mal.append(m); get.append(g); alti += a6
            ayak.append(sum(kaz[i] in sec[i] for i in range(6)))
        return np.array(mal), np.array(get), np.array(ayak), alti

    ADLAR = {"S0": "bot2 (üretim)", "S1": "bot1 (mevcut)",
             "S2": "bot1+ (etkileşim+spline)", "S3": "bot1+ ⊕ AGF"}
    print("\n" + "-" * 104)
    print(f"  {'hücre':>16} {'puan':>26} {'oynanan':>8} {'ort.bedel':>10} "
          f"{'ayak isb.':>10} {'6/6':>5} {'ROI':>9}")
    print("-" * 104)
    S = {}
    for kapsam, kombo in ((0.75, 96), (0.75, 900), (0.90, 288)):
        for ad in ("S0", "S1", "S2", "S3"):
            m, g, y, a6 = kos(ad, kapsam, kombo)
            S[(kapsam, kombo, ad)] = (m, g, y, a6)
            roi = (g.sum() - m.sum()) / m.sum() * 100
            bas = " <-- BAŞ" if (kapsam, kombo) in ((0.75, 96), (0.75, 900)) else ""
            print(f"  {f'kapsam{kapsam}·K{kombo}':>16} {ADLAR[ad]:>26} {len(m):>8,} "
                  f"{m.mean():>10.0f} {y.mean():>10.3f} {a6:>5} {roi:>+8.1f}%{bas}")
        print()

    # ------------------------------- HUKUM ------------------------------------
    print("=" * 104)
    print(f"HÜKÜM — birincil ölçü AYAK İSABETİ (ölçüt 4). Bonferroni GA %{100*(1-BONF):.2f}")
    print("=" * 104)
    lo_q, hi_q = 100 * BONF / 2, 100 * (1 - BONF / 2)
    for kapsam, kombo in ((0.75, 96), (0.75, 900)):
        print(f"\n  --- hücre: kapsam {kapsam} · maxKombo {kombo} ---")
        for a, b, etiket in (("S2", "S1", "BİRİNCİL: bot1+ vs bot1"),
                             ("S3", "S1", "bot1+⊕AGF vs bot1"),
                             ("S1", "S0", "bağlam: bot1 vs bot2")):
            ma, ga, ya, _ = S[(kapsam, kombo, a)]
            mb, gb, yb, _ = S[(kapsam, kombo, b)]
            n = min(len(ya), len(yb))
            d = ya[:n] - yb[:n]
            idx = RNG.integers(0, n, size=(BOOT, n))
            bb = d[idx].mean(1)
            l, h = np.percentile(bb, lo_q), np.percentile(bb, hi_q)
            na, nb = ga[:n] - ma[:n], gb[:n] - mb[:n]
            rb = (na[idx].sum(1) / ma[:n][idx].sum(1) - nb[idx].sum(1) / mb[:n][idx].sum(1)) * 100
            rl, rh = np.percentile(rb, lo_q), np.percentile(rb, hi_q)
            hkm = "GEÇTİ" if l > 0 else "düştü"
            para = " + PARA" if (l > 0 and rl > 0) else ""
            print(f"    {etiket:>26}: ayak {d.mean():+.4f} GA[{l:+.4f},{h:+.4f}] -> {hkm}{para}"
                  f"   | ROI {(na.sum()/ma[:n].sum()-nb.sum()/mb[:n].sum())*100:+.1f} "
                  f"GA[{rl:+.1f},{rh:+.1f}]")
    print("\n  CANLIYA HİÇBİR ŞEY ALINMADI. KUPONLARA DOKUNULMADI (ölçüt 0).")


if __name__ == "__main__":
    main()
