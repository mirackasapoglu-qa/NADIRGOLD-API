---
title: Default module
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
code_clipboard: true
highlight_theme: darkula
headingLevel: 2
generator: "@tarslib/widdershins v4.0.30"

---

# Default module

Nadir Gold müşteri servisi — kimlik doğrulama, kayıt, OTP ve iletişim endpoint'leri

Base URLs:

# Authentication

- HTTP Authentication, scheme: bearer<br/>Login veya register sonrası dönen token. APIDog'da login/register çalıştırıldığında otomatik set edilir.

- HTTP Authentication, scheme: bearer<br/>Opsiyonel JWT token. Token gönderilmezse misafir kullanıcı olarak işlem yapılır.

- HTTP Authentication, scheme: bearer

# 1- Customer Service/1. Auth

<a id="opIdlogout"></a>

## POST Çıkış Yap

POST /api/v1/customer/logout

Oturumu sonlandırır. `ng_auth_token` cookie temizlenir. **Bearer token zorunludur.**

> Response Examples

> 200 Response

```json
{
    "success": true,
    "data": {}
}
```

> 401 Response

```json
{
    "success": false,
    "statusCode": 401,
    "message": "Unauthorized"
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Çıkış başarılı|Inline|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Token eksik veya geçersiz|[ErrorResponse](#schemaerrorresponse)|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» success|boolean|false|none||none|
|» data|object|false|none||none|

HTTP Status Code **401**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» statusCode|integer|false|none||none|
|» message|string|false|none||none|
|» error|string|false|none||none|

<a id="opIdpreRegister"></a>

## POST Ön Kayıt

POST /api/v1/customer/pre-register

E-posta adresini doğrular ve kayıt için hash üretir. Bu hash register adımında kullanılır.

> Body Parameters

```json
{
  "email": "ahmet@example.com"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» email|body|string(email)| yes |none|

> Response Examples

> 200 Response

```json
{
    "success": true,
    "data": {
        "hash": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
    }
}
```

> 400 Response

```json
{
    "success": false,
    "statusCode": 400,
    "message": "Bu e-posta adresi zaten kayıtlı"
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Hash başarıyla oluşturuldu|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|E-posta zaten kayıtlı|[ErrorResponse](#schemaerrorresponse)|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» success|boolean|false|none||none|
|» data|object|false|none||none|
|»» hash|string|false|none||none|

HTTP Status Code **400**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» statusCode|integer|false|none||none|
|» message|string|false|none||none|
|» error|string|false|none||none|

<a id="opIdregister"></a>

## POST Kayıt Ol

POST /api/v1/customer/register

Pre-register hash'i ile yeni müşteri kaydı oluşturur. OTP aktifse hash döner, değilse doğrudan token döner.

> Body Parameters

```json
{
  "firstName": "Ahmet",
  "lastName": "Yılmaz",
  "hash": "a1b2c3d4e5f6...",
  "password": "gizli123",
  "passwordConfirmation": "gizli123",
  "phone": "05551234567",
  "identityNumber": "12345678901",
  "birthdate": "1990-01-15",
  "kvkk": true,
  "membership": true,
  "permissionEmail": false,
  "permissionSms": false
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» firstName|body|string| yes |none|
|» lastName|body|string| yes |none|
|» hash|body|string| yes |pre-register adımından dönen hash|
|» password|body|string| yes |none|
|» passwordConfirmation|body|string| yes |none|
|» phone|body|string| yes |+90 veya 0 ile başlayan Türkiye numarası|
|» identityNumber|body|string| yes |11 haneli TC kimlik no|
|» birthdate|body|string(date)| yes |none|
|» kvkk|body|boolean| yes |none|
|» membership|body|boolean| yes |none|
|» permissionEmail|body|boolean| no |none|
|» permissionSms|body|boolean| no |none|

> Response Examples

> Kayıt başarılı \(token\) veya OTP gerekiyor

```json
{
    "success": true,
    "data": {
        "token": "eyJhbGciOiJIUzI1NiJ9...",
        "customer": {
            "customerId": 100045,
            "email": "ahmet@example.com",
            "phone": "+905551234567",
            "gender": null,
            "firstName": "Ahmet",
            "lastName": "Yılmaz",
            "identityNumber": "12345678901",
            "photo": null,
            "birthday": "1990-01-15",
            "emailVerify": 1
        },
        "deviceToken": null,
        "basketMerge": false
    }
}
```

```json
{
    "success": true,
    "data": {
        "requiresOtp": true,
        "hash": "eyJwaG9uZSI6..."
    }
}
```

> 400 Response

```json
{
    "success": false,
    "statusCode": 400,
    "message": "Şifreler eşleşmiyor"
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Kayıt başarılı (token) veya OTP gerekiyor|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Validasyon hatası|[ErrorResponse](#schemaerrorresponse)|

### Responses Data Schema

HTTP Status Code **400**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» statusCode|integer|false|none||none|
|» message|string|false|none||none|
|» error|string|false|none||none|

<a id="opIdlogin"></a>

## POST Giriş Yap

POST /api/v1/auth/login

E-posta ve şifre ile giriş. Başarılı girişte JWT token döner ve `ng_auth_token` cookie set edilir. OTP aktifse hash döner.

> Body Parameters

```json
{
    "email": "ahmet@example.com",
    "password": "gizli123"
  }

```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» email|body|string(email)| yes |none|
|» password|body|string| yes |none|

> Response Examples

> Giriş başarılı veya OTP gerekiyor

```json
{
    "success": true,
    "data": {
        "token": "eyJhbGciOiJIUzI1NiJ9...",
        "customer": {
            "customerId": 100045,
            "email": "ahmet@example.com",
            "phone": "+905551234567",
            "gender": null,
            "firstName": "Ahmet",
            "lastName": "Yılmaz",
            "identityNumber": "12345678901",
            "photo": null,
            "birthday": "1990-01-15",
            "emailVerify": 1
        },
        "deviceToken": null,
        "basketMerge": false
    }
}
```

```json
{
    "success": true,
    "data": {
        "requiresOtp": true,
        "hash": "eyJwaG9uZSI6..."
    }
}
```

> 401 Response

```json
{
    "success": false,
    "statusCode": 401,
    "message": "E-posta veya şifre hatalı"
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Giriş başarılı veya OTP gerekiyor|Inline|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Hatalı kimlik bilgisi|[ErrorResponse](#schemaerrorresponse)|

### Responses Data Schema

HTTP Status Code **401**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» statusCode|integer|false|none||none|
|» message|string|false|none||none|
|» error|string|false|none||none|

# 1- Customer Service/2. Şifre Sıfırlama

<a id="opIdforgotPassword"></a>

## POST Şifre Sıfırlama E-postası Gönder

POST /api/v1/customer/forgotPassword

Kayıtlı e-postaya şifre sıfırlama bağlantısı gönderir. Hesap bulunamasa bile `success: true` döner (enumeration koruması).

> Body Parameters

```json
{
  "email": "ahmet@example.com"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» email|body|string(email)| yes |none|

> Response Examples

> 200 Response

```json
{
    "success": true,
    "data": {
        "success": true
    }
}
```

> 500 Response

```json
{
    "success": false,
    "statusCode": 500,
    "message": "E-posta gönderilemedi"
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|İstek işlendi|[SuccessResponse](#schemasuccessresponse)|
|500|[Internal Server Error](https://tools.ietf.org/html/rfc7231#section-6.6.1)|E-posta gönderilemedi|[ErrorResponse](#schemaerrorresponse)|

<a id="opIdforgotPasswordReset"></a>

## POST Yeni Şifre Belirle

POST /api/v1/customer/forgotPasswordSet

E-posta bağlantısındaki hash ile yeni şifre belirler. Hash 60 dakika geçerlidir.

> Body Parameters

```json
{
  "hash": "abc123...",
  "password": "YeniSifre123",
  "passwordConfirmation": "YeniSifre123"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» hash|body|string| yes |E-postadaki bağlantıdan alınan hash|
|» password|body|string| yes |none|
|» passwordConfirmation|body|string| yes |none|

> Response Examples

> 200 Response

```json
{
    "success": true,
    "data": {
        "success": true
    }
}
```

> Geçersiz token veya şifreler uyuşmuyor

```json
{
    "success": false,
    "statusCode": 400,
    "message": "Şifreler eşleşmiyor"
}
```

```json
{
    "success": false,
    "statusCode": 400,
    "message": "Geçersiz veya süresi dolmuş şifre sıfırlama bağlantısı"
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Şifre başarıyla güncellendi|[SuccessResponse](#schemasuccessresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Geçersiz token veya şifreler uyuşmuyor|[ErrorResponse](#schemaerrorresponse)|

# 1- Customer Service/3. OTP

<a id="opIdotpSend"></a>

## POST OTP Gönder

POST /api/v1/customer/otp

Telefon numarasına SMS ile OTP kodu gönderir. Dönen hash sonraki adımda kullanılır.

> Body Parameters

```json
{
  "phone": "05551234567"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» phone|body|string| yes |+90 veya 0 ile başlayan Türkiye numarası|

> Response Examples

> 200 Response

```json
{
    "success": true,
    "data": {
        "hash": "eyJwaG9uZSI6Iis5MDU1NTEyMzQ1NjciLCJleHBpcmUiOjE4MH0="
    }
}
```

> 400 Response

```json
{
  "statusCode": 400,
  "message": "Hata mesajı",
  "error": "Bad Request"
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|OTP gönderildi|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Geçersiz telefon numarası|[ErrorResponse](#schemaerrorresponse)|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» success|boolean|false|none||none|
|» data|object|false|none||none|
|»» hash|string|false|none||none|

HTTP Status Code **400**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» statusCode|integer|false|none||none|
|» message|string|false|none||none|
|» error|string|false|none||none|

<a id="opIdotpVerify"></a>

## POST OTP Doğrula

POST /api/v1/otp/verify

Hash ve kod ile OTP doğrular. Login/register akışlarında token + müşteri bilgisi döner.

> Body Parameters

```json
{
    "hash": "{{otp_hash}}",
    "verifyCode": "503084"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» hash|body|string| yes |none|
|» verifyCode|body|string| yes |6 haneli SMS kodu|

> Response Examples

> Doğrulama başarılı

```json
{
    "success": true,
    "data": {
        "verified": true,
        "data": {
            "token": "eyJhbGciOiJIUzI1NiJ9...",
            "customer": {
                "customerId": 100045,
                "email": "ahmet@example.com",
                "phone": "+905551234567",
                "gender": null,
                "firstName": "Ahmet",
                "lastName": "Yılmaz",
                "identityNumber": "12345678901",
                "photo": null,
                "birthday": "1990-01-15",
                "emailVerify": 1
            },
            "deviceToken": null,
            "basketMerge": false
        }
    }
}
```

```json
{
    "success": true,
    "data": {
        "verified": true
    }
}
```

> Geçersiz kod veya süresi dolmuş

```json
{
    "success": false,
    "statusCode": 400,
    "message": "Geçersiz doğrulama kodu"
}
```

```json
{
    "success": false,
    "statusCode": 400,
    "message": "OTP süresi dolmuş"
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Doğrulama başarılı|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Geçersiz kod veya süresi dolmuş|[ErrorResponse](#schemaerrorresponse)|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» success|boolean|false|none||none|
|» data|object|false|none||none|
|»» verified|boolean|false|none||none|
|»» data|any|false|none||Login/register akışlarında token+customer, diğerlerinde undefined|

*oneOf*

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|»»» *anonymous*|[LoginResponse](#schemaloginresponse)|false|none||none|
|»»»» success|boolean|false|none||none|
|»»»» data|object|false|none||none|
|»»»»» token|string|false|none||none|
|»»»»» customer|[LoginCustomer](#schemalogincustomer)|false|none||none|
|»»»»»» customerId|integer|false|none||none|
|»»»»»» email|string|false|none||none|
|»»»»»» phone|string|false|none||none|
|»»»»»» gender|string¦null|false|none||none|
|»»»»»» firstName|string|false|none||none|
|»»»»»» lastName|string|false|none||none|
|»»»»»» identityNumber|string¦null|false|none||none|
|»»»»»» photo|string¦null|false|none||none|
|»»»»»» birthday|string¦null|false|none||none|
|»»»»»» emailVerify|integer|false|none||none|
|»»»»» deviceToken|string¦null|false|none||none|
|»»»»» basketMerge|boolean|false|none||none|

*xor*

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|»»» *anonymous*|object|false|none||none|

HTTP Status Code **400**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» statusCode|integer|false|none||none|
|» message|string|false|none||none|
|» error|string|false|none||none|

<a id="opIdotpResend"></a>

## POST OTP Yeniden Gönder

POST /api/v1/customer/otp/resend

Mevcut hash ile yeni OTP kodu gönderir. Yeni hash döner, eskisi geçersiz olur.

> Body Parameters

```json
{
  "hash": "eyJwaG9uZSI6Iis5MDU1NTEyMzQ1NjciLCJleHBpcmUiOjE4MH0="
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» hash|body|string| yes |none|

> Response Examples

> 200 Response

```json
{
    "success": true,
    "data": {
        "hash": "eyJwaG9uZSI6Iis5MDU1NTEyMzQ1NjciLCJleHBpcmUiOjE4MH0="
    }
}
```

> 400 Response

```json
{
    "success": false,
    "statusCode": 400,
    "message": "Geçersiz veya süresi dolmuş OTP"
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Yeni OTP gönderildi|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Geçersiz veya kullanılmış hash|[ErrorResponse](#schemaerrorresponse)|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» success|boolean|false|none||none|
|» data|object|false|none||none|
|»» hash|string|false|none||none|

HTTP Status Code **400**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» statusCode|integer|false|none||none|
|» message|string|false|none||none|
|» error|string|false|none||none|

# 1- Customer Service/4. İletişim

<a id="opIdcontact"></a>

## POST İletişim Formu Gönder

POST /api/v1/customer/contact

Destek ekibine mesaj iletir. Form kaydedilir, e-posta bildirimi gönderilir.

> Body Parameters

```json
{
    "firstName": "ersin1",
    "lastName": "perzeli1",
    "email": "ersinperzeli1@gmail.com",
    "phone": "5394176667",
    "message": "test1",
    "subject": "konu1"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» firstName|body|string| yes |none|
|» lastName|body|string| yes |none|
|» email|body|string(email)| yes |none|
|» phone|body|string| yes |none|
|» subject|body|string| yes |none|
|» message|body|string| yes |none|

> Response Examples

> 200 Response

```json
{
    "success": true,
    "data": {
        "success": true
    }
}
```

> 400 Response

```json
{
  "statusCode": 400,
  "message": "Hata mesajı",
  "error": "Bad Request"
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Form başarıyla gönderildi|[SuccessResponse](#schemasuccessresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Validasyon hatası|[ErrorResponse](#schemaerrorresponse)|

# 1- Customer Service/5. Müşteri Profil

<a id="opIdcontact"></a>

## GET Profil

GET /api/v1/customer/detail

Destek ekibine mesaj iletir. Form kaydedilir, e-posta bildirimi gönderilir.

> Body Parameters

```json
{
  "firstName": "Ahmet",
  "lastName": "Yılmaz",
  "email": "ahmet@example.com",
  "phone": "+905551234567",
  "subject": "Sipariş hakkında",
  "message": "Siparişim ile ilgili bilgi almak istiyorum."
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» firstName|body|string| yes |none|
|» lastName|body|string| yes |none|
|» email|body|string(email)| yes |none|
|» phone|body|string| yes |none|
|» subject|body|string| yes |none|
|» message|body|string| yes |none|

> Response Examples

> 200 Response

```json
{
    "success": true,
    "data": {
        "success": true
    }
}
```

> 400 Response

```json
{
  "statusCode": 400,
  "message": "Hata mesajı",
  "error": "Bad Request"
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Form başarıyla gönderildi|[SuccessResponse](#schemasuccessresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Validasyon hatası|[ErrorResponse](#schemaerrorresponse)|

# 2- Commerce Service

<a id="opIddeleteBasket"></a>

## DELETE Sepetten ürün sil

DELETE /api/v1/basket/delete

Verilen SKU listesini sepetten soft-delete eder. Sepet boşalırsa transfer bilgisi temizlenir.

> Body Parameters

```json
{
    "basketHash": "a3f8c2d1e5b9f047",
    "basketId": 42,
    "sku": [
        "ALTIN-GRAM-1"
    ]
}
```

```json
{
    "basketHash": "a3f8c2d1e5b9f047",
    "basketId": 42,
    "sku": [
        "ALTIN-GRAM-1",
        "GUMUS-GRAM-1"
    ]
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|[DeleteBasketDto](#schemadeletebasketdto)| yes |none|

> Response Examples

> 403 Response

```json
{
    "statusCode": 403,
    "message": "Bu sepete erişim yetkiniz yok",
    "error": "Forbidden"
}
```

> 404 Response

```json
{
    "statusCode": 404,
    "message": "Sepet bulunamadı",
    "error": "Not Found"
}
```

> 200 Response

```json
{
  "success": true,
  "data": {
    "id": 42,
    "basketHash": "a3f8c2d1e5b9f047",
    "grandTotal": "2500.00000000",
    "subtotal": "2500.00000000",
    "subtotalInclTax": "2500.00000000",
    "discountAmount": "0.00000000",
    "shippingFee": "0.00000000",
    "taxAmount": "0.00000000",
    "itemsQty": 2,
    "itemsCount": 1,
    "shippingMethodAlias": null,
    "shippingMethodFeText": null,
    "isSubscribe": 0,
    "paymentMethod": "MpayBankTransfer",
    "orderType": "buy",
    "transferBankId": null,
    "calculatedAmount": null,
    "items": [
      {
        "id": 1,
        "sku": "ALTIN-GRAM-1",
        "qty": 2,
        "name": "Altın Gram",
        "slug": "altin-gram",
        "price": "1250.00000000",
        "priceTotal": "2500.00000000",
        "discountAmount": "0.00000000",
        "orderType": "buy",
        "isSubscribe": 0,
        "calculatedAmount": null,
        "transferBankId": null
      }
    ]
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Ürün(ler) sepetten silindi|[BasketApiResponse](#schemabasketapiresponse)|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|Bu sepete erişim yetkiniz yok|[ErrorResponse](#schemaerrorresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Sepet bulunamadı|[ErrorResponse](#schemaerrorresponse)|

<a id="opIdupdateBasket"></a>

## PUT Sepetteki ürün miktarını güncelle

PUT /api/v1/basket/update

Belirtilen SKU'nun miktarını günceller (arttırma değil, direkt set). Yeni miktar 0 ise ürünü soft-delete eder.

> Body Parameters

```json
{
    "basketHash": "a3f8c2d1e5b9f047",
    "sku": "ALTIN-GRAM-1",
    "qty": 3
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|[UpdateBasketDto](#schemaupdatebasketdto)| yes |none|

> Response Examples

> 404 Response

```json
{
    "statusCode": 404,
    "message": "Ürün sepette bulunamadı",
    "error": "Not Found"
}
```

> 422 Response

```json
{
    "statusCode": 422,
    "message": "Sepet limitini aştınız",
    "error": "Unprocessable Entity"
}
```

> 200 Response

```json
{
  "success": true,
  "data": {
    "id": 42,
    "basketHash": "a3f8c2d1e5b9f047",
    "grandTotal": "2500.00000000",
    "subtotal": "2500.00000000",
    "subtotalInclTax": "2500.00000000",
    "discountAmount": "0.00000000",
    "shippingFee": "0.00000000",
    "taxAmount": "0.00000000",
    "itemsQty": 2,
    "itemsCount": 1,
    "shippingMethodAlias": null,
    "shippingMethodFeText": null,
    "isSubscribe": 0,
    "paymentMethod": "MpayBankTransfer",
    "orderType": "buy",
    "transferBankId": null,
    "calculatedAmount": null,
    "items": [
      {
        "id": 1,
        "sku": "ALTIN-GRAM-1",
        "qty": 2,
        "name": "Altın Gram",
        "slug": "altin-gram",
        "price": "1250.00000000",
        "priceTotal": "2500.00000000",
        "discountAmount": "0.00000000",
        "orderType": "buy",
        "isSubscribe": 0,
        "calculatedAmount": null,
        "transferBankId": null
      }
    ]
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Sepet güncellendi|[BasketApiResponse](#schemabasketapiresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Ürün sepette bulunamadı|[ErrorResponse](#schemaerrorresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|İş kuralı ihlali — sepet limiti aşıldı|[ErrorResponse](#schemaerrorresponse)|

<a id="opIdgetBasket"></a>

## GET Sepeti getir

GET /api/v1/basket/get

Mevcut sepeti getirir, toplamları hesaplar. Misafir için basketHash zorunludur. Kimlik doğrulamalı kullanıcıda basketHash opsiyoneldir.

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|basketHash|query|string| no |Sepet hash (misafir kullanıcılar için zorunlu)|
|createBasket|query|boolean| no |Sepet yoksa oluştur (Lumen uyumu)|
|orderType|query|[OrderType](#schemaordertype)| no |İşlem tipi filtresi|
|code|query|string| no |Ödeme yöntemi kodu — uygulanır ve güncellenir|

#### Enum

|Name|Value|
|---|---|
|orderType|buy|
|orderType|sell|

> Response Examples

> 400 Response

```json
{
    "statusCode": 400,
    "message": "Sepet hash gereklidir",
    "error": "Bad Request"
}
```

> 404 Response

```json
{
    "statusCode": 404,
    "message": "Sepet bulunamadı",
    "error": "Not Found"
}
```

> 200 Response

```json
{
  "success": true,
  "data": {
    "id": 42,
    "basketHash": "a3f8c2d1e5b9f047",
    "grandTotal": "2500.00000000",
    "subtotal": "2500.00000000",
    "subtotalInclTax": "2500.00000000",
    "discountAmount": "0.00000000",
    "shippingFee": "0.00000000",
    "taxAmount": "0.00000000",
    "itemsQty": 2,
    "itemsCount": 1,
    "shippingMethodAlias": null,
    "shippingMethodFeText": null,
    "isSubscribe": 0,
    "paymentMethod": "MpayBankTransfer",
    "orderType": "buy",
    "transferBankId": null,
    "calculatedAmount": null,
    "items": [
      {
        "id": 1,
        "sku": "ALTIN-GRAM-1",
        "qty": 2,
        "name": "Altın Gram",
        "slug": "altin-gram",
        "price": "1250.00000000",
        "priceTotal": "2500.00000000",
        "discountAmount": "0.00000000",
        "orderType": "buy",
        "isSubscribe": 0,
        "calculatedAmount": null,
        "transferBankId": null
      }
    ]
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Sepet getirildi|[BasketApiResponse](#schemabasketapiresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Geçersiz istek — misafir kullanıcı için basketHash gereklidir|[ErrorResponse](#schemaerrorresponse)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Sepet bulunamadı|[ErrorResponse](#schemaerrorresponse)|

<a id="opIdaddToBasket"></a>

## POST Sepete ürün ekle

POST /api/v1/basket/add

Hem misafir (basketHash ile) hem de kimlik doğrulamalı kullanıcılar için çalışır. Yeni sepet oluşturur veya mevcut sepete ekler.

> Body Parameters

```json
{
    "sku": "ALTIN-GRAM-1",
    "qty": 1
}
```

```json
{
    "basketHash": "a3f8c2d1e5b9f047",
    "sku": "ALTIN-GRAM-1",
    "qty": 2
}
```

```json
{
    "sku": "ALTIN-GRAM-1",
    "qty": 1,
    "orderType": "buy"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|[AddToBasketDto](#schemaaddtobasketdto)| yes |none|

> Response Examples

> 400 Response

```json
{
    "statusCode": 400,
    "message": "SKU gereklidir",
    "error": "Bad Request"
}
```

> 422 Response

```json
{
    "statusCode": 422,
    "message": "Sipariş tipi belirtmek için giriş yapmanız gerekiyor",
    "error": "Unprocessable Entity"
}
```

> 423 Response

```json
{
    "statusCode": 423,
    "message": "Sepette ürün varken abonelik durumu değiştirilemez",
    "error": "Locked"
}
```

> 200 Response

```json
{
  "success": true,
  "data": {
    "id": 42,
    "basketHash": "a3f8c2d1e5b9f047",
    "grandTotal": "2500.00000000",
    "subtotal": "2500.00000000",
    "subtotalInclTax": "2500.00000000",
    "discountAmount": "0.00000000",
    "shippingFee": "0.00000000",
    "taxAmount": "0.00000000",
    "itemsQty": 2,
    "itemsCount": 1,
    "shippingMethodAlias": null,
    "shippingMethodFeText": null,
    "isSubscribe": 0,
    "paymentMethod": "MpayBankTransfer",
    "orderType": "buy",
    "transferBankId": null,
    "calculatedAmount": null,
    "items": [
      {
        "id": 1,
        "sku": "ALTIN-GRAM-1",
        "qty": 2,
        "name": "Altın Gram",
        "slug": "altin-gram",
        "price": "1250.00000000",
        "priceTotal": "2500.00000000",
        "discountAmount": "0.00000000",
        "orderType": "buy",
        "isSubscribe": 0,
        "calculatedAmount": null,
        "transferBankId": null
      }
    ]
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Ürün sepete eklendi|[BasketApiResponse](#schemabasketapiresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Geçersiz istek — SKU eksik veya hatalı parametre|[ErrorResponse](#schemaerrorresponse)|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Yetkisiz — geçersiz JWT token|[ErrorResponse](#schemaerrorresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|İş kuralı ihlali — sepet limiti aşıldı veya misafir orderType gönderdi|[ErrorResponse](#schemaerrorresponse)|
|423|[Locked](https://tools.ietf.org/html/rfc2518#section-10.4)|Abonelik durumu değiştirilemez — sepette ürün var|[ErrorResponse](#schemaerrorresponse)|

# Data Schema

<h2 id="tocS_LoginCustomer">LoginCustomer</h2>

<a id="schemalogincustomer"></a>
<a id="schema_LoginCustomer"></a>
<a id="tocSlogincustomer"></a>
<a id="tocslogincustomer"></a>

```json
{
  "customerId": 100045,
  "email": "ahmet@example.com",
  "phone": "+905551234567",
  "gender": null,
  "firstName": "Ahmet",
  "lastName": "Yılmaz",
  "identityNumber": "12345678901",
  "photo": null,
  "birthday": "1990-01-15",
  "emailVerify": 1
}

```

### Attribute

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|customerId|integer|false|none||none|
|email|string|false|none||none|
|phone|string|false|none||none|
|gender|string¦null|false|none||none|
|firstName|string|false|none||none|
|lastName|string|false|none||none|
|identityNumber|string¦null|false|none||none|
|photo|string¦null|false|none||none|
|birthday|string¦null|false|none||none|
|emailVerify|integer|false|none||none|

<h2 id="tocS_LoginResponse">LoginResponse</h2>

<a id="schemaloginresponse"></a>
<a id="schema_LoginResponse"></a>
<a id="tocSloginresponse"></a>
<a id="tocsloginresponse"></a>

```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "customer": {
      "customerId": 100045,
      "email": "ahmet@example.com",
      "phone": "+905551234567",
      "gender": null,
      "firstName": "Ahmet",
      "lastName": "Yılmaz",
      "identityNumber": "12345678901",
      "photo": null,
      "birthday": "1990-01-15",
      "emailVerify": 1
    },
    "deviceToken": null,
    "basketMerge": false
  }
}

```

### Attribute

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|success|boolean|false|none||none|
|data|object|false|none||none|
|» token|string|false|none||none|
|» customer|[LoginCustomer](#schemalogincustomer)|false|none||none|
|» deviceToken|string¦null|false|none||none|
|» basketMerge|boolean|false|none||none|

<h2 id="tocS_OtpRequiredResponse">OtpRequiredResponse</h2>

<a id="schemaotprequiredresponse"></a>
<a id="schema_OtpRequiredResponse"></a>
<a id="tocSotprequiredresponse"></a>
<a id="tocsotprequiredresponse"></a>

```json
{
  "success": true,
  "data": {
    "requiresOtp": true,
    "hash": "eyJwaG9uZSI6Iis5MDU1NTEyMzQ1NjciLCJleHBpcmUiOjE4MH0="
  }
}

```

### Attribute

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|success|boolean|false|none||none|
|data|object|false|none||none|
|» requiresOtp|boolean|false|none||none|
|» hash|string|false|none||none|

<h2 id="tocS_SuccessResponse">SuccessResponse</h2>

<a id="schemasuccessresponse"></a>
<a id="schema_SuccessResponse"></a>
<a id="tocSsuccessresponse"></a>
<a id="tocssuccessresponse"></a>

```json
{
  "success": true,
  "data": {
    "success": true
  }
}

```

### Attribute

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|success|boolean|false|none||none|
|data|object|false|none||none|
|» success|boolean|false|none||none|

<h2 id="tocS_ErrorResponse">ErrorResponse</h2>

<a id="schemaerrorresponse"></a>
<a id="schema_ErrorResponse"></a>
<a id="tocSerrorresponse"></a>
<a id="tocserrorresponse"></a>

```json
{
  "statusCode": 400,
  "message": "Hata mesajı",
  "error": "Bad Request"
}

```

### Attribute

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|statusCode|integer|false|none||none|
|message|string|false|none||none|
|error|string|false|none||none|

<h2 id="tocS_OrderType">OrderType</h2>

<a id="schemaordertype"></a>
<a id="schema_OrderType"></a>
<a id="tocSordertype"></a>
<a id="tocsordertype"></a>

```json
"buy"

```

İşlem tipi

### Attribute

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|*anonymous*|string|false|none||İşlem tipi|

#### Enum

|Name|Value|
|---|---|
|*anonymous*|buy|
|*anonymous*|sell|

<h2 id="tocS_AddToBasketDto">AddToBasketDto</h2>

<a id="schemaaddtobasketdto"></a>
<a id="schema_AddToBasketDto"></a>
<a id="tocSaddtobasketdto"></a>
<a id="tocsaddtobasketdto"></a>

```json
{
  "basketHash": "a3f8c2d1e5b9f047",
  "sku": "ALTIN-GRAM-1",
  "qty": 1,
  "orderType": "buy",
  "merchantId": 1,
  "transferBankId": 3,
  "isSubscribe": false,
  "changeProduct": true
}

```

### Attribute

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|basketHash|string|false|none||Mevcut sepet hash (misafir kullanıcılar için)|
|sku|string|false|none||Ürün SKU kodu|
|qty|integer|true|none||Sepete eklenecek miktar|
|orderType|[OrderType](#schemaordertype)|false|none||İşlem tipi|
|merchantId|integer¦null|false|none||Merchant ID|
|transferBankId|integer¦null|false|none||Transfer banka ID (bank_lists.id)|
|isSubscribe|boolean¦null|false|none||Abonelik ürünü mü?|
|changeProduct|null|false|none||Sepeti temizle ve ürünü değiştir|

oneOf

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|» *anonymous*|boolean|false|none||none|

xor

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|» *anonymous*|string|false|none||none|

<h2 id="tocS_UpdateBasketDto">UpdateBasketDto</h2>

<a id="schemaupdatebasketdto"></a>
<a id="schema_UpdateBasketDto"></a>
<a id="tocSupdatebasketdto"></a>
<a id="tocsupdatebasketdto"></a>

```json
{
  "basketHash": "a3f8c2d1e5b9f047",
  "sku": "ALTIN-GRAM-1",
  "qty": 3,
  "merchantId": 1
}

```

### Attribute

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|basketHash|string¦null|false|none||Sepet hash (misafir kullanıcılar için)|
|sku|string|true|none||Güncellenecek ürün SKU kodu|
|qty|integer|true|none||Yeni miktar (arttırma değil, direkt set)|
|merchantId|integer¦null|false|none||Merchant ID|

<h2 id="tocS_DeleteBasketDto">DeleteBasketDto</h2>

<a id="schemadeletebasketdto"></a>
<a id="schema_DeleteBasketDto"></a>
<a id="tocSdeletebasketdto"></a>
<a id="tocsdeletebasketdto"></a>

```json
{
  "basketHash": "a3f8c2d1e5b9f047",
  "basketId": 42,
  "sku": [
    "ALTIN-GRAM-1",
    "GUMUS-GRAM-1"
  ]
}

```

### Attribute

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|basketHash|string|true|none||Sepet hash|
|basketId|integer|true|none||Sepet ID|
|sku|[string]|true|none||Silinecek SKU listesi|

<h2 id="tocS_BasketItemResponseDto">BasketItemResponseDto</h2>

<a id="schemabasketitemresponsedto"></a>
<a id="schema_BasketItemResponseDto"></a>
<a id="tocSbasketitemresponsedto"></a>
<a id="tocsbasketitemresponsedto"></a>

```json
{
  "id": 1,
  "sku": "ALTIN-GRAM-1",
  "qty": 2,
  "name": "Altın Gram",
  "slug": "altin-gram",
  "price": "1250.00000000",
  "priceTotal": "2500.00000000",
  "discountAmount": "0.00000000",
  "orderType": "buy",
  "isSubscribe": 0,
  "calculatedAmount": null,
  "transferBankId": null
}

```

### Attribute

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|id|integer|false|none||none|
|sku|string|false|none||none|
|qty|integer|false|none||none|
|name|string¦null|false|none||none|
|slug|string¦null|false|none||none|
|price|string|false|none||none|
|priceTotal|string|false|none||none|
|discountAmount|string|false|none||none|
|orderType|string¦null|false|none||none|
|isSubscribe|integer|false|none||none|
|calculatedAmount|string¦null|false|none||none|
|transferBankId|integer¦null|false|none||none|

<h2 id="tocS_BasketResponseDto">BasketResponseDto</h2>

<a id="schemabasketresponsedto"></a>
<a id="schema_BasketResponseDto"></a>
<a id="tocSbasketresponsedto"></a>
<a id="tocsbasketresponsedto"></a>

```json
{
  "id": 42,
  "basketHash": "a3f8c2d1e5b9f047",
  "grandTotal": "2500.00000000",
  "subtotal": "2500.00000000",
  "subtotalInclTax": "2500.00000000",
  "discountAmount": "0.00000000",
  "shippingFee": "0.00000000",
  "taxAmount": "0.00000000",
  "itemsQty": 2,
  "itemsCount": 1,
  "shippingMethodAlias": null,
  "shippingMethodFeText": null,
  "isSubscribe": 0,
  "paymentMethod": "MpayBankTransfer",
  "orderType": "buy",
  "transferBankId": null,
  "calculatedAmount": null,
  "items": [
    {
      "id": 1,
      "sku": "ALTIN-GRAM-1",
      "qty": 2,
      "name": "Altın Gram",
      "slug": "altin-gram",
      "price": "1250.00000000",
      "priceTotal": "2500.00000000",
      "discountAmount": "0.00000000",
      "orderType": "buy",
      "isSubscribe": 0,
      "calculatedAmount": null,
      "transferBankId": null
    }
  ]
}

```

### Attribute

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|id|integer|false|none||none|
|basketHash|string¦null|false|none||none|
|grandTotal|string|false|none||none|
|subtotal|string|false|none||none|
|subtotalInclTax|string|false|none||none|
|discountAmount|string|false|none||none|
|shippingFee|string|false|none||none|
|taxAmount|string|false|none||none|
|itemsQty|integer|false|none||none|
|itemsCount|integer|false|none||none|
|shippingMethodAlias|string¦null|false|none||none|
|shippingMethodFeText|string¦null|false|none||none|
|isSubscribe|integer|false|none||none|
|paymentMethod|string¦null|false|none||none|
|orderType|string¦null|false|none||none|
|transferBankId|integer¦null|false|none||none|
|calculatedAmount|string¦null|false|none||none|
|items|[[BasketItemResponseDto](#schemabasketitemresponsedto)]|false|none||none|

<h2 id="tocS_BasketApiResponse">BasketApiResponse</h2>

<a id="schemabasketapiresponse"></a>
<a id="schema_BasketApiResponse"></a>
<a id="tocSbasketapiresponse"></a>
<a id="tocsbasketapiresponse"></a>

```json
{
  "success": true,
  "data": {
    "id": 42,
    "basketHash": "a3f8c2d1e5b9f047",
    "grandTotal": "2500.00000000",
    "subtotal": "2500.00000000",
    "subtotalInclTax": "2500.00000000",
    "discountAmount": "0.00000000",
    "shippingFee": "0.00000000",
    "taxAmount": "0.00000000",
    "itemsQty": 2,
    "itemsCount": 1,
    "shippingMethodAlias": null,
    "shippingMethodFeText": null,
    "isSubscribe": 0,
    "paymentMethod": "MpayBankTransfer",
    "orderType": "buy",
    "transferBankId": null,
    "calculatedAmount": null,
    "items": [
      {
        "id": 1,
        "sku": "ALTIN-GRAM-1",
        "qty": 2,
        "name": "Altın Gram",
        "slug": "altin-gram",
        "price": "1250.00000000",
        "priceTotal": "2500.00000000",
        "discountAmount": "0.00000000",
        "orderType": "buy",
        "isSubscribe": 0,
        "calculatedAmount": null,
        "transferBankId": null
      }
    ]
  }
}

```

### Attribute

|Name|Type|Required|Restrictions|Title|Description|
|---|---|---|---|---|---|
|success|boolean|false|none||none|
|data|[BasketResponseDto](#schemabasketresponsedto)|false|none||none|

