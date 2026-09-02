# -*- coding: utf-8 -*-
"""
duzeltme_haritasi.py — K145 / BEKLEYENLER 22-G: KARAR DÜZELTME GRAFİĞİ. SALT-OKUNUR.

NE İŞE YARAR: 146 kararın hangisi hangisini düzeltti/çürüttü. Projenin epistemik omurgası —
"bu bulguya hâlâ güveniyor muyuz, yoksa üstü çizilmiş mi?" sorusunun tek bakışta cevabı.

NEDEN ELLE KÜRE EDİLDİ: serbest metinden otomatik çıkarım kırılgandır ve **sessizce yanlış
cevap verir**. Bu dersin bedeli aynı gün ödendi: `deney_durum.py`'nin ilk sürümü hızı yanlış
pencereden hesaplayıp #18 için "216 gün" dedi (doğrusu ~93). Kırılgan otomasyon yerine
açık kayıt tercih edildi — liste burada, kaynağıyla birlikte.

TÜR ETİKETLERİ:
  ölçüm    — sayı yanlıştı, düzeltildi (araç/kod hatası)
  varsayım — inanılan bir şey ölçülünce çürüdü
  aşırı    — ifade fazla güçlüydü, geri çekildi
  veri     — veri hattında kusur bulundu
  kapsam   — bulgu doğru ama iddia edilen alandan dar çıktı
"""
from datetime import datetime
from html import escape
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
CIKTI = KOK / "raporlar" / "duzeltme_haritasi.html"

# (düzelten, düzeltilen, tür, ne değişti)
D = [
    ("K130", "K3", "veri",
     "K3 'program feed'inin GANYAN'ı canlı muhtemel orandır' demişti. Ölçüldü: 6 yılın "
     "%100'ünde KAPANIŞ fiyatının kopyası. Backtest'in piyasa terimi iyimser."),
    ("K33", "K19", "kapsam",
     "K19 özellik mühendisliğini açmıştı. 8 test sonunda ön-taahhütle KAPATILDI: hiçbir "
     "kamuya-açık-veri özelliği Bot2'yi oynatmıyor."),
    ("K38", "K38", "ölçüm",
     "`par` tablosunda look-ahead bulundu (eğitim dönemi galip zamanları hız özelliklerine "
     "sızıyordu). Kendi içinde düzeltildi ve etkisi ölçüldü."),
    ("K104", "K93", "varsayım",
     "K93 'ganyan −%25,4, kesinti %25,5 — birebir tuttu' demişti. K104 gerçek ganyan "
     "kesintisini %28,3 ölçtü; eşleşme kısmen tesadüfmüş."),
    ("K107", "K106", "aşırı",
     "K106'daki A0 ifadesi fazla güçlüydü. Güç kapısı eklendi: n=4'te sonuç 4-0 çıksa bile "
     "p=0,125 — test hiçbir sonuçla anlamlı olamaz."),
    ("K110", "K52/K57/K92", "ölçüm",
     "Tam kod incelemesinde ÜÇ ölçüm-etkileyen hata bulundu (birim fiyat, temettü çarpımı, "
     "bayat veri). Backtest ROI'leri yeniden hesaplandı: −%32,3 → −%36,5."),
    ("K120", "K85", "ölçüm",
     "K85'in '5'li/4'lü de oynasaydık' hesabı düzeltildi: 94.293 TL DAHA kaybedilirdi."),
    ("K121", "—", "kapsam",
     "25 Ağu uyarısı 'kod hatası' sanılabilirdi. Teşhis: kod doğru, 15 dk kolu YAPISAL tek "
     "nokta arızası — Altılı postaları %100 çeyrek saatte, pencereye tek geçiş düşüyor."),
    ("K125", "K124", "ölçüm",
     "K124'ün çapası iki kez düştü (+51, +8,7 puan). Yanlılığın rastgele değil ayak sayısıyla "
     "doğrusal olduğu görüldü → kalibre ölçer kuruldu, LOO ile doğrulandı."),
    ("K129", "K74", "varsayım",
     "K74'ün başlık rakamı (AGF payı ≤%2 olan atlar 2,73 kat kazanıyor) 2025-26'da "
     "REPLİKE OLMADI: oran 0,87. K74'ün (1) numaralı tablosu şüpheli işaretlendi."),
    ("K132", "K131", "kapsam",
     "K131 bot1'i bot2'nin dağıtıcı eşikleriyle yarıştırmıştı (kullanıcı yakaladı). "
     "Ölçek-bağımsız açgözlüyle tekrarlandı: handikap gerçekti (−0,27 ayak) ama hüküm değişmedi."),
    ("K132", "K118", "kapsam",
     "K118 bot1_1800'ü emeklilik adayı ilan etmişti. K132 adil kıyasta bot1 puanının bot2'den "
     "anlamlı KÖTÜ olduğunu gösterdi; para üstünlüğü tek 539.029 TL'lik bilete dayanıyor."),
    ("K134", "K125", "varsayım",
     "K125 7'Lİ PLASE ayaklarını 'plase alanlar' saymıştı → %0 doğrulama. Doğrusu İLK 2 + "
     "çıkanlar + ekürie ortakları: doğrulama %26 → %51,4. Pencere (K94) doğruymuş."),
    ("K102", "K102", "varsayım",
     "'Ata özel kulvar tercihi kariyer_galip_oran ile eşdoğrusaldır' tahmini YANLIŞ çıktı — "
     "eşdoğrusal değilmiş, ama yine de eklenmedi (katkı yok)."),
    ("K143", "2 Eyl değerlendirmesi", "aşırı",
     "Değerlendirme 'çokluluk hesaplanmadı, birikmiş güven şişkin' demişti. Ölçüldü: düzeltmeden "
     "düşen bulgulara proje ZATEN dayanmamıştı. İddia GERİ ALINDI."),
    ("K144", "K122", "ölçüm",
     "#11'in kendi notu tetiği 'Ekim ortası' diyordu; ölçüm ~7 Eylül gösterdi. Madde sırası "
     "geldiği hâlde kenarda bekliyordu."),
]

