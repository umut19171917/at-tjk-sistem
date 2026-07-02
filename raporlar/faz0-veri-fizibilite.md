# Faz 0 — Veri Fizibilite Raporu
*Tarih: 2026-06-29. Durum: Kapı #1 (veri elde edilebilirlik) GEÇTİ.*

## 1. Veri kaynağı: TJK statik JSON
Kimlik doğrulama gerektirmez. `{Ymd}` = tarih (örn. 20260628), `{KEY}` = pist anahtarı.

| Amaç | Endpoint |
|---|---|
| Program indeksi | `ebayi.tjk.org/s/d/program/{Ymd}/yarislar.json` |
| Program tam kart | `ebayi.tjk.org/s/d/program/{Ymd}/full/{KEY}.json` |
| Sonuç indeksi | `ebayi.tjk.org/s/d/sonuclar/{Ymd}/yarislar.json` |
| Sonuç + ödemeler | `ebayi.tjk.org/s/d/sonuclar/{Ymd}/full/{KEY}.json` |
| At kariyer geçmişi (HTML) | `tjk.org/TR/yarissever/Query/ConnectedPage/AtKosuBilgileri?QueryParameter_AtId={id}` |

Arşiv ≥2021 doğrulandı. TR + yabancı pistler aynı formatta.

## 2. Üç veri katmanı (TJK JSON'da hepsi var)
- **Özellikler:** MESAFE, PIST, GRUP, KILO, HANDIKAP, YAS, JOKEY/ANTRENOR/SAHIP (kodlu),
  soyağacı, START, TAKI, SON6/SON20 form, KOSMAZ.
- **Piyasa fiyatı:** Program `GANYAN` (muhtemel) + `AGF1/AGF2`; Sonuç `GANYAN` (kapanış temettüsü).
- **Gerçek ödeme:** GANYAN, PLASE, İKİLİ, SIRALI İKİLİ, ÜÇLÜ, PLASE İKİLİ, SIRALI 5'Lİ, TABELA, ÇİFTE.

## 3. Önemli not
- Kesinti veriden ölçülebilir: Σ(1/GANYAN) − 1 = overround (havuz türü başına).
- Havuz büyüklüğü (toplam TL) şemada YOK → price-impact modellenemiyor (açık).
- Yabancı atların formu seyrek olabilir → yabancı koşular ertelendi.

## 4. Kaynaklar
- https://www.tjk.org/TR/Yarissever/Static/Page/Bahisler
- https://www.mevzuat.gov.tr/anasayfa/MevzuatFihristDetayIframe?MevzuatTur=7&MevzuatNo=14920&MevzuatTertip=5
- https://github.com/SezerFidanci/TJK-API (endpoint keşfi)
- ebayi.tjk.org statik JSON (doğrudan gözlem, 2026-06-29)
