# Döküman ↔ Canlı API Farkları

Tarih: 2026-07-07 · Canlı ortam: `https://api-v2.nadirgold.dev` (443)
Kaynak döküman: `nadir-v2.md`

Testler kurulurken canlı gateway'e karşı yoklama yapıldı. Aşağıdaki uyuşmazlıklar tespit edildi.

## 🔴 Bağlantı & altyapı

| Konu | Verilen / Beklenen | Gerçek |
|---|---|---|
| Base URL | `https://api-v2.nadirgold.dev:3001` | `:3001` Cloudflare arkasında **proxy'lenmiyor** (timeout). Çalışan adres portsuz: `https://api-v2.nadirgold.dev` (443) |
| Cloudflare bot koruması | — | Varsayılan Python `urllib` User-Agent'ı **banlanıyor** (HTTP 403, error 1010). İstemciye tarayıcı benzeri `User-Agent` header'ı eklendi. |
| **Commerce (sepet) servisi** | Çalışır | **503 "Service unavailable"** — `basket/add` geçerli auth + geçerli SKU ile bile 503. Servis ayakta değil. |

`GET /health` → `{"success":true,"data":{"status":"ok","service":"nadir-gateway"}}` — istekler bir **gateway** üzerinden gidiyor.

## 🟠 Yanlış endpoint yolları (döküman ≠ canlı)

| Endpoint | Dökümandaki yol | Canlı doğru yol | Kanıt |
|---|---|---|---|
| Giriş (login) | `/api/v1/auth/login` | **`/api/v1/customer/login`** | doküman yolu 404 "Cannot POST" |
| OTP doğrula | `/api/v1/otp/verify` | **`/api/v1/customer/otp/verify`** | doküman yolu 404 |
| Şifre sıfırlama | `/api/v1/customer/forgotPassword` | **`/api/v1/customer/forgot-password`** | doküman yolu 404 (camelCase → kebab-case) |

## 🟡 Davranış / status farkları

| Endpoint | Döküman | Canlı | Not |
|---|---|---|---|
| `POST /customer/contact` | 200 | **201 Created** | POST-create semantiği; test 200/201 kabul edecek şekilde güncellendi |
| `POST /basket/add` | Misafir `basketHash` ile eklenebilir | Tokensiz istek **401** | Auth gerektiriyor; misafir akışı doğrulanamadı |
| Hata gövdesi | `{statusCode, message, error}` | Ek olarak `errors.validation: [...]` dizisi de var | Şema toleranslı bırakıldı |

## 🟣 Spec tanım hataları (Apidog `nadir-v2`)

Canlı davranıştan bağımsız, **spec'in kendi içindeki** hatalar (Apidog `read_project_oas` 2026-07-09 çekiminde de mevcut):

| Endpoint | Sorun | Olması gereken |
|---|---|---|
| `GET /api/v1/customer/detail` (Profil) | Operasyon tanımı **`contact`'tan kopyalanmış**: `operationId: "contact"`, açıklama "Destek ekibine mesaj iletir…", GET olmasına rağmen `requestBody` var, örnek gövde `""` | Profil'e ait `operationId` (`customerDetail`), doğru açıklama, `requestBody` **yok**, `SuccessResponse` + `401` |
| Güvenlik şeması adı tutarsız | 3 farklı isim kullanılıyor: `BearerAuth` (login/logout/delete), `bearerAuth` (basket), `bearer` (detail) | Tek bir isimde birleştirilmeli (ör. `BearerAuth`) |

> Not: Contract bundle'ında (`contract/openapi.json`) `detail` operasyonu Profil'e uygun şekilde **düzeltilerek** alındı; kaynak Apidog spec'i hâlâ hatalı.

## ⚪ Bulunamayan / erişilemeyen endpoint'ler

Gateway (443) üzerinde 404 dönüyor:

- `POST /api/v1/customer/forgotPasswordSet` — denenen varyantlar (`/forgot-password/set`, `/reset-password`, `/forgotPasswordReset`) hep 404.
  İpucu: gateway `/customer/forgot-password/*` isteğini `/auth/forgot-password/*` olarak yeniden yazıyor.
- `GET /api/v1/basket/get` · `PUT /api/v1/basket/update` · `DELETE /api/v1/basket/delete` → 404
- `POST /api/v1/basket/add` → **503** (route var ama arkadaki commerce servisi kapalı)

## 🔵 V1 → V2 Dönüşüm Farkları (statik doküman karşılaştırması)

Kaynak: V1 `NadirgoldV1.md` (Apidog export, 235 uç) ↔ V2 `nadir-v2` (16 müşteri ucu). Karşılaştırma **16 örtüşen uç** ile sınırlı; V2 sütunu **canlı/doğrulanmış** yolu gösterir.

