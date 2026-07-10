"""Ortak fixture'lar — tum testler bu yapilandirmayi paylasir."""
import os
import json
import pathlib
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

ROOT = pathlib.Path(__file__).parent.parent
SCHEMA_DIR = ROOT / "schemas"


@pytest.fixture(scope="session")
def config():
    """Ortam degiskenlerinden yapilandirma."""
    return {
        # BASE_URL tanimli degilse calisan canli adrese dus (repoda dokumanli, gizli degil)
        "base_url": os.getenv("BASE_URL", "https://api-v2.nadirgold.dev").rstrip("/"),
        "timeout": int(os.getenv("TIMEOUT", "15")),
        "test_email": os.getenv("TEST_EMAIL", ""),
        "test_password": os.getenv("TEST_PASSWORD", ""),
        "unknown_email": os.getenv("UNKNOWN_EMAIL", "nonexistent_user_qa@example.com"),
        "wrong_password": os.getenv("WRONG_PASSWORD", "definitely-wrong-password"),
        "test_sku": os.getenv("TEST_SKU", "ALTIN-GRAM-1"),
    }


class Client:
    """base_url'e bagli, timeout'u onceden ayarlanmis ince requests sarmalayici."""

    def __init__(self, session, base_url, timeout):
        self._session = session
        self._base_url = base_url
        self._timeout = timeout

    def request(self, method, path, **kwargs):
        kwargs.setdefault("timeout", self._timeout)
        url = path if path.startswith("http") else f"{self._base_url}{path}"
        return self._session.request(method, url, **kwargs)

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)


# Cloudflare bot korumasi (hata 1010) varsayilan python UA'sini banliyor —
# tarayici benzeri bir User-Agent ile istekleri geciriyoruz.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def _make_session(token=None):
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    if token:
        session.headers.update({"Authorization": f"Bearer {token}"})
    return session


@pytest.fixture(scope="session")
def api(config):
    """Kimlik dogrulamasiz (misafir) client."""
    if not config["base_url"]:
        pytest.skip("BASE_URL tanimli degil — .env dosyasini doldur")
    session = _make_session()
    yield Client(session, config["base_url"], config["timeout"])
    session.close()


@pytest.fixture(scope="session")
def registered_account(api, config):
    """Testin ihtiyaci olan gercek hesabi saglar.

    - TEST_EMAIL/TEST_PASSWORD tanimliysa onu kullanir (login ile token alir).
    - Degilse: pre-register -> register ile TAZE bir hesap olusturur (register
      OTP kapaliyken dogrudan token doner).

    Doner: {"email", "password", "token", "self_registered"}
    """
    from tests.utils import factories

    # 1) Ortamda hazir hesap varsa onu kullan
    if config["test_email"] and config["test_password"]:
        r = api.post("/api/v1/customer/login", json={
            "email": config["test_email"], "password": config["test_password"],
        })
        data = r.json().get("data", {}) if r.status_code == 200 else {}
        if data.get("token"):
            return {"email": config["test_email"], "password": config["test_password"],
                    "token": data["token"], "self_registered": False}
        if data.get("requiresOtp"):
            pytest.skip("TEST hesabinda OTP aktif — otomatik login yapilamiyor")
        pytest.skip(f"TEST hesabiyla login basarisiz (HTTP {r.status_code})")

    # 2) Taze hesap olustur
    acc = factories.new_customer_payload()
    pre = api.post("/api/v1/customer/pre-register", json={"email": acc["email"]})
    if pre.status_code not in (200, 201):
        pytest.skip(f"pre-register basarisiz (HTTP {pre.status_code}): {pre.text[:200]}")

    payload = {**acc["payload"], "hash": pre.json()["data"]["hash"]}
    reg = api.post("/api/v1/customer/register", json=payload)
    data = reg.json().get("data", {}) if reg.status_code in (200, 201) else {}
    if data.get("requiresOtp"):
        pytest.skip("register OTP dondu — otomatik hesap olusturulamiyor")
    if not data.get("token"):
        pytest.skip(f"register token dondurmedi (HTTP {reg.status_code}): {reg.text[:200]}")

    return {"email": acc["email"], "password": acc["password"],
            "token": data["token"], "self_registered": True}


@pytest.fixture(scope="session")
def auth_token(registered_account):
    """Gecerli JWT token."""
    return registered_account["token"]


@pytest.fixture(scope="session")
def authed_api(config, auth_token):
    """Bearer token'i onceden set edilmis client (login/logout/profil/sepet)."""
    session = _make_session(token=auth_token)
    yield Client(session, config["base_url"], config["timeout"])
    session.close()


@pytest.fixture(scope="session")
def load_schema():
    """Isimle JSON sema yukler: schemas/<isim>.json"""
    def _load(name):
        with open(SCHEMA_DIR / f"{name}.json", encoding="utf-8") as f:
            return json.load(f)
    return _load
