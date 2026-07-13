"""1. Auth — login, pre-register, register, logout."""
import pytest
from tests.api import endpoints as ep
from tests.utils.assertions import assert_status, assert_schema


# ---------------------------------------------------------------- login

@pytest.mark.auth
@pytest.mark.negative
def test_login_yanlis_sifre_401(api, config, load_schema):
    r = api.post(ep.LOGIN, json={
        "email": config["test_email"] or "someone@example.com",
        "password": config["wrong_password"],
    })
    assert_status(r, 401)
    assert_schema(r.json(), load_schema("error"))


@pytest.mark.auth
@pytest.mark.negative
def test_login_kayitsiz_email_401(api, config, load_schema):
    r = api.post(ep.LOGIN, json={
        "email": config["unknown_email"],
        "password": "whatever123",
    })
    assert_status(r, 401)
    assert_schema(r.json(), load_schema("error"))


@pytest.mark.auth
@pytest.mark.negative
def test_login_eksik_alan_hata(api):
    r = api.post(ep.LOGIN, json={"email": "a@b.com"})  # password yok
    assert r.status_code in (400, 401, 422), (
        f"Eksik alanda 4xx bekleniyordu, gelen {r.status_code}"
    )


@pytest.mark.auth
@pytest.mark.smoke
def test_login_basarili(api, registered_account, load_schema):
    """Gercek hesapla login → token (veya OTP hash)."""
    r = api.post(ep.LOGIN, json={
        "email": registered_account["email"],
        "password": registered_account["password"],
    })
    assert_status(r, 200)
    data = r.json().get("data", {})
    if data.get("requiresOtp"):
        assert_schema(r.json(), load_schema("otp_required"))
    else:
        assert_schema(r.json(), load_schema("login"))


# ---------------------------------------------------------------- pre-register

@pytest.mark.negative
def test_pre_register_kayitli_email_400(api, registered_account, load_schema):
    """Zaten kayitli e-posta ile pre-register → 400."""
    r = api.post(ep.PRE_REGISTER, json={"email": registered_account["email"]})
    assert_status(r, 400)
    assert_schema(r.json(), load_schema("error"))


@pytest.mark.negative
def test_pre_register_gecersiz_email(api):
    r = api.post(ep.PRE_REGISTER, json={"email": "gecersiz-email"})
    assert r.status_code in (400, 422), (
        f"Gecersiz e-postada 4xx bekleniyordu, gelen {r.status_code}"
    )


# ---------------------------------------------------------------- register

@pytest.mark.smoke
def test_register_basarili(api, load_schema):
    """pre-register -> register ile taze hesap → dogrudan token (OTP kapali)."""
    from tests.utils import factories
    acc = factories.new_customer_payload()

    pre = api.post(ep.PRE_REGISTER, json={"email": acc["email"]})
    assert_status(pre, 200)
    assert_schema(pre.json(), load_schema("hash"))

    payload = {**acc["payload"], "hash": pre.json()["data"]["hash"]}
    r = api.post(ep.REGISTER, json=payload)
    assert_status(r, 200)
    data = r.json().get("data", {})
    if data.get("requiresOtp"):
        assert_schema(r.json(), load_schema("otp_required"))
    else:
        assert_schema(r.json(), load_schema("login"))


@pytest.mark.negative
def test_register_sifreler_uyusmuyor_400(api, load_schema):
    r = api.post(ep.REGISTER, json={
        "firstName": "Test",
        "lastName": "QA",
        "hash": "gecersiz-hash",
        "password": "gizli123",
        "passwordConfirmation": "farkli456",
        "phone": "05551234567",
        "identityNumber": "12345678901",
        "birthdate": "1990-01-15",
        "kvkk": True,
        "membership": True,
    })
    assert r.status_code == 400
    assert_schema(r.json(), load_schema("error"))


# ---------------------------------------------------------------- logout

@pytest.mark.auth
@pytest.mark.negative
def test_logout_tokensiz_401(api, load_schema):
    r = api.post(ep.LOGOUT)
    assert_status(r, 401)
    assert_schema(r.json(), load_schema("error"))


@pytest.mark.auth
@pytest.mark.smoke
def test_logout_basarili(authed_api):
    """Gecerli token ile cikis → 200."""
    r = authed_api.post(ep.LOGOUT)
    assert_status(r, 200)
    assert r.json().get("success") is True


# ---------------------------------------------------------------- delete (hesap)

@pytest.mark.negative
def test_delete_hesap_tokensiz_401(api, load_schema):
    """DELETE /customer/delete tokensiz → 401 (hesabi pasife alir, auth zorunlu)."""
    r = api.delete(ep.DELETE_ACCOUNT)
    assert_status(r, 401)
    assert_schema(r.json(), load_schema("error"))
