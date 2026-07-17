"""Endpoint yollari — CANLI API (https://api-v2.nadirgold.dev) ile dogrulanmistir.

DIKKAT: Asagidaki yollar 2026-07-07'de canli gateway'e karsi yoklanmistir.
Dokuman (nadir-v2.md) ile canli API arasinda birkaç fark tespit edildi;
farkli olanlar # DOKUMAN FARKI ile isaretlendi.
"""

# 1- Customer Service / Auth
LOGIN = "/api/v1/customer/login"          # DOKUMAN FARKI: dokumanda /api/v1/auth/login (404)
LOGOUT = "/api/v1/customer/logout"        # dogrulandi (401 auth gerekiyor)
PRE_REGISTER = "/api/v1/customer/pre-register"  # dogrulandi
REGISTER = "/api/v1/customer/register"    # dogrulandi
DELETE_ACCOUNT = "/api/v1/customer/delete"  # dogrulandi (tokensiz 401; hesabi pasife alir)

# 2. Sifre Sifirlama
FORGOT_PASSWORD = "/api/v1/customer/forgot-password"  # DOKUMAN FARKI: dokumanda /forgotPassword (404)
FORGOT_PASSWORD_SET = "/api/v1/customer/forgot-password/reset"  # dogrulandi (otoritatif spec + canli 400). Eski denenen /forgotPasswordSet yanlisti.

# 3. OTP
OTP_SEND = "/api/v1/customer/otp"                 # dogrulandi
OTP_VERIFY = "/api/v1/customer/otp/verify"        # DOKUMAN FARKI: dokumanda /api/v1/otp/verify (404)
OTP_RESEND = "/api/v1/customer/otp/resend"        # dogrulandi

# 4. Iletisim
CONTACT = "/api/v1/customer/contact"      # dogrulandi

# 5. Musteri Profil
PROFILE = "/api/v1/customer/detail"       # dogrulandi (401 auth gerekiyor)

# 2- Commerce Service / Basket
BASKET_ADD = "/api/v1/basket/add"         # dogrulandi (401 auth gerekiyor)
BASKET_GET = "/api/v1/basket/get"         # ERISILEMEDI: 404 (muhtemelen :3001 backend'de, gateway'de yok)
BASKET_UPDATE = "/api/v1/basket/update"   # ERISILEMEDI: 404
BASKET_DELETE = "/api/v1/basket/delete"   # ERISILEMEDI: 404

# 6. Sehir/Ilce (customer-service / CityModule) — top-level, /customer/ prefix'i YOK
GET_CITIES = "/api/v1/getCities"          # /{countryId}; NSB-5409. Turkiye canli countryId=1 (spec 212 bos)

# 3- Product Service (2026-07-16 dogrulandi)
PRODUCT_BANK_LIST_CONVERTER = "/api/v1/product/bankListConverter"  # NSB-5384 CLEAN PASS (cacheable)
PRODUCT_GET_PRICES = "/api/v1/product/getPrices"                   # POST {productId}; NSB-5400 (201 bug NSB-5962)
PRODUCT_GET_PRICE_HISTORY = "/api/v1/product/getPriceHistory"      # /{productId}; NSB-5401 (bos veri NSB-5963)
PRODUCT_CATEGORY_PRODUCTS_SUMMARY = "/api/v1/product/category-products/summary"  # NSB-5403

# 4- Content Service (2026-07-14/16 dogrulandi)
CONTENT_SITEMAP_SLUGS = "/api/v1/content/sitemap/slugs"   # NSB-5338; updatedAt eksik NSB-5954
CONTENT_BEST_SELLER = "/api/v1/content/best-seller"       # NSB-5483; tip NSB-5920
CONTENT_BEST_SELLER_LITE = "/api/v1/content/best-seller-lite"  # NSB-5354; prices bos NSB-5928

# 5- Notification Service
NOTIFICATION_GOOGLE_REVIEW_CALLBACK = "/api/v1/notification/google/review/callback"  # NSB-5359 CLEAN PASS
