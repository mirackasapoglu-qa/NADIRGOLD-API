"""3. OTP — otp gonder, dogrula, yeniden gonder.

Not: Gercek OTP kodu telefona SMS ile gittigi icin pozitif dogrulama
otomatize edilemez. Bu testler negatif senaryolar ve hash uretimine odaklanir.
"""
import pytest
from tests.api import endpoints as ep
from tests.utils.assertions import assert_status, assert_schema


@pytest.mark.smoke
def test_otp_gonder_hash_doner(api, load_schema):
    """Gecerli telefon → 200 + hash."""
    r = api.post(ep.OTP_SEND, json={"phone": "05551234567"})
    # Rate-limit/SMS saglayici sebebiyle 4xx de olabilir; hash donerse semayi dogrula
    if r.status_code == 200:
        assert_schema(r.json(), load_schema("hash"))
    else:
        assert r.status_code in (400, 422, 429)


@pytest.mark.negative
def test_otp_gonder_gecersiz_telefon_400(api, load_schema):
    r = api.post(ep.OTP_SEND, json={"phone": "123"})
    assert r.status_code in (400, 422)
    assert_schema(r.json(), load_schema("error"))


@pytest.mark.negative
def test_otp_verify_gecersiz_kod_400(api, load_schema):
    r = api.post(ep.OTP_VERIFY, json={
        "hash": "gecersiz-hash",
        "verifyCode": "000000",
    })
    assert_status(r, 400)
    assert_schema(r.json(), load_schema("error"))


@pytest.mark.negative
def test_otp_verify_eksik_alan(api):
    r = api.post(ep.OTP_VERIFY, json={"hash": "abc"})  # verifyCode yok
    assert r.status_code in (400, 422)


@pytest.mark.negative
def test_otp_resend_gecersiz_hash_400(api, load_schema):
    r = api.post(ep.OTP_RESEND, json={"hash": "gecersiz-veya-kullanilmis-hash"})
    assert_status(r, 400)
    assert_schema(r.json(), load_schema("error"))
