# Apidog Spec Düzeltme Notu — Yanlış Endpoint Yolları

**Proje:** Nadir Gold müşteri servisi (Apidog `nadir-v2`, id `1310703`)
**Tarih:** 2026-07-07 · **Kanıt ortamı:** `https://api-v2.nadirgold.dev` (canlı gateway, 443)
**Hazırlayan:** QA (test suite ile senkron)

## Özet

Canlı gateway'e karşı yapılan doğrulamada, Apidog spec'indeki **3 endpoint yolu** 404 dönüyor.
Doğru yollar aşağıda. Bu düzeltmeler **yalnızca path'i (endpoint adresini) değiştirir** —
request body, response şeması, örnekler, tag ve `operationId` **aynı kalır**.

Kaynak: `DISCREPANCIES.md` · Testler zaten canlı-doğru yolları kullanıyor (`tests/api/endpoints.py`).

---

## Düzeltilecek 3 yol

| # | Endpoint | ❌ Spec'teki (yanlış) | ✅ Doğru (canlı) | Kanıt |
|---|---|---|---|---|
| 1 | Giriş / Login | `POST /api/v1/auth/login` | `POST /api/v1/customer/login` | spec yolu → 404 "Cannot POST /api/v1/auth/login" |
| 2 | OTP Doğrula | `POST /api/v1/otp/verify` | `POST /api/v1/customer/otp/verify` | spec yolu → 404 |
| 3 | Şifre Sıfırlama | `POST /api/v1/customer/forgotPassword` | `POST /api/v1/customer/forgot-password` | spec yolu → 404 (camelCase → kebab-case) |

> Not: 1 ve 2'de servis prefix'i `customer/` altına giriyor. 3'te aynı servis ama isimlendirme
> `forgotPassword` yerine `forgot-password` (kebab-case).

---

## Apidog'da nasıl uygulanır (adım adım)

Her endpoint için Apidog UI'da:

1. **API Management → nadir-v2 → Default module** altında ilgili endpoint'i aç.
2. Üstteki **path alanını** yukarıdaki "Doğru (canlı)" değeriyle güncelle.
3. Request/Response tanımlarına **dokunma** — sadece path değişiyor.
4. Kaydet.

Değişecek path'ler (metod ve gövde sabit):

```
1. Giriş Yap        : /api/v1/auth/login              →  /api/v1/customer/login
2. OTP Doğrula      : /api/v1/otp/verify              →  /api/v1/customer/otp/verify
3. Şifre Sıfırlama  : /api/v1/customer/forgotPassword →  /api/v1/customer/forgot-password
```

Düzeltme sonrası: **Apidog → Refresh** → test suite `endpoints.py` ile birebir senkron olur
(bu 3 endpoint için `# DOKUMAN FARKI` notları ve `test_password_reset.py` xfail'i kaldırılabilir).

---

## Ek: bu düzeltmeyle çözülmeyen açık maddeler

Bunlar path yeniden adlandırmayla ilgili değil, ayrı takip gerektirir (bkz. `DISCREPANCIES.md`):

- `POST /api/v1/customer/forgotPasswordSet` — canlıda 404; doğru yol belirsiz (gateway
  `/customer/forgot-password/*` → `/auth/forgot-password/*` rewrite yapıyor). Netleşince eklenecek.
- `GET /api/v1/basket/get` · `PUT /basket/update` · `DELETE /basket/delete` — gateway'de 404.
- `POST /api/v1/basket/add` — route var ama commerce servisi **503** (kapalı).
- `DELETE /api/v1/customer/delete` — spec'te tanımlı ama **test kapsamında değil** (ayrı iş).
