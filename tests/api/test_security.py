"""OWASP API Security Top 10 farkindalik testleri.

Kapsam (canlida GUVENLI, yikici olmayan probe'lar):
- API1 BOLA        : baskasinin/uydurma kaynak referansiyla veri sizmasi
- API2 Kirik Auth  : gecersiz/bozuk/eksik token ile korumali uca erisim → 401
- API8 Method      : yanlis HTTP metodu → 404/405 (500 degil)
- Injection        : SQLi/NoSQLi denemeleri 5xx patlatmamali, giris saglamamali
- API4 Rate limit  : sinirli hizli istek probe'u (VARSAYILAN KAPALI — ban riski)

Not: Gercek BOLA ancak iki farkli kullanicinin token'i + kaynak ID'si ile kesin
kanitlanir; buradaki probe'lar "uydurma referans VERI SIZDIRMAMALI" seviyesindedir.
"""
import os
import pytest

from tests.api import endpoints as ep
from tests.utils.assertions import assert_schema


# Korumali (auth gerektiren) uclara gecersiz token ile erisim → 401 beklenir
BOGUS_TOKENS = {
    "uydurma": "Bearer tamamen-gecersiz-token",
    "bozuk_jwt": "Bearer eyJhbGciOiJIUzI1NiJ9.bozuk.imza",
    "bos_bearer": "Bearer ",
    "sema_yok": "sadece-duz-metin",
}


# --------------------------------------------------------------------------- #
# API2 — Kirik kimlik dogrulama                                                #
# --------------------------------------------------------------------------- #

@pytest.mark.security
@pytest.mark.parametrize("etiket,token", list(BOGUS_TOKENS.items()))
def test_profil_gecersiz_token_401(api, etiket, token):
    """customer/detail gecersiz/bozuk token ile → 401/403, asla 200 (veri sizmaz)."""
    r = api.get(ep.PROFILE, headers={"Authorization": token})
    assert r.status_code in (401, 403), f"[{etiket}] beklenen 401/403, gelen {r.status_code}"
    assert r.status_code != 200


@pytest.mark.security
def test_logout_gecersiz_token_401(api):
    """logout uydurma token ile → 401 (oturum yok)."""
    r = api.post(ep.LOGOUT, headers={"Authorization": "Bearer uydurma-token"})
    assert r.status_code in (401, 403)


@pytest.mark.security
def test_profil_tokensiz_401(api):
    """Token olmadan korumali uc → 401 (temel kontrol)."""
    r = api.get(ep.PROFILE)
    assert r.status_code == 401


# --------------------------------------------------------------------------- #
# API1 — BOLA / kaynak referansi ile sizinti                                   #
# --------------------------------------------------------------------------- #

@pytest.mark.security
def test_basket_uydurma_hash_veri_sizdirmaz(api):
    """Uydurma/baskasinin basketHash'i → baska kullanicinin sepetini DONDURMEMELI.

    Kabul: 400/401/403/404 (ya da commerce kapaliysa 503). 200 ile dolu sepet
    donmesi BOLA sizintisi olur.
    """
    r = api.get(ep.BASKET_GET, params={"basketHash": "baskasinin-sepeti-0xDEADBEEF"})
    assert r.status_code in (400, 401, 403, 404, 429, 503), (
        f"Uydurma hash beklenmedik status dondurdu: {r.status_code}"
    )
    # 200 dondurse bile icinde baskasinin urunleri OLMAMALI
    if r.status_code == 200:
        data = r.json().get("data") or {}
        items = data.get("items") or []
        assert not items, "BOLA: uydurma hash ile dolu sepet dondu!"


@pytest.mark.security
def test_profil_query_id_ile_zorlanamaz(api):
    """detail'e ?customerId=1 eklemek token'siz erisim SAGLAMAMALI → yine 401.

    (V2 kimligi token'dan aliyor; query ile baska kullaniciya gecilememeli.)
    """
    r = api.get(ep.PROFILE, params={"customerId": 1, "id": 1})
    assert r.status_code == 401


# --------------------------------------------------------------------------- #
# API8 — Yanlis HTTP metodu                                                    #
# --------------------------------------------------------------------------- #

@pytest.mark.security
def test_login_yanlis_metot(api):
    """POST-only login'e GET → 404/405 (500 degil)."""
    r = api.get(ep.LOGIN)
    assert r.status_code in (404, 405), f"Beklenen 404/405, gelen {r.status_code}"
    assert r.status_code < 500


@pytest.mark.security
def test_detail_yanlis_metot(api):
    """GET-only detail'e DELETE → 401/404/405, 5xx degil."""
    r = api.delete(ep.PROFILE)
    assert r.status_code < 500
    assert r.status_code in (401, 404, 405)


# --------------------------------------------------------------------------- #
# Injection farkindaligi — girdi 5xx patlatmamali, giris saglamamali            #
# --------------------------------------------------------------------------- #

@pytest.mark.security
@pytest.mark.parametrize("kotu", [
    "' OR '1'='1",
    "admin'--",
    '{"$ne": null}',            # NoSQL enjeksiyon denemesi
    "'; DROP TABLE customers;--",
])
def test_login_injection_5xx_ve_bypass_yok(api, kotu):
    """SQLi/NoSQLi payload'lari → 400/401/422; asla 200 (bypass), asla 5xx."""
    r = api.post(ep.LOGIN, json={"email": kotu, "password": kotu})
    assert r.status_code != 200, f"Injection ile giris BASARILI oldu: {kotu!r}"
    assert r.status_code < 500, f"Injection 5xx patlatti: {kotu!r} → {r.status_code}"
    assert r.status_code in (400, 401, 422)


# --------------------------------------------------------------------------- #
# API4 — Rate limit probe (VARSAYILAN KAPALI: Cloudflare ban riski)            #
# --------------------------------------------------------------------------- #

@pytest.mark.security
@pytest.mark.skipif(os.getenv("RUN_RATELIMIT") != "1",
                    reason="Hizli istek Cloudflare ban riski — RUN_RATELIMIT=1 ile acilir")
def test_rate_limit_probe(api, config):
    """15 hizli hatali-login → 429 gorulur mu? (bilgilendirici; 429 yoksa da gecer).

    Amac: rate limit VAR MI diye gozlemlemek. Yoksa test gecer ama not dusulur.
    """
    body = {"email": config["unknown_email"], "password": config["wrong_password"]}
    kodlar = [api.post(ep.LOGIN, json=body).status_code for _ in range(15)]
    saw_429 = 429 in kodlar
    # Sunucu hatasi olmamali; 429 gorulmesi ise pozitif bir guvenlik sinyali
    assert all(c < 500 for c in kodlar), f"Rate probe 5xx: {kodlar}"
    print(f"\n[rate-limit] 15 istek durum kodlari: {kodlar} · 429 goruldu: {saw_429}")