> ⚠️ V1 export'unda 16 ucun tamamında `Responses Data Schema` **boş** → yanıt gövdesi alan-alan kıyaslanamadı; karşılaştırma **istek + yol/metot** ile sınırlı.

### 🔴 Yüksek önem — arayüz kıran farklar

| Uç | Eski (V1) | Yeni (V2) | Fark |
|---|---|---|---|
| Login | `POST /customer/login` · `username`+`password` | `POST /customer/login` · **`email`**+`password` | Alan `username`→`email` |
| Sepet getir | `POST /basket/get` · `basket_hash` | **`GET`** `/basket/get` · query `basketHash` | Metot POST→GET + `basket_hash`→`basketHash` |
| Sepet güncelle | `POST /basket/update` | **`PUT`** `/basket/update` | Metot POST→PUT |
| Sepet sil | `POST /basket/delete` | **`DELETE`** `/basket/delete` | Metot POST→DELETE |
| OTP gönder | `POST /customer/sendCode` | `POST /customer/otp` | Yol yeniden adlandırıldı |
| OTP yeniden gönder | `POST /customer/resendCode` | `POST /customer/otp/resend` | Yol yeniden adlandırıldı |
| OTP doğrula | `POST /customer/otpVerify` | `POST /customer/otp/verify` | `otpVerify`→`otp/verify` |
| Şifre sıfırla (iste) | `POST /customer/forgotPassword` · **`phone`** | `POST /customer/forgot-password` · **`email`** | camelCase→kebab **+ tetikleyici telefon→e-posta** |
| İletişim | `POST /customer/contact` · **snake_case** | `POST /customer/contact` · **camelCase** | Alan adları snake→camel |

### 🟠 Orta önem

| Uç | Eski (V1) | Yeni (V2) | Fark |
|---|---|---|---|
| Ön kayıt | `POST /customer/preRegister` | `POST /customer/pre-register` | camelCase→kebab |
| Header'lar | `Device-Type` / `Content-Language` (bazı uçlar zorunlu) | Dokümante değil | V2'de kaldırılmış/opsiyonel |

### 🟢 Değişmemiş
`logout` · `register` · `forgotPasswordSet` · `customer/detail` (GET) · `basket/add` (POST) · `customer/delete` (DELETE) → yol + metot aynı.

### Notlar
- V1'in `login` yolu (`/customer/login`), V2'nin **canlı** yoluyla aynı — ama V2 *Apidog dokümanı* yanlışlıkla `/auth/login` diyor (NSB-5855). V2 dokümanı hem V1'den hem V2-canlıdan geri kalmış.
- V1 iç tutarsızlıkları: `basket/get` → `basket_hash` (snake), diğerleri `basketHash` (camel); `merchantId` Add'te string / Update'te integer; yol prefix'i (`/DOMAIN/`) bazı uçlarda var bazılarında yok.
- **Kapsam:** V2 yalnızca bu 16 müşteri ucunu kapsıyor; V1'deki diğer ~219 uç (adres, banka, KYC, tasarruf, sipariş, LOGO, lojistik…) V2 `nadir-v2` spec'inde yok.

## ✅ Kayıt (register) akışı — kurallar

`register` **OTP kapalı** ve doğrudan token dönüyor → test suite dışarıdan hesap gerektirmeden kendi hesabını yaratıp login/logout/profil'i test edebiliyor. Ancak:

- **Telefon benzersiz olmalı** → "Bu telefon numarası zaten kayıtlı" (400)
- **TC kimlik no algoritmik olarak geçerli olmalı** (checksum) — `tests/utils/factories.py` üretiyor
- `register` başarılı yanıtı **200** (contact'ın aksine 201 değil)
- Kayıt sonrası **logout, Bearer JWT'yi geçersiz kılmıyor** (stateless; sadece cookie temizleniyor)

## ✅ Doğrulanan endpoint'ler (canlı ile birebir)

`pre-register` · `register` · `logout` (401) · `otp` · `otp/resend` · `contact` · `customer/detail` (401) · `basket/add` (401)

## Aksiyon önerileri

1. **Base URL:** `:3001` yerine portsuz adres kullanılmalı (veya `:3001` Cloudflare page-rule ile açılmalı).
2. **Döküman düzeltilmeli:** login / otp-verify / forgot-password yolları + contact 201 status.
3. **forgotPasswordSet ve basket get/update/delete** yolları netleşince `endpoints.py` güncellenip xfail/skip kalkacak.
4. Auth'lı testleri koşmak için **OTP'siz test hesabı** (`TEST_EMAIL`/`TEST_PASSWORD`) gerekiyor.
