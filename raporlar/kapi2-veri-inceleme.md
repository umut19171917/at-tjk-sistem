# Kapı #2 — Eldeki Verinin İncelemesi
*Tarih: 2026-06-29. Kullanıcının 3 aylık seti (tjk_veri_2024).*

## Veri seti: 5 tablo
| Tablo | İçerik | Not |
|---|---|---|
| `katilimlar_real_2024` | Her satır = at-koşu (oran+sonuç+özellik) | **Asıl tablo** |
| `yarislar_real` | Koşu düzeyi (mesafe, zemin, ırk, sınıf) | Join'i kopuk |
| `atlar_real` | At master (ırk, soyağacı, güncel antrenör) | Snapshot |
| `jokeyler_real` / `antrenorler_real` | Kariyer toplam istatistik | Snapshot (look-ahead) |

## Nicel
- `katilimlar`: **2024-10-04 … 2024-12-31 (~3 ay)**, 14.464 satır, 1.602 koşu, ~9,03 at/koşu.
- `yarislar`: 2024-07-01 … 2024-12-31 (6 ay), 3.068 koşu. (Oran/sonuç YOK; sadece meta.)
- İzinli pist (4 şüpheli hariç): **1.041 koşu / 9.340 katılım.**
- İngiliz/Arap (yarislar geneli): 1.702 / 1.366.
- `ganyan_orani` dolu: 14.187/14.464 = **%98,1**.
- **Ganyan kesintisi (ölçülen): medyan overround 1,345 → ~%25,7** (P25/P75: 1,187/1,664).

## A. Olumlu (yapı doğru)
- `ganyan_orani` (piyasa fiyatı / Katman 2) mevcut ve %98 dolu.
- Sonuç: `kosu_sira` (bitiriş), `kazanan_mi`, `derece` (zaman).
- Özellik: `kilo`, `at_yas`, jokey/sahip/antrenör, ve yarislar'da mesafe/zemin/sınıf.
- İngiliz/Arap ayrımı yapılabilir (yarislar.kosu_grubu).

## B. Sorunlar
1. **Miktar yetersiz:** 3 ay, ~600-700 İngiliz+izinli koşu. Model-fit için overfit riski.
   Çözüm: ebayi.tjk.org arşiviyle (≥2021) genişlet.
2. **Kesinti yüksek (~%25,7):** HK'dan (~%17-19) sert → edge marjı dar.
3. **`*_id` kolonları aslında metin** (at_id="MİR BABA(5) KG…", jokey_id="C.PASO AP Apranti").
   Start pozisyonu `(N)` olarak at_id içinde gömülü. Entity join isim normalizasyonu ister.
4. **katilimlar↔yarislar join anahtarı yok** (yarislar.kosu_no=0). Mesafe/zemin/ırk bu join'e
   bağlı → koşu-sırası eşleme veya atlar tablosu üzerinden çözülecek.
5. **Entity tabloları snapshot → look-ahead bias.** Point-in-time rolling istatistik
   katilimlar'dan yeniden hesaplanmalı.
6. `ganyan_orani` muhtemel mi kapanış mı belirsiz (overround 1,345 kapanışa uyumlu) — teyit.
7. Parsing: kilo, at_yas, at_id, tarih formatı (DD/MM/YYYY vs YYYY-MM-DD).
8. Bu sette YOK (ebayi'de VAR): havuz büyüklüğü, SON6, AGF, handikap puanı, temiz start.
9. 277 satır ganyansız (scratch) — normalizasyonda ele al.

## Verdict
- Yapı: ✓ Geçti. Miktar: ⚠ Yetersiz (genişlet). Kalite: ⚠ Temizlik/join işi var ama aşılabilir.
- Özet: **"kavram kanıtı" için doğru, "kâr kanıtı" için yetersiz.**
