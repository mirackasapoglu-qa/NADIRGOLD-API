"""Contract bundle'ini uretir: contract/openapi.json

Kaynak-of-truth = backend'in OTORITATIF Customer Service OpenAPI'si
(contract/customer-service-openapi.json) — dogru gateway yollari + gercek DTO'lar.

Bu spec commerce (sepet) uclarini icermez (ayri servis), o yuzden basket
uclari + semalari burada eklenir (Apidog nadir-v2'den alinan, V2 canli metotlariyla:
add=POST, get=GET, update=PUT, delete=DELETE).

Guncelleme: backend spec'i yenilenince customer-service-openapi.json'u degistir,
sepet degisince asagidaki BASKET_* bloklarini guncelle, sonra:

    python contract/build_openapi.py
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
CUSTOMER_SPEC = HERE / "customer-service-openapi.json"
LIVE_BASE_URL = "https://api-v2.nadirgold.dev"

# --- Sepet (commerce) uclari — otoritatif customer spec'te yok --------------
BASKET_PATHS = {
    "/api/v1/basket/add": {
        "post": {
            "operationId": "addToBasket", "summary": "Sepete urun ekle", "tags": ["basket"],
            "requestBody": {"required": True, "content": {"application/json": {
                "schema": {"$ref": "#/components/schemas/AddToBasketDto"},
                "example": {"sku": "ALTIN-GRAM-1", "qty": 1}}}},
            "responses": {
                "200": {"description": "Eklendi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BasketApiResponse"}}}},
                "400": {"description": "Gecersiz istek", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                "401": {"description": "Yetkisiz", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                "422": {"description": "Is kurali", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                "423": {"description": "Kilitli", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
            },
            "security": [{"bearer": []}],
        }
    },
    "/api/v1/basket/get": {
        "get": {
            "operationId": "getBasket", "summary": "Sepeti getir", "tags": ["basket"],
            "parameters": [{"name": "basketHash", "in": "query", "required": False,
                            "schema": {"type": "string"}, "example": "a3f8c2d1e5b9f047"}],
            "responses": {
                "200": {"description": "Sepet", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BasketApiResponse"}}}},
                "400": {"description": "basketHash gerekli", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                "404": {"description": "Bulunamadi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
            },
            "security": [{"bearer": []}],
        }
    },
    "/api/v1/basket/update": {
        "put": {
            "operationId": "updateBasket", "summary": "Sepet miktar guncelle", "tags": ["basket"],
            "requestBody": {"required": True, "content": {"application/json": {
                "schema": {"$ref": "#/components/schemas/UpdateBasketDto"},
                "example": {"basketHash": "a3f8c2d1e5b9f047", "sku": "ALTIN-GRAM-1", "qty": 3}}}},
            "responses": {
                "200": {"description": "Guncellendi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BasketApiResponse"}}}},
                "404": {"description": "Bulunamadi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                "422": {"description": "Is kurali", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
            },
            "security": [{"bearer": []}],
        }
    },
    "/api/v1/basket/delete": {
        "delete": {
            "operationId": "deleteBasket", "summary": "Sepetten urun sil", "tags": ["basket"],
            "requestBody": {"required": True, "content": {"application/json": {
                "schema": {"$ref": "#/components/schemas/DeleteBasketDto"},
                "example": {"basketHash": "a3f8c2d1e5b9f047", "basketId": 1, "sku": ["ALTIN-GRAM-1"]}}}},
            "responses": {
                "200": {"description": "Silindi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BasketApiResponse"}}}},
                "403": {"description": "Yetkisiz", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
                "404": {"description": "Bulunamadi", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}},
            },
            "security": [{"bearer": []}],
        }
    },
}

BASKET_SCHEMAS = {
    "ErrorResponse": {"type": "object", "properties": {
        "statusCode": {"type": "integer"}, "message": {"type": "string"}, "error": {"type": "string"}}},
    "OrderType": {"type": "string", "enum": ["buy", "sell"]},
    "AddToBasketDto": {"type": "object", "required": ["qty"], "properties": {
        "basketHash": {"type": "string"}, "sku": {"type": "string"},
        "qty": {"type": "integer", "minimum": 1},
        "orderType": {"$ref": "#/components/schemas/OrderType"},
        "merchantId": {"type": ["integer", "null"]}}},
    "UpdateBasketDto": {"type": "object", "required": ["sku", "qty"], "properties": {
        "basketHash": {"type": ["string", "null"]}, "sku": {"type": "string"},
        "qty": {"type": "integer", "minimum": 1}}},
    "DeleteBasketDto": {"type": "object", "required": ["basketHash", "basketId", "sku"], "properties": {
        "basketHash": {"type": "string"}, "basketId": {"type": "integer"},
        "sku": {"type": "array", "items": {"type": "string"}, "minItems": 1}}},
    "BasketItemResponseDto": {"type": "object", "properties": {
        "id": {"type": "integer"}, "sku": {"type": "string"}, "qty": {"type": "integer"},
        "name": {"type": ["string", "null"]}, "price": {"type": "string"},
        "priceTotal": {"type": "string"}}},
    "BasketResponseDto": {"type": "object", "properties": {
        "id": {"type": "integer"}, "basketHash": {"type": ["string", "null"]},
        "grandTotal": {"type": "string"}, "itemsQty": {"type": "integer"},
        "items": {"type": "array", "items": {"$ref": "#/components/schemas/BasketItemResponseDto"}}}},
    "BasketApiResponse": {"type": "object", "properties": {
        "success": {"type": "boolean"}, "data": {"$ref": "#/components/schemas/BasketResponseDto"}}},
}


def build():
    spec = json.loads(CUSTOMER_SPEC.read_text(encoding="utf-8"))

    # Canli base URL — Schemathesis -u ile de gecilebilir ama servers'a da yazalim
    spec["servers"] = [{"url": LIVE_BASE_URL, "description": "Canli (V2)"}]

    # Sepet uclarini + semalarini ekle (mevcut customer semalariyla cakismaz)
    spec["paths"].update(BASKET_PATHS)
    spec.setdefault("components", {}).setdefault("schemas", {}).update(BASKET_SCHEMAS)

    out = HERE / "openapi.json"
    out.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    n_paths = len(spec["paths"])
    n_schemas = len(spec["components"]["schemas"])
    print(f"OK -> {out}  ({n_paths} path, {n_schemas} schema)")


if __name__ == "__main__":
    build()
