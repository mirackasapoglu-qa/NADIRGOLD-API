"""Sinir deger & derinlik testleri — idempotency, buyuk payload, Unicode/emoji,
malformed govde, eszamanli istek (race).

Tasarim ilkesi: CANLI API'ye karsi GUVENLI. Testler kalicilasmayan/dogrulama
katmaninda reddedilen uclara (login, pre-register, forgot-password) yonelir; boylece
gercek veri kirlenmez. Beklenti "5xx DONMEsin ve sizinti olmasin" seviyesindedir —
kesin durum kodu backend'e gore degisebilecegi icin tolere edilir.

Yazma tarafinda gercek benzersizlik yarisini test eden opsiyonel bir race testi
RUN_WRITE_RACE=1 ile acilir (varsayilan kapali — hesap olusturur).
"""
import os
import json
import concurrent.futures as cf

import pytest
import requests

from tests.api import endpoints as ep
from tests.utils import factories
from tests.conftest import _make_session, USER_AGENT


# --------------------------------------------------------------------------- #
# Idempotency — ayni istegi iki kez gonderince tutarli davranis                #
# --------------------------------------------------------------------------- #

@pytest.mark.boundary
def test_pre_register_ayni_email_iki_kez_tutarli(api):
    """Ayni (taze) email ile iki kez pre-register → tutarli sonuc, 5xx yok.

    pre-register hesap OLUSTURMAZ (yalniz email dogrular + hash uretir), bu yuzden
    iki kez cagirmak guvenli ve idempotency davranisi gozlemlenebilir.
    """
    email = factories.gen_email("qa_idem")
    r1 = api.post(ep.PRE_REGISTER, json={"email": email})
    r2 = api.post(ep.PRE_REGISTER, json={"email": email})

    for r in (r1, r2):
        assert r.status_code < 500, f"5xx alindi: {r.status_code} {r.text[:200]}"
    # Iki cagri ayni sinifta sonuc dondurmeli (ikisi de 2xx ya da ikisi de 4xx)
    assert (r1.status_code // 100) == (r2.status_code // 100), (
        f"Tutarsiz: {r1.status_code} vs {r2.status_code}"
    )


@pytest.mark.boundary
def test_forgot_password_tekrar_idempotent(api, config):
    """Kayitsiz email ile iki kez forgot-password → ikisi de 200 (enumeration korumasi)."""
    body = {"email": config["unknown_email"]}
    r1 = api.post(ep.FORGOT_PASSWORD, json=body)
    r2 = api.post(ep.FORGOT_PASSWORD, json=body)
    for r in (r1, r2):
        assert r.status_code in (200, 201), f"Beklenen 200/201, gelen {r.status_code}"


@pytest.mark.boundary
def test_login_tekrar_deterministik(api, config):
    """Ayni hatali kimlik bilgisi iki kez → ikisi de ayni status (deterministik)."""
    body = {"email": config["unknown_email"], "password": config["wrong_password"]}
    r1 = api.post(ep.LOGIN, json=body)
    r2 = api.post(ep.LOGIN, json=body)
    assert r1.status_code == r2.status_code, f"{r1.status_code} != {r2.status_code}"
    assert r1.status_code in (400, 401, 422)


# --------------------------------------------------------------------------- #
# Buyuk payload — asiri boyut zarifce reddedilmeli (413/400/422), 5xx/200 degil #
# --------------------------------------------------------------------------- #

@pytest.mark.boundary
@pytest.mark.xfail(reason="NSB-5867: ~200KB+ payload canlida 500 donduruyor (413/400 olmali)",
                   strict=False)
def test_login_asiri_buyuk_payload_reddedilir(api):
    """~256 KB'lik password alani → 413/400/401/422 beklenir; asla 5xx, asla 200.

    BULGU (NSB-5867): canlida ~100-200KB esiginin ustunde 500 donuyor → xfail.
    """
    huge = "A" * 256_000
    r = api.post(ep.LOGIN, json={"email": "qa_big@example.com", "password": huge})
    assert r.status_code != 200, "Devasa payload ile giris BASARILI olmamali"
    assert r.status_code < 500, f"5xx alindi: {r.status_code}"
    assert r.status_code in (400, 401, 413, 422, 429)


@pytest.mark.boundary
def test_pre_register_asiri_uzun_email_reddedilir(api):
    """Cok uzun email (~64 KB local part) → 400/413/422, 5xx yok."""
    email = ("x" * 64_000) + "@example.com"
    r = api.post(ep.PRE_REGISTER, json={"email": email})
    assert r.status_code < 500, f"5xx alindi: {r.status_code}"
    assert r.status_code in (400, 413, 422, 429)


# --------------------------------------------------------------------------- #
# Unicode / emoji / RTL — 5xx patlatmadan islenebilmeli                        #
# --------------------------------------------------------------------------- #

