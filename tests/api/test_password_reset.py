"""2. Sifre Sifirlama — forgotPassword, forgotPasswordSet."""
import pytest
from tests.api import endpoints as ep
from tests.utils.assertions import assert_status, assert_schema


@pytest.mark.smoke
def test_forgot_password_kayitsiz_email_yine_200(api, config, load_schema):
    """Enumeration korumasi: hesap yoksa bile success:true doner."""
    r = api.post(ep.FORGOT_PASSWORD, json={"email": config["unknown_email"]})
    assert_status(r, 200)
    assert_schema(r.json(), load_schema("success"))


@pytest.mark.negative
def test_forgot_password_gecersiz_email(api):
    r = api.post(ep.FORGOT_PASSWORD, json={"email": "gecersiz"})
    assert r.status_code in (200, 400, 422), (
        f"Beklenmeyen status: {r.status_code}"
    )


# forgotPasswordSet gercek yolu: /customer/forgot-password/reset (otoritatif spec).
# Eski denenen /forgotPasswordSet yanlisti; gercek yol canli 400 donuyor (NSB-5864).
@pytest.mark.negative
def test_forgot_password_set_gecersiz_hash_400(api, load_schema):
    r = api.post(ep.FORGOT_PASSWORD_SET, json={
        "hash": "gecersiz-veya-suresi-dolmus-hash",
        "password": "YeniSifre123",
        "passwordConfirmation": "YeniSifre123",
    })
    assert_status(r, 400)
    assert_schema(r.json(), load_schema("error"))


@pytest.mark.negative
def test_forgot_password_set_sifreler_uyusmuyor_400(api, load_schema):
    r = api.post(ep.FORGOT_PASSWORD_SET, json={
        "hash": "herhangi-bir-hash",
        "password": "YeniSifre123",
        "passwordConfirmation": "FarkliSifre456",
    })
    assert_status(r, 400)
    assert_schema(r.json(), load_schema("error"))
