"""Endpoint response yakalama & sema dogrulama & V1<->V2 fark aracı.

Her endpoint icin captures/<metot>_<slug>/ klasoru olusturur:
  request.json          — gonderilen istek (metot, yol, query, body, auth?)
  v2_response.json      — YENI (V2) canli yanit: status, sure, secili header, body
  schema_validation.json— documented DTO response semasina gore PASS/FAIL + hatalar
  v1_v2_diff.md         — eski (V1) <-> yeni (V2) fark notu

Kaynak sema: contract/openapi.json (otoritatif Customer Service DTO'lari + sepet).
Guvenlik: yan-etkili uclar (register/contact/otp/forgot) varsayilan ATLANIR;
CAPTURE_SIDE_EFFECTS=1 ile dahil edilir. Auth icin AUTH_TOKEN env kullanilir.

Kullanim:
    AUTH_TOKEN=<jwt> python contract/capture.py
"""
import os
import re
import json
import copy
import pathlib

import requests
from jsonschema import Draft7Validator

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
SPEC = HERE / "openapi.json"
OUT = ROOT / "captures"
BASE_URL = os.getenv("BASE_URL", "https://api-v2.nadirgold.dev").rstrip("/")
TIMEOUT = int(os.getenv("TIMEOUT", "15"))
TOKEN = os.getenv("AUTH_TOKEN", "")
INCLUDE_SIDE_EFFECTS = os.getenv("CAPTURE_SIDE_EFFECTS") == "1"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Gercek veri ureten / SMS-eposta / oturum-hesap bozan uclar — varsayilan atlanir
SIDE_EFFECT_PATHS = {
    "/api/v1/customer/register",
    "/api/v1/customer/contact",
    "/api/v1/customer/otp",
    "/api/v1/customer/otp/resend",
    "/api/v1/customer/forgot-password",
    "/api/v1/customer/forgot-password-device-token",
    "/api/v1/customer/forgot-password/reset",
    "/api/v1/customer/logout",   # oturumu dusurur (koşum ortasinda token'i bozar)
    "/api/v1/customer/delete",   # hesabi pasife alir
}

# Authorization header'i YALNIZ bu uclara eklenir (digerleri misafir/auth'suz)
AUTH_PATHS = {
    "/api/v1/customer/detail",
    "/api/v1/basket/add",
    "/api/v1/basket/get",
    "/api/v1/basket/update",
    "/api/v1/basket/delete",
}

# Taze token icin login bilgisi (register kacagiyla olusan hesap; env ile ezilebilir)
AUTH_EMAIL = os.getenv("AUTH_EMAIL", "ahmet@example.com")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "gizli123")

# Elimizdeki V1->V2 statik analizinden bilinen farklar (V2 anahtari: "METOT yol")
V1_V2_DIFF = {
    "POST /api/v1/customer/login": "V1 `POST /customer/login` · gövde `username` → V2 **`email`**.",
    "POST /api/v1/customer/pre-register": "V1 `POST /customer/preRegister` (camelCase) → V2 `pre-register` (kebab).",
    "POST /api/v1/customer/register": "V1 `POST /customer/register` — yol aynı.",
    "POST /api/v1/customer/logout": "V1 `POST /customer/logout` — yol aynı.",
    "DELETE /api/v1/customer/delete": "V1 `DELETE /customer/delete` — yol+metot aynı.",
    "POST /api/v1/customer/otp": "V1 `POST /customer/sendCode` → V2 `otp` (yeniden adlandırıldı).",
    "POST /api/v1/customer/otp/verify": "V1 `POST /customer/otpVerify` → V2 `otp/verify`.",
    "POST /api/v1/customer/otp/resend": "V1 `POST /customer/resendCode` → V2 `otp/resend`.",
    "POST /api/v1/customer/forgot-password": "V1 `POST /customer/forgotPassword` · gövde **`phone`** → V2 `forgot-password` · **`email`**.",
    "POST /api/v1/customer/forgot-password/reset": "V1 `POST /customer/forgotPasswordSet` → V2 `forgot-password/reset` (yeni yol).",
    "POST /api/v1/customer/contact": "V1 `POST /customer/contact` · **snake_case** alanlar → V2 **camelCase**.",
    "GET /api/v1/customer/detail": "V1 `GET /customer/detail` — yol aynı. (Not: NSB-5869 tip hatası)",
    "POST /api/v1/basket/add": "V1 `POST /basket/add` — metot aynı.",
    "GET /api/v1/basket/get": "V1 **`POST`** `/basket/get` → V2 **`GET`** + `basket_hash`→`basketHash`.",
    "PUT /api/v1/basket/update": "V1 **`POST`** `/basket/update` → V2 **`PUT`**.",
    "DELETE /api/v1/basket/delete": "V1 **`POST`** `/basket/delete` → V2 **`DELETE`**.",
}
DIFF_UNKNOWN = "V1 karşılığı bu turda analiz edilmedi (V1 canlı kapsam dışı)."