@pytest.mark.boundary
@pytest.mark.parametrize("email", [
    "qa😀emoji@example.com",       # emoji
    "qá̀combining@example.com",  # combining diacritics
    "qa‮RTL@example.com",     # right-to-left override
    "аdmin@example.com",            # Cyrillic 'а' (homoglyph)
])
def test_pre_register_unicode_5xx_donmez(api, email):
    """Unicode/emoji/homoglyph email → 5xx DONMEMELI (400/422 ya da 200 kabul)."""
    r = api.post(ep.PRE_REGISTER, json={"email": email})
    assert r.status_code < 500, f"Unicode girdi 5xx patlatti: {r.status_code} / {email!r}"


@pytest.mark.boundary
def test_login_unicode_alanlar_5xx_donmez(api):
    """Emoji iceren email+password ile login → 5xx yok, giris basarili degil."""
    r = api.post(ep.LOGIN, json={"email": "🔥@example.com", "password": "şifre🔥émoji"})
    assert r.status_code < 500
    assert r.status_code != 200


# --------------------------------------------------------------------------- #
# Malformed govde / yanlis content-type                                        #
# --------------------------------------------------------------------------- #

@pytest.mark.boundary
def test_login_bozuk_json_400(api):
    """Gecersiz JSON govdesi → 400 (parse hatasi), 5xx degil."""
    r = api.post(
        ep.LOGIN,
        data='{"email": "a@b.com", "password": ',  # yarim JSON
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code in (400, 415, 422), f"Beklenen 400/415/422, gelen {r.status_code}"
    assert r.status_code < 500


@pytest.mark.boundary
def test_login_bos_govde(api):
    """Bos govde → 400/401/422, 5xx degil."""
    r = api.post(ep.LOGIN, data="", headers={"Content-Type": "application/json"})
    assert r.status_code < 500
    assert r.status_code in (400, 401, 422)


# --------------------------------------------------------------------------- #
# Race condition — eszamanli istekler                                          #
# --------------------------------------------------------------------------- #

def _independent_post(base_url, timeout, path, payload):
    """Her thread icin bagimsiz session (requests.Session thread-safe garantisi yok)."""
    s = _make_session()
    try:
        return s.post(f"{base_url}{path}", json=payload, timeout=timeout).status_code
    finally:
        s.close()


@pytest.mark.boundary
def test_pre_register_eszamanli_ayni_email(config):
    """Ayni email ile 2 ES ZAMANLI pre-register → ikisi de saglikli (5xx yok).

    pre-register kalicilastirmadigi icin bu, veri kirletmeden eszamanlilik davranisini
    gozler. Yaris kaynakli 5xx / deadlock olmamali.
    """
    if not config["base_url"]:
        pytest.skip("BASE_URL tanimli degil")
    email = factories.gen_email("qa_race")
    payload = {"email": email}
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        futs = [ex.submit(_independent_post, config["base_url"], config["timeout"],
                          ep.PRE_REGISTER, payload) for _ in range(2)]
        codes = [f.result() for f in futs]
    assert all(c < 500 for c in codes), f"Eszamanli istekte 5xx: {codes}"


@pytest.mark.boundary
@pytest.mark.skipif(os.getenv("RUN_WRITE_RACE") != "1",
                    reason="Yazma yarisi hesap olusturur — RUN_WRITE_RACE=1 ile acilir")
def test_register_ayni_telefon_yarisi_tek_basari(config):
    """OPT-IN: Ayni telefonla 2 eszamanli register → benzersizlik korunmali.

    Beklenti: en fazla BIR tanesi 200 (token), digeri 400 (telefon zaten kayitli).
    Iki 200 gelirse benzersizlik yarisi (race) kirilmis demektir.
    """
    if not config["base_url"]:
        pytest.skip("BASE_URL tanimli degil")
    base, to = config["base_url"], config["timeout"]

    # Ortak telefon/TC, farkli email ile iki tam register govdesi
    phone = factories.gen_phone()
    tc = factories.gen_tc()

    def build():
        acc = factories.new_customer_payload()
        p = {**acc["payload"], "phone": phone, "identityNumber": tc}
        pre = requests.post(f"{base}{ep.PRE_REGISTER}", json={"email": acc["email"]},
                            headers={"User-Agent": USER_AGENT}, timeout=to)
        p["hash"] = pre.json().get("data", {}).get("hash", "x")
        return p

    bodies = [build(), build()]

    def do(body):
        return requests.post(f"{base}{ep.REGISTER}", json=body,
                             headers={"User-Agent": USER_AGENT}, timeout=to).status_code

    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        codes = [f.result() for f in ex.map(do, bodies)]

    basarili = sum(1 for c in codes if c in (200, 201))
    assert basarili <= 1, f"Benzersizlik yarisi kirildi — {basarili} basarili kayit: {codes}"
