"""5. Musteri Profil — GET /customer/detail (Bearer zorunlu)."""
import pytest
from tests.api import endpoints as ep
from tests.utils.assertions import assert_status, assert_schema


@pytest.mark.auth
@pytest.mark.negative
def test_profil_tokensiz_401(api, load_schema):
    r = api.get(ep.PROFILE)
    assert_status(r, 401)
    assert_schema(r.json(), load_schema("error"))


@pytest.mark.auth
@pytest.mark.smoke
def test_profil_token_ile_200(authed_api):
    r = authed_api.get(ep.PROFILE)
    assert_status(r, 200)
    body = r.json()
    assert body.get("success") is True
    assert "data" in body