VOLATILE_HEADERS = {"date", "cf-ray", "set-cookie", "server", "report-to",
                    "cf-cache-status", "nel", "expect-ct", "vary", "etag"}


def slug(method, path):
    s = path.replace("/api/v1/", "").strip("/")
    s = re.sub(r"[/{}]", "_", s)
    return f"{method.lower()}_{s}"


def openapi_to_jsonschema(node, components, seen=None):
    """OpenAPI 3.0 semasini jsonschema-uyumlu hale getirir: $ref coz, nullable uygula."""
    seen = seen or set()
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        ref = node["$ref"]
        name = ref.split("/")[-1]
        if name in seen:
            return {}
        target = components.get(name, {})
        return openapi_to_jsonschema(target, components, seen | {name})
    out = {}
    for k, v in node.items():
        if k in ("example", "examples", "description", "nullable"):
            continue
        if k in ("properties",):
            out[k] = {pk: openapi_to_jsonschema(pv, components, seen) for pk, pv in v.items()}
        elif k in ("items",):
            out[k] = openapi_to_jsonschema(v, components, seen)
        elif k in ("oneOf", "anyOf", "allOf"):
            out[k] = [openapi_to_jsonschema(s, components, seen) for s in v]
        else:
            out[k] = v
    if node.get("nullable"):
        t = out.get("type")
        if isinstance(t, str):
            out["type"] = [t, "null"]
        elif isinstance(t, list) and "null" not in t:
            out["type"] = t + ["null"]
    return out


def example_from(media):
    if "example" in media:
        return media["example"]
    exs = media.get("examples")
    if exs:
        first = next(iter(exs.values()))
        return first.get("value")
    return None


def build_request(op, path):
    """Operasyondan istek bileseni cikar: path/query params + body."""
    params = op.get("parameters", [])
    real_path = path
    query = {}
    for p in params:
        ex = p.get("example", (p.get("schema") or {}).get("example"))
        if ex is None:
            continue
        if p["in"] == "path":
            real_path = real_path.replace("{" + p["name"] + "}", str(ex))
        elif p["in"] == "query":
            query[p["name"]] = ex
    body = None
    rb = op.get("requestBody", {}).get("content", {}).get("application/json")
    if rb:
        body = example_from(rb)
    return real_path, query, body


def validate_response(op, status, body, components):
    """Yaniti documented response semasina gore dogrula."""
    responses = op.get("responses", {})
    resp = responses.get(str(status))
    if not resp:
        return {"result": "UNDOCUMENTED_STATUS", "status": status,
                "documented": sorted(responses.keys()), "errors": []}
    media = (resp.get("content") or {}).get("application/json")
    if not media or "schema" not in media:
        return {"result": "NO_SCHEMA", "status": status, "errors": []}
    schema = openapi_to_jsonschema(media["schema"], components)
    errors = []
    for e in Draft7Validator(schema).iter_errors(body):
        errors.append({"path": list(e.absolute_path), "message": e.message})
    return {"result": "PASS" if not errors else "FAIL", "status": status,
            "error_count": len(errors), "errors": errors[:20]}


