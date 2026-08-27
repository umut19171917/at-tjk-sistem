# -*- coding: utf-8 -*-
"""
bot1_kupon2.py — K132: K131'in EKSİĞİ KAPATILIYOR — bot1'e KENDİ parametreleri. SALT-OKUNUR.

KULLANICI HAKLI ÇIKTI (27 Ağu): *"sadece bot1 için ölçmedin mi fikrimi, yani kamudan asla
sızıntı olmadan"*. Denetlendi, iki ayrı yer var:

  (1) PUANDA SIZINTI YOK — doğrulandı. `select_scope` yalnız ırk/pist/tek-galip/saha
      filtreler; FEAT'teki 17 özelliğin hiçbiri orandan türemez. bot1 gerçekten oran-kör.
  (2) DAĞITICI AYARLARINDA VAR — K131'in kusuru. `kupon_kur` MUTLAK olasılık eşikleri
      kullanıyor (banker>=0,70 · kapsam>=0,75) ve bunlar BOT2'nin ölçeğine göre seçilmiş.
      bot1'in olasılıkları daha DÜZ -> banker neredeyse hiç tetiklenmez, kapsam için çok at
      gerekir, kupon hep bütçe tavanına çarpıp BUDANIR. Yani K131 bot1'i bot2'nin
      elbisesiyle yarıştırdı. Kullanıcı "YENİ PARAMETRELERLE" demişti; kullanılmadı.

=====================================================================================
ÖN-KAYITLI ÖLÇÜT — SONUÇLAR GÖRÜLMEDEN YAZILDI VE GİT'E MÜHÜRLENDİ
=====================================================================================
0) MUTLAK SINIR: hiçbir dosyaya yazılmaz; canlı yol, config, KUPONLAR değişmez.

1) ADİL DAĞITICI = AÇGÖZLÜ (K65). Gerekçe: `kupon_kur_acgozlu(ayak_atlari, max_kombo)`
   **hiçbir mutlak eşik kullanmaz** — ne banker ne kapsam. Yalnız bütçe dolana dek
   kazanç/bedel oranına göre at ekler. Bu yüzden ÖLÇEK-BAĞIMSIZDIR ve bot1'i de bot2'yi de
   aynı biçimde ele alır. Zaten sistemde mevcut (K65), bu ölçüm için UYDURULMADI.
   **Birincil kıyaslar açgözlü üzerinden yapılır.**

2) AYRICA: `kapsam` dağıtıcısı bot1 için taranır — banker ∈ {0,70 · 0,40 · 0,25},
   kapsam ∈ {0,75 · 0,55 · 0,40}. Bu tarama SONUCU SEÇMEK İÇİN DEĞİL, bot1'in kendi
   elbisesiyle ne yaptığını GÖRMEK içindir; hüküm buradan çıkarsa "en iyi hücreyi seçtim"
   olur (K33 yasağı). Tarama tablosu bilgi olarak basılır, hüküm (3)'ten çıkar.

3) HÜKÜMLER — birincil ölçü AYAK İSABETİ (K122: ROI 6/6 varyansıyla savrulur),
   Bonferroni 0,05/3 -> iki yanlı %98,33 GA, olay-eşleşmiş bootstrap:
     H1 (BİRİNCİL): açgözlüde  S2(bot1+) − S1(bot1)  > 0 ?
                    "bot1'i iyileştirmek, bot1 kuponunu iyileştiriyor mu?"
     H2:            açgözlüde  S1(bot1)  − S0(bot2)  > 0 ?
                    "oran-kör kupon, harman kuponundan iyi mi?" (ADİL dağıtıcıda)
     H3:            kapsam-taramasının EN İYİ bot1 hücresi, açgözlü-bot1'i geçiyor mu?
                    (geçerse: kusur dağıtıcıdaydı; geçmezse: kusur bot1'in kendisinde)
   GEÇER: GA tamamen sıfırın üstünde. PARA İDDİASI ancak ROI GA'sı da sıfırın üstündeyse.

4) SIZINTI BEYANI: S0 (bot2) kamu fiyatı içerir — o zaten harman. S1/S2 **hiçbir oran
   bilgisi içermez**; ne özellikte, ne dağıtıcıda (açgözlüde eşik yok), ne budamada.
   Tek ortak nokta: olay kümesi (`ganyan_muhtemel>1` olan koşular) — bu bir KAPSAM
   filtresidir, puana bilgi taşımaz, ve üç puan için de AYNIDIR.

5) Kapsam: 2025-26 gerçek OOS, izinli pist, K131'in aynı olay kümesi (eşleşmiş kıyas).
=====================================================================================
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from ozellik import load_katilim, build_features, select_scope       # noqa: E402
import altili_backtest as AB                                        # noqa: E402
from bot1_kupon import irk_puanla                                   # noqa: E402

BOOT = 4000
BONF = 0.05 / 3
RNG = np.random.default_rng(20260827)
ADLAR = {"S0": "bot2 (üretim)", "S1": "bot1 (oran-kör)", "S2": "bot1+ (oran-kör, iyileştirilmiş)"}


def main():
    print("=" * 106)
    print("K132 — bot1'e KENDİ parametreleri; ölçek-bağımsız AÇGÖZLÜ dağıtıcıyla adil kıyas.")
    print("Ölçüt betiğin başında ÖN-KAYITLI. Canlıya/kuponlara DOKUNULMAZ.")
    print("=" * 106)

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

    print("  özellikler yeniden kuruluyor (üretim hattının aynısı)...", flush=True)
    d = build_features(load_katilim())
    d["yil"] = d["dt"].dt.year
    puan = {}
    for irk in ("Ingiliz", "Arap"):
        f = select_scope(d, irk=irk)
        f["yil"] = pd.to_datetime(f["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
        puan.update(irk_puanla(f, agf))

    olay = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    olay["yil"] = pd.to_datetime(olay["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    olay = olay[(~olay["sehir"].isin(AB.EXCL)) & (olay["yil"] >= 2025)]
    kayit = []
    for o in olay.to_dict("records"):
        legs = [int(o[f"leg{i+1}"]) for i in range(6)]
        if all(x in puan for x in legs):
            kayit.append((o, legs))
    print(f"  2025-26 olay: {len(kayit):,}")

    def kos(ad, kombo, dagitici, kapsam=None, banker=None):
        mal, get, ayak, alti, gen = [], [], [], 0, []
        for o, legs in kayit:
            pm = {x: list(zip(puan[x]["no"], puan[x][ad])) for x in legs}
            pf = {x: list(zip(puan[x]["no"], puan[x][ad], puan[x]["kazandi"])) for x in legs}
            aa = [pm[x] for x in legs]
            if dagitici == "acgozlu":
                sec = AB.kupon_kur_acgozlu(aa, kombo)
            else:
                sec = AB.kupon_kur(aa, kapsam, kombo, banker)
            nk = int(np.prod([len(s) for s in sec]))
            if nk == 0:
                continue
            birim = AB._birim_fiyat(o.get("sehir"))
            kaz = [[n for n, p, kz in pf[x] if kz == 1][0] for x in legs]
            tut = [kaz[i] in sec[i] for i in range(6)]
            g = 0.0
            if all(tut) and pd.notna(o.get("t6_div")):
                g = float(o["t6_div"]); alti += 1
            mal.append(nk * birim); get.append(g); ayak.append(sum(tut))
            gen.append([len(s) for s in sec])
        return (np.array(mal), np.array(get), np.array(ayak), alti,
                np.array(gen).mean(0) if gen else None)

    S = {}
    print("\n" + "-" * 106)
    print("  AÇGÖZLÜ DAĞITICI (ölçek-bağımsız; eşik YOK, budama YOK) — ADİL KIYAS")
    print("-" * 106)
    print(f"  {'bütçe':>7} {'puan':>34} {'oynanan':>8} {'ort.bedel':>10} {'ayak isb.':>10} "
          f"{'6/6':>5} {'ROI':>9}  ayak genişlikleri")
    for kombo in (96, 900):
        for ad in ("S0", "S1", "S2"):
            m, g, y, a6, gen = kos(ad, kombo, "acgozlu")
            S[(kombo, "acgozlu", ad)] = (m, g, y, a6)
            roi = (g.sum() - m.sum()) / m.sum() * 100
            gs = " ".join(f"{x:.1f}" for x in gen) if gen is not None else ""
            print(f"  {f'K{kombo}':>7} {ADLAR[ad]:>34} {len(m):>8,} {m.mean():>10.0f} "
                  f"{y.mean():>10.3f} {a6:>5} {roi:>+8.1f}%  {gs}")
        print()

    print("-" * 106)
    print("  KAPSAM DAĞITICISI — bot1 için EŞİK TARAMASI (bilgi; hüküm buradan ÇIKMAZ)")
    print("-" * 106)
    print(f"  {'banker':>7} {'kapsam':>7} {'puan':>20} {'ort.bedel':>10} {'ayak isb.':>10} {'6/6':>5}")
    en_iyi = None
    for banker in (0.70, 0.40, 0.25):
        for kapsam in (0.75, 0.55, 0.40):
            for ad in ("S1", "S2"):
                m, g, y, a6, _ = kos(ad, 96, "kapsam", kapsam, banker)
                S[(96, f"k{kapsam}b{banker}", ad)] = (m, g, y, a6)
                print(f"  {banker:>7.2f} {kapsam:>7.2f} {ADLAR[ad][:20]:>20} {m.mean():>10.0f} "
                      f"{y.mean():>10.3f} {a6:>5}")
                if ad == "S1" and (en_iyi is None or y.mean() > en_iyi[1]):
                    en_iyi = (f"k{kapsam}b{banker}", y.mean(), kapsam, banker)
    print(f"\n  bot1'in EN İYİ kapsam hücresi: banker {en_iyi[3]} · kapsam {en_iyi[2]} "
          f"-> ayak {en_iyi[1]:.3f}")

    # -------------------------------- HUKUM -------------------------------------
    lo_q, hi_q = 100 * BONF / 2, 100 * (1 - BONF / 2)

    def kiyas(A, B, etiket):
        ma, ga, ya, _ = A
        mb, gb, yb, _ = B
        n = min(len(ya), len(yb))
        dd = ya[:n] - yb[:n]
        idx = RNG.integers(0, n, size=(BOOT, n))
        bb = dd[idx].mean(1)
        l, h = np.percentile(bb, lo_q), np.percentile(bb, hi_q)
        na, nb = ga[:n] - ma[:n], gb[:n] - mb[:n]
        rb = (na[idx].sum(1) / ma[:n][idx].sum(1) - nb[idx].sum(1) / mb[:n][idx].sum(1)) * 100
        rl, rh = np.percentile(rb, lo_q), np.percentile(rb, hi_q)
        hkm = "GEÇTİ" if l > 0 else "düştü"
        para = " + PARA" if (l > 0 and rl > 0) else ""
        print(f"  {etiket:>44}: ayak {dd.mean():+.4f} GA[{l:+.4f},{h:+.4f}] -> {hkm}{para}"
              f"  | ROI {(na.sum()/ma[:n].sum()-nb.sum()/mb[:n].sum())*100:+.1f} GA[{rl:+.1f},{rh:+.1f}]")

    print("\n" + "=" * 106)
    print(f"HÜKÜM — ayak isabeti birincil · Bonferroni GA %{100*(1-BONF):.2f}")
    print("=" * 106)
    for kombo in (96, 900):
        print(f"\n  --- açgözlü, bütçe K{kombo} ---")
        kiyas(S[(kombo, "acgozlu", "S2")], S[(kombo, "acgozlu", "S1")],
              "H1 BİRİNCİL: bot1+ − bot1")
        kiyas(S[(kombo, "acgozlu", "S1")], S[(kombo, "acgozlu", "S0")],
              "H2: bot1 − bot2 (ADİL dağıtıcı)")
    print("\n  --- H3: dağıtıcı mı suçluydu? ---")
    kiyas(S[(96, en_iyi[0], "S1")], S[(96, "acgozlu", "S1")],
          f"bot1@kapsam({en_iyi[3]},{en_iyi[2]}) − bot1@açgözlü")
    print("\n  CANLIYA HİÇBİR ŞEY ALINMADI. KUPONLARA DOKUNULMADI.")


if __name__ == "__main__":
    main()
