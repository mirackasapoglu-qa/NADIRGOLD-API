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

# 2. Sifre Sifirlama
FORGOT_PASSWORD = "/api/v1/customer/forgot-password"  # DOKUMAN FARKI: dokumanda /forgotPassword (404)
FORGOT_PASSWORD_SET = "/api/v1/customer/forgotPasswordSet"  # BULUNAMADI: bu ve varyantlari 404. Gateway /customer/forgot-password/* -> /auth/forgot-password/* olarak yeniden yazliyor; dogru yol netlesince guncellenecek.

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