def main():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    components = spec.get("components", {}).get("schemas", {})
    OUT.mkdir(exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    # Taze token: AUTH_TOKEN env verilmediyse login ile al (auth-gated uclar icin)
    token = TOKEN
    if not token and AUTH_EMAIL and AUTH_PASSWORD:
        try:
            lr = session.post(f"{BASE_URL}/api/v1/customer/login",
                              json={"email": AUTH_EMAIL, "password": AUTH_PASSWORD},
                              timeout=TIMEOUT)
            token = (lr.json().get("data") or {}).get("token", "") if lr.ok else ""
            print(f"[auth] login {lr.status_code} · token: {'alindi' if token else 'YOK'}")
        except Exception as e:
            print(f"[auth] login hata: {e}")
    # Token-login'in biraktigi oturum cookie'sini temizle (yoksa capture'daki login
    # 'zaten girisli' sayilip 400 doner). Auth artik yalniz header ile tasinir.
    session.cookies.clear()

    summary = []
    for path, ops in spec["paths"].items():
        for method, op in ops.items():
            if method not in ("get", "post", "put", "delete", "patch"):
                continue
            key = f"{method.upper()} {path}"
            folder = OUT / slug(method, path)
            folder.mkdir(exist_ok=True)
            diff = V1_V2_DIFF.get(key, DIFF_UNKNOWN)
            (folder / "v1_v2_diff.md").write_text(
                f"# {key}\n\n## Eski (V1) ↔ Yeni (V2) fark\n\n{diff}\n", encoding="utf-8")

            real_path, query, body = build_request(op, path)
            use_auth = path in AUTH_PATHS and bool(token)
            req_headers = {"Authorization": f"Bearer {token}"} if use_auth else {}
            req_record = {"method": method.upper(), "path": real_path,
                          "query": query, "body": body,
                          "auth": use_auth}
            (folder / "request.json").write_text(
                json.dumps(req_record, indent=2, ensure_ascii=False), encoding="utf-8")

            if path in SIDE_EFFECT_PATHS and not INCLUDE_SIDE_EFFECTS:
                (folder / "v2_response.json").write_text(json.dumps(
                    {"skipped": "yan-etki riski — CAPTURE_SIDE_EFFECTS=1 ile yakalanır"},
                    indent=2, ensure_ascii=False), encoding="utf-8")
                summary.append((key, "SKIP", "yan-etki", diff))
                continue

            try:
                r = session.request(method.upper(), f"{BASE_URL}{real_path}",
                                    params=query or None,
                                    json=body if body is not None else None,
                                    headers=req_headers or None,
                                    timeout=TIMEOUT)
            except Exception as e:
                (folder / "v2_response.json").write_text(json.dumps(
                    {"error": f"{type(e).__name__}: {e}"}, indent=2), encoding="utf-8")
                summary.append((key, "ERR", type(e).__name__, diff))
                continue

            try:
                rbody = r.json()
            except ValueError:
                rbody = r.text[:2000]
            headers = {k: v for k, v in r.headers.items()
                       if k.lower() not in VOLATILE_HEADERS}
            (folder / "v2_response.json").write_text(json.dumps({
                "status": r.status_code,
                "elapsed_ms": round(r.elapsed.total_seconds() * 1000),
                "headers": headers, "body": rbody,
            }, indent=2, ensure_ascii=False), encoding="utf-8")

            val = validate_response(op, r.status_code, rbody, components)
            (folder / "schema_validation.json").write_text(
                json.dumps(val, indent=2, ensure_ascii=False), encoding="utf-8")
            summary.append((key, str(r.status_code), val["result"], diff))

    # Ozet
    lines = ["# Capture Özeti", "",
             f"Ortam: `{BASE_URL}` · auth: {'evet' if TOKEN else 'hayır'} · "
             f"yan-etki: {'dahil' if INCLUDE_SIDE_EFFECTS else 'atlandı'}", "",
             "| Endpoint | Status | Şema | V1↔V2 farkı |", "|---|---|---|---|"]
    for key, st, res, diff in summary:
        short = diff if len(diff) < 70 else diff[:67] + "…"
        lines.append(f"| `{key}` | {st} | {res} | {short} |")
    (OUT / "_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK -> {OUT}  ({len(summary)} endpoint)")
    for key, st, res, _ in summary:
        print(f"  {st:>4} {res:20} {key}")


if __name__ == "__main__":
    main()