RENK = {"ölçüm": "#0b6b62", "varsayım": "#a63a2b", "aşırı": "#7a5c10",
        "veri": "#3b5bA9", "kapsam": "#5a6673"}


def main():
    print("=" * 100)
    print("K145 / 22-G — KARAR DÜZELTME HARİTASI")
    print("Hangi karar hangisini düzeltti/çürüttü. Elle küre edildi (gerekçe: betik başlığı).")
    print("=" * 100)
    print(f"  {'düzelten':>10} {'düzeltilen':>22} {'tür':>9}  ne değişti")
    print("-" * 100)
    for a, b, t, n in D:
        print(f"  {a:>10} {b:>22} {t:>9}  {n[:58]}")
    print("\n" + "-" * 100)
    from collections import Counter
    c = Counter(t for _, _, t, _ in D)
    print("  tür dağılımı: " + " · ".join(f"{k} {v}" for k, v in c.most_common()))
    print(f"  toplam kayıtlı düzeltme: {len(D)}")

    H = ["<title>Düzeltme Haritası</title>", """<style>
body{font:15px/1.65 system-ui,Segoe UI,Arial;margin:0;background:#f7f8fa;color:#151b23}
.w{max-width:920px;margin:0 auto;padding:34px 24px 64px}
h1{font-size:24px;margin:0 0 4px}
.alt{color:#5a6673;font-size:13.5px;margin:0 0 8px}
.not{background:#fff8e1;border-left:3px solid #d9a520;padding:14px 18px;margin:22px 0;
border-radius:0 3px 3px 0;font-size:13.5px;color:#4a4130}
.k{display:flex;gap:14px;background:#fff;border:1px solid #dde2e8;border-radius:4px;
padding:16px 18px;margin-bottom:10px;align-items:flex-start}
.ok{font-family:ui-monospace,Consolas,monospace;font-size:13px;white-space:nowrap;
padding-top:2px;min-width:150px}
.ok b{color:#151b23} .ok span{color:#8a94a0}
.rz{display:inline-block;padding:2px 9px;border-radius:11px;font-size:11px;font-weight:600;
color:#fff;margin-bottom:6px}
.mt{font-size:14px;color:#3c4753}
.oz{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0 26px}
.oz div{background:#fff;border:1px solid #dde2e8;border-radius:4px;padding:10px 16px;font-size:13px}
.oz b{font-size:19px;display:block;font-variant-numeric:tabular-nums}
</style>"""]
    H.append("<div class=w><h1>Karar düzeltme haritası</h1>")
    H.append(f"<p class=alt>Hangi karar hangisini düzeltti veya çürüttü · {len(D)} kayıt · "
             f"{datetime.now():%d.%m.%Y}</p>")
    H.append("<div class=oz>")
    for k, v in Counter(t for _, _, t, _ in D).most_common():
        H.append(f"<div><b style='color:{RENK[k]}'>{v}</b>{escape(k)}</div>")
    H.append("</div>")
    H.append("<div class=not><b>Bu liste elle küre edildi.</b> Serbest metinden otomatik "
             "çıkarım kırılgandır ve sessizce yanlış cevap verir — bedeli aynı gün ödendi: "
             "<code>deney_durum.py</code>'nin ilk sürümü #18 için '216 gün' dedi, doğrusu ~93'tü. "
             "Kırılgan otomasyon yerine açık kayıt tercih edildi.</div>")
    for a, b, t, n in D:
        ok = (f"<b>{escape(a)}</b> <span>düzeltti</span> <b>{escape(b)}</b>"
              if a != b else f"<b>{escape(a)}</b> <span>kendi içinde</span>")
        H.append(f"<div class=k><div class=ok>{ok}</div><div>"
                 f"<span class=rz style='background:{RENK[t]}'>{escape(t)}</span>"
                 f"<div class=mt>{escape(n)}</div></div></div>")
    H.append("<p class=alt style='margin-top:24px'><code>kod/duzeltme_haritasi.py</code> — "
             "salt-okunur. Yeni bir düzeltme olduğunda <code>D</code> listesine eklenir.</p>")
    H.append("</div>")
    CIKTI.parent.mkdir(exist_ok=True)
    CIKTI.write_text("\n".join(H), encoding="utf-8")
    print(f"\n  yazıldı: {CIKTI}")


if __name__ == "__main__":
    from collections import Counter
    main()
