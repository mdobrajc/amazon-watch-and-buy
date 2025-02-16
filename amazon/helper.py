from selenium import webdriver
from selenium.webdriver import Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from amazoncaptcha import AmazonCaptcha
from .config import AmazonConfig


class AmazonHelper:
    # Language-specific labels
    _language_labels = {
        "de-de": {
            "delete_button": "Löschen",
            "empty_cart_message": "Ihr Amazon-Einkaufswagen ist leer",
            "thank_you_msg": "Vielen Dank",
        },
        "en-gb": {
            "delete_button": "Delete",
            "empty_cart_message": "Your Amazon Cart is empty",
            "thank_you_msg": "Thank you",
        },
    }

    def __init__(self, config: AmazonConfig):
        self._config = config
        pass

    def create_driver(self, headless=False) -> Remote:
        service = Service(executable_path=self._config.driver_path)
        if self._config.browser == "chrome":
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument("--headless")
                options.add_argument("--disable-application-cache")
                options.add_argument("--disable-cache")
                options.add_argument("--disk-cache-size=0")
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        elif self._config.browser == "firefox":
            options = webdriver.FirefoxOptions()
            if headless:
                options.add_argument("--headless")
                options.set_preference("browser.cache.disk.enable", False)
                options.set_preference("browser.cache.memory.enable", False)
                options.set_preference("browser.cache.offline.enable", False)
                options.set_preference("network.http.use-cache", False)
            driver = webdriver.Firefox(service=service, options=options)
            return driver
        else:
            raise ValueError(f"Unsupported browser: {self._config.browser}")

    def _is_captcha(self, driver: Remote, product=None) -> bool:
        if product and product not in driver.current_url:
            return True
        if not product:
            try:
                driver.find_element(By.ID, "captchacharacters")
                return True
            except Exception:
                pass

        return False

    def _solve_captcha(self, driver: Remote) -> bool:
        try:
            captcha_input = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.ID, "captchacharacters"))
            )
            if captcha_input:
                image_src = driver.find_element(By.XPATH, "//form//img").get_attribute(
                    "src"
                )

                captcha = AmazonCaptcha.fromlink(image_src)
                solution = captcha.solve()
                if solution != "Not solved":
                    captcha_input.send_keys(solution)
                    captcha_input.submit()
                else:
                    return False

                return True
            else:
                return True
        except Exception as e:
            print("_solve_captcha Exception: ", e)
            return False

    def captcha(self, driver: Remote, product="") -> bool:
        if self._is_captcha(driver, product):
            return self._solve_captcha(driver)
        return True

    def _detect_language(self, driver: Remote) -> str:
        html = driver.find_element(By.TAG_NAME, "html")
        # Returns language code like "de-de", "en-gb", etc.
        return html.get_attribute("lang")

    def get_lang_labels(self, driver: Remote) -> dict[str, str]:
        return self._language_labels.get(
            self._detect_language(driver), self._language_labels["en-gb"]
        )

    def get_thousands_separator(self, driver: Remote) -> str:
        language = self._detect_language(driver)
        replace_val = "."

        if "en" in language:
            replace_val = ","

        return replace_val
