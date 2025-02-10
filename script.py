import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from urllib.parse import urljoin
import time
import os

load_dotenv()

# Configuration
BROWSER = os.getenv("BROWSER")
DRIVER_PATH = os.getenv("DRIVER_PATH")
AMZ_URL = os.getenv("AMZ_URL")
AMZ_PRODUCT_BASE_URL = urljoin(AMZ_URL, "/dp/")
AMZ_CART_URL = urljoin(AMZ_URL, "/gp/cart/view.html")
AMZ_EMAIL = os.getenv("AMZ_EMAIL")
AMZ_PWD = os.getenv("AMZ_PWD")
PRODUCTS_STR = os.getenv("PRODUCTS")
MAX_PRICE_STR = os.getenv("MAX_PRICE")
BMFA_TIMEOUT_STR = os.getenv("BMFA_TIMEOUT")
PRODUCTS = [
    urljoin(AMZ_PRODUCT_BASE_URL, id.strip())
    for id in PRODUCTS_STR.split(";")
    if id.strip()
]
MAX_PRICE = int(MAX_PRICE_STR)
BMFA_TIMEOUT = int(BMFA_TIMEOUT_STR)
LOOP_TIMEOUT = 5
RETRY_COUNT = 3

# Language-specific labels
LANGUAGE_LABELS = {
    "de": {
        "cart_button": "In den Einkaufswagen",
        "delete_button": "Löschen",
        "empty_cart_message": "Ihr Amazon-Einkaufswagen ist leer",
        "thank_you_msg": "Vielen Dank",
    },
    "en": {
        "cart_button": "Add to Cart",
        "delete_button": "Delete",
        "empty_cart_message": "Your Amazon Cart is empty",
        "thank_you_msg": "Thank you",
    },
}


# Function to initialize a WebDriver instance
def create_driver(headless=False):
    service = Service(executable_path=DRIVER_PATH)
    if BROWSER == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    elif BROWSER == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(service=service, options=options)
        return driver
    else:
        raise ValueError(f"Unsupported browser: {BROWSER}")


# Detect the page language
def detect_language(driver):
    html = driver.find_element(By.TAG_NAME, "html")
    return html.get_attribute("lang")  # Returns language code like "de", "en", etc.


"""
def check_and_solve_captcha(driver):
    try:
        # Look for CAPTCHA elements (common identifiers)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "captchacharacters"))
        )
        print("CAPTCHA detected.")

        captcha = AmazonCaptcha.fromdriver(driver)
        captcha.solve()

        return True
    except Exception:
        return False
"""


# Log in to Amazon
def login_to_amazon(driver):
    driver.get(AMZ_URL)

    try:
        time.sleep(1)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "nav-link-accountList"))
        ).click()
        time.sleep(1)

        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "ap_email_login"))
            ).send_keys(AMZ_EMAIL + Keys.RETURN)
        except Exception:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "ap_email"))
            ).send_keys(AMZ_EMAIL + Keys.RETURN)

        time.sleep(1)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ap_password"))
        ).send_keys(AMZ_PWD + Keys.RETURN)
    except Exception:
        print("Login failed while entering credentials")
        return False

    # Wait for manual MFA input and verify login success
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
def check_product(driver, productUrl):
    driver.get(productUrl)

    # Check if add-to-cart is present
    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.ID, "add-to-cart-button"))
        )
    except Exception:
        return False

    print("Item in stock! ", productUrl)

    # Price threshold check
    try:
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
        price_str = price_element.text.replace(price_text.text, "")
        price = float(price_str.replace("€", "").replace(",", ""))
    except Exception:
        return False

    if price < MAX_PRICE:
        print(
            f"Price €{price} is below the threshold of €{MAX_PRICE}. Proceeding with purchase."
        )
    else:
        print(
            f"Price €{price} is above the threshold of €{MAX_PRICE}. Aborting purchase."
        )
        return False

    return True


