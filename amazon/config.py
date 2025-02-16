import os
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()


class AmazonConfig:
    _browser = os.getenv("BROWSER")
    _driver_path = os.getenv("DRIVER_PATH")

    _url = os.getenv("AMZ_URL")
    _email = os.getenv("AMZ_EMAIL")
    _password = os.getenv("AMZ_PWD")
    _mfa = bool(int(os.getenv("AMZ_MFA")))
    _currency = os.getenv("AMZ_CURRENCY")

    _max_price = int(os.getenv("MAX_PRICE"))
    _bmfa_timeout = int(os.getenv("BMFA_TIMEOUT"))

    _loop_timeout = int(os.getenv("LOOP_TIMEOUT"))
    _retry_count = int(os.getenv("RETRY_COUNT"))

    def __init__(self):
        self._cart_url = urljoin(self._url, "/gp/cart/view.html")
        self._product_base_url = urljoin(self._url, "/dp/")
        self._products = [
            id.strip() for id in os.getenv("AMZ_PRODUCTS").split(";") if id.strip()
        ]

    @property
    def browser(self):
        return self._browser

    @property
    def driver_path(self):
        return self._driver_path

    @property
    def url(self):
        return self._url

    @property
    def email(self):
        return self._email

    @property
    def password(self):
        return self._password

    @property
    def max_price(self):
        return self._max_price

    @property
    def bmfa_timeout(self):
        return self._bmfa_timeout

    @property
    def cart_url(self):
        return self._cart_url

    @property
    def product_base_url(self):
        return self._product_base_url

    @property
    def products(self):
        return self._products

    @property
    def loop_timeout(self):
        return self._loop_timeout

    @property
    def retry_count(self):
        return self._retry_count
