# veri/ klasörü

Ham veri buraya konur. Mevcut: kullanıcının 3 aylık seti (5 CSV, tjk_veri_2024).

## Tablolar
- `katilimlar_real_2024.csv` — asıl tablo (her satır = at-koşu): tarih, sehir, kosu_no,
  kosu_sira (bitiriş), kazanan_mi, at_id (isim+(start)+ekipman metni), at_yas, kilo,
  jokey_id, sahip_id, antrenor_id, derece (zaman), ganyan_orani (oran).
- `yarislar_real.csv` — koşu meta: yaris_id, tarih_dt, sehir, pist/zemin, mesafe, kosu_grubu
  (İngiliz/Arap + yaş), kosu_cinsi (sınıf), ikramiye. (kosu_no=0 → katilimlar join'i kopuk.)
- `atlar_real.csv` — at master: AtIsmi, IrkAdi, soyağacı, güncel sahip/antrenör (SNAPSHOT).
- `jokeyler_real.csv` / `antrenorler_real.csv` — kariyer toplam istatistik (SNAPSHOT, look-ahead).

## Uyarılar
- Veri 3 ay (2024-10..12). Kapsam ve sorunlar: `../raporlar/kapi2-veri-inceleme.md`.
- Entity snapshot tablolarını doğrudan özellik olarak KULLANMA (look-ahead) — point-in-time
  yeniden hesapla.
