import datetime
import time
from selenium.webdriver import Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from urllib.parse import urljoin
from asyncio import Event
from .config import AmazonConfig
from .helper import AmazonHelper


class AmazonBot:
    def __init__(self):
        config = AmazonConfig()
        self._config = config
        self._helper = AmazonHelper(config)

    # Logins to Amazon
    def _login(self, driver: Remote) -> bool:
        driver.get(self._config.url)

        if not self._helper.captcha(driver):
            return False

        try:
            # Navigate to login
            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.ID, "nav-link-accountList"))
            ).click()
            time.sleep(1)

            # Try to find one of the two inputs for the E-Mail
            try:
                WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.ID, "ap_email_login"))
                ).send_keys(self._config.email + Keys.RETURN)
            except Exception:
                WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.ID, "ap_email"))
                ).send_keys(self._config.email + Keys.RETURN)

            # Fill the password
            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.ID, "ap_password"))
            ).send_keys(self._config.password + Keys.RETURN)

        except Exception:
            print("Login failed while entering credentials")
            return False

        # Wait for manual MFA input and verify login success
        # The driver can't be headless in this case!
        if self._config._mfa:
            try:
                time.sleep(1)
                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "nav-link-accountList"))
                )
            except Exception:
                print("Login failed at MFA")
                return False

        print("Login successful!")
        return True

    # Checks if item is in stock
    def _check_product(self, driver: Remote, product: str) -> bool:
        productUrl = urljoin(urljoin(self._config.url, "/dp/"), product)
        driver.get(productUrl)

        if not self._helper.captcha(driver):
            return False

        self._helper.captcha(driver, product)
        t_separator = self._helper.get_thousands_separator(driver)

        # Check if add-to-cart is present
        # WebDriverWait is maybe too slow?
        """
        try:
            
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.ID, "add-to-cart-button"))
            )
        except Exception:
            return False
        """
        time.sleep(0.1)

        try:
            driver.find_element(By.ID, "buy-now-button")
        except Exception:
            return False

        # Price threshold check
        try:
            # Maybe too slow?
            """
            price_element = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//span[contains(@class, 'priceToPay')]//span[contains(@class, 'a-price-whole')]",
                    )
                )
            )
            price_text = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//span[contains(@class, 'priceToPay')]//span[contains(@class, 'a-price-whole')]/span",
                    )
                )
            )
            """
            price_element = driver.find_element(
                By.XPATH,
                "//span[contains(@class, 'priceToPay')]//span[contains(@class, 'a-price-whole')]",
            )
            price_text = driver.find_element(
                By.XPATH,
                "//span[contains(@class, 'priceToPay')]//span[contains(@class, 'a-price-whole')]/span",
            )
            price_str = price_element.text.replace(price_text.text, "")
            price = float(price_str.replace("€", "").replace(t_separator, "").strip())

            if price > self._config.max_price:
                return False
        except Exception as err:
            print(err)
            return False

        return True

    # Attempts to buy the product
    def _purchase_product(self, driver: Remote, product: str) -> bool:
        productUrl = urljoin(urljoin(self._config.url, "/dp/"), product)
        if product not in driver.current_url:
            driver.get(productUrl)
            time.sleep(0.3)

        if not self._helper.captcha(driver):
            return False

        t_separator = self._helper.get_thousands_separator(driver)
        labels = self._helper.get_lang_labels(driver)

        # Click the Button
        try:
            driver.find_element(By.ID, "buy-now-button").click()
        except Exception:
            print(f"Buy now Button missing at: {productUrl}")
            return False

        is_product_in_url = product in driver.current_url
        turbo_iframe = None
        if is_product_in_url:
            turbo_iframe = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//iframe[@id='turbo-checkout-iframe']")
                )
            )

        # Final price check
        try:
            price_element = None
            if is_product_in_url:
                # Turbo Checkout
                driver.switch_to.frame(turbo_iframe)
                price_element = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located(
                        (
                            By.XPATH,
                            "//div[@cel_widget_id='turbo-cel-price-panel']//span[contains(text(), '€')]",
                        )
                    )
                )
            else:
                # When it redirects to the checkout screen
                # Might have to add more sleep or WebDriverWait here?
                price_element = driver.find_element(
                    By.XPATH,
                    "//div[@id='spc-order-summary']//div[contains(@class, 'order-summary-line-definition')][last()]",
                )

            price = float(
                price_element.text.strip().replace("€", "").replace(t_separator, "")
            )

            if price > self._config.max_price:
                print(
                    f"Final price {price}{self._config._currency} exceeds the set max price {self._config.max_price}{self._config._currency}. Aborting purchase..."
                )
                return False
        except TimeoutException as te:
            print("Final price check timeout: ", te.msg)
            return False
        except NoSuchElementException as ne:
            print("Final price check element not found: ", ne.msg)
            return False
        except Exception as e:
            print(f"Final price check failed: {e}")
            return False
        finally:
            if turbo_iframe:
                driver.switch_to.default_content()

        # Press buy
        try:
            buyButton = None
            if is_product_in_url:
                # Turbo Checkout
                driver.switch_to.frame(turbo_iframe)
                buyButton = WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located(
                        (By.ID, "turbo-checkout-pyo-button")
                    )
                )
            else:
                # When it redirects to the checkout screen
                buyButton = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.NAME, "placeYourOrder1"))
                )
            buyButton.click()
        except TimeoutException as te:
            print("Final order button timeout: ", te.msg)
            return False
        except NoSuchElementException as ne:
            print("Final order button element not found: ", ne.msg)
            return False
        except Exception as e:
            print(f"Final order button error at: {productUrl}\n", e)
            return False
        finally:
            if turbo_iframe:
                driver.switch_to.default_content()

        # Bank MFA
        try:
            WebDriverWait(driver, self._config.bmfa_timeout).until(
                EC.visibility_of_element_located(
                    (By.XPATH, f"//*[contains(text(), '{labels['thank_you_msg']}')]")
                )
            )
            print("Order confirmed!")
        except Exception:
            print("Bank MFA may be required, please proceed manually!")

        return True

    # Clears the cart after purchase attempts
    def _clear_cart(self, driver: Remote) -> bool:
        driver.get(self._config.cart_url)

        if not self._helper.captcha(driver):
            return False

        labels = self._helper.get_lang_labels(driver)

        try:
            # Remove all items from the cart
            while True:
                delete_button = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//input[@value='{labels['delete_button']}']")
                    )
                )
                delete_button.click()
        except Exception:
            pass

        # Verify the cart is empty
        driver.get(self._config.cart_url)

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        f"//h3[contains(text(), '{labels['empty_cart_message']}')]",
                    )
                )
            )
        except Exception:
            print("Couldn't verify that cart is empty.")
            return False

        return True

    def run(self, stop_event: Event) -> None:
        buyDriver = self._helper.create_driver(not self._config._mfa)
        checkDriver = self._helper.create_driver(True)

        # login
        if not self._login(buyDriver):
            print("AmazonBot.run Exiting...")
            buyDriver.quit()
            checkDriver.quit()
            return

        productCheckCounter = 0
        purchaseCounter = 0

        products = self._config.products
        loop_timeout = self._config.loop_timeout

        while not stop_event.is_set():
            try:
                loopStart = datetime.datetime.now()

                for product in products:
                    productCheckCounter = productCheckCounter + 1

                    if self._check_product(checkDriver, product):
                        retry = 0
                        purchase_success = False
                        while retry < self._config.retry_count:
                            purchaseCounter = purchaseCounter + 1
                            if self._purchase_product(buyDriver, product):
                                purchase_success = True
                                stop_event.set()
                                # break should be enough though
                                retry = self._config.retry_count + 1
                                break
                            else:
                                retry = retry + 1

                        if not purchase_success:
                            # Returns a value, but meh, whatever
                            self._clear_cart(buyDriver)
                print(
                    "AmazonBot - ",
                    self._config.loop_timeout,
                    "s sleep! Products checked: ",
                    productCheckCounter,
                    " Purchase attempts: ",
                    purchaseCounter,
                    " Loop start: ",
                    loopStart,
                    " Loop end: ",
                    datetime.datetime.now(),
                )
                time.sleep(loop_timeout)
            except Exception as e:
                print("AmazonBot.run Error: ", e)
                break

        print("AmazonBot.run Exiting...")
        buyDriver.quit()
        checkDriver.quit()
