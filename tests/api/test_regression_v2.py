"""V2 donusum regresyon testleri — 2026-07 canli kosumlarindan dogrulanmis bulgular.

Iki tur test var:
  * Dogrulanan (PASS) davranislari SABITLER — ileride bozulursa kirmizi verir.
  * Bilinen acik bug'lar `@pytest.mark.xfail(strict=True)` ile isaretli — bug DEVAM
    ederken yesil (xfail), bug DUZELINCE test XPASS -> kirmizi vererek "bug kapandi,
    testi guncelle" sinyali verir. Boylece Jira'daki durum ile suite senkron kalir.

Kaynak kartlar: NSB-5384/5400/5401/5403/5409/5354/5359/5483/5702/5338 +
bug'lar NSB-5901/5920/5928/5954/5955/5962/5963.
"""
import pytest
from tests.api import endpoints as ep
from tests.utils.assertions import assert_status


# =============================================================== getCities (NSB-5409)

@pytest.mark.regression
def test_getcities_turkiye_liste(api):
    """countryId=1 -> Turkiye illeri (canli). Ic ice counties[] gelir."""
    r = api.get(f"{ep.GET_CITIES}/1")
    assert_status(r, 200)
    data = r.json().get("data")
    assert isinstance(data, list) and len(data) > 50, "Turkiye il listesi bekleniyor"
    assert "counties" in data[0], "Her sehir counties[] icermeli"


@pytest.mark.regression
@pytest.mark.negative
def test_getcities_sifir_422(api):
    """/getCities/0 -> 422 'Country ID must be set' (spec ile birebir)."""
    r = api.get(f"{ep.GET_CITIES}/0")
    assert_status(r, 422)
    assert r.json().get("message") == "Country ID must be set"


@pytest.mark.regression
@pytest.mark.negative
def test_getcities_non_numeric_422(api):
    r = api.get(f"{ep.GET_CITIES}/abc")
    assert_status(r, 422)


@pytest.mark.regression
@pytest.mark.xfail(reason="NSB-5955/NSB-5901: id/countryId string donuyor, number olmali", strict=True)
def test_getcities_id_numeric(api):
    """BUG: id ve countryId string ('1') donuyor; number olmali."""
    r = api.get(f"{ep.GET_CITIES}/1")
    city = r.json()["data"][0]
    assert isinstance(city["id"], int) and isinstance(city["countryId"], int)


# =============================================================== bankListConverter (NSB-5384 CLEAN PASS)

@pytest.mark.regression
@pytest.mark.smoke
def test_banklistconverter_pass(api):
    """CLEAN PASS: 200, liste, id number, cacheable header."""
    r = api.get(ep.PRODUCT_BANK_LIST_CONVERTER)
    assert_status(r, 200)
    data = r.json().get("data")
    assert isinstance(data, list) and data, "Banka listesi bekleniyor"
    first = data[0]
    assert isinstance(first["id"], int), "id number olmali (regresyon korumasi)"
    for k in ("bankCode", "logo", "cardLogo", "bankName"):
        assert k in first, f"{k} alani bekleniyor"
    assert "cache-control" in {h.lower() for h in r.headers}, "cacheable: Cache-Control bekleniyor"


# =============================================================== getPrices (NSB-5400)

@pytest.mark.regression
@pytest.mark.negative
def test_getprices_productid_zorunlu_400(api):
    r = api.post(ep.PRODUCT_GET_PRICES, json={})
    assert_status(r, 400)
    errs = r.json().get("errors", {}).get("validation", [])
    assert any("productId" in e for e in errs), "productId validasyonu bekleniyor"


@pytest.mark.regression
def test_getprices_finansal_string(api):
    """Finansal alanlar string/Decimal (kritik kural). Not: status 201 bug icin ayri test."""
    r = api.post(ep.PRODUCT_GET_PRICES, json={"productId": 11})
    assert r.status_code in (200, 201), f"beklenmeyen status {r.status_code}"
    item = r.json()["data"][0]
    assert isinstance(item["price"], str), "price string (Decimal) olmali"
    assert isinstance(item["originalPrice"], str), "originalPrice string olmali"


@pytest.mark.regression
def test_getprices_status_200(api):
    """NSB-5962 DUZELDI (2026-07-17): getPrices artik 200 donuyor (onceki 201).
    Regresyon korumasi — tekrar 201'e donerse kirmizi verir."""
    r = api.post(ep.PRODUCT_GET_PRICES, json={"productId": 11})
    assert r.status_code == 200, f"200 bekleniyor (NSB-5962 regresyon), gelen {r.status_code}"


@pytest.mark.regression
def test_getprices_taxid_numeric(api):
    """NSB-5901 DUZELDI (2026-07-17): taxId artik number (onceki '3' string)."""
    r = api.post(ep.PRODUCT_GET_PRICES, json={"productId": 11})
    assert isinstance(r.json()["data"][0]["taxId"], int), "taxId number olmali (NSB-5901 regresyon)"


# =============================================================== getPriceHistory (NSB-5401)

@pytest.mark.regression
@pytest.mark.xfail(reason="NSB-5963 KOTULESTI (2026-07-17): getPriceHistory tum urunlerde 500 crash "
                          "(onceki 200+bos). Duzelince XPASS ile uyarir.", strict=True)