# Clear the cart and verify it's empty
def clear_cart(driver):
    driver.get(AMZ_CART_URL)
    language = detect_language(driver)
    labels = LANGUAGE_LABELS.get(
        language, LANGUAGE_LABELS["en"]
    )  # Default to English if language not found

    try:
        # Remove all items from the cart
        while True:
            delete_button = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//input[@value='{labels['delete_button']}']")
                )
            )
            delete_button.click()
            print(f"Item removed from cart ({language}).")
    except Exception:
        print("No more items to remove.")

    # Verify the cart is empty
    driver.get(AMZ_CART_URL)

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//h3[contains(text(), '{labels['empty_cart_message']}')]")
            )
        )
        print(f"Cart is empty ({language}).")
        return True
    except Exception:
        print("Cart is not empty or verification failed.")
        return False


# Purchase
def purchase(driver, product):
    driver.get(product)
    language = detect_language(driver)
    labels = LANGUAGE_LABELS.get(
        language, LANGUAGE_LABELS["en"]
    )  # Default to English if language not found

    # Add to cart
    try:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "add-to-cart-button"))
        ).click()
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.NAME, "proceedToRetailCheckout"))
        ).click()
    except Exception:
        print("Could not add to cart / proceed to checkout.")
        return False

    # Select address
    try:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "address-book-entry-0"))
        ).click()
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.NAME, "shipToThisAddress"))
        ).click()
    except Exception:
        print("Couldn't select address.")

    # Select shipping option
    try:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "shipping-option-0"))
        ).click()
    except Exception:
        print("Couldn't set shipping.")

    # Price threshold check
    try:
        price_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class, 'grand-total-cell') and contains(@class, 'a-span12') and contains(@class, 'a-column')]",
                )
            )
        )
        price_text = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class, 'grand-total-cell') and contains(@class, 'a-span12') and contains(@class, 'a-column')]/span",
                )
            )
        )
        price_str = price_element.text.replace(price_text.text, "")
        price = float(price_str.replace("€", "").replace(",", ""))
    except Exception:
        print("Couldn't load price.")
        return False

    if price < MAX_PRICE:
        print(
            f"Price €{price} is below the threshold of €{MAX_PRICE}. Proceeding with purchase."
        )
    else:
        print(
            f"Price €{price} is above the threshold of €{MAX_PRICE}. Aborting purchase."
        )
        return False

    # Place order and wait for Bank MFA
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "placeYourOrder1"))
        ).click()
        print("Order placed! Waiting for Bank MFA approval...")
    except Exception:
        print("Couldn't place order")
        return False

    # Wait for Bank MFA approval
    try:
        WebDriverWait(driver, BMFA_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[contains(text(), '{labels['thank_you_msg']}')]")
            )
        )
        print("Bank MFA approval completed. Order confirmed!")
    except Exception:
        print("Bank MFA approval timed out. Please check manually.")
        # raise TimeoutError("Bank MFA approval timed out. Please check manually.")

    return True


# Main function
def main():
    mainDriver = create_driver(False)

    if not login_to_amazon(mainDriver):
        mainDriver.quit()
        exit()

    # checkDriver = create_driver(True)

    loopCounter = 0
    productCheckCounter = 0
    purchaseCounter = 0

    try:
        repeat = True
        while repeat:
            loopStart = datetime.datetime.now()
            for product in PRODUCTS:
                time.sleep(1)
                productCheckCounter = productCheckCounter + 1
                if check_product(mainDriver, product):
                    retry = 0
                    while retry < RETRY_COUNT and repeat:
                        purchaseCounter = purchaseCounter + 1
                        if purchase(mainDriver, product):
                            repeat = False
                        else:
                            clear_cart(mainDriver)
                            retry = retry + 1
                    break

            loopCounter = loopCounter + 1

            print(
                "No purchase - ",
                LOOP_TIMEOUT,
                "s sleep! Loops: ",
                loopCounter,
                " Products checked: ",
                productCheckCounter,
                " Purchase attempts: ",
                purchaseCounter,
                " Loop start: ",
                loopStart,
                " Loop end: ",
                datetime.datetime.now(),
            )
            time.sleep(LOOP_TIMEOUT)
    finally:
        # checkDriver.quit()
        mainDriver.quit()


if __name__ == "__main__":
    main()
