#!/usr/bin/env bash
#
# Contract testi — canli API'yi Apidog nadir-v2 sozlesmesine karsi dogrular.
# Schemathesis "examples" fazi: her endpoint icin sadece dokumante edilen ornek
# istek gonderilir (fuzzing YOK), yanit status/schema/content-type sozlesmeye
# uyuyor mu diye kontrol edilir.
#
# Kullanim:
#   ./contract/run.sh                      # guvenli varsayilan (yan etkili endpointler haric)
#   INCLUDE_SIDE_EFFECTS=1 ./contract/run.sh   # contact/otp/forgotPassword dahil
#   AUTH_TOKEN=<jwt> ./contract/run.sh     # auth gerektiren endpointler icin Bearer token
#
set -euo pipefail
cd "$(dirname "$0")/.."

# .env'den BASE_URL (yoksa canli portsuz adres)
if [ -f .env ]; then set -a; . ./.env; set +a; fi
BASE_URL="${BASE_URL:-https://api-v2.nadirgold.dev}"

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

ARGS=(
  contract/openapi.json
  -u "$BASE_URL"
  --phases examples
  -c status_code_conformance,content_type_conformance,response_schema_conformance,not_a_server_error
  -H "User-Agent: $UA"
  --max-response-time 15
  --report junit
  --report-junit-path reports/contract-junit.xml
)

# Auth token verilirse auth-gated endpointler de gercek yanit dondurebilir.
if [ -n "${AUTH_TOKEN:-}" ]; then
  ARGS+=( -H "Authorization: Bearer $AUTH_TOKEN" )
fi

# Yan etkili (kayit/SMS/e-posta ureten) endpointler varsayilan olarak haric.
if [ "${INCLUDE_SIDE_EFFECTS:-0}" != "1" ]; then
  ARGS+=(
    --exclude-path /api/v1/customer/contact
    --exclude-path /api/v1/customer/otp
    --exclude-path /api/v1/customer/otp/resend
    --exclude-path /api/v1/customer/forgotPassword
  )
fi

echo "▶ Contract run → $BASE_URL  (side-effects: ${INCLUDE_SIDE_EFFECTS:-0}, auth: $([ -n "${AUTH_TOKEN:-}" ] && echo yes || echo no))"
exec schemathesis run "${ARGS[@]}"