def test_getpricehistory_yapi(api):
    """Yapi: {oneMonth, threeMonth, sixMonth, oneYear} her biri {label, value[]}.
    2026-07-17 itibariyle uc 500 donuyor (regresyon)."""
    r = api.get(f"{ep.PRODUCT_GET_PRICE_HISTORY}/11")
    assert_status(r, 200)
    data = r.json()["data"]
    for period in ("oneMonth", "threeMonth", "sixMonth", "oneYear"):
        assert period in data and "value" in data[period], f"{period}.value bekleniyor"


@pytest.mark.regression
@pytest.mark.negative
def test_getpricehistory_non_numeric_400(api):
    r = api.get(f"{ep.PRODUCT_GET_PRICE_HISTORY}/abc")
    assert_status(r, 400)


@pytest.mark.regression
@pytest.mark.xfail(reason="NSB-5963: tum urunlerde fiyat gecmisi bos donuyor", strict=True)
def test_getpricehistory_veri_dolu(api):
    """BUG: 12/12 urunde tum donemler bos. Duzelince en az bir donemde veri bekleriz."""
    r = api.get(f"{ep.PRODUCT_GET_PRICE_HISTORY}/11")
    data = r.json()["data"]
    total = sum(len(data[p].get("value") or []) for p in data)
    assert total > 0, "En az bir donemde fiyat noktasi bekleniyor"


# =============================================================== sitemap/slugs (NSB-5338 / NSB-5954)

@pytest.mark.regression
def test_sitemap_slugs_liste(api):
    r = api.get(ep.CONTENT_SITEMAP_SLUGS)
    assert_status(r, 200)
    data = r.json().get("data")
    assert isinstance(data, list) and len(data) > 100, "Sitemap slug listesi bekleniyor"
    assert all("slug" in x for x in data), "Her kayitta slug bekleniyor"


@pytest.mark.regression
def test_sitemap_slugs_updatedat_tam(api):
    """NSB-5954 DUZELDI (2026-07-17 dogrulandi): tum slug'larda updatedAt dolu.
    Regresyon korumasi — tekrar eksik gelirse kirmizi verir."""
    data = api.get(ep.CONTENT_SITEMAP_SLUGS).json()["data"]
    eksik = [x["slug"] for x in data if "updatedAt" not in x]
    assert not eksik, f"{len(eksik)} slug'da updatedAt eksik (NSB-5954 regresyon)"


# =============================================================== best-seller (NSB-5483 / NSB-5920)

@pytest.mark.regression
def test_best_seller_envelope(api):
    r = api.get(ep.CONTENT_BEST_SELLER)
    assert_status(r, 200)
    body = r.json()
    assert body.get("success") is True and isinstance(body.get("data"), list)
    assert "meta" in body, "pagination meta bekleniyor"


@pytest.mark.regression
def test_best_seller_tipler(api):
    """NSB-5920 DUZELDI (2026-07-17 dogrulandi): productId number, bayraklar bool.
    Regresyon korumasi — tip tekrar string/int'e donerse kirmizi verir."""
    data = api.get(ep.CONTENT_BEST_SELLER).json()["data"]
    if not data:
        pytest.skip("best-seller bos")
    item = data[0]
    assert isinstance(item["productId"], int), "productId number olmali (NSB-5920 regresyon)"
    assert isinstance(item["canBeSubscription"], bool), "canBeSubscription bool olmali"
    assert isinstance(item["isMotoDelivery"], bool), "isMotoDelivery bool olmali"


# =============================================================== logout (NSB-5702)

@pytest.mark.regression
@pytest.mark.negative
def test_logout_gecersiz_token_401(api):
    """Gecersiz token -> 401 'Invalid or expired token.' (eksik token'dan ayri mesaj)."""
    r = api.post(ep.LOGOUT, headers={"Authorization": "Bearer gecersiz.token.abc"})
    assert_status(r, 401)
    assert "Invalid or expired token" in r.json().get("message", "")


# =============================================================== otp/verify (NSB-5454)

@pytest.mark.regression
@pytest.mark.negative
def test_otp_verify_gecersiz_400(api):
    """Gecersiz hash+kod -> 400 (DTO: hash + verifyCode)."""
    r = api.post(ep.OTP_VERIFY, json={"hash": "gecersiz", "verifyCode": "000000"})
    assert_status(r, 400)


# =============================================================== google review callback (NSB-5359 CLEAN PASS)

@pytest.mark.regression
@pytest.mark.negative
def test_google_review_callback_eksik_code_400(api):
    r = api.get(ep.NOTIFICATION_GOOGLE_REVIEW_CALLBACK)
    assert_status(r, 400)
    errs = r.json().get("errors", {}).get("validation", [])
    assert any("code" in e for e in errs), "code validasyonu bekleniyor"


@pytest.mark.regression
@pytest.mark.negative
def test_google_review_callback_prefixsiz_404(api):
    """Gateway prefix zorunlu: /notification/ olmadan 404."""
    r = api.get("/api/v1/google/review/callback", params={"code": "x"})
    assert_status(r, 404)
