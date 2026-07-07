"""Gecerli + benzersiz test verisi ureticileri.

register endpoint'i benzersiz telefon ve gecerli TC kimlik no ister; bu modul
her cagrida yeni, checksum'i dogru degerler uretir.
"""
import random
import time


def gen_tc():
    """Algoritmik olarak gecerli 11 haneli TC kimlik no uretir."""
    d = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(8)]
    d10 = ((d[0] + d[2] + d[4] + d[6] + d[8]) * 7 - (d[1] + d[3] + d[5] + d[7])) % 10
    d11 = (sum(d) + d10) % 10
    return "".join(map(str, d)) + str(d10) + str(d11)


def gen_phone():
    """05XX ile baslayan (buyuk ihtimalle) benzersiz Turkiye cep numarasi."""
    return "0555" + str(random.randint(1000000, 9999999))


def gen_email(prefix="qa_auto"):
    """Zaman + rastgele ekiyle benzersiz e-posta."""
    return f"{prefix}_{int(time.time())}_{random.randint(1000, 9999)}@example.com"


def new_customer_payload(password="Gizli123!"):
    """register icin tam, gecerli ve benzersiz gövde (hash haric)."""
    return {
        "email": gen_email(),
        "password": password,
        "payload": {
            "firstName": "QA",
            "lastName": "Auto",
            "password": password,
            "passwordConfirmation": password,
            "phone": gen_phone(),
            "identityNumber": gen_tc(),
            "birthdate": "1990-01-15",
            "kvkk": True,
            "membership": True,
        },
    }
