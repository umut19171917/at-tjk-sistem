# Faz 1a — Piyasa Baz Cizgisi (izinli pistler, 2024-10..12)

Kosu: 1038 | Kosan at-satiri: 9129 | Ort. at/kosu: 8.8

## 1. Kesinti (takeout)
- Overround medyan: 1.342  => kesinti medyan ~%25.5
- Overround ort.: 1.420  | P25/P75: 1.186 / 1.607

## 2. Favori (en dusuk oran)
- Favori kazanma orani: %34.6  (implied beklenti: %34.2)
- 'Her kosuda favoriyi oyna' ROI (kapanis, iyimser): %-28.6
- Favori ort. oran: 2.31 | medyan: 2.20

## 3. Kalibrasyon (de-vig implied olasilik kovalari)
| kova p_norm | n | tahmin% | gercek% | fark |
|---|---|---|---|---|
| (0.0, 0.05] | 3211 | 2.8 | 2.6 | -0.3 |
| (0.05, 0.1] | 2277 | 7.2 | 7.3 | +0.0 |
| (0.1, 0.15] | 1277 | 12.3 | 13.7 | +1.4 |
| (0.15, 0.2] | 800 | 17.4 | 18.0 | +0.6 |
| (0.2, 0.3] | 917 | 24.5 | 21.5 | -3.0 |
| (0.3, 0.5] | 554 | 37.7 | 40.3 | +2.5 |
| (0.5, 1.0] | 93 | 57.1 | 54.8 | -2.2 |

## 4. Favori-uzunsansli sapma (oran bantlari)
ROI = bu banttaki TUM atlari kapanis oraniyla oyna (iyimser ust sinir).
| oran bandi | n | gercek kazanma% | ort.implied% | ROI(kapanis)% |
|---|---|---|---|---|
| 1-2 | 475 | 44.2 | 42.1 | -30.6 |
| 2-3 | 732 | 26.2 | 27.6 | -33.5 |
| 3-5 | 1346 | 18.1 | 18.3 | -28.3 |
| 5-8 | 1504 | 11.4 | 11.3 | -28.5 |
| 8-15 | 1984 | 7.1 | 6.8 | -24.1 |
| 15-30 | 1790 | 3.9 | 3.6 | -22.8 |
| 30+ | 1298 | 0.8 | 1.7 | -61.7 |

_Not: ROI kapanis oranina gore ve iyimser; gercek (erken bahis + price impact) daha kotu._