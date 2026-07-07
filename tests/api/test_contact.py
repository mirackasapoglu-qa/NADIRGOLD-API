"""4. Iletisim — contact formu."""
import pytest
from tests.api import endpoints as ep
from tests.utils.assertions import assert_status, assert_schema


@pytest.mark.smoke
def test_contact_gecerli_form_basarili(api, load_schema):
    r = api.post(ep.CONTACT, json={
        "firstName": "QA",
        "lastName": "Test",
        "email": "qa.test@example.com",
        "phone": "5551234567",
        "subject": "Test konusu",
        "message": "Otomatik test mesaji",
    })
    # DOKUMAN FARKI: dokuman 200 diyor, canli API 201 Created donuyor (POST create semantigi)
    assert r.status_code in (200, 201), (
        f"200/201 bekleniyordu, gelen {r.status_code}. Govde: {r.text[:300]}"
    )
    assert_schema(r.json(), load_schema("success"))


@pytest.mark.negative
def test_contact_eksik_alan_400(api, load_schema):
    r = api.post(ep.CONTACT, json={
        "firstName": "QA",
        "email": "qa.test@example.com",
        # lastName, phone, subject, message eksik
    })
    assert r.status_code in (400, 422)
    assert_schema(r.json(), load_schema("error"))


@pytest.mark.negative
def test_contact_gecersiz_email_400(api):
    r = api.post(ep.CONTACT, json={
        "firstName": "QA",
        "lastName": "Test",
        "email": "gecersiz-email",
        "phone": "5551234567",
        "subject": "konu",
        "message": "mesaj",
    })
    assert r.status_code in (400, 422)
