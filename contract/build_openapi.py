"""Apidog'un split ($ref'li) OAS parcalarini tek, cozulmus bir OpenAPI 3.1
dosyasinda (contract/openapi.json) birlestirir.

Parcalar Apidog MCP `read_project_oas` / `read_project_oas_ref_resources`
ciktisindan alinmistir (proje: nadir-v2, id 1310703). Spec guncellendiginde
MCP'den yeniden cekip bu dosyadaki bloklari tazeleyip tekrar calistirin:

    python contract/build_openapi.py
"""
import json
import pathlib

# --- Path operasyonlari (path -> {method: operation}) ---------------------
PATHS = {
    "/api/v1/customer/delete": r'''{
  "delete": {
    "summary": "Delete (Pasife Alma)",
    "description": "Oturumu sonlandirir. Bearer token zorunludur.",
    "operationId": "customerDelete",
    "tags": ["1. Auth"],
    "responses": {
      "200": {"description": "Basarili", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": "object", "properties": {}}}}}}},
      "401": {"description": "Token eksik/gecersiz", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": [{"BearerAuth": []}]
  }
}''',
    "/api/v1/customer/pre-register": r'''{
  "post": {
    "summary": "On Kayit",
    "operationId": "preRegister",
    "tags": ["1. Auth"],
    "requestBody": {"required": true, "content": {"application/json": {"schema": {"type": "object", "required": ["email"], "properties": {"email": {"type": "string", "format": "email", "example": "ahmet@example.com"}}}, "example": {"email": "qa_contract_probe@example.com"}}}},
    "responses": {
      "200": {"description": "Hash olusturuldu", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": "object", "properties": {"hash": {"type": "string"}}}}}}}},
      "400": {"description": "E-posta zaten kayitli", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": []
  }
}''',
    "/api/v1/customer/register": r'''{
  "post": {
    "summary": "Kayit Ol",
    "operationId": "register",
    "tags": ["1. Auth"],
    "requestBody": {"required": true, "content": {"application/json": {"schema": {"type": "object", "required": ["firstName", "lastName", "hash", "password", "passwordConfirmation", "phone", "identityNumber", "birthdate", "kvkk", "membership"], "properties": {"firstName": {"type": "string"}, "lastName": {"type": "string"}, "hash": {"type": "string"}, "password": {"type": "string"}, "passwordConfirmation": {"type": "string"}, "phone": {"type": "string"}, "identityNumber": {"type": "string"}, "birthdate": {"type": "string", "format": "date"}, "kvkk": {"type": "boolean"}, "membership": {"type": "boolean"}}}, "example": {"firstName": "QA", "lastName": "Probe", "hash": "invalid-contract-probe-hash", "password": "gizli123", "passwordConfirmation": "gizli123", "phone": "05551234567", "identityNumber": "12345678901", "birthdate": "1990-01-15", "kvkk": true, "membership": true}}}},
    "responses": {
      "200": {"description": "Kayit basarili veya OTP gerekiyor", "content": {"application/json": {"schema": {"oneOf": [{"$ref": "#/components/schemas/LoginResponse"}, {"$ref": "#/components/schemas/OtpRequiredResponse"}]}}}},
      "400": {"description": "Validasyon hatasi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": []
  }
}''',
    "/api/v1/auth/login": r'''{
  "post": {
    "summary": "Giris Yap",
    "operationId": "login",
    "tags": ["1. Auth"],
    "requestBody": {"required": true, "content": {"application/json": {"schema": {"type": "object", "required": ["email", "password"], "properties": {"email": {"type": "string", "format": "email"}, "password": {"type": "string"}}}, "example": {"email": "qa_contract_probe@example.com", "password": "definitely-wrong-password"}}}},
    "responses": {
      "200": {"description": "Giris basarili veya OTP gerekiyor", "content": {"application/json": {"schema": {"oneOf": [{"$ref": "#/components/schemas/LoginResponse"}, {"$ref": "#/components/schemas/OtpRequiredResponse"}]}}}},
      "401": {"description": "Hatali kimlik bilgisi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": []
  }
}''',
    "/api/v1/customer/logout": r'''{
  "post": {
    "summary": "Cikis Yap",
    "operationId": "logout",
    "tags": ["1. Auth"],
    "responses": {
      "200": {"description": "Cikis basarili", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": "object", "properties": {}}}}}}},
      "401": {"description": "Token eksik/gecersiz", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": [{"BearerAuth": []}]
  }
}''',
    "/api/v1/customer/forgotPassword": r'''{
  "post": {
    "summary": "Sifre Sifirlama E-postasi Gonder",
    "operationId": "forgotPassword",
    "tags": ["2. Sifre Sifirlama"],
    "requestBody": {"required": true, "content": {"application/json": {"schema": {"type": "object", "required": ["email"], "properties": {"email": {"type": "string", "format": "email"}}}, "example": {"email": "qa_contract_probe@example.com"}}}},
    "responses": {
      "200": {"description": "Istek islendi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SuccessResponse"}}}},
      "500": {"description": "E-posta gonderilemedi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": []
  }
}''',
    "/api/v1/customer/forgotPasswordSet": r'''{
  "post": {
    "summary": "Yeni Sifre Belirle",
    "operationId": "forgotPasswordReset",
    "tags": ["2. Sifre Sifirlama"],
    "requestBody": {"required": true, "content": {"application/json": {"schema": {"type": "object", "required": ["hash", "password", "passwordConfirmation"], "properties": {"hash": {"type": "string"}, "password": {"type": "string"}, "passwordConfirmation": {"type": "string"}}}, "example": {"hash": "invalid-contract-probe-hash", "password": "YeniSifre123", "passwordConfirmation": "YeniSifre123"}}}},
    "responses": {
      "200": {"description": "Sifre guncellendi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SuccessResponse"}}}},
      "400": {"description": "Gecersiz token veya sifreler uyusmuyor", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": []
  }
}''',
    "/api/v1/customer/otp": r'''{
  "post": {
    "summary": "OTP Gonder",
    "operationId": "otpSend",
    "tags": ["3. OTP"],
    "requestBody": {"required": true, "content": {"application/json": {"schema": {"type": "object", "required": ["phone"], "properties": {"phone": {"type": "string"}}}, "example": {"phone": "not-a-valid-phone"}}}},
    "responses": {
      "200": {"description": "OTP gonderildi", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": "object", "properties": {"hash": {"type": "string"}}}}}}}},
      "400": {"description": "Gecersiz telefon", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": []
  }
}''',
    "/api/v1/otp/verify": r'''{
  "post": {
    "summary": "OTP Dogrula",
    "operationId": "otpVerify",
    "tags": ["3. OTP"],
    "requestBody": {"required": true, "content": {"application/json": {"schema": {"type": "object", "required": ["hash", "verifyCode"], "properties": {"hash": {"type": "string"}, "verifyCode": {"type": "string"}}}, "example": {"hash": "invalid-contract-probe-hash", "verifyCode": "000000"}}}},
    "responses": {
      "200": {"description": "Dogrulama basarili", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": "object", "properties": {"verified": {"type": "boolean"}}}}}}}},
      "400": {"description": "Gecersiz kod / suresi dolmus", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": []
  }
}''',
    "/api/v1/customer/otp/resend": r'''{
  "post": {
    "summary": "OTP Yeniden Gonder",
    "operationId": "otpResend",
    "tags": ["3. OTP"],
    "requestBody": {"required": true, "content": {"application/json": {"schema": {"type": "object", "required": ["hash"], "properties": {"hash": {"type": "string"}}}, "example": {"hash": "invalid-contract-probe-hash"}}}},
    "responses": {
      "200": {"description": "Yeni OTP gonderildi", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": "object", "properties": {"hash": {"type": "string"}}}}}}}},
      "400": {"description": "Gecersiz/kullanilmis hash", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": []
  }
}''',
    "/api/v1/customer/contact": r'''{
  "post": {
    "summary": "Iletisim Formu Gonder",
    "operationId": "contact",
    "tags": ["4. Iletisim"],
    "requestBody": {"required": true, "content": {"application/json": {"schema": {"type": "object", "required": ["firstName", "lastName", "email", "phone", "subject", "message"], "properties": {"firstName": {"type": "string"}, "lastName": {"type": "string"}, "email": {"type": "string", "format": "email"}, "phone": {"type": "string"}, "subject": {"type": "string"}, "message": {"type": "string"}}}, "example": {"firstName": "QA", "lastName": "Contract", "email": "qa_contract_probe@example.com", "phone": "5555555555", "subject": "contract-test", "message": "contract test probe"}}}},
    "responses": {
      "200": {"description": "Form gonderildi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SuccessResponse"}}}},
      "400": {"description": "Validasyon hatasi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": []
  }
}''',
    "/api/v1/customer/detail": r'''{
  "get": {
    "summary": "Profil",
    "operationId": "customerDetail",
    "tags": ["5. Profil"],
    "responses": {
      "200": {"description": "Profil", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SuccessResponse"}}}},
      "401": {"description": "Token eksik/gecersiz", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": [{"BearerAuth": []}]
  }
}''',
    "/api/v1/basket/delete": r'''{
  "delete": {
    "summary": "Sepetten urun sil",
    "operationId": "deleteBasket",
    "tags": ["basket"],
    "requestBody": {"required": true, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/DeleteBasketDto"}, "example": {"basketHash": "contract-probe-hash", "basketId": 1, "sku": ["ALTIN-GRAM-1"]}}}},
    "responses": {
      "200": {"description": "Silindi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BasketApiResponse"}}}},
      "403": {"description": "Yetkisiz", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
      "404": {"description": "Sepet bulunamadi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": [{"bearerAuth": []}]
  }
}''',
    "/api/v1/basket/update": r'''{
  "put": {
    "summary": "Sepetteki urun miktarini guncelle",
    "operationId": "updateBasket",
    "tags": ["basket"],
    "requestBody": {"required": true, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UpdateBasketDto"}, "example": {"basketHash": "contract-probe-hash", "sku": "ALTIN-GRAM-1", "qty": 3}}}},
    "responses": {
      "200": {"description": "Guncellendi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BasketApiResponse"}}}},
      "404": {"description": "Urun bulunamadi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
      "422": {"description": "Is kurali ihlali", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": [{"bearerAuth": []}]
  }
}''',
    "/api/v1/basket/get": r'''{
  "get": {
    "summary": "Sepeti getir",
    "operationId": "getBasket",
    "tags": ["basket"],
    "parameters": [
      {"name": "basketHash", "in": "query", "required": false, "schema": {"type": "string"}, "example": "contract-probe-hash"}
    ],
    "responses": {
      "200": {"description": "Sepet getirildi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BasketApiResponse"}}}},
      "400": {"description": "basketHash gerekli", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
      "404": {"description": "Sepet bulunamadi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": [{"bearerAuth": []}]
  }
}''',
    "/api/v1/basket/add": r'''{
  "post": {
    "summary": "Sepete urun ekle",
    "operationId": "addToBasket",
    "tags": ["basket"],
    "requestBody": {"required": true, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AddToBasketDto"}, "example": {"sku": "ALTIN-GRAM-1", "qty": 1}}}},
    "responses": {
      "200": {"description": "Eklendi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BasketApiResponse"}}}},
      "400": {"description": "Gecersiz istek", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
      "401": {"description": "Yetkisiz", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
      "422": {"description": "Is kurali ihlali", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
      "423": {"description": "Kilitli", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
    },
    "security": [{"bearerAuth": []}]
  }
}''',
}

