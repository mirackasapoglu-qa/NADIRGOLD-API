# NadirGold API Test Suite

Nadir Gold müşteri + ticaret API'si için `pytest` tabanlı API test yapısı.
Kaynak döküman: [`nadir-v2.md`](./nadir-v2.md)

![API Tests](https://github.com/OWNER/REPO/actions/workflows/api-tests.yml/badge.svg)
<!-- ↑ repo push edilince OWNER/REPO yerine gercek yolu yaz -->

## CI (GitHub Actions)

`.github/workflows/api-tests.yml` — canlı API'ye karşı otomatik koşum:

- **push / pull_request** — `tests/`, `schemas/`, `requirements.txt`, `pytest.ini` değişince
- **workflow_dispatch** — manuel; `markers` girdisiyle (`smoke`, `auth` vb.) filtreli koşum
- **schedule** — her gün 06:00 UTC (09:00 TR); commerce servisi/regresyon kontrolü

`report.html` + `junit.xml` her koşumda **artifact** olarak yüklenir (30 gün saklanır).

**Gerekli repo ayarları** (Settings → Secrets and variables → Actions):

| Tip | Ad | Zorunlu | Not |
|---|---|---|---|
| Variable | `BASE_URL` | hayır | Tanımsızsa `https://api-v2.nadirgold.dev` kullanılır |
| Variable | `TEST_SKU` | hayır | Varsayılan `ALTIN-GRAM-1` |
| Secret | `TEST_EMAIL` / `TEST_PASSWORD` | hayır | Verilmezse suite kendi hesabını `register` eder |

> skip/xfail testler build'i kırmaz — yalnızca **gerçek başarısızlık** (failure/error) kırar.

## Kurulum

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # BASE_URL ve test hesabini doldur
```

## Çalıştırma

```bash
pytest                      # tum testler
pytest -m smoke             # kritik akislar
pytest -m negative          # hata senaryolari
pytest -m auth              # kimlik dogrulama testleri
pytest tests/api/test_basket.py   # tek dosya
```

Rapor: `reports/report.html`

## Ortam değişkenleri (`.env`)

| Değişken | Açıklama |
|---|---|
| `BASE_URL` | API kök adresi (`https://api-v2.nadirgold.dev` — **portsuz**, `:3001` çalışmıyor) |
| `TEST_EMAIL` / `TEST_PASSWORD` | **Opsiyonel.** Verilmezse test kendi hesabını `register` ile oluşturur |
| `TEST_SKU` | Geçerli ürün SKU'su (sepet testleri) |
| `UNKNOWN_EMAIL` / `WRONG_PASSWORD` | Negatif senaryolar için |

> **Kendi kendine kayıt:** `register` OTP kapalı ve doğrudan token döndüğü için,
> auth gerektiren testler (login/logout/profil/sepet) dışarıdan hesaba ihtiyaç
> duymaz — `tests/utils/factories.py` her koşuda geçerli TC + benzersiz telefon/email
> üretir, `registered_account` fixture'ı taze hesap açıp token'ı sağlar.

## Kapsam (30 test · canlıya karşı 26 passed / 2 skipped / 2 xfailed)

| Modül | Endpoint'ler |
|---|---|
| `test_auth.py` | login · pre-register · register · logout |
| `test_password_reset.py` | forgotPassword · forgotPasswordSet |
| `test_otp.py` | otp · otp/verify · otp/resend |
| `test_contact.py` | contact |
| `test_profile.py` | customer/detail |
| `test_basket.py` | add · get · update · delete (misafir e2e) |

## Yapı

```
tests/
  conftest.py          # config, misafir + authlı client, auth_token, sema yukleyici
  api/
    endpoints.py       # tum endpoint yollari tek yerde
    test_*.py          # modul basina testler
  utils/assertions.py  # assert_status / assert_schema / assert_response_time
schemas/               # JSON yanit semalari (error, success, login, hash, basket...)
```

## Notlar / bilinen kısıtlar

- **OTP pozitif doğrulama** otomatize edilemez (kod SMS ile telefona gider).
  `test_otp.py` negatif senaryolara ve hash üretimine odaklanır.
- **Commerce (sepet) servisi** şu an canlıda **503** dönüyor → sepet testleri skip.
  Servis ayağa kalkınca otomatik koşacak.
- **forgotPasswordSet** yolu doğrulanamadı (404) → xfail.
- Döküman↔canlı farklarının tam listesi: [`DISCREPANCIES.md`](./DISCREPANCIES.md)
