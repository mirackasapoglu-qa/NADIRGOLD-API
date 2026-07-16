"""OTP tabanli token alma yardimcisi — login/otp -> verify -> token.

Iki adimli akis (SMS kodu kullanici tarafindan girilir):

  1) Tetikle (SMS gonderilir, hash alinir ve .otp_state.json'a yazilir):
       python contract/otp_login.py login --email ahmet@example.com --password gizli123
     veya telefona dogrudan OTP:
       python contract/otp_login.py otp --phone 05551234567

  2) Gelen 6 haneli kod ile dogrula (token doner, .otp_state.json'a yazilir):
       python contract/otp_login.py verify --code 123456

  3) (Opsiyonel) Kodu yeniden gonder:
       python contract/otp_login.py resend

  Sonra token'i kullan:
       python contract/otp_login.py token           # sadece token'i yazar
       AUTH_TOKEN=$(python contract/otp_login.py token) ...

Guvenlik: state dosyasi (.otp_state.json) gitignore'da olmali; hash/token kalicidir,
is bitince `python contract/otp_login.py clear` ile temizle. SMS gercek gonderilir.
"""
import os
import sys
import json
import argparse
import pathlib

import requests

HERE = pathlib.Path(__file__).parent
STATE = HERE / ".otp_state.json"
BASE_URL = os.getenv("BASE_URL", "https://api-v2.nadirgold.dev").rstrip("/")
TIMEOUT = int(os.getenv("TIMEOUT", "15"))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def _session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Content-Type": "application/json"})
    return s


def _load():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def _save(d):
    STATE.write_text(json.dumps(d, indent=2, ensure_ascii=False))


def _post(s, path, body, headers=None):
    r = s.post(f"{BASE_URL}{path}", json=body, headers=headers or {}, timeout=TIMEOUT)
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, {"raw": r.text[:500]}


def cmd_login(a):
    s = _session()
    headers = {"device-type": a.device_type, "app-version": a.app_version,
               "device-name": a.device_name, "device-token": a.device_token}
    code, body = _post(s, "/api/v1/customer/login",
                       {"email": a.email, "password": a.password}, headers)
    data = body.get("data") or {}
    print(f"[login] HTTP {code} · requiresOtp={data.get('requiresOtp')}")
    if data.get("token"):
        _save({"token": data["token"], "customer": data.get("customer")})
        print("[login] OTP GEREKMEDI — token dogrudan alindi ve kaydedildi.")
        return
    if data.get("requiresOtp") and data.get("hash"):
        _save({"hash": data["hash"], "flow": "login",
               "refCode": data.get("refCode"), "phone": data.get("phone")})
        print(f"[login] SMS gonderildi. refCode={data.get('refCode')} phone={data.get('phone')}")
        print("[login] Sonraki: python contract/otp_login.py verify --code <6hane>")
        return
    print(f"[login] Beklenmeyen yanit: {json.dumps(body, ensure_ascii=False)}")
    sys.exit(1)


def cmd_otp(a):
    s = _session()
    code, body = _post(s, "/api/v1/customer/otp", {"phone": a.phone})
    data = body.get("data") or {}
    print(f"[otp] HTTP {code}")
    if data.get("hash"):
        _save({"hash": data["hash"], "flow": "otp", "phone": a.phone})
        print("[otp] SMS gonderildi, hash kaydedildi. Sonraki: verify --code <6hane>")
    else:
        print(f"[otp] hash gelmedi: {json.dumps(body, ensure_ascii=False)}")
        sys.exit(1)


def cmd_resend(a):
    st = _load()
    if not st.get("hash"):
        print("[resend] Once login/otp calistir (hash yok)."); sys.exit(1)
    s = _session()
    code, body = _post(s, "/api/v1/customer/otp/resend", {"hash": st["hash"]})
    data = body.get("data") or {}
    print(f"[resend] HTTP {code}")
    if data.get("hash"):
        st["hash"] = data["hash"]; _save(st)
        print("[resend] Yeni hash kaydedildi.")
    else:
        print(f"[resend] {json.dumps(body, ensure_ascii=False)}")


def cmd_verify(a):
    st = _load()
    if not st.get("hash"):
        print("[verify] Once login/otp calistir (hash yok)."); sys.exit(1)
    s = _session()
    code, body = _post(s, "/api/v1/customer/otp/verify",
                       {"hash": st["hash"], "verifyCode": a.code})
    data = body.get("data") or {}
    print(f"[verify] HTTP {code} · verified={data.get('verified')}")
    # Login akisinda token verify.data icinde doner
    inner = data.get("data") if isinstance(data.get("data"), dict) else {}
    token = inner.get("token") or data.get("token")
    if token:
        st["token"] = token
        st["customer"] = inner.get("customer") or data.get("customer")
        _save(st)
        print("[verify] Token alindi ve kaydedildi.")
    else:
        print(f"[verify] Token yanitta yok: {json.dumps(body, ensure_ascii=False)}")


def cmd_token(a):
    st = _load()
    if st.get("token"):
        print(st["token"])
    else:
        print("", end=""); sys.exit(1)


def cmd_clear(a):
    if STATE.exists():
        STATE.unlink()
    print("[clear] .otp_state.json silindi.")


def main():
    p = argparse.ArgumentParser(description="OTP tabanli token alma yardimcisi")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("login"); pl.set_defaults(fn=cmd_login)
    pl.add_argument("--email", required=True); pl.add_argument("--password", required=True)
    pl.add_argument("--device-type", default="ios"); pl.add_argument("--app-version", default="2.0.4")
    pl.add_argument("--device-name", default="qa-test"); pl.add_argument("--device-token", default="qa-device-token-001")

    po = sub.add_parser("otp"); po.set_defaults(fn=cmd_otp)
    po.add_argument("--phone", required=True)

    pv = sub.add_parser("verify"); pv.set_defaults(fn=cmd_verify)
    pv.add_argument("--code", required=True)

    sub.add_parser("resend").set_defaults(fn=cmd_resend)
    sub.add_parser("token").set_defaults(fn=cmd_token)
    sub.add_parser("clear").set_defaults(fn=cmd_clear)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