# --- Component schemalari -------------------------------------------------
SCHEMAS = {
    "ApiSuccess": r'''{"type": "object", "properties": {"success": {"type": "boolean"}}}''',
    "LoginCustomer": r'''{"type": "object", "properties": {"customerId": {"type": "integer"}, "email": {"type": "string"}, "phone": {"type": "string"}, "gender": {"type": ["string", "null"]}, "firstName": {"type": "string"}, "lastName": {"type": "string"}, "identityNumber": {"type": ["string", "null"]}, "photo": {"type": ["string", "null"]}, "birthday": {"type": ["string", "null"]}, "emailVerify": {"type": "integer"}}}''',
    "LoginResponse": r'''{"type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": "object", "properties": {"token": {"type": "string"}, "customer": {"$ref": "#/components/schemas/LoginCustomer"}, "deviceToken": {"type": ["string", "null"]}, "basketMerge": {"type": "boolean"}}}}}''',
    "OtpRequiredResponse": r'''{"type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": "object", "properties": {"requiresOtp": {"type": "boolean"}, "hash": {"type": "string"}}}}}''',
    "SuccessResponse": r'''{"type": "object", "properties": {"success": {"type": "boolean"}, "data": {"type": "object", "properties": {"success": {"type": "boolean"}}}}}''',
    "ErrorResponse": r'''{"type": "object", "properties": {"statusCode": {"type": "integer"}, "message": {"type": "string"}, "error": {"type": "string"}}}''',
    "OrderType": r'''{"type": "string", "enum": ["buy", "sell"]}''',
    "AddToBasketDto": r'''{"type": "object", "required": ["qty"], "properties": {"basketHash": {"type": "string"}, "sku": {"type": "string"}, "qty": {"type": "integer", "minimum": 1}, "orderType": {"$ref": "#/components/schemas/OrderType"}, "merchantId": {"type": ["integer", "null"]}, "transferBankId": {"type": ["integer", "null"]}, "isSubscribe": {"type": ["boolean", "null"]}}}''',
    "GetBasketDto": r'''{"type": "object", "properties": {"basketHash": {"type": "string"}, "createBasket": {"type": "boolean"}, "orderType": {"$ref": "#/components/schemas/OrderType"}, "code": {"type": "string"}}}''',
    "UpdateBasketDto": r'''{"type": "object", "required": ["sku", "qty"], "properties": {"basketHash": {"type": ["string", "null"]}, "sku": {"type": "string"}, "qty": {"type": "integer", "minimum": 1}, "merchantId": {"type": ["integer", "null"]}}}''',
    "DeleteBasketDto": r'''{"type": "object", "required": ["basketHash", "basketId", "sku"], "properties": {"basketHash": {"type": "string"}, "basketId": {"type": "integer"}, "sku": {"type": "array", "items": {"type": "string"}, "minItems": 1}}}''',
    "BasketItemResponseDto": r'''{"type": "object", "properties": {"id": {"type": "integer"}, "sku": {"type": "string"}, "qty": {"type": "integer"}, "name": {"type": ["string", "null"]}, "slug": {"type": ["string", "null"]}, "price": {"type": "string"}, "priceTotal": {"type": "string"}, "discountAmount": {"type": "string"}, "orderType": {"type": ["string", "null"]}, "isSubscribe": {"type": "integer"}, "calculatedAmount": {"type": ["string", "null"]}, "transferBankId": {"type": ["integer", "null"]}}}''',
    "BasketResponseDto": r'''{"type": "object", "properties": {"id": {"type": "integer"}, "basketHash": {"type": ["string", "null"]}, "grandTotal": {"type": "string"}, "subtotal": {"type": "string"}, "subtotalInclTax": {"type": "string"}, "discountAmount": {"type": "string"}, "shippingFee": {"type": "string"}, "taxAmount": {"type": "string"}, "itemsQty": {"type": "integer"}, "itemsCount": {"type": "integer"}, "shippingMethodAlias": {"type": ["string", "null"]}, "shippingMethodFeText": {"type": ["string", "null"]}, "isSubscribe": {"type": "integer"}, "paymentMethod": {"type": ["string", "null"]}, "orderType": {"type": ["string", "null"]}, "transferBankId": {"type": ["integer", "null"]}, "calculatedAmount": {"type": ["string", "null"]}, "items": {"type": "array", "items": {"$ref": "#/components/schemas/BasketItemResponseDto"}}}}''',
    "BasketApiResponse": r'''{"type": "object", "properties": {"success": {"type": "boolean"}, "data": {"$ref": "#/components/schemas/BasketResponseDto"}}}''',
}

SECURITY = {
    "BearerAuth": r'''{"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}''',
    "bearerAuth": r'''{"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}''',
    "bearer": r'''{"type": "http", "scheme": "bearer"}''',
}


def build():
    spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "Nadir Gold API — Contract (nadir-v2)",
            "description": "Apidog nadir-v2 spec'inden bundle edilmis contract dosyasi.",
            "version": "1.0.0",
        },
        "servers": [{"url": "https://api-v2.nadirgold.dev"}],
        "paths": {p: json.loads(raw) for p, raw in PATHS.items()},
        "components": {
            "schemas": {n: json.loads(raw) for n, raw in SCHEMAS.items()},
            "securitySchemes": {n: json.loads(raw) for n, raw in SECURITY.items()},
        },
    }
    out = pathlib.Path(__file__).parent / "openapi.json"
    out.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK -> {out}  ({len(spec['paths'])} path, {len(SCHEMAS)} schema)")


if __name__ == "__main__":
    build()
